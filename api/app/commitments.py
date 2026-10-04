"""Commitments (NEW_CHANGES NC-03, §6.2, §8.1, §9.1) and POST /projection (NC-04, §9.2).

GET  /commitments/suggested/{property_id}: the catalog at this home, ranked by CO₂ saved per net $ (cost − rebate).
     Effects come only from P1's model: the property's /estimate session re-run with each action's change
     (concurrently, under estimate.MODEL_SLOTS), minus the session's own estimate. Actions P1 can't price yet are
     placeholders: pending_model true, every effect number null.
POST /commitments · PATCH /commitments/{id} · GET /commitments: accepted → completed | dismissed, never backwards.
     Completing records the renter's word (evidence "reported"); it never changes the current grade.
POST /projection: every modeled commitment applied in ONE model run (effects don't add). Stored for
     latest_projection(); never writes a snapshot or touches the session (I3).
"""

import json
import secrets
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import date, datetime, timezone
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app import accounts, db, estimate, fixes, sessions
from app.co2 import co2_kg
from app.score import score_for

router = APIRouter()

PENDING = "pending P1 effect model (NEW_CHANGES NC-01)"
NO_CUT = "P1's model shows no CO₂ cut from this at this home, so it's shown without numbers (as in /fixes)"
LABEL = "projected_if_completed"
EPS_USD = 1  # rank by CO₂ ÷ max(cost − rebate, EPS_USD): free after rebates ranks first
WHO_HOUSING = "https://www.who.int/publications/i/item/9789241550376"  # WHO Housing and health guidelines (2018)
AIR, ATTIC, THERMOSTAT = fixes.UNPRICED
CITED = ("grh_item", "grh_points", "cost_usd", "rebate_usd", "cost_note", "sources")


def _cited(fix: dict) -> dict:
    """GRH item/points, cost, rebate and sources exactly as /fixes cites them (one copy of each figure)."""
    return {k: fix[k] for k in CITED}


CATALOG = {
    "air_sealing": {"title": "Seal drafts (renters: weatherstrip windows and doors)", "who_acts": "landlord",
                    **_cited(AIR), "model_mapping": {"input": "in.infiltration", "change": None}},
    "attic_insulation": {"title": "Insulate the attic to R-50", "who_acts": "landlord", **_cited(ATTIC),
                         "model_mapping": {"input": "in.insulation_ceiling", "change": None}},
    "wall_insulation": {"title": "Insulate the walls", "who_acts": "landlord",
                        "grh_item": "Walls are Insulated", "grh_points": 9, "cost_usd": None, "rebate_usd": 500,
                        "cost_note": "Rebate: A2ZERO above-grade wall insulation $500 ($1,000 income-qualified), "
                                     "250+ sq ft, contractor-installed.",
                        "sources": [fixes.GRH_PDF, fixes.A2ZERO, fixes.A2ZERO_APP],
                        "model_mapping": {"input": "in.insulation_wall", "change": None}},
    "window_upgrade": {"title": "Add storm windows or double-pane windows", "who_acts": "landlord",
                       **_cited(fixes.WINDOWS),
                       "model_mapping": {"input": "window_panes", "change": fixes.WINDOWS["change"]}},
    "thermostat_setback": {"title": "Turn the heat down at night and when you're out", "who_acts": "renter",
                           **_cited(THERMOSTAT), "sources": [*THERMOSTAT["sources"], WHO_HOUSING],
                           # D6: health-based floor, cited; nothing rewards going below it
                           "note": "Never set the heat below 64°F (18°C) while anyone is home, asleep included: the "
                                   "World Health Organization's health-based minimum indoor temperature for cold "
                                   "seasons (keep it warmer for babies, older adults and anyone unwell).",
                           "model_mapping": {"input": None, "change": None,
                                             "note": "P1's model has no thermostat setpoint input (V5): bills only"}},
    "landlord_request": {"title": "Send your landlord the drafted email", "who_acts": "renter→landlord",
                         "grh_item": None, "grh_points": 0, "cost_usd": None, "rebate_usd": None, "cost_note": None,
                         "sources": [], "model_mapping": {"input": "the top envelope fix's, once it's reported done",
                                                          "change": None}},
    "heat_pump": {"title": "Switch to a cold-climate heat pump", "who_acts": "landlord", **_cited(fixes.HEAT_PUMP),
                  "model_mapping": {"input": "heating_fuel + cooling_code", "change": fixes.HEAT_PUMP["change"],
                                    "note": "priced only where the home already heats with electricity: P1's model "
                                            "prices gas → heat pump like resistance heat"}},
}
FIX_IDS = {fixes.WINDOWS["item"]: "window_upgrade", fixes.HEAT_PUMP["item"]: "heat_pump"}
ENVELOPE = ("window_upgrade", "air_sealing", "attic_insulation", "wall_insulation")

SCHEMA = """
CREATE TABLE IF NOT EXISTS commitments (
  id TEXT PRIMARY KEY, user_id TEXT NOT NULL, property_id TEXT NOT NULL, catalog_id TEXT NOT NULL,
  status TEXT NOT NULL, evidence TEXT NOT NULL, target_date TEXT, accepted_at TEXT, completed_at TEXT,
  projection_id TEXT, reminder_channel TEXT NOT NULL DEFAULT 'none', calendar_event_id TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS commitments_accepted ON commitments (property_id, catalog_id)
  WHERE status = 'accepted';
CREATE TABLE IF NOT EXISTS projections (
  id TEXT PRIMARY KEY, property_id TEXT NOT NULL, created_at TEXT NOT NULL, body TEXT NOT NULL);
"""


def _fail(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(status, {"code": code, "message": message})


def _db():
    c = db.connect()
    c.executescript(SCHEMA)
    return c


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _row(r) -> dict:
    """Commitment shape (NEW_CHANGES Appendix A); optional fields left out when unset, plus the catalog title."""
    return {**{k: v for k, v in dict(r).items() if v is not None}, "title": CATALOG[r["catalog_id"]]["title"]}


def list_commitments(property_id: str | None = None, user_id: str | None = None) -> list[dict]:
    with closing(_db()) as c:
        rows = c.execute("SELECT * FROM commitments WHERE (?1 IS NULL OR property_id = ?1) "
                         "AND (?2 IS NULL OR user_id = ?2) ORDER BY rowid", (property_id, user_id)).fetchall()
    return [_row(r) for r in rows]


def latest_projection(property_id: str) -> dict | None:
    with closing(_db()) as c:
        r = c.execute("SELECT body FROM projections WHERE property_id = ? ORDER BY rowid DESC LIMIT 1",
                      (property_id,)).fetchone()
    return json.loads(r[0]) if r else None


def _home(property_id: str, request: Request) -> tuple[dict, dict]:
    """(property, its /estimate session), after checking the caller may see this home."""
    p = accounts.get_property(property_id)
    if p is None:
        raise _fail(404, "property_not_found", "We couldn't find that home. Send its address again to add it.")
    accounts.authorize(request, p["user_id"])
    s = p.get("session_id") and sessions.get(p["session_id"])
    if not s:
        raise _fail(404, "not_found", "We don't have a current estimate for that home. Send its address again.")
    return p, s


def _effect(s: dict, new: dict) -> tuple[dict, int, int]:
    """(score_for the re-run, $ saved a year, kg CO₂ saved a year) vs the session's own estimate."""
    a, n, b = s["heating_cooling"]["annual"], new["annual"], s["building"]
    k = estimate.renter_usd_key(s)  # $ saved is the renter's: cooling only when heat is included in the rent
    return (score_for(n["total_usd"], b["sqft"], b["type"]), round(a[k] - n[k]),
            round(co2_kg(a["gas_ccf"] - n["gas_ccf"], a["electric_kwh"] - n["electric_kwh"])))


def _at_home(s: dict, property_id: str, only: set | None = None) -> tuple[dict, dict, dict]:
    """(catalog entries that apply to this home, {catalog_id: model change} for the ones P1 prices here, {catalog_id:
    its single re-run}). /fixes' rules: windows only below double-pane; heat pump priced only for electric heat
    (skipped if it's already there); nothing priced on a metered building (answers don't enter its own meter fit); a
    change the model says doesn't cut CO₂ here is shown without numbers (noise: double-pane on 912 Mary St's electric
    path came out +$102/yr). landlord_request stands for the top envelope fix and inherits its effect once a
    commitment for that fix here is completed. `only`: re-run just these catalog ids."""
    cands = {FIX_IDS[f["item"]]: f for f in fixes._candidates(s)}
    entries = {cid: {**e, **({k: cands[cid][k] for k in ("grh_item", "grh_points")} if cid in cands else {})}
               for cid, e in CATALOG.items() if cid not in FIX_IDS.values() or cid in cands}
    method, params = s["heating_cooling"]["method"], estimate.session_params(s)
    priced = {cid: f["change"] for cid, f in cands.items() if method in f["methods"] and (only is None or cid in only)}
    with ThreadPoolExecutor(max(len(priced), 1)) as ex:  # estimate.MODEL_SLOTS caps P1 calls at 4 process-wide
        runs = dict(zip(priced, ex.map(lambda c: estimate._hc_ac({**params, **priced[c]}), priced)))
    changes = {c: ch for c, ch in priced.items() if _effect(s, runs[c])[2] > 0}
    # ponytail: windows are the only envelope fix P1 prices; rank by CO₂ per net $ once more are modeled (NC-01)
    target = next((c for c in ENVELOPE if c in changes), next(c for c in ENVELOPE if c in entries))
    t = entries[target]
    entries["landlord_request"] = {**entries["landlord_request"], **{k: t[k] for k in CITED},
                                   "title": f"Send your landlord the drafted email: {t['title'][0].lower()}{t['title'][1:]}",
                                   "requests": target}
    if target in changes and any(c["catalog_id"] == target and c["status"] == "completed"
                                 for c in list_commitments(property_id)):
        changes["landlord_request"], runs["landlord_request"] = changes[target], runs[target]
    return entries, changes, runs


def _item(cid: str, e: dict, s: dict, changes: dict, runs: dict) -> dict:
    proj = None
    if cid in changes:
        sc, usd, kg = _effect(s, runs[cid])
        proj = {"usd_saved_yr": usd, "co2_kg_saved_yr": kg, "score_delta": sc["score"] - s["score"],
                "new_grade": sc["grade"], "label": LABEL}
    net = None if e["cost_usd"] is None else max(e["cost_usd"] - (e["rebate_usd"] or 0), EPS_USD)
    return {"catalog_id": cid, **{k: v for k, v in e.items() if k != "model_mapping"},
            "projected": proj, "pending_model": proj is None,
            "co2_per_net_usd": round(proj["co2_kg_saved_yr"] / net, 4) if proj and net else None,
            "method": f"model_rerun: P1's /hc/estimate for this home with {changes[cid]}, minus its current estimate"
                      if proj else NO_CUT if cid in runs else PENDING}


def _rank(c: dict) -> tuple:
    """Modeled first by CO₂ per net $ (unknown cost after known; ties to more CO₂); then placeholders, the ones a
    renter can start first."""
    p = c["projected"]
    if p is None:
        return 1, c["who_acts"] == "landlord", 0, 0
    r = c["co2_per_net_usd"]
    return 0, r is None, -(r or 0), -p["co2_kg_saved_yr"]


@router.get("/commitments/suggested/{property_id}")
def get_suggested(property_id: str, request: Request) -> dict:
    """Catalog actions at this home, ranked (NEW_CHANGES §9.2). 404 property_not_found / not_found, 503
    model_unavailable."""
    _, s = _home(property_id, request)
    entries, changes, runs = _at_home(s, property_id)
    out = [_item(cid, e, s, changes, runs) for cid, e in entries.items()]
    return {"property_id": property_id, "commitments": sorted(out, key=_rank)}


class CommitRequest(BaseModel):
    user_id: str
    property_id: str
    catalog_id: str
    target_date: date | None = None


@router.post("/commitments")
def post_commitment(req: CommitRequest, request: Request) -> dict:
    """Accept an action: status accepted, evidence projected. Idempotent per (property, action) while accepted."""
    accounts.authorize(request, req.user_id)
    p = accounts.get_property(req.property_id)
    if p is None or p["user_id"] != req.user_id:
        raise _fail(404, "property_not_found", "We couldn't find that home on your account.")
    if req.catalog_id not in CATALOG:
        raise _fail(422, "unknown_action", "We don't have that action. Pick one from your suggested list.")
    prefs = (accounts.get_user(req.user_id) or {}).get("reminder_prefs") or {}
    channel = prefs.get("channel", "none") if req.target_date else "none"  # reminders need a target date (§9.6)
    with closing(_db()) as c, c:
        c.execute("INSERT OR IGNORE INTO commitments (id, user_id, property_id, catalog_id, status, evidence, "
                  "target_date, accepted_at, reminder_channel) VALUES (?, ?, ?, ?, 'accepted', 'projected', ?, ?, ?)",
                  ("cmt_" + secrets.token_hex(6), req.user_id, req.property_id, req.catalog_id,
                   req.target_date and req.target_date.isoformat(), _now(), channel))
        r = c.execute("SELECT * FROM commitments WHERE property_id = ? AND catalog_id = ? AND status = 'accepted'",
                      (req.property_id, req.catalog_id)).fetchone()
    return _row(r)


class PatchRequest(BaseModel):
    status: Literal["completed", "dismissed"]


@router.patch("/commitments/{commitment_id}")
def patch_commitment(commitment_id: str, req: PatchRequest, request: Request) -> dict:
    """accepted → completed (evidence reported) | dismissed. Repeating a status is a no-op; anything else is 409."""
    with closing(_db()) as c, c:
        r = c.execute("SELECT * FROM commitments WHERE id = ?", (commitment_id,)).fetchone()
        if r is None:
            raise _fail(404, "commitment_not_found", "We couldn't find that commitment.")
        accounts.authorize(request, r["user_id"])
        if r["status"] != req.status:
            if r["status"] != "accepted":
                raise _fail(409, "bad_transition", f"That one is already {r['status']}, so it can't be marked "
                            f"{req.status}. Accept it again from your suggestions to start over.")
            done = req.status == "completed"
            c.execute("UPDATE commitments SET status = ?, evidence = ?, completed_at = ? WHERE id = ?",
                      (req.status, "reported" if done else r["evidence"], _now() if done else None, commitment_id))
            r = c.execute("SELECT * FROM commitments WHERE id = ?", (commitment_id,)).fetchone()
    return _row(r)


@router.get("/commitments")
def get_commitments(request: Request, user_id: str | None = None, property_id: str | None = None) -> dict:
    if not (user_id or property_id):
        raise _fail(422, "missing_input", "Send a user_id or a property_id.")
    if not user_id:
        p = accounts.get_property(property_id)
        if p is None:
            raise _fail(404, "property_not_found", "We couldn't find that home.")
    accounts.authorize(request, user_id or p["user_id"])
    return {"commitments": list_commitments(property_id, user_id)}


def _band(p50: float, ref: dict) -> dict:
    """p10/p90 = p50 × the current bill's p10/p50 and p90/p50 (so a projected range is never narrower), else null."""
    mid = ref.get("p50")
    q = lambda x: round(p50 * x / mid) if x is not None and mid else None
    return {"p10": q(ref.get("p10")), "p50": round(p50), "p90": q(ref.get("p90"))}


class ProjectionRequest(BaseModel):
    property_id: str
    commitment_ids: list[str] = []  # commitment ids, or catalog ids for a what-if before accepting


@router.post("/projection")
def post_projection(req: ProjectionRequest, request: Request) -> dict:
    """Current vs projected if the commitments are completed: all modeled changes in ONE composed P1 run (each action's
    own run only screens it, as in suggested). Placeholders and actions the model says don't cut CO₂ here are listed
    in not_modeled. Zero modeled → projected == current."""
    _, s = _home(req.property_id, request)
    mine = {c["id"]: c["catalog_id"] for c in list_commitments(req.property_id) if c["status"] != "dismissed"}
    cids = []
    for i in req.commitment_ids:
        if (cid := i if i in CATALOG else mine.get(i)) is None:
            raise _fail(422, "unknown_commitment", "One of those isn't an open commitment for this home. Pick from "
                        "your accepted ones.")
        cids.append(cid)
    cids = list(dict.fromkeys(cids))
    _, changes, runs = _at_home(s, req.property_id, {*cids, *(ENVELOPE if "landlord_request" in cids else ())})
    modeled = [c for c in cids if c in changes]
    hc, ref = s["heating_cooling"], s["bill"]["annual"]
    a = hc["annual"]
    current = {"score": s["score"], "grade": s["grade"], "percentile_city": s.get("percentile_city"),
               "bill_annual": ref, "co2_kg_yr": _band(co2_kg(a["gas_ccf"], a["electric_kwh"]), ref)}
    projected, delta = {**current, "label": LABEL}, {"score": 0, "usd_saved_yr": 0, "co2_kg_saved_yr": 0}
    if modeled:
        change = {k: v for c in modeled for k, v in changes[c].items()}  # effects don't add: one composed run
        new = next((runs[c] for c in modeled if changes[c] == change), None) \
            or estimate._hc_ac({**estimate.session_params(s), **change})  # one action: its single run is the answer
        sc, usd, kg = _effect(s, new)
        n = new["annual"]
        projected = {"score": sc["score"], "grade": sc["grade"], "percentile_city": sc["percentile_city"],
                     "bill_annual": _band(n[estimate.renter_usd_key(s)], ref),
                     "co2_kg_yr": _band(co2_kg(n["gas_ccf"], n["electric_kwh"]), ref), "label": LABEL}
        delta = {"score": sc["score"] - s["score"], "usd_saved_yr": usd, "co2_kg_saved_yr": kg}
    pid = "prj_" + secrets.token_hex(6)
    body = {"id": pid, "projection_id": pid, "property_id": req.property_id, "commitment_ids": req.commitment_ids,
            "current": current, "projected": projected, "delta": {**delta, "label": LABEL}, "label": LABEL,
            "modeled": modeled, "not_modeled": [c for c in cids if c not in changes],
            "method": "model_rerun", "model_version": f"P1 /hc/estimate ({hc['method']} path)", "created_at": _now()}
    with closing(_db()) as c, c:  # the projection only: never a snapshot, never the session (I3)
        c.execute("INSERT INTO projections (id, property_id, created_at, body) VALUES (?, ?, ?, ?)",
                  (pid, req.property_id, body["created_at"], json.dumps(body)))
        c.executemany("UPDATE commitments SET projection_id = ? WHERE id = ?",
                      [(pid, i) for i in req.commitment_ids if i in mine])
    return body

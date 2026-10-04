"""Opt-in verified boards and private current/projected placement (NEW_CHANGES §9.5).

Verified cut is observed verified kg in billing periods ending this calendar year
as a percent of this home's initial annual CO2 baseline. It is not annualized.
Neighborhoods are Census tracts, and require five distinct homes (D7). Public
responses expose aliases or tract aggregates, never user/property IDs or addresses.
Individual boards cover the city even when scope=neighborhood is supplied: that
parameter alone does not identify a neighborhood. board=neighborhood gives tracts.
"""

import json
import math
import os
import re
import sqlite3
from bisect import bisect_left, bisect_right
from collections import defaultdict
from contextlib import closing
from datetime import date
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

from app import accounts, bills, calibrate, city, commitments, db, score, sessions

router = APIRouter()
BOARDS = ("verified_cut", "co2_avoided", "streak", "follow_through", "neighborhood")
MIN_HOMES = 5  # NEW_CHANGES D7, not a statistical confidence threshold.


def _fail(status: int, code: str, message: str):
    return HTTPException(status, {"code": code, "message": message})


def _number(value):
    try:
        value = float(value)
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def _alias(user: dict) -> str:
    # Only the explicitly chosen alias; never display_name, phone or address.
    alias = " ".join(str(user.get("alias") or "").split())[:64]
    if not alias or "@" in alias or len(re.sub(r"\D", "", alias)) >= 7 or re.match(r"^\d+\s", alias):
        return "Anonymous renter"
    return alias


def _home_key(prop: dict):
    # A footprint without a supplied unit number is one home for the privacy
    # threshold. This conservatively counts unlabeled apartments only once.
    address = " ".join(str(prop.get("address") or "").upper().split())
    unit = re.search(r"(?:\bAPT\b|\bUNIT\b|#)\s*(\S+)", address)
    if prop.get("building_id") is not None:
        return ("building", str(prop["building_id"]), unit.group(1) if unit else "")
    return ("address", address) if address else None


def _tract(prop: dict, session: dict) -> str | None:
    group = str(session.get("model_params", {}).get("block_group") or "")
    if len(group) == 12 and group.isdigit():
        return group[:11]
    # Same public footprint table used by the existing city leaderboard.
    if prop.get("building_id") is not None:
        row = next((r for r in city._table() if r["footprint_id"] == prop["building_id"]), None)
        group = str((row or {}).get("block_group") or "")
        if len(group) == 12 and group.isdigit():
            return group[:11]
    return None


def _streak(session_id: str | None) -> int:
    """Read the existing per-session bill-check store without inserting a bill."""
    path = Path(calibrate.DB).resolve()
    if not session_id or not path.exists():
        return 0
    try:
        with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as con:
            rows = con.execute("SELECT year * 12 + month, pct FROM bills WHERE session_id = ? ORDER BY 1 DESC",
                               (session_id,)).fetchall()
    except sqlite3.OperationalError:
        return 0  # The calibration store/table does not exist yet.
    count = 0
    for month, pct in rows:
        if pct >= 0 or month != rows[0][0] - count:
            break
        count += 1
    return count


def _verified(prop: dict) -> tuple[list[dict], float | None]:
    snapshots = [s for s in bills.list_snapshots(prop["id"]) if s.get("property_id") == prop["id"]
                 and s.get("source") == "initial_estimate"]
    baseline = min(snapshots, key=lambda s: (s.get("created_at", ""), s["id"]), default=None)
    if not baseline:
        return [], None
    kg = _number(baseline.get("co2_kg_yr", {}).get("p50"))
    if kg is None or kg <= 0:
        return [], None
    rows, seen = [], set()
    for impact in bills.list_impact(prop["id"]):
        if impact.get("property_id") != prop["id"] or impact.get("baseline_snapshot_id") != baseline["id"]:
            continue
        if impact.get("verified") is False or impact.get("evidence", "verified") != "verified":
            continue
        period = impact.get("period") or {}
        try:
            start, end = date.fromisoformat(period["start"]), date.fromisoformat(period["end"])
        except (ValueError, TypeError, KeyError):
            continue
        key = (start, end)
        avoided = _number(impact.get("co2_kg_avoided"))
        if end < start or end > date.today() or key in seen or avoided is None or avoided <= 0:
            continue
        seen.add(key)
        rows.append(impact)
    return rows, kg


def _participants() -> list[dict]:
    rows = []
    for user in accounts.list_users():
        if user.get("leaderboard_opt_in") is not True or user.get("demo"):
            continue
        prop = accounts.current_property(user["id"])
        if not prop or not prop.get("active") or prop.get("user_id") != user["id"]:
            continue
        session = sessions.get(prop["session_id"]) if prop.get("session_id") else {}
        impacts, baseline = _verified(prop)
        accepted = {c["id"]: c for c in commitments.list_commitments(property_id=prop["id"])
                    if c.get("property_id") == prop["id"] and
                    (c.get("accepted_at") or c.get("status") in {"accepted", "completed"})}
        # Only same-property verified ledger references establish completion;
        # commitment status/evidence alone never qualifies.
        verified_ids = {cid for impact in impacts for cid in impact.get("commitment_ids", [])}
        rows.append({"alias": _alias(user), "home": _home_key(prop), "tract": _tract(prop, session or {}),
                     "co2_kg_avoided": sum(float(i["co2_kg_avoided"]) for i in impacts
                                           if date.fromisoformat(i["period"]["end"]).year == date.today().year),
                     "baseline_co2_kg_yr": baseline, "streak_months": _streak(prop.get("session_id")),
                     "accepted": len(accepted), "verified": len(set(accepted) & verified_ids),
                     "verified_impact_count": len(impacts), "demo": False})
    return rows


def _demo_rows() -> list[dict]:
    if os.environ.get("DEMO_SEED") != "1":
        return []
    with closing(db.connect()) as con, con:
        con.execute("CREATE TABLE IF NOT EXISTS board_demo_entries (id TEXT PRIMARY KEY, body TEXT NOT NULL)")
        rows = [json.loads(r["body"]) for r in con.execute("SELECT body FROM board_demo_entries ORDER BY id")]
    return [{**r, "alias": "Demo " + str(r["alias"]).removeprefix("Demo "), "demo": True} for r in rows]


def board_result(board: str, scope: str = "city") -> dict:
    if board not in BOARDS:
        raise _fail(422, "bad_board", "Choose verified_cut, co2_avoided, streak, follow_through or neighborhood.")
    if scope not in {"city", "neighborhood"}:
        raise _fail(422, "bad_scope", "Choose scope=city or scope=neighborhood.")
    rows = _participants() + _demo_rows()
    entries = []
    if board == "neighborhood":
        groups = defaultdict(dict)
        for row in rows:
            if row["tract"] and row["home"] and row["co2_kg_avoided"] > 0:
                # Do not double-count a shared home, or combine demo and real evidence.
                home = tuple(row["home"]) if isinstance(row["home"], list) else row["home"]
                groups[(row["tract"], row["demo"])].setdefault(home, row)
        for (tract, demo), homes in groups.items():
            if len(homes) >= MIN_HOMES:
                entries.append({"geoid": tract, "area_type": "census_tract", "home_count": len(homes),
                                "co2_kg_avoided": round(sum(r["co2_kg_avoided"] for r in homes.values()), 2),
                                "value": round(sum(r["co2_kg_avoided"] for r in homes.values()), 2),
                                "unit": "kg", "evidence": "demo" if demo else "verified", "demo": demo})
    else:
        for row in rows:
            if not row["verified_impact_count"]:
                continue
            if board == "verified_cut":
                if row["co2_kg_avoided"] <= 0 or not row["baseline_co2_kg_yr"]:
                    continue
                value, unit = 100 * row["co2_kg_avoided"] / row["baseline_co2_kg_yr"], "percent"
            elif board == "co2_avoided":
                value, unit = row["co2_kg_avoided"], "kg"
            elif board == "streak":
                value, unit = row["streak_months"], "months"
            else:
                if not row["accepted"] or not row["verified"]:
                    continue
                value, unit = 100 * row["verified"] / row["accepted"], "percent"
            if value <= 0:
                continue
            entries.append({"alias": row["alias"], "value": round(value, 2), "unit": unit,
                            "evidence": "demo" if row["demo"] else ("bill_checks_with_verified_impact" if board == "streak" else "verified"),
                            "demo": row["demo"]})
    entries.sort(key=lambda e: (-e["value"], e.get("alias", e.get("geoid", "")), e["demo"]))
    for i, entry in enumerate(entries):
        entry["rank"] = 1 + sum(other["value"] > entry["value"] for other in entries[:i])
    return {"board": board, "scope": scope, "coverage": "census_tract" if board == "neighborhood" else "city",
            "entries": entries, "empty_reason": None if entries else
            ("No census tract has verified reductions from at least five opted-in homes yet." if board == "neighborhood"
             else "No opted-in homes have qualifying evidence for this board yet."),
            "year": date.today().year, "model_version": "verified_ledger_v1",
            "metric_note": "Verified kg are observed reductions in billing periods ending this year; verified_cut divides by the same home's initial annual CO2 baseline. Streaks are bill checks at homes with verified impact, not verified annual savings."}


def _placement(cost: float, peers: list[float]) -> dict:
    n = len(peers)
    lo, hi = bisect_left(peers, cost), bisect_right(peers, cost)
    percentile = 1 - (lo + hi) / (2 * n)
    pts = int(round(100 * percentile))
    # score and rank: same type, as /estimate's score; percentile_city: every city home, as /estimate's (app/score.py)
    city_pct = round(float(1 - score._cheaper(score.peer_costs(None), cost)), 3)
    return {"score": pts, "grade": city.grade(pts), "percentile_city": city_pct, "rank": min(n, lo + 1), "of": n}


@router.get("/leaderboard/position/{property_id}")
def position(property_id: str, request: Request) -> dict:
    prop = accounts.get_property(property_id)
    if not prop:
        raise _fail(404, "not_found", "That home was not found. Save your home first.")
    accounts.authorize(request, prop["user_id"])
    session = sessions.get(prop["session_id"]) if prop.get("session_id") else None
    if not session:
        raise _fail(404, "not_found", "That home's estimate expired. Send the listing again.")
    building = session.get("building") or {}
    sqft, annual = _number(building.get("sqft")), _number(session.get("bill", {}).get("annual", {}).get("p50"))
    snapshots = [s for s in bills.list_snapshots(property_id) if s.get("property_id") == property_id
                 and s.get("source") in {"initial_estimate", "questionnaire", "bill_regrade", "manual_refresh"}
                 and _number((s.get("bill_annual") or {}).get("p50")) is not None]
    latest = max(snapshots, key=lambda s: (s.get("created_at", ""), s["id"]), default=None)
    if latest:
        annual = _number(latest["bill_annual"]["p50"])
    if sqft is None or sqft <= 0 or annual is None or annual < 0:
        raise _fail(503, "position_unavailable", "We cannot place this home's estimate yet. Refresh its estimate.")
    peers = sorted(v for x in city.city_costs(building.get("type")) if (v := _number(x)) is not None and v >= 0)
    if not peers:
        raise _fail(503, "position_unavailable", "There are no scored city homes of this type to compare yet.")
    current = _placement(annual / sqft, peers)
    projection = commitments.latest_projection(property_id)
    projected = None
    if projection and projection.get("property_id") == property_id and not projection.get("pending_model"):
        p50 = _number((projection.get("projected") or {}).get("bill_annual", {}).get("p50"))
        if p50 is not None and p50 >= 0:
            marker, mine = _placement(p50 / sqft, peers), projection.get("projected") or {}
            # the ghost marker is /projection's own projected.score / percentile_city; rank is placed here
            projected = {"rank": marker["rank"], "score": mine.get("score", marker["score"]),
                         "percentile_city": mine.get("percentile_city", marker["percentile_city"]),
                         "label": "projected_if_completed"}
    center = min(len(peers) - 1, bisect_left(peers, annual / sqft))
    nearby = range(max(0, center - 2), min(len(peers), center + 3))
    neighbors = [{"rank": _placement(peers[i], peers)["rank"], "score": _placement(peers[i], peers)["score"],
                  "cost_per_sqft": round(peers[i], 6)} for i in nearby]
    return {"current": current, "projected": projected, "neighbors": neighbors,
            "percentile_basis": "same_type_city_costs", "label": "current",
            "current_source": latest["source"] if latest else "session",
            "model_version": (latest or {}).get("model_version") or session.get("model_version") or session.get("heating_cooling", {}).get("model_version") or "not_reported"}

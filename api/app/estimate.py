"""POST /estimate, POST /answer, GET /session/{id} (PLAN.md §10): listing link | address -> building features
(P2-01/02) -> P1 heating + cooling model -> score/grade/percentiles (app/score.py), p10/p90 band, next questions.
Every body is saved as the session's latest (app/sessions.py). co2_t (P2-03) and badges are wired in at merge.

/api reaches /model over HTTP (P1's server, `make -C model dashboard`, MODEL_BASE_URL, default :8001) so the two
Python environments (api: uv, py3.12; model: root .venv with xgboost/lightgbm/rasterio and pickled models) stay apart.
"""

import os
import re
import secrets
from concurrent.futures import ThreadPoolExecutor
from math import prod

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from shapely.geometry import shape

from app import sessions
from app.geo.features import get_features
from app.links import resolve_link
from app.score import GRADES, score_for

MODEL_BASE_URL = os.environ.get("MODEL_BASE_URL", "http://localhost:8001")
SEASONS = ("winter", "spring", "summer", "fall")
MONTHS = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")
NOT_A_HOME = "That doesn't look like a home. Send a residential address or listing."  # team decision (P2-04)
EXPIRED = "That session expired. Send the listing again."
MULTIFAMILY = ("Multi-Family with 2 - 4 Units", "Multi-Family with 5+ Units")
SKIP = {"skip", "not sure", "unsure", "idk", "dont know", "don't know", "i don't know"}
# Renter questions -> /hc/estimate params: P1's ANSWERS codes (model/heating_cooling/resstock_model.py) plus
# heating_fuel. Options are (value, label, extra words a renter might text instead of the label).
QUESTIONS = {
    "heating_fuel": ("Is the heat gas or electric?", [("gas", "Gas", "natural"), ("electric", "Electric", "")]),
    "window_panes": ("Are the windows single-, double- or triple-pane?",
                     [("1", "Single-pane", "one"), ("2", "Double-pane", "two"), ("3", "Triple-pane", "three")]),
    "floor_level": ("Is the unit on the ground floor, a middle floor or the top floor?",
                    [("0", "Ground floor", "first bottom"), ("1", "Middle floor", "mid"), ("2", "Top floor", "")]),
    "cooling_code": ("What air conditioning does the unit have?",
                     [("0", "No AC", "none"), ("1", "Window/room AC", "wall portable"), ("2", "Central AC", "central air"),
                      ("3", "Heat pump", "mini split minisplit ductless")]),
}

router = APIRouter()


def _fail(status: int, code: str, message: str, **extra) -> HTTPException:
    return HTTPException(status, {"code": code, "message": message, **extra})


def _hc(params: dict) -> dict:
    """GET /hc/estimate on P1's server; errors become friendly 422/503s."""
    try:
        r = httpx.get(f"{MODEL_BASE_URL}/hc/estimate", params={k: v for k, v in params.items() if v is not None},
                      timeout=180)  # a never-seen weather cell downloads its 1991+ history once
    except httpx.HTTPError as e:
        raise _fail(503, "model_unavailable", f"The heating/cooling model isn't reachable at {MODEL_BASE_URL} "
                    f"(start it: make -C model dashboard). {type(e).__name__}")
    if r.status_code == 422:
        raise _fail(422, "not_found", r.json().get("detail", "The model couldn't place this building."))
    if r.is_error:  # any other model failure is a friendly 503, never a bare 500
        raise _fail(503, "model_unavailable", f"The heating/cooling model failed on this building (HTTP {r.status_code}); "
                    "try again or send another address.")
    return r.json()


def _scaled(p50, lo: float, hi: float) -> dict:
    return {"p10": round(p50 * lo), "p50": p50, "p90": round(p50 * hi)}


def _respond(session_id: str, building: dict, params: dict, answers: dict, prev: dict | None = None) -> dict:
    """Run P1's model with the answers so far, then band, score and next questions; saved as the session's latest.

    p10/p90: the model's own spread over the questions not answered yet (each varied across its options, one at a
    time; the low/high ratios multiply, as P1's model works in log space, so p10 can't go negative), widened by P1's
    held-out real-meter error for this estimate path. `prev` (the annual band before this answer) caps it: model
    interactions can make one remaining question swing more than two did, but an answer only adds information."""
    known = {q: v for q, v in answers.items() if v is not None}
    hc = _hc({**params, **known})  # alone first: warms a never-seen weather cell before the parallel calls
    btype = building["type"]
    open_qs = [q for q in QUESTIONS if q not in known and (q != "floor_level" or btype in MULTIFAMILY)
               and not (q == "heating_fuel" and hc["method"] == "metered")]  # metered: fuel is read off the meters
    jobs = [(q, v) for q in open_qs for v, _, _ in QUESTIONS[q][1]]
    with ThreadPoolExecutor(4) as ex:  # ponytail: fixed 4, P1's server is shared (city batch); raise if it idles
        results = ex.map(lambda j: _hc({**params, **known, j[0]: j[1]})["annual"]["total_usd"], jobs)
        totals: dict[str, list] = {}
        for (q, _), t in zip(jobs, results):
            totals.setdefault(q, []).append(t)
    swing = {q: (min(t), max(t)) for q, t in totals.items()}
    p50 = hc["annual"]["total_usd"]
    err = (hc.get("accuracy", {}).get("seasonal_gas_median_abs_error") or {}).get("all") or 0
    p10 = round(p50 * prod(min(1, lo / p50) for lo, _ in swing.values() if p50) * (1 - err))
    p90 = round(p50 * prod(max(1, hi / p50) for _, hi in swing.values() if p50) * (1 + err))
    if prev and None not in (prev["p10"], prev["p90"]) and prev["p10"] <= p50 <= prev["p90"]:
        p10, p90 = max(p10, prev["p10"]), min(p90, prev["p90"])
    lo_r, hi_r = (p10 / p50, p90 / p50) if p50 else (1, 1)

    sqft = hc["unit_sqft"]
    best, worst = score_for(p10, sqft, btype)["grade"], score_for(p90, sqft, btype)["grade"]  # high cost = worse
    span = list(GRADES[GRADES.index(best):GRADES.index(worst) + 1])
    # ask only what moves this estimate and wasn't skipped, biggest swing first
    ask = sorted((q for q in open_qs if q not in answers and swing[q][1] - swing[q][0] >= 1),
                 key=lambda q: swing[q][1] - swing[q][0], reverse=True)
    seasons = {x["season"]: x for x in hc["seasons"]}
    body = {
        "session_id": session_id,
        "building": {**building, "sqft": sqft,
                     "year_built": hc["building"].get("year_built", building["year_built"]),
                     "year_built_source": hc["building"].get("year_built_source", building["year_built_source"])},
        "bill": {"covers": "heating + cooling only (P1 model); base electricity, hot water and fixed charges not yet",
                 "annual": {"p10": p10, "p50": p50, "p90": p90},
                 "seasonal": {x: _scaled(seasons[x]["total_usd"], lo_r, hi_r) for x in SEASONS if x in seasons},
                 "monthly": {MONTHS[m["month"] - 1]: _scaled(m["total_usd"], lo_r, hi_r) for m in hc.get("months", [])},
                 # additive
                 "band_method": f"p10/p90 = p50 × the model's lowest/highest ratio for each of the {len(open_qs)} "
                                f"question(s) not answered yet (each varied over its options, ratios multiplied), "
                                f"widened by ±{err:.0%}: P1's median error vs held-out real Ann Arbor gas meters for "
                                f"this estimate path ({hc['method']}). Never wider than before the last answer. "
                                "Seasons and months are scaled by the same ratios."},
        "co2_t": None,
        **score_for(p50, sqft, btype), "grade_span": span, "locked": len(span) == 1 or not ask,
        "badges": [],
        "questions": [{"id": q, "text": QUESTIONS[q][0],
                       "options": [{"value": v, "label": lab} for v, lab, _ in QUESTIONS[q][1]]} for q in ask],
        "heating_cooling": hc,  # additive: P1's full answer (heating vs cooling, energy, weather, method, accuracy)
        "answers": answers, "model_params": params,  # additive (see app/sessions.py)
    }
    sessions.save(body)
    return body


def estimate(url: str | None = None, address: str | None = None, unit_sqft: float | None = None) -> dict:
    if not (url or address):
        raise _fail(422, "missing_input", "Send a listing link or an Ann Arbor street address.")
    if unit_sqft is not None and not 100 <= unit_sqft <= 10_000:  # the bill scales with it: -50 gave -$81/yr
        raise _fail(422, "bad_unit_sqft", "Unit size should be the unit's floor area in square feet (100 to 10,000).")
    if url:
        link = resolve_link(url)
        if link["needs_address"] or not link["address"]:
            # team decision: never auto-geocode a hint; ask the renter to confirm the address
            raise _fail(422, "needs_address", "That link doesn't show the street address. What's the address?",
                        hint=link.get("hint"), source=link.get("source"))
        address = link["address"]
    try:
        f = get_features(address, unit_sqft)
    except LookupError:
        raise _fail(422, "not_found", "We couldn't find that building. Hidden Rent covers homes in the City of "
                    "Ann Arbor, MI; send a street address there.", address=address)
    except httpx.HTTPError as e:  # Census geocoder / Census Reporter down; cached addresses still work
        raise _fail(503, "lookup_unavailable", f"Address lookup is down right now ({type(e).__name__}); try again.")
    if f["in.geometry_building_type_recs"] is None:
        raise _fail(422, "not_a_home", NOT_A_HOME, address=f["matched_address"])

    # A point inside P2's footprint, so P1 scores the same building (the geocoder point can sit on the street).
    pt = shape(f["footprint_geojson"]).representative_point()
    params = {"lat": pt.y, "lon": pt.x, "unit_sqft": f["in.sqft"],
              "building_type": f["in.geometry_building_type_recs"], "block_group": f["block_group_geoid"]}
    building = {"lat": f["lat"], "lon": f["lon"], "footprint_geojson": f["footprint_geojson"],
                "year_built": f["year_built"], "type": f["in.geometry_building_type_recs"],
                # additive
                "address": f["matched_address"], "sqft_estimated": f["sqft_estimated"],
                "year_built_source": f["year_built_source"],
                "warnings": f["warnings"]}  # P2-01's checks, e.g. a unit size outside ResStock's range
    return _respond(secrets.token_hex(5), building, params, {})


def _words(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", s.lower()))


def _parse(question_id: str, answer) -> str | None:
    """Option value for a texted answer: the value itself, label words ("double pane" -> "2"), or None for skip."""
    text, options = QUESTIONS[question_id]
    a = str(answer).strip().lower()
    try:
        a = f"{float(a):g}"  # 2, 2.0, "2" -> "2"
    except ValueError:
        pass
    if a in SKIP:
        return None
    if a in {v for v, _, _ in options}:
        return a
    hits = [(len(_words(a) & _words(f"{v} {lab} {extra}")), v) for v, lab, extra in options]
    best = max(n for n, _ in hits)
    if best and [n for n, _ in hits].count(best) == 1:
        return next(v for n, v in hits if n == best)
    labels = [lab for _, lab, _ in options]
    raise _fail(422, "bad_answer", f"Sorry, I didn't catch that. {text} Reply {', '.join(labels[:-1])} or {labels[-1]}, "
                "or say skip.")


class AnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str | int | float


@router.post("/answer")
def post_answer(req: AnswerRequest) -> dict:
    """Re-run the model with every answer so far: same shape as /estimate, narrower band, next questions."""
    s = sessions.get(req.session_id)
    if s is None:
        raise _fail(404, "not_found", EXPIRED)
    if req.question_id not in QUESTIONS:
        raise _fail(422, "bad_answer", "I don't have that question. Answer one of the questions I sent, or say skip.")
    answers = {**s["answers"], req.question_id: _parse(req.question_id, req.answer)}
    return _respond(s["session_id"], s["building"], s["model_params"], answers, s["bill"]["annual"])


@router.get("/session/{session_id}")
def get_session(session_id: str) -> dict:
    """The session's latest estimate (website -> iMessage handoff)."""
    s = sessions.get(session_id)
    if s is None:
        raise _fail(404, "not_found", EXPIRED)
    return s

"""POST /estimate glue: listing link | address -> building features (P2-01/02) -> P1 heating + cooling model.

Thin integration only (full P2-04 still to come). Fields of the PLAN.md §10 shape that have no source yet stay
null/empty: session_id, co2_t (P2-03), score/grade/percentiles/hidden rent/badges/questions (P2-04),
bill p10/p90 (needs held-out error quantiles from P1).

/api reaches /model over HTTP (P1's server, `make -C model dashboard`, MODEL_BASE_URL, default :8001) so the two
Python environments (api: uv, py3.12; model: root .venv with xgboost/lightgbm/rasterio and pickled models) stay apart.
"""

import os

import httpx
from fastapi import HTTPException
from shapely.geometry import shape

from app.geo.features import get_features
from app.links import resolve_link

MODEL_BASE_URL = os.environ.get("MODEL_BASE_URL", "http://localhost:8001")
SEASONS = ("winter", "spring", "summer", "fall")
MONTHS = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")
NOT_A_HOME = "That doesn't look like a home. Send a residential address or listing."  # team decision (P2-04)


def _fail(status: int, code: str, message: str, **extra) -> HTTPException:
    return HTTPException(status, {"code": code, "message": message, **extra})


def _band(p50) -> dict:
    return {"p10": None, "p50": p50, "p90": None}


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
    hc = r.json()
    seasons = {s["season"]: s for s in hc["seasons"]}
    return {
        "session_id": None,
        "building": {"lat": f["lat"], "lon": f["lon"], "footprint_geojson": f["footprint_geojson"],
                     "sqft": hc["unit_sqft"], "year_built": hc["building"].get("year_built", f["year_built"]),
                     "type": f["in.geometry_building_type_recs"],
                     # additive
                     "address": f["matched_address"], "sqft_estimated": f["sqft_estimated"],
                     "year_built_source": hc["building"].get("year_built_source", f["year_built_source"])},
        "bill": {"covers": "heating + cooling only (P1 model); base electricity, hot water and fixed charges not yet",
                 "annual": _band(hc["annual"]["total_usd"]),
                 "seasonal": {s: _band(seasons[s]["total_usd"]) for s in SEASONS if s in seasons},
                 "monthly": {MONTHS[m["month"] - 1]: _band(m["total_usd"]) for m in hc.get("months", [])}},
        "co2_t": None,
        "score": None, "grade": None, "grade_span": [], "locked": False,
        "percentile_peers": None, "percentile_city": None, "hidden_rent_usd_mo": None,
        "badges": [], "questions": [],
        "heating_cooling": hc,  # additive: P1's full answer (heating vs cooling, energy, weather, method, accuracy)
    }

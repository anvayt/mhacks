"""GET /map/{session_id}: P3 MapWidgetData, from P2's cached city GIS and P1's HTTP API.

Shape/sample: p3/map-widget web/scripts/build_map_fixture.py and web/HOUSE_SCHEMA.md.
No model imports: look-alike simulation/pricing stays pending P1's HTTP endpoint.
"""

import json
from functools import lru_cache
from threading import Lock

import httpx
import numpy as np
import shapely
from fastapi import APIRouter, HTTPException
from shapely.geometry import mapping, shape

from app import estimate, sessions
from app.geo import DATA_DIR
from app.geo.footprints import _index, _project, mailing_assignment, mailing_labels

router = APIRouter()
TIGERWEB_BG = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2023/MapServer/10/query"
BG_CACHE = DATA_DIR / "map_block_groups"
FOOTPRINTS_URL = "https://a2maps.a2gov.org/a2arcgis/rest/services/OSI/BuildingFootprints/FeatureServer/0"
ADDRESSES_URL = "https://a2maps.a2gov.org/a2arcgis/rest/services/MailingAddress/FeatureServer/0"
HEIGHT_SOURCE = "City of Ann Arbor BuildingFootprints ABG_BLD_HG (above-ground height, originally aerial LiDAR)"
PENDING = "pending P1: matching ResStock rented homes priced at this address needs P1's look-alike HTTP endpoint"
SQFT_PER_M2 = 10.7639  # same conversion as app.geo.features (exact ft = 0.3048 m)
_BG_LOCK = Lock()


def _unavailable(message: str) -> HTTPException:
    return HTTPException(503, {"code": "model_unavailable", "message": message})


@lru_cache(maxsize=1)
def _city_data() -> tuple:
    ix = _index()
    labels = mailing_labels(ix, mailing_assignment(ix))  # P3 HOUSE_SCHEMA §3, same labels as /city
    rows = []
    for i, (p, g, utm) in enumerate(zip(ix.props, ix.wgs, ix.utm)):
        rows.append({"id": int(p["OBJECTID"]), "address": labels.get(i),
                     "center": [round(v, 6) for v in g.centroid.coords[0]],
                     "height_ft": round(p["ABG_BLD_HG"], 1) if p.get("ABG_BLD_HG") else None,
                     "stories": p.get("STORIES"), "residential": p.get("Struc_Type") == "Residential",
                     "footprint_sqft": round(utm.area * SQFT_PER_M2)})
    bounds = [round(float(v), 5) for v in shapely.total_bounds(ix.wgs)]
    return ix, rows, bounds


def _selected(ix, footprint: dict) -> int:
    """Resolve the session's exact footprint, never re-select using a street-interpolated geocode."""
    geom = shape(footprint)
    pt = _project(np.array([geom.representative_point()]))[0]
    for i in ix.tree.query(pt, predicate="intersects"):
        if ix.wgs[i].equals(geom):
            return int(i)
    raise _unavailable("The session's footprint is no longer in the city cache. Send the listing again.")


def _similar(rows: list[dict], me: dict) -> dict:
    # P3 reference sample: at most 10, seed 0, same recorded stories and footprint within ±25%.
    # Deliberately a labelled test sample, not an efficiency ranking or evidence of matching unit size.
    pool = [r for r in rows if r["residential"] and r["address"] and r["id"] != me["id"]
            and r["stories"] == me["stories"] and r["height_ft"]
            and abs(r["footprint_sqft"] / me["footprint_sqft"] - 1) <= 0.25]
    chosen = sorted(np.random.default_rng(0).choice(len(pool), size=min(10, len(pool)), replace=False))
    keys = ("id", "address", "center", "height_ft", "stories", "footprint_sqft")
    return {"rule": f"test sample: {len(chosen)} of {len(pool):,} residential buildings with the same recorded "
                    f"stories ({me['stories']}) and footprint within ±25% of {me['footprint_sqft']:,} sq ft; "
                    "random, not ranked; missing recorded stories match only missing stories",
            "items": [{k: pool[i][k] for k in keys} for i in chosen]}


@lru_cache(maxsize=256)
def _block_group(geoid: str) -> dict:
    if not isinstance(geoid, str) or len(geoid) != 12 or not geoid.isdigit():
        raise _unavailable("This session has no Census block group for the map.")
    path = BG_CACHE / f"{geoid}.geojson"
    with _BG_LOCK:  # concurrent requests share one fetch and cannot read a partial cache file
        if path.exists():
            return json.loads(path.read_text())
        try:
            r = httpx.get(TIGERWEB_BG, params={"where": f"GEOID='{geoid}'", "outFields": "GEOID",
                                             "outSR": 4326, "f": "geojson"}, timeout=30)
            r.raise_for_status()
            geom = r.json()["features"][0]["geometry"]
            if geom["type"] not in {"Polygon", "MultiPolygon"}:
                raise ValueError("block group is not a polygon")
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as e:
            raise _unavailable("The Census block-group map is unavailable right now. Try again.") from e
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(geom))
        tmp.replace(path)
        return geom


def _step_params(model_params: dict, answers: tuple) -> str:
    """/hc/estimate params after these answers, built like /fixes and /forecast (estimate.session_params; skips add
    nothing). Answers left in model_params are stripped so public record is the baseline."""
    base = {k: v for k, v in model_params.items() if k not in estimate.QUESTIONS}
    return json.dumps(estimate.session_params({"model_params": base, "answers": dict(answers)}), sort_keys=True)


@lru_cache(maxsize=1024)
def _model_step(params_json: str) -> dict:
    """Cached per params, so a new answer reuses all previous steps (including public record).

    _hc_ac: same HTTP call as /answer (No AC rule, estimate.MODEL_SLOTS cap of 4). Calls within one request are
    sequential."""
    try:
        return estimate._hc_ac(json.loads(params_json))
    except (HTTPException, httpx.HTTPError) as e:
        raise _unavailable("The heating/cooling model is unavailable for this map. Try again.") from e


def _summary(hc: dict) -> dict:
    return {"annual_usd": round(hc["annual"]["total_usd"]),
            "seasons": {s["season"]: round(s["total_usd"]) for s in hc["seasons"]},
            "heating_fuel": hc["model_detail"]["heating_fuel"],
            "typical_error": hc["accuracy"]["seasonal_gas_median_abs_error"]["all"], "method": hc["method"]}


def _step(question_id: str, answer, hc: dict) -> dict:
    q = estimate.QUESTIONS.get(question_id)
    label = None if question_id == "public_record" else "Skipped" if answer is None else str(answer)
    if q and answer is not None:
        label = next((label for value, label, _ in q[1] if value == str(answer)), label)
    return {"id": question_id, "question": q[0] if q else None, "answer_label": label,
            "estimate": _summary(hc),
            "lookalikes": {"count": 0, "usd_yr": [], "p10": None, "p50": None, "p90": None}}


@router.get("/map/{session_id}")
def get_map(session_id: str) -> dict:
    s = sessions.get(session_id)
    if s is None:
        raise HTTPException(404, {"code": "not_found", "message": estimate.EXPIRED})
    public = _model_step(_step_params(s["model_params"], ()))
    answers = tuple(s.get("answers", {}).items())
    steps = [_step("public_record", None, public)]
    for n, (q, value) in enumerate(answers, 1):
        steps.append(_step(q, value, _model_step(_step_params(s["model_params"], answers[:n]))))

    ix, rows, bounds = _city_data()
    i = _selected(ix, s["building"]["footprint_geojson"])
    me, p = rows[i], ix.props[i]
    b = public["building"]
    stories = p.get("STORIES")
    story_source = "city footprint record (STORIES)"
    if not stories:
        height = p.get("ABG_BLD_HG")
        stories = max(1, round((height - ix.ft_offset) / ix.ft_per_story)) if height else None
        story_source = (f"city LiDAR height: (ABG_BLD_HG − {ix.ft_offset:.1f} ft) / {ix.ft_per_story:.1f} ft per "
                        "story, fitted to city footprints with recorded STORIES" if height else "city height unavailable")
    shares = b.get("heating_fuel_shares") or {}
    geoid = s["model_params"].get("block_group")
    year_source = b.get("year_built_source") or "unavailable"
    area_year = b.get("year_built") if "ACS" in year_source else None
    if area_year is None:
        year_source = "Block-group median unavailable from model HTTP response (building year source: " + year_source + ")"
    return {
        "address": s["building"]["address"],
        "center": [s["model_params"]["lon"], s["model_params"]["lat"]],
        "city_bounds": bounds, "buildings_url": "/data/a2-buildings.geojson",
        "building": {"id": me["id"], "footprint": mapping(ix.wgs[i]),
                     "height_ft": me["height_ft"], "height_source": HEIGHT_SOURCE,
                     "stories": stories, "stories_source": story_source,
                     "footprint_sqft": me["footprint_sqft"], "floor_area_sqft": round(b["gfa_ft2"]),
                     "floor_area_source": b.get("gfa_source") or "City of Ann Arbor public energy benchmarking reported gross floor area", "unit_sqft": round(s["model_params"]["unit_sqft"]),
                     "unit_sqft_source": ("P2 public-record unit-size estimate saved in this session; not measured "
                                          "unit area" if s["building"].get("sqft_estimated") else
                                          "P2 session unit size (listing/renter or single-home footprint × stories)"),
                     "building_type": s["building"]["type"],
                     "building_type_source": "P2 city footprint and mailing-address unit-count/townhouse classification"},
        "similar": _similar(rows, me),
        "block_group": {"geoid": geoid, "geometry": _block_group(geoid),
                        "median_year_built": area_year,
                        "median_year_built_source": year_source,
                        "gas_heat_share": shares.get("gas_share"), "electric_heat_share": shares.get("electric_share"),
                        "heating_fuel_source": b.get("heating_fuel_source", "unavailable")},
        "lookalikes": {"pool_size": 0, "rule": PENDING}, "steps": steps,
        "accuracy_basis": public["accuracy"]["basis"],
        "sources": [{"label": HEIGHT_SOURCE, "url": FOOTPRINTS_URL},
                    {"label": "City of Ann Arbor mailing addresses; P3 inside/nearest footprint within 1.1e-4 degrees for map labels",
                     "url": ADDRESSES_URL},
                    {"label": "US Census TIGERweb ACS 2023 block-group outlines; ACS 5-year year built and heating fuel",
                     "url": "https://tigerweb.geo.census.gov/"},
                    {"label": "NREL ResStock 2024.2 Michigan; P1's heating/cooling estimate", "url": "https://resstock.nrel.gov/"},
                    {"label": public["weather_source"], "url": "https://prism.oregonstate.edu/"},
                    {"label": "EIA Michigan residential gas and electricity prices", "url": "https://www.eia.gov/"}],
    }

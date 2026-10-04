"""Predicted city scores and privacy-preserving leaderboards (PLAN §5/§10).

Generate api/data/city_scores.csv with scripts/score_city.py, then restart the API.
Scores use the midpoint empirical percentile within type: ties share a rank and a
one-building peer set scores 50. Only the public benchmark layer may supply names.
Neighborhood scope uses Census tracts (the first 11 digits of a block-group GEOID),
a sourced coarser proxy, not named neighborhood boundaries:
https://www.census.gov/programs-surveys/geography/about/glossary.html#par_textimage_4
"""

import csv
import gzip
import json
import math
from bisect import bisect_left, bisect_right
from collections import defaultdict
from functools import cache
from pathlib import Path
from statistics import mean, median

from fastapi import APIRouter, HTTPException, Request, Response

from shapely.geometry import mapping

from app.geo.footprints import _index, mailing_assignment, mailing_labels

router = APIRouter()
TABLE_PATH = Path(__file__).resolve().parents[1] / "data" / "city_scores.csv"
BENCHMARK_SOURCE = ("https://utility.arcgis.com/usrsvcs/servers/1e3bed4240284b40b0c4fea6f8cb4522/"
                    "rest/services/OSI/BenchmarkingPerformanceMetrics/FeatureServer/0")
MIN_GROUP_BUILDINGS = 5  # PLAN §5 privacy rule / P2-06 user requirement.


def grade(score: float) -> str:
    return next((letter for threshold, letter in ((80, "A"), (60, "B"), (40, "C"), (20, "D"))
                 if score >= threshold), "F")


def score_rows(rows: list[dict]) -> list[dict]:
    """Return copies with same-type midpoint percentile score and median excess."""
    costs = defaultdict(list)
    for row in rows:
        sqft, annual = float(row["sqft"]), float(row["annual_usd"])
        if not math.isfinite(sqft) or not math.isfinite(annual) or sqft <= 0 or annual < 0:
            raise ValueError("City scores require finite nonnegative costs and positive unit sizes")
        costs[row["type"]].append(annual / sqft)
    costs = {kind: sorted(values) for kind, values in costs.items()}
    medians = {kind: median(values) for kind, values in costs.items()}
    scored = []
    for row in rows:
        cost = float(row["annual_usd"]) / float(row["sqft"])
        peers = costs[row["type"]]
        percentile = 100 * (bisect_left(peers, cost) + bisect_right(peers, cost)) / (2 * len(peers))
        score = 100 - percentile
        scored.append({**row, "cost_per_sqft": round(cost, 8), "score": round(score, 6),
                       "grade": grade(score), "excess_usd_per_sqft": round(cost - medians[row["type"]], 8)})
    return scored


def _unavailable(message: str) -> HTTPException:
    return HTTPException(503, {"code": "city_unavailable", "message": message})


@cache
def _table() -> list[dict]:
    try:
        with TABLE_PATH.open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        if not rows:
            raise ValueError("empty result table")
        ids = set()
        for row in rows:
            row["footprint_id"] = int(row["footprint_id"])
            if row["footprint_id"] in ids:
                raise ValueError("duplicate footprint")
            ids.add(row["footprint_id"])
            for key in ("sqft", "annual_usd", "cost_per_sqft", "score", "excess_usd_per_sqft", "heating_usd"):
                row[key] = float(row[key])
                if not math.isfinite(row[key]):
                    raise ValueError("non-finite score")
            if row["sqft"] <= 0 or row["annual_usd"] < 0 or not 0 <= row["score"] <= 100:
                raise ValueError("invalid score")
        return rows
    except (OSError, ValueError, KeyError) as exc:
        raise _unavailable("City scores are unavailable; run scripts/score_city.py and restart the API.") from exc


def city_costs(building_type: str) -> list[float]:
    """Cost per unit square foot for every scored footprint of this ResStock type."""
    return [row["cost_per_sqft"] for row in _table() if row["type"] == building_type]


def _round_coordinates(coords):
    # Six decimal WGS84 degrees are about 0.1 m: below the source imagery precision.
    return [_round_coordinates(c) if isinstance(c, (list, tuple)) else round(c, 6) for c in coords]


@cache
def _city_payload() -> tuple[bytes, bytes]:
    rows = {row["footprint_id"]: row for row in _table()}
    try:
        ix = _index()
        labels = mailing_labels(ix, mailing_assignment(ix))
        features = []
        for i, p in enumerate(ix.props):
            fid = int(p["OBJECTID"])
            props = {"id": fid, "h": round(p.get("ABG_BLD_HG") or 0, 1),
                     "r": int(p.get("Struc_Type") == "Residential")}
            if i in labels:
                props["a"] = labels[i]
            if fid in rows:
                props.update({key: rows[fid][key] for key in ("score", "grade", "excess_usd_per_sqft", "type")})
            geometry = mapping(ix.wgs[i])
            geometry["coordinates"] = _round_coordinates(geometry["coordinates"])
            features.append({"type": "Feature", "geometry": geometry, "properties": props})
        payload = json.dumps({"type": "FeatureCollection", "features": features},
                             separators=(",", ":"), allow_nan=False).encode()
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        raise _unavailable("City footprint or mailing-address data is unavailable; refresh the footprint cache.") from exc
    return payload, gzip.compress(payload, compresslevel=6, mtime=0)


def _accepts_gzip(header: str) -> bool:
    encodings = {}
    for item in header.lower().split(","):
        encoding, *params = item.strip().split(";")
        quality = 1.0
        for param in params:
            if param.strip().startswith("q="):
                try:
                    quality = float(param.strip()[2:])
                except ValueError:
                    quality = 0
        encodings[encoding] = quality
    return encodings.get("gzip", encodings.get("*", 0)) > 0


@router.get("/city")
def city(request: Request) -> Response:
    """Every footprint with P3 map attributes and scores where available; no landlord names."""
    raw, compressed = _city_payload()
    headers = {"Vary": "Accept-Encoding", "Cache-Control": "public, max-age=3600"}
    if _accepts_gzip(request.headers.get("accept-encoding", "")):
        headers["Content-Encoding"] = "gzip"
        raw = compressed
    return Response(raw, media_type="application/geo+json", headers=headers)


@cache
def _leaderboard(scope: str) -> dict:
    public, areas = defaultdict(list), defaultdict(list)
    for row in _table():
        # Zero metered heating can mean tenant meters are missing (P1 integration note),
        # so these buildings remain on the map but cannot win a named leaderboard.
        if row.get("benchmark_id") and row.get("benchmark_name") and row["heating_usd"] > 0:
            public[row["benchmark_id"]].append(row)
        group = row.get("block_group", "")
        if len(group) == 12 and group.isdigit():
            areas[group if scope == "city" else group[:11]].append(row)
    best = []
    for bid, rows in public.items():
        score = mean(row["score"] for row in rows)
        best.append({"benchmark_id": bid, "name": rows[0]["benchmark_name"], "score": round(score, 2),
                     "grade": grade(score), "cost_per_sqft": round(mean(r["cost_per_sqft"] for r in rows), 4),
                     "building_count": len(rows), "predicted": True, "source": BENCHMARK_SOURCE})
    worst = [{"geoid": geoid, "area_type": "block_group" if scope == "city" else "census_tract",
              "building_count": len(rows), "score": round(mean(r["score"] for r in rows), 2),
              "excess_usd_per_sqft": round(mean(r["excess_usd_per_sqft"] for r in rows), 4), "predicted": True}
             for geoid, rows in areas.items() if len(rows) >= MIN_GROUP_BUILDINGS]
    return {"best": sorted(best, key=lambda r: (-r["score"], r["benchmark_id"]))[:10],
            "worst_blocks": sorted(worst, key=lambda r: (-r["excess_usd_per_sqft"], r["geoid"]))[:10]}


@router.get("/leaderboard")
def leaderboard(scope: str = "city") -> dict:
    if scope not in {"city", "neighborhood"}:
        raise HTTPException(422, {"code": "bad_scope", "message": "Choose scope=city or scope=neighborhood."})
    return _leaderboard(scope)

"""US Census geocoder (no key), cached on disk so repeat lookups work offline.

Source: https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress
(benchmark=Public_AR_Current, vintage=Current_Current). Returns the matched address, lon/lat and the
2020 Census Block GEOID (its first 12 digits are the block group GEOID).
"""

import json

import httpx
from fastapi import HTTPException
from pyproj import Geod
from shapely.geometry import Point, shape

from app import city as city_scores  # not `city`: geocode() has a local of that name
from app.geo import DATA_DIR
from app.geo.footprints import CITY_POINT_MAX_M, city_address

URL = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
CACHE_PATH = DATA_DIR / "geocode_cache.json"
# TIGERweb block-group outlines (ACS 2023 = 2020 block groups), cached as <GEOID>.geojson by
# app.map_widget._block_group and scripts/warm_city.py (make demo-warm-city: the city's 145).
BG_OUTLINES = DATA_DIR / "map_block_groups"


def _key(address: str) -> str:
    return " ".join(address.upper().replace(",", " ").split())


def _save(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_PATH.with_suffix(f".{id(cache)}.tmp")
    tmp.write_text(json.dumps(cache, indent=1))
    tmp.replace(CACHE_PATH)


def geocode(address: str) -> dict | None:
    """Census match, with the exact city mailing point when Census misses or moves it over 250 m.

    A corrected point gets its own Census coordinate geography; the displaced address's block
    group is never reused. If that optional lookup is down, the city point still works and
    get_features derives its block group offline (offline_block_group). Both address and successful
    coordinate lookups are cached.
    """
    cache = json.loads(CACHE_PATH.read_text()) if CACHE_PATH.exists() else {}
    key = _key(address)
    city = city_address(address)
    if key not in cache:
        try:
            r = httpx.get(URL, timeout=30, params={
                "address": address, "benchmark": "Public_AR_Current", "vintage": "Current_Current", "format": "json"})
            r.raise_for_status()
            matches = r.json()["result"]["addressMatches"]
            hit = None
            if matches:
                m = matches[0]
                blocks = m["geographies"].get("2020 Census Blocks") or [{}]
                hit = {"matched_address": m["matchedAddress"], "lon": m["coordinates"]["x"],
                       "lat": m["coordinates"]["y"], "block_geoid": blocks[0].get("GEOID")}
            cache[key] = hit
            _save(cache)
        except httpx.HTTPError:
            if city is None:
                raise
    hit = cache.get(key)
    if city is None or (hit and Geod(ellps="WGS84").inv(
            hit["lon"], hit["lat"], city["lon"], city["lat"])[2] <= CITY_POINT_MAX_M):
        return hit
    city_key = "city-point:" + key
    if city_key in cache:
        return cache[city_key]
    try:
        r = httpx.get(URL.replace("onelineaddress", "coordinates"), timeout=30, params={
            "x": city["lon"], "y": city["lat"], "benchmark": "Public_AR_Current",
            "vintage": "Current_Current", "format": "json"})
        r.raise_for_status()
        blocks = r.json()["result"]["geographies"].get("2020 Census Blocks") or [{}]
        city["block_geoid"] = blocks[0].get("GEOID")
        cache[city_key] = city
        _save(cache)
    except httpx.HTTPError:
        pass  # Coordinate geography is optional; do not discard the authoritative city point.
    return city


def offline_block_group(lon: float, lat: float, footprint_id: int) -> tuple[str | None, str | None]:
    """(2020 block group GEOID, source) from disk only, for when the Census geocoder gave no block.

    The cached TIGERweb outline covering the point, else the footprint's row in api/data/city_scores.csv
    (scripts/score_city.py: the TIGERweb 2020 outline holding the footprint), else (None, None).
    ponytail: reads every cached outline per call (145 files, ~660 KB); only the Census-miss path pays it.
    """
    pt = Point(lon, lat)
    for path in sorted(BG_OUTLINES.glob("*.geojson")):
        if shape(json.loads(path.read_text())).covers(pt):
            return path.stem, "tigerweb_outline_cache"
    try:
        row = next((r for r in city_scores._table() if r["footprint_id"] == footprint_id), None)
    except HTTPException:  # city_scores.csv unreadable
        row = None
    return (row["block_group"], "city_scores") if row else (None, None)

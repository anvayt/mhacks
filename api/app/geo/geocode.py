"""US Census geocoder (no key), cached on disk so repeat lookups work offline.

Source: https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress
(benchmark=Public_AR_Current, vintage=Current_Current). Returns the matched address, lon/lat and the
2020 Census Block GEOID (its first 12 digits are the block group GEOID).
"""

import json

import httpx
from pyproj import Geod

from app.geo import DATA_DIR
from app.geo.footprints import CITY_POINT_MAX_M, city_address

URL = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
CACHE_PATH = DATA_DIR / "geocode_cache.json"


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
    group is never reused. If that optional lookup is down, the city point still works and ACS
    falls back to the county median. Both address and successful coordinate lookups are cached.
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

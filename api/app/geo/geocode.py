"""US Census geocoder (no key), cached on disk so repeat lookups work offline.

Source: https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress
(benchmark=Public_AR_Current, vintage=Current_Current). Returns the matched address, lon/lat and the
2020 Census Block GEOID (its first 12 digits are the block group GEOID).
"""

import json

import httpx

from app.geo import DATA_DIR

URL = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
CACHE_PATH = DATA_DIR / "geocode_cache.json"


def _key(address: str) -> str:
    return " ".join(address.upper().replace(",", " ").split())


def geocode(address: str) -> dict | None:
    """{"matched_address", "lon", "lat", "block_geoid"} for the first match, or None if no match."""
    cache = json.loads(CACHE_PATH.read_text()) if CACHE_PATH.exists() else {}
    key = _key(address)
    if key not in cache:
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
        cache[key] = hit  # a definitive "no match" is cached too; network errors raise and are not cached
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = CACHE_PATH.with_suffix(f".{id(cache)}.tmp")  # atomic replace: a crash never leaves half a file
        tmp.write_text(json.dumps(cache, indent=1))
        tmp.replace(CACHE_PATH)
    return cache[key]

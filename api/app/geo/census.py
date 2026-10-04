"""Median year structure built (ACS table B25035) for Washtenaw County, cached on disk.

Source: Census Reporter API (no key), latest ACS 5-year release (acs2024_5yr = ACS 2020-2024 on
2026-10-03): https://api.censusreporter.org/1.0/data/show/latest?table_ids=B25035&geo_ids=...
One call fetches every block group, every tract and the county itself. (api.census.gov now
redirects keyless requests to missing_key.html, so it is not used.)
Missing values (null, or Census sentinels like -666666666) fall back block group -> tract -> county.
"""

import json

import httpx

from app.geo import DATA_DIR

URL = "https://api.censusreporter.org/1.0/data/show/latest"
GEO_IDS = "150|05000US26161,140|05000US26161,05000US26161"  # Washtenaw block groups, tracts, county
CACHE_PATH = DATA_DIR / "acs_b25035_washtenaw.json"


def _table() -> dict:
    if not CACHE_PATH.exists():
        r = httpx.get(URL, params={"table_ids": "B25035", "geo_ids": GEO_IDS}, timeout=60)
        r.raise_for_status()
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(r.text)
    return json.loads(CACHE_PATH.read_text())


def _valid(v) -> int | None:
    return int(v) if isinstance(v, (int, float)) and 1700 <= v <= 2100 else None


def median_year_built(block_geoid: str | None) -> tuple[int | None, str]:
    """(year, source) for a 15-digit 2020 block GEOID; tries block group, then tract, then county."""
    t = _table()
    release = t["release"]["name"]
    geos = [("block group", "15000US" + block_geoid[:12]), ("tract", "14000US" + block_geoid[:11])] if block_geoid else []
    for name, geo in geos + [("county", "05000US26161")]:
        year = _valid(t["data"].get(geo, {}).get("B25035", {}).get("estimate", {}).get("B25035001"))
        if year:
            note = " (1939 means 1939 or earlier)" if year == 1939 else ""
            return year, f"{release} B25035 median year structure built, {name} {geo}{note}"
    return None, "ACS B25035 unavailable"

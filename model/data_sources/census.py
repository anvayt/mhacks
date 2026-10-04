"""US Census: address geocoding and block-group median year built (no keys).

- Geocoder: https://geocoding.geo.census.gov/geocoder/ (returns lat/lon + block group)
- ACS 5-year via Census Reporter (one request per county, cached): B25040 house heating fuel; B25037 median year structure built by tenure (renter-occupied, B25037003),
  falling back to B25035 (all units). https://api.censusreporter.org
"""
from __future__ import annotations

from functools import lru_cache

from model.data_sources.http import get_json

GEOCODER = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
CR = "https://api.censusreporter.org/1.0/data/show/latest"


def geocode(address: str) -> dict | None:
    js = get_json(GEOCODER, {"address": address, "benchmark": "Public_AR_Current", "vintage": "Current_Current",
                             "layers": "10", "format": "json"}, namespace="census")
    matches = js.get("result", {}).get("addressMatches", [])
    if not matches:
        return None
    m = matches[0]
    bg = (m.get("geographies", {}).get("Census Block Groups") or [{}])[0]
    return {"lat": m["coordinates"]["y"], "lon": m["coordinates"]["x"], "matched_address": m["matchedAddress"],
            "block_group": bg.get("GEOID")}


@lru_cache(maxsize=16)
def _county_bg_table(state_county: str) -> dict:
    js = get_json(CR, {"table_ids": "B25037,B25035,B25040", "geo_ids": f"150|05000US{state_county}"}, namespace="census")
    return js.get("data", {})


def median_year_built(block_group: str) -> tuple[float | None, str]:
    """Renter-occupied median year built for the block group (ACS 5-year)."""
    if not block_group:
        return None, "none"
    data = _county_bg_table(block_group[:5]).get(f"15000US{block_group}", {})
    renter = data.get("B25037", {}).get("estimate", {}).get("B25037003")
    if renter and renter > 1800:
        return float(renter), f"ACS 5-yr B25037 renter-occupied median year built, block group {block_group}"
    allu = data.get("B25035", {}).get("estimate", {}).get("B25035001")
    if allu and allu > 1800:
        return float(allu), f"ACS 5-yr B25035 median year built, block group {block_group}"
    return None, "none"


def heating_fuel(block_group: str) -> dict:
    """Share of occupied homes in the block group heated by utility gas vs electricity (ACS B25040)."""
    if not block_group:
        return {"fuel": "gas", "gas_share": None, "electric_share": None, "source": "default (no block group)"}
    e = _county_bg_table(block_group[:5]).get(f"15000US{block_group}", {}).get("B25040", {}).get("estimate", {})
    tot = e.get("B25040001") or 0
    if tot <= 0:
        return {"fuel": "gas", "gas_share": None, "electric_share": None, "source": "default (no ACS data)"}
    gas, elec = e.get("B25040002", 0) / tot, e.get("B25040004", 0) / tot
    return {"fuel": "gas" if gas >= elec else "electric", "gas_share": round(gas, 3), "electric_share": round(elec, 3),
            "source": f"ACS 5-yr B25040 house heating fuel, block group {block_group}"}

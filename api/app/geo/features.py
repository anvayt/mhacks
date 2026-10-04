"""Address -> building features named like NREL ResStock 2024.2 columns, so the bill model can use them as-is.

Category strings are copied from the ResStock 2024 release 2 Michigan baseline parquet
(MI_baseline_metadata_and_annual_results.parquet, distinct values read 2026-10-03):
- in.vintage: <1940, 1940s, 1950s, 1960s, 1970s, 1980s, 1990s, 2000s, 2010s (no 2020s bin)
- in.geometry_building_type_recs: Single-Family Detached, Single-Family Attached,
  Multi-Family with 2 - 4 Units, Multi-Family with 5+ Units, Mobile Home
- in.geometry_stories: integer strings ("1", "2", ... "35")
- in.county_name: "Washtenaw County" (in.county G2601610)

CLI (from /api): uv run python -m app.geo.features "500 S State St, Ann Arbor, MI" [--unit-sqft N] [--year-built Y]
"""

import argparse
import json

from app.geo.census import median_year_built
from app.geo.footprints import find_building, height_fit, stories_from_height
from app.geo.geocode import geocode

SQFT_PER_M2 = 10.7639  # 1 m = 3.28084 ft (exact definition: 0.3048 m/ft)
COUNTY = "Washtenaw County"
SFD, MF24, MF5 = "Single-Family Detached", "Multi-Family with 2 - 4 Units", "Multi-Family with 5+ Units"


def vintage(year: int) -> str:
    """Year built -> ResStock in.vintage bin. Years >= 2020 go to "2010s" (ResStock 2024.2 has no later bin)."""
    return "<1940" if year < 1940 else f"{min(year, 2019) // 10 * 10}s"


def building_type(struc_type: str | None, units: int) -> str | None:
    """City Struc_Type + unit count -> ResStock in.geometry_building_type_recs.

    Struc_Type only has Residential / Commercial / Office / Public, so the unit count (mailing addresses
    inside the footprint) decides: 1 -> Single-Family Detached, 2-4 -> Multi-Family with 2 - 4 Units,
    5+ -> Multi-Family with 5+ Units. A Residential footprint with no address counts as 1 unit.
    A Commercial/Office/Public footprint with no residential address has no ResStock type (None).
    Never produced (no data to tell them apart): Single-Family Attached, Mobile Home.
    """
    if units >= 5:
        return MF5
    if units >= 2:
        return MF24
    return SFD if units == 1 or struc_type == "Residential" else None


def get_features(address: str, unit_sqft: float | None = None, year_built: int | None = None) -> dict:
    """Features for one Ann Arbor address. Raises LookupError if it can't be geocoded or has no footprint.

    unit_sqft / year_built: optional values from the listing or the renter; they override the estimates.
    """
    geo = geocode(address)
    if geo is None:
        raise LookupError(f"Census geocoder found no match for {address!r}")
    b = find_building(geo["lon"], geo["lat"], streets=[address, geo["matched_address"]])
    p = b.props
    warnings: list[str] = []

    if p["STORIES"]:
        stories, stories_src = int(p["STORIES"]), "city footprint STORIES"
    else:
        stories = stories_from_height(p["ABG_BLD_HG"])
        ft, off = height_fit()
        stories_src = (f"city footprint ABG_BLD_HG {p['ABG_BLD_HG']:.0f} ft / {ft:.1f} ft per story "
                       f"(+{off:.1f} ft; least-squares fit on footprints with both STORIES and height)")

    building_sqft = round(b.area_m2 * SQFT_PER_M2 * stories)
    units = len(b.addresses)
    units_src = f"{units} residential mailing address(es) inside the footprint (City of Ann Arbor MailingAddress)"
    if units == 0 and p["Struc_Type"] == "Residential":
        units, units_src = 1, "no mailing address inside the footprint; Residential footprint assumed 1 unit"
    btype = building_type(p["Struc_Type"], units)
    if btype is None:
        warnings.append(f"Footprint Struc_Type is {p['Struc_Type']!r} with no residential address: not a known home")
    is_multi = units >= 2

    if unit_sqft:
        sqft, sqft_src, sqft_est = round(unit_sqft), "unit sq ft given by caller (listing or renter)", False
    elif btype is None:
        sqft, sqft_src, sqft_est = None, "not a home: no unit sq ft (see building_sqft)", False
    elif is_multi:
        sqft, sqft_est = round(building_sqft / units), True
        sqft_src = f"building floor area {building_sqft} sq ft / {units} units (includes hallways and common areas)"
    else:
        sqft, sqft_src, sqft_est = building_sqft, "footprint area (UTM 17N) x stories", False

    if year_built:
        year, year_src = int(year_built), "given by caller (listing)"
    else:
        year, year_src = median_year_built(geo["block_geoid"])

    return {
        "in.sqft": sqft,
        "in.geometry_stories": str(stories),
        "in.geometry_building_type_recs": btype,
        "in.vintage": vintage(year) if year else None,
        "in.county_name": COUNTY,
        "matched_address": geo["matched_address"],
        "lat": geo["lat"],
        "lon": geo["lon"],
        "footprint_geojson": b.geojson,
        "building_sqft": building_sqft,
        "is_multi_unit": is_multi,
        "est_units": units,
        "sqft_estimated": sqft_est,
        "year_built": year,
        "year_built_source": year_src,
        "block_group_geoid": geo["block_geoid"][:12] if geo["block_geoid"] else None,
        "warnings": warnings,
        "sources": {
            "lat_lon": "US Census geocoder (Public_AR_Current / Current_Current)",
            "footprint": f"City of Ann Arbor BuildingFootprints OBJECTID {p['OBJECTID']} "
                         f"(Struc_Type {p['Struc_Type']}), found via {b.match}",
            "in.geometry_stories": stories_src,
            "in.sqft": sqft_src,
            "building_sqft": "footprint area projected to UTM 17N (EPSG:32617) x stories",
            "est_units": units_src,
            "in.geometry_building_type_recs": f"{units} unit(s) -> ResStock category (see building_type())",
            "in.vintage": f"year built {year} ({year_src}) -> ResStock decade bin",
            "in.county_name": "all Ann Arbor addresses are in Washtenaw County; ResStock 2024.2 string",
        },
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("address")
    ap.add_argument("--unit-sqft", type=float)
    ap.add_argument("--year-built", type=int)
    a = ap.parse_args()
    print(json.dumps(get_features(a.address, a.unit_sqft, a.year_built), indent=2))

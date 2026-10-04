"""Address -> building features named like NREL ResStock 2024.2 columns, so the bill model can use them as-is.

Category strings are copied from the ResStock 2024 release 2 Michigan baseline parquet
(MI_baseline_metadata_and_annual_results.parquet, distinct values read 2026-10-03):
- in.vintage: <1940, 1940s, 1950s, 1960s, 1970s, 1980s, 1990s, 2000s, 2010s (no 2020s bin)
- in.geometry_building_type_recs: Single-Family Detached, Single-Family Attached,
  Multi-Family with 2 - 4 Units, Multi-Family with 5+ Units, Mobile Home
- in.geometry_stories: integer strings, categories 1-15, 20, 21, 35 (raw count kept in stories_raw)
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
SFA = "Single-Family Attached"
STORIES_CATS = (*range(1, 16), 20, 21, 35)  # in.geometry_stories categories, ResStock 2024.2 MI (team decision Oct 3)
# ResStock 2024.2 MI baseline, rechecked 2026-10-04 against model/data/processed/resstock_frame.parquet
# (18,756 homes): observed min/max and type medians, not limits on the size of real homes.
# Source: model/data_sources/resstock.py -> NREL OEDI 2024/resstock_tmy3_release_2/
# metadata_and_annual_results/by_state/state=MI/MI_baseline_metadata_and_annual_results.parquet.
SQFT_MIN = {SFD: 298, SFA: 273, MF24: 322, MF5: 322}
SQFT_MAX = {SFD: 5587, SFA: 7414, MF24: 6348, MF5: 6348}
TYPICAL_SQFT = {SFD: 1698, SFA: 1207, MF24: 854, MF5: 854}


def vintage(year: int) -> str:
    """Year built -> ResStock in.vintage bin. Years >= 2020 go to "2010s" (ResStock 2024.2 has no later bin)."""
    return "<1940" if year < 1940 else f"{min(year, 2019) // 10 * 10}s"


def building_type(struc_type: str | None, units: int) -> str | None:
    """City Struc_Type + unit count -> ResStock in.geometry_building_type_recs.

    Office/Public are not homes: "General Mailing" also includes business addresses. Commercial
    may have homes above shops (get_features also checks plausible floor area per unit).
    For residential candidates the unit count decides: 1 -> Single-Family Detached, 2-4 -> Multi-Family with 2 - 4 Units,
    5+ -> Multi-Family with 5+ Units. A Residential footprint with no address counts as 1 unit.
    A Commercial footprint with no mailing address has no ResStock type (None).
    Single-Family Attached comes from townhouse_row() instead. Never produced (no data): Mobile Home.
    """
    if struc_type in {"Office", "Public"}:
        return None
    if units >= 5:
        return MF5
    if units >= 2:
        return MF24
    return SFD if units == 1 or struc_type == "Residential" else None


def snap_stories(n: int) -> int:
    """Raw story count -> nearest ResStock 2024.2 MI in.geometry_stories category; ties go down (28 -> 21)."""
    return min(STORIES_CATS, key=lambda c: (abs(c - n), c))


def townhouse_row(struc_type: str | None, addresses: list[str], street_units: int, stories: int) -> bool:
    """Townhouse rule -> Single-Family Attached (checked before the unit-count rule).

    The city draws a row of townhouses as ONE footprint and gives each home its own house number
    (2841, 2843, ... 2851 HARDWICK RD), while apartments get "UNIT n" rows or share a number (912 / 912 1/2).
    Fires when: Residential footprint, 2+ residential addresses, each its own house number, no UNIT rows
    (inside the footprint or for the street line), at most 3 stories. That also catches side-by-side
    duplexes (506 / 508 PACKARD ST), which RECS 2020 (ResStock's source) counts as single-family attached.
    ponytail: no shared-wall rule; separate touching footprints (<=0.3 m) are 3 in the whole city.
    """
    nums = [a.split()[0] for a in addresses]
    return (struc_type == "Residential" and len(nums) >= 2 and len(set(nums)) == len(nums) and stories <= 3
            and street_units == 0 and not any(" UNIT " in a for a in addresses))


def get_features(address: str, unit_sqft: float | None = None, year_built: int | None = None) -> dict:
    """Features for one Ann Arbor address. Raises LookupError if it can't be geocoded or has no footprint.

    unit_sqft / year_built: optional values from the listing or the renter; they override the estimates.
    """
    geo = geocode(address)
    if geo is None:
        raise LookupError(f"Census geocoder and city MailingAddress found no match for {address!r}")
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

    building_sqft = round(b.area_m2 * SQFT_PER_M2 * stories)  # raw stories: real floor area
    stories_cat = snap_stories(stories)
    units = len(b.addresses)
    units_src = f"{units} residential mailing address(es) inside the footprint (City of Ann Arbor MailingAddress)"
    if b.street_units > units:
        units_src = (f"{b.street_units} '{b.street} UNIT n' rows, any TYPE (City of Ann Arbor MailingAddress); "
                     f"more than the {units} residential address(es) inside the footprint")
        units = b.street_units
    if units == 0 and p["Struc_Type"] == "Residential":
        units, units_src = 1, "no mailing address inside the footprint; Residential footprint assumed 1 unit"
    row = townhouse_row(p["Struc_Type"], b.addresses, b.street_units, stories)
    # Guard (team decision Oct 3): above the ResStock 2024.2 MI single-family max per address it's a co-op or
    # sorority (1500 Gilbert Ct Escher, 1205 Hill St AEPhi), not townhouses; fall through to the unit-count rule.
    per_addr = round(building_sqft / len(b.addresses)) if row else 0
    if row and per_addr <= SQFT_MAX[SFD]:
        btype = SFA
        type_src = (f"townhouse rule: {units} residential addresses in one Residential footprint, each its own "
                    f"house number, no UNIT rows, {stories} stories (<= 3) -> {SFA}")
    else:
        btype = building_type(p["Struc_Type"], units)
        type_src = f"unit-count rule: {units} unit(s) -> ResStock category (see building_type())"
        if row:
            type_src += (f"; townhouse rule skipped by guard: {per_addr} sq ft floor area per address > "
                         f"{SQFT_MAX[SFD]} (ResStock 2024.2 MI single-family max)")
    # PackedPin identifies accessory structures even when Struc_Type is Residential.
    # City source: OSI/BuildingFootprints/FeatureServer/0 (e.g. Garage, Carport, Canopy).
    accessory = str(p.get("PackedPin") or "").strip().lower() in {"garage", "carport", "canopy", "parking deck"}
    per_unit = building_sqft / max(units, 1)
    if accessory or (p["Struc_Type"] == "Commercial" and btype is not None
                     and not SQFT_MIN[btype] <= per_unit <= SQFT_MAX[btype]):
        btype = None
    if btype is None:
        type_src = f"city use rule: Struc_Type {p['Struc_Type']!r}, PackedPin {p.get('PackedPin')!r}; not a known home"
        warnings.append(type_src + "; General Mailing addresses alone do not establish residential use")
    is_multi = units >= 2

    if btype is None:
        sqft, sqft_src, sqft_est = None, "not a home: no unit sq ft (see building_sqft)", False
    elif unit_sqft:
        sqft, sqft_src, sqft_est = round(unit_sqft), "unit sq ft given by caller (listing or renter)", False
    elif is_multi:
        sqft, sqft_est = round(building_sqft / units), True
        sqft_src = (f"building floor area {building_sqft} sq ft / {units} townhouses (equal split; includes garages)" if btype == SFA else
                    f"building floor area {building_sqft} sq ft / {units} units (includes hallways and common areas)")
        warnings.append("Gross footprint floor area may include garages or unconditioned/common space; "
                        "city geometry does not separate it. Ask for the unit's conditioned sq ft.")
    else:
        sqft, sqft_src, sqft_est = building_sqft, "footprint area (UTM 17N) x stories", False

    if sqft is not None and not SQFT_MIN[btype] <= sqft <= SQFT_MAX[btype]:
        warnings.append(f"in.sqft {sqft} is outside the observed ResStock 2024.2 MI range for {btype} "
                        f"({SQFT_MIN[btype]:,}–{SQFT_MAX[btype]:,} sq ft)")
        if not unit_sqft:
            sqft, sqft_est = TYPICAL_SQFT[btype], True
            sqft_src = (f"ResStock 2024.2 MI {btype} median {sqft} sq ft, "
                        f"replacing implausible {sqft_src}; ask for unit sq ft")

    if year_built:
        year, year_src = int(year_built), "given by caller (listing)"
    else:
        year, year_src = median_year_built(geo["block_geoid"])

    return {
        "in.sqft": sqft,
        "in.geometry_stories": str(stories_cat),
        "in.geometry_building_type_recs": btype,
        "in.vintage": vintage(year) if year else None,
        "in.county_name": COUNTY,
        "stories_raw": stories,
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
            "lat_lon": geo.get("source", "US Census geocoder (Public_AR_Current / Current_Current)"),
            "footprint": f"City of Ann Arbor BuildingFootprints OBJECTID {p['OBJECTID']} "
                         f"(Struc_Type {p['Struc_Type']}), found via {b.match}",
            "in.geometry_stories": f"{stories} stories ({stories_src})"
                                   + (f", snapped to nearest ResStock 2024.2 MI category {stories_cat}"
                                      if stories_cat != stories else ", already a ResStock 2024.2 MI category"),
            "stories_raw": stories_src,
            "in.sqft": sqft_src,
            "building_sqft": "footprint area projected to UTM 17N (EPSG:32617) x stories",
            "est_units": units_src,
            "in.geometry_building_type_recs": type_src,
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

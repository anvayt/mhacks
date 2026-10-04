"""Real blower-door measurements (New York State, NYSERDA), harmonized into one table.

Sources (public, no key; cached under data/raw/nyserda/):
- Residential Statewide Baseline Study (RSBS), Single-Family On-Site Inspections, site level (fielded ~2014–15):
  https://data.ny.gov/d/8wa7-87p5 (641 homes with a completed blower-door test)
- Residential Building Stock Assessment (RBSA) 2018 On-Site Inspections:
  https://data.ny.gov/d/3drn-bhzv (371 sites with a completed blower-door test)

Leakage is reported as CFM50 (airflow at 50 Pa). Target used for modelling: CFM50 per ft² of conditioned floor area
(computable for any Ann Arbor house from footprints). ACH50 = CFM50 × 60 / (floor area × ceiling height) is kept for
reporting. Not public / not used: LBNL ResDB raw records (contact-only), NEEA RBSA (registration, no redistribution).
"""
from __future__ import annotations

import io
import json
import zipfile

import numpy as np
import pandas as pd

from model.data_sources.http import download
from model.paths import RAW

DIR = RAW / "nyserda"
RSBS_URL = "https://data.ny.gov/resource/8wa7-87p5.json?$limit=5000"
RBSA_URL = "https://data.ny.gov/download/3drn-bhzv/application%2Fzip"
RBSA_CSV = "RBSA_On-Site_OpenNY_Dataset_Final/RBSA On-Site OpenNY Dataset Final.csv"

HOME_TYPE = {"Single Family Detached": "detached", "Single Family Attached": "attached_or_2to4",
             "2-4 Unit Bldg": "attached_or_2to4", "Mobile Home": "manufactured", "Modular Home": "manufactured"}


def _num(s):
    return pd.to_numeric(s, errors="coerce")


def load_raw() -> tuple[pd.DataFrame, pd.DataFrame]:
    a = pd.DataFrame(json.loads(download(RSBS_URL, DIR / "rsbs_sf_onsite.json").read_text()))
    z = zipfile.ZipFile(download(RBSA_URL, DIR / "rbsa2018_onsite.zip"))
    r = pd.read_csv(io.BytesIO(z.read(RBSA_CSV)), low_memory=False)
    return a, r


def load() -> tuple[pd.DataFrame, dict]:
    """One row per tested home, harmonized. Returns (table, QC log)."""
    a, r = load_raw()
    A = pd.DataFrame({
        "source": "rsbs2015", "site_id": a.site_id, "region": a.region, "county": a.county,
        "climate_zone": a.climate_zone.str.extract(r"(\d)")[0].astype(float),
        "year_built": _num(a.year_building_built), "area_ft2": _num(a.conditioned_floor_space_measured_in_square_feet),
        "stories": _num(a.number_of_stories_above_grade), "ceiling_ft": _num(a.building_envelope_average_ceiling_height),
        "home_type_raw": a.building_envelope_home_type, "foundation": a.basement_type, "construction": a.construction_type,
        "style": a.style_of_home, "test_done": a.air_duct_blower_door_test_completed,
        "unit": a.building_air_leakage_unit_of_measurement,
        "cfm50": _num(a.building_air_leakage_measured_by_air_duct_blower_door_test),
        "pressure_pa": _num(a.house_pressure_measured_by_air_duct_blower_door), "weight": _num(a.survey_weight)})
    L = "Building Air Leakage Measured by Blower Door Test"
    r = r[r[L].notna()].drop_duplicates("Site ID")
    B = pd.DataFrame({
        "source": "rbsa2018", "site_id": r["Site ID"].astype(str), "region": r["Region"], "county": r["County"],
        "climate_zone": _num(r["Climate Zone"]), "year_built": _num(r["Year Building Built"]),
        "area_ft2": _num(r["Conditioned Floor Space (measured in square feet)"]),
        "stories": _num(r["Number of Stories Above Grade"]), "ceiling_ft": _num(r["Building Envelope Average Ceiling Height"]),
        "home_type_raw": r["Building Envelope Home Type"], "foundation": r["Envelope Foundation Space Type"],
        "construction": r["Construction Type"], "style": r["Style of Home"], "test_done": r["Blower Door Test Completed?"],
        "unit": r["Building Air Leakage Unit of Measurement"], "cfm50": _num(r[L]),
        "pressure_pa": _num(r["House Pressure During Blower Door Test"]), "weight": _num(r["Site Case Weight"])})
    d = pd.concat([A, B], ignore_index=True)
    log = {"raw_rows": {"rsbs2015": int(len(A)), "rbsa2018": int(len(B))}}
    steps = [
        ("blower-door test completed, unit CFM50", (d.test_done == "Yes") & (d.unit == "CFM50") & d.cfm50.notna()),
        ("test at ~50 Pa (|pressure| 45–55)", d.pressure_pa.abs().between(45, 55)),
        ("year built, floor area, stories present", d[["year_built", "area_ft2", "stories"]].notna().all(axis=1)),
        ("floor area 300–8,000 ft²", d.area_ft2.between(300, 8000)),
    ]
    for name, mask in steps:
        before = len(d)
        d = d[mask.reindex(d.index).fillna(False)]
        log[name] = {"kept": int(len(d)), "dropped": int(before - len(d))}
    d = d.copy()
    d["ceiling_ft"] = d.ceiling_ft.where(d.ceiling_ft.between(6, 14))
    d["cfm50_per_ft2"] = d.cfm50 / d.area_ft2
    d["ach50"] = d.cfm50 * 60 / (d.area_ft2 * d.ceiling_ft.fillna(8.0))
    # physically implausible results (data-entry errors): ACH50 outside 0.5–60
    before = len(d)
    d = d[d.ach50.between(0.5, 60)]
    log["ACH50 within 0.5–60"] = {"kept": int(len(d)), "dropped": int(before - len(d))}
    d["home_type"] = d.home_type_raw.map(HOME_TYPE).fillna("other")
    d["y"] = np.log(d.cfm50_per_ft2)
    log["final_by_source"] = d.source.value_counts().to_dict()
    log["final_by_home_type"] = d.home_type.value_counts().to_dict()
    return d.reset_index(drop=True), log

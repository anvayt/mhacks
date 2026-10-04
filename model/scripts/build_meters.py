"""P1-04: Ann Arbor benchmarking → clean building-month meter table.

Findings baked in here (evidence in model/research/heating_cooling.md):
- The published field aliases say kBtu, but monthly `Electricity*` is kWh and `NaturalGas*` is ccf:
  SiteEUI × GFA ≈ 3.412·Σelec + ~104·Σgas (median over 354 gas+electric-only building-years).
- The layer holds 5 blocks of ~419 rows. Blocks 0/1/2 are FilterYear 2021/2022/2023 and match that year's
  weather best. Block 3 is a near-duplicate of block 0. Block 4 is also labelled 2021 but differs and fits
  2022/2024 weather better, so its calendar year is unknown and it is excluded from weather-matched training.

Run: python -m model.scripts.build_meters
"""
import json

import numpy as np
import pandas as pd
from shapely import wkt

from model.data_sources.benchmarking import MONTHS, load_raw
from model.data_sources.footprints import FootprintIndex, envelope_features
from model.paths import PROCESSED, RESULTS

KBTU_PER_KWH = 3.412
KBTU_PER_CCF = 103.7          # EIA US average heat content of natural gas delivered to consumers, ~1,037 Btu/cf
RESIDENTIAL_TYPES = {"Multifamily Housing", "Senior Living Community", "Residence Hall/Dormitory",
                     "Other - Lodging/Residential"}
OTHER_FUELS = ["Propane", "Diesel", "Oil4and5", "Oil4", "Oil2", "Oil1", "Steam", "Hotwater", "Chilledwater", "Kerosene"]


def unit_check(d: pd.DataFrame) -> dict:
    g = d[[f"NaturalGas{m}" for m in MONTHS]].sum(axis=1)
    e = d[[f"Electricity{m}" for m in MONTHS]].sum(axis=1)
    other = sum(d[[f"{f}{m}" for m in MONTHS]].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1) for f in OTHER_FUELS)
    tot = d["SiteEUI"] * d["GrossFloorAreaBuildings"]
    k = (other == 0) & (g > 0) & (e > 0) & (tot > 0)
    r = ((tot - KBTU_PER_KWH * e) / g)[k]
    return {"n_building_years": int(k.sum()), "kbtu_per_gas_unit_median": round(float(r.median()), 1),
            "kbtu_per_gas_unit_iqr": [round(float(r.quantile(.25)), 1), round(float(r.quantile(.75)), 1)],
            "conclusion": "gas unit = ccf (≈103 kBtu), electricity unit = kWh"}


def main():
    raw = load_raw().sort_values("OBJECTID").reset_index(drop=True)
    raw["block"] = np.arange(len(raw)) * 5 // len(raw)
    uc = unit_check(raw[raw.block < 3])
    # property type is blank on some years: carry it over from the same building's other years
    t = raw.replace({"PropertyType": {"": np.nan}}).groupby("AnnArborBenchmarkingID")["PropertyType"].agg(
        lambda s: s.dropna().mode().iloc[0] if s.notna().any() else None)
    raw["ptype"] = raw["AnnArborBenchmarkingID"].map(t)
    d = raw[(raw.block < 3) & raw.ptype.isin(RESIDENTIAL_TYPES)].copy()
    d["year"] = d["block"].map({0: 2021, 1: 2022, 2: 2023})  # a few rows have no FilterYear
    other = sum(d[[f"{f}{m}" for m in MONTHS]].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1) for f in OTHER_FUELS)
    d["has_other_fuel"] = other > 0

    fi = FootprintIndex()
    env = {}
    for bid, grp in d.groupby("AnnArborBenchmarkingID"):
        row = grp.iloc[0]
        env[bid] = envelope_features(fi.within(wkt.loads(row.footprint_wkt))) if isinstance(row.footprint_wkt, str) else {"fp_count": 0}
    env = pd.DataFrame.from_dict(env, orient="index")

    rows = []
    for _, r in d.iterrows():
        for i, m in enumerate(MONTHS, start=1):
            rows.append({"building_id": r.AnnArborBenchmarkingID, "name": r.PropertyName, "address": r.PropertyAddress,
                         "ptype": r.ptype, "year": r.year, "month": i,
                         "gas_ccf": pd.to_numeric(r[f"NaturalGas{m}"], errors="coerce"),
                         "elec_kwh": pd.to_numeric(r[f"Electricity{m}"], errors="coerce"),
                         "gfa_ft2": r.GrossFloorAreaBuildings, "year_built": r.YearBuilt,
                         "site_eui": r.SiteEUI, "energy_star": r.ENERGYSTARScore,
                         "has_other_fuel": r.has_other_fuel, "lat": r.lat, "lon": r.lon})
    m = pd.DataFrame(rows).join(env, on="building_id")
    m = m.drop_duplicates(["building_id", "year", "month"])
    # QC
    m["gas_ok"] = m.gas_ccf.notna() & (m.gas_ccf > 0)
    m["elec_ok"] = m.elec_kwh.notna() & (m.elec_kwh > 0)
    m["gfa_ok"] = m.gfa_ft2.between(5_000, 5_000_000)
    for col in ("gas_ccf", "elec_kwh"):
        ok = m[col] > 0
        inten = (m[col] / m.gfa_ft2).where(ok)
        # flag building-months more than 10× away from that building's median intensity (meter glitches)
        med = inten.groupby([m.building_id, m.year]).transform("median")
        m[f"{col}_outlier"] = ok & ((inten > 10 * med) | (inten < med / 10))
    m.to_parquet(PROCESSED / "meters_monthly.parquet", index=False)

    good_g = m[m.gas_ok & ~m.gas_ccf_outlier & m.gfa_ok].groupby("building_id").size()
    good_e = m[m.elec_ok & ~m.elec_kwh_outlier & m.gfa_ok].groupby("building_id").size()
    summary = {"unit_check": uc, "rows": int(len(m)), "buildings": int(m.building_id.nunique()),
               "buildings_with_10plus_good_gas_months": int((good_g >= 10).sum()),
               "buildings_with_10plus_good_elec_months": int((good_e >= 10).sum()),
               "years": sorted(m.year.unique().tolist()),
               "footprint_join_rate": float((env.get("fp_count", pd.Series(dtype=float)) > 0).mean()),
               "gfa_vs_footprint_estimate_median_ratio": float((m.drop_duplicates("building_id").eval("fp_floor_area_est_ft2 / gfa_ft2")).median())}
    (RESULTS / "meters_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

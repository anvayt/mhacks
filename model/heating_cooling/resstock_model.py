"""P1-07: ResStock heating/cooling model: per-degree-day intensities from 18,756 simulated Michigan homes
(NREL ResStock 2024.2), with optional renter answers.

- Covers every building type: houses, 2–4 unit and 5+ unit buildings. It is the main path for buildings
  under 10,000 ft² (Ann Arbor's meter data only covers properties of 10,000 ft² and up) and a cross-check for large ones.
- Targets per 1,000 ft² of the *unit* per typical-year degree-day at the home's weather station:
  gas heating (ccf/HDD60), electric heating (kWh/HDD60) and cooling (kWh/CDD65).
  Local weather (any season, year or forecast) rescales them through degree-days at the PRISM 800 m cell.
- **Renter answers** (window panes, floor level, foundation, cooling type, occupants: things a renter can know
  before signing) are optional. Training duplicates every home with answers randomly blanked, so one
  XGBoost model (native missing-value handling) accepts any subset of answers. More answers give a more
  specific estimate.
- Degree-days at each of the 31 weather stations use PRISM 800 m normals there, applied to the cached Ann Arbor
  daily shape (zero extra downloads). ResStock simulates TMY3 weather; we normalize by 1991–2020 normals.
- Calibration to real meters: for multifamily, predictions are scaled by
  median(Ann Arbor metered intensity) / median(ResStock 5+ unit intensity) (see results/resstock_hc_validation.json).

Run: python -m model.heating_cooling.resstock_model
"""
from __future__ import annotations

import json
import pickle
import re

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

from model import climate
from model.data_sources import openmeteo, prism
from model.data_sources.resstock import load
from model.heating_cooling.building_model import TAU_C, TAU_H_ELEC, TAU_H_GAS
from model.paths import ARTIFACTS, PROCESSED, RESULTS

KWH_PER_CCF = 103.7 / 3.412          # 1 ccf ≈ 103.7 kBtu (EIA average heat content); 3.412 kBtu per kWh
VINTAGE_YEAR = {"<1940": 1925, "1940s": 1945, "1950s": 1955, "1960s": 1965, "1970s": 1975, "1980s": 1985,
                "1990s": 1995, "2000s": 2005, "2010s": 2015}
BTYPES = ["Single-Family Detached", "Single-Family Attached", "Multi-Family with 2 - 4 Units",
          "Multi-Family with 5+ Units", "Mobile Home"]
MULTIFAMILY = BTYPES[2:4]
ANN_ARBOR = (42.28, -83.74)

PUBLIC = ["sqft", "year_built", "stories", "btype_code", "renter"]
# Answers a renter can actually give before signing (PLAN.md §4 questions). All optional at prediction time.
ANSWERS = {
    "window_panes": "1 (single-pane) or 2 (double-pane); 3 if triple",
    "floor_level": "unit position in a multifamily building: 0 ground/bottom, 1 middle, 2 top",
    "foundation_code": "0 heated basement, 1 unheated basement, 2 slab, 3 crawlspace, 4 open/pier",
    "cooling_code": "0 none, 1 window/room AC, 2 central AC, 3 heat pump",
    "occupants": "number of people",
}
# Envelope details a renter cannot observe (air leakage, insulation R-values, furnace efficiency). They stay out
# of the model's inputs; ResStock samples them from Michigan's housing stock, so they average into the estimate.
# They are used only in model/heating_cooling/leakage_analysis.py to ask whether they could be inferred from bills.
HIDDEN = ["ach50", "wall_r", "ceiling_r", "heating_afue", "low_e"]
FEATURES = PUBLIC + list(ANSWERS)
FOUNDATION = {"Heated Basement": 0, "Unheated Basement": 1, "Slab": 2, "Vented Crawlspace": 3,
              "Unvented Crawlspace": 3, "Ambient": 4}
COOLING = {"None": 0, "Room AC": 1, "Central AC": 2, "Ducted Heat Pump": 3, "Non-Ducted Heat Pump": 3}
LEVEL = {"Bottom": 0, "Middle": 1, "Top": 2}


def _r_value(s: str) -> float:
    if not isinstance(s, str) or s in ("None", "Uninsulated") or "Uninsulated" in s:
        return 0.0
    m = re.search(r"R-(\d+)", s)
    return float(m.group(1)) if m else np.nan


def _afue(s: str) -> float:
    m = re.search(r"([\d.]+)% AFUE", str(s))
    if m:
        return float(m.group(1))
    return 100.0 if "Electric" in str(s) else np.nan


def station_degree_days(lat: float, lon: float) -> dict:
    """Typical-year HDD/CDD at a point: cached Ann Arbor daily shape shifted to the PRISM normals there."""
    hist = openmeteo.daily_archive(*ANN_ARBOR, f"{climate.NORMAL_YEARS[0]}-01-01", f"{climate.NORMAL_YEARS[1]}-12-31").copy()
    clim = hist.groupby(hist.date.dt.month)["tmean_c"].mean()
    offs = np.array([float(prism.sample("tmean", f"norm{m:02d}", lat, lon)[0]) - clim[m] for m in range(1, 13)])
    hist["tmean_c"] = hist["tmean_c"].to_numpy() + offs[hist.date.dt.month.to_numpy() - 1]
    cols = [f"hdd{TAU_H_GAS}", f"hdd{TAU_H_ELEC}", f"cdd{TAU_C}"]
    return climate._monthly(hist).groupby("year")[cols].sum().mean().to_dict()


def frame() -> pd.DataFrame:
    d = load()
    st = d[["in.weather_file_latitude", "in.weather_file_longitude"]].drop_duplicates().astype(float)
    dd = {(r[0], r[1]): station_degree_days(r[0], r[1]) for r in st.itertuples(index=False)}
    key = list(zip(d["in.weather_file_latitude"].astype(float), d["in.weather_file_longitude"].astype(float)))
    win = d["in.windows"].astype(str)
    out = pd.DataFrame({
        "sqft": pd.to_numeric(d["in.sqft"], errors="coerce"),
        "year_built": d["in.vintage"].map(VINTAGE_YEAR).astype(float),
        "stories": pd.to_numeric(d["in.geometry_stories"], errors="coerce"),
        "btype": d["in.geometry_building_type_recs"].astype(str),
        "renter": (d["in.tenure"].astype(str) == "Renter").astype(float),
        "window_panes": win.str.extract(r"^(Single|Double|Triple)")[0].map({"Single": 1, "Double": 2, "Triple": 3}).astype(float),
        "low_e": win.str.contains("Low-E").astype(float),
        "ach50": pd.to_numeric(d["in.infiltration"].astype(str).str.extract(r"([\d.]+)")[0], errors="coerce"),
        "wall_r": d["in.insulation_wall"].astype(str).map(_r_value),
        "ceiling_r": d["in.insulation_ceiling"].astype(str).map(_r_value),
        "floor_level": d["in.geometry_building_level_mf"].astype(str).map(LEVEL).astype(float),
        "foundation_code": d["in.geometry_foundation_type"].astype(str).map(FOUNDATION).astype(float),
        "cooling_code": d["in.hvac_cooling_type"].astype(str).map(COOLING).astype(float),
        "heating_afue": d["in.hvac_heating_efficiency"].astype(str).map(_afue),
        "occupants": pd.to_numeric(d["in.occupants"], errors="coerce"),
        "heating_fuel": d["in.heating_fuel"].astype(str),
        "hdd_gas": [dd[k][f"hdd{TAU_H_GAS}"] for k in key], "hdd_elec": [dd[k][f"hdd{TAU_H_ELEC}"] for k in key],
        "cdd": [dd[k][f"cdd{TAU_C}"] for k in key],
        "gas_heat_kwh": d["out.natural_gas.heating.energy_consumption.kwh"].astype(float),
        "elec_heat_kwh": sum(d[c].astype(float) for c in d.columns if c.startswith("out.electricity.heating")
                             and c.endswith("energy_consumption.kwh")),
        "cool_kwh": d["out.electricity.cooling.energy_consumption.kwh"].astype(float),
        "weather_city": d["in.weather_file_city"].astype(str),
        "county": d["in.county_name"].astype(str),
    })
    out["btype_code"] = out["btype"].map({b: i for i, b in enumerate(BTYPES)}).astype(float)
    k = 1000 / out.sqft
    out["heat_gas_per_hdd"] = out.gas_heat_kwh / KWH_PER_CCF * k / out.hdd_gas   # ccf / 1000 ft² / HDD60
    out["heat_elec_per_hdd"] = out.elec_heat_kwh * k / out.hdd_elec              # kWh / 1000 ft² / HDD55
    out["cool_per_cdd"] = out.cool_kwh * k / out.cdd                              # kWh / 1000 ft² / CDD65
    return out


def augment(df: pd.DataFrame, copies: int = 3, p_missing: float = 0.5, seed: int = 0) -> pd.DataFrame:
    """Original rows + `copies` versions with each renter answer independently blanked with p_missing,
    plus one copy with every answer blanked (public-record-only lookups)."""
    rng = np.random.default_rng(seed)
    parts = [df]
    for _ in range(copies):
        c = df.copy()
        for a in ANSWERS:
            c.loc[rng.random(len(c)) < p_missing, a] = np.nan
        parts.append(c)
    blank = df.copy()
    blank[list(ANSWERS)] = np.nan
    parts.append(blank)
    return pd.concat(parts, ignore_index=True)


def fit_one(df: pd.DataFrame, target: str) -> tuple[XGBRegressor, dict]:
    tr, te = train_test_split(df, test_size=0.2, random_state=0)
    tr_aug = augment(tr)
    mdl = XGBRegressor(n_estimators=700, learning_rate=0.04, max_depth=6, subsample=0.8, colsample_bytree=0.8,
                       min_child_weight=5, random_state=0, n_jobs=-1)
    mdl.fit(tr_aug[FEATURES], np.log(tr_aug[target]))
    metrics = {"n": int(len(df))}
    yte = np.log(te[target])
    for label, X in (("public_record_only", te[FEATURES].assign(**{a: np.nan for a in ANSWERS})),
                     ("all_answers", te[FEATURES])):
        p = mdl.predict(X)
        ape = np.abs(np.exp(p - yte) - 1)
        metrics[label] = {"test_median_ape": round(float(np.median(ape)), 3),
                          "test_r2_log": round(float(1 - np.mean((p - yte) ** 2) / np.var(yte)), 3)}
    # refit on everything for serving
    full = augment(df)
    mdl.fit(full[FEATURES], np.log(full[target]))
    imp = dict(sorted(zip(FEATURES, mdl.feature_importances_.round(3).tolist()), key=lambda kv: -kv[1]))
    metrics["feature_importance"] = imp
    return mdl, metrics


def main():
    f = frame()
    f.to_parquet(PROCESSED / "resstock_frame.parquet", index=False)
    sets = {
        "heat_gas_per_hdd": f[(f.heating_fuel == "Natural Gas") & (f.heat_gas_per_hdd > 0)],
        "heat_elec_per_hdd": f[(f.heating_fuel == "Electricity") & (f.heat_elec_per_hdd > 0)],
        "cool_per_cdd": f[(f.cooling_code > 0) & (f.cool_per_cdd > 0)],
    }
    models, metrics = {}, {}
    for target, df in sets.items():
        df = df.dropna(subset=PUBLIC)
        models[target], metrics[target] = fit_one(df, target)
        print(target, json.dumps({k: v for k, v in metrics[target].items() if k != "feature_importance"}))

    # calibration against real Ann Arbor meters, multifamily (the overlap between the two datasets)
    t = pd.read_parquet(PROCESSED / "building_targets.parquet")
    real_h = (t.heat_int / t.hdd_ref)[(t.gas_r2 >= 0.7) & (t.heat_int > 0)]
    real_c = (t.cool_int / t.cdd_ref)[(t.elec_r2 >= 0.3) & (t.cool_int > 0)]
    mf5 = lambda df: df[df.btype == "Multi-Family with 5+ Units"]
    sim_h, sim_c = mf5(sets["heat_gas_per_hdd"]).heat_gas_per_hdd, mf5(sets["cool_per_cdd"]).cool_per_cdd
    calib = {"heat_gas": round(float(real_h.median() / sim_h.median()), 3),
             "cool": round(float(real_c.median() / sim_c.median()), 3),
             "heat_elec": 1.0,  # too few all-electric metered buildings (n=8) to calibrate
             "evidence": {"metered_median_heat_ccf_per_1000ft2_per_hdd60": round(float(real_h.median()), 4),
                          "resstock_mf5_median_heat": round(float(sim_h.median()), 4),
                          "metered_median_cool_kwh_per_1000ft2_per_cdd65": round(float(real_c.median()), 3),
                          "resstock_mf5_median_cool": round(float(sim_c.median()), 3),
                          "n_metered_heat": int(len(real_h)), "n_metered_cool": int(len(real_c))},
             "applies_to": MULTIFAMILY}
    with open(ARTIFACTS / "resstock_hc.pkl", "wb") as fh:
        pickle.dump({"models": models, "features": FEATURES, "answers": ANSWERS, "btypes": BTYPES,
                     "calibration": calib}, fh)
    out = {"source": "NREL ResStock 2024.2 MI baseline (18,756 simulated homes)", "targets": metrics,
           "calibration_to_meters": calib, "weather_stations": int(f.weather_city.nunique()),
           "mf5_median_unit_sqft": float(mf5(f).sqft.median()),
           "answers": ANSWERS}
    (RESULTS / "resstock_hc_validation.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

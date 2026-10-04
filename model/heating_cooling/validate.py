"""Grounding checks against real, independent data.

1. Weather: our localized typical-year degree-days vs NOAA's official 1991–2020 station normals
   (NCEI, https://www.ncei.noaa.gov/access/services/data/v1?dataset=normals-annualseasonal-1991-2020) at the
   two Ann Arbor stations, using each station's own coordinates.
2. Energy, per season, held out on real Ann Arbor meters: predicted vs metered gas for every building-year-season
   (winter = Jan+Feb+Dec of the same calendar year), for each estimate path:
   - metered:      the building's own change-point fit from its *other* years (out-of-year)
   - meter_model:  building-level regression, 5-fold CV by building (the building never seen)
   - resstock:     ResStock 5+ unit multifamily model, calibrated to meters (no building-specific info)
   - blend:        weighted geometric mean of meter_model and resstock, weight chosen on training buildings
   - null:         the median metered intensity (training buildings) for every building
   The three non-metered paths add the median metered non-heating gas (hot water, cooking) per ft²·day.

Run: python -m model.heating_cooling.validate → results/validation_real.json
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold

from model import climate
from model.data_sources.http import get_json
from model.heating_cooling import changepoint
from model.data_sources.eia import price_table
from model.heating_cooling.building_model import TAU_C, TAU_H_GAS
from model.heating_cooling.features import BUILDING, building_features
from model.heating_cooling.service import DEFAULT_UNIT_SQFT_MF, _intensity_resstock
from model.paths import PROCESSED, RESULTS

NOAA = "https://www.ncei.noaa.gov/access/services/data/v1"
STATIONS = {"USC00200230": ("ANN ARBOR U OF MICH", 42.2981, -83.6639),
            "USW00094889": ("ANN ARBOR MUNI AP", 42.2228, -83.7444)}
TYPES = "ANN-HTDD-NORMAL,ANN-CLDD-NORMAL,DJF-HTDD-NORMAL,MAM-HTDD-NORMAL,SON-HTDD-NORMAL,JJA-CLDD-NORMAL,ANN-TAVG-NORMAL"


def weather_check() -> dict:
    out = {}
    for sid, (name, lat, lon) in STATIONS.items():
        js = get_json(NOAA, {"dataset": "normals-annualseasonal-1991-2020", "stations": sid, "format": "json",
                             "dataTypes": TYPES}, namespace="noaa")[0]
        noaa = {k: float(v) for k, v in js.items() if k != "STATION"}
        s = climate.seasonal(climate.monthly_weather_normal(lat, lon)).set_index("season")
        ours = {"ANN-HTDD-NORMAL": s.hdd65.sum(), "ANN-CLDD-NORMAL": s.cdd65.sum(),
                "DJF-HTDD-NORMAL": s.loc["winter", "hdd65"], "MAM-HTDD-NORMAL": s.loc["spring", "hdd65"],
                "SON-HTDD-NORMAL": s.loc["fall", "hdd65"], "JJA-CLDD-NORMAL": s.loc["summer", "cdd65"],
                "ANN-TAVG-NORMAL": float(climate.c_to_f(np.average(s.tmean_c, weights=s.days)))}
        out[sid] = {"name": name, "lat": lat, "lon": lon,
                    "compare": {k: {"noaa": noaa.get(k), "ours": round(float(v), 1),
                                    "pct_diff": round(float(v / noaa[k] - 1), 3) if noaa.get(k) else None}
                                for k, v in ours.items()}}
    return out


PATHS = ("metered", "meter_model", "resstock", "blend", "null")
FOLD_LOG: dict = {}   # per-fold calibration / blend weight / null, for the report
MONTHLY_SUMMARY: dict = {}
MONTH_ROWS: list = []  # held-out building-month rows (same predictions as the seasonal rows, not aggregated)
SERVE: dict = {}      # blend weights + calibration the service uses
FUEL = {
    # fuel: (meter column, ok flag, outlier flag, CP heating?, CP cooling?, driver column, building-model target,
    #        building target column, base column, ResStock intensity key, unit)
    "gas": ("gas_ccf", "gas_ok", "gas_ccf_outlier", True, False, f"hdd{TAU_H_GAS}", "heat_gas", "heat_int",
            "gas_base_ccf", "heat_ccf_per_hdd", "ccf"),
    "elec": ("elec_kwh", "elec_ok", "elec_kwh_outlier", True, True, f"cdd{TAU_C}", "cool_elec", "cool_int",
             "elec_base_kwh", "cool_kwh_per_cdd", "kWh"),
}


def heldout_rows(fuel: str) -> pd.DataFrame:
    """Building-month predictions for data the model never saw, aggregated to building-year-season.

    gas : all of a season's gas = base (hot water, cooking) + heating
    elec: all of a season's electricity = base (lights, plugs) + cooling (gas-heated buildings only, so electric
          heating doesn't mix in)
    Paths: metered = the building's own change-point fit on its *other* years; meter_model = building-level
    model, 5-fold CV over buildings (building never seen); resstock = calibrated ResStock (never saw these
    buildings); blend = geometric mean of the two; null = median intensity of all metered buildings. The
    unmetered paths use the median metered base load per ft².
    """
    col, ok, outl, cp_h, cp_c, drv, bm_name, tcol, bcol, rs_key, _ = FUEL[fuel]
    m = pd.read_parquet(PROCESSED / "meters_weather.parquet")
    t = pd.read_parquet(PROCESSED / "building_targets.parquet").set_index("building_id")
    r2col, thr = ("gas_r2", 0.7) if fuel == "gas" else ("elec_r2", 0.3)
    t = t[(t[r2col] >= thr) & (t[tcol] > 0)].dropna(subset=["year_built", "surface_to_volume", "height_ft_max"])
    if fuel == "elec":
        t = t[~t.electric_heat.astype(bool)]
    ref = t.hdd_ref if fuel == "gas" else t.cdd_ref
    g = m[m[ok] & ~m[outl] & m.building_id.isin(t.index)].copy()
    base_pd = float((t[bcol] / t.gfa_ft2 * 1000 / 365).median())   # per 1,000 ft² per day

    # Everything an unmetered prediction depends on is computed from TRAINING buildings only (no leakage):
    #  - meter_model: out-of-fold predictions from the nested CV in building_model.py (tuned in inner folds,
    #    averaged over the 5 outer repeats; each building is always predicted by models that never saw it)
    #  - ResStock calibration factor, the null (median) intensity, the base-load median and the blend weight are
    #    re-estimated inside each outer fold below from the training buildings.
    bmv = json.loads((RESULTS / "building_model_validation.json").read_text())["targets"][bm_name]
    oof = pd.read_parquet(RESULTS / f"oof_{bm_name}.parquet").set_index("building_id")
    chosen = bmv["chosen"]
    real_int = (t[tcol] / ref)                                   # per 1,000 ft² per degree-day, from the meters
    mm_all = np.exp(oof.loc[t.index, f"oof_{chosen}"]) / ref     # same units
    rsv = json.loads((RESULTS / "resstock_hc_validation.json").read_text())
    rs_cal_all = rsv["calibration_to_meters"]["heat_gas" if fuel == "gas" else "cool"]
    sim_med = rsv["calibration_to_meters"]["evidence"]["resstock_mf5_median_heat" if fuel == "gas" else "resstock_mf5_median_cool"]
    rs_raw = pd.Series({bid: _intensity_resstock({"unit_sqft": DEFAULT_UNIT_SQFT_MF, "year_built": b.year_built,
                                                  "stories_max": b.stories_max}, "Multi-Family with 5+ Units", {})[rs_key] / rs_cal_all
                        for bid, b in t.iterrows()})
    base_all = t[bcol] / t.gfa_ft2 * 1000 / 365
    W = np.linspace(0, 1, 11)                                     # weight on the meter model in log space
    mm_int, rs_int, null_int, blend_int, base_pd, folds = {}, {}, {}, {}, {}, []
    ids = np.array(t.index)
    for k_, (tr, te) in enumerate(KFold(5, shuffle=True, random_state=0).split(ids)):
        trn, tst = ids[tr], ids[te]
        cal = float(real_int[trn].median() / sim_med)
        rs_tr = rs_raw[trn] * cal
        errs = [np.median(np.abs(np.exp(w * np.log(mm_all[trn]) + (1 - w) * np.log(rs_tr)) / real_int[trn] - 1)) for w in W]
        w = float(W[int(np.argmin(errs))])
        nul = float(real_int[trn].median())
        bpd = float(base_all[trn].median())
        folds.append({"fold": k_, "n_train": int(len(trn)), "n_test": int(len(tst)), "resstock_calibration": round(cal, 3),
                      "blend_weight_meter_model": w, "null_intensity": nul, "base_per_1000ft2_day": bpd})
        for bid in tst:
            mm_int[bid] = float(mm_all[bid]); rs_int[bid] = float(rs_raw[bid] * cal); null_int[bid] = nul; base_pd[bid] = bpd
            blend_int[bid] = float(np.exp(w * np.log(mm_all[bid]) + (1 - w) * np.log(rs_raw[bid] * cal)))
    FOLD_LOG[fuel] = folds
    # serving weights: same rule on all buildings (uses the out-of-fold meter-model predictions)
    cal_full = float(real_int.median() / sim_med)
    errs = [np.median(np.abs(np.exp(w * np.log(mm_all) + (1 - w) * np.log(rs_raw * cal_full)) / real_int - 1)) for w in W]
    SERVE[fuel] = {"blend_weight_meter_model": float(W[int(np.argmin(errs))]), "resstock_calibration": cal_full,
                   "meter_model_family": chosen,
                   "rule": "weight w on log(meter model) and 1−w on log(calibrated ResStock), chosen on out-of-fold predictions to minimize median abs % error"}
    prices = price_table()
    price = {m_: (prices["gas_usd_per_ccf"]["marginal"] if fuel == "gas" else prices["elec_usd_per_kwh"]["average"])[str(m_)]
             for m_ in range(1, 13)}

    rows = []
    for bid, gb in g.groupby("building_id"):
        gfa = t.loc[bid, "gfa_ft2"]
        k = gfa / 1000
        for yr, gy in gb.groupby("year"):
            other = gb[gb.year != yr]
            f = changepoint.fit(other, col, heating=cp_h, cooling=cp_c) if len(other) >= 9 else None
            pm = gy[["month", "days", drv, col]].copy()
            base = base_pd[bid] * pm.days * k
            pm["meter_model"] = mm_int[bid] * pm[drv] * k + base
            pm["resstock"] = rs_int[bid] * pm[drv] * k + base
            pm["null"] = null_int[bid] * pm[drv] * k + base
            pm["blend"] = blend_int[bid] * pm[drv] * k + base
            pm["metered"] = f.predict(gy)["total"].to_numpy() if (f is not None and f.r2 >= thr) else np.nan
            pm["price"] = pm.month.map(price)
            pm["season"] = pm.month.map(climate.MONTH_TO_SEASON)
            for _, mr in pm.iterrows():   # monthly rows: the same held-out predictions, before any aggregation
                mrow = {"fuel": fuel, "building_id": bid, "name": gb.name.iloc[0], "year": int(yr), "month": int(mr.month),
                        "actual": float(mr[col])}
                for p_ in PATHS:
                    mrow[p_] = float(mr[p_]) if pd.notna(mr[p_]) else np.nan
                MONTH_ROWS.append(mrow)
            for season, gs in pm.groupby("season"):
                if len(gs) < 3:
                    continue
                # energy only: there is no cost data for these buildings, so nothing is reported in dollars
                r = {"fuel": fuel, "building_id": bid, "name": gb.name.iloc[0], "year": int(yr), "season": season,
                     "gfa_ft2": float(gfa), "actual": float(gs[col].sum())}
                for p_ in PATHS:
                    r[p_] = float(gs[p_].sum()) if gs[p_].notna().all() else np.nan
                rows.append(r)
    return pd.DataFrame(rows)


def summarize(d: pd.DataFrame) -> dict:
    out = {"n_building_season_years": int(len(d)), "n_buildings": int(d.building_id.nunique()), "median_abs_pct_error": {}}
    for path in PATHS:
        e = (d[path] / d.actual - 1).abs()
        out["median_abs_pct_error"][path] = {
            "all": round(float(e.median()), 3),
            **{s: round(float(e[d.season == s].median()), 3) for s in climate.SEASONS}}
    out["p90_abs_pct_error_winter"] = {p: round(float((d[p] / d.actual - 1).abs()[d.season == "winter"].quantile(.9)), 3) for p in PATHS}
    out["p90_abs_pct_error_summer"] = {p: round(float((d[p] / d.actual - 1).abs()[d.season == "summer"].quantile(.9)), 3) for p in PATHS}
    # bias: does any path systematically over/under-predict?
    out["median_signed_error"] = {p: round(float((d[p] / d.actual - 1).median()), 3) for p in PATHS}
    out["r2_log"] = {p: round(float(1 - np.nanmean((np.log(d[p]) - np.log(d.actual)) ** 2) / np.var(np.log(d.actual))), 3) for p in PATHS}
    return out


def summarize_monthly(d: pd.DataFrame) -> dict:
    """Per calendar month and path: median / p90 absolute % error, median signed error (bias), n."""
    out = {}
    for path in PATHS:
        e = d[path] / d.actual - 1
        ok = e.notna() & np.isfinite(e)
        per = {}
        for m in range(1, 13):
            k = ok & (d.month == m)
            if k.sum() < 10:
                continue
            per[m] = {"median_abs_pct_error": round(float(e[k].abs().median()), 3),
                      "p90_abs_pct_error": round(float(e[k].abs().quantile(.9)), 3),
                      "median_signed_error": round(float(e[k].median()), 3), "n": int(k.sum())}
        out[path] = {"all_months": round(float(e[ok].abs().median()), 3), "by_month": per}
    return out


def seasonal_check() -> tuple[dict, dict]:
    MONTH_ROWS.clear()
    gas, elec = heldout_rows("gas"), heldout_rows("elec")
    pd.concat([gas, elec], ignore_index=True).to_parquet(RESULTS / "heldout_seasonal.parquet", index=False)
    mon = pd.DataFrame(MONTH_ROWS)
    mon = mon[mon.actual > 0]
    mon.to_parquet(RESULTS / "heldout_monthly.parquet", index=False)
    MONTHLY_SUMMARY["gas"] = summarize_monthly(mon[mon.fuel == "gas"])
    MONTHLY_SUMMARY["elec"] = summarize_monthly(mon[mon.fuel == "elec"])
    return summarize(gas), summarize(elec)


def main():
    gas, elec = seasonal_check()
    out = {"weather_vs_noaa_normals": weather_check(), "seasonal_gas_vs_real_meters": gas,
           "seasonal_elec_vs_real_meters": elec,
           "monthly_gas_vs_real_meters": MONTHLY_SUMMARY["gas"], "monthly_elec_vs_real_meters": MONTHLY_SUMMARY["elec"],
           "in_fold_parameters": FOLD_LOG, "serving_blend": SERVE,
           "scheme": "Unmetered paths: 5-fold split over buildings; ResStock calibration, null intensity, base load and "
                     "blend weight are estimated on the training buildings of each fold; meter-model predictions are the "
                     "nested-CV out-of-fold predictions. Metered path: the building's own change-point fit on its other years."}
    (RESULTS / "blend_weights.json").write_text(json.dumps(SERVE, indent=2))
    (RESULTS / "validation_real.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

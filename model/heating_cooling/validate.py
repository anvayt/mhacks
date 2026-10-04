"""Grounding checks against real, independent data.

1. Weather: our localized typical-year degree-days vs NOAA's official 1991–2020 station normals
   (NCEI, https://www.ncei.noaa.gov/access/services/data/v1?dataset=normals-annualseasonal-1991-2020) at the
   two Ann Arbor stations, using each station's own coordinates.
2. Energy, per season, held out on real Ann Arbor meters: predicted vs metered gas for every building-year-season
   (winter = Jan+Feb+Dec of the same calendar year), for each estimate path:
   - metered:      the building's own change-point fit from its *other* years (out-of-year)
   - meter_model:  building-level regression, 5-fold CV by building (the building never seen)
   - resstock:     ResStock 5+ unit multifamily model, calibrated to meters (no building-specific info)
   - blend:        geometric mean of meter_model and resstock intensities
   - null:         the median metered heating slope for every building
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
from model.heating_cooling.building_model import TAU_C, TAU_H_GAS, zoo
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

    chosen = json.loads((RESULTS / "building_model_validation.json").read_text())["targets"][bm_name]["chosen"]
    X = building_features(t.reset_index())[BUILDING]
    y = np.log(t[tcol].to_numpy())
    mm = np.zeros(len(t))
    for tr, te in KFold(5, shuffle=True, random_state=0).split(X):
        mdl = zoo()[chosen].fit(X.iloc[tr], y[tr])
        mm[te] = np.exp(mdl.predict(X.iloc[te]))
    mm_int = pd.Series(mm / ref.to_numpy(), index=t.index)
    null_int = float((t[tcol] / ref).median())
    rs_int = {bid: _intensity_resstock({"unit_sqft": DEFAULT_UNIT_SQFT_MF, "year_built": b.year_built,
                                        "stories_max": b.stories_max}, "Multi-Family with 5+ Units", {})[rs_key]
              for bid, b in t.iterrows()}
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
            base = base_pd * pm.days * k
            pm["meter_model"] = mm_int[bid] * pm[drv] * k + base
            pm["resstock"] = rs_int[bid] * pm[drv] * k + base
            pm["null"] = null_int * pm[drv] * k + base
            pm["blend"] = np.sqrt(mm_int[bid] * rs_int[bid]) * pm[drv] * k + base
            pm["metered"] = f.predict(gy)["total"].to_numpy() if (f is not None and f.r2 >= thr) else np.nan
            pm["price"] = pm.month.map(price)
            pm["season"] = pm.month.map(climate.MONTH_TO_SEASON)
            for season, gs in pm.groupby("season"):
                if len(gs) < 3:
                    continue
                r = {"fuel": fuel, "building_id": bid, "name": gb.name.iloc[0], "year": int(yr), "season": season,
                     "gfa_ft2": float(gfa), "actual": float(gs[col].sum()), "actual_usd": float((gs[col] * gs.price).sum())}
                for p_ in PATHS:
                    r[p_] = float(gs[p_].sum()) if gs[p_].notna().all() else np.nan
                    r[f"{p_}_usd"] = float((gs[p_] * gs.price).sum()) if gs[p_].notna().all() else np.nan
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


def seasonal_check() -> tuple[dict, dict]:
    gas, elec = heldout_rows("gas"), heldout_rows("elec")
    pd.concat([gas, elec], ignore_index=True).to_parquet(RESULTS / "heldout_seasonal.parquet", index=False)
    return summarize(gas), summarize(elec)


def main():
    gas, elec = seasonal_check()
    out = {"weather_vs_noaa_normals": weather_check(), "seasonal_gas_vs_real_meters": gas,
           "seasonal_elec_vs_real_meters": elec}
    (RESULTS / "validation_real.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

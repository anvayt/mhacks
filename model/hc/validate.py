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

Run: python -m model.hc.validate → results/validation_real.json
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold

from model import climate
from model.data_sources.http import get_json
from model.hc import changepoint
from model.hc.building_model import TAU_H_GAS, zoo
from model.hc.features import BUILDING, building_features
from model.hc.service import DEFAULT_UNIT_SQFT_MF, _intensity_resstock
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


def seasonal_check() -> dict:
    m = pd.read_parquet(PROCESSED / "meters_weather.parquet")
    t = pd.read_parquet(PROCESSED / "building_targets.parquet").set_index("building_id")
    t = t[(t.gas_r2 >= 0.7) & (t.heat_int > 0)].dropna(subset=["year_built", "surface_to_volume", "height_ft_max"])
    g = m[m.gas_ok & ~m.gas_ccf_outlier & m.building_id.isin(t.index)].copy()
    g["season"] = g.month.map(climate.MONTH_TO_SEASON)
    base_pd = float((t.gas_base_ccf / t.gfa_ft2 * 1000 / 365).median())  # ccf / 1000 ft² / day

    # meter_model: CV predictions of heating per HDD (per 1,000 ft²), building never seen in training
    X = building_features(t.reset_index())[BUILDING]
    y = np.log(t.heat_int.to_numpy())
    mm = np.zeros(len(t))
    for tr, te in KFold(5, shuffle=True, random_state=0).split(X):
        mdl = zoo()["mlr"].fit(X.iloc[tr], y[tr])
        mm[te] = np.exp(mdl.predict(X.iloc[te]))
    mm_per_hdd = pd.Series(mm / t.hdd_ref.to_numpy(), index=t.index)
    null_per_hdd = float((t.heat_int / t.hdd_ref).median())
    # resstock: one MF5+ prediction per building (public-record features only)
    rs_per_hdd = {}
    for bid, b in t.iterrows():
        feat = {"unit_sqft": DEFAULT_UNIT_SQFT_MF, "year_built": b.year_built, "stories_max": b.stories_max}
        rs_per_hdd[bid] = _intensity_resstock(feat, "Multi-Family with 5+ Units", {})["heat_ccf_per_hdd"]

    rows = []
    for bid, gb in g.groupby("building_id"):
        gfa = t.loc[bid, "gfa_ft2"]
        for yr, gy in gb.groupby("year"):
            other = gb[gb.year != yr]
            f = changepoint.fit(other, "gas_ccf", heating=True, cooling=False) if len(other) >= 9 else None
            for season, gs in gy.groupby("season"):
                if len(gs) < 3:
                    continue
                actual = gs.gas_ccf.sum()
                hdd = gs[f"hdd{TAU_H_GAS}"].sum()
                days = gs.days.sum()
                base = base_pd * days * gfa / 1000
                r = {"building_id": bid, "year": yr, "season": season, "actual": actual,
                     "meter_model": mm_per_hdd[bid] * hdd * gfa / 1000 + base,
                     "resstock": rs_per_hdd[bid] * hdd * gfa / 1000 + base,
                     "null": null_per_hdd * hdd * gfa / 1000 + base,
                     # geometric mean of the two no-meter intensities
                     "blend": np.sqrt(mm_per_hdd[bid] * rs_per_hdd[bid]) * hdd * gfa / 1000 + base}
                if f is not None and f.r2 >= 0.7:
                    r["metered"] = f.predict(gs)["total"].sum()
                rows.append(r)
    d = pd.DataFrame(rows)
    out = {"n_building_season_years": int(len(d)), "n_buildings": int(d.building_id.nunique()), "median_abs_pct_error": {}}
    for path in ("metered", "meter_model", "resstock", "blend", "null"):
        e = (d[path] / d.actual - 1).abs()
        out["median_abs_pct_error"][path] = {
            "all": round(float(e.median()), 3),
            **{s: round(float(e[d.season == s].median()), 3) for s in climate.SEASONS}}
    out["p90_abs_pct_error_winter"] = {p: round(float((d[p] / d.actual - 1).abs()[d.season == "winter"].quantile(.9)), 3)
                                       for p in ("metered", "meter_model", "resstock", "blend", "null")}
    # bias: does any path systematically over/under-predict?
    out["median_signed_error"] = {p: round(float((d[p] / d.actual - 1).median()), 3) for p in ("metered", "meter_model", "resstock", "blend", "null")}
    return out


def main():
    out = {"weather_vs_noaa_normals": weather_check(), "seasonal_gas_vs_real_meters": seasonal_check()}
    (RESULTS / "validation_real.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

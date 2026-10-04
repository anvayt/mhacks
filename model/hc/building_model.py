"""P1-05 (stage 2): building-level heating/cooling intensity models trained on real meters.

Why building-level: in the PRISM model, weather enters linearly (energy = slope × degree-days), so the part
that differs between buildings is the *slope*. We therefore learn, per building:
    heat_int = βh · HDD_normal(τh) / GFA × 1000      [ccf per 1,000 ft² per typical year]   (gas heating)
    cool_int = βc · CDD_normal(τc) / GFA × 1000      [kWh per 1,000 ft² per typical year]   (electric cooling)
    eheat_int (electric heating, only for buildings with no gas heating)
and predict it from footprint/public-record features. Local weather (any season, year or forecast) then
rescales it through degree-days at the building's own 800 m PRISM cell.

Models compared with repeated 5-fold CV (one row per building, so no leakage): null (median), multiple linear
regression, random forest, XGBoost. Targets are modelled in log space (they are right-skewed).

Run: python -m model.hc.building_model
"""
from __future__ import annotations

import json
import pickle

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import RepeatedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from model import climate
from model.hc.features import BUILDING, building_features
from model.hc.train import building_table, cp_object
from model.paths import ARTIFACTS, PROCESSED, RESULTS

# pooled balance points used to rescale predicted intensities by local weather (medians of the per-building fits)
TAU_H_GAS = 60
TAU_H_ELEC = 55
TAU_C = 65


def normal_weather_cache(b: pd.DataFrame) -> dict:
    path = PROCESSED / "normal_weather_buildings.parquet"
    if path.exists():
        w = pd.read_parquet(path)
        if set(b.building_id) <= set(w.building_id):
            return {k: g.drop(columns="building_id").reset_index(drop=True) for k, g in w.groupby("building_id")}
    frames = []
    for _, r in b.iterrows():
        frames.append(climate.monthly_weather_normal(r.lat, r.lon).assign(building_id=r.building_id))
    w = pd.concat(frames, ignore_index=True)
    w.to_parquet(path, index=False)
    return {k: g.drop(columns="building_id").reset_index(drop=True) for k, g in w.groupby("building_id")}


def targets() -> pd.DataFrame:
    m = pd.read_parquet(PROCESSED / "meters_weather.parquet")
    cps = pd.read_parquet(PROCESSED / "changepoints.parquet").set_index("building_id")
    b = building_table(m)
    nw = normal_weather_cache(b)
    rows = []
    for _, r in b.iterrows():
        w = nw[r.building_id]
        out = {"building_id": r.building_id}
        if r.building_id in cps.index:
            row = cps.loc[r.building_id]
            fg, fe = cp_object(row, "gas"), cp_object(row, "elec")
            if fg is not None:
                p = fg.predict(w)
                out.update(gas_r2=fg.r2, heat_ccf=p.heating.sum(), gas_base_ccf=p.base.sum())
            if fe is not None:
                p = fe.predict(w)
                out.update(elec_r2=fe.r2, cool_kwh=p.cooling.sum(), eheat_kwh=p.heating.sum(), elec_base_kwh=p.base.sum())
        rows.append(out)
    t = b.merge(pd.DataFrame(rows), on="building_id", how="left")
    k = 1000 / t.gfa_ft2
    t["heat_int"] = t.heat_ccf * k
    t["cool_int"] = t.cool_kwh * k
    # electric resistance / heat-pump heating: only where the building has no meaningful gas heating
    t["electric_heat"] = t.heat_ccf.isna() | (t.heat_int < 5)
    t["eheat_int"] = np.where(t.electric_heat, t.eheat_kwh * k, np.nan)
    t["hdd_ref"] = [nw[i][f"hdd{TAU_H_GAS}"].sum() for i in t.building_id]
    t["cdd_ref"] = [nw[i][f"cdd{TAU_C}"].sum() for i in t.building_id]
    t.to_parquet(PROCESSED / "building_targets.parquet", index=False)
    return t


def zoo() -> dict:
    return {
        "null_median": DummyRegressor(strategy="median"),
        "mlr": make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-2, 3, 20))),
        "random_forest": RandomForestRegressor(n_estimators=500, min_samples_leaf=4, max_features=0.6, random_state=0, n_jobs=-1),
        "xgboost": XGBRegressor(n_estimators=300, learning_rate=0.03, max_depth=2, subsample=0.8,
                                colsample_bytree=0.8, min_child_weight=4, reg_lambda=5.0, random_state=0),
    }


def cv_compare(X: pd.DataFrame, y: pd.Series) -> tuple[dict, dict]:
    """Repeated 5-fold CV on log(y). Metrics on the original scale."""
    ly = np.log(y)
    preds = {k: [] for k in zoo()}
    truth = []
    for tr, te in RepeatedKFold(n_splits=5, n_repeats=4, random_state=0).split(X):
        truth.append(y.iloc[te].to_numpy())
        for k, mdl in zoo().items():
            mdl.fit(X.iloc[tr], ly.iloc[tr])
            preds[k].append(np.exp(mdl.predict(X.iloc[te])))
    t = np.concatenate(truth)
    res = {}
    for k, p in preds.items():
        p = np.concatenate(p)
        ape = np.abs(p / t - 1)
        res[k] = {"median_ape": round(float(np.median(ape)), 3), "mean_ape": round(float(np.mean(ape)), 3),
                  "within_25pct": round(float(np.mean(ape < 0.25)), 3),
                  "r2_log": round(float(1 - np.mean((np.log(p) - np.log(t)) ** 2) / np.var(np.log(t))), 3)}
    best = min(res, key=lambda k: res[k]["median_ape"])
    return res, {"best": best}


def main():
    t = targets()
    out = {"n_buildings": int(len(t)), "targets": {}, "pooled_balance_points_F": {"heat_gas": TAU_H_GAS, "heat_elec": TAU_H_ELEC, "cool": TAU_C}}
    for name, col, min_r2 in (("heat_gas", "heat_int", ("gas_r2", 0.7)), ("cool_elec", "cool_int", ("elec_r2", 0.3)),
                              ("heat_elec", "eheat_int", ("elec_r2", 0.3))):
        d = t[t[col].notna() & (t[col] > 0) & (t[min_r2[0]] >= min_r2[1])]
        d = d.dropna(subset=["year_built", "surface_to_volume", "height_ft_max"])
        summary = {"n": int(len(d)), "unit": "ccf/1000ft²/yr" if name == "heat_gas" else "kWh/1000ft²/yr",
                   "p10_p50_p90": [round(float(q), 1) for q in d[col].quantile([.1, .5, .9])] if len(d) else None}
        if len(d) < 15:
            summary["note"] = "too few metered buildings for a feature model: the service uses the median"
            out["targets"][name] = summary
            with open(ARTIFACTS / f"bldg_{name}.pkl", "wb") as f:
                pickle.dump({"name": "null_median", "median": float(d[col].median()) if len(d) else None}, f)
            continue
        X = building_features(d)[BUILDING]
        res, sel = cv_compare(X, d[col])
        summary.update(cv=res, chosen=sel["best"])
        mdl = zoo()[sel["best"]].fit(X, np.log(d[col]))
        imp = None
        if hasattr(mdl, "feature_importances_"):
            imp = dict(zip(BUILDING, np.round(mdl.feature_importances_, 3).tolist()))
        summary["feature_importance"] = imp
        out["targets"][name] = summary
        with open(ARTIFACTS / f"bldg_{name}.pkl", "wb") as f:
            pickle.dump({"name": sel["best"], "model": mdl, "features": BUILDING, "median": float(d[col].median()),
                         "train_range": {c: [float(X[c].min()), float(X[c].max())] for c in BUILDING}}, f)
    (RESULTS / "building_model_validation.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

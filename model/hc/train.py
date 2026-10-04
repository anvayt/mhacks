"""P1-05: train heating/cooling models on real Ann Arbor meters.

1. Join every building-month to localized weather (PRISM 800 m level + ERA5 daily shape).
2. Fit PRISM (Princeton Scorekeeping) change-point models per building: real metered heating and cooling.
3. Cross-building models (multiple linear regression, random forest, XGBoost), validated with GroupKFold by
   building, to predict buildings without meters. Held-out error is reported at the month level and at the
   level that matters for the product: each building's annual heating (gas) and cooling (electric) energy.

Run: python -m model.hc.train
"""
from __future__ import annotations

import json
import pickle

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from model import climate
from model.hc import changepoint
from model.hc.features import FEATURES, building_features, weather_features, zero_weather
from model.paths import ARTIFACTS, PROCESSED, RESULTS

TARGETS = {"gas": "gas_ccf", "elec": "elec_kwh"}
PER = 1000.0  # intensities are per 1,000 ft² per day


# ---------------------------------------------------------------- data
def building_table(m: pd.DataFrame) -> pd.DataFrame:
    cols = ["building_id", "name", "address", "ptype", "gfa_ft2", "year_built", "lat", "lon", "fp_count",
            "fp_area_ft2", "fp_floor_area_est_ft2", "height_ft_max", "stories_max", "stories_mean",
            "surface_to_volume", "energy_star"]
    return m.sort_values("year").groupby("building_id").last().reset_index()[cols]


def training_frame(refresh: bool = False) -> pd.DataFrame:
    path = PROCESSED / "meters_weather.parquet"
    if path.exists() and not refresh:
        return pd.read_parquet(path)
    m = pd.read_parquet(PROCESSED / "meters_monthly.parquet")
    m = m[m.gfa_ok]
    frames = []
    for bid, g in m.groupby("building_id"):
        w = climate.monthly_weather_years(g.lat.iloc[0], g.lon.iloc[0], sorted(g.year.unique()))
        frames.append(g.merge(w, on=["year", "month"], how="left"))
    df = pd.concat(frames, ignore_index=True)
    df.to_parquet(path, index=False)
    return df


# ---------------------------------------------------------------- PRISM change-point (metered truth)
def fit_changepoints(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for bid, g in df.groupby("building_id"):
        r = {"building_id": bid}
        gg = g[g.gas_ok & ~g.gas_ccf_outlier]
        ge = g[g.elec_ok & ~g.elec_kwh_outlier]
        fg = changepoint.fit(gg, "gas_ccf", heating=True, cooling=False)
        fe = changepoint.fit(ge, "elec_kwh", heating=True, cooling=True)
        for name, f in (("gas", fg), ("elec", fe)):
            if f is not None:
                r.update({f"{name}_{k}": v for k, v in f.to_dict().items()})
        rows.append(r)
    return pd.DataFrame(rows)


def cp_object(row: pd.Series, fuel: str) -> changepoint.CPFit | None:
    if pd.isna(row.get(f"{fuel}_alpha")):
        return None
    th, tc = row.get(f"{fuel}_tau_h"), row.get(f"{fuel}_tau_c")
    return changepoint.CPFit(row[f"{fuel}_alpha"], row[f"{fuel}_beta_h"], row[f"{fuel}_beta_c"],
                             int(th) if pd.notna(th) else None, int(tc) if pd.notna(tc) else None,
                             row[f"{fuel}_r2"], int(row[f"{fuel}_n"]), row[f"{fuel}_cv_rmse"])


# ---------------------------------------------------------------- cross-building models
def model_zoo(fuel: str) -> dict:
    # physics prior for XGBoost: more heating degree-days never lowers gas use; more cooling degree-days never
    # lowers electricity use
    mono = []
    for f in FEATURES:
        if f.startswith("hdd"):
            mono.append(1)
        elif f.startswith("cdd") and fuel == "elec":
            mono.append(1)
        else:
            mono.append(0)
    return {
        "mlr": make_pipeline(StandardScaler(), LinearRegression()),
        "random_forest": RandomForestRegressor(n_estimators=400, min_samples_leaf=5, max_features=0.5,
                                               n_jobs=-1, random_state=0),
        "xgboost": XGBRegressor(n_estimators=600, learning_rate=0.03, max_depth=4, subsample=0.8,
                                colsample_bytree=0.8, min_child_weight=5, reg_lambda=1.0,
                                monotone_constraints="(" + ",".join(map(str, mono)) + ")", random_state=0),
    }


def mlr_design(X: pd.DataFrame) -> pd.DataFrame:
    """Multiple regression with physics interactions: weather slopes vary with vintage, size and shape."""
    D = X.copy()
    for w in ("hdd60_pd", "hdd65_pd", "cdd65_pd", "cdd70_pd"):
        for b in ("year_built", "log_gfa", "surface_to_volume", "stories_max"):
            D[f"{w}*{b}"] = X[w] * X[b]
    return D


def design(name: str, X: pd.DataFrame) -> pd.DataFrame:
    return mlr_design(X) if name == "mlr" else X


def panel(df: pd.DataFrame, fuel: str) -> tuple[pd.DataFrame, pd.Series, pd.Series, pd.DataFrame]:
    col = TARGETS[fuel]
    ok = df[f"{fuel}_ok"] & ~df[f"{col}_outlier"] & df.hdd65.notna()
    d = df[ok].reset_index(drop=True)
    X = pd.concat([weather_features(d), building_features(d)], axis=1)[FEATURES]
    y = d[col] / d["gfa_ft2"] / d["days"] * PER
    keep = X.notna().all(axis=1)
    return X[keep].reset_index(drop=True), y[keep].reset_index(drop=True), d.loc[keep, "building_id"].reset_index(drop=True), d[keep].reset_index(drop=True)


def evaluate(df: pd.DataFrame, cps: pd.DataFrame, fuel: str, n_splits: int = 5) -> tuple[dict, pd.DataFrame]:
    """GroupKFold by building. Returns metrics per model plus per-building held-out annual components."""
    X, y, groups, d = panel(df, fuel)
    comp = "heating" if fuel == "gas" else "cooling"
    results, per_bldg = {}, []
    for name, _ in model_zoo(fuel).items():
        pred = np.zeros(len(y)); pred_n = np.zeros(len(y))
        zero = "hdd" if fuel == "gas" else "cdd"
        for tr, te in GroupKFold(n_splits).split(X, y, groups):
            mdl = model_zoo(fuel)[name]
            mdl.fit(design(name, X.iloc[tr]), y.iloc[tr])
            pred[te] = mdl.predict(design(name, X.iloc[te]))
            pred_n[te] = mdl.predict(design(name, zero_weather(X.iloc[te], zero)))
        wx = np.clip(pred - pred_n, 0, None)  # heating part of gas / cooling part of electricity
        t = d[["building_id", "year", "month", "days", "gfa_ft2"]].copy()
        t["pred_wx"] = wx * t.gfa_ft2 * t.days / PER
        a = t.groupby("building_id").agg(pred_wx=("pred_wx", "sum"), months=("month", "size"), gfa=("gfa_ft2", "first")).reset_index()
        truth = []
        for _, r in a.iterrows():
            f = cp_object(cps.set_index("building_id").loc[r.building_id], fuel)
            if f is None or f.r2 < 0.5:
                truth.append(np.nan); continue
            sub = d[d.building_id == r.building_id]
            p = f.predict(sub)
            truth.append(p[comp].sum())
        a["true_wx"] = truth
        a = a.dropna()
        a["pred_int"] = a.pred_wx / a.gfa * PER * 12 / a.months  # annualized per 1,000 ft²
        a["true_int"] = a.true_wx / a.gfa * PER * 12 / a.months
        results[name] = {
            "monthly_r2": round(float(r2_score(y, pred)), 3),
            "monthly_mae_per_1000ft2_day": round(float(mean_absolute_error(y, pred)), 4),
            f"building_annual_{comp}_r2": round(float(r2_score(a.true_int, a.pred_int)), 3),
            f"building_annual_{comp}_mape": round(float(np.median(np.abs(a.pred_int / a.true_int - 1))), 3),
            "n_buildings": int(groups.nunique()), "n_building_months": int(len(y)),
            "n_buildings_scored": int(len(a)),
        }
        a["model"] = name
        per_bldg.append(a)
    return results, pd.concat(per_bldg)


def main():
    df = training_frame()
    cps = fit_changepoints(df)
    cps.to_parquet(PROCESSED / "changepoints.parquet", index=False)
    cp_summary = {
        "gas": {"n": int(cps.gas_r2.notna().sum()), "median_r2": round(float(cps.gas_r2.median()), 3),
                "median_cv_rmse": round(float(cps.gas_cv_rmse.median()), 3),
                "tau_h_counts": cps.gas_tau_h.value_counts().to_dict()},
        "elec": {"n": int(cps.elec_r2.notna().sum()), "median_r2": round(float(cps.elec_r2.median()), 3),
                 "median_cv_rmse": round(float(cps.elec_cv_rmse.median()), 3),
                 "tau_c_counts": cps.elec_tau_c.value_counts().to_dict()},
    }
    out = {"changepoint": cp_summary, "models": {}}
    best = {}
    for fuel in ("gas", "elec"):
        res, per = evaluate(df, cps, fuel)
        out["models"][fuel] = res
        per.to_parquet(RESULTS / f"heldout_{fuel}.parquet", index=False)
        key = [k for k in next(iter(res.values())) if k.endswith("_mape")][0]
        best[fuel] = min(res, key=lambda k: res[k][key])
        X, y, _, _ = panel(df, fuel)
        mdl = model_zoo(fuel)[best[fuel]].fit(design(best[fuel], X), y)
        with open(ARTIFACTS / f"hc_{fuel}.pkl", "wb") as f:
            pickle.dump({"name": best[fuel], "model": mdl, "features": FEATURES, "per": PER}, f)
    out["chosen"] = best
    (RESULTS / "hc_validation.json").write_text(json.dumps(out, indent=2, default=str))
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()

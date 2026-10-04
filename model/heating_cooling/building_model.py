"""P1-05 (stage 2): building-level heating/cooling intensity models trained on real meters.

Why building-level: in the PRISM model, weather enters linearly (energy = slope × degree-days), so the part
that differs between buildings is the *slope*. We therefore learn, per building:
    heat_int = βh · HDD_normal(τh) / GFA × 1000      [ccf per 1,000 ft² per typical year]   (gas heating)
    cool_int = βc · CDD_normal(τc) / GFA × 1000      [kWh per 1,000 ft² per typical year]   (electric cooling)
    eheat_int (electric heating, only for buildings with no gas heating)
and predict it from footprint/public-record features. Local weather (any season, year or forecast) then
rescales it through degree-days at the building's own 800 m PRISM cell.

Model selection (model/heating_cooling/modelsel.py): baseline median, median regression on year built, median
regression + lasso, OLS, lasso, ridge, elastic net, Huber, tuned random forest and tuned XGBoost. Hyperparameters
are tuned by an inner 5-fold search on the product metric (median absolute % error), performance is measured by an
outer 5-fold × 5-repeat loop (nested CV), and the family is picked by the one-standard-error rule. Targets are
log(intensity) (one row per building, so no leakage between rows of the same building).

Run: python -m model.heating_cooling.building_model
"""
from __future__ import annotations

import json
import pickle

import numpy as np
import pandas as pd

from model import climate
from model.heating_cooling import modelsel
from model.heating_cooling.features import BUILDING, building_features
from model.heating_cooling.train import building_table, cp_object
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


TARGETS = {  # name: (column, fit-quality filter, unit)
    "heat_gas": ("heat_int", ("gas_r2", 0.7), "ccf/1000ft²/yr"),
    "cool_elec": ("cool_int", ("elec_r2", 0.3), "kWh/1000ft²/yr"),
    "heat_elec": ("eheat_int", ("elec_r2", 0.3), "kWh/1000ft²/yr"),
}


def training_data(t: pd.DataFrame, name: str) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    col, (r2c, thr), _ = TARGETS[name]
    d = t[t[col].notna() & (t[col] > 0) & (t[r2c] >= thr)]
    d = d.dropna(subset=["year_built", "surface_to_volume", "height_ft_max"]).reset_index(drop=True)
    return d, building_features(d)[BUILDING].reset_index(drop=True), np.log(d[col].to_numpy())


def select_and_fit(X: pd.DataFrame, y: np.ndarray, n_repeats: int = 5, log=print) -> tuple[dict, str, dict, object, dict]:
    fams = modelsel.families(X.shape[1])
    res = modelsel.nested_cv(X, y, fams, n_repeats=n_repeats, log=log)
    chosen, why = modelsel.one_se_choice(res)
    final, params = modelsel.fit_final(fams[chosen], X, y)
    return res, chosen, why, final, params


def main(n_repeats: int = 5):
    t = targets()
    out = {"n_buildings": int(len(t)), "targets": {},
           "pooled_balance_points_F": {"heat_gas": TAU_H_GAS, "heat_elec": TAU_H_ELEC, "cool": TAU_C},
           "scheme": {"rows": "one per metered property", "target": "log(weather-normalized intensity from the building's own change-point fit)",
                      "features": BUILDING, "metric": "median |exp(pred − y) − 1| (median absolute % error), used for tuning AND reporting",
                      "outer_cv": f"RepeatedKFold(5 folds × {n_repeats} repeats, seed 0): measures only",
                      "inner_cv": "KFold(5) inside each outer training split: tunes hyperparameters (grid or 40-draw random search)",
                      "selection": "one-standard-error rule across families (simplest within 1 SD of the best mean)",
                      "final_fit": "chosen family re-tuned on all buildings (inner RepeatedKFold 5×3), then refit"}}
    for name, (col, (r2c, thr), unit) in TARGETS.items():
        d, X, y = training_data(t, name)
        summary = {"n": int(len(d)), "unit": unit, "fit_filter": f"{r2c} ≥ {thr}",
                   "p10_p50_p90": [round(float(q), 1) for q in np.exp(np.quantile(y, [.1, .5, .9]))] if len(y) else None,
                   "log_target_skew": float(pd.Series(y).skew()) if len(y) > 2 else None}
        if len(d) < 20:
            summary["note"] = f"only {len(d)} metered buildings: too few for model selection; the service uses their median"
            out["targets"][name] = summary
            with open(ARTIFACTS / f"bldg_{name}.pkl", "wb") as f:
                pickle.dump({"name": "baseline_median", "model": None, "median": float(np.exp(np.median(y))) if len(y) else None}, f)
            continue
        print(f"[{name}] n={len(d)}")
        res, chosen, why, final, params = select_and_fit(X, y, n_repeats)
        summary["families"] = {k: {kk: vv for kk, vv in v.items() if kk != "oof_mean_pred"} for k, v in res.items()}
        summary["chosen"] = chosen
        summary["selection"] = why
        summary["final_params"] = params
        fam = modelsel.families(X.shape[1])[chosen]
        cols = fam.get("cols") or BUILDING
        if fam["linear"]:
            summary["coefficients"] = modelsel.linear_coefficients(final, cols, X)
            summary["intercept_log"] = float(final.named_steps["m"].intercept_)
        elif hasattr(final, "feature_importances_"):
            summary["feature_importance"] = dict(zip(BUILDING, np.round(final.feature_importances_, 3).tolist()))
        # coefficients of every linear family on all data (for the comparison view): fold mean ± sd and selection freq
        summary["linear_coef_by_family"] = {k: {"features": (modelsel.families(7)[k].get("cols") or BUILDING),
                                                "mean": v["coef_fold_mean"], "sd": v["coef_fold_sd"],
                                                "nonzero_freq": v["coef_nonzero_freq"]}
                                            for k, v in res.items() if "coef_fold_mean" in v}
        out["targets"][name] = summary
        with open(ARTIFACTS / f"bldg_{name}.pkl", "wb") as f:
            pickle.dump({"name": chosen, "model": final, "features": cols, "params": params,
                         "median": float(np.exp(np.median(y))),
                         "train_range": {c: [float(X[c].min()), float(X[c].max())] for c in cols}}, f)
        # out-of-fold predictions (mean over repeats) for every family, for downstream honest validation
        pd.DataFrame({"building_id": d.building_id, "y_log": y,
                      **{f"oof_{k}": v["oof_mean_pred"] for k, v in res.items()}}).to_parquet(RESULTS / f"oof_{name}.parquet", index=False)
    (RESULTS / "building_model_validation.json").write_text(json.dumps(out, indent=2, default=float))
    for k, v in out["targets"].items():
        if "chosen" in v:
            print(k, "chosen:", v["chosen"], "params:", v["final_params"])


if __name__ == "__main__":
    main()

"""P1-09: air-leakage model trained on real blower-door tests (New York), built to generalize to Ann Arbor houses.

Target  y = log(CFM50 per ft² of conditioned floor area). Metric: median |exp(ŷ − y) − 1| (median abs % error),
        used for tuning and reporting (model/heating_cooling/modelsel.py).
Inputs  only what exists for every Ann Arbor house (no landlord/renter survey answers):
        year built, log floor area, stories above grade, home type (detached / attached-or-2–4 unit / manufactured),
        IECC climate zone.
Tests
  1. grouped:  leave-one-region-out (10 NY regions); inner GroupKFold(5) by region tunes. This is the generalization test.
  2. random:   5-fold × 2 random CV, to show how optimistic non-grouped CV is.
  3. cross-dataset: train on the 2014–15 survey, test on the 2018 survey (and reverse).
  4. year-built availability in Ann Arbor: per-house year built is not public there, so the service has only the
     ACS block-group median. Re-test (a) true year built, (b) no year built, (c) year built replaced by
     true − e, where e is drawn from the real Ann Arbor gap between known year built (benchmarked buildings) and their
     block-group median.
  5. analysis only: + foundation, construction, style, ceiling height (not available in Ann Arbor), to show what
     richer data would add.
  6. ResStock lookup baseline: median simulated ACH50 by vintage (Michigan), converted at 8 ft ceilings. Not trained on NY.
Selection: one-standard-error rule on the grouped test (SE by bootstrap over homes).

Run: python -m model.leakage.train
"""
from __future__ import annotations

import json
import pickle
import time

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import GridSearchCV, GroupKFold, KFold, LeaveOneGroupOut, RandomizedSearchCV, RepeatedKFold
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from model.heating_cooling import modelsel
from model.leakage.data import load
from model.paths import ARTIFACTS, PROCESSED, RESULTS

AA_FEATURES = ["year_built", "log_area", "stories", "ht_attached_or_2to4", "ht_manufactured", "climate_zone"]
NO_YEAR = [f for f in AA_FEATURES if f != "year_built"]


def design(d: pd.DataFrame, extended: bool = False) -> pd.DataFrame:
    X = pd.DataFrame({"year_built": d.year_built, "log_area": np.log(d.area_ft2), "stories": d.stories,
                      "ht_attached_or_2to4": (d.home_type == "attached_or_2to4").astype(float),
                      "ht_manufactured": (d.home_type == "manufactured").astype(float),
                      "climate_zone": d.climate_zone}, index=d.index)
    if extended:
        f = d.foundation.fillna("").str.lower()
        X["fnd_conditioned_bsmt"] = f.str.startswith("conditioned").astype(float)
        X["fnd_slab"] = f.str.contains("slab").astype(float)
        X["fnd_crawl"] = f.str.contains("crawl").astype(float)
        X["new_construction"] = (d.construction == "New").astype(float)
        X["ceiling_ft"] = d.ceiling_ft.fillna(d.ceiling_ft.median())
        for s in ("Colonial", "Ranch", "Cape Cod", "Victorian", "Townhouse"):
            X[f"style_{s.lower().replace(' ', '_')}"] = (d["style"] == s).astype(float)
    return X


def families(n_features: int, fast: bool = False) -> dict:
    f = modelsel.families(n_features)
    f.pop("year_built_median_reg", None)  # re-added below only where year_built is present
    # absolute-error forests are O(n²) per split; squared-error forest, tuned, is used here
    f["random_forest"]["grid"] = {"min_samples_leaf": [2, 5, 10, 20, 40], "max_features": [0.33, 0.66, 1.0]}
    f["mlp"] = dict(est=Pipeline([("scale", StandardScaler()),
                                  ("m", MLPRegressor(max_iter=4000, early_stopping=True, n_iter_no_change=30,
                                                     validation_fraction=0.15, random_state=0))]),
                    grid={"m__hidden_layer_sizes": [(8,), (16,), (32,), (16, 8), (32, 16)],
                          "m__alpha": [1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0],
                          "m__learning_rate_init": [1e-3, 3e-3, 1e-2]},
                    search="random", n_iter=12 if fast else 20, complexity=7, linear=False,
                    label="Neural network (MLP, tuned)")
    if fast:
        f["xgboost"]["n_iter"] = 20
    return f


def _search(fam, inner, seed):
    if fam["grid"] is None:
        return clone(fam["est"])
    if fam.get("search") == "random":
        return RandomizedSearchCV(clone(fam["est"]), fam["grid"], n_iter=fam.get("n_iter", 20), scoring=modelsel.MEDAPE,
                                  cv=inner, random_state=seed, n_jobs=-1)
    return GridSearchCV(clone(fam["est"]), fam["grid"], scoring=modelsel.MEDAPE, cv=inner, n_jobs=-1)


def fit_tuned(fam, X, y, groups, seed=0):
    s = _search(fam, GroupKFold(n_splits=5), seed)
    if hasattr(s, "best_params_") or fam["grid"] is not None:
        s.fit(X, y, groups=groups)
        return s.best_estimator_, {k.replace("m__", ""): (v.item() if hasattr(v, "item") else v) for k, v in s.best_params_.items()}
    s.fit(X, y)
    return s, {}


def run_outer(fam, X, y, groups, splits, test_X=None, seed=0):
    """Out-of-fold predictions for one family over given outer splits; inner tuning is grouped by region."""
    pred = np.full(len(y), np.nan)
    train_err, params = [], []
    Xt = X if test_X is None else test_X
    for i, (tr, te) in enumerate(splits):
        m, p = fit_tuned(fam, X.iloc[tr], y[tr], groups[tr], seed + i)
        pred[te] = m.predict(Xt.iloc[te])
        train_err.append(modelsel.medape(y[tr], m.predict(X.iloc[tr])))
        params.append(p)
    return pred, float(np.mean(train_err)), params


def stats(y, p, rng=np.random.default_rng(0), n_boot=500) -> dict:
    ok = ~np.isnan(p)
    y, p = y[ok], p[ok]
    ape = np.abs(np.exp(p - y) - 1)
    boots = [np.median(ape[rng.integers(0, len(ape), len(ape))]) for _ in range(n_boot)]
    return {"n": int(len(y)), "medape": float(np.median(ape)), "medape_se": float(np.std(boots)),
            "within_25pct": float(np.mean(ape <= 0.25)), "within_50pct": float(np.mean(ape <= 0.5)),
            "bias_median_signed": float(np.median(np.exp(p - y) - 1)),
            "r2_log": float(1 - np.mean((p - y) ** 2) / np.var(y)), "spearman": float(pd.Series(p).corr(pd.Series(y), method="spearman"))}


def aa_year_gap() -> np.ndarray:
    """Real Ann Arbor gap e = known year built − ACS block-group median year built, from benchmarked buildings."""
    from model.leakage.ann_arbor import block_group_year_built
    t = pd.read_parquet(PROCESSED / "building_targets.parquet")
    bg = block_group_year_built(t.lat.to_numpy(), t.lon.to_numpy())
    e = (t.year_built - bg).dropna().to_numpy()
    return e


def resstock_baseline(d: pd.DataFrame) -> np.ndarray:
    """Median simulated ACH50 by vintage for Michigan single-family homes (ResStock 2024.2) → CFM50/ft² at 8 ft."""
    from model.data_sources.resstock import load as rs_load
    r = rs_load()
    r = r[r["in.geometry_building_type_recs"].astype(str).str.startswith("Single-Family")]
    ach = pd.to_numeric(r["in.infiltration"].astype(str).str.extract(r"([\d.]+)")[0], errors="coerce")
    vint = r["in.vintage"].astype(str)
    med = ach.groupby(vint).median()
    def vbin(y):
        if y < 1940: return "<1940"
        return f"{int(min(y, 2019) // 10 * 10)}s"
    v = d.year_built.map(vbin)
    a = v.map(med).fillna(ach.median())
    return np.log(a.to_numpy() * 8.0 / 60.0)


def main(fast: bool = False):
    t0 = time.time()
    d, qc = load()
    y = d.y.to_numpy()
    groups = d.region.to_numpy()
    X = design(d)
    fams = families(X.shape[1], fast)
    out = {"data": qc, "target": "log(CFM50 per ft² conditioned floor area)", "features": AA_FEATURES,
           "metric": "median absolute % error on CFM50/ft² (same % for CFM50 and ACH50)",
           "tests": {}, "notes": []}
    logo = list(LeaveOneGroupOut().split(X, y, groups))
    rnd = list(RepeatedKFold(n_splits=5, n_repeats=2, random_state=0).split(X))

    # 1. grouped (leave-one-region-out): every family
    res = {}
    for name, fam in fams.items():
        p, tr_err, params = run_outer(fam, X, y, groups, logo)
        s = stats(y, p)
        s.update(label=fam["label"], complexity=fam["complexity"], train_medape=tr_err, overfit_gap=s["medape"] - tr_err,
                 params_per_fold=params)
        s["per_region_medape"] = {g: float(np.median(np.abs(np.exp(p[groups == g] - y[groups == g]) - 1))) for g in np.unique(groups)}
        res[name] = s
        print(f"[grouped] {name:20s} {s['medape']:.3f} ± {s['medape_se']:.3f}  train {tr_err:.3f}  ({time.time()-t0:.0f}s)", flush=True)
    yb_fam = modelsel.families(1)["year_built_median_reg"]
    p, tr_err, _ = run_outer(yb_fam, X[["year_built"]], y, groups, logo)
    s = stats(y, p); s.update(label=yb_fam["label"], complexity=1, train_medape=tr_err, overfit_gap=s["medape"] - tr_err)
    res["year_built_median_reg"] = s
    rs = resstock_baseline(d)
    s = stats(y, rs); s.update(label="ResStock lookup: median simulated ACH50 by vintage (MI), 8 ft ceilings; not fit to NY",
                              complexity=0.5, train_medape=None, overfit_gap=None)
    res["resstock_lookup"] = s
    best = min((k for k in res if k != "resstock_lookup"), key=lambda k: res[k]["medape"])
    thr = res[best]["medape"] + res[best]["medape_se"]
    within = [k for k in res if k != "resstock_lookup" and res[k]["medape"] <= thr]
    chosen = min(within, key=lambda k: (res[k]["complexity"], res[k]["medape"]))
    out["tests"]["grouped_leave_one_region_out"] = {"families": res, "best_by_mean": best, "threshold": thr,
                                                     "within_1se": within, "chosen": chosen}
    print("chosen:", chosen, "best:", best, flush=True)

    # 2. random CV for the chosen family + baseline (how optimistic is non-grouped CV?)
    out["tests"]["random_kfold"] = {}
    for name in dict.fromkeys([chosen, best, "baseline_median"]):
        fam = fams.get(name) or yb_fam
        Xn = X[["year_built"]] if name == "year_built_median_reg" else X
        preds = []
        for rep in range(2):
            sp = [s_ for i_, s_ in enumerate(rnd) if i_ // 5 == rep]
            p, _, _ = run_outer(fam, Xn, y, groups, sp)
            preds.append(p)
        out["tests"]["random_kfold"][name] = stats(y, np.nanmean(preds, axis=0))

    # 3. cross-dataset
    out["tests"]["cross_dataset"] = {}
    src = d.source.to_numpy()
    for a, b in (("rsbs2015", "rbsa2018"), ("rbsa2018", "rsbs2015")):
        tr, te = np.where(src == a)[0], np.where(src == b)[0]
        out["tests"]["cross_dataset"][f"train_{a}_test_{b}"] = {}
        for name in dict.fromkeys([chosen, "baseline_median"]):
            fam = fams.get(name) or yb_fam
            Xn = X[["year_built"]] if name == "year_built_median_reg" else X
            p, _, _ = run_outer(fam, Xn, y, groups, [(tr, te)])
            out["tests"]["cross_dataset"][f"train_{a}_test_{b}"][name] = stats(y[te], p[te])

    # 4. year-built availability scenarios (chosen family, grouped test)
    gap = aa_year_gap()
    out["ann_arbor_year_built_gap"] = {"n_buildings": int(len(gap)), "median": float(np.median(gap)),
                                       "mad": float(np.median(np.abs(gap - np.median(gap)))),
                                       "p10_p90": [float(np.quantile(gap, .1)), float(np.quantile(gap, .9))],
                                       "source": "Ann Arbor benchmarked buildings: reported year built − ACS block-group renter median"}
    rng = np.random.default_rng(0)
    noisy = X.copy(); noisy["year_built"] = X.year_built - rng.choice(gap, len(X))
    fam_c = fams.get(chosen) or yb_fam
    sc = {}
    p, _, _ = run_outer(fam_c, X if chosen != "year_built_median_reg" else X[["year_built"]], y, groups, logo)
    sc["a_true_year_built"] = stats(y, p)
    nf = fams[chosen] if chosen in fams else fams["lasso"]
    p, _, _ = run_outer(nf, X[NO_YEAR], y, groups, logo)
    sc["b_no_year_built"] = stats(y, p)
    Xc = X if chosen != "year_built_median_reg" else X[["year_built"]]
    Nc = noisy if chosen != "year_built_median_reg" else noisy[["year_built"]]
    p, _, _ = run_outer(fam_c, Xc, y, groups, logo, test_X=Nc)
    sc["c_noisy_year_built_trained_on_true"] = stats(y, p)
    p, _, _ = run_outer(fam_c, Nc, y, groups, logo)
    sc["c_noisy_year_built_trained_on_noisy"] = stats(y, p)
    out["tests"]["year_built_scenarios"] = sc
    print("scenarios:", {k: round(v["medape"], 3) for k, v in sc.items()}, flush=True)

    # 5. analysis only: richer (non-Ann-Arbor) features
    Xe = design(d, extended=True)
    fe = families(Xe.shape[1], fast)
    out["tests"]["extended_features_analysis_only"] = {}
    for name in dict.fromkeys(["lasso", chosen if chosen in fe else "lasso"]):
        p, _, _ = run_outer(fe[name], Xe, y, groups, logo)
        out["tests"]["extended_features_analysis_only"][name] = stats(y, p)

    # final model: chosen family, tuned on all homes (GroupKFold by region)
    use_noisy = sc["c_noisy_year_built_trained_on_noisy"]["medape"] < sc["c_noisy_year_built_trained_on_true"]["medape"]
    Xf = (Nc if use_noisy else Xc)
    final, params = fit_tuned(fam_c, Xf, y, groups)
    out["final"] = {"family": chosen, "params": params, "trained_with_noisy_year_built": bool(use_noisy),
                    "features": list(Xf.columns), "n": int(len(y))}
    if fam_c.get("linear"):
        out["final"]["coefficients"] = modelsel.linear_coefficients(final, list(Xf.columns), Xf)
        out["final"]["intercept_log"] = float(final.named_steps["m"].intercept_)
    elif hasattr(final, "feature_importances_"):
        out["final"]["feature_importance"] = dict(zip(Xf.columns, np.round(final.feature_importances_, 3).tolist()))
    with open(ARTIFACTS / "leakage.pkl", "wb") as f:
        pickle.dump({"family": chosen, "model": final, "features": list(Xf.columns), "params": params,
                     "train_ranges": {c: [float(Xf[c].min()), float(Xf[c].max())] for c in Xf.columns}}, f)
    out["runtime_s"] = round(time.time() - t0)
    (RESULTS / "leakage_validation.json").write_text(json.dumps(out, indent=2, default=float))
    print("done in", out["runtime_s"], "s; final:", chosen, params)


if __name__ == "__main__":
    import sys
    main(fast="--fast" in sys.argv)

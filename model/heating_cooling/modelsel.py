"""Model selection done properly for small tabular data (≈100 buildings).

Design
- Target y = log(intensity). The product metric is the median absolute percentage error on the original scale,
  median(|exp(ŷ − y) − 1|). Every search and every report uses that metric (`MEDAPE`), never a proxy.
- Because exp() is monotone, the prediction that minimizes absolute error in log space (the conditional
  median) is the right target. So L1 / median-regression candidates are included next to the usual squared-error
  ones. Squared-error models aim at the conditional mean, which a skewed target pulls away from the median.
- Nested cross-validation: an inner 5-fold search tunes hyperparameters on the training part of each outer fold;
  the outer 5-fold × R-repeat loop only measures. Out-of-fold predictions are kept for every repeat.
- Selection: the one-standard-error rule over model families. Among families whose mean outer score is within one
  standard deviation (across repeats) of the best, take the simplest (lowest `complexity`).
- Final model: the chosen family, re-tuned with the same inner search on all buildings.
"""
from __future__ import annotations

import warnings

import numpy as np
from sklearn.base import clone
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import ElasticNet, HuberRegressor, Lasso, LinearRegression, QuantileRegressor, Ridge
from sklearn.metrics import make_scorer
from sklearn.model_selection import GridSearchCV, KFold, ParameterSampler, RandomizedSearchCV, RepeatedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

warnings.filterwarnings("ignore", category=ConvergenceWarning)


def medape(y_log, p_log) -> float:
    return float(np.median(np.abs(np.exp(np.asarray(p_log) - np.asarray(y_log)) - 1)))


MEDAPE = make_scorer(lambda y, p: -medape(y, p))  # sklearn maximizes scores


def _lin(est):
    return Pipeline([("scale", StandardScaler()), ("m", est)])


def families(n_features: int) -> dict:
    """name → dict(estimator, grid, search, complexity, linear, label). Grids are on the inner metric."""
    a = np.logspace(-3, 1.5, 12)
    return {
        "baseline_median": dict(est=DummyRegressor(strategy="median"), grid=None, complexity=0, linear=False,
                                label="Baseline: median of all buildings (ignores features)"),
        "year_built_median_reg": dict(est=_lin(QuantileRegressor(quantile=0.5, alpha=0.0, solver="highs")), grid=None,
                                      complexity=1, linear=True, cols=["year_built"],
                                      label="Median regression on year built only"),
        "median_lasso": dict(est=_lin(QuantileRegressor(quantile=0.5, solver="highs")),
                             grid={"m__alpha": np.r_[0.0, np.logspace(-4, -0.5, 9)]}, complexity=2, linear=True,
                             label="Median regression + lasso penalty (L1 loss, L1 penalty)"),
        "ols": dict(est=_lin(LinearRegression()), grid=None, complexity=3, linear=True,
                    label="Ordinary least squares"),
        "lasso": dict(est=_lin(Lasso(max_iter=50000)), grid={"m__alpha": a / 10}, complexity=3, linear=True,
                      label="Lasso (squared loss, L1 penalty)"),
        "ridge": dict(est=_lin(Ridge()), grid={"m__alpha": np.logspace(-2, 3, 14)}, complexity=3, linear=True,
                      label="Ridge (squared loss, L2 penalty)"),
        "elastic_net": dict(est=_lin(ElasticNet(max_iter=50000)),
                            grid={"m__alpha": a / 10, "m__l1_ratio": [0.2, 0.5, 0.8]}, complexity=3, linear=True,
                            label="Elastic net (squared loss, L1+L2 penalty)"),
        "huber": dict(est=_lin(HuberRegressor(max_iter=2000)),
                      grid={"m__epsilon": [1.1, 1.35, 2.0], "m__alpha": np.logspace(-4, 1, 6)}, complexity=3,
                      linear=True, label="Huber regression (robust loss, L2 penalty)"),
        "random_forest": dict(est=RandomForestRegressor(n_estimators=200, random_state=0, n_jobs=-1),
                              grid={"min_samples_leaf": [2, 5, 10, 20], "max_features": [0.33, 0.66, 1.0],
                                    "criterion": ["squared_error", "absolute_error"]},
                              complexity=5, linear=False, label="Random forest (tuned)"),
        "xgboost": dict(est=XGBRegressor(random_state=0, n_jobs=1, tree_method="hist"),
                        grid={"max_depth": [1, 2, 3, 4], "n_estimators": [25, 50, 100, 200, 400],
                              "learning_rate": [0.01, 0.03, 0.1, 0.3], "min_child_weight": [1, 3, 8, 15],
                              "subsample": [0.6, 0.8, 1.0], "colsample_bytree": [0.5, 0.8, 1.0],
                              "reg_lambda": [0.1, 1, 10, 50],
                              "objective": ["reg:squarederror", "reg:absoluteerror", "reg:pseudohubererror"]},
                        search="random", n_iter=40, complexity=6, linear=False, label="XGBoost (tuned)"),
    }


def _search(fam: dict, inner, seed: int):
    if fam["grid"] is None:
        return clone(fam["est"])
    if fam.get("search") == "random":
        return RandomizedSearchCV(clone(fam["est"]), fam["grid"], n_iter=fam.get("n_iter", 30), scoring=MEDAPE,
                                  cv=inner, random_state=seed, n_jobs=-1, refit=True)
    return GridSearchCV(clone(fam["est"]), fam["grid"], scoring=MEDAPE, cv=inner, n_jobs=-1, refit=True)


def _cols(fam, X):
    return X[fam["cols"]] if fam.get("cols") else X


def nested_cv(X, y, fams: dict, n_splits: int = 5, n_repeats: int = 5, seed: int = 0, log=print) -> dict:
    """Outer RepeatedKFold measures; inner KFold(5) tunes. Returns per-family results."""
    y = np.asarray(y, float)
    outer = RepeatedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=seed)
    splits = list(outer.split(X))
    res = {}
    for name, fam in fams.items():
        oof = np.full((n_repeats, len(y)), np.nan)
        train_scores, params, coefs = [], [], []
        for i, (tr, te) in enumerate(splits):
            r = i // n_splits
            inner = KFold(5, shuffle=True, random_state=seed + i)
            s = _search(fam, inner, seed + i)
            Xtr, Xte = _cols(fam, X.iloc[tr]), _cols(fam, X.iloc[te])
            s.fit(Xtr, y[tr])
            best = s.best_estimator_ if hasattr(s, "best_estimator_") else s
            oof[r, te] = best.predict(Xte)
            train_scores.append(medape(y[tr], best.predict(Xtr)))
            if hasattr(s, "best_params_"):
                params.append({k.replace("m__", ""): (v.item() if hasattr(v, "item") else v) for k, v in s.best_params_.items()})
            if fam["linear"]:
                coefs.append(np.asarray(best.named_steps["m"].coef_, float))
        per_rep = np.array([medape(y, oof[r]) for r in range(n_repeats)])
        within = np.array([np.mean(np.abs(np.exp(oof[r] - y) - 1) <= 0.25) for r in range(n_repeats)])
        r2l = np.array([1 - np.mean((oof[r] - y) ** 2) / np.var(y) for r in range(n_repeats)])
        res[name] = {"label": fam["label"], "complexity": fam["complexity"],
                     "test_medape_mean": float(per_rep.mean()), "test_medape_sd": float(per_rep.std(ddof=1)),
                     "per_repeat": per_rep.tolist(), "within_25pct": float(within.mean()), "r2_log": float(r2l.mean()),
                     "train_medape_mean": float(np.mean(train_scores)),
                     "overfit_gap": float(per_rep.mean() - np.mean(train_scores)),
                     "chosen_params_per_fold": params, "oof_mean_pred": np.nanmean(oof, axis=0).tolist()}
        if coefs:
            C = np.vstack(coefs)
            res[name]["coef_fold_mean"] = C.mean(axis=0).tolist()
            res[name]["coef_fold_sd"] = C.std(axis=0, ddof=1).tolist()
            res[name]["coef_nonzero_freq"] = (np.abs(C) > 1e-8).mean(axis=0).tolist()
        log(f"  {name:24s} test {per_rep.mean():.3f} ± {per_rep.std(ddof=1):.3f}   train {np.mean(train_scores):.3f}")
    base = np.array(res["baseline_median"]["per_repeat"])
    for name in res:
        d = np.array(res[name]["per_repeat"]) - base
        res[name]["vs_baseline_mean"] = float(d.mean())
        res[name]["vs_baseline_sd"] = float(d.std(ddof=1))
    return res


def one_se_choice(res: dict) -> tuple[str, dict]:
    best = min(res, key=lambda k: res[k]["test_medape_mean"])
    thr = res[best]["test_medape_mean"] + res[best]["test_medape_sd"]
    ok = [k for k in res if res[k]["test_medape_mean"] <= thr]
    chosen = min(ok, key=lambda k: (res[k]["complexity"], res[k]["test_medape_mean"]))
    return chosen, {"best_by_mean": best, "threshold": thr, "within_1se": ok,
                    "rule": "simplest family whose mean held-out error is within one SD (across repeats) of the best"}


def fit_final(fam: dict, X, y, seed: int = 0):
    """Re-tune the chosen family on all data (inner 5-fold, repeated ×3 for stability) and refit."""
    inner = RepeatedKFold(n_splits=5, n_repeats=3, random_state=seed)
    s = _search(fam, inner, seed)
    Xc = _cols(fam, X)
    s.fit(Xc, np.asarray(y, float))
    best = s.best_estimator_ if hasattr(s, "best_estimator_") else s
    params = {k.replace("m__", ""): (v.item() if hasattr(v, "item") else v) for k, v in getattr(s, "best_params_", {}).items()}
    return best, params


def linear_coefficients(model, cols: list[str], X) -> list[dict]:
    """Coefficients of a fitted scaler+linear pipeline: per SD, per raw unit, and as a % multiplier."""
    sc, m = model.named_steps["scale"], model.named_steps["m"]
    out = []
    for f, c, s, mu in zip(cols, np.asarray(m.coef_, float), sc.scale_, sc.mean_):
        out.append({"feature": f, "coef_per_sd": float(c), "feature_mean": float(mu), "feature_sd": float(s),
                    "coef_per_unit": float(c / s), "pct_per_sd": float(np.exp(c) - 1)})
    return out


def sample_params(grid: dict, n: int, seed: int) -> list[dict]:
    return list(ParameterSampler(grid, n_iter=n, random_state=seed))

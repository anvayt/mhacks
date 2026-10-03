"""Forecast grid carbon intensity with XGBoost and backtest it.

One model per horizon h (hours ahead). Each training row is a forecast issued
at hour t using only what was published by then; its label is the carbon
intensity at t + h.

Publication delays (measured on EIA-930 for MISO, Oct 2026):
  - fuel mix / net generation / interchange: once a day; by FUEL_PUBLISH_HOUR
    local time the previous local day is out, so data is 18-41 hours stale
  - demand: about DEMAND_LAG hours behind
  - day-ahead demand forecast: reaches only ~7 hours ahead, so it is used only
    for horizons <= DF_LEAD

    python model.py train --days 120 --test-days 14
    python model.py train --features satellite.csv     # extra hourly features
    python model.py forecast                           # next-24h curve from saved models

Data comes from carbon_intensity.load_history (EIA-930, cached locally).
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb

import carbon_intensity as ci

MODEL_DIR = Path(__file__).resolve().parent / "models"
LOCAL_TZ = "America/Chicago"  # MISO's market time zone, for hour-of-day features
FUEL_PUBLISH_HOUR = 17  # local hour by which yesterday's fuel mix is published
DEMAND_LAG = 2  # hours
DF_LEAD = 6  # hours ahead the day-ahead demand forecast is reliably available
TARGET = "carbon_intensity"

XGB_PARAMS = dict(
    n_estimators=400,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=3,
    objective="reg:squarederror",
)


# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------

def fuel_known_through(index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Latest fuel-mix hour published at each issue time in `index` (UTC)."""
    local = index.tz_convert(LOCAL_TZ)
    last = (local - pd.Timedelta(hours=FUEL_PUBLISH_HOUR)).normalize() - pd.Timedelta(hours=1)
    return last.tz_convert("UTC")


def _at(series: pd.Series, times: pd.DatetimeIndex, index: pd.DatetimeIndex) -> pd.Series:
    """series looked up at `times`, re-labelled with `index`."""
    return pd.Series(series.reindex(times).to_numpy(), index=index)


def _share(hist: pd.DataFrame, codes: list[str]) -> pd.Series:
    fuels = [c for c in hist.columns if str(c).lower() in ci.ALIASES and c not in ci.REGION_COLUMNS.values()]
    total = hist[fuels].clip(lower=0).sum(axis=1, min_count=1)
    part = hist[[c for c in codes if c in hist.columns]].clip(lower=0).sum(axis=1, min_count=1)
    return part / total


def base_features(hist: pd.DataFrame, extra: pd.DataFrame | None = None) -> pd.DataFrame:
    """Horizon-independent features for a forecast issued at each index hour t.

    `hist` must be on a complete hourly index. Fuel-mix features are read at
    the last published hour, demand DEMAND_LAG hours back. `extra` (e.g.
    satellite features) is joined as-is: it must already be indexed by the
    hour it became available.
    """
    idx = hist.index
    known = fuel_known_through(idx)
    y = hist[TARGET]
    f = pd.DataFrame(index=idx)
    f["staleness_h"] = (idx - known) / pd.Timedelta(hours=1)
    f["ci_now"] = _at(y, known, idx)
    f["ci_lag3"] = _at(y, known - pd.Timedelta(hours=3), idx)
    f["ci_delta3"] = f["ci_now"] - f["ci_lag3"]
    f["ci_mean24"] = _at(y.rolling(24, min_periods=12).mean(), known, idx)
    f["ci_std24"] = _at(y.rolling(24, min_periods=12).std(), known, idx)
    f["ci_min24"] = _at(y.rolling(24, min_periods=12).min(), known, idx)
    f["wind_share"] = _at(_share(hist, ["WND", "WNB"]), known, idx)
    f["solar_share"] = _at(_share(hist, ["SUN", "SNB"]), known, idx)
    f["coal_share"] = _at(_share(hist, ["COL"]), known, idx)
    f["gas_share"] = _at(_share(hist, ["NG"]), known, idx)
    if "interchange" in hist:
        f["interchange_now"] = _at(hist["interchange"], known, idx)
    if "demand" in hist:
        f["demand_now"] = hist["demand"].shift(DEMAND_LAG)
        f["demand_delta3"] = f["demand_now"] - hist["demand"].shift(DEMAND_LAG + 3)
    f["issue_hour"] = idx.tz_convert(LOCAL_TZ).hour
    if extra is not None:
        f = f.join(extra.add_prefix("x_"), how="left")
    return f


def horizon_features(hist: pd.DataFrame, base: pd.DataFrame, h: int) -> pd.DataFrame:
    """Add features about the target hour t + h (calendar, seasonal naive, demand forecast)."""
    f = base.copy()
    target_local = (hist.index + pd.Timedelta(hours=h)).tz_convert(LOCAL_TZ)
    f["target_hour"] = target_local.hour
    f["target_dow"] = target_local.dayofweek
    f["target_hour_sin"] = np.sin(2 * np.pi * target_local.hour / 24)
    f["target_hour_cos"] = np.cos(2 * np.pi * target_local.hour / 24)
    f["seasonal_naive"] = seasonal_naive(hist, h)
    if "demand_forecast" in hist:
        dft = hist["demand_forecast"].shift(-h) if h <= DF_LEAD else pd.Series(np.nan, index=hist.index)
        f["demand_forecast_target"] = dft
        f["demand_forecast_delta"] = dft - f.get("demand_now", np.nan)
    return f


def seasonal_naive(hist: pd.DataFrame, h: int) -> pd.Series:
    """Intensity at the target's hour of day on the latest published day."""
    idx = hist.index
    target = idx + pd.Timedelta(hours=h)
    gap_h = (target - fuel_known_through(idx)) / pd.Timedelta(hours=1)
    days_back = np.ceil(gap_h / 24).astype(int)
    source = target - pd.to_timedelta(24 * days_back, unit="h")
    return _at(hist[TARGET], source, idx)


# ---------------------------------------------------------------------------
# Training and backtest
# ---------------------------------------------------------------------------

def _metrics(actual: pd.Series, pred: pd.Series) -> dict:
    m = actual.notna() & pred.notna()
    err = pred[m] - actual[m]
    return {"mae": float(err.abs().mean()), "rmse": float(np.sqrt((err**2).mean())), "n": int(m.sum())}


def train_and_test(
    hist: pd.DataFrame,
    horizons: list[int],
    test_days: int,
    extra: pd.DataFrame | None = None,
    save: bool = True,
):
    """Fit one model per horizon on everything before the test window, score on it.

    Training rows whose label falls inside the test window are dropped so no
    test-period information leaks into training.
    """
    labeled = hist[TARGET].dropna()
    test_start = labeled.index.max() - pd.Timedelta(days=test_days)
    base = base_features(hist, extra)

    results, preds = [], {}
    if save:
        MODEL_DIR.mkdir(exist_ok=True)
    for h in horizons:
        X = horizon_features(hist, base, h)
        y = hist[TARGET].shift(-h)
        target_time = X.index + pd.Timedelta(hours=h)
        ok = y.notna() & X["ci_now"].notna()
        train = ok & (target_time < test_start)
        test = ok & (X.index >= test_start)
        if train.sum() < 100 or test.sum() == 0:
            print(f"h={h:>2}: skipped (train={train.sum()}, test={test.sum()})")
            continue

        model = xgb.XGBRegressor(**XGB_PARAMS)
        model.fit(X[train], y[train])
        p = pd.Series(model.predict(X[test]), index=X.index[test])
        preds[h] = p

        y_test = y[test]
        row = {
            "h": h,
            "model": _metrics(y_test, p),
            "persistence": _metrics(y_test, X.loc[test, "ci_now"]),
            "seasonal_naive": _metrics(y_test, X.loc[test, "seasonal_naive"]),
        }
        results.append(row)
        if save:
            model.save_model(MODEL_DIR / f"xgb_h{h}.json")

    if save:
        meta = {
            "horizons": sorted(preds),
            "fuel_publish_hour": FUEL_PUBLISH_HOUR,
            "demand_lag": DEMAND_LAG,
            "df_lead": DF_LEAD,
            "features": list(horizon_features(hist, base, 1).columns),
            "extra_columns": list(extra.columns) if extra is not None else [],
            "trained_through": str(test_start),
        }
        (MODEL_DIR / "meta.json").write_text(json.dumps(meta, indent=2))
    return results, preds, test_start


def schedule_backtest(hist: pd.DataFrame, preds: dict[int, pd.Series]) -> dict | None:
    """Simulate "run this 1-hour load at the cleanest hour in the next W hours".

    At every test issue hour, pick the horizon with the lowest forecast and
    compare the actual intensity there with running immediately (h=1), with the
    window's average (a random start), with yesterday's curve as the forecast,
    and with perfect foresight.
    """
    horizons = sorted(preds)
    if len(horizons) < 2:
        return None
    y = hist[TARGET]
    P = pd.DataFrame(preds).dropna()
    A = pd.DataFrame({h: y.shift(-h).reindex(P.index) for h in horizons}).dropna()
    S = pd.DataFrame({h: seasonal_naive(hist, h).reindex(A.index) for h in horizons})
    P = P.loc[A.index]
    if A.empty:
        return None

    def realized(choice: pd.Series) -> float:
        return float(np.mean([A.at[t, h] for t, h in choice.items()]))

    out = {
        "decisions": len(A),
        "window_hours": max(horizons),
        "run_now": float(A[horizons[0]].mean()),
        "random_hour": float(A.mean(axis=1).mean()),
        "model_pick": realized(P.idxmin(axis=1)),
        "yesterday_pick": realized(S.fillna(np.inf).idxmin(axis=1)),
        "oracle": float(A.min(axis=1).mean()),
    }
    out["saving_vs_now_pct"] = 100 * (1 - out["model_pick"] / out["run_now"])
    out["saving_vs_random_pct"] = 100 * (1 - out["model_pick"] / out["random_hour"])
    return out


def feature_importance(top: int = 10) -> pd.DataFrame:
    """Gain importance per saved horizon model, for the "which data matters" chart."""
    meta = json.loads((MODEL_DIR / "meta.json").read_text())
    rows = {}
    for h in meta["horizons"]:
        booster = xgb.Booster()
        booster.load_model(MODEL_DIR / f"xgb_h{h}.json")
        rows[h] = booster.get_score(importance_type="gain")
    imp = pd.DataFrame(rows).fillna(0)
    imp = imp / imp.sum()
    return imp.loc[imp.mean(axis=1).sort_values(ascending=False).index[:top]]


# ---------------------------------------------------------------------------
# Live forecast
# ---------------------------------------------------------------------------

def forecast(hist: pd.DataFrame, extra: pd.DataFrame | None = None, issue_time: pd.Timestamp | None = None) -> pd.DataFrame:
    """Predict intensity for each saved horizon from issue_time (default: now)."""
    meta = json.loads((MODEL_DIR / "meta.json").read_text())
    issue_time = (issue_time or pd.Timestamp.now(tz="UTC")).floor("h")
    # Extend the index through the issue time and target hours; future rows stay NaN
    # except demand_forecast, which EIA publishes ahead.
    full = pd.date_range(hist.index.min(), issue_time + pd.Timedelta(hours=max(meta["horizons"])), freq="h")
    hist = hist.reindex(full)
    base = base_features(hist, extra)

    rows = []
    for h in meta["horizons"]:
        X = horizon_features(hist, base, h).loc[[issue_time], meta["features"]]
        model = xgb.XGBRegressor()
        model.load_model(MODEL_DIR / f"xgb_h{h}.json")
        rows.append({"target_time": issue_time + pd.Timedelta(hours=h), "h": h, "carbon_intensity": float(model.predict(X)[0])})
    return pd.DataFrame(rows).set_index("target_time")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_horizons(text: str) -> list[int]:
    if "-" in text:
        a, b = text.split("-")
        return list(range(int(a), int(b) + 1))
    return [int(x) for x in text.split(",")]


def _load_extra(path: str | None) -> pd.DataFrame | None:
    """CSV with a 'time' column (UTC hour the values were available) and feature columns."""
    if not path:
        return None
    df = pd.read_csv(path, parse_dates=["time"])
    df["time"] = pd.to_datetime(df["time"], utc=True).dt.floor("h")
    return df.groupby("time").mean(numeric_only=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("train", "forecast"):
        p = sub.add_parser(name)
        p.add_argument("--ba", default="MISO", help="EIA-930 balancing authority code")
        p.add_argument("--basis", default="lifecycle", choices=list(ci.FACTORS))
        p.add_argument("--features", help="optional CSV of extra hourly features (e.g. satellite)")
        p.add_argument("--refresh", action="store_true", help="ignore the EIA cache")
    sub.choices["train"].add_argument("--days", type=int, default=120, help="history to pull")
    sub.choices["train"].add_argument("--test-days", type=int, default=14)
    sub.choices["train"].add_argument("--horizons", default="1-24", help='e.g. "1-24" or "1,3,6,12,24"')
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    extra = _load_extra(args.features)

    if args.cmd == "train":
        hist = ci.load_history(now - timedelta(days=args.days), now, args.ba, args.basis, refresh=args.refresh)
        results, preds, test_start = train_and_test(hist, _parse_horizons(args.horizons), args.test_days, extra)
        print(f"\nTest window starts {test_start}  (MAE / RMSE in gCO2/kWh)")
        print(f"{'h':>3} {'model':>14} {'persistence':>14} {'yesterday':>14} {'n':>5}")
        for r in results:
            fmt = lambda m: f"{m['mae']:6.1f}/{m['rmse']:6.1f}"
            print(f"{r['h']:>3} {fmt(r['model']):>14} {fmt(r['persistence']):>14} {fmt(r['seasonal_naive']):>14} {r['model']['n']:>5}")
        sched = schedule_backtest(hist, preds)
        if sched:
            print(f"\nScheduling backtest: {sched['decisions']} decisions, {sched['window_hours']}h window (mean gCO2/kWh)")
            for k in ("run_now", "random_hour", "yesterday_pick", "model_pick", "oracle"):
                print(f"  {k:15s} {sched[k]:7.1f}")
            print(f"  saving vs run-now {sched['saving_vs_now_pct']:.1f}%, vs random hour {sched['saving_vs_random_pct']:.1f}%")
        print("\nTop features (share of gain, by horizon):")
        print(feature_importance().round(3).to_string())
    else:
        meta = json.loads((MODEL_DIR / "meta.json").read_text())
        hist = ci.load_history(now - timedelta(days=3), now + timedelta(days=2), args.ba, args.basis, refresh=args.refresh)
        fc = forecast(hist, extra)
        fc.index = fc.index.tz_convert(LOCAL_TZ)
        print(fc.round(1).to_string())
        best = fc["carbon_intensity"].idxmin()
        print(f"\nCleanest hour: {best:%a %H:%M} ({fc.at[best, 'carbon_intensity']:.0f} gCO2/kWh)  "
              f"[{len(meta['horizons'])} horizons]")


if __name__ == "__main__":
    main()

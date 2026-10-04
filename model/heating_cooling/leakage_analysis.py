"""Can bills reveal a leaky building? What real meters support, and what only simulation suggests.

A. REAL METERS (Ann Arbor benchmarking, 2021–2023, buildings with all 3 years):
   A1. Out-of-year accuracy of the degree-day model: fit PRISM change-points on 2 years, predict the 3rd year
       from its actual weather. This error is the noise floor for any "X% above normal for this weather" claim.
   A2. Persistence: each building's weather-normalized heating intensity, per year, relative to the peer median.
       If a building is 40% above its peers in 2021, is it still above them in 2022 and 2023? High year-to-year
       correlation means the deviation is a stable property of the building (envelope, air leakage, boilers,
       thermostat policy), not noise. The meters cannot say *which* of those it is.
   A3. Real spread: P90/P10 of heating intensity among buildings of the same vintage.
B. SIMULATION ONLY (ResStock; not validated against real data):
   B1. Given public-record features + heating per degree-day (what one winter bill gives), how well can air
       leakage (ACH50) be recovered? Compare with public features alone.
   B2. How much of the variance in heating intensity left after public features is due to ACH50 vs insulation
       vs windows vs furnace efficiency?

Run: python -m model.heating_cooling.leakage_analysis  → results/leakage_analysis.json
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_predict
from xgboost import XGBRegressor

from model.heating_cooling import changepoint
from model.heating_cooling.building_model import normal_weather_cache
from model.heating_cooling.resstock_model import HIDDEN, PUBLIC
from model.heating_cooling.train import building_table
from model.paths import PROCESSED, RESULTS


def real_meter_tests() -> dict:
    m = pd.read_parquet(PROCESSED / "meters_weather.parquet")
    g = m[m.gas_ok & ~m.gas_ccf_outlier]
    full = g.groupby("building_id").year.nunique()
    ids = full[full == 3].index
    g = g[g.building_id.isin(ids)]
    nw = normal_weather_cache(building_table(m))

    # A1: leave-one-year-out
    errs, monthly_errs = [], []
    for bid, gb in g.groupby("building_id"):
        for y in (2021, 2022, 2023):
            tr, te = gb[gb.year != y], gb[gb.year == y]
            if len(te) < 10:
                continue
            f = changepoint.fit(tr, "gas_ccf", heating=True, cooling=False)
            if f is None or f.r2 < 0.7:
                continue
            p = f.predict(te)
            errs.append(p.total.sum() / te.gas_ccf.sum() - 1)
            winter = te.month.isin([12, 1, 2])
            if winter.any():
                monthly_errs.extend((p.total[winter] / te.gas_ccf[winter] - 1).tolist())
    errs, monthly_errs = np.array(errs), np.array(monthly_errs)

    # A2: per-year weather-normalized heating intensity and persistence of deviation from peers
    rows = []
    for bid, gb in g.groupby("building_id"):
        gfa = gb.gfa_ft2.iloc[0]
        for y, gy in gb.groupby("year"):
            f = changepoint.fit(gy, "gas_ccf", heating=True, cooling=False, min_months=10)
            if f is None or f.r2 < 0.7 or f.tau_h is None:
                continue
            rows.append({"building_id": bid, "year": y, "year_built": gb.year_built.iloc[0],
                         "heat_int": f.predict(nw[bid])["heating"].sum() / gfa * 1000})
    h = pd.DataFrame(rows)
    h["dev"] = np.log(h.heat_int / h.groupby("year").heat_int.transform("median"))
    piv = h.pivot(index="building_id", columns="year", values="dev").dropna()
    corr = piv.corr().round(3)
    # how often does the sign of the deviation (above/below peers) stay the same across all three years?
    same_sign = float(((piv > 0).all(axis=1) | (piv < 0).all(axis=1)).mean())
    # share of deviation variance that is persistent (between-building) vs year-to-year (within-building)
    between = piv.mean(axis=1).var()
    within = piv.var(axis=1).mean()

    # A3: spread within vintage group
    b = h.groupby("building_id").agg(heat_int=("heat_int", "mean"), year_built=("year_built", "first"))
    b["vintage"] = pd.cut(b.year_built, [0, 1959, 1979, 1999, 2030], labels=["<1960", "1960-79", "1980-99", "2000+"])
    spread = {str(k): {"n": int(len(v)), "p90_over_p10": round(float(v.heat_int.quantile(.9) / v.heat_int.quantile(.1)), 2),
                       "median_ccf_per_1000ft2": round(float(v.heat_int.median()), 1)}
              for k, v in b.groupby("vintage", observed=True)}
    return {
        "A1_out_of_year_degree_day_accuracy": {
            "n_building_years": int(len(errs)),
            "annual_gas_median_abs_error": round(float(np.median(np.abs(errs))), 3),
            "annual_gas_p90_abs_error": round(float(np.quantile(np.abs(errs), .9)), 3),
            "winter_month_median_abs_error": round(float(np.median(np.abs(monthly_errs))), 3),
            "winter_month_p90_abs_error": round(float(np.quantile(np.abs(monthly_errs), .9)), 3),
            "meaning": "a building's own degree-day model predicts a new year's gas this well; deviations smaller "
                       "than this are noise, larger ones are a real change (or a different building)",
        },
        "A2_persistence_of_deviation_from_peers": {
            "n_buildings": int(len(piv)),
            "year_to_year_correlation": {f"{a}-{b_}": float(corr.loc[a, b_]) for a, b_ in ((2021, 2022), (2022, 2023), (2021, 2023))},
            "same_side_of_peer_median_all_3_years": round(same_sign, 3),
            "persistent_share_of_variance": round(float(between / (between + within)), 3),
            "meaning": "how much of 'this building uses more heat than its peers' is a stable building property",
        },
        "A3_real_spread_by_vintage": spread,
    }


def simulation_tests() -> dict:
    f = pd.read_parquet(PROCESSED / "resstock_frame.parquet")
    f = f[(f.heating_fuel == "Natural Gas") & (f.heat_gas_per_hdd > 0)].dropna(subset=PUBLIC + HIDDEN)
    f = f.sample(min(len(f), 8000), random_state=0)
    xgb = lambda: XGBRegressor(n_estimators=300, max_depth=5, learning_rate=0.05, subsample=0.8, random_state=0, n_jobs=-1)
    y = np.log(f.ach50)

    def r2(cols):
        p = cross_val_predict(xgb(), f[cols], y, cv=5)
        return float(1 - np.mean((p - y) ** 2) / np.var(y)), p

    r_pub, _ = r2(PUBLIC)
    f["log_heat"] = np.log(f.heat_gas_per_hdd)
    r_bill, p_bill = r2(PUBLIC + ["log_heat"])
    # practical question: flag "leaky" (ACH50 ≥ 20, the leakier part of the stock) from a bill
    leaky = f.ach50 >= 20
    flag = np.exp(p_bill) >= 20
    tp = float((flag & leaky).sum() / max(flag.sum(), 1))
    rec = float((flag & leaky).sum() / max(leaky.sum(), 1))

    # B2: variance decomposition of log heating intensity after public features (drop-one importance)
    base_cols = PUBLIC + HIDDEN
    yh = f.log_heat
    def r2h(cols):
        p = cross_val_predict(xgb(), f[cols], yh, cv=5)
        return float(1 - np.mean((p - yh) ** 2) / np.var(yh))
    full = r2h(base_cols)
    drop = {c: round(full - r2h([x for x in base_cols if x != c]), 3) for c in HIDDEN}
    return {
        "label": "SIMULATION ONLY (NREL ResStock 2024.2 MI). Not validated against real buildings.",
        "B1_infer_air_leakage_from_bill": {
            "r2_log_ach50_public_only": round(r_pub, 3),
            "r2_log_ach50_public_plus_heating_per_hdd": round(r_bill, 3),
            "flag_leaky_ach50_ge_20_precision": round(tp, 3), "flag_leaky_recall": round(rec, 3),
            "base_rate_leaky": round(float(leaky.mean()), 3),
        },
        "B2_heating_variance_explained_drop_one": {"r2_all": round(full, 3), "loss_in_r2_when_dropped": drop},
    }


def main():
    out = {"real_meters": real_meter_tests(), "simulation": simulation_tests()}
    (RESULTS / "leakage_analysis.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

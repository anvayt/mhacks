"""P1-02: reproduce PLAN.md §6 feasibility numbers on ResStock 2024.2 MI.

Run: python -m model.scripts.reproduce_resstock
"""
import json

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from model.data_sources.resstock import load
from model.paths import RESULTS

A = ["in.sqft", "in.vintage", "in.geometry_building_type_recs", "in.geometry_stories", "in.county_name"]
B = A + ["in.windows", "in.infiltration", "in.insulation_ceiling", "in.insulation_wall",
         "in.geometry_foundation_type", "in.occupants"]


def run(d, cols, target):
    X = d[cols].copy()
    for c in X.columns:
        if not pd.api.types.is_numeric_dtype(X[c]):
            X[c] = X[c].astype("category")
    Xtr, Xte, ytr, yte = train_test_split(X, target, test_size=0.2, random_state=0)
    kw = dict(categorical_features="from_dtype", random_state=0)
    p = HistGradientBoostingRegressor(max_iter=300, **kw).fit(Xtr, ytr).predict(Xte)
    lo = HistGradientBoostingRegressor(loss="quantile", quantile=0.1, **kw).fit(Xtr, ytr).predict(Xte)
    hi = HistGradientBoostingRegressor(loss="quantile", quantile=0.9, **kw).fit(Xtr, ytr).predict(Xte)
    return {"r2": round(r2_score(yte, p), 3), "mae": round(mean_absolute_error(yte, p), 1),
            "median_p10_p90_width": round(float(np.median(hi - lo)), 1),
            "coverage_80": round(float(np.mean((yte >= lo) & (yte <= hi))), 3), "n_test": int(len(yte))}


def main():
    d = load(gas_only=True)
    # sqft arrives as a string bin in some releases; coerce when numeric-like
    d["in.sqft"] = pd.to_numeric(d["in.sqft"], errors="coerce")
    targets = {
        "bill_usd": d["out.bills.all_fuels.usd"].astype(float),
        "gas_heating_kwh": d["out.natural_gas.heating.energy_consumption.kwh"].astype(float),
        "elec_cooling_kwh": d["out.electricity.cooling.energy_consumption.kwh"].astype(float),
    }
    out = {"source": "NREL ResStock 2024.2 MI baseline (gas-heated homes)", "n_homes": int(len(d)), "results": {}}
    for tname, y in targets.items():
        for fname, cols in (("public_record", A), ("plus_6_answers", B)):
            r = run(d, cols, y)
            out["results"][f"{tname}|{fname}"] = r
            print(f"{tname:18s} {fname:15s} {r}")
    (RESULTS / "resstock_reproduce.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

"""Predict blower-door air leakage for Ann Arbor houses that have no test.

    from model.leakage.predict import predict_leakage
    predict_leakage(lat=42.2756, lon=-83.7408)          # or address="…"

Returns a point estimate of CFM50, CFM50 per ft² and ACH50 (at an assumed 8 ft ceiling, the median in the training
data), the inputs used (with sources), whether the house is inside the training data's range, and the held-out
error measured on real blower-door tests from held-out New York regions (results/leakage_validation.json).

    python -m model.leakage.predict --all   → data/processed/leakage_ann_arbor.parquet (+ .csv), every house
"""
from __future__ import annotations

import json
import pickle
from functools import lru_cache

import numpy as np
import pandas as pd

from model.data_sources import census
from model.leakage.ann_arbor import ANN_ARBOR_CLIMATE_ZONE, block_group_of, house_table
from model.paths import ARTIFACTS, PROCESSED, RESULTS

CEILING_FT = 8.0  # median measured ceiling height in both NY datasets


@lru_cache(maxsize=1)
def _model():
    with open(ARTIFACTS / "leakage.pkl", "rb") as f:
        art = pickle.load(f)
    val = json.loads((RESULTS / "leakage_validation.json").read_text())
    return art, val


def features(floor_area_ft2, stories, home_type, year_built, climate_zone=ANN_ARBOR_CLIMATE_ZONE) -> pd.DataFrame:
    return pd.DataFrame({"year_built": np.asarray(year_built, float), "log_area": np.log(np.asarray(floor_area_ft2, float)),
                         "stories": np.asarray(stories, float),
                         "ht_attached_or_2to4": (np.asarray(home_type) == "attached_or_2to4").astype(float),
                         "ht_manufactured": (np.asarray(home_type) == "manufactured").astype(float),
                         "climate_zone": np.asarray(climate_zone, float) * np.ones(np.size(year_built))})


def _predict_df(X: pd.DataFrame) -> pd.DataFrame:
    art, _ = _model()
    cols = art["features"]
    p = np.exp(art["model"].predict(X[cols]))
    rng = art["train_ranges"]
    in_range = np.ones(len(X), bool)
    for c in cols:
        lo, hi = rng[c]
        in_range &= X[c].between(lo, hi).to_numpy()
    return pd.DataFrame({"cfm50_per_ft2": p, "in_training_range": in_range}, index=X.index)


def predict_all() -> pd.DataFrame:
    h = house_table()
    ok = h.home_type.isin(["detached", "attached_or_2to4"]) & h.year_built_bg.notna()
    X = features(h.floor_area_ft2, h.stories_est, h.home_type, h.year_built_bg)
    pr = _predict_df(X)
    h["cfm50_per_ft2"] = np.where(ok, pr.cfm50_per_ft2, np.nan)
    h["in_training_range"] = ok & pr.in_training_range
    h["cfm50"] = h.cfm50_per_ft2 * h.floor_area_ft2
    h["ach50_at_8ft"] = h.cfm50 * 60 / (h.floor_area_ft2 * CEILING_FT)
    h["scope_note"] = np.where(h.home_type == "apartment_5plus", "5+ units: outside the training data (1–4 unit homes)",
                      np.where(h.year_built_bg.isna(), "no block-group year built", ""))
    cols = ["fp_id", "lat", "lon", "bldg_name", "units", "home_type", "stories_est", "floor_area_ft2", "year_built_bg",
            "cfm50_per_ft2", "cfm50", "ach50_at_8ft", "in_training_range", "scope_note"]
    out = h[cols]
    out.to_parquet(PROCESSED / "leakage_ann_arbor.parquet", index=False)
    out.to_csv(PROCESSED / "leakage_ann_arbor.csv", index=False)
    return out


def predict_leakage(lat: float | None = None, lon: float | None = None, address: str | None = None) -> dict:
    if address:
        g = census.geocode(address)
        if g is None:
            raise ValueError(f"could not geocode: {address}")
        lat, lon = g["lat"], g["lon"]
    p = PROCESSED / "leakage_ann_arbor.parquet"
    t = pd.read_parquet(p) if p.exists() else predict_all()
    d2 = (t.lat - lat) ** 2 + ((t.lon - lon) * np.cos(np.radians(lat))) ** 2
    r = t.loc[d2.idxmin()]
    dist_m = float(np.sqrt(d2.min()) * 111_000)
    art, val = _model()
    g = val["tests"]["grouped_leave_one_region_out"]
    sc = val["tests"]["year_built_scenarios"]
    return {
        "location": {"lat": lat, "lon": lon, "matched_house": {"lat": float(r.lat), "lon": float(r.lon), "distance_m": round(dist_m, 1)}},
        "estimate": {"cfm50": None if pd.isna(r.cfm50) else round(float(r.cfm50)),
                     "cfm50_per_ft2": None if pd.isna(r.cfm50_per_ft2) else round(float(r.cfm50_per_ft2), 3),
                     "ach50_at_8ft_ceiling": None if pd.isna(r.ach50_at_8ft) else round(float(r.ach50_at_8ft), 1)},
        "inputs": {"floor_area_ft2": round(float(r.floor_area_ft2)), "floor_area_source": "city footprint area × stories",
                   "stories": float(r.stories_est), "units": int(r.units), "home_type": r.home_type,
                   "home_type_source": "count of city mailing addresses inside the footprint",
                   "year_built": None if pd.isna(r.year_built_bg) else int(r.year_built_bg),
                   "year_built_source": "ACS 5-yr B25037 renter-occupied median, block group (per-house year built is not public)",
                   "block_group": block_group_of([r.lat], [r.lon])[0], "climate_zone": ANN_ARBOR_CLIMATE_ZONE},
        "in_training_range": bool(r.in_training_range), "scope_note": r.scope_note or None,
        "model": {"family": art["family"], "params": art["params"], "trained_on": "947 NY blower-door tests (NYSERDA 2014–15 + 2018)"},
        "accuracy": {"held_out_region_median_abs_error_true_year_built": round(g["families"][g["chosen"]]["medape"], 3),
                     "held_out_region_median_abs_error_with_ann_arbor_year_built_noise":
                         round(min(sc["c_noisy_year_built_trained_on_true"]["medape"], sc["c_noisy_year_built_trained_on_noisy"]["medape"]), 3),
                     "baseline_median_abs_error": round(g["families"]["baseline_median"]["medape"], 3),
                     "basis": "median absolute % error on CFM50, homes in New York regions held out of training"},
    }


if __name__ == "__main__":
    import sys
    if "--all" in sys.argv:
        t = predict_all()
        print(len(t), "houses;", t.in_training_range.sum(), "in training range")
        print(t[["cfm50_per_ft2", "ach50_at_8ft"]].describe().round(2))

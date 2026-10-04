"""Feature construction shared by training and prediction (keep the two in lockstep)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from model.climate import CDD_BASES_F, HDD_BASES_F

WEATHER = [f"hdd{b}_pd" for b in HDD_BASES_F] + [f"cdd{b}_pd" for b in CDD_BASES_F]
BUILDING = ["log_gfa", "year_built", "stories_max", "height_ft_max", "surface_to_volume", "fp_count",
            "fp_area_per_gfa"]
FEATURES = WEATHER + BUILDING


def weather_features(w: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=w.index)
    for b in HDD_BASES_F:
        out[f"hdd{b}_pd"] = w[f"hdd{b}"] / w["days"]
    for b in CDD_BASES_F:
        out[f"cdd{b}_pd"] = w[f"cdd{b}"] / w["days"]
    return out


def zero_weather(X: pd.DataFrame, which: str = "both") -> pd.DataFrame:
    """Counterfactual rows with no heating ('hdd'), no cooling ('cdd') or neither ('both') demand.
    prediction(X) − prediction(zero_weather(X, 'hdd')) = weather-driven heating; same for cooling."""
    Xn = X.copy()
    for c in WEATHER:
        if which == "both" or c.startswith(which):
            Xn[c] = 0.0
    return Xn


def building_features(b: pd.DataFrame | dict) -> pd.DataFrame:
    """b: gfa_ft2, year_built, stories_max, height_ft_max, surface_to_volume, fp_count, fp_area_ft2."""
    b = pd.DataFrame([b]) if isinstance(b, dict) else b
    out = pd.DataFrame(index=b.index)
    out["log_gfa"] = np.log(b["gfa_ft2"].astype(float))
    out["year_built"] = b["year_built"].astype(float)
    out["stories_max"] = b["stories_max"].astype(float)
    out["height_ft_max"] = b["height_ft_max"].astype(float)
    out["surface_to_volume"] = b["surface_to_volume"].astype(float)
    out["fp_count"] = b["fp_count"].astype(float)
    out["fp_area_per_gfa"] = b["fp_area_ft2"].astype(float) / b["gfa_ft2"].astype(float)
    return out

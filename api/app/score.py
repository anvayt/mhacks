"""Hidden Rent Score, letter grade, percentiles and hidden rent (PLAN.md §5)."""

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

BUILDINGS_HC = Path(__file__).resolve().parents[2] / "model" / "data" / "processed" / "buildings_hc.csv"
GRADES = "ABCDF"


@lru_cache
def peer_costs(building_type: str) -> np.ndarray:
    """Sorted annual heating + cooling $ per sq ft of the comparison set for this building type.
    ponytail: every type compares with P1's 591 scored Ann Arbor apartment buildings (typical-year $ for an 854 sq ft
    unit, model/data/processed/buildings_hc.csv); the city batch (P2-06) replaces this with all ~35k city buildings."""
    d = pd.read_csv(BUILDINGS_HC)
    d = d[d.heating_usd_yr > 0]  # $0 heating = tenant-metered heat (Sequoia Place, Hidden Valley Club); falsely "best"
    return np.sort(((d.heating_usd_yr + d.cooling_usd_yr) / d.unit_sqft).to_numpy())


def grade_of(score: int) -> str:
    for grade, low in (("A", 80), ("B", 60), ("C", 40), ("D", 20)):
        if score >= low:
            return grade
    return "F"


def score_for(annual_usd: float, sqft: float, building_type: str) -> dict:
    """score = 100 - percentile of this unit's cost per sq ft among peers (share that cost less; ties count half)."""
    peers = peer_costs(building_type)
    x = annual_usd / sqft
    cheaper = (np.searchsorted(peers, x, "left") + np.searchsorted(peers, x, "right")) / 2 / len(peers)
    score = int(round(100 * (1 - cheaper)))
    return {"score": score, "grade": grade_of(score),
            "percentile_peers": round(float(1 - cheaper), 3),  # share of peers that cost more: score 82 <-> 0.82
            "percentile_city": round(float(1 - cheaper), 3),  # same table until the city batch (P2-06) lands
            "hidden_rent_usd_mo": int(round((annual_usd - float(np.median(peers)) * sqft) / 12))}

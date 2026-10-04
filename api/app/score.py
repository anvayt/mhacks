"""Hidden Rent Score, letter grade, percentiles and hidden rent (PLAN.md §5)."""

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from app import city

BUILDINGS_HC = Path(__file__).resolve().parents[2] / "model" / "data" / "processed" / "buildings_hc.csv"
GRADES = "ABCDF"
MIN_PEERS = 30  # fewer same-type city buildings than this -> P1's 591-building table


@lru_cache
def _p1_buildings() -> np.ndarray:
    """P1's 591 scored Ann Arbor apartment buildings (typical-year $ for an 854 sq ft unit,
    model/data/processed/buildings_hc.csv): the fallback comparison set."""
    d = pd.read_csv(BUILDINGS_HC)
    d = d[d.heating_usd_yr > 0]  # $0 heating = tenant-metered heat (Sequoia Place, Hidden Valley Club); falsely "best"
    return np.sort(((d.heating_usd_yr + d.cooling_usd_yr) / d.unit_sqft).to_numpy())


@lru_cache
def peer_costs(building_type: str | None) -> np.ndarray:
    """Sorted annual heating + cooling $ per sq ft of the comparison set: every scored City of Ann Arbor building of
    the same type (P2-06 city batch, api/data/city_scores.csv, P1's model at default answers), or of every type for
    None. A type with fewer than MIN_PEERS city buildings falls back to P1's 591 apartment buildings."""
    rows = city.city_costs(building_type) if building_type else [r["cost_per_sqft"] for r in city._table()]
    return np.sort(np.array(rows)) if len(rows) >= MIN_PEERS else _p1_buildings()


@lru_cache
def peer_cooling(building_type: str) -> float | None:
    """Median cooling $ per sq ft of same-type city homes (annual − heating, api/data/city_scores.csv), for hidden
    rent when heat is included in the rent."""
    rows = [(r["annual_usd"] - r["heating_usd"]) / r["sqft"] for r in city._table() if r["type"] == building_type]
    return float(np.median(rows)) if rows else None


def grade_of(score: int) -> str:
    for grade, low in (("A", 80), ("B", 60), ("C", 40), ("D", 20)):
        if score >= low:
            return grade
    return "F"


def _cheaper(peers: np.ndarray, x: float) -> float:
    """Share of peers that cost less per sq ft than x (ties count half)."""
    return (np.searchsorted(peers, x, "left") + np.searchsorted(peers, x, "right")) / 2 / len(peers)


def score_for(annual_usd: float, sqft: float, building_type: str) -> dict:
    """score = 100 - percentile of this unit's cost per sq ft among same-type city buildings."""
    peers = peer_costs(building_type)
    x = annual_usd / sqft
    cheaper = _cheaper(peers, x)
    score = int(round(100 * (1 - cheaper)))
    return {"score": score, "grade": grade_of(score),
            "percentile_peers": round(float(1 - cheaper), 3),  # share of peers that cost more: score 82 <-> 0.82
            "percentile_city": round(float(1 - _cheaper(peer_costs(None), x)), 3),  # vs every city building
            "hidden_rent_usd_mo": int(round((annual_usd - float(np.median(peers)) * sqft) / 12))}

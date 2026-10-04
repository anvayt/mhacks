"""Simulated rental peers, ported from P3 build_map_fixture.py lookalike_pool/price_cloud.

NREL ResStock 2024.2 Michigan: same type, rented, decade ± one decade, 0.65–1.5 ×
unit size. Those are display matching choices, not validated uncertainty intervals.
The cloud is simulated Michigan homes, never local measured neighbors.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

from model.heating_cooling.building_model import TAU_C, TAU_H_ELEC, TAU_H_GAS
from model.heating_cooling.resstock_model import ANSWERS, BTYPES, MULTIFAMILY
from model.paths import PROCESSED

CLOUD_SAMPLE = 400  # P3 display budget; percentiles use all matching simulations.


@lru_cache(maxsize=1)
def _frame() -> pd.DataFrame:
    return pd.read_parquet(PROCESSED / "resstock_frame.parquet")


def _year(lat: float, lon: float, block_group: str | None) -> tuple[float, str]:
    """The same vintage sources/fallback as estimate_hc, without rerunning predictions."""
    from model.heating_cooling import service as hc
    from model.data_sources import census
    targets = hc._res()["targets"]
    bid = hc._find_benchmarked(lat, lon)
    if bid is not None and bid in targets.index:
        return float(targets.loc[bid, "year_built"]), "Ann Arbor benchmarking"
    year, source = census.median_year_built(block_group) if block_group else (None, None)
    if year is not None:
        return float(year), str(source)
    return float(targets.year_built.median()), "median of Ann Arbor benchmarked buildings (no usable block-group year)"


@lru_cache(maxsize=256)
def _weather_prices(lat: float, lon: float) -> tuple[float, float, float]:
    from model.heating_cooling import service as hc
    w = hc._weather(lat, lon, "normal")
    gas = w.month.map(lambda m: hc._price(m, "gas"))
    electric = w.month.map(lambda m: hc._price(m, "electric"))
    return (float((w[f"hdd{TAU_H_GAS}"] * gas).sum()),
            float((w[f"hdd{TAU_H_ELEC}"] * electric).sum()),
            float((w[f"cdd{TAU_C}"] * electric).sum()))


def price_cloud(pool: pd.DataFrame, lat: float, lon: float, unit_sqft: float, building_type: str) -> np.ndarray:
    """Simulated intensity × local degree-days × monthly prices × target unit area."""
    from model.heating_cooling import service as hc
    gas_w, electric_w, cool_w = _weather_prices(lat, lon)
    cal = hc._res()["resstock"]["calibration"]
    mf = building_type in MULTIFAMILY
    heat = np.where(pool.heating_fuel == "Natural Gas",
                    pool.heat_gas_per_hdd.to_numpy(float) * (cal["heat_gas"] if mf else 1.0) * gas_w,
                    pool.heat_elec_per_hdd.to_numpy(float) * cal["heat_elec"] * electric_w)
    cool = pool.cool_per_cdd.to_numpy(float) * (cal["cool"] if mf else 1.0) * cool_w
    return (heat + cool) * unit_sqft / 1000


def summarize_cloud(usd) -> dict:
    """Bound the plotted sample; retain full-pool percentiles and honest empty pools."""
    usd = np.asarray(usd, dtype=float)
    usd = np.sort(usd[np.isfinite(usd) & (usd >= 0)])
    if not len(usd):
        return {"count": 0, "usd_yr": [], "p10": None, "p50": None, "p90": None}
    idx = np.unique(np.linspace(0, len(usd) - 1, min(CLOUD_SAMPLE, len(usd))).round().astype(int))
    return {"count": int(len(usd)), "usd_yr": [round(float(v)) for v in usd[idx]],
            **{f"p{p}": round(float(np.percentile(usd, p))) for p in (10, 50, 90)}}


def lookalikes(lat: float, lon: float, unit_sqft: float, building_type: str,
               year_built: float | None = None, answers: dict | None = None,
               heating_fuel: str | None = None, block_group: str | None = None) -> dict:
    """Answers only narrow the pool, never widen an empty match or mutate cached data.

    `pool_size` is the full source frame size, matching P3's top-level metadata.
    """
    if building_type not in BTYPES:
        raise ValueError("unsupported building_type")
    if not np.isfinite(unit_sqft) or unit_sqft <= 0:
        raise ValueError("unit_sqft must be positive and finite")
    if not np.isfinite(lat) or not np.isfinite(lon) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise ValueError("lat/lon must be valid finite coordinates")
    if heating_fuel not in (None, "gas", "electric"):
        raise ValueError("heating_fuel must be gas or electric")
    if year_built is None:
        year_built, year_source = _year(lat, lon, block_group)
    else:
        year_source = "caller-supplied public-record/model year"
    d = _frame()
    if not np.isfinite(year_built):
        return {**summarize_cloud([]), "pool_size": len(d), "rule": "No usable year built; matching vintage is unavailable."}
    lo_yr, hi_yr = (year_built // 10) * 10 - 10, (year_built // 10) * 10 + 19
    lo_ft, hi_ft = round(unit_sqft * .65), round(unit_sqft * 1.5)
    pool = d[(d.btype == building_type) & (d.renter == 1) & d.year_built.between(lo_yr, hi_yr)
             & d.sqft.between(lo_ft, hi_ft) & d.heating_fuel.isin(["Natural Gas", "Electricity"])]
    filters, unsupported = [], []
    if heating_fuel is not None:
        pool = pool[pool.heating_fuel == {"gas": "Natural Gas", "electric": "Electricity"}[heating_fuel]]
        filters.append(f"heating_fuel={heating_fuel}")
    for key, value in (answers or {}).items():
        if value is None:
            continue
        if key not in ANSWERS or key not in pool.columns:
            unsupported.append(key)
            continue
        number = float(value)
        if not np.isfinite(number):
            raise ValueError(f"{key} must be finite")
        pool = pool[pool[key] == number]
        filters.append(f"{key}={number:g}")
    rule = (f"ResStock 2024.2 Michigan simulated rented {building_type}; built {int(lo_yr)}–{int(hi_yr)} "
            f"({year_source}); {lo_ft:,}–{hi_ft:,} sq ft; gas/electric heat; priced at this unit's size and "
            "local typical-year weather with EIA Michigan prices. This is simulation spread, not a confidence interval.")
    if filters:
        rule += " Matching answers: " + ", ".join(filters) + "."
    if unsupported:
        rule += " No matching filter available for: " + ", ".join(unsupported) + "."
    cloud = summarize_cloud(price_cloud(pool, lat, lon, unit_sqft, building_type)) if len(pool) else summarize_cloud([])
    if cloud["count"] < len(pool):
        rule += f" Excluded {len(pool) - cloud['count']} rows with invalid simulated costs."
    return {**cloud, "pool_size": int(len(d)), "rule": rule}

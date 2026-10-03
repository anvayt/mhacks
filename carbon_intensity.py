"""Compute average grid carbon intensity (gCO2/kWh) from a generation fuel mix.

    CI = sum(gen_f * EF_f) / sum(gen_f)

Works on EIA-930 fuel codes (COL, NG, ...) and MISO real-time fuel-mix labels
("Coal", "Natural Gas", ...). Both are normalized to one canonical fuel set so
training labels (EIA-930 history) and live values (MISO feed) stay consistent.

This is *average*, generation-based intensity for the balancing area. It ignores
imports/exports and is not a marginal (MOER) signal.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Mapping

# Lifecycle factors, IPCC AR5 medians (gCO2eq/kWh). Oil has no AR5 median;
# "other" is an assumption for mixed/unknown generation.
LIFECYCLE_EF = {
    "coal": 820,
    "gas": 490,
    "oil": 650,
    "biomass": 230,
    "solar": 48,
    "geothermal": 38,
    "hydro": 24,
    "nuclear": 12,
    "wind": 11,
    "other": 450,
}

# Direct (smokestack) factors, approximate US fleet averages in the style of
# eGRID (gCO2/kWh). Biomass treated as biogenic (0). Swap in MISO-specific
# eGRID rates for better accuracy.
DIRECT_EF = {
    "coal": 1000,
    "gas": 420,
    "oil": 850,
    "biomass": 0,
    "solar": 0,
    "geothermal": 0,
    "hydro": 0,
    "nuclear": 0,
    "wind": 0,
    "other": 450,
}

FACTORS = {"lifecycle": LIFECYCLE_EF, "direct": DIRECT_EF}

# Storage re-emits energy generated earlier; counting it would double-count.
# It is dropped from both numerator and denominator.
STORAGE = "storage"

# Source label (lowercased) -> canonical fuel. Covers EIA-930 codes and MISO labels.
ALIASES = {
    # EIA-930
    "col": "coal",
    "ng": "gas",
    "oil": "oil",
    "nuc": "nuclear",
    "wat": "hydro",
    "sun": "solar",
    "snb": "solar",  # solar with integrated battery
    "wnd": "wind",
    "wnb": "wind",  # wind with integrated battery
    "geo": "geothermal",
    "oth": "other",
    "unk": "other",
    "oes": "other",
    "bat": STORAGE,
    "ps": STORAGE,
    # MISO real-time fuel mix / gridstatus column names
    "coal": "coal",
    "natural gas": "gas",
    "gas": "gas",
    "nuclear": "nuclear",
    "hydro": "hydro",
    "solar": "solar",
    "wind": "wind",
    "other": "other",
    "storage": STORAGE,
    "biomass": "biomass",
    "geothermal": "geothermal",
}


def normalize_mix(mix: Mapping[str, float]) -> dict[str, float]:
    """Map source fuel labels to canonical fuels and sum duplicates.

    Raises ValueError on unknown labels so a schema change in a feed shows up
    immediately instead of silently skewing the intensity.
    """
    out: dict[str, float] = {}
    for label, mwh in mix.items():
        fuel = ALIASES.get(label.strip().lower())
        if fuel is None:
            raise ValueError(f"Unknown fuel label {label!r}; add it to ALIASES")
        if mwh is None or mwh != mwh:  # None or NaN
            continue
        out[fuel] = out.get(fuel, 0.0) + float(mwh)
    return out


def carbon_intensity(mix: Mapping[str, float], basis: str = "lifecycle") -> float | None:
    """Average carbon intensity (gCO2/kWh) for one interval's fuel mix (MW or MWh).

    Negative values (e.g. storage charging, station load) are clipped to zero.
    Returns None if there is no positive generation.
    """
    factors = FACTORS[basis]
    gen = {
        fuel: max(mwh, 0.0)
        for fuel, mwh in normalize_mix(mix).items()
        if fuel != STORAGE
    }
    total = sum(gen.values())
    if total <= 0:
        return None
    return sum(mwh * factors[fuel] for fuel, mwh in gen.items()) / total


def add_carbon_intensity(df, fuel_columns=None, basis: str = "lifecycle", column: str = "carbon_intensity"):
    """Return a copy of a wide pandas DataFrame (one row per interval, one column
    per fuel) with a carbon-intensity column added.

    fuel_columns defaults to every column whose name is a known fuel label.
    """
    if fuel_columns is None:
        fuel_columns = [c for c in df.columns if str(c).strip().lower() in ALIASES]
    out = df.copy()
    out[column] = [
        carbon_intensity(row, basis) for row in df[fuel_columns].to_dict("records")
    ]
    return out


# ---------------------------------------------------------------------------
# EIA-930 data access
#
# Fetches hourly data from the EIA API v2 (free key: https://www.eia.gov/opendata/)
# and caches it per calendar month under data/eia930/, so a backtest re-run
# makes no API calls. Months older than REVISION_WINDOW are cached for good;
# newer ones are re-fetched because BAs revise recent hours.
# ---------------------------------------------------------------------------

EIA_API = "https://api.eia.gov/v2/electricity/rto"
CACHE_DIR = Path(__file__).resolve().parent / "data" / "eia930"
REVISION_WINDOW = timedelta(days=7)
PAGE_SIZE = 5000  # EIA API maximum rows per request

# region-data type codes -> column names (avoids clashing with the NG fuel code)
REGION_COLUMNS = {
    "D": "demand",
    "DF": "demand_forecast",
    "NG": "net_generation",
    "TI": "interchange",
}


def _api_key(api_key: str | None) -> str:
    key = api_key or os.environ.get("EIA_API_KEY") or _dotenv().get("EIA_API_KEY")
    if not key:
        raise RuntimeError("Set EIA_API_KEY in .env or the environment (free at https://www.eia.gov/opendata/)")
    return key


def _dotenv() -> dict[str, str]:
    """KEY=value pairs from the repo's .env, if present."""
    path = Path(__file__).resolve().parent / ".env"
    if not path.exists():
        return {}
    out = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.removeprefix("export ").split("=", 1)
            out[k.strip()] = v.strip().strip("'\"")
    return out


def _fetch_route(route: str, start: datetime, end: datetime, respondent: str, api_key: str) -> list[dict]:
    """All rows of an EIA-930 route for [start, end), following pagination."""
    import requests

    rows: list[dict] = []
    offset = 0
    while True:
        params = [
            ("api_key", api_key),
            ("frequency", "hourly"),
            ("data[0]", "value"),
            ("facets[respondent][]", respondent),
            ("start", start.strftime("%Y-%m-%dT%H")),
            ("end", (end - timedelta(hours=1)).strftime("%Y-%m-%dT%H")),
            ("sort[0][column]", "period"),
            ("sort[0][direction]", "asc"),
            ("offset", offset),
            ("length", PAGE_SIZE),
        ]
        resp = requests.get(f"{EIA_API}/{route}/data/", params=params, timeout=60)
        resp.raise_for_status()
        page = resp.json()["response"]["data"]
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            return rows
        offset += PAGE_SIZE


def _rows_to_wide(rows: list[dict], key_field: str, rename: Mapping[str, str] | None = None):
    """Long EIA rows -> wide DataFrame indexed by UTC hour, one column per key."""
    import pandas as pd

    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["period"] = pd.to_datetime(df["period"], format="%Y-%m-%dT%H", utc=True)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    wide = df.pivot_table(index="period", columns=key_field, values="value", aggfunc="sum")
    wide.columns.name = None
    if rename:
        wide = wide.rename(columns=rename)
    return wide.sort_index()


def _month_starts(start: datetime, end: datetime):
    m = start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    while m < end:
        nxt = (m.replace(day=28) + timedelta(days=4)).replace(day=1)
        yield m, nxt
        m = nxt


def _fetch_cached(route, key_field, rename, start, end, respondent, api_key, refresh):
    import pandas as pd

    now = datetime.now(timezone.utc)
    frames = []
    for m_start, m_end in _month_starts(start, end):
        path = CACHE_DIR / respondent / f"{route}_{m_start:%Y-%m}.pkl"
        final = m_end < now - REVISION_WINDOW
        if path.exists() and final and not refresh:
            frames.append(pd.read_pickle(path))
            continue
        # Future hours only matter for demand_forecast; cap the request there.
        wide = _rows_to_wide(
            _fetch_route(route, m_start, min(m_end, now + timedelta(days=2)), respondent, _api_key(api_key)),
            key_field,
            rename,
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        wide.to_pickle(path)
        frames.append(wide)
    out = pd.concat([f for f in frames if not f.empty]) if frames else pd.DataFrame()
    return out[(out.index >= start) & (out.index < end)] if not out.empty else out


def fetch_fuel_mix(start: datetime, end: datetime, respondent: str = "MISO", api_key: str | None = None, refresh: bool = False):
    """Hourly net generation by fuel (MWh), one column per EIA-930 fuel code."""
    return _fetch_cached("fuel-type-data", "fueltype", None, start, end, respondent, api_key, refresh)


def fetch_region_data(start: datetime, end: datetime, respondent: str = "MISO", api_key: str | None = None, refresh: bool = False):
    """Hourly demand, day-ahead demand forecast, net generation and interchange (MWh)."""
    return _fetch_cached("region-data", "type", REGION_COLUMNS, start, end, respondent, api_key, refresh)


def load_history(
    start: datetime,
    end: datetime,
    respondent: str = "MISO",
    basis: str = "lifecycle",
    api_key: str | None = None,
    refresh: bool = False,
):
    """One hourly, gap-filled (NaN) UTC frame with everything the model needs.

    Columns: one per EIA-930 fuel code (MWh), demand, demand_forecast,
    net_generation, interchange, and carbon_intensity (gCO2/kWh, NaN where
    the fuel mix is missing, e.g. future hours that only have a demand forecast).
    """
    import pandas as pd

    start = start.astimezone(timezone.utc)
    end = end.astimezone(timezone.utc)
    fuels = fetch_fuel_mix(start, end, respondent, api_key, refresh)
    region = fetch_region_data(start, end, respondent, api_key, refresh)
    index = pd.date_range(pd.Timestamp(start).ceil("h"), pd.Timestamp(end), freq="h", inclusive="left")
    hist = fuels.join(region, how="outer").reindex(index)
    return with_carbon_intensity(hist, basis)


def with_carbon_intensity(hist, basis: str = "lifecycle"):
    """Add carbon_intensity from the fuel-code columns of an hourly frame."""
    fuel_cols = [c for c in hist.columns if str(c).strip().lower() in ALIASES and c not in REGION_COLUMNS.values()]
    out = add_carbon_intensity(hist, fuel_cols, basis)
    no_mix = hist[fuel_cols].isna().all(axis=1)
    out.loc[no_mix, "carbon_intensity"] = float("nan")
    return out


if __name__ == "__main__":
    windy_night = {"COL": 18_000, "NG": 15_000, "NUC": 11_000, "WND": 22_000, "SUN": 0, "WAT": 800}
    calm_evening = {"Coal": 32_000, "Natural Gas": 38_000, "Nuclear": 11_000, "Wind": 3_000, "Solar": 1_500, "Other": 1_000, "Storage": 500}

    for name, mix in [("windy night (EIA codes)", windy_night), ("calm evening (MISO labels)", calm_evening)]:
        lc = carbon_intensity(mix, "lifecycle")
        dr = carbon_intensity(mix, "direct")
        print(f"{name:28s} lifecycle={lc:6.1f}  direct={dr:6.1f} gCO2/kWh")

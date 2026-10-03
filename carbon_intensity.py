"""Compute average grid carbon intensity (gCO2/kWh) from a generation fuel mix.

    CI = sum(gen_f * EF_f) / sum(gen_f)

Works on EIA-930 fuel codes (COL, NG, ...) and MISO real-time fuel-mix labels
("Coal", "Natural Gas", ...). Both are normalized to one canonical fuel set so
training labels (EIA-930 history) and live values (MISO feed) stay consistent.

This is *average*, generation-based intensity for the balancing area. It ignores
imports/exports and is not a marginal (MOER) signal.
"""

from __future__ import annotations

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


if __name__ == "__main__":
    windy_night = {"COL": 18_000, "NG": 15_000, "NUC": 11_000, "WND": 22_000, "SUN": 0, "WAT": 800}
    calm_evening = {"Coal": 32_000, "Natural Gas": 38_000, "Nuclear": 11_000, "Wind": 3_000, "Solar": 1_500, "Other": 1_000, "Storage": 500}

    for name, mix in [("windy night (EIA codes)", windy_night), ("calm evening (MISO labels)", calm_evening)]:
        lc = carbon_intensity(mix, "lifecycle")
        dr = carbon_intensity(mix, "direct")
        print(f"{name:28s} lifecycle={lc:6.1f}  direct={dr:6.1f} gCO2/kWh")

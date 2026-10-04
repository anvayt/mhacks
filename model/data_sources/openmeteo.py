"""Open-Meteo daily temperature (no key).

- Archive (ERA5 / ERA5-Land reanalysis, 1940-present, ~5 day lag): https://open-meteo.com/en/docs/historical-weather-api
- Forecast (16 days): https://open-meteo.com/en/docs
- Seasonal (ECMWF SEAS5 ensemble, ~7 months): https://open-meteo.com/en/docs/seasonal-forecast-api
Coordinates are rounded to 0.05° (~5 km) for caching; local 800 m detail comes from PRISM (see model/climate.py).
"""
import datetime as dt

import numpy as np
import pandas as pd

from model.data_sources.http import get_json

ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
FORECAST = "https://api.open-meteo.com/v1/forecast"
SEASONAL = "https://seasonal-api.open-meteo.com/v1/seasonal"


def _r(x: float) -> float:
    return round(round(x / 0.05) * 0.05, 2)


def daily_archive(lat: float, lon: float, start: str, end: str) -> pd.DataFrame:
    """Daily mean/min/max 2 m temperature (°C), local dates."""
    js = get_json(ARCHIVE, {"latitude": _r(lat), "longitude": _r(lon), "start_date": start, "end_date": end,
                            "daily": "temperature_2m_mean,temperature_2m_min,temperature_2m_max",
                            "timezone": "America/New_York"}, namespace="openmeteo")
    d = js["daily"]
    return pd.DataFrame({"date": pd.to_datetime(d["time"]), "tmean_c": d["temperature_2m_mean"],
                         "tmin_c": d["temperature_2m_min"], "tmax_c": d["temperature_2m_max"]}).dropna()


def daily_forecast(lat: float, lon: float) -> pd.DataFrame:
    """Next 16 days (cached 6 h)."""
    js = get_json(FORECAST, {"latitude": _r(lat), "longitude": _r(lon), "forecast_days": 16,
                             "daily": "temperature_2m_mean,temperature_2m_min,temperature_2m_max",
                             "timezone": "America/New_York"}, ttl_s=6 * 3600, namespace="openmeteo")
    d = js["daily"]
    return pd.DataFrame({"date": pd.to_datetime(d["time"]), "tmean_c": d["temperature_2m_mean"],
                         "tmin_c": d["temperature_2m_min"], "tmax_c": d["temperature_2m_max"]}).dropna()


def daily_seasonal(lat: float, lon: float) -> pd.DataFrame:
    """SEAS5 ensemble-mean daily temperature for the coming months (cached 24 h)."""
    js = get_json(SEASONAL, {"latitude": _r(lat), "longitude": _r(lon), "forecast_days": 183,
                             "daily": "temperature_2m_max,temperature_2m_min",
                             "timezone": "America/New_York"}, ttl_s=24 * 3600, namespace="openmeteo")
    d = js["daily"]
    df = pd.DataFrame({"date": pd.to_datetime(d["time"])})
    for v in ("max", "min"):
        cols = [k for k in d if k.startswith(f"temperature_2m_{v}")]
        df[f"t{v}_c"] = np.nanmean(np.array([np.array(d[k], dtype=float) for k in cols]), axis=0)
    df["tmean_c"] = (df.tmax_c + df.tmin_c) / 2
    df["n_members"] = len(cols)
    return df.dropna(subset=["tmean_c"])


def yesterday() -> str:
    return (dt.date.today() - dt.timedelta(days=6)).isoformat()

"""Open-Meteo daily temperature (no key).

- Archive (ERA5 / ERA5-Land reanalysis, 1940-present, ~5 day lag): https://open-meteo.com/en/docs/historical-weather-api
- Forecast (16 days): https://open-meteo.com/en/docs
- Seasonal (ECMWF SEAS5 ensemble, ~7 months): https://open-meteo.com/en/docs/seasonal-forecast-api
Coordinates snap to a 0.1° grid (ERA5-Land resolution; ERA5 itself is 0.25°), so a whole city shares a few
reanalysis cells. Local 800 m detail comes from PRISM (see model/climate.py).
"""
import datetime as dt

import numpy as np
import pandas as pd

from model.data_sources.http import get_json

ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
FORECAST = "https://api.open-meteo.com/v1/forecast"
SEASONAL = "https://seasonal-api.open-meteo.com/v1/seasonal"


def _r(x: float) -> float:
    return round(round(x / 0.1) * 0.1, 2)


ARCHIVE_START = "1991-01-01"


def _fetch_archive(lat_r: float, lon_r: float, start: str, end: str) -> pd.DataFrame:
    js = get_json(ARCHIVE, {"latitude": lat_r, "longitude": lon_r, "start_date": start, "end_date": end,
                            "daily": "temperature_2m_mean,temperature_2m_min,temperature_2m_max",
                            "timezone": "America/New_York"}, namespace="openmeteo", retries=4, cache=False)
    d = js["daily"]
    return pd.DataFrame({"date": pd.to_datetime(d["time"]), "tmean_c": d["temperature_2m_mean"],
                         "tmin_c": d["temperature_2m_min"], "tmax_c": d["temperature_2m_max"]}).dropna()


def _archive_full(lat_r: float, lon_r: float) -> pd.DataFrame:
    """1991→(today−6d) daily series for one reanalysis cell, stored as one parquet per cell.
    The first call downloads the whole history once. Later calls only fetch the missing tail days, at most
    once per day, so a warm cache makes zero requests for past data."""
    from model.paths import CACHE
    path = CACHE / "openmeteo_full" / f"{lat_r:.2f}_{lon_r:.2f}.parquet"
    if not path.exists():
        df = _fetch_archive(lat_r, lon_r, ARCHIVE_START, yesterday())
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(path, index=False)
        return df
    df = pd.read_parquet(path)
    last = df["date"].max().date()
    fresh = (dt.datetime.now().timestamp() - path.stat().st_mtime) < 86400
    if fresh or last >= dt.date.fromisoformat(yesterday()):
        return df
    try:
        tail = _fetch_archive(lat_r, lon_r, (last + dt.timedelta(days=1)).isoformat(), yesterday())
        df = pd.concat([df, tail]).drop_duplicates("date", keep="last").sort_values("date").reset_index(drop=True)
        df.to_parquet(path, index=False)
    except Exception:
        path.touch()  # offline: keep the stale series and don't retry until tomorrow
    return df


def daily_archive(lat: float, lon: float, start: str, end: str) -> pd.DataFrame:
    """Daily mean/min/max 2 m temperature (°C), local dates, sliced from the cached full series."""
    df = _archive_full(_r(lat), _r(lon))
    return df[(df.date >= pd.Timestamp(start)) & (df.date <= pd.Timestamp(end))].reset_index(drop=True)


def daily_forecast(lat: float, lon: float) -> pd.DataFrame:
    """Next 16 days (cached 6 h)."""
    js = get_json(FORECAST, {"latitude": _r(lat), "longitude": _r(lon), "forecast_days": 16,
                             "daily": "temperature_2m_mean,temperature_2m_min,temperature_2m_max",
                             "timezone": "America/New_York"}, ttl_s=6 * 3600, namespace="openmeteo")
    d = js["daily"]
    return pd.DataFrame({"date": pd.to_datetime(d["time"]), "tmean_c": d["temperature_2m_mean"],
                         "tmin_c": d["temperature_2m_min"], "tmax_c": d["temperature_2m_max"]}).dropna()


def daily_seasonal(lat: float, lon: float) -> pd.DataFrame:
    """SEAS5 daily mean temperature per ensemble member (long format: date, member, tmean_c), cached 24 h.
    Degree-days must be computed per member and then averaged (not from the ensemble-mean temperature)."""
    js = get_json(SEASONAL, {"latitude": _r(lat), "longitude": _r(lon), "forecast_days": 183,
                             "daily": "temperature_2m_max,temperature_2m_min",
                             "timezone": "America/New_York"}, ttl_s=24 * 3600, namespace="openmeteo")
    d = js["daily"]
    dates = pd.to_datetime(d["time"])
    frames = []
    for k in d:
        if not k.startswith("temperature_2m_max"):
            continue
        suffix = k[len("temperature_2m_max"):]
        tmax = np.array(d[k], dtype=float)
        tmin = np.array(d["temperature_2m_min" + suffix], dtype=float)
        frames.append(pd.DataFrame({"date": dates, "member": suffix.strip("_") or "member00",
                                    "tmean_c": (tmax + tmin) / 2}))
    return pd.concat(frames).dropna(subset=["tmean_c"])


def yesterday() -> str:
    return (dt.date.today() - dt.timedelta(days=6)).isoformat()

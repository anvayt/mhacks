"""GET /forecast/{session_id}: the next 7 days of heating + cooling $ for a saved session, the numbers behind P4's
weather-triggered reminder texts (the bot owns wording, scheduling, opt-in and quiet hours).

P1's model serves monthly weather only (/hc/weather), so the daily temperatures come from Open-Meteo directly
(free, no key): the 7-day forecast, and the 1991-2020 daily history (ERA5 reanalysis) for "typical" and for the
alert thresholds. Every dollar is P1's: the forecast month's $ (GET /hc/estimate?mode=forecast) divided by that
month's degree-days (GET /hc/weather?mode=forecast) gives $ per degree-day for this unit, which is how P1 builds
the month in the first place (energy = intensity x degree-days x floor area; model/heating_cooling/service.py).
"""

import datetime as dt
import json
from functools import lru_cache
from math import isfinite
from statistics import mean, quantiles
from uuid import uuid4
from zoneinfo import ZoneInfo

import httpx
from fastapi import APIRouter

from app import sessions
from app.estimate import MODEL_BASE_URL, _fail, session_params
from app.geo import DATA_DIR

router = APIRouter()

FORECAST = "https://api.open-meteo.com/v1/forecast"  # https://open-meteo.com/en/docs
ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"  # https://open-meteo.com/en/docs/historical-weather-api
YEARS = range(1991, 2021)  # P1's normal period (model/climate.py NORMAL_YEARS)
# P1's pooled balance points, deg F (model/heating_cooling/building_model.py TAU_H_GAS, TAU_H_ELEC, TAU_C)
TAU_H = {"gas": 60, "electric": 55}
TAU_C = 65
MODEL_DOWN = "Our heating and cooling model isn't reachable right now. Try again in a few minutes."
FORECAST_DOWN = "The weather forecast isn't reachable right now. Try again in a few minutes."
METHOD = (
    "Days: Open-Meteo's daily forecast at P1's 0.1 deg grid cell, shifted by P1's PRISM 800 m offset for the month "
    "(model/climate.py). Daily $ = P1's forecast-month $ (GET /hc/estimate?mode=forecast, this unit, EIA Michigan "
    "monthly prices) x the day's degree-days / P1's forecast-month degree-days (GET /hc/weather?mode=forecast), at "
    "P1's base temperatures: heating HDD60 (gas) or HDD55 (electric), cooling CDD65, or the building's own "
    "change-point balance points on the metered path. week = sum of the returned days. normal_total_usd = the same returned calendar "
    "dates priced the same way in each year 1991-2020 (Open-Meteo ERA5 archive, same shift), averaged; "
    "vs_normal_pct = week / normal - 1, in percent. Alerts: cold_snap = the day's mean temperature is below the 10th "
    "percentile of daily means within 7 days of that date in 1991-2020 (colder than 9 in 10 such days) and the day "
    "has a heating cost; heat_wave = above the 90th percentile and the day has a cooling cost; costly_week = the "
    "week's total is above the 90th percentile of the same dates' totals in 1991-2020 (costliest 1 week in 10). "
    "Up to 7 days: P1 notes that beyond ~2 weeks the weather is not a skilful forecast, and daily forecasts lose "
    "skill with each day ahead. On a network outage, a last-good daily forecast is used only if at least 3 "
    "complete days remain; stale_as_of is its original UTC fetch time."
)
SOURCE = ("P1 heating + cooling model (GET /hc/estimate?mode=forecast, /hc/weather?mode=forecast); Open-Meteo "
          "forecast API and historical weather API (ERA5), open-meteo.com; PRISM Climate Group 800 m normals via P1")


def _get(url: str, params: dict, code: str, message: str) -> dict:
    try:
        r = httpx.get(url, params=params, timeout=180)  # P1's first forecast for a cell downloads SEAS5 once
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError:
        raise _fail(503, code, message)


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _daily(raw: dict) -> dict:
    """Validate the fields we consume before replacing or trusting the last-good response."""
    daily = raw["daily"]
    columns = [daily[k] for k in ("time", "temperature_2m_mean", "temperature_2m_min", "temperature_2m_max")]
    if not all(isinstance(c, list) for c in columns) or not columns[0] or len({len(c) for c in columns}) != 1:
        raise ValueError("incomplete daily forecast")
    for date in columns[0]:
        dt.date.fromisoformat(date)
    if any(v is not None and (type(v) not in (int, float) or not isfinite(v)) for c in columns[1:] for v in c):
        raise ValueError("invalid daily temperature")
    return daily


def _daily_forecast(lat: float, lon: float) -> tuple[dict, str | None]:
    """Live Open-Meteo response per P1 grid cell; on network failure use its last successful fetch.

    Raw response and UTC fetch timestamp live under git-ignored /data. A fallback never refreshes
    that timestamp. The endpoint drops elapsed America/New_York dates and requires 3 usable days.
    """
    path = DATA_DIR / f"openmeteo_forecast_{lat:.2f}_{lon:.2f}.json"
    try:
        r = httpx.get(FORECAST, params={"latitude": lat, "longitude": lon, "forecast_days": 7,
                      "timezone": "America/New_York",
                      "daily": "temperature_2m_mean,temperature_2m_min,temperature_2m_max"}, timeout=180)
        r.raise_for_status()
        raw = r.json()
        daily = _daily(raw)
    except (httpx.TimeoutException, httpx.NetworkError):
        try:
            saved = json.loads(path.read_text())
            if dt.datetime.fromisoformat(saved["fetched_at"]).tzinfo is None:
                raise ValueError("cache timestamp has no timezone")
            return _daily(saved["response"]), saved["fetched_at"]
        except (OSError, ValueError, KeyError, TypeError):
            raise _fail(503, "forecast_unavailable", FORECAST_DOWN)
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        raise _fail(503, "forecast_unavailable", FORECAST_DOWN)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(f".{uuid4().hex}.tmp")  # distinct concurrent requests cannot truncate each other's cache
    tmp.write_text(json.dumps({"fetched_at": _now().isoformat(), "response": raw}))
    tmp.replace(path)
    return daily, None


def _grid(x: float) -> float:  # Open-Meteo cell as P1 snaps it (model/data_sources/openmeteo.py _r)
    return round(round(x / 0.1) * 0.1, 2)


def _f(c: float) -> float:
    return c * 9 / 5 + 32


@lru_cache(maxsize=16)
def _history(lat: float, lon: float) -> dict[dt.date, float]:
    """1991-2020 daily mean temperature (deg C) at one Open-Meteo cell, cached on disk: the first call for a cell
    downloads 30 years (~800 of Open-Meteo's 10,000 free daily calls; a few cells cover Ann Arbor)."""
    path = DATA_DIR / f"openmeteo_daily_1991_2020_{lat:.2f}_{lon:.2f}.json"
    if not path.exists():
        d = _get(ARCHIVE, {"latitude": lat, "longitude": lon, "start_date": f"{YEARS[0]}-01-01",
                           "end_date": f"{YEARS[-1]}-12-31", "daily": "temperature_2m_mean",
                           "timezone": "America/New_York"}, "forecast_unavailable", FORECAST_DOWN)["daily"]
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(d))
    d = json.loads(path.read_text())
    return {dt.date.fromisoformat(t): v for t, v in zip(d["time"], d["temperature_2m_mean"]) if v is not None}


def _same_day(d: dt.date, year: int) -> dt.date:
    try:
        return d.replace(year=year)
    except ValueError:  # Feb 29 in a non-leap year
        return d.replace(year=year, day=28)


def _bases(hc: dict) -> tuple[int | None, int | None]:
    """(heating, cooling) balance points P1 used for this building; None = no such term in its model."""
    d = hc["model_detail"]
    if hc["method"] == "metered":  # the building's own change-point fit (service._monthly_metered)
        h, c = (d["gas_fit"] if d["heating_fuel"] == "gas" else d["elec_fit"])["tau_h"], d["elec_fit"]["tau_c"]
        return (int(h) if h else None), (int(c) if c else None)
    return TAU_H[d["heating_fuel"]], TAU_C


@router.get("/forecast/{session_id}")
def forecast(session_id: str) -> dict:
    """Up to 7 days of heating + cooling $ vs a typical year, plus alerts. 404 not_found, 503 model/forecast down."""
    s = sessions.get(session_id)
    if s is None:
        raise _fail(404, "not_found", "That session expired. Send the listing again.")
    p = session_params(s)  # the renter's answers too (heating_fuel sets the heating base)
    no_ac = p.get("cooling_code") == 0  # never sent to P1 (out of its training data); cooling stays $0, as in /estimate
    p = {k: v for k, v in p.items() if v is not None and not (no_ac and k == "cooling_code")}
    hc = _get(f"{MODEL_BASE_URL}/hc/estimate", {**p, "mode": "forecast"}, "model_unavailable", MODEL_DOWN)
    wx = _get(f"{MODEL_BASE_URL}/hc/weather", {"lat": p["lat"], "lon": p["lon"], "mode": "forecast"},
              "model_unavailable", MODEL_DOWN)
    lat, lon = _grid(p["lat"]), _grid(p["lon"])
    fc, stale_as_of = _daily_forecast(lat, lon)
    today = _now().astimezone(ZoneInfo("America/New_York")).date()
    hist = _history(lat, lon)

    hb, cb = _bases(hc)
    cb = None if no_ac else cb
    usd = {m["month"]: m for m in hc["months"]}  # 12 consecutive months, so the month number is unique
    # ponytail: P1 rounds month $ to whole dollars, so a month of a few $ carries a few % to tens of % rounding
    rate = {}  # month -> ($ per heating degree-day, $ per cooling degree-day, PRISM offset deg C)
    for w in wx["monthly"]:
        hdd, cdd = w.get(f"hdd{hb}"), w.get(f"cdd{cb}")
        m = usd[w["month"]]
        rate[w["month"]] = (m["heating"]["usd"] / hdd if hdd else 0.0, m["cooling"]["usd"] / cdd if cdd else 0.0,
                            w["local_offset_c"])

    def cost(t_c: float, month: int) -> tuple[float, float]:  # (heating $, cooling $) for a day's raw mean temp
        rh, rc, off = rate[month]
        tf = _f(t_c + off)
        return rh * max(hb - tf, 0) if hb else 0.0, rc * max(tf - cb, 0) if cb else 0.0

    days, alerts = [], []
    for date, tmean, tmin, tmax in zip(fc["time"], fc["temperature_2m_mean"], fc["temperature_2m_min"],
                                       fc["temperature_2m_max"]):
        if None in (tmean, tmin, tmax):  # Open-Meteo leaves the last day blank sometimes
            continue
        d = dt.date.fromisoformat(date)
        if stale_as_of is not None and d < today:
            continue
        off = rate[d.month][2]
        h, c = cost(tmean, d.month)
        day = {"date": date, "low_f": round(_f(tmin + off)), "high_f": round(_f(tmax + off)),
               "heating_usd": round(h, 2), "cooling_usd": round(c, 2)}
        days.append(day)
        near = [t for y in YEARS for k in range(-7, 8) if (t := hist.get(_same_day(d, y) + dt.timedelta(k))) is not None]
        q = quantiles(near, n=10)
        lo, hi = q[0], q[-1]
        if tmean < lo and h > 0:
            alerts.append({"type": "cold_snap", "date": date, "detail": (
                f"Low of {day['low_f']}°F, colder than 9 in 10 days around this date (1991-2020). "
                f"Heating that day: about ${h:.2f}.")})
        if tmean > hi and c > 0:
            alerts.append({"type": "heat_wave", "date": date, "detail": (
                f"High of {day['high_f']}°F, hotter than 9 in 10 days around this date (1991-2020). "
                f"Cooling that day: about ${c:.2f}.")})

    if len(days) < (3 if stale_as_of is not None else 1):  # last-good fallback must still cover at least 3 days
        raise _fail(503, "forecast_unavailable", FORECAST_DOWN)
    dates = [dt.date.fromisoformat(x["date"]) for x in days]
    past = [sum(sum(cost(hist[_same_day(d, y)], d.month)) for d in dates) for y in YEARS]
    heating, cooling = round(sum(x["heating_usd"] for x in days), 2), round(sum(x["cooling_usd"] for x in days), 2)
    total, normal = round(heating + cooling, 2), mean(past)
    week = {"heating_usd": heating, "cooling_usd": cooling, "total_usd": total, "normal_total_usd": round(normal, 2),
            "vs_normal_pct": round((total / normal - 1) * 100) if normal else None}
    if total > quantiles(past, n=10)[-1]:
        alerts.append({"type": "costly_week", "date": days[0]["date"], "detail": (
            f"Heating and cooling this week: about ${total:.0f}, vs ${normal:.0f} in a typical year for these dates.")})
    return {"session_id": session_id, "days": days, "week": week, "alerts": alerts, "source": SOURCE, "method": METHOD,
            **({"stale_as_of": stale_as_of} if stale_as_of is not None else {})}


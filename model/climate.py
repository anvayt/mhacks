"""P1-03: localized weather and degree-days for a point (one 800 m PRISM cell).

How the pieces fit:
- **Daily variability** comes from Open-Meteo (ERA5 reanalysis for the past, the GFS/ECMWF blend for
  16 days ahead, and the ECMWF SEAS5 ensemble for ~6 months ahead). It sits on a ~5–25 km grid.
- **Local level** comes from PRISM 800 m monthly mean temperature. For each month we shift every day by
  `PRISM(cell, month) − mean(reanalysis days in that month)`. The daily shape is preserved and the monthly
  mean matches the 800 m cell. This is a standard delta-method downscaling.
- **Typical year**: PRISM 1991–2020 normals for the local level, and the 30 years of 1991–2020 reanalysis
  days for the shape. Degree-days are averaged across years (never computed from an average temperature).

Degree-day bases are in °F, as is conventional in US energy work (65 °F = 18.33 °C).
"""
from __future__ import annotations

import datetime as dt
from functools import lru_cache

import numpy as np
import pandas as pd

from model.data_sources import openmeteo, prism

HDD_BASES_F = (50, 55, 60, 65)
CDD_BASES_F = (65, 70, 75)
SEASONS = {"winter": (12, 1, 2), "spring": (3, 4, 5), "summer": (6, 7, 8), "fall": (9, 10, 11)}
MONTH_TO_SEASON = {m: s for s, ms in SEASONS.items() for m in ms}
NORMAL_YEARS = (1991, 2020)


def c_to_f(c):
    return np.asarray(c) * 9 / 5 + 32


def _degree_days(daily: pd.DataFrame) -> pd.DataFrame:
    """daily: date, tmean_c (local, already shifted) → adds hddXX / cddXX columns (°F-days)."""
    tf = c_to_f(daily["tmean_c"].to_numpy())
    out = daily.copy()
    for b in HDD_BASES_F:
        out[f"hdd{b}"] = np.clip(b - tf, 0, None)
    for b in CDD_BASES_F:
        out[f"cdd{b}"] = np.clip(tf - b, 0, None)
    return out


def _monthly(daily: pd.DataFrame) -> pd.DataFrame:
    dd = _degree_days(daily)
    g = dd.groupby([dd.date.dt.year.rename("year"), dd.date.dt.month.rename("month")])
    agg = {c: "sum" for c in dd.columns if c.startswith(("hdd", "cdd"))}
    agg.update(tmean_c="mean", date="count")
    m = g.agg(agg).rename(columns={"date": "days"}).reset_index()
    return m


@lru_cache(maxsize=256)
def _archive(lat_r: float, lon_r: float, start: str, end: str) -> pd.DataFrame:
    return openmeteo.daily_archive(lat_r, lon_r, start, end)


def _prism_offset(lat: float, lon: float, ym: str, reanalysis_mean_c: float) -> tuple[float, str]:
    """Local shift for one month: PRISM cell monthly mean minus reanalysis mean (°C)."""
    try:
        v = float(prism.sample("tmean", ym, lat, lon)[0])
        if np.isfinite(v):
            return v - reanalysis_mean_c, f"PRISM 800m {ym}"
    except Exception:
        pass
    return np.nan, "none"


@lru_cache(maxsize=64)
def _normal_offsets(lat: float, lon: float) -> tuple:
    """Per calendar month: PRISM 1991–2020 normal at the cell minus the reanalysis 1991–2020 mean."""
    hist = _archive(openmeteo._r(lat), openmeteo._r(lon), f"{NORMAL_YEARS[0]}-01-01", f"{NORMAL_YEARS[1]}-12-31")
    clim = hist.groupby(hist.date.dt.month)["tmean_c"].mean()
    offs = []
    for m in range(1, 13):
        try:
            v = float(prism.sample("tmean", f"norm{m:02d}", lat, lon)[0])
        except Exception:
            v = np.nan
        offs.append(v - clim[m] if np.isfinite(v) else 0.0)
    return tuple(offs)


def monthly_weather_years(lat: float, lon: float, years: list[int]) -> pd.DataFrame:
    """Observed months for the given calendar years, localized to the PRISM cell."""
    start, end = f"{min(years)}-01-01", min(f"{max(years)}-12-31", openmeteo.yesterday())
    daily = _archive(openmeteo._r(lat), openmeteo._r(lon), start, end).copy()
    norm_off = _normal_offsets(lat, lon)
    shifts, srcs = {}, {}
    for (y, m), grp in daily.groupby([daily.date.dt.year, daily.date.dt.month]):
        off, src = _prism_offset(lat, lon, f"{y}{m:02d}", grp.tmean_c.mean())
        if not np.isfinite(off):  # PRISM month not downloaded yet: fall back to the normal-based offset
            off, src = norm_off[m - 1], "PRISM 800m 1991-2020 normal offset"
        shifts[(y, m)], srcs[(y, m)] = off, src
    key = list(zip(daily.date.dt.year, daily.date.dt.month))
    daily["tmean_c"] = daily["tmean_c"].to_numpy() + np.array([shifts[k] for k in key])
    out = _monthly(daily)
    out["local_offset_c"] = [shifts[(y, m)] for y, m in zip(out.year, out.month)]
    out["level_source"] = [srcs[(y, m)] for y, m in zip(out.year, out.month)]
    return out[out.year.isin(years)].reset_index(drop=True)


def monthly_weather_normal(lat: float, lon: float) -> pd.DataFrame:
    """Typical year (1991–2020): 12 rows, degree-days averaged over the 30 years."""
    hist = _archive(openmeteo._r(lat), openmeteo._r(lon), f"{NORMAL_YEARS[0]}-01-01", f"{NORMAL_YEARS[1]}-12-31").copy()
    offs = np.array(_normal_offsets(lat, lon))
    hist["tmean_c"] = hist["tmean_c"].to_numpy() + offs[hist.date.dt.month.to_numpy() - 1]
    per_year = _monthly(hist)
    norm = per_year.drop(columns="year").groupby("month").mean().reset_index()
    norm["days"] = norm["days"].round().astype(int)
    norm["local_offset_c"] = offs
    norm["level_source"] = "PRISM 800m 1991-2020 normals + ERA5 1991-2020 daily shape"
    return norm


def monthly_weather_forecast(lat: float, lon: float, months_ahead: int = 12) -> pd.DataFrame:
    """Next `months_ahead` calendar months: 16-day forecast, then SEAS5 ensemble, then normals."""
    today = dt.date.today()
    offs = np.array(_normal_offsets(lat, lon))
    normal = monthly_weather_normal(lat, lon).set_index("month")

    fc = openmeteo.daily_forecast(lat, lon)[["date", "tmean_c"]].assign(member="fc")
    try:
        seas = openmeteo.daily_seasonal(lat, lon)
        seas = seas[seas.date > fc.date.max()]
    except Exception:
        seas = pd.DataFrame(columns=["date", "member", "tmean_c"])
    # past days of the current month come from the archive so the month is complete
    first = today.replace(day=1)
    past = openmeteo.daily_archive(lat, lon, first.isoformat(), openmeteo.yesterday()) if today.day > 7 else \
        pd.DataFrame(columns=["date", "tmean_c"])
    past = past[past.date < fc.date.min()][["date", "tmean_c"]] if len(past) else past

    rows = []
    y, m = today.year, today.month
    for _ in range(months_ahead):
        mstart = pd.Timestamp(y, m, 1)
        mend = mstart + pd.offsets.MonthEnd(0)
        ndays = mend.day
        known = pd.concat([past[(past.date >= mstart) & (past.date <= mend)],
                           fc[(fc.date >= mstart) & (fc.date <= mend)][["date", "tmean_c"]]])
        s = seas[(seas.date >= mstart) & (seas.date <= mend)]
        n_known = len(known)
        n_seas_days = s.date.nunique() if len(s) else 0
        known = known.assign(tmean_c=known.tmean_c + offs[m - 1])
        kdd = _degree_days(known) if n_known else None
        rec = {"year": y, "month": m, "days": ndays}
        cols = [f"hdd{b}" for b in HDD_BASES_F] + [f"cdd{b}" for b in CDD_BASES_F]
        n_rest = ndays - n_known
        if n_seas_days:
            sdd = _degree_days(s.assign(tmean_c=s.tmean_c + offs[m - 1]))
            per_member_day = sdd.groupby("member")[cols + ["tmean_c"]].mean().mean()  # avg over members of daily mean
            use_seas = min(n_rest, n_seas_days)
        else:
            per_member_day, use_seas = None, 0
        n_norm = n_rest - use_seas
        for c in cols + ["tmean_c"]:
            tot = (kdd[c].sum() if n_known else 0.0)
            if use_seas:
                tot += per_member_day[c] * use_seas
            tot += normal.loc[m, c] / normal.loc[m, "days"] * n_norm if c != "tmean_c" else normal.loc[m, "tmean_c"] * n_norm
            rec[c] = tot / ndays if c == "tmean_c" else tot
        rec["level_source"] = (f"{n_known}d observed/forecast, {use_seas}d SEAS5 ensemble, {n_norm}d PRISM normal"
                               " (all shifted to the PRISM 800m cell)")
        rec["local_offset_c"] = offs[m - 1]
        rows.append(rec)
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return pd.DataFrame(rows)


def monthly_weather(lat: float, lon: float, mode: str | int = "normal") -> pd.DataFrame:
    if mode == "normal":
        return monthly_weather_normal(lat, lon)
    if mode == "forecast":
        return monthly_weather_forecast(lat, lon)
    return monthly_weather_years(lat, lon, [int(mode)])


def seasonal(monthly: pd.DataFrame) -> pd.DataFrame:
    """Aggregate monthly weather (any of the modes) to the four seasons."""
    m = monthly.copy()
    m["season"] = m["month"].map(MONTH_TO_SEASON)
    sums = [c for c in m.columns if c.startswith(("hdd", "cdd"))] + ["days"]
    agg = m.groupby("season").apply(lambda g: pd.Series({
        **{c: g[c].sum() for c in sums},
        "tmean_c": np.average(g["tmean_c"], weights=g["days"])}), include_groups=False)
    agg["tmean_f"] = c_to_f(agg["tmean_c"])
    return agg.reindex(list(SEASONS)).reset_index()

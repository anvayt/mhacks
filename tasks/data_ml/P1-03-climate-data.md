```yaml
id: P1-03
title: Localized climate data (PRISM 800 m + daily reanalysis + normals + forecast)
owner: P1
status: done
branch: p1/heating-cooling
type: build
checkpoint: 1:00 AM GO/NO-GO
depends_on: []
blocks: [P1-05, P1-06]
merges: []
services_touched:
  - /model
services_read:
  - PRISM web service (services.nacse.org; each file is limited to one download per 24 h, so cache everything)
  - Open-Meteo archive + forecast + seasonal APIs (no key)
contract_change: none
```

## Goal
Temperature and degree-days **per building** (800 m grid cell), per month and per season (DJF/MAM/JJA/SON). Available for the past (2021–2023, to train against meters), a typical year (normals), and the future (forecast).

## Method
- Local monthly level: PRISM 800 m monthly `tmean` grid cell for the building (AN dataset).
- Daily shape: Open-Meteo ERA5 daily mean temperature at the city point. Shift each day by that month's PRISM-minus-reanalysis offset, then sum HDD/CDD (base 65°F / 18.3°C, plus other bases for the change-point fit).
- Typical year: a 1991–2020 daily climatology (Open-Meteo archive), shifted by the PRISM cell's offset.
- Forecast: Open-Meteo 16-day forecast plus its seasonal (ECMWF SEAS5) ensemble mean for the next ~6 months, with the same local offset.

## Outputs
- `model/data_sources/prism.py`, `model/data_sources/openmeteo.py`: download + cache + `point_value(lat, lon, …)`
- `model/climate.py`: `monthly_weather(lat, lon, year|"normal"|"forecast")` → DataFrame (month, tmean_c, hdd65, cdd65, …) and `seasonal_weather(...)`

## Done when
- [ ] PRISM cells for all benchmarked buildings extracted for 2021–2023
- [ ] Ann Arbor HDD65 for 2023 is within ~10% of NOAA/NASA POWER figures (cite them)
- [ ] Runs offline after the first download

## Handoff
- `model/climate.py`: `monthly_weather(lat, lon, "normal"|"forecast"|year)`, `seasonal(...)`. Degree-days at bases 50/55/60/65 °F (HDD) and 65/70/75 °F (CDD).
- `model/data_sources/prism.py` (800 m monthly grids 2021-01→2026-08 + 1991–2020 normals, cropped to MI, ~95 MB under `model/data/raw/prism`, git-ignored; re-fetch with `python -m model.scripts.fetch_prism`).
- `model/data_sources/openmeteo.py`: one cached 1991→today series per 0.1° cell, appended incrementally; forecast cached 6 h, SEAS5 cached 24 h. Every network call is logged to `model/data/cache/requests.log`.
- Ann Arbor typical year: HDD65 ≈ 6,475, CDD65 ≈ 643. Forecast = 16-day forecast → SEAS5 51-member ensemble (degree-days per member) → normals.
- Gap: no independent NOAA station check yet (tracked in P1-01).

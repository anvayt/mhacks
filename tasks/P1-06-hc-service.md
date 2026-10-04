```yaml
id: P1-06
title: Heating + cooling estimate service (Python API + dev HTTP server in /model)
owner: P1
status: in-progress
branch: p1/heating-cooling
type: build
checkpoint: 1:00 AM GO/NO-GO
depends_on: [P1-03, P1-05]
blocks: []                 # P2 wraps it inside /api (/estimate bill.monthly); see notes/requests.md
merges: []
services_touched:
  - /model
services_read:
  - US Census geocoder (address → lat/lon)
contract_change: none     # internal P1→P2 interface, not the §10 public contract
```

## Goal
One call returns seasonal heating and cooling point estimates for a location or address, plus the auxiliary weather data, for the past, a typical year or the forecast.

## Outputs
- `model/hc/service.py`: `estimate_hc(lat=None, lon=None, address=None, unit_sqft=None, mode="normal"|"forecast"|year)`
- `model/hc/server.py`: FastAPI dev server (port 8001): `GET /hc/estimate`, `GET /hc/weather`, `GET /hc/buildings`
- `model/data/processed/buildings_hc.parquet`: a pre-scored table of every benchmarked multifamily building (for P3's map)

## Done when
- [ ] `curl 'localhost:8001/hc/estimate?address=...'` returns seasonal {heating, cooling} {kwh/therms, usd} + weather + sources
- [ ] Tests pass; works offline after warm-up

## Handoff
- `model/hc/service.py`: `estimate_hc(address|lat,lon, unit_sqft, mode, answers, heating_fuel, building_type)` → per-season {heating, cooling} {usd, ccf/kWh} + weather (tmean, HDD, CDD) + building + method + accuracy + sources. Also `weather()` and `bill_check()`.
- Routing: metered (own meters) → meter_model (≥10k ft²) → resstock (smaller). A ResStock cross-check is included.
- `model/hc/server.py`: `uvicorn model.hc.server:app --port 8001` (`/hc/estimate`, `/hc/weather`, `/hc/bill_check`, `/hc/answers`, `/hc/buildings`).
- `model/hc/score_buildings.py` → `model/data/processed/buildings_hc.{parquet,csv}`: **591** Ann Arbor apartment buildings/complexes scored (108 metered, 464 meter-model, 19 ResStock).
- TODO: tests, a one-command rebuild (artifacts `*.pkl` are git-ignored), and a P2 wrap (notes/requests.md).

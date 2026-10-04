```yaml
id: P1-06
title: Heating + cooling estimate service (Python API + dev HTTP server in /model)
owner: P1
status: done
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
- `model/heating_cooling/service.py`: `estimate_hc(lat=None, lon=None, address=None, unit_sqft=None, mode="normal"|"forecast"|year)`
- `model/heating_cooling/server.py`: FastAPI dev server (port 8001): `GET /hc/estimate`, `GET /hc/weather`, `GET /hc/buildings`
- `model/data/processed/buildings_hc.parquet`: a pre-scored table of every benchmarked multifamily building (for P3's map)

## Done when
- [ ] `curl 'localhost:8001/hc/estimate?address=...'` returns seasonal {heating, cooling} {kwh/therms, usd} + weather + sources
- [ ] Tests pass; works offline after warm-up

## Handoff
- `model/heating_cooling/service.py`: `estimate_hc(address|lat,lon, unit_sqft, mode="normal"|"forecast"|YYYY, answers, heating_fuel, building_type)` → per-season {heating, cooling} × {usd, gas_ccf, electric_kwh} + weather (tmean_f, HDD65, CDD65, HDD60) + annual + building (name, GFA, year built, fuel, each with a source) + method + accuracy (from real meters) + sources. Also `weather()` and `bill_check()` (path-specific noise floor).
- Server: `make -C model dashboard` (http://localhost:8001/dashboard) → `/hc/estimate`, `/hc/weather`, `/hc/bill_check`, `/hc/answers`, `/hc/buildings`.
- Map table: `model/data/processed/buildings_hc.csv`, 591 apartment buildings/complexes (108 metered, 464 blend, 19 ResStock).
- Rebuild: `python -m model.scripts.build_all` (95 s warm, zero network requests). Tests: `python -m pytest model/tests -q` (7 pass).
- Next: P2 wraps it in `/estimate` + `/calibrate` (notes/requests.md). P3 can use `buildings_hc.csv`.

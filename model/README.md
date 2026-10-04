# /model (P1: data + ML)

Seasonal heating + cooling point estimates per apartment building, grounded in real Ann Arbor meters.
Research write-up and every number: [`research/heating_cooling.md`](research/heating_cooling.md).

```bash
make -C model setup        # .venv + requirements
make -C model build        # downloads once (cached), trains, validates, scores
make -C model test
make -C model dashboard    # heating/cooling server (model.heating_cooling.server) → http://localhost:8001/dashboard
curl 'localhost:8001/hc/estimate?address=2000+Pauline+Blvd,+Ann+Arbor,+MI&unit_sqft=800&mode=normal'
```
The dashboard is a page served by that Python server. Every number on it comes from the server's `/hc/*` endpoints (live
estimates, `buildings_hc.parquet`, `results/*.json`); nothing is hardcoded.

| Path | What |
|---|---|
| `data_sources/` | cached clients: ResStock, benchmarking, footprints, PRISM, Open-Meteo, EIA, Census, NOAA (via `http.py`; every real request is logged to `data/cache/requests.log`) |
| `climate.py` | 800 m localized monthly/seasonal weather: typical year, past year, forecast |
| `heating_cooling/changepoint.py` | PRISM (Princeton Scorekeeping Method) change-point fits |
| `heating_cooling/train.py`, `heating_cooling/building_model.py` | meter-trained models (MLR / random forest / XGBoost, CV by building) |
| `heating_cooling/resstock_model.py` | ResStock per-degree-day model + renter answers, calibrated to meters |
| `heating_cooling/leakage_analysis.py`, `heating_cooling/validate.py` | can bills reveal leakiness; NOAA + held-out real-meter checks |
| `heating_cooling/service.py`, `heating_cooling/server.py` | `estimate_hc`, `weather`, `bill_check`; FastAPI dev server |
| `data/processed/buildings_hc.csv` | 591 Ann Arbor apartment buildings/complexes, seasonal $ (for the map) |
| `scripts/reproduce_resstock.py` | 10:30 PM checkpoint (R² 0.548 → 0.764) |

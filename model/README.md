# /model (P1: data + ML)

Seasonal heating + cooling point estimates per apartment building, grounded in real Ann Arbor meters.
Research write-up and every number: [`research/heating_cooling.md`](research/heating_cooling.md).

```bash
python3 -m venv --system-site-packages .venv && .venv/bin/pip install -r model/requirements.txt
.venv/bin/python -m model.scripts.build_all        # downloads once (cached), trains, validates, scores
.venv/bin/python -m pytest model/tests -q
.venv/bin/uvicorn model.hc.server:app --port 8001
curl 'localhost:8001/hc/estimate?address=2000+Pauline+Blvd,+Ann+Arbor,+MI&unit_sqft=800&mode=normal'
```

| Path | What |
|---|---|
| `data_sources/` | cached clients: ResStock, benchmarking, footprints, PRISM, Open-Meteo, EIA, Census, NOAA (via `http.py`; every real request is logged to `data/cache/requests.log`) |
| `climate.py` | 800 m localized monthly/seasonal weather: typical year, past year, forecast |
| `hc/changepoint.py` | PRISM (Princeton Scorekeeping Method) change-point fits |
| `hc/train.py`, `hc/building_model.py` | meter-trained models (MLR / random forest / XGBoost, CV by building) |
| `hc/resstock_model.py` | ResStock per-degree-day model + renter answers, calibrated to meters |
| `hc/leakage_analysis.py`, `hc/validate.py` | can bills reveal leakiness; NOAA + held-out real-meter checks |
| `hc/service.py`, `hc/server.py` | `estimate_hc`, `weather`, `bill_check`; FastAPI dev server |
| `data/processed/buildings_hc.csv` | 591 Ann Arbor apartment buildings/complexes, seasonal $ (for the map) |
| `scripts/reproduce_resstock.py` | 10:30 PM checkpoint (R² 0.548 → 0.764) |

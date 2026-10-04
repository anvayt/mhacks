"""P1-06: dev HTTP server for the heating/cooling estimator (P2 wraps model.heating_cooling.service inside /api).

Run: uvicorn model.heating_cooling.server:app --port 8001
  GET /hc/estimate?address=…&unit_sqft=850&mode=normal|forecast|2024&window_panes=2&floor_level=1&…
  GET /hc/estimate?lat=42.28&lon=-83.74
  GET /hc/weather?lat=…&lon=…&mode=…
  GET /hc/bill_check?address=…&year=2025&month=1&gas_ccf=95&unit_sqft=850
  GET /hc/buildings          (pre-scored metered + large apartment buildings, for the map)
  GET /hc/validation         (held-out checks against real data)
  GET /dashboard             (local explorer UI; / redirects here)
"""
from __future__ import annotations

import json

import pandas as pd
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, RedirectResponse

from model.heating_cooling import service
from model.heating_cooling.resstock_model import ANSWERS
from model.paths import PROCESSED, RESULTS

app = FastAPI(title="Hidden Rent: heating + cooling estimates (P1)")


def _mode(mode: str):
    return int(mode) if mode.isdigit() else mode


@app.get("/hc/estimate")
def estimate(address: str | None = None, lat: float | None = None, lon: float | None = None,
             unit_sqft: float | None = None, mode: str = "normal", heating_fuel: str | None = None,
             building_type: str | None = None, window_panes: float | None = None, floor_level: float | None = None,
             foundation_code: float | None = None, cooling_code: float | None = None, occupants: float | None = None,
             block_group: str | None = None):
    answers = {k: v for k, v in dict(window_panes=window_panes, floor_level=floor_level, foundation_code=foundation_code,
                                     cooling_code=cooling_code, occupants=occupants).items() if v is not None}
    try:
        return service.estimate_hc(address=address, lat=lat, lon=lon, unit_sqft=unit_sqft, mode=_mode(mode),
                                   answers=answers, heating_fuel=heating_fuel, building_type=building_type,
                                   block_group=block_group)
    except ValueError as e:
        raise HTTPException(422, str(e))


@app.get("/hc/weather")
def weather(lat: float, lon: float, mode: str = "normal"):
    return service.weather(lat, lon, _mode(mode))


@app.get("/hc/bill_check")
def bill_check(year: int, month: int = Query(ge=1, le=12), gas_ccf: float = Query(gt=0), unit_sqft: float = Query(gt=0),
               address: str | None = None, lat: float | None = None, lon: float | None = None):
    try:
        return service.bill_check(year, month, gas_ccf, unit_sqft, address=address, lat=lat, lon=lon)
    except ValueError as e:
        raise HTTPException(422, str(e))


@app.get("/hc/answers")
def answers():
    return ANSWERS


@app.get("/hc/buildings")
def buildings():
    p = PROCESSED / "buildings_hc.parquet"
    if not p.exists():
        raise HTTPException(503, "run python -m model.heating_cooling.score_buildings first")
    return json.loads(pd.read_parquet(p).to_json(orient="records"))


@app.get("/hc/heldout")
def heldout(fuel: str | None = None):
    """Real meters vs every estimate path, for building-seasons the models never saw."""
    return service.heldout(fuel)


@app.get("/hc/metered")
def metered():
    """The Ann Arbor properties with real monthly meter readings (City benchmarking, 2021–23)."""
    return service.metered_list()


@app.get("/hc/metered/{building_id}")
def metered_building(building_id: str):
    try:
        return service.metered_building(building_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@app.get("/hc/validation")
def validation():
    out = {}
    files = (("real", RESULTS / "validation_real.json"), ("leakage", RESULTS / "leakage_analysis.json"),
             ("building_model", RESULTS / "building_model_validation.json"),
             ("resstock", RESULTS / "resstock_hc_validation.json"), ("train", RESULTS / "hc_validation.json"),
             ("meters", RESULTS / "meters_summary.json"), ("prices", PROCESSED / "prices_mi.json"))
    for name, p in files:
        out[name] = json.loads(p.read_text()) if p.exists() else None
    return out


@app.get("/dashboard", include_in_schema=False)
def dashboard():
    return FileResponse(Path(__file__).with_name("dashboard.html"))


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/dashboard")

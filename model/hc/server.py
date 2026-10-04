"""P1-06: dev HTTP server for the heating/cooling estimator (P2 wraps model.hc.service inside /api).

Run: uvicorn model.hc.server:app --port 8001
  GET /hc/estimate?address=…&unit_sqft=850&mode=normal|forecast|2024&window_panes=2&floor_level=1&…
  GET /hc/estimate?lat=42.28&lon=-83.74
  GET /hc/weather?lat=…&lon=…&mode=…
  GET /hc/bill_check?address=…&year=2025&month=1&gas_ccf=95&unit_sqft=850
  GET /hc/buildings          (pre-scored metered + large apartment buildings, for the map)
"""
from __future__ import annotations

import json

import pandas as pd
from fastapi import FastAPI, HTTPException, Query

from model.hc import service
from model.hc.resstock_model import ANSWERS
from model.paths import PROCESSED

app = FastAPI(title="Hidden Rent: heating + cooling estimates (P1)")


def _mode(mode: str):
    return int(mode) if mode.isdigit() else mode


@app.get("/hc/estimate")
def estimate(address: str | None = None, lat: float | None = None, lon: float | None = None,
             unit_sqft: float | None = None, mode: str = "normal", heating_fuel: str | None = None,
             building_type: str | None = None, window_panes: float | None = None, floor_level: float | None = None,
             foundation_code: float | None = None, cooling_code: float | None = None, occupants: float | None = None):
    answers = {k: v for k, v in dict(window_panes=window_panes, floor_level=floor_level, foundation_code=foundation_code,
                                     cooling_code=cooling_code, occupants=occupants).items() if v is not None}
    try:
        return service.estimate_hc(address=address, lat=lat, lon=lon, unit_sqft=unit_sqft, mode=_mode(mode),
                                   answers=answers, heating_fuel=heating_fuel, building_type=building_type)
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
        raise HTTPException(503, "run python -m model.hc.score_buildings first")
    return json.loads(pd.read_parquet(p).to_json(orient="records"))

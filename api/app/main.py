"""Hidden Rent API. Run from /api: uv run uvicorn app.main:app --reload --port 8000"""

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.city import router as city_router
from app.compare import router as compare_router
from app.estimate import estimate, router as estimate_router
from app.fixes import router as fixes_router
from app.forecast import router as forecast_router
from app.geo.features import get_features

app = FastAPI(title="Hidden Rent API")
app.include_router(estimate_router)  # POST /answer, GET /session/{id} (P2-04)
# /web calls /estimate from the browser (Next.js dev server on :3000)
app.add_middleware(CORSMiddleware, allow_origins=os.environ.get("WEB_ORIGINS", "http://localhost:3000").split(","),
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(fixes_router)
app.include_router(forecast_router)
app.include_router(compare_router)
app.include_router(city_router)


class EstimateRequest(BaseModel):
    url: str | None = None
    address: str | None = None
    unit_sqft: float | None = None  # additive (P2-04 decision): from the listing or the renter


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/estimate")
def post_estimate(req: EstimateRequest) -> dict:
    """PLAN.md §10 /estimate. Errors: 422 {"detail": {"code", "message", ...}}, 503 if the model is down."""
    return estimate(req.url, req.address, req.unit_sqft)


@app.get("/debug/features")
def debug_features(address: str, unit_sqft: float | None = None, year_built: int | None = None) -> dict:
    """Internal only (not part of the PLAN.md §10 contract): address -> building features."""
    try:
        return get_features(address, unit_sqft, year_built)
    except LookupError as e:
        raise HTTPException(404, str(e))

"""Hidden Rent API. Run from /api: uv run uvicorn app.main:app --reload --port 8000"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.estimate import estimate
from app.geo.features import get_features

app = FastAPI(title="Hidden Rent API")


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

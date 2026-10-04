"""Hidden Rent API. Run from /api: uv run uvicorn app.main:app --reload --port 8000"""

from fastapi import FastAPI, HTTPException

from app.geo.features import get_features

app = FastAPI(title="Hidden Rent API")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/debug/features")
def debug_features(address: str, unit_sqft: float | None = None, year_built: int | None = None) -> dict:
    """Internal only (not part of the PLAN.md §10 contract): address -> building features."""
    try:
        return get_features(address, unit_sqft, year_built)
    except LookupError as e:
        raise HTTPException(404, str(e))

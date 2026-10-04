"""Compare two listings using the same estimate function as POST /estimate (PLAN.md §10)."""

from concurrent.futures import ThreadPoolExecutor
from math import isfinite

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, model_validator

from app import estimate as estimates
from app.badges import badges

router = APIRouter()


def _missing_input() -> HTTPException:
    return HTTPException(422, {"code": "missing_input", "message": "Send exactly two listings to compare."})


class Listing(BaseModel):
    url: str | None = None
    address: str | None = None
    unit_sqft: float | None = None


class CompareRequest(BaseModel):
    listings: list[Listing]

    @model_validator(mode="before")
    @classmethod
    def exactly_two(cls, value):
        listings = value.get("listings") if isinstance(value, dict) else None
        if not isinstance(listings, list) or len(listings) != 2:
            raise _missing_input()
        return value


@router.post("/compare")
def compare(req: CompareRequest | None = None) -> dict:
    if req is None:
        raise _missing_input()
    results = {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        pending = {side: pool.submit(estimates.estimate, item.url, item.address, item.unit_sqft)
                   for side, item in zip(("a", "b"), req.listings)}
        for side, future in pending.items():
            try:
                est = future.result()
            except HTTPException as exc:
                detail = exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail)}
                raise HTTPException(422, {"code": "estimate_failed", **detail, "listing": side}) from exc
            # Copy the response and badge list: a stored session may reuse the estimate dictionary.
            results[side] = {**est, "badges": list(dict.fromkeys([*(est.get("badges") or []), *badges(est)]))}

    a, b = (results[side]["bill"]["annual"] for side in ("a", "b"))
    winner = "a" if a["p50"] <= b["p50"] else "b"  # equal bills select a deterministically
    if "battle-winner" not in results[winner]["badges"]:
        results[winner]["badges"].append("battle-winner")
    bounds = [band.get(key) for band in (a, b) for key in ("p10", "p90")]
    have_bands = all(isinstance(v, (int, float)) and not isinstance(v, bool) and isfinite(v) for v in bounds)
    confident = bool(have_bands and a["p10"] <= a["p90"] and b["p10"] <= b["p90"]
                     and (a["p90"] < b["p10"] or b["p90"] < a["p10"]))
    return {**results, "winner": winner, "diff_usd_yr": round(abs(a["p50"] - b["p50"])),
            "confident": confident}

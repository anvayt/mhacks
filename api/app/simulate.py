"""POST /simulate/fast-forward: a SIMULATION of savings adding up day by day if the renter keeps their commitments.

The annual savings are /projection's composed what-if (commitments.what_if: P1's model, one run, effects don't add).
They are spread over the days with typical-year weather at the home: a day's share of the heating $ is that calendar
day's 1991-2020 mean heating degree-days at P1's base for this building (forecast._bases) over the typical year's
total, and likewise cooling. So 365 days from today add up to the annual delta, and a January day saves more than an
October day. Placeholders give 0 (not_modeled). Nothing is written anywhere: no habit check-ins, bills, impact,
snapshots, projections or board rows; the real streak and grade never change."""

import datetime as dt
from functools import lru_cache
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app import accounts, commitments, estimate, forecast, habits

router = APIRouter()
LABEL = "simulated_projected_if_kept"
LABEL_TEXT = "Simulated · projected if you keep your commitments"
METHOD = ("Simulation, not usage. Annual savings: /projection's composed what-if (P1's model, all modeled commitments "
          "in one run; tips count 0). Day weights: the calendar day's mean 1991-2020 heating degree-days at P1's base "
          "for this building (HDD60 gas, HDD55 electric, or the metered fit's balance point) divided by the typical "
          "year's, and likewise cooling (CDD65), from Open-Meteo's ERA5 daily means at the home's 0.1 deg cell (no PRISM "
          "offset: it only shapes the weights). Renter $: heating $ follows heating days, the rest cooling days; CO2 "
          "follows the building's heating/cooling $ split. 365 days from today sum to the annual delta (Feb 29 weighs "
          "as Feb 28). habit_day assumes a check-in every day.")


def _fail(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(status, {"code": code, "message": message})


def _today(tz: str | None) -> dt.date:
    try:
        zone = ZoneInfo(tz or habits.DEFAULT_TZ)
    except (KeyError, ValueError):
        zone = ZoneInfo(habits.DEFAULT_TZ)
    return habits._now().astimezone(zone).date()


@lru_cache(maxsize=32)
def _weights(lat: float, lon: float, hb: int | None, cb: int | None) -> dict[tuple[int, int], tuple[float, float]]:
    """(month, day) -> (share of a typical year's heating degree-days, share of its cooling degree-days)."""
    sums: dict[tuple[int, int], list[float]] = {}
    for day, t in forecast._history(lat, lon).items():
        if (day.month, day.day) == (2, 29):
            continue
        f, s = forecast._f(t), sums.setdefault((day.month, day.day), [0.0, 0.0, 0])
        s[0] += max(hb - f, 0) if hb else 0
        s[1] += max(f - cb, 0) if cb else 0
        s[2] += 1
    typical = {k: (h / n, c / n) for k, (h, c, n) in sums.items()}
    total_h, total_c = sum(h for h, _ in typical.values()), sum(c for _, c in typical.values())
    flat = 1 / len(typical)  # no heating (or cooling) term at all: spread evenly so the total still holds
    w = {k: (h / total_h if total_h else flat, c / total_c if total_c else flat) for k, (h, c) in typical.items()}
    w[(2, 29)] = w[(2, 28)]
    return w


class FastForward(BaseModel):
    property_id: str | None = None
    session_id: str | None = None
    days: int
    catalog_ids: list[str] | None = None


@router.post("/simulate/fast-forward")
def fast_forward(req: FastForward, request: Request) -> dict:
    """Simulated day-by-day savings for 1-365 days from today. property_id: owner or agent (its accepted/completed
    commitments unless catalog_ids); session_id: anonymous what-if of catalog_ids. Stores nothing."""
    if not 1 <= req.days <= 365:
        raise _fail(422, "bad_days", "Fast-forward 1 to 365 days.")
    if req.property_id:
        prop, s = commitments._home(req.property_id, request)
        user = accounts.get_user(prop["user_id"]) or {"id": prop["user_id"]}
        cids = req.catalog_ids if req.catalog_ids is not None else [
            c["catalog_id"] for c in commitments.list_commitments(property_id=prop["id"])
            if c["status"] in ("accepted", "completed")]
        real, tz = habits.summary(user)["current"], user.get("timezone")
    elif req.session_id:
        prop, s, cids, real, tz = None, commitments._session(req.session_id), req.catalog_ids or [], 0, None
    else:
        raise _fail(422, "missing_input", "Send a property_id or a session_id.")
    if any(c not in commitments.CATALOG for c in cids):
        raise _fail(422, "unknown_action", "We don't have that action. Pick one from your suggested list.")
    cids = list(dict.fromkeys(cids))
    w = commitments.what_if(s, cids, prop and prop["id"])  # stores nothing (POST /projection is what stores one)
    d = w["delta"]
    usd_yr, kg_yr = d["usd_saved_yr"], d["co2_kg_saved_yr"]
    bh, bc = d["building_heating_usd_saved_yr"], d["building_cooling_usd_saved_yr"]
    renter_heat = 0 if estimate.renter_usd_key(s) == "cooling_usd" else bh  # heat in the rent: renter $ is cooling
    kg_heat = kg_yr * (bh / (bh + bc) if bh + bc else 1)
    weights = None
    if w["modeled"]:
        p = estimate.session_params(s)
        try:
            hb, cb = forecast._bases(s["heating_cooling"])
        except (KeyError, TypeError):  # a session without model_detail: P1's pooled gas/cooling bases
            hb, cb = forecast.TAU_H["gas"], forecast.TAU_C
        weights = _weights(forecast._grid(p["lat"]), forecast._grid(p["lon"]), hb, cb)
    today, days, cu, ck = _today(tz), [], 0.0, 0.0
    for i in range(1, req.days + 1):
        day = today + dt.timedelta(days=i)
        wh, wc = weights[(day.month, day.day)] if weights else (0, 0)
        usd, kg = renter_heat * wh + (usd_yr - renter_heat) * wc, kg_heat * wh + (kg_yr - kg_heat) * wc
        cu, ck = cu + usd, ck + kg
        days.append({"date": day.isoformat(), "usd_saved": round(usd, 2), "kg_co2_saved": round(kg, 2),
                     "cumulative_usd": round(cu, 2), "cumulative_kg": round(ck, 2), "habit_day": real + i})
    return {"label": LABEL, "label_text": LABEL_TEXT, "method": METHOD, "property_id": prop and prop["id"],
            "session_id": s.get("session_id"), "start_date": today.isoformat(), "days": days,
            "totals": {"days": req.days, "end_date": days[-1]["date"], "usd_saved": round(cu, 2),
                       "kg_co2_saved": round(ck, 2)},
            "annual": {"usd_saved_yr": usd_yr, "co2_kg_saved_yr": kg_yr, "label": commitments.LABEL},
            "commitments": [{"catalog_id": c, "title": commitments.CATALOG[c]["title"], "modeled": c in w["modeled"]}
                            for c in cids],
            "modeled": w["modeled"], "not_modeled": w["not_modeled"],
            "real_habit_streak": real, "simulated_habit_streak": real + req.days}

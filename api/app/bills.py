"""Phase 2 bills, snapshots and verified same-property impact (NEW_CHANGES §7, §9.3–4, D3).

Gas only until P1 can weather-normalize electricity. Store numbers and image SHA-256, never images.
Snapshots describe current estimates; projections cannot create them. Baseline = earliest initial_estimate.
"""

import base64
import calendar
import hashlib
import json
from contextlib import closing
from datetime import date, datetime, time, timezone
from math import isfinite
from uuid import uuid4
from zoneinfo import ZoneInfo

from app import co2, commitments, db
from app.estimate import _fail
from app.score import GRADES, score_for

SOURCES = {"initial_estimate", "questionnaire", "bill_regrade", "manual_refresh"}
LABEL = "from your bill, adjusted for weather"
PROVISIONAL = ("early signal from one bill: inside normal month-to-month variation, so your grade doesn't change")
MODEL_VERSION = "P1 heating_cooling + P2 bill regrade v1"  # algorithm identifier; upstream artifact version not exposed
FACTORS = {"gas_kg_per_therm": co2.KG_PER_THERM, "elec_kg_per_kwh": co2.KG_PER_KWH,
           "egrid_year": 2023, "ccf_to_therm": co2.THERMS_PER_CCF,
           "source": "EPA GHG Emission Factors Hub 2025, natural gas; EPA eGRID2023 rev2 RFCM; "
                     "EIA FAQ 45, 2025 US-average 1.037 therms/ccf (app/co2.py)"}
VERIFY_RULE = ("At least one complete monthly billing period (at least 28 inclusive days, the shortest calendar "
               "month), entirely after a same-property commitment was completed, with gas below the weather-normal "
               "expectation by more than P1's actual held-out noise_floor. Electricity is not verified.")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect():
    con = db.connect()
    con.executescript("""
        CREATE TABLE IF NOT EXISTS score_snapshots
            (id TEXT PRIMARY KEY, property_id TEXT NOT NULL, source TEXT NOT NULL, body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS bill_submissions
            (id TEXT PRIMARY KEY, property_id TEXT NOT NULL, period_start TEXT NOT NULL, period_end TEXT NOT NULL,
             image_sha256 TEXT, body TEXT NOT NULL, response TEXT NOT NULL,
             UNIQUE(property_id, period_start, period_end));
        CREATE UNIQUE INDEX IF NOT EXISTS bills_image ON bill_submissions(image_sha256)
            WHERE image_sha256 IS NOT NULL;
        CREATE TABLE IF NOT EXISTS impact_records
            (id TEXT PRIMARY KEY, property_id TEXT NOT NULL, bill_id TEXT NOT NULL UNIQUE, body TEXT NOT NULL);
    """)
    return con


def _list(table: str, property_id: str) -> list[dict]:
    with closing(_connect()) as con:
        return [json.loads(r[0]) for r in con.execute(f"SELECT body FROM {table} WHERE property_id = ? ORDER BY rowid",
                                                     (property_id,))]


def list_snapshots(property_id: str) -> list[dict]:
    return _list("score_snapshots", property_id)


def list_bills(property_id: str) -> list[dict]:
    return _list("bill_submissions", property_id)


def list_impact(property_id: str) -> list[dict]:
    return _list("impact_records", property_id)


def _snapshot(property_id: str, source: str, body: dict) -> dict:
    if source not in SOURCES or body.get("label") == "projected_if_completed" or "projected" in body:
        raise _fail(422, "bad_snapshot_source", "Only estimates, answers and bill checks can update your current grade.")
    carbon = body.get("co2_kg_yr")
    if carbon is None:
        carbon = {q: round(v * 1000, 2) if v is not None else None for q, v in
                  ((q, (body.get("co2_t") or {}).get(q)) for q in ("p10", "p50", "p90"))}
    return {"id": uuid4().hex, "property_id": property_id, "source": source,
            "score": body["score"], "grade": body["grade"], "grade_span": body.get("grade_span", [body["grade"]]),
            "bill_annual": body.get("bill_annual") or body["bill"]["annual"], "co2_kg_yr": carbon,
            "percentile_peers": body.get("percentile_peers"), "percentile_city": body.get("percentile_city"),
            "model_version": body.get("model_version") or MODEL_VERSION, "created_at": _now(),
            **({"label": LABEL} if source == "bill_regrade" else {})}


def _insert_snapshot(con, snapshot: dict):
    con.execute("INSERT INTO score_snapshots VALUES (?, ?, ?, ?)",
                (snapshot["id"], snapshot["property_id"], snapshot["source"], json.dumps(snapshot)))


def record_snapshot(property_id: str, source: str, body: dict) -> dict:
    snapshot = _snapshot(property_id, source, body)
    with closing(_connect()) as con, con:
        _insert_snapshot(con, snapshot)
    return snapshot


def image_hash(image: str | None) -> str | None:
    if not image:
        return None
    encoded = image.split(",", 1)[1] if image.startswith("data:") and "," in image else image
    try:
        raw = base64.b64decode("".join(encoded.split()), validate=True)
    except ValueError:
        raise _fail(422, "unreadable_bill", "That bill photo couldn't be opened. Send it again or type the usage and dates.")
    return hashlib.sha256(raw).hexdigest()


def _duplicate(con, property_id: str, start: str | None, end: str | None, sha: str | None) -> dict | None:
    if sha:
        row = con.execute("SELECT property_id, response FROM bill_submissions WHERE image_sha256 = ?", (sha,)).fetchone()
        if row:
            if row[0] != property_id:
                raise _fail(409, "bill_already_used", "That bill was already submitted for another saved home. "
                            "Use a bill for this home.")
            return json.loads(row[1])
    row = con.execute("SELECT response FROM bill_submissions WHERE property_id = ? AND period_start = ? AND period_end = ?",
                      (property_id, start, end)).fetchone()
    return json.loads(row[0]) if row else None


def duplicate(property_id: str, start: str | None = None, end: str | None = None, sha: str | None = None) -> dict | None:
    with closing(_connect()) as con:
        return _duplicate(con, property_id, start, end, sha)


def _regrade(session: dict, pct: float) -> dict:
    """The year implied by one weather-normalized bill, damped: the change is clamped to the model's own p10–p90 for
    this home, so one bill never moves the grade outside the predicted range. The building's $ (heat included in the
    rent or not), since the grade rates the building."""
    annual = session["bill"].get("building_annual") or session["bill"]["annual"]
    lo, mid, hi = annual.get("p10"), annual["p50"], annual.get("p90")
    implied = mid * (1 + pct / 100)
    factor = min(max(implied, lo if lo is not None else implied), hi if hi is not None else implied) / mid if mid else 1
    bill = {q: round(annual[q] * factor, 2) if annual.get(q) is not None else None for q in ("p10", "p50", "p90")}
    scores = score_for(bill["p50"], session["building"]["sqft"], session["building"]["type"])
    # One gas bill cannot demonstrate lower electricity use; carbon adjusts gas only, with unknown bands.
    energy = session.get("heating_cooling", {}).get("annual", {})
    carbon = {"p10": None, "p50": None, "p90": None}
    if energy.get("gas_ccf") is not None and energy.get("electric_kwh") is not None:
        carbon["p50"] = round(co2.co2_kg(energy["gas_ccf"] * factor, energy["electric_kwh"]), 2)
    low = score_for(bill["p10"], session["building"]["sqft"], session["building"]["type"])["grade"] if bill["p10"] is not None else scores["grade"]
    high = score_for(bill["p90"], session["building"]["sqft"], session["building"]["type"])["grade"] if bill["p90"] is not None else scores["grade"]
    return {**scores, "grade_span": list(GRADES[GRADES.index(low):GRADES.index(high) + 1]), "bill_annual": bill, "co2_kg_yr": carbon,
            "model_version": session.get("model_version") or MODEL_VERSION}


def verify_bill(check: dict, start: date, end: date, candidates: list[dict], *,
                property_id: str, user_id: str, today: date) -> list[str]:
    """Pure D3 rule: IDs supported by a full, completed post-action bill beyond P1's actual noise.

    Dates are inclusive; 28 days is the shortest full calendar month. A same-day midday completion
    cannot cover a period starting that morning. P1's meaningful=False/None is never overruled.
    """
    fraction, noise = check.get("pct_vs_expected_for_weather"), check.get("noise_floor")
    if ((end - start).days + 1 < 28 or end >= today or check.get("meaningful") is not True or
            not isinstance(noise, (int, float)) or not isfinite(noise) or noise < 0 or
            not isinstance(fraction, (int, float)) or not isfinite(fraction) or fraction >= -noise):
        return []
    period_start = datetime.combine(start, time.min, ZoneInfo("America/Detroit"))
    completed = []
    for c in candidates:
        if c.get("property_id") != property_id or c.get("user_id") != user_id or c.get("status") != "completed":
            continue
        try:
            when = datetime.fromisoformat(c["completed_at"].replace("Z", "+00:00"))
            if when.tzinfo is None:
                when = when.replace(tzinfo=ZoneInfo("America/Detroit"))
        except (KeyError, ValueError, TypeError, AttributeError):
            continue
        if when < period_start:
            completed.append(c)
    # A gas drop after electrification is not a net CO2 reduction without verified electricity.
    if any(c.get("catalog_id") == "heat_pump" for c in completed):
        return []
    return [c["id"] for c in completed]


def _gas_price(session: dict, month: int) -> tuple[float, str] | None:
    for m in session.get("heating_cooling", {}).get("months", []):
        heat = m.get("heating", {})
        ccf, usd = heat.get("gas_ccf"), heat.get("usd")
        if m.get("month") == month and ccf and usd is not None and ccf > 0 and usd >= 0:
            return usd / ccf, (f"Rate inferred from rounded P1 session monthly heating cost/use: month {month}, "
                               "heating.usd / gas_ccf; the model uses EIA gas pricing")
    return None


def save_bill(prop: dict, session: dict, extracted: dict, start: date, end: date, ccf: float,
              sha: str | None, check: dict, response: dict) -> dict:
    """Atomically persist the bill, its regrade and any verified impact; replays return the original response."""
    pid, sid = prop["id"], session["session_id"]
    candidates = commitments.list_commitments(property_id=pid)  # initialize other-module schema before our write transaction
    with closing(_connect()) as con, con:
        con.execute("BEGIN IMMEDIATE")
        old = _duplicate(con, pid, start.isoformat(), end.isoformat(), sha)
        if old:
            return old
        snapshots = [json.loads(r[0]) for r in con.execute(
            "SELECT body FROM score_snapshots WHERE property_id = ? AND source = 'initial_estimate' ORDER BY rowid", (pid,))]
        baseline = snapshots[0] if snapshots else _snapshot(pid, "initial_estimate", session)
        if not snapshots:
            _insert_snapshot(con, baseline)
        snapshot = _snapshot(pid, "bill_regrade", _regrade(session, response["pct_vs_expected_for_weather"]))
        # Only a bill P1 calls meaningful (beyond its month-to-month noise) becomes the home's current grade.
        provisional = check.get("meaningful") is not True
        snapshot.update(provisional=provisional, label=PROVISIONAL if provisional else LABEL)
        _insert_snapshot(con, snapshot)
        commitment_ids = verify_bill(check, start, end, candidates, property_id=pid,
                                     user_id=prop["user_id"], today=date.today())
        days = (end - start).days + 1
        verified = bool(prop.get("active")) and bool(commitment_ids)
        reason = "verified" if verified else "early_signal"
        # Different overlapping periods must not count the same energy twice (I7).
        previous = [json.loads(r[0]) for r in con.execute("SELECT body FROM impact_records WHERE property_id = ?", (pid,))]
        if any(i["period"]["start"] <= end.isoformat() and i["period"]["end"] >= start.isoformat() for i in previous):
            verified, reason = False, "overlapping_verified_period"
        impact = None
        price = _gas_price(session, check["month"])
        if verified and price is not None:
            # P1 checks a prorated calendar month; undo that proration to record only this bill's days.
            expected_ccf = check["expected_gas_ccf"] * days / calendar.monthrange(check["year"], check["month"])[1]
            avoided_ccf = max(0, expected_ccf - ccf)
            therms = avoided_ccf * co2.THERMS_PER_CCF
            impact = {"id": uuid4().hex, "property_id": pid, "period": {"start": start.isoformat(), "end": end.isoformat()},
                      "co2_kg_avoided": round(therms * co2.KG_PER_THERM, 4), "kwh_avoided": 0.0,
                      "therms_avoided": round(therms, 4), "usd_saved": round(avoided_ccf * price[0], 2),
                      "baseline_snapshot_id": baseline["id"], "commitment_ids": commitment_ids,
                      "method": "P1 weather-normal expected gas minus observed bill gas, reversed monthly proration; gas only",
                      "emission_factors": dict(FACTORS), "pricing": {"gas_usd_per_ccf": price[0], "source": price[1],
                                  "method": "ratio_of_rounded_model_monthly_cost_and_use"},
                      "model_version": session.get("model_version") or MODEL_VERSION, "created_at": _now()}
        elif verified:
            reason = "verified_gas_reduction_but_session_gas_price_unavailable"
        bill_id = uuid4().hex
        body = {"id": bill_id, "property_id": pid, "session_id": sid, "source": "image" if sha else "manual",
                "period_start": start.isoformat(), "period_end": end.isoformat(), "therms": round(ccf * co2.THERMS_PER_CCF, 6),
                "kwh": extracted.get("electricity_kwh"), "weather_normalized_delta_pct": response["pct_vs_expected_for_weather"],
                "image_sha256": sha, "verified": verified, "noise_floor": response["noise_floor"],
                "commitment_ids": commitment_ids if verified else [], "snapshot_id": snapshot["id"], "created_at": _now()}
        response = {**response, "bill_id": bill_id, "verified": verified,
                    "impact": {**impact, "factors": impact["emission_factors"]} if impact else None, "snapshot": snapshot,
                    "verified_commitment_ids": commitment_ids if verified else [], "verification_rule": VERIFY_RULE,
                    "verification_status": reason, "model_version": session.get("model_version") or MODEL_VERSION,
                    "bill_signal": {"grade": snapshot["grade"], "score": snapshot["score"],
                                    "annual_usd": snapshot["bill_annual"]["p50"],
                                    "pct_vs_expected_for_weather": response["pct_vs_expected_for_weather"],
                                    "label": snapshot["label"]}}
        con.execute("INSERT INTO bill_submissions VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (bill_id, pid, start.isoformat(), end.isoformat(), sha, json.dumps(body), json.dumps(response)))
        if impact:
            con.execute("INSERT INTO impact_records VALUES (?, ?, ?, ?)", (impact["id"], pid, bill_id, json.dumps(impact)))
        return response

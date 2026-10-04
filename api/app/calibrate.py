"""POST /calibrate (PLAN.md §10): one monthly bill (a photo read by xAI Grok vision, or typed numbers) -> P1's
weather-normal gas check (GET $MODEL_BASE_URL/hc/bill_check) -> streak of months below normal (SQLite, CALIBRATE_DB).

Gas only: P1's bill_check models gas, so electricity kWh is echoed in `extracted` but not compared yet.
"""

import calendar
import json
import logging
import os
import sqlite3
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path
from typing import Literal

import httpx
from fastapi import APIRouter, Request
from pydantic import BaseModel

from app import accounts, badges, bills, sessions
from app.estimate import MODEL_BASE_URL, MODEL_SLOTS, _fail

router = APIRouter()
log = logging.getLogger(__name__)

# EIA FAQ "What are Ccf, Mcf, Btu, and therms?" (eia.gov/tools/faqs/faq.php?id=45): 1 Ccf = 103,700 Btu = 1.037 therms
# (2025 US average heat content of gas delivered to consumers, 1,037 Btu per cubic foot).
THERMS_PER_CCF = 1.037
# DTE Gas Residential Rate A monthly customer charge: $15.40. DTE "Rates effective for gas service" rate card, October
# 2026 (MPSC Case No. U-21973, effective Oct 1, 2026), checked Oct 4, 2026:
# https://www.dteenergy.com/content/dam/dteenergy/deg/website/common/about-us/company-information/dte-gas-company/notices/rateCard.pdf
DTE_GAS_CUSTOMER_CHARGE = 15.40
# P1's EIA Michigan residential marginal gas $/ccf by calendar month (fixed charges removed), the prices its model uses
PRICES = Path(__file__).resolve().parents[2] / "model" / "data" / "processed" / "prices_mi.json"
XAI_URL = "https://api.x.ai/v1/chat/completions"
XAI_MODEL = os.environ.get("XAI_VISION_MODEL", "grok-4.7")  # image-input model in docs.x.ai image-understanding, Oct 2026
DB = Path(os.environ.get("CALIBRATE_DB", Path(__file__).resolve().parents[2] / "data" / "calibrate.sqlite"))
INTERNAL = ("answers", "model_params")  # session keys that aren't part of the §10 estimate body

NOT_FOUND = "That session expired. Send the listing again."
UNREADABLE = ("I couldn't read the gas usage on that bill. Send a clearer photo of the usage section "
              "(gas used in CCF or therms, and the billing dates).")
VISION_DOWN = ("Reading bill photos isn't working right now. Type the numbers instead: gas used (therms or CCF), "
               "electricity kWh, and the billing start and end dates.")
MODEL_DOWN = "The bill check isn't reachable right now. Try again in a bit."
NOTE = "Gas only: electricity (kWh) isn't compared with the weather yet."

# The yes/no and evidence fields come first so the model commits to "is it there?" before giving numbers: on a blank
# image Grok made up gas_usage = 43 when only the numbers were asked for.
BILL_SCHEMA = {
    "type": "object",
    "properties": {
        "is_utility_bill": {"type": "boolean"},
        "gas_usage_visible": {"type": "boolean"},
        "gas_usage_evidence": {"type": ["string", "null"]},
        "gas_usage": {"type": ["number", "null"]},
        "gas_unit": {"anyOf": [{"type": "string", "enum": ["ccf", "therms"]}, {"type": "null"}]},
        "electricity_kwh": {"type": ["number", "null"]},
        "start": {"type": ["string", "null"], "format": "date"},
        "end": {"type": ["string", "null"], "format": "date"},
        "utility": {"type": ["string", "null"]},
    },
    "required": ["is_utility_bill", "gas_usage_visible", "gas_usage_evidence", "gas_usage", "gas_unit", "electricity_kwh",
                 "start", "end", "utility"],
}
PROMPT = ("Read this image. is_utility_bill: true only if it is a gas or electric utility bill. gas_usage_visible: true "
          "only if a natural gas usage amount for the billing period is printed and legible. gas_usage_evidence: copy that "
          "printed usage line word for word, else null. Then gas_usage (the number) and gas_unit (ccf or therms), "
          "electricity used in kWh, the billing period start and end dates (YYYY-MM-DD), and the utility's name. "
          "Usage amounts only, never dollar amounts or meter readings. Return null for anything not printed on the "
          "image. Never estimate, infer or guess a value.")
# Most gas a home can use per 1,000 ft² per day: the leakiest gas-heated ResStock 2024.2 MI home (0.550 ccf/1000 ft²
# per HDD60, model/data/processed/resstock_frame.parquet) x Ann Arbor's coldest month on P1's meter weather 2021-23
# (Jan 2022, 41.0 HDD60/day, meters_weather.parquet) + the highest non-heating baseload on Ann Arbor meters
# (0.81 ccf/1000 ft²/day, building_targets.parquet). Catches misreads (meter readings, dollars), not small errors.
GAS_MAX_CCF_PER_1000FT2_DAY = 0.550 * 41.0 + 0.81


class CalibrateRequest(BaseModel):
    session_id: str
    property_id: str | None = None
    bill_image_base64: str | None = None
    therms: float | None = None  # the typed gas number, in gas_unit
    gas_unit: Literal["ccf", "therms"] = "therms"
    amount_usd: float | None = None  # the gas bill's $ total, when the usage isn't known (estimated, see gas_from_amount)
    kwh: float | None = None
    start: date | None = None
    end: date | None = None


def read_bill(image_b64: str) -> dict:
    """Grok vision -> {is_utility_bill, gas_usage_visible, gas_usage_evidence, gas_usage, gas_unit, electricity_kwh,
    start, end, utility} (nulls for what it can't read)."""
    key = os.environ.get("XAI_API_KEY")
    if not key:
        raise _fail(503, "vision_unavailable", VISION_DOWN)
    # P4 sends raw base64 JPEG (HEIC converted); also take PNG and data: URLs (a browser FileReader gives those)
    url = image_b64 if image_b64.startswith("data:") else \
        f"data:image/{'png' if image_b64.startswith('iVBOR') else 'jpeg'};base64,{image_b64}"
    body = {"model": XAI_MODEL, "temperature": 0,
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": url, "detail": "high"}},
                {"type": "text", "text": PROMPT}]}],
            "response_format": {"type": "json_schema",
                                "json_schema": {"name": "bill", "schema": BILL_SCHEMA, "strict": True}}}
    with ThreadPoolExecutor(2) as pool:
        a, b = pool.map(lambda _: _ask_xai(body, key), range(2))
    # Read twice, in parallel: Grok sometimes invents a whole bill (a blank 64 px image came back as "Usage: 111 CCF",
    # then 147 therms, then 64 therms), and invented numbers differ between reads while printed ones don't.
    if any(a[k] != b[k] for k in ("gas_usage", "gas_unit", "start", "end")):
        log.warning("xAI reads disagree: %s vs %s", a, b)
        raise _fail(422, "unreadable_bill", UNREADABLE, extracted=a)
    return a


def _ask_xai(body: dict, key: str) -> dict:
    try:
        r = httpx.post(XAI_URL, json=body, headers={"Authorization": f"Bearer {key}"}, timeout=90)
    except httpx.HTTPError as e:
        log.warning("xAI unreachable: %r", e)
        raise _fail(503, "vision_unavailable", VISION_DOWN)
    if r.status_code >= 500 or r.status_code in (401, 403, 404, 429):  # xAI down, bad key/model name, rate limit
        log.warning("xAI request failed: HTTP %s", r.status_code)
        raise _fail(503, "vision_unavailable", VISION_DOWN)
    try:
        r.raise_for_status()  # remaining 4xx: xAI rejected the image itself
        bill = json.loads(r.json()["choices"][0]["message"]["content"])
        return {k: bill.get(k) for k in BILL_SCHEMA["required"]}
    except (httpx.HTTPError, ValueError, LookupError, TypeError, AttributeError):  # rejected, or not a JSON object
        log.warning("xAI unreadable response: HTTP %s", r.status_code)
        raise _fail(422, "unreadable_bill", UNREADABLE)


def _bill_month(start: date, end: date) -> tuple[int, int]:
    """(year, month) holding most of the billing period's days."""
    days = max((end - start).days + 1, 1)
    return Counter((d.year, d.month) for d in (start + timedelta(i) for i in range(days))).most_common(1)[0][0]


def gas_from_amount(amount_usd: float, start: date, end: date) -> tuple[float, str]:
    """(gas ccf, how): (amount − DTE's monthly customer charge) ÷ P1's marginal $/ccf for the bill's month. Taxes and
    other per-bill items aren't separated, so it's an estimate. Raises ValueError (renter text)."""
    if amount_usd <= DTE_GAS_CUSTOMER_CHARGE:
        raise ValueError(f"That amount is no more than DTE's ${DTE_GAS_CUSTOMER_CHARGE:.2f} monthly customer charge, so "
                         "we can't work out the gas used. Send the gas used (therms or CCF) instead.")
    _, month = _bill_month(start, end)
    price = json.loads(PRICES.read_text())["gas_usd_per_ccf"]["marginal"][str(month)]
    ccf = round((amount_usd - DTE_GAS_CUSTOMER_CHARGE) / price, 1)
    return ccf, (f"estimated from your bill amount: (${amount_usd:,.2f} − DTE's ${DTE_GAS_CUSTOMER_CHARGE:.2f} monthly "
                 f"customer charge) ÷ ${price:.4f} per ccf (EIA Michigan marginal gas price for "
                 f"{calendar.month_name[month]}, as in P1's model) = {ccf} ccf. Taxes aren't separated.")


def month_usage(gas_ccf: float, start: date, end: date, unit_sqft: float) -> tuple[int, int, float]:
    """(year, month, gas ccf) for the calendar month holding most of the billing period. Raises ValueError (renter text)."""
    days = (end - start).days + 1  # billing days count both ends, so Jan 1-31 is a whole 31-day month
    if gas_ccf <= 0:
        raise ValueError("Gas used should be more than 0.")
    if not 1 <= days <= 62:
        raise ValueError("Those billing dates don't look right. A monthly bill starts before it ends, about a month apart.")
    if gas_ccf / days > GAS_MAX_CCF_PER_1000FT2_DAY * unit_sqft / 1000:
        raise ValueError(f"{gas_ccf:,.0f} CCF in {days} days is more gas than a {unit_sqft:,.0f} sq ft home uses even in "
                         "the coldest month. Check the gas usage number (not the meter reading or the dollar amount).")
    year, month = _bill_month(start, end)
    if (year, month) >= (date.today().year, date.today().month):  # P1's weather for that month isn't complete yet
        raise ValueError(f"That bill is mostly {calendar.month_name[month]} {year}, which isn't over yet. "
                         "Send it again once the month ends.")
    # Prorate by days: the bill's average daily gas x the days in that month. Assumes even daily use across the period,
    # so a period that spills into a colder or warmer neighboring month shifts the result a little.
    return year, month, round(gas_ccf * calendar.monthrange(year, month)[1] / days, 1)


def record(session_id: str, year: int, month: int, pct: float) -> int:
    """Store this month (re-sending a month replaces it); return the streak: calendar months in a row, ending at the
    latest month sent, below normal for the weather (pct < 0). A missing month breaks it."""
    DB.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(DB)) as con, con:
        con.execute("CREATE TABLE IF NOT EXISTS bills (session_id TEXT, year INT, month INT, pct REAL, "
                    "PRIMARY KEY (session_id, year, month))")
        con.execute("INSERT OR REPLACE INTO bills VALUES (?, ?, ?, ?)", (session_id, year, month, pct))
        rows = con.execute("SELECT year * 12 + month, pct FROM bills WHERE session_id = ? ORDER BY 1 DESC",
                           (session_id,)).fetchall()
    streak = 0
    for k, p in rows:
        if p >= 0 or k != rows[0][0] - streak:
            break
        streak += 1
    return streak


@router.post("/calibrate")
def calibrate(req: CalibrateRequest, request: Request) -> dict:
    """PLAN.md §10 /calibrate. pct_vs_expected_for_weather is in PERCENT (-12 = 12% below normal for that month's
    weather). Errors: 404 not_found, 422 missing_input/unreadable_bill/bad_bill, 503 vision_unavailable/model_unavailable."""
    sess = sessions.get(req.session_id)
    if sess is None:
        raise _fail(404, "not_found", NOT_FOUND)
    prop, sha = None, None
    if req.property_id:
        prop = accounts.get_property(req.property_id)
        if prop is None:
            raise _fail(404, "property_not_found", "We couldn't find that saved home. Add the address again.")
        accounts.authorize(request, prop["user_id"])
        if prop.get("session_id") != req.session_id:
            raise _fail(422, "property_session_mismatch", "That report belongs to a different home. Open this home's report again.")
        sha = bills.image_hash(req.bill_image_base64)
        old = bills.duplicate(prop["id"], req.start.isoformat() if req.start else None,
                              req.end.isoformat() if req.end else None, sha)
        if old:
            return old
    photo = bool(req.bill_image_base64)
    if photo:
        bill = read_bill(req.bill_image_base64)
    elif req.therms is not None and req.start and req.end:
        bill = {"gas_usage": req.therms, "gas_unit": req.gas_unit, "electricity_kwh": req.kwh,
                "start": req.start.isoformat(), "end": req.end.isoformat(), "utility": None}
    elif req.amount_usd is not None and req.start and req.end:
        try:
            ccf_est, how = gas_from_amount(req.amount_usd, req.start, req.end)
        except ValueError as e:
            raise _fail(422, "bad_bill", str(e))
        bill = {"gas_usage": ccf_est, "gas_unit": "ccf", "electricity_kwh": req.kwh, "start": req.start.isoformat(),
                "end": req.end.isoformat(), "utility": None, "amount_usd": req.amount_usd,
                "estimated_from_amount": True, "note": how}
    else:
        raise _fail(422, "missing_input", "Send a photo of the bill, or the gas therms and the billing start and end dates.")

    gas = bill["gas_usage"]
    if photo and not (bill["is_utility_bill"] is True and bill["gas_usage_visible"] is True and bill["gas_usage_evidence"]
                      and isinstance(gas, (int, float)) and gas > 0 and bill["gas_unit"] in ("ccf", "therms")):
        raise _fail(422, "unreadable_bill", UNREADABLE, extracted=bill)  # missing dates fail just below
    try:
        start, end = date.fromisoformat(bill["start"]), date.fromisoformat(bill["end"])
    except (TypeError, ValueError):  # photo only: no dates read (typed dates were parsed by pydantic)
        raise _fail(422, "unreadable_bill", UNREADABLE, extracted=bill)
    ccf = gas / THERMS_PER_CCF if bill["gas_unit"] == "therms" else gas
    mp = sess["model_params"]
    sqft = mp.get("unit_sqft") or sess["building"]["sqft"]
    try:
        year, month, gas_ccf = month_usage(ccf, start, end, sqft)
    except ValueError as e:
        raise _fail(422, "unreadable_bill" if photo else "bad_bill", str(e), extracted=bill)

    if prop:
        old = bills.duplicate(prop["id"], start.isoformat(), end.isoformat(), sha)
        if old:
            return old
    params = {"year": year, "month": month, "gas_ccf": gas_ccf, "lat": mp["lat"], "lon": mp["lon"], "unit_sqft": sqft}
    try:
        with MODEL_SLOTS:
            r = httpx.get(f"{MODEL_BASE_URL}/hc/bill_check", params=params, timeout=180)
    except httpx.HTTPError as e:
        log.warning("model unreachable: %r", e)
        raise _fail(503, "model_unavailable", MODEL_DOWN)
    if r.is_error:
        log.warning("model /hc/bill_check %s: %s", r.status_code, r.text[:500])
        raise _fail(503, "model_unavailable", MODEL_DOWN)
    chk = r.json()

    pct = round(chk["pct_vs_expected_for_weather"] * 100, 1)  # P1 returns a fraction; the API speaks percent
    noise = chk.get("noise_floor")
    response = {
        "pct_vs_expected_for_weather": pct,
        "streak_months": record(req.session_id, year, month, pct),
        "badges": badges.badges(sess, calibration={"pct_vs_expected_for_weather": pct},
                                used_fixes=bool(sess.get("used_fixes"))),
        "estimate": {k: v for k, v in sess.items() if k not in INTERNAL},
        # additive
        "year": year, "month": month,
        "actual_gas_ccf": chk["actual_gas_ccf"], "expected_gas_ccf": chk["expected_gas_ccf"],
        # percent like pct; P1 judges winter months only, so null outside Dec-Feb (meaningful too)
        "noise_floor": None if noise is None else round(noise * 100, 1),
        "meaningful": chk.get("meaningful"),
        "extracted": bill,
        "note": NOTE,
    }
    if prop:  # Phase 2 fields (bill_id, snapshot, verified, impact, ...) only with a property: P4's call is unchanged
        # A move during a slow model check freezes impact on the now-archived home.
        prop = accounts.get_property(prop["id"]) or {**prop, "active": False}
        return bills.save_bill(prop, sess, bill, start, end, ccf, sha, chk, response)
    return response

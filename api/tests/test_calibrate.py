"""POST /calibrate (api/app/calibrate.py). xAI and P1's /hc/bill_check are faked with bodies shaped like the real ones
(model/heating_cooling/service.py bill_check); the one live xAI test runs only when XAI_API_KEY is set."""

import base64
import json
import os
import struct
import zlib
from datetime import date

import httpx
import pytest
from fastapi.testclient import TestClient

from app import calibrate, sessions
from app.main import app

client = TestClient(app)
PARAMS = {"lat": 42.2701, "lon": -83.7402, "unit_sqft": 850, "building_type": "Multi-Family with 5+ Units",
          "block_group": "261614003001", "window_panes": 2}
EXPECTED_CCF = 125.0  # what the fake model expects for any month


def _session(sid="s1"):
    sessions.save({"session_id": sid, "building": {"lat": 42.27, "lon": -83.74, "address": "912 Mary St, Ann Arbor, MI 48104",
                                                   "sqft": 850, "type": "Multi-Family with 5+ Units"},
                   "bill": {"annual": {"p10": None, "p50": 612.0, "p90": None}}, "score": 64, "grade": "B",
                   "heating_cooling": {"method": "meter_model+resstock"},
                   "answers": {"window_panes": 2}, "model_params": PARAMS})
    return sid


def _bill_check(params):  # same keys and rounding as service.bill_check
    month, gas = int(params["month"]), float(params["gas_ccf"])
    pct = round(gas / EXPECTED_CCF - 1, 3)
    noise = 1.053 if month in (12, 1, 2) else None  # validation_real.json p90_abs_pct_error_winter["blend"]
    return {"year": int(params["year"]), "month": month, "actual_gas_ccf": gas, "expected_gas_ccf": EXPECTED_CCF,
            "expected_heating_ccf": 110.0, "expected_base_ccf": 15.0, "pct_vs_expected_for_weather": pct,
            "hdd65_that_month": 1180.0, "tmean_f_that_month": 24.9, "noise_floor": noise,
            "meaningful": (abs(pct) > noise) if noise else None, "method": "meter_model+resstock", "note": "..."}


@pytest.fixture(autouse=True)
def fakes(monkeypatch, tmp_path):
    """Fresh streak DB, a fake key, and fake model/xAI calls. Returns the recorded calls; set `vision` to change the read."""
    monkeypatch.setattr(calibrate, "DB", tmp_path / "calibrate.sqlite")
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    calls = {"model": [], "xai": [], "vision": {
        "is_utility_bill": True, "gas_usage_visible": True, "gas_usage_evidence": "Gas Usage 95 CCF",
        "gas_usage": 95, "gas_unit": "ccf", "electricity_kwh": 412, "start": "2026-01-05", "end": "2026-02-04",
        "utility": "DTE Energy"}}

    def get(url, params=None, timeout=None):
        assert url.endswith("/hc/bill_check")
        calls["model"].append(params)
        return httpx.Response(200, json=_bill_check(params), request=httpx.Request("GET", url))

    def post(url, **kw):
        assert url == calibrate.XAI_URL
        calls["xai"].append(kw)
        body = {"choices": [{"message": {"role": "assistant", "content": json.dumps(calls["vision"])}}]}
        return httpx.Response(200, json=body, request=httpx.Request("POST", url))

    monkeypatch.setattr(calibrate.httpx, "get", get)
    monkeypatch.setattr(calibrate.httpx, "post", post)
    return calls


def _manual(sid, ccf, start, end, kwh=300):
    return client.post("/calibrate", json={"session_id": sid, "therms": ccf * calibrate.THERMS_PER_CCF, "kwh": kwh,
                                           "start": start, "end": end})


def _err(r, status):
    assert r.status_code == status, r.text
    return r.json()["detail"]["code"]


# --- happy paths --------------------------------------------------------------------------------------------------

def test_manual_whole_month_percent_and_therms(fakes):
    r = client.post("/calibrate", json={"session_id": _session(), "therms": 103.7, "kwh": 300,
                                        "start": "2026-01-01", "end": "2026-01-31"})
    assert r.status_code == 200, r.text
    c = r.json()
    sent = fakes["model"][0]
    assert sent == {"year": 2026, "month": 1, "gas_ccf": 100.0, "lat": 42.2701, "lon": -83.7402, "unit_sqft": 850}
    assert c["pct_vs_expected_for_weather"] == -20.0  # model fraction -0.2 -> percent
    assert c["streak_months"] == 1 and c["badges"] == ["double-pane-club", "weather-beater"]  # app/badges.py
    assert (c["year"], c["month"], c["actual_gas_ccf"], c["expected_gas_ccf"]) == (2026, 1, 100.0, 125.0)
    assert c["noise_floor"] == 105.3 and c["meaningful"] is False
    assert "answers" not in c["estimate"] and "model_params" not in c["estimate"]
    assert c["estimate"]["grade"] == "B" and c["estimate"]["bill"]["annual"]["p50"] == 612.0
    assert c["extracted"]["electricity_kwh"] == 300 and "electricity" in c["note"].lower()
    assert not fakes["xai"]  # manual path never calls vision


def test_above_normal_no_badge_and_summer_noise_null():
    c = _manual(_session(), 150, "2025-07-01", "2025-07-31").json()
    assert c["pct_vs_expected_for_weather"] == 20.0 and c["badges"] == ["double-pane-club"] and c["streak_months"] == 0
    assert c["noise_floor"] is None and c["meaningful"] is None


def test_proration_to_the_month_with_most_days(fakes):
    # Jan 20 - Feb 24, 2026: 36 billing days, 12 in Jan, 24 in Feb -> Feb (28 days): 72 ccf x 28/36 = 56.0
    _manual(_session(), 72, "2026-01-20", "2026-02-24")
    assert (fakes["model"][0]["month"], fakes["model"][0]["gas_ccf"]) == (2, 56.0)


def test_month_usage():
    assert calibrate.month_usage(100, date(2025, 12, 1), date(2025, 12, 31), 850) == (2025, 12, 100.0)  # whole month
    assert calibrate.month_usage(62, date(2025, 11, 20), date(2025, 12, 20), 850) == (2025, 12, 62.0)  # 20 of 31 in Dec
    assert calibrate.month_usage(60, date(2025, 11, 1), date(2025, 11, 15), 850) == (2025, 11, 120.0)  # half month x2
    # cap: 23.36 ccf/1000 ft²/day -> 850 ft² x 31 days = 615.6 ccf
    assert calibrate.month_usage(615, date(2026, 1, 1), date(2026, 1, 31), 850)[2] == 615.0
    for bad in [(10, date(2026, 2, 1), date(2026, 1, 1)), (10, date(2025, 1, 1), date(2025, 6, 1)),
                (0, date(2026, 1, 1), date(2026, 1, 31)), (10, date.today().replace(day=1), date.today()),
                (617, date(2026, 1, 1), date(2026, 1, 31)), (48213, date(2026, 1, 1), date(2026, 1, 31))]:
        with pytest.raises(ValueError):
            calibrate.month_usage(*bad, 850)


def test_photo_path(fakes):
    img = base64.b64encode(b"\xff\xd8\xff\xe0 fake jpeg").decode()
    r = client.post("/calibrate", json={"session_id": _session(), "bill_image_base64": img})
    assert r.status_code == 200, r.text
    c = r.json()
    assert c["extracted"] == fakes["vision"]  # kWh and utility come back so the renter can confirm
    # Jan 5 - Feb 4: 31 days, 27 in Jan -> Jan; 95 ccf x 31/31
    assert (fakes["model"][0]["month"], fakes["model"][0]["gas_ccf"]) == (1, 95.0)
    assert c["pct_vs_expected_for_weather"] == -24.0
    req = fakes["xai"][0]
    assert req["headers"]["Authorization"] == "Bearer test-key" and req["json"]["model"] == calibrate.XAI_MODEL
    assert req["json"]["messages"][0]["content"][0]["image_url"]["url"] == f"data:image/jpeg;base64,{img}"
    assert req["json"]["response_format"]["json_schema"]["strict"] is True


def test_photo_in_therms(fakes):
    fakes["vision"] = {**fakes["vision"], "gas_usage": 103.7, "gas_unit": "therms"}
    client.post("/calibrate", json={"session_id": _session(), "bill_image_base64": "aGk="})
    assert fakes["model"][0]["gas_ccf"] == 100.0


def test_streak_counts_consecutive_months_below_normal():
    sid = _session()
    assert [_manual(sid, 100, f"2025-{m}-01", f"2025-{m}-28").json()["streak_months"] for m in (10, 11)] == [1, 2]
    assert _manual(sid, 100, "2025-12-01", "2025-12-31").json()["streak_months"] == 3
    assert _manual(sid, 150, "2025-12-01", "2025-12-31").json()["streak_months"] == 0  # re-sent Dec, now above: break
    assert _manual(sid, 100, "2026-01-01", "2026-01-31").json()["streak_months"] == 1
    assert _manual(sid, 100, "2025-12-01", "2025-12-31").json()["streak_months"] == 4  # Dec fixed: Oct-Jan
    other = _session("s2")  # streaks are per session; a skipped month breaks it
    _manual(other, 100, "2025-10-01", "2025-10-31")
    assert _manual(other, 100, "2025-12-01", "2025-12-31").json()["streak_months"] == 1


# --- errors -------------------------------------------------------------------------------------------------------

def test_unknown_session():
    r = client.post("/calibrate", json={"session_id": "nope", "therms": 50, "start": "2026-01-01", "end": "2026-01-31"})
    assert _err(r, 404) == "not_found" and r.json()["detail"]["message"] == "That session expired. Send the listing again."


def test_missing_input():
    assert _err(client.post("/calibrate", json={"session_id": _session(), "therms": 50}), 422) == "missing_input"


def test_bad_manual_bill():
    assert _err(_manual(_session(), 50, "2026-02-01", "2026-01-01"), 422) == "bad_bill"
    r = _manual(_session(), 2000, "2026-01-01", "2026-01-31")  # more than any 850 sq ft home uses
    assert _err(r, 422) == "bad_bill" and "850 sq ft" in r.json()["detail"]["message"]


@pytest.mark.parametrize("read", [{"gas_usage": None, "gas_unit": None}, {"gas_unit": None}, {"start": None},
                                  {"start": "2026-03-01"}, {"is_utility_bill": False}, {"gas_usage_visible": False},
                                  {"gas_usage_evidence": None}, {"gas_usage": 48213}])  # last: meter reading, not usage
def test_photo_without_gas_or_dates_is_unreadable(fakes, read):
    fakes["vision"] = {**fakes["vision"], **read}
    r = client.post("/calibrate", json={"session_id": _session(), "bill_image_base64": "aGk="})
    assert _err(r, 422) == "unreadable_bill" and "extracted" in r.json()["detail"] and not fakes["model"]


def test_photo_reads_that_disagree_are_unreadable(monkeypatch, fakes):  # an invented number changes between reads
    reads = iter([95, 147])

    def post(url, **kw):
        content = json.dumps({**fakes["vision"], "gas_usage": next(reads)})
        return httpx.Response(200, json={"choices": [{"message": {"content": content}}]}, request=httpx.Request("POST", url))
    monkeypatch.setattr(calibrate.httpx, "post", post)
    r = client.post("/calibrate", json={"session_id": _session(), "bill_image_base64": "aGk="})
    assert _err(r, 422) == "unreadable_bill" and not fakes["model"]


@pytest.mark.parametrize("status, content, code", [
    (400, None, "unreadable_bill"),  # xAI rejected the image
    (200, "Sorry, I can't read that.", "unreadable_bill"),  # not JSON
    (200, "[95, 412]", "unreadable_bill"),  # JSON, not an object
    (500, None, "vision_unavailable"), (401, None, "vision_unavailable"), (429, None, "vision_unavailable"),
])
def test_xai_failures(monkeypatch, status, content, code):
    body = {"choices": [{"message": {"content": content}}]} if content else {"error": "x"}
    monkeypatch.setattr(calibrate.httpx, "post", lambda url, **kw: httpx.Response(status, json=body,
                                                                                 request=httpx.Request("POST", url)))
    r = client.post("/calibrate", json={"session_id": _session(), "bill_image_base64": "aGk="})
    assert _err(r, 422 if code == "unreadable_bill" else 503) == code


def test_xai_unreachable(monkeypatch):
    def down(url, **kw):
        raise httpx.ConnectError("down")
    monkeypatch.setattr(calibrate.httpx, "post", down)
    r = client.post("/calibrate", json={"session_id": _session(), "bill_image_base64": "aGk="})
    assert _err(r, 503) == "vision_unavailable" and "Type the numbers" in r.json()["detail"]["message"]


def test_no_xai_key(monkeypatch, fakes):
    monkeypatch.delenv("XAI_API_KEY")
    r = client.post("/calibrate", json={"session_id": _session(), "bill_image_base64": "aGk="})
    assert _err(r, 503) == "vision_unavailable" and not fakes["xai"]


@pytest.mark.parametrize("fail", ["connect", 500, 422])
def test_model_unavailable(monkeypatch, fail):
    def get(url, **kw):
        if fail == "connect":
            raise httpx.ConnectError("down")
        return httpx.Response(fail, json={"detail": "boom"}, request=httpx.Request("GET", url))
    monkeypatch.setattr(calibrate.httpx, "get", get)
    assert _err(_manual(_session(), 100, "2026-01-01", "2026-01-31"), 503) == "model_unavailable"


# --- opt-in live xAI check (needs XAI_API_KEY in the real environment) --------------------------------------------

def _blank_png(w=64, h=64) -> str:
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))
    raw = b"".join(b"\x00" + b"\xff" * 3 * w for _ in range(h))
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
    return base64.b64encode(png).decode()


LIVE_KEY, REAL_POST = os.environ.get("XAI_API_KEY"), httpx.post  # before the autouse fakes replace them


@pytest.mark.skipif(not LIVE_KEY, reason="set XAI_API_KEY to run the live xAI vision check")
def test_live_xai_blank_image_is_unreadable(monkeypatch, fakes):
    """The real API takes our model name, image part and JSON schema, and a blank image doesn't pass as a bill."""
    monkeypatch.setenv("XAI_API_KEY", LIVE_KEY)
    monkeypatch.setattr(calibrate.httpx, "post", REAL_POST)
    r = client.post("/calibrate", json={"session_id": _session(), "bill_image_base64": _blank_png()})
    assert _err(r, 422) == "unreadable_bill", r.json()
    assert set(r.json()["detail"]["extracted"]) == set(calibrate.BILL_SCHEMA["required"]) and not fakes["model"]

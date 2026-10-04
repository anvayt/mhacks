"""Phase 2 persistence/verification; synthetic model and vision results, never real bill images."""

import base64
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy

import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import accounts, bills, calibrate, co2, commitments, db, sessions
from app.main import app

client = TestClient(app)
SID, PID = "saved-session", "home-1"


@pytest.fixture
def state(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "app.sqlite")
    monkeypatch.setattr(calibrate, "DB", tmp_path / "calibrate.sqlite")
    monkeypatch.setattr(sessions, "DB", str(tmp_path / "sessions.sqlite"))
    session = {"session_id": SID, "building": {"sqft": 850, "type": "Multi-Family with 5+ Units"},
               "bill": {"annual": {"p10": 700, "p50": 1000, "p90": 1400}}, "score": 40, "grade": "C",
               "grade_span": ["B", "C", "D"], "co2_t": {"p10": 2, "p50": 3, "p90": 4},
               "percentile_peers": .4, "percentile_city": .3, "model_version": "synthetic-test-model",
               "answers": {}, "model_params": {"lat": 42.27, "lon": -83.74, "unit_sqft": 850},
               "heating_cooling": {"annual": {"gas_ccf": 600, "electric_kwh": 300},
                  "months": [{"month": m, "heating": {"usd": 150, "gas_ccf": 100}} for m in range(1, 13)]}}
    sessions.save(session)
    prop = {"id": PID, "user_id": "u1", "session_id": SID, "active": True}
    c = {"id": "commitment1", "property_id": PID, "user_id": "u1", "catalog_id": "air_sealing",
         "status": "completed", "completed_at": "2025-12-15T12:00:00Z", "evidence": "reported"}
    state = {"session": session, "prop": prop, "commitments": [c], "noise": 1.183,
             "model_calls": [], "vision_calls": [], "authorized": []}
    monkeypatch.setattr(accounts, "get_property", lambda pid: deepcopy(prop) if pid == prop["id"] else None)
    def authorize(request, uid):
        state["authorized"].append(uid)
        if request.headers.get("X-Agent-Key") != "test-agent-key":
            raise HTTPException(403, {"code": "forbidden", "message": "This home belongs to another account."})
    monkeypatch.setattr(accounts, "authorize", authorize)
    monkeypatch.setattr(commitments, "list_commitments", lambda property_id=None, user_id=None: state["commitments"])
    def get(url, params, timeout):
        assert url.endswith("/hc/bill_check")
        state["model_calls"].append(params)
        pct = params["gas_ccf"] / 100 - 1
        return httpx.Response(200, request=httpx.Request("GET", url), json={
            "year": params["year"], "month": params["month"], "actual_gas_ccf": params["gas_ccf"],
            "expected_gas_ccf": 100, "pct_vs_expected_for_weather": pct, "noise_floor": state["noise"],
            "meaningful": abs(pct) > state["noise"] if state["noise"] is not None else None})
    monkeypatch.setattr(calibrate.httpx, "get", get)
    def read_bill(image):
        state["vision_calls"].append(image)
        return {"is_utility_bill": True, "gas_usage_visible": True, "gas_usage_evidence": "50 CCF",
                "gas_usage": 50, "gas_unit": "ccf", "electricity_kwh": 300,
                "start": "2026-01-01", "end": "2026-01-31", "utility": "Synthetic test utility"}
    monkeypatch.setattr(calibrate, "read_bill", read_bill)
    return state


def submit(**kwargs):
    return client.post("/calibrate", headers={"X-Agent-Key": "test-agent-key"}, json={
        "property_id": PID, "session_id": SID, "therms": 50 * co2.THERMS_PER_CCF,
        "start": "2026-01-01", "end": "2026-01-31", **kwargs})


def test_linked_bill_regrades_but_does_not_loosen_real_noise_or_change_session(state):
    r = submit()
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["bill_id"] and body["verified"] is False and body["impact"] is None
    assert body["noise_floor"] == 118.3 and body["pct_vs_expected_for_weather"] == -50
    snapshot = body["snapshot"]
    assert snapshot["source"] == "bill_regrade" and snapshot["label"] == "from your bill, adjusted for weather"
    assert snapshot["bill_annual"] == {"p10": 350, "p50": 500, "p90": 700}
    expected = bills.score_for(500, 850, "Multi-Family with 5+ Units")
    assert (snapshot["score"], snapshot["grade"]) == (expected["score"], expected["grade"])
    assert snapshot["co2_kg_yr"]["p50"] == round(co2.co2_kg(300, 300), 2)  # gas only; electricity unchanged
    assert sessions.get(SID) == state["session"] and body["estimate"]["bill"]["annual"]["p50"] == 1000
    assert state["authorized"] == ["u1"]
    assert len(bills.list_bills(PID)) == 1 and len(bills.list_snapshots(PID)) == 2
    assert bills.list_impact(PID) == []


def test_verified_period_stores_same_property_baseline_factors_and_real_price(state):
    state["noise"] = .3  # synthetic held-out error exercises the true path; real model thresholds are never changed
    baseline = bills.record_snapshot(PID, "initial_estimate", state["session"])
    r = submit()
    assert r.status_code == 200, r.text
    body, ledger = r.json(), bills.list_impact(PID)
    assert body["verified"] is True and body["verified_commitment_ids"] == ["commitment1"]
    assert len(ledger) == 1
    impact = ledger[0]
    assert impact["property_id"] == PID and impact["baseline_snapshot_id"] == baseline["id"]
    assert impact["therms_avoided"] == 51.85 and impact["kwh_avoided"] == 0
    assert impact["co2_kg_avoided"] == pytest.approx(51.85 * 5.306, abs=.0001)
    assert impact["usd_saved"] == 75 and impact["pricing"]["gas_usd_per_ccf"] == 1.5
    assert "rounded" in impact["pricing"]["source"]
    assert impact["pricing"]["method"] == "ratio_of_rounded_model_monthly_cost_and_use"
    assert impact["emission_factors"] == bills.FACTORS
    assert impact["emission_factors"]["egrid_year"] == 2023 and impact["emission_factors"]["ccf_to_therm"] == 1.037
    assert impact["commitment_ids"] == ["commitment1"]
    assert baseline["co2_kg_yr"]["p50"] == 3000 and bills.list_impact("other-home") == []


def test_dedupes_period_and_does_not_rerun_model_or_regrade(state):
    state["noise"] = .3
    first = submit().json()
    assert submit(therms=99).json() == first
    assert len(state["model_calls"]) == 1
    assert len(bills.list_bills(PID)) == len(bills.list_impact(PID)) == 1
    assert len(bills.list_snapshots(PID)) == 2


def test_image_hash_dedupe_before_vision_and_never_stores_photo(state):
    raw = b"synthetic private photograph" * 260000  # >6 MB decoded; no server upload-size truncation
    image = base64.b64encode(raw).decode()
    r = submit(bill_image_base64=image)
    assert r.status_code == 200, r.text
    again = submit(bill_image_base64="data:image/jpeg;base64," + image, start="2026-02-01", end="2026-02-28")
    assert again.json() == r.json() and len(state["vision_calls"]) == 1 and len(state["model_calls"]) == 1
    bill = bills.list_bills(PID)[0]
    assert bill["image_sha256"] == hashlib.sha256(raw).hexdigest() and bill["source"] == "image"
    stored = db.DB_PATH.read_bytes()
    assert raw[:200] not in stored and image[:200].encode() not in stored and b"bill_image_base64" not in stored


@pytest.mark.parametrize("change", [
    {"status": "accepted"}, {"property_id": "another-home"}, {"user_id": "another-user"},
    {"completed_at": "2026-01-15T12:00:00Z"}, {"completed_at": "2026-01-01T17:00:00Z"},
    {"completed_at": "2026-01-01T05:00:00Z"}, {"completed_at": "bad-date"}, {"catalog_id": "heat_pump"},
])
def test_ineligible_commitment_never_creates_impact(state, change):
    state["noise"] = .1
    state["commitments"][0].update(change)
    body = submit().json()
    assert body["verified"] is False and body["impact"] is None and not bills.list_impact(PID)


@pytest.mark.parametrize("noise,ccf,verified", [(.5, 50, False), (.499, 50, True), (None, 50, False),
                                              (1.183, 1, False), (.923, 5, True), (.1, 150, False)])
def test_d3_uses_actual_noise_with_strict_below_threshold(state, noise, ccf, verified):
    state["noise"] = noise
    body = submit(therms=ccf * co2.THERMS_PER_CCF).json()
    assert body["verified"] is verified
    assert bool(bills.list_impact(PID)) is verified


def test_partial_bill_and_archived_property_never_create_impact(state):
    state["noise"] = .1
    body = submit(end="2026-01-20", therms=10).json()
    assert body["verified"] is False and not bills.list_impact(PID)
    state["prop"]["active"] = False
    body = submit(start="2026-02-01", end="2026-02-28", therms=10).json()
    assert body["verified"] is False and not bills.list_impact(PID)


def test_overlapping_periods_never_double_count_impact(state):
    state["noise"] = .1
    assert submit().json()["verified"] is True
    body = submit(start="2026-01-05", end="2026-02-04", therms=10).json()
    assert body["verified"] is False and body["verification_status"] == "overlapping_verified_period"
    assert len(bills.list_impact(PID)) == 1 and len(bills.list_bills(PID)) == 2


def test_missing_price_records_no_invented_dollars_or_impact(state):
    state["noise"] = .1
    state["session"]["heating_cooling"]["months"] = []
    sessions.save(state["session"])
    body = submit().json()
    assert body["verified"] is True and body["impact"] is None
    assert "price_unavailable" in body["verification_status"] and not bills.list_impact(PID)


def test_other_property_cannot_borrow_old_baseline_or_commitment(state):
    old = bills.record_snapshot("old-home", "initial_estimate", state["session"])
    state["noise"] = .1
    state["commitments"][0]["property_id"] = "old-home"
    assert submit().json()["verified"] is False
    assert all(s["property_id"] == PID and s["id"] != old["id"] for s in bills.list_snapshots(PID))
    assert not bills.list_impact("old-home") and not bills.list_impact(PID)


def test_property_authorization_and_session_link_precede_processing(state):
    r = client.post("/calibrate", json={"session_id": SID, "property_id": PID, "bill_image_base64": "bad"})
    assert r.status_code == 403 and not state["vision_calls"] and not state["model_calls"]
    assert submit(property_id="missing").status_code == 404
    state["prop"]["session_id"] = "some-other-session"
    r = submit()
    assert r.status_code == 422 and r.json()["detail"]["code"] == "property_session_mismatch"
    assert not bills.list_bills(PID)


def test_anonymous_call_keeps_old_estimate_and_writes_no_phase_two_records(state):
    body = submit(property_id=None).json()
    assert body["estimate"]["bill"]["annual"]["p50"] == 1000
    assert body["bill_id"] is None and body["snapshot"] is None and body["verified"] is False
    assert not state["authorized"] and not bills.list_bills(PID) and not bills.list_snapshots(PID)


def test_projection_cannot_write_snapshot(state):
    with pytest.raises(HTTPException) as e:
        bills.record_snapshot(PID, "projection", state["session"])
    assert e.value.status_code == 422 and bills.list_snapshots(PID) == []


def test_concurrent_duplicate_creates_only_one_bill_regrade_and_impact(state):
    state["noise"] = .1
    with ThreadPoolExecutor(2) as pool:
        responses = list(pool.map(lambda _: submit(), range(2)))
    assert all(r.status_code == 200 for r in responses)
    assert responses[0].json() == responses[1].json()
    assert len(bills.list_bills(PID)) == len(bills.list_impact(PID)) == 1
    assert len(bills.list_snapshots(PID)) == 2



def test_same_image_cannot_be_counted_at_another_property(state):
    image = base64.b64encode(b"one private synthetic bill").decode()
    assert submit(bill_image_base64=image).status_code == 200
    state["prop"]["id"] = "second-home"
    r = submit(property_id="second-home", bill_image_base64=image)
    assert r.status_code == 409 and r.json()["detail"]["code"] == "bill_already_used"
    assert PID not in r.text and "bill_id" not in r.text
    assert not bills.list_bills("second-home") and len(state["vision_calls"]) == 1


def test_projected_body_cannot_be_disguised_as_initial_snapshot(state):
    with pytest.raises(HTTPException) as e:
        bills.record_snapshot(PID, "initial_estimate", {**state["session"], "label": "projected_if_completed"})
    assert e.value.status_code == 422 and bills.list_snapshots(PID) == []


def test_pure_verification_never_overrides_p1_meaningful_false(state):
    from datetime import date
    check = {"pct_vs_expected_for_weather": -.8, "noise_floor": .1, "meaningful": False}
    kwargs = {"property_id": PID, "user_id": "u1", "today": date(2026, 10, 4)}
    assert bills.verify_bill(check, date(2026, 1, 1), date(2026, 1, 31), state["commitments"], **kwargs) == []
    check["meaningful"] = True
    assert bills.verify_bill(check, date(2026, 1, 1), date(2026, 1, 31), state["commitments"], **kwargs) == ["commitment1"]

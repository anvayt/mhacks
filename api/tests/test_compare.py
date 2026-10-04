"""Listing battle contract; estimates are stubbed because the real call needs P1's model server."""

from copy import deepcopy
from threading import Barrier, get_ident

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
LISTINGS = [{"address": "1514 Morton Ave, Ann Arbor, MI", "unit_sqft": 850},
            {"url": "https://www.zillow.com/homedetails/912-Mary-St-Ann-Arbor-MI/123_zpid/", "unit_sqft": 850}]


def _estimate(p50, p10=None, p90=None, **extra):
    return {"session_id": "test-session", "building": {"sqft": 850},
            "bill": {"annual": {"p10": p10, "p50": p50, "p90": p90}}, "badges": [], **extra}


def _stub(monkeypatch, a, b):
    def estimate(url, address, unit_sqft):
        return a if address == LISTINGS[0]["address"] else b
    monkeypatch.setattr("app.estimate.estimate", estimate)


@pytest.mark.parametrize("a,b,winner,diff,confident", [
    (_estimate(1000.2, 900, 1100), _estimate(1400.8, 1200, 1600), "a", 401, True),
    (_estimate(1400, 1200, 1600), _estimate(1000, 900, 1100), "b", 400, True),
    (_estimate(1000, 900, 1300), _estimate(1200, 1100, 1400), "a", 200, False),
    (_estimate(1000, 900, 1100), _estimate(1200, 1100, 1400), "a", 200, False),  # touching
    (_estimate(1000), _estimate(1400), "a", 400, False),  # current dev has no intervals
    (_estimate(1000, 900, None), _estimate(1400, 1200, 1600), "a", 400, False),
    (_estimate(1000, 900, 1100), _estimate(1400, None, 1600), "a", 400, False),
    (_estimate(1000, 900, 1100), _estimate(1000, 900, 1100), "a", 0, False),
    (_estimate(1000, 1100, 900), _estimate(1400, 1200, 1600), "a", 400, False),  # invalid band
])
def test_winner_difference_confidence_and_winner_badge(monkeypatch, a, b, winner, diff, confident):
    _stub(monkeypatch, a, b)
    r = client.post("/compare", json={"listings": LISTINGS})
    assert r.status_code == 200, r.text
    result = r.json()
    assert set(result) == {"a", "b", "winner", "diff_usd_yr", "confident"}
    assert (result["winner"], result["diff_usd_yr"], result["confident"]) == (winner, diff, confident)
    assert result[winner]["badges"] == ["battle-winner"]
    assert result["b" if winner == "a" else "a"]["badges"] == []
    assert result["a"]["bill"] == a["bill"] and result["b"]["bill"] == b["bill"]


def test_estimates_run_concurrently_and_receive_both_listing_inputs(monkeypatch):
    barrier = Barrier(2)
    calls = []

    def estimate(url, address, unit_sqft):
        calls.append((url, address, unit_sqft, get_ident()))
        barrier.wait(timeout=5)  # serial calls would break the barrier instead of completing
        return _estimate(1000 if address else 1500)

    monkeypatch.setattr("app.estimate.estimate", estimate)
    r = client.post("/compare", json={"listings": LISTINGS})
    assert r.status_code == 200, r.text
    assert {(u, a, s) for u, a, s, _ in calls} == {
        (None, LISTINGS[0]["address"], 850), (LISTINGS[1]["url"], None, 850),
    }
    assert len({thread_id for *_, thread_id in calls}) == 2


@pytest.mark.parametrize("side,status", [("a", 422), ("b", 422), ("b", 503)])
def test_listing_error_preserves_details_and_identifies_side(monkeypatch, side, status):
    detail = {"code": "needs_address", "message": "What's the address?", "hint": "Mary St", "source": "listing"}

    def estimate(url, address, unit_sqft):
        if ("a" if address else "b") == side:
            raise HTTPException(status, detail)
        return _estimate(1000)

    monkeypatch.setattr("app.estimate.estimate", estimate)
    r = client.post("/compare", json={"listings": LISTINGS})
    assert r.status_code == status  # the listing's own status and code; extra fields (source) are dropped
    assert r.json() == {"detail": {"code": "needs_address", "listing": side, "message": "What's the address?",
                                   "hint": "Mary St"}}
    assert "listing" not in detail


def test_session_listing_uses_saved_answered_body(monkeypatch):
    saved = _estimate(900, session_id="answered", answers={"heating_fuel": "gas", "window_panes": "1"})
    monkeypatch.setattr("app.sessions.get", lambda sid: deepcopy(saved) if sid == "answered" else None)
    monkeypatch.setattr("app.estimate.estimate", lambda url, address, unit_sqft: _estimate(1500))
    r = client.post("/compare", json={"listings": [{"session_id": "answered"}, LISTINGS[0]]})
    assert r.status_code == 200, r.text
    assert r.json()["a"]["answers"] == saved["answers"] and r.json()["a"]["bill"] == saved["bill"]
    assert r.json()["winner"] == "a"


def test_unknown_session_listing_is_404(monkeypatch):
    monkeypatch.setattr("app.sessions.get", lambda sid: None)
    monkeypatch.setattr("app.estimate.estimate", lambda url, address, unit_sqft: _estimate(1500))
    r = client.post("/compare", json={"listings": [LISTINGS[0], {"session_id": "gone"}]})
    assert r.status_code == 404
    assert r.json()["detail"]["code"] == "not_found" and r.json()["detail"]["listing"] == "b"


@pytest.mark.parametrize("body", [{}, {"listings": None}, {"listings": []}, {"listings": LISTINGS[:1]},
                                  {"listings": LISTINGS + LISTINGS[:1]}, {"listings": "two"}])
def test_exactly_two_listings_required(monkeypatch, body):
    def unexpected(*args):
        pytest.fail("invalid comparison should not call the model")
    monkeypatch.setattr("app.estimate.estimate", unexpected)
    r = client.post("/compare", json=body)
    assert r.status_code == 422
    assert r.json()["detail"]["code"] == "missing_input"


def test_missing_body():
    r = client.post("/compare")
    assert r.status_code == 422 and r.json()["detail"]["code"] == "missing_input"


def test_empty_listing_identified_by_estimate_error(monkeypatch):
    def estimate(url, address, unit_sqft):
        if not (url or address):
            raise HTTPException(422, {"code": "missing_input", "message": "Send an address."})
        assert unit_sqft is None
        return _estimate(1000)
    monkeypatch.setattr("app.estimate.estimate", estimate)
    r = client.post("/compare", json={"listings": [{"address": "1514 Morton Ave"}, {}]})
    assert r.status_code == 422
    assert r.json()["detail"] == {"code": "missing_input", "message": "Send an address.", "listing": "b"}


def test_awards_rules_preserves_existing_badges_and_does_not_mutate_estimates(monkeypatch):
    a = _estimate(1000, score=90, answers={"window_panes": 2}, badges=["leak-hunter", "top-10-efficient"])
    b = _estimate(2000, score=95, badges=None)
    originals = deepcopy((a, b))
    _stub(monkeypatch, a, b)
    result = client.post("/compare", json={"listings": LISTINGS}).json()
    assert result["a"]["badges"] == ["leak-hunter", "top-10-efficient", "double-pane-club", "battle-winner"]
    assert result["b"]["badges"] == ["top-10-efficient"]
    assert (a, b) == originals


def test_shared_estimate_dictionary_does_not_give_both_sides_winner_badge(monkeypatch):
    est = _estimate(1000)
    _stub(monkeypatch, est, est)
    result = client.post("/compare", json={"listings": LISTINGS}).json()
    assert result["a"]["badges"] == ["battle-winner"]
    assert result["b"]["badges"] == [] and est["badges"] == []

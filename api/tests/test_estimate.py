"""POST /estimate glue (api/app/estimate.py). Error paths need at most the footprint cache; the full path needs
P1's model server (make -C model dashboard, MODEL_BASE_URL) and skips without it. No mocks: real services only."""

import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import estimate
from app.estimate import MODEL_BASE_URL
from app.geo import FOOTPRINTS_PATH
from app.main import app

client = TestClient(app)
CONTRACT = {"session_id", "building", "bill", "co2_t", "score", "grade", "grade_span", "locked",
            "percentile_peers", "percentile_city", "hidden_rent_usd_mo", "badges", "questions"}  # PLAN.md §10


def _model_up() -> bool:
    try:
        return httpx.get(f"{MODEL_BASE_URL}/hc/answers", timeout=2).status_code == 200
    except httpx.HTTPError:
        return False


needs_data = pytest.mark.skipif(not FOOTPRINTS_PATH.exists(), reason="run: uv run python scripts/fetch_footprints.py")
needs_model = pytest.mark.skipif(not _model_up(), reason=f"model server not running at {MODEL_BASE_URL}")


def _code(r) -> str:
    assert r.status_code == 422, r.text
    return r.json()["detail"]["code"]


def test_needs_input():
    assert _code(client.post("/estimate", json={})) == "missing_input"


def test_link_without_address_asks_for_it():  # hint-only site; never auto-geocoded (team decision)
    r = client.post("/estimate", json={"url": "https://www.zumper.com/apartment-buildings/p23039/715-arbor-st-ann-arbor-mi"})
    assert _code(r) == "needs_address" and "Arbor St" in r.json()["detail"]["hint"]


@pytest.mark.parametrize("sqft", [-50, 0, 1e9])
def test_bad_unit_sqft(sqft):  # the bill scales with unit size: -50 used to return -$81/yr
    r = client.post("/estimate", json={"address": "1514 Morton Ave, Ann Arbor, MI", "unit_sqft": sqft})
    assert _code(r) == "bad_unit_sqft"


@needs_data
@needs_model
def test_model_error_is_503(monkeypatch):  # a real non-422 error from the model server (404 here), not a bare 500
    monkeypatch.setattr("app.estimate.MODEL_BASE_URL", f"{MODEL_BASE_URL}/no-such-path")
    r = client.post("/estimate", json={"address": "1514 Morton Ave, Ann Arbor, MI 48104"})
    assert r.status_code == 503 and r.json()["detail"]["code"] == "model_unavailable"


def test_model_down_message_hides_internals(monkeypatch):  # no URL, make target or exception name for users
    monkeypatch.setattr("app.estimate.MODEL_BASE_URL", "http://127.0.0.1:9")
    with pytest.raises(HTTPException) as e:
        estimate._hc({"lat": 42.28, "lon": -83.74})
    assert e.value.status_code == 503
    assert e.value.detail == {"code": "model_unavailable", "message": estimate.MODEL_DOWN}


@needs_data
def test_not_a_home():  # UM LSA Building: Public footprint, no residential address
    assert _code(client.post("/estimate", json={"address": "500 S State St, Ann Arbor, MI 48109"})) == "not_a_home"


@needs_data
def test_outside_ann_arbor():
    r = client.post("/estimate", json={"address": "1600 Pennsylvania Ave NW, Washington, DC 20500"})
    assert _code(r) == "not_found"


@needs_data
@needs_model
@pytest.mark.parametrize("body", [
    {"address": "912 Mary St, Ann Arbor, MI 48104"},
    {"url": "https://www.zillow.com/homedetails/1514-Morton-Ave-Ann-Arbor-MI-48104/12345_zpid/"},
])
def test_real_estimate(body):
    r = client.post("/estimate", json=body)
    assert r.status_code == 200, r.text
    e = r.json()
    assert CONTRACT <= set(e)
    b, bill = e["building"], e["bill"]
    assert b["type"] and b["sqft"] > 0 and b["footprint_geojson"] and 42.2 < b["lat"] < 42.33
    assert list(bill["seasonal"]) == ["winter", "spring", "summer", "fall"]
    assert list(bill["monthly"]) == ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    assert abs(sum(m["p50"] for m in bill["monthly"].values()) - bill["annual"]["p50"]) <= 12  # P1 rounds per month
    assert bill["annual"]["p50"] > 0 and bill["seasonal"]["winter"]["p50"] > bill["seasonal"]["summer"]["p50"]
    assert e["heating_cooling"]["method"] in {"metered", "meter_model+resstock", "resstock"}

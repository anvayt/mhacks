"""CO₂ (app/co2.py) and GET /fixes/{session_id} (app/fixes.py). P1's model is monkeypatched with bodies shaped like
model/heating_cooling/service.py estimate_hc (annual.gas_ccf / electric_kwh / total_usd, method, building)."""

import httpx
import pytest
from fastapi.testclient import TestClient

from app import fixes, sessions
from app.co2 import co2_kg, co2_t
from app.main import app

client = TestClient(app)
FIX_KEYS = {"item", "grh_points", "co2_kg_saved", "usd_saved_yr", "cost_usd", "rebate_usd", "new_grade"}  # agent/src/api.ts Fix


def hc(gas_ccf, kwh, usd, method="resstock", fuel="gas"):
    return {"method": method, "building": {"heating_fuel": fuel, "year_built": 1965},
            "unit_sqft": 850.0, "seasons": [], "months": [],
            "annual": {"heating_usd": usd - 90, "cooling_usd": 90, "total_usd": usd, "gas_ccf": gas_ccf,
                       "electric_kwh": kwh, "hdd65": 6420, "cdd65": 690, "tmean_f": 49.4}}


BASE = hc(520.0, 900, 820)                          # gas heat
WINDOWS = hc(450.0, 880, 740)                       # + window_panes=2
E_BASE = hc(0.0, 16316, 3199, fuel="electric")      # electric heat: 912 Mary St on the live model
E_HEAT_PUMP = hc(0.0, 11368, 2236, fuel="electric")  # + cooling_code=3 (live model)


def fake_model(calls):
    def get(url, params=None, timeout=None):
        calls.append(params)
        assert url.endswith("/hc/estimate")
        body = E_HEAT_PUMP if params.get("cooling_code") == 3 else WINDOWS if params.get("window_panes") == 2 else BASE
        return httpx.Response(200, json=body)
    return get


def session(sid="s1", method="resstock", base=BASE, **answers):
    body = {"session_id": sid,
            "building": {"lat": 42.27, "lon": -83.74, "address": "912 Mary St, Ann Arbor, MI 48104", "sqft": 850.0,
                         "type": "Multi-Family with 2 - 4 Units"},
            "bill": {"annual": {"p10": None, "p50": base["annual"]["total_usd"], "p90": None}},
            "heating_cooling": dict(base, method=method),
            # answers as P2-04's /answer stores them: option value strings
            "answers": {q: str(v) for q, v in answers.items()},
            "model_params": {"lat": 42.27, "lon": -83.74, "unit_sqft": 850.0,
                             "building_type": "Multi-Family with 2 - 4 Units", "block_group": "261614001001"}}
    sessions.save(body)
    return sid


@pytest.fixture
def calls(monkeypatch):
    c = []
    monkeypatch.setattr("app.estimate.httpx.get", fake_model(c))
    monkeypatch.setattr("app.fixes.score_for", lambda annual, sqft, t: {"grade": "B" if annual < 800 else "C"})
    return c


# ------------------------------------------------------------------ CO₂
def test_co2_kg_known_amounts():
    assert co2_kg(0, 0) == 0
    assert co2_kg(100, 0) == pytest.approx(550.23, abs=0.01)  # 100 ccf × 1.037 therm/ccf (EIA) × 5.306 kg/therm (EPA)
    assert co2_kg(0, 1000) == pytest.approx(440.26, abs=0.01)  # 1 MWh × 970.6 lb/MWh (eGRID2023 RFCM)
    assert co2_kg(100, 1000) == pytest.approx(co2_kg(100, 0) + co2_kg(0, 1000))


def test_co2_t_band():
    t = co2_t(BASE)
    assert t["p50"] == pytest.approx(co2_kg(520, 900) / 1000, abs=0.01) and t["p10"] is None and t["p90"] is None
    assert co2_t(BASE, {"annual": {"p10": None, "p50": 820, "p90": None}})["p10"] is None
    t = co2_t(BASE, {"annual": {"p10": 615, "p50": 820, "p90": 1230}})
    assert t["p10"] == pytest.approx(t["p50"] * 0.75, abs=0.01) and t["p90"] == pytest.approx(t["p50"] * 1.5, abs=0.01)


# ------------------------------------------------------------------ /fixes
def test_fixes_priced_from_model(calls):
    r = client.get(f"/fixes/{session(window_panes=1, cooling_code=2)}")
    assert r.status_code == 200, r.text
    f = {x["item"]: x for x in r.json()["fixes"]}
    w, hp = f[fixes.WINDOWS["item"]], f[fixes.HEAT_PUMP["item"]]
    assert w["usd_saved_yr"] == 80 and w["co2_kg_saved"] == round(co2_kg(70, 20)) and w["new_grade"] == "B"
    assert not w["unpriced"]
    # one changed input on top of the session's params
    assert calls == [{"lat": 42.27, "lon": -83.74, "unit_sqft": 850.0, "building_type": "Multi-Family with 2 - 4 Units",
                      "block_group": "261614001001", "window_panes": 2, "cooling_code": 2}]
    # gas → heat pump: P1's electric-heat homes aren't cold-climate heat pumps, so it's unpriced, with all 35 points
    assert hp["unpriced"] and hp["usd_saved_yr"] is None and hp["grh_points"] == 35 and hp["rebate_usd"] == 4000


def test_heat_pump_priced_for_electric_heat(calls):  # resistance → heat pump; fuel from the model's lookup
    sid = session(base=E_BASE, window_panes=2, cooling_code=2)
    hp = {x["item"]: x for x in client.get(f"/fixes/{sid}").json()["fixes"]}[fixes.HEAT_PUMP["item"]]
    assert hp["usd_saved_yr"] == 963 and hp["co2_kg_saved"] == round(co2_kg(0, 16316 - 11368)) and hp["new_grade"] == "C"
    assert not hp["unpriced"] and hp["grh_points"] == 20  # "electricity is primary" (15) is already earned
    assert len(calls) == 1 and calls[0]["heating_fuel"] == "electric" and calls[0]["cooling_code"] == 3


def test_no_ac_never_sends_cooling_code_0_and_marks_used_fixes(calls):
    sid = session(window_panes=1, cooling_code=0)
    client.get(f"/fixes/{sid}")
    assert calls and all("cooling_code" not in c for c in calls)  # 0 is outside P1's training data
    assert sessions.get(sid)["used_fixes"]  # badges: leak-hunter


def test_heat_included_saves_the_renter_cooling_only(calls):  # wave 6: the building's fuel stays the model's
    w = {x["item"]: x for x in client.get(f"/fixes/{session(heating_fuel='included', window_panes=1)}").json()["fixes"]}
    assert all("heating_fuel" not in c for c in calls)
    win = w[fixes.WINDOWS["item"]]
    assert win["usd_saved_yr"] == 0 and win["co2_kg_saved"] == round(co2_kg(70, 20))  # cooling $90 → $90; CO₂ is the building's


def test_fix_the_model_says_adds_co2_is_listed_unpriced(calls):  # WINDOWS (450 ccf) adds 50 ccf to this base
    sid = session(base=hc(400.0, 900, 700))
    w = {x["item"]: x for x in client.get(f"/fixes/{sid}").json()["fixes"]}[fixes.WINDOWS["item"]]
    assert w["unpriced"] and w["usd_saved_yr"] is None and w["co2_kg_saved"] is None and w["grh_points"] == 4


def test_shape_matches_agent_types(calls):
    body = client.get(f"/fixes/{session()}").json()
    assert isinstance(body["grh_points_now"], int) and isinstance(body["grh_points_after"], int)
    assert isinstance(body["landlord_email"], str) and body["fixes"]
    for x in body["fixes"]:
        assert FIX_KEYS <= set(x) and isinstance(x["item"], str) and isinstance(x["grh_points"], int)
        for k in ("co2_kg_saved", "usd_saved_yr", "cost_usd", "rebate_usd"):
            assert x[k] is None or isinstance(x[k], int)
    assert body["grh_points_after"] == body["grh_points_now"] + sum(x["grh_points"] for x in body["fixes"])


def test_unpriced_fixes_are_null_and_last(calls):
    fx = client.get(f"/fixes/{session()}").json()["fixes"]
    flags = [x["unpriced"] for x in fx]
    assert flags == sorted(flags) and flags[-1]  # priced first, unpriced last
    for x in fx:
        if x["unpriced"]:
            assert x["usd_saved_yr"] is None and x["co2_kg_saved"] is None and x["new_grade"] is None
    assert {"Air sealing (blower-door tested)", "Attic insulation to R-50"} <= {x["item"] for x in fx}


def test_skips_what_the_unit_already_has(calls):
    items = {x["item"] for x in client.get(f"/fixes/{session(window_panes=2)}").json()["fixes"]}
    assert fixes.WINDOWS["item"] not in items and fixes.HEAT_PUMP["item"] in items
    items = {x["item"] for x in client.get(f"/fixes/{session(base=E_BASE, cooling_code=3)}").json()["fixes"]}
    assert fixes.HEAT_PUMP["item"] not in items and fixes.WINDOWS["item"] in items


def test_metered_building_lists_model_fixes_unpriced(calls):  # answers don't enter a building's own meter fit
    fx = client.get(f"/fixes/{session(method='metered', window_panes=1)}").json()["fixes"]
    assert calls == [] and all(x["unpriced"] for x in fx)
    assert fixes.WINDOWS["item"] in {x["item"] for x in fx}


def test_rank_by_co2_per_net_dollar():
    def f(name, co2, cost, rebate=None, unpriced=False):
        return {"item": name, "co2_kg_saved": co2, "cost_usd": cost, "rebate_usd": rebate, "unpriced": unpriced}
    fx = [f("unpriced", None, 100, unpriced=True), f("no cost", 900, None), f("cheap", 300, 400, 100),
          f("dear", 1000, 5000), f("free after rebate", 50, 300, 300)]
    assert [x["item"] for x in sorted(fx, key=fixes._rank)] == ["free after rebate", "cheap", "dear", "no cost", "unpriced"]


def test_grh_points_from_answers_only(calls):
    assert client.get(f"/fixes/{session()}").json()["grh_points_now"] == 0  # block-group fuel isn't an answer
    body = client.get(f"/fixes/{session(heating_fuel='electric', cooling_code=2)}").json()
    assert body["grh_points_now"] == 17  # electric primary heat 15 + space cooling 2


def test_landlord_email_is_deterministic(calls):
    sid = session(window_panes=1)
    a, b = (client.get(f"/fixes/{sid}").json() for _ in range(2))
    e = a["landlord_email"]
    assert e == b["landlord_email"]
    assert "912 Mary St" in e and "Green Rental Housing" in e and "70" in e and "$80/yr less" in e
    assert f"bring it to {a['grh_points_after']}" in e


def test_unknown_session_404():
    r = client.get("/fixes/nope")
    assert r.status_code == 404 and r.json()["detail"] == {"code": "not_found", "message": fixes.EXPIRED}


def test_model_down_503(monkeypatch):
    def down(*a, **k):
        raise httpx.ConnectError("refused")
    monkeypatch.setattr("app.estimate.httpx.get", down)
    r = client.get(f"/fixes/{session()}")
    assert r.status_code == 503 and r.json()["detail"]["code"] == "model_unavailable"

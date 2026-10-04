"""Commitments + /projection (app/commitments.py). P1's model is monkeypatched with bodies shaped like
model/heating_cooling/service.py estimate_hc; each property is a real app/accounts.py row pointing at a session."""

import json
from contextlib import closing

import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import accounts, commitments, sessions
from app.co2 import co2_kg
from app.main import app
from app.score import grade_of

client = TestClient(app)


def hc(gas_ccf, kwh, usd, fuel="gas", method="resstock"):
    return {"method": method, "building": {"heating_fuel": fuel, "year_built": 1965}, "unit_sqft": 850.0,
            "seasons": [], "months": [],
            "annual": {"heating_usd": usd - 90, "cooling_usd": 90, "total_usd": usd, "gas_ccf": gas_ccf,
                       "electric_kwh": kwh}}


# (block_group, window_panes == 2, heat pump) -> model body. "elec" = 912 Mary St-like electric heat.
MODEL = {("gas", False, False): hc(520.0, 900, 820), ("gas", True, False): hc(450.0, 880, 740),
         ("elec", False, False): hc(0.0, 16316, 3199, "electric"), ("elec", True, False): hc(0.0, 15500, 3050, "electric"),
         ("elec", False, True): hc(0.0, 11368, 2236, "electric"), ("elec", True, True): hc(0.0, 10800, 2130, "electric"),
         ("noisy", False, False): hc(400.0, 900, 700), ("noisy", True, False): hc(450.0, 880, 740)}


def fake_score(annual, sqft, btype):
    score = max(0, round(100 - annual / 40))
    return {"score": score, "grade": grade_of(score), "percentile_city": score / 100}


@pytest.fixture(autouse=True)
def env(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.sqlite")
    monkeypatch.setattr("app.commitments.score_for", fake_score)


@pytest.fixture
def calls(monkeypatch):
    c = []

    def get(url, params=None, timeout=None):
        c.append(params)
        hp = params.get("cooling_code") == 3 and params.get("heating_fuel") == "electric"
        return httpx.Response(200, json=MODEL[(params["block_group"], params.get("window_panes") == 2, hp)])
    monkeypatch.setattr("app.estimate.httpx.get", get)
    return c


def home(pid="p1", kind="gas", user="u1", method="resstock", **answers):
    """A user + property (accounts' own tables) pointing at a fresh session (answers as /answer stores them)."""
    base = MODEL[(kind, False, False)]
    sid = f"s-{pid}"
    sessions.save({"session_id": sid,
                   "building": {"address": "912 Mary St, Ann Arbor, MI 48104", "sqft": 850.0,
                                "type": "Multi-Family with 2 - 4 Units"},
                   "bill": {"annual": {"p10": round(base["annual"]["total_usd"] * 0.8),
                                       "p50": base["annual"]["total_usd"],
                                       "p90": round(base["annual"]["total_usd"] * 1.3)}},
                   **fake_score(base["annual"]["total_usd"], 850, None),
                   "heating_cooling": dict(base, method=method), "answers": {q: str(v) for q, v in answers.items()},
                   "model_params": {"lat": 42.27, "lon": -83.74, "unit_sqft": 850.0,
                                    "building_type": "Multi-Family with 2 - 4 Units", "block_group": kind}})
    with closing(accounts._con()) as con, con:
        con.execute("INSERT OR IGNORE INTO users (id, phone_number, reminder_prefs, created_at) VALUES (?, ?, ?, ?)",
                    (user, f"test:{user}", json.dumps(accounts.DEFAULT_PREFS), accounts._now()))
        active = not con.execute("SELECT 1 FROM properties WHERE user_id = ? AND active = 1", (user,)).fetchone()
        con.execute("INSERT INTO properties (id, user_id, address, session_id, active, move_in_date) "
                    "VALUES (?, ?, '912 Mary St', ?, ?, '2026-10-04')", (pid, user, sid, int(active)))
    return pid


def suggested(pid):
    r = client.get(f"/commitments/suggested/{pid}")
    assert r.status_code == 200, r.text
    return {c["catalog_id"]: c for c in r.json()["commitments"]}, [c["catalog_id"] for c in r.json()["commitments"]]


def accept(pid, cid, user="u1"):
    r = client.post("/commitments", json={"user_id": user, "property_id": pid, "catalog_id": cid})
    assert r.status_code == 200, r.text
    return r.json()


def project(pid, ids):
    r = client.post("/projection", json={"property_id": pid, "commitment_ids": ids})
    assert r.status_code == 200, r.text
    return r.json()


# ------------------------------------------------------------------ suggested
def test_gas_home_windows_modeled_rest_placeholders(calls):
    by, order = suggested(home(window_panes=1))
    assert set(by) == set(commitments.CATALOG)
    w = by["window_upgrade"]
    assert w["projected"] == {"usd_saved_yr": 80, "co2_kg_saved_yr": round(co2_kg(70, 20)), "score_delta": 2,
                              "new_grade": "A", "label": "projected_if_completed"} and not w["pending_model"]
    assert order[0] == "window_upgrade" and len(calls) == 1 and calls[0]["window_panes"] == 2
    for cid in set(by) - {"window_upgrade"}:  # gas → heat pump too: P1 prices it like resistance heat
        c = by[cid]
        assert c["pending_model"] and c["projected"] is None and c["co2_per_net_usd"] is None
        assert c["method"] == commitments.PENDING
    assert by["heat_pump"]["grh_points"] == 35 and by["heat_pump"]["cost_usd"] == 15_400
    assert {"renter", "renter→landlord"} & {by[c]["who_acts"] for c in order}
    assert order.index("thermostat_setback") < order.index("air_sealing")  # renter-doable placeholders first
    t = by["thermostat_setback"]
    assert "64°F" in t["note"] and commitments.WHO_HOUSING in t["sources"]


def test_electric_home_ranked_by_co2_per_net_dollar(calls):
    by, order = suggested(home(kind="elec", window_panes=1, cooling_code=2))
    hp, w = by["heat_pump"], by["window_upgrade"]
    kg = round(co2_kg(0, 16316 - 11368))
    assert hp["projected"]["co2_kg_saved_yr"] == kg and hp["projected"]["usd_saved_yr"] == 963
    assert hp["co2_per_net_usd"] == round(kg / (15_400 - 4_000), 4) and hp["grh_points"] == 20
    assert w["co2_per_net_usd"] is None  # windows have no cited unit cost: after known-cost actions
    assert order[:2] == ["heat_pump", "window_upgrade"] and len(calls) == 2


def test_rank_rule():
    def c(name, kg, ratio, who="landlord"):
        return {"catalog_id": name, "who_acts": who, "co2_per_net_usd": ratio,
                "projected": None if kg is None else {"co2_kg_saved_yr": kg}}
    items = [c("pending landlord", None, None), c("pending renter", None, None, "renter"), c("no cost", 900, None),
             c("tie low", 100, 0.5), c("tie high", 300, 0.5), c("best", 50, 2.0)]
    assert [x["catalog_id"] for x in sorted(items, key=commitments._rank)] == \
        ["best", "tie high", "tie low", "no cost", "pending renter", "pending landlord"]


def test_skips_what_the_home_already_has(calls):
    by, _ = suggested(home(window_panes=2))
    assert "window_upgrade" not in by and calls == []
    by, _ = suggested(home("p2", kind="elec", cooling_code=3))
    assert "heat_pump" not in by
    assert by["landlord_request"]["requests"] == "window_upgrade"


def test_metered_building_is_all_placeholders(calls):
    by, _ = suggested(home(method="metered", window_panes=1))
    assert calls == [] and all(c["pending_model"] for c in by.values())


def test_landlord_request_inherits_the_fix_once_done(calls):
    pid = home(window_panes=1)
    by, _ = suggested(pid)
    assert by["landlord_request"]["pending_model"] and by["landlord_request"]["requests"] == "window_upgrade"
    assert by["landlord_request"]["grh_points"] == by["window_upgrade"]["grh_points"]
    w = accept(pid, "window_upgrade")
    client.patch(f"/commitments/{w['id']}", json={"status": "completed"})
    by, _ = suggested(pid)
    assert by["landlord_request"]["projected"] == by["window_upgrade"]["projected"]


# ------------------------------------------------------------------ accept / complete / dismiss
def test_accept_is_idempotent(calls):
    pid = home()
    a = accept(pid, "air_sealing")
    assert a["status"] == "accepted" and a["evidence"] == "projected" and a["accepted_at"] and a["user_id"] == "u1"
    assert accept(pid, "air_sealing")["id"] == a["id"]
    assert [c["id"] for c in client.get("/commitments", params={"property_id": pid}).json()["commitments"]] == [a["id"]]
    assert client.get("/commitments", params={"user_id": "u1"}).json()["commitments"][0]["id"] == a["id"]
    assert commitments.list_commitments(user_id="nobody") == []


def test_state_machine_has_no_backward_moves(calls):
    pid = home()
    before = sessions.get(f"s-{pid}")
    a = accept(pid, "thermostat_setback")
    r = client.patch(f"/commitments/{a['id']}", json={"status": "completed"})
    assert r.status_code == 200 and r.json()["evidence"] == "reported" and r.json()["completed_at"]
    assert client.patch(f"/commitments/{a['id']}", json={"status": "completed"}).status_code == 200  # repeat: no-op
    r = client.patch(f"/commitments/{a['id']}", json={"status": "dismissed"})
    assert r.status_code == 409 and r.json()["detail"]["code"] == "bad_transition"
    assert client.patch(f"/commitments/{a['id']}", json={"status": "accepted"}).status_code == 422
    assert sessions.get(f"s-{pid}") == before  # completing never changes the current grade

    b = accept(pid, "air_sealing")
    assert client.patch(f"/commitments/{b['id']}", json={"status": "dismissed"}).json()["status"] == "dismissed"
    assert client.patch(f"/commitments/{b['id']}", json={"status": "completed"}).status_code == 409
    assert accept(pid, "air_sealing")["id"] != b["id"]  # a fresh accept after dismissing is a new commitment


def test_errors(calls):
    pid = home()
    assert client.get("/commitments/suggested/nope").status_code == 404
    r = client.post("/commitments", json={"user_id": "u1", "property_id": pid, "catalog_id": "solar"})
    assert r.status_code == 422 and r.json()["detail"]["code"] == "unknown_action"
    r = client.post("/commitments", json={"user_id": "u2", "property_id": pid, "catalog_id": "air_sealing"})
    assert r.status_code == 404  # someone else's home
    assert client.patch("/commitments/nope", json={"status": "completed"}).status_code == 404
    r = client.post("/projection", json={"property_id": pid, "commitment_ids": ["cmt_nope"]})
    assert r.status_code == 422 and r.json()["detail"]["code"] == "unknown_commitment"
    assert client.get("/commitments").status_code == 422


def test_auth_uses_the_homes_owner(calls, monkeypatch):
    pid = home(user="u7")
    a = accept(pid, "air_sealing", user="u7")
    seen = []

    def deny(request, user_id):
        seen.append(user_id)
        raise HTTPException(403, {"code": "forbidden", "message": "Open this from your own texts or account."})
    monkeypatch.setattr(accounts, "authorize", deny)
    assert client.get(f"/commitments/suggested/{pid}").status_code == 403
    assert client.post("/projection", json={"property_id": pid, "commitment_ids": []}).status_code == 403
    assert client.post("/commitments", json={"user_id": "u7", "property_id": pid,
                                             "catalog_id": "heat_pump"}).status_code == 403
    assert client.patch(f"/commitments/{a['id']}", json={"status": "completed"}).status_code == 403
    assert client.get("/commitments", params={"property_id": pid}).status_code == 403
    assert seen == ["u7"] * 5 and calls == []


# ------------------------------------------------------------------ /projection
def test_projection_is_one_composed_run(calls):
    pid = home(kind="elec", window_panes=1, cooling_code=2)
    ids = [accept(pid, c)["id"] for c in ("window_upgrade", "heat_pump", "air_sealing")]
    calls.clear()
    p = project(pid, ids)
    composed = [c for c in calls if c.get("window_panes") == 2 and c.get("cooling_code") == 3]
    assert len(composed) == 1 and len(calls) == 3  # two single runs (screening, as in suggested) + ONE composed run
    assert p["modeled"] == ["window_upgrade", "heat_pump"] and p["not_modeled"] == ["air_sealing"]
    both = MODEL[("elec", True, True)]["annual"]
    assert p["projected"]["bill_annual"]["p50"] == 2130 and p["projected"]["score"] == fake_score(2130, 0, 0)["score"]
    assert p["projected"]["bill_annual"]["p10"] == round(2130 * round(3199 * 0.8) / 3199)  # current band's ratios
    assert p["delta"]["usd_saved_yr"] == 3199 - 2130
    assert p["delta"]["co2_kg_saved_yr"] == round(co2_kg(0, 16316 - both["electric_kwh"]))
    assert p["delta"]["score"] == p["projected"]["score"] - p["current"]["score"]
    # composed, never the sum of separate deltas (window 149 + heat pump 963 here)
    assert p["delta"]["usd_saved_yr"] != (3199 - 3050) + (3199 - 2236)
    assert p["label"] == p["projected"]["label"] == p["delta"]["label"] == "projected_if_completed"
    assert p["current"]["bill_annual"] == sessions.get(f"s-{pid}")["bill"]["annual"]
    assert p["projected"]["percentile_city"] is not None and p["method"] == "model_rerun"
    assert all(c["projection_id"] == p["id"] for c in commitments.list_commitments(pid)[:3])


def test_zero_modeled_is_no_change(calls):
    pid = home(window_panes=1)
    p = project(pid, [accept(pid, "air_sealing")["id"], "thermostat_setback"])
    assert calls == [] and p["not_modeled"] == ["air_sealing", "thermostat_setback"] and p["modeled"] == []
    assert {k: v for k, v in p["projected"].items() if k != "label"} == p["current"]
    assert p["delta"] == {"score": 0, "usd_saved_yr": 0, "co2_kg_saved_yr": 0, "label": "projected_if_completed"}
    assert project(pid, [])["projected"]["score"] == p["current"]["score"]


def test_removing_a_commitment_reverses(calls):
    pid = home(kind="elec", window_panes=1, cooling_code=2)
    w, hp = accept(pid, "window_upgrade")["id"], accept(pid, "heat_pump")["id"]
    only_w = project(pid, [w])
    project(pid, [w, hp])
    again = project(pid, [w])
    assert again["projected"] == only_w["projected"] and again["delta"] == only_w["delta"]
    assert project(pid, [])["delta"]["usd_saved_yr"] == 0


def test_projection_never_touches_the_session(calls):
    pid = home(kind="elec", window_panes=1)
    before = sessions.get(f"s-{pid}")
    p = project(pid, ["window_upgrade", "heat_pump"])  # catalog ids: a what-if before accepting
    assert sessions.get(f"s-{pid}") == before
    assert commitments.latest_projection(pid) == p and commitments.list_commitments(pid) == []


def test_a_change_the_model_says_adds_co2_is_shown_without_numbers(calls):
    pid = home(kind="noisy", window_panes=1)  # double-pane comes out +50 ccf here (model noise)
    w = suggested(pid)[0]["window_upgrade"]
    assert w["pending_model"] and w["projected"] is None and w["method"] == commitments.NO_CUT
    p = project(pid, ["window_upgrade"])
    assert p["not_modeled"] == ["window_upgrade"] and p["delta"]["usd_saved_yr"] == 0


def test_model_down_503(monkeypatch):
    def down(*a, **k):
        raise httpx.ConnectError("refused")
    monkeypatch.setattr("app.estimate.httpx.get", down)
    r = client.get(f"/commitments/suggested/{home(window_panes=1)}")
    assert r.status_code == 503 and r.json()["detail"]["code"] == "model_unavailable"


def test_joined_with_real_accounts():  # merge wave 5a: accounts' property, prefs and history + commitments
    pid = home()
    p = accounts.get_property(pid)
    assert p["user_id"] == "u1" and p["session_id"] == f"s-{pid}"
    r = client.post("/commitments", json={"user_id": "u1", "property_id": pid, "catalog_id": "air_sealing",
                                          "target_date": "2026-11-01"})
    assert r.json()["reminder_channel"] == accounts.DEFAULT_PREFS["channel"]  # from the user's reminder_prefs
    hist = client.get(f"/properties/{pid}/history").json()
    assert [c["catalog_id"] for c in hist["commitments"]] == ["air_sealing"]

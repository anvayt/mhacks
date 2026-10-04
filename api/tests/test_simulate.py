"""POST /simulate/fast-forward (app/simulate.py): seasonal weights keep the annual delta, nothing is stored,
placeholders give 0, auth. P1's model is the fake in test_commitments; the 1991-2020 history is synthetic."""

import datetime as dt
import math
import sqlite3
from contextlib import closing

import pytest
from fastapi.testclient import TestClient

from app import commitments, forecast, habits, sessions, simulate
from app.co2 import co2_kg
from app.main import app
from tests.test_commitments import calls, env, home  # noqa: F401  (fixtures: fake model + temp app DB)

client = TestClient(app)
AGENT = {"X-Agent-Key": "test-agent-key"}


@pytest.fixture(autouse=True)
def world(monkeypatch, tmp_path):
    monkeypatch.setenv("AGENT_API_KEY", "test-agent-key")
    monkeypatch.setattr(sessions, "DB", str(tmp_path / "sessions.sqlite"))
    monkeypatch.setattr(habits, "_now", lambda: dt.datetime.fromisoformat("2026-10-04T12:00:00-04:00"))
    # a cold January, a warm July (deg C), every day of 1991-2020
    history = {dt.date(1991, 1, 1) + dt.timedelta(i): 10 - 15 * math.cos(2 * math.pi * (i % 365 - 15) / 365)
               for i in range((dt.date(2021, 1, 1) - dt.date(1991, 1, 1)).days)}
    seen = []
    monkeypatch.setattr(forecast, "_history", lambda lat, lon: seen.append((lat, lon)) or history)
    simulate._weights.cache_clear()
    return seen


def ff(**body):
    return client.post("/simulate/fast-forward", json=body, headers=AGENT)


def ok(res):
    assert res.status_code == 200, res.text
    return res.json()


def test_365_days_add_up_to_the_annual_delta_and_january_saves_more_than_october(calls):
    sid = f"s-{home(window_panes=1)}"
    r = ok(ff(session_id=sid, days=365, catalog_ids=["window_upgrade"]))
    assert r["annual"] == {"usd_saved_yr": 80, "co2_kg_saved_yr": round(co2_kg(70, 20)), "label": "projected_if_completed"}
    assert abs(r["totals"]["usd_saved"] - 80) < 0.05 and abs(r["totals"]["kg_co2_saved"] - r["annual"]["co2_kg_saved_yr"]) < 0.05
    by_date = {d["date"]: d for d in r["days"]}
    assert r["start_date"] == "2026-10-04" and r["days"][0]["date"] == "2026-10-05" and r["totals"]["end_date"] == "2027-10-04"
    assert by_date["2027-01-15"]["usd_saved"] > by_date["2026-10-05"]["usd_saved"] > by_date["2027-07-15"]["usd_saved"] == 0
    assert r["days"][-1]["cumulative_usd"] == r["totals"]["usd_saved"] and r["days"][-1]["habit_day"] == 365
    assert r["label"] == "simulated_projected_if_kept" and r["label_text"].startswith("Simulated")
    week = ok(ff(session_id=sid, days=7, catalog_ids=["window_upgrade"]))
    assert week["days"] == r["days"][:7]  # same days, same numbers: deterministic, no flat /365


def test_placeholders_give_zero_without_the_model_or_weather(calls, world):
    sid = f"s-{home(window_panes=1)}"
    r = ok(ff(session_id=sid, days=30, catalog_ids=["thermostat_setback", "air_sealing"]))
    assert r["totals"]["usd_saved"] == r["totals"]["kg_co2_saved"] == 0 and r["modeled"] == []
    assert r["not_modeled"] == ["thermostat_setback", "air_sealing"] and calls == [] and world == []
    assert [c["modeled"] for c in r["commitments"]] == [False, False]


def tables():
    rows = {}
    for path in (str(sessions.DB), str(commitments.db.DB_PATH)):
        with closing(sqlite3.connect(path)) as con:
            for (name,) in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'"):
                rows[(path, name)] = con.execute(f"SELECT * FROM {name}").fetchall()
    return rows


def test_property_uses_accepted_commitments_writes_nothing_and_keeps_the_real_streak(calls):
    pid = home(window_panes=1)
    ok(client.post("/commitments", json={"user_id": "u1", "property_id": pid, "catalog_id": "window_upgrade"}, headers=AGENT))
    ok(client.post("/habits/u1/checkin", json={"source": "web"}, headers=AGENT))
    before = tables()
    r = ok(ff(property_id=pid, days=30))
    assert tables() == before  # no check-ins, bills, impact, snapshots, projections or board rows
    assert r["modeled"] == ["window_upgrade"] and 0 < r["totals"]["usd_saved"] < 80
    assert (r["real_habit_streak"], r["simulated_habit_streak"], r["days"][0]["habit_day"]) == (1, 31, 2)
    assert ok(client.get("/habits/u1", headers=AGENT))["current"] == 1


def test_auth_and_input_errors(calls):
    pid = home(window_panes=1)
    assert client.post("/simulate/fast-forward", json={"property_id": pid, "days": 7}).status_code == 401
    assert client.post("/simulate/fast-forward", json={"session_id": f"s-{pid}", "days": 7}).status_code == 200  # anonymous
    for body, code in [({"session_id": f"s-{pid}", "days": 0}, "bad_days"), ({"session_id": f"s-{pid}", "days": 366}, "bad_days"),
                       ({"days": 7}, "missing_input"), ({"session_id": f"s-{pid}", "days": 7, "catalog_ids": ["nope"]}, "unknown_action"),
                       ({"session_id": "missing", "days": 7}, "not_found"), ({"property_id": "missing", "days": 7}, "property_not_found")]:
        r = ff(**body)
        assert r.status_code in (404, 422) and r.json()["detail"]["code"] == code, (body, r.text)

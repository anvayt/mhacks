"""Daily habit streak (api/app/habits.py): local-day boundary, idempotency, breaks, late replies, auth, /me."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app import accounts, db, habits, sessions
from app.main import app
from tests.test_accounts import fake_estimate

client = TestClient(app)
AGENT = {"X-Agent-Key": "test-agent-key"}


@pytest.fixture
def renter(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "app.sqlite")
    monkeypatch.setattr(sessions, "DB", str(tmp_path / "sessions.sqlite"))
    monkeypatch.setenv("AGENT_API_KEY", "test-agent-key")
    monkeypatch.setattr(accounts, "estimate", fake_estimate)
    monkeypatch.setattr(accounts, "_building_id", lambda body: 4242)
    clock = [datetime.fromisoformat("2026-10-04T12:00:00-04:00")]
    monkeypatch.setattr(habits, "_now", lambda: clock[0])
    uid = client.post("/auth/phone", json={"phone": "+17345550100"}, headers=AGENT).json()["user_id"]
    pid = client.post("/properties", json={"user_id": uid, "address": "1514 Morton Ave"}, headers=AGENT).json()["property_id"]
    return {"uid": uid, "pid": pid, "clock": clock}


def at(r, when):
    r["clock"][0] = datetime.fromisoformat(when)


def commit(r, catalog_id="thermostat_setback"):
    res = client.post("/commitments", json={"user_id": r["uid"], "property_id": r["pid"], "catalog_id": catalog_id},
                      headers=AGENT)
    assert res.status_code == 200, res.text
    return res.json()["id"]


def checkin(r, **body):
    return client.post(f"/habits/{r['uid']}/checkin", json={"source": "imessage", **body}, headers=AGENT)


def ok(res):
    assert res.status_code == 200, res.text
    return res.json()


def test_no_habits_until_an_accepted_commitment_and_never_a_dismissed_one(renter):
    res = checkin(renter)
    assert res.status_code == 422 and res.json()["detail"] == {"code": "no_habits",
                                                               "message": "Pick a daily habit first: text 'options'"}
    cid = commit(renter)
    ok(client.patch(f"/commitments/{cid}", json={"status": "dismissed"}, headers=AGENT))
    assert checkin(renter).json()["detail"]["code"] == "no_habits"
    cid = commit(renter, "air_sealing")
    assert ok(checkin(renter, commitment_id=cid))["current"] == 1
    assert checkin(renter, commitment_id="cmt_not_mine").json()["detail"]["code"] == "unknown_commitment"


def test_idempotent_per_local_day(renter):
    commit(renter)
    first, again = ok(checkin(renter)), ok(checkin(renter, source="web"))
    assert first == again == {"current": 1, "best": 1, "checked_in_today": True, "last_checkin_date": "2026-10-04",
                              "badges": []}
    assert [c["source"] for c in ok(client.get(f"/habits/{renter['uid']}", headers=AGENT))["checkins"]] == ["imessage"]


def test_day_boundary_is_america_detroit_not_utc(renter):
    commit(renter)
    at(renter, "2026-10-05T03:30:00+00:00")  # 11:30 PM Oct 4 in Ann Arbor, already Oct 5 in UTC
    assert ok(checkin(renter))["last_checkin_date"] == "2026-10-04"
    at(renter, "2026-10-05T04:30:00+00:00")  # 12:30 AM Oct 5 local: today pending, yesterday still counts
    assert ok(client.get(f"/habits/{renter['uid']}", headers=AGENT))["current"] == 1
    ok(client.patch(f"/me/{renter['uid']}", json={"timezone": "UTC"}, headers=AGENT))
    assert ok(checkin(renter))["last_checkin_date"] == "2026-10-05"  # the account's own timezone decides


def test_streak_grows_today_pending_keeps_it_and_a_missed_day_breaks_it(renter):
    commit(renter)
    for day in ("2026-10-01", "2026-10-02", "2026-10-03"):
        at(renter, f"{day}T20:00:00-04:00")
        last = ok(checkin(renter))
    assert (last["current"], last["best"], last["badges"]) == (3, 3, ["habit-3"])
    at(renter, "2026-10-04T09:00:00-04:00")  # today not done yet: still 3
    pending = ok(client.get(f"/habits/{renter['uid']}", headers=AGENT))
    assert (pending["current"], pending["checked_in_today"]) == (3, False)
    at(renter, "2026-10-05T09:00:00-04:00")  # Oct 4 missed
    broken = ok(client.get(f"/habits/{renter['uid']}", headers=AGENT))
    assert (broken["current"], broken["best"], broken["badges"]) == (0, 3, ["habit-3"])
    assert (ok(checkin(renter))["current"], ok(checkin(renter))["best"]) == (1, 3)


def test_late_reply_after_midnight_counts_yesterday_only(renter):
    commit(renter)
    at(renter, "2026-10-05T00:20:00-04:00")
    assert checkin(renter, date="2026-10-03").json()["detail"]["code"] == "bad_date"
    assert checkin(renter, date="2026-10-06").json()["detail"]["code"] == "bad_date"
    late = ok(checkin(renter, date="2026-10-04"))
    assert (late["current"], late["checked_in_today"], late["last_checkin_date"]) == (1, False, "2026-10-04")
    assert ok(checkin(renter))["current"] == 2  # then today too: yesterday + today


def test_auth_agent_or_own_bearer_only(renter, monkeypatch):
    commit(renter)
    other = client.post("/auth/phone", json={"phone": "+17345550199"}, headers=AGENT).json()["user_id"]
    with db.connect() as con:
        con.execute("INSERT INTO web_tokens VALUES (?, ?, '2099-01-01T00:00:00+00:00')", (accounts._sha256("tok"), other))
    url = f"/habits/{renter['uid']}"
    assert client.post(url + "/checkin", json={"source": "web"}).status_code == 401
    assert client.get(url).status_code == 401
    assert client.post(url + "/checkin", json={"source": "web"}, headers={"Authorization": "Bearer tok"}).status_code == 403
    assert client.get(f"/habits/{other}", headers={"Authorization": "Bearer tok"}).status_code == 200
    assert client.get("/habits/u_missing", headers=AGENT).status_code == 404


def test_me_and_history_last_30_days(renter):
    commit(renter)
    assert ok(client.get(f"/me/{renter['uid']}", headers=AGENT))["habit_streak"] == {"current": 0, "best": 0,
                                                                                     "checked_in_today": False}
    with habits._con() as con:  # an old check-in outside the 30-day window
        con.execute("INSERT INTO habit_checkins VALUES (?, '2026-08-01', NULL, 'web', 'x')", (renter["uid"],))
    ok(checkin(renter))
    assert ok(client.get(f"/me/{renter['uid']}", headers=AGENT))["habit_streak"] == {"current": 1, "best": 1,
                                                                                     "checked_in_today": True}
    assert ok(client.get(f"/habits/{renter['uid']}", headers=AGENT))["checkins"] == [
        {"date": "2026-10-04", "commitment_id": None, "source": "imessage"}]
    history = ok(client.get(f"/properties/{renter['pid']}/history", headers=AGENT))
    assert set(history) == {"property_id", "snapshots", "bills", "impact", "commitments"}  # unchanged

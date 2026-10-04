"""No Photon/model calls: freeze delivery time and provide sourced forecast fixtures."""

import copy
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import accounts, commitments, db, reminders
from app.main import app

KEY = {"X-Agent-Key": "test-agent-key"}


@pytest.fixture
def env(monkeypatch, tmp_path):
    monkeypatch.setenv("AGENT_API_KEY", "test-agent-key")
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "app.sqlite")
    clock = [datetime.fromisoformat("2026-10-04T18:00:00-04:00")]
    monkeypatch.setattr(reminders, "_now", lambda: clock[0])
    users = {"u1": {"id": "u1", "phone_number": "+15550001111", "timezone": "America/Detroit",
                     "reminder_prefs": {"channel": "imessage", "cadence": "monthly", "hour_local": 18, "paused": False}}}
    homes = {"u1": {"id": "p1", "user_id": "u1", "address": "1514 Morton Ave", "active": True, "session_id": "s1"}}
    tasks = [{"id": "c1", "user_id": "u1", "property_id": "p1", "catalog_id": "air_sealing", "status": "accepted",
              "target_date": "2026-10-10", "reminder_channel": "imessage"}]
    weather = {"session_id": "s1", "alerts": [], "week": {"total_usd": 15, "normal_total_usd": 10}}
    calls = []
    def authorize(request, user_id):
        if request.headers.get("X-Agent-Key") == "test-agent-key":
            return
        if request.headers.get("Authorization") == "Bearer " + user_id:
            return
        raise HTTPException(403, {"code": "forbidden", "message": "Not your account."})
    def prefs(user_id, value):
        users[user_id]["reminder_prefs"].update(value)
        return copy.deepcopy(users[user_id]["reminder_prefs"])
    def forecast(session_id):
        calls.append(session_id)
        return copy.deepcopy(weather)
    monkeypatch.setattr(accounts, "authorize", authorize)
    monkeypatch.setattr(accounts, "get_user", users.get)
    monkeypatch.setattr(accounts, "list_users", lambda: list(users.values()))
    monkeypatch.setattr(accounts, "current_property", homes.get)
    monkeypatch.setattr(accounts, "update_reminder_prefs", prefs)
    monkeypatch.setattr(commitments, "list_commitments", lambda **kwargs: copy.deepcopy(tasks))
    monkeypatch.setattr(commitments, "CATALOG", {"air_sealing": {"title": "Seal drafts"}})
    monkeypatch.setattr(reminders.forecast, "forecast", forecast)
    return {"client": TestClient(app), "clock": clock, "users": users, "homes": homes, "tasks": tasks, "weather": weather, "calls": calls}


def due(env, **kwargs):
    response = env["client"].get("/reminders/due", headers=KEY, **kwargs)
    assert response.status_code == 200, response.text
    return response.json()


def ack(env, row):
    response = env["client"].post("/reminders/" + row["reminder_id"] + "/sent", headers=KEY)
    assert response.status_code == 200, response.text
    return response.json()


def inbound(env):
    return env["client"].post("/reminders/inbound", headers=KEY, json={"user_id": "u1"})


def send_checkin(env):
    row = due(env)[0]
    assert row["kind"] == "checkin"
    ack(env, row)
    assert inbound(env).status_code == 200
    return row


def advance(env, days=1):
    env["clock"][0] += timedelta(days=days)


def test_queue_persists_and_ack_is_idempotent(env):
    first = due(env)
    assert first == due(env) and len(first) == 1
    assert first[0]["text_hint"] == "Still at 1514 Morton Ave?"
    assert first[0]["handle"] == "+15550001111"
    second_client = TestClient(app)
    assert second_client.get("/reminders/due", headers=KEY).json() == first
    assert ack(env, first[0])["unanswered"] == 1
    assert ack(env, first[0])["unanswered"] == 1
    assert due(env) == []


@pytest.mark.parametrize("path,method,body", [
    ("/reminders/due", "get", None),
    ("/reminders/inbound", "post", {"user_id": "u1"}),
    ("/reminders/demo-send", "post", {"user_id": "u1"}),
    ("/reminders/fake/sent", "post", None),
])
def test_global_and_handle_endpoints_require_configured_agent_key(env, monkeypatch, path, method, body):
    kwargs = {"json": body} if body else {}
    result = getattr(env["client"], method)(path, headers={"Authorization": "Bearer u1"}, **kwargs)
    assert result.status_code == 401 and "+1555" not in result.text
    monkeypatch.delenv("AGENT_API_KEY")
    result = getattr(env["client"], method)(path, headers=KEY, **kwargs)
    assert result.status_code == 401 and "+1555" not in result.text


def test_daily_cap_all_kinds_and_demo_only_bypass(env):
    env["users"]["u1"]["reminder_prefs"]["cadence"] = "daily"
    row = send_checkin(env)
    assert due(env) == []  # Task is available, but check-in used this local day.
    demo = env["client"].post("/reminders/demo-send", headers=KEY, json={"user_id": "u1", "kind": "task"})
    assert demo.status_code == 200 and demo.json()["kind"] == "task" and demo.json()["demo"] is True
    assert demo.json()["reminder_id"] != row["reminder_id"]
    advance(env)
    assert due(env)[0]["kind"] == "task"


@pytest.mark.parametrize("zone,time,chosen,allowed", [
    ("America/Detroit", "2026-10-05T01:30:00Z", 21, True),
    ("America/Detroit", "2026-10-05T02:00:00Z", 22, False),
    ("America/Detroit", "2026-10-04T11:59:00Z", 7, False),
    ("America/Detroit", "2026-10-04T12:00:00Z", 8, True),
    ("America/Los_Angeles", "2026-10-05T01:00:00Z", 18, True),
    ("America/Los_Angeles", "2026-10-05T01:00:00Z", 17, False),
    ("Invalid/Zone", "2026-10-04T22:00:00Z", 18, False),
])
def test_quiet_hours_respect_timezone_and_selected_hour(env, zone, time, chosen, allowed):
    env["users"]["u1"]["timezone"] = zone
    env["users"]["u1"]["reminder_prefs"]["hour_local"] = chosen
    env["clock"][0] = datetime.fromisoformat(time.replace("Z", "+00:00"))
    assert bool(due(env)) is allowed


def test_daily_cap_uses_local_date_not_utc(env):
    user = env["users"]["u1"]
    user["timezone"] = "America/Los_Angeles"
    user["reminder_prefs"].update(cadence="daily", hour_local=16)
    env["clock"][0] = datetime.fromisoformat("2026-10-04T23:30:00+00:00")
    send_checkin(env)
    user["reminder_prefs"]["hour_local"] = 18
    env["clock"][0] = datetime.fromisoformat("2026-10-05T01:30:00+00:00")
    assert due(env) == []  # Still Oct 4 locally despite UTC midnight.
    advance(env)
    assert due(env)[0]["kind"] == "task"


def test_two_unanswered_auto_pause_and_inbound_reset(env):
    env["users"]["u1"]["reminder_prefs"]["cadence"] = "daily"
    ack(env, due(env)[0])
    advance(env)
    result = ack(env, due(env)[0])
    assert result["unanswered"] == 2 and result["paused"] is True
    advance(env)
    assert due(env) == []
    assert inbound(env).json()["unanswered"] == 0
    assert due(env)[0]["kind"] == "task"


def test_monthly_checkin_one_followup_then_pause(env):
    ack(env, due(env)[0])
    advance(env, 2)
    assert due(env) == []
    advance(env)
    row = due(env)[0]
    assert row["kind"] == "checkin"
    assert ack(env, row)["paused"] is True
    env["clock"][0] = datetime.fromisoformat("2026-11-07T18:00:00-05:00")
    assert due(env) == []
    inbound(env)
    assert due(env)[0]["kind"] == "checkin"


def test_answered_monthly_checkin_waits_until_next_month(env):
    send_checkin(env)
    advance(env, 10)
    assert due(env) == []
    env["clock"][0] = datetime.fromisoformat("2026-11-01T18:00:00-05:00")
    assert due(env)[0]["kind"] == "checkin"


@pytest.mark.parametrize("action", ["pause", "stop"])
def test_explicit_controls_survive_inbound_until_resume(env, action):
    old = due(env)[0]
    headers = {"Authorization": "Bearer u1"}
    result = env["client"].post(f"/reminders/u1/{action}", headers=headers)
    assert result.status_code == 200 and "+1555" not in result.text
    assert due(env) == []
    assert inbound(env).status_code == 200
    assert due(env) == []
    assert env["client"].post("/reminders/demo-send", headers=KEY, json={"user_id": "u1"}).status_code == 422
    result = env["client"].post("/reminders/u1/resume", headers=headers)
    assert result.status_code == 200 and not result.json()["stopped"] and not result.json()["paused"]
    new = due(env)[0]
    assert new["reminder_id"] != old["reminder_id"]
    assert env["client"].post("/reminders/u1/stop", headers={"Authorization": "Bearer other"}).status_code == 403


@pytest.mark.parametrize("cadence,days", [("daily", 1), ("weekly", 7)])
def test_task_cadence_and_target_requirement(env, cadence, days):
    user = env["users"]["u1"]
    user["reminder_prefs"]["cadence"] = cadence
    send_checkin(env)
    advance(env)
    row = due(env)[0]
    assert row["kind"] == "task" and row["commitment_id"] == "c1"
    assert row["text_hint"] == ("Your target for Seal drafts is 2026-10-10. "
                                "Reply done once you've done it today to start a habit streak.")  # app/habits.py
    ack(env, row)
    inbound(env)
    if days > 1:
        advance(env, days - 1)
        assert due(env) == []
        advance(env)
    else:
        advance(env)
    assert due(env)[0]["kind"] == "task"
    env["tasks"][0]["status"] = "completed"
    assert due(env) == []


@pytest.mark.parametrize("patch", [{"target_date": None}, {"target_date": "invalid"}, {"status": "suggested"}, {"reminder_channel": "calendar"}, {"user_id": "other"}, {"property_id": "other"}])
def test_ineligible_tasks_never_queue(env, patch):
    env["users"]["u1"]["reminder_prefs"]["cadence"] = "daily"
    send_checkin(env)
    advance(env)
    env["tasks"][0].update(patch)
    assert due(env) == []


@pytest.mark.parametrize("kind,total,normal,allowed", [
    ("cold_snap", 1, 0, True), ("heat_wave", 1, 0, True),
    ("costly_week", 14.99, 10, False), ("costly_week", 15, 10, True),
    ("costly_week", None, 10, False), ("unknown", 100, 1, False),
])
def test_weather_uses_api_flags_and_cost_floor(env, kind, total, normal, allowed):
    env["users"]["u1"]["reminder_prefs"]["cadence"] = "daily"
    send_checkin(env)
    advance(env)
    env["tasks"].clear()
    env["weather"].update(alerts=[{"type": kind, "date": "2026-10-08", "detail": "Fixture forecast fact: heating and cooling $15."}],
                           week={"total_usd": total, "normal_total_usd": normal})
    rows = due(env)
    assert bool(rows) is allowed
    assert env["calls"] == ["s1"]
    if allowed:
        assert rows[0]["kind"] == "weather" and rows[0]["text_hint"] == env["weather"]["alerts"][0]["detail"]
        ack(env, rows[0])
        inbound(env)
        advance(env)
        assert due(env) == []  # The same alert/date is not repeated.


def test_forecast_failure_isolated_and_monthly_does_not_call_it(env, monkeypatch):
    send_checkin(env)
    advance(env)
    assert due(env) == [] and env["calls"] == []
    env["users"]["u1"]["reminder_prefs"]["cadence"] = "daily"
    env["tasks"].clear()
    def fail(session_id):
        raise HTTPException(503, {"code": "forecast_unavailable", "message": "Try later."})
    monkeypatch.setattr(reminders.forecast, "forecast", fail)
    assert due(env) == []


def test_demo_bypasses_clock_not_stop_or_sends_itself(env):
    env["clock"][0] = datetime.fromisoformat("2026-10-04T03:00:00-04:00")
    assert due(env) == []
    result = env["client"].post("/reminders/demo-send", headers=KEY, json={"user_id": "u1"})
    assert result.status_code == 200 and result.json()["demo"] is True
    with reminders._con() as con:
        row = con.execute("SELECT status,sent_at FROM reminder_queue").fetchone()
        assert row["status"] == "queued" and row["sent_at"] is None
    env["client"].post("/reminders/u1/stop", headers=KEY)
    assert env["client"].post("/reminders/demo-send", headers=KEY, json={"user_id": "u1"}).status_code == 422


@pytest.mark.parametrize("prefs", [{"channel": "none"}, {"channel": "calendar"}, {"cadence": "off"}, {"paused": True}])
def test_opt_outs(env, prefs):
    env["users"]["u1"]["reminder_prefs"].update(prefs)
    assert due(env) == []


def test_bad_now_and_demo_kind(env):
    assert env["client"].get("/reminders/due", headers=KEY, params={"now": "2026-10-04T18:00:00"}).status_code == 422
    assert env["client"].post("/reminders/demo-send", headers=KEY, json={"user_id": "u1", "kind": "invented"}).status_code == 422


def test_late_ack_does_not_undo_stop(env):
    row = due(env)[0]
    env["client"].post("/reminders/u1/stop", headers=KEY)
    assert ack(env, row)["stopped"] is True
    assert due(env) == []


def test_inflight_forecast_rechecks_stop_and_current_clock(env, monkeypatch):
    env["users"]["u1"]["reminder_prefs"].update(cadence="daily", hour_local=21)
    env["clock"][0] = datetime.fromisoformat("2026-10-04T21:00:00-04:00")
    send_checkin(env)
    advance(env)
    env["tasks"].clear()
    def forecast(session_id):
        env["clock"][0] += timedelta(hours=1)
        return {"alerts": [{"type": "cold_snap", "date": "2026-10-08", "detail": "Cold forecast."}]}
    monkeypatch.setattr(reminders.forecast, "forecast", forecast)
    assert due(env) == []  # Forecast finished at22:00; never queue from stale21:00 eligibility.


def test_stop_during_forecast_cancels_candidate(env, monkeypatch):
    env["users"]["u1"]["reminder_prefs"]["cadence"] = "daily"
    send_checkin(env)
    advance(env)
    env["tasks"].clear()
    def forecast(session_id):
        assert env["client"].post("/reminders/u1/stop", headers=KEY).status_code == 200
        return {"alerts": [{"type": "cold_snap", "date": "2026-10-08", "detail": "Cold forecast."}]}
    monkeypatch.setattr(reminders.forecast, "forecast", forecast)
    assert due(env) == []


def test_parallel_polls_share_one_queue_id(env):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: due(env), range(4)))
    assert all(result == results[0] for result in results)
    with reminders._con() as con:
        assert con.execute("SELECT COUNT(*) FROM reminder_queue").fetchone()[0] == 1


def test_prefs_write_failure_cannot_undo_stop(env, monkeypatch):
    def fail(user_id, prefs):
        raise HTTPException(503, {"code": "temporarily_unavailable", "message": "Try again."})
    monkeypatch.setattr(accounts, "update_reminder_prefs", fail)
    assert env["client"].post("/reminders/u1/stop", headers=KEY).status_code == 503
    assert due(env) == []
    assert inbound(env).json()["stopped"] is True
    assert due(env) == []


def test_move_committed_before_queue_lock_rejects_old_home(env, monkeypatch):
    # list_users/current_property saw the old property, but the locked fresh-user
    # read observes a move committed immediately before BEGIN IMMEDIATE.
    monkeypatch.setattr(accounts, "get_user", lambda uid: {**env["users"][uid], "current_property_id": "new-home"})
    assert due(env) == []
    with reminders._con() as con:
        assert con.execute("SELECT COUNT(*) FROM reminder_queue").fetchone()[0] == 0


def test_task_hint_carries_habit_streak_facts(env, monkeypatch):
    from app import habits
    monkeypatch.setattr(habits, "_now", lambda: env["clock"][0])
    with habits._con() as con:
        con.executemany("INSERT INTO habit_checkins VALUES ('u1', ?, NULL, 'imessage', 'x')",
                        [("2026-10-01",), ("2026-10-02",), ("2026-10-03",)])
    hint = env["client"].post("/reminders/demo-send", headers=KEY, json={"user_id": "u1", "kind": "task"}).json()["text_hint"]
    assert hint == "Your target for Seal drafts is 2026-10-10. Habit streak 3 days; reply done to keep it."
    with habits._con() as con:
        con.execute("INSERT INTO habit_checkins VALUES ('u1', '2026-10-04', NULL, 'imessage', 'x')")
    assert habits.reminder_hint(env["users"]["u1"]) == "Habit streak 4 days; today already counts."


def test_inbound_says_which_reminder_it_answers_once(env):
    """The agent words a bare "done" as a habit check-in only when it answers a task reminder (agent conversation.ts)."""
    env["users"]["u1"]["reminder_prefs"]["cadence"] = "daily"
    assert inbound(env).json()["replying_to"] is None
    env["clock"][0] += timedelta(minutes=1)
    shown = env["client"].post("/reminders/demo-send", headers=KEY, json={"user_id": "u1", "kind": "task"}).json()
    advance(env, 0.25)  # 18:01 + 6 h = 00:01 local: a late reply counts for the reminder's own day
    first = inbound(env).json()["replying_to"]
    assert first == {"reminder_id": shown["reminder_id"], "kind": "task", "local_date": "2026-10-04", "commitment_id": "c1"}
    assert inbound(env).json()["replying_to"] is None  # answered: the next text isn't a reply to it
    advance(env, 0.75)
    row = due(env)[0]
    ack(env, row)
    advance(env, 2)  # an unanswered reminder from two days ago is no longer "the" reminder
    assert inbound(env).json()["replying_to"] is None

"""Calendar runs against mocked Google REST; no real events or tokens are used."""

import copy
import logging
import stat
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import accounts, commitments, db, gcal
from app.main import app


@pytest.fixture
def calendar(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "app.sqlite")
    for name in ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REDIRECT_URI", "WEB_ORIGIN"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CALENDAR_STATE_SECRET", "x" * 40)
    users = {key: {"id": key, "phone_number": "+15551234567", "timezone": "America/Detroit",
                   "reminder_prefs": {"hour_local": 10}} for key in ("user-a", "user-b")}
    records = [{"id": "commit-1", "user_id": "user-a", "property_id": "private-property",
                "catalog_id": "air_sealing", "status": "accepted", "title": "Private street address",
                "target_date": "2026-11-01"}]
    def authorize(request, user_id):
        token = request.headers.get("Authorization", "")
        if not token:
            raise HTTPException(401, {"code": "unauthorized", "message": "Sign in."})
        if token != "Bearer " + user_id:
            raise HTTPException(403, {"code": "forbidden", "message": "Not your account."})
    monkeypatch.setattr(accounts, "get_user", users.get)
    monkeypatch.setattr(accounts, "authorize", authorize)
    monkeypatch.setattr(commitments, "CATALOG", {"air_sealing": {"title": "Seal drafts"}})
    monkeypatch.setattr(commitments, "list_commitments", lambda **kwargs: records)
    return TestClient(app), records, users


def connect(client, user="user-a"):
    response = client.post("/calendar/connect", json={"user_id": user}, headers={"Authorization": "Bearer " + user})
    assert response.status_code == 200, response.text
    value = response.json()
    return value, parse_qs(urlparse(value["auth_url"]).query)["state"][0]


def finish(client, state, **params):
    return client.get("/calendar/callback", params={"state": state, **params}, follow_redirects=False)


def create(client, **fields):
    body = {"user_id": "user-a", "commitment_id": "commit-1", "start": "2026-11-01T09:00:00-05:00", **fields}
    return client.post("/calendar/reminders", json=body, headers={"Authorization": "Bearer user-a"})


def real_mode(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-client-secret")


def google_response(url, body=None, status=200):
    return httpx.Response(status, json=body, request=httpx.Request("POST", url)) if body is not None else httpx.Response(status, request=httpx.Request("POST", url))


def mock_google(monkeypatch, handler):
    monkeypatch.setattr(gcal.httpx, "request", handler)


def token_handler(method, url, **kwargs):
    return google_response(url, {"refresh_token": "private-refresh", "access_token": "private-access", "scope": gcal.SCOPE})


def real_connect(client, monkeypatch):
    real_mode(monkeypatch)
    mock_google(monkeypatch, token_handler)
    _, state = connect(client)
    assert finish(client, state, code="private-code").status_code == 303


def test_mock_lifecycle_and_owner_only_storage(calendar, monkeypatch):
    client, records, _ = calendar
    original = copy.deepcopy(records)
    mock_google(monkeypatch, lambda *args, **kwargs: pytest.fail("Mock mode must not call Google"))
    value, state = connect(client)
    assert value["mock"] is True and "Demo" in value["message"]
    result = finish(client, state)
    assert result.status_code == 303
    assert result.headers["location"] == "http://localhost:3000?calendar=connected&calendar_mock=1"
    assert gcal.is_connected("user-a") and not gcal.is_connected("user-b")
    result = create(client, cadence="weekly")
    assert result.status_code == 200
    reminder = result.json()
    assert reminder["mock"] is True and reminder["html_link"] is None
    assert reminder["event_id"].startswith("mock_") and "Demo" in reminder["message"]
    assert stat.S_IMODE(db.DB_PATH.stat().st_mode) == 0o600
    for _ in range(2):
        result = client.delete("/calendar/reminders/" + reminder["reminder_id"], headers={"Authorization": "Bearer user-a"})
        assert result.status_code == 200 and result.json()["deleted"] is True
    assert records == original


def test_real_auth_contract_and_refresh_storage(calendar, monkeypatch):
    client, _, _ = calendar
    real_mode(monkeypatch)
    monkeypatch.setenv("WEB_ORIGIN", "https://hidden-rent.example")
    calls = []
    def handler(method, url, **kwargs):
        calls.append((method, url, kwargs))
        return token_handler(method, url, **kwargs)
    mock_google(monkeypatch, handler)
    value, state = connect(client)
    query = parse_qs(urlparse(value["auth_url"]).query)
    assert value["mock"] is False
    assert query["scope"] == [gcal.SCOPE] and query["access_type"] == ["offline"] and query["prompt"] == ["consent"]
    assert query["response_type"] == ["code"]
    assert query["redirect_uri"] == ["http://localhost:8000/calendar/callback"]
    assert "secret" not in value["auth_url"]
    result = finish(client, state, code="private-code")
    assert result.status_code == 303 and result.headers["location"] == "https://hidden-rent.example?calendar=connected"
    assert result.headers["cache-control"] == "no-store" and result.headers["referrer-policy"] == "no-referrer"
    assert calls[0][0:2] == ("POST", gcal.TOKEN_URL)
    assert calls[0][2]["data"] == {"client_id": "test-client-id", "client_secret": "test-client-secret",
        "redirect_uri": "http://localhost:8000/calendar/callback", "grant_type": "authorization_code", "code": "private-code"}
    assert gcal._saved_connection("user-a")["refresh_token"] == "private-refresh"
    assert "private-refresh" not in result.text


@pytest.mark.parametrize("fault", ["tamper", "expired", "replay", "mode"])
def test_state_rejects_invalid_links(calendar, monkeypatch, fault):
    client, _, _ = calendar
    _, state = connect(client)
    if fault == "tamper":
        state = "Z" + state[1:]
    elif fault == "expired":
        now = gcal.time.time()
        monkeypatch.setattr(gcal.time, "time", lambda: now + 601)
    elif fault == "replay":
        assert finish(client, state).status_code == 303
    else:
        real_mode(monkeypatch)
    result = finish(client, state, code="irrelevant")
    assert result.status_code == 400 and result.json()["detail"]["code"] == "invalid_calendar_state"


def test_state_binds_its_user(calendar):
    client, _, _ = calendar
    _, state = connect(client)
    assert finish(client, state, user_id="user-b").status_code == 303
    assert gcal.is_connected("user-a") and not gcal.is_connected("user-b")


def test_all_mutations_authorize_owner(calendar):
    client, _, _ = calendar
    assert client.post("/calendar/connect", json={"user_id": "user-a"}).status_code == 401
    assert client.post("/calendar/connect", json={"user_id": "user-a"}, headers={"Authorization": "Bearer user-b"}).status_code == 403
    assert client.post("/calendar/reminders", json={"user_id": "user-a", "commitment_id": "commit-1"}).status_code == 401
    _, state = connect(client)
    finish(client, state)
    reminder = create(client).json()["reminder_id"]
    assert client.delete("/calendar/reminders/" + reminder).status_code == 401
    assert client.delete("/calendar/reminders/" + reminder, headers={"Authorization": "Bearer user-b"}).status_code == 403
    with gcal._connection() as con:
        assert con.execute("SELECT deleted FROM gcal_reminders WHERE id=?", (reminder,)).fetchone()[0] == 0


@pytest.mark.parametrize("cadence", ["daily", "weekly", "once"])
def test_event_recurrence_and_google_delete(calendar, monkeypatch, cadence):
    client, records, _ = calendar
    original = copy.deepcopy(records)
    real_connect(client, monkeypatch)
    calls = []
    def handler(method, url, **kwargs):
        calls.append((method, url, kwargs))
        if url == gcal.TOKEN_URL:
            assert kwargs["data"]["refresh_token"] == "private-refresh"
            assert kwargs["data"]["grant_type"] == "refresh_token"
            return google_response(url, {"access_token": "access"})
        if method == "DELETE":
            return google_response(url, status=204)
        return google_response(url, {"id": "google-event", "htmlLink": "https://calendar.google.com/event?eid=demo"})
    mock_google(monkeypatch, handler)
    result = create(client, cadence=cadence)
    assert result.status_code == 200 and result.json()["mock"] is False
    method, url, request = calls[1]
    assert (method, url) == ("POST", gcal.EVENTS_URL)
    assert request["headers"] == {"Authorization": "Bearer access"} and request["params"] == {"sendUpdates": "none"}
    event = request["json"]
    assert event["summary"] == "Hidden Rent: Seal drafts"
    assert event["reminders"] == {"useDefault": False, "overrides": [{"method": "popup", "minutes": 10}]}
    assert event["visibility"] == "private" and event["start"]["timeZone"] == "America/Detroit"
    assert "Private" not in str(event) and "+1555" not in str(event) and "private-property" not in str(event)
    if cadence == "once":
        assert "recurrence" not in event
    else:
        assert event["recurrence"] == ["RRULE:FREQ=" + cadence.upper()]
    deleted = client.delete("/calendar/reminders/" + result.json()["reminder_id"], headers={"Authorization": "Bearer user-a"})
    assert deleted.status_code == 200
    assert calls[-1][0:2] == ("DELETE", gcal.EVENTS_URL + "/google-event")
    assert records == original


@pytest.mark.parametrize("phase", ["exchange", "refresh", "insert", "delete", "malformed", "transport"])
def test_google_failures_are_isolated(calendar, monkeypatch, phase):
    client, records, _ = calendar
    original = copy.deepcopy(records)
    real_mode(monkeypatch)
    if phase != "exchange":
        real_connect(client, monkeypatch)
    reminder = None
    if phase == "delete":
        mock_google(monkeypatch, lambda method, url, **kwargs: google_response(url, {"access_token": "access"} if url == gcal.TOKEN_URL else {"id": "event"}))
        reminder = create(client).json()["reminder_id"]
    def handler(method, url, **kwargs):
        if phase in {"insert", "delete", "malformed"} and url == gcal.TOKEN_URL:
            return google_response(url, {"access_token": "access"})
        if phase == "transport":
            raise httpx.ConnectError("SECRET failure")
        return google_response(url, [] if phase == "malformed" else {"error": "SECRET failure"}, status=200 if phase == "malformed" else 500)
    mock_google(monkeypatch, handler)
    if phase == "exchange":
        _, state = connect(client)
        result = finish(client, state, code="code")
    elif phase == "delete":
        result = client.delete("/calendar/reminders/" + reminder, headers={"Authorization": "Bearer user-a"})
    else:
        result = create(client)
    assert result.status_code == 503 and result.json()["detail"]["code"] == "calendar_unavailable"
    assert "SECRET" not in result.text and records == original
    with gcal._connection() as con:
        if reminder:
            assert con.execute("SELECT deleted FROM gcal_reminders WHERE id=?", (reminder,)).fetchone()[0] == 0
        else:
            assert con.execute("SELECT count(*) FROM gcal_reminders").fetchone()[0] == 0


def test_invalid_and_foreign_commitments(calendar):
    client, records, _ = calendar
    assert create(client).json()["detail"]["code"] == "calendar_not_connected"
    assert create(client, cadence="monthly").status_code == 422
    assert create(client, start="not a date").status_code == 422
    records[0]["status"] = "suggested"
    assert create(client).json()["detail"]["code"] == "commitment_not_accepted"
    records[0]["status"], records[0]["user_id"] = "accepted", "user-b"
    assert create(client).status_code == 404


def test_date_only_target_and_reconnect_retains_token(calendar, monkeypatch):
    client, records, users = calendar
    event = gcal._event(gcal.ReminderRequest(user_id="user-a", commitment_id="commit-1"), users["user-a"], records[0])
    assert event["start"]["dateTime"] == "2026-11-01T10:00:00-05:00"
    real_connect(client, monkeypatch)
    mock_google(monkeypatch, lambda method, url, **kwargs: google_response(url, {"access_token": "access"}))
    _, state = connect(client)
    assert finish(client, state, code="code").status_code == 303
    assert gcal._saved_connection("user-a")["refresh_token"] == "private-refresh"


@pytest.mark.parametrize("token", [{"access_token": "access"}, {"refresh_token": "refresh", "scope": "wrong"}, {"refresh_token": "refresh", "scope": []}])
def test_initial_token_requires_refresh_and_requested_scope(calendar, monkeypatch, token):
    client, _, _ = calendar
    real_mode(monkeypatch)
    mock_google(monkeypatch, lambda method, url, **kwargs: google_response(url, token))
    _, state = connect(client)
    assert finish(client, state, code="code").status_code == 503
    assert not gcal.is_connected("user-a")


def test_denied_consent_leaves_commitment(calendar):
    client, records, _ = calendar
    original = copy.deepcopy(records)
    _, state = connect(client)
    result = finish(client, state, error="access_denied")
    assert result.status_code == 422 and result.json()["detail"]["code"] == "calendar_denied"
    assert not gcal.is_connected("user-a") and records == original


def test_partial_config_does_not_break_account_status(calendar, monkeypatch):
    client, _, _ = calendar
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "only-id")
    assert not gcal.is_connected("user-a")
    result = client.post("/calendar/connect", json={"user_id": "user-a"}, headers={"Authorization": "Bearer user-a"})
    assert result.status_code == 503 and result.json()["detail"]["code"] == "calendar_unavailable"


def test_callback_log_filter_hides_authorization_code():
    record = logging.LogRecord("uvicorn.access", logging.INFO, __file__, 1, '%s - "%s %s HTTP/%s" %d',
                              ("127.0.0.1", "GET", "/calendar/callback?code=secret-code&state=secret-state", "1.1", 303), None)
    assert gcal._CallbackLogFilter().filter(record)
    assert "secret" not in record.getMessage() and "/calendar/callback" in record.getMessage()

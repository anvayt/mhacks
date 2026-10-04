"""Optional Google Calendar reminders; Google failures never change commitments.

OAuth web-server flow: https://developers.google.com/identity/protocols/oauth2/web-server
Events: https://developers.google.com/workspace/calendar/api/v3/reference/events/insert
No cryptography package is in api/uv.lock, so refresh tokens live only in APP_DB
(git-ignored by default, chmod 0600), never in responses or logs. Access tokens are
short-lived locals. Missing Google credentials selects explicitly labelled mock mode.
Replace the marked accounts/commitments stubs with their owners' modules at merge.
"""

import base64
import hmac
import json
import logging
import os
import secrets
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from urllib.parse import quote, urlencode
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app import accounts, commitments, db

router = APIRouter()
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
SCOPE = "https://www.googleapis.com/auth/calendar.events"
STATE_TTL = 600  # Short-lived, single-use local CSRF challenge; not a Google token TTL.
_MOCK_SECRET = secrets.token_bytes(32)
UNAVAILABLE = "Google Calendar isn't available right now. Your commitment is still saved; try connecting again later."


class _CallbackLogFilter(logging.Filter):
    """Uvicorn otherwise logs callback query strings containing authorization codes."""
    def filter(self, record):
        if isinstance(record.args, tuple) and len(record.args) >= 3 and str(record.args[2]).split("?", 1)[0] == "/calendar/callback":
            args = list(record.args)
            args[2] = "/calendar/callback"
            record.args = tuple(args)
        return True


logging.getLogger("uvicorn.access").addFilter(_CallbackLogFilter())


def _fail(status: int, code: str, message: str):
    return HTTPException(status, {"code": code, "message": message})


def _config() -> dict:
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    mock = not client_id and not client_secret
    state_secret = os.environ.get("CALENDAR_STATE_SECRET", "")
    if not mock and (not client_id or not client_secret or len(state_secret) < 32):
        raise _fail(503, "calendar_unavailable", UNAVAILABLE)
    return {"client_id": client_id, "client_secret": client_secret, "mock": mock,
            "state_secret": state_secret.encode() if state_secret else _MOCK_SECRET,
            "redirect_uri": os.environ.get("GOOGLE_REDIRECT_URI") or "http://localhost:8000/calendar/callback",
            "web_origin": (os.environ.get("WEB_ORIGIN") or "http://localhost:3000").rstrip("/")}


@contextmanager
def _connection():
    # Create with owner-only mode before any token can be written, including when
    # other modules initialized the shared file first. Only Calendar-owned tables.
    db.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(db.DB_PATH, os.O_CREAT | os.O_RDWR, 0o600)
    os.fchmod(fd, 0o600)
    os.close(fd)
    con = db.connect()
    try:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS gcal_connections (
                user_id TEXT PRIMARY KEY, refresh_token TEXT, mock INTEGER NOT NULL, connected_at INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS gcal_oauth_states (
                nonce TEXT PRIMARY KEY, user_id TEXT NOT NULL, expires INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS gcal_reminders (
                id TEXT PRIMARY KEY, user_id TEXT NOT NULL, commitment_id TEXT NOT NULL,
                event_id TEXT NOT NULL, html_link TEXT, start TEXT NOT NULL, cadence TEXT NOT NULL,
                mock INTEGER NOT NULL, deleted INTEGER NOT NULL DEFAULT 0);
        """)
        with con:
            yield con
    finally:
        con.close()
        for suffix in ("", "-wal", "-shm", "-journal"):
            path = db.DB_PATH.with_name(db.DB_PATH.name + suffix)
            if path.exists():
                path.chmod(0o600)


def _saved_connection(user_id: str):
    with _connection() as con:
        row = con.execute("SELECT * FROM gcal_connections WHERE user_id=?", (user_id,)).fetchone()
        return dict(row) if row else None


def is_connected(user_id: str) -> bool:
    """A saved connection in the current real/mock mode; never makes a Google call."""
    try:
        config = _config()
    except HTTPException:
        return False
    row = _saved_connection(user_id)
    return bool(row and bool(row["mock"]) == config["mock"] and (row["mock"] or row["refresh_token"]))


def _user(request: Request, user_id: str) -> dict:
    accounts.authorize(request, user_id)
    user = accounts.get_user(user_id)
    if user is None:
        raise _fail(404, "not_found", "That account wasn't found. Sign in again to connect your calendar.")
    return user


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _new_state(user_id: str, config: dict) -> str:
    nonce, expires = secrets.token_urlsafe(24), int(time.time()) + STATE_TTL
    body = _b64(json.dumps({"user_id": user_id, "nonce": nonce, "expires": expires, "mock": config["mock"]},
                            separators=(",", ":")).encode())
    signature = _b64(hmac.digest(config["state_secret"], body.encode(), "sha256"))
    with _connection() as con:
        con.execute("DELETE FROM gcal_oauth_states WHERE expires<=?", (int(time.time()),))
        con.execute("INSERT INTO gcal_oauth_states VALUES (?,?,?)", (nonce, user_id, expires))
    return body + "." + signature


def _consume_state(state: str, config: dict) -> str:
    try:
        body, signature = state.split(".")
        expected = _b64(hmac.digest(config["state_secret"], body.encode(), "sha256"))
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        if payload["expires"] <= time.time() or payload["mock"] != config["mock"]:
            raise ValueError
        with _connection() as con:
            deleted = con.execute("DELETE FROM gcal_oauth_states WHERE nonce=? AND user_id=? AND expires=?",
                                  (payload["nonce"], payload["user_id"], payload["expires"])).rowcount
        if deleted != 1:
            raise ValueError
        return payload["user_id"]
    except (ValueError, KeyError, TypeError, UnicodeError):
        raise _fail(400, "invalid_calendar_state", "That Calendar connection link expired or was already used. Connect again.") from None


def _google(method: str, url: str, *, allow_gone: bool = False, **kwargs) -> dict:
    try:
        response = httpx.request(method, url, timeout=20, **kwargs)
        if allow_gone and response.status_code in (404, 410):
            return {}
        response.raise_for_status()
        result = response.json() if response.content else {}
        if not isinstance(result, dict):
            raise ValueError
        return result
    except (httpx.HTTPError, ValueError):
        raise _fail(503, "calendar_unavailable", UNAVAILABLE) from None


def _access_token(user_id: str, config: dict) -> str:
    row = _saved_connection(user_id)
    if not row or bool(row["mock"]) != config["mock"]:
        raise _fail(422, "calendar_not_connected", "Connect Google Calendar before adding a reminder.")
    token = _google("POST", TOKEN_URL, data={"client_id": config["client_id"], "client_secret": config["client_secret"],
                   "refresh_token": row["refresh_token"], "grant_type": "refresh_token"})
    if not isinstance(token.get("access_token"), str) or not token["access_token"]:
        raise _fail(503, "calendar_unavailable", UNAVAILABLE)
    return token["access_token"]


class ConnectRequest(BaseModel):
    user_id: str


class ReminderRequest(BaseModel):
    user_id: str
    commitment_id: str
    start: str | None = None
    cadence: str = "once"


@router.post("/calendar/connect")
def connect_calendar(body: ConnectRequest, request: Request) -> dict:
    _user(request, body.user_id)
    config = _config()
    state = _new_state(body.user_id, config)
    if config["mock"]:
        return {"auth_url": config["redirect_uri"] + "?" + urlencode({"state": state, "mock": "1"}),
                "mock": True, "message": "Demo Calendar connection only; no Google account will be linked."}
    return {"auth_url": AUTH_URL + "?" + urlencode({"client_id": config["client_id"], "redirect_uri": config["redirect_uri"],
             "response_type": "code", "scope": SCOPE, "access_type": "offline", "prompt": "consent", "state": state}),
            "mock": False}


@router.get("/calendar/callback", include_in_schema=False)
def calendar_callback(state: str = "", code: str | None = None, error: str | None = None):
    config = _config()
    user_id = _consume_state(state, config)
    if accounts.get_user(user_id) is None:
        raise _fail(404, "not_found", "That account wasn't found. Sign in again to connect your calendar.")
    if error:
        raise _fail(422, "calendar_denied", "Calendar wasn't connected. Your commitment is still saved.")
    refresh_token = None
    if not config["mock"]:
        if not code:
            raise _fail(422, "missing_input", "Google didn't return a connection code. Connect Calendar again.")
        token = _google("POST", TOKEN_URL, data={"client_id": config["client_id"], "client_secret": config["client_secret"],
                       "redirect_uri": config["redirect_uri"], "grant_type": "authorization_code", "code": code})
        if token.get("scope") is not None and (not isinstance(token["scope"], str) or SCOPE not in token["scope"].split()):
            raise _fail(503, "calendar_unavailable", UNAVAILABLE)
        refresh_token = token.get("refresh_token")
        if not refresh_token:
            old = _saved_connection(user_id)
            refresh_token = old["refresh_token"] if old and not old["mock"] else None
        if not isinstance(refresh_token, str) or not refresh_token:
            raise _fail(503, "calendar_unavailable", UNAVAILABLE)
    with _connection() as con:
        con.execute("INSERT OR REPLACE INTO gcal_connections VALUES (?,?,?,?)",
                    (user_id, refresh_token, int(config["mock"]), int(time.time())))
    query = {"calendar": "connected"}
    if config["mock"]:
        query["calendar_mock"] = "1"
    return RedirectResponse(config["web_origin"] + "?" + urlencode(query), status_code=303,
                            headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"})


def _event(body: ReminderRequest, user: dict, commitment: dict) -> dict:
    if body.cadence not in {"daily", "weekly", "once"}:
        raise _fail(422, "bad_cadence", "Choose a daily, weekly, or one-time Calendar reminder.")
    catalog = commitments.CATALOG.get(commitment.get("catalog_id"), {})
    title = catalog.get("title")
    if not isinstance(title, str) or not title.strip():
        raise _fail(422, "missing_input", "That commitment doesn't have a Calendar reminder title yet.")
    try:
        zone = ZoneInfo(user.get("timezone") or "America/Detroit")
        hour = (user.get("reminder_prefs") or {}).get("hour_local", 9)
        hour = hour if isinstance(hour, int) and 0 <= hour <= 23 else 9
        now = datetime.now(zone)
        value = body.start or commitment.get("target_date")
        if value:
            start = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if len(value) == 10:
                start = start.replace(hour=hour)
            start = start.replace(tzinfo=zone) if start.tzinfo is None else start.astimezone(zone)
        else:
            start = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if start <= now:
                start += timedelta(days=1)
    except (ValueError, TypeError, ZoneInfoNotFoundError):
        raise _fail(422, "bad_start", "Choose a valid reminder date and time, and check your account time zone.") from None
    event = {"summary": f"Hidden Rent: {title.strip()}",
             "description": "A reminder for your accepted energy-saving commitment. Mark it done in Hidden Rent when finished.",
             "start": {"dateTime": start.isoformat(), "timeZone": zone.key},
             "end": {"dateTime": (start + timedelta(minutes=15)).isoformat(), "timeZone": zone.key},
             "reminders": {"useDefault": False, "overrides": [{"method": "popup", "minutes": 10}]},
             "visibility": "private", "transparency": "transparent"}
    if body.cadence != "once":
        event["recurrence"] = ["RRULE:FREQ=" + body.cadence.upper()]
    return event


@router.post("/calendar/reminders")
def create_reminder(body: ReminderRequest, request: Request) -> dict:
    user = _user(request, body.user_id)
    commitment = next((c for c in commitments.list_commitments(user_id=body.user_id)
                       if c.get("id") == body.commitment_id and c.get("user_id") == body.user_id), None)
    if commitment is None:
        raise _fail(404, "not_found", "That commitment wasn't found in your account.")
    if commitment.get("status") != "accepted":
        raise _fail(422, "commitment_not_accepted", "Accept this commitment before adding a Calendar reminder.")
    event = _event(body, user, commitment)
    config = _config()
    if not is_connected(body.user_id):
        raise _fail(422, "calendar_not_connected", "Connect Google Calendar before adding a reminder.")
    reminder_id = secrets.token_hex(16)
    if config["mock"]:
        result = {"id": "mock_" + reminder_id, "htmlLink": None}
    else:
        token = _access_token(body.user_id, config)
        result = _google("POST", EVENTS_URL, headers={"Authorization": "Bearer " + token},
                         params={"sendUpdates": "none"}, json=event)
    if not isinstance(result.get("id"), str) or not result["id"]:
        raise _fail(503, "calendar_unavailable", UNAVAILABLE)
    with _connection() as con:
        con.execute("INSERT INTO gcal_reminders (id,user_id,commitment_id,event_id,html_link,start,cadence,mock) VALUES (?,?,?,?,?,?,?,?)",
                    (reminder_id, body.user_id, body.commitment_id, result["id"], result.get("htmlLink"),
                     event["start"]["dateTime"], body.cadence, int(config["mock"])))
    return {"reminder_id": reminder_id, "event_id": result["id"], "html_link": result.get("htmlLink"),
            "mock": config["mock"], **({"message": "Demo reminder only; no Google Calendar event was created."} if config["mock"] else {})}


@router.delete("/calendar/reminders/{reminder_id}")
def delete_reminder(reminder_id: str, request: Request) -> dict:
    with _connection() as con:
        row = con.execute("SELECT * FROM gcal_reminders WHERE id=?", (reminder_id,)).fetchone()
        reminder = dict(row) if row else None
    if reminder is None:
        raise _fail(404, "not_found", "That Calendar reminder wasn't found.")
    _user(request, reminder["user_id"])
    if not reminder["deleted"] and not reminder["mock"]:
        config = _config()
        if config["mock"]:
            raise _fail(503, "calendar_unavailable", UNAVAILABLE)
        token = _access_token(reminder["user_id"], config)
        _google("DELETE", EVENTS_URL + "/" + quote(reminder["event_id"], safe=""), allow_gone=True,
                headers={"Authorization": "Bearer " + token}, params={"sendUpdates": "none"})
    with _connection() as con:
        con.execute("UPDATE gcal_reminders SET deleted=1 WHERE id=?", (reminder_id,))
    return {"reminder_id": reminder_id, "deleted": True, "mock": bool(reminder["mock"])}

"""Phone accounts, web login by text, properties and the demo check-in (NEW_CHANGES.md NC-01, NC-02, NC-07, D5, D8, D9).

The phone number (iMessage handle) is the account (I1). Photon only delivers texts from allowlisted handles, so an
inbound text from a handle proves the phone: inbound-first, no passwords, no outbound texts from us.
Web login: POST /auth/web/start allowlists the phone with Photon and returns a link that opens Messages with
"login <code>" pre-filled; when that text arrives the agent calls POST /auth/web/confirm; the web polls
GET /auth/web/{login_id} and gets a bearer token once (only its SHA-256 is stored).
Agent-only endpoints need X-Agent-Key == AGENT_API_KEY (open, with a warning, while it's unset: dev mode)."""

import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import sqlite3
from contextlib import closing
from datetime import UTC, date, datetime, timedelta
from urllib.parse import quote
from zoneinfo import ZoneInfo

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app import bills, commitments, db, gcal, sessions
from app.estimate import MULTIFAMILY, _fail, estimate
from app.geo.footprints import _index
from app.map_widget import _selected

log = logging.getLogger(__name__)
router = APIRouter()
PHOTON_API = "https://spectrum.photon.codes"
CODE_TTL = timedelta(minutes=10)
TOKEN_TTL = timedelta(days=30)
# ponytail: limits are counts over web_logins rows (no in-memory state; a concurrent burst can overshoot by one)
PER_PHONE_10MIN = 3
PER_IP_10MIN = 20  # judges share one venue IP
NEW_NUMBERS_PER_HOUR = 5  # Photon's free tier has ~10 allowlist slots in all (P4's /join uses them too)
DEFAULT_PREFS = {"channel": "imessage", "cadence": "monthly", "hour_local": 18, "paused": False}
PREF_CHOICES = {"channel": ("imessage", "calendar", "none"), "cadence": ("daily", "weekly", "monthly", "off")}
INTERNAL_KEYS = ("answers", "model_params", "used_fixes")  # session-body keys that aren't part of the estimate
PHOTON_DOWN = ("photon_unavailable", "We couldn't reach our texting service. Try again in a minute.")
BAD_PHONE = ("bad_phone", "That doesn't look like a phone number. Send it with the area code, like (734) 555-0123.")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    phone_number TEXT NOT NULL UNIQUE,  -- normalized handle (I1)
    photon_user_id TEXT,
    display_name TEXT,
    alias TEXT,
    leaderboard_opt_in INTEGER NOT NULL DEFAULT 0,
    timezone TEXT NOT NULL DEFAULT 'America/Detroit',
    reminder_prefs TEXT NOT NULL,       -- JSON
    pending_checkin TEXT,               -- JSON {message_hint, property_id, address, created_at} or NULL
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS properties (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    building_id INTEGER,                -- /city and /map footprint id (OBJECTID)
    address TEXT NOT NULL,
    session_id TEXT NOT NULL,           -- the /estimate session holding its current estimate
    unit_sqft_given REAL,
    active INTEGER NOT NULL,
    move_in_date TEXT NOT NULL,
    move_out_date TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS properties_one_active ON properties(user_id) WHERE active = 1;  -- I2
CREATE TABLE IF NOT EXISTS web_logins (
    id TEXT PRIMARY KEY,
    phone_number TEXT NOT NULL,
    code TEXT NOT NULL,
    ip TEXT,
    new_number INTEGER NOT NULL,
    photon_user_id TEXT,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    user_id TEXT,                       -- set when the agent confirms the code
    token_issued INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS web_tokens (
    token_sha256 TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    expires_at TEXT NOT NULL
);
"""
USER_SQL = "SELECT u.*, p.id AS current_property_id FROM users u LEFT JOIN properties p ON p.user_id = u.id AND p.active = 1"


def _con() -> sqlite3.Connection:
    con = db.connect()
    con.executescript(SCHEMA)
    return con


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")  # one format everywhere, so strings compare as times


def _ago(delta: timedelta) -> str:
    return (datetime.now(UTC) - delta).isoformat(timespec="seconds")


def _sha256(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def normalize_handle(raw: str) -> str:
    """iMessage handle -> account key (I1): E.164 phone, same rule as agent/src/photon.ts normalizePhone (10 digits
    = US), or a lowercased email handle. ValueError if it's neither."""
    s = (raw or "").strip()
    if "@" in s:
        return s.lower()
    d = re.sub(r"\D", "", s)
    if not s.startswith("+"):
        d = "1" + d if len(d) == 10 else d if len(d) == 11 and d[0] == "1" else ""
    if not re.fullmatch(r"[1-9]\d{6,14}", d):
        raise ValueError("not a phone number or email handle")
    return "+" + d


def _handle(raw: str, phone_only: bool = False) -> str:
    try:
        h = normalize_handle(raw)
    except ValueError:
        raise _fail(422, *BAD_PHONE)
    if phone_only and "@" in h:
        raise _fail(422, *BAD_PHONE)
    return h


def mask(handle: str) -> str:
    """For logs and /me: •••-•••-0100, or j•••@icloud.com."""
    if "@" in handle:
        name, _, domain = handle.partition("@")
        return f"{name[:1]}•••@{domain}"
    return f"•••-•••-{handle[-4:]}"


_warned = False


def _agent_ok(request: Request) -> bool:
    global _warned
    key = os.environ.get("AGENT_API_KEY")
    if key:
        return hmac.compare_digest(request.headers.get("x-agent-key", "").encode(), key.encode())
    if not _warned:
        _warned = True
        log.warning("AGENT_API_KEY is unset: agent-only endpoints are open (dev mode). Set it for the demo.")
    return True


def agent_only(request: Request) -> None:
    """Dependency for endpoints only the iMessage agent may call."""
    if not _agent_ok(request):
        raise _fail(401, "agent_only", "Only the Hidden Rent texting agent can do that.")


def authorize(request: Request, user_id: str) -> None:
    """Allow the agent (X-Agent-Key) or a web token (Authorization: Bearer) for this user; else 401/403."""
    scheme, _, token = request.headers.get("authorization", "").partition(" ")
    if scheme.lower() == "bearer" and token:
        with closing(_con()) as con:
            row = con.execute("SELECT user_id FROM web_tokens WHERE token_sha256 = ? AND expires_at > ?",
                              (_sha256(token.strip()), _now())).fetchone()
        if row is None:
            raise _fail(401, "login_expired", "Your sign-in expired. Sign in again with your phone number.")
        if row["user_id"] != user_id:
            raise _fail(403, "forbidden", "That's not your account.")
        return
    if not _agent_ok(request):
        raise _fail(401, "login_required", "Sign in with your phone number first.")


def _user(row: sqlite3.Row) -> dict:
    u = dict(row)
    u["leaderboard_opt_in"] = bool(u["leaderboard_opt_in"])
    u["reminder_prefs"] = json.loads(u["reminder_prefs"])
    u["pending_checkin"] = json.loads(u["pending_checkin"]) if u["pending_checkin"] else None
    return u


def get_user(user_id: str) -> dict | None:
    with closing(_con()) as con:
        row = con.execute(USER_SQL + " WHERE u.id = ?", (user_id,)).fetchone()
    return _user(row) if row else None


def list_users() -> list[dict]:
    with closing(_con()) as con:
        return [_user(r) for r in con.execute(USER_SQL + " ORDER BY u.created_at")]


def _need_user(user_id: str) -> dict:
    u = get_user(user_id)
    if u is None:
        raise _fail(404, "not_found", "We don't have an account for that yet. Text Hidden Rent a listing to start.")
    return u


def _upsert_user(handle: str, photon_user_id: str | None = None) -> tuple[str, bool]:
    """(user_id, created). Race-safe: the unique handle decides, so two quick first messages make one user (I1)."""
    with closing(_con()) as con, con:
        cur = con.execute("INSERT INTO users (id, phone_number, photon_user_id, reminder_prefs, created_at) "
                          "VALUES (?, ?, ?, ?, ?) ON CONFLICT(phone_number) DO NOTHING",
                          ("u_" + secrets.token_hex(6), handle, photon_user_id, json.dumps(DEFAULT_PREFS), _now()))
        if photon_user_id:
            con.execute("UPDATE users SET photon_user_id = ? WHERE phone_number = ?", (photon_user_id, handle))
        uid = con.execute("SELECT id FROM users WHERE phone_number = ?", (handle,)).fetchone()["id"]
    return uid, cur.rowcount == 1


def _sqft(given: float | None, b: dict) -> dict:
    if given:
        return {"value": given, "source": "unit size sent with the address", "kind": "renter"}
    if b.get("sqft_estimated"):
        src = "estimated from the city building footprint (no unit size given; see the estimate's building.warnings)"
    elif b.get("type") in MULTIFAMILY:
        return {"value": b.get("sqft"), "source": "unit size from the listing or the renter", "kind": "listing"}
    else:
        src = "city building footprint area × stories"
    return {"value": b.get("sqft"), "source": src, "kind": "city_record"}


def _property(row: sqlite3.Row) -> dict:
    """Property shape (Appendix A) + session_id. Unit size and fuel come from the session, so answers show up."""
    p = dict(row)
    s = sessions.get(p["session_id"]) or {}
    fuel = (s.get("answers") or {}).get("heating_fuel")
    hc = s.get("heating_cooling") or {}
    p["unit_sqft"] = _sqft(p.pop("unit_sqft_given"), s.get("building") or {})
    p["heating_fuel"] = ({"value": fuel, "source": "renter's answer", "kind": "renter"} if fuel else
                         {"value": (hc.get("building") or {}).get("heating_fuel"),
                          "source": f"P1 heating/cooling model ({hc.get('method')})", "kind": "model"})
    p["active"] = bool(p["active"])
    return p


def get_property(property_id: str) -> dict | None:
    with closing(_con()) as con:
        row = con.execute("SELECT * FROM properties WHERE id = ?", (property_id,)).fetchone()
    return _property(row) if row else None


def _properties(user_id: str) -> list[dict]:
    with closing(_con()) as con:
        rows = con.execute("SELECT * FROM properties WHERE user_id = ? ORDER BY active DESC, move_in_date DESC, rowid DESC",
                           (user_id,)).fetchall()
    return [_property(r) for r in rows]


def current_property(user_id: str) -> dict | None:
    with closing(_con()) as con:
        row = con.execute("SELECT * FROM properties WHERE user_id = ? AND active = 1", (user_id,)).fetchone()
    return _property(row) if row else None


def property_for_session(session_id: str) -> dict | None:
    """The active home whose current estimate is this /estimate session (so /answer can snapshot it), else None."""
    with closing(_con()) as con:
        row = con.execute("SELECT * FROM properties WHERE session_id = ? AND active = 1", (session_id,)).fetchone()
    return _property(row) if row else None


def update_reminder_prefs(user_id: str, prefs: dict) -> dict:
    """Merge and validate (NEW_CHANGES.md §9.6: never at night); returns the stored prefs."""
    new = {**_need_user(user_id)["reminder_prefs"], **prefs}
    if set(new) - set(DEFAULT_PREFS):
        raise _fail(422, "bad_prefs", f"Reminder settings are {', '.join(DEFAULT_PREFS)}.")
    for k, ok in PREF_CHOICES.items():
        if new[k] not in ok:
            raise _fail(422, "bad_prefs", f"Reminder {k} can be {', '.join(ok[:-1])} or {ok[-1]}.")
    h = new["hour_local"]
    if type(h) is not int or not 8 <= h <= 21:
        raise _fail(422, "bad_hour", "Pick a reminder hour from 8 (8 AM) to 21 (9 PM). We never text at night.")
    if type(new["paused"]) is not bool:
        raise _fail(422, "bad_prefs", "Reminder paused should be true or false.")
    with closing(_con()) as con, con:
        con.execute("UPDATE users SET reminder_prefs = ? WHERE id = ?", (json.dumps(new), user_id))
    return new


def _building_id(body: dict) -> int | None:
    """The estimate's footprint id, as /map's building.id and /city's id; None if the city cache can't place it."""
    try:
        ix = _index()
        return int(ix.props[_selected(ix, body["building"]["footprint_geojson"])]["OBJECTID"])
    except (RuntimeError, HTTPException):
        return None


def _insert_property(con: sqlite3.Connection, user_id: str, body: dict, building_id: int | None,
                     unit_sqft: float | None) -> str:
    pid = "p_" + secrets.token_hex(6)
    con.execute("INSERT INTO properties (id, user_id, building_id, address, session_id, unit_sqft_given, active, "
                "move_in_date) VALUES (?, ?, ?, ?, ?, ?, 1, ?)",
                (pid, user_id, building_id, body["building"]["address"], body["session_id"], unit_sqft,
                 date.today().isoformat()))
    return pid


# --- iMessage accounts (agent) -----------------------------------------------------------------------------------

class PhoneAuth(BaseModel):
    phone: str
    photon_user_id: str | None = None
    session_id: str | None = None


@router.post("/auth/phone", dependencies=[Depends(agent_only)])
def auth_phone(req: PhoneAuth) -> dict:
    """Idempotent: an existing handle returns its user. A web session_id becomes the home if there's none yet."""
    uid, created = _upsert_user(_handle(req.phone), req.photon_user_id)
    if req.session_id and not current_property(uid) and (s := sessions.get(req.session_id)):
        bid = _building_id(s)
        try:
            with closing(_con()) as con, con:
                pid = _insert_property(con, uid, s, bid, None)
            bills.record_snapshot(pid, "questionnaire" if any(s.get("answers", {}).values()) else "initial_estimate", s)
        except sqlite3.IntegrityError:
            pass  # a concurrent first message already made the home (I2)
    return {"user_id": uid, "created": created, "current_property_id": _need_user(uid)["current_property_id"]}


# --- web login by text -------------------------------------------------------------------------------------------

def _allowlist(phone: str) -> dict | None:
    """agent/src/photon.ts createSharedUser: POST /projects/{id}/users/ (shared; idempotent per phone on Photon's side)
    -> {id, phoneNumber, assignedPhoneNumber}. None in dev mode (no creds, or USE_MOCKS like agent/src/env.ts)."""
    pid, secret = os.environ.get("PHOTON_PROJECT_ID"), os.environ.get("PHOTON_PROJECT_SECRET")
    if os.environ.get("USE_MOCKS", "").lower() in ("1", "true", "yes") or not (pid and secret):
        log.warning("Photon dev mode (no PHOTON_PROJECT_ID/SECRET or USE_MOCKS): %s not allowlisted; sms: link instead",
                    mask(phone))
        return None
    try:
        r = httpx.post(f"{PHOTON_API}/projects/{pid}/users/", json={"type": "shared", "phoneNumber": phone},
                       auth=(pid, secret), timeout=15)
        body = r.json()
    except (httpx.HTTPError, ValueError) as e:
        log.warning("Photon allowlist for %s failed: %s", mask(phone), type(e).__name__)
        raise _fail(503, *PHOTON_DOWN)
    if r.is_error or not (isinstance(body, dict) and body.get("succeed") and body.get("data")):
        log.warning("Photon allowlist for %s failed: HTTP %s", mask(phone), r.status_code)
        raise _fail(503, *PHOTON_DOWN)
    return body["data"]


class WebStart(BaseModel):
    phone: str


@router.post("/auth/web/start")
def web_start(req: WebStart, request: Request) -> dict:
    """Allowlist the phone with Photon, then a link that opens Messages with "login <code>" (the user taps Send)."""
    phone = _handle(req.phone, phone_only=True)
    ip = request.headers.get("cf-connecting-ip") or (request.client.host if request.client else None)
    with closing(_con()) as con:
        count = lambda where, *args: con.execute(f"SELECT count(*) FROM web_logins WHERE {where}", args).fetchone()[0]
        by_phone = count("phone_number = ? AND created_at > ?", phone, _ago(timedelta(minutes=10)))
        by_ip = count("ip = ? AND created_at > ?", ip, _ago(timedelta(minutes=10)))
        new = not (count("phone_number = ?", phone) or
                   con.execute("SELECT 1 FROM users WHERE phone_number = ?", (phone,)).fetchone())
        new_this_hour = count("new_number = 1 AND created_at > ?", _ago(timedelta(hours=1)))
    if by_phone >= PER_PHONE_10MIN or by_ip >= PER_IP_10MIN:
        raise _fail(429, "too_many_codes", "Too many login codes. Wait 10 minutes and try again.")
    if new and new_this_hour >= NEW_NUMBERS_PER_HOUR:
        raise _fail(429, "signups_full", "Hidden Rent is taking a few new numbers an hour tonight. Try again later.")

    photon = _allowlist(phone)
    code = f"{secrets.randbelow(10**6):06d}"
    text = f"login {code}"
    login_id = secrets.token_urlsafe(16)
    expires = (datetime.now(UTC) + CODE_TTL).isoformat(timespec="seconds")
    with closing(_con()) as con, con:
        con.execute("INSERT INTO web_logins (id, phone_number, code, ip, new_number, photon_user_id, created_at, "
                    "expires_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (login_id, phone, code, ip, int(new), photon and photon["id"], _now(), expires))
    return {"login_id": login_id, "code": code, "text_body": text,
            "redirect_url": (f"{PHOTON_API}/users/{quote(photon['id'], safe='')}/redirect?msg={quote(text, safe='')}"
                             if photon else f"sms:&body={quote(text, safe='')}"),
            "assigned_number_masked": mask(photon["assignedPhoneNumber"]) if photon else None,
            "expires_at": expires}


class WebConfirm(BaseModel):
    code: str
    phone: str


@router.post("/auth/web/confirm", dependencies=[Depends(agent_only)])
def web_confirm(req: WebConfirm) -> dict:
    """The agent got "login <code>" from handle `phone`: that text is the proof. Creates the user if needed."""
    phone = _handle(req.phone)
    with closing(_con()) as con:
        row = con.execute("SELECT * FROM web_logins WHERE phone_number = ? AND code = ? ORDER BY created_at DESC",
                          (phone, re.sub(r"\D", "", req.code))).fetchone()
    if row is None:
        raise _fail(404, "bad_code", "That login code doesn't match this number. Start again on the website and "
                    "text the new code from the same phone.")
    if not row["user_id"] and row["expires_at"] <= _now():
        raise _fail(410, "code_expired", "That login code expired. Start again on the website for a new one.")
    uid, created = row["user_id"], False
    if not uid:  # a redelivered text is a no-op
        uid, created = _upsert_user(phone, row["photon_user_id"])
        with closing(_con()) as con, con:
            con.execute("UPDATE web_logins SET user_id = ? WHERE id = ?", (uid, row["id"]))
    return {"login_id": row["id"], "user_id": uid, "created": created}


@router.get("/auth/web/{login_id}")
def web_status(login_id: str) -> dict:
    """The web polls this. Once verified, the first poll returns the bearer token; later polls don't."""
    with closing(_con()) as con, con:
        row = con.execute("SELECT * FROM web_logins WHERE id = ?", (login_id,)).fetchone()
        if row is None:
            raise _fail(404, "not_found", "That sign-in expired. Start again with your phone number.")
        if not row["user_id"]:
            return {"status": "expired" if row["expires_at"] <= _now() else "pending"}
        token = None
        if con.execute("UPDATE web_logins SET token_issued = 1 WHERE id = ? AND token_issued = 0", (login_id,)).rowcount:
            token = secrets.token_urlsafe(32)
            con.execute("INSERT INTO web_tokens (token_sha256, user_id, expires_at) VALUES (?, ?, ?)",
                        (_sha256(token), row["user_id"], (datetime.now(UTC) + TOKEN_TTL).isoformat(timespec="seconds")))
    return {"status": "verified", "user_id": row["user_id"], **({"token": token} if token else {})}


# --- /me (D8 rehydration) ----------------------------------------------------------------------------------------

def _me(user_id: str) -> dict:
    u = _need_user(user_id)
    props = _properties(user_id)
    cur = next((p for p in props if p["active"]), None)
    est = sessions.get(cur["session_id"]) if cur else None
    return {"user_id": u["id"], "phone_masked": mask(u["phone_number"]), "alias": u["alias"],
            "leaderboard_opt_in": u["leaderboard_opt_in"], "timezone": u["timezone"],
            "reminder_prefs": u["reminder_prefs"], "current_property_id": u["current_property_id"],
            "properties": props, "current_estimate": est and {k: v for k, v in est.items() if k not in INTERNAL_KEYS},
            "pending_checkin": u["pending_checkin"], "calendar_connected": gcal.is_connected(u["id"])}


@router.get("/me/{user_id}")
def get_me(user_id: str, request: Request) -> dict:
    authorize(request, user_id)
    return _me(user_id)


class MePatch(BaseModel):
    alias: str | None = None
    leaderboard_opt_in: bool | None = None
    timezone: str | None = None
    reminder_prefs: dict | None = None
    pending_checkin: None = None  # send null to clear it once the check-in reply is handled


@router.patch("/me/{user_id}")
def patch_me(user_id: str, req: MePatch, request: Request) -> dict:
    authorize(request, user_id)
    u = _need_user(user_id)
    alias = ((req.alias or "").strip() or None) if "alias" in req.model_fields_set else u["alias"]
    if alias and len(alias) > 24:
        raise _fail(422, "bad_alias", "Pick a leaderboard name of 24 characters or fewer.")
    opt_in = u["leaderboard_opt_in"] if req.leaderboard_opt_in is None else req.leaderboard_opt_in
    if opt_in and not alias:
        raise _fail(422, "alias_required", "Pick a leaderboard name first, so your phone number never shows.")
    if req.timezone:
        try:
            ZoneInfo(req.timezone)
        except (KeyError, ValueError):  # ZoneInfoNotFoundError is a KeyError
            raise _fail(422, "bad_timezone", "That time zone isn't one we know. Try America/Detroit.")
    if req.reminder_prefs is not None:
        update_reminder_prefs(user_id, req.reminder_prefs)
    with closing(_con()) as con, con:
        con.execute("UPDATE users SET alias = ?, leaderboard_opt_in = ?, timezone = COALESCE(?, timezone) WHERE id = ?",
                    (alias, int(opt_in), req.timezone, user_id))
        if "pending_checkin" in req.model_fields_set:
            con.execute("UPDATE users SET pending_checkin = NULL WHERE id = ?", (user_id,))
    return _me(user_id)


# --- properties (NC-02) ------------------------------------------------------------------------------------------

class PropertyRequest(BaseModel):
    user_id: str
    address: str | None = None
    url: str | None = None
    unit_sqft: float | None = None
    session_id: str | None = None  # adopt this /estimate session (answers kept, no re-estimate)


@router.post("/properties")
def post_property(req: PropertyRequest, request: Request) -> dict:
    """New home: a fresh estimate (and session), or the session the renter already answered on the web; the previous
    active home archived (I2), any check-in resolved."""
    authorize(request, req.user_id)
    _need_user(req.user_id)
    if req.session_id:
        body = sessions.get(req.session_id)
        if body is None:
            raise _fail(404, "not_found", "That report expired. Send the address again.")
        cur = current_property(req.user_id)
        if cur and cur["session_id"] == req.session_id:  # a double tap: already this home
            return {"property_id": cur["id"], "building_id": cur["building_id"], "estimate": body, "active": True}
    else:
        body = estimate(req.url, req.address, req.unit_sqft)
    bid = _building_id(body)
    with closing(_con()) as con, con:  # one transaction: the archive's write lock serializes concurrent moves
        con.execute("UPDATE properties SET active = 0, move_out_date = ? WHERE user_id = ? AND active = 1",
                    (date.today().isoformat(), req.user_id))
        pid = _insert_property(con, req.user_id, body, bid, req.unit_sqft)
        con.execute("UPDATE users SET pending_checkin = NULL WHERE id = ?", (req.user_id,))
    # as the /auth/phone handoff: an answered session snapshots as questionnaire
    bills.record_snapshot(pid, "questionnaire" if any((body.get("answers") or {}).values()) else "initial_estimate", body)
    return {"property_id": pid, "building_id": bid, "estimate": body, "active": True}


def _owned(property_id: str, request: Request) -> dict:
    p = get_property(property_id)
    if p is None:
        raise _fail(404, "not_found", "We don't have that home on file.")
    authorize(request, p["user_id"])
    return p


@router.post("/properties/{property_id}/activate")
def activate_property(property_id: str, request: Request) -> dict:
    """Make an earlier home current again (moving back); the active one is archived."""
    p = _owned(property_id, request)
    with closing(_con()) as con, con:
        con.execute("UPDATE properties SET active = 0, move_out_date = ? WHERE user_id = ? AND active = 1 AND id != ?",
                    (date.today().isoformat(), p["user_id"], property_id))
        con.execute("UPDATE properties SET active = 1, move_out_date = NULL WHERE id = ?", (property_id,))
        con.execute("UPDATE users SET pending_checkin = NULL WHERE id = ?", (p["user_id"],))
    return get_property(property_id)


@router.get("/properties/{property_id}/history")
def property_history(property_id: str, request: Request) -> dict:
    _owned(property_id, request)
    return {"property_id": property_id, "snapshots": bills.list_snapshots(property_id),
            "bills": bills.list_bills(property_id), "impact": bills.list_impact(property_id),
            "commitments": commitments.list_commitments(property_id=property_id)}


# --- NC-07 check-in trigger (D9: manual for the demo) ------------------------------------------------------------

class CheckinRequest(BaseModel):
    user_id: str


@router.post("/checkins/trigger", dependencies=[Depends(agent_only)])
def trigger_checkin(req: CheckinRequest) -> dict:
    """Record a pending "Still at <address>?" check-in (shown on /me); the agent texts it. A "moved" reply goes to
    POST /properties, a "yes" to the bill flow; then PATCH /me {"pending_checkin": null}."""
    p = current_property(_need_user(req.user_id)["id"])
    if p is None:
        raise _fail(409, "no_property", "No home on file yet. Text an address or listing link to get started.")
    pending = {"message_hint": "still_at_address", "property_id": p["id"], "address": p["address"], "created_at": _now()}
    with closing(_con()) as con, con:
        con.execute("UPDATE users SET pending_checkin = ? WHERE id = ?", (json.dumps(pending), req.user_id))
    return pending

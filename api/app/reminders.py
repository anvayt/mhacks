"""Durable reminder payloads for P4; this module NEVER sends messages.

Policy source: NEW_CHANGES.md §4 C4 (Photon deliverability), §6.4, §9.6, D4/D8/D9:
opt in, one proactive text per local day across kinds, pause after two unanswered,
and never at night. Chosen quiet hours are 22:00–08:00 local (not a Photon clock
rule); send only during the user's chosen hour, matching accounts' 8–21 bounds.
Monthly check-in gets one follow-up after 3 local days (our 'few days' policy).
Daily/weekly opt-in enables task/weather reminders as well as monthly check-ins.
A costly_week alert additionally needs >= $5 above the forecast's normal week:
this is a notification-noise floor we chose, NOT a model/accuracy threshold.

P4: one serialized poller every 5 min, X-Agent-Key required. Send each returned
reminder_id at most once, then POST /{id}/sent only after transport success. Keep a
local durable delivered-ID receipt until that idempotent acknowledgement succeeds;
retry the acknowledgement, not the text. Failed sends leave the same queued ID.
POST /inbound for each verified incoming message; stop/pause persist across inbound.
No distributed exactly-once transport claim: multiple simultaneous senders need a
transport idempotency key or a future lease/claim protocol. Never log raw handles.
"""

import hmac
import os
import secrets
from contextlib import closing
from datetime import date, datetime, timezone
from math import isfinite
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app import accounts, commitments, db, forecast

router = APIRouter()
QUIET_END, QUIET_START = 8, 22
CHECKIN_FOLLOWUP_DAYS = 3
COSTLY_WEEK_MIN_EXCESS_USD = 5.0
KINDS = {"checkin", "task", "weather"}


def _fail(status, code, message):
    return HTTPException(status, {"code": code, "message": message})


def _now():
    return datetime.now(timezone.utc)


def _instant(value=None):
    if value is None:
        return _now()
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError
        return parsed.astimezone(timezone.utc)
    except (ValueError, TypeError):
        raise _fail(422, "bad_time", "Use an ISO date and time with a time zone, such as 2026-10-04T18:00:00-04:00.") from None


def _con():
    con = db.connect()
    con.executescript("""
        CREATE TABLE IF NOT EXISTS reminder_controls (
            user_id TEXT PRIMARY KEY, stopped INTEGER NOT NULL DEFAULT 0,
            paused INTEGER NOT NULL DEFAULT 0, auto_paused INTEGER NOT NULL DEFAULT 0,
            unanswered INTEGER NOT NULL DEFAULT 0, last_inbound TEXT);
        CREATE TABLE IF NOT EXISTS reminder_queue (
            id TEXT PRIMARY KEY, user_id TEXT NOT NULL, property_id TEXT NOT NULL,
            commitment_id TEXT, kind TEXT NOT NULL, text_hint TEXT NOT NULL,
            fact_key TEXT NOT NULL, session_id TEXT, slot TEXT NOT NULL,
            demo INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'queued', sent_at TEXT,
            UNIQUE(user_id, slot));
        CREATE INDEX IF NOT EXISTS reminder_sent_user ON reminder_queue(user_id, status, sent_at);
    """)
    return con


def _agent_only(request):
    # accounts.authorize also accepts a web bearer and its current dev mode may
    # allow no key. Neither can grant a global feed of private phone handles.
    key = os.environ.get("AGENT_API_KEY", "")
    given = request.headers.get("X-Agent-Key", "")
    if not key or not hmac.compare_digest(given.encode(), key.encode()):
        raise _fail(401, "agent_only", "Only the Hidden Rent texting agent can do that.")


def _user(request, user_id):
    accounts.authorize(request, user_id)
    user = accounts.get_user(user_id)
    if user is None:
        raise _fail(404, "not_found", "We couldn't find that account. Text Hidden Rent to start.")
    return user


def _history(con, user_id):
    control = con.execute("SELECT * FROM reminder_controls WHERE user_id=?", (user_id,)).fetchone()
    sent = [dict(r) for r in con.execute("SELECT * FROM reminder_queue WHERE user_id=? AND status='sent' ORDER BY sent_at DESC, rowid DESC", (user_id,))]
    return dict(control) if control else {}, sent


def _local(user, now):
    try:
        return now.astimezone(ZoneInfo(user.get("timezone") or "America/Detroit"))
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        return None  # A broken timezone must never guess a safe send hour.


def eligible(user, control, sent, now, *, kind=None, demo=False):
    """The single D4 delivery gate, used for both queued and new payloads."""
    prefs = user.get("reminder_prefs") or {}
    cadence = prefs.get("cadence", "off")
    local = _local(user, now)
    if (local is None or not user.get("phone_number") or prefs.get("channel") != "imessage"
            or cadence not in {"daily", "weekly", "monthly"} or prefs.get("paused")
            or control.get("stopped") or control.get("paused") or control.get("auto_paused")
            or control.get("unanswered", 0) >= 2):
        return False
    if demo:
        return True  # Explicit demo bypasses clock, cadence interval and daily cap only.
    hour = prefs.get("hour_local", 18)
    if type(hour) is not int or not QUIET_END <= local.hour < QUIET_START or local.hour != hour:
        return False
    if any(_instant(row["sent_at"]).astimezone(local.tzinfo).date() == local.date() for row in sent):
        return False
    if kind in {"task", "weather"}:
        if cadence == "monthly":
            return False
        previous = next((r for r in sent if r["kind"] in {"task", "weather"}), None)
        if cadence == "weekly" and previous and (local.date() - _instant(previous["sent_at"]).astimezone(local.tzinfo).date()).days < 7:
            return False
    return True


def _tasks(user, home):
    result = []
    for item in commitments.list_commitments(property_id=home["id"], user_id=user["id"]):
        if (item.get("user_id") != user["id"] or item.get("property_id") != home["id"]
                or item.get("status") != "accepted" or not item.get("target_date")
                or item.get("reminder_channel", "imessage") != "imessage"):
            continue
        try:
            date.fromisoformat(item["target_date"])
        except (ValueError, TypeError):
            continue
        title = commitments.CATALOG.get(item.get("catalog_id"), {}).get("title")
        if isinstance(title, str) and title.strip():
            result.append({**item, "safe_title": title.strip()})
    return sorted(result, key=lambda c: (c["target_date"], c["id"]))


def _candidate(user, home, control, sent, now, *, kind=None, demo=False, forecasts=None):
    local = _local(user, now)
    if not eligible(user, control, sent, now, demo=demo):
        return None
    checkins = [r for r in sent if r["kind"] == "checkin" and r["property_id"] == home["id"]]
    first_this_month = not any(_instant(r["sent_at"]).astimezone(local.tzinfo).strftime("%Y-%m") == local.strftime("%Y-%m") for r in checkins)
    followup = (control.get("unanswered") == 1 and sent and sent[0]["kind"] == "checkin"
                and sent[0]["property_id"] == home["id"]
                and (local.date() - _instant(sent[0]["sent_at"]).astimezone(local.tzinfo).date()).days >= CHECKIN_FOLLOWUP_DAYS)
    if kind in (None, "checkin") and home.get("address") and (first_this_month or followup or demo):
        return {"kind": "checkin", "text_hint": f"Still at {home['address']}?",
                "fact_key": "checkin:" + local.strftime("%Y-%m")}
    if kind in (None, "task") and eligible(user, control, sent, now, kind="task", demo=demo):
        tasks = _tasks(user, home)
        if tasks:
            task = tasks[0]
            return {"kind": "task", "commitment_id": task["id"],
                    "text_hint": f"Your target for {task['safe_title']} is {task['target_date']}.",
                    "fact_key": "task:" + task["id"]}
    if kind not in (None, "weather") or not home.get("session_id") or not eligible(user, control, sent, now, kind="weather", demo=demo):
        return None
    try:
        forecasts = forecasts if forecasts is not None else {}
        if home["session_id"] not in forecasts:
            forecasts[home["session_id"]] = forecast.forecast(home["session_id"])
        weather = forecasts[home["session_id"]]
    except HTTPException:
        return None  # Forecast outage or expired session never blocks other users/kinds.
    for alert in weather.get("alerts", []):
        if alert.get("type") not in {"cold_snap", "heat_wave", "costly_week"} or not isinstance(alert.get("detail"), str):
            continue
        try:
            alert_date = date.fromisoformat(alert["date"])
        except (KeyError, ValueError, TypeError):
            continue
        if alert_date < local.date():
            continue
        if alert["type"] == "costly_week":
            week = weather.get("week") or {}
            total, normal = week.get("total_usd"), week.get("normal_total_usd")
            if (type(total) not in (int, float) or type(normal) not in (int, float)
                    or not isfinite(total) or not isfinite(normal) or total - normal < COSTLY_WEEK_MIN_EXCESS_USD):
                continue
        fact = f"weather:{home['session_id']}:{alert['type']}:{alert['date']}"
        if any(r["fact_key"] == fact for r in sent) and not demo:
            continue
        return {"kind": "weather", "text_hint": alert["detail"], "fact_key": fact}
    return None


def _payload(row, user):
    # Raw handle is returned only by agent-key-only routes, never by web controls.
    return {"reminder_id": row["id"], "user_id": row["user_id"], "handle": user["phone_number"],
            "kind": row["kind"], "text_hint": row["text_hint"], "property_id": row["property_id"],
            **({"commitment_id": row["commitment_id"]} if row.get("commitment_id") else {}),
            **({"demo": True} if row.get("demo") else {})}


def _queued_valid(row, user, home, now):
    if row["property_id"] != home["id"] or row["slot"] != _local(user, now).date().isoformat():
        return False
    if row["kind"] == "task":
        return any(c["id"] == row["commitment_id"] for c in _tasks(user, home))
    return row["kind"] != "weather" or row["session_id"] == home.get("session_id")


def _next(user, now, *, kind=None, demo=False, forecasts=None, fixed_time=False):
    home = accounts.current_property(user["id"])
    if not home or home.get("user_id") != user["id"] or home.get("active") is False:
        return None
    with closing(_con()) as con, con:
        control, sent = _history(con, user["id"])
        if not eligible(user, control, sent, now, demo=demo):
            return None
        queued = con.execute("SELECT * FROM reminder_queue WHERE user_id=? AND status='queued' AND demo=0 ORDER BY created_at DESC LIMIT 1", (user["id"],)).fetchone()
        if queued and not demo:
            row = dict(queued)
            if _queued_valid(row, user, home, now) and eligible(user, control, sent, now, kind=row["kind"]):
                return _payload(row, user)
            con.execute("UPDATE reminder_queue SET status='cancelled',slot=slot||':cancelled:'||id WHERE id=?", (row["id"],))
    candidate = _candidate(user, home, control, sent, now, kind=kind, demo=demo, forecasts=forecasts)
    if candidate is None:
        return None
    now = now if fixed_time or demo else _now()
    if accounts.current_property(user["id"]) != home:
        return None  # The renter moved while the forecast was being fetched.
    slot = "demo:" + secrets.token_hex(12) if demo else _local(user, now).date().isoformat()
    with closing(_con()) as con, con:
        con.execute("BEGIN IMMEDIATE")
        control, sent = _history(con, user["id"])
        # Recheck after a potentially slow forecast: stop/sent can happen meanwhile.
        fresh_user = accounts.get_user(user["id"])
        if (fresh_user is None or ("current_property_id" in fresh_user and fresh_user["current_property_id"] != home["id"])
                or not eligible(fresh_user, control, sent, now, kind=candidate["kind"], demo=demo)):
            return None
        row = con.execute("SELECT * FROM reminder_queue WHERE user_id=? AND slot=?", (user["id"], slot)).fetchone()
        if row:
            return _payload(dict(row), fresh_user) if row["status"] == "queued" else None
        identifier = "r_" + secrets.token_hex(12)
        con.execute("INSERT INTO reminder_queue (id,user_id,property_id,commitment_id,kind,text_hint,fact_key,session_id,slot,demo,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (identifier, user["id"], home["id"], candidate.get("commitment_id"), candidate["kind"], candidate["text_hint"],
                     candidate["fact_key"], home.get("session_id"), slot, int(demo), now.isoformat()))
        row = dict(con.execute("SELECT * FROM reminder_queue WHERE id=?", (identifier,)).fetchone())
        return _payload(row, fresh_user)


class UserRequest(BaseModel):
    user_id: str


class DemoRequest(UserRequest):
    kind: str | None = None


@router.get("/reminders/due")
def due(request: Request, now: str | None = None) -> list[dict]:
    _agent_only(request)
    moment = _instant(now)
    result, forecasts = [], {}
    for user in accounts.list_users():
        accounts.authorize(request, user["id"])
        item = _next(user, moment, forecasts=forecasts, fixed_time=now is not None)
        if item is not None:
            result.append(item)
    return result


@router.post("/reminders/inbound")
def inbound(body: UserRequest, request: Request):
    _agent_only(request)
    user = _user(request, body.user_id)
    with closing(_con()) as con, con:
        con.execute("INSERT OR IGNORE INTO reminder_controls (user_id) VALUES (?)", (body.user_id,))
        con.execute("UPDATE reminder_controls SET unanswered=0,auto_paused=0,last_inbound=? WHERE user_id=?", (_now().isoformat(), body.user_id))
        con.execute("UPDATE reminder_queue SET status='cancelled',slot=slot||':cancelled:'||id WHERE user_id=? AND status='queued'", (body.user_id,))
        control, _ = _history(con, body.user_id)
    return {"user_id": body.user_id, "unanswered": 0, "stopped": bool(control["stopped"]), "paused": bool(control["paused"] or (user.get("reminder_prefs") or {}).get("paused"))}


@router.post("/reminders/demo-send")
def demo_send(body: DemoRequest, request: Request):
    _agent_only(request)
    user = _user(request, body.user_id)
    if body.kind is not None and body.kind not in KINDS:
        raise _fail(422, "bad_kind", "Choose a check-in, task, or weather reminder.")
    result = _next(user, _now(), kind=body.kind, demo=True)
    if result is None:
        raise _fail(422, "no_reminder", "No reminder is available. Reminders may be paused, stopped, or switched off.")
    return result


@router.post("/reminders/{reminder_id}/sent")
def sent(reminder_id: str, request: Request):
    _agent_only(request)
    with closing(_con()) as con, con:
        con.execute("BEGIN IMMEDIATE")
        row = con.execute("SELECT * FROM reminder_queue WHERE id=?", (reminder_id,)).fetchone()
        if row is None:
            raise _fail(404, "not_found", "That reminder wasn't found.")
        _user(request, row["user_id"])
        if row["status"] != "sent":
            # An acknowledgement records an actual send, even if a stop or hour
            # boundary raced it; it must not re-enable reminders or lose the cap.
            con.execute("UPDATE reminder_queue SET status='sent',sent_at=? WHERE id=?", (_now().isoformat(), reminder_id))
            con.execute("INSERT OR IGNORE INTO reminder_controls (user_id) VALUES (?)", (row["user_id"],))
            con.execute("UPDATE reminder_controls SET unanswered=unanswered+1,auto_paused=(unanswered+1>=2) WHERE user_id=?", (row["user_id"],))
        control, _ = _history(con, row["user_id"])
    return {"reminder_id": reminder_id, "sent": True, "unanswered": control["unanswered"],
            "paused": bool(control["paused"] or control["auto_paused"]), "stopped": bool(control["stopped"])}


def _control(request, user_id, action):
    _user(request, user_id)
    with closing(_con()) as con, con:
        con.execute("INSERT OR IGNORE INTO reminder_controls (user_id) VALUES (?)", (user_id,))
        if action == "resume":
            con.execute("UPDATE reminder_controls SET stopped=0,paused=0,auto_paused=0,unanswered=0 WHERE user_id=?", (user_id,))
        elif action == "stop":
            con.execute("UPDATE reminder_controls SET stopped=1 WHERE user_id=?", (user_id,))
        else:
            con.execute("UPDATE reminder_controls SET paused=1 WHERE user_id=?", (user_id,))
        con.execute("UPDATE reminder_queue SET status='cancelled',slot=slot||':cancelled:'||id WHERE user_id=? AND status='queued'", (user_id,))
        control, _ = _history(con, user_id)
    # Never directly edit accounts' table. A failed prefs write leaves our stop in
    # force; explicit resume retries safely. Keep channel/cadence choices intact.
    prefs = accounts.update_reminder_prefs(user_id, {"paused": action != "resume"})
    return {"user_id": user_id, "stopped": bool(control["stopped"]),
            "paused": bool(control["paused"] or control["auto_paused"] or prefs.get("paused")), "reminder_prefs": prefs}


@router.post("/reminders/{user_id}/stop")
def stop(user_id: str, request: Request):
    return _control(request, user_id, "stop")


@router.post("/reminders/{user_id}/pause")
def pause(user_id: str, request: Request):
    return _control(request, user_id, "pause")


@router.post("/reminders/{user_id}/resume")
def resume(user_id: str, request: Request):
    return _control(request, user_id, "resume")

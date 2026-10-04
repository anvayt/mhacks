"""Daily habit streak per account: consecutive local days the renter kept their pledge to an accepted commitment.

POST /habits/{user_id}/checkin {date?, commitment_id?, source}: one check-in per (user, local date), idempotent.
     Only today or yesterday (a late reply after midnight) in the user's timezone (default America/Detroit). Needs an
     accepted or completed (never dismissed) commitment at the current home, else 422 no_habits.
GET  /habits/{user_id}: the same summary + the last 30 days of check-ins.
Streak = consecutive local days with a check-in ending today, or ending yesterday while today is still pending.
Self-reported habit keeping, never counted as savings or impact (NEW_CHANGES §16)."""

from contextlib import closing
from datetime import UTC, date as Date, datetime, timedelta
from typing import Literal
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app import accounts, badges, commitments, db

router = APIRouter()
DEFAULT_TZ = "America/Detroit"
SCHEMA = """
CREATE TABLE IF NOT EXISTS habit_checkins (
  user_id TEXT NOT NULL, local_date TEXT NOT NULL, commitment_id TEXT, source TEXT NOT NULL, created_at TEXT NOT NULL,
  PRIMARY KEY (user_id, local_date));
CREATE TABLE IF NOT EXISTS habit_best (user_id TEXT PRIMARY KEY, best INTEGER NOT NULL);
"""
NO_HABITS = "Pick a daily habit first: text 'options'"


def _fail(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(status, {"code": code, "message": message})


def _con():
    c = db.connect()
    c.executescript(SCHEMA)
    return c


def _now() -> datetime:
    return datetime.now(UTC)


def today(user: dict) -> Date:
    try:
        tz = ZoneInfo(user.get("timezone") or DEFAULT_TZ)
    except (KeyError, ValueError):  # ZoneInfoNotFoundError is a KeyError; PATCH /me validates, so this is old data
        tz = ZoneInfo(DEFAULT_TZ)
    return _now().astimezone(tz).date()


def _current(con, user_id: str, day: Date) -> tuple[int, str | None]:
    """(streak ending today, or yesterday while today is pending; latest check-in date)."""
    days = [r[0] for r in con.execute("SELECT local_date FROM habit_checkins WHERE user_id = ? ORDER BY local_date DESC",
                                      (user_id,))]
    have = set(days)
    end = day if day.isoformat() in have else day - timedelta(days=1)
    n = 0
    while (end - timedelta(days=n)).isoformat() in have:
        n += 1
    return n, days[0] if days else None


def summary(user: dict) -> dict:
    day = today(user)
    with closing(_con()) as con:
        current, last = _current(con, user["id"], day)
        row = con.execute("SELECT best FROM habit_best WHERE user_id = ?", (user["id"],)).fetchone()
    best = max(current, row["best"] if row else 0)
    return {"current": current, "best": best, "checked_in_today": last == day.isoformat(), "last_checkin_date": last,
            "badges": badges.habit_badges(best)}


def reminder_hint(user: dict) -> str:
    """The streak facts a daily task reminder carries (app/reminders.py); the agent sends text_hint as is."""
    s = summary(user)
    days = f"{s['current']} day{'' if s['current'] == 1 else 's'}"
    if s["checked_in_today"]:
        return f"Habit streak {days}; today already counts."
    if s["current"]:
        return f"Habit streak {days}; reply done to keep it."
    return "Reply done once you've done it today to start a habit streak."


def _user(request: Request, user_id: str) -> dict:
    accounts.authorize(request, user_id)
    user = accounts.get_user(user_id)
    if user is None:
        raise _fail(404, "not_found", "We don't have an account for that yet. Text Hidden Rent a listing to start.")
    return user


class CheckinRequest(BaseModel):
    date: Date | None = None
    commitment_id: str | None = None
    source: Literal["imessage", "web"]


@router.post("/habits/{user_id}/checkin")
def checkin(user_id: str, req: CheckinRequest, request: Request) -> dict:
    user = _user(request, user_id)
    day = today(user)
    when = req.date or day
    if when not in (day, day - timedelta(days=1)):
        raise _fail(422, "bad_date", "You can check in for today, or for yesterday right after midnight.")
    home = accounts.current_property(user_id)
    habits = {c["id"] for c in commitments.list_commitments(property_id=home["id"])
              if c["status"] in ("accepted", "completed")} if home else set()
    if not habits:
        raise _fail(422, "no_habits", NO_HABITS)
    if req.commitment_id and req.commitment_id not in habits:
        raise _fail(422, "unknown_commitment", "That isn't one of your daily habits. Text 'options' to see them.")
    with closing(_con()) as con, con:
        con.execute("INSERT OR IGNORE INTO habit_checkins (user_id, local_date, commitment_id, source, created_at) "
                    "VALUES (?, ?, ?, ?, ?)", (user_id, when.isoformat(), req.commitment_id, req.source,
                                               _now().isoformat(timespec="seconds")))
        current, _ = _current(con, user_id, day)
        con.execute("INSERT INTO habit_best (user_id, best) VALUES (?, ?) "
                    "ON CONFLICT(user_id) DO UPDATE SET best = max(best, excluded.best)", (user_id, current))
    return summary(user)


@router.get("/habits/{user_id}")
def get_habits(user_id: str, request: Request) -> dict:
    user = _user(request, user_id)
    since = (today(user) - timedelta(days=29)).isoformat()
    with closing(_con()) as con:
        rows = [dict(r) for r in con.execute("SELECT local_date AS date, commitment_id, source FROM habit_checkins "
                                             "WHERE user_id = ? AND local_date >= ? ORDER BY local_date DESC",
                                             (user_id, since))]
    return {**summary(user), "checkins": rows}

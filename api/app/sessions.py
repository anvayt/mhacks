"""Sessions: the latest /estimate or /answer body per session_id, in SQLite (env SESSIONS_DB, default /data/).

A body is the PLAN.md §10 estimate plus "answers" {question_id: value or None if skipped} and "model_params"
(the /hc/estimate query params: lat, lon, unit_sqft, building_type, block_group)."""

import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path

from app.geo import DATA_DIR

DB = os.environ.get("SESSIONS_DB") or str(DATA_DIR / "sessions.sqlite")


def _connect() -> sqlite3.Connection:
    Path(DB).parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, body TEXT NOT NULL)")
    return c


def save(body: dict) -> None:
    with closing(_connect()) as c, c:
        c.execute("INSERT OR REPLACE INTO sessions (id, body) VALUES (?, ?)", (body["session_id"], json.dumps(body)))


def get(session_id: str) -> dict | None:
    with closing(_connect()) as c:
        row = c.execute("SELECT body FROM sessions WHERE id = ?", (session_id,)).fetchone()
    return json.loads(row[0]) if row else None

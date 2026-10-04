"""Shared SQLite for Phase 2 records (users, properties, commitments, bills, impact). Path: APP_DB, default <repo>/data/app.sqlite."""

import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.environ.get("APP_DB") or Path(__file__).resolve().parents[2] / "data" / "app.sqlite")


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

# STUB: P2-04's version replaces this at merge
"""Saved /estimate bodies by session_id (in memory). P2-04 owns the real one."""

_SESSIONS: dict[str, dict] = {}


def save(body: dict) -> None:
    _SESSIONS[body["session_id"]] = body


def get(session_id: str) -> dict | None:
    return _SESSIONS.get(session_id)

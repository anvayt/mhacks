# STUB: P2-04's version replaces this at merge
"""Session store: the latest PLAN.md §10 estimate body per session_id, plus "answers" and "model_params"."""

_SESSIONS: dict[str, dict] = {}


def save(body: dict) -> None:
    _SESSIONS[body["session_id"]] = body


def get(session_id: str) -> dict | None:
    return _SESSIONS.get(session_id)

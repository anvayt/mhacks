# STUB: ACCOUNTS agent's version replaces this at merge
"""Stub of the shared accounts interface (users, properties, auth). get_property reads PROPERTIES, which tests fill."""

PROPERTIES: dict[str, dict] = {}  # property_id -> Property shape (Appendix A) + session_id


def normalize_handle(raw: str) -> str:
    return raw


def get_user(user_id: str) -> dict | None:
    return None


def list_users() -> list[dict]:
    return []


def get_property(property_id: str) -> dict | None:
    return PROPERTIES.get(property_id)


def current_property(user_id: str) -> dict | None:
    return None


def update_reminder_prefs(user_id: str, prefs: dict) -> dict:
    return {}


def authorize(request, user_id: str) -> None:
    return None

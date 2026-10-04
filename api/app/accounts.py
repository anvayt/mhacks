# STUB: accounts agent's version replaces this at merge


def normalize_handle(raw: str) -> str:
    return None


def get_user(user_id: str) -> dict | None:
    return None


def list_users() -> list[dict]:
    return []


def get_property(property_id: str) -> dict | None:
    return None


def current_property(user_id: str) -> dict | None:
    return None


def update_reminder_prefs(user_id: str, prefs: dict) -> dict:
    return {}


def authorize(request, user_id: str) -> None:
    return None

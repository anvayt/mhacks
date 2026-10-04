# STUB: accounts agent's version replaces this at merge
USERS = {}
PROPERTIES = {}


def normalize_handle(raw: str) -> str:
    return ""


def get_user(user_id: str) -> dict | None:
    return USERS.get(user_id)


def list_users() -> list[dict]:
    return list(USERS.values())


def get_property(property_id: str) -> dict | None:
    return PROPERTIES.get(property_id)


def current_property(user_id: str) -> dict | None:
    user = get_user(user_id)
    return get_property(user["current_property_id"]) if user and user.get("current_property_id") else None


def update_reminder_prefs(user_id: str, prefs: dict) -> dict:
    return {}


def authorize(request, user_id: str) -> None:
    return None

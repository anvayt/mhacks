# STUB: commitments agent's version replaces this at merge
CATALOG: dict[str, dict] = {}
COMMITMENTS = []
PROJECTIONS = {}


def list_commitments(property_id: str | None = None, user_id: str | None = None) -> list[dict]:
    return [c for c in COMMITMENTS if (property_id is None or c.get("property_id") == property_id)
            and (user_id is None or c.get("user_id") == user_id)]


def latest_projection(property_id: str) -> dict | None:
    return PROJECTIONS.get(property_id)

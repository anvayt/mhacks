# STUB: bills agent's version replaces this at merge
SNAPSHOTS = []
BILLS = []
IMPACT = []


def record_snapshot(property_id: str, source: str, body: dict) -> dict:
    return {}


def list_snapshots(property_id: str) -> list[dict]:
    return [s for s in SNAPSHOTS if s.get("property_id") == property_id]


def list_bills(property_id: str) -> list[dict]:
    return [b for b in BILLS if b.get("property_id") == property_id]


def list_impact(property_id: str) -> list[dict]:
    return [i for i in IMPACT if i.get("property_id") == property_id]

"""Explicitly synthetic board data. Run with DEMO_SEED=1; never writes real users or impact."""

import json
import os
import sys
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import db


def seed() -> int:
    if os.environ.get("DEMO_SEED") != "1":
        raise SystemExit("Set DEMO_SEED=1 to create explicitly labelled demo board entries.")
    with closing(db.connect()) as con, con:
        con.execute("CREATE TABLE IF NOT EXISTS board_demo_entries (id TEXT PRIMARY KEY, body TEXT NOT NULL)")
        for i, alias in enumerate(("Maple", "Oak", "Elm", "Pine", "Birch", "Cedar"), 1):
            row = {"alias": "Demo " + alias, "home": ["demo", str(i)], "tract": "26161400400",
                   "co2_kg_avoided": i * 20, "baseline_co2_kg_yr": 2000,
                   "streak_months": i, "accepted": 4, "verified": 1 + i % 3, "verified_impact_count": 1, "demo": True}
            con.execute("INSERT OR REPLACE INTO board_demo_entries (id, body) VALUES (?, ?)",
                        (f"demo-{i}", json.dumps(row)))
    return 6


if __name__ == "__main__":
    print(f"Seeded {seed()} synthetic Demo aliases. They are visible only while DEMO_SEED=1.")

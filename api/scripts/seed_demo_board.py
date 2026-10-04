"""Explicitly demo board data. Run with DEMO_SEED=1; never writes real users or impact.

The 10 competitors come from api/data/demo_competitors.json (built by scripts/build_demo_competitors.py): each is
based on a real Ann Arbor home from a public Zillow listing URL, placed on its city footprint and scored by our model.
Their behavior (streaks, commitments, CO2 avoided) is synthetic. Boards show only the "Demo …" alias and tract.
"""

import json
import os
import sys
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import db

COMPETITORS = Path(__file__).resolve().parents[1] / "data" / "demo_competitors.json"
# The fields boards.py reads; "basis" (address, listing URL) stays in the data file and is never stored or shown.
FIELDS = ("alias", "home", "tract", "co2_kg_avoided", "baseline_co2_kg_yr", "streak_months", "accepted", "verified",
          "verified_impact_count", "demo", "named", "habit_streak", "habit_best")


def seed() -> int:
    if os.environ.get("DEMO_SEED") != "1":
        raise SystemExit("Set DEMO_SEED=1 to create explicitly labelled demo board entries.")
    competitors = json.loads(COMPETITORS.read_text())["competitors"]
    with closing(db.connect()) as con, con:
        con.execute("CREATE TABLE IF NOT EXISTS board_demo_entries (id TEXT PRIMARY KEY, body TEXT NOT NULL)")
        con.execute("DELETE FROM board_demo_entries")  # replaces any older placeholder rows
        for i, c in enumerate(competitors, 1):
            row = {k: c[k] for k in FIELDS} | {"demo": True}
            con.execute("INSERT OR REPLACE INTO board_demo_entries (id, body) VALUES (?, ?)",
                        (f"demo-{i}", json.dumps(row)))
    return len(competitors)


if __name__ == "__main__":
    print(f"Seeded {seed()} Demo competitors (real Ann Arbor homes, synthetic behavior). Visible only while DEMO_SEED=1.")

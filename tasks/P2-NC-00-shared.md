# P2 Phase 2 (NEW_CHANGES.md): shared rules for every P2 NC agent

Six agents build P2's Phase 2 slices in parallel, one branch each, then one merge into `dev`.
Read this file, then `NEW_CHANGES.md` §1, §5–§11 and Appendix A (shapes). Where this file differs from NEW_CHANGES.md, this file wins.

| Slice | Owner | Branch | Module | Live-check API port |
|---|---|---|---|---|
| NC-01/02/07 accounts, Photon phone login, properties, history, check-in trigger | Claude | `p2/accounts` | `app/accounts.py` | 8015 |
| NC-03/04 commitments + `/projection` | Claude | `p2/commitments` | `app/commitments.py` | 8016 |
| NC-05 bills, verification, impact, snapshots | Astra | `p2/bills-impact` | `app/bills.py` (+ `app/calibrate.py`) | 8021 |
| NC-06 leaderboards (boards, ghost marker, neighborhood totals) | Astra | `p2/boards` | `app/boards.py` (+ `/leaderboard` in `app/city.py`) | 8022 |
| NC-08 Google Calendar | Astra | `p2/calendar` | `app/gcal.py` | 8023 |
| Reminders and messaging policy (D4, §9.6), server side | Astra | `p2/reminders` | `app/reminders.py` | 8024 |

## Team decisions (Oct 4, ~2:40 AM)
1. **The phone number is the login.** iMessage handle = account. The web signs in by texting `login <code>` from the user's own Messages app. `/api` allowlists the number with Photon and returns Photon's redirect link with the code pre-filled. The inbound text is the verification. No passwords, and we never text first.
2. **Commitments the model can't price yet are placeholders:** no $/CO₂/grade numbers, `pending_model: true`, until P1's effect model lands (NEW_CHANGES P1 NC-01).
3. SQLite (D10). Manual check-in trigger for the demo (D9). Google Calendar is in scope (NC-08).

## Rules
- Branch off `origin/dev`; push your branch. Never merge into `dev`, push to `main`, or edit `/model`, `/web`, `/agent`, `notes/` or `tasks/`.
- P1's model server is at `http://localhost:8001` (`MODEL_BASE_URL`). Never start, stop or rebuild it, never run `make -C model stop`, and keep ≤4 concurrent calls (use `app/estimate.py`'s helpers: `session_params`, `_hc_ac`, the shared cap).
- Endpoints go in your own module with an `APIRouter`. In `app/main.py`, add only the import and the `include_router` line.
- Errors: `HTTPException(status, {"code", "message"})`. Messages are written for renters (the agent texts them verbatim).
- Mask phone numbers in logs and responses (`•••-•••-1234`). No secrets in code, logs or commits; keys come from env (names go in the root `.env.example`).
- Simplest code that works, matching the surrounding style. `cd api && uv run pytest -q` must pass. Live-check against :8001 on your port.
- Final report: branch + head commit, files, every endpoint with an example request/response, stubs created, what the merge must wire, and what P3 (`/web`) and P4 (`/agent`) must do.

## Shared file `app/db.py`
If it doesn't exist on your branch, create it with exactly this text (identical everywhere, so the merge is clean). Each module creates its own tables with `CREATE TABLE IF NOT EXISTS` and never alters another module's tables.

```python
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
```

## Shared interfaces (exact signatures; the owner implements, everyone else imports)
- `app/accounts.py` (accounts):
  - `normalize_handle(raw: str) -> str`
  - `get_user(user_id: str) -> dict | None`: User shape (Appendix A) plus `created_at`
  - `list_users() -> list[dict]`
  - `get_property(property_id: str) -> dict | None`: Property shape plus `session_id`, the `/estimate` session holding its current estimate
  - `current_property(user_id: str) -> dict | None`
  - `update_reminder_prefs(user_id: str, prefs: dict) -> dict`
  - `authorize(request, user_id: str) -> None`: raises 401/403 unless the request carries `X-Agent-Key` (env `AGENT_API_KEY`) or a web bearer token for that user
- `app/commitments.py` (commitments):
  - `CATALOG: dict[str, dict]`
  - `list_commitments(property_id: str | None = None, user_id: str | None = None) -> list[dict]`: Commitment shape
  - `latest_projection(property_id: str) -> dict | None`: Projection shape, including `projected.score` and `projected.percentile_city`
- `app/bills.py` (bills):
  - `record_snapshot(property_id: str, source: str, body: dict) -> dict`: ScoreSnapshot
  - `list_snapshots(property_id: str) -> list[dict]`
  - `list_bills(property_id: str) -> list[dict]`
  - `list_impact(property_id: str) -> list[dict]`: ImpactRecord

If you import one of these and the file doesn't exist on your branch, create a stub with exactly those signatures. Make its first line `# STUB: <owner> agent's version replaces this at merge`, and have it return None, [] or {} (`authorize`: allow everything). An in-memory map your tests fill is fine.

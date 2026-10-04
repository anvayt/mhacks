```yaml
id: P2-05
title: /calibrate, /fixes, /compare + badge rules
owner: P2
status: done
branch: p2/calibrate-fixes-compare
type: build
checkpoint: 5:00 AM checkpoint
depends_on: [P2-04]
blocks: [P3, P4]
merges: []
services_touched:
  - /api
services_read:
  - /model (calibration fit, fix simulator)
  - Green Rental Housing checklist (PLAN.md §4)
contract_change: none
```

## Goal
The after-move-in and comparison endpoints in the §10 shapes, plus the badge rules from PLAN.md §5 as simple functions on API fields.

## Done when
- [x] Each endpoint returns its §10 shape from real computations; badges appear in `/estimate`, `/answer`, `/calibrate`

## Handoff (Oct 4, ~3 AM; merged into `dev` at `fd8c31c` via `p2/merge-wave2`)
- **What changed:** `api/app/calibrate.py` `POST /calibrate` (Grok vision via `XAI_API_KEY`/`XAI_VISION_MODEL`, two reads that must agree + evidence fields + a gas plausibility cap; or typed `{therms, kwh, start, end}`) → P1 `/hc/bill_check`, pct in percent, streak in SQLite (`CALIBRATE_DB`). `api/app/fixes.py` `GET /fixes/{session_id}` (GRH checklist points, cited costs/rebates, model-priced savings; unpriced fixes null). `api/app/compare.py` `POST /compare` (`confident` when ranges don't overlap). `api/app/badges.py` `badges(est, *, calibration, used_fixes, previous_grade)` + `BADGES`; used by `/estimate`, `/answer`, `/calibrate`, `/compare` (battle-winner). `/fixes` saves `used_fixes` on the session (leak-hunter). Also `api/app/forecast.py` `GET /forecast/{session_id}` (7-day $ vs typical, alerts for P4 reminders).
- **How to run:** `cd api && uv sync && uv run python scripts/fetch_footprints.py` (once), P1's model on :8001 (`make -C model dashboard`), `uv run uvicorn app.main:app --port 8000`; tests `uv run pytest -q` (377 pass). Live xAI test: `uv run --env-file ../.env pytest -q tests/test_calibrate.py`.
- **Gaps:** gas → heat pump unpriced (P1 request a); calibrate is gas only and P1's noise floor makes `meaningful` mostly false (P1 request c); badges are recomputed per response, so grade-jumper shows only on the answer that raised the grade.
- **Next:** P4 makes `Fix` fields nullable and adds a $ floor for `costly_week` (requests.md).

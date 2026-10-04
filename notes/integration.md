# Hidden Rent: integrated version on dev (`4602d55`)

Merged Oct 4, 12:07 AM from `p2/integration` (`9c02b5d`). It is the 10:30 PM checkpoint work from P1 to P4 plus thin glue, verified end to end from a clean clone. Every new task branches off `dev` from here.

## What's in it
- **/model (P1)**: P1-02..P1-07 heating + cooling (ResStock, PRISM/ERA5, Ann Arbor meters, change-point and building models, a 591-building table) plus monthly `months[]`, and P1-09 air leakage (merged with status: review, not used by /api yet). Served by `model.heating_cooling.server` on :8001 (`/hc/estimate`, `/hc/weather`, `/hc/bill_check`, `/hc/buildings`, `/dashboard`).
- **/api (P2)**: P2-01 address -> features, P2-02/02b listing and map link parsing, and `POST /estimate` in the PLAN §10 shape (`api/app/estimate.py`).
- **/agent (P4)**: P4-01 Spectrum iMessage agent plus the onboarding page (:8787) and add/remove-user scripts. Links and addresses now go to the real `/estimate`.
- **/web (P3)**: the landing screen. The form POSTs to `/estimate` and shows a one-line placeholder; the iMessage link opens the onboarding page.

## How the pieces connect
`web form / agent text` -> `POST :8000/estimate {url|address, unit_sqft?}` -> `resolve_link` (short links expanded, never auto-geocodes a hint) -> `get_features` (Census geocoder + city footprints + ACS) -> `GET :8001/hc/estimate?lat,lon(point inside the footprint),unit_sqft,building_type,block_group` -> response.
- /api reaches /model over HTTP (`MODEL_BASE_URL`). The agent uses `API_BASE_URL` and the web uses `NEXT_PUBLIC_API_BASE_URL`; /api's CORS allows `WEB_ORIGINS`. Every env name is in the root `.env.example`.
- `/estimate`.heating_cooling is byte-identical to calling `estimate_hc` directly with the same inputs (verified on all 3 model paths).

## Run it (repo root; see README "Run the whole thing")
1. `brew install libomp` (macOS). Then `make -C model setup && make -C model build && make -C model leakage`. Cold, this takes about an hour of downloads. PRISM serves each grid only twice a day per IP, so copy `model/data/raw/prism/` from a teammate. Warm, it takes about 5 min. The build rewrites ~17 tracked files under model/data/processed and model/results: don't commit them, and keep them together with model/artifacts/*.pkl.
2. `cd api && uv sync && uv run python scripts/fetch_footprints.py`; `cd agent && npm ci && cp .env.example .env`; `cd web && npm ci`.
3. Start in this order: `make -C model dashboard` (:8001); `cd api && uv run uvicorn app.main:app --port 8000`; `cd web && npm run dev` (:3000); `cd agent && npm run onboard` (:8787, mock without creds); `cd agent && npm run agent` (iMessage with creds; with no creds or `AGENT_TERMINAL=1` it runs the terminal chat, which downloads the tuichat binary).
4. Tests: `make -C model test` (14); `(cd api && uv run pytest -q)` (170 + 1 opt-in skip, with the model up); `(cd agent && npm test && npm run typecheck)` (17); `(cd web && npm run build)`.
5. Try it: `curl -s localhost:8000/estimate -H 'content-type: application/json' -d '{"address":"2200 Fuller Ct, Ann Arbor, MI 48105"}'`.

## Real vs not yet
- **Real**: building (lat/lon, footprint, unit sqft, year built, ResStock type, address), bill annual/seasonal/monthly **p50** for **heating + cooling only**, heating_cooling (P1's full answer with method, accuracy, weather, prices), the agent reply numbers, and the web placeholder line.
- **Null/empty**: session_id, p10/p90, co2_t, score, grade, grade_span, percentiles, hidden_rent_usd_mo, badges, questions (locked=false).
- **Not served**: /answer, /compare, /calibrate, /fixes, /leaderboard, /city, /session.
- **Mock switches** (unchanged): agent `USE_MOCKS` (Photon user API only) and `AGENT_TERMINAL`. The agent never invents numbers; if the API is down it sends a "try again" text.
- **Errors**: 422 `{detail:{code,message}}` with missing_input, needs_address (+hint), not_found, not_a_home, bad_unit_sqft; 503 model_unavailable / lookup_unavailable.

## Known gaps per owner
- **P1**: the cold build is fragile (PRISM per-IP limit; a failed fetch is silently skipped) and the retrain isn't reproducible (3.14 vs 3.12, different chosen model). No signed held-out quantiles for p10/p90. No year_built override; fuel comes from the block-group majority. Two metered buildings show $0 heating. `make stop` kills every model server on the machine. P1-09 still in review. Keep the block_group and NaN edits.
- **P2**: P2-04 (sessions, /answer, score/grade/percentile/hidden rent, questions, bands), P2-03 CO2, /calibrate, /fixes, /compare, /leaderboard, /city, P2-07 fixtures. P2-01 lets Office footprints through as homes with huge unit sizes (e.g. 2500 Packard St 32,959 sq ft) and counts garages in SFA/2-4 unit areas. Some big complexes are not found (1780 Broadway St). year_built is a block-group median. Record this integration in tasks/notes on main.
- **P3**: report card, error and loading states (show the needs_address hint), map, battle, fix simulator, share card, tests; work on a p3/* branch.
- **P4**: P4-02 interview loop. Reword the reply's accuracy and year-built claims using accuracy.basis and year_built_source. Public onboarding URL. A real-phone run of the /api-backed replies.

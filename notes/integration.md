# Hidden Rent: how the integrated demo runs

Wave 7 is on `dev` at `de8ccdbe014dea2f421b5582c72bd9d3bb3e9e64` (October 4, 2026). Code runs from `dev`; coordination and submission drafts stay on `main`. The final check table and complete terminal conversation are in [WAVE7_VERIFICATION.md](../docs/WAVE7_VERIFICATION.md). The midnight snapshot is retained below as history.

## What is integrated

- P1's existing heating/cooling model serves `:8001`. The API calls it over HTTP. Its built artifacts and matching processed data stay in P1's checkout; this integration never started, stopped, restarted or rebuilt that server.
- P2 serves estimates/answers, sessions and saved homes, map/city data, comparisons, bills, commitments/projections, boards, reminders and optional Calendar. `/city` includes 35,007 footprints, of which 25,704 are scored.
- P3's live web flow covers lookup, unit size, questions, report, phone-code sign-in, peer bars and a separate projected marker, monthly bills, map, comparison and share card. `NEXT_PUBLIC_USE_MOCKS=0` is the real-data default.
- P4's agent uses the real Phase 2 API and sends `X-Agent-Key` on every request when configured. Terminal mode never initializes Photon and sends no iMessages.
- Public guards, `/health`, warm/check tooling, the reviewed web smoke harness and backup-video scripts are integrated. The launcher builds and runs the production web (`npm run build` then `npm run start`).

Merged branches: `p2/public-demo` (`b369a65`), `p3/int-flow` (`5ffd90a`), reviewed `p3/int-board` (`d1f3054`), reviewed `p3/int-map-compare` (`17fd15f`), `p4/phase2-real` (`d9a7442`), and `demo/backup-video` (`4e3b134`). W2/W3's reviewed heads merged cleanly. W2 consumes the estimate returned by W1's `ListingForm` and adopts that session on a move, avoiding a second `/estimate`; each option toggle makes one projection request. W3 adds saved-session comparisons, explicit per-listing errors and user-safe API failure text. Integration keeps all API routers, the shared browser client, combined env examples and `web/app/css-custom-properties.d.ts`; the duplicate map CSS declaration is removed.

## Start order

1. Reuse P1's already-running `http://localhost:8001` model. Read-only `GET /hc/answers` checks availability. Do not rebuild or restart it during rehearsal, and never run `make -C model stop`.
2. Start API `:8000`, then build/start web `:3000`, onboarding `:8787`, and the agent. Use `AGENT_TERMINAL=1` for rehearsal; real phone delivery is a separate operator step.
3. Run `API_BASE_URL=http://localhost:8000 make demo-warm`. This warms all five estimates, each map, one forecast per weather cell and `/city`, and preserves response/timing logs.
4. For a public run, follow README's “Run the demo publicly.” A working tunnel network, real phone-auth configuration and the onboarding abuse-cap follow-up are required. Reprint the onboarding `/card` whenever a temporary tunnel URL changes.

Load keys only with `uv run --env-file /Users/anvaytodkar/Code/mhacks/.env`; never print them. Dependencies and city cache must already be installed (`uv sync`, `npm ci`, `scripts/fetch_footprints.py`, as documented in README). Root `.env.example` and `agent/.env.example` list the variable names.

Example manual rehearsal in separate terminals, from the merged checkout (all processes except the model are yours):

```bash
# API; the existing model stays on :8001.
(cd api && MODEL_BASE_URL=http://localhost:8001 WEB_ORIGINS=http://localhost:3000 \
  uv run --env-file /Users/anvaytodkar/Code/mhacks/.env \
  uvicorn app.main:app --host 127.0.0.1 --port 8000)

# Web: compile the public URLs into the production build, then serve it.
(cd web && NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 \
  NEXT_PUBLIC_ONBOARD_URL=http://localhost:8787 NEXT_PUBLIC_USE_MOCKS=0 npm run build && \
  npm run start -- --hostname 127.0.0.1 --port 3000)

# Onboarding, then terminal agent; private env is loaded without printing it.
(cd agent && uv run --project ../api --env-file /Users/anvaytodkar/Code/mhacks/.env npm run onboard)
(cd agent && AGENT_TERMINAL=1 API_BASE_URL=http://localhost:8000 \
  uv run --project ../api --env-file /Users/anvaytodkar/Code/mhacks/.env npm run agent)
```

`make demo` is the supervised alternative after P1's server is healthy; it may start a missing model, so it was not used during the protected wave 7 integration. `make demo-public` never restarts the model/agent. `make demo-check` starts separate isolated check processes and is an offline simulation, not a universal offline guarantee; it was not run as part of wave 7's protected-model checks.

## Environment and safety boundaries

| Setting | Role |
|---|---|
| `MODEL_BASE_URL` | API → existing model; `http://localhost:8001`. |
| `API_BASE_URL` | Agent/scripts → API. |
| `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_ONBOARD_URL` | Public browser destinations. Never place secrets in `NEXT_PUBLIC_*`. |
| `WEB_ORIGINS`, `WEB_ORIGIN` | API CORS allowlist and Calendar return destination. |
| `AGENT_API_KEY` | Shared server/agent secret sent as `X-Agent-Key` on all agent API calls; never sent by the browser. |
| `RATE_LIMIT_PER_MIN` | Public expensive-request budget; default **120 per IP per minute**. |
| `SESSIONS_DB`, `APP_DB`, `CALIBRATE_DB` | Session, Phase 2 and bill-month/streak SQLite paths. The spelling is `CALIBRATE_DB`. |
| `USE_MOCKS=1` | Mock phone onboarding/auth for rehearsal; estimates still use the real model. |
| `AGENT_TERMINAL=1`, `USE_MOCK_API=0` | Real API terminal conversation, no iMessages. |
| `XAI_API_KEY`, `XAI_VISION_MODEL` | Optional bill-photo reader; typed therms/ccf/amount work without it. |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`, `CALENDAR_STATE_SECRET` | Optional real Calendar OAuth; missing client credentials yield labeled mock Calendar. |
| `REMINDER_RECEIPTS` | Durable reminder-send receipt file; run one sender process. |

Wave 7 used only API **8060** and production web **3006**, with scratch `SESSIONS_DB`/`APP_DB`/`CALIBRATE_DB`, mock phone onboarding and the existing real model on 8001. Test setup keys were loaded through `uv run --env-file`; no key was printed or put in browser requests.

Only a constant-time match to a **nonempty** agent key bypasses rate limits. Read-only suggestions and plain position requests are exempt; a position request containing `catalog_ids` is counted because it can run a what-if. The separate photo cap stays **three per IP per ten minutes**. The streamed body cap is **8 MiB base64 photo plus 64 KiB JSON overhead** and applies to agent calls too. These are single-process operational limits, not model thresholds or a distributed production defense. `/health` returns API liveness and model availability separately.

## Five addresses and demo beats

The canonical list is `demo/addresses.txt`; detailed captured payloads are in `demo/DEMO_PICKS.md`. Live returned numbers take priority over older captures.

| Address (Ann Arbor, MI) | Beat | Reference |
|---|---|---|
| 2322 Arrowwood Trl | Lock in the grade | A–B → Central AC → B; annual band about $435/$470/$505. The illustrative answer is not an inspection. |
| 624 Church St | Listing battle, lower predicted bill | $265/year against Forest below. |
| 1022 S Forest Ave | Listing battle and F city example | $2,179/year; captured gap $1,914/year. Same type and similar inferred unit sizes; heating/cooling only. |
| 615 S Main St (The Yard) | City top 2% and public meter evidence | A, scored-table 99.764151, footprint 50892, about $143/year; publicly benchmarked name. |
| 1514 Morton Ave | Questions → windows → monthly return | Gas, skip AC, single-pane: C/45, $2,185/year. Windows project C/56, $125/year and 699 kg CO₂/year less, 4 GRH points; current stays fixed. |

For Morton's bill beat, explicitly say **hypothetical 120 therms, February 1–28, 2026**. The final terminal run returned 66% below expected for that weather, inside the approximately 118% error, streak one and an unverified early signal; current stayed C. Default typed bills use the last full month, so give February's dates when reproducing this demonstration. “Done” is reported completion, not verified impact.

A locked grade means the API has one reachable grade **or no remaining eligible question to ask**. Skipped or ineffective questions can leave a wider grade span when locked. Neither a lock nor a narrow answer-driven span removes the model-error dollar range.

## Verification and known limits

API **616 passed, 2 skipped**; agent **70 passed** and typecheck passed; `npm ci` and production web build passed; final Phase 2 check **16/16**. Final full browser smoke result: **433 passed, 0 warnings, 0 failures; 0 HTTP 429s; 37 guarded browser requests, peak 25/minute**. The first complete browser run had 350 passing assertions, nine legacy warnings, zero failures and zero 429s; its 37 guarded browser requests peaked at 22/minute. The final harness repeat supersedes its assertion count. See [full verification and exact terminal transcript](../docs/WAVE7_VERIFICATION.md).

- Heating/cooling only; relative predicted grades are not official GRH inspection scores. Public-record year/fuel/size can be inferred. Real-meter validation on larger buildings does not establish the same accuracy for small rentals; cooling is less validated. P1 still owns final running-artifact/result sign-off.
- P1 look-alikes remain empty; unsupported fixes remain tips without numbers. Metered homes currently have no priced commitment effects. The session-preserving “Continue in iMessage” web link is still open in requests.md.
- Bill noise is about 92–118% in tested cases. Provisional bill signals are clamped and never replace current grade. Verification requires same-home, full post-completion billing evidence beyond model noise; gas only. Verified boards may honestly be empty.
- After a meaningful bill regrade, projections still use the old session baseline; web/agent withhold the stale what-if. Saved heat-included homes can have mismatched bill/rank bases; W2 explains and withholds that rank instead of inventing a correction.
- Real Calendar needs human OAuth setup. Durable event-create idempotency and `Commitment.calendar_event_id` wiring remain incomplete. Unknown reminder delivery after a crash fails closed; inspect receipts instead of blindly resending.
- Locked web dependencies still carry npm audit findings: **MapLibre critical, Next.js moderate, PostCSS high**. The map uses `setText` for address popups, not `setHTML`; this does not prove the dependencies are safe. No broad major-version upgrade was attempted at freeze. Track and patch these before unrestricted production deployment.
- The prior public tunnel attempt ended in Cloudflare edge timeouts/HTTP 530, so no working judge URL is claimed. Onboarding `/join` still needs its public abuse cap. Real-phone Phase 2, a genuine consenting bill-photo run and the final playable video are not established by terminal/browser checks.
- Warm caches are not a universal offline service. Forecast may use last-good data with `stale_as_of` if at least three future days remain; fresh GIS/weather data, map assets, tunnels and message transport can still need the network.

## Historical midnight integration snapshot

The following is retained for provenance. Its missing-feature lists and test counts describe `4602d55`, not wave 7.

## Hidden Rent: integrated version on dev (`4602d55`)

Merged Oct 4, 12:07 AM from `p2/integration` (`9c02b5d`). It is the 10:30 PM checkpoint work from P1 to P4 plus thin glue, verified end to end from a clean clone. Every new task branches off `dev` from here.

### What's in it
- **/model (P1)**: P1-02..P1-07 heating + cooling (ResStock, PRISM/ERA5, Ann Arbor meters, change-point and building models, a 591-building table) plus monthly `months[]`, and P1-09 air leakage (merged with status: review, not used by /api yet). Served by `model.heating_cooling.server` on :8001 (`/hc/estimate`, `/hc/weather`, `/hc/bill_check`, `/hc/buildings`, `/dashboard`).
- **/api (P2)**: P2-01 address -> features, P2-02/02b listing and map link parsing, and `POST /estimate` in the PLAN §10 shape (`api/app/estimate.py`).
- **/agent (P4)**: P4-01 Spectrum iMessage agent plus the onboarding page (:8787) and add/remove-user scripts. Links and addresses now go to the real `/estimate`.
- **/web (P3)**: the landing screen. The form POSTs to `/estimate` and shows a one-line placeholder; the iMessage link opens the onboarding page.

### How the pieces connect
`web form / agent text` -> `POST :8000/estimate {url|address, unit_sqft?}` -> `resolve_link` (short links expanded, never auto-geocodes a hint) -> `get_features` (Census geocoder + city footprints + ACS) -> `GET :8001/hc/estimate?lat,lon(point inside the footprint),unit_sqft,building_type,block_group` -> response.
- /api reaches /model over HTTP (`MODEL_BASE_URL`). The agent uses `API_BASE_URL` and the web uses `NEXT_PUBLIC_API_BASE_URL`; /api's CORS allows `WEB_ORIGINS`. Every env name is in the root `.env.example`.
- `/estimate`.heating_cooling is byte-identical to calling `estimate_hc` directly with the same inputs (verified on all 3 model paths).

### Run it (repo root; see README "Run the whole thing")
1. `brew install libomp` (macOS). Then `make -C model setup && make -C model build && make -C model leakage`. Cold, this takes about an hour of downloads. PRISM serves each grid only twice a day per IP, so copy `model/data/raw/prism/` from a teammate. Warm, it takes about 5 min. The build rewrites ~17 tracked files under model/data/processed and model/results: don't commit them, and keep them together with model/artifacts/*.pkl.
2. `cd api && uv sync && uv run python scripts/fetch_footprints.py`; `cd agent && npm ci && cp .env.example .env`; `cd web && npm ci`.
3. Start in this order: `make -C model dashboard` (:8001); `cd api && uv run uvicorn app.main:app --port 8000`; `cd web && npm run dev` (:3000); `cd agent && npm run onboard` (:8787, mock without creds); `cd agent && npm run agent` (iMessage with creds; with no creds or `AGENT_TERMINAL=1` it runs the terminal chat, which downloads the tuichat binary).
4. Tests: `make -C model test` (14); `(cd api && uv run pytest -q)` (170 + 1 opt-in skip, with the model up); `(cd agent && npm test && npm run typecheck)` (17); `(cd web && npm run build)`.
5. Try it: `curl -s localhost:8000/estimate -H 'content-type: application/json' -d '{"address":"2200 Fuller Ct, Ann Arbor, MI 48105"}'`.

### Real vs not yet
- **Real**: building (lat/lon, footprint, unit sqft, year built, ResStock type, address), bill annual/seasonal/monthly **p50** for **heating + cooling only**, heating_cooling (P1's full answer with method, accuracy, weather, prices), the agent reply numbers, and the web placeholder line.
- **Null/empty**: session_id, p10/p90, co2_t, score, grade, grade_span, percentiles, hidden_rent_usd_mo, badges, questions (locked=false).
- **Not served**: /answer, /compare, /calibrate, /fixes, /leaderboard, /city, /session.
- **Mock switches** (unchanged): agent `USE_MOCKS` (Photon user API only) and `AGENT_TERMINAL`. The agent never invents numbers; if the API is down it sends a "try again" text.
- **Errors**: 422 `{detail:{code,message}}` with missing_input, needs_address (+hint), not_found, not_a_home, bad_unit_sqft; 503 model_unavailable / lookup_unavailable.

### Known gaps per owner
- **P1**: the cold build is fragile (PRISM per-IP limit; a failed fetch is silently skipped) and the retrain isn't reproducible (3.14 vs 3.12, different chosen model). No signed held-out quantiles for p10/p90. No year_built override; fuel comes from the block-group majority. Two metered buildings show $0 heating. `make stop` kills every model server on the machine. P1-09 still in review. Keep the block_group and NaN edits.
- **P2**: P2-04 (sessions, /answer, score/grade/percentile/hidden rent, questions, bands), P2-03 CO2, /calibrate, /fixes, /compare, /leaderboard, /city, P2-07 fixtures. P2-01 lets Office footprints through as homes with huge unit sizes (e.g. 2500 Packard St 32,959 sq ft) and counts garages in SFA/2-4 unit areas. Some big complexes are not found (1780 Broadway St). year_built is a block-group median. Record this integration in tasks/notes on main.
- **P3**: report card, error and loading states (show the needs_address hint), map, battle, fix simulator, share card, tests; work on a p3/* branch.
- **P4**: P4-02 interview loop. Reword the reply's accuracy and year-built claims using accuracy.basis and year_built_source. Public onboarding URL. A real-phone run of the /api-backed replies.

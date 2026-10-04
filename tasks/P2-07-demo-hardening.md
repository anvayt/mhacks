```yaml
id: P2-07
title: Demo hardening: caching + offline demo listings
owner: P2
status: done
branch: p2/demo-hardening
type: build
checkpoint: 8:00 AM FEATURE FREEZE
depends_on: [P2-04, P2-05, P2-06]
blocks: []
merges: []
services_touched:
  - /api
services_read: []
contract_change: none
```

## Goal
The demo must never depend on a live external API: cache geocoder/footprint/census results and precompute 5 demo listings so the whole flow works with Wi-Fi off.

## Also
- Geocoder fallback: when the Census geocoder moves an address (e.g. Ashley Mews → S Ashley St, ~450 m) and the 250 m city-point guard rejects it, fall back to the city's own mailing-address point for that street line.

## Done when
- [x] With outbound network blocked, all 5 demo listings return full /estimate responses and /forecast passes (`make demo-check`, Oct 4 ~4:30 AM). Other endpoints: see Handoff.

## Handoff (Oct 4, ~4:30 AM; merged into `dev` at `26b1541` via `p2/merge-wave4`)
- **What changed:** root `Makefile` + `scripts/demo*.sh` (`p2/demo-hardening`): `make demo` (start the stack), `make demo-warm` (run each demo address through `/estimate` and one `/forecast` per weather cell, filling every disk cache), `make demo-check` (its own API :18000 + model :18001 with a socket-level outbound guard; lists every external host still attempted). `api/app/forecast.py` (`p2/offline-fallbacks`): saves the last good Open-Meteo forecast per grid cell (`data/openmeteo_forecast_<lat>_<lon>.json`) and serves it with `stale_as_of` when the live fetch fails (≥ 3 future days required); its model call now goes through `_hc_ac` (No AC rule, 4-call cap). Geocoder fallback to the city's own mailing-address point: `p2/lookup-fixes` (`city_address` in `app/geo/footprints.py`). `demo/DEMO_PICKS.md` + `demo/picks/*.json` (`p2/demo-picks`): captured live evidence per pitch beat. `demo/addresses.txt` = the final five, in rehearsal order:
  1. 2322 Arrowwood Trl (grade lock): B 73, span A–B, $470/yr p50, metered; one "Central AC" answer locks B.
  2. 624 Church St, ArborBlu (battle winner): A 97, locked, $265/yr, metered.
  3. 1022 S Forest Ave (battle comparator + F map example): F 4, span A–F, $2,179/yr.
  4. 615 S Main St, The Yard (top-2% map + public leaderboard + real meters): A 100, locked, $143/yr, metered.
  5. 1514 Morton Ave (typed bill calibration + a priced fix): C 50, span B–F, $2,117/yr; gas + single-pane scenario prices windows.
- **Results (Oct 4, ~4:30 AM):** `make demo-warm` against :8014: 5/5 estimates + forecast pass. `make demo-check`: 5/5 estimates + forecast pass with outbound blocked; the only host attempted was `api.open-meteo.com` (1 attempt, blocked), and the forecast came from the last-good cache (`stale_as_of` 2026-10-04T06:32Z). The model process attempted none.
- **How to run:** `cd api && uv sync && uv run python scripts/fetch_footprints.py` (once); P1's model on :8001; `make demo` or the API alone; then `API_BASE_URL=<api> make demo-warm` before going offline; `MODEL_DIR=<built model checkout> make demo-check` to prove it (uses :18000/:18001 only).
- **Gaps:** demo-check covers /estimate and /forecast only. /answer, /session, /fixes, /compare, /city, /leaderboard make no external calls (model + local data). /map needs TIGERweb once per block group (cached on disk after), so open each demo session's map once while online. /calibrate with a photo needs xAI (typed numbers work offline). A last-good forecast older than ~4 days fails (needs 3 future days), so re-run `make demo-warm` the morning of the demo. Browser assets, Photon and tunnels aren't covered.
- **Next:** none blocking. P4 can use the five sessions from `demo-warm` logs for rehearsal.

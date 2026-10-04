# Hidden Rent API (`/api`)

FastAPI backend. Python 3.12, managed with [uv](https://docs.astral.sh/uv/).

## Run

```bash
cd api
uv sync                                   # install deps (+ pytest)
uv run python scripts/fetch_footprints.py # once: ~36 MB of city GIS data -> ../data/ (git-ignored), ~20 s
uv run uvicorn app.main:app --reload --port 8000
```

- `GET /health` → `{"status": "ok"}`
- `POST /estimate` `{"url": "<listing or map link>"}` | `{"address": "..."}` (+ optional `unit_sqft`) → PLAN.md §10 shape
  (`app/estimate.py`): link → `resolve_link` → `get_features` → P1's model over HTTP (`GET $MODEL_BASE_URL/hc/estimate`,
  default `http://localhost:8001`; start it with `make -C model dashboard`). Real: `session_id` (SQLite at `SESSIONS_DB`,
  default `../data/sessions.sqlite`), `building` (+ P2-01 `warnings`), `bill.annual` / `seasonal` / `monthly` p10/p50/p90
  (heating + cooling only; how the band is made is in `bill.band_method`; "No AC" sets cooling to $0, `bill.note`),
  score / grade / grade_span / locked (grade range = only what the answers can change: `grade_band_usd`,
  `grade_span_method`) / percentiles / hidden rent (`app/score.py`: vs every scored city building of the same type
  in `data/city_scores.csv`, `percentile_city` vs all 25,670; a type with < 30 falls back to P1's 591 apartment
  buildings), `co2_t` (`app/co2.py`), `badges` (`app/badges.py`), `questions` (`{id, text,
  options: [{value, label}]}`), `heating_cooling` (P1's full answer), `answers`, `model_params`. "No AC"
  (`cooling_code=0`) is never sent to P1's model (outside its training data); cooling is zeroed instead, in /estimate,
  /answer, /fixes and /forecast alike. Errors: 422 `{"detail": {"code", "message"}}` (`missing_input`, `needs_address` +
  `hint`, `not_found`, `not_a_home`, `bad_unit_sqft` outside 100–10,000), 503 (`model_unavailable` when the model is
  down or errors, `lookup_unavailable`; user-safe messages, the detail is logged server-side only). CORS allows `WEB_ORIGINS`, comma-separated (default `http://localhost:3000`,
  for `/web`); the web integration dev servers on 3001–3003 must be listed, e.g.
  `WEB_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003`.
- `POST /answer` `{"session_id", "question_id", "answer"}` → same shape, re-run with every answer so far (narrower band,
  next questions, `locked: true` once the span is one grade or no question moves the estimate). `answer` is an option
  value, label words ("double pane") or "skip". 422 `bad_answer` (message lists the options), 404 `not_found`.
- `GET /session/{id}` → the session's latest body; 404 `not_found` ("That session expired. Send the listing again.").
- `GET /debug/features?address=...&unit_sqft=...&year_built=...` (internal, not part of PLAN.md §10) → building features; 404 if the address can't be geocoded or has no Ann Arbor footprint within 25 m.
- `GET /fixes/{session_id}` (`app/fixes.py`) → PLAN.md §10 shape. Green Rental Housing fixes ranked by CO₂ saved per net $
  (cost − rebate); model-priced first, `unpriced: true` last. $ and CO₂ only from P1's model: the session's
  `model_params` re-run on `/hc/estimate` with one changed input per fix (`window_panes=2`; `cooling_code=3` +
  `heating_fuel=electric` only when the unit already heats with electricity), minus the session's estimate. Fixes
  the model can't price (air sealing, attic R-50, smart thermostat; a gas → heat pump switch, since P1's electric-heat
  homes are near-resistance; anything on a metered building; anything the model says adds CO₂) keep their GRH points
  and rebate with null `usd_saved_yr` / `co2_kg_saved` / `new_grade`. Additive: per fix `unpriced`, `grh_item`,
  `cost_note`, `sources`; top level `grh_points_now_note`, `grh_points_required` (70). `landlord_email` is a fixed
  template. Errors: 404 `not_found` (unknown session), 503 `model_unavailable`. Saves `used_fixes: true` on the
  session (badge leak-hunter).
- `GET /forecast/{session_id}` (`app/forecast.py`) → `{session_id, days: [{date, low_f, high_f, heating_usd,
  cooling_usd}], week: {heating_usd, cooling_usd, total_usd, normal_total_usd, vs_normal_pct}, alerts: [{type:
  cold_snap|heat_wave|costly_week, date, detail}], source, method}`: next 7 days (Open-Meteo) priced with P1's
  forecast-month $ per degree-day. 404 `not_found`, 503 `model_unavailable` / `forecast_unavailable`.
- `POST /compare` `{"listings": [{url|address, unit_sqft?} | {session_id}, {…}]}` (`app/compare.py`) → `{a, b, winner,
  diff_usd_yr, confident}` (`a`/`b` are full /estimate bodies; a `{session_id}` listing is that session's current body,
  answers included, not re-estimated; winner gets `battle-winner`; `confident` = the p10–p90 ranges don't overlap).
  422 `missing_input` (not exactly two). A listing that fails keeps its own status and code:
  `{"detail": {"code", "listing": "a"|"b", "message", "hint"?}}` (e.g. 422 `needs_address` + `hint`, 404 `not_found`
  for an unknown session, 503 `model_unavailable`).
- `GET /city` (`app/city.py`) → GeoJSON FeatureCollection of every city footprint (35,007; `properties: {id`
  (= OBJECTID, same as `/map` `building.id`), `h` (height ft), `r` (1 = Residential), `a` (street label, P3 HOUSE_SCHEMA
  §3, `mailing_assignment` in `app/geo/footprints.py`), and for the 25,704 scored homes `score, grade,
  excess_usd_per_sqft, type}`), gzip when accepted (~2.5 MB). `GET /leaderboard?scope=city|neighborhood` → `{best: [10 public
  benchmark buildings], worst_blocks: [10 block groups / tracts with ≥ 5 buildings]}`. Built by
  `uv run python scripts/score_city.py` (P1's model on every footprint) into `data/city_scores.csv`. 503 `city_unavailable`.
- `GET /map/{session_id}` (`app/map_widget.py`) → P3's `MapWidgetData` (`web/components/hidden-rent-map/types.ts` on
  `p3/map-widget`): building (footprint, LiDAR height, stories, sizes, each with a source), 10 similar buildings,
  block group (TIGERweb outline, cached in `../data/map_block_groups/`), `steps` (public record, then one P1 estimate
  per answer, same params as `/answer`), `sources`. Look-alikes are empty pending P1. 404 `not_found`, 503 `model_unavailable`.
- `POST /calibrate` (`app/calibrate.py`) `{session_id, bill_image_base64}` (xAI Grok vision, `XAI_API_KEY`,
  `XAI_VISION_MODEL`; two reads that must agree) or `{session_id, therms, kwh, start, end}` → `{pct_vs_expected_for_weather
  (percent), streak_months, badges, estimate}` + additive `year, month, actual_gas_ccf, expected_gas_ccf, noise_floor,
  meaningful, extracted, note` (P1's `/hc/bill_check`, gas only; streaks in `CALIBRATE_DB`). Errors: 404 `not_found`,
  422 `missing_input` / `unreadable_bill` / `bad_bill`, 503 `vision_unavailable` / `model_unavailable`.
- Accounts (`app/accounts.py`, SQLite `APP_DB`, default `../data/app.sqlite`; NEW_CHANGES.md NC-01/02/07). The phone
  (iMessage handle, normalized like `agent/src/photon.ts`) is the account. **Agent-only** (header `X-Agent-Key` =
  `AGENT_API_KEY`; open with a warning while unset): `POST /auth/phone {phone, photon_user_id?, session_id?}` →
  `{user_id, created, current_property_id}` (idempotent; a web `session_id` becomes the home if there's none),
  `POST /auth/web/confirm {code, phone}` (on an inbound "login <code>"), `POST /checkins/trigger {user_id}` →
  `{message_hint: "still_at_address", property_id, address, created_at}`. **Web login:** `POST /auth/web/start {phone}`
  allowlists the phone with Photon (`PHOTON_PROJECT_ID`/`SECRET`; `USE_MOCKS=1` or no creds = `sms:` link) →
  `{login_id, code, text_body, redirect_url, assigned_number_masked, expires_at}` (10 min; 3 per phone and 20 per IP
  per 10 min, 5 new numbers an hour); `GET /auth/web/{login_id}` → `{status: pending|verified|expired, user_id?,
  token?}` (token once). **Agent key or `Authorization: Bearer <token>`:** `GET /me/{user_id}` → `{user_id,
  phone_masked, alias, leaderboard_opt_in, timezone, reminder_prefs, current_property_id, properties[],
  current_estimate, pending_checkin}`; `PATCH /me/{user_id} {alias?, leaderboard_opt_in?, timezone?, reminder_prefs?,
  pending_checkin: null?}`; `POST /properties {user_id, address|url, unit_sqft?}` → `{property_id, building_id (= /map
  building.id), estimate, active}` (archives the old home); `POST /properties/{id}/activate`;
  `GET /properties/{id}/history` → `{property_id, snapshots, bills, impact, commitments}`. Errors: 401 `agent_only` /
  `login_required` / `login_expired`, 403 `forbidden`, 404 `not_found` / `bad_code`, 409 `no_property`, 410
  `code_expired`, 422 `bad_phone` / `alias_required` / `bad_alias` / `bad_hour` / `bad_prefs` / `bad_timezone`, 429
  `too_many_codes` / `signups_full`, 503 `photon_unavailable`.
- Commitments (`app/commitments.py`, same `APP_DB`; NEW_CHANGES.md NC-03/04). Agent key or the user's bearer token
  (`accounts.authorize`). `CATALOG` ids: `air_sealing`, `attic_insulation`, `wall_insulation`, `window_upgrade`,
  `thermostat_setback` (with a 64°F WHO floor `note`), `landlord_request`, `heat_pump`; GRH points, costs, rebates and
  sources are /fixes' own. `GET /commitments/suggested/{property_id}` → `{property_id, commitments: [{catalog_id,
  title, who_acts, grh_item, grh_points, cost_usd, rebate_usd, cost_note, sources, note?, projected: {usd_saved_yr,
  co2_kg_saved_yr, score_delta, new_grade, label} | null, pending_model, co2_per_net_usd, method}]}` ranked by CO₂ per
  net $ (P1 prices only windows and, for electric heat, the heat pump; everything else is `pending_model: true` with
  null numbers). `POST /commitments {user_id, property_id, catalog_id, target_date?}` → Commitment `{id, user_id,
  property_id, catalog_id, status: accepted, evidence: projected, target_date?, accepted_at, reminder_channel (the
  user's reminder_prefs.channel when there's a target date, else none), title}` (idempotent while accepted);
  `PATCH /commitments/{id} {status: completed|dismissed}` (completed → evidence `reported`; never backwards);
  `GET /commitments?user_id=|property_id=`. `POST /projection {property_id, commitment_ids: [commitment or catalog
  ids]}` → `{id, property_id, current: {score, grade, percentile_city, bill_annual, co2_kg_yr}, projected: {…, label:
  projected_if_completed}, delta, modeled, not_modeled, method, model_version, created_at}`: all modeled changes in one
  P1 run; never touches the session. Errors: 401/403 (accounts), 404 `property_not_found` / `not_found` /
  `commitment_not_found`, 409 `bad_transition`, 422 `unknown_action` / `unknown_commitment` / `missing_input`, 503
  `model_unavailable`. History (`GET /properties/{id}/history`) lists them.
- Bills, snapshots, impact (`app/bills.py`, NC-05): `POST /calibrate` with `property_id` (agent key or bearer) also
  stores the bill (numbers + image SHA-256, never the image; a resend of the same period or image returns the first
  response), a `bill_regrade` snapshot (`label: "from your bill, adjusted for weather"`) and, when D3 holds (a full
  month after a completed commitment, beyond P1's noise floor, meaningful), a verified gas-only `impact`. Extra fields:
  `bill_id, verified, verification_status, verification_rule, verified_commitment_ids, impact, snapshot,
  model_version`. Errors: 404 `property_not_found`, 409 `bill_already_used`, 422 `property_session_mismatch`. Without
  `property_id` the response is exactly the old one. Snapshots: `initial_estimate` (POST /properties, /auth/phone
  handoff), `questionnaire` (each /answer on a saved home), `bill_regrade`. A bill regrade is damped (the implied year
  is clamped to the model's p10–p90 for the home) and is `provisional: true` (label "early signal from one bill: …
  so your grade doesn't change") unless P1 calls the bill `meaningful`; provisional snapshots never become the current
  grade (`/me current_grade`, `/leaderboard/position`). The response's `bill_signal {grade, score, annual_usd,
  pct_vs_expected_for_weather, label}` carries the bill-based numbers either way.
- Wave 6, for the web: `heating_fuel` answer `included` ("Heat is included in my rent"): the model keeps the
  block-group fuel, so grade/score/percentiles/co2_t rate the building; the renter's `bill` (annual, seasonal,
  monthly) is cooling only, `bill.building_annual` keeps the building's band, `bill.note` says so, and
  `hidden_rent_usd_mo` compares cooling only (`hidden_rent_method`); /fixes, /forecast and /projection count the
  renter's $ as cooling only. `/calibrate` also takes `amount_usd` (with start, end; `kwh` optional) when the gas used
  isn't known: (amount − DTE's $15.40 Rate A monthly customer charge, Oct 2026 rate card) ÷ P1's EIA marginal $/ccf for
  the bill's month (`model/data/processed/prices_mi.json`), flagged `extracted.estimated_from_amount` with a `note`;
  and `gas_unit: ccf | therms` for the typed number (default therms). `POST /properties {user_id, session_id}` adopts
  an answered session (no re-estimate). No auth, by session: `GET /commitments/suggested?session_id=`,
  `POST /projection {session_id, commitment_ids: [catalog ids]}` (what-if: `id: null`, not stored),
  `GET /leaderboard/position?session_id=[&catalog_ids=a,b]` (ghost marker from that what-if).
- Reminders (`app/reminders.py`; never sends anything): agent key only: `GET /reminders/due?now=` → `[{reminder_id,
  user_id, handle, kind: checkin|task|weather, text_hint, property_id, commitment_id?}]` (at most one per user a local
  day, only in the user's `hour_local`, 8 AM–10 PM, iMessage channel, not paused/stopped, paused after 2 unanswered);
  `POST /reminders/{id}/sent` after delivery; `POST /reminders/inbound {user_id}` on any reply; `POST
  /reminders/demo-send {user_id, kind?}` (ignores clock and cap). Agent key or bearer: `POST /reminders/{user_id}/stop
  | pause | resume`. Weather reminders come from /forecast's alerts (`costly_week` only when ≥ $5 above normal).
  `/reminders/inbound` also returns `replying_to: {reminder_id, kind, local_date, commitment_id?} | null` (the reminder
  delivered, or demo-shown, since the previous reply, from today or yesterday local). A task reminder's `text_hint`
  carries the habit streak ("Habit streak 4 days; reply done to keep it.").
- Fast-forward (`app/simulate.py`, a SIMULATION that stores nothing): `POST /simulate/fast-forward {property_id |
  session_id, days: 1-365, catalog_ids?}` → `{label: simulated_projected_if_kept, label_text, method, start_date, days:
  [{date, usd_saved, kg_co2_saved, cumulative_usd, cumulative_kg, habit_day}], totals, annual, commitments, modeled,
  not_modeled, real_habit_streak, simulated_habit_streak}`: /projection's composed what-if spread over typical-year
  (1991-2020) heating/cooling degree-days at the home, so 365 days sum to the annual delta. property_id: owner or agent
  (accepted/completed commitments unless catalog_ids); session_id: anonymous. Rate-limited like /projection.
  `/projection`'s `delta` also carries `building_heating_usd_saved_yr` / `building_cooling_usd_saved_yr`.
- Daily habit streak (`app/habits.py`; agent key or bearer): `POST /habits/{user_id}/checkin {date?, commitment_id?,
  source: imessage|web}` → `{current, best, checked_in_today, last_checkin_date, badges}`; idempotent per local day
  (user's `timezone`, default America/Detroit); only today or yesterday (422 `bad_date`); needs an accepted or
  completed commitment at the current home (422 `no_habits`). Streak = consecutive local days ending today, or
  yesterday while today is pending. `GET /habits/{user_id}` → the same + `checkins` (last 30 days). `GET /me` has
  `habit_streak {current, best, checked_in_today}`; badges `habit-3`, `habit-7` (best streak). Self-reported, not savings.
- Boards (`app/boards.py`, NC-06): `GET /leaderboard` without `board` is unchanged. `GET /leaderboard?board=verified_cut|
  co2_avoided|streak|follow_through|neighborhood|habit_streak[&scope=]` → `{board, scope, coverage, entries: [{alias | geoid, value,
  unit, evidence, demo, rank}], empty_reason, year, model_version, metric_note}`: opted-in homes with verified bill
  impact only (aliases, never phones/addresses; tracts need 5 homes). `habit_streak`: opted-in renters with a chosen
  alias, current habit streak in days (ties by `best`), evidence `self_reported_checkins`. 422 `bad_board` / `bad_scope`.
  `GET /leaderboard/position/{property_id}` (agent key or bearer) → `{current: {score, grade, percentile_city, rank, of},
  projected: {rank, score, percentile_city, label} | null (the latest /projection's own score/percentile_city),
  neighbors, percentile_basis, label, current_source, model_version}`; 404 `not_found`, 503 `position_unavailable`.
  Demo entries only with `DEMO_SEED=1` (`uv run python scripts/seed_demo_board.py`), labelled `demo: true`.
- Calendar (`app/gcal.py`, NC-08; `GOOGLE_CLIENT_ID`/`SECRET`, `GOOGLE_REDIRECT_URI`, `CALENDAR_STATE_SECRET`,
  `WEB_ORIGIN`; no Google creds = labelled mock mode): `POST /calendar/connect {user_id}` → `{auth_url, mock, message?}`;
  `GET /calendar/callback` → 303 to `WEB_ORIGIN?calendar=connected`; `POST /calendar/reminders {user_id, commitment_id,
  start?, cadence: once|daily|weekly}` → `{reminder_id, event_id, html_link, mock}`; `DELETE /calendar/reminders/{id}`.
  `/me` has `calendar_connected`. Errors: 400 `invalid_calendar_state`, 404 `not_found`, 422 `calendar_not_connected` /
  `commitment_not_accepted` / `bad_cadence` / `bad_start` / `calendar_denied` / `missing_input`, 503 `calendar_unavailable`.
- `make phase2-check` (`scripts/phase2-e2e.sh`, root): the Phase 2 flow against `API_BASE_URL` with `AGENT_API_KEY`,
  on a fictional phone; no texts or events sent.

## CO₂ and fix sources (checked Oct 4, 2026)

`app/co2.py`: `co2_kg(gas_ccf, kwh)` and `co2_t(heating_cooling, bill=None)` → `{p10, p50, p90}` t/yr (p10/p90 scale by
the bill's annual p10/p50, p90/p50 when present, else null). Heating + cooling energy only, as P1's model gives it.
- Gas 5.306 kg CO₂/therm (53.06 kg/mmBtu): [EPA GHG Emission Factors Hub 2025](https://www.epa.gov/system/files/documents/2025-01/ghg-emission-factors-hub-2025.pdf), Table 1, natural gas (Jan 15, 2025).
- 1 ccf = 1.037 therms (2025 US average, 1,037 Btu/cf): [EIA FAQ](https://www.eia.gov/tools/faqs/faq.php?id=45&t=8).
- Electricity 970.6 lb CO₂/MWh = 0.4403 kg/kWh: [eGRID2023 rev 2](https://www.epa.gov/system/files/documents/2025-06/summary_tables_rev2.pdf) (Jun 12, 2025, latest EPA release), Table 1, RFCM (RFC Michigan) CO₂ total output rate.

`app/fixes.py`:
- GRH points: [Green Rental Housing Checklist](https://www.a2gov.org/media/dxxnmkyt/green-rental-housing-checklist.pdf) (PDF modified Jun 29, 2026; 310 possible; 70 needed through Jul 5, 2028, then 110). Windows: Energy Efficient Windows 4; heat pump: Electricity is the Primary Type of Energy Used for Space Heating 15 + Medium-Efficiency Cold-Climate Heat Pump with Electric Backup Heat 20; Air Sealing 9; Attic … Insulated 9; Programmable 2 + ENERGY STAR Smart Thermostat 2. `grh_points_now` counts only renter answers (electric heat 15, central AC/heat pump → Space Cooling is Provided 2).
- Heat pump cost $15,400 = midpoint of $11,300–$19,500 ([DOE/LBNL Midwest fact sheet](https://bsesc.energy.gov/sites/default/files/2024-12/Heat%20Pumps%20Regional%20Factsheet%20Midwest.pdf), Dec 2024). Federal 25C credit ended Dec 31, 2025 (IRS FS-2025-05).
- Rebates, market-rate: [A2ZERO Home Energy Rebates 2026–27](https://www.a2gov.org/sustainability-innovations-home/sustainability-me/for-families-individuals/a2zero-rebates/) (owners or renters; ≤ 90% of cost): cold-climate heat pump $4,000, air sealing $500, insulation $500 each. [DTE](https://www.dteenergy.com/us/en/residential/save-money-energy/rebates-and-offers/wi-fi-enabled-thermostats.html) smart thermostat $50 (2026).
- Windows: no unit total (cost is per window): low-e storm windows $60–$200 per window ([DOE Energy Saver, archived May 1, 2026](http://web.archive.org/web/20260501010625/https://www.energy.gov/energysaver/do-it-yourself-savings-project-install-exterior-storm-windows-low-e-coating)); [DTE](https://www.dteenergy.com/us/en/residential/save-money-energy/rebates-and-offers/insulation-and-windows.html) $15 per replacement window. No cited cost for air sealing, insulation or thermostats, so `cost_usd` is null.

CLI, same output: `uv run python -m app.geo.features "912 Mary St, Ann Arbor, MI" [--unit-sqft 850] [--year-built 1965]`

Tests: `uv run pytest -q` (real-address tests skip until the footprint cache exists; `/estimate` end-to-end tests skip unless the model server is up).

## Address → features (`app/geo/`)

| Step | Module | Source (cached in `../data/`) |
|---|---|---|
| Geocode, 2020 block GEOID | `geocode.py` | US Census geocoder, `geocode_cache.json` |
| Footprint, stories, units | `footprints.py` | City of Ann Arbor BuildingFootprints + MailingAddress FeatureServers (`scripts/fetch_footprints.py`) |
| Median year built | `census.py` | ACS 2020-2024 5-year B25035 via Census Reporter (block group → tract → county), `acs_b25035_washtenaw.json` |
| Assemble ResStock-named dict | `features.py` | ResStock 2024.2 MI baseline category strings |

Only the first lookup of a new address needs the network; everything else is offline.

**How values are derived** (each response also has a `sources` dict):
- **Footprint**: the city's mailing-address point for the address (sits inside the building) if within 250 m of the geocode, else the geocoded point; containing footprint, else nearest within 25 m, preferring footprints that hold a mailing address (houses over garages).
- **Stories** (`in.geometry_stories`, string like ResStock): `STORIES`, else from `ABG_BLD_HG` (feet) with a least-squares fit on the ~15k footprints that have both (≈11.1 ft/story + 1.4 ft; 85% exact, 99% within one story). Then snapped to the nearest ResStock 2024.2 MI category (1–15, 20, 21, 35; ties go down), e.g. Tower Plaza 26 → 21. The unsnapped count is `stories_raw` (and is what `building_sqft` uses).
- **Units / type** (`in.geometry_building_type_recs`): `Struc_Type` is only Residential/Commercial/Office/Public, so the type comes from counting residential ("General Mailing") addresses inside the footprint: 1 → Single-Family Detached, 2–4 → Multi-Family with 2 - 4 Units, 5+ → Multi-Family with 5+ Units. A Residential footprint with no address = 1 unit. Non-residential footprint with no residential address → `null` type and sq ft, plus a warning. **Townhouse rule first** (`townhouse_row()`): a Residential footprint with 2+ residential addresses, each its own house number (2841, 2843, … Hardwick Rd), no `UNIT` rows, ≤ 3 stories → Single-Family Attached (also side-by-side duplexes, as in RECS 2020); `in.sqft` = floor area ÷ townhouses. `sources` says which rule fired. Mobile Home is never produced.
- **Sq ft** (`in.sqft`): footprint area in UTM 17N × stories for houses; for multi-unit: `unit_sqft` if given, else building floor area ÷ units (`sqft_estimated: true`; includes hallways, so it runs high).
- **Vintage** (`in.vintage`): `year_built` if given, else block-group median year built; binned `<1940`, `1940s` … `2010s` (2020+ → `2010s`, ResStock has no later bin).
- **County** (`in.county_name`): `Washtenaw County` (exact ResStock 2024.2 string).

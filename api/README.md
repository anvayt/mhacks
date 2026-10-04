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
  down or errors, `lookup_unavailable`). CORS allows `WEB_ORIGINS` (default `http://localhost:3000`, for `/web`).
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
- `POST /compare` `{"listings": [{url|address, unit_sqft?}, {…}]}` (`app/compare.py`) → `{a, b, winner, diff_usd_yr,
  confident}` (`a`/`b` are full /estimate bodies; winner gets `battle-winner`; `confident` = the p10–p90 ranges don't
  overlap). 422 `missing_input` (not exactly two), `estimate_failed` + `listing: "a"|"b"` + the estimate's error.
- `GET /city` (`app/city.py`) → GeoJSON FeatureCollection of every scored footprint (`properties: {score, grade,
  excess_usd_per_sqft, type}`), gzip when accepted. `GET /leaderboard?scope=city|neighborhood` → `{best: [10 public
  benchmark buildings], worst_blocks: [10 block groups / tracts with ≥ 5 buildings]}`. Built by
  `uv run python scripts/score_city.py` (P1's model on every footprint) into `data/city_scores.csv`. 503 `city_unavailable`.
- `POST /calibrate` (`app/calibrate.py`) `{session_id, bill_image_base64}` (xAI Grok vision, `XAI_API_KEY`,
  `XAI_VISION_MODEL`; two reads that must agree) or `{session_id, therms, kwh, start, end}` → `{pct_vs_expected_for_weather
  (percent), streak_months, badges, estimate}` + additive `year, month, actual_gas_ccf, expected_gas_ccf, noise_floor,
  meaningful, extracted, note` (P1's `/hc/bill_check`, gas only; streaks in `CALIBRATE_DB`). Errors: 404 `not_found`,
  422 `missing_input` / `unreadable_bill` / `bad_bill`, 503 `vision_unavailable` / `model_unavailable`.

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

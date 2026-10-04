# Hidden Rent

**Tagline:** See the heating and cooling costs behind a rental listing, then turn questions into a plan for a better home.

**P4 editing draft — October 4, 2026.** Submission target: 11:30 AM; feature freeze: 8:00 AM (`PLAN.md` §8/§12). This is a sourced draft, not a submitted Devpost page. Replace the human TODOs at the end before publishing. Fact-checked against repository sources on October 4 (branch `docs/devpost-factcheck`); items with no repository source are marked **TODO**.

Final integration: `dev` at `97aec3677e77129baca1b439fd9561e18cb24aa9` (wave 7 `de8ccdb` plus a web-only null-size fix), verified October 4, 2026. API: 616 passed, 2 skipped; agent: 70 passed and typecheck; production web build passed; Phase 2: 16/16 (all at `de8ccdb`; backend/agent code unchanged since); latest full browser smoke at `97aec36`: 444 passed, 0 warnings, 0 failures; 0 HTTP 429s; 38 guarded browser requests, peak 25/minute. The real-model terminal conversation and check limits are recorded in [WAVE7_VERIFICATION.md](WAVE7_VERIFICATION.md). Historical model/data measurements below remain sourced at `534f67afd15f0b427472c0fce281c92ee0b0cd7a`, with demo captures at their stated revisions; they are not newly executed benchmarks. The final playable video, real-phone Phase 2 and genuine bill-photo evidence remain separate human checks.

## Inspiration

A renter can compare rent, bedrooms and location before signing. Heating and cooling are harder to see. Hidden Rent starts with that missing question: what might this particular home cost to keep comfortable?

Ann Arbor's Green Rental Housing ordinance took effect in January 2026. It gives us a local reason to connect a renter's question to an actionable request for a landlord, while keeping our predicted grade separate from an official inspection or compliance score. [City announcement](https://www.a2gov.org/news/posts/city-of-ann-arbor-s-green-rental-housing-ordinance-goes-into-effect-jan-6-2026/); repository context: `PLAN.md` §4 and `NEW_CHANGES.md` §2.

## What it does

Enter an Ann Arbor address or a supported listing link. Hidden Rent resolves the building, estimates **heating and cooling only**, and shows a dollar range, a predicted A–F grade, carbon emissions and a comparison with homes of the same building type. It asks about details such as heating fuel, windows and air conditioning, then updates the estimate as the renter answers.

The web experience connects the individual home to a city map, a listing comparison and a share card. The iMessage experience uses Photon Spectrum to run the same address-and-questions interview by text, without installing an app; handing an open web session over to iMessage is not built yet (`notes/requests.md`, `notes/P3.md`). A saved home keeps its answers and history when the renter returns.

After move-in, a renter can type gas usage, provide a bill amount marked as an estimate, or submit a bill photo (photo reading is implemented but has not yet been tested on a genuine bill). The API compares gas usage with weather-normal expectation. Suggestions lead to a modeled what-if, commitments, optional reminders and a landlord email draft. **The projected marker never moves the current marker.** An uncertain bill produces an early signal, not a new confirmed grade or verified savings. [`api/README.md`][api]; `NEW_CHANGES.md` §6/§16; [`agent/PHASE2_REPORT.md`][agent-report].

## Innovation

The product combines a decision before signing with a return visit after move-in. A range becomes a question the renter can actually ask; a modeled improvement becomes a commitment; a bill becomes evidence that can challenge the estimate.

The game mechanics have defined meanings. The score ranks predicted annual heating/cooling cost per square foot within building type. The API marks a grade locked when its reachable span has one grade or no remaining eligible question can narrow the interview further. Skipped or ineffective questions can leave a wider span, and the model-error dollar range remains visible. The public efficiency leaderboard is distinct from the verified-reduction board. We can show useful predictions today without claiming that a pledge has already saved carbon. [`api/app/score.py`][score], [`api/app/city.py`][city], [`api/app/boards.py`][boards].

## Technical Complexity

We built a pipeline from address matching through building features, weather, energy estimation, prices and carbon factors. The model has separate paths for a property with public meter history, a large unmetered building and a smaller building represented by DOE simulations. Public-record assumptions and renter answers remain visible instead of becoming hidden facts.

A FastAPI service owns sessions, accounts, properties, bills and history in SQLite. It calls the Python model over HTTP; the browser and TypeScript agent call the API. The model supplies energy and cost outputs; neither interface invents scores or savings. Bill reading is isolated from the numeric model: xAI extracts structured fields, two reads must agree, and the API validates the result before weather comparison. [`model/heating_cooling/service.py`][service], [`api/README.md`][api], [`api/app/calibrate.py`][calibrate].

## Usability

A street address is enough to begin; saving progress requires sign-in. Listing links are parsed for an address rather than scraped for an unverifiable full listing. Renters can correct unit size and answer plain-language questions, use typed gas usage when a photo cannot be read, and see the source of estimated building attributes.

The interface distinguishes current, projected and early-signal states with text, not just color. Heat included in rent is handled explicitly: renter dollars cover cooling, while the building's grade and carbon still include heating. Bill-amount conversion says “estimated from your bill amount.” Missing modeled effects appear as tips without invented savings. [`api/README.md`][api], [`web/app/leaderboard.tsx` on W2][web-board].

## Adherence to Theme

Hidden Rent is a Sustainability project. Its aim is to help renters and landlords identify avoidable energy use and follow through on improvements. The intended impact metric is **verified, weather-normalized CO₂ avoided at the same home**. Choosing an efficient home, accepting a commitment or moving to a different address is not counted as an achieved carbon reduction. `NEW_CHANGES.md` §2/§7/§9; [`api/app/bills.py`][bills].

## How we built it

**Model.** Change-point fits separate weather-related use from baseline loads in Ann Arbor's public meters. Building models and ResStock per-degree-day models estimate homes without their own public meter history. PRISM local monthly temperatures adjust daily weather from Open-Meteo; EIA Michigan prices convert modeled gas and electricity into dollars. EPA factors convert energy into CO₂. The original ResStock bill-model experiment is a reproducibility checkpoint, not the source of production dollars. [`model/heating_cooling/service.py`][service], `UtilizationToMoney.md`, `ResStock.md`.

**API and persistence.** FastAPI exposes estimates, questions, comparisons, the city layer, bills, commitments and leaderboards. SQLite keeps a current home and archives previous homes. Bills are deduplicated; stored evidence includes numbers and an image hash, never the bill image. Projections cannot write current score snapshots. [`api/README.md`][api], [`api/app/bills.py`][bills].

**Web and iMessage.** Next.js/React provides the report, peer bars, comparison, share and MapLibre map. Photon `spectrum-ts` connects the TypeScript conversation to iMessage; API-returned numbers drive its replies. xAI Grok is used in the bill-photo extraction integration, not to invent an energy estimate. Optional Google Calendar reminders have a labeled mock mode until OAuth is configured. [`web/package.json` on W3][web-package], [`agent/package.json`][agent-package], [`api/app/calibrate.py`][calibrate], [`api/README.md`][api].

The data and external services used in these paths are named below. The repository paths identify our implementation; the linked publisher identifies the source.

| Source | Use and provenance |
|---|---|
| DOE/NREL ResStock 2024.2 Michigan baseline | Simulated stock and end-use energy; [release bucket](https://data.openei.org/s3_viewer?bucket=oedi-data-lake&prefix=nrel-pds-building-stock%2Fend-use-load-profiles-for-us-building-stock%2F2024%2Fresstock_tmy3_release_2%2F). `model/data_sources/resstock.py`, `ResStock.md`. |
| City of Ann Arbor BuildingFootprints and MailingAddress | Geometry, LiDAR height, structure labels and address assignment; [footprints](https://a2maps.a2gov.org/a2arcgis/rest/services/OSI/BuildingFootprints/FeatureServer/0), [mailing addresses](https://a2maps.a2gov.org/a2arcgis/rest/services/MailingAddress/FeatureServer/0). `api/app/geo/footprints.py`, `api/data/city_layer.json`. |
| City of Ann Arbor public energy benchmarking | Monthly gas/electric meter data and the only named public hall-of-fame buildings; [FeatureServer](https://utility.arcgis.com/usrsvcs/servers/1e3bed4240284b40b0c4fea6f8cb4522/rest/services/OSI/BenchmarkingPerformanceMetrics/FeatureServer/0). `model/data_sources/benchmarking.py`, `api/scripts/score_city.py`. |
| U.S. Census geocoder, ACS and TIGERweb | Address/block geography; ACS B25035/B25037 year and B25040 fuel estimates accessed through Census Reporter; block-group map outlines. [Geocoder](https://geocoding.geo.census.gov/geocoder/), [ACS](https://www.census.gov/programs-surveys/acs), [Census Reporter API](https://api.censusreporter.org/1.0/data/show/latest?table_ids=B25035&geo_ids=05000US26161), [TIGERweb](https://tigerweb.geo.census.gov/). `api/app/geo/census.py`, `model/data_sources/census.py`, `api/app/map_widget.py`. Area medians are not a building's measured year or fuel. |
| PRISM Climate Group, Oregon State University | Local temperature level and typical-year normals; [PRISM normals](https://prism.oregonstate.edu/normals/). `model/data_sources/prism.py`, `model/climate.py`. |
| Open-Meteo / ECMWF ERA5 family and seasonal forecasts | Daily history, forecast and seasonal weather; [historical API](https://open-meteo.com/en/docs/historical-weather-api), [forecast](https://open-meteo.com/en/docs), [seasonal API](https://open-meteo.com/en/docs/seasonal-forecast-api). `model/data_sources/openmeteo.py`, `api/app/forecast.py`. |
| NOAA NCEI climate normals | Independent station-normal validation; [normals access](https://www.ncei.noaa.gov/access/us-climate-normals/). `model/heating_cooling/validate.py`. |
| U.S. Energy Information Administration | Michigan residential natural-gas price/volume and electricity sales/revenue; [gas prices](https://www.eia.gov/dnav/ng/hist/n3010mi3m.htm), [gas volumes](https://www.eia.gov/dnav/ng/hist/n3010mi2m.htm), [EIA-861M](https://www.eia.gov/electricity/data/eia861m/). `model/data_sources/eia.py`, `model/data/processed/prices_mi.json`. Statewide prices are not a complete DTE tariff. |
| EPA and EIA energy/carbon conversion | Gas factor, eGRID RFC Michigan electricity factor and gas heat content; [EPA factors](https://www.epa.gov/system/files/documents/2025-01/ghg-emission-factors-hub-2025.pdf), [eGRID2023 rev. 2](https://www.epa.gov/system/files/documents/2025-06/summary_tables_rev2.pdf), [EIA units](https://www.eia.gov/tools/faqs/faq.php?id=45&t=8). `api/app/co2.py`; factors and vintage are retained with verified impact. |
| Ann Arbor GRH and A2ZERO; DOE/LBNL; DTE | Checklist points, cited cost/rebate information and the fixed charge used only for the bill-amount shortcut. [GRH checklist](https://www.a2gov.org/media/dxxnmkyt/green-rental-housing-checklist.pdf), [A2ZERO rebates](https://www.a2gov.org/sustainability-innovations-home/sustainability-me/for-families-individuals/a2zero-rebates/), [DOE/LBNL heat-pump factsheet](https://bsesc.energy.gov/sites/default/files/2024-12/Heat%20Pumps%20Regional%20Factsheet%20Midwest.pdf), [DOE window guide, archived](http://web.archive.org/web/20260501010625/https://www.energy.gov/energysaver/do-it-yourself-savings-project-install-exterior-storm-windows-low-e-coating), [DTE windows](https://www.dteenergy.com/us/en/residential/save-money-energy/rebates-and-offers/insulation-and-windows.html), [DTE thermostats](https://www.dteenergy.com/us/en/residential/save-money-energy/rebates-and-offers/wi-fi-enabled-thermostats.html), [DTE gas rate card](https://www.dteenergy.com/content/dam/dteenergy/deg/website/common/about-us/company-information/dte-gas-company/notices/rateCard.pdf). `api/app/fixes.py`, `api/app/calibrate.py`. Unavailable total costs stay null. |
| OpenFreeMap / OpenStreetMap | Web basemap, separate from city building geometry and model data; [OpenFreeMap](https://openfreemap.org/), [OpenStreetMap attribution](https://www.openstreetmap.org/copyright). `web/components/hidden-rent-map/` on W3; preserve the widget attribution. |
| Renter answers and bill submissions | User-provided evidence, labeled illustrative when used in our scripted demo. Photos go to [xAI image understanding](https://docs.x.ai/developers/model-capabilities/images/understanding); messaging uses [Photon Spectrum](https://photon.codes/docs/spectrum-ts/introduction). `api/app/calibrate.py`, `agent/src/agent.ts`. No real bill photo was supplied in `demo/DEMO_PICKS.md`. |

NASA POWER and Microsoft fallback footprints were considered in `PLAN.md`; they are not the sources of the current served weather and city layer. The leakage research is not wired into the served API and is not claimed as a product feature. `notes/integration.md`, `model/climate.py`, `api/app/map_widget.py`.

## What we measured

These are repository measurements, not newly executed benchmarks. Paths below are at the evidence revision above unless stated otherwise. Percent errors are median absolute percentage errors; they are not “accuracy percentages.”

| Measurement | Result | Exact repository evidence and scope |
|---|---|---|
| Michigan simulation data | **18,756** simulated homes; **14,341** gas-heated homes in the reproduction; **2,869** test homes | `ResStock.md`; [`model/results/resstock_reproduce.json`][reproduce], `n_homes` and `results.*.n_test`. |
| Early bill-model reproduction | R² **0.548 → 0.764** with six additional features; MAE **$495.4 → $352.9**; median P10–P90 width **$1,524.9 → $992.1** | [`model/results/resstock_reproduce.json`][reproduce], `results.bill_usd|public_record` / `bill_usd|plus_6_answers`. Simulated bill-column experiment; **not production tariff accuracy**. Empirical interval coverage was **77.8% / 74.0%**, below the nominal **80%**. |
| Held-out seasonal gas versus real Ann Arbor meters | **7.4% metered**, **28.4% meter model**, **29.9% ResStock**, **29.2% served blend**; **36.2%** median-intensity baseline | [`model/results/validation_real.json`][validation], `seasonal_gas_vs_real_meters.median_abs_pct_error.*.all`; **101 buildings / 800 building-season-years**. Unmetered paths use five folds by building with calibration/blend fitted within training folds. Metered prediction uses the same building's other years. These tests include non-heating gas when comparing with total meters; they do not validate a tenant's heating-only bill directly. |
| Small-building simulation path | Gas-heating intensity test median error **24.8% → 21.1%** with answers | [`model/results/resstock_hc_validation.json`][resstock-validation], `targets.heat_gas_per_hdd`. Simulated held-out examples; local real-meter validation is on large buildings, not small rental houses. |
| Weather cross-check | University station annual heating degree-days **−0.7%**, cooling **+0.5%**; airport heating **−4.0%**, cooling **+24.0%** relative to NOAA normals | [`model/results/validation_real.json`][validation], `weather_vs_noaa_normals`. Do not repeat the historical blanket “within 2.5%” claim from `notes/P1.md`; it does not describe both stations. |
| City coverage | **35,007 footprints**, **25,704 scored**, **9,303 unscored**; compressed layer **2,506,627 bytes** | [`api/data/city_layer.json`][layer]; [`api/data/city_scores.csv`][city-csv] has **25,704 unique footprint rows**. Footprints are not rental units, customers or verified savings. |
| The Yard city example | **615 S Main St**, footprint **50892**, A, score **99.764151**, predicted **$143/year** | [`api/data/city_scores.csv`][city-csv], row `footprint_id=50892`. Public benchmark name “The Yard”; same-type rank qualifies for top 2%. |
| Captured comparison | **624 Church St: $265/year** versus **1022 S Forest Ave: $2,179/year**; gap **$1,914/year** | [`demo/picks/compare/01-arborblu-forest.json`][battle], captured at API revision `fd8c31c`. Same building type; **1,198 / 1,328 ft²** estimated sizes, not verified rental floorplans or equal asking rents. Forest's grade was unlocked (captured span A–F). After P1 restored the model, the warm check returned the same **$265 / $2,179** midpoints ([`README.md` public-demo verification][public-check]). **TODO P2:** the lead reports the current API (25,704-row peer table) returns Forest as F with a **D–F** span; no repository record yet, so read the live span and record it. |
| Modeled Morton improvement | Windows: **$125/year**, **699 kg CO₂/year**, **4 GRH points**; grade remains C | [`demo/picks/bill/05-fixes.json`][fix-capture], gas/single-pane illustrative scenario at **1514 Morton Ave**, capture revision `fd8c31c`. Projected, not measured savings; no total installation price. |
| Wave 6 early bill signal | Hypothetical **120 therms** in **February 2026**: **66% below** expected gas, **118.3% noise floor**; provisional bill signal A/94, current remains C/45 | [`notes/P2.md`][p2-notes], “Wave 6” live integration record; [`api/app/bills.py`][bills]. The signal is **not meaningful or verified** and does not replace the current grade. |

The served-blend figure is **29.2%** per the reproducible artifact sign-off (`model/results/SIGNOFF.md` on `dev`: predictions recomputed from the live artifacts; the older tracked `validation_real.json` summary said 28.7%). `model/results/validation.json`, requested in the drafting brief, does not exist at this revision. The actual real-meter result is `model/results/validation_real.json`. The **28.3%** in older `notes/P1.md` differs from the tracked **28.4%** meter-model statistic; the served blend is **29.2%**. P1 must confirm the final running artifacts match the result files before submission.

## Challenges

Address points do not always fall on the right footprint. Garages, shared buildings and office mailing addresses can distort a home's inferred area. We added city-address matching and size plausibility checks, and still ask renters for unit size where the public record is uncertain.

The harder challenge is making uncertainty understandable. An answer can narrow the grade span while a substantial model-error band remains. A building's public meter may cover a whole complex. A colder month can erase an apparent saving. We made these separate states explicit and retained sources in the API rather than asking a language model to smooth over the uncertainty. [`api/app/geo/`][geo], [`api/README.md`][api], [`model/heating_cooling/service.py`][service].

## Accomplishments

We connected local building records, weather and meter evidence to a renter-facing question loop. We preserved the model's numbers through a web interface and Photon conversation, made a complete scored-city table available for peer comparisons, and added an auditable separation between current estimates, hypothetical improvements and bill evidence. The documented Photon phone round trip passed. The expanded Phase 2 agent also completed the Morton interview, commitments, projection, hypothetical bill and stop flow against the real API/model in terminal mode; this did not send real iMessages or Calendar events. `notes/P4.md`; [`agent/PHASE2_REPORT.md`][agent-report].

A real-browser rehearsal passed all six beats at both desktop and mobile sizes, with 44 screenshots and no browser errors. It used a temporary integration of the web branches and real model responses; only the fictional account onboarding was mocked. That rehearsal predates the wave 7 merge; the merged web (`97aec36`) has since passed the browser smoke above. No final WebM/MP4 has been recorded yet. [`demo/video/README.md`][video-check]; [WAVE7_VERIFICATION.md](WAVE7_VERIFICATION.md).

## Limitations

- **Heating and cooling only.** Hot water, appliances, rent and a full utility tariff are outside the estimate. EIA prices are statewide approximations. Heat included in rent changes renter dollars, not the building's energy/carbon rating. `UtilizationToMoney.md`; [`api/README.md`][api].
- **Simulated small buildings.** ResStock is simulated housing. Real local meter validation covers larger buildings; it does not establish the same error on small houses or duplexes. Year, fuel and size can be inferred, and a complex's meters can be allocated by floor area. [`model/heating_cooling/service.py`][service], `ResStock.md`.
- **Intervals are estimates.** P10/P90 labels are not a promise of calibrated real-bill coverage. Cooling is less well validated than heating; the early simulated intervals under-covered their nominal target. [`model/results/resstock_reproduce.json`][reproduce]; `notes/integration.md`.
- **One uncertain bill is an early signal.** In the documented Morton example the **118.3%** noise floor exceeds its **66%** reduction. No verified saving is awarded. Verification requires a completed commitment, a full subsequent billing period, the same home, a meaningful below-normal result beyond the model's noise floor, and the API verification checks. Verified impact is gas-only; electric use is not yet weather-verified. [`notes/P2.md`][p2-notes], [`api/app/bills.py`][bills].
- **Some actions are tips.** Air sealing, insulation and other unsupported actions remain `pending_model`, with no fabricated dollar or carbon effect. Metered buildings have no priced commitment effects today. A projected gain is never an achieved reduction. [`api/README.md`][api].
- **No demonstrated longitudinal impact yet.** Hypothetical typed bills do not prove real savings. Verified boards can honestly be empty; seeded rows must say “demo data.” Photos can fail and typed entry remains available. [`api/app/boards.py`][boards], [`demo/DEMO_PICKS.md`][picks].
- **Hackathon operations.** Photon Free is limited to **10 allowlisted users** in the team's documented plan; confirm the account limit before inviting judges (`NEW_CHANGES.md` §4). Temporary tunnel URLs change, the running model is required for fresh estimates, and warm caches are not a universal offline service. End-to-end real-phone Phase 2 and a genuine bill-photo check remain human rehearsal items. `notes/P4.md`, [`agent/PHASE2_REPORT.md`][agent-report].
- **Privacy and fairness.** The public hall of fame names only public benchmark buildings. Other public rankings aggregate areas with at least **5 buildings**; opted-in impact boards use aliases. This is a relative predicted grade, not a building inspection or a basis to shame a named small landlord. [`api/app/city.py`][city], [`api/app/boards.py`][boards].

## What's next

Collect consenting renters' real bills across seasons, evaluate small-building errors directly, and improve the verification noise floor through better evidence rather than a looser rule. Add defensible effects for the unpriced fixes, improve equipment and unit-size records, and validate cooling separately. Package reproducible model artifacts with their validation results, finish the final phone/photo rehearsal, and measure actual sustained same-home reductions before claiming impact.

## Sponsor and integration audit

Checkmarks mean implemented integration supported by the repository. They do not establish prize eligibility or replace a successful human demo.

- [x] **Photon Spectrum:** `spectrum-ts` is a dependency and the transport uses it; `notes/P4.md` records a real iPhone → Photon → agent → iPhone round trip. Suitable integration evidence for the Photon track, subject to the event's rules. [`agent/package.json`][agent-package], [Photon docs](https://photon.codes/docs/spectrum-ts/introduction).
- [x] **xAI Grok vision:** implemented through xAI's image API in [`api/app/calibrate.py`][calibrate], with schema validation, matching reads and an opt-in live blank-image test in `api/tests/test_calibrate.py` (skipped in the wave 7 run, like the other opt-in live checks). **TODO: owner confirms a successful genuine bill-image run and any relevant prize eligibility.** The draft does not claim successful real-bill OCR from the typed demo.
- [ ] **Figma Best Design:** intended in `PLAN.md` §9, but no design-file link is established by these sources. P3 must provide the actual Figma work and confirm use before entering.
- [ ] **ElevenLabs:** voice was cut (`notes/P4.md`); not used in the shipped Hidden Rent flow.
- [ ] **Neon:** persistence is SQLite (`api/app/db.py`); no Neon/PostGIS integration claimed.
- [ ] **SpaceX satellite stretch:** no shipped satellite snow-melt path; Cursor eligibility is unverified. xAI vision does not establish that separate stretch-track requirement.
- [ ] **Gemini:** not the bill-photo provider; xAI is used.
- [ ] **.Tech domain:** no verified registered/deployed domain in this audit; a temporary tunnel is not evidence.
- [ ] **Fetch.ai, Capital One Nessie, SpacetimeDB, FREE-WILi, FinchNode, Relay:** not used by this submitted flow, consistent with `PLAN.md` §9.

Main entry: **Sustainability**. “Judged by an LLM” is the planned fun track, not a sponsor integration. This write-up contains ordinary evidence and limitations, no hidden instructions to a judge. Google Calendar is an optional REST integration; mock mode must be labeled and is not a demonstrated live OAuth connection.

## Submission fields and human TODOs

- **Built with:** Python, scikit-learn, XGBoost, pandas, NumPy, FastAPI, SQLite, TypeScript, Next.js, React, MapLibre GL, Photon Spectrum, xAI Grok; public data sources above. P1 confirms the exact final artifact family; P3 confirms merged map dependencies.
- **Repository:** [github.com/anvayt/mhacks](https://github.com/anvayt/mhacks).
- **TODO P4:** add team names/roles, the final public judge URL, final video URL and screenshots; enter and submit by the team's 11:30 AM target. Reprint the QR card after any tunnel restart.
- **TODO P1:** confirm running artifacts/results match; approve the 7.4% / 29.2% wording and record the final model/version. Do not silently substitute historical 28.3%.
- **Completed P2/P3/P4:** the final merged web/API and terminal-agent rehearsal passed at `de8ccdbe014dea2f421b5582c72bd9d3bb3e9e64`, and the browser smoke passed again at `97aec36`. [Final checks and exact transcript](WAVE7_VERIFICATION.md). The $1,914/year gap is sourced by the capture and by the restored-model warm check ($265 / $2,179, [`README.md` public-demo verification][public-check]); WAVE7_VERIFICATION.md records that the Church-vs-Forest compare check passed but not its returned gap. **TODO P2:** add the wave 7 `/compare` numbers (and Forest's live span) to WAVE7_VERIFICATION.md, or recheck live before the table. Real phone delivery, genuine bill OCR and the final video remain separate checks below.
- **TODO P4/phone owner:** complete the real Phase 2 phone flow and a consenting real bill-photo check; otherwise demonstrate typed hypothetical numbers and say so.
- **TODO P3/P4:** supply the actual Figma file if used; confirm sponsor eligibility, Photon slots, optional Calendar credentials and any domain claim.
- **TODO video owner:** the web merge is done (`dev` at `97aec36`); record and verify the final local backup against it; replace any “offline” promise with the actual recorded artifact that can be played without Wi-Fi. Dry-run screenshots do not replace that final recording.

[api]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/api/README.md
[service]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/model/heating_cooling/service.py
[score]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/api/app/score.py
[city]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/api/app/city.py
[boards]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/api/app/boards.py
[bills]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/api/app/bills.py
[calibrate]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/api/app/calibrate.py
[geo]: https://github.com/anvayt/mhacks/tree/534f67afd15f0b427472c0fce281c92ee0b0cd7a/api/app/geo
[reproduce]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/model/results/resstock_reproduce.json
[validation]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/model/results/validation_real.json
[resstock-validation]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/model/results/resstock_hc_validation.json
[layer]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/api/data/city_layer.json
[city-csv]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/api/data/city_scores.csv
[picks]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/demo/DEMO_PICKS.md
[battle]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/demo/picks/compare/01-arborblu-forest.json
[fix-capture]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/demo/picks/bill/05-fixes.json
[p2-notes]: https://github.com/anvayt/mhacks/blob/6d8638fcf330248a18512f83cd7b50411da8db88/notes/P2.md
[agent-package]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/agent/package.json
[agent-report]: https://github.com/anvayt/mhacks/blob/d9a74423af6387f54284b875b94f59810769bea8/agent/PHASE2_REPORT.md
[web-board]: https://github.com/anvayt/mhacks/blob/421dcfa/web/app/leaderboard.tsx
[web-package]: https://github.com/anvayt/mhacks/blob/d8e555a/web/package.json

[public-check]: https://github.com/anvayt/mhacks/blob/b369a65b2289e75b66447ed9f49226d74ed4b94f/README.md
[video-check]: https://github.com/anvayt/mhacks/blob/4e3b134348f9c88578e8035fa4667c536f755bee/demo/video/README.md

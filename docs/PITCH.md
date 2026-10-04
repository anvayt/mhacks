# Hidden Rent — three-minute table pitch

**P4 rehearsal draft, October 4, 2026.** Assign actual names to P1–P4 before rehearsing. Spoken copy is in blockquotes; operator directions and source notes are not spoken. The slots below total **180 seconds**. P4 owns the timer and cuts to the next slot at its boundary; finish at 3:00. Fact-checked against repository sources on October 4 (branch `docs/devpost-factcheck`); items with no repository source are marked **TODO**.

This script preserves historical captures from `demo/DEMO_PICKS.md` and its JSON, originally recorded at `fd8c31c`; captions must retain that provenance. The final web/API integration is now `dev` at `97aec3677e77129baca1b439fd9561e18cb24aa9` (wave 7 `de8ccdb` plus a web-only null-size fix). At `de8ccdb`: API 616 passed/2 skipped, agent 70 passed/typecheck, production web build and Phase 2 16/16 passed. Latest browser smoke at `97aec36`: 444 passed, 0 warnings, 0 failures; 0 HTTP 429s; 38 guarded browser requests, peak 25/minute. The real-model terminal run confirms Morton's C/45 current result, modeled window improvement and provisional hypothetical February bill signal. [Final checks and exact transcript](WAVE7_VERIFICATION.md).

The earlier recorder rehearsal passed six beats at desktop and mobile, but this is not evidence of a final playable recording. Before the table, save and verify that recording, confirm the public URL and phone flow, and have P1 approve the running artifact/result match. Keep the 120-therm bill labeled hypothetical. Read live returned numbers if they differ from a historical capture.

## Three-minute script

### 0:00–0:15 — P4 — the renter and the missing cost (15 seconds)

> Imagine Sam, a renter choosing a home in Ann Arbor. Rent is visible; winter heating is not. Hidden Rent makes that missing cost visible—and connects it to improvements under Ann Arbor's Green Rental Housing program.

**Screen:** address input, then prepared comparison tab. Sam is an illustrative persona, not a claimed customer. Source: `PLAN.md` §4; [City GRH announcement](https://www.a2gov.org/news/posts/city-of-ann-arbor-s-green-rental-housing-ordinance-goes-into-effect-jan-6-2026/). The original plan's $1,200 hook came from simulated bill columns; this script uses the captured $1,914 comparison instead.

### 0:15–0:45 — P2 — the listing battle (30 seconds)

> Here are 624 Church Street and 1022 South Forest Avenue: the same building type, with similar estimated unit sizes. Our captured heating-and-cooling predictions are $265 and $2,179 a year—a $1,914 difference. These are model estimates, not total utilities or verified asking rents. Forest's wide uncertainty is still visible. We show what we know, and what a renter should ask next.

**Screen/action:** `/compare`, submit both addresses, hold the two cards and gap. Keep Forest's range visible: captured **$301–$5,154**, unlocked **A–F** at `fd8c31c`; Church **$221–$285**. **TODO P2:** the lead reports the current API returns Forest as F with a **D–F** span (no repository record yet); read the live span, never the captured one. The restored-model warm check repeated the **$265 / $2,179** midpoints ([`README.md` public-demo verification][public-check]). Captured `confident: true` means these returned bands do not overlap, not that fuel and unit size have been inspected. If the live result differs, read the returned gap; never narrate the old number over a new screen. Sources: [`demo/DEMO_PICKS.md` §2][picks], [`demo/picks/compare/01-arborblu-forest.json`][battle].

### 0:45–1:10 — P3 — one answer locks the grade (25 seconds)

> Now try 2322 Arrowwood Trail. Its captured grade spans A to B. Choose “Central AC”—our illustrative answer—and the grade locks at B. The dollar range remains: locking a grade doesn't remove model uncertainty. A renter can answer here on the web, or run the same interview by iMessage through Photon.

**Screen/action:** prepared Arrowwood survey; invite the judge to select **Central AC**. If their phone is already onboarded and its iMessage conversation is already at Arrowwood's AC question, they can answer by text instead; the web screen will not update from that text, because the web→iMessage session hand-off is still open (`notes/requests.md`). Do not spend this slot on a new allowlist/signup flow. Hold the lock briefly. Captured annual band after answer: **$435 / $470 / $505** (P10/P50/P90). Arrowwood uses a cooperative's property-wide meter history allocated across buildings, not this townhouse's own tenant meter. Sources: [`demo/picks/grade/01-estimate.json`][grade-before], [`demo/picks/grade/02-answer.json`][grade-after], `notes/P4.md`. Wave 6 reports B/73 versus the earlier captured B/70; avoid an outdated spoken score.

### 1:10–1:52 — P1 — how we know it works (42 seconds)

> The model combines public building records, local weather and 18,756 simulated Michigan homes with Ann Arbor's real meter data. In our recorded validation across 101 buildings, median seasonal gas error was 7.4 percent using a building's other years, and 28.7 percent for the blended model on held-out buildings. Those are different tests. Small rental houses lack that local meter validation, so we keep the uncertainty visible. We price predicted energy with EIA data; a language model doesn't invent the bill.

**Screen:** one prepared evidence panel with **metered 7.4% / unmetered blend 28.7%**, **101 buildings / 800 building-season-years**, and the split description beneath it. Do not label this “92.6% accurate” or “28.7% error on every home.” The real-meter comparison includes modeled baseload when comparing with total gas meters. Sources: [`model/results/validation_real.json`][validation] `seasonal_gas_vs_real_meters` and `scheme`; [`model/heating_cooling/validate.py`][validate-code]; `ResStock.md`; `UtilizationToMoney.md`.

### 1:52–2:20 — P3 — improvements without imaginary impact (28 seconds)

> At 1514 Morton Avenue, we assume gas heat and single-pane windows. Double-pane windows are projected to save $125 and 699 kilograms of CO₂ a year. The ghost marker moves; today's grade stays put. “Projected if completed” is the label. Unmodeled actions remain tips, and a landlord email helps the renter start the conversation.

**Screen/action:** Morton board, signed in as a saved home, with **Gas → skip AC → Single-pane** already answered (the wave 7 sequence that returned C/45). Answering AC can move the grade (the captured span after Gas and Single-pane was B–D), so skip it. Toggle windows; hold the ghost label. Wave 6's recorded score is **C/45 → projected C/56**, not a new B grade. The fix has **4 GRH points**, with no sourced total installation cost or payback. Keep the original “You” marker in place. Sources: [`demo/picks/bill/05-fixes.json`][fixes], [`notes/P2.md` “Wave 6”][p2-notes], [`api/README.md`][api].

### 2:20–2:40 — P4 — the monthly return (20 seconds)

> Returning renters can check a bill against the weather. This hypothetical February bill uses 120 therms. It comes back 66 percent below expected—but inside the model's noise floor. We label it an early signal. The current grade stays C; this is not verified savings.

**Screen/action:** show the prepared typed-bill result or submit **120 therms, February 1–28, 2026**, for Morton's saved home. `bill_signal` is returned only for a saved property (`api/README.md`); an anonymous session gets the percentage without it. Read the live returned percentage if it differs. Recorded noise floor: **118.3%**, `meaningful: false`, provisional `bill_signal` A/94 at **$1,283/year**; current **C/45** remains. Do not perform a fresh photo upload during this time-limited slot. Photo extraction is a separate optional demonstration after judging questions. Source: [`notes/P2.md` “Wave 6”][p2-notes]; [`api/app/bills.py`][bills].

### 2:40–2:55 — P2 — zoom out to Ann Arbor (15 seconds)

> Across Ann Arbor: 35,007 building footprints, 25,704 of them scored. The Yard ranks in the top two percent. The leaderboard names public benchmark buildings; other areas are aggregated.

**Screen/action:** `/map?session=<prepared Yard session>`, zoom out to grade colors. The Yard is footprint **50892**, A, current city score **99.764151**, annual heating/cooling midpoint **$143**; the live estimate card rounds its score to **A/100** (`demo/DEMO_PICKS.md` §3). Scored features are buildings, not homes or rental units. This is a prediction allocated from public property meters, not verified retrofit savings. Sources: [`api/data/city_layer.json`][layer], [`api/data/city_scores.csv`][city-csv].

### 2:55–3:00 — P4 — close (5 seconds)

> Know the hidden cost. Ask better questions. Improve your home.

**Screen:** prepared share card and current QR. Do not promise the QR works without checking the day's public tunnel URL.

## Operator setup and evidence card

Use prepared tabs/sessions so the pitch is about the product rather than typing. Start fresh sessions for the final rehearsal; the session IDs in the saved JSON belong to an isolated capture database and are not reusable links.

| Tab | Input / illustrative answer | Number to have visible | Evidence |
|---|---|---|---|
| Compare | **624 Church St** versus **1022 S Forest Ave**, Ann Arbor, MI | Historical **$265 vs $2,179**, **$1,914/year gap**, both intervals; Church A/97; Forest F with its live span (captured A–F, reported D–F now) | `demo/picks/compare/01-arborblu-forest.json` |
| Grade lock | **2322 Arrowwood Trl**, then **Central AC** | Historical A–B → B; **$435–$505/year**, midpoint **$470** | `demo/picks/grade/01-estimate.json`, `02-answer.json` |
| Current + projection | **1514 Morton Ave**, **Gas**, skip AC, **Single-pane**; saved home; windows toggle | Current **C/45**; projected **C/56**; **$125/year**, **699 kg CO₂/year**, **4 GRH points** | `notes/P2.md` Wave 6; `demo/picks/bill/05-fixes.json` |
| Monthly return | Same Morton session; **120 therms**, **2026-02-01 → 2026-02-28** | **−66%**, **118.3% noise floor**, early signal, current **C/45** | `notes/P2.md` Wave 6; `api/app/bills.py` |
| City map | **615 S Main St**, Ann Arbor, MI | The Yard: **A / 99.764151**, top 2%; city **35,007 / 25,704** | `api/data/city_scores.csv`, `api/data/city_layer.json` |

Do not mix the old **150-therm January** capture (−67.6%) with the **120-therm February** Wave 6 result (−66%). Neither is a real tenant bill. Do not call the earlier `demo/DEMO_PICKS.md` city response the current full layer: it contains **25,670** scored features; the current map contains **35,007** footprints, **25,704** scored. Current Yard CSV score is **99.764151**, not the old capture's **99.76145**.

**Timing rehearsal:** keep the allotted pauses for the comparison, grade lock and ghost marker. The spoken script is intentionally short enough to allow those actions. Rehearse with a stopwatch and the actual speakers; assigned slot times are a run-of-show, not a measured delivery-time claim. P4 records the final rehearsal duration and cuts words if needed. Keep the original `PLAN.md` goal of five rehearsals.

## Thirty-second fallback — no Wi-Fi

**Prerequisite:** download the final real-site backup video and screenshots to the demo laptop, then test playback with Wi-Fi disabled. **TODO video owner:** the web is merged (`dev` at `97aec36`); record the final merged UI and fill in the local video filename. Dry-run artifacts remain rehearsal evidence. The raw JSON in `demo/picks/` is evidence for replay; it is not a working offline API. If the video is not ready, show the saved comparison capture as explicitly recorded evidence and omit claims about a working offline app.

| Time | Speaker / display |
|---|---|
| 0:00–0:05 | P4; switch to local recording, overlay “Recorded demo — October 4, 2026.” |
| 0:05–0:18 | P2; pause comparison and grade-lock frames. |
| 0:18–0:30 | P4; pause projection, early-signal and city frames. |

> This is our recorded demo; venue Wi-Fi is unavailable. Hidden Rent compares predicted heating and cooling: these two nearby addresses differ by $1,914 a year in our captured run. A renter's answer narrows the grade. Windows show potential savings, while a bill inside the model's noise stays an early signal. The city map shows where to ask better questions—not claimed carbon already saved.

The $1,914 comes from [`demo/picks/compare/01-arborblu-forest.json`][battle]. If the final video uses a newer gap, update this line to exactly what that recording shows.

## Judge questions and sourced answers

| Likely question | Answer |
|---|---|
| “What did your team build?” | The address-to-feature pipeline, multiple energy-estimation paths and held-out validation, the question/score API, city scoring, the web flow and Spectrum conversation, and the current/projected/bill-evidence separation. We use public datasets and external weather/vision/transport services rather than claiming we created those sources. `model/heating_cooling/`, `api/README.md`, `agent/README.md`; the source inventory is in [DEVPOST.md](DEVPOST.md). |
| “Why not an ordinary utility estimate?” | Our specific contribution is a building-linked estimate with an uncertainty range, renter-answer refinement and an improvement/evidence loop. We have not audited every competitor's current features; do not claim nobody else estimates utilities. `PLAN.md` §5; `api/README.md`. |
| “Is your data real or simulated?” | Both, with distinct paths. ResStock supplies **18,756 simulated Michigan homes**. Public Ann Arbor meter histories support a metered path and large-building validation. Small houses are not locally meter-validated. `ResStock.md`; `model/heating_cooling/service.py`; `model/results/validation_real.json`. |
| “What does the error actually mean?” | Recorded median absolute seasonal gas error is **7.4%** predicting a metered building from its other years and **28.7%** for the served blend on held-out buildings. The raw meter-model comparison is **28.4%**. This is **101 buildings / 800 building-season-years**, not a real-bill trial on every small rental. Cooling and monthly-bill validation are separate. `model/results/validation_real.json`, `model/heating_cooling/validate.py`. |
| “Didn't you get R² 0.76?” | The early simulation bill experiment reproduced **0.548 → 0.764** with extra features on a **2,869-home** test set, from **14,341 gas-heated** simulations. It used bill columns later flagged as inconsistent. The product instead prices end-use energy using EIA data; that R² is not real-dollar accuracy. `model/results/resstock_reproduce.json`; `ResStock.md`; `UtilizationToMoney.md`. |
| “Is the comparison really equal rent and equal size?” | No claim of equal rent or current availability. Captured estimated sizes are **1,198 and 1,328 ft²**, same type; equipment/condition are inferred. Forest's inferred electric heat and its unlocked grade span need renter confirmation. The captured gap is a conditional heating/cooling estimate. `demo/DEMO_PICKS.md` §2. |
| “Does a locked grade guarantee my bill?” | No. The answer-driven grade is locked, while the dollar range retains model uncertainty. P10/P90 are model bands, not guaranteed real-bill coverage. `demo/DEMO_PICKS.md` §1; `api/README.md`; `notes/integration.md`. |
| “How is the score calculated?” | Predicted annual heating/cooling cost per square foot is compared within building type. Score is **100 minus its midpoint empirical cost percentile**; grades are A≥80, B≥60, C≥40, D≥20, otherwise F. This is a relative prediction, not an official energy rating or GRH inspection. `api/app/city.py::score_rows`, `api/app/score.py`; `PLAN.md` §5. |
| “What if heat is included in rent?” | Renter dollars and hidden rent compare cooling only; the building's grade and CO₂ retain heating. `bill.building_annual` and `bill.note` explain that split. Do not call the smaller renter bill lower building emissions. `api/README.md`, Wave 6; `notes/P2.md`. |
| “Have you actually saved carbon?” | We have not demonstrated longitudinal real-user reductions. Commitments and projections do not count. The API requires a full post-completion billing period, a same-home meaningful reduction beyond the held-out noise floor, and its verification checks. Until then, the board can be empty. `api/app/bills.py::verify_bill`, `api/app/boards.py`; `NEW_CHANGES.md` §9.3. |
| “Why show 66% below expected but refuse to verify?” | Morton's hypothetical bill has a **118.3% noise floor**, so **66%** is insufficient under the existing rule. We do not loosen the rule for a demo. The result is an early signal and leaves the current grade unchanged. `notes/P2.md` Wave 6; `model/results/validation_real.json`, `p90_abs_pct_error_winter.resstock`. |
| “Can renters install the fixes themselves?” | Recommendations identify who acts. Window savings are modeled; landlord requests can start the work. Unsupported effects stay tips, and missing total costs remain null, so we do not promise payback or claim a projection is a certified GRH result. `api/app/commitments.py`, `api/app/fixes.py`. |
| “What happens to a bill photo?” | The photo is sent to xAI for extraction; two structured reads must agree, and validation can reject it. Stored property evidence keeps numeric fields and a hash, not the image. Typed entry is available. The draft does not claim a successful genuine-photo trial until the owner supplies one. `api/app/calibrate.py`, `api/app/bills.py`, `demo/DEMO_PICKS.md` §5. |
| “How private are the boards?” | Public named efficiency entries come only from city benchmarking. Other public results are aggregated with a minimum of **5 buildings**; personal reduction boards require opt-in and aliases. Moving archives history and never combines two properties into one reduction. `api/app/city.py`, `api/app/boards.py`, `api/app/bills.py`. |
| “What does Photon add?” | Spectrum carries the interview and bill/photo conversation over iMessage. The core phone round trip is documented; the expanded Phase 2 flow still needs its final real-phone rehearsal. The team's documented Free tier allows **10 allowlisted users**. `notes/P4.md`; `NEW_CHANGES.md` §4; `agent/PHASE2_REPORT.md` on `p4/phase2-real`. |
| “What happens without Wi-Fi?” | We can show a locally stored recording and captured evidence, labeled as such. Warm caches cover tested calls, not arbitrary new addresses or every live service. We must test the actual saved backup before promising it. `demo/DEMO_PICKS.md` “Rehearsal and provenance”; `PLAN.md` §10/§12. |

## Projected-versus-verified language rule

| State | Say | Never substitute |
|---|---|---|
| Current | “Your current **predicted** grade is C.” | A certified inspection/compliance grade. |
| What-if | “Projected if completed: C/56; potential $125/year.” | “Your new grade,” “you saved $125,” or an achieved leaderboard gain. |
| Reported completion | “You marked the windows done.” | “Verified improvement.” |
| Provisional bill | “This bill suggests …; early signal; your current grade stays C.” | “New monthly grade A” when `snapshot.provisional` is true. |
| Verified bill impact | “The API verified a weather-normalized gas reduction at this home.” | Electricity savings, cross-property savings, causal proof or a guaranteed future annual reduction. Quote only actual API impact fields. |
| Seed/mock/replay | “Demo data,” “mock Calendar,” or “recorded run,” as applicable. | Live user adoption, real monthly savings or live OAuth evidence. |

Source: `NEW_CHANGES.md` §7/§9/§16, `api/app/bills.py`, `api/app/boards.py`. **Never change a hypothetical monthly bill to a “real bill” in narration.** When the backend says `meaningful: false` or `verified: false`, say that plainly even if the badge is attractive.

## Human sign-off before the table

- **P1:** approve the final validation/artifact match and source display. The requested `model/results/validation.json` is absent; use `validation_real.json`. Older `notes/P1.md` says 28.3%, while the current tracked meter model says 28.4% and the served blend says 28.7%.
- **P2:** warm final sessions, verify the final comparison/grade/calibration values, and check the current public API. Do not start a new model build during rehearsal.
- **P3:** merge the intended web integrations, test the actual visible copy and QR origin, prepare the tabs, and capture the final video/screenshots.
- **P4:** assign speaker names, verify one real phone, confirm Photon slots, add the final local-video filename and Devpost video URL, rehearse five times and submit by 11:30 AM. Keep the caption “hypothetical bill” visible. Treat a bill-photo failure as a reason to type the numbers, not to improvise them.

[picks]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/demo/DEMO_PICKS.md
[battle]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/demo/picks/compare/01-arborblu-forest.json
[grade-before]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/demo/picks/grade/01-estimate.json
[grade-after]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/demo/picks/grade/02-answer.json
[fixes]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/demo/picks/bill/05-fixes.json
[validation]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/model/results/validation_real.json
[validate-code]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/model/heating_cooling/validate.py
[p2-notes]: https://github.com/anvayt/mhacks/blob/6d8638fcf330248a18512f83cd7b50411da8db88/notes/P2.md
[api]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/api/README.md
[bills]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/api/app/bills.py
[layer]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/api/data/city_layer.json
[city-csv]: https://github.com/anvayt/mhacks/blob/534f67afd15f0b427472c0fce281c92ee0b0cd7a/api/data/city_scores.csv

[public-check]: https://github.com/anvayt/mhacks/blob/b369a65b2289e75b66447ed9f49226d74ed4b94f/README.md
[agent-report]: https://github.com/anvayt/mhacks/blob/d9a74423af6387f54284b875b94f59810769bea8/agent/PHASE2_REPORT.md
[video-check]: https://github.com/anvayt/mhacks/blob/4e3b134348f9c88578e8035fa4667c536f755bee/demo/video/README.md

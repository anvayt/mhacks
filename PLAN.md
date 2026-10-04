# MHacks 2026: Hidden Rent, Team Plan

**Last updated:** Sat Oct 3, 2026, ~8:45 PM EDT. **Hacking ends 12:00 PM Sun Oct 4. Submit on Devpost by 11:30 AM.**

This file is the single source of truth for the team and for any AI agent helping us. It's written so someone with **zero context** can read it top to bottom and start building. The research behind every claim is in `results/` (see [§13](#13-research-files-in-this-repo)).

---

## 0. Read this first

- **We are building Hidden Rent** in the **Sustainability** main track. The decision is made; don't re-open it.
- **`HANDOFF.md` is superseded.** It summarizes the earlier "Clean Hours" plan (dryer scheduling, Fern, FREE-WILi, Relay) from ~6 PM Saturday. Its event facts are still useful, but **follow this file for what we're building.**
- **The quality bar:** [Watt's Up](https://devpost.com/software/watt-s-up), which won Best Overall at HackPrinceton Fall 2025. Its formula: **anyone types an address and gets a personal answer in seconds, from a model the team built, with money and carbon in one view, scaling from one home to a city map, in a polished visual demo.** We copy the *shape*, not the idea.
- **Rules for everyone (humans and agents):**
  1. Never commit secrets. API keys live in a local `.env` that is git-ignored.
  2. Never invent numbers, sources or quotes. Every number shown to judges comes from data or code, with its source cited.
  3. Build the demo-critical path first, and respect the checkpoints in §8.
  4. The agent (chatbot) may **only say numbers returned by our API**. Never let an LLM make up figures.
  5. If we might enter the **SpaceX** sponsor track (stretch only), code must be written in **Cursor**.

---

## 1. TL;DR

**Hidden Rent shows the energy bill a rental listing doesn't, and turns it into a score you can compare, improve and brag about.**

> Paste any Zillow, Apartments.com or Redfin link, or type an address. In about 5 seconds you see what that place will really cost to heat, cool and power: a **$ range per month and per year plus CO₂**, a **Hidden Rent Score (0–100) and letter grade**, and **where it ranks** ("this unit is in the top 2% most efficient rentals in Ann Arbor", or the bottom 10%). You also get **the 3 questions to ask the landlord** that matter most. Text us the answers and watch the range shrink and the grade lock in. After you move in, text a photo of your bill: we tell you whether it's normal for the weather and track your streak. If the place is leaky, we draft the fix request to your landlord. Zoomed out, every Ann Arbor rental sits on a map and a leaderboard.

- **Who:** every renter. That's 45.0M US households (34.8%) and 27,544 Ann Arbor households (54.5%), at every apartment search and every winter bill.
- **The one-line hook:** *"Same-size Michigan apartments differ by about $1,200 a year in energy, and you don't see it until January."*
- **The technical core we build:** a quantile bill model trained on 18,756 Department of Energy simulated Michigan homes (NREL ResStock), plus a **question picker**, checked against **real Ann Arbor meter data**. Already prototyped: R² 0.55 → 0.76 once the renter answers 6 questions, with a 35% narrower range.
- **Rated #1 of 12 ideas** by three independent AI judges (niche score 2/10). Details: `results/pivot-round2/00-synthesis.md`.


Important: jPer season is the most intuitive for the user, and it is what they excpect for utilities estimiations

---

## 2. Event facts

- **Event:** MHacks 2026, University of Michigan.
- **Links:** Devpost <https://mhacks-2026.devpost.com/> · Hacker Handbook <https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af> · Tracks & Prizes <https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5> · Live schedule <https://www.mhacks.org/live>
- **Hacking:** 12:00 PM Sat Oct 3 → **12:00 PM Sun Oct 4.** Devpost shows 12:15, but the handbook says "Submissions Close @ 12 PM" with no late submissions. **Submit by 11:30.**
- **Judging:** Sun 12:30–3:00 PM, Duderstadt Center basement. **Expo style: about 3-minute pitches at our table**, repeated for different judges; sponsors judge their own tracks. Someone must be at the table at all times.
- **Criteria (2026 Devpost, unweighted):** **Innovation · Technical Complexity · Usability (including accessibility and inclusivity) · Adherence to Theme**, plus presentation.
- **Our tracks:**
  - **Main:** Sustainability ("Innovate for a greener tomorrow. Build solutions that rethink energy, climate, and resource systems for lasting impact on our planet."). It had the smallest pool in 2025 (15 of 122 projects).
  - **Fun:** Judged by an LLM (an AI reads our Devpost write-up).
  - **Sponsors:** see §9.
- **Reality check:** in person, a project usually wins **one** prize (2024: 30 prizes went to 30 projects). The main track is the real target.

---


## 4. The product

### Key facts for the pitch (sourced in `results/pivot-round2/`)
- Ann Arbor has about 31,500 rental units, with a **median build year of 1964**, before Michigan's first energy code (1977).
- 800–1,200 sq ft gas-heated Michigan rentals: simulated annual energy bills run **$1,052 (P10) to $2,254 (P90)**, per NREL ResStock.
- Ann Arbor's **Green Rental Housing (GRH)** ordinance took effect **Jan 6, 2026**: units need 70 of 308 checklist points through Jul 5, 2028, then 110. [news](https://www.a2gov.org/news/posts/city-of-ann-arbor-s-green-rental-housing-ordinance-goes-into-effect-jan-6-2026/) · [checklist PDF](https://www.a2gov.org/media/dxxnmkyt/green-rental-housing-checklist.pdf) · [FAQ](https://www.a2gov.org/media/yykptaqy/grh-faq.pdf)
- Ann Arbor discloses home energy scores only at **sale** (HERD), never at lease. Minneapolis requires disclosure at rent time, for some buildings.
- Buildings are ~68% of Ann Arbor's emissions (A2ZERO).

# User flow 

0. Text an agent as the interface, it texts back to you (Photon)
1. **Input:** paste a listing URL (the address is in Zillow/Redfin URLs; **parse the URL, never scrape the page**) or type an address, on the web app or **by iMessage**.
2. **Lookup:** address → geocode → city building footprint → features. Floor area = footprint × storeys, plus height and structure type mapped to a ResStock building type. Year built comes from the listing, else the census block-group median. Fuel defaults to gas (70.7% of Ann Arbor homes).
3. **Estimate:** P10/P50/P90 for annual and monthly bill and CO₂, the **Hidden Rent Score + grade**, and **percentiles** versus same-size Ann Arbor rentals and all Ann Arbor rentals.
4. **Questions:** the picker returns the **3 questions that most shrink the range**, all answerable before signing: single or double-pane windows, top/middle/ground floor, insulation or air-sealing work since a given year, heating fuel and who pays it, last January's gas bill (ask the current tenant).
5. **Answers:** each one → re-estimate → narrower range. The grade "locks in" once the range fits inside one grade (see §5).
6. **After move-in:** text a bill photo. A vision LLM extracts therms, kWh and dates, and a degree-day fit returns "X% above or below normal for this weather". The estimate recalibrates and your **streak** updates.
7. **Fix path:** GRH checklist items (air sealing, attic R-50, walls…) ranked by **CO₂ saved per net $ after rebates** (DTE, Insulate Ann Arbor), with the points each earns, the new grade it would unlock, and a drafted landlord email.
8. **City layer:** every residential footprint scored and shaded on a map, plus leaderboards. Name only buildings the city already publishes (benchmarking); show others aggregated by block or neighborhood.

---

## 5. Gamification (the "you're in the top 2%" layer)

Goal: make an invisible cost **visible, comparable and shareable**, and make improving it feel like progress. Every game number must come from the model; nothing is made up.

| Feature | What the user sees | How it's computed | Owner |
|---|---|---|---|
| **Hidden Rent Score (0–100)** | "Score 82 / 100" | `100 − percentile` of the unit's predicted **energy cost per sq ft (P50)** among all scored Ann Arbor rentals of the same building type. Top 2% → 98. | P1 (math), P2 (serve) |
| **Letter grade A–F** | Big grade badge on the card | Score bands: A ≥ 80, B 60–79, C 40–59, D 20–39, F < 20 | P2 |
| **Percentile line** | "**Top 2%** most efficient rentals in Ann Arbor" / "Bottom 10%: leakier than 9 in 10 similar units" | Same percentile, versus same-type peers and versus the whole city | P1 |
| **Lock in your grade** | "Your grade is somewhere between B and D. Answer 2 questions to lock it in." Progress bar fills as you answer. | If P10–P90 maps to more than one grade, show the span; each answer narrows it. Turns the interview into a game. | P1 + P3 + P4 |
| **Hidden rent** | "**+$94/mo hidden rent** vs the typical same-size unit" | P50 monthly bill minus the peer median | P1 |
| **Listing battle** | Two listings side by side, "Listing B costs $1,140/yr more to live in", with the winner badge | Run `/estimate` on both; compare P50 and ranges | P2 + P3 |
| **Badges** | "Double-pane club", "Top 10% efficient", "Leak hunter" (used the fix path), "Weather-beater" (bill below weather-normal), "Grade jumper" (a fix unlocks a better grade) | Simple rules on API fields | P2 (rules), P3 (UI), P4 (texts) |
| **Bill streak** | "3 months in a row below normal for the weather 🔥" (after move-in) | Monthly bill vs degree-day expectation from the calibration fit | P1 + P4 |
| **Fix simulator** | Toggle fixes, watch grade D → B, $ saved and GRH points 45/70 → 72/70 ✅ | Re-score with ResStock upgrade deltas or the model with changed features | P1 + P3 |
| **Leaderboards** | "Most efficient rentals" (hall of fame) and "Leakiest blocks" (aggregated by block or neighborhood, never naming small landlords) | City batch scores; name only buildings in the city's public benchmarking data | P2 + P3 |
| **Share card** | Image: grade, percentile, hidden rent $, QR "check yours" | Server-rendered PNG or canvas export | P3 |

**Honesty rules for the game layer:** show the range when uncertain ("B–C"), label the score "predicted", never shame a named small landlord, and keep a visible "How this is calculated" link.

---

## 6. Technical core

1. **Bill model:** quantile gradient boosting (LightGBM, or sklearn `HistGradientBoostingRegressor` with `loss='quantile'`) for P10/P50/P90, trained on NREL ResStock 2024.2 Michigan.
   - **Targets:** `out.bills.all_fuels.usd` (annual bill), `out.natural_gas.heating.energy_consumption.kwh` (heating), and CO₂ from the `out.emissions.*` columns.
   - **Public-record features:** `in.sqft`, `in.vintage`, `in.geometry_building_type_recs`, `in.geometry_stories`, `in.county_name`.
   - **Renter-answerable features:** `in.windows`, `in.infiltration`, `in.insulation_ceiling`, `in.insulation_wall`, `in.geometry_foundation_type`, `in.occupants`.
   - **Tested tonight** (sklearn, 80/20 split, 14,341 gas-heated homes):

     | Inputs | R² | MAE | median P10–P90 width |
     |---|---|---|---|
     | public-record only | 0.55 | $507 | $1,596 |
     | + 6 renter answers | 0.76 | $363 | $1,041 (35% narrower) |

   - Interval coverage was 0.73–0.78 against a nominal 0.80, so add **split-conformal calibration** (~20 lines).
   - ResStock 2024.2's bill columns are flagged as inconsistent ([note](https://natlabrockies.github.io/ResStock.github.io/docs/resources/explanations/Issue_2024_2_Electricity_and_Energy_Bills.html)). For final dollars, **price energy (kWh, therms) with our own tariff code** (DTE rates, EIA Michigan prices).
2. **Question picker** (~60 lines of NumPy): for each unanswered feature, take the ResStock rows consistent with the answers so far, split by each possible answer, and pick the question with the smallest expected P10–P90 width.
3. **Real-meter check:** Ann Arbor's benchmarking service has **monthly** gas and electric readings for large buildings (116 multifamily properties in 2023). Fit each building's gas use against NASA POWER heating degree-days (a change-point fit), predict the same buildings with our model, apply a leave-one-building-out correction, and **report the held-out error**. In the pitch, lead with the real-world spread: metered energy use per sq ft varies about 3×, and heating slope about 6×.
4. **CO₂:** gas ≈ 5.306 kg CO₂/therm (EPA, 53.06 kg/MMBtu). Electricity at the eGRID RFCM subregion rate.
5. **Peer distribution (for the score and percentiles):** batch-score every Ann Arbor residential footprint with the model, then compute percentiles of P50 $/sq ft within each building type. Cache the result; the score is a lookup.

**Starter code (the tested feasibility script):**
```python
# quick feasibility check only, not the product model
import pandas as pd, numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
d = pd.read_parquet('MI_baseline_metadata_and_annual_results.parquet')  # ResStock MI baseline (§7)
d = d[d['in.heating_fuel'] == 'Natural Gas'].copy()
y  = d['out.bills.all_fuels.usd'].astype(float)
yh = d['out.natural_gas.heating.energy_consumption.kwh'].astype(float)
A = ['in.sqft','in.vintage','in.geometry_building_type_recs','in.geometry_stories','in.county_name']
B = A + ['in.windows','in.infiltration','in.insulation_ceiling','in.insulation_wall','in.geometry_foundation_type','in.occupants']
def run(cols, target, name):
    X = d[cols].copy()
    for c in X.columns:
        if not pd.api.types.is_numeric_dtype(X[c]): X[c] = X[c].astype('category')
    Xtr, Xte, ytr, yte = train_test_split(X, target, test_size=0.2, random_state=0)
    m  = HistGradientBoostingRegressor(categorical_features='from_dtype', max_iter=300).fit(Xtr, ytr)
    p  = m.predict(Xte)
    lo = HistGradientBoostingRegressor(loss='quantile', quantile=0.1, categorical_features='from_dtype').fit(Xtr, ytr).predict(Xte)
    hi = HistGradientBoostingRegressor(loss='quantile', quantile=0.9, categorical_features='from_dtype').fit(Xtr, ytr).predict(Xte)
    cov = np.mean((yte >= lo) & (yte <= hi))
    print(f"{name}: R2={r2_score(yte,p):.2f} MAE={mean_absolute_error(yte,p):.0f} width={np.median(hi-lo):.0f} coverage={cov:.2f}")
run(A, y, 'bill | public-record'); run(B, y, 'bill | + 6 answers')
```
(The original test read the CSV version of the same file; the parquet has the same columns.)

---

## 7. Data sources (verified by research agents on Oct 3)
| Data | Where | Notes |
|---|---|---|
| NREL ResStock 2024.2, Michigan baseline (18,756 homes) | [parquet](https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2024/resstock_tmy3_release_2/metadata_and_annual_results/by_state/state=MI/parquet/MI_baseline_metadata_and_annual_results.parquet) · [browse bucket](https://data.openei.org/s3_viewer?bucket=oedi-data-lake&prefix=nrel-pds-building-stock%2Fend-use-load-profiles-for-us-building-stock%2F2024%2Fresstock_tmy3_release_2%2F) · [docs PDF](https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2024/resstock_tmy3_release_2/resstock_documentation_2024_release_2.pdf) · [upgrade list](https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2024/resstock_tmy3_release_2/upgrades_lookup.json) | Public S3, no key, ~60 MB. Upgrade scenarios (e.g. insulation, air sealing) live in the same folder; use them for the fix simulator. |
| Ann Arbor building footprints (35,110) | [FeatureServer](https://a2maps.a2gov.org/a2arcgis/rest/services/OSI/BuildingFootprints/FeatureServer/0) | `ABG_BLD_HG` (height), `STORIES`, `Struc_Type`, `PackedPin` (parcel). ArcGIS REST `query`. |
| Ann Arbor energy benchmarking (monthly gas + electric) | [FeatureServer](https://utility.arcgis.com/usrsvcs/servers/1e3bed4240284b40b0c4fea6f8cb4522/rest/services/OSI/BenchmarkingPerformanceMetrics/FeatureServer/0) · [public map](https://a2gov.org/benchmarkingmap) | **Confirm the gas units in hour 1** (probably Portfolio Manager kBtu). Addresses are ranges, so join spatially on polygons. These are the only buildings we name on leaderboards. |
| Ann Arbor GIS catalog | <https://a2maps.a2gov.org/a2arcgis/rest/services> | Other city layers |
| NASA POWER (temperature, heating degree-days) | [API docs](https://power.larc.nasa.gov/docs/services/api/) · [monthly HDD example](https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=T2M,HDD18_3&community=RE&longitude=-83.74&latitude=42.28&start=2024&end=2025&format=JSON) | No key |
| US Census geocoder | <https://geocoding.geo.census.gov/geocoder/> | No key |
| Census Reporter (renters, year built) | [API example](https://api.censusreporter.org/1.0/data/show/latest?table_ids=B25003,B25040&geo_ids=16000US2603000,04000US26,01000US) | No key; block-group median year built is table B25035 |
| Microsoft US building footprints (fallback) | <https://github.com/microsoft/USBuildingFootprints> | If the city service is down |

---

## 8. Build plan (4 people)

**Roles:** **P1** data and ML · **P2** backend and data plumbing · **P3** frontend, design and game UI · **P4** agent, voice and story.

### Timeline and checkpoints
| Time (EDT) | P1: data/ML | P2: backend | P3: frontend/design | P4: agent/story |
|---|---|---|---|---|
| **First 20 min (all)** | Repo layout, **API contract (§10) frozen**, `.env.example`, Devpost skeleton with the 4 criteria as headers | | | |
| → 10:30 PM | Download ResStock MI; reproduce R² ≈ 0.55 / 0.76 | **Mock API with fake JSON within 30 min**; geocoder; footprints | Figma: card, grade badge, range bar, battle view, city map | Photon `spectrum-ts` iMessage hello-world; judge QR onboarding page |
| **10:30 PM checkpoint** | Model numbers reproduced | Address → features works | Design agreed | A judge's phone can text the agent |
| 10:30 PM → 1 AM | Quantile models + conformal; question picker; score/percentile math | Real `/estimate` + `/answer`; URL parser; tariffs + CO₂ | Next.js + MapLibre 3D map; report card; **range-shrinking + grade lock-in animation** | Interview loop over iMessage (API numbers only) |
| **1:00 AM GO/NO-GO** | **End to end: link → card with grade and percentile → one texted answer → narrower range on screen.** If it's not working, cut the city layer, leaderboards and fix path, and finish the core. | | | |
| 1 AM → 5 AM (2-hour sleep shifts, never more than one person down) | Real-meter check + held-out error; city batch percentiles | `/city`, `/leaderboard`, `/compare`, `/fixes`, badges; offline demo fixtures | City map + leaderboards; listing battle; fix simulator; share card | Bill photo → `/calibrate`; badge and streak texts; landlord email |
| **5:00 AM checkpoint** | All demo screens work with real numbers | | | |
| 5 AM → 8 AM | Final numbers; real-bill check (3–5 teammates' DTE bills) | Hardening, caching | Polish, accessibility, backup demo video | Devpost write-up; film the demo video |
| **8:00 AM FEATURE FREEZE** | Only fixes, rehearsal and the Devpost page from here | | | |
| 8 → 11:30 AM | | | | Rehearse the 3-minute pitch 5×; README; **submit by 11:30** |
| 12:30–3:00 PM | **Judging at our table; someone always present** | | | |

### Per-person checklists (each person works from their own list)
"Depends on" says whose output you need; until then, work against P2's mock API.

#### P1: Data and ML ("the thing we built")
**Owns:** `/model`. **Delivers to:** P2 (functions and artifacts the API calls).
- [ ] Python env: `pandas pyarrow numpy scikit-learn lightgbm requests`
- [ ] Download ResStock MI baseline (§7), filter to gas-heated, reproduce R² ≈ 0.55 / 0.76 with the starter script → **10:30 PM checkpoint**
- [ ] Train P10/P50/P90 models for annual bill and CO₂; split annual into monthly (heating-degree-day weighting); add split-conformal calibration so 80% intervals cover about 80%
- [ ] Question picker: `next_questions(answers) → top 3` by expected P10–P90 shrink, using only pre-signing questions
- [ ] Score math: peer distributions → **Hidden Rent Score, grade, percentile vs same type and vs city, "hidden rent $/mo vs peer median"**
- [ ] Fix simulator: re-score with ResStock upgrade deltas (or changed features) → $ saved, CO₂ saved, new grade
- [ ] Real-meter check: Ann Arbor benchmarking monthly gas vs NASA POWER heating degree-days; compare with the model; leave-one-building-out correction; **held-out error** + scatter data for P3
- [ ] Bill-streak math: monthly bill vs the degree-day expectation from the calibration fit
- [ ] Export `model/predict.py` (no network calls at request time; cache everything) for P2
- [ ] Hand P4 the final numbers for the Devpost "What we measured" section by 8 AM

#### P2: Backend and data plumbing
**Owns:** `/api`, data download/caching, city batch scoring. **Depends on:** P1's `predict.py`. **Delivers to:** P3 + P4.
- [ ] **Within 30 minutes:** mock API returning fake JSON in the exact §10 shapes, on `localhost:8000`, with the URL shared with P3/P4
- [ ] Census geocoder + Ann Arbor footprint lookup → features
- [ ] Listing URL → address parser for Zillow, Redfin and Apartments.com (from the URL only)
- [ ] Tariff + CO₂ module: DTE gas/electric rates, EIA Michigan prices, EPA 5.306 kg/therm, eGRID RFCM
- [ ] Real endpoints: `/estimate`, `/answer`, `/calibrate`, `/fixes`, `/compare`, `/leaderboard`, `/city` (same shapes as the mocks)
- [ ] Badge rules (§5) as simple functions on API fields
- [ ] City batch: score every footprint → GeoJSON/vector tiles + leaderboard tables (name only public-benchmarking buildings)
- [ ] Caching + **offline fixtures for 5 demo listings/addresses**; the demo must never depend on a live external API
- [ ] *(Stretch)* Sentinel-2 satellite "snow melts first on leaky roofs" test from last winter's imagery; go/no-go at 3 AM (SpaceX track only if it works)

#### P3: Frontend, design and game UI
**Owns:** `/web`, Figma. **Depends on:** P2's mock API (from minute 30).
- [ ] Figma frames: input, report card, grade badge, range bar, listing battle, fix simulator, city map + leaderboards, share card (enter Figma Best Design)
- [ ] Next.js + MapLibre (OpenFreeMap basemap), 3D building extrusion for the looked-up address
- [ ] Report card: grade badge, score, **percentile line ("Top 2%…")**, $ range per month and year, hidden rent $/mo, CO₂, 3 questions
- [ ] **Signature animation:** the range narrows and the grade "locks in" after each answer (progress bar)
- [ ] Listing battle view (two links side by side, winner badge)
- [ ] Fix simulator: toggles → grade, $ and GRH points update live
- [ ] City map (shaded by score, legend, data source and date) + leaderboards
- [ ] Badges strip + share card (PNG with QR)
- [ ] "How this is calculated" panel with the real-meter scatter chart (P1's data)
- [ ] Polish: contrast, keyboard navigation, mobile width, loading and error states; record the **backup demo video** by 8 AM

#### P4: Agent, voice and story
**Owns:** `/agent`, Devpost, the pitch. **Depends on:** P2's API (mock first).
- [ ] Photon account + `spectrum-ts` iMessage hello-world (cloud mode); judge QR onboarding page (allowlist via `POST /users`)
- [ ] Agent loop: link/address → `/estimate` → reply with grade, percentile, $ range and the first question (**API numbers only**)
- [ ] Interview: answers → `/answer` → "Range now $X–$Y; grade locked: B 🔒" texts with badges
- [ ] After move-in: bill photo → `/calibrate` → "12% below normal for this weather; streak 3 🔥" → `/fixes` → landlord email draft
- [ ] *(Optional)* ElevenLabs "call me and explain my bill" voice
- [ ] Devpost: headers = Innovation / Technical Complexity / Usability / Adherence to Theme / What we measured / Limitations (for Judged by an LLM); tick only sponsors we truly used
- [ ] Write and rehearse the 3-minute pitch (5 run-throughs; who says what); choose demo ideas from §11
- [ ] Final submission by **11:30 AM**, with the video + repo link attached

---

## 9. Sponsor integration
**Rule:** only enter sponsors whose integration genuinely improves the product.

| Sponsor | How it fits Hidden Rent | Effort | Owner |
|---|---|---|---|
| **Photon (iMessage)** | The interview, listing-link share, bill photo and badge/streak texts *are* the product's input and loop. **Qualification rule: must use Photon's Spectrum framework to connect the agent to iMessage.** Free tier ≈ 10 allowlisted numbers: use the QR onboarding page, or demo from a teammate's phone. | 3–4 h | P4 |
| **Figma Best Design** | Grade card, range bar, battle view and map are real design problems | ~1 h extra | P3 |
| **Judged by an LLM** (fun track) | Devpost write-up with the criteria headers + "What we measured" + "Limitations"; no hidden text aimed at the AI judge | 1 h | P4 |
| ElevenLabs (optional) | "Call me and explain my bill" voice; MLH also has a separate ElevenLabs prize | 2 h | P4 |
| Neon (optional) | Use Neon Postgres + PostGIS for the city layer and leaderboards | ~free if chosen early | P2 |
| SpaceX (stretch only) | Only if the satellite snow-melt test works by ~3 AM, and only if we've been coding in Cursor | | P2 |
| Skip | Fetch.ai, Capital One Nessie, SpacetimeDB, FREE-WILi, FinchNode, Relay (Photon instead) | | |

**Cheap MLH prizes (listed in `HANDOFF.md`; separate from the sponsor tracks, so check MLH's rules on Devpost):**
- **.Tech domain:** register a domain like `hiddenrent.tech` and point it at the web app. About 15 minutes.
- **Gemini API:** if we use Gemini as the vision model that reads bill photos, it's a natural entry.
- **ElevenLabs (MLH):** only if we add the optional voice call.

---

## 10. Technical spec

### Stack
- **Model / data:** Python 3.11+, pandas, pyarrow, numpy, scikit-learn and/or lightgbm, requests.
- **API:** FastAPI + uvicorn (`/api`).
- **Web:** Next.js (TypeScript) + MapLibre GL. Basemap without a key: OpenFreeMap (`https://tiles.openfreemap.org/styles/liberty`).
- **Agent:** TypeScript + Photon `spectrum-ts` (docs <https://photon.codes/docs>; management API `https://spectrum.photon.codes`, HTTP Basic `projectId:projectSecret`, 5 req/s). Optional voice: ElevenLabs API.
- **DB:** SQLite for speed, or Neon Postgres + PostGIS if entering Neon.

### Repo layout
```
/model      data download, training, question picker, score/percentiles, validation
/api        FastAPI app: endpoints below, cached data, tariffs/CO2 factors, badge rules
/web        Next.js app: input, report card, battle, fix simulator, map, leaderboards
/agent      Photon spectrum-ts iMessage agent (+ optional ElevenLabs); calls /api only
/results    research (read-only; see §13)
PLAN.md     this file
.env        local secrets, NEVER committed (.env.example lists the names)
```

### Environment variables (`.env.example`; real values only in your local `.env`)
```
PHOTON_PROJECT_ID=
PHOTON_PROJECT_SECRET=
ELEVENLABS_API_KEY=     # optional voice
DATABASE_URL=           # Neon/Postgres if used
API_BASE_URL=http://localhost:8000
```

### API contract (freeze in the first 20 minutes; P2 serves mocks first)
```
POST /estimate   {"url": "https://www.zillow.com/..."} | {"address": "123 Main St, Ann Arbor, MI"}
 → {"session_id",
    "building": {"lat","lon","footprint_geojson","sqft","year_built","type"},
    "bill": {"annual": {"p10","p50","p90"}, "monthly": {"jan": {"p10","p50","p90"}, ...}},
    "co2_t": {"p10","p50","p90"},
    "score": 82, "grade": "B", "grade_span": ["B","C"], "locked": false,
    "percentile_peers": 0.82, "percentile_city": 0.79, "hidden_rent_usd_mo": 94,
    "badges": ["double-pane-club"],
    "questions": [{"id","text","options":[...]}]}
POST /answer     {"session_id","question_id","answer"} → same shape (narrower range, maybe locked: true) + next questions
POST /compare    {"listings": [{"url"|"address"}, {"url"|"address"}]} → {"a": <estimate>, "b": <estimate>, "winner", "diff_usd_yr"}
POST /calibrate  {"session_id","bill_image_base64"} | {"session_id","therms","kwh","start","end"}
 → {"pct_vs_expected_for_weather", "streak_months", "badges", "estimate": <updated>}
GET  /fixes/{session_id} → {"fixes": [{"item","grh_points","co2_kg_saved","usd_saved_yr","cost_usd","rebate_usd","new_grade"}],
                            "grh_points_now","grh_points_after","landlord_email"}
GET  /leaderboard?scope=city|neighborhood → {"best": [...public buildings...], "worst_blocks": [...aggregated...]}
GET  /city       → GeoJSON/vector tiles: every residential footprint with score, grade, excess_usd_per_sqft
```

### Demo-safety checklist
- Pre-cache 5 demo listings/addresses (offline fixtures) in case Wi-Fi or an external API fails.
- Record a backup demo video by 8 AM.
- Show the data source and date on every number; label scores "predicted".

---

## 11. Demo ideas (pick 3–4 beats for the 3-minute pitch)

1. **"Where do you live?"** Ask the judge for their apartment or street. Type it in and the building pops up in 3D: "**Your building is in the top 18% of Ann Arbor rentals**, about $X/month of hidden rent." Personal and instant: the strongest opener.
2. **Listing battle (the money shot).** Two real Zillow listings, same rent, same size, side by side. Reveal: "Listing B costs **$1,140/year more** to actually live in." The winner badge pops. Judges see the "hidden rent" instantly.
3. **Lock in your grade (judge participates).** The judge scans the QR code, texts the agent a listing link, and gets "Grade B–D, answer 2 questions to lock it in." They text "double pane", "top floor", and on the big screen the range shrinks and the grade locks to **B 🔒**, with a badge unlocked. (The FocusFlow/MotionSurfer pattern: the judge takes part.)
4. **Real bill, real check.** A teammate texts a photo of a real DTE bill: "You're 18% above normal for this weather." Then the fix list: "Air sealing + attic insulation: grade D → B, $310/yr saved, +18 Green Rental Housing points, rebate pays half." The landlord email is drafted on screen.
5. **Fix simulator.** Toggle fixes on the screen and watch the grade climb D → C → B, the $ saved tick up, and the GRH progress bar cross 70/70 ✅.
6. **City zoom-out.** Fly out from the building to every rental in Ann Arbor, shaded by score. "The leakiest 10% of blocks waste $X a year and Y tonnes of CO₂. Ann Arbor makes sellers disclose energy scores; renters still sign blind." Show the leaderboard's hall of fame.
7. **"How we know it works."** One chart: real Ann Arbor buildings' monthly gas vs the weather (a 6× spread), and our model's held-out error. "Trained on 18,756 DOE simulations, checked against real meters." (Technical Complexity.)
8. **Physical prop.** A printed **QR code card on the table**: "What's your apartment's hidden rent?" Passers-by and judges try it on their own phones, which draws a crowd to the table (MotionSurfer-style).
9. **Share card.** End by showing the judge's own share card: grade, percentile, hidden rent, and "check yours" QR.

**Suggested 3-minute run:**
- 0:00 hook: "Who's split a surprise January DTE bill?"
- 0:15 demo 2, the listing battle
- 0:50 demo 3, the judge locks in a grade by text
- 1:35 demo 7, how we know it works
- 2:05 demo 5, fix simulator, or demo 4, real bill
- 2:35 demo 6, city zoom-out + close
- Keep demo 1 ready as an alternate opener when a judge seems engaged.

---

## 12. Pitch and Devpost checklist
- [ ] Hook with a named user + the $1,200 number + the Ann Arbor law (first 15 seconds)
- [ ] The judge takes part (locks in a grade by text, or their own address)
- [ ] The technical core in one sentence with its measured number
- [ ] City-scale zoom-out at the end
- [ ] Honest limitations said out loud ("simulated stock, checked against real meters; every number is a range")
- [ ] Devpost: headers = Innovation / Technical Complexity / Usability / Adherence to Theme / What we measured / Limitations; built-with tags; video; repo link
- [ ] Tick only the sponsor tracks we genuinely used
- [ ] Objection answers ready:
  - "Zillow and Rent.com already show utilities." → Those are area or sq-ft averages. Ours models *this* building with a range, narrows it with your answers, checks it against real meters, and ends in a fix.
  - "It's simulated data." → Yes, so we validate on real Ann Arbor meters and real bills and say so.
  - "Picking a better unit just moves emissions." → The impact comes from the fix path and the city targeting map.
  - "Heat is included in my rent." → Then the landlord pays $X/yr of waste: it's their fix (and their GRH points).

---

## 13. Research files in this repo
| File | What it is |
|---|---|
| `results/pivot-round2/00-synthesis.md` | **Hidden Rent's origin:** 12 ideas, 3 judges, Hidden Rent ranked #1, with the full original plan |
| `results/pivot-round2/03-everyday-consumer.md`, `04-campus-city-scale.md`, `06-agentic-ai.md` | The three ideas merged into Hidden Rent, with data details and tests |
| `results/pivot-round2/01–02` | What wins: MHacks winner anatomy, peer-hackathon sustainability winners |
| `results/SUMMARY.md` | Earlier strategy research: 6 years of winners, all tracks, sponsors |
| `results/year-research/2020–2025.md` | Past MHacks winners and judging, by year |
| `results/sponsor-tracks/` | One file per sponsor (APIs, requirements, prizes); Photon is `06` |
| `results/pivot-ideas/` | Round 1 of new ideas (superseded) |

## 14. What we already have
- **Research:** all of `results/` (on GitHub).
- **Fern:** a cartoon houseplant persona with Grok Imagine face videos and a custom ElevenLabs voice. It's local only, on Anvay's laptop (`fern/`), and not committed. Optional as the iMessage agent's persona ("a houseplant who hates drafts") only if it costs under an hour.
- **API credit:** ElevenLabs Creator ≈ 130k characters; xAI ≈ $3.40 left of $25. Keys are in Anvay's local `.env`; ask him.
- **FREE-WILi board:** not used for Hidden Rent.

## 15. Open questions (answer and edit this file)
- [ ] Who is P1 / P2 / P3 / P4?
- [ ] Photon account set up? Who owns it?
- [ ] Which 5 demo listings/addresses do we cache? (Use real Ann Arbor listings near campus, same size and rent, very different scores.)
- [ ] Are we attempting the SpaceX snow-melt stretch (requires Cursor for all code)?

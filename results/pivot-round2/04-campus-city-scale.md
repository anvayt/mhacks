# Ideas — Campus/city-scale lens

## Prompt given (excerpt)
> Your lens: Campus/city-scale lens. Problems at the scale of a campus, city or region where one tool helps thousands at once: University of Michigan campus operations, Ann Arbor/Detroit, transit, buildings, events, dining halls, local grid, municipal services, Great Lakes. Use real open data where possible (verify it). Propose 3 distinct, concrete ideas for the Sustainability main track that (a) clearly fit the winning formula, (b) are NOT niche by the definition above and reach the Watt's Up bar on all five points while being original, (c) are not on the saturated list, and (d) are buildable by 4 students in ~18 h with a strong 3-minute demo. For each, verify the key data/APIs exist and are accessible, name the closest past winners and how yours differs, and list only the sponsor tracks that fit naturally.

*Written Sat Oct 3, 2026, ~7:10 PM EDT. Tags: **[V]** I checked it myself tonight at the linked source or endpoint. **[C]** I computed it tonight from public data (method stated). **[F]** From a team research file (its citations apply). **[I]** My inference. Scores are inference.*

---

## TL;DR

| | Idea | One line | System | Satellite in the core? | Watt's Up bar (5 points) | Recommend |
|---|---|---|---|---|---|---|
| **1** | **Drafty** | Type any Ann Arbor address and see its January heating bill, its CO₂ and what the landlord should fix, before you sign the lease. A text conversation of up to six questions narrows the estimate as you watch. | Buildings / heat | Partly. NASA POWER weather is in the core. An ISS ECOSTRESS night-heat layer is a stretch goal. | 5 of 5 | **Top pick** |
| 2 | **Raindrop** | Type an address and watch last night's storm, measured by satellite, run off your roof and through the city's real storm pipes to the Huron River. See the gallons, your stormwater fee and the fix. On storm nights, neighbours coordinate on a live map to clear leaf-clogged drains. | Water / stormwater | **Yes.** GPM IMERG satellite rainfall, plus a model trained on imagery against the city's own billing polygons. | 4 of 5 (money + *water*, not carbon) | Best satellite fit |
| 3 | **Shift** | Type your address and weekly trips. See which trips could be done by bike, e-bike or bus on low-stress streets, how many days a year Michigan weather allows it, and what going car-light saves. The city view ranks the unbuilt miles of Ann Arbor's bike plan by how many car trips each would remove. | Transport | Minor (NASA POWER weather, elevation) | 4 of 5 (originality is weakest) | Backup |

**Why Drafty is first:**
- **Breadth.** 45.0M US renter households, and 27,544 in Ann Arbor (54.5% of households) [V].
- **Instant recognition.** "I've split a $300 January DTE bill."
- **A hard, surprising number.** Same-size (800–1,200 sq ft) gas-heated Michigan rentals range from $1,052 to $2,254 a year in energy bills, P10 to P90, in NREL's simulated stock [C].
- **A model we train that I already sanity-checked.** Held-out R² is 0.55 from public records alone and 0.76 after six renter-answerable questions. The P10–P90 band shrinks by 35% [C].
- **A conversation that measurably adds value.**
- **A live local policy hook.** Ann Arbor's Green Rental Housing Ordinance took effect in January 2026, but inspection-level energy results for tenants aren't published [V].

**Why not lead with Raindrop**, which has the most satellite and the most visual demo: judges recognise "basement" and "stormwater fee" less instantly than "heating bill", the dollar amounts in Ann Arbor are small ($39–$206 a quarter), and address-to-drain tracing tools already exist (§3).

**What the lens bought us.** Ann Arbor publishes, through a public ArcGIS REST service with no key, data no other city in the brief comes close to [V]:
- **35,110 building footprints** with height and storeys
- **24,400 parcel-level impervious-surface polygons** from 2023, the same ones the city bills from
- **36,348 storm mains** with upstream and downstream node IDs, inverts and diameters
- **18,555 catch basins**

Two of the three ideas are built on that layer. That is the "local hook" pattern behind V²/R (the EECS 215 lab), FarmX (Michigan farms) and F.L.U.D.D (SE Michigan floods) [F].

---

## 0. What I verified before choosing (lens-specific)

| Data | What exists, checked tonight | Access |
|---|---|---|
| **NREL ResStock 2024 Release 2, Michigan** | `MI_baseline_metadata_and_annual_results.csv` (60.5 MB). It covers **18,756 simulated homes** with tenure, vintage, square footage, building type, insulation, infiltration, windows, `out.bills.*.usd`, `out.emissions.*.co2e_kg` and per-end-use energy. It includes 3,494 gas-heated **renter** homes. Upgrade files 1–16 cover heat pumps, geothermal and a light-touch envelope package [V, downloaded] | Public S3, no key ([bucket listing](https://oedi-data-lake.s3.amazonaws.com/?list-type=2&prefix=nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2024/resstock_amy2018_release_2/metadata_and_annual_results/by_state/state=MI/)) |
| **Ann Arbor building footprints** | 35,110 polygons with `ABG_BLD_HG` (height), `STORIES`, `Struc_Type` and `PackedPin` (parcel ID) [V] | [OSI/BuildingFootprints FeatureServer](https://a2maps.a2gov.org/a2arcgis/rest/services/OSI/BuildingFootprints/FeatureServer/0) |
| **Ann Arbor impervious surfaces (billing basis)** | 2023 layer: 24,400 parcel polygons with `PACKEDPIN` and area. A 2020 layer also exists. The city measures these "by computer analysis of infrared photographs taken from the air" [V] | [ImperviousSurfaces/MapServer/7](https://a2maps.a2gov.org/a2arcgis/rest/services/ImperviousSurfaces/MapServer/7); [rates page](https://www.a2gov.org/systems-planning/water-resources/stormwater/stormwater-rates/) |
| **Ann Arbor storm network** | `ST_Mains` (36,348, with `USNODEID`/`DSNODEID`, `UPSTREAMINVERT`/`DOWNSTREAMINVERT`, `DIAMETER`, `BASIN`), `ST_Manholes` and `ST_CatchBasin`. The public catch-basin layer holds 18,555 [V] | [ITPIPES_Storm](https://a2maps.a2gov.org/a2arcgis/rest/services/ITPIPES_Storm/MapServer); [Catchbasins](https://a2maps.a2gov.org/a2arcgis/rest/services/PublicServices/Catchbasins/MapServer/0) |
| **Census (ACS 2024 5-yr)** | Ann Arbor has 50,499 households, of which 27,544 rent (54.5%), and 70.7% heat with utility gas. Michigan: 74.9% heat with utility gas. US: 45.0M renter households (34.8%) [V] | [Census Reporter API](https://api.censusreporter.org/1.0/data/show/latest?table_ids=B25003,B25040&geo_ids=16000US2603000,04000US26,01000US) |
| **NASA POWER** | Monthly heating degree-days for Ann Arbor. In 2025: 3,717 °C-days for the year, 777 of them in January (21%) [V] | [API, no key](https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=T2M,HDD18_3&community=RE&longitude=-83.74&latitude=42.28&start=2024&end=2025&format=JSON) |
| **GPM IMERG Early (half-hourly, 0.1°)** | The latest granule found was for 17:30 UTC today, so latency is about 5 h [V] | [CMR search](https://cmr.earthdata.nasa.gov/search/granules.json?short_name=GPM_3IMERGHHE&bounding_box=-83.8,42.2,-83.6,42.35&page_size=5&sort_key=-start_date); download needs a free Earthdata login, which the team creates |
| **NAIP 2022, 0.6 m, 4-band** | Ann Arbor tiles dated 2022-08-24 [V] | [Planetary Computer STAC](https://planetarycomputer.microsoft.com/api/stac/v1) (free) |
| **ISS ECOSTRESS LST (70 m)** | Pre-dawn winter granules over Ann Arbor, for example 2025-12-22 ~03:00 local and 2025-12-29 ~01:00 local. Cloud cover is unknown [V] | [CMR](https://cmr.earthdata.nasa.gov/search/granules.json?short_name=ECO_L2T_LSTE&bounding_box=-83.80,42.22,-83.67,42.32&temporal=2025-12-01T00:00:00Z,2026-03-15T00:00:00Z) (Earthdata login) |
| **NHTS 2022, OSM, TheRide GTFS** | NHTS `csv.zip` (3.9 MB) returns HTTP 200. Overpass returns 30,800 highway ways in Ann Arbor. The GTFS feed is listed on Transitland and the Mobility Database [V] | [NHTS](https://nhts.ornl.gov/assets/2022/download/csv.zip) · [Transitland](https://www.transit.land/feeds/f-dps2-annarborareatransportationauthority) |

---

## 1. Idea 1 (top pick): **Drafty**: know the January bill before you sign

**One-liner.** Type any Ann Arbor address and get a personal energy report in seconds:
- the unit's expected **January heating bill** as a range, plus its annual dollars and tonnes of CO₂;
- how that compares with similar rentals;
- what the landlord should fix, and what each fix is worth.

Then Drafty texts you. It asks up to six questions only a tenant can answer ("do the windows frost on the inside?", "top floor?"). With each answer the range visibly narrows. It ends with a ready-to-send landlord question list. Zoom out and the same model colours every residential building in the city, showing where efficiency dollars do the most.

### Who has the problem, and how many
- **45.0M US renter households** (34.8%) and **1.09M in Michigan** [V, ACS 2024 5-yr].
- **Michigan heats with gas:** 74.9% of homes [V].
- **Ann Arbor:** 27,544 renter households (54.5%) [V]. The city counts **~31,500 rental units across ~8,500 properties, with a median build year of 1964**, before Michigan's first energy code in 1977 ([City GRH FAQ](https://www.a2gov.org/media/yi5cussn/grh-faq.pdf)) [V].
- **Only 27% of U-M undergraduates live in campus housing** (search summary of a Michigan Daily piece; not opened, so treat as unverified). Most students rent off campus.
- **The money at stake** comes from NREL's ResStock simulated Michigan stock [C] (method: `MI_baseline` file, gas-heated, tenure = Renter, n = 3,494; ResStock's own bill assumptions):
  - annual energy bill P10 **$1,016**, median **$1,652**, P90 **$2,854**;
  - for the **same size** (800–1,200 sq ft, n = 1,486), P10 **$1,052** to P90 **$2,254**, a spread of about $1,200 a year;
  - bill per sq ft ranges 2.4× (P10 $1.11 vs P90 $2.71);
  - median CO₂ is 7.1 t a year;
  - space heating is about 60% of site energy.

### How often it's used
- **Every lease decision.** That is yearly for most students. Ann Arbor's Early Leasing Ordinance sets when renewals and showings start, 180 and 210 days into a lease ([Michigan Daily](https://www.michigandaily.com/news/early-leasing-changes-move-forward-in-ann-arbor-city-council/)) [V].
- **Every monthly bill from October to April.** Forward or upload the DTE bill. Drafty fits a degree-day regression (PRISM-style) of your actual use against NASA POWER weather, reports "your unit vs. our prediction", and recalibrates.
- **Every cold snap.** A text says "Tuesday–Thursday will cost about $X more; here's the setback that saves Y."
- **Continuously at city level.** The Office of Sustainability & Innovations (OSI) and Rental Housing Services can work from the building map.

### Why it isn't niche
- A judge says "my roommate has that" within 5 seconds: the shared $300 January bill.
- The problem is broad (every renter in a heating climate), frequent (monthly bills, yearly leases) and has value in one sentence: "same rent, up to $1,200 a year difference, and you can't see it until January."
- The demo is specific: the judge's own address, one building, one number.
- It is **not** a footprint calculator. The output is a decision (which unit; what to ask the landlord) plus money.

### Watt's Up bar, point by point
| Watt's Up point | Drafty |
|---|---|
| Anyone can use it instantly | Address in, January bill out, in seconds. No account, no bill needed. |
| A real technical core the team trained | Quantile gradient-boosted models (P10/P50/P90) trained on NREL ResStock Michigan, plus a question picker that asks whichever question would narrow your range the most. Both are ours (below). |
| Money + carbon in one view | Dollars per month and year, kg CO₂ per year, and the dollars and CO₂ of each fix, on one card. |
| Scales from one home to city/policy | Every one of 35,110 Ann Arbor buildings is scored. Rental filter. A priority list for Insulate Ann Arbor and the Green Rental Housing Ordinance. ResStock covers every US state, so other cities need only footprints. |
| Beautiful visual demo | 3D extruded building, a live-narrowing bill band, a city map shaded by predicted heat cost. |

### Winning-formula match
- **Broad problem, specific demo:** every renter, demonstrated on the judge's own address.
- **Watch it happen in 20 s:** the judge's phone buzzes with a question, and the band shrinks on screen as they answer. It is participatory, like FocusFlow's webcam demo.
- **A core we built and can name in one sentence:** "a model trained on 14,341 simulated Michigan homes that asks you the question that most narrows your bill."
- **One hard number:** "same-size apartments: $1,052 vs $2,254 a year", and "6 questions cut the uncertainty 35%."
- **Local hook:** the Green Rental Housing Ordinance, passed unanimously in June 2025 and effective January 2026, with 500+ rentals compliant by July 2026 ([WEMU](https://www.wemu.org/wemu-news/2025-06-18/ann-arbor-steps-closer-to-a-carbon-neutral-future-as-green-rental-housing-ordinance-passes), [Concentrate](https://concentratemedia.com/500-ann-arbor-rentals-now-in-compliance-with-new-green-housing-ordinance/)) [V]. Also HERD: home sellers have had to disclose an energy score since March 12, 2024, and 1,000+ homes have been scored, but this covers **sales, not rentals** ([a2gov](https://www.a2gov.org/news/posts/over-1-000-ann-arbor-homes-now-have-home-energy-scores/)) [V].
- **Touches a resource system, not guilt:** buildings produce over two-thirds of Ann Arbor's emissions, and gas burned in buildings was 520,000 tCO₂e (28%) in 2021 (search summary of the city's GHG inventory) [V-search].
- **Measured impact:** the pipeline compares predictions to real bills.

### Closest past winners, and how Drafty differs
- **Watt's Up** (HackPrinceton F25 Best Overall; [Devpost](https://devpost.com/software/watt-s-up)) [F]. Same shape: address to personal energy report, money plus carbon, city layer. Different question (heating loss, not solar generation) and different user (renters, who can't install anything). The core is a narrowing interview, not roof segmentation.
- **FarmX** (MHacks 2024 Sustainability; [Devpost](https://devpost.com/software/farmx-zpw0yq)) [F]. A model trained on public data with a Michigan hook. Drafty adds per-building city data, quantified uncertainty and a live interview.
- **Chilladelphia** (PennApps XXV) and **ZoneZero** (TreeHacks 2026) [F]. Address to rating to fixes, with an institutional dashboard. Ours is money plus carbon, the payer is the landlord, and there is an ordinance hook.
- **Prior art to name honestly:**
  - **UtilityScore**: 2015 utility-cost scores shown on Zillow's HotPads ([Inman](https://www.inman.com/2015/07/10/utilityscores-can-show-which-of-2-identically-priced-homes-actually-costs-more/)) [V-search]. A one-number black box, with no tenant input, no uncertainty and no fixes.
  - **Green Home Audit** on Devpost, a homeowner audit ([Devpost](https://devpost.com/software/green-home-audit)) [V-search].
  - **Minneapolis's Time-of-Rent Energy Disclosure ordinance**: landlords must disclose average utility costs ([City](https://www2.minneapolismn.gov/business-services/licenses-permits-inspections/rental-licenses/renter-protections/energy-disclosure)) [V-search]. This is evidence that the policy exists elsewhere. Ann Arbor doesn't have it, and Drafty estimates without it.
- **Saturated list:** not a footprint tracker, not a chatbot, not solar.

### Technical core we build
1. **Feature builder.** Address → city footprint, giving footprint area × storeys = floor area, height, and structure type mapped to ResStock building type. Vintage comes from a neighbourhood prior (Census Reporter B25035, block-group median year built) or a question. Heating fuel defaults to gas (70.7% in Ann Arbor).
2. **Bill model.** Quantile gradient boosting for P10/P50/P90 of annual heating energy, gas bill, total bill and CO₂, trained on ResStock MI.
   - **Feasibility check I ran tonight [C]** (sklearn `HistGradientBoostingRegressor`, 80/20 split, 14,341 gas-heated homes):
     - from public-record features only: R² **0.55**, MAE $507, median P10–P90 width $1,596;
     - adding 6 interview features (windows, infiltration, ceiling insulation, wall insulation, foundation, occupants): R² **0.76**, MAE $363, width **$1,041** (−35%);
     - heating energy alone: R² 0.65 → **0.85**, with the band 45% narrower.
   - Interval coverage was 0.73–0.78 against a nominal 0.80, so **conformal calibration** is a to-do.
3. **Question picker.** For each unanswered feature, take the ResStock rows consistent with the answers so far. Simulate each possible answer and pick the question whose answer most shrinks the expected P10–P90 width. This is about 60 lines of NumPy, and it is what makes the conversation load-bearing.
4. **Monthly and price layer.** Spread the annual estimate across months by NASA POWER heating degree-days (January ≈ 21% in 2025) [V]. Re-price with DTE tariffs. For reference, EIA's Michigan residential gas price was $11.13/Mcf in February 2026 ([EIA](https://www.eia.gov/dnav/ng/NG_PRI_SUM_DCU_SMI_M.htm)) [V].
5. **Fix simulator.** Join ResStock upgrade files by `bldg_id`.
   - **Honest finding [C]:** the light-touch envelope package (upgrade 16) saves Michigan gas-heated renters a median of only 58–124 therms a year, depending on building type. It adds mechanical ventilation, so *total* bills barely move for apartments.
   - The money story is therefore **which unit you choose** (the $1,200 spread), not "the landlord insulates and you save $500". Show fixes as therms plus CO₂, with dollars where they are real (P90 savings for pre-1980 units: about $207 a year [C]).
6. **City batch.** Score all 35,110 buildings, write vector tiles, and add a rental filter, if OSI or rental-registry data can be obtained (unverified; otherwise use structure type).
7. **Bill check, the measured number.** Two to five teammates or friends supply real DTE bills, and we show predicted vs. actual.
8. **Stretch, gated at 2 AM: ISS ECOSTRESS pre-dawn winter LST.** Granules exist [V]. Show a block-level "warm roofs at 3 a.m." layer and correlate it with the model's predicted heat-loss intensity by block. Label it "block-level signal, not a per-house measurement." This is what would make the SpaceX track genuine.

### Conversational layer (why it earns its place)
- **Renters cannot measure their insulation, but they can answer questions about it.** Six answers cut the uncertainty by 35% [C]. The agent asks one question at a time, in iMessage (Photon) or by phone (ElevenLabs or Grok Voice), and the band shrinks on screen as each answer arrives.
- **After the report:**
  - "Questions to ask your landlord": GRH checklist or HERS status, attic insulation, storm windows, who pays which meter, the last 12 months of bills.
  - A draft email.
  - A January follow-up: "Forward your first DTE bill; I'll check it against the estimate."
- **Numbers rule:** the LLM may only say figures returned by the model API, as in Fern's persona rule [F].
- **Fern is optional and fits:** ferns hate cold drafts.

### Demo (3:00 at the table)
1. **0:00, hook.** "Who's split a $300 January DTE bill? Same-size Michigan apartments range from about $1,050 to $2,250 a year in energy. You sign the lease before you see any of it. Ann Arbor's median rental was built in 1964."
2. **0:20.** The judge types **their own address**, or one near campus. The building extrudes in 3D. The card shows "January: $150–$260", the annual dollars, and t CO₂ per year against similar rentals.
3. **0:40.** **The judge's phone buzzes** (iMessage): "Do your windows frost or fog on the inside in winter?" They answer. On screen the band snaps narrower. Second question, narrower again: "−35% uncertainty."
4. **1:30.** Fixes and the landlord card. Toggle "air sealing + attic insulation" and watch therms and CO₂ fall. Show the ready-to-send landlord questions, including the GRH compliance status.
5. **2:00.** Zoom out to 35,110 buildings shaded by predicted heat cost per sq ft. "Start Insulate Ann Arbor here: these 10% emit N t."
6. **2:30, tech plus honesty.** "Trained on 14,341 NREL-simulated Michigan homes. Held-out R² 0.55 → 0.76 with your answers. Checked against N real DTE bills. NASA POWER weather [+ ISS night heat layer]." Close: "Ann Arbor makes sellers disclose energy scores. Renters still sign blind. This is the rental disclosure the city hasn't built."

### Sponsor tracks (natural only)
- **Photon iMessage agents**, or **Relay** if calls work: the interview *is* the product's input.
- **ElevenLabs**: only if the interview runs as a phone call.
- **Figma Best Design**: the report card and city map are real design problems.
- **SpaceX "Make it Legendary"**: *only* if the ECOSTRESS layer ships (real space data in), Grok Voice runs the call, and the team builds in Cursor. Otherwise skip it; NASA POWER alone is garnish [F sponsor 07].
- **Skipped:** Fetch.ai, Nessie, FinchNode, SpacetimeDB, FREE-WILi (no natural role).

**Fun track:** Judged by an LLM (Devpost of about 500 words with the eval numbers).

### Build plan (6:30 PM Sat → 12:00 PM Sun, 4 people)
| Time | P1: model | P2: data + API | P3: frontend | P4: agent + story |
|---|---|---|---|---|
| 6:30–8:30 | Pull ResStock MI baseline + upgrades (minutes). Map ResStock fields to city-observable features | Pull 35,110 footprints into SQLite or PostGIS. Address geocoder (city `AddressLocators` service or Census geocoder) | Figma wireframe (1 h), then Next.js + MapLibre 3D extrusions | Photon (or Relay) hello-world. Persona with the numbers rule |
| 8:30–12:00 | Quantile GBMs (bill, heat, CO₂). Holdout metrics. Conformal calibration | NASA POWER monthly split, DTE pricing, CO₂ factors. FastAPI `/estimate` | Report card, band animation | Interview loop calling `/next_question` and `/estimate` |
| **Gate 12:00** | **Address → report → 1 question → narrower band, end to end** | | | |
| 12–3 AM | Question picker. Upgrade-delta model | Batch-score 35k buildings → tiles | City view, rental filter, fix toggles | Landlord card + email draft. Bill-upload PRISM fit |
| 3–7 AM | Sleep in shifts. **2 AM ECOSTRESS go/no-go** (one clean pre-dawn granule georeferenced, or cut) | | | |
| 7–10 AM | Real-bill check (2–5 bills). Final numbers | Hardening, caching for 20 demo addresses | Polish, mobile view | Film the demo video in a real old Ann Arbor rental |
| 10–12 | Devpost (~500 words, eval table, "Limitations"), public repo, rehearse the 3-min pitch with two at the table | | | |

### Risks
- **ResStock is simulated, not metered.** Say so. Show a real-bill check, even with n = 3, and label it.
- **Building vintage isn't in open city data** (I found no public year-built field). Use the neighbourhood prior plus a question; it's the first thing the picker asks when it matters.
- **Unit-level splits in large apartment buildings** are approximate. ResStock does model multifamily units individually, so map footprint ÷ units.
- **Retrofit savings are modest for apartments** [C]. Don't oversell fixes. The decision value is choosing the unit.
- **The LLM inventing figures:** apply the numbers rule; templates for all money lines.
- **Photon or Relay access on the day:** the web flow runs the same interview in-page.

**Scores [I]:** win 7 · non-niche 9 · feasibility 8 · demo wow 7 · sponsor fit 6 · originality 7.

---

## 2. Idea 2: **Raindrop**: follow the rain off your roof

**One-liner.** Type an address. Raindrop paints your roof, driveway and patio on the aerial photo using a model we trained against the city's own billing polygons. Then it replays last night's storm, measured from space by GPM IMERG. Animated droplets run off your lot, into catch basin #N, through the city's real storm pipes, and out to the Huron River, with a running gallon count and a clock. You see your stormwater fee tier and the rain garden that would catch it. On forecast storm nights in leaf season, neighbours claim and clear the most important clogged drains on a shared live map.

### Who and how many
- **Every property in the 2,202 US stormwater utilities** (WKU 2024 survey; [PDF](https://digitalcommons.wku.edu/cgi/viewcontent.cgi?article=1019&context=seas_faculty_pubs)) [V-search].
- **Ann Arbor:** 24,400 parcels billed by impervious area [V].
- **Detroit** charges **$750 per impervious acre per month**, with credits up to 80% for green infrastructure ([DWSD drainage charge](https://detroitmi.gov/departments/water-and-sewerage-department/dwsd-customer-service/drainage-charge)) [V-search]. That figure is from older city documents; recheck the current rate.
- **Basements and the river.** In the June 2021 Detroit storm, about **30,000 households** were directly impacted and 70% of FEMA claims involved basements ([Detroit](https://detroitmi.gov/news/city-expands-private-sewer-repair-program-reach-75-more-neighborhoods-hardest-hit-2021-flood)) [V-search]. Michigan combined sewers send about **5.7 billion gallons of raw sewage** into waterways in an average year ([Clean Water Action](https://cleanwater.org/michigans-outdated-and-dangerous-combined-sewer-systems)) [V-search].
- **Trend.** Midwest heaviest-1% rain days carry **45% more** precipitation than in 1958 ([NCA5 Ch. 24](https://nca5.climate.us/chapter/24)) [V-search].

### How often
- **Every rain:** a post-storm report and a pre-storm "clear your drain" text.
- **Every quarterly water bill:** the stormwater line ($39.17–$205.58 a quarter for Ann Arbor residential tiers, FY26 ([a2gov](https://www.a2gov.org/systems-planning/water-resources/stormwater/stormwater-rates/))) [V].
- **Leaf season, now.** Ann Arbor asks residents to adopt storm drains because fall leaves clog them ([a2gov](https://www.a2gov.org/ann-arbor-water/ann-arbor-water-news/adopt-a-storm-drain-to-help-with-fall-leaves/)) [V-search].

### Why it isn't niche, and the honest limit
- Every roof sheds rain every storm, and one inch on 1,000 sq ft is **623 gallons** (1 in × 1 sq ft = 0.623 gal).
- The limit: judges know "flooded basement" and "water bill" but don't *feel* stormwater the way they feel a heating bill. In Ann Arbor the money is small: rain-garden credits are **$8.59 a quarter** and rain barrels $4.15 ([a2gov](https://www.a2gov.org/systems-planning/water-resources/stormwater/residential-stormwater-credits/)) [V-search].
- So **lead with basements and the river, and use Detroit's fee for the dollars.**
- It hits Watt's Up's "money + carbon" only as **money + water**.

### Watt's Up bar
- **Instant:** address in.
- **Trained core:** an impervious segmentation model.
- **Money + impact:** fee, gallons, overflow share.
- **Scales to city/policy:** which pipes overload, where green infrastructure helps most, and a model that lets any of the 2,202 utilities measure imperviousness without paying for hand digitising.
- **Visual:** droplets flowing through real pipes, the best "watch it happen" of the three.

### Winning-formula match
- **Watch it happen:** a physical-feeling animation within 20 s.
- **Our core with a number:** IoU against the city's polygons, and "% of held-out parcels placed in the correct fee tier."
- **Resource system:** water infrastructure, not guilt.
- **Make the invisible visible:** the anatomy file's lesson [F].
- **Local hook:** the Huron River, Malletts and Allen Creeks.
- **Real space data:** IMERG rainfall.

### Closest past winners, and how Raindrop differs
- **Water Monitor** (MHacks 14 MLH GCP; [Devpost](https://devpost.com/software/water-monitor-96zalt)) [F]. A passive Great Lakes heatmap. Ours is a personal decision with a trained model.
- **F.L.U.D.D** (MHacks 14 GCP 1st; [Devpost](https://devpost.com/software/f-l-u-d-d)) [F]. Basement sensors that alert you. Ours goes after the upstream cause, needs no hardware, and runs every rain.
- **Watt's Up** [F]. The same imagery-segmentation shape, but a different target and **labels taken from a city billing system**.
- **Prior art to name:**
  - address-to-outfall tracers: MWMO's "Path to the River" ([MWMO](https://www.mwmo.org/learn/storymap/)) and ALCOSAN's "Flush It" ([3 Rivers](https://www.3riverswetweather.org/about-wet-weather-issue/understanding-sewer-collection-system/flush-it-interactive-tracing-tool)) [V-search];
  - HRWC's Adopt-a-Storm-Drain map ([HRWC](https://www.hrwc.org/volunteer/adoptastormdrain/)) [V-search];
  - AquaDash (GovHack 2022, roof area for rain harvesting) [V-search].
  - **Our difference:** a trained imperviousness model that generalises nationwide on NAIP, plus measured storm depth, plus the fee and the fix, plus live coordination.

### Technical core we build
1. **Impervious segmentation.**
   - Data: NAIP 2022 (0.6 m RGB-NIR, Planetary Computer) tiles, with masks rasterised from the city's 2023 parcel polygons (24,400) and the building footprints.
   - Model: SegFormer-B0 or a small U-Net (`segmentation_models_pytorch`).
   - Evaluation: hold out two neighbourhoods. Report IoU, per-parcel area error and **fee-tier accuracy**. Baseline to beat: an NDVI + brightness rule.
   - Note: NAIP is aerial, not space. That's fine for the model. The space data is the rain.
2. **Storm-network graph.** Directed edges `USNODEID → DSNODEID` from 36,348 mains. Snap the parcel to the nearest downhill catch basin (1-ft contours are in the city GIS) and trace to the outfall. Compute upstream impervious area per pipe and a Manning full-pipe capacity check at 1 in/hr, which yields the "overloaded pipe" map.
3. **Rain.** GPM IMERG Early half-hourly for the last storm. It's a 0.1° cell, so it gives storm depth and timing, not street-level detail. Label that. The fallback is NOAA MRMS radar (not space), also labelled.
4. **Storm Night.** A live shared table of the 50 catch basins with the most upstream impervious area. Claim → cleared → photo. Texts go out before IMERG or NWS-forecast storms.

### Demo (3:00)
1. **0:00, hook.** "An inch of rain on your roof and driveway is about 1,200 gallons. In 2021, 30,000 Detroit homes flooded, mostly basements."
2. **0:20.** The judge's address: our mask over the aerial photo, the city's polygon overlaid, both areas, and the fee tier.
3. **0:50.** "Replay last storm": IMERG rain and droplets flowing roof → catch basin → pipes → creek → Huron, with a clock and gallons.
4. **1:30.** Add a 150 sq ft rain garden: gallons to pipe fall, and the credit appears. A Grok Imagine render of their yard with the garden, labelled "illustration".
5. **2:00.** City view: overloaded pipes. Storm Night: the judge claims a drain on their phone and the second screen updates live.
6. **2:30.** Tech: IoU and fee-tier accuracy on held-out neighbourhoods; 36,348 pipes traced; scales anywhere NAIP exists.

### Sponsor tracks (natural only)
- **SpaceX "Make it Legendary"**: satellite rainfall is the input, Grok Imagine renders the fix, built in Cursor. *Unverified* whether Earth-observation data counts as "space data" [F SUMMARY open question]. Ask at the expo.
- **SpacetimeDB**: Storm Night is a genuinely multi-user, real-time state problem: drains, claims, live map.
- **Figma Best Design.**
- Photon or ElevenLabs only if the storm texts or calls ship. Don't stack them by default.

**Fun track:** Judged by an LLM.

### Build plan (18 h)
- **P1, ML.**
  - 6:30–9 PM: NAIP tile fetch + mask rasterisation.
  - 9 PM–1 AM: train (Colab, Kaggle or Modal GPU) and evaluate.
  - 1–3 AM: batch-infer the city.
- **P2, network and rain.**
  - 6:30–10 PM: pull mains, basins and manholes, build the graph and the trace.
  - 10 PM–1 AM: capacity check.
  - 1–3 AM: IMERG ingest. **Gate at 2 AM:** IMERG or the labelled MRMS fallback.
- **P3, frontend.** Figma (1 h), then deck.gl `TripsLayer` droplets along traced pipes, 3D lot, rain-garden toggle.
- **P4, live layer.** SpacetimeDB module (drains table, claim/clear reducers), Storm Night UI, Grok Imagine call, Devpost.
- **Gates:** 10 PM, first validation IoU; midnight, trace works for 3 addresses; 8 AM, feature freeze; 10–12, video, Devpost, rehearsal.

### Risks
- GPU access for training: fall back to a smaller model at 256 px, or the NDVI rule as a labelled baseline.
- NAIP (2022) vs. labels (2023) date mismatch, so a few parcels changed. Use the 2020 layer to drop parcels that changed.
- IMERG is coarse (about 10 km); label it.
- Earthdata login needed (the team signs up).
- Pipe direction or connectivity gaps in city GIS: trace only where connected, and show "gap" honestly.
- Recognition and money are weaker than Drafty's (above). Carbon is absent.

**Scores [I]:** win 6 · non-niche 6 · feasibility 7 · demo wow 9 · sponsor fit 8 · originality 6.

---

## 3. Idea 3: **Shift**: the car trips your street could drop

**One-liner.** Type your address and text Shift your weekly places ("Kroger on Packard twice a week, North Campus every weekday"). For each trip it shows the best non-car option: TheRide or Blue Bus, or a bike or e-bike route on **low-stress** streets. It gives the time penalty, how many days a year Michigan weather makes riding reasonable (20 years of NASA POWER daily data), and the dollars and CO₂ of going car-light. The city view ranks the **unbuilt miles of Ann Arbor's All Ages & Abilities bike network** by how many car trips each would remove. Toggle one, and watch the low-stress bikeshed jump across Stadium Blvd.

### Who and how many
- **Ann Arbor residents commute 43.0% drive-alone, 7.2% transit, 2.1% bike and 28.7% work from home** [V, ACS 2024 5-yr].
- **Transport is about 26% of Ann Arbor's emissions** (A2ZERO newsletter, search summary) [V-search].
- **About half of adults in large US metros are "interested but concerned" cyclists** (Dill & McNeil 2016; [TRR](https://journals.sagepub.com/doi/10.3141/2587-11)) [V-search].
- **A new car costs $12,863 a year** to own and run (AAA, Sept 2026; [AAA](https://newsroom.aaa.com/2026/09/aaa-new-vehicle-ownership-costs-hit-12863-annually/)) [V-search].
- **Ann Arbor's AAA network:** 102 miles planned, 26 built as of Oct 2022, target 2035 ([Ann Arbor Observer](https://annarborobserver.com/building-a-bike-safe-city/)) [V].
- **U-M affiliates ride TheRide free** with an Mcard (M-Ride) [V-search].

### How often
Daily trips, plus a morning text: "41°F, dry: e-bike to North Campus 14 min via the Fuller path; bus 4 at 8:12."

### Why it isn't niche, and the honest limit
- Everyone travels daily, and "would you bike if it felt safe?" lands instantly.
- **But** it is the least original of the three:
  - the city already publishes a bike-stress map;
  - PeopleForBikes' Bicycle Network Analysis already scores low-stress connectivity by census block ([city rating](https://cityratings.peopleforbikes.org/cities/ann-arbor-mi)) [V-search];
  - Walk Score and Google Maps exist.
- It also risks reading as the saturated "trip footprint calculator". Lead with the money and the segment ranking, never "your commute's carbon."

### Watt's Up bar
- **Instant:** address in.
- **Trained core:** a mode-shift model on NHTS 2022, plus our own low-stress (LTS) classifier and graph.
- **Money + carbon:** car-light dollars a year, and tonnes.
- **City/policy:** ranks the city's own plan.
- **Visual:** a bikeshed animation.
- **Weak spot:** originality.

### Winning-formula match and closest winners
- **Precedent:** transport is open space. The anatomy file found no 2024–25 Sustainability entry about transport [F].
- **Campus-data precedents won sponsor prizes, not the track:** Fastr Food (MHacks 14: U-M dining-hall wait times; [Devpost](https://devpost.com/software/fastr-food)) and MBathroom (MHacks 2025: the U-M building API; [Devpost](https://devpost.com/software/mbathrooms)) [F].
- **How Shift differs from BNA and the city map:** it predicts trips shifted rather than just connectivity, and adds a personal trip plan and weather days.

### Technical core we build
1. **LTS classifier** on OSM (Furth/Mekuria criteria: lanes, speed, cycleway tags, crossings) feeding a low-stress graph with reachability (igraph).
2. **Mode-shift model** trained on 2022 NHTS public microdata. Inputs: trip distance, purpose, age, household vehicles. It is combined with a low-stress-connectivity factor. *Caveat:* NHTS has no route-stress field, so that factor comes from the literature. Say so.
3. **Segment ranking.** Greedy marginal gain over the planned AAA segments, scored by trips shifted per mile.
4. **GTFS times** via r5py or OpenTripPlanner; elevation for grades; NASA POWER daily data for rideable days.

### Demo (3:00)
1. The judge's address and three trips by text. Their small low-stress bikeshed blooms on the map.
2. A trip table with car / bus / e-bike times and "N rideable days a year."
3. Toggle a planned segment: the bikeshed jumps, and city counters move (households connected, car trips a week, t CO₂, dollars).
4. The ranked list of remaining segments.
5. Tech and honesty.

### Sponsor tracks (natural only)
- **Photon iMessage agents**: the trip diary *is* a conversation.
- **Figma Best Design.**
- **No SpaceX:** weather and elevation are garnish.

**Fun track:** Judged by an LLM.

### Build plan (18 h)
- **P1:** NHTS model (6:30–11 PM), then segment ranker.
- **P2:** OSM pull + LTS + graph (6:30 PM–midnight), then GTFS routing.
- **P3:** map and bikeshed animation.
- **P4:** Photon trip-diary agent, NASA POWER rideable days, Devpost.
- **Gate at midnight:** address → bikeshed → one toggle works.

### Risks
- Originality vs. BNA and the city's own map.
- The NHTS stress gap.
- Theme reading as "urban planning".
- An Ann Arbor bike layer in usable form is unverified; compute LTS from OSM instead.

**Scores [I]:** win 5 · non-niche 8 · feasibility 7 · demo wow 7 · sponsor fit 5 · originality 4.

---

## 4. Considered and rejected (lens ideas that failed the bar)
| Idea | Why not |
|---|---|
| Lead service line predictor (Ann Arbor publishes `WaterServiceLeadMaterialAll`) | BlueConduit, which grew out of U-M's own Flint work, already does it, and it's health/justice more than sustainability |
| "Outage-proof": DTE outage risk + home battery | A rare-event adaptation story (the anatomy file's warning) |
| Landfill methane from space (Arbor Hills, EMIT/Tanager) | Duplicates round 1's Plume Patrol and sits next to saturated food-waste ideas; weak money |
| Night-light waste / bird "Lights Out" (VIIRS) | 500 m resolution; no personal decision; judges don't "have" it |
| Snow-melt-on-roof heat-loss census (Sentinel-2) | 10 m pixels can't resolve houses; Michigan winter clouds; unvalidatable in 18 h. Kept only as Drafty's ECOSTRESS stretch |
| Parking lots → housing near transit | Reads as housing policy rather than Sustainability; no personal decision |
| Campus fume hoods / lab freezers | Real energy hogs, but a narrow user group (lab users) |
| Lawn-to-meadow from imagery | Students have no lawns; next to the saturated canopy idea |
| Contrails from GOES over DTW | Not city scale; consumer decision too weak |

## 5. Recommendation
**Build Drafty.**
- It is the only one of the three that is instantly recognised (heating bill), broad (every renter), frequent (monthly bills, yearly leases) and has a local policy hook that is live right now: the Green Rental Housing Ordinance, effective January 2026, with HERD covering sales only.
- It is the only one where I could **verify the core works tonight**: R² 0.55 → 0.76 with six answers, and a 35% narrower band.
- Its conversational layer does real work rather than decoration.

**Weakness.** Satellite data is not in Drafty's core unless the ECOSTRESS stretch lands. If the team wants a satellite-first project above all, **Raindrop** is the honest alternative: the strongest visual and the strongest SpaceX + SpacetimeDB fit. It trades away instant recognition, money size and carbon.

**First 60 minutes if Drafty:**
1. Download ResStock MI (2 minutes) and rerun the feasibility script on the renter subset only.
2. Pull 35,110 footprints and check that structure types map cleanly.
3. Settle Photon vs. Relay for the interview.
4. Ask three teammates for last winter's DTE bills (the real-bill check).
5. Create an Earthdata account (the team does this) and try to fetch one ECOSTRESS pre-dawn granule before the 2 AM gate.

---

## Sources

**Team research (read):** `/Users/anvaytodkar/Code/mhacks/results/year-research/2025.md`, `2024.md`; headings, tables and key sections of `2023.md`, `2021.md`, `2020.md` (`2022.md` = no event); `/Users/anvaytodkar/Code/mhacks/results/SUMMARY.md` ("Lessons from six years of MHacks winners", "Cross-check"); `/Users/anvaytodkar/Code/mhacks/results/pivot-ideas/01-past-winner-patterns.md`, `00-synthesis.md`; `/Users/anvaytodkar/Code/mhacks/results/pivot-round2/01-mhacks-winner-anatomy.md` (§3–8), `02-peer-sustainability-winners.md` (§2, §7); `/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/13-debate-and-verdict.md`, `07-spacex-make-it-legendary.md`, `08-spacetimedb.md`.

**Past winners cited:** Watt's Up https://devpost.com/software/watt-s-up · FarmX https://devpost.com/software/farmx-zpw0yq · Chilladelphia https://devpost.com/software/chilladelphia · ZoneZero https://devpost.com/software/zonezero · Wattson https://devpost.com/software/wattson-5btsyd · V²/R https://devpost.com/software/v-r · FocusFlow https://devpost.com/software/focusflow-ucwma0 · Water Monitor https://devpost.com/software/water-monitor-96zalt · F.L.U.D.D https://devpost.com/software/f-l-u-d-d · Fastr Food https://devpost.com/software/fastr-food · MBathroom https://devpost.com/software/mbathrooms · SolarVista https://devpost.com/software/solarvista

**Data and APIs (checked tonight):**
- ResStock 2024.2 MI files: https://oedi-data-lake.s3.amazonaws.com/?list-type=2&prefix=nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2024/resstock_amy2018_release_2/metadata_and_annual_results/by_state/state=MI/ · upgrades lookup: https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2024/resstock_amy2018_release_2/upgrades_lookup.json
- Ann Arbor GIS: https://a2maps.a2gov.org/a2arcgis/rest/services/OSI/BuildingFootprints/FeatureServer/0 · https://a2maps.a2gov.org/a2arcgis/rest/services/ImperviousSurfaces/MapServer/7 · https://a2maps.a2gov.org/a2arcgis/rest/services/ITPIPES_Storm/MapServer · https://a2maps.a2gov.org/a2arcgis/rest/services/PublicServices/Catchbasins/MapServer/0 · services index https://a2maps.a2gov.org/a2arcgis/rest/services
- Census Reporter (ACS 2024 5-yr, B25003/B25040/B08301/B25044): https://api.censusreporter.org/1.0/data/show/latest?table_ids=B25003,B25040&geo_ids=16000US2603000,04000US26,01000US
- NASA POWER: https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=T2M,HDD18_3&community=RE&longitude=-83.74&latitude=42.28&start=2024&end=2025&format=JSON
- GPM IMERG via CMR: https://cmr.earthdata.nasa.gov/search/granules.json?short_name=GPM_3IMERGHHE&bounding_box=-83.8,42.2,-83.6,42.35&page_size=5&sort_key=-start_date
- ECOSTRESS via CMR: https://cmr.earthdata.nasa.gov/search/granules.json?short_name=ECO_L2T_LSTE&bounding_box=-83.80,42.22,-83.67,42.32&temporal=2025-12-01T00:00:00Z,2026-03-15T00:00:00Z
- NAIP via Planetary Computer STAC: https://planetarycomputer.microsoft.com/api/stac/v1
- NHTS 2022: https://nhts.ornl.gov/assets/2022/download/csv.zip · Overpass: https://overpass-api.de/api/interpreter · TheRide GTFS: https://www.transit.land/feeds/f-dps2-annarborareatransportationauthority
- EIA Michigan gas prices: https://www.eia.gov/dnav/ng/NG_PRI_SUM_DCU_SMI_M.htm

**Policy, statistics and prior art:**
- Ann Arbor Green Rental Housing FAQ: https://www.a2gov.org/media/yi5cussn/grh-faq.pdf · passage: https://www.wemu.org/wemu-news/2025-06-18/ann-arbor-steps-closer-to-a-carbon-neutral-future-as-green-rental-housing-ordinance-passes · compliance: https://concentratemedia.com/500-ann-arbor-rentals-now-in-compliance-with-new-green-housing-ordinance/
- HERD: https://www.a2gov.org/news/posts/over-1-000-ann-arbor-homes-now-have-home-energy-scores/ · https://www.cbsnews.com/detroit/news/new-ann-arbor-ordinance-requires-home-sellers-to-disclose-home-energy-score/
- Early Leasing Ordinance: https://www.michigandaily.com/news/early-leasing-changes-move-forward-in-ann-arbor-city-council/
- Ann Arbor SEU: https://planetdetroit.org/2026/01/ann-arbor-sustainable-energy-utility/ · https://www.detroitnews.com/story/news/local/michigan/2026/09/17/ann-arbor-utility-prepares-expand-solar-program/91581179007/
- A2ZERO / GHG: https://www.a2gov.org/sustainability-innovations-home/carbon-neutrality-home/ · https://www.a2gov.org/media/dcnn3ilj/10_a2zero_newsletter_oct2023.pdf
- Minneapolis Time-of-Rent disclosure: https://www2.minneapolismn.gov/business-services/licenses-permits-inspections/rental-licenses/renter-protections/energy-disclosure
- UtilityScore / HotPads: https://www.inman.com/2015/07/10/utilityscores-can-show-which-of-2-identically-priced-homes-actually-costs-more/ · Green Home Audit: https://devpost.com/software/green-home-audit
- Ann Arbor stormwater rates: https://www.a2gov.org/systems-planning/water-resources/stormwater/stormwater-rates/ · credits: https://www.a2gov.org/systems-planning/water-resources/stormwater/residential-stormwater-credits/ · Sanborn impervious study: https://sanborn.com/project/impervious-surface-calculation-case-study/ · adopt-a-drain: https://www.a2gov.org/ann-arbor-water/ann-arbor-water-news/adopt-a-storm-drain-to-help-with-fall-leaves/
- Detroit drainage charge: https://detroitmi.gov/departments/water-and-sewerage-department/dwsd-customer-service/drainage-charge · 2021 flood: https://detroitmi.gov/news/city-expands-private-sewer-repair-program-reach-75-more-neighborhoods-hardest-hit-2021-flood
- WKU Stormwater Utility Survey 2024: https://digitalcommons.wku.edu/cgi/viewcontent.cgi?article=1019&context=seas_faculty_pubs
- Michigan CSO volume: https://cleanwater.org/michigans-outdated-and-dangerous-combined-sewer-systems · NCA5 Midwest: https://nca5.climate.us/chapter/24
- Tracing tools: https://www.mwmo.org/learn/storymap/ · https://www.3riverswetweather.org/about-wet-weather-issue/understanding-sewer-collection-system/flush-it-interactive-tracing-tool · https://www.hrwc.org/volunteer/adoptastormdrain/ · AquaDash: https://medium.com/@olafwrieden/we-built-a-service-to-calculate-rainwater-harvesting-from-satellite-images-using-image-segmentation-b7fad8985753
- Transport: Dill & McNeil 2016 https://journals.sagepub.com/doi/10.3141/2587-11 · AAA 2026 https://newsroom.aaa.com/2026/09/aaa-new-vehicle-ownership-costs-hit-12863-annually/ · Ann Arbor bike network https://annarborobserver.com/building-a-bike-safe-city/ · PeopleForBikes https://cityratings.peopleforbikes.org/cities/ann-arbor-mi · M-Ride https://ltp.umich.edu/transportation-alternatives/mride

**My own computations (reproducible):** scratch script `fit.py` and the ResStock CSVs in this session's scratchpad (`/private/tmp/claude-501/-Users-anvaytodkar-Code-mhacks/da74b3f8-1169-43ff-8beb-579fcf8ef895/scratchpad/`). It filters to gas-heated homes and fits sklearn `HistGradientBoostingRegressor` (mean plus 0.1/0.9 quantiles) on an 80/20 split with `random_state=0`.

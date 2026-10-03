# Ideas — Technical-core / wow lens

## Prompt given (excerpt)
> Your lens: Technical-core / wow lens. Ideas whose winning edge is an impressive technical core the team builds itself (a trained/fine-tuned model, computer vision, a clever algorithm, real-time systems, hardware sensing with the FREE-WILi) — the kind of build that wins Grand Awards at MHacks — applied to a broad sustainability problem.
>
> Propose 3 distinct, concrete ideas for the Sustainability main track that (a) clearly fit the winning formula, (b) are NOT niche by the definition above and reach the Watt's Up bar on all five points while being original, (c) are not on the saturated list, and (d) are buildable by 4 students in ~18 h with a strong 3-minute demo. For each, verify the key data/APIs exist and are accessible, name the closest past winners and how yours differs, and list only the sponsor tracks that fit naturally.

*Written Sat Oct 3, 2026, ~7 PM EDT. Tags: **[V]** I checked it today at the linked source. **[S]** I computed it today from verified public data (a spike, not product code). **[F]** From a team research file (its own citations apply). **[I]** Inference or estimate.*

Inputs read: `year-research/2020–2025.md` (both researchers), SUMMARY.md "Lessons from six years" and "Cross-check", `pivot-ideas/00-synthesis.md` and `01-past-winner-patterns.md`, `pivot-round2/01-mhacks-winner-anatomy.md` and `02-peer-sustainability-winners.md`, and `sponsor-tracks/07-spacex-make-it-legendary.md`.

---

## TL;DR

| # | Idea | One line | Technical core the team builds | Broad / how often | Money + carbon | Home → city | Wow moment |
|---|---|---|---|---|---|---|---|
| **1 (top pick)** | **Hearth** | Type any address and get that home's heating bill, its carbon, the right-size heat pump and the one upgrade to do first. Then zoom out to every home in Ann Arbor. | A surrogate model trained on **18,756 DOE EnergyPlus simulations of Michigan homes** × 17 upgrade packages, fed by building geometry from aerial and satellite imagery, plus the team's own tariff engine | Every home heats. Heating is **42% of household energy** (EIA). Agent texts every week in heating season | $/yr and t CO2e side by side for each upgrade | One house → all of Ann Arbor (A2ZERO, HERD, the new city energy utility) | The judge types their own address and the 3D house lights up with numbers in seconds |
| 2 | **Pane** | Scan your room with a phone. Every window and wall gets painted with what it costs you this winter, then the $15–60 renter fixes are ranked and the landlord letter is written for you. | LiDAR room capture → the team's **heat-loss solver**, plus a **flashlight-reflection CV test** that tells single from double from low-E glass | 45M US renter households. **44% of Michigan rented units have single-pane windows** [S] | $/winter and kg CO2 for each surface and each fix | Room → whole building (roommates' scans merge live) → city map of rentals | The judge sweeps a phone and the walls turn red or blue in AR |
| 3 | **Load** | See the AI data centers going up on your grid from orbit, measured by a model that counts their chillers and cooling towers, and translated into MW, gallons a day, CO2 and your bill range. | A **fine-tuned detector** for rooftop chillers and cooling towers, a capacity estimator calibrated on Epoch AI's CC-BY site data, and Sentinel-2 change detection | Every ratepayer. Michigan approved **2.4 GW** for two data centers within 25 mi of Ann Arbor in 10 months | Bill range (contested) + water + CO2 | Address → town vote → state commission | A Sentinel-2 time-lapse of the Saline Stargate site, then boxes snap onto 300 chillers |

**Top pick: Hearth.** It is the closest to Watt's Up's shape (address in, a personal decision out, city scale), but it answers a different and bigger question: heating, not solar. It has a counterintuitive Michigan finding that I computed from DOE data today: **for gas-heated Michigan homes, a cold-climate heat pump alone raises the bill in 93% of cases (median −$458/yr) while cutting ~2.6 t CO2e/yr, whereas for propane, electric-resistance and oil homes it saves ~$900–1,250/yr in essentially every case** [S]. So the right answer depends on the house, and that dependence is the product. The judge can try it on their own home, and the technical core is a real trained model with held-out numbers already measured (R² 0.85 on heat-pump savings) [S].

Ideas 1 and 2 share the home-heating domain. They can merge: Pane becomes Hearth's "inside the house" mode. Idea 3 is the most space-native and most visually striking, but it has the weakest answer to "what do I do, and how often?"

---

## 0. The lens, applied

Grand-level MHacks winners each had a core the team built and could name in one sentence: ASI's ACT policy, V²/R's circuit solver, FocusFlow's LSTM, DECO.ai's NeRF pipeline [F 2025/2024/2023]. **No MHacks sustainability winner trained a model or built a solver.** The track winners were technically thin: Wattson's brightness diff, FarmX's random forest, Water Monitor's heatmap [F anatomy §3]. A sustainability project with a real core plus a judge-can-touch-it demo is therefore unusually well placed, both for the track and for a shot at the Grand Award.

Each idea below was run through the anatomy file's one-minute filter (§8) and the peer file's breadth test, which asks "can a judge try it on their own home, photo or bill?". The **open space** the anatomy researcher found was also a guide: no 2024–2025 Sustainability entry was mainly about *heating and cooling of homes or dorms*, *transport*, *campus energy/water*, or *repair/e-waste* [F anatomy §7].

| Filter question | Hearth | Pane | Load |
|---|---|---|---|
| 1. Judge says "I have that" within 5 s | Yes: heating bill, parents' house | Yes: drafty rental | Partly: "my bill keeps rising" |
| 2. Weekly or more | Weekly texts Oct–Apr | Winter comfort is daily; the scan happens once a season | No (alerts only) |
| 3. Visible effect within 20 s | Yes | Yes (AR) | Yes |
| 4. Core that isn't an API call | Surrogate + tariff engine | Solver + optical CV | Detector + estimator |
| 5. One measured number | R² 0.85, MAE $269 [S] | Pane-test accuracy on N windows | MW error vs Epoch AI |
| 6. Touches a resource system | Heating / gas / grid | Building envelope | Grid + water |
| 7. Not on the saturated list | Yes (not rooftop solar) | Yes | Yes (not "green AI") |

---

## 1. Idea 1 (top pick): **Hearth**: every home's heating bill, decoded from above

### One-liner
Type any address. Hearth reads the house from aerial and satellite data (footprint, height, roof, age) and runs a model the team trained on 18,756 DOE building-energy simulations of Michigan homes. In seconds it shows what heating costs that home in dollars and CO2, how big a heat pump it really needs, and the single upgrade to do first, with money and carbon side by side. Then you zoom out to every home in Ann Arbor. You can also text or call Hearth to ask "what should I do first?" or "is this contractor quote right?"

### Who has the problem, and how many
- **Every household heats.** Space heating was **42%** of US residential energy use in RECS 2020 ([EIA](https://www.eia.gov/energyexplained/use-of-energy/homes.php)) [V search].
- **Michigan:** ResStock's Michigan sample represents **4.73 million housing units**. By weight, **76.5% heat with natural gas and 8.7% with propane**; 25% of the models are renters [S, from the files below].
- Michigan uses **more residential propane than any other state**: about 370M gallons, and roughly 320,000 households heat with it ([MPSC Winter Energy Appraisal 2024–25](https://www.michigan.gov/mpsc/-/media/Project/Websites/mpsc/regulatory/reports/energy-appraisal/2024-2025_Winter_Energy_Appraisal.pdf), via search) [V search].
- **Local hooks, all current:**
  - Ann Arbor's **Home Energy Rating Disclosure** ordinance (in force since Mar 12, 2024) requires a Home Energy Score before any single-family home is listed. **About 1,000 homes** have been scored in two years ([a2gov, Mar 12 2026](https://www.a2gov.org/news/posts/over-1-000-ann-arbor-homes-now-have-home-energy-scores/)) [V]. Hearth gives every home an estimate today.
  - The city's **Sustainable Energy Utility** began installing solar and batteries on 80+ homes in the Bryant neighborhood in Sept 2026, with a citywide launch planned for 2027 ([WDIV](https://www.clickondetroit.com/news/local/2026/09/22/ann-arbor-launches-community-owned-solar-utility-with-battery-backup/), [a2gov SEU](https://www.a2gov.org/sustainable-energy-utility/)) [V search].
  - **A2ZERO** targets carbon neutrality by 2030 [V search].

### How often it's used
- **The decision** (replace the furnace, add insulation, or add a heat pump) comes up for every home, and every Ann Arbor sale now triggers an energy score.
- **The pain is monthly**, from October to April. Hearth's agent sends a weekly heating-season text, for example: *"Tuesday hits 19°F. Your house will burn about $9 of gas that day; closing the storm windows saves about $1."* That message comes from the same model run on the forecast (NASA POWER/NOAA temperatures).

### Why it's not niche
The judge brings their own input (their house or their parents' house) and gets a personal number back. This is the peer researchers' most reliable broad shape: Chilladelphia, U-Plan, Watt's Up, ZoneZero [F peer §2A]. Heating is the biggest energy flow in every judge's home. It's October in Michigan, and the heat came on this week.

### The insight that makes it a decision, not a dashboard [S]
I trained nothing on this yet; it is a plain comparison of ResStock Michigan baseline vs. upgrade files, with bills recomputed from energy at flat rates. The rates are $0.20/kWh, $10.5/Mcf gas, $2.50/gal propane and $3.80/gal oil (EIA-based, see Sources). I recomputed bills because ResStock 2024.2's own bill columns are known to be inconsistent ([NREL issue page](https://natlabrockies.github.io/ResStock.github.io/docs/resources/explanations/Issue_2024_2_Electricity_and_Energy_Bills.html)) [V].

| Upgrade (ResStock 2024.2, Michigan) | Gas-heated homes (n=14,251) | Propane (n=1,636) | Electric-heated (n=1,748) |
|---|---|---|---|
| Cold-climate heat pump | **Bill up** in 93%: median **−$458/yr**; −2.6 t CO2e | Saves **$894/yr** median (100%); −3.8 t | Saves **$1,229/yr** (100%); −2.6 t |
| Envelope only ("light touch") | Saves **$134/yr** median (100%); −0.8 t | Saves $265/yr; −0.8 t | Saves $325/yr; −0.7 t |
| Heat pump + envelope | Bill up in 84%; median −$271/yr; −3.0 t | Saves $1,012/yr; −4.0 t | Saves $1,366/yr; −2.9 t |

The pitch line: **"The internet says heat pumps save money. In Michigan, for 3 in 4 homes, they don't yet, but they do cut 2.6 tons. For the 320,000 propane homes they save about $900 a year. Hearth tells you which house you live in."** This plays the same role as ZoneZero's CalFIRE insight that beat five other wildfire entries [F peer §1]. Hearth shows a rate slider, because the result depends on the gas-to-electric price ratio.

### Technical core the team builds
1. **Surrogate model (the named core).** Gradient-boosted models trained on all 18,756 Michigan ResStock models × baseline + 16 upgrade packages. They predict annual energy by fuel, CO2e, design heating load (kBtu/h) and per-upgrade deltas from ~12 observable inputs: vintage, floor area, stories, building type, heating fuel, foundation, attic, garage, wall type, county, cooling type, water-heater fuel. Bills come from **the team's own tariff engine** (DTE/Consumers volumetric rates), not ResStock's flawed bill columns.
   - **Spike today, 80/20 held-out split** [S]:
     - annual energy bill R² 0.71 (MAE $694 on a $2,587 median)
     - CO2e R² 0.69
     - design heating load R² 0.72 (MAE 12 kBtu/h)
     - **cold-climate heat-pump $ savings R² 0.85 (MAE $269)**
     - envelope-only savings only R² 0.40 (MAE $114), because insulation levels aren't observable, so Hearth asks two questions (attic insulation depth; single or double windows)
     - training takes under a second on a laptop, and one prediction takes ~5 ms
2. **Geometry from above.**
   - Building footprint, and from it floor area, from Microsoft's US Building Footprints (Michigan file, 162 MB) [V].
   - NAIP 0.6 m aerial imagery (2022 over Ann Arbor) for the roof view [V].
   - Vintage from Washtenaw parcel data, where Regrid reports 80% year-built coverage [V search; county download not tested], otherwise from the user.
   - Climate: NASA POWER satellite-derived temperature and degree-days (Ann Arbor HDD at base 18.3 °C = 3,784 °C-days/yr) [V API call].
3. **Right-sizing and quote check.** The predicted design heating load, plus ResStock's own sizing output (`out.params.size_heating_system_primary_k_btu_h`), gives a tonnage range. The agent compares it to a contractor's quote.
4. **City run.** Batch every residential footprint in Ann Arbor through the model. A 3D city colored by heating CO2 per square foot, with filters like "propane + leaky" or "where a heat pump saves money now", and totals such as "N homes, $X M/yr, Y kt CO2e". Add an equity overlay (ACS income → energy burden), Watt's Up-style.
5. **Benchmark (honesty).** Rewiring America's Residential Electrification Model API already predicts address-level upgrade impacts from ResStock ([REM docs](https://docs.rewiringamerica.org/api/residential-electrification-model)) [V search]. Hearth does **not** call it for answers. It uses REM as an outside check: "our surrogate agrees with Rewiring America within X% on 20 Ann Arbor addresses". That is a measured number, and it answers the judge who says "this exists".

### Demo (3:00 at the table)
1. **0:00** "Heating is 42% of the energy in an American home, and Michigan turned the heat on this week. Type your address." Hand the judge the laptop.
2. **0:15** The map flies into the house in 3D (Google Photorealistic 3D Tiles; MapLibre extrusion as fallback), with the footprint outlined. "Built ~1950s, ~1,600 sq ft, gas furnace. Heating: $X/yr, Y t CO2e."
3. **0:40** **Do this first:** money and carbon bars for envelope, heat pump, and both. For a gas home it reads "insulate first; a heat pump costs ~$450/yr more today but cuts 2.6 t". Then the teammate types a rural propane address: "heat pump now, saves ~$900/yr."
4. **1:10** **Right size:** "Your design load is ~38 kBtu/h, about a 3-ton cold-climate unit." A teammate texts Hearth "Contractor quoted 5 tons for $21k" and the reply explains the oversizing (Relay/Photon thread or a Grok Voice call on speaker).
5. **1:45** Zoom out to Ann Arbor in 3D, each home colored. Filter "where a heat pump saves money now" to get totals. One sentence on HERD and the city energy utility: "the city already scores homes at sale; we just scored all of them."
6. **2:20** **The core:** "trained on 18,756 DOE simulations; 0.85 R² on held-out heat-pump savings; within X% of Rewiring America's model on 20 local homes."
7. **2:45** Close. The real-life video shows a teammate's actual house, its real winter gas bill next to Hearth's estimate.

### Sponsor tracks that fit naturally
| Track | Genuine use |
|---|---|
| **SpaceX "Make it Legendary"** | Real space data goes in: NASA POWER satellite-derived temperatures (CERES/MERRA-2) and building geometry from imagery. The agent is a **Grok Voice** call ("what should I do first?") and the team builds in Cursor. The space core is moderate, not central; claim only what's true [F sponsor 07]. |
| **Relay or Photon** (pick one) | The text/call channel for the quote check and the weekly heating-season message. Pick based on which one rang at the workshop [F 13-verdict]. |
| **Figma Best Design** | The report is a design problem: two currencies (money and carbon) and a counterintuitive answer. |
| ElevenLabs | Only if Grok Voice isn't used. The two voice engines conflict [F sponsor 07]. |

Not natural: Nessie (financing would be a token), FREE-WILi, FinchNode, SpacetimeDB, Fetch.ai.

### Fun tracks
Judged by an LLM (submit a rubric-shaped Devpost). Not Useless AI or Dumbest Idea.

### Build plan (≈18 h, 4 people; P1 = ML, P2 = geo/data, P3 = frontend, P4 = agent + story)
| Time | P1 | P2 | P3 | P4 |
|---|---|---|---|---|
| 7–8 PM | Pull the 17 MI parquet files (~190 MB; 2 min today) | Microsoft footprints MI; NAIP STAC; NASA POWER client | Repo, Cursor rules, map shell | Gates: Relay vs Photon, xAI key, Google Maps billing |
| 8–11 PM | Train surrogates for each target; tariff engine; held-out metrics | Address → geocode → footprint → features | Report page: money/carbon bars, "do this first" | Agent skeleton with tool calls into the model API |
| 11 PM–2 AM | Sizing model; REM comparison on 20 addresses (if key) | Parcel join or 2-question fallback | 3D house view; rate slider | Quote-check flow; first real-life video takes |
| 2–6 AM | Sleep in shifts. P2 runs the city batch overnight (Ann Arbor footprints) | | | |
| 6–9 AM | Uncertainty bands; propane / gas story numbers | Equity overlay (ACS) | City 3D view + filters | Weekly-text flow; Figma pass |
| 9–11:30 AM | Freeze model | Cache all demo addresses offline | Polish | Devpost (~500 words), video, rehearse 3:00 ×5 |

Stretch, only if ahead by 2 AM: a **propane-tank detector** on NAIP imagery to find propane homes from above. Residential propane-tank detection looks under-studied in the literature [V search], so this would be novel. 0.6 m pixels make a 500-gal tank ~5×2 px, so it is risky [I].

### Data and APIs verified today
- **ResStock 2024.2 AMY2018, Michigan:** baseline + 16 upgrade parquet files (7–12 MB each) on public OEDI S3. Downloaded and parsed: **18,756 models, 288 columns**, including bills, CO2e (LRMER), heating peak load and heating system size [V].
- The upgrade list: ENERGY STAR / cold-climate / ultra-efficient / geothermal heat pumps, each ± light-touch envelope ± full appliance electrification, plus envelope only [V].
- NREL's bill-inconsistency notice for 2024.2; the workaround is to recompute from energy [V].
- NASA POWER climatology API returned Ann Arbor T2M, HDD18.3 and irradiance with no key [V].
- Microsoft US Building Footprints, `Michigan.geojson.zip` (162 MB, HTTP 200) [V].
- NAIP over Ann Arbor via Planetary Computer STAC: 2022, 0.6 m [V].
- Google Photorealistic 3D Tiles: 1,000 free root-tile sessions/month, then $6 per 1,000 [V search]. MapLibre extrusions as fallback.
- Rewiring America REM API (signup required) [V search].
- Ann Arbor HERD and SEU [V].
- EIA prices: MI residential gas $10.02–11.32/Mcf (Jan–Mar 2026) [V search]; MI residential electricity ~20–23 ¢/kWh in 2026 per sites citing EIA [V search, secondary].

### Closest past winners and how Hearth differs
- **Watt's Up** (HackPrinceton F25 Best Overall): address → solar. Hearth keeps that shape but asks the heating question. Heating is a bigger energy flow than rooftop generation, and it is not on the saturated list.
- **SolarVista** (MHacks 2024 MLH MATLAB) and **Chilladelphia** (PennApps XXV) are the address/siting precedents. Hearth is not siting or canopy.
- **FarmX** (MHacks 2024 Sustainability): a model trained on public data with a Michigan hook. Hearth trains on 18,756 physics simulations and outputs a household decision.
- **V²/R** (MHacks 2024 Grand Prize) won with its own solver and no LLM. Hearth's core is likewise a model and an engine, not a chat call.
- **ZoneZero** (TreeHacks 2026) won its pool on one counterintuitive insight; Hearth's is "heat pump vs envelope depends on your fuel".

### Risks
1. **"Rewiring America already does this."** Say so in the first minute. Hearth's additions are its own trained model with published error, a Michigan-specific counterintuitive answer, sizing and quote checks, the city twin, and use of REM as a benchmark.
2. **Simulated, not metered.** ResStock is synthetic. Show bands, never single points. Validate against a teammate's real gas bill and against REM.
3. **Envelope savings are poorly predicted (R² 0.40).** Ask the two questions; show it as "range".
4. **The rate assumption drives the gas-vs-heat-pump result.** Keep the slider and cite EIA. Re-run with DTE/Consumers tariff sheets in hour 1.
5. **Space data is real but not central.** If the SpaceX judges want orbit as the core, Load (Idea 3) is the better SpaceX play.
6. **3D tiles billing setup.** Fallback is MapLibre extrusions from the footprints.

---

## 2. Idea 2: **Pane**: point your phone at the room and see what each window costs you

### One-liner
Scan your room with an iPhone. Pane builds a 3D model, finds every window and door, tells single from double from low-E glass with a flashlight-reflection test, and paints each surface by what it costs you this winter in dollars and CO2. Then it ranks renter-friendly fixes (cellular shades, film kits, rope caulk, door sweeps) and writes the landlord letter. When roommates scan their rooms, the whole house model assembles live.

### Who has the problem, and how many
- **45.3M US renter households** (2024) [V search, Census via secondary].
- **44% of Michigan rented units have single-pane windows** (28% of all Michigan homes), and **18.7% of Michigan renters heat with electricity**, about twice the share among owners [S, ResStock MI].
- Windows cause **25–30%** of residential heating and cooling energy use ([DOE Energy Saver](https://www.energy.gov/energysaver/energy-efficient-windows)) [V search].
- Tightly installed cellular shades cut window heat loss **40%+**, about **10%** of heating energy ([DOE](https://www.energy.gov/energysaver/energy-efficient-window-attachments)) [V search].
- Every student in an old Ann Arbor rental knows the cold window.

### How often
- The discomfort is daily all winter. The scan happens once a room per season, and again after every move; students move every year.
- The building model accumulates as more tenants scan.

### Why it's not niche
Renters are a third of households and most of the student judges. The input is the room the judge is in, and the payoff is personal and immediate. It also passes the anatomy test of a visible effect within 20 seconds [F anatomy §8].

### Technical core the team builds
1. **Heat-loss solver (the named core, V²/R-style).** Input: Apple RoomPlan's parametric output (walls, windows, doors with dimensions and transforms) [V Apple]. For each surface, the solver computes UA from glazing type and vintage defaults, applies infiltration by window type, and multiplies by local heating degree-days from NASA POWER (Ann Arbor 3,784 °C-days/yr) [V]. It converts the result to $ and kg CO2 for the unit's heating fuel and rate.
   - Back-of-envelope [I]: a 1.8 m² single-pane window conducts about 950 kWh of heat per winter in Ann Arbor. That is roughly $35 on gas or $190 on electric baseboard, and about 190 kg CO2 on gas.
   - The honest message: the money is small on gas, big on electric heat, and comfort matters either way.
2. **Optical pane test (CV).**
   - The phone flashlight shines at the glass at about 45°. OpenCV finds the specular highlights: their count (2 for single pane, 4 for double), their spacing (the air gap) and the color of one pair (the low-E coating).
   - This automates the well-known "lighter test" ([example](https://installixwnd.ca/blog/identifying-low-e-on-installed-windows/)) [V search].
   - **Measured number:** classification accuracy on 25+ campus and apartment windows, labeled overnight.
3. **Fix ranking and landlord loop.** DOE/AERC-backed savings for each attachment, cost and payback, then an auto-written landlord letter with the numbers.
4. **Live building twin.** Each roommate's scan streams into a shared building model (SpacetimeDB), which supports a building-level report and an anonymized city map of scanned rentals.

### Demo (3:00)
1. **0:00** "44% of Michigan rentals still have single-pane windows. Here's what yours costs you."
2. **0:10** The judge sweeps the iPhone around the booth corner. The RoomPlan outline appears, and the web view shows walls and windows colored from blue to red with $/winter labels.
3. **0:45** Pane test on a window (shaded with a jacket if the room is bright): "4 reflections, one pinkish → double, low-E."
4. **1:10** Pre-scanned teammate apartments from the night before. "Jake's 1920s Kerrytown room: three single-pane windows, $X/winter on electric baseboard; $45 of cellular shades returns 40% of that heat."
5. **1:40** Roommates' scans assemble live into the whole house, then the landlord letter is generated.
6. **2:10** The core and its numbers: pane-test accuracy, scan-vs-tape-measure error, and "we scanned N student rooms in Ann Arbor tonight; median window heat loss $X." That last one is a real number measured at the event, which no sustainability winner has had [F anatomy §6].

### Sponsor tracks that fit naturally
- **SpacetimeDB.** Several roommates scanning at once into one shared, live building model is that sponsor's real-time multiplayer archetype.
- **Figma Best Design.** AR overlays and the landlord report.

Not natural: SpaceX (no real space data beyond degree-days), Relay/Photon (a letter by text adds little), Nessie, FREE-WILi, Fetch.ai, ElevenLabs.

### Fun tracks
Judged by an LLM.

### Build plan (≈18 h)
| Time | P1 (iOS) | P2 (physics) | P3 (web viewer + SpacetimeDB) | P4 (pane CV + data) |
|---|---|---|---|---|
| 7–8 PM | **Gate:** does a teammate own a LiDAR iPhone (12 Pro or newer Pro)? Run Apple's RoomPlan sample | U-values, infiltration, HDD client | three.js scene from the RoomPlan JSON | Capture 10 test photos at a window |
| 8 PM–1 AM | Export CapturedRoom JSON + upload; torch-burst capture | Solver, $/CO2 per surface, fix catalog | Coloring, labels, room → building merge | Highlight detector, count/spacing/color |
| 1–2 AM | Scan teammates' rooms (4 apartments) | Validate the solver on one room against hand calculation | Landlord letter | **Label 25+ windows across campus at night** (dark = ideal) |
| 2–6 AM | Sleep in shifts | | | |
| 6–11:30 AM | Polish the AR overlay | Accuracy table | City/building map | Devpost, video, rehearsal |

### Data and APIs verified today
- Apple RoomPlan outputs the dimensions of recognized components (walls, windows, doors) as parametric USD/USDZ, and **requires a LiDAR iPhone or iPad** [V].
- DOE window figures (25–30%; cellular shades 40% / 10%) [V search].
- ResStock Michigan window and tenure fields (computed) [S].
- NASA POWER HDD [V].
- The reflection-count and color method for pane and low-E identification is documented by window installers [V search].

### Closest past winners and how Pane differs
- **DECO.ai** (MHacks 16 1st) scanned furniture into 3D. Pane scans a room into a **physics model with a price tag**.
- **FocusFlow** (MHacks 2024 Runner-Up): camera + the team's own model + a participatory demo.
- **Wattson** (MHacks 2025 Greenprint) made energy waste visible. Pane does it without a pet or guilt, on the building envelope, and with a fix attached.
- **Commercial prior art:** Heat Engineer and Heatworx sell LiDAR heat-loss surveys **to heating engineers** ([Heat Engineer](https://heat-engineer.com/en/features/lidar-technology/), [Heatworx](https://heatworx.io/)) [V search]. Pane is for renters, adds the optical pane test, and closes the loop with the landlord.

### Risks
1. **The hardware gate.** RoomPlan needs LiDAR, and the app must be native iOS. Fallback: ARKit corner-tapping on any iPhone, or WebXR hit-test on Android Chrome.
2. **The pane test needs darkness.** The demo hall is bright at 1 PM. Use a jacket as a hood and show the night-labeled accuracy table.
3. **Dollars per window are small on gas heat.** Lead with comfort, the electric-heat cases and building totals, not single-window dollars.
4. **City scale is crowdsourced and thin in 18 h.** Present the building twin and say "the city map grows with users".
5. **The problem overlaps Idea 1.** It is a different user and a different core, but the same domain.

---

## 3. Idea 3: **Load**: the AI data centers coming to your grid, measured from orbit

### One-liner
Type your address. Load shows every AI data center planned or rising on your utility's grid. It watches construction from Sentinel-2, and a model the team fine-tuned counts each site's rooftop chillers and cooling towers in aerial imagery. Those counts become megawatts, gallons of water a day and tons of CO2, plus the documented range of what it may mean for your bill. Call or text Load to ask what it means for you, or have it draft your comment for the public hearing.

### Who has the problem, and how many
- **Everyone who pays an electric bill.**
- US data centers used **4.4%** of US electricity in 2023 (176 TWh), heading to **6.7–12%** by 2028. Direct water use was **66 billion liters** in 2023 ([LBNL 2024](https://eta-publications.lbl.gov/sites/default/files/2024-12/lbnl-2024-united-states-data-center-energy-usage-report_1.pdf)) [V search].
- **Within 25 miles of this room:**
  - **Saline Township, 1.4 GW** (OpenAI/Oracle). Approved Dec 18, 2025. DTE must expand capacity by about a quarter ([Michigan Public](https://www.michiganpublic.org/environment-climate-change/2025-12-18/michigan-regulators-approve-saline-twp-data-center-request-with-conditions)) [V].
  - **Google, Van Buren Township, 1 GW.** MPSC approved it **Oct 1, 2026**, two days ago ([Planet Detroit](https://planetdetroit.org/2026/10/dte-google-data-center-contract-approval/)) [V].
  - **U-M's $1.25B computing center** in Ypsilanti Township [V same source].
  - Data centers are eyed in at least 10 Michigan towns ([Bridge Michigan](https://bridgemi.com/michigan-environment-watch/data-centers-eyed-in-at-least-10-michigan-towns-how-they-might-change-state/)) [V search title].

### How often
This is the weak point: individuals check it occasionally. Weekly alerts help: a new filing or visible construction near you (Sentinel-2 had **55 clear scenes over Saline in the past 12 months**) [V]. Town votes are happening now, statewide.

### Why it's not niche
The bill and the water are everyone's, the story is in this week's news, and the judge can type their own address. The risk is that "what do I do?" is civic (comment, vote, ask for conditions), not a household purchase.

### Technical core the team builds
1. **Cooling-equipment detector.** Fine-tune YOLOv8 to find air-cooled chillers, dry coolers and cooling towers in NAIP 0.6 m aerial imagery. Labels come from ~15 operational sites in Epoch AI's database, hand-labeled in Roboflow (~2 h; each site has dozens to hundreds of units) [I].
2. **Capacity estimator.** Map detected units to Epoch's **chiller spec table (143 models: cooling kW, fan count, dimensions)** and **cooling-tower table (527 rows)**. That gives cooling capacity, then IT MW. Calibrate on Epoch's published MW for 72 powered sites, and report held-out error against Epoch's own 80% CI of about 1.4× ([Epoch AI](https://epoch.ai/data/ai-data-centers), CC-BY) [V; files downloaded].
3. **Construction tracker.** Sentinel-2 bare-soil and built-up index change on the site polygon, which should reproduce Epoch's hand-written timeline for **"OpenAI Stargate Michigan"**: land clearing Dec 4, 2025; groundwork Mar 12, 2026; target 988 MW IT / 1,383 MW total by end-2028 [V, Epoch timelines CSV].
4. **Water and carbon.** Cooling type (evaporative towers vs dry coolers, visible from above) gives a water-use range. MW × hours × a grid emission factor gives CO2.
5. **Bill exposure, shown as a contested range, never a single number:**
   - CMU: +8% average generation cost and +30% power-sector emissions by 2030 nationally ([CMU](https://www.cmu.edu/work-that-matters/energy-innovation/data-center-growth-could-increase-electricity-bills-8)) [V search].
   - NC State: 6–29% national average, up to 57% in some regions ([NCSU](https://news.ncsu.edu/2026/05/data-centers-power-bills/)) [V search].
   - The MPSC record: a ~$300M/yr net *benefit* to other DTE customers [V Michigan Public].

### Demo (3:00)
1. **0:00** "Two days ago Michigan approved a gigawatt data center about 20 miles from this table, on top of the 1.4 GW one in Saline. Type your address."
2. **0:15** The globe flies to Saline. A Sentinel-2 time-lapse plays from the Dec 2025 clearing through Sept 2026, with "construction detected Mar 2026" matching Epoch's record.
3. **0:50** Switch to an operational site. Boxes snap onto rooftop chillers: "312 units → ~X MW (Epoch: Y MW)". Cooling towers detected, so "~Z million gallons a day".
4. **1:30** Your grid: approved MW vs. your utility's load, CO2, and the bill range with every source on screen. A Grok Voice call answers "what does this mean for me?", and the agent drafts a public comment.
5. **2:20** The core: detector precision/recall, MW error vs Epoch on held-out sites.

### Sponsor tracks that fit naturally
- **SpaceX "Make it Legendary"**: the strongest natural fit of the three ideas. Real satellite imagery is the core input (Sentinel-2), the agent runs on Grok Voice, and the team builds in Cursor [F sponsor 07]. Caveat [I]: SpaceXAI runs its own large data centers, so frame Load as transparency, not opposition.
- **Relay or Photon**: alerts and the conversational agent.
- **Figma**: the globe and report.

### Fun tracks
Judged by an LLM.

### Build plan (≈18 h)
| Time | P1 (CV) | P2 (geo) | P3 (frontend) | P4 (data, agent, story) |
|---|---|---|---|---|
| 7–9 PM | Pick 15 Epoch sites with NAIP coverage; label in Roboflow | Planetary Computer STAC: NAIP + Sentinel-2 chips | Globe (deck.gl/Cesium) | Epoch CSVs → site DB; Michigan MPSC facts |
| 9 PM–1 AM | Fine-tune YOLOv8n; capacity regression | Change-detection series for Saline / Van Buren | Time-lapse player; detection overlay | Bill-range card with citations; agent |
| 1–6 AM | Sleep in shifts; held-out eval runs overnight | | | |
| 6–11:30 AM | Accuracy table | Cache every demo tile | Polish | Devpost, video, rehearsal |

### Data and APIs verified today
- **Epoch AI CSVs downloaded:** `data_centers.csv` (93 sites; 72 with power >0, 13,746 MW total), `data_center_chillers.csv` (143 specs), `data_center_cooling_towers.csv` (527), `data_center_timelines.csv` (549 rows, including water use in MGD). Includes the Stargate Michigan row. License: CC-BY [V].
- **NAIP** via Planetary Computer STAC: 0.6 m. **This is aerial, not satellite**; label it that way [V].
- **Sentinel-2 L2A** via the same STAC: 55 scenes with <10% cloud over Saline, Oct 2025 – Sep 2026 [V].
- MPSC approvals and the DTE capacity statement [V]. LBNL, CMU and NCSU figures [V search].

### Closest past winners and how Load differs
- **OverSEA** (PennApps XXVI 3rd overall): satellite detections on a 3D globe for a global problem. Load is local and personal, and counts equipment to estimate capacity.
- **GridVeda** (TreeHacks 2026): grid infrastructure, a measured accuracy number, a 3D view.
- **Dynamic Load Balancing** (MHacks 2024 MLH Streamlit) scheduled compute load. Load measures the physical build-out instead.
- **Epoch AI and the Washington Post** already analyze data centers from imagery, by hand ([WaPo, Sep 28 2026](https://www.washingtonpost.com/technology/interactive/2026/09/28/satellite-images-show-scale-americas-data-center-build-out/)) [V search]. Load automates Epoch's method and points it at your address.

### Risks
1. **Weakest on "used often" and "what do I do".** The team rejected niche ideas for the same reason; this one is broad, but its action is civic.
2. **The bill number is contested.** Show the range with sources. Never invent a personal $.
3. **Political charge, with a SpaceXAI judge.** Stay descriptive.
4. **Detection at 0.6 m and the labeling time.** Fallback: hand-labeled counts for the demo sites, with the detector shown on two of them.
5. **"Epoch already does this."** Credit them on screen; the automation and the personal lens are the additions.

---

## 4. Considered and rejected (this lens)
- **Contrails from GOES** (train on Google's OpenContrails, 20,544 labeled GOES-16 examples [V search], then attribute contrails to flights via ADS-B). The best space-data wow, but no money in it for a person and a professional user (airlines). It fails two of the five bar points.
- **Lead service lines** (BlueConduit-style prediction; a Flint hook). Broad and local, but no carbon, and judges would read it as health.
- **Smart-meter disaggregation trained on ResStock 15-min profiles.** Frequent and broad, but Opower, Bidgely and Sense exist, the demo is a chart, and it overlaps Hearth.
- **Apartment "true cost" (rent + utilities + commute).** Strong for students, but it reads as a housing app, and Ann Arbor-style energy disclosure covers sales, not rentals.
- **FREE-WILi reading utility meters over sub-GHz** (rtlamr-style). Real wow, but high hardware risk for this team and a privacy problem.
- **Open windows in steam-heated dorms.** Students say "I have that", but the actor is campus facilities.

## 5. Recommendation
**Build Hearth.** It meets all five Watt's Up points:
- Anyone can type an address.
- The team trains a real model and has held-out numbers.
- Money and carbon sit in one view, with a counterintuitive local answer.
- It scales from one home to all of Ann Arbor, with HERD, SEU and A2ZERO as hooks.
- The demo is a 3D house and a 3D city.

The conversational layer has a real job in Hearth: checking quotes and sending heating-season texts. If the team wants more participatory wow, fold Pane in as Hearth's "inside" mode after midnight. If the team wants SpaceX as the anchor prize, Load is the most space-native of the three.

**First 60 minutes for Hearth:**
1. Re-run the spike with DTE/Consumers tariff sheets.
2. Freeze the 12 input features.
3. Sign up for the Rewiring America key.
4. Set up Google 3D Tiles billing, or commit to MapLibre.
5. Decide Relay vs Photon.
6. Pick 3 demo addresses: one gas house in Ann Arbor, one propane house in rural Washtenaw, and a teammate's real house with its real bill.

---

## Sources

**Team research (read)**
- `/Users/anvaytodkar/Code/mhacks/results/year-research/2020.md`, `2021.md`, `2022.md`, `2023.md`, `2024.md`, `2025.md`
- `/Users/anvaytodkar/Code/mhacks/results/SUMMARY.md` (Lessons from six years; Cross-check)
- `/Users/anvaytodkar/Code/mhacks/results/pivot-ideas/00-synthesis.md`, `01-past-winner-patterns.md`
- `/Users/anvaytodkar/Code/mhacks/results/pivot-round2/01-mhacks-winner-anatomy.md`, `02-peer-sustainability-winners.md`
- `/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/07-spacex-make-it-legendary.md`, `13-debate-and-verdict.md`

**Past winners cited**
- Watt's Up https://devpost.com/software/watt-s-up · Chilladelphia https://devpost.com/software/chilladelphia · ZoneZero https://devpost.com/software/zonezero · OverSEA https://devpost.com/software/oversear · GridVeda https://devpost.com/software/gridveda · SkySplat https://devpost.com/software/skysplat
- SolarVista https://devpost.com/software/solarvista · FarmX https://devpost.com/software/farmx-zpw0yq · V²/R https://devpost.com/software/v-r · FocusFlow https://devpost.com/software/focusflow-ucwma0 · DECO.ai https://devpost.com/software/deco-ai · Wattson https://devpost.com/software/wattson-5btsyd · Dynamic Load Balancing https://devpost.com/software/dynamic-load-balancing-for-energy-efficient-cloud-computing · Artificial Sandwich Intelligence https://devpost.com/software/artificial-sandwich-intelligence

**Data and APIs (verified today)**
- ResStock 2024.2 AMY2018 Michigan files (OEDI S3): https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2024/resstock_amy2018_release_2/metadata_and_annual_results/by_state/state%3DMI/parquet/
- ResStock 2024.2 documentation: https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2024/resstock_tmy3_release_2/resstock_documentation_2024_release_2.pdf
- NREL bill issue: https://natlabrockies.github.io/ResStock.github.io/docs/resources/explanations/Issue_2024_2_Electricity_and_Energy_Bills.html
- NASA POWER API: https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=T2M,HDD18_3,ALLSKY_SFC_SW_DWN&community=RE&longitude=-83.743&latitude=42.281&format=JSON
- Microsoft US Building Footprints (Michigan): https://minedbuildings.z5.web.core.windows.net/legacy/usbuildings-v2/Michigan.geojson.zip
- Planetary Computer STAC (NAIP, Sentinel-2 L2A): https://planetarycomputer.microsoft.com/api/stac/v1/search
- Google 3D Tiles pricing: https://developers.google.com/maps/billing-and-pricing/pricing · https://www.woosmap.com/blog/google-maps-api-pricing-breakdown
- Rewiring America REM API: https://docs.rewiringamerica.org/api/residential-electrification-model · https://www.rewiringamerica.org/tools/api
- Regrid Washtenaw parcels (year-built coverage): https://app.regrid.com/store/us/mi/washtenaw
- Apple RoomPlan: https://developer.apple.com/augmented-reality/roomplan/
- Epoch AI data centers (CC-BY): https://epoch.ai/data/ai-data-centers · CSVs: https://epoch.ai/data/data_centers/data_centers.csv · https://epoch.ai/data/data_centers/data_center_chillers.csv · https://epoch.ai/data/data_centers/data_center_cooling_towers.csv · https://epoch.ai/data/data_centers/data_center_timelines.csv
- OpenContrails: https://arxiv.org/abs/2304.02122 · https://sites.research.google/gr/contrails/public-datasets/

**Facts and local hooks**
- EIA use of energy in homes (space heating 42%): https://www.eia.gov/energyexplained/use-of-energy/homes.php
- EIA Michigan electricity profile: https://www.eia.gov/electricity/state/michigan/ · EIA Michigan natural gas prices: https://www.eia.gov/dnav/ng/NG_PRI_SUM_DCU_SMI_M.htm · Michigan residential electricity 2026 (secondary, citing EIA): https://www.priceofelectricity.com/michigan
- MPSC Winter Energy Appraisal 2024–25 (propane): https://www.michigan.gov/mpsc/-/media/Project/Websites/mpsc/regulatory/reports/energy-appraisal/2024-2025_Winter_Energy_Appraisal.pdf
- Ann Arbor HERD: https://www.a2gov.org/news/posts/over-1-000-ann-arbor-homes-now-have-home-energy-scores/ · https://www.a2gov.org/media/ncxdl1vh/herd-faq-092723.pdf
- Ann Arbor SEU: https://www.a2gov.org/sustainable-energy-utility/ · https://www.clickondetroit.com/news/local/2026/09/22/ann-arbor-launches-community-owned-solar-utility-with-battery-backup/
- DOE windows: https://www.energy.gov/energysaver/energy-efficient-windows · https://www.energy.gov/energysaver/energy-efficient-window-attachments
- Census renter households (secondary): https://www.census.gov/newsroom/press-releases/2024/acs-5-year-homeowners-renters.html
- Pane/low-E reflection test: https://installixwnd.ca/blog/identifying-low-e-on-installed-windows/
- LiDAR heat-loss prior art: https://heat-engineer.com/en/features/lidar-technology/ · https://heatworx.io/
- Saline data center approval: https://www.michiganpublic.org/environment-climate-change/2025-12-18/michigan-regulators-approve-saline-twp-data-center-request-with-conditions · https://www.michigan.gov/ag/news/press-releases/2025/12/18/ag-nessel-on-the-mpsc
- Google Van Buren approval (Oct 1, 2026): https://planetdetroit.org/2026/10/dte-google-data-center-contract-approval/
- Michigan data-center towns: https://bridgemi.com/michigan-environment-watch/data-centers-eyed-in-at-least-10-michigan-towns-how-they-might-change-state/
- LBNL 2024 data center report: https://eta-publications.lbl.gov/sites/default/files/2024-12/lbnl-2024-united-states-data-center-energy-usage-report_1.pdf
- CMU bill study: https://www.cmu.edu/work-that-matters/energy-innovation/data-center-growth-could-increase-electricity-bills-8 · NC State: https://news.ncsu.edu/2026/05/data-centers-power-bills/
- Washington Post satellite data-center piece: https://www.washingtonpost.com/technology/interactive/2026/09/28/satellite-images-show-scale-americas-data-center-build-out/

**Spike scripts (scratch, not product code):** `/private/tmp/claude-501/-Users-anvaytodkar-Code-mhacks/da74b3f8-1169-43ff-8beb-579fcf8ef895/scratchpad/wow/spike2.py` (surrogate R²/MAE) and the fuel-split savings table, both run on the Michigan ResStock parquet files in the same folder.

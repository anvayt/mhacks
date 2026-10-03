# Pivot Round 2 — Synthesis

## Prompt given (excerpt)
> Your job: final synthesis (impartial; you generated none of these). Combine the judges (weight the niche skeptic heavily — the team has rejected two ideas as niche; anything the skeptic scores ≥ 6 on niche-ness needs a strong argument). Merge near-duplicate ideas. Produce a ranked **top 3** with, for each: name, one-liner, why it's not niche, how it matches what won before (cite winners), the technical core, the 3-minute demo, the natural sponsor tracks, an 18-hour build plan split across 4 people, and the main risks. Give a clear single recommendation.
>
> Context: MHacks 2026, Sustainability main track, hacking ends 12:00 PM Sun Oct 4. Quality bar: Watt's Up (HackPrinceton Fall 2025 Best Overall). Rejected as niche: "Clean Hours" (dryer scheduling) and "Fern on Call" (heat/smoke check-ins for older people living alone).

*Written Sat Oct 3, 2026, ~7 PM EDT. Tags: **[V]** I checked it myself today at the linked source. **[F]** From a team research file (named; its own citations apply). **[I]** Inference or estimate.*

Inputs read: the six year files (`results/year-research/2020–2025.md`), the "Lessons from six years" and "Cross-check" sections of `results/SUMMARY.md`, `results/pivot-ideas/01-past-winner-patterns.md`, all six `results/pivot-round2/` files (01–06), sponsor files 06 (Photon), 07 (SpaceX), 11 (Relay) and 13 (verdict), the 12 ideas and the 3 judges' verdicts.

---

## TL;DR

**Build Hidden Rent (merged).** You paste a listing link or type an address and see the heating bill the listing doesn't show, as a range in dollars and CO₂. You get the three questions that would most narrow that range, and you answer them by text. After you move in, your real bill recalibrates it, and if the unit is leaky, Hidden Rent drafts the request to the landlord. Zoomed out, it is a map of every Ann Arbor rental by wasted heat.

| Rank | Idea (after merging) | Weighted score* | Skeptic's niche score | One line |
|---|---|---|---|---|
| **1** | **Hidden Rent** (Hidden Rent + both Draftys) | **7.75** (best part) | **2** | "Listing sites guess utilities from square footage. Same-size Michigan apartments differ by about $1,200 a year. We show the difference before you sign." |
| 2 | **CarLight** (+ Shift's city view) | 6.1 | 2 | "Find out in 10 seconds whether you need your car, and how much you keep if you don't." |
| 3 | **Hearth** (+ Pane as a later "inside" mode) | 6.0 | 5 | "Type your address: heat pump or insulation first? In Michigan the answer depends on your fuel." |

\*Weighted score = 25% past-MHacks judge + 25% sustainability expert + 50% niche skeptic, out of 10. The skeptic gets double weight because they stand in for the team.

**Why #1 wins:**
- It is the only idea that all three judges put in their top two.
- The skeptic and the sustainability expert both rated it 8.
- All three judges gave it a niche score of 2.
- After the merge it fixes each judge's main complaint:
  - The past-MHacks judge said the pipeline was too big for 18 h. It now uses one training set instead of four.
  - The sustainability expert said picking a better unit only moves emissions around. The impact now comes from the landlord fix and the city map.
  - The skeptic said Drafty's questions can't be answered before signing. The picker now asks only questions you can put to the landlord before you sign.

**The honest cost:** satellite data is a supporting input (NASA POWER degree-days), not the core. The two ideas with satellite data at the core, Raindrop and Load, failed the niche test (§7).

---

## 1. How the judges combine

| Idea | Past-MHacks | Sustainability | **Skeptic** | Weighted | Niche (PJ / SE / **Sk**) | Outcome |
|---|---|---|---|---|---|---|
| Hidden Rent | 7 | 8 | **8** | **7.75** | 2 / 2 / **2** | **Merged → #1** |
| Drafty: January bill | **7.5** (PJ #1) | 6.5 | 7 | 7.0 | 2 / 3 / 2 | **Merged → #1** (question picker + ResStock model) |
| Drafty: landlord call | 7 | 7.5 | 5 | 6.1 | 3 / 4 / 4 | **Merged → #1** (Green Rental Housing fix path; the AI phone call is cut) |
| CarLight | 5.5 | 7 | 6 | 6.1 | 2 / 2 / 2 | **#2** |
| Hearth | 6.5 | 7.5 (SE #2) | 5 | 6.0 | 4 / 3 / 5 | **#3** |
| Buy It Once | 5 | 5.5 | 5 | 5.1 | 2 / 3 / 2 | Next in line (absorbs Mend) |
| Raindrop | 6 | 5.5 | 4 | 4.9 | 5 / 5 / **7** | Cut: skeptic niche ≥ 6 |
| Pane | 6 | 5 | 4 | 4.75 | 4 / 5 / **6** | Cut: skeptic niche ≥ 6; later an "inside" mode of #1 or #3 |
| Load | 5.5 | 5.5 | 4 | 4.75 | 5 / 6 / **6** | Cut: skeptic niche ≥ 6 |
| Seatmate | 5 | 5 | 4 | 4.5 | 3 / 3 / 4 | Cut: stock carpool idea, synthetic riders |
| Shift | 4.5 | 5 | 4 | 4.4 | 3 / 3 / 4 | Merged into CarLight's city view |
| Mend | 4 | 4.5 | 4 | 4.1 | 4 / 4 / 4 | Merged into Buy It Once; its AI calls are cut |

**Niche ≥ 6 (Raindrop, Pane, Load): I found no argument strong enough to overrule the skeptic.**
- **Raindrop.** The user cares when a basement floods, which is the rare-event trap that sank Fern on Call. Ann Arbor's money is $8.59 a quarter, and there is no carbon line [F 04].
- **Load.** It is checked occasionally, and the action is a public comment, the "rare and civic" pattern the team already rejected.
- **Pane.** One building component and a ~$35-per-window fix is the Clean Hours failure mode in another room. It also needs a LiDAR iPhone [F 05].

---

## 2. Merges and cuts

| Cluster | Merged into | What survives | What is cut, and why |
|---|---|---|---|
| Renter heating: Hidden Rent, Drafty (Jan bill), Drafty (landlord call) | **#1 Hidden Rent** | Hidden Rent's name, listing-link input, real-meter validation, bill calibration and city layer. Drafty's ResStock quantile model and question picker, both already feasibility-tested. Drafty-call's Green Rental Housing (GRH) checklist and rebates as the fix path | RECS, Chicago benchmarking, Overture and the canopy map (the judge said there were too many pipelines). The AI call to the landlord: the skeptic called it awkward and sponsor-driven, the past-MHacks judge said it can read as a gimmick, and BidBot already won with AI calls ([Devpost](https://devpost.com/software/bidbot)) [F 06]. A drafted email does the same job |
| Home heating, owners: Hearth, Pane | **#3 Hearth** | Surrogate model, fuel-split insight, sizing, city map | Pane: LiDAR and native iOS gate, pane test unreliable in a bright hall |
| Transport: CarLight, Shift, Seatmate | **#2 CarLight** | Personal car verdict, switching model, NASA weather, city scenario. Shift's bike-segment toggle as the alternative city scenario | Shift's own traffic-stress (LTS) classifier: R5 already routes by traffic stress through r5py's `max_bicycle_traffic_stress` ([r5py docs](https://r5py.readthedocs.io/stable/reference/reference.html)) [V]. Seatmate: carpool apps are a stock prompt, and the demo runs on synthetic riders |
| Durability: Buy It Once, Mend | Buy It Once (next in line, not top 3) | Review-mined survival model plus the iFixit repair branch | Mend's parallel shop calls (BidBot) |

---

## 3. #1 (recommended): **Hidden Rent**, the heating bill the listing doesn't show

### One-liner
Paste any Zillow, Apartments.com or Redfin link, or type an Ann Arbor address. In about 5 seconds you see:
- the unit's **January heating bill as a range**
- its dollars a year and tonnes of CO₂ a year
- where it ranks among same-size rentals
- **the 3 questions to ask the landlord** that would narrow the range most

Text the answers and watch the range shrink. After move-in, text a photo of your DTE bill. Hidden Rent recalibrates to your unit, tells you whether the bill is normal for the weather, and, if the unit is leaky, drafts the request to your landlord. The request names the Green Rental Housing checklist points the fix earns and the rebates that pay for it. Zoomed out, every rental in Ann Arbor is shaded by its predicted excess heating cost.

### Why it isn't niche
- **Who:** 45.0M US renter households (34.8%) [F 04, ACS 2024 via Census Reporter]. Ann Arbor has 27,544 renter households, 54.5% of its households [F 03/04]. The city counts about 31,500 rental units, median build year 1964, which predates Michigan's first energy code in 1977 [F 04, city GRH FAQ](https://www.a2gov.org/media/yykptaqy/grh-faq.pdf).
- **How often:**
  - Every housing search, comparing many listings. Renters move about 4× as often as owners [F 03].
  - Every winter bill, as a check that it's normal for the weather.
  - Every lease decision, which is yearly for students under Ann Arbor's Early Leasing Ordinance [F 03/04].
- **One sentence:** "Same rent, up to about $1,200 a year apart, and you can't see it until January." For 800–1,200 sq ft gas-heated Michigan rentals, simulated annual energy bills run from $1,052 (P10) to $2,254 (P90) [F 04, computed from NREL ResStock].
- **The 5-second test:** "My roommate and I split a $300 January DTE bill." Every judge has paid a heating bill, and most were renters once.
- **Neither rejected failure mode applies.** Clean Hours was one appliance and a minor behaviour. This is a 12-month lease and the largest energy flow in the home. Fern on Call was a small group and a rare event. This is every renter, every winter.

### How it matches what won before
- **Broad problem, specific demo, a core the team built.** That is the top-prize recipe at MHacks [F 01-anatomy §5]:
  - FocusFlow (2024 Runner-Up) trained its own LSTM and let the judge take part through the webcam ([Devpost](https://devpost.com/software/focusflow-ucwma0)).
  - V²/R (2024 Grand) wrote its own circuit solver ([Devpost](https://devpost.com/software/v-r)).
  - Hidden Rent's equivalent: a model trained on simulations, corrected against real meters, plus a question picker. The judge takes part by answering on their phone while the range narrows. That is the same participatory beat as FocusFlow and MotionSurfer ([Devpost](https://devpost.com/software/motionsurfer)).
- **The best-performing peer shape: address in, personal decision out.** Watt's Up ([Devpost](https://devpost.com/software/watt-s-up)), Chilladelphia ([Devpost](https://devpost.com/software/chilladelphia)) and ZoneZero ([Devpost](https://devpost.com/software/zonezero)) all won with it. Address and imagery projects had the best sustainability hit rate of any category across 351 peer entrants: 4 track wins from ~9 entries [F 02].
- **Local hook**, as V²/R used the EECS 215 lab, FarmX used Michigan farms ([Devpost](https://devpost.com/software/farmx-zpw0yq)) and F.L.U.D.D used the SE Michigan floods ([Devpost](https://devpost.com/software/f-l-u-d-d)):
  - Ann Arbor's Green Rental Housing ordinance took effect **Jan 6, 2026**. Units need **70 of 308 checklist points** through Jul 5, 2028, then 110 ([a2gov](https://www.a2gov.org/news/posts/city-of-ann-arbor-s-green-rental-housing-ordinance-goes-into-effect-jan-6-2026/)) [V].
  - HERD energy-score disclosure covers sales only [F 03/04].
  - Minneapolis already requires time-of-rent energy disclosure, but only for buildings with 5+ units and under 50,000 sq ft ([city summary](https://lims.minneapolismn.gov/Download/FileV2/20402/Energy-Disclosure-Policies-Summary-Readable.pdf)) [V search snippet]. So old houses split into rentals fall through there too.
- **A measured impact number:**
  - No MHacks sustainability winner has measured impact. Carbon Footprint Extension gave no CO₂ method, and Dynamic Load Balancing gave no savings figure [F 01-anatomy].
  - Hidden Rent shows held-out error against **real Ann Arbor meters** and real bills.
- **It touches a resource system rather than guilt.** That is the FarmX and SolarVista pattern. Its output is a decision (which lease, what to ask, what to fix), not a dashboard [F 01-anatomy §6, F 02 §4].
- **Open space.** No 2024–25 MHacks Sustainability entry was about home heating [F 01-anatomy §7].
- **How it differs from Watt's Up:**
  - Watt's Up asks what your roof could *make*. Hidden Rent asks what your apartment will *cost*.
  - It serves renters, who can't install anything.
  - There is no roof segmentation.
  - It shows an uncertainty band that the interview shrinks.

### Technical core the team builds (one sentence for the judge)
"A heating-bill model trained on 18,756 DOE-simulated Michigan homes, checked and corrected against real Ann Arbor meters, that asks the questions that most narrow your bill."

1. **Bill model.** LightGBM quantile regression (P10/P50/P90) for heating energy and CO₂, trained on **NREL ResStock 2024.2 Michigan**. That is 18,756 models on public S3 with no key, and the baseline file is 60.5 MB [F 04/05].
   - **Inputs from the address:** floor area (city footprint × storeys, from the **35,110 city building footprints**), building type, and year built (from the listing, else the ACS block-group median). Fuel defaults to gas, which 70.7% of Ann Arbor homes use [F 04].
   - **Already tested tonight** on 14,341 gas-heated homes [F 04]:

     | Inputs | Held-out R² | MAE | P10–P90 width |
     |---|---|---|---|
     | Public-record features only | 0.55 | $507 | $1,596 |
     | + 6 renter-answerable features | 0.76 | $363 | $1,041 (35% narrower) |

   - **Calibration fix:** coverage was 0.73–0.78 against a nominal 0.80, so add split-conformal calibration (about 20 lines).
   - **Pricing:** bills are priced by the team's own tariff code (DTE rates, EIA Michigan prices). ResStock 2024.2's bill columns are officially flagged as inconsistent [F 05].
2. **Question picker.**
   - For each candidate question, take the ResStock rows consistent with the answers so far. Split them by each possible answer, and ask the question with the smallest expected P10–P90 width. That is empirical conditional quantiles, with no new model.
   - **Only questions a renter can answer before signing:** single- or double-pane windows, top/middle/bottom floor, any insulation or air-sealing work since a given year, heating fuel and who pays, and "what was last January's gas bill?" (ask the current tenant).
   - The top 3 questions *are* the "3 questions to ask the landlord." That answers the skeptic's objection that "windows frost inside?" can't be answered before you sign.
3. **Real-meter check (sim to real).**
   - Ann Arbor's benchmarking feature service is openly queryable and has **monthly** gas and electric readings. In 2023 it covered 116 multifamily properties and 17.7M sq ft [F 03].
   - Fit each building's heating slope against NASA POWER heating degree-days (a PRISM-style change-point fit). Predict the same buildings with the ResStock model, then apply a leave-one-building-out linear correction. **Report the held-out error.**
   - **Lead with the spread, not the per-building fit.** Metered EUI runs about 3× from P10 to P90, and the heating slope per 1,000 sq ft varies about 6× [F 03]. The per-building fit's median R² of 0.95 is high by construction, as the past-MHacks judge noted. The spread is the evidence that the problem is real and not a simulation artifact.
4. **Bill calibration.**
   - A vision LLM reads therms and dates from the bill photo. The tenant's own bills get the same degree-day fit, which shifts the estimate.
   - The agent may say only numbers returned by tools (templated money lines).
5. **Money and CO₂.** EPA's 53.06 kg CO₂ per MMBtu of gas (≈5.3 kg per therm), and eGRID RFCM for electricity [F 03/06].
6. **Landlord fix path** (from Drafty-call).
   - The GRH checklist items (air sealing 9 points, attic R-50 9, walls 9, and so on), ranked by **tonnes CO₂ saved per net dollar after rebates** (DTE; Insulate Ann Arbor). That responds to the expert's warning that a cost-only optimiser picks low-carbon-impact items [F 06].
   - It is a sort over about 15 items. No integer program is needed until a judge asks for exact point packing.
   - Output: a drafted email.
7. **City layer.** Batch-score every residential footprint into vector tiles, and rank by excess heating $/sq ft. Name only buildings the city already publishes; aggregate the rest.
8. **Stretch (one person, after the midnight gate, go/no-go at 3 AM): snow on roofs from Sentinel-2.**
   - Sentinel-2 L2A scenes exist for **Feb 15, 2026** (~90% snow) and **Feb 27 / Mar 2, 2026** (~2–4%) [F 03].
   - Test whether early snow loss on large flat roofs correlates with the metered heating slopes.
   - Keep it only if the correlation is real. If it is, satellite data gets a real role, and SpaceX becomes eligible (with Cursor and Grok, below).

### 3-minute demo
- **0:00 Hook.** "Who's split a surprise January DTE bill? Listing sites that estimate utilities use square footage. Same-size Michigan apartments differ by about $1,200 a year in energy. Ann Arbor's median rental was built in 1964, and you sign before the first bill."
- **0:20 The judge's own input.** The judge scans a QR code, joins the iMessage agent and pastes a listing link (or a teammate types an address near campus). The map flies to the building, which extrudes in 3D. The card shows:
  - January $X–$Y
  - $/yr and t CO₂/yr
  - "leakier than N% of same-size Ann Arbor rentals"
  - 3 questions to ask
- **0:50 Watch it happen.** The judge answers two questions by text ("single pane", "top floor"). The range snaps narrower on screen each time, and the uncertainty reduction is shown.
- **1:20 The core.** A scatter of real Ann Arbor buildings' monthly gas against NASA degree-days: the 6× spread, then our model's held-out error on those buildings. "Trained on 18,756 DOE simulations, corrected against real Ann Arbor meters."
- **1:50 After move-in.** A teammate texts a photo of a real DTE bill. "You're 18% above predicted for this weather." Then the ranked fixes: "Air sealing + attic: 18 GRH points, N kg CO₂/yr, Insulate Ann Arbor pays half." The landlord email is drafted.
- **2:20 City scale.** Every rental shaded by excess heating cost. "The worst 10% waste $X and Y t CO₂ a year; start Insulate Ann Arbor here. Minneapolis makes landlords disclose at lease time. Ann Arbor discloses only at sale."
- **2:45 Close, with honesty.** "Simulated stock, checked against real meters and N real bills; every number is a range."

### Sponsor tracks (natural only)
- **Photon iMessage agents.** The interview, the listing-link share and the bill photo *are* the product's input.
  - Judges must be allowlisted on the free tier. A one-hour QR onboarding page fixes that (`POST /users` + redirect) [F sponsor 06], ([docs](https://photon.codes/docs/spectrum-ts/troubleshooting/imessage)).
  - Pitch one surface. Relay is the fallback, but it needs the app on iOS 26 [F sponsor 11].
- **Figma Best Design.** A two-currency report card with an uncertainty band, plus a city map, are real design problems.
- **Fun: Judged by an LLM.** Write a rubric-shaped Devpost of about 500 words with an evaluation table and a Limitations section.
- **Conditional: SpaceX "Make it Legendary."** Enter only if the snow-roof stretch holds, the project is built in Cursor, and Grok runs the agent. Garnish entries lose: 29 of 65 projects opted in at DivHacks [F sponsor 07].
- **Not natural (skip):** ElevenLabs (no call), FREE-WILi, Fetch.ai, Nessie, SpacetimeDB.
- **Fern:** optional as the texting persona ("a houseplant who hates drafts"). Drop it if it costs more than an hour; it is not the premise.
- **One prize per project is the in-person norm** (2024: 30 prizes went to 30 projects) [F SUMMARY]. **The main track is the target.**

### 18-hour build plan
Roles: **P1** data and ML · **P2** backend and geo · **P3** frontend and design · **P4** agent and story.

| Time | P1 (ML) | P2 (backend/geo) | P3 (frontend) | P4 (agent/story) |
|---|---|---|---|---|
| **Start → 8:30 PM** | Pull the ResStock MI baseline; reproduce R² ≈ 0.55 / 0.76 (gate) | Query the Ann Arbor benchmarking and footprint services. **Confirm gas units** against one building's EUI (gate) | Figma frames: card, range bar, city map | Photon hello-world, judge QR onboarding, persona with an only-tool-numbers rule |
| **8:30 PM → midnight** | Quantile models; conformal fix; question picker with pre-signing questions only | Geocoder → footprint → features; NASA POWER monthly HDD; DTE tariff and CO₂; FastAPI `/estimate`, `/next_question` | Next.js + MapLibre 3D extrusion; card; narrowing-range animation | Interview loop on the API; listing-URL slug parser (Zillow URLs contain the address; no scraping) |
| **MIDNIGHT GATE** | Address → card → one texted answer → narrower range on screen, end to end. **If it fails, cut the city layer and the landlord path.** | | | |
| **Midnight → 4 AM** (sleep in 2 h shifts) | Real-meter check: per-building slopes, model vs. meter, leave-one-building-out correction, held-out error | Batch-score the city into vector tiles. *Stretch: Sentinel-2 snow test, go/no-go 3 AM* | City view; core scatter chart | Bill-photo parsing and recalibration; GRH fix ranking; landlord email |
| **4 → 8 AM** | Real-bill check on 3–5 teammates' own DTE bills | Caching; offline fixtures for demo addresses | Figma polish pass; accessibility (contrast, keyboard) | Devpost draft (evaluation table, Limitations); film the video in a real old rental with a real bill |
| **8 AM freeze → 11:30 AM** | Final numbers on screen | Hardening | Backup video | Rehearse the 3:00 five times; README; **submit by 11:30** |

### Main risks
1. **"Zillow and Rent.com already show utilities."**
   - Zillow launched a Cost of Renting summary in 2023 and said utilities would come later ([Zillow](https://zillow.mediaroom.com/2023-07-19-Say-goodbye-to-surprise-fees-New-Zillow-tool-helps-renters-avoid-unexpected-costs)) [V search snippet].
   - Rent.com shows electricity estimates on listings ([BusinessWire, Feb 2024](https://www.businesswire.com/news/home/20240226592602/en/New-Rent.com-Feature-Helps-Renters-Understand-True-Cost-of-Renting)) [V search snippet; method not verified, page returned 403].
   - UtilityScore put 1–100 utility scores on HotPads in 2015 ([Inman](https://www.inman.com/2015/07/10/utilityscores-can-show-which-of-2-identically-priced-homes-actually-costs-more/)) [V].
   - **Answer:** those are area or square-footage averages, or a black-box score. Ours models *this building's heating* with a range, checks it against real meters, narrows it with your answers, and ends in a fix. **Drop the line "Zillow shows the rent; we show the rent you don't see." Lead with the $1,200 same-size spread.**
2. **Simulated vs. real.** ResStock is simulated, and the metered buildings are large (≥20,000 sq ft), not student houses. Show both checks and say so out loud. With only a handful of real bills, label them n=3–5.
3. **"Choosing a better unit just moves emissions"** (sustainability expert). The impact claim lives in the landlord fix path and the city targeting map. Pitch those.
4. **Heat included in rent.** The agent asks first, then reframes as "your landlord pays $X a year of waste."
5. **Messaging platform.** Photon allowlist (onboarding page) and Junk-banner risk (design inbound-first). The same interview runs on the web page.
6. **Data quirks.** Gas units aren't labelled in the city feed (assume Portfolio Manager kBtu, confirm in hour 1). Benchmark addresses are ranges, so join spatially on polygons.
7. **SpaceX temptation.** Claim it only if the stretch is real.

---

## 4. #2: **CarLight**, do you need your car?

### One-liner
Enter your home address and the 3–5 places you go each week. In seconds you see:
- what your car really costs
- which trips a bus, bike, e-bike or walk would honestly cover, from a model trained on how car-light households actually travel
- the dollars and CO₂ you'd keep by going car-light

A 7:30 AM text then tells you the best way to get where you're going today. The city view shows how one transit or bike-network change moves the whole map.

### Why it isn't niche
- Almost everyone travels every day, and the car is the biggest household cost after housing.
- Owning a new car costs $12,863 a year (AAA, Sept 2026) [F 03].
- Transportation is the largest US emissions sector at 28.9% (EPA 2022) [F 03].
- Locally, A2ZERO aims to cut vehicle miles travelled 50%, but VMT rose from 955M (2021) to 1.11B (2023) [F 03].
- All three judges gave it a niche score of 2.
- Weak spot (skeptic): many MHacks students have no car to give up. Pitch to the judges, who are mostly volunteer industry engineers [F SUMMARY], and to the student deciding whether to bring a car to campus.

### How it matches what won before
- **Fastr Food** (MHacks 14, Beginner + Google Cloud 2nd) answered a campus "wait or walk?" question with Maps times ([Devpost](https://devpost.com/software/fastr-food)). CarLight scales that instinct to a $12k-a-year decision, with a trained model.
- **SunLite** (MHacks 14 1st) is the daily-use "I would use this" benchmark ([Devpost](https://devpost.com/software/sunlite-sunrise-lamp)).
- **Self-interest framing on a planet problem** won Sustain-ify HackHarvard 2024 Best Overall ([Devpost](https://devpost.com/software/sustain-ify)) [F 02].
- **A planner view,** like SolarVista (MHacks 2024 MLH MATLAB, [Devpost](https://devpost.com/software/solarvista)).
- **Open space:** no 2024–25 MHacks Sustainability entry was about transport [F 01-anatomy §7].

### Technical core
1. **Switching model** trained on NHTS 2022 public trip files: P(non-car mode | distance, purpose, vehicles per driver, age, density, season), scaled by the routed time ratio.
   - Honest caveat: public NHTS lacks travel times for unchosen modes, so this is a propensity model, not a full logit [F 03].
   - Number on screen: held-out log-loss against a distance-only baseline.
2. **Routing:** r5py (Conveyal R5) with TheRide GTFS and OSM, using R5's built-in traffic-stress limit for bikes [V docs]. An e-bike speed profile with elevation. This is a library; the "we built it" claim rests on items 1, 3 and 5.
3. **Weather viability** from 20+ years of NASA POWER hourly data at the address (MERRA-2 reanalysis): "X% of weekday 8 AM departures from your street were dry and above freezing." Word it as reanalysis, not satellite rainfall [F 03].
4. **Money and CO₂:** AAA costs, fueleconomy.gov MPG, Michigan insurance and parking; EPA per-mile CO₂.
5. **City scenario engine:** car-light potential per H3 cell, recomputed under **one** precomputed change. Pick at midnight:
   - Route 4 every 10 min (synthesized GTFS trips), or
   - one planned All Ages & Abilities bike segment (Shift's idea).

### 3-minute demo
- **0:00** "A new car costs $12,863 a year. Ann Arbor promised to cut driving in half; it went up 16%."
- **0:20** The judge's address and 3 places. An isochrone blooms. Trip cards: bus 18 min, bike 14, car 11 plus parking.
- **0:50** Verdict in $/yr and t CO₂/yr, plus the honesty line: "people like you take trips like this by bus X% of the time."
- **1:15** Dry 8 AM departures at your address, computed from 20 years of NASA data.
- **1:35** The "tomorrow" 7:30 text arrives on the judge's phone (simulated clock). The judge asks "how do I get to Costco?" and gets an answer.
- **2:05** City slider: the scenario toggles, and car-light households and VMT move.
- **2:40** Core numbers and close.

### Sponsor tracks
- **Photon iMessage:** the morning text and Q&A.
- **Figma.**
- **Optional: Capital One Nessie.** Only if the car's real cost is computed from seeded transactions, read and write, the pattern LoadCheck won with [F pivot-ideas/01]. Badge every Nessie figure, and skip it if it reads as a token integration.
- **Fun: Judged by an LLM.**
- **SpaceX:** not natural.

### 18-hour build plan
| Time | P1 (model) | P2 (routing) | P3 (frontend) | P4 (agent/story) |
|---|---|---|---|---|
| Start → 8 PM | Download NHTS 2022; build features | Java 21 + r5py; clip Michigan OSM to Washtenaw with osmium; TheRide GTFS; first matrix | Figma; map shell | Photon hello-world + QR onboarding; car-cost model |
| 8 PM → midnight | Train and evaluate the switching model | `/plan` API (trips × modes × times); NASA POWER weather viability. **9 PM gate:** if r5py isn't routing, use precomputed matrices for preset destinations | Isochrone animation, trip cards, verdict | Morning-text job, Q&A tools |
| **MIDNIGHT GATE** | Judge's address → verdict → text arrives | | | |
| Midnight → 4 AM | Citywide H3 grid for 8 destination types | Precompute one scenario | City map + slider | (Optional Nessie) |
| 4 → 11:30 AM | Numbers on screen | Hardening, cached demo addresses | Polish | Devpost, a real morning bus ride on video with the text arriving; freeze at 8 AM; rehearse; submit by 11:30 |

### Main risks
- **"That's Google Maps or Walk Score."** Open on money and the household decision, never on a route.
- **A thin "we built it."** The routing is a library, so the switching model and scenario engine must carry it.
- **r5py setup** (Java, OSM clipping) can take 1–2 h. Hold the 9 PM gate.
- **The model must be allowed to say "keep the car"** (families, disabilities, night shifts).
- **Weather is supporting data**, so there is no satellite core.

---

## 5. #3: **Hearth**, heat pump or insulation first? (the owner-side sibling of #1)

### One-liner
Type any address and get, in seconds:
- that home's heating cost and carbon
- the right-size heat pump
- **the one upgrade to do first**, with money and carbon side by side

It runs on a model trained on 18,756 DOE EnergyPlus simulations of Michigan homes. Then zoom out to every home in Ann Arbor.

### Why it isn't niche, and where it falls short
- **Broad.** Space heating is 42% of US residential energy (EIA RECS 2020) [F 05]. Every judge's parents' house qualifies.
- **But the decision is rare.** It comes up at furnace replacement and heat-pump quotes, roughly once a decade. Hence the skeptic's niche score of 5.
- **Pick it over #1 only if** the team finds the renter framing too Ann Arbor-specific. It reuses about 70% of #1's pipeline (ResStock, footprints, NASA POWER, tariff code, map) [I]. That makes it a cheap pivot within the first hours.

### How it matches what won before
- **Same shape as Watt's Up**, but on heating, the bigger flow, instead of solar.
- **ZoneZero** won its pool on one counterintuitive expert insight ([Devpost](https://devpost.com/software/zonezero)) [F 02]. Hearth's insight comes from DOE data [F 05]:
  - **Gas-heated Michigan homes:** a cold-climate heat pump alone *raises* the bill in 93% of cases (median −$458/yr) while cutting about 2.6 t CO₂e/yr. Envelope work saves a median $134/yr.
  - **Propane, electric-resistance and oil homes:** a heat pump saves about $900–1,250/yr.
- **V²/R** won Grand with its own engine and no LLM [F].

### Technical core
- **Gradient-boosted surrogates** on ResStock 2024.2 MI: baseline + 16 upgrade packages, 12 observable inputs [F 05].
- **Held-out results:** heat-pump savings R² 0.85 (MAE $269), design heating load R² 0.72, bill R² 0.71.
- **Plus:** the team's tariff code; sizing from design load and a contractor-quote check; a city batch.
- **Benchmark:** agreement with Rewiring America's REM API on 20 addresses. REM requires an Authorization key ([docs](https://docs.rewiringamerica.org/api/residential-electrification-model)) [V]. Sign up in hour 1.

### 3-minute demo
- **0:00** "Heating is 42% of a home's energy, and Michigan turned the heat on this week."
- **0:15** The judge's address → a 3D house: vintage, sq ft, gas, $/yr, t CO₂e.
- **0:40** Money-vs-carbon "do this first" bars. For a gas home: insulate first, because a heat pump costs ~$450/yr more today but cuts 2.6 t. A rural propane address: heat pump now.
- **1:10** A teammate texts "quoted 5 tons for $21k". Hearth explains the oversizing.
- **1:45** Ann Arbor in 3D, filtered to "where a heat pump saves money now."
- **2:20** Core numbers and REM agreement.
- **2:45** A real teammate's gas bill next to Hearth's estimate.

### Sponsor tracks
- Photon or Relay (pick one) for the quote-check thread.
- Figma.
- Judged by an LLM.
- SpaceX: moderate at best (NASA POWER plus imagery-derived footprints). Don't count on it.

### 18-hour build plan
| Time | P1 (ML) | P2 (geo/data) | P3 (frontend) | P4 (agent/story) |
|---|---|---|---|---|
| Start → 8 PM | Pull 17 MI parquet files (~190 MB) | Footprints, NASA POWER client | Repo, map shell | REM signup; messaging gate |
| 8 → 11 PM | Surrogates, tariff code, held-out metrics | Address → geocode → footprint → features | Report page | Agent with tool calls |
| 11 PM → 2 AM | Sizing; REM comparison on 20 addresses | Year-built join or two-question fallback | 3D house, rate slider | Quote check; first video takes |
| 2 → 6 AM | City batch runs while the team sleeps in shifts | | | |
| 6 → 11:30 AM | Uncertainty bands, equity overlay | City filters | Figma pass | Freeze at 9; Devpost; rehearse; submit |

### Main risks
- **"Rewiring America already does this."** Name it in minute one and use it as the benchmark.
- **A GBM on a table is a thin "we built it"** (past-MHacks judge).
- **"Decoded from above" oversells the imagery** (skeptic, sustainability expert). Drop that subtitle.
- **Envelope savings are poorly predicted (R² 0.40).** Ask two questions.
- **Rates drive the answer.** Keep a rate slider.

---

## 6. The anatomy filter, applied

These are the seven questions from `01-mhacks-winner-anatomy.md` §8. Keep an idea only if it passes 1 and 3, plus at least four of the rest.

| Question | Hidden Rent | CarLight | Hearth |
|---|---|---|---|
| 1. Judge says "I have that" in 5 s | ● | ● (car owners) | ◐ (owners) |
| 2. Happens at least weekly | ◐ (monthly bills; many listings per search) | ● (daily) | ✕ (once a decade) |
| 3. Effect visible in 20 s | ● (range narrows as you answer) | ● (isochrone blooms) | ● (3D house) |
| 4. Own core, one sentence | ● (sim-to-real model + question picker) | ◐ (routing is a library) | ◐ (GBM surrogate) |
| 5. One measured number | ● (held-out error on real meters; −35% band) | ● (log-loss vs baseline; $/yr) | ● (R² 0.85; REM agreement) |
| 6. Touches a resource system | ● (building stock) | ● (transport network) | ● (building stock) |
| 7. Not on the saturated list | ● | ◐ (footprint-calculator lookalike) | ◐ (rooftop-solar-adjacent shape) |
| **Passes** | **6.5 / 7** | **6 / 7** | **5 / 7** |

---

## 7. What happened to the satellite spitball

- **The team asked for satellite data as the core.** In this round, every idea with satellite data truly at its core failed the breadth test:
  - **Raindrop** (GPM IMERG rainfall and a NAIP segmentation model): skeptic niche score 7.
  - **Load** (Sentinel-2 change detection plus a chiller detector): skeptic niche score 6.
  - The everyday-lens writer also tested contrail-aware flights and lawn water from space, and both failed "used often" [F 03 §5].
- **SpaceX's judges reward space at the core and punish garnish** [F sponsor 07]. Earth-observation data counting as "space data" is unverified.
- **So the recommendation trades the satellite wish for breadth.** The team's own rejection of two niche ideas says that is the right trade.
- **How Hidden Rent keeps space data honest:**
  - NASA POWER (CERES/MERRA-2) drives the weather normalisation.
  - The Sentinel-2 snow-roof test is a gated bet. If the correlation holds, it is novel and gives space data a real role.
  - Claim SpaceX only then.
- **The conversational layer passes the "not decoration" test in #1.** The interview narrows the number, the bill photo recalibrates it, and the agent drafts the landlord request. It does no voice call and no small talk.

---

## 8. First 60 minutes (Hidden Rent)

1. **P1:** download the ResStock 2024.2 MI baseline from OEDI S3. Reproduce R² ≈ 0.55 (public features) and ≈ 0.76 (with answers) on a gas-heated holdout. If it is far off, stop and re-plan before 9 PM.
2. **P2:** query the Ann Arbor benchmarking ArcGIS service and the OSI BuildingFootprints service. Confirm the gas units on one building. Run the Census geocoder on 3 campus-area addresses.
3. **P4:** Photon hello-world, then add a teammate through `POST /users`, then a QR redirect works. Decide Photon vs. Relay by 8 PM and pitch only one.
4. **P3:** Figma card with the range bar, and freeze the pitch's three numbers:
   - the $1,052–$2,254 same-size spread
   - 54.5% of Ann Arbor households rent
   - 70 of 308 GRH points since Jan 6, 2026
5. **Everyone:** ask 3–5 friends or teammates for a real DTE bill photo they're happy to share. The real-bill check needs them by 4 AM.

---

## Sources

**Team files (read):**
- `results/year-research/2020.md`–`2025.md`
- `results/SUMMARY.md` (Lessons; Cross-check)
- `results/pivot-ideas/01-past-winner-patterns.md`
- `results/pivot-round2/01-mhacks-winner-anatomy.md`, `02-peer-sustainability-winners.md`, `03-everyday-consumer.md`, `04-campus-city-scale.md`, `05-technical-wow.md`, `06-agentic-ai.md`
- `results/sponsor-tracks/06-photon-imessage-agents.md`, `07-spacex-make-it-legendary.md`, `11-relay-interactive-agents.md`, `13-debate-and-verdict.md`

**Winners cited (via team files):**
- **MHacks:**
  - FocusFlow https://devpost.com/software/focusflow-ucwma0
  - V²/R https://devpost.com/software/v-r
  - FarmX https://devpost.com/software/farmx-zpw0yq
  - F.L.U.D.D https://devpost.com/software/f-l-u-d-d
  - MotionSurfer https://devpost.com/software/motionsurfer
  - Fastr Food https://devpost.com/software/fastr-food
  - SunLite https://devpost.com/software/sunlite-sunrise-lamp
  - SolarVista https://devpost.com/software/solarvista
- **Peer events:**
  - Watt's Up https://devpost.com/software/watt-s-up
  - Chilladelphia https://devpost.com/software/chilladelphia
  - ZoneZero https://devpost.com/software/zonezero
  - Sustain-ify https://devpost.com/software/sustain-ify
  - BidBot https://devpost.com/software/bidbot

**Checked today [V]:**
- Ann Arbor Green Rental Housing in effect Jan 6, 2026; 70 of 308 points until Jul 5, 2028, then 110: https://www.a2gov.org/news/posts/city-of-ann-arbor-s-green-rental-housing-ordinance-goes-into-effect-jan-6-2026/ · checklist https://www.a2gov.org/media/dxxnmkyt/green-rental-housing-checklist.pdf · FAQ https://www.a2gov.org/media/yykptaqy/grh-faq.pdf
- Minneapolis time-of-rent disclosure (5+ units, under 50,000 sq ft, in effect 2021; search snippet): https://lims.minneapolismn.gov/Download/FileV2/20402/Energy-Disclosure-Policies-Summary-Readable.pdf · http://news.minneapolismn.gov/2019/02/15/minneapolis-require-residential-energy-disclosure/
- UtilityScore on HotPads (2015): https://www.inman.com/2015/07/10/utilityscores-can-show-which-of-2-identically-priced-homes-actually-costs-more/
- Rent.com "Total Cost of Renting" electricity estimates (Feb 2024; search snippet, the page returned 403): https://www.businesswire.com/news/home/20240226592602/en/New-Rent.com-Feature-Helps-Renters-Understand-True-Cost-of-Renting
- Zillow Cost of Renting Summary (Jul 2023; search snippet): https://zillow.mediaroom.com/2023-07-19-Say-goodbye-to-surprise-fees-New-Zillow-tool-helps-renters-avoid-unexpected-costs
- Rewiring America REM API (Authorization required): https://docs.rewiringamerica.org/api/residential-electrification-model
- r5py `max_bicycle_traffic_stress`: https://r5py.readthedocs.io/stable/reference/reference.html
- Photon allowlist troubleshooting (via the sponsor file): https://photon.codes/docs/spectrum-ts/troubleshooting/imessage

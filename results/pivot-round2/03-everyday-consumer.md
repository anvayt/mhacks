# Ideas — Everyday-life lens

## Prompt given (excerpt)
> Your lens: Everyday-life lens. Sustainability problems almost everyone has every day or week: food and groceries, food waste, commuting/transport, shopping and clothing, energy bills, water, packaging/recycling confusion, travel. Ideas a student or household would genuinely use often.
>
> Propose 3 distinct, concrete ideas for the Sustainability main track that (a) clearly fit the winning formula, (b) are NOT niche by the definition above and reach the Watt's Up bar on all five points while being original, (c) are not on the saturated list, and (d) are buildable by 4 students in ~18 h with a strong 3-minute demo. For each, verify the key data/APIs exist and are accessible, name the closest past winners and how yours differs, and list only the sponsor tracks that fit naturally.

*Written Sat Oct 3, 2026, ~7:30 PM EDT. Tags: **[V]** I checked it myself today: an API call, a download, or a page read at the linked source. **[F]** From a team research file (named). **[I]** My inference or estimate. All scores are inference.*

---

## TL;DR

| | Idea | One line | Not niche | Watt's Up bar (5 pts) | 18 h feasibility | Demo | Space data | Saturation risk |
|---|---|---|---|---|---|---|---|---|
| **1 (top pick)** | **Hidden Rent** | Type any address or paste a listing link and see the rent the listing doesn't show: what that apartment or house will cost to heat and cool each month, and its CO₂. Then text your first bill to the agent and it tells you what's off and what to ask the landlord. | 9 | 5/5 | 7 | 8 | Supporting | Low |
| 2 | **CarLight** | Enter your address and the places you go each week. See what your car really costs, which trips a bus, bike or e-bike would honestly cover, and the money and CO₂ you'd keep by going car-light. A morning text then tells you how to get there today. | 9 | 4.5/5 | 6 | 8 | Light | Medium |
| 3 | **Buy It Once** | Share any product link and see how long it actually lasts according to thousands of owners' reviews, shown as cost per year and kg CO₂ per year, next to the longer-lasting alternative. When something breaks, text the agent and it tells you whether to repair or replace it. | 8 | 3.5/5 | 7 | 7 | None | Medium–high |

**Top pick: Hidden Rent.**
- It has the strongest local data. Ann Arbor publishes **monthly** gas and electricity readings for its benchmarked apartment buildings through an open ArcGIS service [V].
- The core works on that data. I tested the core method tonight: a weather-normalized heating fit gets a **median R² of 0.95** on 349 Ann Arbor building-years [V, my run].
- It falls into a real policy gap. Ann Arbor's two disclosure laws skip exactly where students live: old houses split into rentals [V].
- The value fits in one sentence: *"Zillow shows the rent. We show the rent you don't see."*

**An honest note on the team's satellite spitball.** This lens produces ideas that are broad and used often, and in all three the space data is an input, not the core:
- **Hidden Rent:** NASA POWER, built from CERES satellite data plus MERRA-2; building footprints and heights that ML models derived from imagery; the Meta/WRI canopy-height map built from Maxar imagery.
- **CarLight:** NASA POWER hourly weather.
- **Buy It Once:** no space data.

SpaceX judges want space at the core [F `sponsor-tracks/07`]. So **I don't list SpaceX as a natural fit for any of the three.** The one exception is a 3-hour stretch experiment in Hidden Rent (§1.5): if Sentinel-2 snow-on-roof data really tracks metered heat loss, space data becomes a real second signal. The satellite-first everyday ideas I tested (contrail-aware flights, lawn water from space) failed the "used often / not niche" bar (§5).

---

## 1. Hidden Rent: the rent the listing doesn't show

### 1.1 One-liner
Paste a Zillow, Apartments.com or Redfin link, or type any address. In about five seconds you get that home's **monthly heating and cooling cost and CO₂**, how it ranks against comparable Ann Arbor buildings, and three questions to ask the landlord, all before you sign. After you move in, you text a photo of your first bill. The model recalibrates to your unit, tells you whether the bill is normal for the weather, and drafts the request for weatherstripping that the landlord should pay for.

### 1.2 Who has the problem, and how many
- **45.5 million US renter households**, 34.3% of occupied homes (Census HVS, Q4 2024) [V search].
- **In Ann Arbor, 54.5% of the 50,499 occupied homes are rented (27,544 units)** (ACS 2020–2024 via QuickFacts) [V search].
- The rental stock is old: **3,326 renter-occupied units were built in 1939 or earlier**, and students make up about 25% of renter households in the Ann Arbor housing market area (HUD market analysis) [V search].
- Every household pays an energy bill, and for many the burden is heavy: **1 in 4 low-income US households spends more than 15% of income on energy** (ACEEE, Sept 2024) [V search].
- Michigan homes in the RECS 2020 microdata spend a median of **$2,061/yr on energy, $612 of it on natural gas** (my unweighted median over 388 Michigan records) [V, computed from the file].
- Owners can use the same engine to see what to fix first. They are a second audience.

### 1.3 How often it's used
- **During every housing search.** Renters move about 4× as often as owners; about 16% of renters moved in 2023 (CPS figures as summarized by HomeSnacks) [V search]. A single search compares many listings. Ann Arbor students commit to the next lease months ahead, because the 2021 Early Leasing Ordinance lets showings start 150 days into the current lease, and landlords take deposits even earlier (Michigan Daily) [V search].
- **Monthly.** Each bill gets a weather-adjusted check: *"Your $186 January bill is normal for 1,240 heating degree-days."*
- **Weekly from November to March.** Cold-snap texts: *"This week will cost you about $41 to heat. Here's a free 10-minute fix."*

### 1.4 Why it isn't niche
- **The problem is universal and recurring.** Every renter, every winter, every month. Every judge has paid a surprise heating bill.
- **It avoids both rejected failure modes.**
  - Clean Hours was niche because it was one appliance and a minor behavior.
  - Fern on Call was niche because it served a small group during a rare event.
  - The heating bill is the largest energy cost in a Michigan home and arrives every month. The decision it changes, a 12-month lease, is large and comes back every year.
- **It takes no science lesson.** "This apartment costs $230 a month more in January than the one down the street" is understood instantly. Clean Hours needed a grid-carbon lesson first.

### 1.5 Technical core (what we build and can name in one sentence)
> *"We fit a heat-loss fingerprint to every Ann Arbor apartment building that reports monthly gas, then trained a model on 18,496 US homes and 11,000 Chicago buildings to predict that fingerprint for any address. The tenant's own bill then corrects it."*

1. **Fingerprint engine (built and tested tonight).**
   - Method: a change-point regression in the style of Princeton's PRISM method, fitting monthly gas use against heating degree-days.
   - Inputs: degree-days computed from **NASA POWER** daily temperature (the API reports its sources as CERES SYN1deg and MERRA-2 [V]), and Ann Arbor's benchmarking data.
   - Test run [V, my run]: a plain linear version fit to **349 Ann Arbor multifamily building-years** (2021–2023, 12 non-zero gas months each) gives a **median R² of 0.95**, with **76% of fits above 0.9**.
   - The fingerprint varies a lot. The heating slope per 1,000 sq ft is about **6× higher** at the 90th percentile than at the 10th.
2. **Generalization model.**
   - Type: LightGBM quantile regression (P10/P50/P90).
   - Training data:
     - **EIA RECS 2020**: 18,496 households and 799 variables, including `HDD65`, `YEARMADERANGE`, `TOTSQFT_EN`, `TYPEHUQ`, `KOWNRENT` and `DOLLARNG` [V, downloaded].
     - **Chicago's energy benchmarking dataset**: 11,278 multifamily records through its open Socrata API [V].
   - Features (all derivable from an address):
     - Footprint area and floors, from Overture or Microsoft buildings.
     - Year built, from the listing text, or else the ACS block-group median.
     - Building type.
     - Local heating and cooling degree-days.
     - Tree shading, from the Meta/WRI 1 m canopy-height map built from Maxar satellite imagery.
   - **Validation:** leave one building out across Ann Arbor's benchmarked buildings, scored against their *actual* monthly gas. The held-out error is the hard number we show on screen.
3. **Bill calibration.**
   - A vision LLM reads the bill photo and pulls out therms, kWh and billing dates.
   - A Bayesian update then shifts the unit's fingerprint toward the real reading.
   - The agent follows a "numbers only from tools" rule: it never makes up a figure.
4. **Money and CO₂ in one view.**
   - Prices: EIA Michigan residential gas and electricity.
   - CO₂: gas at about 5.3 kg per therm (EPA equivalencies factor), and electricity at the eGRID RFCM subregion rate.
5. **City layer.**
   - We precompute every Ann Arbor residential building and rank them by excess heating cost per square foot.
   - The decision this produces: which buildings a weatherization program should reach first, and how much money and CO₂ the worst 10% waste.
6. **Stretch (3 h, strict go/no-go): "the roof that melts first."**
   - Idea: after a snowfall, roofs that leak heat lose their snow first. We'd test whether that shows up in Sentinel-2 imagery for Ann Arbor's large flat roofs, and whether it correlates with the metered fingerprints above.
   - Data: clear Sentinel-2 scenes over Ann Arbor exist for **Feb 15, 2026 (about 90% snow across the tile)** and for Feb 27 and Mar 2, 2026 (about 2–4% snow) [V, Earth Search STAC].
   - **Keep it only if the correlation is real.** If it is, it gives space data a genuine role and opens SpaceX. If not, write "we tested it; it didn't hold" in the Devpost.

### 1.6 Demo (3:00 at the table)
1. **0:00, the hook.** "54.5% of Ann Arbor homes are rented. The listing says $1,400. It doesn't say January's $230 gas bill. Ann Arbor makes home *sellers* disclose an energy score. It makes buildings over 20,000 sq ft report their energy use. The old houses split into student rentals fall through both."
2. **0:20, the judge's own address.** The judge types their address, or picks their apartment building. The map flies in and outlines the building. On screen: **Hidden rent: $148/mo average, $231 in January**, a 12-month bar chart split into heating, cooling and base load, **2.4 t CO₂/yr**, and *"leakier than 78% of comparable Ann Arbor buildings."* (These numbers are illustrative; the real ones come from the model.)
3. **0:50, the judge's phone.** The judge shares any Zillow listing to the agent's iMessage number. About 10 seconds later the reply arrives: the hidden rent, plus three questions to ask the landlord. Who pays heat? When were the windows replaced? How old is the boiler?
4. **1:20, how it works.** A scatter of real Ann Arbor buildings, gas use against NASA-derived degree-days, with the fitted lines and the 6× spread. Then the held-out error. "We trained it ourselves."
5. **2:00, bill calibration.** A teammate photographs a real DTE bill. The fingerprint shifts: *"Your unit runs 18% leakier than predicted. A $40 window-film and weatherstrip kit saves about $X this winter. Here's the email to your landlord."*
6. **2:30, the city.** Zoom out to every rental, colored by excess heating cost. Show what the worst 10% waste in dollars and tons of CO₂. The policy ask: extend disclosure to rentals. Minneapolis already requires landlords to disclose average utility costs before the lease is signed [V].

### 1.7 Winning-formula match
- **Broad problem, specific demo:** every renter's bill, shown on the judge's own address.
- **Something happens within 20 seconds:** the judge's building lights up, and then the judge's phone buzzes.
- **A core the team built and can name:** fingerprints plus a trained model, validated on Ann Arbor's metered buildings. No step is just an API call.
- **Hard numbers:** median R² 0.95; a 6× spread; the held-out error; "$X hidden rent."
- **Local hook:** the gap between Ann Arbor's HERD ordinance and its benchmarking ordinance; the 54.5% renter share; the 3,326 pre-1940 rental units.
- **The peer formula:** "address in, a personal decision out" (Watt's Up, Chilladelphia, ZoneZero). The output is a decision (which lease, what to ask, what to fix), not a dashboard.
- **Sustainability as a side effect of money:** it touches a resource system and its producers (the housing stock and the landlords who own it), not a shopper's conscience.
- **Frequency:** a monthly bill, plus weekly winter texts.

### 1.8 Closest past winners, and how this differs
| Winner | What it did | How Hidden Rent differs |
|---|---|---|
| **Watt's Up** (HackPrinceton Fall 2025, Best Overall Hack; one search snippet says 2nd place) | Address → rooftop solar report: SegFormer roof segmentation plus NASA irradiance | The team loves the same shape, but this is a different problem. Watt's Up covers the *supply side* (solar) for *owners*; Hidden Rent covers the *demand side* (heating and cooling) for *renters*. No roof segmentation. It is trained on locally metered buildings. |
| **Chilladelphia** (PennApps XXV, Best Sustainability) | A Philly address → a "chill rating" from tree cover | Same "your address" demo, but the output is the money and carbon cost of living there, not heat comfort. |
| **LEED Bud** (TreeHacks 2024, Ecopreneurship) | Building specs → estimated LEED tier, for developers | Built for tenants, needs only an address, and uses real metered training data. |
| **GreenPrint** (MHacks 2025, AgentMail) | An IoT hub that monitors building CO₂ | No hardware, and it covers every building in a city. |
| **FarmX** (MHacks 2024, Sustainability) | A random-forest model aimed at Michigan farms | Same local, model-backed pattern, aimed at people the judges actually are. |
| Commercial prior art | UtilityScore sold estimated utility costs to listing sites around 2015–16 (Inman). DOE's Home Energy Score needs an assessor visit (Ann Arbor HERD). Minneapolis makes landlords disclose costs. | Ours is renter-first, needs only an address, is calibrated by the tenant's own bill, includes carbon, and adds an agent that drafts the landlord request. Say so out loud: "UtilityScore tried this for buyers; nobody does it for renters." |

### 1.9 Sponsor tracks that fit naturally
- **Photon iMessage agents.** Sharing a listing link from Safari or Zillow is the natural way to use it, and judges need no app.
  - Caveat: the free tier allows only about 10 allowlisted numbers [F `13-debate-and-verdict.md`]. Add judges' numbers during the pitch, or demo from a teammate's phone.
  - Relay is the alternative surface if its workshop confirms texting works on the public build. Pick one and pitch one.
- **Figma Best Design.** A consumer report card plus a city map is a real design problem.
- **Not natural:**
  - SpaceX: only if the §1.5 stretch holds.
  - ElevenLabs: voice isn't needed.
  - Capital One Nessie: utility bill amounts carry dollars but no therms, so it would be decorative.
  - FREE-WILi: no sensor fits.
  - Fern is optional; nothing needs her.

**Fun track:** Judged by an LLM. Write the Devpost to the rubric with real numbers.

### 1.10 Build plan (Sat 6:30 PM → Sun 11:30 AM; P1 data/ML, P2 backend/geo, P3 frontend/design, P4 agent/story)
| Time | P1 | P2 | P3 | P4 |
|---|---|---|---|---|
| 6:30–8:00 | Pull Ann Arbor benchmarking polygons and monthly fields over ArcGIS REST, Chicago over Socrata, and the RECS CSV. NASA POWER daily temperatures, 2021–2026 | Address → coordinates (Census geocoder) → building polygon (Overture via DuckDB; Ann Arbor polygons) → features. Parse listing URL slugs, since Zillow URLs contain the address | Figma: report card, map, iMessage reply. Next.js + MapLibre skeleton | Photon (or Relay) hello-world. Tool schema: `get_report`, `compare`, `calibrate_bill`, `draft_landlord_email` |
| 8:00–12:00 | Change-point fits for every Ann Arbor building. LightGBM quantile model on RECS (cold-climate subset) plus Chicago. Leave-one-building-out evaluation | `/report` API: monthly breakdown, EIA prices, CO₂ factors, caching | Report UI and building layer | Agent flows; reading the bill photo with a vision LLM |
| **12:00 AM gate** | **The judge's address returns a report end to end, and a Zillow link gets a reply.** If not, cut the city layer. | | | |
| 12–4 AM | Citywide predictions with uncertainty bands. *Stretch: the Sentinel-2 snow test, go/no-go at 3 AM* | Calibration endpoint | City map, percentile ranking | Landlord email; cold-snap message |
| 4–8 AM | Put the evaluation numbers on screen | Hardening and fixtures | Polish | Devpost (~500 words, with a Limitations section). Film the video in a real apartment with a real bill |
| 8–11:30 | Freeze at 10. Rehearse 5×. Backup video, README, submit by 11:30 | | | |

### 1.11 Data and APIs I verified today
- **Ann Arbor benchmarking feature service** (behind a2gov.org/benchmarkingmap) [V]:
  - Openly queryable: **2,094 records**; **575 Multifamily Housing records for 2021–2023**; **116 multifamily properties in 2023**, covering **17.7M sq ft**.
  - Fields: monthly natural gas and electricity, `SiteEUI`, `YearBuilt`, `GrossFloorAreaBuildings`, polygons.
  - **2023 site energy use intensity (kBtu per sq ft): 30.0 at the 10th percentile, 56.8 median, 89.1 at the 90th, about 3× from best to worst.** 39% of the buildings were built before 1970.
- **RECS 2020 CSV** (56 MB) downloaded [V]: 18,496 rows, 799 columns, 388 Michigan records.
- **Chicago benchmarking** over Socrata: 11,278 multifamily records [V].
- **NASA POWER** daily and hourly point API returns 2025–2026 data, with sources listed as `SYN1DEG` (CERES) and `MERRA2` [V].
- **Census geocoder**: works [V].
- **Overture buildings** (height and number of floors in GeoParquet, queryable with DuckDB by bounding box) and the **Meta/WRI 1 m canopy map** (on AWS, CC-BY-4.0): verified from their docs. Neither queried for Ann Arbor yet; **test in hour 1** [V docs].
- **Sentinel-2 L2A over Ann Arbor** through Earth Search STAC: Feb 15, 2026 (about 90% snow) and Feb 27 / Mar 2, 2026 [V].
- **Policy facts:**
  - Ann Arbor HERD: Home Energy Score required before *sale* of single-family homes; in effect Mar 12, 2024; enforced from Sept 8, 2024 [V].
  - Ann Arbor benchmarking: buildings of 20,000 sq ft or more [V].
  - Minneapolis time-of-rent energy cost disclosure [V].

### 1.12 Risks
- **"Isn't this Watt's Up?"** Lead with the renter and the bill, never with a roof. Show no segmentation. Use the line: "Watt's Up asks what your roof could make. We ask what your apartment will cost."
- **Small houses are uncertain**, because RECS can't see insulation. Always show a P10–P90 range, and push the bill calibration.
- **Who pays heat?** Many leases include it. The agent asks first. If heat is included, say so: "Your landlord pays $X/yr of waste."
- **Join problems:** benchmark addresses are ranges ("3505–3855 Greenbrier"). Use spatial joins on the polygons, not address matching.
- **Gas units** in the city feed aren't labeled. Assume Portfolio Manager kBtu and confirm in hour 1 with one building's EUI.
- **Ethics:** publicly naming the "worst landlords." Only show buildings the city already publishes; aggregate everything else.
- **Messaging surface:** Photon's allowlist limit, and Relay's iOS 26 requirement with calls unconfirmed [F]. Keep the web page as the fallback.

---

## 2. CarLight: what your car really costs, and the week without it

### 2.1 One-liner
Enter your home address and the 3–5 places you go each week. CarLight routes every trip by bus, bike, e-bike and on foot at the times you actually travel. A model trained on how car-light households really behave estimates which trips you'd *actually* switch. It shows the verdict as money and CO₂: *"Go car-light: 86% of your trips are covered, keep $8,900/yr and 2.9 t CO₂/yr"* (illustrative). From then on, a 7:30 AM text tells you the best way to get there today.

### 2.2 Who has the problem, and how many
- **Owning a new car costs $12,863 a year** (AAA, Sept 2026) [V search].
- Michigan full-coverage insurance averages about **$2,703/yr** (Experian, Aug 2026) and is among the most expensive in the US [V search].
- **Transportation is the largest source of US greenhouse gas emissions**: 28.9% in 2022 (EPA) [V search].
- **52% of all US trips were under 3 miles** in 2021, and 28% were under 1 mile (DOE Fact of the Week #1230) [V search].
- **Local hook:** A2ZERO set a goal of cutting vehicle miles traveled by 50%. Instead, **Ann Arbor's VMT rose from 955 million (2021) to 1.11 billion (2023)**, per the city's OSI dashboard as reported by the A2 Independent [V]. Walking and biking fell from 49.9% to 38.8% of trips between 2019 and 2023 (Ann Arbor Observer) [V].
- U-M students and staff ride TheRide free with an Mcard [V], so the alternative already exists. People don't trust it.

### 2.3 How often it's used
**Daily.** The morning text, the "how do I get to Meijer without a car?" question, and re-planning on a rainy afternoon. The big money decision (sell the second car, or don't bring a car to campus) comes up every year.

### 2.4 Why it isn't niche
Almost everyone commutes, every day, and the car is the biggest household cost after housing. The value fits in one sentence: *"Find out in 10 seconds whether you need your car, and how much money you keep if you don't."* It's self-interest first. No guilt is required.

### 2.5 Technical core
> *"Our own multimodal router on Ann Arbor's live bus schedule, plus a switching model trained on the federal travel survey, tells you not just what's possible but what you'd really do."*

1. **Accessibility engine.**
   - Built on r5py (the Conveyal R5 engine, v1.1.7 on PyPI [V]).
   - Inputs: **TheRide GTFS**, an OSM walk/bike network filtered for low-stress streets, and e-bike speed profiles that account for hills using elevation data (USGS 3DEP, or NASA SRTM).
   - TheRide feed [V, downloaded]: AAATA, valid 2026-08-23 → 2027-01-30, 30 routes.
2. **Realistic-switching model.**
   - Training data: **NHTS 2022** public trip files (household, person, vehicle and trip records in CSV) [V search].
   - Model: a classifier that predicts the probability of a non-car mode from trip distance, purpose, vehicles per driver, age, density and season.
   - Combining it with routing: the classifier's output is scaled by the routed time ratio. The time weight comes from published value-of-time ranges, and that is an assumption we label.
   - *Caveat to say out loud:* the public NHTS has no travel times for the modes people didn't choose, so this is a propensity model, not a full mode-choice logit.
   - Hard number: held-out log-loss against a distance-only baseline.
3. **Weather viability at your address.**
   - Data: more than 20 years of **NASA POWER hourly** precipitation and temperature [V]. This is MERRA-2 reanalysis, which assimilates satellite observations.
   - Output: *"Over the past 20 years, X% of weekday 8 AM departures from your street were dry and above freezing."* Compute it live; don't guess it.
4. **Money and CO₂.**
   - Costs: AAA's fixed and per-mile costs, the car's MPG from the **fueleconomy.gov** API [V], Michigan insurance, and parking.
   - CO₂: EPA per-mile figures for cars; buses per passenger-mile; e-bike electricity at eGRID RFCM rates.
5. **City scenario engine.**
   - We compute car-light potential for every H3 cell in Ann Arbor, then rerun it with an edited GTFS feed (for example, Route 4 every 10 minutes).
   - Output: **how many more households become car-light, and how much VMT drops**, as a decision for TheRide and the council against A2ZERO.

### 2.6 Demo (3:00)
1. **0:00:** "A new car costs $12,863 a year. Ann Arbor promised to cut driving in half. Instead it went *up* 16%." (955M → 1.11B is +16% [I, arithmetic].)
2. **0:20:** The judge enters their address and three places. An isochrone blooms on the map: *"everywhere you can reach in 20 minutes without a car, Tuesday 8 AM."* Trip cards appear: bus #4, 18 min; bike, 14 min; car, 11 min plus parking.
3. **0:50:** The verdict, with the money and CO₂ number. Then the honesty line: *"People like you take trips like this by bus about X% of the time."*
4. **1:15:** The space data: dry 8 AM departures at your address, computed live from 20 years of NASA data.
5. **1:35:** The judge's phone gets "tomorrow's" 7:30 text (with the clock simulated): *"#4 at 8:12, on time, 41°F and dry. Rain from 5 PM, so take the bus home."* The judge asks how to get to Costco and gets an answer.
6. **2:05:** The city map. A slider sets Route 4 to every 10 minutes, and the screen shows the gain in car-light households and the VMT cut.
7. **2:40:** The core and the close.

### 2.7 Winning-formula match
- **Broad and daily:** the commute.
- **Money and carbon in one number:** $12,863 a year is a figure judges feel.
- **Built core:** a router plus a trained switching model.
- **Hard numbers:** dollars per year; the share of dry mornings.
- **Local hook:** A2ZERO's VMT goal, and the free Mcard bus.
- **Decision output:** for the person (keep or sell the car) and for the city (which route to upgrade).
- **Self-interest framing** (Watt's Up), and it **touches a resource system** (the transit network).
- **Weaker spots:**
  - The routing engine is a library, so the switching model and the scenario engine have to carry the "we built it" claim.
  - Novelty against Google Maps has to be argued (§2.8).

### 2.8 Closest past winners, and how this differs
| Winner / prior art | What it did | How CarLight differs |
|---|---|---|
| **Fastr Food** (MHacks 14, Best Beginner + Google Cloud) | Crowdsourced dining-hall waits plus walking times: "wait or walk?" | Same "campus decision" instinct, but scaled up to the biggest household money decision, backed by a trained model and real schedules. |
| **SolarVista** (MHacks 2024, MLH MATLAB) | A siting map for planners | Ours is personal and also produces a planner view, with a "what if" slider. |
| **GreenRide** (Hack on the Hill 2022), **TogetherRide** (Northeastern Husky Hackathon, carpool matching), **Tripster** (Connected Car Hackathon Grand Prize) | CO₂ per route; carpool matching; a driving-impact history | Those count CO₂ or match riders. CarLight answers *"do I need the car?"* in dollars, and admits which trips you won't switch. |
| Commercial: Walk Score/Transit Score, CNT's H+T index and AllTransit, Google Maps eco-routing | Area scores; routing | Ours is about *your* trips and *your* car cost, includes weather from 20 years of NASA data, and adds a city scenario tool. Say "Walk Score rates the block; we tell you whether to sell the car." |

### 2.9 Sponsor tracks that fit naturally
- **Capital One Nessie.**
  - Read: seed 90 days of gas-station, parking, insurance and car-loan transactions, then compute what the car *really* cost last quarter.
  - Write: a monthly transfer of the savings into a "car-free fund."
  - This copies LoadCheck's read-and-write pattern, which won "Best Use of Nessie" [F `12-capital-one-nessie.md`]. Put a "Powered by Capital One Nessie" badge on every Nessie figure.
- **Photon iMessage** (or Relay): the daily morning text and Q&A.
- **Figma Best Design.**
- **Not natural:**
  - SpaceX: the weather is supporting data, not the core.
  - ElevenLabs.
  - FREE-WILi.
  - Fetch.ai: forced here.

**Fun track:** Judged by an LLM.

### 2.10 Build plan
| Time | Work |
|---|---|
| 6:30–8:00 | **P2:** Java 21 + r5py; Michigan OSM from Geofabrik clipped to Washtenaw County with osmium; TheRide GTFS; first travel-time matrix. **P1:** NHTS 2022 download and trip features. **P3:** Figma and map skeleton. **P4:** agent hello-world; car-cost model; Nessie seed script. |
| 8–12 | **P1:** train and evaluate the switching model. **P2:** `/plan` API (trips × modes × times) plus weather viability. **P3:** isochrone animation, trip cards, verdict. **P4:** morning-text job, Q&A tools, Nessie reads. |
| **12 AM gate** | The judge's address returns a verdict, and the text arrives. **If r5py isn't routing by 9 PM**, fall back to OpenTripPlanner, or precomputed matrices for preset destinations. |
| 12–4 AM | Citywide H3 grid for 8 destination types; 2 GTFS scenarios; Nessie savings transfer; city map plus slider. |
| 4–8 AM | Polish; Devpost. Film a real morning bus ride with the text arriving. |
| 8–11:30 | Freeze at 10; rehearse; submit. |

### 2.11 Data and APIs I verified today
- **TheRide GTFS** (2.5 MB; feed valid 2026-08-23 to 2027-01-30; 30 routes) [V].
- **r5py** v1.1.7 on PyPI [V].
- **NASA POWER hourly** `PRECTOTCORR` and `T2M` for Ann Arbor [V].
- **fueleconomy.gov** REST API [V].
- **Census geocoder** [V].
- **NHTS 2022** public CSVs at nhts.ornl.gov/download.shtml [V search; not downloaded].
- **AAA's $12,863** [V search].
- **Ann Arbor VMT, 955M → 1.11B** [V, A2 Independent citing the OSI dashboard].
- **Mcard free fares** [V].
- **Unverified:** whether U-M's Blue Bus publishes a GTFS feed [I]. Test it; the fallback is TheRide only.

### 2.12 Risks
- **"That's Google Maps."** Open on the money and the household decision; never open on a route.
- **r5py setup** (Java, OSM clipping) can eat 1–2 hours. Hit the 9 PM gate or fall back.
- **The switching model is a propensity model, not a full logit.** Say so in the Limitations section.
- **Car-light isn't for everyone** (families, disabilities, night shifts). Show "keep the car" as a respectable outcome, and make the model allowed to say no.
- **NASA POWER precipitation is reanalysis, not direct satellite rainfall.** Word it exactly that way. GPM IMERG would need an Earthdata login; it's optional.
- **Nessie** sandboxes start empty, so seed your own data and namespace it [F].

---

## 3. Buy It Once: how long it really lasts, as cost per year

### 3.1 One-liner
Share any product link (a kettle, vacuum, blender, headphones) with the agent, or paste it into the web app. Buy It Once mines thousands of owners' reviews for **when things actually died**. It returns the product's survival curve, **cost per year of use and kg CO₂ per year**, and a longer-lasting alternative: *"The $24 kettle reports failures at a median of 7 months, which works out to $41 per year of use. The $58 one costs $11 per year."* (Illustrative.) When something breaks, you text the agent. It names the common failure, pulls the iFixit guide and the part price, and says whether to repair or replace.

### 3.2 Who has the problem, and how many
- Everyone who buys appliances, electronics and home goods.
- **Americans throw out almost 8 million tons of electronics a year**, and the world generated 62 million tonnes in 2022, of which only 22.3% was documented as recycled (UN Global E-waste Monitor 2024, via PIRG) [V search].
- **Policy hook:** since Jan 1, 2025, France has required a **durability index** next to the price of TVs, extended to washing machines from Apr 8, 2025 [V search]. The US has nothing comparable.
- **Local hook:** U-M's move-out program collected a record 16.5 tons of goods [V search].

### 3.3 How often it's used
Every time you buy a durable item, which for most households is weekly to monthly, and every time something breaks.

### 3.4 Why it isn't niche
Everyone buys things that break. The judge gets it in one sentence: *"The cheap one isn't cheap if it dies in eight months."* It's money first; the sustainability is a side effect.

### 3.5 Technical core
> *"We turned 2.1 million appliance reviews into survival curves: an LLM pipeline pulls out time-to-failure events, and a hazard model compares products on what they cost per year of use."*

1. **Failure-event miner.**
   - Step 1: regex prefilter.
   - Step 2: LLM extraction, pulling out the product, the event (failed or still working), the duration and the failure mode.
   - Sources: **Amazon Reviews 2023** (McAuley Lab): Appliances has 2.1M reviews, and Home & Kitchen has 67.4M, from which we'd take small-appliance subsets [V].
   - **Tested tonight on a 297,340-review Appliances sample** [V, my run]:
     - 4.2% mention failure words.
     - **0.63% pair a failure with a duration** ("broke within a year").
     - "Still working after X" is rare (0.07%).
   - That projects to roughly 13k failure events for Appliances alone [I, extrapolation].
2. **Survival model.** A Cox proportional-hazards or Weibull model (lifelines) across product, brand, price band and category.
   - Reviews over-report failures, so they give *relative* hazards.
   - *Absolute* lifespans come from category baselines anchored to published lifespan tables.
   - Say this in the pitch.
3. **Extraction precision:** 300 hand-labeled reviews. That precision is the hard number on screen.
4. **Money and CO₂ from one figure.**
   - Cost per year = price ÷ expected life.
   - kg CO₂e per year = price × the **EPA Supply Chain GHG Emission Factor** (v1.3, kg CO₂e per USD by NAICS commodity) ÷ expected life [V search].
5. **Repair branch:** iFixit API guides for the common failure mode, plus the part price, set against the cost and CO₂ of replacing [V, API call].

### 3.6 Demo (3:00)
1. **0:00:** "Americans throw out almost 8 million tons of electronics a year. France now prints a durability score next to the price. The US has nothing."
2. **0:15:** The judge shares an Amazon link from their own phone. The reply: median reported failure, cost per year, CO₂ per year, and a better alternative.
3. **0:45:** On the web: two survival curves pulling apart, cost-per-year bars, and the common failure modes ("heating element," "lid hinge").
4. **1:15:** The core: the number of events extracted, the extraction precision, and the hazard ratios.
5. **1:50:** "My Keurig died." The agent returns the iFixit pump-replacement guide, a $12 part against a $90 replacement, and the kg CO₂ avoided.
6. **2:20:** Policy scale: a brand durability leaderboard, *what France's index would show if the US had one.*
7. **2:45:** Close.

### 3.7 Winning-formula match
- **Broad and frequent;** money first.
- **Built core:** the event miner and the hazard model.
- **Hard numbers:** precision, hazard ratios, dollars per year.
- **Decisions:** buy A, not B; repair, don't replace.
- **Producer-facing:** a brand durability index, not guilt.
- **Weaker spots:**
  - The city scale is weak; the scale story is the national label instead.
  - No space data.
  - **It resembles the "sustainable-shopping extension" ideas on the saturated list** (EcoScout).

### 3.8 Closest past winners, and how this differs
| Winner / prior art | What it did | How Buy It Once differs |
|---|---|---|
| **EcoScout** (MHacks 2025, Base44) | Barcode → a 0–100 EcoScore | No eco-score at all. It predicts **lifespan** and **cost per year** from owner evidence. |
| **Carbon Cut** (TreeHacks 2024, Cotopaxi) | A clothing-tag carbon grader, among other features | Ours is about durability, not footprint. |
| **deCluttered.ai** (MHacks 2025, Fetch.ai Agentverse) | Resale-listing agents | It works *before* the purchase, plus repair. |
| **Terminal.AI** (MHacks 16, 2nd) | A tool judges would use the next day | The same "judge will use it tomorrow" quality. |
| Prior art | productlifespans.com (manual reviews); France's manufacturer-declared index | Automated, based on owner evidence, gives cost per year, and adds the repair branch. |

### 3.9 Sponsor tracks that fit naturally
- **Photon iMessage:** share-sheet a product link. That is how people already pass links around.
- **Fetch.ai ASI:One:** a "durability oracle" agent on Agentverse (Chat Protocol) that shopping agents query before recommending a product. It is a real multi-agent action. **Fetch's hard requirements apply** [F `01-fetchai`]: register on Agentverse, use the Chat Protocol, make ASI:One the reasoner, and submit a demo video.
- **Figma Best Design.**
- **Not natural:** SpaceX, Nessie, ElevenLabs, FREE-WILi.

**Fun track:** Judged by an LLM.

### 3.10 Build plan
| Time | Work |
|---|---|
| 6:30–8:00 | **P1:** download Appliances reviews (270 MB gz) and metadata; stream small-appliance subsets; regex prefilter. **P2:** link resolver (ASIN → `parent_asin`, otherwise a title-embedding match). **P3:** Figma; chart components. **P4:** Photon agent; iFixit tool. |
| 8–12 | **P1:** batch LLM extraction (about 20–50k candidate reviews, a few dollars of credit [I]); hand-label 300. **P2:** lifelines fits; EPA factor mapping. **P3:** product page with survival chart. **P4:** repair-or-replace flow. |
| **12 AM gate** | A link returns a verdict end to end. If extraction precision is under 80%, narrow to 3 categories. |
| 12–4 AM | Covariate hazard model; alternatives recommender; brand index. Fetch.ai agent only if the core is done. |
| 4–8 AM | Polish; Devpost; video. |
| 8–11:30 | Freeze; rehearse; submit. |

### 3.11 Data and APIs I verified today
- **Amazon Reviews 2023:** category sizes from Hugging Face; the direct Appliances file (270 MB) returned HTTP 200; sample statistics from my run [V].
- **EPA supply-chain emission factors v1.3** on data.gov [V search].
- **iFixit API** search returned Keurig pump guides [V].
- **France's durability index dates** [V search].

### 3.12 Risks
- **The saturated lookalike** (EcoScout, shopping extensions). Never show an "eco" score. Lead with dollars per year.
- **Review bias.** Failures are over-reported and survivors rarely post. Use relative hazards with category baselines, and disclose this.
- **Wrong-product failures.** In the sample, many reviews of replacement parts describe the *old* part failing. Have the LLM decide which product failed, and measure that with the hand labels.
- **Stale data.** The dataset ends in Sept 2023. New products fall back to brand and category estimates.
- **Theme fit is only medium** for Sustainability judges. Open on e-waste and France's law. Frame it as the "resource systems" part of the track.

---

## 4. Side by side

| | Hidden Rent | CarLight | Buy It Once |
|---|---|---|---|
| Everyday flow | Heating bill (monthly, plus winter weekly) | Commute (daily) | Purchases and breakdowns (weekly to monthly) |
| Instant personal answer | Address or listing link | Address plus places | Product link |
| Core the team builds | Fingerprints + LightGBM, validated on metered Ann Arbor buildings | Switching model + scenario engine on r5py | Review event miner + hazard model |
| Money + CO₂ in one view | $/mo + t/yr | $/yr + t/yr | $/yr of use + kg/yr |
| One home → city/policy | Every rental; disclosure gap | Every block; Route-4 slider vs A2ZERO | Brand index; durability label |
| Local hook | HERD/benchmarking gap; 54.5% renters | VMT +16%; free Mcard bus | U-M move-out (weak) |
| Natural sponsors | Photon/Relay, Figma | Nessie, Photon/Relay, Figma | Photon, Fetch.ai, Figma |
| Biggest risk | Watt's Up resemblance | "That's Google Maps" | Shopping-extension lookalike |

**Recommendation: Hidden Rent.**
- It is the only one of the three whose core I could test tonight on real local data, and the result was strong (median R² 0.95).
- It also has the most specific policy story: two Ann Arbor ordinances that skip student rentals, plus a Minneapolis precedent.

CarLight is the strongest on frequency and on money. Its "we built it" core is thinner, and r5py setup is a real schedule risk. Hidden Rent and CarLight share the same shell (address → report → agent → city map), so if Hidden Rent's data join fails by 9 PM, about 4–6 hours of work carry over [I].

---

## 5. Considered and dropped (so nobody re-litigates them)

| Idea | Why it was attractive | Why I dropped it |
|---|---|---|
| **Contrail-aware flight picker** (a GOES-19 contrail detector trained on Google's OpenContrails, plus pycontrails) | Space data at the core, a stunning live-satellite demo, a perfect SpaceX fit. Night flights are 25% of traffic but 60–80% of contrail forcing (Stuber et al., *Nature* 2006) [V search] | People fly a few times a year, and it needs a science lesson first, which is exactly Clean Hours' failure mode. It would read as niche. |
| **Lawn water from space** (Sentinel-2 greenness plus OpenET evapotranspiration, which now covers all 48 states [V search]) | Space-data core; address in. Outdoor use is 30% of household water, and up to 50% of it is wasted (EPA WaterSense) [V search] | Homeowners only, summer only, and in Michigan in October the demo is a replay. It sits next to "auto-watering" on the saturated list. |
| **Tap vs bottled water / lead-line predictor** | Daily, with a Flint hook. Bottled water hit 16.4B gallons in 2024 (IBWA/BMC) [V search]; about 61M Americans don't drink tap water (Rosinger et al.) [V search] | **Ann Arbor has no lead service lines** [V search], and **Detroit already uses BlueConduit's ML** [V search]. The demo is flat and the idea isn't new. It also reads as a health project. |
| Grocery or meal carbon swaps, pantry and leftovers | Daily | Saturated: 0 for 6 at MHacks, about 24 entrants across peer pools [F round-2 anatomy and peer files]. |
| Cost-per-wear clothing extension | Weekly | Lookalike of the saturated sustainable-shopping extension. Buy It Once keeps the good part (durability) without the look. |
| A plain car-free route planner | Daily | It's Google Maps. Folded into CarLight's money decision. |

---

## Sources

**Team research (read in full or in the required sections)**
- `/Users/anvaytodkar/Code/mhacks/results/year-research/2025.md`, `2024.md`, `2023.md`, `2022.md`, `2021.md`, `2020.md`
- `/Users/anvaytodkar/Code/mhacks/results/SUMMARY.md` (sections "Lessons from six years of MHacks winners" and "Cross-check")
- `/Users/anvaytodkar/Code/mhacks/results/pivot-ideas/01-past-winner-patterns.md`, `00-synthesis.md`
- `/Users/anvaytodkar/Code/mhacks/results/pivot-round2/02-peer-sustainability-winners.md` (skimmed; its formula was supplied in the prompt)
- `/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/13-debate-and-verdict.md`, `07-spacex-make-it-legendary.md`, `12-capital-one-nessie.md` (grepped)

**Past winners cited**
- Watt's Up: https://devpost.com/software/watt-s-up · HackPrinceton Fall 2025 gallery: https://hackprinceton-fall-2025.devpost.com/project-gallery
- Chilladelphia: https://devpost.com/software/chilladelphia · LEED Bud: https://devpost.com/software/leed-bud · ZoneZero: https://devpost.com/software/zonezero
- GreenPrint: https://devpost.com/software/greenprint-c2deb1 · EcoScout: https://devpost.com/software/ecoscout-g01h43 · deCluttered.ai: https://devpost.com/software/declutttered-ai · Wattson: https://devpost.com/software/wattson-5btsyd
- FarmX: https://devpost.com/software/farmx-zpw0yq · SolarVista: https://devpost.com/software/solarvista · Fastr Food: https://devpost.com/software/fastr-food · Terminal.AI: https://devpost.com/software/terminal-ai
- Carbon Cut: https://devpost.com/software/carbon-cut-3d5k2g · Green Home Audit (prior art): https://devpost.com/software/green-home-audit
- GreenRide: https://github.com/jakegreenbergbell/greenride · Husky Hackathon (TogetherRide): https://siliconvalley.northeastern.edu/west-coast-hackathon-spring-2023/ · Connected Car Hackathon (Tripster): https://mtc.ca.gov/news/connected-car-hackathon-generates-innovative-ideas-address-bay-areas-transportation-challenges

**Hidden Rent: data and policy (checked today)**
- Ann Arbor benchmarking map → ArcGIS dashboard: https://a2gov.org/benchmarkingmap ; feature service queried: https://utility.arcgis.com/usrsvcs/servers/1e3bed4240284b40b0c4fea6f8cb4522/rest/services/OSI/BenchmarkingPerformanceMetrics/FeatureServer/0
- Ann Arbor benchmarking news (Jan 22, 2026): https://www.a2gov.org/news/posts/ann-arbors-energy-water-benchmarking-reaches-compliance-milestone-launches-public-map/ · ordinance page: https://www.a2gov.org/sustainability-innovations-home/sustainability-me/for-businesses/energy-and-water-benchmarking-and-disclosure-ordinance/
- Ann Arbor HERD: https://www.a2gov.org/news/posts/over-1-000-ann-arbor-homes-now-have-home-energy-scores/ · FAQ: https://www.a2gov.org/media/ncxdl1vh/herd-faq-092723.pdf · https://www.cbsnews.com/detroit/news/new-ann-arbor-ordinance-requires-home-sellers-to-disclose-home-energy-score/
- Minneapolis time-of-rent disclosure: https://fresh-energy.org/minneapolis-makes-climate-and-equity-commitment-with-residential-energy-disclosure-ordinance · https://www2.minneapolismn.gov/media/content-assets/www2-documents/business/Xcel-Energy-Disclosure---Quick-Start-Guide-(1).pdf
- EIA RECS 2020 microdata: https://www.eia.gov/consumption/residential/data/2020/index.php?view=microdata (CSV: https://www.eia.gov/consumption/residential/data/2020/csv/recs2020_public_v7.csv)
- Chicago energy benchmarking (Socrata): https://data.cityofchicago.org/resource/xq83-jr8c.json
- NASA POWER API: https://power.larc.nasa.gov/api/temporal/daily/point · https://power.larc.nasa.gov/api/temporal/hourly/point
- Overture buildings with DuckDB: https://docs.overturemaps.org/getting-data/duckdb/ · Meta/WRI canopy height on AWS: https://github.com/awslabs/open-data-registry/blob/main/datasets/dataforgood-fb-forests.yaml · https://sustainability.atmeta.com/blog/2024/04/22/using-artificial-intelligence-to-map-the-earths-forests/
- Sentinel-2 STAC (Earth Search): https://earth-search.aws.element84.com/v1/search
- Census geocoder: https://geocoding.geo.census.gov/geocoder/
- UtilityScore prior art: https://www.inman.com/2015/07/10/utilityscores-can-show-which-of-2-identically-priced-homes-actually-costs-more/
- Renter counts: https://www.census.gov/housing/hvs/files/currenthvspress.pdf (via https://yieldpro.com/2025/02/number-of-renter-households-falls-in-q4/) · Ann Arbor QuickFacts: https://www.census.gov/quickfacts/fact/table/annarborcitymichigan/INC910218 · HUD Ann Arbor market analysis: https://www.huduser.gov/portal/publications/pdf/Ann-ArborMI-comp-16.pdf
- Mover rates: https://www.homesnacks.com/moving-statistics/ · https://www.census.gov/newsroom/press-releases/2024/geographic-mobility-cps.html
- Early Leasing Ordinance: https://www.michigandaily.com/news/ann-arbor/students-report-landlords-finding-loopholes-in-the-early-leasing-ordinance/
- ACEEE energy burden 2024: https://www.aceee.org/press-release/2024/09/study-one-four-low-income-households-spend-over-15-income-energy-bills

**CarLight: data and context**
- TheRide GTFS: https://www.theride.org/sites/default/files/google/google_transit.zip · Mcard fares: https://www.theride.org/services/fixed-route/student-services
- r5py: https://pypi.org/project/r5py/ · NHTS 2022: https://nhts.ornl.gov/download.shtml · https://nhts.ornl.gov/assets/2022/doc/2022%20NextGen%20NHTS%20%20User's%20Guide%20V1_PubUse.pdf
- fueleconomy.gov API: https://www.fueleconomy.gov/ws/rest/vehicle/menu/year
- AAA 2026 driving costs: https://newsroom.aaa.com/2026/09/aaa-new-vehicle-ownership-costs-hit-12863-annually/
- Michigan insurance (Experian): https://www.experian.com/blogs/ask-experian/average-cost-car-insurance-michigan/
- EPA transportation emissions: https://www.epa.gov/ghgemissions/transportation-sector-emissions
- DOE FOTW #1230: https://www.energy.gov/cmei/vehicles/articles/fotw-1230-march-21-2022-more-half-all-daily-trips-were-less-three-miles-2021
- Ann Arbor VMT: https://a2independent.com/2026/07/21/a2zero-osi-missed-goals-mean-in-2028-taxpayers-will-begin-to-spend-public-money-to-buy-carbon-offsets/ · A2Zero mode share: https://annarborobserver.com/a2zero-six-years-in/ · https://www.michigandaily.com/news/ann-arbor/ann-arbor-commissioners-and-city-council-discuss-a2zero-plan/

**Buy It Once: data and context**
- Amazon Reviews 2023: https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023 · https://amazon-reviews-2023.github.io/ · Appliances file: https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/review_categories/Appliances.jsonl.gz
- EPA supply-chain emission factors v1.3: https://catalog.data.gov/dataset/supply-chain-greenhouse-gas-emission-factors-v1-3-by-naics-6
- iFixit API: https://www.ifixit.com/api/2.0/search/keurig%20pump?filter=guide
- France durability index: https://www.ecologie.gouv.fr/politiques-publiques/indice-durabilite · https://www.sgs.com/en-us/news/2024/06/safeguards-8724-durability-index-for-washing-machines-and-televisions-in-france
- E-waste: https://pirg.org/articles/6-surprising-facts-from-the-uns-2024-electronic-waste-report/ · https://www.greenpolicyplatform.org/research/global-e-waste-monitor-2024
- U-M move-out: https://news.umich.edu/u-m-student-move-out-results-in-12-5-tons-of-goods-donated-locally/ · https://www.wemu.org/wemu-news/2026-05-29/u-m-collects-tons-of-items-for-reuse-during-spring-student-move-out
- Prior art: https://productlifespans.com/pages/review-process

**Dropped ideas**
- Contrails: https://www.nature.com/articles/nature04877
- OpenET: https://www.nasa.gov/general/openet-launches-a-new-api/ · https://etdata.org/faqs/ · EPA WaterSense: https://www.epa.gov/watersense/how-we-use-water
- Bottled water: https://bottledwater.org/wp-content/uploads/2025/07/BWR_BWstats_June2025_FinalwithBMCad.pdf · tap distrust: https://pmc.ncbi.nlm.nih.gov/articles/PMC8664888/
- Ann Arbor service lines: https://www.a2gov.org/ann-arbor-water/ann-arbor-water-news/lead-and-copper-rule-update/ · Detroit/BlueConduit: https://detroitmi.gov/news/detroits-lead-service-line-replacement-program-use-cost-efficient-location-technology-save-estimated

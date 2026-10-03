# Pivot Ideas — Sustainability-impact scout

## Prompt given (excerpt)
> You are the Sustainability-impact scout. Find big, non-niche sustainability problems where live satellite/space data plus an agent that can call, text and act creates real impact (wildfire smoke, heat waves, flooding/Great Lakes, air quality, urban heat, crop/water stress, grid-scale demand response, methane, etc.). Prefer problems with a Michigan/Midwest hook and free real-time data you verify is accessible. Also say whether Sustainability is still the right main track or whether Hardware or AI would be stronger for a given idea.

*Written Sat Oct 3, 2026, ~5:20–6:15 PM EDT. Hacking ends 12:00 PM Sun. Every data source below was probed by me between 21:50 and 22:15 UTC today unless marked otherwise. "Inference" marks my reasoning, not a sourced fact. Scores are my judgment.*

---

## Read this first: where the past-winner research lives

All six years of winner research are in the repo. Each idea below cites them, so open them when you want the evidence behind a claim:

| File | What's in it | Most useful for this pivot |
|---|---|---|
| [`results/year-research/2025.md`](../year-research/2025.md) | MHacks 2025: all 30 winners, sponsor rubrics (Fetch.ai weights), the MDredd pairwise-judging tool | Wattson (Greenprint + FREE-WiLi), MobiLens (Fetch + hardware), "agents must close the loop" |
| [`results/year-research/2024.md`](../year-research/2024.md) | MHacks 2024 + Google x MHacks: 30 winners, Hacker Guide judging format (3-min table pitch) | FarmX (Sustainability, Michigan farms), SolarVista (satellite + MATLAB), the clean-hours load-shifting winner, WiLi Watch |
| [`results/year-research/2023.md`](../year-research/2023.md) | MHacks 16 (in person) + MHacks 15 (online) | DECO.ai's "research-grade core", Quick Action's two-sided user + operator design, Carbon Footprint Extension (2nd) |
| [`results/year-research/2022.md`](../year-research/2022.md) | No event was held in 2022 | Don't look for 2022 winners |
| [`results/year-research/2021.md`](../year-research/2021.md) | MHacks 14 (online) with judge quotes from closing-ceremony captions | **F.L.U.D.D** (SE Michigan floods, text → call escalation), **Water Monitor** (Great Lakes), SunLite (1st), "would I use this myself" |
| [`results/year-research/2020.md`](../year-research/2020.md) | MHacks 13 Beta (online) | "Every placement cited a statistic"; Sportable placed despite cutting its broken model |
| [`results/SUMMARY.md`](../SUMMARY.md) §"Lessons from six years" and §"Cross-check" | The ten repeating patterns and the cross-check against Clean Hours | Read the cross-check table before pitching anything |

---

## TL;DR

| # | Idea | Main track | Win | Non-niche | Feasible in 18 h | Demo wow | Sponsor fit | Reuse |
|---|---|---|---|---|---|---|---|---|
| **1** | **Fern on Call**: a smoke-and-heat check-in line. Satellites forecast the hazard, Fern calls the people least likely to have an app, and a FREE-WILi bedside beacon asks them to press "I'm OK". | Sustainability | **6** | **9** | 6 | **8** | **8** | **8** |
| 2 | **Plume Patrol**: satellite-detected landfill methane leaks become a call to the operator, a follow-up, and a resident alert | Sustainability | 5 | 7 | **7** | 6 | 7 | 5 |
| 3 | **Bloomline**: Lake Erie's live toxic algae bloom, turned into "don't let the dog in" calls and EGLE reports | Sustainability | 4 | 5 | 6 | 6 | 5 | 4 |

**Top pick: #1, Fern on Call.** It is the least niche (everyone breathes, and heat is the deadliest US weather). It reuses the most of what you've already built: Fern's wilted/normal/blooming moods map one-to-one onto bad-air/okay/clean-air days, so it needs no new xAI spend. It puts the FREE-WILi to genuine use. And it hits the patterns MHacks has rewarded for six years: a physical device on the table, a named local user with a statistic, and an agent that escalates from text to a call.

**Main-track verdict:** Sustainability is still right for all three, but for different reasons. For #1 the risk is that judges read "climate adaptation/health" as off-theme, so frame it as climate resilience. AI is the fallback if organizers say adaptation doesn't count. Hardware is wrong for all three: a FREE-WILi is the floor in that pool (the "Wattson asymmetry" in [07 verdict](../main-and-fun-tracks/07-debate-and-verdict.md)).

---

## Findings from past winners that drive this pivot

1. **Physical demos take MHacks-run prizes, and FREE-WILi + Sustainability is the one proven double win.** In 2025, hardware won 4 of 6 MHacks-run prizes, and Wattson took both Greenprint and Best Use of FREE-WiLi ([2025](../year-research/2025.md)). In 2021, 4 of 5 hardware entries won something ([2021](../year-research/2021.md)). Caveat: on prizes open to everyone, 2025 hardware won 3 of 15, so the edge is at the top only ([verdict](../main-and-fun-tracks/07-debate-and-verdict.md)).
2. **"Text, then call" escalation for a local climate hazard has already won here.** F.L.U.D.D (2021, Google Cloud 1st) was a solo build: SE Michigan basement-flood sensors that text you, then call if you don't respond in 15 minutes ([2021](../year-research/2021.md)). It shows the pattern works. It also means flood alerts specifically are already taken.
3. **Great Lakes and Michigan environmental data wins smaller prizes.** Water Monitor (2021, MLH Google Cloud) was a Great Lakes water heatmap. FarmX (2024 Sustainability) aimed at Michigan farms. SolarVista (2024, MLH MATLAB) used satellite data for solar siting ([2021](../year-research/2021.md), [2024](../year-research/2024.md)).
4. **Every year's placements opened with a named user, a statistic and a local hook.** NurseNotes had 41% of a shift spent on paperwork, MCall had a Michigan Daily survey, and every 2020 placement had a COVID number ([2024](../year-research/2024.md), [2021](../year-research/2021.md), [2020](../year-research/2020.md)). The most specific judge praise on record is first-person: the presenter said she would use 1st-place SunLite herself ([2021](../year-research/2021.md)).
5. **Top prizes go to a technical core the team built, not to API glue.** Examples: ASI's trained policy, V²/R's circuit solver, DECO.ai's NeRF pipeline. In 2023, 14 of 24 MHacks 16 winners called an LLM, so the differentiator was grounding in specific data ([2025](../year-research/2025.md), [2024](../year-research/2024.md), [2023](../year-research/2023.md)). Each idea below therefore names one measured result the team computes itself.
6. **Agents must close the loop.** The 2025 agent winners sent email, filed GitHub issues, negotiated, or drove devices. Fetch.ai's 2025 Best Use winner, MobiLens, was hardware + agents with caregiver alerts ([2025](../year-research/2025.md)). Across 11 events, all 48 verified Fetch winners completed a real action ([SUMMARY](../SUMMARY.md)).
7. **The Sustainability pool is small and the field was weak.** The identical 2025 track drew 15 of 122 projects, mostly carbon calculators ([01 Sustainability](../main-and-fun-tracks/01-main-sustainability.md)). Adaptation projects have won Sustainability prizes elsewhere: SkySplat (TreeHacks 2024, disaster recovery), Morro (TreeHacks 2026, disaster prediction), Chilladelphia (PennApps, urban heat) (same file).
8. **Overlap to avoid.** These have already been done at MHacks:
   - Clean-hour load shifting: the 2024 MLH Streamlit winner ([2024](../year-research/2024.md)).
   - A screen pet on a FREE-WILi: Wattson, 2025.
   - Flood alerts that escalate to a call: F.L.U.D.D, 2021.
   - A Great Lakes water heatmap: Water Monitor, 2021.

   None of the three ideas below repeats those. The overlaps that remain are named under each idea.
9. **Judging mechanics.** You get about 3 minutes at your table, several judges, and possibly MDredd pairwise comparisons where absences count as strikes. A demo that works live in seconds matters more than breadth. Honest scoping still wins: Ventura (2025) and Sportable (2020) both did ([2025](../year-research/2025.md), [2020](../year-research/2020.md)).
10. **Name collisions hurt.** In 2021 a judge seems to have confused two water projects on stage ([2021](../year-research/2021.md)). Pick one memorable name and use it everywhere.

---

## What I verified live today (Oct 3, 2026, ~22:00 UTC)

| Source | Result | Used by |
|---|---|---|
| GOES-19 ABI L2 on public S3: **ADPC** (aerosol/smoke detection), **AODC** (aerosol optical depth), **LSTC** (land-surface temperature), **FDCC** (fire), **RRQPEF** (rain rate), DSRF | All present. ADPC/AODC/FDCC newest scan started 21:51 UTC, about 6 min old. LSTC hourly at 21:01 ([bucket](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-ADPC/2026/276/)) | #1 |
| GOES-19 archive for Michigan's 2025 smoke days | ADPC and AODC exist for 2025 day 213 (Jul 31/Aug 1) ([listing](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-ADPC/2025/213/17/)) | #1 replay |
| NOAA HMS analyst smoke polygons | `hms_smoke20261003.kml` is up: 50 polygons, **0 over Michigan**. Heavy smoke spans lon −122 to −111 (the West) ([KML dir](https://satepsanone.nesdis.noaa.gov/pub/FIRE/web/HMS/Smoke_Polygons/KML/2026/10/)) | #1 |
| HRRR smoke forecast (AWS) | `hrrr.t18z.wrfsfcf01.grib2` has **MASSDEN 8 m above ground**, **AOTK** and **COLMD**, so you can fetch just those fields by byte range from the `.idx` ([idx](https://noaa-hrrr-bdp-pds.s3.amazonaws.com/hrrr.20261003/conus/hrrr.t18z.wrfsfcf01.grib2.idx)) | #1 |
| AirNow hourly files (**keyless**) | Today, 19:00 UTC: Detroit PM2.5 1.1–1.7 µg/m³ ([file](https://files.airnowtech.org/airnow/today/HourlyData_2026100319.dat)). Archive: Detroit's hourly max hit **77.0** on Jul 31, 2025 (14Z) and **74.6** on Jun 6, 2025 (20Z). My scan of the [2025 archive](https://files.airnowtech.org/airnow/2025/20250731/HourlyData_2025073114.dat) | #1 |
| NWS alerts API | `alerts/active?area=MI` returned 0 active alerts ([API](https://api.weather.gov/alerts/active?area=MI)) | #1, #3 |
| **Carbon Mapper plume API (keyless reads)** | 22,750 US plumes. The newest were **published today at 19:19 UTC**. The SE Michigan box holds **23 CH4 plumes, all sector 6A (landfills)**, aggregated into 6 sources. The newest is a Tanager-1 satellite plume dated Aug 31, 2026 ([API](https://api.carbonmapper.org/api/v1/catalog/plumes/annotated?bbox=-84.6&bbox=41.9&bbox=-82.9&bbox=42.8&limit=200)). The OpenAPI spec marks read endpoints as token-optional ([spec](https://api.carbonmapper.org/api/v1/openapi.json)) | #2 |
| EPA GHGRP via Envirofacts (keyless) | Michigan facility coordinates match the plume locations, and reported CH4 by year is available ([facilities](https://data.epa.gov/efservice/PUB_DIM_FACILITY/STATE/MI/YEAR/2023/JSON), [emissions](https://data.epa.gov/efservice/PUB_FACTS_SUBP_GHG_EMISSION/FACILITY_ID/1003582/JSON)) | #2 |
| NOAA NCCOS Lake Erie HAB bulletin | Updated **today, 19:56 UTC**. It reports a ~240 sq mi cyanobacteria bloom offshore of Monroe, MI. Sentinel-3 OLCI imagery is from Sep 29 (clouds since). Toxins are below the recreational limit ([PDF](https://cdn.coastalscience.noaa.gov/hab-data/forecasts/LErie_forecast/web_latest/current_bulletin.pdf)) | #3 |
| GLERL ERDDAP West Lake Erie water-quality grid | It exists, but coverage **ends Nov 2024**, so it is not live ([info](https://apps.glerl.noaa.gov/erddap/info/cppa_WLE/index.json)) | #3 (risk) |
| ElevenLabs Agents outbound phone calls | Native Twilio integration: an imported number can place outbound calls ([docs](https://elevenlabs.io/docs/agents-platform/phone-numbers/twilio-integration/native-integration)) | #1, #2 |

**What is actually built (checked in the repo):** only Fern. That covers `fern/assets` (3 moods × talking/listening HD loops), `fern/voice` (the ElevenLabs voice, lines, lip-sync pipeline) and `fern/persona.md`. GOES-19, Relay, Fetch.ai and FIRMS exist as researched plans with verified endpoints, **not code**. The reuse numbers below count them that way.

---

## Idea 1 (top pick): **Fern on Call**, a smoke-and-heat check-in line

**One-liner.** Fern watches the sky through GOES-19 and NOAA's smoke forecast. Before wildfire smoke or a heat wave reaches your block, she checks on the people most at risk. She calls them on an ordinary phone, lights up a FREE-WILi beacon by their bed ("press the button if you're okay"), and if nobody answers, she calls their daughter.

### Problem and user
- **Scale:**
  - Heat is the deadliest US weather. NOAA's 30-year average is 183 deaths a year, more than floods, tornadoes or hurricanes ([Fox Weather citing NOAA](https://www.foxweather.com/extreme-weather/heat-deadliest-weather-united-states)).
  - AARP reports that more than 80% of an estimated 12,000 annual US heat-related deaths are people over 60 ([AARP](https://www.aarp.org/health/healthy-living/extreme-heat-danger-older-adults.html)).
  - NWS's own advice is to check in on older adults living alone ([NWS heat safety](https://weather.gov/safety/heat)).
- **Michigan hook:**
  - Canadian wildfire smoke put Detroit's air among the world's worst. By August 2025, Wayne County had logged its **16th** air-quality alert day of the year, 14 of them for PM2.5 ([Planet Detroit](https://planetdetroit.org/2025/08/detroit-air-pollution-alert/), [Great Lakes Now](https://www.greatlakesnow.org/2025/05/30/wildfire-smoke-from-canadian-blazes-threatens-detroit-air-quality/)).
  - My AirNow archive scan shows Detroit hourly PM2.5 reaching **77 µg/m³** on Jul 31, 2025. Today it is about 1–2.
  - Detroit's asthma hospitalization rate is **16.8 per 10,000 vs 2.8 statewide** for 2021–2023 ([MDHHS](https://www.michigan.gov/mdhhs/-/media/Project/Websites/mdhhs/Keeping-Michigan-Healthy/Chronic-Disease-Epidemiology/Asthma-Epi/Hospitalization/Mich-Detroit-Asthma-Hospitalization-Rates-by-Zip-Code_2021-2023.pdf)).
- **Named user:**
  - *Mrs. G*, 78, in Southwest Detroit (48217, Michigan's most-monitored air). She has COPD, lives alone, has a landline and no smartphone.
  - Her daughter in Ann Arbor uses Relay.
  - The judge plays the daughter.
- **Why an agent that *calls* is the right medium (inference):** the people most at risk are the least likely to install an alert app. A phone call and a big physical button reach them, and the escalation to family is what protects them.

### How it works (one tool layer, reusable everywhere)
1. **`smoke_now(lat, lon)`:**
   - GOES-19 ADPC smoke flag and AODC aerosol optical depth at the pixel.
   - Whether the point sits in an NOAA HMS polygon, and its density (light/medium/heavy).
   - Nearest AirNow PM2.5 reading. The hourly file needs no key.
2. **`smoke_forecast(lat, lon)`:**
   - HRRR `MASSDEN` (near-surface smoke) for f01–f18 from the latest cycle, fetched by byte range.
   - Returns the forecast arrival time and peak value.
   - **This is the team's technical core** (see the measured result below).
3. **`heat_forecast(lat, lon)`:** NWS gridpoint apparent temperature plus active heat alerts. GOES-19 LSTC adds a "how hot your block's surface gets" figure.
4. **`triage(person)`:**
   - Formula: hazard × vulnerability (respiratory or cardiac condition, heat-sensitive medication class, age, lives alone, no AC) → action tier.
   - Tier 0: nothing.
   - Tier 1: text the caregiver.
   - Tier 2: call the person.
   - Tier 3: beacon alert, then escalate to the caregiver if there's no "I'm OK" within N minutes.
   - Optional: FinchNode's demo patient supplies conditions and medications. Its advocate already mapped CDC heat-and-medication classes ([FinchNode file](../sponsor-tracks/10-finchnode-healthtech.md), Sketch A).
5. **Channels:**
   - **FREE-WILi beacon:** LEDs show the AQI color, the screen shows Fern's mood, the speaker plays Fern's pre-rendered line, and a button press means "I'm OK".
   - **ElevenLabs Agents outbound call** through Twilio to a real phone number.
   - **Relay** for the caregiver: text plus an agent-initiated video call using the existing Fern loops.
   - **ASI:One / Fetch.ai** with the request "check on my mom in Detroit".

### The measured result (for the Technical Complexity judges and the LLM judge)
**Backtest the warning lead time.** For Michigan's two 2025 smoke peaks (Jun 4–7 and Jul 30–Aug 2), measure how many hours before Detroit's AirNow PM2.5 first crossed 35 µg/m³ the HRRR smoke forecast (archived cycles) and the GOES-19 smoke flag would have triggered Fern's call. Put "Fern would have called N hours before the air turned unhealthy" on screen. This number is **not known yet**: computing it is the work, and it could come out small. If it does, report it honestly. Sportable and Ventura both won while being candid ([2020](../year-research/2020.md), [2025](../year-research/2025.md)).

### Tracks
- **Main: Sustainability**, framed as *climate resilience*. The track text says "rethink energy, climate, and resource systems for lasting impact" ([Tracks](https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b)).
  - Adaptation has won Sustainability prizes elsewhere (SkySplat, Morro, Chilladelphia), but the debate rated it weaker on Adherence to Theme than mitigation ([SUMMARY](../SUMMARY.md) debate).
  - Open the pitch with "climate change is making smoke and heat days more frequent here", then show the data.
  - **AI** is the fallback if a help-desk answer says adaptation is off-theme. It is a bigger pool, but the track text ("solves a real problem") fits.
  - **Hardware: no.** The beacon is a small part, and a FREE-WILi is the floor in that pool.
- **Fun:** Judged by an LLM (the backtest number and a rubric-shaped Devpost). **Not** Dumbest Idea: a joke about elderly people in smoke would sink the main pitch.
- **Tone change from the Clean Hours persona:** Fern stays warm. With the at-risk person she is calm and clear, with no fainting-couch theatrics. Her humor lives only in the caregiver chat.

### Sponsor tracks, with genuine use
| Sponsor | Genuine use |
|---|---|
| **FREE-WILi** | The beacon *is* the product for a household without a smartphone: LED AQI color, Fern's mood on the 320×240 screen, Fern's voice from the speaker, and the button as the check-in. It works nothing like Wattson's pet. |
| **ElevenLabs** | The custom Fern voice (already built) across three surfaces: pre-rendered beacon lines, live **outbound phone calls** through the Agents + Twilio integration, and Relay call audio. That's two or more capabilities, with voice as the interface, which is the ElevenLabs winner pattern ([02](../sponsor-tracks/02-elevenlabs.md)). |
| **Relay** | The caregiver's channel: texts, a place card for the nearest cooling or clean-air center, and an **agent-initiated video call** when Mom doesn't check in. It uses the Fern loops already made. |
| **SpaceX** | Real space data at the core: GOES-19 ADP/AOD/LST, plus FIRMS showing *which* fires the smoke came from. Use the Grok Imagine API per event (about $0.04 per image, labeled as AI) for Fern's "my window today" card, build in Cursor, and keep `.cursor/rules`. **This still depends on the Earth-observation ruling** from SpaceXAI. |
| **Fetch.ai ASI:One** | The request "Is the air okay for my mom in Detroit? Check on her." runs triage and **fires the beacon and the call**, which is a real action. Cut it at 2 AM if it isn't working end to end. |
| FinchNode (optional) | Conditions and medications from the keyless demo API set vulnerability (COPD → smoke priority; diuretic or beta-blocker → heat priority). Enter only if it's wired into triage, not decorative. |

### Why it would win (past evidence)
- **F.L.U.D.D's escalation pattern** (2021) plus **Wattson's FREE-WILi Sustainability double win** (2025), pointed at a far bigger problem ([2021](../year-research/2021.md), [2025](../year-research/2025.md)).
- **MobiLens** won Fetch Best Use in 2025 with hardware + agents + caregiver alerts. That is the same shape ([2025](../year-research/2025.md)).
- **A named user, a Michigan statistic and an accessibility story.** Usability explicitly includes accessibility in the rubric ([2025](../year-research/2025.md) Researcher B).
- **A physical moment on the table:** the beacon turns red, then the judge's phone rings.

### Novelty and overlap check
- **Different from F.L.U.D.D:** that one used home sensors for flooding. This uses satellite and model forecasts for smoke and heat, adds vulnerability triage, and gives the user a check-in device.
- **Different from Wattson:** a pet that nags about energy. This is a safety device.
- AQI alert apps are common elsewhere (e.g. Wildfire Watch Canada on Devpost, [link](https://devpost.com/software/wildfire-watch-canada)). The novelty here is the **forecast lead time + call + beacon + escalation** loop, not "an AQI alert". Say that out loud.
- No MHacks winner in 2020–2025 addressed smoke or heat.

### Reuse (~65%)
- **Reused as-is:**
  - Fern's three moods: wilted = smoky or hot, normal = moderate, blooming = clean.
  - The talking/listening HD loops for Relay video calls and the saved ElevenLabs voice (`XnLFOJOtoPqkoo60ohxA`).
  - The lip-sync pipeline for one or two new talking clips (costs xAI credit, so only if needed).
- **Reused with edits:** the persona system prompt (swap the dryer for smoke/heat and add the tone rules).
- **Reused as knowledge:**
  - The verified GOES-19 S3 path and NetCDF approach (same bucket, different product).
  - The Relay call plan, the Fetch.ai plan (`uagents==0.25.5`), and FIRMS from Overpass.
- **Reused as hardware:** the FREE-WILi.
- **New spend:** none for xAI beyond optional per-event Grok Imagine stills.

### New work and hours (≈40 person-hours, 4 people, starting ~6:30 PM)
| Who | Work | Hours |
|---|---|---|
| P2 (data) | AirNow parser 0.5 · HMS point-in-polygon 1 · GOES-19 ADPC/AODC pixel lookup (lat/lon → fixed grid) 1.5 · HRRR MASSDEN byte-range forecast + arrival time 3 · Jul 31, 2025 replay mode 1 · lead-time backtest (2 events) 2 · NWS heat 1 | ~10 |
| P3 (brain) | Roster + vulnerability rules 2 · tier/escalation state machine 2 · Fetch uAgent + ASI:One 4 · map dashboard 2 · (FinchNode 1.5 optional) | ~10–11.5 |
| P1 (voice/agent) | Persona re-script + tone rules 1 · pre-render ~12 beacon lines with the saved voice 1 · ElevenLabs Agent + Twilio outbound call 2–3 · Relay caregiver chat + agent-initiated call with Fern loops 3 | ~8 |
| P4 (hardware/story) | FREE-WILi beacon (LED color, mood images resized to 320×240, audio playback, button acknowledgement) 4–5 · escalation hook 1 · real-life demo video 1 · Devpost (rubric headings + "What we measured") 2 · pitch 1 | ~10 |

**Cut order if behind:**
1. FinchNode.
2. Heat (smoke only).
3. Fetch.ai, at 2 AM.
4. Backtest down to one event.
5. Never cut: the beacon, the call and the live smoke path.

### Demo moment (about 90 seconds)
1. The FREE-WILi is on the table showing a green, blooming Fern. "This is Mrs. G's beacon in Southwest Detroit. She doesn't own a smartphone."
2. Press **Replay Jul 31, 2025**. The map shows the GOES-19 smoke mask, the HMS heavy-smoke polygon over Detroit, and the HRRR arrival forecast with the backtested lead time.
3. The beacon turns red and Fern wilts. The speaker plays Fern's voice: windows shut, run the filter fan, press the button if you're okay. **The judge doesn't press it.**
4. Sixty seconds later **the judge's phone rings**. It is an ElevenLabs phone call (or a Relay video call with Fern's face) to "the daughter", giving the real PM2.5 number and what to do.
5. Switch to **Live**: drop a pin on today's real heavy-smoke polygon in the western US, and the same pipeline fires on today's data.

### Risks (honest)
- **No live smoke or heat hazard in Michigan this weekend.** It is verified clean (PM2.5 ~1–2, 0 NWS alerts). The local demo has to be a *labeled replay*, and live-ness is shown with western smoke. This is the same weakness the debate raised against Overpass. The beacon and the call stay live either way.
- **Theme adherence** (adaptation). Ask the help desk, and frame it as climate resilience.
- **Twilio trial accounts only call verified numbers.** To ring an arbitrary judge's phone you need an upgraded account; otherwise ring a teammate's phone. The team creates its own Twilio/ElevenLabs accounts.
- HRRR GRIB2 parsing (eccodes/cfgrib) could eat 2–3 hours. Fallback: HMS + GOES + AirNow only, and drop the forecast arrival time.
- Relay calls are still unverified on the App Store build ([SUMMARY](../SUMMARY.md) gates). Fallback: the ElevenLabs phone call carries the demo.
- Health liability: Fern gives NWS/CDC/EPA guidance, never medical advice, and never "stop your medication".

**Scores:** win 6 · non-niche 9 · feasibility 6 · demo wow 8 · sponsor fit 8 · reuse 8.

---

## Idea 2: **Plume Patrol**, from methane seen from space to a leak fixed on the ground

**One-liner.** When Carbon Mapper's Tanager satellite publishes a methane plume over a Michigan landfill, an agent works out which facility it came from and compares it with what that facility reports to EPA. It then calls the operator with the evidence and checks back on the next overpass. Residents can text Fern "what's that smell in Northville?" and get the satellite record plus a ready-to-send EGLE complaint.

### Problem and user
- **Scale:**
  - Municipal solid-waste landfills are the **third-largest source of human-caused US methane**, about 14% ([EPA LMOP](https://www.epa.gov/lmop/basic-information-about-landfill-gas)).
  - In the Carbon Mapper / EPA study (Science, 2024), **52%** of 200+ surveyed landfills had point-source plumes, **60%** of those persisted for months or years, and measured rates were **1.4×** what GHGRP reported ([phys.org summary](https://phys.org/news/2024-03-landfill-source-emissions-outsized-impact.html), [Science](https://www.science.org/doi/10.1126/science.adi7735)).
- **The bottleneck is action, not detection.** Carbon Mapper says it delivered or supported 460+ methane notifications, which led to **68 confirmed mitigations** ([PR Newswire, Oct 1 2026](http://www.prnewswire.com/news-releases/tanager-2-launch-to-scale-up-carbon-mappers-methane-impact-302896690.html)). An agent that notifies, follows up and escalates targets exactly that gap (inference).
- **Michigan hook (verified today):**
  - All 23 CH4 plumes in a SE Michigan box are landfills, and they match EPA facility coordinates:
    - Riverview Land Preserve: 8 plumes, latest a Tanager pass on May 31, 2026.
    - Sauk Trail Hills, Canton: Tanager pass on Aug 31, 2026.
    - Arbor Hills, Northville, about 20 km from the venue.
    - Oakland Heights.
    - Carleton Farms.
    - The Waste Management facility at 5900 Hannan Rd, Wayne.
  - Arbor Hills settled with the Michigan AG and EGLE in 2022 for more than $2.3M over its gas collection and odors ([MI AG](https://www.michigan.gov/ag/news/press-releases/2022/03/10/ag-nessel-egle-reach-settlement-with-arbor-hills-landfill)). Later in 2022, EGLE said its methane levels violated the agreement ([Detroit News](https://www.detroitnews.com/story/news/local/wayne-county/2022/10/22/northville-landfill-methane-violates-michigan-agreement/69582029007/)).
- **SpaceX hook:** **Tanager-2 launched on SpaceX's Transporter-18 on Oct 1, 2026**, two days before MHacks ([PR Newswire](http://www.prnewswire.com/news-releases/tanager-2-launch-to-scale-up-carbon-mappers-methane-impact-302896690.html)).
- **Users:**
  1. Landfill environmental managers, who get the call.
  2. Nearby residents, who text and subscribe.
  3. Regulators and reporters, who get a weekly digest.

  It is a two-sided design like Quick Action (MHacks 15) ([2023](../year-research/2023.md)).

### The measured result (team-built core)
For each plume source, the agent does three things:
1. Attributes it to the nearest GHGRP facility within 1 km.
2. Converts the reported CH4 (t CO2e) to kg/h.
3. Compares it with the satellite or airborne source average, with uncertainty and a persistence score.

**Worked example from today's pull:**
- The Wayne (5900 Hannan Rd) source averages **2,134 ± 514 kg/h**, seen on 4 of 4 observation dates in 2021–22.
- The facility reported 181,540.5 t CO2e of CH4 for 2022. At GWP 25 (verify the GWP that GHGRP used for that year) that is about **829 kg/h**, so the satellite/airborne figure is ≈**2.6×** (≈2.0–3.2× across the uncertainty).
- Riverview goes the other way: 786 ± 179 kg/h measured against ≈1,162 kg/h reported, about 0.7×.

Present these as **daytime snapshots vs. annual averages: "indicative, not a violation finding"**. The honest ranking is the product.

### Tracks
- **Main: Sustainability**, the strongest theme fit of the three. It is mitigation of a resource system (waste).
- **Fun:** Judged by an LLM.
- **Sponsors:**
  - **SpaceX:** satellite methane from a constellation SpaceX just launched. The cleanest "real space data" story of any idea. Add Grok Voice or Imagine for the call or the evidence card.
  - **Fetch.ai:** a watcher agent (polls `published_at`), an attributor agent and a notifier agent. ASI:One request "any methane leaks near Ann Arbor?" → it sends a notification or a drafted complaint, a real action.
  - **Relay:** residents text Fern, and she calls them when a new plume is published within 15 km.
  - **ElevenLabs:** the operator-notification call voice.
  - **FREE-WILi: none.** Say so.

### Why it would win, and novelty
- It hits pattern 5 (a computed core on real data) and pattern 6 (an agent that closes the loop) ([SUMMARY](../SUMMARY.md)).
- The local Arbor Hills saga means the judges are Michigan residents.
- No MHacks winner from 2020–2025 touched methane. The 2025 Greenprint field was carbon calculators ([01](../main-and-fun-tracks/01-main-sustainability.md)).
- I found no hackathon project using the Carbon Mapper API with an agent (search, not exhaustive).

### Reuse (~40%)
- **Reused:** Fern (persona, voice, mood loops; a wilted Fern for a big plume), the Relay and Fetch plans, and Cursor/Grok for SpaceX.
- **Not reused:** GOES-19, FIRMS and the FREE-WILi.
- **Mismatch to handle:** methane itself is odorless, so the "smell" line has to be scripted carefully (inference).

### New work and hours (~24 person-hours)
| Work | Hours |
|---|---|
| Carbon Mapper client (plumes + `sources.geojson`) | 2 |
| GHGRP pull, attribution, unit and uncertainty math | 2 |
| Persistence ranking and watcher | 2 |
| Leaflet map with `plume_png` overlays (bounds come with each plume) | 3 |
| Operator-notification call/email with evidence, plus follow-up tracker | 4 |
| Relay resident agent | 3 |
| Fetch.ai agents | 4 |
| Persona re-script | 1 |
| Devpost | 3 |

### Demo moment
- The map opens on the venue. Five landfill pins glow around Ann Arbor, and Arbor Hills is ~20 km away.
- Tap Wayne: the Tanager/airborne plume image and the "2.6× what it reports" card appear.
- Press **Notify**. The judge's phone rings: Fern, in a calm professional register, gives the plume coordinates and rate and asks the "site manager" to check that cell. The follow-up gets logged for the next overpass.
- Then show the live feed: "Carbon Mapper published new plumes at 19:19 UTC today. Here they are."

### Risks
- **No new Michigan plume will likely publish during the hackathon.** Publication lags the observation by about 30 days (Aug 31 scene → published Sep 30). The live trigger works on US-wide plumes.
- **Naming real companies:** use careful, sourced language, never say "violation", and **never notify a real operator or file a real complaint** during the event. Send to a team inbox and role-play instead.
- Carbon Mapper's terms require citing it as the data provider ([API description](https://api.carbonmapper.org/api/v1/openapi.json)).
- Less personal for judges ("would I use this?"). The resident channel addresses that.

**Scores:** win 5 · non-niche 7 · feasibility 7 · demo wow 6 · sponsor fit 7 · reuse 5.

---

## Idea 3: **Bloomline**, Lake Erie's toxic algae bloom, on call

**One-liner.** Subscribers register their beach, marina, fishing spot or dog-walk shoreline. Each day the agent reads NOAA's Lake Erie bloom bulletin, with Sentinel-3 satellite imagery and a 5-day bloom-position forecast. It texts or calls before scum is likely at your spot ("calm winds plus bloom = scum"), and one tap files a photo bloom report to the state.

### Problem and user
- **Live today:** NOAA's bulletin, updated at 19:56 UTC, reports a **~240 sq mi bloom offshore of Monroe, MI**, with patches along the Michigan and Ohio coasts and in Maumee Bay. The scum warning tells you to keep pets out ([bulletin](https://cdn.coastalscience.noaa.gov/hab-data/forecasts/LErie_forecast/web_latest/current_bulletin.pdf)).
- **Stakes:** in August 2014 nearly half a million Toledo residents were told not to drink tap water after microcystin from a Lake Erie bloom reached the city's intake ([WTOL timeline](https://www.wtol.com/article/news/local/protecting-our-water/5-years-since-the-toledo-water-crisis-a-timeline-of-what-happened/512-71a2414b-a34d-4b4a-9632-58e1c212d098), [Michigan Radio](https://www.michiganradio.org/post/toledo-works-restore-trust-its-water-after-2014-microcystin-scare)). NOAA forecast a moderate (3.5) bloom for 2026 ([NCCOS](https://coastalscience.noaa.gov/news/moderate-harmful-algal-bloom-predicted-for-western-lake-erie-in-summer-2026/)).
- **Users:** anglers, boaters, dog owners and beach-goers on the Michigan and Ohio shore. Water-intake operators would be a stretch goal.

### Tracks and sponsors
- **Main: Sustainability**, as water-resource systems. That is a better theme fit than #1 and a weaker one than #2.
- **Fun:** Judged by an LLM.
- **Sponsors:**
  - Relay: subscriber texts and calls.
  - ElevenLabs: the voice.
  - Fetch.ai: ASI:One "is it safe for my dog at Sterling State Park?" → answer plus a filed report.
  - SpaceX: Sentinel-3 OLCI is Earth observation, but it isn't a SpaceX-launched satellite and the team uses NOAA's product, not raw data. Weak.
  - FREE-WILi: none.

### Why it could win, and overlap
- It is the most "live and local" of the three: the bloom exists today, about 40 miles from the venue.
- F.L.U.D.D and Water Monitor (2021) show that Michigan water stories win smaller prizes ([2021](../year-research/2021.md)). Water Monitor's overlap is real but partial: it was a heatmap with no agent and no alerts.
- Algal-bloom detection projects are common at other hackathons (inference).

### Reuse (~35%)
Fern (blooming vs. wilted gets an ironic twist: "my cousins the cyanobacteria are blooming"), the voice, the Relay and Fetch plans. Nothing from GOES or the FREE-WILi.

### New work and hours (~26 person-hours)
| Work | Hours |
|---|---|
| Bulletin fetch and text parse | 1 |
| Extract the bulletin's map images and **georeference them by hand-calibrated corners**, then color-classify at each spot | 4–5 (high risk; leave a calibration knob) |
| NWS marine wind | 1 |
| Spot registry with Michigan beaches | 1.5 |
| Risk rules | 1.5 |
| Relay agent and call | 3 |
| Photo report draft to EGLE (in the demo, sent to a team inbox) | 2 |
| Fetch.ai | 4 |
| Dashboard | 2 |
| Devpost | 2 |

### Demo moment
"The bloom off Monroe is real, and here's today's NOAA bulletin." Register Sterling State Park, and the 5-day forecast shows bloom drifting toward the shore with calm winds Tuesday. Fern calls: keep the dog out, here's the satellite image, and want me to tell your fishing group?

### Risks
- **No machine-readable live bloom grid found.** The GLERL ERDDAP grid ends in Nov 2024, so the pipeline depends on parsing NOAA's PDF maps.
- Clouds have blocked imagery since Sep 29.
- The season ends within weeks.
- It is regional and seasonal, which makes it the most niche of the three.
- The technical core is thin unless the team processes Sentinel-3 itself, which isn't realistic in 18 hours.

**Scores:** win 4 · non-niche 5 · feasibility 6 · demo wow 6 · sponsor fit 5 · reuse 4.

---

## Considered and rejected
- **Grid-scale demand response (MISO peak events, big flexible loads):** this is the only "bigger-load" scheduling variant, and it is still scheduling. The 2024 MLH Streamlit winner already shifted data-center load to clean hours ([2024](../year-research/2024.md)). The user is a facility manager, with no personal demo user. It fails the team's niche test.
- **Flash-flood or basement alerts with GOES-19 rain rate:** the data is live (RRQPEF verified), but it is F.L.U.D.D (2021) with satellites, too close to a past MHacks winner.
- **Farm runoff ("don't spread manure before the storm"):** timely, since fall is manure season and it feeds Lake Erie blooms, but the user is too narrow for a student and engineer jury ("would I use this?").
- **Urban-heat tree planting:** Chilladelphia already won this at PennApps ([01](../main-and-fun-tracks/01-main-sustainability.md)), it has no live trigger, and the agent can't act.

---

## Top pick and why

**Fern on Call (#1).** It is the only idea that scores well on every criterion at once:
- **The biggest non-niche problem:** heat is the deadliest US weather, and smoke drove Wayne County to 16 alert days by August 2025.
- **The most reuse:** Fern's moods, voice and loops fit with no new xAI spend, and the GOES-19 plan carries over with a product swap.
- **The only genuine FREE-WILi use:** a no-smartphone check-in beacon. That keeps the proven Sustainability + FREE-WILi double-win path from Wattson open without copying Wattson.
- **The strongest physical demo moment** (the beacon goes red, then the judge's phone rings) plus a team-built measured result (the forecast lead time).

Its weak spots are the October timing (labeled replay plus live western smoke) and adaptation-vs-mitigation theme risk. Answer both in the first 20 seconds of the pitch.

**If SpaceXAI has already ruled that Earth observation doesn't count,** #1 loses SpaceX but keeps everything else. If the team values SpaceX above FREE-WILi, build **#2** instead. A satellite SpaceX launched two days ago is the clearest "real space data" case available.

### First three hours if you pick #1 (6:30–9:30 PM)
- **P2:** AirNow + HMS + one GOES-19 ADPC pixel for Detroit on Jul 31, 2025. Prove the replay end to end.
- **P4:** FREE-WILi shows the three resized Fern PNGs, sets the LED color, plays one WAV from `fern/voice`, and reads the button.
- **P1:** ElevenLabs Agent + Twilio outbound call rings a teammate's phone with one scripted line.
- **P3:** the triage table and the escalation timer as a stub. Ask the help desk whether climate-resilience projects count for Sustainability.
- **Go/no-go at 9:30 PM:** beacon + call + replay working → commit. If not, fall back to #2, which needs no hardware.

---

## Sources

**Past-winner research (this repo):** [2025](../year-research/2025.md) · [2024](../year-research/2024.md) · [2023](../year-research/2023.md) · [2022](../year-research/2022.md) · [2021](../year-research/2021.md) · [2020](../year-research/2020.md) · [SUMMARY](../SUMMARY.md) · [01 Sustainability](../main-and-fun-tracks/01-main-sustainability.md) · [07 main/fun verdict](../main-and-fun-tracks/07-debate-and-verdict.md) · [13 sponsor verdict](../sponsor-tracks/13-debate-and-verdict.md) · [10 FinchNode](../sponsor-tracks/10-finchnode-healthtech.md) · [07 SpaceX](../sponsor-tracks/07-spacex-make-it-legendary.md) · [11 Relay](../sponsor-tracks/11-relay-interactive-agents.md) · [02 ElevenLabs](../sponsor-tracks/02-elevenlabs.md) · [04 FREE-WILi](../sponsor-tracks/04-free-wili.md)

**Past winners cited:** [Wattson](https://devpost.com/software/wattson-5btsyd) · [F.L.U.D.D](https://devpost.com/software/f-l-u-d-d) · [Water Monitor](https://devpost.com/software/water-monitor-96zalt) · [SunLite](https://devpost.com/software/sunlite-sunrise-lamp) · [MobiLens](https://devpost.com/software/mobilens) · [FarmX](https://devpost.com/software/farmx-zpw0yq) · [SolarVista](https://devpost.com/software/solarvista) · [Dynamic Load Balancing (2024)](https://devpost.com/software/dynamic-load-balancing-for-energy-efficient-cloud-computing) · [Quick Action](https://devpost.com/software/quick-action) · [Wildfire Watch Canada (non-MHacks)](https://devpost.com/software/wildfire-watch-canada)

**Live data probed today:**
- GOES-19 S3: [ADPC 2026/276](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-ADPC/2026/276/) · [AODC](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-AODC/2026/276/) · [LSTC](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-LSTC/2026/276/) · [RRQPEF](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-RRQPEF/2026/276/) · [ADPC 2025/213 archive](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-ADPC/2025/213/17/)
- NOAA HMS smoke KML: https://satepsanone.nesdis.noaa.gov/pub/FIRE/web/HMS/Smoke_Polygons/KML/2026/10/
- HRRR on AWS: https://noaa-hrrr-bdp-pds.s3.amazonaws.com/hrrr.20261003/conus/hrrr.t18z.wrfsfcf01.grib2.idx
- AirNow hourly files: https://files.airnowtech.org/airnow/today/HourlyData_2026100319.dat · archive https://files.airnowtech.org/airnow/2025/20250731/HourlyData_2025073114.dat
- NWS alerts: https://api.weather.gov/alerts/active?area=MI
- Carbon Mapper: https://api.carbonmapper.org/api/v1/catalog/plumes/annotated · https://api.carbonmapper.org/api/v1/catalog/sources.geojson · https://api.carbonmapper.org/api/v1/openapi.json
- EPA GHGRP Envirofacts: https://data.epa.gov/efservice/PUB_DIM_FACILITY/STATE/MI/YEAR/2023/JSON · https://data.epa.gov/efservice/PUB_FACTS_SUBP_GHG_EMISSION/FACILITY_ID/1003582/JSON · https://data.epa.gov/efservice/PUB_DIM_GHG/JSON
- NOAA Lake Erie HAB bulletin: https://cdn.coastalscience.noaa.gov/hab-data/forecasts/LErie_forecast/web_latest/current_bulletin.pdf
- GLERL ERDDAP (not live): https://apps.glerl.noaa.gov/erddap/info/cppa_WLE/index.json

**Facts and context:**
- Heat deaths: https://www.foxweather.com/extreme-weather/heat-deadliest-weather-united-states · https://www.aarp.org/health/healthy-living/extreme-heat-danger-older-adults.html · https://weather.gov/safety/heat
- Michigan smoke: https://planetdetroit.org/2025/08/detroit-air-pollution-alert/ · https://www.greatlakesnow.org/2025/05/30/wildfire-smoke-from-canadian-blazes-threatens-detroit-air-quality/ · https://planetdetroit.org/2025/05/wildfire-smoke-michigan-air-quality/
- Detroit asthma: https://www.michigan.gov/mdhhs/-/media/Project/Websites/mdhhs/Keeping-Michigan-Healthy/Chronic-Disease-Epidemiology/Asthma-Epi/Hospitalization/Mich-Detroit-Asthma-Hospitalization-Rates-by-Zip-Code_2021-2023.pdf
- Landfill methane: https://www.epa.gov/lmop/basic-information-about-landfill-gas · https://phys.org/news/2024-03-landfill-source-emissions-outsized-impact.html · https://www.science.org/doi/10.1126/science.adi7735
- Tanager-2 / Carbon Mapper impact: http://www.prnewswire.com/news-releases/tanager-2-launch-to-scale-up-carbon-mappers-methane-impact-302896690.html
- Arbor Hills: https://www.michigan.gov/ag/news/press-releases/2022/03/10/ag-nessel-egle-reach-settlement-with-arbor-hills-landfill · https://www.detroitnews.com/story/news/local/wayne-county/2022/10/22/northville-landfill-methane-violates-michigan-agreement/69582029007/
- Lake Erie / Toledo: https://coastalscience.noaa.gov/news/moderate-harmful-algal-bloom-predicted-for-western-lake-erie-in-summer-2026/ · https://www.wtol.com/article/news/local/protecting-our-water/5-years-since-the-toledo-water-crisis-a-timeline-of-what-happened/512-71a2414b-a34d-4b4a-9632-58e1c212d098 · https://www.michiganradio.org/post/toledo-works-restore-trust-its-water-after-2014-microcystin-scare
- ElevenLabs outbound calls: https://elevenlabs.io/docs/agents-platform/phone-numbers/twilio-integration/native-integration
- MHacks 2026 track text: https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b

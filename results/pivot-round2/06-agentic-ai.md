# Ideas — Agentic-AI lens

## Prompt given (excerpt)
> Your lens: Agentic-AI lens. Ideas where an AI agent takes real actions for people on a broad sustainability problem (negotiates, files, books, switches, buys, reports, coordinates), using voice/messaging interfaces where natural (ElevenLabs, Relay, Photon, Fetch.ai ASI:One). The action must create real environmental impact for many people. Propose 3 distinct, concrete ideas for the Sustainability main track that (a) clearly fit the winning formula, (b) are NOT niche by the definition above and reach the Watt's Up bar on all five points while being original, (c) are not on the saturated list, and (d) are buildable by 4 students in ~18 h with a strong 3-minute demo. For each, verify the key data/APIs exist and are accessible, name the closest past winners and how yours differs, and list only the sponsor tracks that fit naturally.

*Written Sat Oct 3, 2026, about 7:30 PM EDT, with about 16.5 hours of hacking left.*

**Tags:**
- **[V]** I checked it myself today: I fetched the page, called the API, or downloaded and analysed the data.
- **[S]** From a search-result summary. I did not open the page.
- **[F]** From a team research file.
- **[I]** My inference or estimate.

Inputs read: `year-research/2020–2025.md`, the "Lessons" and "Cross-check" sections of `SUMMARY.md`, `pivot-ideas/01-past-winner-patterns.md`, `pivot-ideas/00-synthesis.md`, `sponsor-tracks/13-debate-and-verdict.md`, and the Relay (11), Photon (06), ElevenLabs (02), SpacetimeDB (08), Fetch.ai (01) and SpaceX (07) advocate files.

---

## TL;DR

| # | Idea | The agent's real action | Who, and how many | How often | Hard number on screen | Natural sponsor tracks |
|---|---|---|---|---|---|---|
| **1 (top pick)** | **Drafty**: your rental's heat leaks, fixed by the landlord, with the agent making the call | Reads your heating bill, then **calls your landlord**. It brings the cheapest route to the 70 points Ann Arbor's new Green Rental Housing law requires, shows who pays for it (up to 90%), books the assessment, and checks your next bill | 54.5% of Ann Arbor households rent: about 31,500 units in about 8,500 properties. About a third of Americans rent | Every bill in winter, plus every lease decision | About 500 of about 8,500 rental properties had complied by July 2026. 41% of Michigan's gas-heated homes are leaky; sealing and insulating them cuts gas use about 14% | ElevenLabs, Relay |
| 2 | **Seatmate**: carpools your agent negotiates for you | Every evening it **negotiates tomorrow's pickups** with other commuters' agents, re-plans when someone texts "running late", and splits fuel and the U-M permit | 78,014 people commute into Ann Arbor jobs, 81% of the city's jobs | Twice a day, every workday | 72% of in-commuters share a home tract and work tract with at least 3 others | Fetch.ai ASI:One, SpacetimeDB, Relay |
| 3 | **Mend**: repair-first, with the agent doing the phoning | Shown a broken item, it **calls repair shops in parallel**, books the best quote, orders the part or files the warranty claim | Every household | Whenever something breaks | Repair could save the average family $382/yr. Making one smartphone emits about 84 kg CO2e | ElevenLabs, Relay |

**Top pick: Drafty.**
- **Closest to Watt's Up.** It has the same shape (an address or bill goes in, a personal answer in money and carbon comes out, and it scales to a city map) but answers a different question.
- **Strongest local hook on the board.** Ann Arbor's Green Rental Housing ordinance took effect Jan 6, 2026. Insulate Ann Arbor launched in April 2026.
- **Data core verified today.** Michigan ResStock is downloaded and a test model is trained (numbers in §1).
- **The call does the work.** The live call to the landlord is the product, not decoration.

**The honest catch.** Each Michigan home saves only a modest amount: a median of $102/yr for leaky gas-heated homes. And heat pumps *raise* median bills for Michigan gas homes in ResStock (§1). So Drafty leads with compliance, comfort and who pays, and never overclaims savings.

### How I applied the lens
1. **The action is the product.** Each idea has one agent action the judge watches happen in the first minute: a phone call to the landlord, pickups renegotiated across phones, or parallel calls to repair shops. An agent that only explains things fails this lens.
2. **Consent first.** The FCC's Feb 8, 2024 ruling treats AI-generated voices as "artificial" under the TCPA, which means prior consent, identification and opt-out ([FCC](https://docs.fcc.gov/public/attachments/DOC-400393A1.pdf)) [S]. Every design below therefore texts or emails first and **calls only after the person opts in**. In the demo, the person called is always a teammate.
3. **One prize per project in person.** Each idea lists only the 1–3 sponsor tracks whose own product the build actually exercises [F SUMMARY].
4. **Satellite data is honest or absent.** Under this lens satellite data is a supporting input, not the core. Drafty uses NASA POWER degree-days and building footprints ML-extracted from imagery. Its one real satellite option, a Sentinel-2 snow-on-roof layer, is gated because it is an experiment. Seatmate and Mend use no space data and do not claim SpaceX.

---

## Idea 1 — Drafty: your rental's heat leaks, fixed by the landlord, with the agent making the call

### One-liner
Text Drafty your address, or a photo of your DTE bill. In seconds it shows how many dollars and kilograms of CO2 your rental leaks each winter, and roughly how many of the **70 points** Ann Arbor's Green Rental Housing law requires the unit already has. Then, with your approval, it **calls your landlord**. On the call it brings the cheapest path to compliance and the rebates that pay for 50–90% of it, and it books the energy assessment. Your next bill shows whether the fix worked.

### Who and how many
- **Renters, who are most of the city.**
  - 54.5% of Ann Arbor's 50,499 occupied units are renter-occupied ([Census Reporter, ACS 2019–23](http://censusreporter.org/profiles/16000US2603000-ann-arbor-mi/)) [S].
  - The city counts about 31,500 rental units across about 8,500 properties. Their median year built is 1964, and Michigan's first energy code dates from 1977 ([GRH FAQ](https://www.a2gov.org/media/yykptaqy/grh-faq.pdf)) [V].
- **Nationally,** about a third of Americans rent. Over 90% of renters pay at least some of their energy bills, and about three-quarters pay all of them ([Binghamton study in *Energy Research & Social Science*, via Phys.org Jan 2026](https://phys.org/news/2026-01-left-cold-renters-energy.html)) [V].
- **Energy hardship is common.** 27% of US households had difficulty meeting their energy needs in 2020 ([EIA RECS](https://www.eia.gov/todayinenergy/detail.php?id=51979)) [S].
- **Landlords are the second user.** The ordinance applies to every off-campus rental unit in the city ([GRH FAQ](https://www.a2gov.org/media/yykptaqy/grh-faq.pdf)) [V]. By Jul 28, 2026 only "over 500" rental properties had complied ([Concentrate](https://concentratemedia.com/500-ann-arbor-rentals-now-in-compliance-with-new-green-housing-ordinance/)) [V].

### How often it's used
- **Monthly through the heating season.** Each DTE bill is re-read and weather-normalised with NASA POWER heating degree-days. The leak estimate is updated, and after a fix the savings are checked.
- **At every lease decision.** Michigan renters' modelled annual energy bills run from **$1,031 to $3,319 (10th–90th percentile)**. Two units at the same rent can differ by about $2,000 a year in energy ([ResStock 2024.2 MI](https://data.openei.org/s3_viewer?bucket=oedi-data-lake&prefix=nrel-pds-building-stock%2Fend-use-load-profiles-for-us-building-stock%2F2024%2Fresstock_tmy3_release_2%2F)) [V: my calculation].
- **At every rental inspection** for landlords.

### Why it isn't niche
- **Broad problem.** Renters are the majority of Ann Arbor households and about a third of Americans. Heating bills arrive every winter, and the law covers every rental in the city.
- **Value in one sentence:** *"Your landlord now has to fix your drafty apartment, and Drafty makes the call, with the city and DTE covering most of the cost."*
- **Not just Ann Arbor.** The city based the ordinance on Boulder's SmartRegs ([GRH FAQ](https://www.a2gov.org/media/yykptaqy/grh-faq.pdf)) [V]. Any city with rental efficiency rules uses the same engine.
- **Specific demo, broad problem.** The specificity (one duplex, one landlord) lives in the demo. The problem itself is the split incentive: renters pay the bill but can't fix the building.

### Winning-formula match
- **Broad problem, specific demo.** The judge types their own address. The insight, ZoneZero-style: "renters pay the heat but can't fix the building; landlords can fix it but don't pay the heat" [I].
- **Watch it happen.** About a minute in, a teammate's phone rings and Drafty negotiates with the "landlord" live, handling objections with numbers.
- **A core we built, with numbers.**
  - A ResStock-trained model of leakiness and gas use, calibrated against the tenant's bill.
  - A cheapest-path-to-70-points optimiser.
  - On screen: model AUC, "41% leaky", and "14% gas cut" (all from my tests below).
- **Local hook.**
  - The Green Rental Housing (GRH) ordinance took effect Jan 6, 2026: 70 points through Jul 5, 2028, then 110 ([checklist](https://www.a2gov.org/media/dxxnmkyt/green-rental-housing-checklist.pdf)) [V].
  - Insulate Ann Arbor launched Apr 23, 2026 ([WEMU](https://www.wemu.org/wemu-news/2026-04-23/ann-arbor-dte-launch-energy-efficiency-rebate-program-for-multi-family-housing)) [V].
  - Buildings are 68% of Ann Arbor's emissions ([Ann Arbor Observer](https://annarborobserver.com/a2zero-six-years-in/)) [V].
- **Touches a resource system, not a conscience.** The target is the building stock, the same lesson FarmX, GreenPrint and Dynamic Load Balancing teach [F]. Nothing asks the renter to feel guilty.
- **A decision, not a dashboard.** The output is a ranked compliance plan with net cost after rebates.
- **Money and carbon in one view, home to city.** One card shows $/yr and kg CO2/yr. A city "leak map" helps the city's Office of Sustainability and Innovations (OSI) and Insulate Ann Arbor target buildings.
- **An outside voice is within reach.** The GRH FAQ invites questions to OSI's Joe Lange. A short email or call quoted in the Devpost would add ZoneZero's "real expert" signal [I].

### Closest past winners, and how Drafty differs
| Past project | What it did | Difference |
|---|---|---|
| [Watt's Up](https://devpost.com/software/watt-s-up) (HackPrinceton F25, Best Overall) | Address in, solar report out, with a bill-upload "Savings Mirror" and an equity index [V] | A different question: heat *loss*, not solar generation. Built for renters, not roof owners. And an agent *acts* on the answer instead of reporting it |
| [ZoneZero](https://devpost.com/software/zonezero) (TreeHacks 2026) | Address in, Zone 0 wildfire compliance (LE-100), with an expert insight [F] | The same compliance-plus-insight shape, applied to a *daily-life* rule (GRH) instead of a rare hazard. The agent negotiates the fix |
| [Chilladelphia](https://devpost.com/software/chilladelphia) (PennApps XXV) | Address in, heat rating from imagery [F] | Indoor heating costs, not outdoor heat. It acts instead of advising |
| [GreenPrint](https://devpost.com/software/greenprint-c2deb1) (MHacks 2025, AgentMail) | IoT building CO2 hub that emails alerts [F] | No sensors needed. The agent's action is a negotiation that ends in a retrofit |
| [Wattson](https://devpost.com/software/wattson-5btsyd) (MHacks 2025 Greenprint) | A pet that nags you about lights [F] | Changes the building, not the tenant's behaviour |
| Outside hackathons | The A2ZERO Heat Pump Concierge (Pearl Edison) gives **homeowners** designs and guaranteed prices ([a2gov](https://www.a2gov.org/news/posts/a2zero-heat-pump-concierge-platform-offers-convenient-switch-to-clean-healthy-heating-and-cooling/)) [V]. RentRelay (DivHacks 2026) splits ConEd bills among tenants ([GitHub](https://github.com/arpeymorshed/DivHacks-2026-Track-2)) [S]. BidBot (HackHayward 2026, AI track 1st) calls contractors for quotes ([Devpost](https://devpost.com/software/bidbot)) [V] | Drafty serves the **54.5% the concierge doesn't**, which is renters. It brings the landlord a *policy-backed business case*, not a quote request |

I found no hackathon winner for tenant–landlord efficiency (searched Devpost for tenant/landlord/insulation/energy agents) [V: searched].

### Technical core we build
1. **Leak model, trained by us.** We train it on NREL **ResStock 2024.2, Michigan**: 18,756 modelled dwellings that represent about 4.73M homes, with 288 columns. The columns include tenure, vintage, building type, county, infiltration (ACH50, air changes per hour at 50 Pa), ceiling insulation, and bills and emissions. The release also has 16 upgrade packages, including #16 "Envelope Only – Light Touch Envelope" with per-home savings [V: downloaded and inspected].
   - **My quick tests today** (gradient boosting, 20% held out, gas-heated homes):
     - Predicting annual gas use: R² **0.646** from public features alone, **0.737** once envelope features are added.
     - Classifying "leaky" (≥20 ACH50): AUC **0.765** from public features. Adding the annual gas use per sq ft that a bill reveals raises it to **0.825** [V: my run].
   - So the bill is exactly what fills in the hidden envelope. *Caveat: this is model-on-model validation with simulated homes, not real bills.*
2. **Bill calibration (PRISM-style).**
   - A vision LLM extracts therms, kWh and billing dates from a bill photo.
   - We fit usage against NASA POWER `HDD18_3` for the billing period. The API returns this for Ann Arbor [V], sourced from MERRA-2.
   - The fit gives a heating slope that feeds the classifier, which outputs P(leaky) and savings ranges from ResStock upgrade 16.
3. **GRH compliance optimiser.**
   - The checklist becomes a small integer program. Point values come from the city PDF: air sealing 9, attic R-50 9, walls 9, ducts 9, foundation 9, cold-climate heat pump 10–30, heat-pump water heater 15, plus 2-point items such as weatherstripping, LEDs and bus passes ([checklist](https://www.a2gov.org/media/dxxnmkyt/green-rental-housing-checklist.pdf)) [V].
   - It minimises the landlord's **net** cost after rebates, subject to ≥70 points, with tenant savings as the tie-breaker. The rebates it applies:
     - **DTE**, for buildings of ≤2 units: $600 for attic insulation, plus a $250 "Do More" bonus for installs Sept 15–Dec 15, 2026 ([DTE](https://www.dteenergy.com/us/en/residential/save-money-energy/rebates-and-offers/insulation-and-windows.html)) [V].
     - **Insulate Ann Arbor**, for buildings of ≥3 units: 50% of costs up to $75k, or 90% up to $250k if income-qualified [V].
     - **MiHER**, if the household is income-qualified: $1,600 for insulation and air sealing at ≤80% of area median income ([EGLE FAQ via search](https://www.michigan.gov/egle/faqs/climate-and-energy/home-energy-rebates-program)) [S].
   - Measure costs are estimates [I], shown as ranges.
4. **The agent.** An ElevenLabs voice agent with tools `get_plan`, `propose_times`, `send_summary` and `log_outcome`.
   - It places outbound calls through the Twilio endpoint `/v1/convai/twilio/outbound-call` ([docs](https://elevenlabs.io/docs/agents-platform/api-reference/twilio/outbound-call)) [S].
   - Consent ladder: Drafty first texts or emails the landlord a one-page plan and calls only on "reply CALL".
   - The tenant's side runs in Relay. The tenant texts the bill photo, asks "what should I do first?", or video-calls so the agent can see the window. Relay agents can read the person's camera frame by frame [F 11].
   - Those photos double as the **documentation the GRH checklist requires** [V checklist].
5. **City leak map.**
   - The leak model runs over Ann Arbor's building footprints ([Microsoft US Building Footprints](https://github.com/microsoft/USBuildingFootprints), repo reachable [V]), with vintage priors.
   - Output: a 3D map coloured by P(leaky), plus an estimate of each building's gap to 70 points. That gives OSI and Insulate Ann Arbor a targeting list.
6. **Optional satellite layer (gated, not core).**
   - Sentinel-2 L2A on Feb 15, 2026 is a clear, snow-covered scene over Ann Arbor: 0.87% cloud, 89.98% snow/ice ([Earth Search STAC](https://earth-search.aws.element84.com/v1)) [V: queried].
   - The idea: flag flat roofs on 3+ unit buildings that are bare among snow-covered surroundings as candidate heat leaks.
   - Keep it only if bare roofs correlate with pre-1977 vintage. At 10 m, small houses are only 1–2 pixels, so this works for apartment blocks only. The next clear scene (Feb 27) was already about 3.5% snow, so melt *timing* can't be used [V].

### Demo (3:00, at the table)
1. **0:00, hook.** "54% of Ann Arbor households rent. Since January, every rental must score 70 points on the city's green checklist. By July, only about 500 of about 8,500 properties had. Renters pay the heat but can't fix the building."
2. **0:20, the judge's own input.** The judge types any Ann Arbor address, or picks our example 1920s duplex. Within about 8 s the card reads: "Leaky (82%). ~$X/yr and ~Y kg CO2/yr of avoidable heat. Estimated checklist points: 22 of 70." The building glows on the 3D map.
3. **0:45, the bill.** We upload a teammate's DTE bill photo. The heating slope is 1.6× similar homes, so the leak estimate tightens.
4. **1:05, the call.**
   - In Relay we ask "What should I do first?" and Drafty answers in one sentence.
   - We say "Call my landlord." A teammate's phone rings and Drafty, after an AI disclosure, says roughly: *"Air sealing plus attic insulation gets 18 of the 48 points you're missing. Insulate Ann Arbor covers half, and your tenant's gas use drops about 14%."*
   - The "landlord" objects ("too expensive"). Drafty answers with the net cost and the inspection deadline, then books DTE's free assessment.
   - An email summary lands.
5. **2:00, the city view.** The leak map, the model numbers (AUC 0.765 → 0.825 with a bill), and the "next bill" verification view with a simulated February bill.
6. **2:40, close.** The same engine works in any city with rental standards. What doesn't work yet: STREAM inspection lookup is manual, and the cost ranges are estimates.

### Sponsor tracks that fit naturally
- **ElevenLabs.** The phone call is the core action, not narration.
- **Relay.** The tenant's agent, which you text and video-call. It reads the bill photo and sees the drafty window.
- *Not natural:* Fetch.ai, Nessie, SpacetimeDB and Photon (Photon would just duplicate Relay).
- *SpaceX only if* the Sentinel-2 layer passes its gate **and** the team builds with Cursor and uses Grok Voice or Imagine. Otherwise it would be a token entry.

**Fun track:** Judged by an LLM, with a rubric-shaped Devpost of about 500 words.

### 18-hour build plan (H0 = 6 PM Sat; submit by H17.5)
| Time | P1 Data/ML | P2 Rules/optimiser | P3 Agent/voice | P4 Frontend/story |
|---|---|---|---|---|
| H0–1 (gates) | Load the MI baseline and upgrade-16 parquet (7 MB + 12 MB) | Transcribe the checklist and rebate table | **Gate:** ElevenLabs + Twilio outbound call rings a teammate. Upgrade Twilio off trial, because trial accounts blocked live audio for a past team [F 02] | Scaffold React + deck.gl/Mapbox |
| H1–5 | Train the gas-use and leaky models. Export them behind FastAPI | ILP in PuLP/OR-Tools; unit tests on 5 sample buildings | Agent prompt, tools, consent ladder (email/text, then call) | House card: $/yr, kg/yr, points bar out of 70 |
| H5–9 | PRISM calibration with NASA POWER HDD | Bill-photo parser (vision LLM → JSON), tested on 3 bills | Relay tenant agent: text, photo and video, using the workshop cookbook [F 11] | 3D map; landlord one-pager (PDF) |
| **H6 (midnight) gate** | | **Address → plan → call works end to end** | | |
| H9–12 | Batch run over Ann Arbor footprints → GeoJSON; eval numbers | STREAM/A2Trak lookup (stretch) | Rehearse 15 landlord calls with objections; measure latency | City view, polish |
| H12–14 | Optional Sentinel-2 roof layer *only if ahead at 2 AM* | Edge cases | Next-bill verification flow | Freeze at H14 (8 AM) |
| H14–17.5 | Devpost numbers | Limitations section | Backup call recording | Real-life demo video, Devpost, README |

### Data & APIs verified
- **ResStock 2024.2 MI on OEDI S3** (public, no key) [V]. Numbers below are my calculations.
  - Upgrade 16 (light-touch envelope), gas-heated homes:
    - Median bill saving $36/yr.
    - For leaky homes (≥20 ACH50, **41%** of gas-heated homes by weight): median **$102/yr**, 75th percentile $210/yr, median gas cut **14.4%**.
    - That gas cut is about **846 kg CO2/yr**, using EPA's 53.06 kg CO2/MMBtu for natural gas ([EPA factors](https://www.epa.gov/system/files/documents/2025-01/ghg-emission-factors-hub-2025.pdf)) [S].
  - **Heat-pump packages 7 and 9 *raise* median bills for MI gas homes** by $342 and $253/yr. That is why Drafty leads with envelope measures, not heat pumps.
- **NASA POWER daily API** returns `HDD18_3` and `T2M` for Ann Arbor (source: MERRA-2) [V].
- **City sources** [V]: the GRH checklist PDF, the GRH FAQ, and the Concentrate count of over 500 compliant properties. Rental inspection records are public on A2Trak/STREAM ([city](https://www.a2gov.org/building-rental-and-inspection-services/rental-housing/property-registration-and-inspection-information/)) [S].
- **Rebate rules** [V]: DTE insulation rebates and Insulate Ann Arbor. MiHER amounts, and the Detroit pause since May 2026, are [S]. The federal 25C credit ended for property placed in service after Dec 31, 2025 ([IRS](https://www.irs.gov/newsroom/faqs-for-modification-of-sections-25c-25d-25e-30c-30d-45l-45w-and-179d-under-public-law-119-21-139-stat-72-july-4-2025-commonly-known-as-the-one-big-beautiful-bill-obbb)) [S], so Drafty never cites it.
- **Platform APIs.**
  - The ElevenLabs Twilio outbound-call endpoint is documented [S].
  - Relay supports calls, video, the user's camera, and group chats [F 11]. Its iOS 26-only status and the question of whether calls work in the current app build are open [F 11].
  - The Sentinel-2 STAC query worked [V].

### Risks
- **Per-home savings are modest.** $102/yr median for leaky homes is not Watt's Up's solar payback. *Mitigation:* lead with compliance, comfort and "someone else pays 50–90%". Show ranges, and never claim a heat pump saves money in Michigan.
- **Model-on-model numbers.** The AUC and R² come from simulated homes. Say so, and show the real-bill calibration as the honest test.
- **Point estimates are guesses until inspection.** The agent asks the tenant 5 photo questions (thermostat, windows, weatherstripping, lights, water heater) and labels unverified points.
- **Consent and tone.** The FCC ruling governs AI voice calls, so the design calls only after opt-in. The tenant approves every outreach. The agent is cordial and never threatens.
- **Platform risk.** Twilio trial limits (pay about $20), and Relay calls may need an app update [F 11]. Fallback: the ElevenLabs web widget on the "landlord's" laptop.
- **Judge question: "Why would a landlord listen?"** Answer: the ordinance plus fines for non-compliance ([GRH FAQ](https://www.a2gov.org/media/yykptaqy/grh-faq.pdf)) [V], plus the rebates.

---

## Idea 2 — Seatmate: carpools your agent negotiates for you

### One-liner
Seatmate lives in your texts. Tell it once where you live and when you need to be at work. Every evening it finds people from your neighbourhood heading to the same part of town and **negotiates tomorrow's pickups with their agents**. At 7:40 AM it handles "running 10 min late". It splits fuel and the U-M parking permit, and shows each rider the dollars and CO2 saved.

### Who and how many
- **Ann Arbor imports its workforce.** 96,175 primary jobs held by Michigan residents are located in Ann Arbor. **78,014 of them (81%) are held by people who live outside the city.** The median straight-line commute is **26.6 km** (LEHD LODES 2021; Michigan is missing from the 2022 release) [V: my calculation from [LODES8](https://lehd.ces.census.gov/data/lodes/LODES8/mi/od/) + crosswalk].
- **Nationally,** 69.2% of workers drove alone in 2023 (ACS) [S].
- **Transport is Ann Arbor's stuck problem.** It is 30% of the city's emissions and has "not budged". Walking and biking trips fell from 49.9% to 38.8% between 2019 and 2023 ([Ann Arbor Observer](https://annarborobserver.com/a2zero-six-years-in/)) [V].

### How often it's used
Twice a day, every workday. The agent works every evening, and again in the morning when plans change.

### Why it isn't niche
- **Everyone who commutes, every day.**
- **Money people feel.**
  - AAA's 2026 estimate is **$12,863/yr** to own a new car, with gas at $4.152/gal ([Repairer Driven News on AAA](https://www.repairerdrivennews.com/2026/09/15/aaa-it-costs-12863-annually-to-own-a-new-vehicle-ev-and-hybrid-fuel-savings-dont-offset-higher-costs/)) [V].
  - A U-M Blue permit is **$71.92/month** from July 2026 ([LTP](https://ltp.umich.edu/2026/04/29/new-campus-parking-permit-rates-effective-july-1-2026/)) [V].
- **Value in one sentence:** *"Carpools don't fail for lack of people. They fail on coordination, and Seatmate's agent does the coordinating."*

### Winning-formula match
- **Universal daily problem**, the same as SunLite's waking up and Terminal.AI's debugging.
- **Watch it happen.** The judges' phones join the network and get matched live.
- **A core we built, with a hard number from real data.** 72% of in-commuters share a home tract → work tract pair with at least 3 others, and 86% with at least 1 [V: my LODES calculation].
- **Local hook.** U-M already allows registered carpools of 4+ to share a permit and get a reserved space, but you apply through Parking Customer Services forms ([LTP carpools](https://ltp.umich.edu/transportation-alternatives/carpools/)) [V]. Seatmate removes that friction.
- **Closes the loop.** It negotiates, re-plans and splits the cost.
- **Money and carbon on one card, rider to city.** A "commute shed" map of the 37 work tracts shows how many cars a 10% match rate removes.

### Closest past winners, and how Seatmate differs
| Past project | What it did | Difference |
|---|---|---|
| [Concord](https://devpost.com/software/concord-ha3jnv) (MHacks 2025, AgentMail) | Each group trip gets an AI coordinator with an email address and shared memory [F] | Same "agent coordinates a group" shape. Seatmate does it **daily**, between strangers' agents, with an optimiser underneath |
| [Bazaar](https://devpost.com/software/bazaar-ai-agent-marketplace-fetch-ai) (MHacks 2025, Fetch.ai ASI:One) | Agents negotiate real tasks; payment is released after verification [F] | The same Fetch archetype (agents negotiating), applied to seats and pickup times |
| Waze Carpool | Shut down in 2022 because commutes became unpredictable ([TechCrunch](https://techcrunch.com/2022/08/26/googles-waze-shutting-down-its-carpool-service/)) [S] | Seatmate's whole thesis is unpredictability: the agent renegotiates every evening and morning, so nobody has to |
| ShellHacks 2026 (Waymo challenge) | Its prompt lists "an app to help students carpool to campus" as an example ([Devpost](https://shellhacks-2026.devpost.com/)) [V] | **Carpool apps are a stock idea.** Lead with the agent negotiation and the LODES number, not "carpool app" |

### Technical core we build
1. **Pool-potential analysis.** LODES 2021 origin-destination flows plus 2020 block centroids from the crosswalk give a city flow map. The "poolability" curve (share of commuters matchable at detours of 4, 8 and 12 min) uses OSRM travel times. The public demo server answered a Ypsilanti → Ann Arbor route (12.1 km, 15 min) [V].
2. **Matcher.** Every evening it solves a pickup-and-delivery routing problem with time windows: capacity 4, a maximum driver detour, and arrival deadlines. We use OR-Tools on an OSRM time matrix.
   - It re-solves in under 2 s for about 50 commuters on events like "late", "can't drive" or "leaving early".
   - It reports vehicle-km avoided against everyone driving alone. CO2 uses EPA's 8,887 g/gal ([EPA](https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle)) [S]; dollars use AAA fuel prices and the permit split.
3. **Negotiating agents.**
   - One Fetch.ai uAgent per commuter, speaking the Chat Protocol and holding preferences (earliest departure, maximum detour, quiet ride).
   - They negotiate propose/accept/counter, and a human approves with a tap.
   - Setup happens through ASI:One ("I live in Canton, need to be at Michigan Medicine by 7:30").
4. **Shared live state** in SpacetimeDB, with tables for commuters, offers, matches and trips. Every phone and the map subscribe to it.
5. **Simulator.** Synthetic commuters are sampled from real LODES flows to stress-test the matcher. It reports match rate against detour.

**Worked example** [I]: a 26.6 km straight-line commute is about 33 km by road (1.25 circuity, assumed), or about 41 mi/day round trip. At 25 mpg (assumed) that is about 1.64 gal/day, or about $6.81 at $4.152/gal. A 2-person pool saves each rider about **$3.40/day (≈$820/yr over 240 days)** and about **7.3 kg CO2/day (≈1.75 t/yr)**, before the permit split.

### Demo (3:00)
1. **0:00, hook.** "78,000 people commute into Ann Arbor jobs. Transportation emissions here haven't budged. 72% of those commuters have at least 3 others from the same neighbourhood going to the same part of town."
2. **0:20, the judge joins.** The judge scans a QR code, joins the Relay group "Ypsi → North Campus", and enters a nearby intersection and a 9:00 arrival.
3. **0:40, the match.** On the live map, the judge's dot joins about 30 synthetic commuters sampled from LODES, plus 2 teammates. The matcher re-solves, and the judge's phone buzzes: "Maya passes 0.6 mi from you at 8:21. Ride together? You'd each save $3.40 and 3.6 kg CO2 today."
4. **1:10, the curveball.** The teammate texts "running 10 min late." The agents renegotiate, and the judge gets either an 8:31 pickup or a TheRide bus plus a ride home.
5. **1:45, week card and city view.** The week card shows dollars, CO2 and the permit split. The commute-shed map shows "if 10% matched, N cars/day leave Ann Arbor's roads."
6. **2:20, engineering.** The solver, re-solve latency, the poolability curve, and what is synthetic.

### Sponsor tracks that fit naturally
- **Fetch.ai ASI:One.** Agents negotiating on people's behalf is Fetch's own "intent to action" brief.
  - Hard requirements: Agentverse registration, the Chat Protocol, README badges, and a 3–5 min video [F 01].
- **SpacetimeDB.** Real-time shared state for a multi-user product, which is its archetype [F 08].
- **Relay.** Group chats are supported [F 11].
- *Optional:* Capital One Nessie for per-ride cost splits.
- *Not natural:* SpaceX (no space data) and Photon (group chats need its $250 Business tier or a local Mac [F 06]).

**Fun track:** Judged by an LLM.

### 18-hour build plan
| Time | P1 Data | P2 Optimiser | P3 Agents | P4 Frontend |
|---|---|---|---|---|
| H0–1 (gates) | LODES + crosswalk already reproducible (scripted today) | OSRM table call for 50 points (self-host `osrm-backend` with a Michigan extract if rate-limited) | uAgent with the Chat Protocol answering in ASI:One; Relay group hello | `spacetime dev --template react-ts` [F 08] |
| H1–6 | Flow map, synthetic commuter sampler, poolability curve | OR-Tools pickup/delivery with time windows; re-solve API | Preference schema, propose/accept/counter, human approval | Map with live routes, join-by-QR |
| **H6 gate** | | **Judge joins → matched → text arrives** | | |
| H6–12 | City "commute shed" view; numbers | Event handling (late/cancel); bus fallback via TheRide GTFS (stretch) | Relay group bridge; nightly negotiation loop | Week card, cost split |
| H12–17.5 | Devpost numbers | Load test (200 commuters) | Fetch video, README badges | Real-life video, Devpost |

### Data & APIs verified
- LODES8 Michigan OD 2017–2021 is downloadable, and **2022 omits Michigan** ([Census note](https://www.census.gov/programs-surveys/ces/news-and-updates/updates/11192024.html)) [V].
- I computed 96,175 jobs / 78,014 in-commuters / 26.6 km median / 72% ≥4-person tract pairs [V].
- The OSRM demo route worked [V].
- U-M LTP carpool rules [V] and permit rates [V]; AAA 2026 [V]; Ann Arbor Observer transport figures [V].
- ACS 69.2% [S]; EPA 8,887 g/gal [S].

### Risks
- **Familiar category.** The ShellHacks prompt proves it. *Mitigation:* the pitch never says "carpool app" first. It says "your agent negotiates tomorrow's commute", and it carries the LODES number.
- **Cold start.** The demo seeds synthetic riders drawn from real flows; say so out loud.
- **LODES limits.** It counts jobs, not cars. 2021 is a pandemic year. It has no mode or schedule data, and out-of-state workers are excluded.
- **Trust and safety.** Restrict to verified `umich.edu` coworkers, show a profile and photo, and never share an exact home address until both riders accept.
- **Platform risk.** Relay is iOS 26 only [F 11]. Fetch's hard requirements cost about 6 hours [F 01].

---

## Idea 3 — Mend: repair-first, with the agent doing the phoning

### One-liner
Show Mend your broken thing, by photo or on a live video call. In seconds it puts repair against replacement in **dollars and kg CO2**. Then it does the part that makes people give up and buy new: it **calls local repair shops in parallel for quotes**, books the best one (or Ann Arbor's free Repair Café), orders the part with the iFixit guide, or drafts the warranty claim.

### Who and how many
- **Every household.** Repair could cut household spending on electronics and appliances by 21.6%, about **$382 per family per year** and $49.6B across 129M households ([US PIRG](https://pirg.org/edfund/resources/repair-saves-families-big/)) [S].
- **Global e-waste reached 62 Mt in 2022, and only 22.3% was documented as recycled** ([UNITAR, Global E-waste Monitor 2024](https://unitar.org/about/news-stories/press/global-e-waste-monitor-2024-electronic-waste-rising-five-times-faster-documented-e-waste-recycling)) [S].
- **Students in particular:** cracked phones, laptops, headphones, bikes.

### How often it's used
Whenever something breaks, which for most households means several items a year across phones, laptops, appliances, bikes and clothes. The agent then follows up on bookings, parts and claims.

### Why it isn't niche
- Everyone owns electronics.
- **Value in one sentence:** *"Repair loses because getting a quote means calling three shops; buying new is one tap. Mend makes repair one tap."*
- **Money and embodied carbon share one card.** Boavizta's API gives about **84 kg CO2e** embodied in a generic smartphone [V: API call].

### Winning-formula match
- **The judge's own input.** Most people carry a damaged phone or earbuds.
- **Watch it happen.** Two shop calls run in parallel, and the quotes stream onto the screen.
- **Money and carbon in one view.**
- **Decision, then action.** Repair, DIY, Repair Café or replace, followed by booking.
- **Local hook.** Ann Arbor's Repair Café at Arbor Good Neighbor House ([AGNH](https://agnh.org/repair-cafe/)) [S] and Maker Works' Fix-It Friday ([Maker Works](https://www.maker-works.com/fixitfriday)) [S].
- **City scale.** An Ann Arbor "repair economy" map of shops (OpenStreetMap), quotes and blockers (missing parts by brand). It works as evidence for right-to-repair policy [I].

### Closest past winners and prior art, and how Mend differs
| Project | What it did | Difference |
|---|---|---|
| [deCluttered.ai](https://devpost.com/software/declutttered-ai) (MHacks 2025, Fetch Agentverse) | Scans a room, lists items for resale, and agents negotiate with buyers [F] | Mend keeps the item *in use*: repair before resale |
| [BidBot](https://devpost.com/software/bidbot) (HackHayward 2026, AI track 1st) | ElevenLabs + Twilio agents call contractors at once and negotiate [V] | **The calling pattern already exists and has won.** Mend's new part is the repair-vs-replace decision with embodied carbon, and routing to DIY, Repair Café or warranty |
| iFixit FixBot (Dec 2025) | AI diagnosis and DIY guides from about 125k repair guides ([9to5Mac](https://9to5mac.com/2025/12/09/ifixit-launches-fixbot-ai-repair-helper-with-free-and-paid-versions/)) [S] | FixBot advises a DIYer; Mend *gets it fixed* for people who won't DIY |
| AIRecycler / Recyclify (MHacks 2025/2024, no prize) | Photo → "is this recyclable?" [F] | Same photo-in input, but the opposite end of life. Mend must never look like a recycling classifier |

### Technical core we build
1. **Damage triage model.** Fine-tune a small YOLOv8 or ViT classifier on Roboflow Universe cracked-screen and damage sets (about 300–400 images each, CC BY 4.0, per the listings) ([example](https://universe.roboflow.com/abhinavpoc/cracked-screen)) [S], plus about 100 photos the team takes at the event, FocusFlow-style. Report held-out accuracy.
2. **Repair-or-replace engine.**
   - Device ID (vision LLM) feeds an iFixit category lookup: guide, difficulty, parts. The iFixit API answered for "iPhone 13" [V].
   - Embodied CO2 comes from Boavizta [V]; refurbished prices come from a table for the top 20 devices [I].
   - Decision rule: cost per remaining year of life, repair against replace, plus a success probability.
3. **Quote agent.**
   - ElevenLabs agent calls go out in parallel (batch calling is documented ([docs](https://elevenlabs.io/docs/eleven-agents/phone-numbers/batch-calls)) [S]), with a `record_quote(price, eta)` tool.
   - Consent-first: in production, shops opt in or are reached by web form and email. In the demo, teammates play the shops.
   - It then books, and drafts the warranty or AppleCare claim text.
4. **Relay video intake.** The agent reads the camera frames [F 11] and asks you to tilt the phone.

### Demo (3:00)
1. **0:00.** "Repairing saves a family about $382 a year, yet we replace. Why? Getting a quote takes three phone calls."
2. **0:20.** The judge's own cracked phone, or our cracked laptop. Within 10 s the card reads: "Cracked display. Repair ≈ $X–Y, replace ≈ $Z. 84 kg CO2e embodied."
3. **0:50.** "Get quotes." Two teammates' phones ring at once, and the quotes stream in.
4. **1:40.** Mend books the best quote and shows the iFixit guide as the DIY alternative.
5. **2:10.** The city repair map and the model accuracy.
6. **2:40.** Close, including the limitation that refurbished prices are hand-curated.

### Sponsor tracks that fit naturally
- **ElevenLabs:** the parallel calls are the action.
- **Relay:** video intake of the broken item.
- *Optional:* Fetch.ai, with shop agents in a quote marketplace (the Bazaar/deCluttered archetype).
- *Not natural:* SpaceX (no space data).

**Fun track:** Judged by an LLM.

### 18-hour build plan
- **P1:** dataset download plus 100 own photos (H0–3), fine-tune and evaluate (H3–8), serve (H8–10).
- **P2:** iFixit, Boavizta and price table; decision engine with tests (H0–8); city repair map from an OpenStreetMap Overpass query (H8–12).
- **P3:** ElevenLabs agent plus 2 parallel outbound calls, as the **H1 gate**. Then the quote tool and booking (H1–8), Relay video intake (H8–12), and 15 rehearsal calls (H12–14).
- **P4:** UI split card and quote stream (H0–10), then Devpost and a real-life video (H12–17.5).
- **H6 gate:** photo → decision → two calls → booked.

### Data & APIs verified
- **APIs:** Boavizta `/v1/terminal/smartphone` returned 84 kg CO2e embedded [V]. The iFixit `/api/2.0/wikis/CATEGORY/iPhone 13` endpoint answered [V].
- **Prior art:** the BidBot page [V]; Roboflow datasets [S]; FixBot [S].
- **Statistics:** PIRG [S]; Global E-waste Monitor [S].

### Risks
- **Novelty is the weakest of the three.** BidBot has already won with parallel AI calls, and FixBot covers diagnosis. The carbon decision has to carry the Innovation score.
- **Thin core.** A fine-tuned damage classifier is a modest technical core.
- **Infrequent use.** It is used less often than Ideas 1 and 2.
- **Consent.** Calling real businesses with an AI voice brings in the FCC/TCPA consent rules; the demo calls only teammates.
- **Hand-curated prices.** Refurbished prices are curated by hand.

---

## Scorecard (inference, 1–10)
| | Drafty | Seatmate | Mend |
|---|---|---|---|
| Non-niche (breadth × frequency) | 8 | 9 | 7 |
| Watt's Up bar: instant / trained core / money+carbon / home→city / visual | 9 / 8 / 6 / 9 / 8 | 8 / 7 / 8 / 9 / 8 | 9 / 6 / 9 / 6 / 7 |
| Novelty against past winners | 8 | 5 | 5 |
| Agent action a judge watches | 9 (landlord call) | 8 (phones matched live) | 8 (parallel calls) |
| 18 h feasibility | 7 | 7 | 8 |
| Natural sponsor fit | 7 | 8 | 7 |
| Local hook | 10 | 8 | 6 |

**Recommendation: Drafty.** It is the only one of the three with (a) a brand-new law that every judge living in Ann Arbor has heard of or rents under, (b) a trained core on a real national dataset, already tested, and (c) an agent action that cannot be done by a dashboard. If the team wants a daily-use, multiplayer demo and is comfortable with the "carpool app" association, Seatmate is the backup.

## Considered and dropped
- **Heat-pump concierge for homeowners.** Ann Arbor already has one (Pearl Edison) [V]. ResStock also shows heat pumps raise median bills for Michigan gas homes [V].
- **Water-leak agent on smart meters.** Utility AMI portals already send continuous-flow leak alerts ([EPA AMI guide](https://www.epa.gov/system/files/documents/2022-09/ws-commercial-ami-guide-facility-managers.pdf)) [S].
- **Stormwater-fee credit filer.** Only property owners pay it, and it is a one-off filing.
- **Satellite methane/emissions "accountability" agent** (Climate TRACE/TROPOMI). There is no personal money in it and it reads as advocacy.
- **Used-EV negotiator.** Too infrequent, and AAA 2026 shows EVs costing more to own than gas cars because of depreciation.
- **Utility rate-plan switcher.** It collapses into the rejected Clean Hours (load shifting).

## Sources
**Team files:**
- `/Users/anvaytodkar/Code/mhacks/results/year-research/2020.md`–`2025.md`
- `/Users/anvaytodkar/Code/mhacks/results/SUMMARY.md`
- `/Users/anvaytodkar/Code/mhacks/results/pivot-ideas/01-past-winner-patterns.md`
- `/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/01-fetchai-asi-one-agent-challenge.md`, `02-elevenlabs.md`, `06-photon-imessage-agents.md`, `08-spacetimedb.md`, `11-relay-interactive-agents.md`, `13-debate-and-verdict.md`
- `/Users/anvaytodkar/Code/mhacks/results/pivot-round2/01-mhacks-winner-anatomy.md`, `02-peer-sustainability-winners.md`

**Past winners and prior art:**
- Watt's Up: https://devpost.com/software/watt-s-up
- ZoneZero: https://devpost.com/software/zonezero
- Chilladelphia: https://devpost.com/software/chilladelphia
- GreenPrint: https://devpost.com/software/greenprint-c2deb1
- Wattson: https://devpost.com/software/wattson-5btsyd
- Concord: https://devpost.com/software/concord-ha3jnv
- Bazaar: https://devpost.com/software/bazaar-ai-agent-marketplace-fetch-ai
- deCluttered.ai: https://devpost.com/software/declutttered-ai
- BidBot: https://devpost.com/software/bidbot
- RentRelay: https://github.com/arpeymorshed/DivHacks-2026-Track-2
- ShellHacks 2026: https://shellhacks-2026.devpost.com/
- iFixit FixBot: https://9to5mac.com/2025/12/09/ifixit-launches-fixbot-ai-repair-helper-with-free-and-paid-versions/
- Waze Carpool shutdown: https://techcrunch.com/2022/08/26/googles-waze-shutting-down-its-carpool-service/

**Ann Arbor and Michigan:**
- Green Rental Housing checklist: https://www.a2gov.org/media/dxxnmkyt/green-rental-housing-checklist.pdf
- GRH FAQ: https://www.a2gov.org/media/yykptaqy/grh-faq.pdf
- GRH effective Jan 6, 2026: https://www.a2gov.org/news/posts/city-of-ann-arbor-s-green-rental-housing-ordinance-goes-into-effect-jan-6-2026/
- 500+ compliant: https://concentratemedia.com/500-ann-arbor-rentals-now-in-compliance-with-new-green-housing-ordinance/
- Insulate Ann Arbor: https://www.wemu.org/wemu-news/2026-04-23/ann-arbor-dte-launch-energy-efficiency-rebate-program-for-multi-family-housing
- A2ZERO six years in: https://annarborobserver.com/a2zero-six-years-in/
- Heat Pump Concierge: https://www.a2gov.org/news/posts/a2zero-heat-pump-concierge-platform-offers-convenient-switch-to-clean-healthy-heating-and-cooling/
- Rental inspection records: https://www.a2gov.org/building-rental-and-inspection-services/rental-housing/property-registration-and-inspection-information/
- Census Reporter, Ann Arbor: http://censusreporter.org/profiles/16000US2603000-ann-arbor-mi/
- DTE insulation rebates: https://www.dteenergy.com/us/en/residential/save-money-energy/rebates-and-offers/insulation-and-windows.html
- MiHER FAQ: https://www.michigan.gov/egle/faqs/climate-and-energy/home-energy-rebates-program
- U-M LTP carpools: https://ltp.umich.edu/transportation-alternatives/carpools/
- U-M permit rates FY2027: https://ltp.umich.edu/2026/04/29/new-campus-parking-permit-rates-effective-july-1-2026/
- Repair Café (AGNH): https://agnh.org/repair-cafe/
- Maker Works Fix-It Friday: https://www.maker-works.com/fixitfriday

**Data and APIs** (each checked today):
- ResStock 2024.2 on OEDI: https://data.openei.org/s3_viewer?bucket=oedi-data-lake&prefix=nrel-pds-building-stock%2Fend-use-load-profiles-for-us-building-stock%2F2024%2Fresstock_tmy3_release_2%2F
  - MI baseline file: https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2024/resstock_tmy3_release_2/metadata_and_annual_results/by_state/state=MI/parquet/MI_baseline_metadata_and_annual_results.parquet
  - Upgrade list: https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2024/resstock_tmy3_release_2/upgrades_lookup.json
- NASA POWER API: https://power.larc.nasa.gov/docs/services/api/
- Earth Search STAC (Sentinel-2 L2A): https://earth-search.aws.element84.com/v1
- Microsoft US Building Footprints: https://github.com/microsoft/USBuildingFootprints
- LEHD LODES8 Michigan: https://lehd.ces.census.gov/data/lodes/LODES8/mi/od/
  - 2022 release note: https://www.census.gov/programs-surveys/ces/news-and-updates/updates/11192024.html
- OSRM demo server: https://router.project-osrm.org/
- Boavizta API: https://api.boavizta.org
- iFixit API: https://www.ifixit.com/api/2.0/
- ElevenLabs outbound call via Twilio: https://elevenlabs.io/docs/agents-platform/api-reference/twilio/outbound-call
- ElevenLabs batch calls: https://elevenlabs.io/docs/eleven-agents/phone-numbers/batch-calls
- Roboflow cracked-screen dataset: https://universe.roboflow.com/abhinavpoc/cracked-screen

**Statistics and policy:**
- Renters (Binghamton, *ERSS*): https://phys.org/news/2026-01-left-cold-renters-energy.html
- EIA RECS energy insecurity: https://www.eia.gov/todayinenergy/detail.php?id=51979
- IRS OBBB 25C FAQ: https://www.irs.gov/newsroom/faqs-for-modification-of-sections-25c-25d-25e-30c-30d-45l-45w-and-179d-under-public-law-119-21-139-stat-72-july-4-2025-commonly-known-as-the-one-big-beautiful-bill-obbb
- EPA emission factors hub 2025: https://www.epa.gov/system/files/documents/2025-01/ghg-emission-factors-hub-2025.pdf
- EPA typical passenger vehicle: https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle
- AAA 2026 driving costs: https://www.repairerdrivennews.com/2026/09/15/aaa-it-costs-12863-annually-to-own-a-new-vehicle-ev-and-hybrid-fuel-savings-dont-offset-higher-costs/
- US PIRG, *Repair Saves Families Big*: https://pirg.org/edfund/resources/repair-saves-families-big/
- Global E-waste Monitor 2024: https://unitar.org/about/news-stories/press/global-e-waste-monitor-2024-electronic-waste-rising-five-times-faster-documented-e-waste-recycling
- FCC AI-voice robocall ruling: https://docs.fcc.gov/public/attachments/DOC-400393A1.pdf
- EPA AMI guide: https://www.epa.gov/system/files/documents/2022-09/ws-commercial-ami-guide-facility-managers.pdf

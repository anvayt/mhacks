# Peer-Hackathon Sustainability Winners

## Prompt given (excerpt)
> Your job: what wins sustainability tracks at peer hackathons. Research sustainability/climate/environment track winners and grand-prize winners with a sustainability theme at major collegiate hackathons from 2024–2026 (TreeHacks, Cal Hacks, HackMIT, PennApps, HackGT, LA Hacks, HackPrinceton, Hack the North, MIT/Stanford climate hackathons, etc.) via Devpost galleries and write-ups. Dissect 12–20 winners: what they did, how broad the problem, the demo, the tech core, why they won. Then distil a winning formula for sustainability tracks, lessons, and a list of saturated/overdone sustainability hackathon ideas (e.g. carbon-footprint calculators, recycling-sorting cameras) that judges are tired of.
>
> Context from the user: the team rejected "Clean Hours" (dryer scheduling) and "Fern on Call" (heat/smoke check-ins for older people living alone) as too niche: "dude but again i feel like this is super fucdking niche? like?"

*Written Sat Oct 3, 2026, ~7 PM EDT. Tags: **[V]** I checked it myself today at the linked source (Devpost project pages were read directly; every "won X" below is the winner label on the project's own page unless marked otherwise). **[F]** From a team research file (named). **[I]** My inference or estimate.*

---

## TL;DR

1. **Your instinct is right, and peer winners back it up.** Of the 20 winners dissected below, 16 tackle a problem whose scale can be stated as a big number: every rooftop, every Philly block, the whole US grid, 60M tons of wasted produce, the world's oceans. Only 4 are narrow (LEED Bud, ERWIN, BAS, CarbonChain). All 4 won **sponsor-run prizes**, 3 of them TreeHacks Stanford Ecopreneurship prizes that score user pain, prototyping or venture viability; none won a general-judge award [V/I]. Clean Hours (one appliance) and Fern on Call (a rare event for a small group) would have been among the narrowest projects on this list.
2. **The real test is the denominator, not daily use.** Few winners are used every day. The common thread is **how many people have the problem × what's at stake**: your house burning, your bill, a blackout, a hurricane. Frequency helped the consumer winners (SnackSnap, Sustain-ify, Wattson), but scale and stakes carried the rest [I].
3. **Three shapes keep winning** (§2):
   - **A. Address/photo in → a personal decision out, from satellite or public data.** Chilladelphia, U-Plan, Watt's Up, ZoneZero, CarbonCompass and Solar Flair all won between 2024 and 2026. This is the broadest shape that also demos well: **the judge types in their own address**.
   - **B. A system-level resilience tool with a hard technical core.** Examples: GridVeda, SkySplat, OverSEA, Garuda, SaR 3D, Griddy.
   - **C. A charming everyday consumer loop.** Examples: SnackSnap, Sustain-ify, and MHacks' own Wattson. It is the broadest shape, but also the most crowded.
4. **The field is full of the same 8–10 ideas.** I scraped all **351 entrants** in 11 sustainability prize pools (TreeHacks '24–'26, PennApps XXV–XXVI, HackHarvard '24–'25, Cal Hacks 11, LA Hacks '25, HackPrinceton S'25, MHacks '25). They contain about 20 food-waste/pantry apps, about 20 gamified eco-habit apps, about 14 recycling classifiers or smart bins, about 10 footprint calculators, about 10 "green AI" prompt or compute trackers, about 9 eco-score shopping scanners and about 7 blockchain carbon-credit platforms. **Those categories won almost no dedicated sustainability-track prizes** (§3) [V counts from titles and taglines; tallies approximate].
5. **For MHacks specifically** (general volunteer judges; Innovation / Technical Complexity / Usability / Theme [F SUMMARY]): the closest peer analogs are general-judge overall prizes. Sustain-ify, SnackSnap, Garuda, OverSEA and Watt's Up all won overall prizes with a sustainability theme. That suggests **shape A or B with something the team built itself**, shown as a number on screen. HackHarvard's published rubric even asks: *"Is it a completely new idea, or does it seem familiar?"* ([HackHarvard 2025](https://hackharvard-2025.devpost.com/)) [V].

---

## Method

- **Galleries scraped [V]:** I listed each event's prize filters on Devpost, pulled every entrant in its sustainability or climate prizes, then opened each winner's project page to read which prize it actually won (a search-page badge only means "won something").
  - Events with a dedicated sustainability prize: TreeHacks 2024/2025/2026 (Stanford Ecopreneurship ×3; Cotopaxi; Sustainability Grand Prize), PennApps XXV/XXVI (Bloomberg), HackHarvard 2024 (Sustainability Track) and 2025 (Coolant Climate Tech), Cal Hacks 11.0 (SCET/PepsiCo), LA Hacks 2025 ("Clean Code"), HackPrinceton Spring 2025, and MHacks 2025 Greenprint.
  - HackMIT: from news coverage, because its gallery (Plume) is JavaScript-only.
  - No sustainability prize on Devpost: HackGT 11/12, Hack the North 2024/2025, HackDuke 2025/2026, Hacklytics 2025/2026, HackIllinois 2025, Hacktech 2025, LA Hacks 2024/2026, HackPrinceton Fall 2025 (its sustainability prize isn't filterable). I added **overall** winners with a sustainability theme where I found them.
- **Not found:** the name of HackMIT 2024's Sustainability Grand Prize winner. Palantir's CTO said it used Foundry and won 3 sponsor challenges ([X](https://x.com/ssankar/status/1836076339691999679)), but no source I could reach names it. It is excluded.
- **Caveat:** many teams tick every prize box. TreeHacks 2024's sustainability pool held 100 opt-ins, mostly off-topic, so "pool size" overstates on-theme competition.

---

## 1. Twenty winners, dissected

**Breadth key.** **B1** = everyone or every household has the problem. **B2** = the problem is broad (the grid, disasters, oceans) but the user is a professional. **B3** = a narrow user group.

| # | Event · prize | Project | What it does | Breadth / how often | Demo | Tech core | Why it won (evidence + [I]) |
|---|---|---|---|---|---|---|---|
| 1 | TreeHacks 2024 · **Sustainability Grand Prize** | [SkySplat](https://devpost.com/software/skysplat) | Drone video in, an automated 3D Gaussian-splat model of any building out, for disaster recovery and inspection | B2 · event-driven | A 3D splat of the team itself, captured by their own pipeline, spun around in the browser | Parrot/Olympe drone SDK → COLMAP structure-from-motion → Gaussian-splatting training on cloud GPUs → three.js/gsplat viewer | A research-grade technique built end to end in 36 h. The pitch opened on a hard number (the 2010 Haiti quake, about 220k deaths, blamed on poor construction). Visual wow [V/I] |
| 2 | TreeHacks 2024 · Ecopreneurship: Best Solves User's Pain Point ($1k) | [LEED Bud](https://devpost.com/software/leed-bud) | Enter building specs, get an estimated LEED tier and what it takes to reach the next one | B3 · occasional | Building specs in, tier out | Next.js + an OpenAI model given past building specs as context; StackAI | **A real user on the team** (a community manager at a real-estate developer). The prize is judged on how well it solves a user's pain point. Thin tech; it won on validation [V/I] |
| 3 | TreeHacks 2024 · Ecopreneurship Best Prototyping **+ Cotopaxi Most Innovative Sustainability + Convex** (3 prizes) | [Spark](https://devpost.com/software/spark-mhxso9) | Environmental nonprofits post campaigns, and people who want to help find and join them, earning "spark points" | B1-ish · occasional | Browse campaigns, join, see points | Next.js + Convex (deep feature use), Figma | Interviewed a nonprofit executive director and **documented each iteration**, which is exactly what the prototyping prize asks for. Heavy Convex use took the sponsor prize too [V/I] |
| 4 | TreeHacks 2024 · Cotopaxi Most Innovative Sustainability Hack | [Carbon Cut](https://devpost.com/software/carbon-cut-3d5k2g) | Footprint calculator + clothing-tag/barcode carbon grader + sustainable restaurants + green routes + chat with "the Amazon rainforest" | B1 · weekly | Dashboard, tag photo → grade | FastAPI, OpenAI + Chroma RAG, Google Maps | **The exception to "footprint calculators lose."** It won a consumer outdoor brand's prize by planning brand-credit rewards (Cotopaxi, Patagonia) and talking to users. Note this was 2024 [V/I] |
| 5 | TreeHacks 2025 · Sustainability: Best Solves User's Pain Point ($800) | [ERWIN](https://devpost.com/software/erwin-enhanced-rock-weathering-impact-navigator) | Pick a region and a rock type, get a forecast of CO₂ removal from enhanced rock weathering, plus nearby quarries | B3 · professional | Draw a region → CO₂/pH curves over years; Basic/Advanced modes | Wraps **CrunchFlow** (a Fortran geochemistry model) with SoilGrids + Open-Meteo + Mapbox; quarry data scraped from the National Mine Map Repository | Answered a **provided challenge**, and the team interviewed a Stanford Earth Systems professor. It turned a PhD-only model into one click [V] |
| 6 | TreeHacks 2025 · Sustainability Best Prototyping ($800) **+ InterSystems GenAI** | [BAS Climate Action Matcher](https://devpost.com/software/bas-climate-action-matcher) | An agent matches a company to UN climate initiatives and peer companies' climate actions | B3 · professional | Company in → cited report out | DAIN agent; RAG over **172 UN initiatives + 17,000 report paragraphs**; NVIDIA embeddings; Gemini scoring | Partnered with Race to Zero, built a real corpus whose size it states, and the agent cites its sources. Sponsor database used for real [V] |
| 7 | TreeHacks 2025 · Sustainability Best Broader Context ($800) | [Lemon](https://devpost.com/software/lemon-7gn5hq) | A marketplace for farmers' surplus "ugly" produce, with consumer and business accounts | B1 · weekly | Shop discounted local produce | Flutter + Supabase (light) | Scored on "broader context" (regulation, buyer vs. user, word of mouth). It cited the US goal to halve food waste by 2030 and laid out incentives for three sides. **Farm-side supply**, not yet another pantry app [V/I] |
| 8 | TreeHacks 2026 · Ecopreneurship Best Prototyping ($1.5k) | [GridVeda](https://devpost.com/software/gridveda) | Edge-AI early warning for 20 substation transformers: degradation, fault type, time to failure | B2 (everyone depends on the grid) · continuous | Live dashboard streaming 180 data points every 2 s; 3D transformer heat maps; "why is T047 flagged?" | Physics features → gradient-boosting ensemble; 6-qubit variational quantum classifier; reports **98.09% gas-analysis fault accuracy**; Nemotron explanations; runs on a Jetson | Statistic-led problem (aging grid, rising outage risk), a measured number, edge hardware, and a striking 3D view [V] |
| 9 | TreeHacks 2026 · Ecopreneurship Best Broader Context ($1.5k) | [Morro](https://devpost.com/software/morro) | A "geoengineering OS": simulate cloud-seeding interventions against droughts and cyclones and pick the most effective | B2 · event-driven | Control vs. seeded cyclone vortex; four seeding methods compared | Perturbs initial states of **GraphCast and NVIDIA Earth2Studio** with physics-based masks on ERA5; random-forest severity classifiers | Ran real foundation weather models. Framed itself around governance and controversy, which is what the "broader context" prize scores [V] |
| 10 | TreeHacks 2026 · Stanford Ecopreneurship prize (per the [Stanford Daily](https://stanforddaily.com/2026/02/15/12th-annual-treehacks/); no winner label on Devpost) | [ZoneZero](https://devpost.com/software/zonezero) | Enter an address, get a check of the first 5 ft around the house ("Zone 0") against wildfire rules, plus a *good-looking* fix | B1 for wildfire-belt homeowners · one-time decision | Address → Street View/aerial → flagged mulch and fencing → before/after designs | Gemini vision on Street View; "style twin" adoption prediction; insurer dashboard | **An expert insight:** a CalFIRE chief told them looks, not cost, is the #1 barrier. Address-in demo, regulation tie-in (LE-100), and a payer (insurers). Note: 6 wildfire entries were in that pool, and this one won on the insight [V] |
| 11 | PennApps XXV · Best Sustainability Hack (Bloomberg) | [Chilladelphia](https://devpost.com/software/chilladelphia) | Enter a Philly address, get a "chill rating" from tree cover in aerial imagery, plus cooling centers and fixes | B1 (every resident) · every summer | Type your address → rating + map | DetecTrees model on scraped aerial imagery; MERN stack | **Local hook (the host city)**, address-in demo, a computer-vision core on real imagery, and an actionable output [V] |
| 12 | PennApps XXVI · Sustainability (Bloomberg) | [CarbonChain](https://devpost.com/software/carbonchain-m2hxz4) | A carbon-credit marketplace with "Proof-of-Impact" NFTs and milestone-gated smart contracts | B3 · professional | Search a project → buy credits → NFT certificate | React + smart contracts | Crisp problem (greenwashing, double counting), and it answered "why blockchain, not a database" up front. The pool was small (23 opt-ins, many off-topic) [V/I] |
| 13 | PennApps XXVI · **3rd Place Overall** | [OverSEA](https://devpost.com/software/oversear) | Flags untracked "dark" fishing vessels by matching satellite radar against AIS broadcasts, then predicts hotspots | B2 (global oceans) · continuous | A 3D globe of tens of thousands of detections; agent drafts a legal/impact report | Sentinel-1 SAR via Global Fishing Watch + AIS; SciPy density clustering; Gemini + Exa agent; Auth0 clearance levels | **Real satellite data at scale** on a striking globe, built on a Nature 2024 paper [V] |
| 14 | HackHarvard 2024 · **1st Best Overall** | [Sustain-ify](https://devpost.com/software/sustain-ify) | An everyday app: eco-shopping assistant, DIY sustainability projects, health reports ("good for Earth and for you") | B1 · daily-ish | Ask → agentic answers | CrewAI agents, ScrapeGraph, Neo4j knowledge graph, vector search, Groq/Gemini/GPT-4o, Flutter | **Self-interest framing** (your health) on a planet problem, with a lot of agent plumbing. General judges. Proof that a broad consumer app *can* take an overall prize [V/I] |
| 15 | HackHarvard 2024 · Sustainability Track | [U-Plan](https://devpost.com/software/u-plan) | Enter a zip code, get urban-heat-island maps (surface temperature, vegetation and water indices) plus design fixes, for planners | B2 · per project | Zip → heat map → chatbot recommendations | Satellite imagery + **SAM semantic segmentation**; Folium/Mapbox; Cloudflare Workers | Satellite + segmentation core, personal hook (Arizona heat) [V] |
| 16 | HackHarvard 2024 · **2nd Place Overall** | [Garuda](https://devpost.com/software/garuda-pb7qtf) | After a hurricane, drone footage gives damage maps, rescue needs, equipment dispatch and drowning alerts | B2 · event-driven | Drone video → annotated report + live heat map | MSNet damage model + LLaVA vision-language model; Flask; Google Maps | A teammate had lived through a Houston hurricane; a computer-vision pipeline; decisions as output, not just charts [V] |
| 17 | Cal Hacks 11.0 · **3rd Overall** | [SnackSnap](https://devpost.com/software/snacksnap-lw4b9q) | Snap yourself recycling; Gemini checks the photo is real; feed your pet "Baby Chester" | B1 · daily | Photo → verified → pet grows | SwiftUI + Firebase + Gemini (light) | **A relatable insight** (the paper-cup moment between trash and recycling), a cute finished character, and a 10-second loop. General judges at a 352-project event [V; size F] |
| 18 | HackPrinceton Spring 2025 · Best Hack in Sustainability **+ MLH Cloudflare** | [SaR 3D](https://devpost.com/software/sar-3d) | 3D maps for search-and-rescue drones from plain camera video (no LiDAR), plus AI scene understanding | B2 · event-driven | Video → stitched 3D mesh; live agent-view inference | Custom COLMAP + Open3D pipeline, ICP stitching, ball-pivoting mesh; LLaVA on Workers AI | Its own reconstruction pipeline, and the cost framing that drones need no LiDAR [V] |
| 19 | HackMIT 2025 · Sustainability track 1st | Griddy ([Khoury News](https://www.khoury.northeastern.edu/khoury-undergrads-win-three-categories-at-prestigious-mit-hackathon)) | A micro-grid model powered by **homemade iron-air batteries** | B2 (the grid) · continuous | A physical micro-scale grid in wood and metal frames | Batteries made from fertilizer-derived chemicals, built in MIT makerspaces | **They built real hardware chemistry in 24 h.** The most "we built this" project on the list [V] |
| 20 | HackPrinceton Fall 2025 · **Best Overall Hack** (one of 3; a search snippet says 2nd, unverified) | [Watt's Up](https://devpost.com/software/watt-s-up) | Enter an address and outline the roof, get a solar score, kWh, cost, payback, CO₂, a "Savings Mirror" from your bill, and an equity score | B1 (every rooftop) · one-time decision | Address → report in seconds | SegFormer-B0 roof segmentation on satellite imagery + **NASA POWER** irradiance; Census equity index; Dedalus agents | Money **and** carbon numbers for anyone's house, plus an equity layer for cities [V] |

**Also noted [V]:**
- Solar Flair, another rooftop-solar estimator, won LA Hacks 2025's DAIN agent challenge ([Devpost](https://devpost.com/software/solar-flair-rkxz0f)).
- Magic Mirror won LA Hacks 2025's "Clean Code" sustainability track with virtual try-on (FastSAM/YOLO + FitDiT + a LiveKit voice agent), pitched as cutting clothing returns ([Devpost](https://devpost.com/software/magic-mirror-muya4w)).
- CarbonCompass won HackHarvard 2025's Coolant Climate Tech challenge (8 opt-ins): describe a business, get the greenest neighborhoods on a 3D map ([Devpost](https://devpost.com/software/carboncompass-hyqob0)).
- Project Lend won TreeHacks 2026's Anthropic Human Flourishing track. It is an autonomous food-rescue operation (robot arm + Claude agents) that **delivered food to real Palo Alto shelters during the weekend** ([Devpost](https://devpost.com/software/project-lend)).
- CarbonInsight won TreeHacks 2024 "broader stakeholders" with forward price curves for carbon offsets ([Devpost](https://devpost.com/software/carbon-price-curves)).

**MHacks' own sustainability winners for comparison [F]:**
- Wattson, 2025 Greenprint + FREE-WiLi: a pet that dies if the lights stay on.
- FarmX, 2024: a fertilizer model for Michigan farms.
- SolarVista, 2024 MLH MATLAB: satellite-based solar siting.
- The 2024 MLH Streamlit winner: data-center load shifting to clean hours.
- Carbon Footprint Extension: MHacks 15 2nd place, 2023, online.

---

## 2. The three shapes that win (and how broad each is)

### A. "Your address/photo in → your personal decision out" (from orbit or public data)
- **Winners:** Chilladelphia, U-Plan, Watt's Up, ZoneZero, CarbonCompass, Solar Flair (plus MHacks' SolarVista) [V/F].
- **Why it's broad:** everyone has an address, a roof, a block or a bill. The problem is local but universal.
- **Why it demos well:** **the judge types in their own address** and gets a number about *their* home in seconds. That is participatory (MHacks pattern P6 [F 01-past-winner-patterns]) and holds up over repeated 3-minute pitches.
- **Why it's a fair SpaceX fit:** the input really is satellite data (NASA POWER, Sentinel, aerial imagery), which is what the "real space data goes in" track asks for [F sponsor 07] [I].
- **Risk: rooftop solar is now done.** Three winners in two years (SolarVista at **MHacks** 2024, Solar Flair, Watt's Up), plus tree-canopy/heat twice (Chilladelphia, U-Plan). The shape works; those two *questions* are used up [I].

### B. A system-level resilience tool with a hard technical core
- **Winners:** SkySplat, GridVeda, OverSEA, Garuda, SaR 3D, Griddy, Morro.
- **Why it's broad:** everyone depends on the grid, the oceans and disaster response. The *user* is a professional, but the *problem* fits in one sentence.
- **Why it wins:** each team can name a component it built (a splat pipeline, an ensemble with a measured accuracy, satellite-to-AIS fusion, batteries) and shows a 3D or map visual. It hits MHacks' "own technical core" pattern [F SUMMARY pattern 5].
- **Risk for this team:** it needs a strong ML, computer-vision or hardware builder, and a judge has to imagine the professional user [I].

### C. A charming everyday consumer loop
- **Winners:** SnackSnap (Cal Hacks 3rd overall), Sustain-ify (HackHarvard 1st overall), Wattson (MHacks Greenprint).
- **Why it's broad:** everyone, every day.
- **Why it wins:** one relatable moment, a character, and a finished product.
- **Risk:** **this is the most crowded lane** (§3). The winners each had something extra: a photo check that the action really happened (SnackSnap), hardware (Wattson), or a big multi-agent stack plus health self-interest (Sustain-ify). Plain versions of the same apps lost all over the pools [V/I].

**What the narrow winners teach:** LEED Bud, ERWIN, BAS and CarbonChain won **sponsor-run** prizes, three of them TreeHacks' expert-judged Stanford Ecopreneurship prizes. TreeHacks' Ecopreneurship pain-point prize literally asks *the users themselves* to rate the solutions ([TreeHacks 2025](https://treehacks-2025.devpost.com/)) [V]. MHacks' Sustainability track is judged by general MHacks judges on the four standard criteria [F SUMMARY]. So narrow-but-validated is the wrong bet for MHacks, and broad-and-novel is the right one [I].

---

## 3. What the field actually looks like (saturation data)

All 351 entrants in the 11 pools, grouped by title and tagline. Counts are my hand tallies and approximate. "Track wins" means the project won the *sustainability* prize it entered [V/I].

| Category | ≈ Entrants | Examples (event) | Sustainability-track wins |
|---|---|---|---|
| Household food waste: pantry, fridge scan, leftover recipes, dining-hall waste cameras | ~24 | Crumb&GetIt, Snap Chef, Nema, Leftys, WasteFree, Beat the Receipt, Grocify, HodgePodge, NoWaste.ai, Pare, Savor, RePlate, WasteRA | **0.** Lemon won by going farm-side instead |
| Gamified eco-habits: points, streaks, leaderboards, pets, quizzes and games | ~21 | Sustainify, EcoQuest, GreenPulse, EcoStore, Trashure Hunt, EcoKitty, EcoRush, Sustaino, EcoAlchemy, Compost Chaos, GHGuessr, CARBONLE, Mailopolis, SnackSnap, Wattson | 1 (Wattson, with hardware). SnackSnap won *overall* |
| Wildfire / disaster dashboards and assistants | ~22 (9 in TreeHacks 2026 alone, 6 of them wildfire) | Redhue, Flashpoint, EmberWatch, ContainOS, Resonant CWPP, Pyro*AI, CHRONOS, SnapSpark, Just Hurry!, Firefly | 3 (SkySplat, SaR 3D, ZoneZero), each on a distinct technique or insight |
| "Is this recyclable?" classifiers / smart bins | ~14 | AIRecycler (MHacks '25), Recycletron, ecoscan-AR, RecycleMagic, SmartBin, Releaf, Pepsicycle, TreeTrash | **0** (TrashToTreasure won PepsiCo's brand-specific upcycling prize) |
| Personal carbon-footprint calculators (incl. for websites, code, trips, meals) | ~10 | EcoAgent (MHacks '25), Carbon Cut, FoodPrint, trace, RepoReLeaf, EcoMeter, FourSeasons, Clouds2Campus, ReduceNow | 1 (Carbon Cut, 2024, an outdoor-brand sponsor prize) |
| "Green AI": prompt shorteners, compute/token carbon | ~10 | Sustain-A-Prompt, Type-less, CarbonSight, DataBot, TinderDB, CarbonShift, EcoCompute, Ventura | **0** (several won unrelated MLH or sponsor prizes) |
| Eco-score product scanners / sustainable shopping | ~9 | EcoScout (MHacks '25), terra, EcoNomNom, Lucidity, alt+cart, Shameify | **0** (EcoScout won Base44; Sustain-ify won overall as a broader app) |
| Blockchain carbon credits / offsets / NFTs | ~7 | EcoChain, EcoCoin, TradeREC, ecoxchange, Carbon ∅, CarbonChain | 1 (CarbonChain, in a 23-entry pool) |
| Address/imagery geospatial (heat, solar, siting, wildfire zone) | ~9 | Chilladelphia, U-Plan, ZoneZero, CarbonCompass, ShadeNav, TerraFind, RIFFAI Atlas, Solar Flair | **4 track wins + 1 sponsor win.** The best hit rate of any category |
| Grid / energy infrastructure | ~6 | GridVeda, PriorityQueue, Rizz The Grid, EnergyX, flipIt | 1 (GridVeda); PriorityQueue won Elastic |
| Climate volunteer / job / initiative matching | ~5 | Spark, ECO-MATCH, C3, Vuzz, BAS | 2 (Spark, BAS), both expert-judged |

**Takeaway [I]:** the consumer-behavior categories (food, habits, recycling, footprint, shopping, green AI) make up about **80 unique entrants, roughly a quarter of all 351 and well over half of the clearly on-theme ones**. Between them they won about 2 dedicated sustainability prizes (Wattson, Carbon Cut). The geospatial and resilience categories are smaller and win far more often.

---

## 4. The winning formula for a sustainability track

1. **A huge denominator in the first sentence, a specific person in the demo.** Open with a number for the scale: every rooftop, 46% of distribution infrastructure past its useful life (GridVeda's pitch), 60M tons of wasted produce (Lemon). Then demo on one named address, transformer or neighborhood.
2. **Let the judge bring their own input.** Their address, their photo, their roof, their bill. Give back a personal number in under 10 seconds: a chill rating, kWh and payback, Zone 0 compliance. This is the most reliable pattern among broad winners.
3. **Ground it in real external data, ideally from orbit.** 10 of the 20 winners used satellite, aerial or drone imagery, or climate and earth-model data (SAR, NASA POWER, ERA5/GraphCast, SoilGrids, Street View).
4. **Own one hard technical core and show its number.** Examples: SkySplat's splat pipeline, ERWIN's wrapped geochemistry model, GridVeda's 98% classifier, SaR 3D's reconstruction, Griddy's batteries, Watt's Up's roof segmentation. Plain LLM wrappers won sponsor prizes, almost never the track.
5. **Output a decision, not just a dashboard.** Which fix (ZoneZero), which intervention (Morro), which transformer to test now (GridVeda), which crew to send (Garuda), which neighborhood (CarbonCompass).
6. **Bring one real outside voice.** A CalFIRE chief (ZoneZero), a Stanford professor (ERWIN), a nonprofit director (Spark), a teammate who is the user (LEED Bud). Put one line of it in the pitch.
7. **Make it visible.** A 3D globe (OverSEA), splats (SkySplat), 3D transformer heat maps (GridVeda), a city heat map (Chilladelphia). Sustainability judges sit through a lot of plain dashboards [I].
8. **Show the broader context in one slide:** the rule it complies with (LE-100, IEEE C57.104, the 2030 food-waste goal), who pays (insurers), and who gets left out (Watt's Up's equity score).
9. **If you go consumer, add proof and charm.** Verify the behavior really happened (SnackSnap's photo check), use a sensor (Wattson), and make the character lovable. Otherwise you're one of about 20 habit apps.

---

## 5. Sustainability-specific lessons

- **Adaptation beats mitigation for breadth.** 8 of the 20 winners are about surviving climate impacts (heat, wildfire, hurricanes, grid failure, disaster mapping), not cutting emissions. Self-interest ("your house," "your block," "the lights staying on") makes a problem feel universal without guilt [V/I].
- **Make sustainability a side effect of something people already want.** Money (Watt's Up), health (Sustain-ify), clothes that fit (Magic Mirror), a home that looks good *and* won't burn (ZoneZero). Guilt-driven trackers lose [I].
- **Know who is judging.**
  - Sponsor/expert prizes (TreeHacks Ecopreneurship, Bloomberg, Coolant, PepsiCo) reward validated pain, prototyping iterations and venture viability ([TreeHacks 2025 criteria](https://treehacks-2025.devpost.com/)) [V].
  - General-judge prizes reward novelty, technical depth and wow ([HackHarvard criteria](https://hackharvard-2025.devpost.com/); [TreeHacks criteria](https://treehacks-2025.devpost.com/)) [V].
  - MHacks Sustainability is the general kind [F].
- **Sustainability pools are small but noisy.** MHacks 2025 Greenprint had 15 entries, at least 3 of them off-topic [F 01-main-sustainability]. PennApps XXVI had 23, many off-topic [V]. A serious on-theme project with a real technical core can stand out, which is how Wattson and FarmX won [F].
- **Recency kills novelty.** The pet-you-keep-alive idea won MHacks itself in 2025 (Wattson), and rooftop solar won MHacks in 2024 (SolarVista). Some judges may return, so assume they remember [I].
- **One real-world outcome during the weekend is powerful.** Project Lend delivered food to real shelters during TreeHacks, and Griddy built working batteries. "It already happened" beats "it could" [V/I].
- **A crowded theme can still be won with a sharp insight.** Wildfire had 6 entries in TreeHacks 2026's sustainability pool (9 counting other disasters). ZoneZero won because of one non-obvious finding: homeowners skip fire-safe landscaping because of how it looks, not what it costs [V].

---

## 6. Saturated sustainability ideas to avoid (judges have seen these many times)

1. **"Is this recyclable?" camera / smart bin / recycling sorter.** About 14 entrants across the pools; no track wins. One was in MHacks' own 2025 Greenprint pool (AIRecycler).
2. **Personal carbon-footprint calculator or tracker,** including browser extensions, website/code footprint and meal footprint. About 10 entrants. MHacks 15 already gave 2nd place to a footprint extension (2023).
3. **Gamified eco-habit app** (points, streaks, leaderboards, badges, "Strava for sustainability"). About 21 entrants.
4. **A virtual pet that thrives when you're green.** Wattson won MHacks 2025 and SnackSnap won Cal Hacks 11. It's been done, at MHacks itself.
5. **Eco-score barcode or product scanner / sustainable-shopping extension.** About 9 entrants; EcoScout did it at MHacks 2025.
6. **Pantry/fridge scanner and leftover-recipe app for household food waste.** About 24 entrants, the single most common idea.
7. **Dining-hall food-waste camera / demand predictor** (Pare, Savor, WasteRA, and more).
8. **"Green AI" prompt shortener or token-carbon meter.** About 10 entrants.
9. **Blockchain carbon-credit marketplace / NFT certificates.** About 7 entrants.
10. **Rooftop solar estimator from an address.** Three winners already, including MHacks 2024's SolarVista.
11. **Urban-heat / tree-canopy map for a city.** Already won at PennApps XXV and HackHarvard 2024.
12. **Generic wildfire dashboard or incident-command assistant.** 6 wildfire entries in TreeHacks 2026's sustainability pool alone.
13. **Carbon-aware load shifting / clean-hours scheduling.** Won MHacks 2024 (MLH Streamlit) and reappeared at TreeHacks 2026 (CarbonShift). This is the team's rejected Clean Hours.
14. **Climate-volunteer / climate-job / initiative matching platform** (Spark, ECO-MATCH, C3, Vuzz).
15. **Eco-education quiz or game** (GHGuessr, CARBONLE, EcoAlchemy, Compost Chaos, TreeCycle, EcoKitty, Mailopolis).

---

## 7. What this means for MHacks 2026 (brief, for the idea round)

- **A breadth test that matches peer winners:** can you finish the sentence "X million people / every Y has this problem, and it costs them Z" with a real number, and can a judge try it on *their own* home, photo or bill at the table? Clean Hours fails the first half and Fern on Call fails both [I].
- **Best fit for this team (strong web/mobile/AI APIs, little hardware): shape A.** Address, photo or bill in → a personal decision and a hard number out, from satellite or public data, with one model or algorithm the team built itself and shows a number for. It stays broad and makes SpaceX genuine. **Pick a question that hasn't been asked:** not rooftop solar, tree canopy, or wildfire zones [I].
- **Shape B** suits the team only if someone can own a computer-vision or ML core for about 14 hours.
- **Shape C** only with a non-obvious behavior *and* verification (a sensor or photo check); the FREE-WILi could be that sensor, but the Wattson precedent makes the pet framing risky [I].
- **Keep sponsors natural.** In this shape, SpaceX (satellite input) and ElevenLabs/Grok voice (if the judge talks to it) fit naturally. Don't force Nessie or FinchNode [I].

---

## Sources

**Project pages (Devpost, read directly) [V]**
- SkySplat: https://devpost.com/software/skysplat
- LEED Bud: https://devpost.com/software/leed-bud
- Spark: https://devpost.com/software/spark-mhxso9
- Carbon Cut: https://devpost.com/software/carbon-cut-3d5k2g
- CarbonInsight: https://devpost.com/software/carbon-price-curves
- ERWIN: https://devpost.com/software/erwin-enhanced-rock-weathering-impact-navigator
- BAS Climate Action Matcher: https://devpost.com/software/bas-climate-action-matcher
- Lemon: https://devpost.com/software/lemon-7gn5hq
- GridVeda: https://devpost.com/software/gridveda
- Morro: https://devpost.com/software/morro
- ZoneZero: https://devpost.com/software/zonezero
- Project Lend: https://devpost.com/software/project-lend
- Chilladelphia: https://devpost.com/software/chilladelphia
- CarbonChain: https://devpost.com/software/carbonchain-m2hxz4
- OverSEA: https://devpost.com/software/oversear
- Sustain-ify: https://devpost.com/software/sustain-ify
- U-Plan: https://devpost.com/software/u-plan
- Garuda: https://devpost.com/software/garuda-pb7qtf
- CarbonCompass: https://devpost.com/software/carboncompass-hyqob0
- SnackSnap: https://devpost.com/software/snacksnap-lw4b9q
- TrashToTreasure: https://devpost.com/software/trashtotreasure-sustainable-showcase
- SaR 3D: https://devpost.com/software/sar-3d
- Magic Mirror: https://devpost.com/software/magic-mirror-muya4w
- Solar Flair: https://devpost.com/software/solar-flair-rkxz0f
- Watt's Up: https://devpost.com/software/watt-s-up
- Wattson: https://devpost.com/software/wattson-5btsyd
- FarmX: https://devpost.com/software/farmx-zpw0yq

**Event pages, prize criteria and galleries [V]**
- TreeHacks 2024: https://treehacks-2024.devpost.com/
- TreeHacks 2025: https://treehacks-2025.devpost.com/ (Ecopreneurship criteria; judging criteria)
- TreeHacks 2026: https://treehacks-2026.devpost.com/
- PennApps XXV: https://pennapps-xxv.devpost.com/
- PennApps XXVI: https://pennapps-xxvi.devpost.com/
- HackHarvard 2024: https://hackharvard-2024.devpost.com/
- HackHarvard 2025: https://hackharvard-2025.devpost.com/ (judging criteria)
- Cal Hacks 11.0: https://cal-hacks-11-0.devpost.com/
- LA Hacks 2025: https://la-hacks-2025.devpost.com/ ("Clean Code" track text)
- HackPrinceton Spring 2025: https://hackprinceton-spring-2025.devpost.com/
- HackPrinceton Fall 2025: https://hackprinceton-fall-2025.devpost.com/ (Best Overall ×3; Best Sustainability Hack)
- MHacks 2025 Greenprint pool: https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90481
- Entrant lists: each event's `/submissions/search?prize_filter[prizes][]=<id>`. Prize IDs: TreeHacks 2024 73403/73628/73629/73630/73716; 2025 83865–83867; 2026 96820–96822; PennApps XXV 79013, XXVI 90475; HackHarvard 2024 80033, 2025 91183; Cal Hacks 11 80290; LA Hacks 2025 84645; HackPrinceton S25 85365.
- Events checked with no sustainability prize on Devpost: HackGT 11 (https://hackgt-11-circus-of-invention.devpost.com/), HackGT 12, Hack the North 2024/2025 (https://hackthenorth2025.devpost.com/), HackDuke 2025/2026, Hacklytics 2025/2026, HackIllinois 2025, Hacktech 2025, LA Hacks 2024/2026.

**News and write-ups [V]**
- Stanford Daily, TreeHacks 2026 winners (ZoneZero, Ecopreneurship): https://stanforddaily.com/2026/02/15/12th-annual-treehacks/
- Stanford Daily, TreeHacks 2025 winners: https://stanforddaily.com/2025/02/18/treehacks-awards-200000-in-prizes-to-students-from-around-the-world/
- Khoury News, HackMIT 2025 (Griddy, sustainability track): https://www.khoury.northeastern.edu/khoury-undergrads-win-three-categories-at-prestigious-mit-hackathon
- The Tech, HackMIT 2026 (no sustainability winner named): https://thetech.com/2026/10/01/hackmit-2026
- HackMIT 2024 Sustainability Grand Prize (Foundry; project name not found): https://x.com/ssankar/status/1836076339691999679

**Team files [F]**
- `results/SUMMARY.md` ("Lessons from six years of MHacks winners", "Cross-check")
- `results/pivot-ideas/01-past-winner-patterns.md`
- `results/main-and-fun-tracks/01-main-sustainability.md` (pool sizes, 2025 Greenprint field)
- `results/year-research/2023.md`, `2024.md`, `2025.md` (Carbon Footprint Extension, SolarVista, the load-balancing winner, EcoScout, Wattson, FarmX)

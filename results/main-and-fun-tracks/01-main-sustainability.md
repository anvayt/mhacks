# Main Track Advocate — Sustainability

## Prompt given (excerpt)
> You are the advocate for the main track "Sustainability" at MHacks 2026. Research how it is judged, how crowded it will be, what has won analogous categories, how it stacks with the fun and sponsor tracks, three project directions, honest weaknesses, and a 1–10 scorecard. Make the strongest honest case — an impartial judge will weigh your file against five other track advocates.

---

## 0. Bottom line

- **Same money, fewer opponents.** Each of the four main tracks pays the same $2,500, and the Grand Prize is $5,000 ([Handbook, Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)). So the main-track choice comes down to which pool gives the best odds. The closest past data point is MHacks 2025's "Greenprint" track. Its description matches the 2026 Sustainability text word for word ([MHacks 2025 rules](https://mhacks-2025.devpost.com/rules)). It drew **15 of 122 submissions (12%)**, tied for the smallest track. The "Optimization" track drew 40 (33%) (my counts from Devpost's prize filter: [Greenprint](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90481), [Overdrive](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90484)).
- **The 2025 field was weak.** Greenprint entries included a "simple" image classifier that tells you if something is recyclable, several carbon-footprint trackers, and at least three projects that had nothing to do with sustainability (a credit-card rewards app, an edtech app, and a Q&A app that won a different track) ([filtered gallery](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90481)). The winner, *Wattson*, was a 4-person build: OpenCV light detection, a FREE-WILi board and a virtual pet. It **also won Best Use of FREE-WiLi** ([Wattson](https://devpost.com/software/wattson-5btsyd)). FREE-WILi is a sponsor again in 2026.
- **The 2026 event branding is about nature.** MHacks 2026 calls itself "Digital Garden," with the tagline "Build something that grows" and "24 hours of building at the intersection of nature and technology" ([mhacks.org](https://www.mhacks.org/); [site metadata in the MHacks repo](https://github.com/mhacks/dashboard/blob/main/app/layout.tsx)). Sustainability is the only main track that matches that theme directly. *(Inference: this can help with judge reception and theme fit. It may also draw a few more teams than in 2025.)*
- **Every sponsor track the team likes can stack on it.** SpaceX "Make it Legendary" asks for "Real space data goes in," and satellite Earth-observation data (NASA FIRMS, NASA POWER) is one of the most natural uses of space data. FREE-WILi, Fetch.ai, ElevenLabs, Neon, Notability, Figma, SpacetimeDB and Relay also combine cleanly. Capital One is the one awkward fit.

**Scorecard (detail in §8):** Win probability 7 · Competition 8 · Feasibility 8 · Demo impact 7 · Stacking 8 · Fit with team preferences 9.

> ⏰ **Time-sensitive:** hacking runs **12 PM Oct 3 → 12 PM Oct 4**. Devpost closes at 12 PM with "no late submissions or exceptions" ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)). If the team stacks SpaceX, **build in Cursor from minute one** ("The more you use Cursor, the more likely you are to win"). Do ideation in **Notability Pro** now; the track needs at least 2 screenshots ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)).

---

## 1. What the track rewards and how it's judged

**Track text (official):** "Innovate for a greener tomorrow. Build solutions that rethink energy, climate, and resource systems for lasting impact on our planet." ([MHacks 26 Tracks page in the Handbook](https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b)). The handbook says hackers are "required to build under one of the themes" (same source).

**Prize:** $2,500, the same for all four main tracks. Grand Prize: $5,000 cash ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)).

**Judging process (2026 Hacker Handbook)** ([source](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)):
- On-site at the Duderstadt Center, **Sun Oct 4, 12:30–2:30 PM**. Each team gets a **three-minute** slot. "Projects may be judged more than once by different judges."
- Sponsors judge their tracks during the same window. "To be judged for any track, your team must be present."
- What to prepare: a concise demo, a 3-minute pitch on "the problem your project solves, its unique features, and potential impact," and readiness for Q&A on "development process, challenges faced, and future plans."
- Scoring: "predefined criteria … such as **innovation, technical complexity, usability, and presentation quality**."

**Historical rubric (2024 and 2025 Devpost):** Innovation, Technical Complexity, Usability, and **Adherence to Theme**. Adherence to Theme means "Clear demonstration of how the project addresses and contributes to the theme" ([MHacks 2025 rules](https://mhacks-2025.devpost.com/rules); [MHacks 2024](https://mhacks-2024.devpost.com/)). *Inference:* the 2026 list says "such as," so theme adherence probably still counts. A sustainability project scores well on it almost by default.

**What this rewards in practice (inference from the rubric plus the winners in §3):** a credible real-world problem in energy, climate or resources; a demo that works live; a measurable impact claim (kWh, kg CO₂, gallons, dollars); and enough technical depth to survive Q&A. Track judges will have just seen several generic carbon calculators, so originality matters more here than in most tracks.

---

## 2. Competition density

### Hard data (counted 2026-10-03 from Devpost prize filters, which list every project that opted into a prize)

| Hackathon | Prize | Opted in | Total subs | Share |
|---|---|---|---|---|
| **MHacks 2025** | **Greenprint (same text as 2026 Sustainability)** | **15** | 122 | **12%** |
| MHacks 2025 | Overdrive (Optimization) | 40 | 122 | 33% |
| MHacks 2025 | Portal (Frontier Interfaces) | 24 | 122 | 20% |
| MHacks 2025 | Lifeline (Health) | 15 | 122 | 12% |
| TreeHacks 2024 | Sustainability Grand Prize | 39 | 331 | 12% |
| TreeHacks 2025 | Sustainability prizes (×3) | 28–33 | 257 | 11–13% |
| TreeHacks 2026 | Stanford Ecopreneurship Sustainability (×3) | 33–45 | 378 | 9–12% |
| PennApps XXV | Best Sustainability Hack (Bloomberg) | 15 | 103 | 15% |
| PennApps XXVI | Sustainability (Bloomberg) | 23 | 85 | 27% |
| Cal Hacks 11.0 | PepsiCo PEP+ Sustainability (sponsor-specific) | 21 | 352 | 6% |

Sources: filter and gallery URLs in §Sources. MHacks 2025 track names and descriptions: [MHacks 2025 rules](https://mhacks-2025.devpost.com/rules) and [search summary of the MHacks 2025 tracks](https://www.mhacks.org/prizes). Total 122: [MHacks 2025 gallery](https://mhacks-2025.devpost.com/project-gallery).

**Caveats:** (a) Opt-in counts overstate on-topic entries. At least 3 of the 15 Greenprint entries were not about sustainability, and one of them (*Ventura*) won Overdrive. So in 2025, teams could tick more than one track box on Devpost even though the rules said one track. (b) TreeHacks and PennApps sustainability prizes were stackable, not exclusive, so their shares are an upper bound for a pick-one main track. (c) One year of MHacks data is a small sample.

### Why 2026 should stay light (inference, labeled)
1. **The sponsor lineup pulls teams toward AI.** About half of the 12 sponsor tracks are AI-agent or voice tracks: Fetch.ai ASI:One, ElevenLabs, Photon iMessage agents, Relay interactive agents, and SpaceX (Grok API). Neon's prize is AI Gateway credits ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)). Teams that build for those sponsors will default to "Actually Intelligent."
2. **FinTech also has a sponsor pull.** Capital One Nessie, plus SpacetimeDB, whose brief lists "trading / financial-style apps," "prediction market," and "real-time portfolio sim" as examples (same source).
3. **No sponsor track is sustainability-specific.** Nothing pushes teams into this track except their own interest.
4. **The counter-pressure is the theme.** The "Digital Garden / nature and technology" branding ([mhacks.org](https://www.mhacks.org/)) may pull some extra teams in. My estimate: Sustainability gets **roughly 10–20% of submissions**, versus 35–50% for AI. If 2026 is about the size of 2025 (122 submissions; [gallery](https://mhacks-2025.devpost.com/project-gallery)), that means **about 12–25 Sustainability teams**. MHacks markets "1,000+ student builders" ([mhacks.org](https://www.mhacks.org/)), but Devpost counted 380 participants in 2025 ([MHacks 2025](https://mhacks-2025.devpost.com/)), so the true scale is uncertain.

---

## 3. Precedent: what actually won

### MHacks (direct)
| Year / prize | Winner | What they actually built |
|---|---|---|
| **2025 Greenprint** (sustainability) | **Wattson** (4 people) | Reduces electricity waste by gamifying lights-off time. OpenCV detects whether a light is on; a virtual pet thrives when lights are off; built with Python, Pillow and a **FREE-WiLi** device. **Also won Best Use of FREE-WiLi.** ([Devpost](https://devpost.com/software/wattson-5btsyd)) |
| **2024 Sustainability Track** | **FarmX** (2 people) | A Random-Forest ML platform that predicts optimal nitrogen and fertilizer use from temperature, humidity, pH and rainfall, and forecasts crop yield. Built with Streamlit and Next.js. ([Devpost](https://devpost.com/software/farmx-zpw0yq)) |
| 2025 Greenprint entrant (did not win the track) | GreenPrint (solo) | IoT hub with AI-agent alerts on CO₂ and energy. Won Best Use of AgentMail, but the author says it was never deployed ([Devpost](https://devpost.com/software/greenprint-c2deb1)). Lesson: sponsor tracks still pay out for sustainability builds. |
| 2025 Grand Award (context) | Artificial Sandwich Intelligence (solo) | A transformer robot policy on a LeRobot SO101 arm that makes a sandwich ([Devpost](https://devpost.com/software/artificial-sandwich-intelligence)) |
| 2024 Grand Prize (context) | V²/R | VR breadboard simulator ([gallery](https://mhacks-2024.devpost.com/project-gallery); [prize check](https://devpost.com/software/v-r)) |

**Takeaway:** the MHacks sustainability bar has been beatable: a 2-person Streamlit ML app won in 2024. The 2025 winner beat a weak field by adding **a physical sensing element and a playful loop**. MHacks Grand Prizes have gone to physical or immersive demos.

### Peer hackathons
| Event / prize | Winner | What they did |
|---|---|---|
| TreeHacks 2024 Sustainability Grand Prize | **SkySplat** | Parrot drones plus Gaussian-splatting 3D models (COLMAP, GPU training, three.js) for disaster recovery and infrastructure inspection ([Devpost](https://devpost.com/software/skysplat)) |
| TreeHacks 2024 Most Innovative Sustainability Hack | Carbon Cut; Spark | A climate-action hub; a platform matching people to sustainability projects (Spark also won a Convex prize) ([Carbon Cut](https://devpost.com/software/carbon-cut-3d5k2g), [Spark](https://devpost.com/software/spark-mhxso9)) |
| TreeHacks 2025 Sustainability ("best solves user's pain point") | **ERWIN** | Carbon-removal assessment for enhanced rock weathering, using SoilGrids, Open-Meteo and Mapbox data to forecast CO₂ removal ([Devpost](https://devpost.com/software/erwin-enhanced-rock-weathering-impact-navigator)) |
| TreeHacks 2025 Sustainability ("best prototyping") | BAS Climate Action Matcher | Embedding search plus agentic workflows matching companies to climate actions; also won an InterSystems GenAI prize ([Devpost](https://devpost.com/software/bas-climate-action-matcher)) |
| TreeHacks 2025 Sustainability ("broader context") | Lemon | Marketplace for surplus or "imperfect" produce from local farmers, to cut food waste ([Devpost](https://devpost.com/software/lemon-7gn5hq)) |
| TreeHacks 2026 Sustainability ("best prototyping") | **GridVeda** | Edge-AI predictive failure detection for 20 grid transformers on a Jetson, ML ensembles, 3D dashboard ([Devpost](https://devpost.com/software/gridveda)) |
| TreeHacks 2026 Sustainability ("broader context") | Morro | A "geoengineering operating system": predict disasters and choose cloud-seeding interventions ([Devpost](https://devpost.com/software/morro)) |
| PennApps XXV Best Sustainability Hack | **Chilladelphia** | Enter a Philly address and get a "chill rating" from aerial-imagery tree detection (DetecTrees), plus tree-planting suggestions and cooling centers ([Devpost](https://devpost.com/software/chilladelphia)) |
| PennApps XXVI Sustainability | CarbonChain | Blockchain carbon-credit marketplace with "Proof-of-Impact" NFTs ([Devpost](https://devpost.com/software/carbonchain-m2hxz4)) |
| Cal Hacks 11.0 PepsiCo Sustainability | TrashToTreasure; Peps Towards Sustainability | AI upcycling ideas for waste; a sustainability-metrics dashboard ([TrashToTreasure](https://devpost.com/software/trashtotreasure-sustainable-showcase), [Peps](https://devpost.com/software/peps-towards-sustainability)) |
| HackMIT 2024 | (unnamed) | A team won the Sustainability Grand Prize **plus 3 sponsor challenges** on a Palantir Foundry backend, per Palantir's CTO ([X post](https://x.com/ssankar/status/1836076339691999679)). Project name not verified. |

**Patterns across winners:** (1) **real external data**: satellite and aerial imagery, soil and climate APIs, sensor feeds; (2) **a specific user and place**: Philly residents, ERW project developers, grid operators; (3) **a tangible or visual output**: 3D models, maps, a pet, a physical device; (4) sustainability winners **often also win sponsor prizes** (Wattson, BAS, Spark, HackMIT 2024).

---

## 4. Win levers (what specifically wins this track)

1. **Act, don't just show a dashboard.** Close the loop: turn a device off, reschedule a load, route surplus food. Fetch.ai's MHacks hackpack explicitly rewards agents that "take meaningful action," not "simple chatbots" ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5); [Fetch.ai hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)).
2. **Live, real data on stage.** Use the actual Midwest grid's carbon intensity (Electricity Maps covers zone `US-MIDW-MISO`; the free tier is limited to one zone ([Electricity Maps](https://app.electricitymaps.com/datasets?zone=US-MIDW-MISO); [Green Web Foundation explainer](https://developers.thegreenwebfoundation.org/grid-intensity-cli/explainer/providers/))), satellite fire detections (NASA FIRMS, free MAP_KEY ([FIRMS](https://firms.modaps.eosdis.nasa.gov/api/map_key/))), or satellite-derived solar irradiance (NASA POWER, no key needed ([POWER docs](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/))).
3. **One quantified impact number in the pitch.** For example, "shifting this load saves X kg CO₂ per week at today's MISO intensity." The handbook asks pitches to cover "potential impact" ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)).
4. **A local hook.** Ann Arbor's A2ZERO plan targets community-wide carbon neutrality by 2030 ([a2gov.org](https://www.a2gov.org/sustainability-innovations-home/carbon-neutrality-home/)), and the city has an opt-in Sustainable Energy Utility ([a2gov.org](https://www.a2gov.org/news/posts/sustainable-energy-utility-seu-authorized-in-the-city-of-ann-arbor/)). U-M has committed to eliminating Scope 1 emissions by 2040 ([Planet Blue goals](https://planetblue.umich.edu/campus/goals-and-dashboards/goals)). A judge in Ann Arbor will recognize these.
5. **Something physical or visually striking.** Wattson (hardware) won Greenprint, and both recent Grand Prizes were physical or immersive (§3).
6. **Avoid the clichés the 2025 field was full of:** recyclability classifiers, generic footprint calculators, eco-score shopping apps ([2025 Greenprint entries](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90481)).
7. **A pitch that survives repeat judging.** Projects "may be judged more than once," so open with a 20-second hook and leave 2 minutes for the live demo ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)).

---

## 5. Stacking: one coherent project, many tracks

Sponsor and fun tracks are open to entries from any main track ("On top of your main track, submit to as many sponsor tracks as apply"), so stacking is about **coherence**, not eligibility.

| Track | Fit with Sustainability | How (and what it requires) |
|---|---|---|
| **SpaceX: Make it Legendary** | **Strong** | "Real space data goes in." NASA FIRMS (MODIS/VIIRS satellites) and NASA POWER (satellite-derived irradiance) are space-mission data ([FIRMS](https://firms.modaps.eosdis.nasa.gov/api/map_key/); [POWER](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/)). **Must** be built with Cursor and use **Grok Imagine or the Grok Voice API** ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)). The Grok Voice Agent API supports function calling over a realtime WebSocket ([xAI docs](https://docs.x.ai/developers/model-capabilities/audio/voice-agent)); Grok Imagine generates video ([promptfoo xAI provider docs](https://www.promptfoo.dev/docs/providers/xai/)). *Risk (inference):* judges may prefer "space-y" data (orbits, launches) over Earth observation, so frame it as "satellites watching Earth." Prize is mechanical keyboards, not cash. |
| **FREE-WILi** | **Strong (proven)** | Wattson won both Greenprint and FREE-WiLi in 2025 ([Devpost](https://devpost.com/software/wattson-5btsyd)). FREE-WILi 2 has an **SHT40 temp/humidity sensor, OPT4001 ambient-light sensor, IR Tx/Rx**, Wi-Fi/BLE/LoRa, and Python APIs ([freewili.com](https://freewili.com/)). The IR transmitter can switch off IR-controlled ACs, fans and TVs. *Unverified:* which model MHacks hands out, and whether loaners exist (2025 had 5 FREE-WiLi entries ([filter](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90539))). Ask at the sponsor table first. |
| **Fetch.ai ASI:One** | **Strong** | An agent that turns intent ("run my laundry when the grid is cleanest") into action. Needs Agentverse registration, Chat Protocol, a 3–5 min demo video, and a separate submission through the ASI:One Submission Agent. Rubric: Functionality 25%, Fetch tech 20%, Innovation 20%, **Real-World Impact 20%**, UX 15% ([hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)). |
| **ElevenLabs** | Good | A voice narrator or coach. Low cost to add. Every participant gets 1 month of Creator tier ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)). If going for SpaceX, the Grok Voice API already covers voice, so pick one as the main voice. |
| **Neon Backend** | Good | Postgres for sensor time-series or user data. Judged on using Neon "to its fullest," so use more than one feature, e.g. auth plus database (same source). |
| **Notability** | Free | Qualify by using Notability Pro for ideation and wireframes; tag it on Devpost with 2+ screenshots (same source). |
| **Figma Best Design** | Good | Any polished UI. Top 3 get merch (same source). |
| **SpacetimeDB** | Good (Direction C) | Live shared state: a multiplayer energy game, community dashboard, or coordinated agents. Must be the *core* backend, "not just added on the side" (same source). |
| **Relay Interactive Agents** | Moderate–Good | Relay's own idea list includes "🍽️ Food: dining halls, free food." A food-rescue agent that students text about leftover event food is a sustainability project that sits inside Relay's suggested category. "Your agent must work in the Relay app" (same source; [docs](https://docs.relayapp.im/llms.txt)). |
| **Photon (iMessage)** | Moderate | Same idea through iMessage group chats. Requires Photon's Spectrum framework (same source). |
| **Capital One Nessie** | **Weak / splits the pitch** | Possible angles: green round-ups into a community-solar fund, or putting $ saved by load-shifting into a Nessie account ([Nessie endpoints](https://github.com/andrewalexander/capital_one_python)). But Nessie judges want to "reimagine the banking experience," and adding it pulls the story toward FinTech. Add it only if it falls out naturally. |
| **FinchNode (HealthTech)** | Conflict | Requires an integration with synthetic health records (same source). Heat-health is a stretch. Skip. |
| **Judged by an LLM** (fun) | **Strong** | "Technically sharp enough to impress an AI judge" ([MHacks 26 Tracks](https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b)). A data-heavy, well-documented sustainability build with a precise Devpost write-up is a good fit. The prize is chosen by the LLM from a list ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)). |
| **Useless AI / Dumbest Idea** (fun) | Tonal conflict | These reward pointlessness; Sustainability rewards impact. Submitting costs nothing, but don't bend the pitch. One exception: a deliberately silly feature (e.g., a houseplant that roasts you in an ElevenLabs voice) could justify a Dumbest Idea entry without hurting the main pitch. |

**Realistic stack for one project:** Sustainability + SpaceX + FREE-WILi *or* Fetch.ai + Neon + Notability + Figma + Judged by an LLM (+ ElevenLabs if voice isn't Grok). That is 6–7 entries with one story.

---

## 6. Three project directions

### A. "Second Sky": a satellite view of your block's future (flagship for the SpaceX stack, software-only)
A user enters an Ann Arbor or Detroit address. The app pulls **satellite data**: NASA POWER solar irradiance for rooftop solar potential, NASA FIRMS fire and smoke detections, and tree-canopy / heat-island signals from imagery (the same approach that won PennApps XXV with Chilladelphia ([Devpost](https://devpost.com/software/chilladelphia))). It then produces a concrete plan: which A2ZERO programs apply, the Sustainable Energy Utility opt-in ([a2gov.org](https://www.a2gov.org/news/posts/sustainable-energy-utility-seu-authorized-in-the-city-of-ann-arbor/)), and where to add canopy and solar. **Grok Imagine** renders a "greened" before/after video of the street. A **Grok Voice** agent answers questions and can call tools for live data. Build it in Cursor. **Stacks:** SpaceX, Figma, Neon, Notability, Judged by an LLM; Fetch.ai if the planner becomes an Agentverse agent. **Why it wins:** real space data, a local hook, and a striking visual that holds up through repeat 3-minute judging. **Risk:** generated images can look like fluff, so put the hard numbers (kWh/yr, kg CO₂) beside them.

### B. "Gridlock": a grid-aware agent that actually flips the switch (hardware-light, action-taking)
A **FREE-WILi** board sits in a dorm room. Its light and temperature/humidity sensors detect waste such as lights on in an empty room or AC running with the window open (Wattson's proven idea, extended ([Devpost](https://devpost.com/software/wattson-5btsyd))). Its **IR transmitter** turns off the AC, fan or TV ([freewili.com](https://freewili.com/)). A **Fetch.ai agent** registered on Agentverse takes requests like "dry my laundry when MISO is cleanest tonight." It checks live MISO carbon intensity ([Electricity Maps](https://app.electricitymaps.com/datasets?zone=US-MIDW-MISO)) and schedules the action. The demo is physical: a judge says it out loud, and a device on the table turns off. **Stacks:** FREE-WILi, Fetch.ai, ElevenLabs (voice confirmations), Neon (event log), Notability, Judged by an LLM. If NASA POWER solar forecasts drive the "when," plus a Grok voice interface, it can also enter SpaceX. **Why it wins:** it closes the action loop, matches 2025 precedent, and a physical demo has done well at MHacks. **Risk:** hardware access and IR compatibility. Bring a cheap IR-controlled fan or LED strip as a known-good target.

### C. "Floor Wars": a real-time dorm energy competition (multiplayer, social)
Dorm floors or friend groups compete live on energy waste. Each "player" is a FREE-WILi sensor node or a phone check-in. Scores are weighted by real-time grid carbon intensity, so a waste at 7 PM peak costs more than at 3 AM. **SpacetimeDB** holds the shared world state: a live leaderboard and a shared "garden" that grows or wilts with the group's footprint, which is a direct nod to the "Build something that grows" theme ([mhacks.org](https://www.mhacks.org/)). A **Relay** or **Photon** agent nudges the group chat ("Floor 3, your lounge lights have been on for 2h with nobody there"). **Stacks:** SpacetimeDB ($1,000/$500/$200 cash), FREE-WILi, Relay or Photon, Figma, Notability, Judged by an LLM. **Why it wins:** a multiplayer, visual, social demo; SpacetimeDB is the core backend, not a bolt-on. **Risk:** the most moving parts of the three. Scope it to 2–3 sensor nodes plus simulated players.

*Recommendation if the team leans SpaceX: A as the base. Bolt on B's Fetch.ai agent only if time allows.*

---

## 7. Honest weaknesses, rival arguments, rebuttals

| Weakness or rival argument | Rebuttal |
|---|---|
| **"Sustainability hacks are clichés; judges are tired of carbon calculators."** (true, see the 2025 field) | That is exactly why the pool is beatable. The levers in §4 (act, live data, physical or visual output) separate a team from the clichés. FarmX won with a 2-person Streamlit app ([Devpost](https://devpost.com/software/farmx-zpw0yq)). |
| **AI advocate: "Six sponsor tracks are AI; pick the AI main track to match."** | Sponsor tracks are open to every main track. A sustainability project can use Fetch.ai, Grok and ElevenLabs and enter all of them, while competing for the $2,500 in a pool that is likely a third the size of AI's. The AI track says "Build AI that actually solves a real problem" ([MHacks 26 Tracks](https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b)). An AI-powered sustainability project would fit there too, but would face the biggest crowd. |
| **FinTech advocate: "Capital One stacks naturally and money problems are concrete."** | The team already expects FinTech to be crowded, and the sponsor list adds pull (Nessie; SpacetimeDB's trading examples ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5))). Capital One's prize is a $300 gift card per member. Sustainability keeps SpaceX, FREE-WILi, Fetch.ai, SpacetimeDB, Relay and Neon at the cost of a weaker Nessie fit. |
| **Hardware advocate: "Physical demos win MHacks; the 2025 Grand Award was a sandwich robot."** | Agreed that physical demos win, which is why Directions B and C include a small hardware element. But the team's hardware experience is unknown. In the Hardware track you are judged against robotics teams; in Sustainability, a FREE-WILi plus an IR blaster is a highlight, not the minimum (Wattson precedent). |
| **"No sponsor is sustainability-themed, so there's no extra prize money behind the domain."** | True. But that is the same reason the pool is small (§2). Sustainability winners routinely also win tool-based sponsor prizes (Wattson, BAS Climate Action Matcher, Spark, HackMIT 2024 (§3)). |
| **"The Digital Garden theme will flood the track this year."** | Possible, and I can't verify it. Even doubling 2025's 12% share keeps it below the likely AI share. If organizers chose a nature theme, they may also favor nature-themed work on theme adherence (inference). |
| **"Impact claims can't be proven in 24 hours."** | Don't claim global impact. Show one measured or computed number from live data (§4.3), and say what is simulated. |
| **"Only $2,500, and Grand Prizes went elsewhere."** | Every main track pays $2,500, so the comparison is a wash. A strong Sustainability project still competes for the $5,000 Grand Prize. |
| **"One year of MHacks data is a thin basis."** | Agreed, it's n=1. But TreeHacks 2024–26 and PennApps XXV point the same way (9–15% opt-in) (§2). PennApps XXVI (27%) is the outlier I found. |

---

## 8. Scorecard (1–10)

| Criterion | Score | One-line justification |
|---|---|---|
| **Win probability** | **7** | Smallest likely pool (12% of submissions in 2025) and a historically weak field; still need to beat roughly 12–25 teams for one $2,500 slot. |
| **Competition** (10 = least crowded) | **8** | Tied for the least crowded MHacks 2025 track, and no sponsor pulls teams in; the nature theme is the main reason it isn't a 9. |
| **Feasibility (24 h)** | **8** | All directions run on free public APIs (NASA POWER needs no key; FIRMS has a free key) plus optional hardware; scope risk mainly in C. |
| **Demo impact** | **7** | Can be very strong (Grok Imagine before/after, a device turning off) but drops to 4 if it becomes a dashboard. |
| **Stacking potential** | **8** | Clean fit with SpaceX, FREE-WILi, Fetch.ai, ElevenLabs, Neon, Notability, Figma, SpacetimeDB, Relay, Judged by an LLM; weak with Capital One; conflicts with FinchNode. |
| **Fit with team preferences** | **9** | Avoids FinTech crowding, keeps the SpaceX bias central, includes a fun track (Judged by an LLM), allows several sponsor tracks; Capital One is the one preference it serves poorly. |

---

## 9. Head-to-head vs the other main tracks

| | **Sustainability** | Actually Intelligent (AI) | FinTech | Beyond the Code (Hardware) |
|---|---|---|---|---|
| Prize | $2,500 | $2,500 | $2,500 | $2,500 |
| Likely crowding (inference) | **Low–moderate**: 12% in 2025 | **Highest**: about half the sponsor tracks are AI agents | Moderate–high: Nessie and SpacetimeDB trading pull; team already expects crowding | Low–moderate: limited by hardware access (MLH lab "first-come, first-served" ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af))) |
| Clarity of what wins | Clear: real problem, real data, measurable impact | Vague ("actually solves a real problem"), so judges must pick among many similar agents | Clear but well-trodden | Clear: working physical device |
| Fit with event theme ("nature and technology") | **Direct** | Indirect | None | Indirect ("bridges the digital and the real") |
| SpaceX stack | **Natural** (Earth-observation space data) | Possible | Awkward | Possible |
| Capital One stack | Weak | Possible | **Natural** | Weak |
| Software-team feasibility | High | High | High | Unknown (hardware experience unconfirmed) |
| Ceiling for a strong team | Track win + 4–6 sponsor or fun prizes | Many sponsor prizes but a crowded track | Capital One + track, in a crowded field | Grand-Prize-type demo, but high execution risk |

**Verdict:** For a 4-person software team that wants to avoid crowds and leans toward SpaceX, Sustainability has the best mix of small field, theme fit and stacking. Compared with **FinTech**, it gives up only Capital One and avoids the crowd the team is worried about. Compared with **AI**, it keeps every AI sponsor track while competing in a pool that is probably a third the size. Compared with **Hardware**, it keeps the benefit of a physical demo without betting the main-track result on unconfirmed hardware skills.

---

## Sources

**MHacks 2026 (official)**
- 2026 Hacker Handbook (Notion): https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af
- Handbook › Tracks & Prizes: https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5
- Handbook › MHacks 26 Tracks: https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b
- Handbook URL in MHacks source code: https://github.com/mhacks/dashboard/blob/main/lib/wallet/event.ts
- Handbook-linking PR: https://github.com/mhacks/dashboard/pull/197
- Site metadata ("Digital Garden," "intersection of nature and technology"): https://github.com/mhacks/dashboard/blob/main/app/layout.tsx
- FAQ copy ("climate tools" among past projects): https://github.com/mhacks/dashboard/blob/main/components/landing/sections/Faq.tsx
- MHacks site: https://www.mhacks.org/
- MHacks live site: https://www.mhacks.org/live
- Fetch.ai MHacks 2026 hackpack: https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack

**MHacks past years**
- MHacks 2025 Devpost: https://mhacks-2025.devpost.com/
- MHacks 2025 rules (judging criteria, Greenprint text, one-track rule): https://mhacks-2025.devpost.com/rules
- MHacks 2025 gallery: https://mhacks-2025.devpost.com/project-gallery
- MHacks 2025 track names (search result for the old live site): https://live.mhacks.org/prizes → https://www.mhacks.org/prizes
- MHacks 2025 Greenprint opt-ins: https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90481
- MHacks 2025 Overdrive opt-ins: https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90484
- MHacks 2025 Portal opt-ins: https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90485
- MHacks 2025 Lifeline opt-ins: https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90483
- MHacks 2025 FREE-WiLi opt-ins: https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90539
- Wattson: https://devpost.com/software/wattson-5btsyd
- GreenPrint: https://devpost.com/software/greenprint-c2deb1
- Artificial Sandwich Intelligence: https://devpost.com/software/artificial-sandwich-intelligence
- MHacks 2024 Devpost: https://mhacks-2024.devpost.com/
- MHacks 2024 gallery: https://mhacks-2024.devpost.com/project-gallery
- FarmX: https://devpost.com/software/farmx-zpw0yq
- V²/R: https://devpost.com/software/v-r
- MHacks 16 (2023): https://mhacks-16.devpost.com/

**Peer hackathons**
- TreeHacks 2024 gallery: https://treehacks-2024.devpost.com/project-gallery
- TreeHacks 2024 Sustainability Grand Prize opt-ins: https://treehacks-2024.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=73403
- TreeHacks 2025 gallery: https://treehacks-2025.devpost.com/project-gallery
- TreeHacks 2025 Sustainability opt-ins: https://treehacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=83866
- TreeHacks 2026 gallery: https://treehacks-2026.devpost.com/project-gallery
- TreeHacks 2026 Sustainability opt-ins: https://treehacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=96820
- PennApps XXV gallery / opt-ins: https://pennapps-xxv.devpost.com/project-gallery ; https://pennapps-xxv.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=79013
- PennApps XXVI gallery / opt-ins: https://pennapps-xxvi.devpost.com/project-gallery ; https://pennapps-xxvi.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90475
- Cal Hacks 11.0 gallery / opt-ins: https://cal-hacks-11-0.devpost.com/project-gallery ; https://cal-hacks-11-0.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=80290
- Stanford Daily on TreeHacks 2025: https://stanforddaily.com/2025/02/18/treehacks-awards-200000-in-prizes-to-students-from-around-the-world/
- SkySplat: https://devpost.com/software/skysplat
- Carbon Cut: https://devpost.com/software/carbon-cut-3d5k2g
- Spark: https://devpost.com/software/spark-mhxso9
- ERWIN: https://devpost.com/software/erwin-enhanced-rock-weathering-impact-navigator
- BAS Climate Action Matcher: https://devpost.com/software/bas-climate-action-matcher
- Lemon: https://devpost.com/software/lemon-7gn5hq
- GridVeda: https://devpost.com/software/gridveda
- Morro: https://devpost.com/software/morro
- Chilladelphia: https://devpost.com/software/chilladelphia
- CarbonChain: https://devpost.com/software/carbonchain-m2hxz4
- TrashToTreasure: https://devpost.com/software/trashtotreasure-sustainable-showcase
- Peps Towards Sustainability: https://devpost.com/software/peps-towards-sustainability
- HackMIT 2024 Sustainability Grand Prize mention: https://x.com/ssankar/status/1836076339691999679

**Sponsor tooling and data sources**
- FREE-WILi 2 hardware: https://freewili.com/
- xAI Grok Voice Agent API: https://docs.x.ai/developers/model-capabilities/audio/voice-agent
- xAI Grok Voice Agent announcement: https://x.ai/news/grok-voice-agent-api
- Grok Imagine video via xAI provider: https://www.promptfoo.dev/docs/providers/xai/
- Relay docs index: https://docs.relayapp.im/llms.txt
- Nessie API endpoints (community wrapper listing): https://github.com/andrewalexander/capital_one_python
- Electricity Maps MISO zone: https://app.electricitymaps.com/datasets?zone=US-MIDW-MISO
- Electricity Maps free-tier limits: https://developers.thegreenwebfoundation.org/grid-intensity-cli/explainer/providers/
- NASA FIRMS MAP_KEY: https://firms.modaps.eosdis.nasa.gov/api/map_key/
- NASA POWER hourly API: https://power.larc.nasa.gov/docs/services/api/temporal/hourly/

**Local context**
- Ann Arbor A2ZERO / carbon neutrality: https://www.a2gov.org/sustainability-innovations-home/carbon-neutrality-home/
- Ann Arbor Sustainable Energy Utility: https://www.a2gov.org/news/posts/sustainable-energy-utility-seu-authorized-in-the-city-of-ann-arbor/
- U-M Planet Blue carbon goals: https://planetblue.umich.edu/campus/goals-and-dashboards/goals

*Method note: the opt-in and total-submission counts in §2 are my own tallies of Devpost's public gallery and prize-filter pages, taken on 2026-10-03. Devpost lists every project that opted into a prize, not only winners. Anything marked "inference" is my reasoning, not a sourced fact.*

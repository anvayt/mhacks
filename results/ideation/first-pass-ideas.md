# Project Ideas — First Ideation Pass

> **Note:** this agent ran before the team chose Clean Hours (satellite-imagery version) as the main idea, so it ranks ideas on its own. The chosen plan is in `../SUMMARY.md` → "Project ideas". These are kept as extra alternatives.
### Prompt given (excerpt)
> You are the ideation agent. Using the results of every prior agent (year research, both verdict files, the sponsor and advocate files, and the final debate), generate concrete MHacks 2026 project ideas that fit the recommended track combination, explain why each would win based on past MHacks winners and judges' remarks, and give a fast way to test each idea before committing.

*Written Sat Oct 3, 2026, starting 9:30 AM EDT. Hacking starts at noon, and the Sponsor Expo is at 11:30 ([schedule](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365)).*

**Tags used below:**
- **[V]**: I checked it myself today at the linked URL.
- **[R]**: it comes from the team's research files, which cite the linked source. I did not re-check it.
- **[I]**: my inference.
- **[U]**: unverified. Ask on site.

MHacks held no event in 2022 ([`year-research/2022.md`](/Users/anvaytodkar/Code/mhacks/results/year-research/2022.md)), so the precedents below come from 2020, 2021 and 2023–2025, plus 2026 peer events for the sponsors.

### The two combinations

- **Combo A, the recommended one.** Ideas 1–7 fit it exactly.
  - **Main track:** Sustainability.
  - **Fun tracks:** Judged by an LLM and Dumbest Idea.
  - **Core sponsors:** Relay, SpaceX "Make it Legendary", Fetch.ai ASI:One, ElevenLabs and FREE-WILi.
  - **Optional sponsors:** Figma, Capital One Nessie and Notability.
  - **Free extra:** the separate [MLH] Best Use of ElevenLabs prize. It is listed on the Devpost and costs nothing extra to enter [R] ([Devpost](https://mhacks-2026.devpost.com/)).
- **Combo B, the strongest runner-up.** Ideas 8–9 fit it.
  - Same main and fun tracks as Combo A.
  - **Core sponsors:** Relay, SpaceX, Fetch.ai and ElevenLabs, with **no FREE-WILi**.
  - **Optional sponsors:** the same three: Figma, Capital One (as the parametric payout or the Green Fund) and Notability.
  - This is the debate's own fallback branch. It applies if SpaceXAI says only orbit or mission data counts, or if there are no FREE-WILi loaners (final debate, round 2, main-track rep §5).

### At a glance

| # | Idea | One-liner | Combo | Rank |
|---|---|---|---|---|
| 1 | **Clean Hours (sharpened)** | Text a houseplant named Fern. She moves your loads to the grid's cleanest hours, phones you when the window opens, and flips the switch herself if you ignore her. | A | **Top 1** |
| 2 | **T-Minus Laundry** | Mission Control for chores. Every big load is a "launch" with GO/NO-GO criteria from the live grid and GOES-19. A flight director calls you, and the FREE-WILi console fires at T-0. | A | **Top 2** |
| 3 | **Cloudbreak** | A satellite nowcast of clean power. GOES-19's 5-minute cloud mask over the region's solar farms predicts solar surges 30–60 min ahead, and the agent times your load to them. | A | **Top 3** |
| 4 | **Hang Time** | A FREE-WILi on the washer feels the cycle end. The agent calls: GOES-19 says three more hours of sun, so hang it and skip the dryer. If it's cloudy, it runs the dryer at the clean hour. | A | |
| 5 | **Sweater Weather** | Your room as a heat battery. Pre-heat when the grid is clean and the sun is out, then coast through the dirty evening peak. "Grandma Thermostat" tells you to put on a sweater. | A | |
| 6 | **Count Kilowatt** | A "last one out" sweep for shared rooms such as co-ops, labs and club offices. A vampire count hunts down devices left on, and he knows from orbit when the lights are pointless. | A | |
| 7 | **Sun Budget** | The Digital Garden made literal. Your room may only spend the sunlight GOES-19 measured on it today. Appliances eat from the budget, and the garden on the device grows or wilts. | A | |
| 8 | **Overpass (sharpened)** | A satellite wildfire watcher that calls you when a new detection lands near a place you care about and names the satellite that looks next. The joke is "Wave at NOAA-21." | B | |
| 9 | **Clean Hours Lite + Green Fund** | Idea 1 with no FREE-WILi. A USB-powered or simulated device, and each shifted load moves a pledge into a Capital One Nessie "Green Fund". | B | |

---

### Shared spine (ideas 1–7; ideas 8–9 drop the FREE-WILi parts)

**Why the ideas share an engine.** Combo A forces one shape on every idea: satellite data → decision → physical action → voice call. So ideas 1–7 run on **one engine** and differ only in three things: the load they control, the signal they trust, and the joke. The payoff is that the team can choose the "skin" as late as 6 PM without throwing work away [I].

#### Data feeds, checked this morning (13:30 UTC = 9:30 AM EDT)

| Feed | What I saw | Used by |
|---|---|---|
| **GOES-19 ABI Downward Shortwave Radiation** (sunlight at the ground, `ABI-L2-DSRF`) | Newest file: the 13:10 UTC scan, written 13:29 UTC. Scans arrive every 10 minutes [V] ([S3 listing](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-DSRF/2026/276/)). The grid is a simple 0.5° lat/lon grid [R] ([NCEI](https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ncdc%3AC01524)) | 1–7 |
| **GOES-19 Clear Sky Mask, CONUS** (`ABI-L2-ACMC`) | The 13:21 UTC scan was written at 13:24 UTC. It updates every 5 minutes [V] ([S3 listing](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-ACMC/2026/276/)) | 1–3, 5, 7 |
| **GOES-19 Land Surface Temperature, CONUS** (`ABI-L2-LSTC`) | Hourly. The 13:01 UTC scan was written at 13:05 UTC [V] ([S3 listing](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-LSTC/2026/276/)) | 5 |
| **GOES-19 GeoColor image, Upper Mississippi Valley** | HTTP 200, 3.4 MB, last modified 13:26 UTC [V] ([latest.jpg](https://cdn.star.nesdis.noaa.gov/GOES19/ABI/SECTOR/umv/GEOCOLOR/latest.jpg)) | 1–7: a "satellite window" panel |
| NASA POWER | The daily series ends Sep 28, and the hourly series has only fill values since Aug 1 [R] ([probe](https://power.larc.nasa.gov/api/temporal/daily/point?parameters=ALLSKY_SFC_SW_DWN&community=RE&longitude=-83.74&latitude=42.28&start=20260801&end=20261003&format=JSON)) | **Don't use it for live decisions** |
| **Grid signal, option 1: WattTime** | Its plans page lists a CO₂ percentile for all regions on the free Basic plan, with the full signals limited to one region. The page is ambiguous [V] ([plans](https://watttime.org/docs-dev/data-plans/)). The signal is marginal-based [R] ([signals](https://watttime.org/data-science/data-signals/)) | `grid_now` (marginal) |
| **Grid signal, option 2: Electricity Maps** | The free tier covers one zone, with carbon intensity latest and history [V, via third-party summary] ([Green Web Foundation](https://developers.thegreenwebfoundation.org/grid-intensity-cli/explainer/providers/), [zone page](https://app.electricitymaps.com/datasets?zone=US-MIDW-MISO)) | `grid_now` (average) and backtest |
| **Grid signal, option 3: EIA-930** | Hourly MISO generation by fuel through EIA API v2 `electricity/rto/fuel-type-data` with `respondent=MISO` [V, endpoint documented] ([EIAapi docs](https://ramikrispin.github.io/EIAapi/)). Reporting lag is unverified [U] | Backtest; idea 3 validation |
| MISO's own fuel-mix feed | The old data-broker URL now returns "no data". MISO switched to JSON-only feeds on Dec 12, 2025, with endpoints documented behind its help center [V] ([MISO](https://www.misoenergy.org/markets-and-operations/rtdataapis)) | Skip unless found fast |

#### One tool layer
Use one Python FastAPI process and one SQLite file. That is deliberately minimal: no Neon (not entered), no queue, no second database. Both front ends call it over HTTP: the Relay agent (TypeScript, the workshop path) and the Fetch uAgents (Python, mailbox) [I].
- `grid_now()` returns the marginal percentile plus the average gCO₂/kWh, each tagged with its source and timestamp.
- `sky_now(lat, lon)` returns GOES-19 sunlight and cloud fraction, with the scan time on every value (provenance in NOVA's style).
- `plan(load, deadline)` returns the window and the expected grams avoided.
- `actuate(device, cmd)` sends FREE-WILi IR.
- `confirm(device)` checks FREE-WILi accelerometer vibration to see whether the thing really turned on or off.
- `impact()` and `garden_state()`.

**"The remote is the meter" [I].** Every on/off goes through `actuate`, so runtime × nameplate watts gives an estimated kWh with no power meter. Label it as an estimate in the UI and in Limitations.

#### What "genuine use" means for each sponsor (the checkbox test)

| Sponsor | Must be true in the demo | Source |
|---|---|---|
| Relay | The agent works in the Relay app over text, call and video. An **agent-initiated call** to a phone that has added the agent is the demo moment. Keep a QR code on the table so hackers really use it all weekend | [R] [call-a-person](https://docs.relayapp.im/calls/call-a-person.md), [workshop README](https://raw.githubusercontent.com/RelayMessenger/Relay-SDK/main/cookbook/mhacks-workshop/README.md) |
| SpaceX | Code in Cursor from minute one (`.cursor/rules`, frequent commits, Agent screenshots). Grok Imagine makes the persona and garden art, labeled "AI illustration". **GOES-19 data must change a decision live**, not decorate it | [R] [Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5) |
| Fetch.ai | Agents registered on Agentverse, with the Chat Protocol and an @handle. The workflow finishes inside ASI:One with a **Review card**, then a **real action** (the device fires). README addresses and badges. Second submission through the Submission Agent, which every teammate must join. Pin `uagents==0.25.5` | [R] [hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack), [cards](https://innovationlab.fetch.ai/resources/docs/interactive-cards/asi-interactive-cards) |
| ElevenLabs | The persona's voice on every call, through the `@relaymessenger/elevenlabs` bridge with Rive lip-sync. Show emotional range. Use at least two capabilities (agent plus TTS or SFX) | [R] [bridge](https://docs.relayapp.im/calls/elevenlabs.md), [Hack the 6ix rubric](https://hackthe6ix2026.devpost.com/) |
| FREE-WILi | The device is the product's **hands and face**: IR learn and send, accelerometer confirmation, the screen garden, the button and the speaker. The OneWili API has these menus: `ir_save_capture`, `ir_send_button`, `enable_motion_stream`, `enable_env_stream`, plus a sub-GHz `radio` menu with `set_frequency` and `packet_send` [V] ([ir.py](https://github.com/freewili/onewili/blob/main/python/onewili/menus/ir.py), [sensors.py](https://github.com/freewili/onewili/blob/main/python/onewili/menus/sensors.py), [radio.py](https://github.com/freewili/onewili/blob/main/python/onewili/menus/radio.py)) | [R] [OG specs](https://freewili.com/freewili-og.html) |
| Figma (optional) | One designed dashboard plus the 320×240 device-screen states. The workshop is at 5:30 PM | [R] [schedule](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365) |
| Capital One (optional) | Only as a swap-in if FREE-WILi fails, as the Green Fund, which must both read and write Nessie. Never in the main-track pitch | Final debate |
| Notability (optional) | Only with a free Pro code or an existing Pro account, because Pro is $79.99 with no trial [R] ([pricing](https://notability.com/pricing)). Do ideation in it before noon and capture 2+ screenshots | [R] [Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5) |

#### Comic rules (Dumbest Idea), as settled by the final debate
- Tough-love mode is opt-in.
- Roast appliances and habits, never people. The Handbook bans "hateful or toxic" messages ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)).
- The persona never appears on ASI:One, because Fetch gives Real-World Impact 20%.
- With Sustainability judges, the joke gets 15 seconds or less, after the impact number.
- With Relay, ElevenLabs and SpaceX judges, open with the joke.
- **Midnight cut line:** if the core doesn't work end to end by then, switch to a neutral voice and untick Dumbest Idea.

#### Judged by an LLM
P3 writes the Devpost from hour one under these headers:
- the four published criteria: Innovation, Technical Complexity, Usability, Adherence to Theme [R] ([Devpost](https://mhacks-2026.devpost.com/));
- **What we measured:** the backtest table and the actuation log;
- **Limitations:** for example, average vs marginal intensity, and estimated kWh.

Put no hidden instructions to the judge anywhere ([LLM-judge advocate](/Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/06-fun-judged-by-an-llm.md)).

#### Common clock and staffing
| When (Sat → Sun) | P1: Relay + voice (has an iOS 26 phone) | P2: Data + SpaceX | P3: Fetch + write-up | P4: FREE-WILi + design + pitch |
|---|---|---|---|---|
| 9:45–11:30 AM | T3, T6 | T1, T2, T5 | T4; Devpost skeleton | T7, T8; Notability notes |
| 11:30 Expo | Ask Relay: do calls work on the App Store build? | Ask SpaceXAI: does GOES Earth observation count? Any credits? | Ask Fetch: who judges? | Ask FREE-WILi: loaners? Which model and firmware? |
| 12–1 PM | Repo in Cursor; Relay login; cookbook steps 1–2 | Service skeleton; cache GOES and grid data | Mailbox hello-world reachable by @handle | Get a device; LEDs blink |
| 1–2 PM | **Relay workshop** | GOES pixel reader | Tools wrapped behind the chat handler | **FREE-WILi workshop**; learn and send IR |
| 2–4 PM | Persona; call-a-person | Planner, `impact`, backtest data pull | **Fetch workshop (2 PM)**; Review card | **2 PM gate:** smoke test; `actuate` + `confirm` |
| 4–6 PM | **4 PM gate:** Relay calls | **SpaceXAI session (4 PM)**; Grok Imagine art | **6 PM gate:** ASI:One end to end with a real action | Garden screen states; **Figma (5:30)** |
| 6 PM–12 AM | Idea-specific persona logic | Idea-specific signal logic | Split into 2–3 role agents; README; ≥10 interactions | Dashboard |
| **12 AM gate** | Core works end to end? Keep the joke? Is Capital One needed? | | | |
| 12–6 AM | Hardening: `event_id` dedupe, laptop never sleeps | Eval table | Devpost v1 | Polish; **6 AM UI freeze** |
| 9–11:45 AM | 5 timed rehearsals; record the fallback video | | 3–5 min Fetch video; Submission Agent (all four join) | Pitch |
| By 12:00 PM | Devpost submitted. The Handbook says submissions close at noon with no exceptions, while the Devpost page lists 12:15 PM, so treat noon as the deadline [R] ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af), [Devpost](https://mhacks-2026.devpost.com/)) | | | |
| 12:30–2:30 PM judging | Relay and ElevenLabs judges | SpaceX judges | Fetch judges | Main-track judges. Everyone stays present; it is required [R] ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)) |

#### Common "test it first" checks (run 9:45–11:30 AM; about 15–20 min each)
These are throwaway probes, not project code, so keep them out of the submission repo. The 2026 code-timing rule is unverified [U]. MHacks 14's rules required code written during the event and allowed planning beforehand [R] ([2021 research](/Users/anvaytodkar/Code/mhacks/results/year-research/2021.md)).

| # | Check | Pass bar | Owner |
|---|---|---|---|
| T1 | Download one `ABI-L2-DSRF` file and read Ann Arbor's value (42.28, −83.74) with `xarray` | A plausible W/m² number from a scan less than 30 min old, in under 30 min of work | P2 |
| T2 | Register for WattTime and ask for MISO's CO₂ percentile. If refused, use an Electricity Maps free key for `US-MIDW-MISO`. If that fails, use EIA-930 hourly data | Any live MISO number, with its timestamp. Note how old the data is | P2 |
| T3 | An iOS 26 phone on the team; Relay installed; `npx relaymessenger@latest login` | A logged-in agent you can text | P1 |
| T4 | ASI:One and Agentverse accounts; redeem `MHACKS26` / `MHACKSAV`; mailbox hello-world | ASI:One answers through your @handle | P3 |
| T5 | xAI key; one Grok Imagine call (about $0.04 per image [R] ([pricing](https://docs.x.ai/developers/pricing))) | An image comes back | P2 |
| T6 | Claim the ElevenLabs Creator month; generate one line in the persona voice with emotion tags | It sounds like a character, not a GPS | P1 |
| T7 | Install OneWili from source and `pyfwfinder` on two laptops. One should run Windows or Linux, because of earlier macOS trouble [R] ([FREE-WILi advocate](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/04-free-wili.md)) | Imports work | P4 |
| T8 | **Bring IR targets from your rooms before noon:** an IR-remote fan, an LED strip, a TV or a space heater, with its remote | At least 2 devices whose remotes work | P4 |
| T9 | Five-person reaction test in the hacker line: read each persona's 10-second pitch aloud | 3 of 5 smile *and* can say what it does | P4 |

---
### 1. Clean Hours (sharpened): "Fern" moves your loads to clean hours and flips the switch herself

**One-liner.** You text Fern, a houseplant who lives in Relay. She watches MISO's grid and GOES-19's view of the sky, runs or pauses your IR devices at the right hour, and calls you when it matters. If you ignore her, she does it herself.

**Tracks (Combo A, exact).**
- **Main:** Sustainability.
- **Fun:** Judged by an LLM and Dumbest Idea.
- **Core sponsors:** Relay, SpaceX, Fetch.ai, ElevenLabs (plus the MLH ElevenLabs prize) and FREE-WILi.
- **Optional:** Figma (about 3.5 h). Capital One only as the Green Fund swap-in if the 2 PM FREE-WILi gate fails. Notability only with a free Pro code.

**How each sponsor's tech is genuinely used**
- **Relay.** Fern is the agent people text, call and video-call. The key feature is that she **calls you** when a clean window opens, or when a dirty spike means she paused your heater [R] ([call-a-person](https://docs.relayapp.im/calls/call-a-person.md)). Her portrait and talking/listening loop videos come from the workshop's Grok Imagine steps [R] ([README](https://raw.githubusercontent.com/RelayMessenger/Relay-SDK/main/cookbook/mhacks-workshop/README.md)).
- **SpaceX.**
  - Built in Cursor throughout.
  - Grok Imagine renders Fern's wilt and bloom states.
  - **GOES-19 makes the short-term call.** The ACMC cloud mask (5-minute) and DSR (10-minute) over the region's solar farms give a "cleaner hour coming in about 40 min" nowcast. That breaks ties and fills the gap that grid APIs leave when they publish no free forecast [I].
  - Every decision card carries a provenance line: "GOES-19 ABI, scan 13:10Z."
- **Fetch.ai.** Three role agents: Grid, Planner and Actuator (a local mailbox agent that drives the USB device).
  - The flow in ASI:One: "@cleanhours run my fan and pre-heat when the grid is cleanest tonight" → Form card → **Review card** ("Fan 1:40–2:40 AM, saves ≈X g CO₂ (est.), Confirm / Edit") → the Actuator fires IR at the scheduled time.
  - It covers the bonus items: real-time data, multi-agent, cards, and error handling (a retry when `confirm` fails) [R] ([hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)).
- **ElevenLabs.** Fern's voice on every call through the Relay bridge with Rive lip-sync. She has three emotional registers: chipper, worried, and wilting. Grid-state SFX (a short wind gust for "wind's up") is a second capability [R] ([bridge](https://docs.relayapp.im/calls/elevenlabs.md)).
- **FREE-WILi.**
  - It **learns** the room's IR remotes and **sends** their codes.
  - Its **accelerometer, taped to the fan, confirms** that the fan actually started or stopped. This is closed-loop actuation, which gives the success rate and latency in the eval.
  - Its **screen** is the garden. Update it only when the state changes, because full-image pushes take seconds per frame [R] ([Wattson blog](https://web.archive.org/web/20251110035750/https://docs.freewili.com/blog/wattson/)).
  - Its **A button** means "I'm leaving, run everything clean," and its **speaker** plays Fern's one-liners.
- **Dumbest Idea: Fern's tough-love ladder** (opt-in, 1–1.5 h):
  1. A text: "Grid's on coal. Hold the dryer."
  2. A call: "I'm a fern. I will wilt."
  3. If ignored, she sends IR herself, saying "I asked nicely." The fan goes off and the garden perks up.

**Why it would win (past-winner patterns and judges' remarks)**
- **Same track text, same device, same playful loop.**
  - *Wattson* won 2025 Greenprint **and** Best Use of FREE-WiLi with a pet on a FREE-WiLi that suffers when lights are left on [R] ([Devpost](https://devpost.com/software/wattson-5btsyd)).
  - Clean Hours keeps that loop, a garden instead of a pet, and adds what Wattson lacked: live grid data, an agent, and an actuator.
  - The 2025 Greenprint pool was 15 of 122 projects, mostly dashboards [R] ([filter](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90481)).
- **Load-shifting on screen alone has a ceiling.**
  - In 2024, a load-shifting project (*Dynamic Load Balancing for Energy-Efficient Cloud Computing*) won only an MLH tool prize, not the Sustainability track [R] ([Devpost](https://devpost.com/software/dynamic-load-balancing-for-energy-efficient-cloud-computing)). That track went to *FarmX*, which had a Michigan hook [R] ([Devpost](https://devpost.com/software/farmx-zpw0yq)).
  - Inference: the shifting idea needs a physical action and a measured number to reach the track prize.
- **Text-to-control plus a physical effect won 1st before.**
  - *SunLite* (2021, 1st) was a smart bulb you schedule by texting. Judges called it well-rounded and said they'd use it themselves (closing ceremony, [~24:45](https://www.youtube.com/watch?v=YMbf9pfdGZg&t=1485s)) [R].
  - Fern's text → call → act ladder copies *F.L.U.D.D.* (2021), which texted an alert and escalated to a **phone call** after 15 minutes without a reply [R] ([Devpost](https://devpost.com/software/f-l-u-d-d)).
- **Fetch.**
  - *MobiLens* won 2025 Best Use of Fetch.ai with agents that controlled a smart home [R] ([Devpost](https://devpost.com/software/mobilens)).
  - Only 1 of 48 verified Fetch winners was green [R] ([Fetch advocate](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/01-fetchai-asi-one-agent-challenge.md)), so the theme stands out under the 20% Innovation weight.
- **Voice persona.**
  - *Judy AI* won 2025's fun prize as a voiced Gemini + ElevenLabs companion [R] ([Devpost](https://devpost.com/software/judy-ai-4vc9ah)).
  - ElevenLabs' own rubric rewards agentic depth, emotional inflection and persona prompt work [R] ([Hack the 6ix](https://hackthe6ix2026.devpost.com/)).
  - 0 of 35 ElevenLabs winners were about climate [R] ([ElevenLabs advocate](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/02-elevenlabs.md)).
- **SpaceX.** The most relevant recent SpaceXAI winners are below. Fern's provenance lines and "AI illustration" labels follow their pattern.
  - *WaterFlow* (environmental, satellite imagery, Grok as a careful explainer) [R] ([Devpost](https://devpost.com/software/waterflow-41mrqd)).
  - *NOVA* (rigorous real data) [R] ([Devpost](https://devpost.com/software/nova-hzgjy0)).
- **Format fit.** Three-minute table pitches, judged repeatedly, have been the format since 2023 [R] ([2024 Hacker Guide](http://web.archive.org/web/20250720162056/https://docs.google.com/document/d/1kpIZGN8-MbPODH5jmi3DoAfl-k6LWUxheGCQoeMBP54/edit)). MHacks may also judge pairwise this year [R] ([MDredd](https://github.com/mhacks/MDredd)). A phone ringing and a fan stopping is a one-glance "aha," like *we-Learn*'s jump-to-the-word moment (2020, 2nd) [R] ([Devpost](https://devpost.com/software/we-learn)).

**Architecture / stack** [I]
- The spine service (FastAPI + SQLite).
- The FREE-WILi driver runs as a thread inside the same process, over USB (OneWili).
- The Relay agent is in TypeScript, from the workshop.
- Fetch is three uAgents in a single Python process. Use **separate mailbox registrations, not one `Bureau`**, because Bureau caused 404s for a past team [R] ([Dispatch](https://devpost.com/software/dispatch-tabspl)).
- `xarray` + `h5netcdf` for GOES.
- One static web dashboard, designed in Figma: the satellite window, the grid gauge, the decision log and the garden.

**Build plan (deltas on the common clock)**

| Person | Sat 12–6 PM | Sat 6 PM–Sun 6 AM | Sun 6–11:45 AM |
|---|---|---|---|
| P1 | Workshop persona (Fern); text plus an agent-initiated call | Tough-love ladder; Rive states; "dirty spike" outbound call | Rehearse call timing; record a fallback video |
| P2 | `grid_now` (T2 winner); GOES DSR + ACMC readers; planner | Nowcast tie-breaker; 7-day backtest (naive 7 PM run vs. Clean Hours) | Freeze the numbers into the Devpost |
| P3 | Grid, Planner and Actuator agents; Review card | Retry logic, README, ≥10 interactions, Devpost v1 | Fetch video; Submission Agent |
| P4 | IR learn/send for 2 devices; accelerometer `confirm`; button | Garden screen states (Figma → PNG); dashboard | Pitch; table setup with the QR code |

**Demo script (2:45, Sustainability judge)**
- **0:00–0:20.** "Michigan's grid gets cleaner and dirtier by the hour. Clean Hours moves your plug loads to the clean hours and actually flips the switch." Point at the live counter: "This weekend: N loads shifted, about X g CO₂ avoided (est.)."
- **0:20–1:05.** A judge or teammate texts Fern: "pre-heat my room cheaply and cleanly." Fern replies with the plan. Then the **live decision**: the grid is in its dirty band right now, so Fern **pauses** the "heater" (the fan) and rings the phone. The judge answers and Fern explains in about 10 seconds. The fan stops, the FREE-WILi accelerometer confirms it, and the garden ticks up. This works in either grid state without fast-forwarding the clock. If the grid is clean, she *starts* the load instead.
- **1:05–1:35.** The laptop shows ASI:One with the same intent, the Review card, Confirm, and the device acting. Keep it to 30 seconds for main judges and give it a full minute for Fetch.
- **1:35–2:20.** The tech: a one-slide diagram, then the backtest table (kg CO₂/week, naive vs. ours) and the actuation success rate and latency. One sentence on GOES: "This satellite measured the clouds over the solar farms 4 minutes ago."
- **2:20–2:45.** Fern's closer: ignore her and she switches off the LED strip herself: "I asked nicely." The garden perks up.

**Risks → mitigations**
- **Relay calls don't work on the App Store build.**
  - Evidence: v1.1 lists no calls [R] ([App Store](https://apps.apple.com/us/app/relay-agent-messenger/id6789704419)), and an Oct 2 changelog entry adds a refusal for phones that can't take calls [R] ([changelog](https://docs.relayapp.im/changelog.md)).
  - Mitigation: ask at the Expo and the 1 PM workshop. If calls don't work by 4 PM, switch to Photon and keep everything else.
- **The FREE-WILi is missing or broken.** Decide at the 2 PM gate. Fall back to a simulated device panel plus the Capital One Green Fund (idea 9). *OmniComm* still won FREE-WiLi after its hardware died [R] ([Devpost](https://devpost.com/software/assistive_communicator)).
- **Average vs. marginal intensity.** Use WattTime's marginal percentile for the *decision* and average gCO₂ for the *number*, and say so in Limitations [I].
- **A flat sky** (overcast all weekend). GOES still reports real values, but the nowcast won't change many decisions. Say so; the grid signal carries the decision [I].
- **The persona eats the pitch.** Keep Fern to 15 seconds or less after the impact number for Sustainability judges.

**Test it first (≤2 h)**
1. T1 + T2 + T8 from the common list.
2. **A decision you can see:** pull today's last 24 h of MISO data (T2's source). Pass if the dirtiest and cleanest hours differ by enough that a shifted 1.5 kW load moves a visible number of grams. If the day is flat, lead with the weekly backtest [I].
3. **Paper prototype (20 min):** script Fern's three-step ladder on cards and act it out for 5 hackers (T9). Pass if 3 of 5 laugh *and* can say "it runs stuff when the grid is clean."
4. **At 1–2 PM with a device:** learn one IR code, send it, and see the accelerometer vibration change when the fan starts. Pass if this works within 30 minutes.

---

### 2. T-Minus Laundry: Mission Control for your chores

**One-liner.** Every big load (heater, fan, AC, dryer nudge) is treated as a crewed launch.
- A Review card lists **Launch Commit Criteria**: Grid (MISO marginal percentile), Sky (GOES-19 cloud fraction over the solar farms) and Range (you replied).
- A flight director calls you at T-10.
- The FREE-WILi is a launch console: a countdown on the screen, LEDs turning green, the A button to commit, and IR fires at T-0.
- When the grid spikes, it **scrubs**: "Grid rule violated, recycling to T-minus 3 hours."

**Tracks (Combo A, exact).**
- **Main:** Sustainability.
- **Fun:** Judged by an LLM and Dumbest Idea.
- **Core sponsors:** Relay, SpaceX, Fetch.ai, ElevenLabs (+MLH) and FREE-WILi.
- **Optional:** Figma. Capital One only as the swap-in. Notability only with a free code.

**How each sponsor is used.** This is the same engine as idea 1; only the skin changes.
- **Relay:** "Flight" calls you with a GO/NO-GO poll.
- **SpaceX:** GOES-19 is a real commit criterion. For flavor, the scrub messages quote real launch weather-rule names from the Launch Library 2 API [R] ([LL2](https://ll.thespacedevs.com/2.2.0/launch/upcoming/)). LL2 allows 15 requests per hour per IP, so cache it [R] ([throttle](https://ll.thespacedevs.com/2.3.0/api-throttle/)). Grok Imagine makes a **mission patch** for every load, labeled as art.
- **Fetch:** "@tminus launch laundry and pre-cool tonight" → a Review card listing the commit criteria → GO → the Actuator fires at T-0.
- **ElevenLabs:** a calm flight-director voice, plus a countdown and liftoff SFX.
- **FREE-WILi:** the console. IR at T-0, and the accelerometer confirms "liftoff" when the fan's vibration appears.

**Why it would win**
- **Absurd premise, real engine.** That is the archetype MHacks rewarded twice in 2025:
  - *Artificial Sandwich Intelligence* won the Grand Award [R] ([Devpost](https://devpost.com/software/artificial-sandwich-intelligence)).
  - *Judy AI* won the fun prize [R] ([Devpost](https://devpost.com/software/judy-ai-4vc9ah)).
- **The judge is SpaceX.** A launch-ops frame speaks their language, and SpaceXAI's own Grokathon scored usefulness and craft/"beauty" [R] ([Grokathon](https://spacexai-grokathon.devpost.com/)). Inference: a polished console with real commit data reads as craft, not as garnish.
- **A crowd-drawing demo.** A countdown with LEDs and a liftoff sound pulls people to the table. *MotionSurfer*'s team credited the attention it got from judges (2023, Game Dev) [R] ([Devpost](https://devpost.com/software/motionsurfer)).
- **Physical plus voice plus several sponsors in one coherent story.** *EscapeMate* won the 2024 Interactive Media track with a Raspberry Pi prop and a voice companion built on three sponsor tools [R] ([Devpost](https://devpost.com/software/escapemate)).

**Architecture.** The spine, plus a `commit_criteria()` view and an LL2 cache file.

**Build plan.** The same as idea 1, except:
- P1 writes the flight-director script instead of Fern's ladder (about the same 1–1.5 h).
- P4 builds the console screen: countdown digits and GO tiles, about 1 h more than garden states.
- P2 adds the LL2 cache (0.5 h).

**Demo script (2:40)**
- **0:00–0:20.** The impact number first, then: "We run your chores like SpaceX runs launches."
- **0:20–1:10.** The judge says "launch the space heater." The console shows Grid **NO-GO** (88th percentile). The call comes in: "Flight, we are scrubbing for grid." The judge hears the recycle time.
- **1:10–1:40.** Flip to a criteria set that's GO (say a clean window or the pre-heat limit), then T-10, T-0: the IR fires, the fan starts, the accelerometer registers "liftoff," and the mission patch lands in Relay.
- **1:40–2:20.** The backtest, the actuation log, and GOES provenance.
- **2:20–2:40.** The patch gallery: "STS-Laundry-7."

**Risks → mitigations**
- **Theme drift.** Sustainability judges may see a gimmick. Lead with the number, and keep "launch" as the interface, not the premise [I].
- **SpaceX garnish risk.** At DivHacks, *Julia's Time Machine* took the Grand Prize but **not** SpaceXAI, because it didn't use Grok Imagine/Voice for real [R] ([Devpost](https://devpost.com/software/julia-s-time-machine)). Here GOES must decide GO/NO-GO, not just decorate.
- The other risks are the same as idea 1.

**Test it first (≤2 h)**
1. T1, T2, T8.
2. **Reaction test.** Pitch both skins, Fern and Flight, to 5 people each (T9). Pick the one with more "I'd use that." Run it again with a SpaceX rep at the 11:30 Expo if possible.
3. **Pull LL2 once.** Pass if at least 3 real weather-rule names are available to quote. Otherwise write the scrub lines from the grid and GOES only.

---

### 3. Cloudbreak: satellite nowcasting of clean power

**One-liner.** Grid APIs report what already happened. GOES-19 sees the clouds coming. Cloudbreak tracks cloud gaps moving over the region's utility solar farms in the 5-minute clear-sky mask and predicts a solar surge 30–60 minutes ahead. It then calls you to start the big load at the surge, and the FREE-WILi fires it.

**Tracks (Combo A, exact).**
- **Main:** Sustainability.
- **Fun:** Judged by an LLM and Dumbest Idea.
- **Core sponsors:** Relay, SpaceX, Fetch.ai, ElevenLabs (+MLH) and FREE-WILi.
- **Optional:** Figma. Capital One only as the swap-in. Notability only with a free code.

**How each sponsor is used**
- **SpaceX: the strongest space-data case in Combo A.** The satellite *is* the forecaster.
  - Read ACMC (5-minute) frames over plant locations from EIA-860, the public generator inventory [I: not yet opened] ([EIA-860](https://www.eia.gov/electricity/data/eia860/)).
  - Estimate cloud motion between frames with OpenCV optical flow, and extrapolate 30–60 minutes ahead.
  - Weight by DSR.
  - Grok Imagine renders the persona.
  - The dashboard shows the GeoColor window with an overlay of predicted gaps.
- **Relay:** "Storm-chaser" Sunny calls you: "Gap's 35 minutes out over Lake Michigan, get the kettle ready."
- **Fetch:**
  - "@cloudbreak run my dehumidifier in the next solar surge" → Review card with a predicted window and a confidence → the Actuator fires.
  - A **Data agent** and a **Nowcast agent** talk to each other, which is real multi-agent work.
- **ElevenLabs:** the over-caffeinated storm-chaser voice; its tension rises as the gap approaches.
- **FREE-WILi:** a handheld "sun radar." The screen shows the incoming gap as a sweep, the LEDs ramp up as it approaches, IR fires at the surge, and the accelerometer confirms.

**Why it would win**
- **Innovation and Technical Complexity.**
  - *DECO.ai* (2023, 1st) applied research-grade technique to a familiar problem [R] ([Devpost](https://devpost.com/software/deco-ai)).
  - *V²/R* (2024 Grand Prize) won with a core the team built itself rather than API calls [R] ([Devpost](https://devpost.com/software/v-r)).
  - A homemade satellite nowcaster with a published backtest is that kind of core.
- **Satellite data for solar has won before:** *SolarVista* (2024, MLH prize) [R] ([Devpost](https://devpost.com/software/solarvista)) and *WaterFlow* (SpaceXAI, Fall 2026) [R] ([Devpost](https://devpost.com/software/waterflow-41mrqd)). Cloudbreak goes further by using the satellite live to make a decision.
- **Judged by an LLM** rewards numbers over adjectives [R] ([LLM-judge advocate](/Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/06-fun-judged-by-an-llm.md)). "GOES solar index vs. reported MISO solar MWh, r = …, over N hours" is exactly that.

**Architecture.** The spine, plus:
- `nowcast.py`: ACMC frames → plant-pixel cloud fraction → optical-flow extrapolation;
- `validate.py`: the GOES index vs. EIA-930 MISO solar generation (fuel type SUN).

A cheaper fallback, if the projection math stalls: use DSR at plant pixels (already on a lat/lon grid) without the motion forecast.

**Build plan.** P2 is fully on the nowcaster. **P3 takes `grid_now` and the planner** from P2 in addition to Fetch, which puts P3 over capacity, so cut the Fetch multi-agent split to two agents [I]. P1 and P4 are the same as idea 1, with storm-chaser lines and a radar screen.

| Person | Sat 12–6 PM | Sat 6 PM–Sun 6 AM | Sun |
|---|---|---|---|
| P2 | ACMC fixed-grid → lat/lon (pyproj with the file's projection attributes); plant pixel list | Optical flow; 30/60-min forecast; validation run | Freeze the r and MAE figures |

**Demo script (2:50)**
- **0:00–0:20.** "Grid data tells you the past. This satellite tells you the next hour."
- **0:20–1:10.** The GeoColor window plus the predicted gap arrival. The radar on the FREE-WILi sweeps. Sunny calls: the gap reaches the plants in N minutes.
- **1:10–1:40.** A teammate triggers "run on surge," and the planner holds the load until the surge.
- **1:40–2:30.** The validation chart, honestly labeled: the hours where it was right and the hours where it was wrong.
- **2:30–2:50.** Sunny's sign-off.

**Risks → mitigations**
- **The October solar share in MISO may be too small** for the CO₂ effect to show [I]. Report it honestly. The project's claim is forecasting skill, with CO₂ second.
- **The projection math and the 26 MB DSR files eat P2's night** (about 26 MB per DSR file, per the final debate, round 2). Use the DSR-only fallback by midnight.
- **Clouds over Michigan are not the whole MISO footprint.** Weight plants by capacity and list the limitation [I].
- **A demo during a fully clear or fully overcast sky.** Show the replay of today's validation with a visible "replay" label.

**Test it first (≤2 h)**
1. **ACMC to lat/lon (60 min, P2).** Open one ACMC file and convert scan angles to lat/lon using its `goes_imager_projection` attributes. Pass if a pixel near Ann Arbor flips between clear and cloudy across frames in a way that matches today's GeoColor image.
2. **Validation feasibility (30 min).** Pull 3 days of EIA-930 MISO SUN data. Pass if the hourly data exists and is fresher than 24 h. If it fails, validate against DSR alone and say so.
3. **Plant list (15 min).** Pass if at least 20 utility solar plants with coordinates are found in MISO states in EIA-860.

**If test 1 fails by 11:30, build idea 1 and keep Cloudbreak as a stretch layer for P2 [I].**

---
### 4. Hang Time: the washer snitch that saves the whole dryer cycle

**One-liner.** A FREE-WILi clipped to the washer feels the cycle end. The agent, "Tumble," a needy dryer with abandonment issues, calls you then.
- **If GOES-19 shows strong sun on your block for the next few hours:** "Hang them. I'll be fine. I'm *fine*."
- **If not:** it books the dryer for the cleanest hour tonight and calls you then.
- Meanwhile it uses IR to run a fan at a drying rack.
- Unlike shifting, this **avoids** a load.

**Tracks (Combo A, exact).**
- **Main:** Sustainability.
- **Fun:** Judged by an LLM and Dumbest Idea.
- **Core sponsors:** Relay, SpaceX, Fetch.ai, ElevenLabs (+MLH) and FREE-WILi.
- **Optional:** Figma. Capital One only as the swap-in. Notability only with a free code.

**How each sponsor is used**
- **FREE-WILi:** accelerometer streaming (`enable_motion_stream`) [V] ([sensors.py](https://github.com/freewili/onewili/blob/main/python/onewili/menus/sensors.py)) feeds a cycle detector. IR drives the fan at the rack, and the screen counts down to "dry."
- **SpaceX:** GOES-19 DSR plus a 5-minute cloud trend over your address decides between hanging and drying. Grok Imagine draws Tumble's moods.
- **Relay:** a "wash done" call with the decision, plus a text with a dry-by time.
- **Fetch:** "@hangtime watch my laundry" → Form card (outdoor line? rack? dryer?) → Review → the Actuator arms the sensor and schedules the fan and the dryer reminder.
- **ElevenLabs:** Tumble's melodrama, with escalating sighs as SFX.

**Why it would win**
- **The accelerometer is FREE-WILi's most common winning feature.** It powered three winners [R] ([FREE-WILi advocate](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/04-free-wili.md)):
  - *Gestura* (MHacks 2025) [R] ([Devpost](https://devpost.com/software/gestura-9oaugq));
  - *thereMINI* (SpartaHack X) ([Devpost](https://devpost.com/software/theremini));
  - *Agent Unblind* (Hack Dearborn) ([Devpost](https://devpost.com/software/agent-unblind)).
- **A chore every judge does.** The most specific 2021 praise was first-person, "I would use this" (*SunLite*, closing ceremony [~24:45](https://www.youtube.com/watch?v=YMbf9pfdGZg&t=1485s)) [R]. Laundry is that kind of pain.
- **"Show one quantified impact number"** was the Sustainability advocate's lever #3 [R] ([advocate](/Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/01-main-sustainability.md)). An avoided dryer cycle is a bigger and simpler number than a shifted one [I].

**Architecture.** The spine, plus `cycle_detect()`: the rolling variance of the acceleration magnitude with on/off hysteresis. Add one small test file, because this is a parser of noisy data [I].

**Build plan.** P4 builds the detector and tapes the FREE-WILi to the stand-in "washer" (a desk fan's base vibrates). The other roles follow idea 1, with Tumble's lines for P1.

**Demo script (2:30)**
- **0:00–0:20.** "The dryer is one of the biggest plug loads in a student house [I; quote your unit's label]. On sunny days, you don't need it."
- **0:20–1:10.** Stop the stand-in washer. The FREE-WILi detects that the cycle ended, and Tumble calls: GOES says sun until 3:40 PM.
- **1:10–1:40.** In ASI:One, the Review card arms tomorrow's watch.
- **1:40–2:15.** The detector's accuracy on 20 recorded on/off cycles, and the GOES provenance.
- **2:15–2:30.** Tumble's closing sob.

**Risks → mitigations**
- **Dorm residents can't line-dry outdoors** [I]. Target off-campus houses, and treat an indoor rack plus the fan as the default action.
- **An October overcast streak.** The decision flips to "dryer at the clean hour," which is still real. Show both branches.
- **Weaker Fetch action.** It's a reminder plus a fan, not a big load. Make the IR fan and the calendar write the "real action."

**Test it first (≤2 h)**
1. **Detector feasibility before a device is available (30 min).** Record a phone's accelerometer (any sensor-logger app) on a running washer or a desk fan. Pass if on and off are separable by eye in the variance plot.
2. **User test.** Ask 5 off-campus students whether they have a place to hang laundry. Pass if 3 of 5 say yes. Otherwise pick another idea.
3. T1 for the address pixel.

---

### 5. Sweater Weather: your room as a heat battery

**One-liner.** It's October in Michigan, and the space heaters are coming out.
- The agent **pre-heats** with an IR-remote heater during clean or sunny windows, then **coasts** through the dirty evening peak.
- It turns the heater off when GOES-19 says the sun is about to warm your south window.
- "Grandma Thermostat" calls you: "Put on a sweater, sweetheart."

**Tracks (Combo A, exact).**
- **Main:** Sustainability.
- **Fun:** Judged by an LLM and Dumbest Idea.
- **Core sponsors:** Relay, SpaceX, Fetch.ai, ElevenLabs (+MLH) and FREE-WILi.
- **Optional:** Figma. Capital One only as the swap-in. Notability only with a free code.

**How each sponsor is used**
- **FREE-WILi:** IR controls the heater.
  - Temperature comes from OneWili's `enable_env_stream` if the loaner model supports it [V menu exists, model support U] ([sensors.py](https://github.com/freewili/onewili/blob/main/python/onewili/menus/sensors.py)). Otherwise use an I²C temperature sensor on the FREE-WILi's GPIO, from the MLH lab if it has one [U].
  - The screen shows a thermometer that knits a sweater as the "battery" drains.
- **SpaceX:** GOES-19 **DSR** (solar gain) and **LSTC** (land surface temperature, hourly [V] ([S3](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-LSTC/2026/276/))) feed the pre-heat plan.
- **Relay:** Grandma calls before the peak: "I warmed it up at 2 PM when the wind was blowing. Don't touch that dial."
- **Fetch:** "@sweater keep my room at 68 °F by 10 PM, cheapest-carbon way" → Review card with the pre-heat schedule → the Actuator runs it.
- **ElevenLabs:** a warm, judgmental grandmother voice designed with Voice Design [R] ([ElevenLabs advocate, sketch C](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/02-elevenlabs.md)).

**Why it would win**
- **A talking device with emotional range.** *DoortectiveAI* (Bitcamp 2026, MLH ElevenLabs) switched its tone by context [R] ([Devpost](https://devpost.com/software/doortective)), and talking devices were 17% of ElevenLabs winners [R] ([ElevenLabs advocate](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/02-elevenlabs.md)).
- **A local, seasonal, relatable problem.** In 2021, *F.L.U.D.D.* won on SE Michigan basement floods and *Water Monitor* on the Great Lakes [R] ([F.L.U.D.D.](https://devpost.com/software/f-l-u-d-d), [Water Monitor](https://devpost.com/software/water-monitor-96zalt)). Ann Arbor's A2ZERO plan gives a local hook [R] ([a2gov](https://www.a2gov.org/sustainability-innovations-home/carbon-neutrality-home/)).
- **Heating is the biggest plug load in this set** (space heaters are typically about 1.5 kW nameplate [I; read the label]), so the impact number is the largest.

**Architecture.** The spine, plus a one-parameter room model (the temperature decay rate, fitted from 30 minutes of logged data). Mark it `# ponytail: first-order model; add a solar-gain term only if the fit is poor` [I].

**Build plan.** P2 fits the room model with a 30-minute log during the evening. P4 handles the sensor and heater IR. P1 builds Grandma. P3 builds Fetch, as in idea 1.

**Demo script (2:30).** Use a fan or LED strip as the "heater" stand-in, because a 1.5 kW heater at a crowded table is a safety risk [I].
- **0:00–0:20.** The number: "kWh moved off the evening peak, and grams avoided."
- **0:20–1:00.** The plan graph: pre-heat, coast, temperature band.
- **1:00–1:40.** Grandma's call, then IR off and the accelerometer confirming.
- **1:40–2:15.** The model fit, and the backtest on today's grid.
- **2:15–2:30.** "Put on a sweater."

**Risks → mitigations**
- **A dorm room's thermal mass may hold only 30–60 minutes of shift** [I]. Measure it and report it.
- **No IR heater on the team.** Use an IR fan as a stand-in and frame it for AC in summer.
- **The temperature sensor is uncertain on the OG.** That's the deciding test below.

**Test it first (≤2 h)**
1. **Does a teammate own an IR-remote space heater?** Bring it, or drop this idea.
2. **At the 1 PM workshop:** does `enable_env_stream` return temperature on the loaner? If not, does the MLH lab have an I²C temperature sensor? If both fail, drop the idea.
3. **Check venue policy on space heaters at the help desk** [U].

---

### 6. Count Kilowatt: the "last one out" sweep for shared rooms

**One-liner.** In co-op houses, lab rooms and club offices, nobody turns things off.
- Each member texts the Count (one Relay chat each).
- When the last person says they're leaving, or presses the FREE-WILi's big button at the door, the Count sweeps every learned IR device off.
- He calls the last person out if something was left on.
- If GOES-19 shows bright daylight over the building while the lights are on, he mocks the room: "Six hundred watts per square meter of free light, and you burn a bulb?"

**Tracks (Combo A, exact).**
- **Main:** Sustainability.
- **Fun:** Judged by an LLM and Dumbest Idea.
- **Core sponsors:** Relay, SpaceX, Fetch.ai, ElevenLabs (+MLH) and FREE-WILi.
- **Optional:** Figma. Capital One only as the swap-in. Notability only with a free code.

**How each sponsor is used**
- **Relay:** one chat per member, because a Relay group holds only one human plus up to six agents [R] ([group chats](https://docs.relayapp.im/chats/group-chats.md)). The Count tracks who's still in from "leaving" texts and calls the last one out.
- **FREE-WILi:**
  - It is the doorway console: the A button is "I'm out," and the screen shows the room's devices as candles being snuffed.
  - IR sends the codes for the sweep.
  - Optionally, **IR receive logs every remote press**, a cheap usage sensor, via OneWili's `enable_ir_stream` [V] ([ir.py](https://github.com/freewili/onewili/blob/main/python/onewili/menus/ir.py)).
- **SpaceX:** GOES-19 DSR over the building pixel gives the "daylight harvesting" nudge. Grok Imagine renders vampire portraits of the room's worst offenders.
- **Fetch:** "@countkw close up the lab when the last of us leaves" → Review card listing the devices and members → the sweep is armed.
- **ElevenLabs:** the Count's theatrical voice, with SFX (a coffin creak when the sweep runs).

**Why it would win**
- **Humor with a real use, finished.** *MBathroom* (2025) won an MLH AI prize with a comic campus app [R] ([Devpost](https://devpost.com/software/mbathrooms)). Judges remember personas (*Judy AI*, 2025).
- **The theme is timed for October and Halloween** [I]. Make the name memorable. In 2021 a judge mixed up two water projects on stage [R] ([closing ~21:08](https://www.youtube.com/watch?v=YMbf9pfdGZg&t=1268s)).
- **Wattson's lights-on idea, extended from one person to a shared room** [R] ([Wattson](https://devpost.com/software/wattson-5btsyd)).

**Architecture.** The spine, plus a `presence` table built from "in/out" texts. No location polling: Relay location is one-to-one and limited to one request per minute [R] ([location](https://docs.relayapp.im/chats/location.md)).

**Build plan.** The same roles as idea 1. P1 builds the multi-member presence logic, which needs 2–3 Relay accounts for testing (about 1.5 h more than idea 1). P4 builds the door-console screen.

**Demo script (2:30).** Three teammates "leave" by texting the Count. The last one gets a call, the LED strip and fan go dark, the accelerometer confirms, and the dashboard shows kWh saved this weekend. Close with the GOES daylight roast.

**Risks → mitigations**
- **IR "off" usually leaves TVs in standby, so this is not true phantom-load removal** [I]. Frame it as devices left **on**. True outlet cutting would need a 433 MHz remote outlet driven by the FREE-WILi sub-GHz radio. `packet_send` exists [V], but replaying outlet codes is unverified [U]. Treat that as a stretch.
- **Multi-human testing needs several iOS 26 phones.** Confirm at T3 how many teammates have one.

**Test it first (≤2 h)**
1. **Count the iOS 26 phones on the team.** At least 2 are needed for a credible multi-member demo.
2. **Pick a real shared room** (a club office or co-op). Ask 3 members whether they'd text "leaving." Pass if 2 of 3 say yes.
3. **Stretch:** if anyone owns a 433 MHz remote-outlet kit, bring it to the 1 PM FREE-WILi session and ask whether `radio.packet_send` can replay it.

---

### 7. Sun Budget: the Digital Garden, literally

**One-liner.** Each day your room gets an energy allowance equal to the sunlight GOES-19 measured on your roof today: a notional 1 m² panel [I] times the integrated DSR.
- Every appliance run through the FREE-WILi spends from the budget ("the remote is the meter").
- The garden on the device screen grows while you're under budget and wilts when you overspend.
- The gardener calls you at 9 PM with the day's verdict.

**Tracks (Combo A, exact).**
- **Main:** Sustainability.
- **Fun:** Judged by an LLM and Dumbest Idea.
- **Core sponsors:** Relay, SpaceX, Fetch.ai, ElevenLabs (+MLH) and FREE-WILi.
- **Optional:** Figma, and **Capital One, which fits this idea more naturally than the others**: overspending moves a user-set "sun fine" from checking into a Nessie Green Fund. Nessie is HTTPS only and starts empty, so seed it and namespace your data [R] ([Nessie advocate](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/12-capital-one-nessie.md)). Notability only with a free code.

**How each sponsor is used**
- **SpaceX:** GOES-19 DSR *is* the currency, and Grok Imagine renders the garden's growth stages.
- **FREE-WILi:** IR runs every appliance and accumulates runtime. The screen is the garden, and the A button means "I'll wait for tomorrow's sun."
- **Relay:** the nightly verdict call, plus "you have 0.4 kWh of sunshine left; dryer or space heater?"
- **Fetch:** "@sunbudget plan tonight within today's sunshine" → Review card → schedule → the Actuator runs it.
- **ElevenLabs:** a nature-documentary narrator for the garden. The Eleven Music/SFX bed is a second capability [R] ([ElevenLabs advocate, sketch A](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/02-elevenlabs.md)).

**Why it would win**
- **It matches the event's own theme**, "Digital Garden / build something that grows" [R] ([mhacks.org](https://www.mhacks.org/)), which counts toward the Adherence to Theme criterion [R] ([Devpost](https://mhacks-2026.devpost.com/)).
- **Gamified sustainability on a FREE-WiLi screen won Greenprint in 2025** (*Wattson*) [R]. *LORAX* (2020) also placed among Wolfram's Top 30 for gamified green actions [R] ([Devpost](https://devpost.com/software/lorax-luring-others-to-retain-our-abode-extensively)).

**Architecture.** The spine, plus `budget()` = ∫DSR × area × efficiency [I], with a stated assumption. Compare it with `spent()` = Σ runtime × watts.

**Build plan.** The same as idea 1. P2 builds the budget integrator. P4 builds garden art with more states (about 1 h more). Capital One, if added, goes to P3 after midnight (about 4 h [R]).

**Demo script (2:30)**
- **0:00–0:20.** "Today the sun gave this room 1.9 kWh."
- **0:20–1:10.** Run the heater stand-in and watch the budget drain and the garden wilt. The gardener calls.
- **1:10–1:40.** ASI:One plans the rest of the night within the budget.
- **1:40–2:15.** The math and its assumptions.
- **2:15–2:30.** The narrator's closing line.

**Risks → mitigations**
- **"Budget = sunlight" is a metaphor, not physics** [I]. Say so in Limitations, and keep the grid-carbon number as the real impact metric.
- **The Capital One "sun fine" can read as gimmicky to Nessie judges.** It needs real writes plus a read-back, or it shouldn't be entered.

**Test it first (≤2 h)**
1. T1, then integrate yesterday's DSR for the pixel. Pass if it yields a number a student can understand in kWh.
2. **Reaction test (T9) on the line "your room can only spend today's sunshine."** Pass if 3 of 5 get it on the first try.

---
### 8. Overpass (sharpened), the Combo B runner-up: the satellites watching your sky, on call

**When to build it.** Build Overpass only if the debate's branch conditions hit: **SpaceXAI says only orbit or mission data counts**, or there are **no FREE-WILi loaners** at the Expo (final debate, round 2, §5).

**One-liner.** Overpass watches NASA FIRMS fire detections from each satellite near places you care about. It propagates the orbits of the satellites that made those detections, so it can say which one looks next and when. It calls you in Relay when a new detection lands.

**Tracks (Combo B).**
- **Main:** Sustainability.
- **Fun:** Judged by an LLM and Dumbest Idea.
- **Core sponsors:** Relay, SpaceX, Fetch.ai and ElevenLabs (+MLH).
- **Optional:** Figma (the live globe), and **Capital One as a parametric payout**: a detection within X km of an insured address triggers a Nessie deposit, the app reads the balance back, and Relay calls the user. Build the payout only if the core works end to end by midnight. Notability only with a free code.

**How each sponsor is used**
- **SpaceX: unambiguous space data.**
  - Per-satellite VIIRS CSVs (keyless) [R] ([NOAA-20 24 h CSV](https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_USA_contiguous_and_Hawaii_24h.csv)).
  - CelesTrak weather-group TLEs, downloaded once per cycle and cached [R] ([CelesTrak](https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=json)), propagated with SGP4 via satellite.js [R] ([npm](https://registry.npmjs.org/satellite.js/latest)).
  - Grok Imagine makes clearly labeled "pass postcards."
- **Relay:** text the watcher, video-call it with the live globe as its camera, and it calls you on a new detection [R] ([Relay advocate](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/11-relay-interactive-agents.md)).
- **Fetch:** "@overpass watch my parents' place" → Review card → the watch is created, and an alert email or calendar hold is written. ASI:One can't push, so Relay carries the proactive alerts [R] ([Fetch advocate](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/01-fetchai-asi-one-agent-challenge.md)).
- **ElevenLabs:** the call voice.
- **Climate framing.** An emissions estimate: fire radiative power × 0.368 kg of biomass per MJ (Wooster et al., as used in [Kaiser et al. 2012](https://bg.copernicus.org/articles/9/527/2012/bg-9-527-2012.pdf)), multiplied by emission factors ([Andreae 2019](https://acp.copernicus.org/articles/19/8523/2019/)). Label it order-of-magnitude [R].
- **Dumbest Idea: "Wave at NOAA-21"** (fun rep, round 1).
  - Opt-in. A minute before a pass, the agent calls: "Go outside and wave."
  - It then texts a Grok Imagine "satellite selfie" labeled AI ILLUSTRATION, next to the single gray 375 m pixel VIIRS actually recorded [R] ([Earthdata FIRMS](https://www.earthdata.nasa.gov/data/tools/firms)).
  - The punchline: "You're about four-millionths of a pixel."
  - Joke about satellites only, never about fires or victims.

**Why it would win**
- **SpaceXAI's recent winners were rigorous real-data products:** *WaterFlow* (environmental, satellite) [R] ([Devpost](https://devpost.com/software/waterflow-41mrqd)) and *NOVA* [R] ([Devpost](https://devpost.com/software/nova-hzgjy0)).
- **Adaptation projects have won sustainability prizes elsewhere:** *SkySplat* [R] ([Devpost](https://devpost.com/software/skysplat)) and *Chilladelphia* [R] ([Devpost](https://devpost.com/software/chilladelphia)).
- **A local-hazard alert that escalates to a call won at MHacks before:** *F.L.U.D.D.*, 2021 [R] ([Devpost](https://devpost.com/software/f-l-u-d-d)).
- **Fetch's winners lean toward high-stakes domains** (about 17 of 48 were health, emergency or accessibility) [R] ([Fetch advocate](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/01-fetchai-asi-one-agent-challenge.md)).
- **For Capital One, a climate-risk money feature** follows the pattern of *InsureFire / Embers* (LA Hacks 2025 FinTech) [R] ([Devpost](https://devpost.com/software/insurefire)).

**Architecture.** The same spine, without FREE-WILi.
- Tools: `fires_near`, `next_look` (SGP4), `explain_detection`, `create_watch`, `notify`.
- A Figma-designed globe in the browser.

**Build plan**
- **P1:** Relay persona, calls and video.
- **P2:** FIRMS ingest and the SGP4 `next_look`. Validate predicted passes against real detection timestamps.
- **P3:** Fetch agents and the write-up.
- **P4:** the globe UI, Figma and the pitch.
- **P3, after midnight:** the Capital One payout, about 4 h [R].

**Demo script (2:45)**
- **0:00–0:20.** Climate framing and the emissions estimate first. This is the Adherence to Theme fix.
- **0:20–1:20.** The judge texts "anything burning near X?" The globe answers and names the satellite and its next pass. A new detection triggers a call.
- **1:20–1:50.** In ASI:One, the watch is created and the email is sent.
- **1:50–2:30.** The eval: predicted vs. actual pass times, and grounded vs. ungrounded answers.
- **2:30–2:45.** The wave gag.

**Risks → mitigations**
- **Adaptation reads weaker than mitigation** against "rethink energy, climate, and resource systems" [R] ([Tracks](https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b)). Lead with the emissions number.
- **Michigan's detections today are small:** 27 / 22 / 10 across the three VIIRS satellites, none high-confidence, with a maximum of 7.2 MW (final debate, round 2, from the FIRMS CSVs). Demo live data from anywhere in the US, and say so.
- **The FIRMS area API showed outage notices** [R] ([FIRMS API](https://firms.modaps.eosdis.nasa.gov/api/)). Use the keyless CSVs and cache them.

**Test it first (≤2 h)**
1. Pull the three VIIRS CSVs and one CelesTrak file (20 min).
2. **Wave-gag check:** compute the passes over Ann Arbor for **Sun 12:30–2:30 PM**. If none falls in the window, use a labeled replay mode.
3. **At the 11:30 Expo**, ask SpaceXAI whether FIRMS plus orbits counts.

---

### 9. Clean Hours Lite + Green Fund, the Combo B fallback for idea 1

**When to build it.** Only if the team **committed to idea 1 and then the 2 PM FREE-WILi gate failed**. Stay on the design rather than redesigning mid-hack (final debate, round 2 table).

**One-liner.** It's idea 1's agent, persona, data and Fetch flow, with a different "hands" and a Nessie fund:
- **Hands:** a USB fan or LED strip whose port power the laptop toggles. `uhubctl` works only on hubs with per-port power switching [I/U]. If that fails, use a clearly labeled simulated device panel.
- **Green Fund:** every shifted load moves a user-set pledge into a **Capital One Nessie "Green Fund"** savings account, and the agent reads the balance back on calls.

**Tracks (Combo B).**
- **Main:** Sustainability.
- **Fun:** Judged by an LLM and Dumbest Idea.
- **Core sponsors:** Relay, SpaceX, Fetch.ai and ElevenLabs (+MLH).
- **Optional:** Figma, Capital One (the Green Fund, which needs a read *and* a write, about 4 h [R] ([Nessie advocate](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/12-capital-one-nessie.md))) and Notability (free code only).

**How each sponsor is used**
- Relay, SpaceX, Fetch and ElevenLabs are used as in idea 1.
- **Nessie:**
  - `POST /customers/{id}/accounts` creates the Green Fund.
  - Transfers or deposits go in on every shift.
  - A `GET` provides the call's balance line.
  - Seed your own data, because sandboxes start empty, and every write is visible to other teams through `/enterprise`. Use fake data only [R] ([Nessie advocate](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/12-capital-one-nessie.md)).

**Why it would win**
- **A clear framing with an honest gap can still win:**
  - *Ventura* took 2025 Overdrive despite failed auth and LLM integration [R] ([Devpost](https://devpost.com/software/ventura)).
  - *Sportable* placed 3rd in 2020 after cutting its broken model from the demo [R] ([Devpost](https://devpost.com/software/sportable)).
- **Nessie used both ways has precedent:** *ZenStock* won Capital One at MHacks 16 (2023) using Nessie [R] ([Devpost](https://devpost.com/software/zenstock)).

**Build plan.** The same as idea 1, except that P4 switches from FREE-WILi to the `uhubctl` hands and then the Green Fund, starting at 2 PM.

**Demo script.** The same as idea 1. The physical beat is the USB fan stopping. The closing call line becomes "Green Fund is at $4.25."

**Risks → mitigations**
- **It loses the main-track "physical" edge.** Lead with the number and the call.
- **Capital One is off-domain.** Keep it out of the main-track pitch.

**Test it first**
1. Run `uhubctl` on a team laptop with any USB hub (15 min). Pass if a USB LED turns off.
2. Get a Nessie key and run a seed → create account → deposit → read-back script (30 min).

Run both checks before 2 PM, so the fallback is ready if the gate fails.

---

### Top 3, ranked

**1. Clean Hours (sharpened), idea 1.** It has the best expected value across every prize pool the team is entering.
- **Main track.** It is the only design whose impact number is CO₂ avoided by **its own action**, shown on a device the judge watches. That fits the published Adherence to Theme criterion [R] ([Devpost](https://mhacks-2026.devpost.com/)) and the *Wattson* pattern that won this exact track text in 2025 [R] ([Devpost](https://devpost.com/software/wattson-5btsyd)).
- **Sponsors.** All five core sponsors are native rather than bolted on.
- **Risk is already mapped.** The debate scoped it at about 22 sponsor-specific hours, or 25.5 h with Figma. It has fallbacks for each of the three biggest risks: Photon, idea 9, and dropping SpaceX without a redesign.
- **What this file adds over the debate's version:**
  - GOES-19 replaces the stale NASA POWER feed, and it now makes a live short-term decision [V] ([S3](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-ACMC/2026/276/)).
  - Accelerometer **closed-loop confirmation** turns "command sent" into a measured success rate. That helps the LLM judge and Fetch's error-handling bonus.
  - A marginal signal drives the decision and average intensity drives the number, with the gap stated honestly.
  - A "pause now / run now" demo works in any grid state without faking the clock.
  - The remote doubles as the meter.

**2. T-Minus Laundry, idea 2.** It is the same engine (roughly 90% shared build [I]) in a louder skin.
- **Upside.** More presentation with the Dumbest Idea, SpaceX, Relay and ElevenLabs judges, who are SpaceX's own people in one case. Absurd-premise-on-real-engine is MHacks' proven 2025 archetype (*ASI* and *Judy AI*).
- **Downside.** Slightly more theme-drift risk with Sustainability judges.
- **Rank it second, not as a rival.** The team can decide "Fern or Flight" from the T9 reaction test and the Expo conversation, as late as **6 PM**, at a cost of about 1–2 h of persona work.

**3. Cloudbreak, idea 3.** It is the strongest Innovation and Technical Complexity story and the best SpaceX case available within Combo A: the satellite *is* the forecaster. It also gives the LLM judge a validation number (*DECO.ai* and *V²/R* both won with cores the teams built themselves [R]). Its risk sits with one person, P2, and it **layers onto idea 1**. So the best plan is idea 1 + Cloudbreak as P2's stretch, gated at midnight. If test 1 fails, the GOES DSR tie-breaker from idea 1 remains.

**Why the others aren't in the top 3**
- **Hang Time (4):** the action is a nudge, and line-drying depends on housing.
- **Sweater Weather (5):** it depends on someone owning an IR heater and on temperature sensing on the loaner. A heater can't be demoed at the table.
- **Count Kilowatt (6):** it needs several iOS 26 phones, and IR-off isn't true phantom-load removal.
- **Sun Budget (7):** the budget is a metaphor, not physics. Its garden is best used as idea 1's screen.
- **Ideas 8–9:** only under their branch conditions.

### Decision rules for today (one line each)
- **11:30 Expo.**
  - SpaceXAI accepts GOES Earth-observation data (or states no rule against it) **and** FREE-WILi has loaners → **idea 1**, with the skin chosen by T9.
  - SpaceXAI says only orbit or mission data counts, **or** there are no loaners → **idea 8** (final debate, round 2).
- **2 PM.** The FREE-WILi smoke test fails after committing to idea 1 → **idea 9**. Don't redesign.
- **4 PM.**
  - Relay calls don't work → move the surface to Photon and keep everything else.
  - SpaceXAI rejects GOES → drop SpaceX and don't redesign (final debate).
- **6 PM.**
  - ASI:One must work end to end with one real action, or cut Fetch.
  - Last call on Fern vs. Flight.
- **Midnight.** Core working end to end? If not, cut the joke and untick Dumbest Idea. Also decide whether the Cloudbreak stretch and Capital One go ahead.

### Key sources (beyond those inline)
- MHacks 2026: [Devpost](https://mhacks-2026.devpost.com/) · [Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af) · [Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5) · [Tracks text](https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b) · [schedule](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365) · [mhacks.org](https://www.mhacks.org/)
- Team research: [`year-research/`](/Users/anvaytodkar/Code/mhacks/results/year-research/) (2020–2025) · [main/fun verdict](/Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md) · [sponsor verdict](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/13-debate-and-verdict.md) · advocate files under [`results/`](/Users/anvaytodkar/Code/mhacks/results/). The final three-way debate exists only in this run's prompt transcript and is cited as "final debate."
- Checked today [V]: [GOES-19 DSRF](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-DSRF/2026/276/) · [GOES-19 ACMC](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-ACMC/2026/276/) · [GOES-19 LSTC](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-LSTC/2026/276/) · [GeoColor UMV](https://cdn.star.nesdis.noaa.gov/GOES19/ABI/SECTOR/umv/GEOCOLOR/latest.jpg) · [WattTime plans](https://watttime.org/docs-dev/data-plans/) · [MISO data APIs](https://www.misoenergy.org/markets-and-operations/rtdataapis) · [OneWili menus](https://github.com/freewili/onewili/tree/main/python/onewili/menus)

# Pivot Ideas — Sponsor-stack maximizer

## Prompt given (excerpt)
> You are the Sponsor-stack maximizer. Maximize expected prize value from GENUINE sponsor use: one coherent project that naturally earns Relay, SpaceX (real space data + Grok), Fetch.ai, ElevenLabs and FREE-WILi (plus optional SpacetimeDB/Figma/Neon/Capital One/Photon if they fit without checkbox-stuffing). Read every sponsor file and 13-debate-and-verdict.md; sponsor judges see through token integrations.

*Written Sat Oct 3, 2026, about 6 PM EDT. Hacking ends 12:00 PM Sunday. Tags: **[V]** I checked it tonight at the linked source. **[F]** from a team research file (which carries its own citations). **[I]** my inference or estimate. Every probability and score is [I].*

---

## TL;DR

| | Idea | Main track | Genuine sponsor stack | Win | Non-niche | 18 h | Wow | Sponsor fit | Reuse |
|---|---|---|---|---|---|---|---|---|---|
| **1 (top pick)** | **Fern on Call**: a satellite-watching houseplant that checks on people who live alone during heat and smoke emergencies, through a FREE-WILi "pot" on their table and a Relay video call to their family | Sustainability | Relay, ElevenLabs, FREE-WILi, SpaceX, Fetch.ai (+ FinchNode, Figma optional) | 7 | 8 | 6 | 8 | **9** | **8** |
| 2 | **Ember Fund**: wildfire evacuation cash that pays out the moment two satellites agree there is fire near your home | FinTech (or Sustainability) | Capital One, SpaceX, Fetch.ai (Payment Protocol), Relay, ElevenLabs | 5 | 7 | 5 | 6 | 8 | 5 |
| 3 | **Thirty**: a sideline lightning siren driven by a camera in geostationary orbit | Beyond the Code (Hardware) | FREE-WILi, SpaceX, Relay, ElevenLabs, Fetch.ai | 5 | 5 | 6 | 8 | 8 | 4 |

**Top pick: Fern on Call.** It is the only idea where all five target sponsors are load-bearing *and* the problem is big: heat killed 2,325 Americans in 2023, a record and 117% more than in 1999 ([JAMA](https://jamanetwork.com/journals/jama/fullarticle/2822854); [AP via energy.gov](https://www.energy.gov/documents/098-associated-press-2023-set-record-us-heat-deaths-ap-analysis-findspdf)), and 16.2 million older Americans (28%) live alone ([ACL 2023 Profile of Older Americans](https://acl.gov/sites/default/files/Profile%20of%20OA/ACL_ProfileOlderAmericans2023_508.pdf)). It reuses almost all of the Fern character work; her **wilted** mood is literally what heat does to a plant. And there is a **live Extreme Heat Warning right now** over Santa Clarita, Ventura, the Inland Empire, Orange and San Diego counties through Oct 7 [V] ([NWS alerts API](https://api.weather.gov/alerts/active)), so the demo runs on today's data, not a replay.

---

## 0. Where the past-years research lives (start here)

Everything below cites these files. They are the team's six-year MHacks record, and they are worth five minutes before you pick.

| File | What is in it | The part most useful tonight |
|---|---|---|
| [`results/SUMMARY.md`](/Users/anvaytodkar/Code/mhacks/results/SUMMARY.md) → **"Lessons from six years of MHacks winners"** and **"Cross-check"** | Winners at a glance (2020–2025), ten repeating patterns, how MHacks judges (3-min table pitch, sponsors judge in parallel, possible MDredd pairwise judging), and a pattern-by-pattern check of the old plan | Patterns 2 (one project rarely wins two prizes), 3 (sponsor winners match the sponsor's own product), 5 (a technical core you built) and 6 (agents that close the loop) |
| [`year-research/2025.md`](/Users/anvaytodkar/Code/mhacks/results/year-research/2025.md) | Same venue, same rubric. 122 projects, 30 winners. Wattson (Greenprint + FREE-WiLi), MobiLens (Fetch Best Use), Gestura (FREE-WiLi), Judy AI (fun prize, ElevenLabs) | Fetch.ai's weighted rubric (25/20/20/20/15) and its hard requirements; FREE-WiLi had 5 entrants and 2 winners |
| [`year-research/2024.md`](/Users/anvaytodkar/Code/mhacks/results/year-research/2024.md) | 132 projects, 30 prizes to 30 different projects. V²/R and FocusFlow (self-built cores). Cartesia's TTS rubric. Two FREE-WILi winners | "Voice must be central" (Cartesia), "does it demo live" (BoundaryML), the 3-minute pitch format |
| [`year-research/2023.md`](/Users/anvaytodkar/Code/mhacks/results/year-research/2023.md) | MHacks 16 relaunch. DECO.ai, Terminal.AI, ZenStock (Nessie) | 14 of 24 winners already used an LLM; grounding in real data is what stood out |
| [`year-research/2022.md`](/Users/anvaytodkar/Code/mhacks/results/year-research/2022.md) | Confirms there was no 2022 event | Nothing to copy |
| [`year-research/2021.md`](/Users/anvaytodkar/Code/mhacks/results/year-research/2021.md) | SunLite (1st), F.L.U.D.D (text → phone-call escalation), Cosmic Cleaner (space + servos). The only judge quotes in six years | "Would definitely use this", "well-rounded", and a judge praising a demo video shot in real life |
| [`year-research/2020.md`](/Users/anvaytodkar/Code/mhacks/results/year-research/2020.md) | Online, inflated badges. Dystic, Sportable | Honest scoping still placed (Sportable cut its broken model and said so) |
| [`sponsor-tracks/13-debate-and-verdict.md`](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/13-debate-and-verdict.md) | All 12 sponsors ranked, EV table, stacking and conflicts | Fit table §4.2: Relay ⟂ Photon, Capital One ⟂ FinchNode, SpacetimeDB needs a multi-user core |
| [`main-and-fun-tracks/07-debate-and-verdict.md`](/Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md) | Main-track pool sizes, the FinTech reality check | Sustainability drew 15 of 122 in 2025; FinTech is probably 15–25%; AI about 35–50% |

---

## 1. What six years of winners say about stacking sponsors

1. **One project rarely wins two prizes in person.** 2024: 30 prizes went to 30 different projects. 2025: only Wattson and MobiLens won two of 30. MHacks 16: only Terminal.AI and ALERT ([F] [SUMMARY](/Users/anvaytodkar/Code/mhacks/results/SUMMARY.md) pattern 2; [2024](/Users/anvaytodkar/Code/mhacks/results/year-research/2024.md)). **So a summed sponsor EV is an upper bound, not an expectation.** The sponsor-maximizer's job is to buy many *genuine* lottery tickets whose work also strengthens the main demo, not to promise five wins.
2. **The one proven MHacks double is Sustainability + FREE-WILi, with a character on the screen.** Wattson (2025) won Greenprint and Best Use of FREE-WiLi with a virtual pet that loses health when lights stay on ([Devpost](https://devpost.com/software/wattson-5btsyd); [F] [2025](/Users/anvaytodkar/Code/mhacks/results/year-research/2025.md)).
3. **Sponsor winners use the sponsor's tech as the product.** Terminal.AI won Warp with a terminal tool; ZenStock used Nessie; the UM ITS winners used ITS's own data ([F] [2023](/Users/anvaytodkar/Code/mhacks/results/year-research/2023.md)). At DivHacks 2026 the Grand Prize winner opted into SpaceXAI with Gemini imagery and did **not** win it; NOVA won with rigorous real data and Grok voice serving an underserved user ([F] [SpaceX file](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/07-spacex-make-it-legendary.md)).
4. **FREE-WILi winners make the device the product, usually for accessibility.** Gestura (wrist mouse for arthritis), OmniComm and thereMINI elsewhere; ElevenLabs lines played through the FREE-WILi speaker won FREE-WiLi at GrizzHacks 8 ([F] [FREE-WILi file](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/04-free-wili.md)). The 13-verdict calls a "satellite pass beeper" a gimmick; the device has to do the core job.
5. **Fetch.ai winners close the loop, and a third of them are health/emergency/accessibility.** MobiLens (2025 Best Use, $1,250) was caregiver alerts + smart-home control + agents. Only 1 of 48 Fetch winners was green ([F] [Fetch file](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/01-fetchai-asi-one-agent-challenge.md)).
6. **Text, then call, then act has won at MHacks.** F.L.U.D.D (2021, Google Cloud 1st) texted a flood alert and escalated to a phone call after 15 minutes, for SE Michigan basements ([F] [2021](/Users/anvaytodkar/Code/mhacks/results/year-research/2021.md)).
7. **Voice has to be central.** Cartesia's 2024 MHacks rubric scored "how central and impactful text-to-speech is"; ElevenLabs' own rubric (Hack the 6ix) scores "Agentic Depth" beyond TTS; 23% of 35 ElevenLabs winners were accessibility projects and 2 were phone-call agents ([F] [2024](/Users/anvaytodkar/Code/mhacks/results/year-research/2024.md), [ElevenLabs file](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/02-elevenlabs.md)).
8. **Judges reward a problem they personally feel.** 2021's closing ceremony: 1st-place SunLite was "so well-rounded", and the presenter "would definitely use this" ([F] [2021](/Users/anvaytodkar/Code/mhacks/results/year-research/2021.md)). Every judge has a parent or grandparent.
9. **A named user, a statistic and a local hook** appear in nearly every winner (NurseNotes' 41%, FarmX's Michigan farms, F.L.U.D.D's SE Michigan floods) ([F] SUMMARY pattern 4).
10. **Top prizes go to a technical core the team built** (ASI's trained policy, V²/R's solver, DECO.ai's NeRF pipeline), and grounded LLMs beat raw chat (OneVote, Pinpoint Ai) ([F] SUMMARY pattern 5; [2023](/Users/anvaytodkar/Code/mhacks/results/year-research/2023.md)).
11. **Physical demos take MHacks' own top awards** (2025: Grand Award, Greenprint, Portal; 2021 and MHacks 15 1st places), and the 2021 MLH judge singled out a demo video "shot in real life" ([F] [2025](/Users/anvaytodkar/Code/mhacks/results/year-research/2025.md), [2021](/Users/anvaytodkar/Code/mhacks/results/year-research/2021.md)).

---

## 2. What I verified tonight

| Check | Result |
|---|---|
| GOES-19 lightning (GLM L2 LCFA) on public S3 | **Live.** 173 twenty-second files in the 21 UTC hour. The newest covered 21:58:00–21:58:20 UTC and was created 21:58:21.6 UTC. I parsed it: **755 flashes in 20 s**, 678 over South/Central America, 14 over CONUS, 0 over the Great Lakes [V] ([bucket listing](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=GLM-L2-LCFA/2026/276/21/)) |
| GOES-19 land surface temperature, smoke, fire, aerosol, cloud | ABI-L2-**LSTC** (hourly), **ADPC** (aerosol/smoke detection), **FDCC** (fire), AODC, ACMC (every 5 min) all posted for hour 21 UTC today [V] ([bucket](https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-LSTC/2026/276/21/)). **GOES-18** (West, better view of California) has LSTC and ADPC too [V] ([bucket](https://noaa-goes18.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-LSTC/2026/276/21/)). GOES-18 SoCal GeoColor returns 200 [V] ([psw](https://cdn.star.nesdis.noaa.gov/GOES18/ABI/SECTOR/psw/GEOCOLOR/1200x1200.jpg)) |
| Archived GOES fire data (for backtests) | GOES-18 and GOES-16 FDCC files exist for Jan 7, 2025 (the LA fires) [V] ([bucket](https://noaa-goes18.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-FDCC/2025/007/18/)) |
| NWS active alerts (keyless) | 414 active. **8 Extreme Heat Warnings** (Santa Clarita Valley, Ventura County, Santa Barbara County, the Inland Empire, Orange and San Diego counties; some run to Oct 7 8 PM PDT), **6 Heat Advisories**, 1 Air Quality Alert (Imperial County), 47 Flood Warnings [V] ([api.weather.gov](https://api.weather.gov/alerts/active)) |
| NASA FIRMS NOAA-20 24 h CSV (keyless) | 200, 2,007 rows [V] ([CSV](https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_USA_contiguous_and_Hawaii_24h.csv)) |
| Relay | App Store build is **still v1.1** (Sep 20), minimum iOS 26.0, and its notes don't mention calls. The Oct 2 changelog refuses a call with `422`/`1005` when none of the person's devices can take calls [V] ([lookup](https://itunes.apple.com/lookup?id=6789704419), [changelog](https://docs.relayapp.im/changelog.md)). Whatever the 1 PM workshop told you about calls governs every idea below |
| FREE-WILi OG on the new OneWili API | The Python menus include `audio.play_audio_file`, `audio.speak`, `audio.tone`, `gui.show_fwi_image`, `gui.show_text`, `gui.set_led_color`, and an IR menu [V] ([audio.py](https://github.com/freewili/onewili/blob/main/python/onewili/menus/audio.py), [gui.py](https://github.com/freewili/onewili/blob/main/python/onewili/menus/gui.py), [menus](https://github.com/freewili/onewili/tree/main/python/onewili/menus)). I did not run them on hardware |
| Novelty | Generic "AI calls an elderly person to check in" projects already exist at online hackathons (a "Neighborhood Safety Check-In Agent" in Agents for Humans; SunnyCalls in Voice & Video AI Agents) [V] ([gallery](https://agentsforhumans.devpost.com/project-gallery?page=2), [gallery](https://voice-video-ai-agents.devpost.com/project-gallery)). FIRMS wildfire-alert projects are common (e.g. [Signet](https://devpost.com/software/signet-3jhw9i); whole [wildfire hackathons](https://big-earth-hackathon-2022.devpost.com/)). I found **no** Devpost project using GOES GLM lightning [V, absence in one search] |

---

## 3. Idea 1 (top pick): **Fern on Call**

**One-liner.** Fern is a houseplant with a phone line who watches the sky through GOES. When a heat wave or wildfire smoke reaches someone who lives alone, her pot on their table lights up and asks them to check in; if they don't, she video-calls their family in Relay, in her own voice, and works down the list until a human has checked.

**Tagline for the pitch:** *"She wilts before you do."*

### 3.1 Problem and user
- **The problem.** Heat is the deadliest US weather hazard and it is getting worse: 2,325 heat-related deaths in 2023, the most on record, up 117% since 1999 ([JAMA](https://jamanetwork.com/journals/jama/fullarticle/2822854); [AP](https://www.energy.gov/documents/098-associated-press-2023-set-record-us-heat-deaths-ap-analysis-findspdf)). The people most at risk are older adults on heat-sensitizing medications who live alone and don't notice they are overheating. CDC's clinician guidance lists diuretics, beta blockers, ACE inhibitors/ARBs and some antidepressants as raising heat risk ([CDC guidance mirror](https://restoredcdc.org/www.cdc.gov/heat-health/hcp/clinical-guidance/heat-and-medications-guidance-for-clinicians.html)).
- **Who.** 16.2 million Americans 65+ live alone; 42% of women 75+ do ([ACL 2023 Profile](https://acl.gov/sites/default/files/Profile%20of%20OA/ACL_ProfileOlderAmericans2023_508.pdf)). Two users:
  - **"June", 81, Santa Clarita** (fictional, label her so): no new apps, maybe no smartphone. Her endpoint is the FREE-WILi pot.
  - **Her daughter "Maya", a U-M student in Ann Arbor**, 2,000 miles away. Her endpoints are Relay (calls) and ASI:One (setup).
- **Local hook.** Maya is in Ann Arbor; June is under tonight's real Extreme Heat Warning. Every judge has a "June."
- **Why it is not niche.** It is not about one appliance or one grid. It is about every climate-driven hazard that kills quietly (heat first; smoke, cold and storms through the same pipeline) for a population of 16 million.
- **Why it is Sustainability.** The track text is "rethink energy, climate, and resource systems." Heat waves are the climate impact that already kills the most Americans; this is climate resilience. Say it in the first 20 seconds, because the 13-verdict warns adaptation reads weaker than mitigation unless framed ([F] [13-verdict §4.1](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/13-debate-and-verdict.md)). The event theme, "Digital Garden," is a plant that grows when you're safe and wilts when you're not.

### 3.2 How it works
1. **Setup in ASI:One (Fetch.ai).** Maya types: `@fernoncall watch over my mom at <address>; she's 81, lives alone, takes furosemide and metoprolol; call me first, then her neighbor Ana.` A **Planner** agent replies with a **Review card**: hazards watched, check-in times, escalation ladder, quiet hours. Confirm → a **Dispatcher** agent registers the watch, emails the escalation contacts a "you're on June's list" note, and sends Maya a calendar hold for the daily check-in. Real actions, inside ASI:One.
2. **Sky (SpaceX real space data).** Every 5–60 minutes the **Sky** agent pulls, for June's location: NWS active alerts (authoritative trigger), **GOES-18/19 land-surface temperature** at her block (hourly, 2 km), **GOES aerosol/smoke detection** (5 min), and **FIRMS + GOES fire detections** within 50 km. It turns these into a risk tier (green/amber/red), and every number carries its satellite, scan time and posting time.
3. **The pot (FREE-WILi).** The FREE-WILi sits on June's table (in a terracotta pot as a prop). Amber or red tier:
   - the screen shows Fern's **wilted** face (`show_fwi_image`) and big text ("104°F today. Drink water."),
   - the 7 LEDs glow amber or red (`set_led_color`),
   - the speaker plays a Fern line in her ElevenLabs voice (`play_audio_file`),
   - **the green button = "I'm OK."** Pressed → Fern blooms on screen and the family gets a "June checked in at 2:14 PM" text in Relay.
4. **No check-in within N minutes → Relay video call to Maya.** Fern's wilted talking/listening loops are the camera; her voice is ElevenLabs; her brain is Grok with tools. *"[sighs] It's 104 in Santa Clarita and GOES-18 says your mom's block hit 131°F at the surface an hour ago. She hasn't pressed her button in 40 minutes. Want me to call Ana next door?"* Maya says yes → Fern texts or calls Ana (the next contact) and logs who confirmed. *(The 104°F and 131°F in these lines are illustrative; at runtime every number comes from the tools, per the persona's "numbers only from DATA" rule.)*
5. **Nobody answers →** the ladder ends at "call 911 yourself" guidance to Maya, never an automated 911 call (say this out loud: it is a safety design choice).
6. **Optional FinchNode (meds-aware tier).** With consent, read the synthetic `polypharmacy-senior` record (14 meds incl. furosemide, metoprolol, lisinopril, sertraline [F] [FinchNode file](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/10-finchnode-healthtech.md)) and raise the tier one step when CDC's heat-sensitizing classes are present. Fern says *why* ("she's on a diuretic, CDC flags those in heat"), never "change your medication."

### 3.3 Sponsor tracks and exactly how each is earned

| Sponsor | Genuine use (the checkbox test: would that sponsor's judge see through it?) | Hours [I] |
|---|---|---|
| **Relay** | The family-facing product: text Fern, and **Fern calls you** (agent-initiated video call) when June doesn't check in. Uses calls, video (Fern's loops as the agent camera), and the escalation through several people. Passes: it is Relay's headline feature doing the core job | ≈4 |
| **ElevenLabs** | Voice *is* the accessibility interface for an 81-year-old: the designed **Fern voice** (Voice Design), `eleven_v4_turbo` with audio tags on calls, **Speech-to-Speech** for the lip-synced hero clips (already built), the same voice through the FREE-WILi speaker, and optionally Scribe STT so June can just say "I'm fine." Passes the "beyond simple TTS" rubric | ≈1.5 (mostly done) |
| **FREE-WILi** | The device is the product for someone who won't install an app: screen face, LED alert ring, check-in button, speaker voice. Matches the assistive, device-as-product pattern of Gestura/OmniComm and the ElevenLabs-through-speaker GrizzHacks winner | ≈5 |
| **SpaceX "Make it Legendary"** | **Real space data goes in:** GOES-18/19 LST, smoke and fire products plus FIRMS decide the tier, with provenance on every number. **Grok Imagine:** Fern's face and all call loops (already generated with `grok-imagine-image-2.0` / `grok-imagine-video-1.5`). **Grok** is the brain on texts and calls. **Cursor** for all new code from now on, with `.cursor/rules` and Agent screenshots. Hedge if SpaceXAI wanted more than Earth observation: a 1-hour "which satellite is watching June right now" card (CelesTrak GOES-18/19 + NOAA-20/21 next pass) | ≈4 |
| **Fetch.ai ASI:One** | The caregiver's whole setup flow happens in ASI:One: Planner, Sky and Dispatcher uAgents (multi-agent), a **Review card**, real actions (emails, calendar, and the Dispatcher can trigger the Relay call itself: "Confirm → Maya's phone rings"). Chat Protocol, Agentverse, README badges, video, Submission Agent | ≈7 |
| *FinchNode (optional)* | Meds-aware heat tier from the keyless demo API, with consent shown. It is the only bolt-on that changes a decision; the 13-verdict says pick at most one domain bolt-on, and this is it | ≈2 |
| *Figma (optional)* | Caregiver dashboard + the 320×240 pot screens as one design system | ≈3.5 |
| Skip | **Capital One** (no money in this story), **SpacetimeDB** (one household is not a multi-user core; a neighbor "block watch" board would be stuffing at this hour), **Neon** (SQLite is enough), **Photon** (fallback surface only, if Relay calls fail), **Notability** (only with a free Pro code) | — |

**Fun tracks:** Judged by an LLM (a rubric-shaped Devpost with the measured results in §3.7). Not Dumbest Idea or Useless AI: this is a safety product.

### 3.4 Why it can win: past evidence
- **The mechanism has won here before.** F.L.U.D.D (2021, Google Cloud 1st): local hazard → text → phone call after 15 minutes ([F] [2021](/Users/anvaytodkar/Code/mhacks/results/year-research/2021.md)). Fern adds the satellite trigger, a physical endpoint and a character.
- **Fetch's own MHacks winner is the same shape.** MobiLens (2025 Best Use of Fetch.ai): accessibility, caregiver alerts, agents reachable through ASI:One ([F] [2025](/Users/anvaytodkar/Code/mhacks/results/year-research/2025.md)). About 17 of 48 Fetch winners are health/emergency/accessibility; a climate one is rare ([F] [Fetch file](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/01-fetchai-asi-one-agent-challenge.md)).
- **The FREE-WILi double has a template.** Wattson won Greenprint + FREE-WiLi with a character on the device screen ([Devpost](https://devpost.com/software/wattson-5btsyd)). Fern on the pot screen is the same proven form, aimed at a person's safety instead of a lights-off game.
- **Character + voice wins at MHacks.** Judy AI, a voiced ElevenLabs companion, took the 2025 fun prize ([F] [2025](/Users/anvaytodkar/Code/mhacks/results/year-research/2025.md)).
- **Judges reward what they'd personally use.** "I would definitely use this" (2021, 1st place) ([F] [2021](/Users/anvaytodkar/Code/mhacks/results/year-research/2021.md)).
- **SpaceX judges reward rigor for an underserved user.** NOVA (DivHacks SpaceXAI) and WaterFlow (HopHacks SpaceXAI, environmental satellite data) ([F] [13-verdict](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/13-debate-and-verdict.md)).

### 3.5 Novelty and overlap check
- **Generic elder check-in calls are not new** (online-hackathon projects above; commercial companions exist). **Do not pitch "an AI that calls Grandma."** Pitch the three things those don't have: (1) **hazard-triggered by satellites**, so it only escalates when the sky says it is dangerous; (2) **a no-app physical endpoint** for the person at risk; (3) **escalation across people** with a human confirming at the end.
- **Wattson overlap** is surface-level (character on a FREE-WILi screen). Say the difference: Wattson was a game for the user; Fern is a safety line between two people.
- **Not a Clean Hours re-skin:** different user, problem, data, action and success metric. Only the character carries over.

### 3.6 What it reuses (exactly)
- **Fern persona kit:** `fern/assets/fern_{normal,blooming,wilted}.png`, the six HD call loops in `fern/assets/video_hd/`, the saved ElevenLabs voice `Fern (MHacks 2026)` (`XnLFOJOtoPqkoo60ohxA`), `fern/voice/make_voice.py` (TTS + gate), `fern/voice/lipsync.py` (Grok performs → ElevenLabs STS), and the TypeScript Relay camera player in `fern/README.md`. The **wilted** mood becomes "heat/smoke," **blooming** becomes "checked in," **normal** is idle.
- **Persona prompt** (`fern/persona.md` §2): keep the voice rules, the "numbers only from DATA" rule and the safety section; replace the dryer/ladder text with the check-in ladder.
- **GOES pipeline research:** the S3 listing pattern and fixed-grid reprojection (`SUMMARY.md` §4.3) apply unchanged to LSTC/ADPC/FDCC; only the variable names differ.
- **Clean Hours architecture:** one Python `brain` with a frozen tool contract, an asyncio scheduler, SQLite, a Node Relay process, mailbox uAgents, a FREE-WILi driver with a simulator. Reused as-is.
- **Whatever the 1 PM Relay, 2 PM Fetch and FREE-WILi bring-up produced** (scaffold, `@handle`, LEDs blinking).
- **xAI credit:** none needed for the core. New lines can use the free loop-switch method; budget about 4 lip-synced hero lines at roughly $1–1.5 each (per `fern/voice/final/README.md`).

### 3.7 New work and hours (≈32 person-hours core, +5.5 optional)

| Owner | Work | Hours |
|---|---|---|
| P2 Sky | `sky.py` for LSTC/ADPC/FDCC point values at a lat/lon (reuse the reprojection), NWS alerts, FIRMS within 50 km, risk tier with a written rule table | 5 |
| P2/P3 | Escalation state machine (check-in window → call contact 1 → contact 2 → guidance), SQLite log, REST tools: `hazard_now`, `checkin`, `escalate`, `status` | 3 |
| P1 Relay | Workshop agent → Fern with tools; agent-initiated call to the next contact; mood switch from tier; 6–8 new lines rendered (TTS free; 3–4 lip-synced) | 5.5 |
| P4 FREE-WILi | OneWili: convert 3 mood screens to `.fwi`, LED tiers, button → `POST /checkin`, upload 6 audio lines, `play_audio_file`; a simulator with the same interface | 5 |
| P3 Fetch | Planner/Sky/Dispatcher uAgents (pinned `uagents==0.25.5`), Review card, email + calendar action, trigger-a-call action, README badges, Submission Agent | 7 |
| P4/P2 | One-page caregiver dashboard (map, satellite tile, tier, check-in log) | 2.5 |
| All | Devpost (rubric-shaped), 3–5 min video (Fetch requires it; shoot the pot in real life), rehearsal | 4 |
| *optional* | FinchNode meds tier 2; Figma 3.5 | 5.5 |

**"What we built ourselves" (the technical core judges want):** the satellite-to-block hazard engine (geostationary reprojection, quality flags, freshness rules) plus the escalation engine, with a measured table: for each of today's live heat-warning counties, the GOES LST at the warned addresses vs. the county's coolest blocks, detection-to-alert latency (GOES scan → posted → Fern speaks), and check-in → call timing in rehearsal runs. Report whatever the numbers are.

### 3.8 Build plan from now (Sat ~6 PM → Sun 12 PM)

| Time | Gate |
|---|---|
| **7:30 PM** | FREE-WILi on OneWili: an image on screen, one LED, one audio file plays, a button press reaches the laptop. If it fails, keep going with the simulator and decide again at 10 PM |
| **8:30 PM** | Relay: Fern answers a text and **calls a teammate's iOS 26 phone**. If calls still fail, the escalation goes out as a Relay voice note + text, and Photon becomes the backup surface. Don't redesign |
| **9:30 PM** | GOES-18 LST value for a Santa Clarita lat/lon, with scan and posted times |
| **10:00 PM** | Fetch: `@handle` answers in ASI:One with a Review card |
| **Midnight** | End to end: alert → pot → no press → Relay call → second contact. If not, cut FinchNode and Figma |
| **6 AM** | Freeze UI and lines. Film the pot and the phone ringing, in real life |
| **11:30 AM** | Fetch video + Submission Agent (every teammate joined), Devpost submitted |

### 3.9 Demo moment (3 minutes at the table)
- **0:00** "Heat killed 2,325 Americans in 2023, a record. 16 million older Americans live alone. Right now there's an Extreme Heat Warning over Santa Clarita." Dashboard: the NWS warning and the GOES-18 view, "imaged N minutes ago."
- **0:30** The pot on the table goes amber; Fern's wilted face; her voice: *"It's going to be hot today, June. Have some water, and press the green button so I know you're okay."*
- **1:00** Nobody presses (shortened timer, say so). **The judge's phone rings** (judge texted Fern from the QR at the start; otherwise a teammate's phone): Fern on video, wilted, with the real numbers. The judge says "call Ana" → the second phone on the table buzzes.
- **1:45** Someone presses the green button → Fern **blooms** on the pot and on the call: *"She's okay. I'll stop worrying. Mostly."*
- **2:15** ASI:One: the Review card Maya confirmed, and the email it sent.
- **2:40** "Every number came from a satellite or NWS with a timestamp; Fern never calls 911 for you; she never guesses."

### 3.10 Data sources (all checked tonight unless marked)
NWS alerts API [V]; GOES-19 and GOES-18 LSTC/ADPC/FDCC on public S3 [V]; FIRMS 24 h CSV [V]; GOES-18 GeoColor [V]; Relay call docs ([call a person](https://docs.relayapp.im/calls/call-a-person.md)) [F]; OneWili audio/gui/IR menus [V, code only]; FinchNode keyless demo API `polypharmacy-senior` [F]; Fetch hackpack requirements [F].

### 3.11 Risks and fallbacks
| Risk | Fallback |
|---|---|
| Relay calls don't work on the public build (still v1.1) | Relay text + voice note escalation; Photon iMessage as the backup surface. Same brain |
| Reads as "health," not Sustainability | Open with climate: heat deaths doubling, heat is the deadliest climate hazard; Fern's garden = people kept safe. If organizers say adaptation doesn't count, AI main is the fallback (crowded) |
| FREE-WILi firmware/library or audio volume | Simulator on screen (OmniComm still won FREE-WiLi with hardware dead before judging [F]); laptop speaker |
| GOES LST is clear-sky only and is *surface*, not air, temperature | Use NWS for the heat number and satellites for "which blocks run hottest"; say it in Limitations |
| Judge's phone isn't iOS 26 | Call a teammate's phone on the table, mirrored |
| Liability optics | Never automates 911, never gives medication advice; "stop" ends everything; synthetic data only |

**Scores:** win 7 · non-niche 8 · feasibility 6 · demo wow 8 · sponsor fit 9 · reuse 8.

---

## 4. Idea 2: **Ember Fund** — satellite-triggered evacuation cash

**One-liner.** A wildfire emergency fund for renters and low-income households that pays evacuation cash into their account the moment two independent satellites agree there's fire near their home, and calls them to say the money is there.

### 4.1 Problem and user
- More than 4.5 million US structures are at high or extreme wildfire risk, over 2 million households in California alone ([Verisk](https://www.verisk.com/blog/growing-wildfire-exposure-feeds-need-to-grasp-risk-factors/), via search summary). Insurance and aid pay weeks or months later; evacuation costs (gas, a motel, a pet kennel) are due *tonight*.
- **Anticipatory cash works.** GiveDirectly sent $105 to over 4,600 people in Nigeria *before* a flood peak using AI forecasts, and reports food insecurity dropped 90% ([GiveDirectly](https://www.givedirectly.org/flood-forecast-ai); [Rest of World](https://restofworld.org/2025/google-flood-hub-cash-aid/)). Ember Fund does that for wildfire, with satellites as the trigger.
- **User:** a renter in the wildland-urban interface with no renters insurance, plus a community fund or mutual-aid group that wants to pay *before* the fire.

### 4.2 How it works
1. **Trigger engine (the "we built it" core).** GOES-18/19 FDC (every 5 min) gives the first sighting; a VIIRS detection from Suomi NPP, NOAA-20 or NOAA-21 (FIRMS) within R km confirms it. CelesTrak + SGP4 tells the member when the confirming satellite passes next ("NOAA-21 looks again in 47 min"). Two satellites must agree before money moves.
2. **Capital One Nessie.** Seed the fund's pool account and members' checking accounts; on trigger, write a transfer/deposit from pool to member, read the balance back, badge every Nessie number.
3. **Relay + ElevenLabs.** Fern calls the member: *"Two satellites saw fire 4 km from you. $300 is in your account now."* (Fern re-scripted: ferns are among the first plants back after a fire.)
4. **Fetch.ai.** Members join and donors contribute in ASI:One through the **Payment Protocol** (Stripe test mode), which is named inside Fetch's 20% "Use of Fetch.ai Technology" criterion ([F] [Fetch file](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/01-fetchai-asi-one-agent-challenge.md)); a Review card shows the payout rule.
5. **Backtest** on the Jan 7, 2025 Los Angeles fires using archived GOES-18/16 FDC (verified present on S3 tonight): when the trigger would have fired. That is the measured table for Judged by an LLM.

### 4.3 Tracks
- **Main: FinTech** ("faster, fairer, more accessible"); Sustainability is the alternative. FinTech's pool is likely 15–25% vs Sustainability's 10–20% ([F] [07-verdict](/Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md)).
- **Fun:** Judged by an LLM.
- **Sponsors:** Capital One (core: read + write, pool and payouts), SpaceX (the trigger *is* satellite data; Grok brain, Fern's Grok Imagine face; Cursor), Fetch.ai (Payment Protocol + Review card + multi-agent), Relay (the payout call), ElevenLabs (voice on calls). **FREE-WILi: honestly no.** A "go-bag beacon" would be stuffing.

### 4.4 Why it can win
- The main/fun verdict said no advocate found a coherent finance + real-space-data project; the 13-verdict found exactly this parametric payout as the bridge ([F] [13-verdict §2.3](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/13-debate-and-verdict.md)).
- Money-track winners pair finance with another domain; InsureFire/Embers (wildfire valuables) won LA Hacks 2025 FinTech ([F] [07-verdict §4](/Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md)).
- Capital One winners read *and* write Nessie (LoadCheck), and none of 55 recent Nessie entries was climate-themed ([F] [Capital One file](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/12-capital-one-nessie.md)). ZenStock won MHacks 16's Capital One prize with Nessie ([F] [2023](/Users/anvaytodkar/Code/mhacks/results/year-research/2023.md)).

### 4.5 Overlap, reuse, hours, risks
- **Overlap:** FIRMS wildfire alerts are a crowded genre (Signet, wildfire hackathons). The novelty has to be the *two-satellite payout rule* and the money arriving before the fire, not the alert.
- **Reuses:** Overpass research and data checks (FIRMS, CelesTrak), the GOES fixed-grid code, Fern's voice/face (re-scripted), the Relay and Fetch scaffolds. About 25% of the work.
- **New work ≈34 person-hours:** trigger engine + orbit pass 7, backtest 4, Nessie seeding/read/write 4, Payment Protocol 3, Fetch agents/cards/submission 6, Relay call 3, dashboard 3, Devpost/video 4.
- **Risks:** "insurance" is regulated, so call it a mutual-aid fund with play money; Nessie data is mock; no live Michigan fire (demo on replayed real Jan 2025 files plus live CONUS detections, labeled); bigger main-track pool; FREE-WILi lost; Payment Protocol card timing is finicky ([F] Fetch file).

**Scores:** win 5 · non-niche 7 · feasibility 5 · demo wow 6 · sponsor fit 8 · reuse 5.

---

## 5. Idea 3: **Thirty** — a sideline lightning siren that watches from orbit

**One-liner.** A box on the bench (FREE-WILi) that listens to GOES-19's lightning camera: when it sees a flash within 10 miles of your field, it flashes red, says "clear the field," calls the coach in Relay, and counts down the 30-minute all-clear.

### 5.1 Problem and user
- NWS guidance: no place outside is safe in a thunderstorm; wait 30 minutes after the last thunder. Coaches, lifeguards, camps and outdoor event staff make that call by ear.
- US lightning deaths are down to about 18.6 a year (2015–2024), with roughly 300 people struck annually ([Springer](https://link.springer.com/article/10.1007/s11069-025-07899-5); [iWeatherNet](https://www.iweathernet.com/thunderstorms/annual-lightning-injuries-fatalities)). Globally estimates run 6,000–24,000 deaths a year, mostly where there is no warning network ([Holle](https://aclenet.org/file_download/21dc2171-cc21-4b66-b02b-cd29c514ad93); [ResearchGate](https://www.researchgate.net/publication/372495269_A_Year_of_Global_Lightning_Deaths_and_Injuries)). GLM covers the whole Americas for free.
- **Honest:** the US death count is small, so non-niche impact rests on the global and youth-sports framing.

### 5.2 How it works
- **Space data:** GLM L2 LCFA 20-second files; tonight's file was posted about 2 s after its window closed and held 755 flashes [V]. A state machine: CLEAR → CAUTION (20 mi) → STOP (10 mi) → all-clear 30 min after the last flash in range.
- **FREE-WILi:** LEDs as a range ring, screen countdown ("ALL CLEAR IN 23:41"), speaker announcements (pre-rendered ElevenLabs files), button = coach acknowledges.
- **Relay:** calls the coach or athletic director with a live map of flashes; **Fetch.ai:** in ASI:One the AD schedules watches for games, gets a Review card, and the agent emails parents "practice delayed" (a real action). **Grok Imagine:** a labeled storm postcard; Grok voice or ElevenLabs for the announcer.

### 5.3 Tracks
- **Main: Beyond the Code (Hardware)** ("bridges the digital and the real"); the FREE-WILi is the product.
- **Sponsors:** FREE-WILi (strongest fit of the three ideas), SpaceX (GLM is the most "legendary" space data: a camera at 35,786 km seeing every flash), Relay, ElevenLabs, Fetch.ai (weakest fit). Judged by an LLM.

### 5.4 Why it can win, overlap, reuse, risks
- **Evidence:** physical demos took MHacks' top awards in 2025 ([F] [2025](/Users/anvaytodkar/Code/mhacks/results/year-research/2025.md)); Wili-Party won FREE-WILi in 2024 with simple LEDs and buttons ([F] [2024](/Users/anvaytodkar/Code/mhacks/results/year-research/2024.md)); Cosmic Cleaner won 2021's MLH space prize with a physical space build ([F] [2021](/Users/anvaytodkar/Code/mhacks/results/year-research/2021.md)).
- **Novelty:** I found no Devpost GLM lightning project [V, one search].
- **Reuse (≈20%):** GOES S3 fetch pattern, Relay and Fetch scaffolds, the ElevenLabs voice, FREE-WILi bring-up. Fern doesn't fit well.
- **New work ≈28 person-hours.**
- **Risks:** Sunday in Ann Arbor will likely be dry, so the live demo points the "field" at wherever storms are (label it); GLM's 8 km resolution and detection limits mean it is not a certified safety device (say so); in the Hardware pool a FREE-WILi is the floor, not a differentiator ([F] [07-verdict](/Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md)); the OG speaker is quiet.

**Scores:** win 5 · non-niche 5 · feasibility 6 · demo wow 8 · sponsor fit 8 · reuse 4.

---

## 6. Top pick: **Fern on Call**, and why

1. **Most genuine sponsor tickets.** Five core sponsors are load-bearing (Relay, ElevenLabs, FREE-WILi, SpaceX, Fetch.ai), plus FinchNode and Figma as honest bolt-ons. Ember Fund loses FREE-WILi; Thirty's Fetch use is the weakest.
2. **Each sponsor's work improves the main demo.** The pot lighting up and the judge's phone ringing with Fern on video are the main-track demo; nothing is a side widget. That matters because in-person MHacks rarely gives one project two prizes.
3. **Not niche:** 16.2 million people live alone at 65+, and heat deaths have doubled in 25 years. Every judge has a June.
4. **Highest reuse:** the whole Fern kit (face, moods, voice, lip-sync) maps directly, and the wilted mood finally *means* something.
5. **Live data at judging:** a real Extreme Heat Warning is in effect through Oct 7.

**What would flip it:** if Relay calls are dead *and* the FREE-WILi won't run OneWili by 10 PM, Fern on Call loses its two best demo beats; switch to **Ember Fund** (no hardware, Capital One core). If a teammate wants to own the hardware and the team prefers the Hardware track, take **Thirty**.

---

## Sources

**Verified tonight**
- NWS active alerts API: https://api.weather.gov/alerts/active
- GOES-19 GLM L2 LCFA listing: https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=GLM-L2-LCFA/2026/276/21/
- GOES-19 LSTC listing: https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-LSTC/2026/276/21/ · ADPC: https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-ADPC/2026/276/21/ · FDCC: https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-FDCC/2026/276/21/
- GOES-18 LSTC listing: https://noaa-goes18.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-LSTC/2026/276/21/
- GOES-18 FDCC archive, Jan 7 2025: https://noaa-goes18.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-FDCC/2025/007/18/
- GOES-18 SoCal GeoColor: https://cdn.star.nesdis.noaa.gov/GOES18/ABI/SECTOR/psw/GEOCOLOR/1200x1200.jpg
- NASA FIRMS NOAA-20 24 h CSV: https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_USA_contiguous_and_Hawaii_24h.csv
- Relay App Store lookup: https://itunes.apple.com/lookup?id=6789704419 · Relay changelog: https://docs.relayapp.im/changelog.md · Call a person: https://docs.relayapp.im/calls/call-a-person.md
- OneWili Python menus: https://github.com/freewili/onewili/tree/main/python/onewili/menus · audio: https://github.com/freewili/onewili/blob/main/python/onewili/menus/audio.py · gui: https://github.com/freewili/onewili/blob/main/python/onewili/menus/gui.py

**Statistics and precedents (web)**
- Heat deaths 1999–2023 (JAMA): https://jamanetwork.com/journals/jama/fullarticle/2822854
- AP analysis, 2023 heat-death record: https://www.energy.gov/documents/098-associated-press-2023-set-record-us-heat-deaths-ap-analysis-findspdf
- ACL 2023 Profile of Older Americans (16.2 M live alone): https://acl.gov/sites/default/files/Profile%20of%20OA/ACL_ProfileOlderAmericans2023_508.pdf
- CDC heat and medications guidance (mirror): https://restoredcdc.org/www.cdc.gov/heat-health/hcp/clinical-guidance/heat-and-medications-guidance-for-clinicians.html
- Lightning mortality 1979–2023: https://link.springer.com/article/10.1007/s11069-025-07899-5 · annual US stats: https://www.iweathernet.com/thunderstorms/annual-lightning-injuries-fatalities
- Global lightning deaths (Holle): https://aclenet.org/file_download/21dc2171-cc21-4b66-b02b-cd29c514ad93 · https://www.researchgate.net/publication/372495269_A_Year_of_Global_Lightning_Deaths_and_Injuries
- Verisk wildfire exposure: https://www.verisk.com/blog/growing-wildfire-exposure-feeds-need-to-grasp-risk-factors/
- GiveDirectly anticipatory cash: https://www.givedirectly.org/flood-forecast-ai · https://restofworld.org/2025/google-flood-hub-cash-aid/
- Existing elder check-in hackathon projects: https://agentsforhumans.devpost.com/project-gallery?page=2 · https://voice-video-ai-agents.devpost.com/project-gallery
- FIRMS wildfire projects: https://devpost.com/software/signet-3jhw9i · https://big-earth-hackathon-2022.devpost.com/

**Past MHacks winners cited**
- Wattson: https://devpost.com/software/wattson-5btsyd · MobiLens: https://devpost.com/software/mobilens · Gestura: https://devpost.com/software/gestura-9oaugq · Judy AI: https://devpost.com/software/judy-ai-4vc9ah · F.L.U.D.D: https://devpost.com/software/f-l-u-d-d · SunLite: https://devpost.com/software/sunlite-sunrise-lamp · Cosmic Cleaner: https://devpost.com/software/spacejunk · Wili-Party: https://devpost.com/software/wili-party · ZenStock: https://devpost.com/software/zenstock · NOVA: https://devpost.com/software/nova-hzgjy0 · WaterFlow: https://devpost.com/software/waterflow-41mrqd · InsureFire: https://devpost.com/software/insurefire

**Team research files**
- `/Users/anvaytodkar/Code/mhacks/results/SUMMARY.md` (Lessons from six years; Cross-check; Clean Hours §4.3 GOES pipeline)
- `/Users/anvaytodkar/Code/mhacks/results/year-research/2025.md`, `2024.md`, `2023.md`, `2022.md`, `2021.md`, `2020.md`
- `/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/01`–`13` (all twelve advocates and the verdict)
- `/Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md`
- `/Users/anvaytodkar/Code/mhacks/fern/README.md`, `fern/persona.md`, `fern/voice/final/README.md`

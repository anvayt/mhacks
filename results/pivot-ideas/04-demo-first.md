# Pivot Ideas — Demo-first / wow-factor designer

## Prompt given (excerpt)
> You are the Demo-first / wow-factor designer. Design backward from the 3-minute judging demo: the single moment a judge remembers (their phone rings; something physical happens on the table; a satellite image updates live; a character reacts). Use the Fern character, Relay calls, ElevenLabs voice and the FREE-WILi (IR, screen, LEDs, buttons, accelerometer, speaker, sub-GHz radio). Include how the idea plays for the fun tracks (Dumbest Idea / Judged by an LLM) without undercutting the main track.

*Written Sat Oct 3, 2026, about 6 PM EDT. About 18 hours of hacking are left (it ends at 12:00 PM Sun), and judging runs 12:30–3:00 PM Sun at team tables. Tags: **[V]** I checked it myself this evening (22:00 UTC), with the link given. **[F]** It comes from a team research file. **[I]** Inference. **[U]** Unverified, so ask on site.*

---

## TL;DR

| | Idea | Main track | The moment a judge remembers | Win | Non-niche | 18 h | Wow | Sponsors | Reuse |
|---|---|---|---|---|---|---|---|---|---|
| **1 (top pick)** | **Smoke Signal**: Fern watches the sky for the people you love | Sustainability | Fern replays the real GOES-19 smoke from **July 16, 2026, when Detroit had the worst air on Earth**. The FREE-WILi "Mom's pot" on the table turns purple and speaks. Nobody answers, so the "daughter's" phone rings with a wilted Fern on video | 6 | 8 | 6 | 9 | 8 | 8 |
| 2 | **Tend**: a plant that needs your parent and checks on them each time they water it | Actually Intelligent (AI) | The judge tips the FREE-WILi like a watering can. Fern blooms on the device, and the "daughter's" phone gets "Mom watered me ✓". Then we skip a day, and the phone rings | 5 | 8 | 8 | 8 | 7 | 6 |
| 3 | **Sun Break**: GOES-19 rings you when real sun reaches your block | Actually Intelligent (AI) | "You're in a basement. GOES-19 saw sun over North Campus 4 minutes ago." The phone rings: "Go photosynthesize." | 4 | 6 | 9 | 6 | 6 | 9 |

**Top pick: Smoke Signal.** It is the only one of the three where all four memorable beats happen in one 60-second run: a satellite image updates, a device on the table reacts, a phone rings, and the character reacts. It is about a problem every Michigan judge lived through 11 weeks ago: Detroit's AQI hit 490 on July 16, 2026, a city record ([Yale Climate Connections][YCC26]). It keeps the less crowded Sustainability track and SpaceX's "real space data". It also reuses Fern's three moods one-to-one: blooming is clean air and wilted is smoke.

---

## Read the past-year research first

These are the files behind every "why it wins" claim below. Researcher A covers winners and projects; Researcher B covers judging and signal.

| Year | File | Read it for |
|---|---|---|
| 2025 | [../year-research/2025.md](../year-research/2025.md) | Wattson (Greenprint + FREE-WiLi), Judy AI (fun prize, ElevenLabs), MobiLens (Fetch.ai, caregiver alerts), Gestura, sponsor rubrics, the MDredd pairwise judging tool |
| 2024 | [../year-research/2024.md](../year-research/2024.md) | 3-minute table pitch, the 2024 Hacker Guide's prep list, The WiLi Watch (FREE-WILi assistive), Cartesia's "voice must be central" rubric, the 2024 load-shifting winner (overlap warning) |
| 2023 | [../year-research/2023.md](../year-research/2023.md) | CogniCare (Alzheimer's companion), MotionSurfer ("drew judges to the table"), Aipeiron (made its demo fast), LumiGUI |
| 2022 | [../year-research/2022.md](../year-research/2022.md) | No event that year, so skip it |
| 2021 | [../year-research/2021.md](../year-research/2021.md) | **F.L.U.D.D** (a text that escalates to a phone call), **SunLite** (1st: light plus wellbeing), the closing-ceremony judge quotes ("I would definitely use this") |
| 2020 | [../year-research/2020.md](../year-research/2020.md) | we-Learn's single "aha" demo, and Sportable placing 3rd after honestly cutting a broken model |
| All | [../SUMMARY.md](../SUMMARY.md), sections "Lessons from six years of MHacks winners" and "Cross-check" | The ten repeating patterns and how MHacks judges |

---

## What six years of winners say about demos

1. **The top MHacks-run awards go to things a judge can watch happen physically.** In 2025, hardware or wearables won 4 of 6 MHacks-run prizes: the Grand Award robot arm, Wattson, Dementia Assistant and ScreenWave. XR took the top prize at both 2024 events, and the 1st places at MHacks 15 and in 2021 were small hardware builds (LumiGUI, SunLite) [F 2025, 2024, 2023, 2021]. **Caveat:** on prizes open to everyone, 2025 hardware won 3 of 15, no better than average. The advantage shows up only at the top [F SUMMARY].
2. **The pitch is 3 minutes at your table, and several judges hear it.** The 2023 Handbook and the 2024 Hacker Guide both say "projects may be judged multiple times by different judges", and sponsors judge their own prizes in the same window [F 2023, 2024]. MDredd, MHacks' 2026 tool, shows judges two projects at a time [F 2025]. **Design rule:** the memorable moment has to land in the first 60 seconds, and it has to be repeatable 6+ times without anyone touching a laptop.
3. **"Escalate to a phone call" has already won here.** F.L.U.D.D (2021, Google Cloud 1st) texted you about a flooding basement, then **called you if you hadn't replied in 15 minutes**. SunLite (2021 1st) was a light scheduled by text message [F 2021]. Both are the ancestors of a Relay agent-initiated call.
4. **The judges' most specific praise was first-person.** At the 2021 closing ceremony, the presenter said of 1st place that she "would definitely use this" [F 2021]. Every judge has parents, a body that needs daylight, and lungs.
5. **Name a user, give a statistic, add a local hook.** NurseNotes ("41% of a shift"), FarmX (Michigan farms), F.L.U.D.D (SE Michigan floods) and MCall (a Michigan Daily statistic) all did this [F 2024, 2021]. Detroit's July 2026 smoke record is the strongest local hook available this year.
6. **The top prizes need a technical core the team built itself:** V²/R's circuit solver, FocusFlow's LSTM, DECO.ai's NeRF, ASI's trained policy [F 2024, 2023, 2025]. Each idea below has one measured "we built this" piece: a backtest, a routine model or a nowcast.
7. **Agents have to close a loop in the real world.** All of 2025's agent winners sent, filed, negotiated or controlled something. MobiLens won Fetch.ai Best Use with caregiver alerts [F 2025].
8. **Fun prizes went to projects that were funny and finished.** Judy AI was a voiced ElevenLabs companion. The Grand Award was an absurd premise on real engineering [F 2025]. A comic element can't undercut a safety pitch, though: Devpost shows fun-track opt-ins publicly [F SUMMARY].
9. **Film it in real life, and give it a memorable name.** The 2021 MLH judge praised a video "shot in real life", and he seems to have mixed up two flood and water projects on stage [F 2021].
10. **Overlap list (things already done):**
    - Clean-hour load shifting (2024 MLH Streamlit) [F 2024].
    - A FREE-WiLi pet that nags you (Wattson, 2025) [F 2025].
    - Fridge-to-recipe suggestions (Cosmocook, 2024) [F 2024].
    - Barcode eco-scores (EcoScout, 2025) [F 2025].
    - **OpenAI's open-source "Plant Talk" (June 2026)**, which gives a houseplant a ChatGPT voice ([GitHub][PLANTTALK]) [V]. A talking houseplant is therefore **not** novel by itself. Fern is the delivery, and the novelty has to be what she does.

---

## Idea 1 (top pick): Smoke Signal

**One-liner.** Fern, a houseplant with a phone line, watches GOES-19's smoke detection for the cities where your people live. Before the smoke arrives she warns them, through a little "pot" on their windowsill or a Relay call. If they don't confirm they're safe, she video-calls **you**.

### Problem and user (why it isn't niche)
- **Smoke is now everyone's problem in the Great Lakes.**
  - On **July 16, 2026, Detroit recorded an AQI of 490**, beating its old record of 226 (June 2023). Grand Rapids hit 482, Flint 343, and five states reached "Hazardous" ([Yale Climate Connections][YCC26]) [V].
  - The next day Detroit was again the most polluted city in the world, at an AQI of 428 ([CBS Detroit][CBS26]) [V].
  - In 2023 Detroit topped IQAir's world ranking at 426 ([WXYZ][WXYZ23]) [V].
- **This is a lasting trend, not one event.** Since 2016, wildfire smoke has erased about 25% of the US's air-quality gains since 2000, and it has slowed or reversed PM2.5 trends in 35 states (Burke et al., *Nature* 2023, via [Stanford][STAN23]) [V].
- **The people most at risk are the least likely to see an app alert.**
  - **16.2 million older Americans (28%) live alone** (ACL Profile of Older Americans, per a search summary of [acl.gov][ACL]) [V, search summary].
  - In Portland's 2021 heat dome, **48 of the 72 people who died lived alone**, and most had no AC ([Multnomah County][MULT]) [V]. That is heat, not smoke, but it is the same pattern: climate hazards kill people who are alone.
- **User.** "Priya, a U-M student whose mom lives alone in Detroit" (a fictional persona, labeled as such), and her mom. The pitch: *every judge has someone they'd want Fern to watch.*

### What it does (the product loop)
1. **Care circle.** Priya texts Fern in Relay: "Watch Detroit for my mom." Fern asks for a location (a Relay location request [F Relay file]) and registers Mom's "pot" (the FREE-WILi) or Mom's own Relay. Each person gets their own chat, because Relay chats can't hold two humans [F Relay file].
2. **Sky watch, every 10 minutes.** For each watched place the system reads:
   - the **GOES-19 ABI Aerosol Detection Product (ADPC: smoke and dust flags)** and **Aerosol Optical Depth (AODC)** at that pixel and along an upwind ring;
   - **NASA FIRMS** fire detections;
   - **Open-Meteo's surface PM2.5 forecast** (CAMS model, keyless).

   These are fused into a risk level and an arrival time. GOES sees the smoke column; the surface forecast says whether it will reach the ground. Saying so out loud is a rigor point. [V for every source; see "Data sources" below.]
3. **The ladder** (the F.L.U.D.D pattern, upgraded):
   - (a) Mom's pot turns the AQI color and Fern speaks the EPA "clean room" steps: close the windows, run a box fan with a MERV-13 filter ([EPA][EPA-CR], [EPA DIY][EPA-DIY]).
   - (b) Mom presses the leaf button, or picks up the pot (accelerometer), to say "done".
   - (c) No answer within N minutes: **Fern video-calls Priya** in Relay, wilted, with the numbers.
   - (d) Priya's "I'll call her" or "keep trying" goes back to the agent.
4. **The log.** Each alert shows its satellite scan time, and each acknowledgment has a timestamp. Fern's numbers come only from tool results, under the persona's hard rule ([persona.md](../../fern/persona.md) §2).

### The 3-minute demo (designed backward from the moment)
| Time | What happens | What the judge sees, hears or holds |
|---|---|---|
| 0:00–0:15 | Hook. P4 holds up the FREE-WILi "pot": "Eleven weeks ago Detroit had the worst air on Earth. Sixteen million older Americans live alone." | The device, with Fern's face on its 320×240 screen |
| 0:15–0:45 | **Live**: "Where do your parents live?" We type the judge's answer. The map flies there and shows the **latest GOES-19 scan (n minutes old)**, the smoke and aerosol overlay, FIRMS dots and a surface forecast. Fern, on screen, gives the honest live state: "[curious] Clear air over Columbus. GOES-19 looked seven minutes ago." | **A satellite image updates live, personalized to them** |
| 0:45–1:30 | **Replay: July 16, 2026, from the real GOES-19 archive**, labeled "REPLAY". The smoke mask floods Michigan. The **pot on the table turns purple**, its screen flips to wilted Fern, and its speaker says: "[sighs] Smoke's coming, worst by four. Close the windows, run the box fan with the filter, then press my leaf." The judge has been asked to play Mom and ignore it. | **Something physical happens on the table** |
| 1:30–1:50 | A 30-second demo timer runs out (10 minutes in the product). **The "daughter's" iPhone on the table rings.** It's a Relay video call: wilted Fern, live ElevenLabs voice: "Your mom hasn't answered me, and Detroit hits hazardous by four. Want me to keep trying her, or will you call?" | **The phone rings, and the character reacts** |
| 1:50–2:05 | The judge (as Mom) presses the button. The pot blooms, and the daughter's chat gets "Mom pressed my leaf at 1:52 ✓". | Relief. The loop is closed |
| 2:05–2:40 | The technical core, shown as **our backtest** of July 15–17, 2026 and June 2023: how many hours before surface PM2.5 crossed 55 µg/m³ the GOES smoke flag plus upwind ring fired over Detroit, plus false alarms per week. **Measure these before claiming them.** | A results table, with Limitations shown next to it |
| 2:40–3:00 | Close, with the joke: "NASA said in 1989 that plants like me clean your air. A 2019 review found you'd need up to a thousand of us per square meter. So instead, I call you." ([Drexel][DREXEL]) | A laugh that doesn't undercut the safety pitch |

For the **Relay judge**, who has the app: scan the QR, text Fern first (an agent can only call people who messaged it [F Relay file]), and Fern calls *their* phone in the replay.

### Tracks
- **Main: Sustainability.** The track text is "rethink energy, climate, and resource systems for lasting impact on our planet" ([F 01-main-sustainability](../main-and-fun-tracks/01-main-sustainability.md)).
  - Smoke is the climate impact people feel most directly, and the claim is measured (hours of warning, people reached).
  - **Honest risk:** this is climate *adaptation*, which a judge may score lower on "Adherence to Theme" than mitigation [F SUMMARY, Overpass risk]. Mitigation: say "climate resilience" in the first 10 seconds, and show the Burke trend line (smoke is reversing air-quality progress).
- **Fun:**
  - **Judged by an LLM: yes.** Write a Devpost around the four criteria, plus a "What we measured" section (the backtest) and a "Limitations" section (column smoke vs surface smoke, daytime-only ADP, cloud gaps, model underestimates).
  - **Dumbest Idea: no.** It's a safety product for older adults, and opt-ins are public. The NASA-plant joke stays as personality only.
  - **Useless AI: no.**

**Sponsors (each one load-bearing):**

| Sponsor | Genuine use |
|---|---|
| **SpaceX "Make it Legendary"** | GOES-19 ADP/AOD **is** the input ("real space data goes in"). Fern's portrait, mood stills and call loops are already **Grok Imagine** assets, Grok is her brain on calls, and the team builds in Cursor. If SpaceXAI ruled at 4 PM that Earth observation doesn't count, add a **"which satellite saw this fire, and its next pass"** card from FIRMS's per-satellite field plus CelesTrak (~1 h) [F SpaceX file]. |
| **Relay** | Text onboarding, a location request, an **agent-initiated video call to a second person** (the escalation), and Fern's mood loops as her camera. "Agents that do things and feel personal" is the judge's taste [F Relay file]. |
| **ElevenLabs** | Voice is the interface for someone who won't read an app. That means Fern's designed voice on calls (`eleven_v4_turbo` + audio tags), plus the same voice played **through the FREE-WILi speaker**. Voice through a FREE-WiLi speaker already won FREE-WiLi at GrizzHacks 8 [F FREE-WILi file]. |
| **FREE-WILi** | **The device is the product:** Mom's pot. It uses the screen (mood stills resized to 320×240), 7 LEDs (AQI color), speaker (alerts), button (ack) and accelerometer (picked up = ack). That matches the "device is the product" pattern in every FREE-WILi winner [F FREE-WILi file]. |
| **Fetch.ai ASI:One** | "@smokesignal watch Detroit for my mom" leads to a Review card (place, thresholds, who to escalate to), then Confirm, then a watcher agent that runs the ladder. Real action: a phone call. Gate it at midnight. |
| *FinchNode (optional, ~2–3 h)* | Read the care-circle member's conditions from FinchNode's keyless synthetic records. Asthma, COPD or heart disease lowers that person's alert threshold to EPA's "sensitive groups" level [F FinchNode file]. |
| *Figma (optional)* | Only if ahead at 6 AM. |

### Why it would win (past evidence)
- **F.L.U.D.D (2021)** won Google Cloud 1st with a local Michigan disaster alert that escalated to a call [F 2021]. This is that pattern, on live satellites and an agent that video-calls.
- **Wattson (2025)** proves Sustainability plus a FREE-WiLi device wins both [F 2025]. Smoke Signal avoids the look-alike because it isn't a pet that nags: the device is an alert terminal for someone else.
- **MobiLens (2025 Fetch.ai Best Use)** was caregiver alerts with agents [F 2025]. **NOVA (DivHacks SpaceXAI winner)** handled real data rigorously for an underserved user, with voice for access [F SpaceX file].
- **2021 judge test:** "would I use this?" Every judge has a parent, and every Michigan judge breathed July 16 [F 2021; V YCC26].
- **Local hook plus statistic** (patterns 4 and 5) are built into the first sentence.

### Novelty vs past winners
- **Already done:** generic smoke and fire alert apps exist on Devpost ("Wildfire Watch Canada", an SMS air-quality monitor; [Devpost][WWC]), and EPA's AirNow sends alerts.
- **Ours:**
  - (1) A **satellite-first** signal (the GOES-19 smoke mask every 10 minutes), fused with a surface forecast and **backtested on a real local record event**.
  - (2) **The alert reaches someone without an app** (the pot) and **escalates to family through an agent-initiated video call**.
- No MHacks winner in 2020–2025 did smoke [F year files]. Overpass (our earlier backup) watched fires and orbits; this keeps its research but changes the user and the loop.

### Reuse (what exactly)
- **Fern kit, 100%:** three mood stills, for the device screen and Relay profile; the six HD talking and listening loops, for the call camera; the ElevenLabs voice `Fern (MHacks 2026)`; the lip-synced lines and the pipeline for pre-rendered demo beats; and the persona's hard numbers rule.
  - Mood mapping is free: **wilted = smoke, normal = moderate, blooming = clean**.
  - We need **no new xAI video spend**. At most 2 new lip-synced lines for the filmed backup (≈$1–1.5 each).
- **Researched plans:**
  - Relay call path and workshop [F Relay file].
  - GOES-19 fixed-grid projection math: ADPC/AODC share the ABI fixed-grid projection used for DSR/ACM in SUMMARY §4.3 [F SUMMARY].
  - FIRMS and CelesTrak (from Overpass) [F SpaceX file].
  - Fetch.ai Review-card flow [F SUMMARY §2].
  - FREE-WILi smoke-test plan [F FREE-WILi file].
- **Dropped:** grid carbon and MISO work.
- **Estimated reuse ≈ 50%** of the total effort, counting finished assets plus plans that transfer directly.

### New work and hours (4 people, ~18 h, sleep included)
| Owner | Work | Hours |
|---|---|---|
| P1 Relay + voice | Workshop path to text, call and video with mood loops (~2 h); escalation ladder + a second-person call + ack handling (2 h); rewrite Fern's prompt and lines for smoke (1 h) | ~5 |
| P2 Satellite | ADPC/AODC download + fixed-grid lat/lon→pixel + upwind ring (3 h); FIRMS + Open-Meteo fusion → risk/ETA (2 h); **replay mode for Jul 15–17 2026** (1.5 h); **backtest table** (2 h) | ~8.5 |
| P3 Backend + Fetch | State machine, SQLite care circle, API (3 h); dashboard map with live GeoColor + overlay (2.5 h); Fetch.ai watcher + Review card (3 h, gated) | ~8.5 |
| P4 FREE-WILi + pitch | Firmware/library smoke test (1 h); screen/LED/speaker/button/accelerometer "pot" (4 h); Devpost (Judged by an LLM), demo choreography, **real-life video** (3 h) | ~8 |

**Checkpoints:**
- **9 PM:** one ADPC pixel value printed for Detroit at 2026-07-16 18:01 UTC; a Relay call rings a teammate; the FREE-WILi lights an LED from Python.
- **Midnight:** the replay runs end to end (pot glows, no ack, daughter's phone rings, ack, bloom). Otherwise cut Fetch.ai.
- **6 AM:** freeze. **10 AM:** film the video.
- **11:30 AM:** submit.

### Data sources (verified tonight)
- **GOES-19 ADPC + AODC are live.** The latest CONUS scans were listed at 21:41 and 21:51 UTC when I checked at 22:00 UTC, on a 10-minute cadence (Mode 6) ([S3 ADPC][S3-ADP], [S3 AODC][S3-AOD]) [V].
  - The product is daytime-only and clear-sky only, every 10 minutes in Mode 6 ([GOES-19 ADP ReadMe][ADP-RM]) [V].
  - Judging (12:30–3 PM) is in daylight.
- **The July 16, 2026 event is in the archive.** `ABI-L2-ADPC/2026/197/18/` and `ABI-L2-AODC/2026/197/18/` exist ([S3][S3-197]) [V].
  - So does June 2023 on GOES-16 (`2023/158`, `2023/179`) ([S3 G16][S3-G16]) [V].
- **Open-Meteo Air Quality needs no key** and returns an hourly `pm2_5`/`us_aqi` forecast and history ([API][OM-AQ]) [V].
  - Its modeled Detroit PM2.5 peaked at **156.5 µg/m³ at 2026-07-17 20:00 local** [V]. That is far below the monitor readings behind IQAir's 490 AQI, which is a Limitation to state and the reason to use AirNow as ground truth.
- **NASA FIRMS** has a keyless 24 h CSV per satellite. NOAA-21 listed **1,857** US detections in the last 24 h ([CSV][FIRMS]) [V].
- **AirNow API** answers 401 without a key, so it is live and a free key is needed ([AirNow][AIRNOW]) [V].

### Risks
- **Theme adherence (adaptation).** See Tracks.
- **No live smoke on Sunday:** Ann Arbor's NWS forecast is "Sunny, 69" ([NWS][NWS]) [V]. The live beat is honest ("clear air"), and the drama comes from the **labeled replay of real archived data**.
- **Overclaiming:** never call ADP "ground-level smoke". Report the measured lead time, not an assumed one.
- **Relay calls** depend on today's app build and an iOS 26 phone [F Relay file]. Fallback: Photon, or a mirrored recorded call.
- **FREE-WILi firmware/library churn** (OneWili vs legacy) [F FREE-WILi file]. Fallback: an on-screen simulated pot.
- **Scope creep:** heat waves are the natural v2. Mention them, don't build them.

**Scores:** win 6 · non-niche 8 · feasibility 6 · demo wow 9 · sponsor fit 8 · reuse 8.

---

## Idea 2: Tend

**One-liner.** Fern lives on your parent's windowsill and asks to be watered every morning. Each watering is a quiet "I'm OK". When it doesn't happen, she calls them, and then she calls you.

### Problem and user
- **16.2 million older Americans live alone** (per a search summary of [ACL][ACL]) [V, search summary].
- Lacking social connection carries a mortality risk similar to **smoking up to 15 cigarettes a day** ([Surgeon General advisory][SG]) [V].
- **The evidence hook:** in Langer & Rodin's 1976 nursing-home study, residents encouraged to take responsibility, including **caring for their own plant**, had **15% mortality at 18 months vs 30%** in the comparison group ([summary][LR]) [V].
  - **Honest caveat:** the intervention was broader responsibility and choice, not the plant alone, and the sample was small and later critiqued ([critique][LR-CRIT]). Present it as inspiration, not proof.
- **User:** adult children who live far from a parent who lives alone, and the parent.

### The demo moment
1. The judge plays Mom. The FREE-WILi pot shows wilted Fern: "[sighs] Morning. I'm parched."
2. The judge **tips the device like a watering can**. The accelerometer pour gesture is a tilt over about 60° held for about 1.5 s.
3. The LEDs ripple blue, the screen blooms, and the speaker says: "[laughs] Oh, that's the stuff. How'd you sleep?"
4. The judge answers through the laptop mic and STT, because OG mic streaming wasn't available to Gestura [F FREE-WILi file].
5. At the same moment, the "daughter's" phone gets: "Mom watered me at 12:41. Slept badly; knee came up (3rd time this week)."
6. **Then we skip a day:** no watering by 11 AM. The pot chimes, and nobody answers. **The daughter's iPhone rings**, with Fern on video: "She didn't water me and didn't answer. That's not like her; she's 6 for 6 this week."

### Technical core we build
- A **per-person routine model**: the distribution of watering times, with an alert when a check-in is outside the usual window (with a tuning knob).
- **LLM summaries of each chat with concern extraction** (pain, falls, mood, missed meds), each with a quote and a timestamp.
- Optionally, the parent's medication list from **FinchNode** (its keyless synthetic 78-year-old polypharmacy patient [F FinchNode file]), so that watering time is also pill time.

### Tracks
- **Main: Actually Intelligent.** The "not just AI for AI's sake" test is met by routine anomaly detection plus grounded summaries [F 02-main-AI].
  - **Honest:** this is the most crowded pool (about 47% of 2025 projects listed an LLM [F SUMMARY]).
  - Beyond the Code becomes plausible only if the MLH hardware desk has a capacitive soil-moisture sensor, so a *real* fern's soil is the check-in [U]. A FREE-WILi alone is "the bare minimum" in that pool [F SUMMARY].
- **Fun:** Judged by an LLM, yes (a routine-model eval on synthetic weeks). Dumbest Idea, no (elder care).

**Sponsors:**

| Sponsor | Genuine use |
|---|---|
| **Relay** | Strongest fit of the three. Advait's own Companion.AI is "an AI companion with video calling, memory, streaks" [F Relay file], and the watering habit *is* a streak. The flow is a text digest, then an agent-initiated escalation call. |
| **ElevenLabs** | Voice is the whole interface for the parent, through the pot's speaker and on calls. |
| **FREE-WILi** | The device is the product: accelerometer pour, screen, LEDs, speaker, button. This is the assistive pattern of Gestura, The WiLi Watch and Agent Unblind [F FREE-WILi file]. |
| **FinchNode** | Medication list and conditions drive what Fern asks about. |
| *Fetch.ai (optional)* | "How's Mom this week?" in ASI:One returns the digest, and "call her now" triggers the call. |
| **SpaceX** | **Dropped.** It would be garnish, and garnish entries lose [F SpaceX file]. |

### Why it would win, and the overlap
- **For:**
  - CogniCare (2023 Social Impact) and Dementia Assistant (2025 Lifeline) show elder-care companions win here.
  - MobiLens (2025) won Fetch with caregiver alerts.
  - The WiLi Watch (2024) won with an assistive FREE-WILi.
  - Judy AI (2025) won the fun prize as a character companion with ElevenLabs.
  - F.L.U.D.D (2021) used the same escalation ladder [F 2023, 2025, 2024, 2021].
- **Against (novelty):**
  - Elder AI companions are common on Devpost (CompanionAI, VoiceCare, Cara) ([Devpost][DP-COMP]).
  - ElliQ is a commercial product.
  - OpenAI's Plant Talk makes a talking plant ordinary ([GitHub][PLANTTALK]).
  - The new part is **reciprocity as the check-in signal** (the parent cares for Fern, which tells the family they're OK), delivered on an app-free device with a video-call escalation.

### Reuse and new work
- **Reuses:**
  - All of the Fern kit: wilted = thirsty or worried, blooming = watered.
  - The voice, loops and lip-sync pipeline.
  - The Relay plan, and the FREE-WILi in hand.
- **Drops:** all satellite and grid work. **Reuse ≈ 40%.**
- **Hours:**
  - P1 Relay calls + escalation: 5 h.
  - P4 FREE-WILi pour gesture + screen/LED/speaker: 5 h.
  - P3 routine model + LLM summaries + digest: 6 h.
  - P2 FinchNode + Fetch (optional) + Devpost/video: 6 h.
  - That leaves the most slack of the three.
- **Optional:** 2–3 new lip-synced lines for the video (≈$3–4.5 xAI).

### Risks
- The AI pool is crowded.
- "Elder companion" sounds familiar, so lead with the watering mechanism and the escalation, not the chat.
- Privacy and consent framing (the parent opts in, summaries are shown to the parent too) has to be on the slide.
- The pour gesture needs a calibration knob (the threshold angle and hold time).

**Scores:** win 5 · non-niche 8 · feasibility 8 · demo wow 8 · sponsor fit 7 · reuse 6.

---

## Idea 3: Sun Break

**One-liner.** Fern photosynthesizes for a living, and she thinks you should too. She watches GOES-19's clear-sky mask over your exact block and calls you when real sun lines up with a free 15 minutes.

### Problem and user
- **Americans spend about 90% of their time indoors** ([EPA][EPA-90]) [V].
- **About 5% of US adults have seasonal affective disorder**, rising toward 10% at northern latitudes ([APA][APA-SAD], [AAFP][AAFP]) [V].
- **Nearly 4 in 10 Americans report their mood declining in winter** (APA 2022 poll, [UTHealth][APA-POLL]) [V].
- **User:** students and office workers in cloudy northern cities like Ann Arbor in November.
- **Honest:** the impact is real but low-stakes per person. A judge may see it as "a weather app with a phone call".

### The demo moment
- "You're in a basement. It's 'Sunny, 69' outside ([NWS][NWS]) [V]. GOES-19, 35,786 km up, can see that. You can't."
- The dashboard shows the **latest GOES-19 clear-sky-mask scan for the Duderstadt pixel (5-minute cadence)** and a nowcast: "clear for at least 40 min".
- The judge says they're free at 3. **The phone rings:** blooming Fern: "[gasps] Real photons over North Campus. GOES-19 saw clear sky four minutes ago. Go photosynthesize. I'll wait."
- **Stretch:** "Show me the sky" uses Relay's ability to read the user's camera frames [F Relay file], so Fern can confirm the blue sky with her own eyes. The basement has no windows, so this beat lives in the video only.

### Technical core we build
- A **cloud-motion nowcast** from consecutive ACM frames (optical flow on the clear-sky mask around the user's pixel).
- A **backtest** of its precision for "clear in the next 15 minutes".

### Tracks
- **Main: Actually Intelligent** (honestly thin for that track's text). It doesn't fit Sustainability.
- **Fun: Dumbest Idea, yes.** The premise *is* the joke: a geostationary weather satellite used to tell you to touch grass. It's the 2025 pattern of an absurd premise on a real engine [F 05-fun-dumbest-idea]. Judged by an LLM, yes (the nowcast backtest).
- This is the only idea of the three where a fun track doesn't undercut the main pitch, because there's no safety claim to undercut.

**Sponsors:**

| Sponsor | Genuine use |
|---|---|
| **SpaceX** | The satellite *is* the product, but it is Earth observation. Add the GOES-19 orbit card from CelesTrak (NORAD 60133) as the hedge [F SUMMARY]. |
| **Relay** | Text, location request, agent-initiated call, and the camera-vision stretch. |
| **ElevenLabs** | Fern's voice and audio tags. |
| **FREE-WILi** | Weak: a desk "sun lamp" whose LEDs mirror the satellite sky is garnish. Don't enter it. |
| **Fetch.ai** | Weak. Skip it. |

### Why it would win, and the overlap
- **For:**
  - SunLite (2021 1st) was light for wellbeing, and its judge said she'd use it [F 2021].
  - we-Learn (2020) won on one "aha" moment [F 2020].
  - Judy AI and ASI show MHacks rewards funny on top of real [F 2025].
- **Against:**
  - A "Touch Grass" Devpost project exists (photo scavenger hunt; different idea) ([Devpost][TG]).
  - **Structurally it is Clean Hours with a new target**: "Fern calls you at the right hour, from GOES-19". The team may feel it's the same project. That is also why it's the cheapest.

### Reuse and new work
- **Reuses:**
  - The GOES-19 ACM/DSR fixed-grid pipeline planned for Clean Hours, exactly [F SUMMARY §4.3].
  - Fern's catchphrase "I photosynthesize for a living" is already in [persona.md](../../fern/persona.md), and blooming = sun.
  - The Relay plan.
  - **Reuse ≈ 65%.**
- **Hours:**
  - P2 ACM pixel + nowcast + backtest: 7 h.
  - P1 Relay calls + scheduling: 5 h.
  - P3 dashboard + streaks: 5 h.
  - P4 Devpost + video + joke polish: 4 h.

### Risks
- Low perceived impact.
- Looks like a re-skin of Clean Hours.
- Earth observation may not count for SpaceX.
- The basement kills the camera beat.

**Scores:** win 4 · non-niche 6 · feasibility 9 · demo wow 6 · sponsor fit 6 · reuse 9.

---

## Top pick: Smoke Signal

1. **The best demo of the three.** One run covers live satellite, the device reacting on the table, the phone ringing and Fern reacting. It survives being judged six times because the replay is deterministic and the live beat is honest.
2. **Not niche, with a local hook no other team can top:** Detroit's AQI hit 490 eleven weeks ago, a city record ([YCC][YCC26]). Smoke has erased about a quarter of US air-quality gains ([Stanford][STAN23]). The people at risk live alone ([ACL][ACL], [Multnomah][MULT]).
3. **It keeps the strategy the team already settled:** the Sustainability pool (15/122 in 2025 [F SUMMARY]), SpaceX with space data at the core, Relay + ElevenLabs on one path, and FREE-WILi as the product.
4. **It has the "we built this" core judges reward:** a backtested satellite-to-surface lead time on a real record event.
5. **Highest reuse that isn't a re-skin.** Fern's moods map one-to-one onto smoke, and no new xAI spend is needed.

**What would change my mind:**
- If SpaceXAI said at 4 PM that Earth observation doesn't count *and* the team values SpaceX above Sustainability, take **Overpass** (SUMMARY backup #1). Smoke Signal's shell carries over.
- If Relay calls failed at the workshop, **Tend** degrades more gracefully: the pot plus a Photon text still tells the story.
- **Cheap merge if ahead at 6 AM:** add Tend's "press my leaf every morning" as the daily I'm-OK signal in Smoke Signal. Do not start it before the replay works end to end.

---

## Sources

**Team research (read these first)**
- Year research: [2025](../year-research/2025.md) · [2024](../year-research/2024.md) · [2023](../year-research/2023.md) · [2022](../year-research/2022.md) · [2021](../year-research/2021.md) · [2020](../year-research/2020.md)
- [SUMMARY.md](../SUMMARY.md) (Lessons from six years; Cross-check; GOES §4.3; backup ideas)
- Track files: [01 Sustainability](../main-and-fun-tracks/01-main-sustainability.md) · [02 AI](../main-and-fun-tracks/02-main-actually-intelligent-ai.md) · [05 Dumbest Idea](../main-and-fun-tracks/05-fun-dumbest-idea.md) · [07 verdict](../main-and-fun-tracks/07-debate-and-verdict.md)
- Sponsor files: [04 FREE-WILi](../sponsor-tracks/04-free-wili.md) · [07 SpaceX](../sponsor-tracks/07-spacex-make-it-legendary.md) · [10 FinchNode](../sponsor-tracks/10-finchnode-healthtech.md) · [11 Relay](../sponsor-tracks/11-relay-interactive-agents.md) · [13 verdict](../sponsor-tracks/13-debate-and-verdict.md)
- Fern kit: [fern/README.md](../../fern/README.md) · [fern/persona.md](../../fern/persona.md) · [fern/voice/final/README.md](../../fern/voice/final/README.md)

**Smoke, heat, health**
- [YCC26] Yale Climate Connections, July 2026 smoke event (Detroit 490 AQI record): https://yaleclimateconnections.org/2026/07/dangerous-and-historic-wildfire-smoke-pollution-event-engulfs-the-u-s-and-canada/
- [CBS26] CBS Detroit, Jul 17 2026 (Detroit worst in world, AQI 428): https://www.cbsnews.com/detroit/news/detroit-worst-air-quality-in-world-canadian-wildfire-smoke-july-17/
- [WXYZ23] WXYZ, Detroit worst air in world (IQAir, 426), June 2023: https://www.wxyz.com/news/detroit-has-the-worst-air-quality-in-the-world-from-canadian-wildfire-smoke-iqair-says
- ClickOnDetroit, June 7 2023: https://www.clickondetroit.com/news/local/2023/06/07/detroit-air-quality-among-worst-on-earth-as-canadian-wildfire-smoke-moves-through/
- [STAN23] Stanford on Burke et al. (Nature 2023): https://news.stanford.edu/stories/2023/09/wildfire-smokes-toxic-influence · Grist: https://grist.org/wildfires/study-wildfire-smoke-is-reversing-years-of-us-air-quality-progress/
- [MULT] Multnomah County 2021 heat deaths: https://www.multco.us/help-when-its-hot/news/2021-heat-killed-72-people-multnomah-county-most-were-older-lived-alone-had
- [ACL] ACL Profile of Older Americans: https://acl.gov/news-and-events/announcements/acl-releases-2023-profile-older-americans · https://acl.gov/sites/default/files/Profile%20of%20OA/ACL_ProfileOlderAmericans2023_508.pdf
- [SG] Surgeon General advisory on social connection: https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf
- [EPA-CR] EPA clean room: https://www.epa.gov/emergencies-iaq/create-clean-room-protect-indoor-air-quality-during-wildfire · [EPA-DIY] https://www.epa.gov/air-research/research-diy-air-cleaners-reduce-wildfire-smoke-indoors
- [DREXEL] Drexel 2019 (potted plants don't improve indoor air): https://drexel.edu/news/archive/2019/november/potted-plants-do-not-improve-air-quality
- [LR] Langer & Rodin summary: https://www.wise-interventions.org/posters/taking-responsability-of-themselves-and-making-their-own-choices-improved-health-and-well-being-among-nursing-home-residents · [LR-CRIT] critique: https://www.coyneoftherealm.com/2014/11/05/re-examining-ellen-langers-classic-study-giving-plants-nursing-home-residents/
- [EPA-90] EPA indoor air (90% indoors): https://www.epa.gov/report-environment/indoor-air-quality
- [APA-SAD] https://www.psychiatry.org/patients-families/seasonal-affective-disorder · [AAFP] https://www.aafp.org/pubs/afp/issues/2012/1201/p1037.html · [APA-POLL] https://med.uth.edu/psychiatry/2022/12/19/nearly-4-in-10-americans-experience-declining-mood-in-winter-apa-poll-finds/

**Data (probed 2026-10-03 22:00 UTC)**
- [S3-ADP] https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-ADPC/2026/276/ · [S3-AOD] https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-AODC/2026/276/
- [S3-197] https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-ADPC/2026/197/18/
- [S3-G16] https://noaa-goes16.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-ADPC/2023/179/17/
- GOES-19 ACMC (clear-sky mask) listing: https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-ACMC/2026/276/
- [ADP-RM] GOES-19 ADP Provisional ReadMe: https://www.ospo.noaa.gov/operations/goes/product-quality-overview/ps-pvr/goes-19/ABI/Aerosol%20Detection/Provisional/GOES-19_ABI_L2_ADP_Provisional_ReadMe.pdf · STAR ADP page: https://www.star.nesdis.noaa.gov/goesr/product_aero_det.php
- [OM-AQ] Open-Meteo Air Quality: https://air-quality-api.open-meteo.com/v1/air-quality?latitude=42.33&longitude=-83.05&hourly=pm2_5,us_aqi
- [FIRMS] NOAA-21 VIIRS 24 h CSV: https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-21-viirs-c2/csv/J2_VIIRS_C2_USA_contiguous_and_Hawaii_24h.csv
- [AIRNOW] https://www.airnowapi.org/aq/observation/latLong/current/
- [NWS] https://api.weather.gov/gridpoints/DTX/42,30/forecast

**Novelty checks**
- [PLANTTALK] OpenAI Plant Talk: https://github.com/openai/planttalk
- [WWC] Wildfire Watch Canada (Devpost): https://devpost.com/software/wildfire-watch-canada · Air Quality Monitor: https://devpost.com/software/cog-hackathon-air-quality
- [DP-COMP] Elder companions on Devpost: https://devpost.com/software/companionai · https://devpost.com/software/voicecare-ai-companion-for-elderly · https://devpost.com/software/cara-caretaker-assistant
- [TG] Touch Grass (Devpost): https://devpost.com/software/touch-grass-cvkd4w

[YCC26]: https://yaleclimateconnections.org/2026/07/dangerous-and-historic-wildfire-smoke-pollution-event-engulfs-the-u-s-and-canada/
[CBS26]: https://www.cbsnews.com/detroit/news/detroit-worst-air-quality-in-world-canadian-wildfire-smoke-july-17/
[WXYZ23]: https://www.wxyz.com/news/detroit-has-the-worst-air-quality-in-the-world-from-canadian-wildfire-smoke-iqair-says
[STAN23]: https://news.stanford.edu/stories/2023/09/wildfire-smokes-toxic-influence
[MULT]: https://www.multco.us/help-when-its-hot/news/2021-heat-killed-72-people-multnomah-county-most-were-older-lived-alone-had
[ACL]: https://acl.gov/news-and-events/announcements/acl-releases-2023-profile-older-americans
[SG]: https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf
[EPA-CR]: https://www.epa.gov/emergencies-iaq/create-clean-room-protect-indoor-air-quality-during-wildfire
[EPA-DIY]: https://www.epa.gov/air-research/research-diy-air-cleaners-reduce-wildfire-smoke-indoors
[DREXEL]: https://drexel.edu/news/archive/2019/november/potted-plants-do-not-improve-air-quality
[LR]: https://www.wise-interventions.org/posters/taking-responsability-of-themselves-and-making-their-own-choices-improved-health-and-well-being-among-nursing-home-residents
[LR-CRIT]: https://www.coyneoftherealm.com/2014/11/05/re-examining-ellen-langers-classic-study-giving-plants-nursing-home-residents/
[EPA-90]: https://www.epa.gov/report-environment/indoor-air-quality
[APA-SAD]: https://www.psychiatry.org/patients-families/seasonal-affective-disorder
[AAFP]: https://www.aafp.org/pubs/afp/issues/2012/1201/p1037.html
[APA-POLL]: https://med.uth.edu/psychiatry/2022/12/19/nearly-4-in-10-americans-experience-declining-mood-in-winter-apa-poll-finds/
[S3-ADP]: https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-ADPC/2026/276/
[S3-AOD]: https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-AODC/2026/276/
[S3-197]: https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-ADPC/2026/197/18/
[S3-G16]: https://noaa-goes16.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-ADPC/2023/179/17/
[ADP-RM]: https://www.ospo.noaa.gov/operations/goes/product-quality-overview/ps-pvr/goes-19/ABI/Aerosol%20Detection/Provisional/GOES-19_ABI_L2_ADP_Provisional_ReadMe.pdf
[OM-AQ]: https://air-quality-api.open-meteo.com/v1/air-quality?latitude=42.33&longitude=-83.05&hourly=pm2_5,us_aqi
[FIRMS]: https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-21-viirs-c2/csv/J2_VIIRS_C2_USA_contiguous_and_Hawaii_24h.csv
[AIRNOW]: https://www.airnowapi.org/aq/observation/latLong/current/
[NWS]: https://api.weather.gov/gridpoints/DTX/42,30/forecast
[PLANTTALK]: https://github.com/openai/planttalk
[WWC]: https://devpost.com/software/wildfire-watch-canada
[DP-COMP]: https://devpost.com/software/companionai
[TG]: https://devpost.com/software/touch-grass-cvkd4w

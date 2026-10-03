# Pivot Ideas — Past-winner pattern miner

## Prompt given (excerpt)
> You are the Past-winner pattern miner. Work backward from what has actually won MHacks 2020–2025 (Grand Award, main-track/category winners, sponsor winners) and what judges said they reward. Identify the 4–6 strongest recurring winning patterns, then propose ideas that hit those patterns hardest while reusing our build.

*Written Sat Oct 3, 2026, ~5:30 PM EDT. Hacking ends 12:00 PM Sun. Tags: **[V]** I checked it myself today at the linked source. **[F]** From a team research file (named; its own citations apply). **[I]** Inference or estimate. All scores are inference.*

Inputs read in full: `results/year-research/2025.md`, `2024.md`, `2023.md`, `2022.md`, `2021.md`, `2020.md`, and the "Lessons from six years of MHacks winners" and "Cross-check" sections of `results/SUMMARY.md`. I also used the sponsor files for Nessie (12), FREE-WILi (04), FinchNode (10) and Relay (11), and the Fern kit in `fern/`.

---

## TL;DR

| | Idea | Main track | One line | Win | Non-niche | 18 h | Wow | Sponsors | Reuse |
|---|---|---|---|---|---|---|---|---|---|
| **1 (top pick)** | **Hold the Line** | FinTech | Fern, Grandma's houseplant, puts a scam payment on hold in her (Nessie) bank account, asks her for the family safe word, and video-calls the grandkid in Relay before the money leaves | 7 | 8 | 8 | 8 | 8 | 5 |
| 2 | **Sprout** | Beyond the Code (Hardware) | A FREE-WILi strapped to your forearm measures your physical-therapy reps and range of motion in degrees, while Fern counts out loud, grows as you recover, and calls when you skip | 6 | 7 | 5 | 8 | 7 | 5 |
| 3 | **Still Here** | Actually Intelligent (AI) | For older adults living alone: "watering" Fern's pot each morning is the daily check-in. She asks about meds and heart-failure warning signs from the FinchNode record, and if the check-in is missed or something sounds wrong, she texts and then video-calls the family caregiver | 5 | 8 | 7 | 6 | 8 | 7 |

**Top pick: Hold the Line.** It hits five of the six winning patterns. It is the most buildable with this team's web and AI-API skills, with no hardware on the critical path while the FREE-WILi is still being re-flashed. Its demo is something a judge plays a part in, it stops real (sandbox) money, and it competes in the FinTech pool. The research shows plain budgeting apps lose there, and the winners pair finance with a second domain. The cost: **SpaceX is out**, because no space data fits it honestly.

Ideas 1 and 3 share a shell: Fern's escalation to a family member in Relay. Ideas 2 and 3 share the FREE-WILi pot. Whichever one the team picks, roughly the first 6 hours of work carry over to a sibling (§6).

---

## 1. What six years of MHacks winners reward

Weighting follows SUMMARY.md. The in-person relaunch era carries the most weight: MHacks 16 (2023), MHacks 2024 and MHacks 2025. 2020, 2021 and MHacks 15 were small online events judged by the core team, so they count for less. 2022 had no event [F `2022.md`].

### The six strongest recurring patterns

| # | Pattern | Evidence (year → winner) | Strength |
|---|---|---|---|
| **P1** | **Top MHacks-run awards go to a demo you can watch or touch that has a technical core the team built itself.** | 2025 Grand Award: Artificial Sandwich Intelligence, a robot arm running an ACT policy the builder trained himself and benchmarked against a human. 2025 Greenprint: Wattson (FREE-WiLi). 2025 Portal: ScreenWave (accelerometer glove). 2024 Grand Prize: V²/R (VR, with its own circuit solver and no LLM). 2024 Runner-Up: FocusFlow (self-trained LSTM). MHacks 16 1st: DECO.ai (NeRF pipeline). MHacks 15 1st: LumiGUI (Arduino). 2021 1st: SunLite (smart bulb) [F 2025/2024/2023/2021]. | Strong at the top. **Caveat:** on prizes open to everyone, hardware won only 3 of 15 in 2025, so the edge applies to the top awards only [F SUMMARY verdict]. |
| **P2** | **A named, often vulnerable user, plus a statistic and a local hook. Accessibility and health dominate.** | 2025: Dementia Assistant, SoundSense, MobiLens, Gestura and Conversenses all lead with accessibility or health. 2024: 6 of 8 track winners name a specific group (NurseNotes' "41% of a shift is paperwork", SignVerse, Msign, FarmX for Michigan farms). 2023: CogniCare (Alzheimer's), Quick Action (accessibility), LumiGUI (hospital). 2021: MCall used a Michigan Daily statistic, and F.L.U.D.D was about SE Michigan floods. 2020 1st: Dystic, a job finder for disabled job-seekers [F all years]. Usability is a published criterion, and it explicitly includes "accessibility and inclusivity" [F 2025 R1]. | **Strongest and most consistent pattern across all years** |
| **P3** | **An agent that closes the loop in the real world, often with escalation.** | 2025 agent winners sent email, filed GitHub issues (Bazaar, 9+ real issues), negotiated sales and controlled devices. MobiLens sent caregiver and fall alerts. 2021: F.L.U.D.D texted, then escalated to a phone call after 15 minutes, and SunLite was controlled by SMS. BoundaryML's 2024 rubric put "does it demo live" first [F 2025/2024/2021]. | Strong |
| **P4** | **The sponsor's tech is load-bearing and matches that sponsor's own archetype.** | Terminal.AI, a terminal tool, won Warp. ZenStock used Nessie and won Capital One. Every UM ITS winner used ITS's own data. Gestura came out of the FREE-WiLi workshop, and **three FREE-WiLi winners were accelerometer-plus-accessibility builds** (Gestura, thereMINI, Agent Unblind). Cartesia's Boogie Battle made voice essential [F 2023/2024/2025; F sponsor 04]. | Strong for sponsor prizes |
| **P5** | **A character or companion that is funny and actually finished.** | Judy AI (2025 Brainrot: Gemini + ElevenLabs pets). Wattson (a pet that loses health). ASL EVO (an evolving pet, Biff → Buuf → Boof). EscapeMate (Raspberry Pi AI companion). V²/R's "Eely the IA". SunLite's "Larry" brand. 2021 judges said "I would definitely use this" [F 2025/2024/2023/2021]. | Medium-strong. It helps every track, and the fun prizes require it. |
| **P6** | **A participatory, crowd-drawing demo with one hard number.** | MotionSurfer (MHacks 16) credited "attention from mentors and judges". Boogie Battle, osulation!, VSAT. Numbers: Pixzip "93% smaller", SoundSage "<5 ms", ASI vs. a human, Aipeiron cut latency to fit the 3-minute slot [F 2023/2024/2025]. | Medium-strong |

### Facts that shape scoring
- **One prize per project is the norm in person.** In 2024, 30 prizes went to 30 different projects. In 2025, 2 of 30 winners took two. At MHacks 16, 2 of 24 did [F]. Treat sponsor prizes as separate lottery tickets; their EVs don't add up.
- **Format:** a ~3-minute pitch at the team's table, judged repeatedly, with sponsors judging in parallel. MDredd pairwise judging may count an empty table as a strike [F 2025 R14].
- **Health has no main track in 2026,** so P2-style health and accessibility projects will flood "Actually Intelligent", the largest pool (≈47% of 2025 projects listed an LLM) [F verdict]. A P2 project in a **less crowded main track** is the arbitrage.
- **The FinTech pool is estimated at 15–25% of entries** (second-largest). Its winners at peer events paired finance with another domain, and plain budgeting apps lost [F SUMMARY FinTech check; F sponsor 12].

### "Already won / already done" map (checked for every idea)
| Shape | Where it already won | Consequence |
|---|---|---|
| Clean-hours load shifting | 2024 MLH Streamlit (data-center load shifting) | Avoided (and banned by the brief) |
| Pet you keep alive by behaving sustainably | Wattson, 2025 Greenprint + FREE-WiLi | Fern stays a character, not the premise |
| Wrist accelerometer on a FREE-WiLi or glove | Gestura and ScreenWave, both 2025 | Positive precedent for Idea 2, but it must not be a cursor or gesture controller |
| AI companion or memory aid for older adults | CogniCare (MHacks 16), Dementia Assistant (2025 Lifeline); also many outside MHacks | Idea 3's main novelty risk |
| Fraud detection + voice + Nessie | Not at MHacks. **HR Audit won Capital One Best Financial Hack at HackGT 12** ([Devpost](https://devpost.com/software/the-hr-audit)) [V] | Idea 1: positive signal for Capital One judges, but a novelty risk (§2) |

---

## 2. Idea 1 (top pick): **Hold the Line**

**One-liner.** Fern has lived on Grandma's windowsill for twelve years, and now she watches Grandma's bank account too. When a payment looks like a scam (a rushed wire, gift cards, crypto, or a brand-new payee in the middle of a "grandson in jail" story), she puts it on hold as *pending* in Nessie. She asks Grandma for the family safe word, and she texts and then video-calls the trusted grandkid in Relay. The money moves only after a human says "that's really me."

**Main track:** FinTech ("Money, reimagined… faster, fairer, and more accessible for everyone"). Protecting the account holders who lose the most is the "fairer, more accessible" half of that text.
**Fun track:** Judged by an LLM. Not Useless AI, not Dumbest Idea.

### Problem and user (verified)
- **Americans 60+ filed 201,266 complaints and reported $7.7 billion in losses in 2025, more than any other age group.** Their biggest categories were investment ($3.52B) and tech/customer-support scams ($1.04B), and 60+ crypto losses alone were $4.43B ([FBI IC3 2025 Annual Report](https://www.ic3.gov/AnnualReport/Reports/2025_IC3Report.pdf)) [V, read from the PDF].
- **The FTC estimates the real 2024 cost to older adults may be as high as $81.5B**, because most fraud goes unreported ([CNBC on FTC](https://www.cnbc.com/2025/12/13/financial-fraud-seniors-ftc.html)) [V search].
- **Speed is what saves money.** When the FBI's Financial Fraud Kill Chain acted on 642 elder cases in 2025, it froze $32.9M of $65.4M. IC3's own guidance is "time is of the essence" (IC3 2025) [V]. Fern acts *before* the money leaves.
- **The FBI already prescribes the fix, but nobody uses it in the moment:** "Create a secret word or phrase with your family to verify their identity" ([FBI PSA I-120324-PSA, Dec 3, 2024](https://www.ic3.gov/PSA/2024/PSA241203)) [V]. IC3 2025 reports over $5M lost to AI voice-clone "distress" (grandparent) scams [V].
- **There is regulatory precedent for the exact mechanic:** FINRA Rule 2165 lets brokerages place a temporary hold when they suspect exploitation and notify the customer's trusted contact (Rule 4512) ([FINRA FAQ](https://www.finra.org/rules-guidance/guidance/faqs/frequently-asked-questions-regarding-finra-rules-relating-financial-exploitation-seniors)) [V]. Hold the Line brings that hold-and-call-the-trusted-contact pattern to everyday bank payments.
- **Named user for the pitch:** "Margaret, 78, lives alone in Ypsilanti, and her grandson is a U-M sophomore." Every judge has a grandparent [I].

### Sponsor tracks and genuine use
| Sponsor | Genuine use | Status |
|---|---|---|
| **Capital One Nessie** | **Reads** 90 days of purchases, bills, deposits and transfers to build Grandma's baseline. **Writes** every outgoing payment: low-risk ones go through, high-risk ones are created as `status: "pending"` and labelled "Held by Fern". They are then cancelled with `DELETE /transfers/{id}` or released. Nessie's official SDK shows transfers with `status: "pending"` plus PUT and DELETE ([SDK transfer.rb](https://github.com/nessieisreal/nessie-ruby-sdk/blob/master/lib/capital_one/transfer.rb), [spec](https://github.com/nessieisreal/nessie-ruby-sdk/blob/master/spec/capital_one/transfer_spec.rb)) [V]. Show a "Powered by Capital One Nessie" badge on every Nessie figure, per the LoadCheck lesson [F sponsor 12]. | **Core** |
| **Relay** | The trusted contact's channel. A hold card arrives as text, and after N minutes without a reply Fern starts a **video call** using the existing wilted loops. The grandkid answers "not me" or "it's legit" in chat, and that cancels or releases the Nessie transfer. | **Core** (gate: calls on the App Store build) |
| **ElevenLabs** | Fern's existing voice is Grandma's whole interface on a hold ("Before this goes, dear, what's our family word?"), with `eleven_v4_turbo` audio tags, plus speech-to-text on her answer. Voice is essential here, not decorative, which is Boogie Battle's lesson [F 2024]. | **Core** |
| Fetch.ai ASI:One | A "Family Guard" agent on Agentverse. The trusted contact asks "anything held on Mom's account?" in ASI:One and approves or denies, which is a real action. | Optional, only if the core works end to end by ~midnight (hard requirements: Agentverse, Chat Protocol, a video, every teammate joined) [F sponsor 01] |
| FREE-WILi | Grandma's pot, the no-app interface. It speaks the hold, shows the held amount on screen, and has two buttons ("I know them" / "stop it"). | Optional, +3 h, after the FREE-WILi re-flash works |
| Figma | A big-type, high-contrast bank UI for a 78-year-old. That is a real design problem. | Optional |
| SpaceX | **Not eligible.** No real space data fits honestly. | Dropped |

### Why it wins (past evidence)
- **P2:** a named vulnerable user with an FBI statistic, the exact shape of NurseNotes, CogniCare and Dystic.
- **P3:** it acts on money and escalates the way F.L.U.D.D did (text → call). Bazaar's 2025 Fetch win was also a hold-until-verified loop: escrow released only after independent verification [F 2025].
- **P4:** Nessie is used both ways (LoadCheck won VTHacks 14 that way). ZenStock won MHacks 16's Capital One prize with Nessie. **HR Audit won Capital One at HackGT 12 with fraud detection plus voice over Nessie** [V]. That is direct evidence that Capital One judges reward this shape.
- **P5:** Fern, finished and funny ("I'm a fern. I've heard every phone call in this kitchen.").
- **P6:** the judge plays the scammer, and the number on screen is "$2,000 stayed home."
- **Pool:** FinTech's own winners were never plain budgeting apps [F verdict]. A "fairer" safety product stands out from a pool of budgeting and trading apps [I].

### Novelty vs. past winners (honest)
- **No MHacks winner in 2020–2025 did scam interception** [F, all six year files].
- Outside MHacks it is a known theme: HR Audit (above); HughKnew, a voice-clone detector, took 1st at Clawckathon 2026 ([Resemble](https://www.resemble.ai/resources/could-you-tell-your-grandsons-voice-from-a-clone-of-it-hughknew-was-built-to-find-out-safely)); ScamShield is a message checker ([Devpost](https://devpost.com/software/scamshield-v4)) [V].
- **Differentiator:** those classify *messages or voices*. Hold the Line acts *on the payment rail*: it holds the money, runs the FBI's safe-word protocol, and loops in a trusted contact the way FINRA 2165 does. Say this in the first 30 seconds.

### What it reuses (exactly)
- **Fern kit, unchanged:** `fern/assets/fern_normal.png` (Relay profile picture) and the six `fern/assets/video_hd/fern_<mood>_<talking|listening>.mp4` call loops. Wilted means a hold is in progress, blooming means the money stayed home.
- The TypeScript Relay camera player in `fern/README.md`. The ElevenLabs voice `Fern (MHacks 2026)` (`XnLFOJOtoPqkoo60ohxA`) with `fern/voice/make_voice.py` for new lines, and `fern/voice/lipsync.py` for 1–2 pitch clips (~$1–1.5 of xAI credit each).
- **Persona structure** from `fern/persona.md`: the NUMBERS hard rule (only say figures from tool results), the escalation ladder (rung 1 ask, rung 2 call, rung 3 act → becomes ask Grandma, call the trusted contact, cancel the transfer), and the safety section ("stop" ends it, she admits she's an AI). Only the character's job and lines change.
- **Research:** `results/sponsor-tracks/12-capital-one-nessie.md` (HTTPS only, fresh keys start empty so seed your own data, routes, fixture fallback, badge lesson), `11-relay-interactive-agents.md` (workshop cookbook, 422 when no device can take calls), `01-fetchai…` (optional), `06-fun-judged-by-an-llm.md` (Devpost structure).
- **Not reused:** GOES-19, MISO, FIRMS/CelesTrak, IR actuation. **Reuse ≈ 35–40%** of the demo-visible work (the character, voice, call surface and agent scaffolding) [I].

### New work and hours (≈34 person-hours core)
| Owner | Work | h |
|---|---|---|
| P1 (Nessie + backend) | Seed script: Grandma customer, checking account, 90 days of realistic purchases, bills and deposits, a real-grandkid payee and a "Bail Bonds LLC" account. Payment intake API. Hold, release and cancel. Audit log. Fixture fallback | 9 |
| P2 (risk engine + eval) | Deterministic features: new payee, amount z-score vs. 90-day baseline, wire/crypto/gift-card merchant, after-hours, velocity, round amounts. Plus an LLM pass over the payment note and Grandma's spoken answer for scam scripts (urgency, secrecy, authority). The LLM explains but never decides alone. **Eval:** ~120 labelled cases built from IC3's top 60+ crime types plus hard negatives (real tuition help, a new roofer). Report scam recall, false-hold rate and "$ protected" | 8 |
| P3 (voice + Relay) | Relay trusted-contact agent: hold card, approve or deny, video call using the README player. Grandma-side voice loop: ElevenLabs TTS, then STT, then a safe-word check. ~15 new Fern lines | 9 |
| P4 (UI + story) | Big-type "Grandma's bank" web UI and family dashboard (timeline, reasons, Nessie badges). Rubric-shaped Devpost with eval numbers and a "Limitations" section. Pitch and real-life demo video | 8 |
| Optional | FREE-WILi pot (+3) · Fetch.ai Family Guard (+6) · Figma pass (+3) | — |

**Ethics and design guardrails (judges will ask):** the elder can override any hold with a 24-hour cool-off. Holds are capped at amount thresholds she chose. The trusted contact sees holds only, not her full statement. All data is synthetic Nessie data.

### Demo moment (3:00 at the table)
1. **0:00:** "Americans over 60 reported $7.7 billion lost to fraud last year, the most of any age group. The FBI says to set a family safe word. Nobody remembers it mid-panic."
2. **0:20:** Hand the judge a card: *"You're 'Jake'. You're in jail and need $2,000 bail by wire. Tell Grandma not to tell Mom."* The judge pitches the teammate playing Grandma.
3. **0:45:** Grandma taps **Send $2,000** in the big-type bank. The Nessie transfer appears as **pending, held by Fern**. Fern speaks from the pot or laptop: *"[curious] Before this goes, dear, what's our family word?"*
4. **1:10:** A teammate's phone rings (or the judge's, if they have Relay). It's a **Relay video call from wilted Fern**: *"Someone calling himself Jake wants two thousand dollars of bail from your grandma. Was that you?"* "No." → `DELETE` → the dashboard turns blooming: **"$2,000 stayed home"**, with the three reasons that fired.
5. **2:00:** Engineering: the scorer, eval numbers, and Nessie read and write. **2:40:** FINRA-style holds for everyday payments; next steps.

### Data sources verified
- Nessie: up over HTTPS and refuses HTTP [F sponsor 12]. Transfer `status: "pending"`, PUT and DELETE are in the official SDK [V]. **Unverified: whether PUT can change `status` on the live API.** Test in the first 20 minutes. If not, "release" means re-POST as completed.
- IC3 2025 figures [V, PDF text]. FBI PSA safe word [V]. FINRA 2165 [V].

### Risks
- **Judges say "banks already do fraud alerts."** Answer: alerts come after the fact, while this holds the payment, runs the safe-word protocol and brings in a trusted contact. Lead with the hold.
- **Relay calls fail on the App Store build** → fall back to Photon or to a Relay text-only ladder; ElevenLabs still carries the call voice.
- **A self-built eval is circular.** Label it synthetic, publish the cases, and report the false-hold rate prominently.
- **No SpaceX.** The FinTech pool is about 1.5–2× Sustainability's [F verdict].
- **Persona tone:** Fern roasts *scammers*, never Grandma.

**Scores:** win 7 · non-niche 8 · feasibility 8 · demo wow 8 · sponsor fit 8 · reuse 5. *Inference: maybe 55–65% chance of at least one prize, 15–20% for the FinTech main track.*

---

## 3. Idea 2: **Sprout**, a physical-therapy coach that measures you

**One-liner.** Strap a FREE-WILi to your forearm. Fern counts every home-exercise rep out loud, measures your range of motion in degrees from the accelerometer, blooms as your numbers climb, and video-calls you in Relay when you skip two days. Your PT gets a weekly range-of-motion report.

**Main track:** Beyond the Code (Hardware): "circuits, sensors, wearables". **Fun track:** Judged by an LLM.

### Problem and user (verified)
- Non-adherence to home exercise programs runs from 50% to 70% ([overview of systematic reviews, 2024](https://link.springer.com/article/10.1186/s13643-024-02538-9); [Physitrack summary](https://www.physitrack.com/insights/why-patients-stop-home-exercises-adherence-data)) [V search].
- 53.2 million US adults have diagnosed arthritis ([CDC MMWR 2023](https://www.cdc.gov/mmwr/volumes/72/wr/mm7241a1.htm)), and more than 795,000 people a year have a stroke ([CDC](https://www.cdc.gov/stroke/data-research/facts-stats/index.html)) [V search].
- Named user: "a 67-year-old six weeks after a wrist fracture, doing wrist and forearm exercises alone at the kitchen table" [I].

### Sponsor tracks and genuine use
| Sponsor | Genuine use |
|---|---|
| **FREE-WILi** (core) | OneWili `enable_motion_stream` streams the accelerometer ([sensors.py](https://github.com/freewili/onewili/blob/main/python/onewili/menus/sensors.py)) [V]. The screen shows the rep count, degrees and Fern's mood. The 7 LEDs are the per-set progress bar. Buttons are start, skip and "ouch" (pain stops the set and lowers the target). The speaker plays Fern's `.wav` lines through `play_audio_file` ([audio.py](https://github.com/freewili/onewili/blob/main/python/onewili/menus/audio.py)) [V]. **This is the accelerometer-plus-accessibility archetype that won FREE-WiLi three times** [F sponsor 04]. |
| **ElevenLabs** (core) | Counting and coaching in Fern's voice. Numbers 1–20 and about 30 cues are pre-rendered for zero latency. The live call uses `eleven_v4_turbo`. |
| **Relay** (core) | Daily reminder, a wilted-Fern video call after two skipped days, and a weekly progress card (a range-of-motion chart image). |
| Figma | Optional design for the dashboard and PT report. |
| FinchNode | **Weak fit.** No rehab scenario exists in the demo API; I checked the 12 scenarios live [V]. Skip. |
| SpaceX, Fetch.ai | Not used. |

### Why it wins (past evidence)
- **P1 is the strongest of the three ideas:** a wearable sensor plus signal processing the team writes itself (tilt from the gravity vector, filtering, hysteresis rep detection, range of motion per rep), with **measured accuracy**. That is the Grand-Award recipe (built it yourself, benchmark it) at hackathon scale [F 2025 ASI, 2024 Pixzip].
- **P4:** FREE-WiLi's winners were accelerometer and accessibility builds (Gestura, thereMINI, Agent Unblind), and its pool was 5 entrants with 2 winners at MHacks 2025 [F sponsor 04].
- **P6:** the judge straps it on and does reps. That is MotionSurfer's crowd-draw. **P5:** Fern blooms as you recover, which fits "Build something that grows".

### Novelty vs. past winners
- Accelerometer-on-wrist won **twice at MHacks 2025, both times as a cursor or gesture controller** (Gestura, ScreenWave). Sportable (2020 3rd) checked PE form with computer vision [F]. Sprout is clinical measurement plus coaching, a different job.
- Outside MHacks, rehab coaches are common but **webcam-based** (Kinexis, Rehabit) ([Kinexis](https://devpost.com/software/kinexis), [Rehabit](https://devpost.com/software/rehabit-c093se)) [V search]. Hinge Health and Sword do this commercially, which is proof the problem is real, but say so up front.

### What it reuses
Fern's six call loops (mood follows the adherence streak), the voice and `make_voice.py`, the README camera player, the persona's numbers rule and ladder (remind → call), FREE-WILi research (`04-free-wili.md`: install OneWili from source, the 1–2 PM session notes) and the device itself. **Reuse ≈ 40%** [I].

### New work and hours (≈32 person-hours)
| Owner | Work | h |
|---|---|---|
| P4 (hardware) | OneWili motion stream at about 50 Hz. Tilt (pitch/roll) with a low-pass filter, accepting samples only when the magnitude is near 1 g, because the OG has **no gyroscope** (`ponytail:` comment; this is fine for slow PT moves). Neutral-pose calibration (the calibration knob). Per-exercise hysteresis rep detector for wrist flexion/extension, pronation/supination and shoulder raise. Strap. LEDs and screen | 10 |
| P2 (eval) | 3 people × 10 sets with hand-counted reps, and angles checked against a phone clinometer at 0/30/60/90°. Report rep accuracy and mean angle error | 5 |
| P1 (agent + voice) | Relay reminders, skip call, weekly card. ~50 voice lines | 9 |
| P3 (dashboard + story) | Range-of-motion trend, PT CSV/PDF export, Devpost, video | 8 |

### Demo moment
The judge straps the FREE-WILi on and does five wrist curls. Fern counts aloud, *"three… four… [excited] five! Sixty-two degrees, eight more than Tuesday!"*, while the LEDs fill and Fern blooms on the screen. Then "skip two days" is fast-forwarded, and a teammate's phone gets a Relay video call from wilted Fern.

### Risks
- **The FREE-WILi is being re-flashed now.** The OneWili motion stream on the OG is unverified and needs a 45-minute test. The fallback is a phone's DeviceMotion, which weakens the Hardware track.
- The team has little hardware experience, and Wattson called the API "a huge learning curve" [F sponsor 04].
- In the Hardware pool a FREE-WILi is "the floor, not a differentiator" [F verdict]. The signal-processing core and the accuracy numbers must carry the pitch.
- Medical framing: say "not a medical device; your PT sets the targets."

**Scores:** win 6 · non-niche 7 · feasibility 5 · demo wow 8 · sponsor fit 7 · reuse 5.

---

## 4. Idea 3: **Still Here**, the houseplant that checks on Grandma

**One-liner.** For older adults living alone, the daily check-in *is* watering the plant. Each morning Grandma presses Fern's pot (a FREE-WILi), and Fern spends about a minute asking about her morning meds, today's weight and her breathing, using her FinchNode health record. If the check-in is missed, or a heart-failure warning sign shows up, Fern texts and then video-calls the family caregiver in Relay.

**Main track:** Actually Intelligent (AI). **Fun track:** Judged by an LLM.

### Problem and user (verified)
- **16.2 million (28%) of community-dwelling Americans 65+ live alone** ([ACL 2023 Profile of Older Americans](https://acl.gov/sites/default/files/Profile%20of%20OA/ACL_ProfileOlderAmericans2023_508.pdf)) [V search].
- Lacking connection raises the risk of early death about as much as smoking 15 cigarettes a day, and about 1 in 4 older adults are socially isolated (Surgeon General advisory, 2023; [NPR](https://www.npr.org/2023/05/02/1173418268/loneliness-connection-mental-health-dementia-surgeon-general)) [V search].
- **63 million Americans are family caregivers** ([AARP 2025](https://www.aarp.org/press/releases/2025-07-24-new-report-reveals-crisis-point-for-americas-63-million-family-caregivers.html)) [V search].
- **The plant hook is real research:** in Langer & Rodin's nursing-home study, residents given responsibility (including caring for their own plant) had 15% mortality at 18 months, versus 30% for the comparison group ([Garfield classic summary](https://garfield.library.upenn.edu/classics1985/A1985ASW0900001.pdf); [Gerontologist retrospective](https://academic.oup.com/gerontologist/article/54/1/67/558565)) [V search]. **Caveat for the pitch:** the plant was one part of a broader responsibility intervention, and critics have re-examined the study ([Coyne](https://www.coyneoftherealm.com/2014/11/05/re-examining-ellen-langers-classic-study-giving-plants-nursing-home-residents/)). Say "inspired by", not "proven by".
- Clinical anchor: the AHA advises heart-failure patients to call their clinician after a 2–3 lb gain in a day or 5 lb in a week ([AHA](https://www.heart.org/en/health-topics/heart-failure/treatment-options-for-heart-failure/lifestyle-changes-for-heart-failure)) [V search].

### Sponsor tracks and genuine use
| Sponsor | Genuine use |
|---|---|
| **FinchNode** (core) | The keyless demo API's `polypharmacy-senior` record (age 78: 14 active meds, CKD 3, AFib, heart failure, 40 labs, 30 vitals) drives which meds Fern asks about and switches on the heart-failure weight rule. I called `/scenarios` live today [V]. "A named user and a care moment… data that changes what happens" is the FinchNode advocate's rubric [F sponsor 10]. |
| **Relay** (core) | The caregiver's channel: a daily summary text, then on red flags a text followed by a wilted-Fern video call. |
| **ElevenLabs** (core) | Fern's voice is the elder's whole interface (no app, no screen to learn). |
| **FREE-WILi** (core) | The pot: a button means "watered" (checked in), the screen shows the mood, LEDs show the streak, and the speaker plays Fern. OneWili `record_audio_file` exists for the mic [V], with the laptop mic as fallback. |
| SpaceX (optional, +3 h) | Smoke-day check-ins. The GOES-19 ABI-L2-ADPC (aerosol/smoke detection) and AODC files exist for **July 16, 2026** [V S3], the day Detroit had the world's worst air ([Detroit News](https://www.detroitnews.com/story/news/local/michigan/2026/07/16/detroit-has-most-polluted-air-in-world-due-to-wildfire-smoke-today/90939851007/)) [V search]. Replay it, labelled as a replay. Fern was already made with Grok Imagine. It still needs Cursor. |
| Fetch.ai | Optional: "how's Mom this week?" in ASI:One. |

### Why it wins (past evidence)
- P2 is at its strongest here: the same shape as CogniCare (MHacks 16 Social Impact), Dementia Assistant (2025 Lifeline) and MobiLens (2025 Fetch Best Use, with caregiver alerts) [F].
- P3: F.L.U.D.D's text → call ladder [F 2021].
- P5 is the best persona fit of the three. Fern *literally* needs watering, and her blooming/normal/wilted moods map one-to-one to checked-in / not yet / missed.
- It has the largest sponsor stack, all genuine (FinchNode, Relay, ElevenLabs, FREE-WILi, and optionally SpaceX).

### Novelty vs. past winners (the weak spot)
- The "AI companion for elders" shape **has already won at MHacks twice** (CogniCare, Dementia Assistant). Outside MHacks it is crowded: ClaraCare, ForeverYours, Caregiver Check-In, CareCompanion and VoiceCare ([search results](https://devpost.com/software/claracare)), and commercially ElliQ (proactive check-ins, $250 plus a monthly fee) ([ElliQ](https://elliq.com/)) [V search].
- What makes it different: a no-screen physical ritual grounded in the plant study, a caregiver loop over video, and FinchNode-grounded clinical rules.

### What it reuses
The highest reuse of the three, **≈55%**: the persona needs almost no change ("Digital Garden" → Grandma's windowsill), plus all six loops, the voice, the ladder, the README player, the FREE-WILi device and research, `10-finchnode-healthtech.md` (keyless API, MCP, gotchas), and the GOES-19 S3 notes in SUMMARY §4.3 for the optional smoke hook.

### New work and hours (≈31 person-hours, +3 for smoke)
P4: FREE-WILi pot (button, wav playback, screen mood, LEDs), 6 h. P2: check-in brain (STT → LLM structured extraction of meds taken, weight, breath, swelling, mood and falls; baseline deviation; the AHA rule) plus a ~40-case labelled eval, 9 h. P1: Relay caregiver agent and call ladder, 8 h. P3: caregiver dashboard and Devpost, 8 h.

### Demo moment
A fast clock passes 10 AM with no "watering". Fern wilts on the pot screen, and the caregiver's phone gets a Relay text and then a video call: *"Your mom hasn't watered me this morning. Yesterday she said her ankles were puffy, and she's up three pounds since Tuesday."* Grandma presses the pot, Fern blooms, and they have a short check-in.

### Risks
- Novelty, as above.
- The AI main track is the largest pool.
- Health-advice liability: use deterministic rules first, cite every flag's source, and frame it as "call your clinician."
- The OneWili mic path is unverified.
- A slower demo beat than Idea 1.

**Scores:** win 5 · non-niche 8 · feasibility 7 · demo wow 6 · sponsor fit 8 · reuse 7.

---

## 5. Pattern scorecard

| Pattern | Hold the Line | Sprout | Still Here |
|---|---|---|---|
| P1 physical demo + core the team built | ◐ (optional pot; the risk scorer is the core) | ● | ◐ |
| P2 named vulnerable user + statistic | ● ($7.7B, FBI) | ● (50–70% non-adherence) | ● (16.2M alone) |
| P3 closes a real-world loop | ● (holds money) | ◐ | ● |
| P4 sponsor load-bearing + archetype | ● (Nessie both ways; HR Audit precedent) | ● (FREE-WiLi accelerometer archetype) | ● (FinchNode polypharmacy) |
| P5 character, funny and finished | ● | ● | ● (best fit) |
| P6 participatory + one number | ● (judge plays scammer; "$2,000 stayed home") | ● (judge does reps; degrees) | ◐ |
| Already done at MHacks? | No | Partly (wrist accelerometer, different job) | **Yes, twice** |
| Main-track pool | FinTech, medium | Hardware, small but hardware-heavy | AI, largest |

## 6. Top pick and how to move fast

**Hold the Line.** Of the three, it is the only one that:
- hits P2, P3, P4 and P6 at full strength;
- has **no MHacks precedent** but has **direct evidence that Capital One judges reward the shape** (HR Audit, ZenStock, LoadCheck);
- needs **no hardware on the critical path**, which matters for a web/AI team with a FREE-WILi still being re-flashed;
- lands in a mid-size pool where budgeting apps are the norm.

The FREE-WILi pot and Fetch.ai are add-ons that can be cut at midnight without breaking the demo.

**First 60 minutes (gates):**
1. **Nessie (20 min):** create a customer and account, POST a transfer with `status: "pending"`, then try PUT status and DELETE.
2. **Relay:** did calls ring at the 1 PM workshop? If not, the ladder is text plus Photon.
3. **Persona:** re-script Fern's lines and render 15 with `make_voice.py`.
4. **Freeze the pitch's three numbers:** $7.7B, 201,266 complaints, and the FBI safe-word PSA.

**Pivot path:** if Nessie writes misbehave, the same Fern → Relay escalation shell becomes **Still Here** (FinchNode replaces Nessie, about 6 hours carry over). If the FREE-WILi re-flash works early and someone wants hardware, **Sprout** is the Hardware-track option.

---

## Sources

**Team research (read in full)**
- `/Users/anvaytodkar/Code/mhacks/results/year-research/2025.md`, `2024.md`, `2023.md`, `2022.md`, `2021.md`, `2020.md`
- `/Users/anvaytodkar/Code/mhacks/results/SUMMARY.md` (Lessons from six years; Cross-check; FinTech check)
- `/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/12-capital-one-nessie.md`, `04-free-wili.md`, `10-finchnode-healthtech.md`, `11-relay-interactive-agents.md`, `13-debate-and-verdict.md`; `/Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md`
- `/Users/anvaytodkar/Code/mhacks/fern/README.md`, `/Users/anvaytodkar/Code/mhacks/fern/persona.md`

**Past winners cited (via the year files)**
- Artificial Sandwich Intelligence https://devpost.com/software/artificial-sandwich-intelligence · Wattson https://devpost.com/software/wattson-5btsyd · Gestura https://devpost.com/software/gestura-9oaugq · ScreenWave https://devpost.com/software/screenwave · Dementia Assistant https://devpost.com/software/dementia-assistant · MobiLens https://devpost.com/software/mobilens · Bazaar https://devpost.com/software/bazaar-ai-agent-marketplace-fetch-ai · Judy AI https://devpost.com/software/judy-ai-4vc9ah
- V²/R https://devpost.com/software/v-r · FocusFlow https://devpost.com/software/focusflow-ucwma0 · NurseNotes https://devpost.com/software/nursenotes · Boogie Battle https://devpost.com/software/boogie-battle · Pixzip https://devpost.com/software/shrinking-size-amplifying-brilliance · Dynamic Load Balancing https://devpost.com/software/dynamic-load-balancing-for-energy-efficient-cloud-computing
- DECO.ai https://devpost.com/software/deco-ai · ZenStock https://devpost.com/software/zenstock · CogniCare https://devpost.com/software/cognicare-companion-app-for-memory-support · MotionSurfer https://devpost.com/software/motionsurfer · LumiGUI https://devpost.com/software/lumigui
- SunLite https://devpost.com/software/sunlite-sunrise-lamp · F.L.U.D.D https://devpost.com/software/f-l-u-d-d · Dystic https://devpost.com/software/dystic · Sportable https://devpost.com/software/sportable
- Other events: HR Audit (HackGT 12, Capital One Best Financial Hack) https://devpost.com/software/the-hr-audit [V] · LoadCheck https://devpost.com/software/loadcheck · thereMINI https://devpost.com/software/theremini · Agent Unblind https://devpost.com/software/agent-unblind

**Checked today**
- FBI IC3 2025 Annual Report (60+: 201,266 complaints, $7.7B; FFKC elder freezes; distress scams): https://www.ic3.gov/AnnualReport/Reports/2025_IC3Report.pdf
- FBI PSA I-120324-PSA (family secret word): https://www.ic3.gov/PSA/2024/PSA241203
- FTC estimate up to $81.5B (2024): https://www.cnbc.com/2025/12/13/financial-fraud-seniors-ftc.html
- FINRA Rule 2165 / 4512 FAQ: https://www.finra.org/rules-guidance/guidance/faqs/frequently-asked-questions-regarding-finra-rules-relating-financial-exploitation-seniors
- Nessie SDK transfers (pending status, PUT, DELETE): https://github.com/nessieisreal/nessie-ruby-sdk/blob/master/lib/capital_one/transfer.rb · https://github.com/nessieisreal/nessie-ruby-sdk/blob/master/spec/capital_one/transfer_spec.rb
- Prior art: HughKnew https://www.resemble.ai/resources/could-you-tell-your-grandsons-voice-from-a-clone-of-it-hughknew-was-built-to-find-out-safely · ScamShield https://devpost.com/software/scamshield-v4
- OneWili sensors and audio: https://github.com/freewili/onewili/blob/main/python/onewili/menus/sensors.py · https://github.com/freewili/onewili/blob/main/python/onewili/menus/audio.py
- HEP adherence: https://link.springer.com/article/10.1186/s13643-024-02538-9 · https://www.physitrack.com/insights/why-patients-stop-home-exercises-adherence-data
- CDC arthritis: https://www.cdc.gov/mmwr/volumes/72/wr/mm7241a1.htm · CDC stroke: https://www.cdc.gov/stroke/data-research/facts-stats/index.html
- Rehab prior art: https://devpost.com/software/kinexis · https://devpost.com/software/rehabit-c093se
- ACL 2023 Profile of Older Americans: https://acl.gov/sites/default/files/Profile%20of%20OA/ACL_ProfileOlderAmericans2023_508.pdf
- Surgeon General loneliness advisory (NPR): https://www.npr.org/2023/05/02/1173418268/loneliness-connection-mental-health-dementia-surgeon-general
- AARP Caregiving in the US 2025: https://www.aarp.org/press/releases/2025-07-24-new-report-reveals-crisis-point-for-americas-63-million-family-caregivers.html
- Langer & Rodin: https://garfield.library.upenn.edu/classics1985/A1985ASW0900001.pdf · https://academic.oup.com/gerontologist/article/54/1/67/558565 · critique https://www.coyneoftherealm.com/2014/11/05/re-examining-ellen-langers-classic-study-giving-plants-nursing-home-residents/
- AHA heart-failure weight guidance: https://www.heart.org/en/health-topics/heart-failure/treatment-options-for-heart-failure/lifestyle-changes-for-heart-failure
- Elder-companion prior art: https://devpost.com/software/claracare · https://elliq.com/
- FinchNode demo scenarios (called live): https://api.finchnode.com/demo/v1/scenarios
- GOES-19 smoke products for 2026-07-16: https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-ADPC/2026/197/ · Detroit worst air, July 16, 2026: https://www.detroitnews.com/story/news/local/michigan/2026/07/16/detroit-has-most-polluted-air-in-world-due-to-wildfire-smoke-today/90939851007/

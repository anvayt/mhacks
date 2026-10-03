# Main Track Advocate — Beyond the Code (Hardware)

## Prompt given (excerpt)
> You are the advocate for the main track "Beyond the Code (Hardware)" at MHacks 2026. Research how it is judged, how crowded it will be, what has won analogous categories, how it stacks with the fun and sponsor tracks, three project directions, honest weaknesses, and a 1–10 scorecard. Make the strongest honest case — an impartial judge will weigh your file against five other track advocates.

---

## Bottom line

Hardware is the **least crowded main track with the best recent win record at MHacks itself**. It pays the same $2,500 as every other main track [H2]. In 2025, physical builds were about 11% of MHacks submissions, but they took the **Grand Award, the Portal track and the Greenprint track** (3 of 6 MHacks-run prizes) plus the $1,000 Best Hardware Hack prize [M25a–M25f]. The same kind of project has recently taken top overall prizes at TreeHacks 2026, TreeHacks 2025 (3rd) and PennApps XXV [P1–P4].

The cost is execution risk. We have 24 hours, parts are first-come-first-served, and the team's hardware experience is unknown. **Choose this track only if one teammate will own the electronics from minute one.** If someone will, the expected value is better than the AI track: the pool is far smaller and the judging pitch is easier. It also avoids FinTech's crowd while still reaching Capital One's Nessie prize. The recommended direction (Direction A below) stacks naturally with the team's favorite sponsor track, SpaceX "Make it Legendary".

---

## 1. What the track rewards and how it is likely judged

**Official facts (2026 Hacker Handbook, found via MHacks' own dashboard repo [H0]):**
- Track text: "Push past the screen. Build physical, tangible tech — circuits, sensors, wearables, robotics." Each main track awards **$2,500**. The **Grand Prize is $5,000 cash** [H2].
- Hacking runs **12 PM Oct 3 to 12 PM Oct 4 (24 h)**. Teams have 1–4 people. "All coding and building must be done during the hackathon." [H1]
- **Judging** happens at the Duderstadt Center, Sun Oct 4, 12:30–2:30 PM. Each team gets a **three-minute window** to present. Projects "may be judged more than once by different judges." Judges score "innovation, technical complexity, usability, and presentation quality." Sponsors judge their own tracks at the same time, and teams must be present to be judged [H1].
- **Hardware resources**: "MLH provides these resources, which will be distributed on a first-come, first-served basis" [H1]. They link to the MLH Hardware Lab list [MLH], which includes 9 Raspberry Pi 4B kits, 12 Arduinos with base shields, 8 webcams, Grove sensors (accelerometer, ultrasonic, light, sound, touch, air quality, etc.), 4 Grove servos, 3 stepper motors, LCDs, breadboards and a multimeter. *Unverified:* whether MHacks gets the full list or a subset.
- The site says MHacks is "24 hours of creative engineering, design, building, and prototyping that blur the line between code and the real world" [S1]. The FAQ says past projects "have spanned AI agents, hardware, wearables, climate tools, games, creative installations" [S1].
- Live schedule, today: **FREE-WILi session 1–2 PM (Room 3336)**, **Theta Tau Embedded Systems Workshop 3–4 PM**, and Spot / Go2 robot demos [S2].

**What that means (inference):**
- A 3-minute pitch scored on innovation, complexity, usability and presentation strongly favors something a judge can **see move, light up, or react within 10 seconds**. A physical object works better there than a slide or a scrolling web app. Hardware also scores "technical complexity" by default, because firmware plus wiring plus software reads as harder than an API wrapper.
- Possible re-judging by several judges makes **reliability** a scoring factor. A demo that breaks on the second judge pass hurts us.
- The track text lists four sub-genres. A project hitting two of them (e.g. sensor + actuator, or wearable + sensor) is squarely in scope. A project that only reads a phone's sensors is not.

## 2. Competition density

**Measured base rate (my own scrape of every MHacks Devpost project page; keyword heuristic, so treat as ±a few projects):**

| Year | Projects | Physical builds (MCU/SBC/robot/custom wearable) | Physical builds that won ≥1 prize | All projects that won ≥1 prize |
|---|---|---|---|---|
| 2025 | 122 [M25a] | ~13 (~11%) | **7 of 13 (54%)** | 30 of 122 (25%) |
| 2024 | 133 [M24a] | ~3 (~2–3%) | **3 of 3** | 30 of 133 (23%) |

For 2025, I excluded projects whose only "hardware" was a sponsor-supplied AR headset or the MemryX accelerator alone. Counting them would raise hardware's share to ~24%.

**For comparison, from the same scrape:** projects that mention LLM/AI APIs at least twice were **57% of 2025 submissions (70/122)** and **49% of 2024 (65/133)**. Finance/crypto keywords appeared in ~15% of 2025 projects (18/122), driven by a Solana sponsor track that year [M25b].

**2026 estimate (inference):**
- Every team must pick exactly one main track [H2 / team brief]. Most of the 2025 AI-heavy majority will default to "Actually Intelligent". FinTech will draw the Nessie and Spacetime crowd, since Spacetime's own track text pitches "trading / financial-style apps" and "prediction market[s]" [H2]. Hardware needs parts, and the parts are first-come-first-served, which self-selects a small pool.
- Expected hardware share: **~10–20% of submissions**. 2025 already reached ~11% without a hardware main track, and a $2,500 track plus FREE-WILi on site should raise it somewhat. Devpost totals were 122–133 projects in 2024–25 [M24a, M25a]. The site advertises "1,000+" builders [S1], but 2025's Devpost showed 380 participants [M25b]. So the hardware pool is likely **~15–35 teams**, versus perhaps 60–100+ in AI. *All inferred; nobody publishes per-track counts.*
- Quality matters as much as quantity. Many hardware entries at student hackathons are half-working sensor dashboards. A **reliable** physical demo is likely already top-third of the pool.

## 3. Precedent: what actually won

**MHacks itself (strongest evidence, same judges' culture):**
- **2025 Grand Award ($4,000): *Artificial Sandwich Intelligence*.** LeRobot SO-101 robot arms ("just $200 of hardware") with a self-trained masked-transformer (ACT) policy that makes a sandwich autonomously [M25c, M25b].
- **2025 Best Hardware Hack ($1,000, Embedder): *Conductor*.** An AI agent turns natural-language commands into hardware actions on Arduino/Raspberry Pi with IR sensors, buzzers and servos ("gives LLM irl hands and eyes") [M25d].
- **2025 Portal track: *ScreenWave*.** A glove with three accelerometer/magnetometer sensors on Arduinos. Rotating your hand moves a cursor and pinching clicks, for projector presentations [M25e].
- **2025 Greenprint (Sustainability) track + Best Use of FREE-WiLi: *Wattson*.** OpenCV plus a UI running on the FREE-WILi handheld [M25f]. So a hardware build won the *sustainability* track too.
- **2025 Best Use of FREE-WiLi: *Gestura*.** A gesture mouse using the FREE-WILi accelerometer plus offline voice commands, for accessibility [M25g].
- 2024: *EscapeMate* (Raspberry Pi puzzle box) won the Interactive Media & Gaming track. *Wili-Party* won Best Use of FREE-WILi. *The WiLi Watch* (FREE-WILi wristband + Orange Pi + Arduino, smart-home control for movement-impaired users) won Best App Built on Groq [M24b–M24d].
- Counterexample, to be fair: the **2024 Grand Prize** went to *V²/R*, a software-only VR breadboard simulator [M24e].

**Peer hackathons:**
- **TreeHacks 2026 Grand Prize: *Shepherd*.** A motorized smart cane for visually impaired users that uses computer vision to detect obstacles and steer [P1].
- **TreeHacks 2025:** *Portable Braille* (Arduino/ESP32 device, 3D-printed) took **Grand Prize 3rd place** plus NVIDIA's Robo Prize [P2]. *BrailleBot*, a sub-$15 braille embosser built on a low-cost 3D printer, won Best Hardware Hack [P3]. *Therms*, a Peltier-module thermoregulation wearable, won 2nd in the Healthcare Grand Prize [P4].
- **PennApps XXV Best Overall 1st: *SoundShield*.** A Raspberry Pi wearable headphone that adapts audio for autistic users and alerts when someone is behind them [P5]. Best Overall 3rd was *SurgeVue* (AR + Arduino gyroscope hand tracking) [P6].
- **Cal Hacks 11.0 Best Hardware Hack: *PulseWalk*.** A smart shoe with IR sensors and 5 servos giving haptic terrain/obstacle feedback for blind users [P7].
- Counterexample: Cal Hacks 12's grand prize went to *FaceTimeOS*, a software computer-use agent. The winners stress that "judges only see the presentation" and that UI and demo polish matter most [P8].

**Pattern:** hardware winners (1) solve a concrete human problem, very often accessibility or health; (2) put **AI inside a physical loop** (sense → model → actuate); (3) use cheap, legible parts (a $200 arm, a $15 embosser, a glove); and (4) demo in seconds. Smart canes and haptic aids for blind users are the most common archetype, so we should *not* build the 50th smart cane.

## 4. Win levers

1. **A 10-second "it moved" moment.** The judge should see a physical reaction to something they do or say before you finish your first sentence.
2. **AI in the loop, not on the side.** Conductor and Artificial Sandwich Intelligence won because the model *drives* the hardware [M25c, M25d]. That also scores "technical complexity".
3. **Reliability over ambition.** Two judges may visit [H1]. Build a "demo mode" with a fallback path, charged batteries, and a hard reset under 10 seconds.
4. **Calibration knobs.** Real sensors drift: magnetometers read off, servos overshoot. Expose a manual offset/zero setting instead of trusting the ideal math.
5. **Enclosure and story.** Cardboard or a 3D print beats loose breadboard wires for "usability" and "presentation quality". Tie the device to a specific person's problem.
6. **Claim parts at 12:00 PM sharp** (first-come-first-served [H1]), or bring your own common modules. *Verify with organizers* that bringing un-assembled off-the-shelf parts is fine under "all building must be done during the hackathon" [H1].
7. **Use the free on-site help:** the FREE-WILi session at 1 PM and the embedded systems workshop at 3 PM [S2].

## 5. Stacking (one coherent project)

The main track is fixed as Hardware. Everything below is additive [H2].

**Strong fits:**
- **SpaceX "Make it Legendary"** (team's favorite). Requirements: real space data in, "built with Cursor", and use of "the Grok Imagine or Voice API" [H2]. Hardware gives space data a physical body, such as a device that points at satellites. Grok's Voice Agent API is a realtime WebSocket speech-to-speech API with function calling [X1]. A LiveKit Agents plugin exists for it [X3]. Grok Imagine generates images/video [X2]. Free real data: CelesTrak GP/TLE JSON [D1], wheretheiss.at [D2].
- **Relay "Interactive Agents"** ("text, call and video chat with" an agent in the Relay app) [H2]. Relay calls can be answered by a **LiveKit Agents** session or a Pipecat pipeline, and agents can read the caller's camera on video calls [R1, R2]. *Inferred:* one LiveKit voice agent using Grok Voice could satisfy SpaceX's Voice-API rule **and** be callable in Relay, making the device "phone-able". Unverified end-to-end; prototype the Relay connection first.
- **Best Use of FREE-WILi.** The device has a 9-DOF IMU, mic array, speaker, IR TX/RX, touchscreen, Wi-Fi/BLE/LoRa and 25 GPIO, with a Python API [F1, F2]. It has gone to hardware projects both years (2024 and 2025) [M24c, M25f, M25g]. It is also a whole wearable or handheld in one box, which removes most wiring risk.
- **ElevenLabs.** Any device that talks. Every participant who uses it gets one month of the Creator tier [H2].
- **Notability "Trust the Process".** You qualify by using Notability Pro for ideation or wireframing, tagging it, and adding 2 screenshots [H2]. Nearly free for any project.
- **Fun tracks:** *Dumbest Idea* and *Useless AI* fit a physical gag naturally. A dumb robot is funnier in person than a dumb web app (inference).

**Conditional fits:**
- **Capital One Nessie.** Fits if the device reacts to (mock) bank data: accounts, merchants, bills, P2P [H2]. See Direction C.
- **FinchNode (HealthTech).** Fits a health wearable that reads synthetic patient records (meds, conditions, allergies) through FinchNode's sandbox [H2, FN1]. The Apple Watch SE3 prize is attractive.
- **Photon iMessage.** The device's agent texts you over iMessage, but you must use Photon's Spectrum framework [H2]. It overlaps Relay, so pick one.
- **SpacetimeDB.** Fits only if live shared state is core, e.g. several devices or users syncing in real time [H2]. A telemetry dashboard alone is "added on the side", which they explicitly don't want.
- **Fetch.ai ASI:One.** You could register the device-controlling agent on Agentverse. Conductor-style "agent with hands" is on-theme. But Fetch wants "real utility, autonomy" and a separate submission agent [H2], so it is real extra work.

**Weak or conflicting:**
- **Judged by an LLM.** *Inferred:* an LLM judge likely reads the write-up, repo or video, so the physical "wow" is lost. Enter anyway (no cost), with a rigorous technical write-up.
- **Figma Best Design** goes to UI-heavy entries (inference). Enter only if the companion app is designed in Figma.
- **Neon.** You *can* store telemetry in Neon, but "utilizing Neon to its fullest" [H2] isn't natural here.
- Realistic ceiling: **3–4 sponsor integrations** done well in 24 h, plus Notability and the fun tracks.

## 6. Three project directions

**Direction A (recommended): "Skyward", a desk-sized satellite pointer you can call.**
A two-servo pan/tilt mount points a physical arrow, plus an LED that glows brighter as the target rises, at the ISS or a chosen satellite **through the ceiling, in real time**. It computes position from CelesTrak TLEs [D1] (fallback: wheretheiss.at [D2]) and the venue's lat/long. A Grok Voice agent [X1] answers questions like "When can I see the ISS from Ann Arbor tonight?" or "Point at the newest Starlink launch", and moves the mount by function call. The same agent is reachable through a **Relay call** [R2]. Grok Imagine [X2] renders a "postcard from orbit" of what the satellite is passing over right now, shown on the FREE-WILi screen or a laptop. Built in Cursor per the SpaceX rule [H2].
- Parts: 2 servos (MLH lab has 4 [MLH]), an Arduino or FREE-WILi, a cardboard or 3D-printed mount. Include a **manual "north/zero" calibration knob**, because compass headings indoors will be wrong.
- Stacks: Hardware + **SpaceX** + **Relay** + ElevenLabs (optional narration voice) + Notability + Useless AI / Judged-by-LLM.
- Why it wins: the 10-second moment is the arm swinging to "the ISS, right there, 410 km up". It is real data, AI in the loop, and impossible to fake with a slide.

**Direction B: "Tremor-to-Text" / "Steady", a FREE-WILi health companion wired to a real-shaped record.**
A wrist- or table-mounted FREE-WILi uses its IMU and microphone [F1] to log medication-taking events. Shake the pill bottle and the device registers it, or speak "took my metformin". It checks the dose against a **FinchNode synthetic patient's medication list and allergies** [FN1], and speaks a confirmation or warning in an ElevenLabs voice. If a dose is missed, an agent **calls or texts the caregiver via Relay** [R1]. It is close to the winning 2024 *WiLi Watch* and 2025 *Gestura* patterns [M24d, M25g], but aimed at a FinchNode prize.
- Stacks: Hardware + **FinchNode** + **FREE-WILi** + **Relay** + ElevenLabs + Notability.
- Why it wins: very low wiring risk (one device), clear health impact, and three sponsor prizes from one coherent story. Risk: it feels less "built" than Direction A unless it gets a real enclosure.

**Direction C (fun-track maximizer): "Piggy Bank of Judgment".**
A piggy bank whose servo-locked slot, buzzer and LCD react to your **Nessie** account. A coffee purchase from the mock merchant data and the pig audibly sighs. A bill coming due and it locks itself and roasts you in an ElevenLabs voice. Overspending on the mock P2P transfers sends a passive-aggressive text through Photon or Relay. It reaches Capital One's prize ($300 per member [H2]) without entering the crowded FinTech main track.
- Stacks: Hardware + **Capital One Nessie** + **Dumbest Idea** + **Useless AI** + ElevenLabs + Photon *or* Relay + Notability.
- Why it might win: the funniest booth in the room, and the fun-track judges get an in-person gag. Risk: weaker on the main-track "impact" criterion, so it is better as a backup if parts or skills are thin.

## 7. Honest weaknesses, rival arguments, rebuttals

| Rival argument | Honest assessment | Rebuttal |
|---|---|---|
| "Your team has no confirmed hardware experience; you'll burn 10 hours debugging wiring." | **The biggest real risk.** | Use FREE-WILi or Grove (plug-in, no soldering) [MLH, F1]. Keep the scope to 2 servos or 1 device. Attend the 1 PM FREE-WILi and 3 PM embedded workshops [S2]. If nobody will own the hardware, pick another track. |
| "Parts are first-come-first-served; you may get nothing." | Real [H1]. The MLH list has only 4 servos and 3 ultrasonic sensors [MLH]. | Be at the hardware desk at 12:00. Have a FREE-WILi-only fallback for each direction. Bring own common modules if organizers allow. |
| "Build your hardware but enter the AI track instead; a hardware demo wins anywhere." | Partly true: Wattson won Sustainability in 2025 [M25f]. | That puts you in a pool 3–5× larger, where judges may score you as "AI project with a gimmick". In the Hardware pool you compete with ~15–35 mostly shakier builds (inferred) for the same $2,500, and still qualify for the $5,000 Grand Prize. |
| "Hardware demos break." | True. | Demo mode, scripted 3-minute run, a recorded backup video for Devpost, a hard reset. Reliability is itself a differentiator in this pool. |
| "The LLM-judged fun track and Figma can't appreciate physical work." | Mostly true (inferred). | Those are minor prizes. The ones that matter here are SpaceX, Relay, FREE-WILi, Nessie and FinchNode. |
| "FinTech/AI have more sponsor overlap (Nessie, Spacetime, Neon, Fetch)." | True for FinTech's Nessie and Spacetime [H2]. | Direction C reaches Nessie from Hardware anyway. Agent sponsors (Relay, Fetch, Photon) work with a device just as well as with a chat UI. |
| "MHacks 2024's grand prize was software." | True [M24e]. | 2025's was a robot arm [M25c], and hardware won top overall prizes at TreeHacks 2026, TreeHacks 2025 (3rd) and PennApps XXV [P1, P2, P5]. Trend favors physical AI. |
| "Accessibility hardware is a cliché (canes, braille)." | True [P1–P3, P7]. | That's why Direction A is a space device, not a cane. Direction B is meds/caregiving, not navigation. |

## 8. Scorecard (1–10)

| Criterion | Score | Justification |
|---|---|---|
| Win probability (main track $2,500) | **7** | Smallest pool, and hardware won 54% of the time at MHacks 2025 versus 25% overall [scrape of M25a]. Capped by unknown team hardware skill. |
| Competition (10 = least crowded) | **8** | ~11% of 2025 submissions were physical builds versus ~57% AI-heavy. A dedicated track will grow the pool somewhat (inferred). |
| Feasibility in 24 h | **5** | Parts scarcity, first-come-first-served [H1], and unknown experience. Rises to ~7 with FREE-WILi/Grove and a tight scope. |
| Demo impact | **9** | A 3-minute in-person pitch [H1] favors something that moves. Precedent: the sandwich robot and the glove [M25c, M25e]. |
| Stacking potential | **7** | SpaceX + Relay + FREE-WILi + ElevenLabs + Notability + fun tracks fit one story. Weak for the LLM judge, Figma and Neon. |
| Fit with team preferences | **7** | Avoids FinTech crowding, fits the SpaceX bias (Dir. A) and Capital One (Dir. C), fun tracks are natural. Docked for the hardware-skill unknown. |

## 9. Head-to-head against the other main tracks

- **vs Actually Intelligent (AI):** same $2,500 [H2], but likely the biggest pool (~half or more of submissions are LLM-centric [scrape]), and judges have seen hundreds of agent wrappers. AI is easier to build, while Hardware is easier to *win* if you can build it. A hardware project with AI inside gets AI's technical credit anyway.
- **vs FinTech:** the team already leans away because of crowding. Nessie and Spacetime both pull finance apps toward this track [H2]. FinTech's only unique draw is the Capital One prize, and Direction C reaches it from Hardware. **Not worth switching unless the team has a killer finance idea.**
- **vs Sustainability:** moderate crowding (~11% sustainability-keyword projects in 2025 by my scrape, mostly dashboards and calculators). It is the closest rival: a sensor-based climate device could enter either. Its judges value impact claims that are hard to show in 3 minutes, while Hardware judges value a working object you can see.
- **Grand Prize ($5,000) [H2]:** open to any main track. Recent grand/overall winners skew physical-AI at MHacks 2025, TreeHacks 2026 and PennApps XXV [M25c, P1, P5]. So choosing Hardware doesn't cap the upside; it probably raises it.

**Recommendation:** Hardware main track with **Direction A (Skyward)**. Sponsor stack: SpaceX + Relay + Notability (+ ElevenLabs). Fun tracks: Useless AI + Judged by an LLM. Keep Direction C as the low-skill fallback if no one can own the electronics by 1 PM.

---

## Sources

- [H0] MHacks dashboard repo (handbook URL constant, `lib/wallet/event.ts`) and PR #197 — https://github.com/mhacks/dashboard/blob/main/lib/wallet/event.ts ; https://github.com/mhacks/dashboard/pull/197
- [H1] MHacks 2026 Hacker Handbook — https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af
- [H2] MHacks 2026 Tracks & Prizes (handbook subpage) — https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5
- [MLH] MLH Hardware Lab contents (linked from handbook) — https://guide.mlh.com/organizer-resources/hardware-lab-contents
- [S1] MHacks 2026 site (tagline, FAQ) — https://www.mhacks.org/
- [S2] MHacks 2026 live schedule — https://www.mhacks.org/live
- [M25a] MHacks 2025 project gallery — https://mhacks-2025.devpost.com/project-gallery
- [M25b] MHacks 2025 Devpost overview (prizes, 380 participants) — https://mhacks-2025.devpost.com/ ; rules/judging criteria — https://mhacks-2025.devpost.com/rules
- [M25c] Artificial Sandwich Intelligence — https://devpost.com/software/artificial-sandwich-intelligence
- [M25d] Conductor — https://devpost.com/software/temp-cbdzve
- [M25e] ScreenWave — https://devpost.com/software/screenwave
- [M25f] Wattson — https://devpost.com/software/wattson-5btsyd
- [M25g] Gestura — https://devpost.com/software/gestura-9oaugq
- [M24a] MHacks 2024 Devpost overview and gallery — https://mhacks-2024.devpost.com/ ; https://mhacks-2024.devpost.com/project-gallery
- [M24b] EscapeMate — https://devpost.com/software/escapemate
- [M24c] Wili-Party — https://devpost.com/software/wili-party
- [M24d] The WiLi Watch — https://devpost.com/software/wili-watch
- [M24e] V²/R (2024 Grand Prize) — https://devpost.com/software/v-r
- Other 2024/2025 project pages used in the hardware count — e.g. https://devpost.com/software/soundsense-jvz6yx , https://devpost.com/software/wordhawk , https://devpost.com/software/visioncane , https://devpost.com/software/greenhouse-butler-agricultural-work-assistant
- [P1] Stanford Daily, TreeHacks 2026 (Shepherd grand prize) — https://stanforddaily.com/2026/02/15/12th-annual-treehacks/
- [P2] Portable Braille (TreeHacks 2025) — https://devpost.com/software/portable-braille-cdq8v5
- [P3] BrailleBot (TreeHacks 2025 Best Hardware Hack) — https://devpost.com/software/readable-ai-braille-printer
- [P4] Therms (TreeHacks 2025) — https://devpost.com/software/therms-thermoregulation-wearables-with-ai-powered-insights ; TreeHacks 2025 prizes — https://treehacks-2025.devpost.com/
- [P5] SoundShield (PennApps XXV) — https://devpost.com/software/soundsheild
- [P6] SurgeVue (PennApps XXV) — https://devpost.com/software/surgikalai
- [P7] PulseWalk (Cal Hacks 11.0 Best Hardware Hack) — https://devpost.com/software/pulsewalk
- [P8] Cal Hacks 12 grand prize write-up — https://blog.dylanlu.com/cal-hacks-12/
- [F1] FREE-WILi 2 specs — https://freewili.com/
- [F2] FREE-WILi Python API docs — https://freewili.github.io/freewili-python/index.html
- [X1] xAI Grok Voice docs — https://docs.x.ai/developers/model-capabilities/audio/voice
- [X2] xAI Grok Imagine docs — https://docs.x.ai/developers/model-capabilities/imagine
- [X3] LiveKit SpaceXAI/Grok Voice plugin — https://docs.livekit.io/agents/models/realtime/plugins/spacexai/
- [R1] Relay docs (index) — https://docs.relayapp.im/ ; https://docs.relayapp.im/llms.txt
- [R2] Relay calls / LiveKit integration — https://docs.relayapp.im/calls/index.md ; https://docs.relayapp.im/integrations/livekit.md ; https://docs.relayapp.im/calls/video.md
- [D1] CelesTrak GP data formats — https://celestrak.org/NORAD/documentation/gp-data-formats.php
- [D2] wheretheiss.at API guide — https://apipark.com/techblog/en/how-to-use-the-wheretheiss-at-api-for-live-iss-tracking/
- [FN1] FinchNode — https://finchnode.com/
- Capital One Nessie API (from handbook) — https://api.nessieisreal.com

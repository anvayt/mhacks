# Sponsor Track Advocate — Best Use of FREE-WILi

## Prompt given (excerpt)
> You are the advocate for the sponsor track "Best Use of FREE-WILi" at MHacks 2026. Research the sponsor's tech and how fast a team can integrate it, what its judges reward, prize value vs competition, expected value, how it stacks with the main/fun picks and other sponsors, 2–3 winning project sketches, honest red flags, and a 1–10 scorecard. Make the strongest honest case — an impartial judge will weigh your file against eleven other sponsor advocates.

---

## TL;DR — the case in six lines

1. **This is the least-contested prize I can document at MHacks.** In 2025, **5 of 122** MHacks projects entered Best Use of FREE-WiLi, and **2 of those 5 won** [D25-filter, D25]. FREE-WILi has now sponsored MHacks three years running (2024, 2025, 2026) [D24, D25, HB-P].
2. **It also boosts the main track.** The 2025 Sustainability (Greenprint) winner, *Wattson*, was a FREE-WiLi build that won **both** Greenprint and FREE-WiLi [P-Wattson]. The judge picked Sustainability for us, and FREE-WILi is the cheapest way to add the "small physical element" the judge already recommends.
3. **The prize is hardware, not cash**: one FREE-WILi kit per member, up to 4 [HB-P]. Retail is **$600** for four FREE-WILi OG units ($150 each) or **$1,600** for four FREE-WILi 2 units ($400 each) [SHOP]. Which model MHacks hands out is **unverified**.
4. **Integration is a few hours, not a weekend.** The device is a finished handheld (screen, buttons, LEDs, IR transmit and receive, accelerometer, speaker and mic), controlled from a laptop over USB in Python [FW-OG, PY]. No soldering. **Best estimate: 5 hours** to a demo-quality integration, counting the 1 PM session.
5. **The real risks are logistics, not difficulty.** Will loaners be available? Which firmware and API do they run? The old `freewili` Python package is deprecated for the new OG firmware [PY-README]. Some past teams also hit macOS problems [P-M3SH, P-Pot]. All of these can be settled at the **FREE-WILi session, 1–2 PM today, Room 3336** [LIVE].
6. **Scorecard:** Prize value 4 · Win probability 8 · Integration ease 6 · Stacking 8 · Demo impact 9 · Fit with team preferences 6.

---

## 1. The technology

### What FREE-WILi is
- An **open-hardware handheld electronics multitool**, sold as a "pocket lab" for GPIO, analog I/O, wireless protocols and even retro gaming [FW-DOCS2, FW]. It is made by **Intrepid Control Systems**, a Michigan company that builds vehicle-network tools; FREE-WILi's privacy policy is Intrepid's [FW-PRIV]. That explains why the 2025 MHacks sponsor contacts were Intrepid staff (CEO plus engineers) [SD25], and why FREE-WILi mostly sponsors Michigan hackathons: MHacks, SpartaHack, Hack Dearborn and GrizzHacks [BLOG-CDX].
- **Two models exist. Which one MHacks hands out is unverified.**

| | **FREE-WILi OG** (in stock, $150 [SHOP]) | **FREE-WILi 2 Founder Edition** ($400, "Shipping Q4 2026", listed unavailable [SHOP]) |
|---|---|---|
| Compute | RP2040 + iCE40UP5K FPGA [FW-OG] | 2× RP2350, iCE40 FPGA, Raspberry Pi CM0 running Linux, ESP32-C5 [FW] |
| Screen / input | 320×240 color display, 5 buttons, 7 RGB LEDs [FW-OG] | 3.5″ 480×320 touchscreen, D-pad + A/B/X/Y [FW] |
| Sensors / audio | Accelerometer (LIS3DH per [P-VisionCane]), speaker, microphone [FW-OG] | IMU, magnetometer, ambient light, temp/humidity, 4-mic array, 0.5 W speaker [FW] |
| Radios | IR TX/RX, two CC1101 sub-GHz radios; **no Wi-Fi/BLE** [FW-OG, P-WiLiWatch] | IR, Wi-Fi 5 GHz, BLE, LoRa, sub-GHz, NFC/RFID, CAN FD [FW] |
| I/O | 11 GPIO (1.1–5.5 V; SPI/I²C/UART) [FW-OG] | 20- and 10-pin connectors, analog in/out, programmable PSU [FW] |

*Inference:* the kits are most likely the **OG**. It is the in-stock model, and FREE-WILi pushed new OG firmware (v023/v024) on Sept 28–30, 2026, days before MHacks [FW-REL]. Plan the project around OG capabilities and treat FREE-WILi 2 extras (magnetometer, light and temperature sensors, Wi-Fi) as a bonus.

### How you program it
- **Host Python over USB (the hackathon path).** Every MHacks winner I could check ran logic on a laptop and used the device for I/O [P-Gestura, P-Wattson, P-WiliParty, P-AISocial].
  - Legacy library: `pip install freewili`, Python ≥ 3.10, v0.0.51 [PYPI]. It covers LEDs, buttons, accelerometer events, IR send/receive, display images, audio playback, file upload and the WILEye camera [PY]. Examples are 10–40 lines, for example `fw.send_ir(bytes([...]))` and `fw.enable_accel_events(True, 33)` [PY-EX-IR, PY-EX-EV].
  - **Gotcha:** the README now says *"THE FW 1 firmware supported by this API is deprecated. The new OG firmware… uses the OneWili API."* [PY-README]
  - New library: **OneWili**, "628 commands across 83 menus", with Python, C, Rust, WASM and CM0 packages [OW]. It is **not on PyPI** (404 [OW-PYPI]); you install it from the GitHub source (`cd python && pip install -e .`) [OW]. It includes an IR menu (`send_ir_data`, `ir_save_capture`, `ir_send_button`, IR stream) [OW-IR].
  - **Action:** at 1 PM, ask which firmware the loaners run and which library to use.
- **On-device options:** WASM scripting [WASM-EX], the GUI, and on FREE-WILi 2 also rThon, WiliBlocks and Linux on the CM0 [FW]. Hack Dearborn 2025 ran a separate **"Best use of FREE-WILi WASM"** prize [P-Unblind]. *Inference:* FREE-WILi values on-device WASM use. Treat it as a stretch goal only.
- **AI tooling:** FREE-WILi says its GUI ships with Claude and LM Studio integration, and that its repos have Agent.md files so coding agents can write firmware [FW-AI]. The OneWili repo has an `AGENTS.md` [OW].
- **Platforms:** the device finder (`pyfwfinder`) ships macOS universal2, Windows and Linux wheels [FINDER-PYPI, FINDER]. The desktop GUI's macOS arm64 build was released Oct 2, 2026 [GUI-REL]. Linux needs udev rules [PY].

### Access, cost, signup
- No API key, account or signup. It is local USB hardware. Cost to the team: **$0 if loaners exist**, otherwise $150 per OG [SHOP].
- **Kits at MHacks 2026: unverified.** The handbook lists only the prize, and MLH's hardware lab (first-come, first-served) is a separate pool [HB]. The live schedule has a "FREE-WILi" event, **1:00–2:00 PM Oct 3, Room 3336**, with no description [LIVE]. Strong precedent says loaners will exist:
  - 2024: the Wili-Party team "discovered the device merely 24 hours before submission" and still won [P-WiliParty].
  - 2025: FREE-WILi ran a hands-on workshop on connecting sensors, SPI/I²C/UART and WASM [SD25]. One team used **several** devices talking over IR and got help from "the folks at FreeWili" on site [P-Celest]. Gestura's idea came from a demo at that workshop [BLOG-Gestura].
  - 2026 (GrizzHacks 8): a team's device failed an hour before judging, which shows devices were in hand at that event too [P-OmniComm].

### Realistic integration time (one owner, OG device, host Python)

| Step | Hours |
|---|---|
| FREE-WILi session (1–2 PM) + getting a device | 1.0 |
| Install, firmware/library match, "LEDs blink" smoke test | 0.5–1.5 |
| 2–3 features wired into the app (e.g., IR send of learned codes, image push to screen, button/accel events) | 2–3 |
| Demo hardening (reconnect on USB drop, simulator fallback) | 0.5–1 |
| **Total** | **≈ 4–6.5 → best single estimate 5 h** |

Evidence it can be done fast: Wili-Party built four working minigames in under 24 hours from first contact [P-WiliParty]. Evidence it can bite: Wattson called the Python API "a huge learning curve", and could only push whole images to the screen, so it got "seconds per frame" [BLOG-Wattson]. Celestaisle "couldn't get CMake working at all, even with the help of the folks at FreeWili" and hit an API bug on RF [P-Celest].

---

## 2. What this sponsor's judges reward

There are no published criteria for 2026. The track text is only "Awarded to the project with the best use of FREE-WILi" [HB-P]. The 2025 sponsor doc listed Description and Judging Criteria as "TBD" [SD25]. The MHacks handbook says company-track sponsors judge their own tracks during the 12:30 PM main judging window, and teams must be present [HB]. So the operative signal is **who has actually won**. Every winner I could verify:

| Event | Winner (prize label) | What it was | FREE-WILi features | Source |
|---|---|---|---|---|
| MHacks 2024 | **Wili-Party** (Best Use of Free-WILi) | Four 1v1 LED/button party minigames | LEDs, buttons, display images | [P-WiliParty] |
| MHacks 2024 | The WiLi Watch (won **Groq**, not FREE-WILi) | Smart-home wristband for limited mobility | IR to a hub; pivoted because the OG has no Wi-Fi/BLE | [P-WiLiWatch] |
| MHacks 2025 | **Wattson** (Greenprint **+** Best Use of FREE-WiLi) | Virtual pet that loses health when lights are left on | Custom GUI on the screen; OpenCV on the laptop | [P-Wattson, BLOG-Wattson] |
| MHacks 2025 | **Gestura** (Best Use of FREE-WiLi) | Wrist/ankle gesture mouse + voice commands for arthritis and amputees | Accelerometer | [P-Gestura, BLOG-Gestura] |
| SpartaHack X (2025) | **thereMINI** ("[FREE-WiLi] Best Use of FREE-WiLi application") | Wearable theremin, motion → MIDI | Accelerometer | [P-thereMINI] |
| Hack Dearborn 2025 | **Agent Unblind** (Best use of FREE-WILi WASM + MLH Arm) | Assistive business agent; theft detection from motion | Accelerometer over Web Serial, Rust→WASM | [P-Unblind] |
| SpartaHack 11 (2026) | **Potsticker** ("Free-Wili") | Self-evolving Wi-Fi honeypot | Orca module as Wi-Fi access point | [P-Pot] |
| GrizzHacks 8 (2026) | **AI Social Intrigue Game** ("Free-WiLi") | "Mafia" with AI + human players | Speaker plays **ElevenLabs** voice lines sent over USB; device as voice I/O + UI | [P-AISocial] |
| GrizzHacks 8 (2026) | **OmniComm** ("Free-WiLi") | All-in-one assistive communicator (blind ↔ deaf) | Planned as an edge device; **hardware failed ~1 h before judging and they demoed on laptops** | [P-OmniComm] |

MHacks 2025 entrants that did **not** win: *celestaisle*, a multi-device IR pager system plus a React Native app, ambitious but with features that failed; *VisionCane*, with accelerometer and speaker work still "in development"; and *Will I Study?* [D25-filter, P-Celest, P-VisionCane, P-WillIStudy].

**What wins (my reading; inferred from the table):**
1. **The device is the product, not a peripheral.** In every winner, a judge can hold or watch the FREE-WILi doing the core job: a wearable, a pet that lives on the screen, a game console, a voice box.
2. **A human story, often accessibility.** Gestura, thereMINI, Agent Unblind and OmniComm are all assistive. WiLi Watch (2024) was too, though it won Groq.
3. **One or two features done well beat many done halfway.** The accelerometer appears in 3 winners. Celestaisle's breadth did not win.
4. **The bar is reachable.** Simple LED party games won in 2024. A team whose hardware died before judging still won at GrizzHacks 8. *Inference:* small pools mean "working, clearly FREE-WILi-centric, and pitched well" is usually enough.
5. **AI and voice stacking already has a precedent.** ElevenLabs audio through the FREE-WILi speaker won at GrizzHacks 8 [P-AISocial].
6. **Bonus perk:** FREE-WILi wrote up **every** 2025 MHacks entrant on its blog, not only the winners. All 5 opt-ins appear in the post list [BLOG-CDX, D25-filter]. That is free publicity for résumés (inference that they will do it again).

---

## 3. Prize value and expected competition

**Prize:** "FREE WILi Kits for each team member up to 4" [HB-P]. The Instagram slide lists 1st place only.
- Retail value for a 4-person team: **$600** (4 × $150 OG) to **$1,600** (4 × $400 FREE-WILi 2) [SHOP]. *Inference:* OG is more likely. Resale or personal value is lower for students who won't keep doing embedded work.
- Number of winners: **1 listed for 2026** [HB-P]. MHacks had 1 in 2024 [D24] and 2 in 2025 [D25]. GrizzHacks 8 had 2 [P-AISocial, P-OmniComm]. More could be named on the day, but that is unverified.

**Competition (expected: LOW):**
- MHacks 2025: **5 entrants** out of 122 projects (≈4%) [D25-filter, verdict file].
- Other events, counting FREE-WILi blog posts per event as a rough proxy for entrants: about 8 at Hack Dearborn 2025, 2 at SpartaHack X, 2 at SpartaHack 11 and 4 at GrizzHacks 8 [BLOG-CDX]. *Inference:* FREE-WILi pools run **3–8 teams**.
- Two 2026 changes push the number up:
  - MHacks added a $2,500 **Beyond the Code (Hardware)** main track [HB-P].
  - 2025's other hardware-specific sponsor prizes (MemryX, Snap AR, Embedder's Best Hardware Hack) are absent in 2026 [D25, HB-P]. FREE-WILi is now the **only hardware sponsor prize**.
- My estimate for 2026: **6–12 entrants** (inference). Software-sponsor tracks plausibly see several times that, since about half of 2025 projects were LLM-based (verdict file).

---

## 4. Expected value (rough; all probabilities are my inference)

| Track | Prize pool (handbook [HB-P]) | Guess at entrants | P(our strong entry places) | EV (cash-equivalent) |
|---|---|---|---|---|
| **FREE-WILi** | 1 × kit/member: $600 (OG) – $1,600 (FW2) | 6–12 | **~30%** | **~$180 – $480** |
| Fetch.ai ASI:One | $1,250 / $750 / $500 cash | many (agent projects are the most common type) | ~8–15% any place | ~$200 – $375 |
| SpacetimeDB | $1,000 / $500 / $200 cash | moderate | ~10–15% any place | ~$170 – $255 |
| Capital One Nessie | $300 gift card × 4 = $1,200 | moderate (FinTech pull) | ~5–10% | ~$60 – $120 |

**Honest reading:** in dollars, FREE-WILi is **mid-pack**, not a runaway. In **probability per hour invested** it is the best I can document. It also has two payoffs the table leaves out:
- **Main-track lift.** A physical demo helped win Greenprint in 2025 [P-Wattson]. Hardware took 3 of the 5 serious MHacks-run 2025 awards (verdict file). Even a few points of extra main-track probability on a **$2,500** prize is worth as much as the kit EV itself.
- **It does not compete with the cash tracks; it stacks with them.** The device can be the physical "hands" of a Fetch.ai or Relay agent (§5). FREE-WILi's EV is additive.

---

## 5. Stacking

**Main track**
| Main | Fit | Why |
|---|---|---|
| **Sustainability (judge's pick)** | **Strong, proven** | Wattson won Greenprint + FREE-WiLi together [P-Wattson]. IR transmit turns off real IR-controlled appliances (fans, TVs, LED strips, window ACs) [FW-OG, PY-EX-IR]. Here a FREE-WILi is a **differentiator** (verdict file: the 2025 Sustainability field was mostly dashboards). |
| Beyond the Code (Hardware) | Natural, but it's the baseline | Any FREE-WILi project qualifies. Here you compete against robotics builds, so FREE-WILi alone won't stand out. This matches the judge's own flip rule: "confirmed electronics owner by noon → Hardware." |
| Actually Intelligent (AI) | OK | Works if the device is the I/O for an agent with real intent handling (AI Social Intrigue pattern [P-AISocial]). |
| FinTech | Weak | The OG has no NFC or payments hardware [FW-OG]. No FREE-WILi fintech winner found. |

**My position:** keep the judge's **Sustainability** pick. FREE-WILi is the "small physical element" the verdict already recommends. Switch to Hardware only if a teammate wants to own electronics full-time.

**Fun tracks**
- **Judged by an LLM:** neutral. An LLM judge can't see hardware, so the Devpost write-up needs photos and a video. It costs nothing.
- **Dumbest Idea:** good if played for laughs. Physical gags demo well, and 2024's LED party games won FREE-WILi [P-WiliParty].
- **Useless AI:** good, but conflicts with a sincere Sustainability pitch.

**Other sponsors (one coherent project)**
| Sponsor | Fit with FREE-WILi | Note |
|---|---|---|
| **Relay** | **Strong** | An agent you **call** whose tool call fires IR or LEDs on the device. The demo moment is a phone call that changes something physical on the table. Relay's workshop is at the **same hour** (1–2 PM, VR Lab) as FREE-WILi's [LIVE], so split the team. |
| **Fetch.ai ASI:One** | **Strong** | The rubric asks agents to "take meaningful action" [HB-P]. Driving hardware is the most literal version. Precedent: two Hack Dearborn FREE-WILi entries used Fetch.ai uAgents, one of them the WASM winner [P-Unblind, BLOG-M3SH]. |
| **ElevenLabs** | **Strong, proven** | Voice played through the FREE-WILi speaker won at GrizzHacks 8 [P-AISocial]. |
| **SpaceX "Make it Legendary"** | Good | The device can be a physical display and controller for space data: push Grok Imagine renders to its screen, beep when a satellite passes. The device adds nothing to the "space data" requirement itself, which still needs Cursor + Grok Imagine/Voice [HB-P]. |
| Notability | Free add-on | Use it for planning screenshots [HB-P]. |
| Figma | Weak–OK | You could design the 320×240 screen UI in Figma, but it's a minor prize. |
| SpacetimeDB | OK if several devices | Multiple devices as live "players" in shared state. Kits are probably one per team (unverified). |
| Neon | Bolt-on | An event log. |
| FinchNode | Conflicts with Sustainability | Fine with Hardware (medication-adherence wearable). |
| Capital One Nessie | Conflict | FinTech pull. No hardware angle on the OG. |

**Realistic stack (keep it to 3–4 real integrations, per the verdict):** Sustainability + **FREE-WILi** + **Relay *or* Fetch.ai** + **ElevenLabs *or* SpaceX (Grok Voice)** + Notability + Judged by an LLM.

---

## 6. Project sketches

### A. "Off Switch": an energy agent with physical hands (Sustainability) — *my top pick*
- **What:** A FREE-WILi sits on a dorm desk.
  - Setup: it **learns IR codes** from existing remotes (fan, TV, LED strip, window AC) using IR receive and save-capture [OW-IR, PY].
  - Physical "I'm leaving" button: it **switches everything off** over IR [PY-EX-IR].
  - Automatic mode: an agent switches devices off when the room is empty (laptop webcam brightness/presence, Wattson's proven trick [BLOG-Wattson]) or when grid carbon is high.
  - Display: its screen shows a **garden that grows** with kWh saved, matching the event's "Digital Garden" theme (verdict file).
  - Voice: confirmations play through the FREE-WILi speaker (ElevenLabs or Grok Voice).
- **Agent surface:** pick one.
  - Relay: "call your dorm": "I already left, kill everything."
  - Fetch.ai: an Agentverse agent, discoverable on ASI:One, that schedules loads.
- **Space data (for SpaceX):** satellite-derived solar or fire data (NASA POWER / FIRMS). Whether SpaceX judges accept Earth observation is **unverified** (verdict file). Ask at the SpaceXAI session, 4–5 PM [LIVE].
- **Why it wins FREE-WILi:** the device is the product. It uses IR TX/RX, screen, buttons, LEDs and speaker, which is more of the board than Wattson used, with the same winning theme.
- **Why it wins Sustainability:** it **closes the loop** (it acts, not just measures) and it is physical in a field of dashboards.
- **Demo (30 s):** a judge presses the button or calls the agent → the LED strip and fan on the table go dark → the device says "Saved 0.4 kWh" → the garden blooms.
- **Risks:** looks like Wattson, so lead with the agent and the IR action. IR compatibility: bring a cheap IR LED strip or fan as a known-good target. The library example uses NEC codes [PY-EX-IR]; that most cheap strips use NEC is an inference. Keep a software simulator so the app still demos if the device dies (OmniComm precedent [P-OmniComm]).

### B. "Skyward": a satellite-pass handheld (Hardware main, or Sustainability if Earth-observation-framed) — *the max-SpaceX option*
- **What:** the laptop computes live ISS/Starlink positions from CelesTrak TLEs (Skyfield). The FREE-WILi becomes a handheld "sky radar":
  - It counts down to the next visible pass over Ann Arbor.
  - LEDs and speaker ramp up as the pass approaches.
  - **Tilting it to the satellite's current elevation** (accelerometer) turns the LEDs green.
  - Pressing A pushes a **Grok Imagine** "postcard" of what the satellite is passing over to the screen.
  - Grok Voice answers questions through the laptop.
  - Built in Cursor, per the SpaceX rule [HB-P].
- **Stacks:** SpaceX (strongest fit of my three), FREE-WILi, Relay ("call the sky"), Dumbest Idea if framed as "satellite dowsing", Notability.
- **Honest limit:** the OG has **no magnetometer**, so it can't sense which way you're facing; use a "face north, press B" calibration. FREE-WILi 2 has one (BMM350) [FW]. I considered using the OG's sub-GHz radio to hear amateur-satellite beacons near 435–438 MHz, inside the CC1101's 387–464 MHz range [FW-OG]. It is **not recommended**: it needs an outdoor antenna and a pass during judging. Inference, untested.

### C. "Reach": a gesture-and-voice remote for limited mobility (AI or Hardware main) — *the proven FREE-WILi pattern*
- **What:** a wrist-worn FREE-WILi.
  - Tilt gestures (accelerometer events [PY-EX-EV]) plus one button pick among learned IR devices.
  - An LLM agent turns spoken intent from the laptop mic ("it's too warm in here") into multi-step actions (fan on, blinds LED off).
  - ElevenLabs confirms through the device speaker.
  - A caregiver can **call in via Relay** to check status or act.
- **Why it wins FREE-WILi:** it directly matches the most common winning pattern: assistive, wearable, accelerometer (Gestura, thereMINI, Agent Unblind, OmniComm) [P-Gestura, P-thereMINI, P-Unblind, P-OmniComm].
- **Risk:** it is close to 2024's WiLi Watch and 2025's Gestura, so FREE-WILi judges have seen the idea. The agentic intent layer and the caregiver loop are the new parts. The OG's mic streaming was not available to Gestura in 2025 [BLOG-Gestura], so use the laptop mic.

---

## 7. Red flags, rival arguments, rebuttals

**Honest red flags**
1. **The prize is non-cash and its value is unclear:** $600 vs $1,600 retail depending on the model [SHOP]. Only **one** winner is listed for 2026 [HB-P].
2. **Loaner availability for 2026 is unverified.** Three years of precedent say yes (§1), but confirm at the Sponsor Expo (11:30 AM–1 PM, Pierpont Connector Hall) or the 1 PM session [LIVE].
3. **API and firmware churn.** The PyPI library targets deprecated firmware [PY-README]. OneWili must be installed from source [OW, OW-PYPI]. New OG firmware shipped Sept 28–30 [FW-REL]. A firmware/library mismatch can eat hours, so run a **30-minute smoke test** before committing.
4. **macOS friction.** M3SH fell back to Windows machines for flashing because of "the lack of macOS support for Free-WiLi development" [P-M3SH]. Potsticker used a teammate's Windows laptop as the device interface [P-Pot]. The finder library does ship macOS wheels [FINDER-PYPI]. *Mitigation:* stay on host Python over USB, and have one Windows or Linux laptop available.
5. **OG limits:** no Wi-Fi or BLE (it must be tethered to a laptop) [P-WiLiWatch]; screen updates are slow if you push whole images [BLOG-Wattson].
6. **Demo-day hardware failure.** It happened to a winner [P-OmniComm]. Build a simulator fallback.
7. **The pool may grow** with the new Hardware main track (§3). Criteria are unpublished (TBD in 2025 [SD25]).
8. **Hardware experience on the team is unknown.** Someone has to own the device for about 5 hours.

**Best rival arguments → rebuttals**
- *"It's a gadget, not cash. Fetch.ai pays $1,250."* → Fetch.ai and FREE-WILi are not either/or. Sketch A enters both, and the device makes the Fetch.ai demo *more* convincing: "take meaningful action" becomes literal. Per hour of work, FREE-WILi has the best odds documented here.
- *"Hardware will eat a software team's weekend."* → This is a finished handheld, not a breadboard: no soldering, Python over USB, examples of 10–40 lines [PY-EX-IR, PY-EX-EV]. A 2024 team went from first contact to a win within 24 hours [P-WiliParty]. Limit the scope to 2–3 features.
- *"It only fits the Hardware main track."* → Wattson won **Sustainability** with it [P-Wattson], and the judge already recommends a small physical element for Sustainability.
- *"It doesn't help SpaceX."* → It doesn't conflict either. Sketch B makes space data physical. For SpaceX-max, B is the better choice.
- *"The LLM-judged fun track can't see hardware."* → True, but that is a minor prize. Put the photos and video in the Devpost write-up.
- *"Kits might not be there."* → Then drop FREE-WILi before 2 PM and nothing else breaks, as long as the device sits behind a thin adapter with a simulator. The downside is bounded at about 1.5 hours.

**Go/no-go by 2 PM today:** (a) a device is in hand; (b) LEDs blink and an IR code fires from our laptop within 30 minutes; (c) we know whether it's an OG or a FREE-WILi 2. All three → go. Any one fails → drop FREE-WILi and keep the rest of the plan.

**Questions to ask the FREE-WILi reps at 1 PM:** Which model are the loaners, and can we borrow two? Which firmware and library: legacy `freewili` or OneWili? Any macOS caveats? What will you judge on? Is on-device WASM a plus? How many winners this year?

---

## 8. Scorecard (1–10)

| Criterion | Score | One-line justification |
|---|---|---|
| Prize value | **4** | Non-cash kit, $600 (OG) to $1,600 (FW2) retail for 4 [SHOP]; only one winner listed [HB-P]. |
| Win probability | **8** | 5 entrants and 2 winners at MHacks 2025 [D25-filter]; even a 2026 pool of 6–12 leaves a strong entry around 30% (inference). |
| Integration ease | **6** | Finished handheld, Python over USB, about 5 h; minus points for API/firmware churn and macOS friction [PY-README, P-M3SH]. |
| Stacking potential | **8** | Proven with Sustainability [P-Wattson] and ElevenLabs [P-AISocial]; natural with Relay and Fetch.ai; conflicts only with FinTech, Capital One and FinchNode-under-Sustainability. |
| Demo impact | **9** | Something physically changes on the table during a 3-minute pitch; hardware took 3 of the 5 serious MHacks-run 2025 awards (verdict file). |
| Fit with team's stated preferences | **6** | Fits the judge's Sustainability pick and keeps SpaceX, Relay and Fetch.ai open. Not on the team's sponsor shortlist, and hardware skill is unconfirmed. |

**Integration hours estimate: 5.** **Expected competition: low.**

---

## Sources

**MHacks 2026 (official)**
- [HB] 2026 Hacker Handbook (judging, sponsors judge their tracks, hardware resources): https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af
- [HB-P] Handbook, Tracks & Prizes (FREE-WILi prize text, all sponsor prizes): https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5
- [LIVE] MHacks live schedule (FREE-WILi 1–2 PM Room 3336; Relay 1–2 PM; Fetch.ai 2–3 PM; SpaceXAI 4–5 PM; Sponsor Expo; judging): https://www.mhacks.org/live
- MHacks site (FreeWILi listed as sponsor): https://www.mhacks.org/
- MLH hardware lab list: https://guide.mlh.com/organizer-resources/hardware-lab-contents

**FREE-WILi product, docs, code**
- [FW] FREE-WILi home (FREE-WILi 2 specs, software, AI integration): https://freewili.com/
- [FW-OG] FREE-WILi OG specs: https://freewili.com/freewili-og.html
- [FW-AI] AI agents spec page: https://freewili.com/specs/ai-agents.html
- [FW-PRIV] Privacy policy (Intrepid, Michigan): https://freewili.com/privacy-policy.html
- [FW-DOCS2] What is FREE-WILi 2: https://docs.freewili.com/start-here/what-is-freewili2/ · Docs root: https://docs.freewili.com/
- [SHOP] Shop catalog with prices (OG $150; FREE-WILi 2 Founder Edition $400, Q4 2026): https://shop.freewili.com/products.json · https://shop.freewili.com/products/free-wili-2
- [PY] Python library docs: https://freewili.github.io/freewili-python/index.html
- [PYPI] `freewili` on PyPI: https://pypi.org/project/freewili/
- [PY-README] freewili-python README (deprecation notice): https://github.com/freewili/freewili-python
- [PY-EX-IR] IR example: https://github.com/freewili/freewili-python/blob/master/examples/send_ir.py
- [PY-EX-EV] Events example: https://github.com/freewili/freewili-python/blob/master/examples/events.py
- [OW] OneWili API repo: https://github.com/freewili/onewili · reference: https://freewili.com/onewili/
- [OW-IR] OneWili IR menu: https://github.com/freewili/onewili/blob/main/python/onewili/menus/ir.py
- [OW-PYPI] `onewili` not on PyPI (404): https://pypi.org/project/onewili/
- [FINDER] freewili-finder (cross-platform): https://github.com/freewili/freewili-finder
- [FINDER-PYPI] pyfwfinder wheels: https://pypi.org/project/pyfwfinder/
- [FW-REL] OG firmware releases v023/v024 (Sept 28–30, 2026): https://github.com/freewili/freewili-firmware/releases
- [GUI-REL] FREE-WILi GUI releases (macOS arm64 Oct 2, 2026): https://github.com/freewili/freewili-gui/releases
- [WASM-EX] WASM examples: https://github.com/freewili/wasm-examples
- GitHub org: https://github.com/freewili

**Past MHacks data**
- [D24] MHacks 2024 Devpost (Best Use of Free-WILi, 1 winner): https://mhacks-2024.devpost.com/
- [D25] MHacks 2025 Devpost (Best Use of FREE-WiLi, 2 winners; full prize list): https://mhacks-2025.devpost.com/
- [D25-filter] MHacks 2025 FREE-WiLi opt-ins (5 projects): https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90539
- [SD25] MHacks 2025 public sponsor doc, FREE-WiLi (workshop, "TBD" criteria, kit per member): https://safe-banon-80d.notion.site/FREE-WiLi-27224ca0c81b8095afbacb6048908962

**Winning and entrant projects**
- [P-WiliParty] https://devpost.com/software/wili-party
- [P-WiLiWatch] https://devpost.com/software/wili-watch
- [P-Wattson] https://devpost.com/software/wattson-5btsyd
- [P-Gestura] https://devpost.com/software/gestura-9oaugq
- [P-Celest] https://devpost.com/software/celestaisle
- [P-VisionCane] https://devpost.com/software/visioncane
- [P-WillIStudy] https://devpost.com/software/will-i-study
- [P-thereMINI] https://devpost.com/software/theremini
- [P-Unblind] https://devpost.com/software/agent-unblind
- [P-Pot] https://devpost.com/software/potsticker
- [P-AISocial] https://devpost.com/software/ai-social-intrigue-game-on-free-wili
- [P-OmniComm] https://devpost.com/software/assistive_communicator
- [P-M3SH] https://devpost.com/software/m3sh-vhqy3j
- DriveGuard (Hack Dearborn, "2nd Place"; category not stated): https://devpost.com/software/driveguard
- Block Cycle (Hack Dearborn, WILEye camera Orca): https://devpost.com/software/beatbox-jrpklt

**FREE-WILi blog (archived)**
- [BLOG-Gestura] https://web.archive.org/web/20251110044500/https://docs.freewili.com/blog/gestura/
- [BLOG-Wattson] https://web.archive.org/web/20251110035750/https://docs.freewili.com/blog/wattson/
- [BLOG-M3SH] https://web.archive.org/web/20251110050755/https://docs.freewili.com/blog/m3sh/
- AI Social Intrigue Game post: https://web.archive.org/web/20260415153717/https://docs.freewili.com/blog/ai-social-intrigue-game-on-freewili/
- [BLOG-CDX] Archived blog index and event tags (mhacks, hackdearborn, spartahack-x, spartahack-11, grizzhacks7, grizzhacks8): https://web.archive.org/cdx/search/cdx?url=docs.freewili.com/blog/*&collapse=urlkey · e.g. https://web.archive.org/web/20260415161856/https://docs.freewili.com/blog/tags/grizzhacks8/ · https://web.archive.org/web/20251110050308/https://docs.freewili.com/blog/tags/hackdearborn/

**Team's own prior research (context)**
- Main/fun verdict: /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md
- 2025 and 2024 year research: /Users/anvaytodkar/Code/mhacks/results/year-research/2025.md · /Users/anvaytodkar/Code/mhacks/results/year-research/2024.md

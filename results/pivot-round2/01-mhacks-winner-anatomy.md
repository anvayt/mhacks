# MHacks Winner Anatomy

## Prompt given (excerpt)
> **Your job: MHacks winner anatomy.** Dissect every top-level winner (Grand Award / 1st–3rd overall) and every sustainability/climate/environment category winner at MHacks 2020–2025 from the year files (verify details on Devpost where useful). For each: what it did, who it served, how broad the problem was, the demo moment, the technical core the team built itself, and why it won (citing judges' remarks where the files have them). Then distil a concrete **winning formula** for MHacks specifically, sustainability-specific lessons, and a list of saturated/overdone sustainability ideas to avoid (things that have already won or appear constantly).
>
> Context: the team rejected "Clean Hours" (dryer scheduling) and "Fern on Call" (heat/smoke check-ins for older people living alone) as too niche. "Not niche" means a problem many people have, something used often, and value a judge gets in one sentence. Specificity in the *demo* is fine; the *problem* must be broad.

*Written Sat Oct 3, 2026, ~6:30 PM EDT. Tags: **[V]** I checked it today at the linked source. **[F]** From a team research file (its citations apply). **[I]** Inference.*

---

## TL;DR

1. **None of the 18 top-level winners from 2020 to 2025 served a small group facing a rare event.** Every 1st/2nd/3rd/Grand winner fixed something a judge has done, or watched a friend struggle with, this month: waking up, debugging, reading a long PDF, furnishing a room, cooking, sitting the SAT, searching a lecture video, filling in a form. The narrowest ones (Dystic, Shadow Clone) came from small online years with weak competition.
2. **The "named vulnerable user" pattern wins *category* prizes, not top prizes.** NurseNotes, CogniCare, Dementia Assistant, HopeHire, Plasma Desk and SoundSense all won a track or sponsor prize. None of them placed overall. The earlier pattern file (`pivot-ideas/01`, P2) blurred these two levels. That blur is how Fern on Call ended up feeling niche.
3. **The top-prize recipe is: a broad problem, a specific demo, and a core the team built.** Every top winner pairs a problem everyone recognises with a 10-second "watch it happen" moment and one piece of real engineering that isn't an API call. Examples: a trained robot policy, a circuit solver, a NeRF pipeline, a self-trained LSTM.
4. **MHacks sustainability winners have been tangible and technically modest.** Wattson compared photo brightness. Carbon Footprint Extension measured page weight. FarmX fit a random forest. Water Monitor drew a heatmap. The track bar is "visible and clear", not "deep". No sustainability project has won a top-level prize at an in-person MHacks.
5. **The sustainability pool is crowded with the same consumer apps, and they don't win.** In 2024–2025, **10 recycling or food-waste apps entered the Sustainability track and none won anything** [V]. Footprint trackers, eco-chatbots and plant-care apps went 0 for 7. The winners put a physical object in the loop, served producers or systems rather than shoppers' guilt, or made something invisible visible.
6. **The rubric itself rewards breadth.** MHacks' Usability criterion includes "impact on a broader audience", and Innovation includes "real-world issues or needs addressed" [F 2025 R1]. With pairwise judging (MDredd) [F 2025 R14], a judge picks between two tables. The bigger, more obviously real problem has the edge in that comparison [I].

---

## 1. Scope: which winners count

| Year | Event | Top-level prizes dissected | Sustainability / environment winners dissected | Weight for 2026 |
|---|---|---|---|---|
| 2025 | MHacks 2025 (in person, 122 projects) | Grand Award | Greenprint track; sustainability-themed sponsor winners | High |
| 2024 | MHacks 2024 (in person, 132) | Grand Prize, Runner-Up | Sustainability track; two MLH climate winners | High |
| 2024 | Google x MHacks (in person, 65) | 1st, 2nd, 3rd | none | Medium |
| 2023 | MHacks 16 (in person, 100) | 1st, 2nd, 3rd | none (no sustainability theme); one adjacent sponsor win | High |
| 2023 | MHacks 15 (online, 61) | 1st, 2nd, 3rd | 2nd place was a sustainability project | Low |
| 2022 | none held | — | — | n/a |
| 2021 | MHacks 14 (online, 59) | 1st, 2nd, 3rd | two Google Cloud/MLH climate winners | Low |
| 2020 | MHacks 13 Beta (online, ~61) | 1st, 2nd, 3rd | none (only "Wolfram Top 30" badges) | Low |

Sources: year files [F 2020–2025]; galleries re-checked for 2024–2025 [V].

**Breadth scale used below.** *Universal* means most judges have the problem themselves. *Broad* means a large, familiar group (all students, all homeowners, all developers). *Bounded* means one profession or condition. *Narrow* means a small group facing a rare event. Frequency runs from constant through daily, weekly and seasonal to rare.

---

## 2. Top-level winners, dissected

### MHacks 2025 (in person, high weight)

| Prize | Project | What it did | Who / how broad | Demo moment | Core they built | Why it won |
|---|---|---|---|---|---|---|
| **Grand Award** ($4,000) | **Artificial Sandwich Intelligence** (solo) | A $200 LeRobot SO-101 arm makes a sandwich on its own | Every quick-service sandwich line ("automate Subway/Jimmy John's"). **Broad, constant** | A robot arm assembles a sandwich at the table; the video benchmarks it against a human | An end-to-end ACT transformer policy trained on his own teleoperation data in ~4 h on one RTX 4090 [V]. The Hugging Face profile shows separate per-ingredient policies (BREAD1, TOMATO, LETTUCE…) [F] | The only learned robot policy on physical hardware in the room. The joke premise sits on serious engineering. He claims to "significantly outperform" a human benchmark and to be state of the art for the compute used [V]. No judge quotes exist [F]. |

### MHacks 2024 (in person, high weight)

| Prize | Project | What it did | Who / how broad | Demo moment | Core they built | Why it won |
|---|---|---|---|---|---|---|
| **Grand Prize** ($3,000) | **V²/R** | A VR replica of U-M's EECS 215 lab: place resistors, wires and LEDs, flip the power supply, and the LED lights if the circuit is right | Every intro-EE student, framed as K-12 hardware education. **Broad, every lab session**. Local hook: the real U-M lab | Put on the headset, wire a circuit, flip the switch, and the LED glows. "Eely the IA" shows the lab slides [V] | Its own circuit analysis (loop detection plus linear network analysis), its own Blender models, and breadboard-node connectivity [V] | Immersive and instantly legible. It used **no LLM** in an AI-heavy year, and the local hook was real [F]. Most of the team was new to Unity/C# [V]. |
| **Runner-Up** ($1,500) | **FocusFlow** | A PDF reader with webcam eye tracking. The text you're reading highlights, and the page changes colour when your gaze wanders. Includes reading stats and a chatbot | Anyone reading long documents, with urgency from an NIMH figure: 7.1M children and teens diagnosed with ADHD in 2022 [V]. **Broad, daily** | Calibrate the webcam, read, and the highlight follows your eyes; look away and the UI reacts | They recorded their own dataset and trained an LSTM regression model on Intel Cloud. WebGazer handled raw gaze [V] | Four AI parts in one working app, with a live webcam demo the judge takes part in [F]. |

### Google x MHacks, Apr 2024 (in person, medium weight; Gemini required)

| Prize | Project | What it did | Who / how broad | Demo moment | Core they built | Why it won |
|---|---|---|---|---|---|---|
| **1st** ($3,000) | **Cosmocook!** | A HoloLens 2 cooking assistant: 3D step-by-step instructions, ingredient detection and substitutions, all hands-free | Everyone who cooks. **Universal, daily** | Wear the headset, look at ingredients, get a recipe, and follow it hands-free | A 15-second rolling video buffer streamed to Gemini for low latency, plus Unity/MRTK integration. The team brought NASA AR project experience [F] | A memorable headset demo of a universal chore [F]. |
| **2nd** ($1,500) | **Gemini Forge** (solo) | "pip install for prompts": a library's code, issues and docs become a prompt store, with a VS Code extension | Every developer using LLMs with libraries. **Broad, daily** | Install it, then ask about a library and get grounded answers | The ingestion pipeline plus the extension [F] | A clear developer pain with a one-line analogy [F]. |
| **3rd** ($500) | **Rusteze** | Converts C to memory-safe Rust with Gemini, feeding compiler errors back until it builds | C codebases, tied to the White House memory-safety push. **Bounded but policy-relevant** | The C version breaks under an attack test while the Rust version holds | A self-correcting compile-and-fix loop plus the tests that verify it [F] | Timely, and the output is verified rather than merely generated [F]. |

### MHacks 16, Nov 2023 (in person, high weight)

| Prize | Project | What it did | Who / how broad | Demo moment | Core they built | Why it won |
|---|---|---|---|---|---|---|
| **1st** | **DECO.ai** | Scan furniture with an iPhone; NeRFs turn the photos into 3D models you arrange in a virtual room | Anyone furnishing a room. **Universal, occasional but costly** (students move every year [I]) | Photograph a chair, and minutes later it sits in a virtual room you can rearrange | A NeRF synthesis pipeline built from papers, plus a Rust/Bevy desktop designer [V] | The team says it brought research-grade technology to a real-world problem [V], which maps onto Innovation plus Technical Complexity [F]. |
| **2nd** + Warp Best Dev Tool | **Terminal.AI** | A CLI that reads your error stack and codebase and tells you the fix, with file and line | Every developer. **Universal among judges, many times a day** | Trigger an error, run the tool, and get the exact fix in the terminal | Codebase-context gathering plus prompt engineering. Shipped to PyPI [V] | Judges could picture using it the next day, and it really ships. It won two prizes [F]. |
| **3rd** | **VSAT** | A VR SAT exam room: desks, a test booklet, a real-time clock, other students, coughing | Every SAT taker. **Broad, high-stakes, a few times in a life** | Sit the test in VR with real-room distractions | Hand-built Unreal/Blender assets and a custom drawing system. The write-up opens with cited research on context-dependent recall [F] | Immersive and polished, built by first-years who learned Unreal during the event [F]. |

### MHacks 15, Feb 2023 (online, low weight)

| Prize | Project | What it did | Who / how broad | Demo moment | Core they built | Why it won |
|---|---|---|---|---|---|---|
| **1st** | **LumiGUI** | Touchless hospital form-filling: photoresistors detect a hand ~2 cm away | Every patient at check-in (hygiene). **Broad, per visit** | Wave a hand over the box and the form advances | Arduino sensing, a 3D-printed enclosure (their first print), and serial → PyAutoGUI → React/Express/MongoDB [V] | The only notable hardware entry, integrated from hardware all the way to the database [F]. |
| **2nd** | **Carbon Footprint Extension** | A Chrome extension estimating the CO₂ and energy of your browsing, with a dashboard | Everyone who browses. **Universal, constant** | Browse, then watch your footprint grow on the dashboard | Network-data capture via Chrome APIs (page weight) and charts. The page gives **no CO₂ conversion method** [V] | A clear sustainability story with real-time data, built around Chrome's privacy limits [V]. *The only sustainability project ever to place overall, at a 61-project online event.* |
| **3rd** | **MyNewsWire** | A personalised news newsletter, live at mynewswire.tech | Everyone who reads news. **Universal, daily** | Pick interests and receive a real email | Rate-limit engineering (caching plus key rotation), deployed [F] | Complete and deployed, from a team at its first hackathon [F]. |

### MHacks 14, Oct 2021 (online, low weight; the only year with judge remarks)

| Prize | Project | What it did | Who / how broad | Demo moment | Core they built | Why it won (judges, paraphrased from captions [F]) |
|---|---|---|---|---|---|---|
| **1st** | **SunLite Sunrise Lamp** | A LIFX bulb fakes a sunrise 30 min before your alarm, scheduled in a web app or **by text** | Everyone who struggles to wake up. **Universal, daily** | Text a time, and the bulb glows up | Flask/Postgres scheduler, Twilio SMS and the LIFX API; "our first hardware hack" [F] | The core team called it incredible and **well-rounded**. The presenter said she struggles to wake up: "I would definitely use this." |
| **2nd** | **Shadow Clone** (solo) | Rebalances ML training data by replicating under-represented samples | ML practitioners, with a societal effect. **Bounded, but the harm is broad** | Upload a dataset and get a rebalanced one | Flutter ↔ Django ↔ GCP real-time model serving [F] | Praised for technical depth and a beautiful UI. |
| **3rd** | **MCall** | A voice-call journal for student mental health | Students; cites a Michigan Daily survey (~40% feel less adequate than peers). **Broad, daily** | Call a number, talk, and get a transcribed journal | Twilio Voice and AssemblyAI in the core flow [F] | Called a good use case, well-rounded, on an important issue. |

### MHacks 13 Beta, Aug 2020 (online, low weight)

| Prize | Project | What it did | Who / how broad | Demo moment | Core they built | Why it won |
|---|---|---|---|---|---|---|
| **1st** | **Dystic** | A job finder for people with disabilities, with an AI resume builder and a chatbot "job agent" | Disabled job-seekers hit by COVID layoffs. **Bounded but millions of people** | Log in, see jobs, build a resume, chat with the agent | About 10 Google products integrated into one flow [F] | Social good was a scored criterion, and it swept Google Cloud's prizes [F]. |
| **2nd** | **we-Learn** | Searchable lecture videos: search a word and jump to where it's spoken | Every student in remote 2020. **Broad, daily** | Type a keyword and the video jumps to that moment | A Speech-to-Text pipeline on GCP [F] | One clear "aha" moment, on a problem every student judge had that summer [F]. |
| **3rd** | **Sportable** | A PE and fitness trainer with computer-vision form checks and AR exercise models | Everyone exercising at home in 2020. **Broad, daily** | AR exercise models in the app | An I3D video classifier that **didn't work and was cut from the demo**, and they said so [F] | Ambition plus honesty plus a working app [F]. |

---

## 3. Sustainability, climate and environment winners, dissected

| Year / prize | Project | What it did | Who / how broad | Demo moment | Core they built | Why it won |
|---|---|---|---|---|---|---|
| **2025 Greenprint (Sustainability track) + Best Use of FREE-WiLi** | **Wattson** | A virtual pet on a FREE-WiLi that loses health while your lights are left on; saving energy earns cosmetics | Everyone who leaves lights on. **Universal, daily** | Switch the room light off and the pet on the device's screen recovers | OpenCV compares photo brightness every 15 s; a Pet class; a custom Pillow-drawn GUI on the FREE-WiLi screen [V] | A physical, playful object in a 15-entry pool of mostly apps and dashboards [V]. The FREE-WiLi API learning curve was its main challenge [V]. Technically thin, but tangible. |
| 2025 Base44 (sponsor; sustainability challenge) | **EcoScout** | Scan a barcode to get a 0–100 EcoScore, greener swaps and an impact dashboard | Every shopper. **Universal, weekly** | Scan a product and get its score and a swap | A multi-agent pipeline on Base44. LCA data was incomplete, so fallback rules filled gaps [V] | Base44's challenge went only to workshop attendees, so the pool was small [F]. **It did not win the track.** |
| 2025 AgentMail (sponsor) | **GreenPrint** (solo) | An IoT hub and dashboard; agents email an analysis when CO₂ spikes | Buildings. **Broad, constant** | Sensor data comes in and an agent emails a diagnosis | Elixir/Phoenix LiveView, Mastra agents and AgentMail. **Never deployed** [V] | A load-bearing use of AgentMail; won while admitting gaps [V]. |
| 2025 Overdrive (Optimization track) | **Ventura** (solo) | Reuses semantically similar past AI answers so queries aren't re-run, pitched as saving compute and energy | Everyone using AI. **Broad, daily** | Ask a question and see the top-3 similar posts | A home-built FastEmbed similarity service; auth and Gemini didn't work [F] | A clear one-line framing in a thin category. It also opted into Greenprint [V]. |
| **2024 Sustainability track** | **FarmX** | Predicts the right nitrogen amount and crop yield from temperature, humidity, pH and rainfall | Michigan farmers; fertilizer overuse as a climate lever. **Bounded, seasonal**, but on the producer side | Enter conditions and get a nitrogen recommendation and yield forecast (deployed on Streamlit) | Random-forest models on public crop and fertilizer datasets [V] | A local Michigan hook plus a climate mechanism (fertilizer greenhouse gases). Among the 14 track entries, it was one of only two aimed at producers or planners rather than consumers; the other was SolarVista, which also won (my own count from taglines) [I]. |
| 2024 MLH Best Use of MATLAB | **SolarVista** | Maps where solar installations make sense, for NGOs and planners | Energy planners. **Bounded** | Enter a region and get three suitable sites | Python ML plus a Next.js/Flask bridge [V] | Fit the sponsor's tool, aimed at the system level [V]. |
| 2024 MLH Best Use of Streamlit | **Dynamic Load Balancing for Energy-Efficient Cloud Computing** | Routes data-center tasks toward servers with more reliable renewable energy | Data-center operators. **Bounded, constant** | A Streamlit dashboard of task routing | Framed as a k-server problem: an LSTM weather forecaster on EIA and Open-Meteo data plus a randomised weighted heuristic. **No CO₂ savings figure** [V] | Classic CS theory on a climate problem. It entered a different theme, not Sustainability [V]. *This is the "clean hours" shape, and it already won here.* |
| 2023 MHacks 15, 2nd overall | **Carbon Footprint Extension** | See §2 | Universal | — | — | See §2 |
| 2023 MHacks 16, Caterpillar Business Value (adjacent) | **CampusCloset** | A campus apparel marketplace for buying, selling and trading | Students. **Broad** | — | React Native/Firebase [F] | Won on business value, not a sustainability pitch [F]. |
| 2021 MHacks 14, Google Cloud 1st | **F.L.U.D.D** (solo) | Basement flood sensors that text you, then **escalate to a phone call** if you don't reply within 15 min | SE Michigan homeowners after that summer's floods. **Broad-local, event-driven** | A sensor trips and your phone gets a text, then a call | Arduino Mega + ESP8266 → GCP IoT Core / Pub/Sub / BigQuery, plus Twilio [V] | The deepest GCP use in the field, on working hardware. An MLH judge related it to his own home's water problems [F]. Low weight (59-project online event). |
| 2021 MLH Google Cloud | **Water Monitor** | A Google Maps heatmap of Great Lakes water data (flow, stage, percentile) | The Great Lakes region. **Broad-regional, passive** | Toggle the heatmap layers | GLDW API → heatmap [V] | Simple, complete, regional [F]. |
| 2021 MLH Space Force (adjacent) | **Cosmic Cleaner** | Classifies space debris and sorts it into bins with Arduino servos | **Narrow**, but matched the sponsor's theme word for word | Servos sort the items | ML plus Arduino plus Qiskit [F] | The MLH judge praised a demo video filmed in real life [F]. |
| 2020 (no sustainability prize) | LORAX, EnvYard, FoodShare, Know Your Closet | Gamified green actions, a greenhouse sim, food sharing, clothing stories | — | — | — | They won only the "Wolfram Top 30" badge, which half the field received. **No signal** [F]. |

### What the sustainability winners have in common
- **They serve a constant behaviour or system, not a rare event**: lights every day, browsing constantly, fertilizer every season, data-center load all the time, building CO₂ all the time. F.L.U.D.D is the one event-driven winner, and it was a small online year where the sensors run all the time anyway.
- **Each makes something physical or invisible visible**: a pet that sickens (Wattson), a footprint counter (Carbon Footprint Extension), a heatmap (Water Monitor), a ringing phone (F.L.U.D.D).
- **The technical depth is low.** No MHacks sustainability winner trained a novel model or built hardware beyond a board plus sensors. The top-level winners did.
- **Measured impact is almost always missing.** Carbon Footprint Extension gives no CO₂ method, and Dynamic Load Balancing gives no savings figure [V]. A real, measured impact number would set a project apart [I].

---

## 4. The breadth test: winners vs. the rejected ideas

| Project | Who has the problem | How often | One-sentence value a judge feels | Demo specificity |
|---|---|---|---|---|
| SunLite (1st 2021) | Everyone | Daily | "Wake up gently" | One bulb, one text |
| Terminal.AI (2nd 2023) | Every developer | Many times a day | "Fix the error without leaving the terminal" | One stack trace |
| DECO.ai (1st 2023) | Anyone furnishing a room | Occasional, costly | "See the couch in your room before you buy it" | One scanned chair |
| FocusFlow (RU 2024) | Anyone reading a long doc | Daily | "Stay focused while reading" | One PDF, one webcam |
| V²/R (Grand 2024) | Every EE student | Every lab | "Do the circuit lab anywhere" | One LED, the EECS 215 room |
| ASI (Grand 2025) | Every sandwich shop | Every order | "A robot makes your sandwich" | One sandwich, vs. a human |
| Wattson (Greenprint 2025) | Everyone | Daily | "Your pet suffers when you waste power" | One room light |
| *Clean Hours (rejected)* | Dryer owners on a dirty grid | A few times a week | Needs marginal emissions explained first: the benefit is invisible and small per load | — |
| *Fern on Call (rejected)* | Older people living alone, during heat or smoke | A few days a year | Clear, but for a group judges don't belong to, triggered by an event that isn't happening this weekend | — |

**What "niche" really meant [I]:**
- **Fern on Call failed on frequency and on who it served.** Its user group is not one the judges belong to, and its trigger is rare.
- **Clean Hours failed differently.** Laundry is universal, so audience size wasn't the problem. The value was invisible: a judge needs a lesson on grid carbon intensity before the benefit lands, and the per-household effect is small. Wattson had a similarly small behaviour (lights), but made the stakes visible and emotional in one glance.
- **The working test:** could a judge say "I have that" or "my roommate has that" within 5 seconds, and see the effect happen within 20?

---

## 5. Winning formula for MHacks (concrete)

1. **Broad problem, specific demo.** Pick a problem most judges have (universal or broad, at least weekly), then demo it with one named user, one object and one number. Every top-level winner in §2 fits. *Category* prizes are where narrow, vulnerable users win (NurseNotes, CogniCare, Dementia Assistant, HopeHire, Plasma Desk) [F]. For the main track and Grand Prize, aim at the broad version.
2. **A "watch it happen" moment within 20 seconds, ideally physical or embodied.** Examples: the arm makes a sandwich, the LED lights in VR, the scanned chair appears in the room, the bulb glows, the page reacts to your gaze, Wattson's pet recovers. Physical and XR projects took the top MHacks-run prize in 2024 and 2025 [F]. Participatory demos draw crowds; MotionSurfer credited attention from judges [F].
3. **One technical core the team built and can name in a sentence.** ASI trained its own ACT policy, V²/R wrote its own circuit solver, FocusFlow trained its own LSTM, DECO.ai built a NeRF pipeline, and Dementia Assistant trained its own face model [F/V]. In 2023, 14 of 24 MHacks 16 winners already called an LLM, so an LLM call is not a core [F]. V²/R won the Grand Prize with no LLM at all [V].
4. **One hard number on screen.** Examples: ASI's ~4 h of training on one 4090 for $200 of arms, and its claim to beat a human [V]; FocusFlow's 7.1M figure [V]; Pixzip's 93% smaller files; NurseNotes' 41% [F]. Sustainability winners almost never measured impact, which is an opening [V/I].
5. **A local hook.** Examples: the EECS 215 lab (V²/R), Michigan farms (FarmX), SE Michigan floods (F.L.U.D.D), a Michigan Daily statistic (MCall) [F/V]. A local hook makes a broad problem feel concrete. It doesn't make it niche.
6. **Works live, end to end; cut what doesn't.** BoundaryML's 2024 rubric listed "does it demo live" first. Aipeiron cut latency to fit the 3-minute slot. Sportable and Ventura won while saying what they had cut [F].
7. **Well-rounded beats spiky.** In 2021, judges used "well-rounded" for both 1st and 3rd, and praised the UI on 2nd [F]. The four MHacks criteria are unweighted: Innovation, Technical Complexity, Usability (including "impact on a broader audience") and Adherence to Theme [F 2025 R1].
8. **Sponsor tech must be load-bearing, and plan for one prize.** In person, 30 prizes went to 30 different projects in 2024. In 2025 only 2 of 30 winners took two prizes, and one of those was Sustainability + FREE-WiLi (Wattson) [F].
9. **Document for judges who read.** Film a demo video in real life (the MLH judge preferred that). Link a public GitHub repo. Write a Devpost of about 500 words: MHacks 16 winners had a median of ~505 words versus ~379 for non-winners [F].
10. **Stay at the table.** Expect a ~3-minute pitch, repeated to several judges, with sponsors judging in parallel. MDredd's pairwise draw may count an empty table as a strike [F]. Under pairwise judging, the project whose problem the judge recognises instantly has the edge [I].

---

## 6. Sustainability-specific lessons

1. **The track is small and soft, and the Grand Prize is hard.** The pools were 14 entries (2024) and 15 (2025) [V]. Track winners were thin technically, so a sustainability project that clears §5 items 2–4 is unusually well placed for the track. To compete for the Grand Prize it also needs item 3, which no MHacks sustainability winner has had [I].
2. **Don't build the consumer guilt app.** Recycling classifiers, food-waste trackers, meal planners, footprint calculators and eco-chatbots went **0 for 14** across the two pools [V] (§7). Judges at a 122-table science fair have seen them [I].
3. **Winners touched a resource system, not just a person's conscience.** FarmX (fertilizer), SolarVista (siting), Dynamic Load Balancing (data-center energy), GreenPrint (building CO₂) and Ventura (compute) all fit. That matches the 2026 track wording: "rethink energy, climate, and resource systems". Wattson is the exception, and it won by being physical and funny.
4. **Make the invisible visible, physically if you can.** Energy, carbon and water are invisible, so the winners turned them into something you can see: a sick pet, a footprint counter, a heatmap, a ringing phone. Peer events show the same thing. HackMIT 2025's sustainability winner, Griddy, built a working micro-grid with homemade iron-air batteries [V]. TreeHacks 2025's sustainability-track prizes included a CO₂-removal prediction site (seen in a search summary only) and a Waterloo team's planting-decision app (Stanford Daily) [V]. Both are system-level tools rather than personal-guilt apps.
5. **Frequency matters as much as audience size.** Winners targeted daily or constant flows (lights, browsing, load, CO₂). Rare-event adaptation (heat, smoke) has no top-level MHacks precedent, and its demo has to be a replay [I].
6. **Measure the impact.** No MHacks sustainability winner showed a validated saving. A before/after number measured during the hackathon would be a real differentiator for Innovation and Technical Complexity [I].
7. **FREE-WiLi + Sustainability is a proven pairing, but the look-alike risk is high.** Wattson already won both. A pet-on-a-device that reacts to wasted energy would read as a copy [F].
8. **Sponsor prizes in the sustainability space reward the sponsor's own archetype, not the climate story.** EcoScout won Base44 rather than the track. GreenPrint won AgentMail. SolarVista won MATLAB [V].

---

## 7. Saturated sustainability ideas to avoid

| Idea shape | Already at MHacks (2020–2025) | Elsewhere | Result |
|---|---|---|---|
| "Is this recyclable?" photo classifier / recycling assistant | AIRecycler (2025), Recyclify, RecycleBuddy, Eco Reward (2024) [V] | HackerEarth's 2025 stock idea list ("plastic waste classifier") [V]; Ecobot in MLH's Avanade top 10 [V] | 0 of 4 won at MHacks |
| Food-waste fridge tracker / surplus food to charity / sustainable meal planner | FridgeFresh, Fresco, Replate, Squash, Sift (2024), Terava (2025) [V]; FoodShare (2020) [F] | HackerEarth stock idea [V] | 0 of 6 won |
| Personal carbon footprint tracker or calculator | Carbon Footprint Extension (placed at online MHacks 15) [V]; EcoAgent, TLI (2025) [V] | HackerEarth's #1 sustainability idea [V]; C4 Carbon Media (MLH Avanade) [V] | Won once in a small online year; 0 since |
| Sustainability chatbot / "all-in-one climate education" | GreenBrother (2024), Enviducate, TLI (2025) [V] | — | 0 of 3 |
| Barcode eco-score / green shopping cart | EcoScout (won Base44 only), EverCart (2024) [V] | — | Never won the track |
| Gamified green habits / pet that suffers when you waste | **Wattson won (2025)** [V]; LORAX (2020), Mailopolis (2025), Eco Reward (2024) [V/F] | Plantagotchi (MLH Avanade) [V] | Taken; a copy reads as a copy |
| Clean-hours / carbon-aware scheduling of loads | **Dynamic Load Balancing won (2024)** [V]; Carbon ∅ (2025) [V]; the team's own Clean Hours | — | Taken; rejected by the team |
| Smart plant care / greenhouse / auto-watering / hive monitor | Magic Seeds (2024), Greenhouse Butler, Swarm (2025) [V] | Plantagotchi [V] | 0 of 3 |
| Environmental-data heatmap dashboard | Water Monitor won (2021) [V]; Enviducate (2025) [V] | HackerEarth "water quality monitoring" [V] | Taken; 2025's pool was described as mostly dashboards [F] |
| Crop/fertilizer recommendation ML on public datasets | **FarmX won (2024)** [V] | Crops+ (Avanade) [V]; TreeHacks 2025 planting app [V] | Taken |
| Solar/wind siting maps | **SolarVista won (2024)** [V] | Your Biggest Fan (Avanade) [V] | Taken |
| Generic IoT "monitor + alert" sustainability hub | **GreenPrint won (2025)** [V] | HackerEarth IoT water monitor [V] | Taken |
| Elder or vulnerable check-in on climate hazard days | CogniCare and Dementia Assistant won the elder-companion shape [F] | ElliQ, many Devpost clones [F] | Rejected as niche by the team |

**Open space [I, from 2024–2025 taglines only]:** no Sustainability entry in either pool was mainly about transport or commuting, heating and cooling of homes or dorms, campus-scale energy or water systems, or repair and e-waste. Absence from two 15-project pools is weak evidence, so treat it as a hint, not proof.

---

## 8. A one-minute filter for the next candidate idea [I]

Answer each question yes or no. Keep an idea only if it passes 1 and 3, plus at least four of the other five:
1. Will most judges say "I have that" or "my roommate has that" within 5 seconds?
2. Does the problem happen at least weekly?
3. Can a judge **see** the effect happen at the table within 20 seconds?
4. Is there one piece the team builds that isn't an API call (a model, solver, signal pipeline or controller), and can you name it in one sentence?
5. Can you show one measured number (before/after, accuracy, kg, $, minutes)?
6. Does it touch a resource system (energy, water, materials, food production, transport), not just someone's guilt?
7. Is it absent from the §7 table?

Checked against questions 1–5 [I]:
- ASI passes all five.
- SunLite and V²/R pass four each: SunLite has no number, and V²/R has no impact number.
- DECO.ai passes three, failing on frequency and on a measured number. Its research-grade core carried it.
- Clean Hours fails 3, because the benefit is invisible. It arguably fails 1 as well: judges do laundry but don't feel grid timing as a problem.
- Fern on Call fails 1 and 2.

---

## Sources

**Team research files (read in full)**
- `/Users/anvaytodkar/Code/mhacks/results/year-research/2025.md`, `2024.md`, `2023.md`, `2022.md`, `2021.md`, `2020.md`
- `/Users/anvaytodkar/Code/mhacks/results/SUMMARY.md` ("Lessons from six years of MHacks winners", "Cross-check")
- `/Users/anvaytodkar/Code/mhacks/results/pivot-ideas/01-past-winner-patterns.md`, `00-synthesis.md`

**Re-verified today on Devpost [V]**
- Artificial Sandwich Intelligence: https://devpost.com/software/artificial-sandwich-intelligence
- V²/R: https://devpost.com/software/v-r
- FocusFlow: https://devpost.com/software/focusflow-ucwma0
- DECO.ai: https://devpost.com/software/deco-ai
- Terminal.AI: https://devpost.com/software/terminal-ai
- LumiGUI: https://devpost.com/software/lumigui
- Carbon Footprint Extension: https://devpost.com/software/carbon-footprint-extension
- Wattson: https://devpost.com/software/wattson-5btsyd
- EcoScout: https://devpost.com/software/ecoscout-g01h43
- GreenPrint: https://devpost.com/software/greenprint-c2deb1
- FarmX: https://devpost.com/software/farmx-zpw0yq
- SolarVista: https://devpost.com/software/solarvista
- Dynamic Load Balancing: https://devpost.com/software/dynamic-load-balancing-for-energy-efficient-cloud-computing
- F.L.U.D.D: https://devpost.com/software/f-l-u-d-d
- Water Monitor: https://devpost.com/software/water-monitor-96zalt

**Sustainability pools (entries listed today [V])**
- MHacks 2025 Greenprint opt-ins (15): https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90481. Includes https://devpost.com/software/airecycler · https://devpost.com/software/enviducate · https://devpost.com/software/mailopolis · https://devpost.com/software/tli-the-lorax-initiative · https://devpost.com/software/terava · https://devpost.com/software/greenhouse-butler-agricultural-work-assistant · https://devpost.com/software/carbon-mosg1n · https://devpost.com/software/ecoagent-kdyst3 · https://devpost.com/software/swarm-4uzerb · https://devpost.com/software/ventura
- MHacks 2024 Sustainability theme (14): https://mhacks-2024.devpost.com/submissions/search?filter%5Btheme%3F%5D%5B%5D=sustainability. Includes https://devpost.com/software/squash · https://devpost.com/software/fridgefresh-yzcjh1 · https://devpost.com/software/fresco-13zfns · https://devpost.com/software/recyclify-7t05rg · https://devpost.com/software/sift-na7j51 · https://devpost.com/software/evercart · https://devpost.com/software/recyclebuddy-mkvu9j · https://devpost.com/software/eco-reward · https://devpost.com/software/greenbrother · https://devpost.com/software/replate-eyqrsw · https://devpost.com/software/magic-seeds · https://devpost.com/software/foundai

**Other winners cited (via year files [F])**
- Cosmocook https://devpost.com/software/cosmocook · Gemini Forge https://devpost.com/software/mhack · Rusteze https://devpost.com/software/rusteze-t0r5ak · VSAT https://devpost.com/software/vsat · MyNewsWire https://devpost.com/software/mynewswire-45dlzk · SunLite https://devpost.com/software/sunlite-sunrise-lamp · Shadow Clone https://devpost.com/software/shadow-clone · MCall https://devpost.com/software/freeshirt-exe · Dystic https://devpost.com/software/dystic · we-Learn https://devpost.com/software/we-learn · Sportable https://devpost.com/software/sportable · Ventura https://devpost.com/software/ventura · CampusCloset https://devpost.com/software/campuscloset · Cosmic Cleaner https://devpost.com/software/spacejunk · LORAX https://devpost.com/software/lorax-luring-others-to-retain-our-abode-extensively
- Category-level narrow-user winners: NurseNotes https://devpost.com/software/nursenotes · CogniCare https://devpost.com/software/cognicare-companion-app-for-memory-support · Dementia Assistant https://devpost.com/software/dementia-assistant · HopeHire https://devpost.com/software/hopehire-2s6zq3 · Plasma Desk https://devpost.com/software/plasma-desk · SoundSense https://devpost.com/software/soundsense-jvz6yx
- MHacks 2021 closing ceremony (judge remarks, auto-captions): https://www.youtube.com/watch?v=YMbf9pfdGZg
- MHacks 2025 rules (criteria incl. "impact on a broader audience"): https://mhacks-2025.devpost.com/rules · MDredd pairwise judging: https://github.com/mhacks/MDredd

**Outside evidence (checked today [V])**
- HackerEarth, "50+ Hackathon Ideas" (Jul 1, 2025; stock sustainability ideas): https://www.hackerearth.com/blog/hackathon-ideas
- MLH, top 10 Avanade Best Sustainability Hack winners (Oct 24, 2023): https://blog.mlh.com/top-10-prize-winning-hackathon-projects-for-the-avanade-best-sustainability-hack-challenge-10-24-2023
- Khoury News on HackMIT 2025 sustainability winner Griddy (Feb 5, 2026): https://www.khoury.northeastern.edu/khoury-undergrads-win-three-categories-at-prestigious-mit-hackathon
- Stanford Daily, TreeHacks 2025 winners (Feb 18, 2025): https://stanforddaily.com/2025/02/18/treehacks-awards-200000-in-prizes-to-students-from-around-the-world/

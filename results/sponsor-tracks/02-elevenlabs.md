# Sponsor Track Advocate — Best Project Built w/ ElevenLabs

## Prompt given (excerpt)
> You are the advocate for the sponsor track "Best Project Built w/ ElevenLabs" at MHacks 2026. Research the sponsor's tech and how fast a team can integrate it, what its judges reward, prize value vs competition, expected value, how it stacks with the main/fun picks and other sponsors, 2–3 winning project sketches, honest red flags, and a 1–10 scorecard. Make the strongest honest case — an impartial judge will weigh your file against eleven other sponsor advocates.

---

## 0. Bottom line

**ElevenLabs should be the team's voice layer and a secondary sponsor entry, not the reason for the project.** Its prize is credits, not cash, and the track will be crowded. What it offers is the cheapest big upgrade to the demo, a free double entry with Relay, and a clean split with SpaceX.

- **The integration is almost free.** Every MHacks participant gets 1 month of the Creator tier ([Tracks & Prizes][H2]). Basic text-to-speech takes about 30 minutes. A hosted voice agent with tools takes 3–4 hours. A "best use"-grade build takes **about 6 person-hours** (my estimate, §1).
- **One integration counts for two sponsors.** Relay ships an official bridge (`@relaymessenger/elevenlabs`) that connects an ElevenLabs Agent to a Relay call and drives a lip-synced Rive character ([Relay docs][R2]). Relay is on the team's shortlist.
- **It doesn't break SpaceX if you split the work.** SpaceX requires "the Grok Imagine **or** Voice API" ([Tracks & Prizes][H2]). Use **Grok Imagine** for visuals to qualify for SpaceX, and let ElevenLabs handle every sound. The conflict is real only if the team picks Grok *Voice*.
- **The track will be crowded.** I counted opt-ins at 35 student hackathons from 2025–26 with an ElevenLabs prize: **844 of 4,547 projects (18.6%)** entered. The two events with the same direct-from-ElevenLabs Scale-tier prize as MHacks drew **29–32%** ([HackRice 16][D-rice], [Hack the 6ix 2026][D-6ix]). At MHacks 2025, with no ElevenLabs prize, only **1 of 122** projects used it, and that one won the fun prize ([Judy AI][P-judy]). **Expect 25–40 MHacks entrants (inference).** About 30% of them will make voice central, so roughly **8–12 real contenders**.
- **What wins "best use" is voice as the interface, not a read-aloud button.** In 35 ElevenLabs prize winners I verified, the pattern is consistent. Winners made voice the whole product, used two or more ElevenLabs capabilities, and engineered around latency (§2). The one rubric ElevenLabs has published scores "Agentic Depth: Does the project go beyond simple text-to-speech?", plus interaction design, technical integration and novelty ([Hack the 6ix 2026][D-6ix]).
- **Expected value is modest on paper and good per hour of work.** The prize lists at **$3,588 for a team of 4** (3 months of Scale at $897 per member) ([Tracks & Prizes][H2]). Its realistic cash-equivalent is far lower (§3). My estimate is P(win) ≈ **10%** for a voice-central build and ≈2–3% for a token one. If the project already talks (a Relay call agent, a narrated SpaceX visual), the extra entry costs about 2–4 hours.

**Scorecard:** prize value 5 · win probability 4 · integration ease 9 · stacking 7 · demo impact 8 · fit with team preferences 6.

**Main/fun pick:** keep the judge's **Sustainability + Judged by an LLM**. ElevenLabs fits it if voice is how the user uses the product (Sketches A and B). It fits even better if the team flips to Hardware (Sketch C). Voice-on-a-device builds took 6 of the 35 winners, and FREE-WILi 2 has a speaker and a microphone array ([freewili.com][FW]).

---

## 1. The technology: what it is and how fast you can ship it

### What ElevenLabs offers (verified from docs)
| Capability | What it gives you | Doc |
|---|---|---|
| **Text to Speech** | Models: **Eleven v4** (newest, "most emotive"; 10,000-char limit), **v4 Turbo** (~100 ms median latency, audio tags), **v3 Conversational** (~280 ms), **Flash v2.5** (~75 ms, 32 languages), Multilingual v2 | [TTS models][E-tts] |
| **Speech to Text (Scribe)** | Batch and realtime transcription | [Docs index][E-llms], [API pricing][E-papi] |
| **ElevenAgents** (formerly Conversational AI) | Hosted voice agent: "a fine-tuned Speech to Text (ASR) model," an LLM you choose, low-latency TTS "across 5k+ voices and 70+ languages," and a proprietary turn-taking system. Tools (API/client), knowledge base/RAG, Twilio and SIP telephony, embeddable widget, and React, React Native, Swift and Kotlin SDKs | [Agents overview][E-agents] |
| **Custom LLM for agents** | Any OpenAI-compatible Chat Completions or Responses endpoint ("Enter the server URL and the Model ID of your custom LLM server") | [Custom LLM][E-cllm] |
| **Speech Engine** | "Adds voice capabilities to any chat agent." You bring your own LLM server, and it handles STT, TTS, turn-taking and interruption | [Speech Engine][E-se] |
| Sound Effects, Music, Voice Design, Instant/Professional Voice Cloning, Dubbing, Voice Isolator/Changer | One shared credit pool; Music ~$0.15/min, SFX ~$0.12/min via API | [Docs index][E-llms], [API pricing][E-papi] |

SDKs: `pip install elevenlabs` and `npm install @elevenlabs/elevenlabs-js`. The quickstart's default is model `eleven_v4`, voice "George" ([Quickstart][E-qs]). The no-code path is a one-line web widget: `<elevenlabs-convai agent-id=…>` plus a script tag ([Agents quickstart][E-aqs]).

**Grok as the brain.** The xAI API is OpenAI-SDK-compatible at `https://api.x.ai/v1` ([xAI tutorial][X-tut]), so it can serve as an ElevenAgents custom LLM ([Custom LLM][E-cllm]). *Inference:* I have not tested this end to end. Using Grok as the LLM does **not** satisfy SpaceX, which requires Grok **Imagine or Voice** ([Tracks & Prizes][H2]).

### Access and cost
| Plan | Price | Credits/mo | Relevant limits | Source |
|---|---|---|---|---|
| Free | $0 | 10k (~10 min TTS) | **No Instant Voice Cloning, no commercial license; 2 concurrent TTS requests; 15 agent call-minutes, 4 concurrent calls** | [Pricing][E-price], [Agents pricing][E-pag] |
| **Creator (free for every MHacks participant, 1 month)** | $22 | 121k per ElevenLabs' page (the handbook says "131k") | IVC + PVC, 5 concurrent TTS, **275 agent call-minutes, 10 concurrent calls** | [Tracks & Prizes][H2], [Pricing][E-price], [Agents pricing][E-pag] |
| Pro | $99 | 600k | 44.1 kHz PCM via API | [Pricing][E-price] |
| Scale (the track prize, 3 months) | $299 | 1.8M | 3 seats, 15 concurrent, 3,738 agent minutes | [Pricing][E-price], [Agents pricing][E-pag] |

Agent overage costs $0.08/min ([Agents pricing][E-pag]). The Creator allowance easily covers a 24-hour hackathon. How participants redeem the Creator month is **unverified**: it is not in the handbook. Ask on the MHacks Discord in hour one.

### Realistic integration time (my estimates, for one developer who knows web/AI APIs)
| Level | Work | Hours |
|---|---|---|
| Token TTS | SDK call, then play an MP3 | 0.5 |
| Hosted agent + widget | Dashboard agent, prompt, voice choice, embed | 1–2 |
| Agent + server tools (webhooks into your own API) ± custom LLM | Tool schemas, prompt, testing | 3–4 |
| + Relay bridge | `ElevenLabsCall.connect({relay, callId, elevenlabs:{apiKey, agentId}})` inside `call.created` ([Relay docs][R2]) | +1–2 (inference; not tested end to end) |
| Best-use polish | Voice design or cloning, v4 audio tags, SFX/Music stingers, latency tuning, transcript UI | 2–3 |
| **Best-use-grade total** | | **≈6** |
| DIY STT → LLM → TTS chain with Twilio | The path that cost past winners hours (below) | 8–10 |

### Known gotchas (with evidence)
1. **Free-tier "unusual activity" blocks.** Users report "Unusual activity detected. Free Tier usage limit has been reached," and free-tier blocks on data-center IPs ([elevenlabs-python #119][G2], [GitHub issue search][G2s]). *Fix:* redeem the Creator month before building, and don't make a free account per teammate on shared Wi-Fi.
2. **Free accounts can't use library voices via the API.** HTTP 402: "Free users cannot use library voices via the API. Please upgrade your subscription to use this voice" ([GitHub issue search][G1]). Creator fixes this.
3. **Concurrency.** `concurrent_limit_exceeded` ([Errors][E-err]). Free allows 2 concurrent TTS requests and Creator allows 5 ([Pricing][E-price]). Judges hitting the demo while teammates test can trip this.
4. **Latency in a hand-built pipeline.** UGAHacks 11's ElevenLabs winner: "too many moving parts (Twilio → Server → Gemini → ElevenLabs)… getting the latency down… took hours" ([Lifeline][P-lifeline]). TreeHacks 2025's winner rewrote its Python client tools in Next.js "with only hours left," with help from an ElevenLabs sponsor rep ([CodeCrack][P-codecrack]). *Fix:* use the hosted agent and its turn-taking instead of chaining services yourself.
5. **Twilio trial accounts block live audio streaming.** One ShellHacks 2026 winner fell back to turn-based calls ([Public City Announcements][P-pca]). Prefer the Relay app or the web widget for the demo.
6. **Product names change fast.** v4 and "Speech Engine" are new, and v4 has a "3x credits… until October 12" promotion ([Pricing][E-price]). Follow current docs, not old tutorials.

### MHacks 2026-specific resources
- The live schedule has **no ElevenLabs workshop or session**. Relay, Fetch.ai, FinchNode, SpaceXAI, Figma and FREE-WILi have sessions ([live schedule][L]). *Inference:* on-site ElevenLabs mentors are uncertain, so plan to be self-sufficient. Check the Sponsor Expo.
- Judging: sponsors judge their tracks while main judging runs (12:30–2:30 PM Oct 4), and "to be judged for any track, your team must be present" ([Handbook][H1]).
- MHacks hasn't had an ElevenLabs track before. In 2025 there was no ElevenLabs prize, and 1 of 122 projects used it ([MHacks 2025 gallery][M25]; my scan of all 122 project pages, §3).

---

## 2. What ElevenLabs judges reward

### Published criteria (MHacks gives only "best use of ElevenLabs")
- **Hack the 6ix 2026, ElevenLabs' own track (6 months of Scale as the prize).** This is the most detailed rubric ElevenLabs has posted for a student event ([Hack the 6ix 2026][D-6ix]):
  - *Agentic Depth:* "Does the project go beyond simple text-to-speech? We prioritize autonomous agents that handle complex logic and real-time dialogue."
  - *Interaction Design:* "low-latency response times and emotional inflection."
  - *Technical Integration:* creative API use, "especially multimodal implementations (Voice + Video)," or prompt engineering for the agent's personality.
  - *Novelty:* "A use case we haven't seen before that solves a real-world problem using conversational AI."
- **TreeHacks 2025 (judged by ElevenLabs):** "the most creative and impactful hack that pushes the boundaries of what's possible with AI voice technologies," using TTS, Conversational AI, "or any of our other products" ([TreeHacks 2025][D-tree]).
- **MLH's ElevenLabs prize copy:** "interactive AI companions… narrated stories and voice-enabled apps" ([HackGT 13][D-gt] and others).
- **MHacks precedent:** in 2024, Cartesia's TTS prize at MHacks judged "how central and impactful text-to-speech is" ([2024 year research][Y24]).

### Who won: 35 ElevenLabs prize winners, 2025–26 (verified from Devpost winner badges)
I took every project that opted into an ElevenLabs prize and carried a winner badge, then confirmed on its project page that the badge was for the ElevenLabs prize. That gave 35 winners across 34 events. The most informative ones:

| Event (prize type) | Winner | What it is, and how ElevenLabs was used |
|---|---|---|
| **HackRice 16, Sep 2026 (direct, 3 mo Scale, same as MHacks) + MLH** | [SingBack][P-singback] | Karaoke party game. "ElevenLabs handles lyric transcription and host narration." It degrades gracefully when the APIs are slow. **Won both ElevenLabs prizes.** |
| **Hack the 6ix 2026 (direct, 6 mo Scale)** | [feetball][P-feet] | 22 AI agents play football while 1,000+ agents bet. ElevenLabs is the live commentator, built from pre-generated clip banks stitched in WebAudio because "a live round-trip would always lose the race." |
| **TreeHacks 2025 (ElevenLabs-judged)** | [CodeCrack][P-codecrack] | Voice mock interviews using ElevenLabs agents, a custom client tool (`sendNewQuestion`) and ElevenLabs' criteria-evaluation feature for feedback |
| TreeHacks 2025 | [The Duck You Mean?][P-duck] | Explain-to-learn tutor. ElevenLabs runs "the full conversation process from user mic input to duck voice" |
| Bay Hacks 2026 (direct credits) | [Cerebro][P-cerebro] | Voice-first navigation for visually impaired students: "voice the primary interaction… rather than adding it as an extra feature" |
| ShellHacks 2026 (MLH) | [Public City Announcements][P-pca] | Reads city agendas and **calls affected residents** in English or Spanish before votes |
| UGAHacks 11 (MLH) | [Lifeline][P-lifeline] | Voice intake for 911 overflow: call a real number, have a two-way conversation |
| Bitcamp 2026 (MLH) | [DoortectiveAI][P-door] | Raspberry Pi doorbell with ElevenLabs agents. Tone switches between friendly, skeptical and firm based on the threat level. Also won People's Choice |
| SB Hacks XII (MLH) | [flow.][P-flow] | Speak a concept and walk around inside a generated 3D scene with voice Q&A. Also won President's Pick |
| HackPSU S26 (MLH) | [Align][P-align] | Also won the **HackPSU Grand Prize** |
| nwHacks 2026 (MLH) | [HUDson][P-hudson] | ESP32 wearable that visualizes sound for deaf users |
| UofTHacks 13 | [Slotify][P-slotify] | Generates voice-consistent sponsor reads and finds the best spots to insert them in podcast audio |
| SwampHacks XI | [ATC-Trainer][P-atc] | Godot air-traffic-control game: speak real ATC commands and AI pilots answer |
| Hack@Brown 2026 (MLH) | [HandyDaddy][P-handy] | "FaceTime your dad for home repair advice," combining vision and voice |

The other 21 winners are listed in §Sources. Tallies across all 35 (my classification):
- **Accessibility/assistive:** 8 (23%). Examples: Cerebro, HUDson, ClearVision, Intelux, Eye AAC, ClarityAI, immi, Lume.
- **A voice persona *is* the product** (coach, tutor, simulator, interviewer): 8 (23%). Examples: CodeCrack, Duck, Saynario, CounselCoach, InterviewAI, Quack Council, ATC-Trainer, Janulus.
- **Games and audio media:** 8 (23%). Examples: SingBack, feetball, Emergency Crops, Slotify, Memo Music, Linguana, flow., Cosmo Corral.
- **Hardware device that talks:** 6 (17%). Examples: HUDson, immi, Doortective, ClearVision, Intelux, Hudson.
- **Phone-call agents:** 2. Examples: PCA, Lifeline.
- **Also won a non-ElevenLabs prize:** 9 (26%), including a Grand Prize (Align).
- **Sustainability/climate themed:** **0 of 35.** That is a risk, because nobody has proven it, and also an opening, because the rubric scores "a use case we haven't seen before."

### What separates "best use" from token TTS (audit of a direct-prize field)
I read all 38 projects that entered HackRice 16's direct "Best Project Built with ElevenLabs" prize ([gallery filter][D-rice]):
- **About 9 (≈25%)** had ElevenLabs only as a built-with tag, or not at all in the write-up (e.g., Reva, Irabu, Hoot, Callback).
- **About 17 (≈45%)** used voice as an add-on: narration, "nudges play in an ElevenLabs voice," a voice for an existing chatbot.
- **About 11 (≈30%)** made voice central or used several ElevenLabs products. Examples:
  - Mimic Mayhem: instant voice cloning, transcription, speech and character timestamps.
  - Casey: an ElevenLabs Agents scam caller.
  - Chill Pill: all audio from Eleven Music.
  - Wayne Finance: Scribe in, Turbo out.
  - Medicall: an ElevenLabs Conversational AI agent plus Twilio for live recall calls.
  - SingBack, the winner.

**The winning recipe, from the evidence:**
1. The product doesn't work with the sound off.
2. It uses at least 2 ElevenLabs capabilities: agents + tools, STT + TTS, cloning, SFX or Music.
3. Latency is designed for (feetball's clip banks, hosted turn-taking).
4. It has a personality or emotional range (commentator, host, duck, tone modes).
5. The demo works live and fails gracefully.
6. The Devpost explains *why* ElevenLabs was the right tool. feetball wrote a "Why it's good and suitable" section ([feetball][P-feet]).

---

## 3. Prize value and expected competition

### Prize (handbook text)
"All participants: 1 month free of the Creator tier ($22/month value, 131k credits). Overall winning team: 3 months of the Pro tier per team member ($297 value/member, 600k credits/mo). Best Project Built with ElevenLabs: 3 months of the Scale tier per team member ($897 value/member, 1.8M credits/mo)" ([Tracks & Prizes][H2]).

- **List value:** $897 × 4 = **$3,588** for the track winner. The **$88** Creator value (4 × $22) comes with attendance, win or lose.
- **"Overall winning team"** is ambiguous. WiCS × Opportunity Hack used the identical three-line package, and there it reads as the *hackathon's* overall winner, separate from the ElevenLabs prize ([WiCS × OHack][D-wics]). *Inference:* the Pro tier goes to MHacks' Grand Prize team. Confirm with organizers.
- **Realistic value:** credits can't be sold or turned into cash. A student who wouldn't otherwise pay for voice AI gets maybe **$100–500 of real value per team** (my judgment). It is worth close to list value only to a team that will keep building a voice product (1.8M credits/mo ≈ 30 hours of TTS per member per month, per [Pricing][E-price]). The single winner takes everything; there is no 2nd or 3rd place.

### Crowding: opt-in share at 35 student hackathons with an ElevenLabs prize (Devpost prize filters, counted 2026-10-03)
| Event | Prize type | Opted in / projects | Share |
|---|---|---|---|
| **HackRice 16 (Sep 2026)** | **Direct, 3 mo Scale** (+ separate MLH prize) | 38 / 119 | **32%** |
| **Hack the 6ix 2026** | **Direct, 6 mo Scale** | 39 / 133 | **29%** |
| ShellHacks 2026 | MLH | 81 / 294 | 28% |
| HackRU Fall 2025 | MLH | 39 / 142 | 27% |
| TreeHacks 2025 | Direct (credits + AirPods Max) | 53 / 257 | 21% |
| HackPrinceton Fall 2025 / Spring 2026 | MLH | 40/194, 26/131 | 21%, 20% |
| DeltaHacks 12 | MLH | 30 / 143 | 21% |
| UofTHacks 13 / HackTX 2025 / HackDavis 2026 | MLH / MLH-style | 31/160, 43/225, 26/138 | 19% each |
| nwHacks 2026 / Hacklytics 2026 | MLH | 31/169, 39/234 | 18%, 17% |
| DubHacks '25 / Bitcamp 2026 / TAMUhack 2026 | MLH | 32/247, 28/222, 22/171 | 13% each |
| WiCS × OHack Sp26 | Direct (same package as MHacks) | 3 / 26 | 12% |
| SB Hacks XII / CruzHacks 2026 | MLH | 6/106, 6/87 | 6%, 7% |
| **All 35 events pooled** | | **844 / 4,547** | **18.6%** (median 19%; interquartile range 13–21% among the 22 events with ≥100 projects) |

The full list of all 35 events, with links, is in §Sources. Self-reported tool use agrees: at HackGT 13, 69 of 268 projects said they used ElevenLabs (26%), and at HackRice 16, 43 of 119 (36%) ([HackGT 13][D-gt], [HackRice 16][D-rice]).

**MHacks 2026 forecast (inference):**
- **Project count:** 122 projects in 2025 and 132 in 2024 ([2025 research][Y25], [2024 research][Y24]). Assume 110–150.
- **Opt-in rate:** the direct Scale-tier format pulled 29–32% at its two closest peers. MHacks gives everyone a free Creator month, which lowers friction further. Pulling the other way, the SpaceX track pushes some voice teams toward Grok Voice.
- **Forecast:** about 20–32% → **25–40 entrants**. About 30% of them will have a voice-central build (HackRice audit), so **8–12 real contenders**.
- **Rating:** competition by raw count is **high**. Among serious builds it is **medium**.

---

## 4. Expected value vs. the other sponsor tracks

**P(win), my estimate.**
- A voice-central, multi-capability build with a live demo has roughly a top-3 chance among 8–12 contenders. Judging taste is unpredictable: at HackRice the karaoke game beat the more "agentic" Medicall and Mimic Mayhem. So P(win) ≈ **10%** (range 6–15%).
- A token TTS entry: ≈2–3%, about the 1-in-30 base rate.

**EV.**
- 0.10 × $3,588 ≈ **$360 at list value**. At realistic value, ≈ $10–50.
- Per hour of extra work: if the product already speaks, a best-use-grade entry costs about 2–4 additional hours. That is a good ticket for the time.

| Sponsor (handbook prizes [H2]) | Headline prize | Cash? | Winners | Honest comparison to ElevenLabs |
|---|---|---|---|---|
| Fetch.ai | $1,250 / $750 / $500 | Cash | 3 | Far better money and 3 winners. It also needs Agentverse/ASI:One work, and ElevenLabs can be its voice front end |
| SpacetimeDB | $1,000 / $500 / $200 | Cash | 3 | Better money. It needs SpacetimeDB at the core of the project |
| Capital One Nessie | $300 gift card per member | Near-cash | 1 | ≈$1,200 for 4, but FinTech-shaped |
| Relay | SF trip + week at Relay house | Experience | 1 + runner-up | Higher career value. **Complements ElevenLabs** through the official bridge |
| Photon | $400 + $300 credits + interview fast-track | Partly cash | 2 | Text-first (iMessage), so a weak fit with voice |
| FinchNode | Apple Watch SE3 / $500 | Mixed | 3 | Voice health intake has precedent (Healthcare Helper, MHacks 2024 [Y24]) but conflicts with a Sustainability main |
| Neon | $1,000 / $500 / $100 AI Gateway credits | Credits | 3 | Credits, like ElevenLabs, but 3 winners |
| SpaceX | Keyboards + bottle raffle | Goods | 1 | Lower value. Stacks with ElevenLabs via Grok Imagine |
| FREE-WILi / Figma / Notability | Kits / LEGO + merch / Pro + merch | Goods | 1–3 | Lower value, cheap to stack |

**Verdict on EV:** ElevenLabs is **mid-pack** on prize value. It is **near the top on marginal EV per hour** when the project is already voice-driven, and it raises the odds on Relay and on the main track, because a talking demo is memorable in a 3-minute pitch.

---

## 5. Stacking: one coherent project

**With the recommended main and fun tracks (Sustainability + Judged by an LLM):**
- **Sustainability: workable, if voice is how the user acts.** For example, an agent that calls you at the cleanest-grid hour, or a narrated satellite view of your block. None of the 35 verified winners was climate-themed. That makes the pitch novel, but voice must not be a bolt-on: the rubric marks down "simple text-to-speech" ([Hack the 6ix 2026][D-6ix]).
- **Judged by an LLM: neutral to positive.** A write-up that explains the voice pipeline (latency budget, tool calls, fallbacks) is exactly the "technically sharp" material it rewards. It costs nothing extra.
- **Dumbest Idea / Useless AI: strong.** A comic voice persona is the cheapest way to get a laugh. MHacks 2025's fun prize went to a Gemini + ElevenLabs companion ([Judy AI][P-judy]).
- **Should the main track change?** Not because of ElevenLabs. It fits **AI** best, since voice agents are native there, but AI is the most crowded main track per the verdict. It fits **Hardware** very well if the team flips (Sketch C). I accept Sustainability.

**With other sponsors:**
| Sponsor | Fit | Why |
|---|---|---|
| **Relay** | **Excellent** | Official `@relaymessenger/elevenlabs` bridge: an ElevenLabs Agent handles the Relay call, with Rive lip-sync driven by viseme alignment ([Relay call docs][R2], [Relay integration][R3]). One agent counts for two tracks. The agent "must work in the Relay app" ([Tracks & Prizes][H2]) |
| **SpaceX** | **Good if you use Grok Imagine; conflicts if you use Grok Voice** | SpaceX needs Grok Imagine *or* Voice ([Tracks & Prizes][H2]). Grok Imagine does image and video (`grok-imagine-image-2.0`, `grok-imagine-video-1.5`) ([xAI Imagine][X-img]), so ElevenLabs can own audio. Two voice engines in one product muddies both stories. Grok Voice also offers TTS, STT and voice cloning ([xAI Voice][X-voice]), so that route makes ElevenLabs redundant |
| **FREE-WILi** | **Good** | FREE-WILi 2 has an "onboard 0.5 Watt speaker and 4 channel phased-array microphone" plus Wi-Fi and IR ([freewili.com][FW]). A talking, listening device is the 17% hardware pattern among winners |
| **Fetch.ai** | Fair | An Agentverse agent is text-first. ElevenLabs can be the voice front end, and the agent's actions still count |
| **Neon / Figma / Notability** | Free stacks | No conflict: a transcript/event log in Neon, the voice UI in Figma |
| **SpacetimeDB** | Fair | Multiplayer voice games (Mimic Mayhem style) fit, but not with a Sustainability main |
| **Photon** | Weak | iMessage is text. Voice memos through Spectrum are unverified |
| **FinchNode / Capital One** | Domain conflict | Voice health intake or voice banking work, but break the Sustainability main |

**Realistic stack:** Sustainability + SpaceX (Grok Imagine) + **ElevenLabs** + Relay + Judged by an LLM, with Neon, Figma and Notability as free extras. Add FREE-WILi if someone owns the hardware.

---

## 6. Project sketches

### A. "Second Sky, Narrated": your block's satellite future as a talking documentary
*(Sustainability + SpaceX + ElevenLabs + Judged by an LLM; extends the Sustainability advocate's Direction A.)*
- **What it does:** a user enters an address. The app pulls satellite-derived data (NASA POWER irradiance, FIRMS detections, per the Sustainability file) and computes rooftop solar, heat and canopy numbers.
  - **Grok Imagine** renders a before/after video of the street in 2040 (SpaceX requirement).
  - **ElevenLabs** narrates it as a 45-second nature documentary, using v4 with emotional delivery and audio tags ([TTS models][E-tts]), with an **Eleven Music** score and **SFX** (wind, cicadas, solar inverter hum).
  - The user can then **interrupt and ask questions** of an **ElevenAgents** guide. Its server tools return the real kWh and CO₂ numbers. Optionally, Grok is its custom LLM ([Custom LLM][E-cllm]).
- **Why it can win best use:** it hits "multimodal implementations (Voice + Video)" and personality prompt engineering, which the 6ix rubric names. It uses 4 ElevenLabs capabilities (TTS, Music, SFX, Agents + tools), and it is a novel climate use.
- **Hours on the ElevenLabs part:** ~6 (narration script + audio-tag pass 1.5, music/SFX 1, agent + tools 3, latency polish 0.5).
- **Risk:** the narration could feel like a read-aloud. The agent Q&A has to be live in the demo, with the judge asking the question.

### B. "Grid Call": the energy agent you phone (or that phones you)
*(Sustainability + Relay + ElevenLabs + Judged by an LLM; FREE-WILi and Fetch.ai optional.)*
- **What it does:** you call the agent inside the **Relay app** ("can I run laundry now?"). An **ElevenLabs Agent** bridged into the call ([Relay docs][R2]) checks live MISO carbon intensity and the solar forecast through server tools. It negotiates a time ("cleanest hour is 1 AM; want me to schedule it?") and calls you back when the hour arrives.
- **Optional:** a FREE-WILi 2 next to the device announces through its speaker and switches the load over IR ([freewili.com][FW]).
- **Demo:** a judge holds the phone, the Rive avatar talks, and something on the table switches off.
- **Why it can win:** it copies the proven call-agent winners (Public City Announcements, Lifeline) and the "voice is the interface" rule (Cerebro). It ties ElevenLabs' best-use story to Relay's track in one integration.
- **Hours on the ElevenLabs part:** ~6–7 (agent + tools 3–4, Relay bridge 1–2, voice/persona polish 1).
- **Risk:** the Relay bridge path is untested by us. Keep the web widget as a fallback demo ([Agents quickstart][E-aqs]).

### C. "The Thermostat Has Opinions" (the Hardware-flip or comic version)
*(Hardware or Sustainability + ElevenLabs + FREE-WILi + Dumbest Idea / Useless AI + Judged by an LLM.)*
- **What it does:** a FREE-WILi 2 sits in the dorm. Its sensors catch waste (lights on, AC with the window open). A designed voice persona ("disappointed grandmother," made with Voice Design) **scolds you out loud** through the onboard speaker. You **argue back** through the mic array, transcribed by ElevenLabs STT, and it either negotiates or switches the device off over IR.
- **Why it can win:** a talking device (17% of verified winners) with emotional range and a comic hook (Judy AI precedent). It is novel for ElevenLabs judges and stacks every fun track.
- **Hours on the ElevenLabs part:** ~5. The hardware is extra, and the main risk.
- **Risk:** hardware time and audio quality from a 0.5 W speaker. Pair it with a laptop speaker fallback.

**My pick:** **B** if Relay is a priority, since one integration counts for two sponsors. **A** if SpaceX is the anchor. Either way, put the ElevenLabs Agent at the center, not at the edge.

---

## 7. Weaknesses, red flags, and rebuttals

| Rival argument | How strong | Rebuttal |
|---|---|---|
| "It's credits, not cash. $3,588 is a sticker price." | **Strong, and true** | Agreed. Rank it below the cash tracks on prize value. The case is marginal cost: a voice layer the project wants anyway, ≈2–4 extra hours, and a better pitch for main-track judges. |
| "One winner out of 25–40 entrants: that's a lottery." | **Strong** | The raw base rate is 2.5–4%. But ~70% of a direct-prize field is token or add-on use (HackRice audit), so a voice-central build competes with only 8–12 teams. That gives roughly 10% (inference), not a lottery. |
| "It conflicts with SpaceX, the team's favorite." | Medium | Only if the team uses Grok **Voice**. Use **Grok Imagine** for visuals, which qualifies for SpaceX ([Tracks & Prizes][H2], [xAI Imagine][X-img]), and ElevenLabs for audio. |
| "No climate project has ever won an ElevenLabs prize." | Medium | True in my sample (0/35). The 6ix rubric rewards a use case judges "haven't seen before." Sketches A and B follow proven winner patterns (narrated multimodal media; call agents) applied to a new domain. |
| "No ElevenLabs rep on the schedule; who even judges?" | Medium, **unverified** | No ElevenLabs session is listed ([live schedule][L]). Make the Devpost carry the argument: a "Why ElevenLabs" section like feetball's, and a demo video that shows the live agent. |
| "Voice demos die in a loud judging hall." | Medium | Real risk (my inference). Bring a headset or speaker, show a live transcript on screen, and pre-record a fallback clip. Hosted turn-taking handles barge-in ([Agents overview][E-agents]). |
| "Every team will add a voice now that Creator is free." | Medium | That is why §2's recipe matters. Most will add TTS. Few will add agents + tools + a second capability with a latency plan. |
| "Relay's bridge or Grok-as-custom-LLM may not work." | Medium, **untested** | Both are documented ([Relay docs][R2], [Custom LLM][E-cllm]). Spike it in the first two hours; the fallback is the ElevenLabs widget plus the default LLM. |

**Red flags to watch:** how to redeem the Creator code (ask in hour one); free-tier IP blocks; the 402 error for library voices; who the "overall winning team" for the Pro tier is; the ~121k vs "131k" credit discrepancy (immaterial).

---

## 8. Scorecard (1–10)

| Criterion | Score | One-line justification |
|---|---|---|
| Prize value | **5** | $3,588 list for 4 is among the highest sticker values, but it is non-cash subscription credit with a single winner. Realistic value is a few hundred dollars. |
| Win probability | **4** | 25–40 expected entrants (18.6% pooled; 29–32% at direct-Scale peers). ≈10% only with a voice-central build. |
| Integration ease | **9** | Free Creator tier for everyone, TTS in 30 min, hosted agent in 1–2 h, best-use grade ≈6 h. Gotchas are known and avoidable. |
| Stacking potential | **7** | Native Relay bridge, FREE-WILi 2 speaker and mics, SpaceX via Grok Imagine, all fun tracks. Weak with Photon, conflicts with Grok Voice, and Sustainability is unproven terrain. |
| Demo impact | **8** | A judge talking to the product beats any slide. 26% of verified winners also took another prize, including a Grand Prize. |
| Fit with team preferences | **6** | Not on the shortlist, but it strengthens two shortlisted sponsors (Relay, SpaceX) and suits a software-strong team. |

---

## 9. Day-of checklist (if the team enters)
1. **Hour 0–1:** redeem the Creator month for every teammate; ask organizers how. Confirm who the "Overall winning team" for the Pro tier is, and who judges ElevenLabs.
2. **Hour 1–3:** spike an ElevenAgents agent with one server tool. Bridge it into Relay ([Relay docs][R2]) or embed the widget. Decide Grok Imagine (not Grok Voice) for SpaceX.
3. **Build:** voice is the main way into the product. Use at least 2 ElevenLabs capabilities. Use the hosted turn-taking, and use v4 Turbo or Flash where latency matters ([TTS models][E-tts]).
4. **Devpost:** add a "How we used ElevenLabs and why" section with a latency budget, a fallback description, and a live-agent clip in the video.

---

## Sources

**MHacks 2026 (official)**
- [H1] 2026 Hacker Handbook (judging, presence rule, Devpost TBD): https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af (retrieved via Notion's public page API, 2026-10-03)
- [H2] Handbook › Tracks & Prizes (ElevenLabs, Relay, SpaceX and all sponsor texts and prizes): https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5
- [L] MHacks live schedule (no ElevenLabs session listed): https://www.mhacks.org/live
- [M25] MHacks 2025 gallery (122 projects; my scan of every project page found ElevenLabs only in Judy AI, plus a "what's next" mention in Dill.study): https://mhacks-2025.devpost.com/project-gallery
- [P-judy] Judy AI (MHacks 2025 Brainrot winner, Gemini + ElevenLabs TTS): https://devpost.com/software/judy-ai-4vc9ah · Dill.study: https://devpost.com/software/dill-study
- [Y24] Internal: /Users/anvaytodkar/Code/mhacks/results/year-research/2024.md (Cartesia 2024 rubric; 132 projects; Healthcare Helper)
- [Y25] Internal: /Users/anvaytodkar/Code/mhacks/results/year-research/2025.md (122 projects; sponsor list without ElevenLabs)

**ElevenLabs**
- [E-price] Pricing (plans, credits, concurrency, free-tier limits, credit costs): https://elevenlabs.io/pricing
- [E-papi] API pricing (per-model TTS, Speech Engine $0.08/min, Music, SFX): https://elevenlabs.io/pricing/api
- [E-pag] Agents pricing (call minutes and concurrency per plan): https://elevenlabs.io/pricing/agents
- [E-llms] Docs index: https://elevenlabs.io/docs/llms.txt
- [E-qs] API quickstart: https://elevenlabs.io/docs/eleven-api/quickstart.md
- [E-agents] ElevenAgents overview: https://elevenlabs.io/docs/eleven-agents/overview.md
- [E-aqs] ElevenAgents quickstart (widget embed): https://elevenlabs.io/docs/eleven-agents/quickstart.md
- [E-cllm] Custom LLM: https://elevenlabs.io/docs/eleven-agents/customization/llm/custom-llm.md
- [E-se] Speech Engine: https://elevenlabs.io/docs/overview/capabilities/speech-engine.md
- [E-tts] TTS models: https://elevenlabs.io/docs/overview/capabilities/text-to-speech.md
- [E-err] Error codes: https://elevenlabs.io/docs/eleven-api/resources/errors.md
- [G1] GitHub issue search, 402 "Free users cannot use library voices via the API": https://github.com/search?q=%22Free+users+cannot+use+library+voices+via+the+API%22&type=issues
- [G2] "RateLimitError: unusual activity detected": https://github.com/elevenlabs/elevenlabs-python/issues/119 · [G2s] search: https://github.com/search?q=elevenlabs+%22detected_unusual_activity%22&type=issues

**Other sponsors' tech**
- [R1] Relay docs index: https://docs.relayapp.im/llms.txt
- [R2] Relay calls ↔ ElevenLabs bridge: https://docs.relayapp.im/calls/elevenlabs.md
- [R3] Relay ElevenLabs integration: https://docs.relayapp.im/integrations/elevenlabs.md
- [X-voice] xAI Grok Voice API: https://docs.x.ai/developers/model-capabilities/audio/voice
- [X-img] xAI Grok Imagine API: https://docs.x.ai/docs/guides/image-generations
- [X-tut] xAI OpenAI-SDK compatibility: https://docs.x.ai/docs/tutorial
- [FW] FREE-WILi 2 (speaker, mic array, Wi-Fi, IR): https://freewili.com/

**Peer-event ElevenLabs prizes: texts, opt-in counts, galleries** (counts from each event's `/submissions/search` prize filter on 2026-10-03; each gallery is at `https://<event>.devpost.com/project-gallery`)
- [D-rice] HackRice 16 (direct 3 mo Scale + MLH; 38/119; tool-use 43/119): https://hackrice-16.devpost.com/
- [D-6ix] Hack the 6ix 2026 (ElevenLabs rubric; 39/133): https://hackthe6ix2026.devpost.com/
- [D-tree] TreeHacks 2025 (ElevenLabs prize text; 53/257): https://treehacks-2025.devpost.com/
- [D-wics] WiCS × Opportunity Hack Sp26 (same package as MHacks; 3/26): https://wics-ohack-sp26-hackathon.devpost.com/
- [D-gt] HackGT 13 (MLH ElevenLabs; tool-use 69/268): https://hackgt13.devpost.com/
- Bay Hacks 2026 (10/23): https://bayhacks-2026.devpost.com/ · Jewel City Hacks 5.0 (3 mo Scale, no submissions yet): https://jewel-city-hacks-5-0.devpost.com/
- MLH-prize events (opted in / total): ShellHacks 2026 81/294 https://shellhacks-2026.devpost.com/ · HackPrinceton F25 40/194 https://hackprinceton-fall-2025.devpost.com/ · HackPrinceton S26 26/131 https://hackprinceton-spring-26.devpost.com/ · Hacklytics 2026 39/234 https://hacklytics-2026.devpost.com/ · HackTX 2025 43/225 https://hacktx2025.devpost.com/ · DubHacks '25 32/247 https://dubhacks25.devpost.com/ · Bitcamp 2026 28/222 https://bitcamp-2026.devpost.com/ · DeltaHacks 12 30/143 https://deltahacks-12.devpost.com/ · UofTHacks 13 31/160 https://uofthacks-13.devpost.com/ · nwHacks 2026 31/169 https://nwhacks-2026.devpost.com/ · TAMUhack 2026 22/171 https://th26.devpost.com/ · HackRU F25 39/142 https://hackru-fall-2025.devpost.com/ · Technica 2025 19/127 https://technica-2025.devpost.com/ · SwampHacks XI 22/112 https://swamphacks-xi.devpost.com/ · hackUMBC 2026 17/104 https://hackumbc-2026.devpost.com/ · HackDavis 2026 26/138 https://hackdavis-2026.devpost.com/ · QHacks 2026 19/77 https://qhacks-2026.devpost.com/ · Hack Western 12 20/82 https://hack-western-12.devpost.com/ · GreatUniHack 2025 15/56 https://greatunihack2025.devpost.com/ · SpartaHack 11 14/106 https://spartahack-11.devpost.com/ · UGAHacks 11 15/151 https://ugahacks-11.devpost.com/ · HackPSU F25 15/95 https://hackpsu-fall-2025.devpost.com/ · HackPSU S26 10/93 https://hackpsu-spring-2026.devpost.com/ · SB Hacks XII 6/106 https://sb-hacks-xii.devpost.com/ · RowdyHacks XI 10/98 https://rowdyhacks-xi.devpost.com/ · CruzHacks 2026 6/87 https://cruzhacks--2026.devpost.com/ · Hack@Brown 2026 14/62 https://hack-brown-2026.devpost.com/ · Citrus Hack 2026 12/44 https://citrus-hack-2026.devpost.com/ · WildHacks 2026 15/68 https://wildhacks-2026.devpost.com/ · Kent Hack Enough 2026 4/51 https://kent-hack-enough-2026.devpost.com/

**ElevenLabs prize winners (winner badge verified on each project page)**
- [P-singback] SingBack: https://devpost.com/software/singback
- [P-feet] feetball: https://devpost.com/software/feetball
- [P-codecrack] CodeCrack: https://devpost.com/software/codecrack
- [P-duck] The Duck You Mean?: https://devpost.com/software/the-duck-you-mean
- [P-cerebro] Cerebro: https://devpost.com/software/cerebro-yixfr4
- [P-pca] Public City Announcements: https://devpost.com/software/public-city-announcements-pcl
- [P-lifeline] Lifeline: https://devpost.com/software/the-second-responder
- [P-door] DoortectiveAI: https://devpost.com/software/doortective
- [P-flow] flow.: https://devpost.com/software/flow-8pgm1k
- [P-align] Align: https://devpost.com/software/align-ct75em
- [P-hudson] HUDson: https://devpost.com/software/hudson-uw5kn7
- [P-slotify] Slotify: https://devpost.com/software/slotify-avmxe8
- [P-atc] ATC-Trainer: https://devpost.com/software/atc-trainer
- [P-handy] HandyDaddy: https://devpost.com/software/dad-on-call
- Other winners used in the tallies: Team-03-nanpossible https://devpost.com/software/team-03-nanpossible · Lume https://devpost.com/software/lume-zrlypk · Janulus.ai https://devpost.com/software/janulus-ai · Vigilant https://devpost.com/software/project-wu4vkiag5yd9 · immi https://devpost.com/software/immi-325jt0 · ClearVision https://devpost.com/software/clearvision · Memo Music https://devpost.com/software/memo-music · Saynario https://devpost.com/software/saynario · Rekindle https://devpost.com/software/rekindle-koiq9s · Emergency Crops! https://devpost.com/software/emergency-crops · ClarityAI https://devpost.com/software/clarityai-ztxi0e · The Quack Council https://devpost.com/software/the-quack-council · Eye AAC Select https://devpost.com/software/eye-select · CarryOver https://devpost.com/software/carryover-tcrfw3 · Linguana https://devpost.com/software/boots_and_cats · CounselCoach https://devpost.com/software/counselcoach · Intelux https://devpost.com/software/intelux · SlugRoute https://devpost.com/software/slugroute · Hudson https://devpost.com/software/hudson-9h0juf · InterviewAI https://devpost.com/software/interviewai-r1pbow · Cosmo Corral https://devpost.com/software/cosmo-corral
- HackRice 16 opt-in audit examples: Mimic Mayhem https://devpost.com/software/mimic-mayhem · Casey https://devpost.com/software/casey-he74km · Chill Pill https://devpost.com/software/chill-pill-ziecm7 · Wayne Finance https://devpost.com/software/wayne-finance-kjgyif · Medicall https://devpost.com/software/medicall-pcyuz9

[H1]: https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af
[H2]: https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5
[L]: https://www.mhacks.org/live
[M25]: https://mhacks-2025.devpost.com/project-gallery
[Y24]: /Users/anvaytodkar/Code/mhacks/results/year-research/2024.md
[Y25]: /Users/anvaytodkar/Code/mhacks/results/year-research/2025.md
[E-price]: https://elevenlabs.io/pricing
[E-papi]: https://elevenlabs.io/pricing/api
[E-pag]: https://elevenlabs.io/pricing/agents
[E-llms]: https://elevenlabs.io/docs/llms.txt
[E-qs]: https://elevenlabs.io/docs/eleven-api/quickstart.md
[E-agents]: https://elevenlabs.io/docs/eleven-agents/overview.md
[E-aqs]: https://elevenlabs.io/docs/eleven-agents/quickstart.md
[E-cllm]: https://elevenlabs.io/docs/eleven-agents/customization/llm/custom-llm.md
[E-se]: https://elevenlabs.io/docs/overview/capabilities/speech-engine.md
[E-tts]: https://elevenlabs.io/docs/overview/capabilities/text-to-speech.md
[E-err]: https://elevenlabs.io/docs/eleven-api/resources/errors.md
[G1]: https://github.com/search?q=%22Free+users+cannot+use+library+voices+via+the+API%22&type=issues
[G2]: https://github.com/elevenlabs/elevenlabs-python/issues/119
[G2s]: https://github.com/search?q=elevenlabs+%22detected_unusual_activity%22&type=issues
[R2]: https://docs.relayapp.im/calls/elevenlabs.md
[R3]: https://docs.relayapp.im/integrations/elevenlabs.md
[X-voice]: https://docs.x.ai/developers/model-capabilities/audio/voice
[X-img]: https://docs.x.ai/docs/guides/image-generations
[X-tut]: https://docs.x.ai/docs/tutorial
[FW]: https://freewili.com/
[D-rice]: https://hackrice-16.devpost.com/
[D-6ix]: https://hackthe6ix2026.devpost.com/
[D-tree]: https://treehacks-2025.devpost.com/
[D-wics]: https://wics-ohack-sp26-hackathon.devpost.com/
[D-gt]: https://hackgt13.devpost.com/
[P-judy]: https://devpost.com/software/judy-ai-4vc9ah
[P-singback]: https://devpost.com/software/singback
[P-feet]: https://devpost.com/software/feetball
[P-codecrack]: https://devpost.com/software/codecrack
[P-duck]: https://devpost.com/software/the-duck-you-mean
[P-cerebro]: https://devpost.com/software/cerebro-yixfr4
[P-pca]: https://devpost.com/software/public-city-announcements-pcl
[P-lifeline]: https://devpost.com/software/the-second-responder
[P-door]: https://devpost.com/software/doortective
[P-flow]: https://devpost.com/software/flow-8pgm1k
[P-align]: https://devpost.com/software/align-ct75em
[P-hudson]: https://devpost.com/software/hudson-uw5kn7
[P-slotify]: https://devpost.com/software/slotify-avmxe8
[P-atc]: https://devpost.com/software/atc-trainer
[P-handy]: https://devpost.com/software/dad-on-call

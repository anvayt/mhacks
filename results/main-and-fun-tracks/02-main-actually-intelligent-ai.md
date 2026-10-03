# Main Track Advocate — Actually Intelligent (AI)

## Prompt given (excerpt)
> You are the advocate for the main track "Actually Intelligent (AI)" at MHacks 2026. Research how it is judged, how crowded it will be, what has won analogous categories, how it stacks with the fun and sponsor tracks, three project directions, honest weaknesses, and a 1–10 scorecard. Make the strongest honest case — an impartial judge will weigh your file against five other track advocates.

---

## TL;DR (the honest version)

- **This will very likely be the most crowded main track, not FinTech.** I scraped every MHacks 2024 and 2025 Devpost submission. **51% (62/122) of 2025 projects and 55% (73/132) of 2024 projects list an LLM or LLM platform in "Built With".** Mentions of "agent" in write-ups jumped from 6% (8/132) to 35% (43/122) in one year. FinTech-themed projects were only about 4–12%. (Method below. These are keyword heuristics, so treat them as approximate.)
- **The prize is the same everywhere.** Each of the four main tracks pays one $2,500 prize, and a separate $5,000 Grand Prize is on top ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). Crowding counts against AI.
- **Why argue for it anyway:**
  1. It stacks with more prizes than any other main track. 5 of the 12 sponsor tracks require an AI agent or an AI API (Fetch.ai, Photon, Relay, ElevenLabs, SpaceX/Grok). These include **both** of the team's favorites, SpaceX and Relay. The "Judged by an LLM" fun track also fits naturally.
  2. It is the most feasible track for a software-strong team in 24 hours.
  3. The crowd is mostly weak. The official track text and Fetch.ai's own rubric both say thin wrappers lose. A team that ships **an agent that takes real actions, is grounded in real data and shows a measured eval** stands out from a crowd of chatbots.
- **Scorecard:** Win probability 4 · Competition 3 · Feasibility 9 · Demo impact 7 · Stacking 10 · Fit with preferences 8.

---

## 1. What this track rewards and how it is likely judged

**Official track text** (from the MHacks 26 Tracks page in the 2026 Hacker Handbook):
> "Smart should mean something. Build AI that actually solves a real problem — not just AI for AI's sake." — [MHacks 26 Tracks](https://safe-banon-80d.notion.site/p/MHacks-26-Tracks-3e424ca0c81b802b86d4ebacf0cbfc0b)

Our Instagram transcription was missing the second clause, "not just AI for AI's sake". **That clause is the rubric.** Judges will ask two questions: what is the problem, and why does this need AI?

**Prize:** $2,500 for the track winner. The table shows one prize per track, with no 2nd or 3rd place. The Grand Prize is $5,000 cash. Fun tracks ("Side quests") award a "mystery useless prize" (Useless AI), "bop it" (Dumbest Idea) and "LLM decides a prize from list of prizes" (Judged by an LLM). Source: [Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5).

**Judging format (2026 Hacker Handbook):**
- Hacking runs **12 PM Oct 3 to 12 PM Oct 4**. Devpost submission is due by 12 PM with no exceptions. Judging is **12:30–2:30 PM Sunday at the Duderstadt Center**. Each team gets **a three-minute window**, "projects may be judged more than once by different judges", sponsors judge their tracks at the same time, and "to be judged for any track, your team must be present." ([2026 Hacker Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af))
- Scoring: "Judges will use predefined criteria to score each project based on factors such as **innovation, technical complexity, usability, and presentation quality**." (same source)
- The handbook lists "Devpost: TBD", and the live site's Prizes tab still says judging criteria "will appear here once they are finalized" ([handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af), [mhacks.org/live](https://www.mhacks.org/live)). **The exact 2026 rubric weights are not published.**
- **Inference from prior years:** MHacks 2024 and 2025 used the same four Devpost criteria: Innovation, Technical Complexity, Usability and **Adherence to Theme**. Adherence to Theme was defined as "clear demonstration of how the project addresses and contributes to the theme" ([MHacks 2025 Devpost](https://mhacks-2025.devpost.com/), [MHacks 2024 Devpost](https://mhacks-2024.devpost.com/)). Expect the same or similar. In this track, "theme" means *the AI is necessary and the problem is real*.

**Main-track rule ambiguity.** The Instagram slide says to build under exactly one of the four main tracks. The handbook's "MHacks 26 Tracks" page, however, lists all seven (including the three fun tracks) under "Hackers are required to build under one of the themes" ([MHacks 26 Tracks](https://safe-banon-80d.notion.site/p/MHacks-26-Tracks-3e424ca0c81b802b86d4ebacf0cbfc0b)). The Tracks & Prizes page splits them into "MHacks Tracks" and "Side quests". Unverified: ask at the help desk or on Discord. Plan on one main track plus fun tracks.

**What this means in practice (inference):** A 3-minute, science-fair-style pitch to rotating judges rewards (a) a problem stated in one sentence with a number, (b) a live demo where the AI visibly *does* something, and (c) a ready answer to "isn't this just a ChatGPT wrapper?"

---

## 2. Competition density: how crowded will it be?

### Hard data from past MHacks (my scrape)
I pulled every project in the [MHacks 2025](https://mhacks-2025.devpost.com/project-gallery) and [MHacks 2024](https://mhacks-2024.devpost.com/project-gallery) Devpost galleries and parsed each project page's "Built With" list and write-up.

| Metric | MHacks 2024 (132 submissions, 434 Devpost participants) | MHacks 2025 (122 submissions, 380 Devpost participants) |
|---|---|---|
| LLM or LLM platform in "Built With" (OpenAI, Gemini, Claude, Groq, Llama, LangChain, Fetch.ai, etc.) | **73 (55%)** | **62 (51%)** |
| LLM in Built-With **or** named in the write-up | 85 (64%) | 85 (70%) |
| Write-up mentions "agent(s)/agentic" | 8 (6%) | **43 (35%)** |
| Finance-themed (≥1 finance keyword early in the write-up or tech list) | 5 (~4%) | 15 (~12%) |

*Method and caveats:* These are regex keyword heuristics, so expect some misclassification. For example, Wattson matched only because its write-up mentions "generative AI" in passing. Use the numbers for direction and size, not precision. Participant and submission counts come from the Devpost pages above.

### Projection for 2026 (inference, clearly flagged)
- MHacks says "1,000+ student builders" are expected ([mhacks.org](https://www.mhacks.org/)). Peer benchmark: HackMIT 2026 had 1,000+ students and "nearly 300 projects" ([The Tech](https://thetech.com/2026/10/01/hackmit-2026)). **If MHacks reaches a similar size, expect about 200–300 submissions.** If attendance looks more like the 2024 and 2025 Devpost numbers, expect about 120–150.
- Every team must pick one main track. AI is the default home for any general AI app with no domain angle. **My estimate: AI takes 35–50% of submissions, roughly 50–150 teams, for one $2,500 prize.** FinTech will grow because it now has its own track plus Capital One Nessie, but its historical base is far smaller.
- **Bottom line: the team's instinct ("avoid the most crowded track") would, on this data, point away from AI more than away from FinTech.** I score Competition 3/10 to reflect that.

### Why crowding is less bad than it looks (the quality-adjusted argument)
- The 2025 winner set shows that most AI submissions are not where prizes went. Among the 2025 winners, the Grand Award went to a self-trained robot policy, and every MHacks-run track except Overdrive (Optimization) went to a hardware or AR project (see §3). In other words, **most LLM-wrapper submissions won nothing.** The AI track will be large and full of shallow entries, and the official text ("not just AI for AI's sake") tells judges to filter exactly those out.
- Sponsor rubrics say the same thing. Fetch.ai: "Avoid simple chatbots or thin wrappers around a single API" ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). A TreeHacks 2026 track winner wrote that "technical implementation is becoming less and less of a differentiator" and that execution and presentation decide outcomes ([evanyu.dev](https://www.evanyu.dev/blog/treehacks-2026)).
- **The effective competition is the top roughly 10–15% of AI entries**, perhaps 8–20 teams, not all 50–150. That estimate is inference, not data.

---

## 3. Precedent: what won this or analogous categories

### MHacks 2025 (closest analog: same venue, same 24-hour format, same four criteria)
MHacks 2025 had no "AI" track. Its tracks were Greenprint (Sustainability), Lifeline (Healthcare), Overdrive (Optimization) and Portal (Frontier Interfaces), plus a Brainrot fun prize ([MHacks 2025 Devpost](https://mhacks-2025.devpost.com/)).
- **Grand Award ($4,000): [Artificial Sandwich Intelligence](https://devpost.com/software/artificial-sandwich-intelligence).** A solo builder made "a fully self-trained end to end masked transformer robot policy" based on the ACT paper. It was trained "with just 4 hours on a 4090" and runs on about $200 LeRobot SO-101 arms, with a comparison to a human benchmark. Built with PyTorch, LeRobot and ACT. **Lesson: "actually intelligent" won the top prize, meaning a trained model with a measured comparison, not an API call.**
- **Overdrive (Optimization): [Ventura](https://devpost.com/software/ventura).** "Reddit mixed with ChatGPT." It deduplicates repeated AI questions with embedding similarity, pitched as saving compute. The solo author admits auth and the Gemini integration did not work. **Lesson: a sharp "why AI / why it matters" framing can win even an unfinished build in a thin category.**
- **Lifeline (Healthcare): [Dementia Assistant](https://devpost.com/software/dementia-assistant).** The team trained its own face-recognition model because the platform lacked one, and paired it with live transcription to help dementia patients. **Lesson: custom ML beats off-the-shelf.**
- **Brainrot: [Judy AI](https://devpost.com/software/judy-ai-4vc9ah).** A VS Code companion with Gemini and ElevenLabs, playful but working.
- AI-agent sponsor winners: [deCluttered.ai](https://devpost.com/software/declutttered-ai) (AI scans and prices your items, then agents handle offers; Agentverse prize), [Bazaar](https://devpost.com/software/bazaar-ai-agent-marketplace-fetch-ai) (ASI:One prize) and [MobiLens](https://devpost.com/software/mobilens) (Best Use of Fetch.ai plus a Snap AR prize).

### MHacks 2024 (Sept)
- Grand Prize: [V²/R](https://devpost.com/software/v-r), a VR breadboard simulator with no AI. **Runner-Up: [FocusFlow](https://devpost.com/software/focusflow-ucwma0)**, which combines ML webcam eye tracking with AI parsing to keep ADHD readers on task, running on an Intel AI PC backend ([MHacks 2024 Devpost](https://mhacks-2024.devpost.com/)).
- Health Track: [NurseNotes](https://devpost.com/software/nursenotes). Nurse audio goes through speech-to-text and an LLM into SOAP(IE)-formatted notes stored in a database. The pitch opened with a statistic: 41% of a nurse's shift goes to paperwork. **Lesson: a narrow, real workflow plus an LLM plus a hard number.**
- Accessibility Track: [SignVerse](https://devpost.com/software/signverse), with a custom-trained Roboflow ASL model for real-time two-way translation.

### MHacks x Google (April 2024): an all-AI MHacks event, the most direct analog
231 participants, every project built on Gemini ([Devpost](https://mhacks-x-google.devpost.com/)). Winners:
1. [Cosmocook](https://devpost.com/software/cosmocook): an AR cooking expert with multimodal Gemini 1.5 Pro context.
2. [Gemini Forge](https://devpost.com/software/mhack): a "pip install" for few-shot prompts.
3. [Rusteze](https://devpost.com/software/rusteze-t0r5ak): translates C projects to memory-safe Rust.
4. [DataMask](https://devpost.com/software/datamask): human-AI PII anonymization.
5. [Insight](https://devpost.com/software/insight-2cs417): a memory assistant on a Raspberry Pi.

**Lesson: when *everyone* uses AI, winners are multimodal, embodied, or developer tools with a crisp before/after. None of the top 5 is a plain chat UI.**

### Peer hackathons
- **Cal Hacks 12.0 (Oct 2025), 1st Overall:** FaceTimeOS, a computer-use agent you control by FaceTime-calling your Mac. 695 projects, 3,000+ hackers. The author credits three things: picking an underexplored AI niche from recent papers, broad relatability, and one teammate dedicated to polished UI ([Dylan Lu's blog](https://blog.dylanlu.com/cal-hacks-12/)).
- **HackMIT 2026 (Sept 2026), Grand Prize:** Peel, a low-cost optical dissolution tester (LEDs and light sensors) plus "an AI evidence engine" that cross-checks recall and safety databases to detect counterfeit pills. About 300 projects. Education Track: Burrow, a Socratic AI study companion ([The Tech](https://thetech.com/2026/10/01/hackmit-2026)).
- **TreeHacks 2026:** Grand Prize Shepherd, a motorized smart cane that uses computer vision to steer visually impaired users ([Stanford Daily](https://stanforddaily.com/2026/02/15/12th-annual-treehacks/)). Education Track 1st: Minerva, a live-avatar AI tutor that generates Manim/Desmos visuals ([evanyu.dev](https://www.evanyu.dev/blog/treehacks-2026)). TreeHacks also ran a dedicated "[OpenAI] Artificial Intelligence Track" ([TreeHacks 2026 Devpost](https://treehacks-2026.devpost.com/)).

**Pattern across all of these:** winning AI projects (1) target a specific user with a quantified pain, (2) make the AI *act* (control a computer, drive a cane, check a pill, write notes into a database) instead of just chatting, (3) often own a model or a non-trivial pipeline, and (4) demo cleanly.

---

## 4. Win levers (specific to this track)

1. **Open with the problem, not the model.** One named user, one number (as NurseNotes did with its 41% paperwork statistic). The track text explicitly penalizes "AI for AI's sake".
2. **Have a "why AI?" answer ready.** Prepare a 15-second answer: "a rules engine can't do X because Y." Judges in this track will ask it.
3. **Show a measured eval.** This is the cheapest way to separate yourself from wrappers. Build a small labeled test set (20–50 cases), then show *baseline vs. ours* (for example, plain LLM vs. your grounded agent) on accuracy or precision. Artificial Sandwich Intelligence won partly on a human-benchmark comparison ([Devpost](https://devpost.com/software/artificial-sandwich-intelligence)). Almost no hackathon team does this (inference).
4. **Make the agent take actions.** Use tool calls that change state (book, file, send, flag, write to a database), not text output alone. This matches Fetch.ai's rubric ("turn a user's request into an outcome") and Relay's and Photon's premise.
5. **Ground answers in real data, with citations.** This kills the hallucination question and lets you show provenance on screen.
6. **Use a voice or phone-call demo.** "Call the agent" is visceral in 3 minutes. Relay supports text, call and video. Grok Voice and ElevenLabs make voice cheap ([Relay docs](https://docs.relayapp.im/llms.txt), [xAI Voice](https://docs.x.ai/developers/model-capabilities/audio/voice)).
7. **Reliability over breadth.** The pitch gets repeated to multiple judges, so it must work every time. Keep a cached or recorded fallback and a local copy of the demo data.
8. **Make polish someone's job** (the FaceTimeOS lesson). The same work feeds the Figma Best Design track.

---

## 5. Stacking: what combines in ONE coherent project

### Fun tracks
| Fun track | Fit with AI main | Notes |
|---|---|---|
| **Judged by an LLM** | **Strong** | "Build something technically sharp enough to impress an AI judge" ([MHacks 26 Tracks](https://safe-banon-80d.notion.site/p/MHacks-26-Tracks-3e424ca0c81b802b86d4ebacf0cbfc0b)). An eval-backed, well-documented AI system is exactly what an LLM reading a write-up will score highly. *Unverified:* what the LLM judge reads (probably the Devpost text and repo), so write a structured, specific Devpost. |
| Useless AI | **Conflicts** | Its thesis ("gloriously pointless AI") contradicts "AI that actually solves a real problem." Entering both with one project undercuts the main-track pitch. |
| Dumbest Idea | **Conflicts** | Same problem. Skip it unless a deliberately silly side feature exists, and don't dilute the main pitch. |

### Sponsor tracks (12): fit with an AI main-track project
| Sponsor track | Fit | Why |
|---|---|---|
| **Fetch.ai ASI:One Agent Challenge** ($1,250/$750/$500) | **Native** | Requires an agent registered on Agentverse, the Chat Protocol, a primary workflow that works inside ASI:One, and a public GitHub repo. Weights: Functionality 25%, Fetch tech 20%, Innovation 20%, Impact 20%, UX 15% ([Fetch hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)). Fetch is also MHacks' "AI Concierge" partner ([mhacks.org/live](https://www.mhacks.org/live)). |
| **Relay Interactive Agents** (SF trip + Relay house week) | **Native** | "Build an AI agent people can text, call and video chat with in the Relay app." Bring your own LLM; Python and TypeScript SDKs; LiveKit, Pipecat and ElevenLabs integrations ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5), [Relay docs](https://docs.relayapp.im/llms.txt)). A team favorite. |
| **SpaceX "Make it Legendary"** (keyboards) | **Native if the domain is space** | Must be built with Cursor and must use the **Grok Imagine or Voice API**, with real space data ("decades of missions, and a literature no human can read all of"). Grok Bot usage earns bonus points ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). A team favorite. Forces a space-data domain. |
| **Photon iMessage Agents** ($400 + credits + interview fast-track) | Native | Requires Photon's Spectrum (TypeScript SDK) to connect the agent to iMessage ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5), [Photon blog](https://photon.codes/blog/introducing-spectrum)). It overlaps with Relay as a second messaging surface: doable, but it splits effort. |
| **ElevenLabs** (Scale tier, 3 months per member) | Native | Any voice output. Mild conflict with SpaceX, which wants Grok *Voice*. Use Grok Voice for the agent conversation and ElevenLabs for one distinct voice feature only if time allows, or pick one. |
| **Neon Backend** ($1,000 AI Gateway credits) | Strong | Postgres with pgvector for retrieval ([Neon pgvector](https://neon.com/docs/extensions/pgvector)) plus Neon Auth. Low marginal cost if Neon is your database anyway. |
| **SpacetimeDB** ($1,000/$500/$200) | Medium | Sponsor explicitly welcomes "AI agent coordination" and "AI systems coordinating in a persistent world state", but wants it "meaningfully used, not just added on the side" ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). Only worth it if the product has live shared state. |
| **Figma Best Design** | Strong | Any polished UI. Cheap if someone owns design. |
| **Notability** | Free add-on | Qualify by using Notability Pro for ideation and wireframes, plus 2 screenshots in the Devpost ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). Near-zero cost. |
| **FinchNode (HealthTech)** (Apple Watch SE3 / $500) | Strong *if health domain* | "Working FinchNode integration using our synthetic demo health records" (same source). The synthetic API covers medications, labs, conditions and allergies across 12 named scenarios ([FinchNode](https://finchnode.com/)). |
| **Capital One Nessie** ($300 gift card per member) | Medium | Mock accounts, merchants, bills and P2P transfers ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). It works in an AI-main project (a money agent), but judges may see it as FinTech in disguise. A team favorite, though it **can't share one coherent project with SpaceX**. |
| **FREE-WILi** | Weak | A hardware dev tool. Only fits if the team goes AI plus hardware. |

**Key point for the team:** your two top sponsor picks, **SpaceX and Relay, both require AI**. If you take them, you are building an AI project whatever main track you choose. The real question is whether your AI project has a strong enough domain angle (climate, money, hardware) to sit credibly in a less crowded track. If it doesn't, AI is the honest home.

**Best coherent stack (Direction 1 below):** AI main + Judged by an LLM + SpaceX + Relay + Fetch.ai + Neon + Figma + Notability. That is 6 sponsor tracks plus 1 fun track, all in one project.

---

## 6. Three concrete project directions

### Direction 1: "Lessons Learned": a mission-safety agent for student space teams (best stack, hits SpaceX + Relay)
Student rocketry and CubeSat teams keep repeating failures NASA has already documented. NASA's Lessons Learned Information System holds about 2,100 public, reviewed lessons from Apollo through Artemis, and it is queryable and dumpable ([data.gov catalog](https://catalog.data.gov/dataset/nasa-engineering-network-lessons-learned); repo listing [llis.nasa.gov](https://llis.nasa.gov/), API details per [this mirror's README](https://github.com/Oht8wooWi8yait9n/llis), which is unofficial). That fits SpaceX's "a literature no human can read all of" exactly.

The agent ingests a team's design doc or test plan. It retrieves relevant lessons with pgvector on Neon, flags concrete risks with **cited** lesson IDs, and drafts a pre-flight checklist. Team members can **call or text it in Relay** ("we're switching to a LiPo pack, what's burned people before?") with Grok Voice for speech, and it's registered on Agentverse so it's reachable from ASI:One.

For the "actually intelligent" proof, seed 3 historical failure write-ups. Show that a plain LLM misses the relevant lesson while your grounded agent catches it with a citation, and report hit rate on a 20–30-case set. Grok Imagine can render a "failure mode" annotated diagram as visual flair.

Real user: U-M's student space teams are next door (unverified that they'd pilot it; ask on Discord or at the sponsor expo). **Stacks:** AI, Judged by an LLM, SpaceX, Relay, Fetch.ai, Neon, Figma, Notability.

### Direction 2: "Callable care-check": a medication-safety agent for older patients and caregivers (strongest "real problem", hits FinchNode + Relay)
An older patient or caregiver calls an agent in Relay ("is it okay to take ibuprofen with my new prescription?"). The agent pulls the patient's **synthetic FinchNode record** (meds, allergies, conditions, labs) ([FinchNode](https://finchnode.com/)), reasons about interactions and contraindications, answers in plain voice (ElevenLabs), and **takes an action**: it texts a caregiver summary or drafts a pharmacist question. It always cites the record fields it used and refuses to diagnose.

Eval: seed the 12 synthetic scenarios with known interaction cases, then show precision and recall against a no-context LLM baseline. The problem is universally legible to judges (polypharmacy in older adults; cite a stat during the build) and closely matches the NurseNotes and Dementia Assistant precedents that won health-flavored MHacks tracks.

**Stacks:** AI, Judged by an LLM, FinchNode (Apple Watch SE3 for 1st), Relay, ElevenLabs, Fetch.ai, Neon, Figma, Notability. **Conflicts:** SpaceX (no space data) and Capital One.

### Direction 3: "Money agent you can call": overdraft and subscription-creep prevention (hits Capital One + Relay; the FinTech-adjacent hedge)
A student texts or calls an agent in Relay (Relay itself lists "💸 Money" as a starter idea ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5))). The agent reads the student's **Nessie** accounts, bills and transactions, forecasts the balance through the next bill cycle, detects recurring charges, and **acts** in the sandbox: it schedules a transfer or flags a bill. It explains everything in natural language.

The "actually intelligent" proof is a backtest. Replay 60 days of mock transactions and show how many overdrafts the agent would have prevented compared with a naive threshold alert.

**Stacks:** AI, Judged by an LLM, Capital One, Relay, Photon (optional iMessage surface), ElevenLabs, Fetch.ai, Neon or SpacetimeDB, Figma, Notability. **Honest caveat:** this is close enough to FinTech that the team should decide whether it is stronger in the AI pool (judged on agent depth) or the FinTech pool (judged on finance impact). Budgeting apps are probably the most common FinTech hackathon idea (inference), so the agentic action and backtest are what differentiate it either way.

---

## 7. Honest weaknesses, best rival arguments, and rebuttals

| Rival argument | Strength | Rebuttal |
|---|---|---|
| **"AI is the most crowded track, and your own data proves it."** (every rival) | **Strong. I concede it.** | True: about half of past MHacks projects already list an LLM. But most are wrappers that won nothing in 2025. The effective field is the top tier, and an eval-backed, action-taking agent clears the wrappers by construction. The cost is real: I score Competition 3/10. |
| **"AI is a technique, not a domain. Build the same agent and file it under Sustainability or FinTech, where there are fewer rivals."** (Sustainability and FinTech advocates) | **Strong** | If your idea genuinely has a climate or money angle, they're right, and the team should take the less crowded track. But SpaceX requires space data and Relay's starter ideas (social, food, school, fitness) are mostly neither climate nor money. Forcing a domain fit risks failing "Adherence to Theme". The AI track also scores your strongest axis, technical AI depth. |
| **"Hardware wins grand prizes: MHacks 2025 Grand Award, TreeHacks Shepherd, HackMIT Peel."** (Hardware advocate) | Medium–strong | Correct about the pattern, and hardware is likely less crowded (my scrape: about 9 of 132 projects in 2024 and 30 of 122 in 2025 mentioned hardware keywords). But the team's hardware experience is unknown, MLH hardware is "first-come, first-served" ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)), 24 hours is unforgiving for hardware debugging, and hardware stacks with only about 1 sponsor (FREE-WILi). Note too that all three of those grand prizes were *AI-powered*. |
| **"Judges are tired of AI. Being in the AI track signals 'yet another LLM app'."** | Medium | That is why the track text exists: these judges are primed to reward the *opposite* of a wrapper. A measured eval and visible actions make you the contrast case. |
| **"One $2,500 prize: the expected value is low."** | Medium | Same $2,500 in every main track. AI's EV comes from **stacking**: one project can credibly enter 5–7 sponsor tracks plus Judged by an LLM, with cash and near-cash prizes (Fetch $1,250, Neon $1,000 credits, Photon $400, FinchNode $500/Apple Watch, Relay SF trip). No other main track gets near that. |
| **"Your preferred sponsors don't all fit together."** | Valid | Correct. SpaceX and Capital One can't share one coherent project. Pick Direction 1 (SpaceX + Relay) or Direction 3 (Capital One + Relay). Relay works with both. |

**Weaknesses I won't spin:**
1. The highest variance comes from judge fatigue with AI pitches.
2. Software demos are less visceral than physical ones.
3. The rubric for 2026 isn't published yet.
4. My crowding projection is an inference from two prior years plus one peer event.

---

## 8. Scorecard (1–10)

| Dimension | Score | One-line justification |
|---|---|---|
| **Win probability** | **4** | One $2,500 prize against about 50–150 entrants (inference), but most are wrappers. An eval-backed agent puts a strong team in the top tier, not a lock. |
| **Competition** (10 = least crowded) | **3** | 51–55% of past MHacks projects already listed LLM tools, and agent mentions went from 6% to 35% in a year. Likely the most crowded track. |
| **Feasibility in 24h** | **9** | Pure software, mature SDKs (Relay, Fetch uAgents, Grok, Neon), and no hardware queue. Squarely in a web/mobile/AI-API team's wheelhouse. |
| **Demo impact** | **7** | A live phone or voice call to an agent that takes a visible action, plus a baseline-vs-ours eval chart, lands in 3 minutes. Still less visceral than a robot arm. |
| **Stacking potential** | **10** | 5 of 12 sponsor tracks are AI-native, plus Neon, Figma and Notability as cheap add-ons, plus Judged by an LLM. Best of any main track. |
| **Fit with team preferences** | **8** | SpaceX and Relay both *require* AI, Capital One works via Direction 3, and fun-track coverage comes via Judged by an LLM. It loses points because it violates the "avoid the crowd" preference more than FinTech does. |

---

## 9. Head-to-head against the other main tracks

| | **Actually Intelligent (AI)** | Sustainability | FinTech | Beyond the Code (Hardware) |
|---|---|---|---|---|
| Prize | $2,500 | $2,500 | $2,500 | $2,500 |
| Likely crowding (inference from 2024–25 data) | **Highest** (about half of projects are LLM-based) | Low–medium (about 17–19 of roughly 125 projects had sustainability-heavy write-ups in both years by my keyword pass) | Medium (about 4–12% finance-themed historically; boosted by Nessie and its own track this year) | Low–medium (rose to about 25% hardware-keyword projects in 2025, but most of those were sponsor-hardware add-ons) |
| Feasibility for a software team | **Highest** | High | High | Uncertain (hardware skills unknown) |
| Sponsor stacking | **Fetch, Relay, Photon, ElevenLabs, SpaceX, Neon, Figma, Notability, (FinchNode / SpacetimeDB / Nessie by domain)** | SpaceX (Earth or space data could fit), Neon, Figma, Notability; agents possible | Capital One (native), SpacetimeDB (sponsor names trading and prediction markets), Neon, Figma; agents possible | FREE-WILi, Figma; AI optional |
| Fit with SpaceX + Relay favorites | **Both native** | SpaceX plausible, Relay awkward | Relay "Money" idea fits, SpaceX doesn't | Weak |
| Grand-prize precedent | AI-heavy projects took the Cal Hacks 12 and MHacks 2024 runner-up prizes; AI-plus-hardware took MHacks 2025, HackMIT 2026 and TreeHacks 2026 grand prizes | — | — | Strong (often with AI inside) |

**On FinTech specifically:** the team's fear that FinTech is the most crowded track is **not supported** by MHacks history. Finance-themed projects were a small minority in 2024 and 2025, while LLM projects were the majority. FinTech's real risks are different: idea saturation (budgeting apps) and every Nessie team drawing on the same mock data. If the team's favorite idea is Direction 3, filing it under **FinTech** may actually be the better competitive bet. I say so even though it argues against my own track.

**My recommendation as advocate:** choose AI **if** the team commits to Direction 1 or 2, i.e. a SpaceX + Relay or FinchNode + Relay agent with a measured eval and visible actions. That is where AI's stacking (6+ sponsor tracks plus Judged by an LLM) outweighs its crowding. If the team's best idea is really about money or climate, take that domain track instead and keep the AI depth.

---

## Sources
- MHacks 2026 Hacker Handbook: https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af
- MHacks 2026 Tracks & Prizes (handbook subpage): https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5
- MHacks 26 Tracks (handbook subpage): https://safe-banon-80d.notion.site/p/MHacks-26-Tracks-3e424ca0c81b802b86d4ebacf0cbfc0b
- Handbook URL source (MHacks dashboard repo): https://github.com/mhacks/dashboard/pull/197 and https://github.com/mhacks/dashboard/blob/main/lib/wallet/event.ts
- MHacks 2026 site: https://www.mhacks.org/
- MHacks 2026 live site (schedule, prizes "coming soon", Devpost "coming soon"): https://www.mhacks.org/live
- Fetch.ai MHacks 2026 event page: https://www.fetch.ai/events/mhacks-2026
- Fetch.ai MHacks 2026 hackpack (judging weights): https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack
- MHacks 2025 Devpost (prizes, criteria, 380 participants): https://mhacks-2025.devpost.com/
- MHacks 2025 project gallery (122 submissions; scraped): https://mhacks-2025.devpost.com/project-gallery
- MHacks 2024 Devpost (prizes, criteria, 434 participants): https://mhacks-2024.devpost.com/
- MHacks 2024 project gallery (132 submissions; scraped): https://mhacks-2024.devpost.com/project-gallery
- MHacks x Google 2024 Devpost: https://mhacks-x-google.devpost.com/
- Devpost hackathon search (MHacks event list): https://devpost.com/hackathons?search=mhacks
- Artificial Sandwich Intelligence: https://devpost.com/software/artificial-sandwich-intelligence
- Ventura: https://devpost.com/software/ventura
- Dementia Assistant: https://devpost.com/software/dementia-assistant
- Judy AI: https://devpost.com/software/judy-ai-4vc9ah
- deCluttered.ai: https://devpost.com/software/declutttered-ai
- Bazaar: https://devpost.com/software/bazaar-ai-agent-marketplace-fetch-ai
- MobiLens: https://devpost.com/software/mobilens
- V²/R: https://devpost.com/software/v-r
- FocusFlow: https://devpost.com/software/focusflow-ucwma0
- NurseNotes: https://devpost.com/software/nursenotes
- SignVerse: https://devpost.com/software/signverse
- Cosmocook: https://devpost.com/software/cosmocook
- Gemini Forge: https://devpost.com/software/mhack
- Rusteze: https://devpost.com/software/rusteze-t0r5ak
- DataMask: https://devpost.com/software/datamask
- Insight: https://devpost.com/software/insight-2cs417
- Cal Hacks 12.0 grand prize write-up: https://blog.dylanlu.com/cal-hacks-12/
- HackMIT 2026 winners: https://thetech.com/2026/10/01/hackmit-2026
- TreeHacks 2026 winners: https://stanforddaily.com/2026/02/15/12th-annual-treehacks/
- TreeHacks 2026 Devpost (track list): https://treehacks-2026.devpost.com/
- TreeHacks 2026 Education Track winner write-up: https://www.evanyu.dev/blog/treehacks-2026
- Relay docs: https://docs.relayapp.im and https://docs.relayapp.im/llms.txt
- Photon Spectrum: https://photon.codes/blog/introducing-spectrum
- xAI Voice API: https://docs.x.ai/developers/model-capabilities/audio/voice
- Neon pgvector: https://neon.com/docs/extensions/pgvector
- FinchNode: https://finchnode.com/
- NASA Lessons Learned (data.gov): https://catalog.data.gov/dataset/nasa-engineering-network-lessons-learned
- NASA LLIS: https://llis.nasa.gov/
- LLIS mirror README (unofficial; API details): https://github.com/Oht8wooWi8yait9n/llis

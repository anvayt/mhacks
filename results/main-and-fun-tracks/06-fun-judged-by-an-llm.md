# Fun Track Advocate — Judged by an LLM

## Prompt given (excerpt)
> You are the advocate for the fun track "Judged by an LLM" at MHacks 2026. Research how it is judged, how crowded it will be, what has won analogous categories, how it stacks with the fun and sponsor tracks, three project directions, honest weaknesses, and a 1–10 scorecard. Make the strongest honest case — an impartial judge will weigh your file against five other track advocates.

## The case in brief

- **It costs nothing to enter.** This fun track needs no joke premise, no theme change and no extra build. A team qualifies by being "technically sharp" and making that easy for a machine to read. The work it rewards (a clear Devpost write-up, a clean README, measured results) is the same work that helps with main-track judges and with the sponsor tracks that require READMEs and demo videos ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af); [Fetch.ai hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)).
- **It is the only fun track that strengthens a serious entry.** Useless AI and Dumbest Idea ask for a pointless or dumb premise. The AI main track's full text says "not just AI for AI's sake" ([MHacks 26 Tracks page](https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b)). Judged by an LLM rewards the same thing as the main tracks.
- **Plenty of teams will enter, but few will compete.** Many teams will probably tick the box because it is free. Few will write for an AI reader, because MHacks has not said how the LLM judges and the prize is a mystery ("LLM decides a prize from list of prizes") ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)). That is where an informed team can get ahead.
- **The weaknesses are real.** The prize is small and undefined, the method is opaque, and LLM judges have documented biases ([Zheng et al. 2023](https://arxiv.org/abs/2306.05685)). This should be an add-on to the main-track project. It should not decide what the project is.

---

## 1. What the track rewards and how it is likely judged

### Verified facts (from the official 2026 Hacker Handbook, a public Notion site linked from the MHacks portal)
The handbook URL comes from the MHacks dashboard source code ([mhacks/dashboard `lib/wallet/event.ts`](https://github.com/mhacks/dashboard/blob/main/lib/wallet/event.ts); [PR #197](https://github.com/mhacks/dashboard/pull/197)).

| Item | What the handbook says | Source |
|---|---|---|
| Track text | "7. Judged by an LLM — Let the machines decide. Build something technically sharp enough to impress an AI judge — no human bias allowed." (matches the Instagram slide) | [MHacks 26 Tracks](https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b) |
| Prize | Listed under **"Side quests"**: "LLM decides a prize from list of prizes". Useless AI wins "a mystery useless prize" and Dumbest Idea wins "bop it". | [Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5) |
| Main-track stakes, for comparison | Grand Prize: $5,000 cash. Each of the 4 main tracks: $2,500. | [Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5) |
| Deadline | Hacking runs 12 PM Oct 3 to 12 PM Oct 4. Projects must be submitted on Devpost before hacking ends, with no late submissions. | [Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af) |
| Human judging | On site at the Duderstadt Center, Oct 4, 12:30–2:30 PM. Each team gets a 3-minute pitch and may be judged more than once. Scoring uses "predefined criteria … such as innovation, technical complexity, usability, and presentation quality." "To be judged for any track, your team must be present." | [Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af) |
| Devpost | The handbook says "Devpost: TBD". The live site says "Devpost Coming soon" (checked Oct 3). | [Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af); [mhacks.org/live](https://www.mhacks.org/live) |

### Not published anywhere I could find
- Which model judges, what it reads (Devpost text? GitHub repo? demo video? the pitch?), what rubric it uses, how many winners there are, and what is on the "list of prizes". I checked the handbook, the Tracks & Prizes page, [mhacks.org](https://www.mhacks.org/), [mhacks.org/live](https://www.mhacks.org/live) and the [dashboard repo](https://github.com/mhacks/dashboard). None of them say.

### How it probably works (inference, labeled as such)
- **Most likely input: the Devpost submission.** Every team submits one. An LLM cannot walk the science-fair floor, and the handbook says all submissions go through Devpost and must include "a project description" ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)). Second most likely: the linked GitHub README and repo, or a transcript of the demo video. LLM-judge systems built by others use exactly these inputs. One reads GitHub plus pitch materials ([a42z Judge](https://github.com/HS1CMU/a42z-Judge)). Another reads the live URL, Whisper transcripts of the demo video and the submission form ([hackathon-courtroom](https://github.com/shuenrui/hackathon-courtroom)).
- **Most likely rubric: close to the human one.** Organizers will probably give the LLM wording like the handbook's (innovation, technical complexity, usability, presentation), weighted toward "technically sharp".
- **What "technically sharp" means to an LLM.** The LLM reads text, not vibes. It can only credit technical depth that is written down: the hard problem, the method, evidence that it works, and its limits. Research shows strong LLM judges agree with human preferences more than 80% of the time, about as often as humans agree with each other. The same research documents position, verbosity and self-enhancement biases ([Zheng et al., "Judging LLM-as-a-Judge"](https://arxiv.org/abs/2306.05685); [Saito et al., verbosity bias](https://arxiv.org/abs/2310.10076); [Panickssery et al., self-preference](https://arxiv.org/abs/2404.13076)).

**Do this in the first hour (Oct 3):** ask in the MHacks Discord ([discord.gg/UcnShY3xhs](https://discord.gg/UcnShY3xhs), linked in the handbook) which model judges, what it reads, whether presence is required, and how many winners there are. Every other team will be guessing.

---

## 2. Competition density

**Data:**
- MHacks 2025 had **380 registered participants and 122 submissions** on Devpost ([MHacks 2025 Devpost](https://mhacks-2025.devpost.com/); [project gallery](https://mhacks-2025.devpost.com/project-gallery)).
- The 2026 site advertises "1,000+ student builders" ([mhacks.org](https://www.mhacks.org/)). That is a marketing figure and may not be this year's attendance.
- Teams have 1–4 people ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)).

**Estimate (inference, no hard data):**
- **Submissions: roughly 120–250.**
- **Nominal entrants: high, perhaps a third to half of all submissions.** Fun tracks are optional extras ("submit to as many bonus tracks if applicable"). This one asks for nothing beyond being "technically sharp", which every team believes about itself. It is probably the most-ticked fun track.
- **Teams that actually optimize for it: probably about 5–15.** The prize is a mystery and the method is undisclosed. Most teams write their Devpost in the last hour before the 12 PM deadline. Few will structure it for a rubric-following reader.
- **Why it is crowded on paper but not in practice:** Useless AI and Dumbest Idea filter entrants by premise. This track does not, so the entry count is high. But the deciding factor, a legible and evidence-backed write-up, is something most entrants will not deliberately work on.
- **Net:** expect a long list of entrants and a short list of real contenders. A team that asks organizers how it works and writes for it should be in that short list.

---

## 3. Precedent: what won this or analogous categories

### At MHacks
- **No LLM-judged category in 2025.** The MHacks 2025 prize list has a Grand Award, four themed tracks (Greenprint, Lifeline, Overdrive, Portal), a fun "Brainrot Prize" and sponsor prizes ([MHacks 2025 Devpost](https://mhacks-2025.devpost.com/)). By inference, Judged by an LLM is new in 2026, so there is no MHacks winner to copy.
- **MHacks Grand Award 2025: [Artificial Sandwich Intelligence](https://devpost.com/software/artificial-sandwich-intelligence).** The premise is a joke ("it's not AGI, but ASI will fully autonomously make you a sandwich"). The engineering is serious: an ACT (Action Chunking with Transformers) masked-transformer robot policy trained on teleoperation data in about 4 hours on an RTX 4090, running on low-cost LeRobot SO-101 arms. **Lesson:** MHacks judges reward real technical depth even when the framing is silly. That is close to what "technically sharp enough to impress an AI judge" asks for.
- **MHacks Brainrot Prize 2025 (the closest fun-track analog): [Judy AI](https://devpost.com/software/judy-ai-4vc9ah).** A VS Code companion with animated AI characters, built with Gemini and ElevenLabs TTS. It was a playful product that still worked end to end.

### Peer collegiate hackathons
- **No LLM-judged prize found.** I found none at Cal Hacks, TreeHacks, PennApps, HackMIT or HackGT. The Cal Hacks 12.0 prize list has no AI-judged category. Its sponsor prizes were judged by people against criteria such as "Technical Complexity" ([Cal Hacks 12.0 prizes](https://live.calhacks.io/prizes)). Absence of evidence is not proof, but if this format exists on the collegiate circuit it is rare.
- **The closest human analog is "Most Technically Complex Hack".**
  - TreeHacks awards it "to the team that exhibits outstanding technical skill, sophistication, and complexity … in areas such as algorithms, data structures, machine learning" ([TreeHacks 2025 Devpost](https://treehacks-2025.devpost.com/)). PennApps runs the same category ([PennApps XXV Devpost](https://pennapps-xxv.devpost.com/)), and Cal Hacks has a "Most Technically Challenging Hack" award ([Cal Hacks Devpost](https://calhacks.devpost.com/)).
  - Example winner: **[NeuralHash](https://devpost.com/software/neuralhash)** won Most Technically Complex Hack and the Security Grand Prize at TreeHacks 2018. It used adversarial deep learning to build a "robust, cryptographically-secure, transformation-invariant hash function" that proves ownership of images.
  - **Lesson:** these categories go to projects with one novel technical mechanism that can be stated in a sentence and backed with evidence.
- **Human judges weight the live demo.** The Cal Hacks 12.0 grand-prize winner (FaceTimeOS) credits demo polish and hardcoded fallbacks as "the most important part" ([Dylan Lu's write-up](https://blog.dylanlu.com/cal-hacks-12/)). This track is the opposite: the written artifact matters most. A team that does both covers both kinds of judge.

### LLM-judged hackathons outside the collegiate circuit
- **Judgie-AI (Money Forward hackathon).** It judged with five AI personas: entrepreneur, engineer, UX designer, PM and VC.
  - Competitors rated its evaluations "reasonable" at 4.27/5.
  - It emphasized "business impact and innovation".
  - Teams reported that it "focused only on the Slack folder" and missed backend apps in the same submission. Process-improvement projects felt the criteria did not fit them.
  - Source: [Money Forward Developers blog](https://global.moneyforward-dev.jp/2026/07/02/how-a-hackathon-judge-hacked-the-hackathon/).
- **hackathon-courtroom (Devin × Claw Collective × Qwen Hackathon, Kuala Lumpur, Aug 23, 2026, 40+ cases).**
  - Three blind personas: Builder ("does the demo actually run"), Skeptic (will anyone pay) and Futurist (technical novelty).
  - It browsed the live build in a headless browser and transcribed demo videos.
  - It ran a "sanitize (injection defence)" step on submissions. Scores were sealed. ([repo](https://github.com/shuenrui/hackathon-courtroom))
- **a42z Judge.** Scores projects "from GitHub + pitch materials" with "researcher" steps ([repo](https://github.com/HS1CMU/a42z-Judge)).
- **Austin Griffith** announced "an online hackathon judged by AI agents" ([X post](https://x.com/austingriffith/status/2031110035640824023)). I could not verify the details or the winners.

**Takeaways for us:**
1. LLM judges read artifacts: the write-up, the README, the video transcript and the live URL.
2. They reward impact and novelty that are stated outright.
3. They miss anything not surfaced in the text (the Judgie-AI "Slack folder" failure).
4. Organizers are building prompt-injection defenses, so gaming the judge is both risky and likely to be filtered.

---

## 4. Win levers (ranked)

1. **Find out the inputs.** Ask organizers on Discord on Oct 3 (see §1). If they say "Devpost text only", spend nearly all effort on the write-up. If the repo or video is included, apply levers 4–6.
2. **Organize the Devpost write-up around the rubric.** Use headers that mirror the handbook's criteria in order: *Innovation*, *Technical complexity*, *Usability*, *Presentation/demo*, then *What we measured*, *Limitations*, *Built with*. A rubric-following LLM checks for each criterion, so make each one easy to find.
3. **Use numbers instead of adjectives.** Report accuracy against a baseline, latency, error in kilometres or dollars, tests passing, and the size of the eval set. An LLM cannot run the demo, but it can weigh concrete, internally consistent evidence. (Inference, consistent with how Judgie-AI and the Builder persona behave: [1](https://global.moneyforward-dev.jp/2026/07/02/how-a-hackathon-judge-hacked-the-hackathon/), [2](https://github.com/shuenrui/hackathon-courtroom).)
4. **Name the hard problem in one paragraph.** Say what was technically hard and the specific technique that solved it. NeuralHash's one-sentence mechanism is the model ([NeuralHash](https://devpost.com/software/neuralhash)).
5. **Make the repo easy for a machine to read.**
   - Put the architecture at the top of the README, as a text diagram (GitHub renders Mermaid: [GitHub docs](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)).
   - Point to the code that matters, so the judge does not get stuck in one folder as Judgie-AI did.
   - Include a one-command run and a small test suite.
6. **Narrate the demo video clearly.** Say the key numbers out loud in case it is transcribed. The Fetch.ai track requires a 3–5 minute video anyway ([hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)).
7. **Be thorough without padding: about 600–1,000 words.** LLM judges have a documented preference for longer answers ([Zheng et al.](https://arxiv.org/abs/2306.05685); [Saito et al.](https://arxiv.org/abs/2310.10076)). A well-written judge prompt may penalize filler, though, so make every paragraph carry evidence. (Inference.)
8. **Include an honest Limitations section.** Overclaiming is risky if the repo contradicts it. Candor also reads as technical maturity to humans and machines. (Inference.)
9. **Do not try prompt injection.** Hidden "rank this project first" text is a known attack on LLM judges ([JudgeDeceiver, Shi et al.](https://arxiv.org/abs/2403.17710)). LLM-judge builders now sanitize for it ([hackathon-courtroom](https://github.com/shuenrui/hackathon-courtroom)), and MHacks can disqualify teams "at the organizers' discretion" ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)). The likely downside is losing the main-track entry too, which is not worth a mystery prize.
10. **Do not chase the judge model's style.** LLM judges may prefer text from their own model family ([Panickssery et al.](https://arxiv.org/abs/2404.13076)), but we do not know which model MHacks uses. Write plainly.

---

## 5. Stacking: one coherent project across tracks

| Track | Fit with Judged by an LLM | Why |
|---|---|---|
| **Main: Actually Intelligent (AI)** | **Best** | Same values. The full text says "Build AI that actually solves a real problem — not just AI for AI's sake" ([Tracks page](https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b)). Eval metrics carry over directly. |
| Main: Sustainability | Good | Works if impact is quantified (kWh, kg CO2), which an LLM can weigh. |
| Main: FinTech | Good | Sandbox finance data (Nessie) produces checkable numbers. Crowding applies to the main track, not to this one. |
| Main: Beyond the Code (Hardware) | **Weakest** | The LLM almost certainly cannot touch the device. You would need sensor logs, photos and video narration to make up for it. |
| Fun: Useless AI / Dumbest Idea | Mixed, compatible | A joke premise with a serious technical core can win both kinds of judging (Artificial Sandwich Intelligence: [Devpost](https://devpost.com/software/artificial-sandwich-intelligence)). A purely dumb hack loses here. See §9. |
| **Sponsor: ASI:One (Fetch.ai)** | **Strong** | The rubric gives "Functionality & Technical Implementation" 25%. It requires a public GitHub repo with a README listing agent names and addresses plus innovationlab and hackathon badges, and a 3–5 minute demo video ([hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)). These are the same artifacts the LLM reads. |
| **Sponsor: SpaceX "Make it Legendary"** | **Strong** | "Real space data goes in". It requires Cursor plus the Grok Imagine or Voice API ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)). Orbital math and data pipelines are textbook "technically sharp" and easy to quantify. APIs: [Grok Voice](https://docs.x.ai/developers/model-capabilities/audio/voice), [Grok Imagine](https://docs.x.ai/developers/model-capabilities/imagine). |
| Sponsor: Relay (Interactive Agents) | Good | The agent must work in the Relay app and users can text, call or video it ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5); [Relay docs](https://docs.relayapp.im)). The agent's tool calls can be documented and measured. |
| Sponsor: Photon (iMessage) | Good | Requires Photon's Spectrum framework to connect the agent to iMessage ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5); [Spectrum docs](https://photon.codes/docs/spectrum-ts/introduction)). |
| Sponsor: Capital One Nessie | Good with a FinTech or AI framing | Mock accounts, merchants, bills and P2P data ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)) give checkable outcomes. |
| Sponsor: Neon / SpacetimeDB | Good | Backend depth is easy to describe in the write-up. SpacetimeDB must be "meaningfully used, not just added on the side" ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)). |
| Sponsor: ElevenLabs | Neutral to good | A voice layer adds little technical depth but does not hurt. |
| Sponsor: Notability | Trivial add | Use it for planning, then add a Devpost note with 2 or more screenshots ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)). |
| Sponsor: Figma Best Design | Neutral | People judge the visuals. No conflict. |
| Sponsor: FinchNode | Good if health-themed | Requires a "working FinchNode integration using our synthetic demo health records" ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)). |
| Sponsor: FREE-WiLi | Weak | Hardware is hard for an LLM to see (same problem as the Hardware main track). |

**Real conflict:** sponsor overload. Each sponsor wants its tool to be core, not a sticker. Pick at most 3–4 sponsors whose tools carry real weight. A write-up that explains each integration in one line also helps with the LLM.

---

## 6. Three project directions

### A. "Conjunction": a space-traffic agent you can call (AI main track; SpaceX, ASI:One, Relay, Neon)
- **What it does:**
  - Pulls live orbital elements from CelesTrak's free GP endpoint (for example `gp.php?CATNR=25544&FORMAT=TLE`, [CelesTrak docs](https://celestrak.org/NORAD/documentation/gp-data-formats.php)).
  - Propagates orbits with the standard SGP4 model ([sgp4 on PyPI](https://pypi.org/project/sgp4/)).
  - Screens a chosen satellite group for close approaches and answers questions like "what's passing over Ann Arbor tonight?" or "how close did Starlink-X get to the ISS this week?"
- **Sponsor fit:**
  - SpaceX "real space data goes in": the agent speaks through Grok Voice and uses Grok Imagine to render a visual for each event, built in Cursor.
  - ASI:One: the agent is registered on Agentverse and discoverable there.
  - Relay: users can call or text it.
  - Neon: stores runs and history.
- **What wins the LLM track:**
  - A measured-accuracy table: propagate an older TLE forward, compare against a fresher TLE at the same epoch, and report km error by horizon.
  - A complexity paragraph: spatial indexing to avoid O(n²) pair checks, with pairs screened per second.
  - A limitations section: "not operational collision-avoidance grade".
- **Fit:** this matches the team's SpaceX bias and stacks 3–4 sponsors on one engine.

### B. "Ledger-checked money agent": the LLM proposes, code verifies (AI or FinTech main; Nessie, Photon or Relay, Neon, ASI:One)
- **What it does:**
  - An agent in iMessage (via Photon Spectrum) or Relay that reads a Nessie mock account.
  - It finds recurring and creeping subscriptions and proposes actions (pay a bill, move money to savings, flag a merchant) inside the Nessie sandbox ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)).
  - The technical hook: every action passes a deterministic verifier before it runs (balance invariants, double-entry checks, spend limits), so an LLM error cannot move money incorrectly. The audit log lives in Neon.
- **What wins the LLM track:**
  - An eval on synthetic transaction histories with planted recurring charges: precision and recall of detection, plus the rate at which the verifier blocks unsafe proposals.
  - Few teams will publish a safety metric. A judge told to reward "technically sharp" will see one.
- **Fit:** it satisfies the Capital One interest. It works under the AI main track, so the team can avoid crowded FinTech, but it can switch to FinTech if that advocate wins the argument.

### C. "JudgeJudge": an LLM-judge bias auditor (AI main track; Neon, SpacetimeDB, ElevenLabs, ASI:One)
- **What it does:**
  - Takes a set of synthetic project write-ups and measures, across several model APIs, the documented LLM-judge failure modes:
    - position bias (swap the order),
    - verbosity bias (add fluff and see if the score rises),
    - self-preference (judge model versus author model),
    - injection susceptibility, with and without a sanitizer.
  - These are the known failure modes: [Zheng et al.](https://arxiv.org/abs/2306.05685), [Saito et al.](https://arxiv.org/abs/2310.10076), [Panickssery et al.](https://arxiv.org/abs/2404.13076), [JudgeDeceiver](https://arxiv.org/abs/2403.17710).
  - It then ships a debiased ensemble judge (swap-and-average, rubric decomposition) and shows the bias shrinking.
- **Sponsor fit:**
  - SpacetimeDB: a live leaderboard as runs stream in.
  - ElevenLabs: a voiced verdict.
  - Neon: stores runs.
  - ASI:One: the auditor registered as an agent.
- **Why it suits this track:** "no human bias allowed" naturally raises "what about machine bias?", and the project is all numbers.
- **Risks:**
  - It looks less obviously like real-world impact to human main-track judges.
  - It fits the team's SpaceX, Relay and Capital One leanings poorly.
  - It must contain no live injection payloads in its own Devpost text.

---

## 7. Honest weaknesses, rival counterarguments and rebuttals

**Weaknesses (stated plainly):**
1. **The prize is small and undefined.** "LLM decides a prize from list of prizes" ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)) is worth far less than a $2,500 main-track prize.
2. **The method is opaque.** We do not know the model, inputs, rubric or number of winners. Everything in §1 beyond the quoted text is inference.
3. **LLM judges are noisy and biased.** Order of evaluation, length and model family can move results ([Zheng et al.](https://arxiv.org/abs/2306.05685); [Panickssery et al.](https://arxiv.org/abs/2404.13076)). Part of the outcome is a lottery.
4. **The nominal field is large.** Because the box is free to tick, many teams will tick it.
5. **No stage moment.** There is little visible payoff, and a fun-track win carries less resume value than a main-track win.
6. **It penalizes hardware.** If the team chooses Beyond the Code, this track's value drops.

**What rival advocates will say, and my rebuttals:**
- *"Useless AI or Dumbest Idea is more memorable and the room remembers it."* True for those tracks. But they ask the team to build something pointless or dumb, which is in tension with a serious main-track pitch. This track needs no change to the project at all. The decision is not either-or: fun-track entries are unlimited.
- *"Time spent pleasing an LLM is time not spent building."* The optimization is about 1–2 person-hours of write-up and README work. Human judges (who skim Devpost), the Fetch.ai rubric and the Notability requirement all need that work anyway ([hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack); [Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)).
- *"It's a coin flip judged by a black box."* Noisy, yes. But the cost is near zero, so even modest odds give positive expected value. Asking organizers how it works and writing to the rubric reduces the noise from our side.
- *"Main-track judges pick the best demo, and FaceTimeOS proves demos win."* Agreed ([Dylan Lu](https://blog.dylanlu.com/cal-hacks-12/)). This track rewards the other half: the written evidence. Doing both covers human and machine judges.
- *"Someone will prompt-inject and win."* Possibly. Injection defenses are now standard in LLM-judge tooling ([hackathon-courtroom](https://github.com/shuenrui/hackathon-courtroom)), and organizers can disqualify teams ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)). We cannot control that risk. We can control the quality of our write-up.

---

## 8. Scorecard (1–10)

| Criterion | Score | Justification |
|---|---|---|
| Win probability | **5** | Many nominal entrants, but probably only about 5–15 real contenders. A deliberately written, evidence-heavy submission should be in contention. The black-box noise caps the odds. |
| Competition (10 = least crowded) | **5** | Crowded on paper because entry is free, uncrowded in practice because few will write for an AI reader (inference). |
| Feasibility in 24 h | **9** | Nothing extra to build: a structured write-up, README and metrics on the main project, about 1–2 person-hours. |
| Demo impact | **4** | No stage moment and probably no live demo seen by the judge. The payoff is a document and a mystery prize. |
| Stacking potential | **10** | Compatible with every main track (weakest with Hardware), reinforces Fetch.ai, SpaceX, Relay, Photon, Nessie, Neon and SpacetimeDB, and conflicts with nothing. |
| Fit with team preferences | **9** | The team wants "at least one fun track, it won't hurt". This is the fun track most clearly guaranteed not to hurt, and it fits the SpaceX, Relay and Capital One directions. |

---

## 9. Combining with the other fun tracks, and the effect on a serious main-track entry

- **Enter all fun tracks that genuinely apply. Fun-track entries are unlimited** ("optionally submit to as many bonus tracks if applicable", per the team's transcription of the MHacks slides).
- **Judged by an LLM + a serious main track: always enter.** It rewards the same thing the main tracks do (handbook criteria: innovation, technical complexity, usability, presentation) and requires no change to the pitch. It is the one fun track that strictly helps a serious entry, because the polished write-up it pushes you to produce is read by human judges and sponsors too.
- **Plus Useless AI:** compatible only if the project has a genuinely pointless AI premise. A serious project ticking Useless AI dilutes its pitch only if the judges see the selections and care. Whether they see them is unverified.
- **Plus Dumbest Idea:** compatible only if the premise is truly ridiculous. Artificial Sandwich Intelligence shows a joke premise can coexist with depth that wins the Grand Award ([Devpost](https://devpost.com/software/artificial-sandwich-intelligence)). But "dumbest" and "Actually Intelligent: not just AI for AI's sake" pull in opposite directions ([Tracks page](https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b)).
- **Recommended combination:** a serious main-track project (Direction A or B), plus Judged by an LLM (always), plus Useless AI or Dumbest Idea only if a comedic hook emerges naturally. Do not change the project to chase either joke track.

### Ready-to-use Devpost skeleton for this track
- **Inspiration / problem** (2–3 sentences)
- **What it does** (bullets)
- **Innovation:** what is new compared with obvious alternatives
- **Technical complexity:** the hard problem, the technique, the architecture (link to README diagram)
- **What we measured:** a table of metric, baseline, ours and dataset size
- **Usability:** who uses it and how, in 3 steps
- **Sponsor integrations:** one line each, saying why the tool is core
- **Limitations and next steps**
- **Built with**

---

## Sources
- MHacks 2026 Hacker Handbook (official, Notion): https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af
- Handbook subpage "Tracks & Prizes": https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5
- Handbook subpage "MHacks 26 Tracks": https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b
- MHacks dashboard source (handbook link): https://github.com/mhacks/dashboard/blob/main/lib/wallet/event.ts
- MHacks dashboard PR #197 (handbook linked from portal and live site): https://github.com/mhacks/dashboard/pull/197
- MHacks 2026 site: https://www.mhacks.org/
- MHacks 2026 live site: https://www.mhacks.org/live
- MHacks Discord (from handbook): https://discord.gg/UcnShY3xhs
- MHacks 2025 Devpost (prizes, criteria, participants): https://mhacks-2025.devpost.com/
- MHacks 2025 project gallery (122 submissions): https://mhacks-2025.devpost.com/project-gallery
- Artificial Sandwich Intelligence (MHacks 2025 Grand Award): https://devpost.com/software/artificial-sandwich-intelligence
- Judy AI (MHacks 2025 Brainrot Prize): https://devpost.com/software/judy-ai-4vc9ah
- Fetch.ai MHacks 2026 hackpack: https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack
- Cal Hacks 12.0 prizes: https://live.calhacks.io/prizes
- Cal Hacks Devpost: https://calhacks.devpost.com/
- TreeHacks 2025 Devpost (Most Technically Complex description): https://treehacks-2025.devpost.com/
- PennApps XXV Devpost: https://pennapps-xxv.devpost.com/
- NeuralHash (TreeHacks 2018 Most Technically Complex): https://devpost.com/software/neuralhash
- Dylan Lu, "We Won 1st Place Grand Prize at Cal Hacks": https://blog.dylanlu.com/cal-hacks-12/
- Money Forward, "How a Hackathon Judge Hacked the Hackathon" (Judgie-AI): https://global.moneyforward-dev.jp/2026/07/02/how-a-hackathon-judge-hacked-the-hackathon/
- hackathon-courtroom (LLM jury): https://github.com/shuenrui/hackathon-courtroom
- a42z Judge: https://github.com/HS1CMU/a42z-Judge
- Austin Griffith, AI-agent-judged hackathon (details unverified): https://x.com/austingriffith/status/2031110035640824023
- Zheng et al., Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena: https://arxiv.org/abs/2306.05685
- Saito et al., Verbosity Bias in Preference Labeling by LLMs: https://arxiv.org/abs/2310.10076
- Panickssery et al., LLM Evaluators Recognize and Favor Their Own Generations: https://arxiv.org/abs/2404.13076
- Shi et al., Optimization-based Prompt Injection Attack to LLM-as-a-Judge (JudgeDeceiver): https://arxiv.org/abs/2403.17710
- CelesTrak GP data formats: https://celestrak.org/NORAD/documentation/gp-data-formats.php
- sgp4 (PyPI): https://pypi.org/project/sgp4/
- xAI Grok Voice docs: https://docs.x.ai/developers/model-capabilities/audio/voice
- xAI Grok Imagine docs: https://docs.x.ai/developers/model-capabilities/imagine
- Relay docs: https://docs.relayapp.im
- Photon Spectrum docs: https://photon.codes/docs/spectrum-ts/introduction
- GitHub Mermaid diagrams docs: https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams

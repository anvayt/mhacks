# Sponsor Track Advocate — Trust the Process / Best Use of Notability

## Prompt given (excerpt)
> You are the advocate for the sponsor track "Trust the Process / Best Use of Notability" at MHacks 2026. Research the sponsor's tech and how fast a team can integrate it, what its judges reward, prize value vs competition, expected value, how it stacks with the main/fun picks and other sponsors, 2–3 winning project sketches, honest red flags, and a 1–10 scorecard. Make the strongest honest case — an impartial judge will weigh your file against eleven other sponsor advocates.

Labels used below: **[V]** verified at the cited URL on 2026-10-03, **[I]** my inference, **[U]** unverified, so ask the sponsor.

---

## TL;DR: the case in five lines

1. **This is a process track, not an API track.** The official rule says you qualify by using Notability Pro "at some point during the hackathon." Recommended uses are "ideation, brainstorming, discussion summaries, wireframing." You then tag "Notability" on Devpost and add a short note with **at least 2 screenshots** [V] ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)). Notability has no public developer API (notability.com/developers and /api both return 404) [V].
2. **Qualifying costs about 1.5–2 person-hours and zero code.** Most of that is planning work the team does anyway. It never constrains the main track, the fun track or any other sponsor track. That makes it the cheapest entry in the stack.
3. **The prize is small:** one winner gets "1 year of Notability Pro, 4 pieces of exclusive Notability merch for each team member" [V]. Pro lists at $99.99/yr, $79.99 on the current sale [V] ([pricing](https://notability.com/pricing)). That is roughly $400–800 retail for a team of 4 if Pro is per member, and less in real value.
4. **Winning is plausible.** At MHacks 2025, the closest "just use the tool" prize (GoDaddy domain) drew 10 of 122 projects, about 8% (my recount). Most entrants in a track like this submit two throwaway screenshots. A team that uses the Pro-only features on purpose and documents them well should be in the top few (inference). I estimate a **15–25% win chance**, which gives the best expected value per hour of any sponsor track but the smallest expected value in absolute terms.
5. **Verdict: always enter.** Make it the free tail of whatever stack the judge picks, whether that is Sustainability + Judged by an LLM + SpaceX or another. It should not decide the project. Make it a headline track only if sketch B or C below is chosen.

---

## 1. What "build with Notability Pro" means in practice

The full official text, from the MHacks 2026 Hacker Handbook › Tracks & Prizes [V]:

> "To qualify, a team has to build with Notability Pro at some point during the hackathon. Recommended uses: ideation, brainstorming, discussion summaries, wireframing, etc. Teams submit on Devpost (or whatever platform you use), tag "Notability" in reference to tools used, and add a quick note on how they used Notability Pro (including at least 2 screenshots)."
> — [Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)

So the qualifying checklist is:

| Requirement | What it takes | Source |
|---|---|---|
| Use **Notability Pro** (not the free Starter tier) during the 24 h | One Pro account. Teammates can join one shared note by live collaboration (see §2) | [V] rule; the shared-note approach is [I] |
| Use it for process work (ideation, brainstorm, summaries, wireframes) | No product integration required | [V] |
| Add "Notability" to Devpost's *Built With* tags | 10 seconds | [V] |
| Write a "quick note" on how you used it, with **≥2 screenshots** | About 20–30 min | [V] |

**Bottom line:** this is a *usage* requirement, not an *integration* requirement, so qualifying costs almost nothing. A product-level integration is optional. It is possible through Notability's file formats (PDF/PNG export, CSV flashcard import, public share links, §2), and it is a way to stand out rather than a requirement.

The one real cost is getting Pro access. Pro is $79.99/yr on sale, or $99.99/yr list [V] ([pricing](https://notability.com/pricing)). I could not verify a Pro free trial, the monthly price, or whether Notability is handing out event codes [U]. The handbook has no Notability workshop and no promo code, and the schedule lists no Notability session on either day [V] ([schedule sheet embedded in the handbook](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q)). **Ask at the Sponsor Expo (11:30 AM, Pierpont Connector Hall)** [V schedule]. If no codes exist, one person paying for Pro covers the team (inference).

---

## 2. The technology

**What it is.** Notability is Ginger Labs' note-taking app (San Francisco): handwriting, PDF annotation, audio recording synced to ink, and AI study tools [V] ([notability.com](https://notability.com/)). It has 457K App Store ratings at 4.8 and is an Editors' Choice [V] ([App Store](https://apps.apple.com/us/app/notability-smarter-ai-notes/id360593530)). It claims "5M+ students worldwide" [V] ([students page](https://notability.com/students)).

**Platforms.** iPad, iPhone, Mac, Windows, Android and web [V] ([pricing](https://notability.com/pricing); [Back-to-School 2026 post](https://blog.notability.com/post/notabilitys-back-to-school-2026-guide-every-new-feature-explained)). The FAQ says it works "via web browser — including Windows and Chromebook" [V] ([students](https://notability.com/students)). Requirements are iOS 17 / macOS 14 or later [V] ([Subscription FAQ](https://support.gingerlabs.com/hc/en-us/articles/4409501940122-Notability-Subscription-FAQ)).

**What Pro adds**, and therefore what a "best use" entry should visibly show [V] ([pricing](https://notability.com/pricing); [Subscription FAQ](https://support.gingerlabs.com/hc/en-us/articles/4409501940122-Notability-Subscription-FAQ); [Learn](https://support.gingerlabs.com/hc/en-us/articles/8073483239834-Notability-Learn)):

| Pro-only or Pro-unlimited feature | Hackathon use |
|---|---|
| **Live Transcripts** (unlimited, real time) | Record your own team's brainstorm and decision meetings. Record sponsor talks only with the speaker's OK. |
| **Smart Notes** (real-time structured summary while recording) | Automatic "discussion summaries", one of the sponsor's own recommended uses |
| **Action Items** (generated from notes) | A task list straight out of the kickoff meeting |
| **Chat with your notes** | "What exactly did the SpaceX rep say counts as space data?" |
| Unlimited quizzes and flashcards (Learn) | Drill the team on judge Q&A before the 3-minute pitch. The handbook stresses "Q&A Readiness" [V] ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)). |

Pro also includes everything in Plus, and Plus includes "everything in Lite and Classic" [V] ([pricing](https://notability.com/pricing)). Classic includes **live collaboration** [V] ([Subscription FAQ](https://support.gingerlabs.com/hc/en-us/articles/4409501940122-Notability-Subscription-FAQ)), so Pro includes live collaboration (inference from those two pages).

**Collaboration and sharing.** Live collaboration works "across iOS, Mac, and Web". You invite by email or link, with view/edit permissions and presence indicators. Learn features work only for contributors who have Plus or Pro [V] ([Live Collaboration](https://support.gingerlabs.com/hc/en-us/articles/10463526132122-Live-Collaboration)). **Link sharing** produces a public link "viewed in any browser" [V] ([Link Sharing](https://support.gingerlabs.com/hc/en-us/articles/360052943751-Link-Sharing)). That link can go straight into the Devpost write-up.

**I/O formats, the only way into a product.** Notes export as PDF, Note, JPEG, PNG or NTB [V] ([Sharing Notes](https://support.gingerlabs.com/hc/en-us/articles/205228298-Sharing-Notes)). Flashcard Import takes Anki decks, text files or "a CSV of cards you generated with Claude or ChatGPT" [V] ([Back-to-School 2026 post](https://blog.notability.com/post/notabilitys-back-to-school-2026-guide-every-new-feature-explained); [flashcard import](https://notability.com/flashcard-import)). Smart Notes and transcripts can't be exported, only copied and pasted [V] ([Smart Notes – Web](https://support.gingerlabs.com/hc/en-us/articles/9598555904794-Smart-Notes-Web-App); [Live Transcripts – Web](https://support.gingerlabs.com/hc/en-us/articles/9628119505562-Live-Transcripts-Web-App)).

**Known gotchas**
- **Live Transcripts aren't on the Mac app** ("Currently, this feature is not available on Mac") [V] ([Live Transcripts – Web](https://support.gingerlabs.com/hc/en-us/articles/9628119505562-Live-Transcripts-Web-App)). Record on an iPad, an iPhone or the web app.
- **The web app is weak for handwriting:** "using a stylus is not supported on the Web App when using an iOS device" [V] ([Web App FAQ](https://support.gingerlabs.com/hc/en-us/articles/9343031114906-Web-App-FAQ)). Hand-drawn wireframes really want an iPad with a pencil. If nobody has one, type and import, and use iPhone finger-sketching (inference).
- **Purchase paths differ:** App Store subscriptions are tied to an Apple ID, and web subscriptions go through Stripe [V] ([Subscription FAQ](https://support.gingerlabs.com/hc/en-us/articles/4409501940122-Notability-Subscription-FAQ)).
- **The free tier caps you at 5 notes** [V] ([pricing](https://notability.com/pricing)). That is fine for teammates who are only contributors on one shared note (inference).

**Realistic integration time:** about **1.5–2 person-hours** for a strong process entry: 15–30 min setup, about 30 min of net-new note work (the rest replaces planning you'd do anyway), and 30 min for screenshots and the Devpost note. Add **3–5 hours** for a product-level integration (sketches B/C). These are my estimates (inference).

**MHacks-specific resources:** no Notability workshop on Sat or Sun [V] ([schedule](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q)). No codes are mentioned in the handbook [V]. Notability is a **second-tier sponsor** on mhacks.org: its logo is in the large-logo row with FREE-WILi and U-M, just below Fetch.ai's solo top slot and above Capital One, SpaceX/xAI, Relay and the rest. I measured this from logo-size classes in the page HTML [V] ([mhacks.org](https://www.mhacks.org/)). That points to reps on site and real interest in the entries (inference).

---

## 3. What this sponsor's judges reward

**Published criteria:** only the track name, "Trust the Process (Best use of Notability)," plus the rule text above [V] ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)). No rubric is published.

**Prior winners:** I found **none**. I checked about 140 Devpost hackathon pages from fall 2026 and earlier for "Notability" or "Ginger Labs" with no hit. Devpost then started returning 403 to my requests, so the check is incomplete, and my web-search quota was exhausted. **Treat "no precedent" as unverified.** It may be Notability's first hackathon prize [U].

**What they most likely reward** (inference from the rule wording, the track name, and the sponsor's 2026 product push):
1. **Visible use of Pro-only features** (Live Transcripts, Smart Notes, Action Items, Chat, Learn), not plain handwriting that the free tier also does. The rule names *Pro*, so the sponsor cares about Pro specifically.
2. **A real "process" story.** The title is "Trust the Process," and the recommended uses are all process steps. The best entry shows how the notes changed decisions: an idea killed in the brainstorm, a wireframe that became the UI, a transcript quote that changed scope.
3. **Marketing-ready artifacts.** A tier-2 sponsor wants screenshots and stories it can reuse. Clean, legible, well-captioned screenshots and a public share link help (inference).
4. **A product tie-in to the 2026 roadmap, as a bonus.** Notability's back-to-school post leads with Flashcard Import from "Claude or ChatGPT" CSVs, cross-device sync and live collaboration [V] ([post](https://blog.notability.com/post/notabilitys-back-to-school-2026-guide-every-new-feature-explained)). A project that produces or consumes Notability files fits that story directly (sketches B/C).

Judging logistics: sponsors judge their tracks during the 12:30–2:30 PM main judging, and "To be judged for any track, your team must be present" [V] ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)). Have the Notability note open on a tablet at the table (inference).

---

## 4. Prize value

Official prize: "1 year of Notability Pro, 4 pieces of exclusive Notability merch for each team member" [V] ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)). The brief's "1 year of Notability Pro + exclusive merch" understates it: the merch is **4 pieces per member**. It is ambiguous whether "for each team member" also covers the Pro year. I read it as per member, but that is [U].

| Component | Retail | Basis |
|---|---|---|
| Pro, 1 yr × 4 members | $320–400 | $79.99 sale / $99.99 list [V] ([pricing](https://notability.com/pricing)) |
| Merch, 4 pieces × 4 members | ~$80–300 | Unknown items. My guess is $5–20 per piece [I] |
| **Team total (retail)** | **~$400–700** | If Pro is one per team instead: ~$180–400 |
| **Realistic value to students** | **~$150–400** | Pro only matters to members who would otherwise pay for a notes app [I] |

**Against the other sponsor prizes** (handbook values [V]): Fetch.ai $1,250/$750/$500 cash. SpacetimeDB $1,000/$500/$200. Neon $1,000/$500/$100 in credits. Capital One $300 per member, so about $1,200 for 4. Photon $700 ($400 cash). ElevenLabs Scale tier ($897 per member nominal, in credits). Relay: SF trip and a week at the Relay house. FinchNode: Apple Watch SE3, $500 cash for 2nd. Notability sits in the **bottom third on prize value**, near Figma (LEGO set plus merch) and SpaceX (keyboards).

---

## 5. Expected competition

**Analog data from my recount** of Devpost prize filters at MHacks 2025 (122 submissions), counting unique project links per filter on 2026-10-03 [V] ([gallery](https://mhacks-2025.devpost.com/project-gallery)):

| 2025 prize | Barrier | Opt-ins | Share |
|---|---|---|---|
| MLH Best Domain Name (GoDaddy): "register a domain" | Tool-only, the closest analog | 10 | 8% |
| MLH Best Use of Auth0 | Light API | 6 | 5% |
| MLH Best Use of Gemini API | Free API most teams already use | 47 | 39% |
| Best Use of Fetch.ai | Real integration | 14 | 11% |
| Best use of Snap AR | Hardware/AR | 9 | 7% |

The Overdrive filter returned 40, matching the main-track verdict's independent count of 40, which validates the method ([Overdrive filter](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90484)).

**Estimate for Notability 2026 (inference):** 10–25% of submissions opt in. The barrier is as low as GoDaddy's, the brand is well known among students, and a tier-2 sponsor will promote it at the expo. If MHacks 2026 lands near 2025's 122 submissions [U], that is **about 12–35 opt-ins**. Most will be two screenshots of a free-tier doodle. I expect only **3–10 deliberate entries** that show Pro features and a coherent process story (inference).

**expected_competition: medium.** The opt-in count may be high, but the serious field is small.

---

## 6. Expected value, honestly compared

- **P(win) for a team running the playbook in §9: about 15–25%** (inference: 1 winner among about 3–10 serious entries, with a better-than-average entry). With no Pro features and two screenshots, it drops to about 3–5%.
- **EV ≈ 0.20 × $150–700 ≈ $30–140**, with a midpoint around **$80**. The cost is about 2 person-hours, or **≈ $40/person-hour**.
- **Comparison (inference, rough):** a typical cash sponsor track such as Fetch.ai (3 cash places, $2,500 pool) or SpacetimeDB ($1,700 pool) probably gives a careful team 10–25% odds at *some* place. That is an EV of a few hundred dollars, but it costs 4–10 person-hours of real integration and the integration must fit the product. Those tracks win on absolute EV, and Notability wins on EV per hour and on zero constraint.
- **Honest ranking:** if the team can enter only 3 sponsor tracks, Notability should **not** take a slot from SpaceX, Relay or a cash track that fits the product. It does not have to, though: Notability takes no slot, because it never touches the codebase or the demo.

---

## 7. Stacking

Notability is the most orthogonal track on the board. It constrains nothing about the product.

| Pairing | Fit | Notes |
|---|---|---|
| **Main: Sustainability** (the verdict) | ✅ | Neutral. Sketch B adds a native tie-in. |
| Main: Hardware / AI / FinTech | ✅ | Neutral. Hand-sketched circuit diagrams and wiring notes are good Notability screenshots for Hardware (inference). |
| **Fun: Judged by an LLM** (the verdict) | ✅+ | The LLM judge's inputs and rubric are unpublished [V] ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)). If it reads Devpost, a structured "How we built it" with process evidence costs little and may help (inference). |
| Fun: Dumbest Idea / Useless AI | ✅ | The brainstorm transcript of rejected dumb ideas is good comic material for the write-up (inference). |
| **SpaceX "Make it Legendary"** | ✅ with care | SpaceX gives "Bonus points, if you use Grok Bot for project planning and team collaboration" [V] ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)). Both tracks reward the planning process. **Split roles:** Grok Bot for task chat and coordination, Notability for the visual and audio record (sketches, wireframes, transcripts). Both get screenshots. There is no rule conflict [V]; looking scattered is the risk [I]. |
| Figma Best Design | ✅+ | Low-fi wireframes in Notability, then high-fi in Figma, is a natural before/after pair for both write-ups (inference). |
| Relay / Photon / Fetch.ai / ElevenLabs / Neon / SpacetimeDB / FREE-WILi / FinchNode / Capital One | ✅ | Neutral. Sketch C gives Relay and Fetch.ai a Notability tie-in. |
| Conflicts | None | The only cost is roughly 2 person-hours of attention. |

**Recommended stack line:** *Sustainability + Judged by an LLM + SpaceX + (Relay or Fetch.ai) + FREE-WILi (optional) + Figma + **Notability***. This matches the verdict's "3–4 real integrations + Notability as the free extra" ([verdict file](/Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md)).

---

## 8. Project sketches

### A. "Lab Notebook" (default): Notability as the visible process layer on the verdict's project. Cost about 2 h.
Run the Sustainability + SpaceX project as planned, and keep **one live-collaboration Notability note** as the team's 24-hour lab notebook:
1. **12:00–1:00 kickoff:** record the team brainstorm with Live Transcripts and Smart Notes. Generate **Action Items** and use them as the task list.
2. **Sponsor sessions:** ask before recording, e.g. at the SpaceXAI 4 PM session ([schedule](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q)). Later use **Chat with your notes**: "Did they say Earth-observation data counts as space data?" That question is the verdict's open eligibility risk.
3. **Wireframes and architecture** hand-drawn on an iPad, then rebuilt in Figma for a before/after screenshot.
4. **A "decision log" page:** ideas killed and why, plus the 2 AM pivot.
5. **Sunday 10–11:30 AM:** run **Learn** on the pitch notes to generate practice questions and drill judge Q&A.
6. **Devpost:** a "How we used Notability Pro" section with 4–6 captioned screenshots and the public share link.
- **Stacks:** everything; no product change.
- **Why it wins:** it shows 5 Pro-only features with a story arc, where most entrants show 2 screenshots of a free-tier doodle.

### B. "WattWalk": a Sustainability product with Notability inside the loop. Adds about 3–5 h.
A building energy-audit flow. A student opens a dorm floor-plan PDF in Notability, walks the floor and circles waste on the plan: lights left on in empty rooms, drafty windows, a space heater. They record voice notes as they go, and Live Transcripts capture them. They **export the annotated PDF** [V export formats] and upload it to the web app. A vision LLM pulls out the marked issues and joins them to satellite and grid data: NASA POWER irradiance, as the Sustainability advocate proposed, plus carbon intensity. The app returns a prioritized, carbon-weighted fix list, and sends a summary PDF **back for import into Notability** for the RA's own markup.
- **Stacks:** Sustainability, Judged by an LLM, SpaceX if satellite data is accepted [U, the verdict's open question], Fetch.ai (agent that files maintenance requests), Neon (audit store), FREE-WILi (sensor confirms the "lights on in an empty room" mark), Figma, Notability.
- **Why it wins Notability:** Notability is the field-capture device in the product, not just the planning notebook. Pencil-on-PDF is Notability's core strength.
- **Risk:** the PDF-parsing pipeline costs hours and adds a demo step. Only worth it if the team wants a stronger Notability bid than sketch A.

### C. "Lecture → Deck": the AI-track fallback (if the verdict flips to AI). Adds about 3–5 h.
A Relay or Fetch.ai agent receives an exported Notability lecture PDF or PNG, together with the copy-pasted live transcript. It writes **spaced-repetition flashcards as a CSV in the format Notability's new Flashcard Import accepts** [V]. An **eval** reports card accuracy against the source, which matches the verdict's "AI, with an eval" flip condition. The student imports the CSV into Notability and studies there with built-in spaced repetition [V].
- **Stacks:** Actually Intelligent (AI), Judged by an LLM, Relay (the sponsor's "📚 School: classes, study spots" idea [V]), Fetch.ai, ElevenLabs (spoken quiz), Neon, Notability.
- **Conflicts:** SpaceX, unless the course content is space science, which is a stretch.
- **Why it wins Notability:** it feeds Notability's 2026 headline feature, CSV import of "cards made with Claude or ChatGPT" [V].
- **Risk:** it overlaps Notability's own Learn quiz generator, so the pitch must show something Learn can't do, such as cross-lecture decks, the eval, or the text-your-agent channel (inference).

---

## 9. Playbook (cheap, time-boxed)

| When | Who | What |
|---|---|---|
| 11:30 AM, Sponsor Expo | Pitcher | Ask Notability: (1) are there Pro codes or a trial? (2) one Pro account per team, or Pro for everyone? (3) is it judged from Devpost, at the table, or both? (4) what did they hope to see? |
| 12:00 PM | Anyone with an iPad | Create the shared "MHacks26 Lab Notebook" note and invite teammates (live collaboration). |
| 12:00–1:00 PM | Team | Record the brainstorm with Live Transcripts. Save Smart Notes and Action Items. |
| Through Sat | Designer | Do wireframes and architecture by hand in the note. Keep a decision log. |
| Sun 10:00–11:00 AM | Pitcher | Generate a Learn quiz from the pitch notes and drill Q&A. Take screenshots. |
| Sun 11:00–11:45 AM | Pitcher | Write the Devpost "How we used Notability Pro" section: ≥4 captioned screenshots, the public link, and the "Notability" Built-With tag. **Submit before 12 PM: "no late submissions or exceptions"** [V] ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)). |
| 12:30–2:30 PM | At the table | Keep the notebook open on the iPad next to the demo, and offer a 20-second walkthrough to the Notability rep. |

---

## 10. Red flags, rival arguments, rebuttals

**Honest weaknesses**
1. **The prize is small, non-cash, and goes to one winner.** That is about $150–400 of real value (§4).
2. **There is no rubric and no precedent.** I found no prior Notability hackathon winners [U], so "best use" is subjective and may reward rapport or polish.
3. **Pro access may cost money:** $79.99–99.99/yr if no codes exist [V price; U codes].
4. **The hardware dependency is soft but real.** The best Notability experience needs an iPad with a pencil, and Live Transcripts are missing on the Mac app [V]. A team of laptop-only Mac users gets a weaker entry.
5. **There is no demo impact.** Judges at other tables won't care, so the track does nothing for the main-track or grand prize.
6. **Recording etiquette.** Transcribing sponsor talks or other teams without consent is a bad look. Record your own team, and ask before recording sessions (inference, common courtesy).

**Rival advocates' best attacks, with rebuttals**
- *"This isn't a sponsor track, it's a screenshot contest. The prize is a $100 app subscription."* Partly true on value. But in EV per person-hour it is the best track on the board (§6), and it is the only one that costs nothing in architecture, demo time or main-track fit. The judge shouldn't rank it *instead of* a cash track, and it doesn't need to be.
- *"Everyone will enter, so your odds are 1 in 30."* The closest MHacks 2025 analog (GoDaddy) drew only 8% of projects, and most low-barrier entries are low-effort. The relevant field is the 3–10 deliberate entries (inference).
- *"Those 2 hours belong on the Fetch.ai/SpacetimeDB integration."* Most of the hours *replace* planning the team does anyway (brainstorm, wireframes, task list). Net new work is about 1 hour, and the least-loaded member (designer or pitcher) can do it.
- *"It muddies SpaceX's Grok Bot planning bonus."* Split the roles as in §7. Two process tools each doing a distinct job is a better "process" story than one tool doing everything (inference).
- *"Notability might see sketch C as competing with Learn."* That is why sketch A is the default and C is only the AI-track fallback. C's pitch frames itself as feeding Notability's import feature.

---

## 11. Scorecard

| Criterion | Score | One-line justification |
|---|---|---|
| Prize value | **3/10** | One winner. Pro ($99.99/yr list) plus 4 merch items per member is roughly $400–700 retail and about $150–400 of real value, near the bottom of the 12 tracks. |
| Win probability | **6/10** | A tool-only analog drew 8% at MHacks 2025. Most entries will be low-effort, so a deliberate Pro-feature entry has about a 15–25% chance (inference). |
| Integration ease | **10/10** | No code and no API. About 1.5–2 person-hours, mostly planning work done anyway. |
| Stacking potential | **10/10** | Fits every main, fun and sponsor track with no conflicts. It even pairs with the Figma and SpaceX planning bonuses. |
| Demo impact | **3/10** | Invisible in the product demo unless sketch B or C is built (then about 5). |
| Fit with team preferences | **8/10** | The team wants "several sponsor tracks if they fit." This one fits anything and never threatens the SpaceX/Relay preferences, but the team never named it. |

**Overall:** enter it, cheaply and deliberately (sketch A). Never let it steer the project.

---

## Sources
- MHacks 2026 Hacker Handbook (schedule embed, judging, deadline, presence rule): https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af
- Handbook › Tracks & Prizes (Notability rule and prize text, all sponsor prizes, SpaceX Grok Bot bonus, Relay ideas): https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5
- Handbook › MHacks 26 Tracks: https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b
- MHacks 2026 schedule sheet (Sat and Sun tabs, no Notability session): https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q
- mhacks.org sponsor wall (Notability in the second logo tier): https://www.mhacks.org/
- Notability home: https://notability.com/
- Notability pricing (Starter/Lite/Plus/Pro, sale vs list, platforms, "Everything in Lite and Classic plus"): https://notability.com/pricing
- Notability plan comparison: https://notability.com/pricing/compare
- Notability for Students (platforms, web on Windows/Chromebook, 5M+ students): https://notability.com/students
- Notability flashcard import: https://notability.com/flashcard-import
- Notability Back-to-School 2026 post (Flashcard Import CSV from Claude/ChatGPT, cross-platform, collaboration): https://blog.notability.com/post/notabilitys-back-to-school-2026-guide-every-new-feature-explained
- App Store listing: https://apps.apple.com/us/app/notability-smarter-ai-notes/id360593530
- Subscription FAQ (tiers, Classic includes live collaboration, iOS 17/macOS 14, Stripe web purchase): https://support.gingerlabs.com/hc/en-us/articles/4409501940122-Notability-Subscription-FAQ
- Notability Learn (Live Transcripts, Smart Notes, Chat, Action Items are Pro): https://support.gingerlabs.com/hc/en-us/articles/8073483239834-Notability-Learn
- Live Collaboration: https://support.gingerlabs.com/hc/en-us/articles/10463526132122-Live-Collaboration
- Link Sharing: https://support.gingerlabs.com/hc/en-us/articles/360052943751-Link-Sharing
- Sharing Notes / export formats: https://support.gingerlabs.com/hc/en-us/articles/205228298-Sharing-Notes
- Web App FAQ (no stylus on iOS web): https://support.gingerlabs.com/hc/en-us/articles/9343031114906-Web-App-FAQ
- Smart Notes – Web App: https://support.gingerlabs.com/hc/en-us/articles/9598555904794-Smart-Notes-Web-App
- Live Transcripts – Web App (not on Mac): https://support.gingerlabs.com/hc/en-us/articles/9628119505562-Live-Transcripts-Web-App
- MHacks 2025 Devpost (prize list, gallery): https://mhacks-2025.devpost.com/ and https://mhacks-2025.devpost.com/project-gallery
- MHacks 2025 opt-in filters (my recount, 2026-10-03): GoDaddy https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90669 · Auth0 https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90666 · Gemini https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90668 · Fetch.ai https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90535 · Snap AR https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90536 · Overdrive (validation) https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90484
- Main/fun verdict (context for the stack): /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md

*Method note: Notion pages were read through Notion's public page API. Devpost opt-in counts are unique `devpost.com/software/...` links per prize filter. My scan of Devpost pages for earlier Notability sponsorships was cut short by Devpost 403s, and the web-search quota was exhausted, so "no prior Notability winners found" is unverified. Everything marked [I] is my reasoning, not a sourced fact.*

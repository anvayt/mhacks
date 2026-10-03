# Sponsor Track Advocate — Best Design (Figma x MHacks)

## Prompt given (excerpt)
> You are the advocate for the sponsor track "Best Design (Figma x MHacks)" at MHacks 2026. Research the sponsor's tech and how fast a team can integrate it, what its judges reward, prize value vs competition, expected value, how it stacks with the main/fun picks and other sponsors, 2–3 winning project sketches, honest red flags, and a 1–10 scorecard. Make the strongest honest case — an impartial judge will weigh your file against eleven other sponsor advocates.

Tags: **[V]** verified at the cited URL on 2026-10-03 · **[I]** my inference · **[U]** unverified / ask on site.

---

## Core case

**Best Design is the cheapest prize on the board, and the work it rewards pays off in every other track.** Entering is a Devpost checkbox. Competing seriously takes about 3.5 hours from one person: a Figma file with a small design system, 3–5 high-fidelity screens, and a design-to-code pass. The team needs a usable UI anyway, because MHacks' own judges score on "innovation, technical complexity, usability, and presentation quality" [V, [Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)].

**The prize itself is small, and I won't hide that.** 1st place gets a LEGO Architecture Trevi Fountain set ($159.99 retail, one set). The top 3 each get a "Figma merch bundle (7+ items)". The handbook says 7+, not the 13+ in the brief [V, [Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5); [Brickset](https://brickset.com/sets/21062-1/Trevi-Fountain)]. Direct expected value is about **$20–30**, one of the lowest of the 12 sponsor tracks.

**The real argument is spillover.** At peer events in 2026, the projects that won design prizes kept winning other prizes too:
- **Rekindle** (HackDavis 2026) won Hacker's Choice, Best UI/UX Design (sponsored by Figma) and Best Use of ElevenLabs.
- **NeighborFridge** (LA Hacks 2026, a food-waste app) won both the Figma Make Challenge and Best UI/UX.
- **BraceML** (Hacklytics 2026) won First in Sports and Figma Make.

All three are [V], see §2. At MHacks, judges get 3 minutes at the table [V], and may compare projects **two at a time** using MHacks' new MDredd tool ([V repo](https://github.com/mhacks/MDredd); whether MHacks uses it this weekend is [U]). In both formats, how the product looks is the first thing a judge sees.

**Verdict:** enter Best Design with whatever the team builds under Sustainability. Give one person the job of owning design, with a 3.5-hour budget. Don't pick the project around this prize. It keeps the judge's recommended stack (Sustainability + Judged by an LLM + SpaceX) as it is. The Figma MCP server runs inside **Cursor** [V], so the design work also counts as more Cursor use for SpaceX's "the more you use Cursor, the more likely you are to win" [V].

**Do now (hacking started at noon):**
1. Start Figma Education verification immediately. It can take days (see §1).
2. Send the design owner to **"Figma: Hackathon Design + Figma", Sat 5:30–6:30 PM, Duderstadt 3336** [V, [schedule](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365)]. Ask four things there: is a Figma file required, who judges, what the rubric is, and whether the merch is per team or per member.

---

## 1. The technology

### What it is
Figma is a browser and desktop design tool. Four parts of it matter here:
- **Figma Design:** frames, components, variables and clickable prototypes.
- **FigJam:** a whiteboard.
- **Dev Mode:** inspect and handoff.
- **Figma Make:** prompt-to-app. It produces "code-backed" prototypes and web apps that you can still edit visually, and they can be published to a URL with a backend [V, [Make](https://www.figma.com/make/), [Explore Make](https://help.figma.com/hc/en-us/articles/31304412302231-Explore-Figma-Make)].

The **Figma MCP server** connects AI coding agents to Figma files. It can pull design context, generate code from frames, and capture live UI back as layers. It supports **Cursor**, VS Code, Claude Code and others. The remote server "is available on all seats and plans" [V, [MCP guide](https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Dev-Mode-MCP-Server)].

### Is a Figma file required? How is it judged?
- **Requirement:** none is published. The handbook's Best Design entry has a heading, "Figma x MHacks", and the prize line, and nothing else. There is no description or eligibility rule [V, [Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)]. Compare Notability on the same page: "To qualify, a team has to build with Notability Pro" [V]. So **as written, Figma is not mandatory.**
  - *[I]* The "Figma x MHacks" branding and a Figma-run workshop make it very likely the judges expect Figma in the process. Peer Figma prizes asked for it explicitly (§2). Treat a linked Figma file as effectively required.
- **Who judges:** [U]. Figma is **not** on the sponsor logo wall in MHacks' site source ([V, Sponsors.tsx](https://github.com/mhacks/dashboard/blob/main/components/landing/sections/Sponsors.tsx)). That fits "Figma x MHacks" being an MHacks-run prize with Figma-supplied merch and a Figma-led workshop [I]. Judges could be MHacks organizers, the workshop host, or both [U].
- **How:** no rubric has been published [V]. The logistics are known [V, [Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)]:
  - Judging runs Sunday 12:30–2:30 PM in the Duderstadt Center.
  - Each team gets a "three-minute window", and "Projects may be judged more than once by different judges."
  - "Company-track sponsors will evaluate projects" during the same block.
  - "To be judged for any track, your team must be present."
- **Best proxy rubric** [I], built from MHacks' own "Usability" definition plus the peer Figma briefs in §2:
  1. Visual craft and consistency: a real design system.
  2. Usability and accessibility. MHacks 2025 defined usability as "Intuitiveness and user-friendliness… Accessibility and inclusivity in design and functionality" ([V, MHacks 2025 Devpost](https://mhacks-2025.devpost.com/)).
  3. Visible design process: wireframe → hi-fi → build.
  4. Delight.
  5. The design is the working product, not a mockup.

### Access and cost
| Option | What you get | Catch |
|---|---|---|
| **Education plan** (free, higher-ed) | Professional plan **with AI tools, including Figma Make**, and 3,000 AI credits/month [V, [verify eligibility](https://help.figma.com/hc/en-us/articles/360041061214-Verify-your-eligibility-for-Figma-for-Education)]. MCP: 200 tool calls/day, 10/min [V, [rate limits](https://developers.figma.com/docs/figma-mcp-server/rate-limits-access/)]. | Verification goes through SheerID: "SheerID will email you within a few days" [V]. It **may not clear before Sunday's deadline.** |
| **Starter** (free) | "A single team with one folder and 3 files" plus unlimited drafts, prototypes included [V, [plans](https://help.figma.com/hc/en-us/articles/360040328273-Figma-plans-and-features)]. 150 AI credits/day, up to 500/month [V, [pricing](https://www.figma.com/pricing/)]. | Make is for "Full seats on paid plans", though "You can try Figma Make on other seats and plans" [V]. MCP is capped at **20 tool calls per month** [V]. |

The [education page](https://www.figma.com/education/) also confirms that Design, FigJam and Dev Mode are free for students [V].

### Realistic integration time (one design owner; my estimates [I])
| Step | Hours |
|---|---|
| Accounts, a shared team file, and starting Education verification | 0.25 |
| Moodboard plus tokens (color, type, spacing as Figma variables). Optionally, 2–3 directions explored in Make | 0.75 |
| 3–5 key screens in hi-fi, plus a clickable prototype of the main flow | 1.5 |
| Connect the Figma MCP server in Cursor and pull frames and components into code | 0.5 |
| Devpost assets: design-system frame, before/after, view-only Figma link, and a 20-second "design story" for the pitch | 0.5 |
| **Total incremental** | **≈3.5** |

Front-end implementation itself isn't counted, because the team builds a UI regardless.

### Known gotchas
- **Verification lag.** Start SheerID now. If it hasn't cleared, design on Starter (3 team files is enough) and use MCP sparingly, since Starter allows only 20 calls a month [V].
- **Rule risk:** "All coding and building must be done during the hackathon" [V, [Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)]. Create the Figma file after noon Saturday so its version history shows that [I]. Credit any community UI kit you use [I].
- **Sharing:** set the file to "anyone with the link can view" before linking it on Devpost, or judges can't open it [I].
- **Mismatch risk.** A beautiful Figma file next to a different-looking shipped UI hurts more than it helps [I]. Judges see the real app at the table.
- **Time sink.** The MHacks 2024 rubric literally asked whether the project demos live ([year research](/Users/anvaytodkar/Code/mhacks/results/year-research/2024.md), from the archived 2024 guide). Make sure the end-to-end demo works first, freeze the UI by about 6 AM Sunday, then polish only [I].

---

## 2. What this sponsor's judges reward

MHacks has **no Best Design precedent**. The 2024 and 2025 MHacks Devpost prize lists have no design prize, only "Usability" as a general criterion ([V, 2024](https://mhacks-2024.devpost.com/), [V, 2025](https://mhacks-2025.devpost.com/)). So the evidence comes from Figma-linked prizes at peer events in 2026. I pulled each prize's Devpost filter and opened every winner's page.

| Event / prize | Brief (what Figma asked for) | Entrants / total projects | Winner(s) and what they built |
|---|---|---|---|
| **HackDavis 2026, "Best UI/UX Design", Sponsored by Figma** (Sony WH-1000XM5) | "Project uses Figma to create beautiful design and intuitive web experiences that bring joy to users… not only functional but also delightful, demonstrates wireframing, responsive design" [V, [event](https://hackdavis-2026.devpost.com/)] | **60 / 139 (43%)** [V, [filter](https://hackdavis-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=101832)] | **Rekindle:** an always-on display for elderly relatives with an ElevenLabs voice companion, plus a family mobile app. Its gallery has a "Design System" image and two linked Figma files. It also won **Hacker's Choice** and **Best Use of ElevenLabs** [V, [Devpost](https://devpost.com/software/rekindle-koiq9s)]. |
| **LA Hacks 2026, "Figma Make Challenge"** (Figma plushies; highlighted by Figma for Edu) | "We're not looking for a finished product built entirely in Make… show us the process… No design experience required" [V, [brief](https://docs.google.com/document/d/1jEZ_NcL3acSJh5H2YwzfTYL8gAuj73k_Bsj9Y5uVWVg)] | **104 / 307 (34%)**, 13 winners [V, [filter](https://la-hacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=101253)] | **NeighborFridge**, a food-waste app that also won Best UI/UX: Figma moodboard → Make → Codex [V, [Devpost](https://devpost.com/software/neighborfridge)]. **GoTrail**: Make used "to explore design system directions before writing a single line of SwiftUI" [V, [Devpost](https://devpost.com/software/gotrail)]. **Grouper**: the team says "Figma Make is the reason we slept at night" [V, [Devpost](https://devpost.com/software/grouper-fr2h1q)]. **Accent** also won a main track [V, [Devpost](https://devpost.com/software/accent-cdw2qi)]. |
| **LA Hacks 2026, "Best UI/UX"** (organizer prize, Wacom tablet; not Figma) | n/a | **152 / 307 (50%)**, 1 winner [V, [filter](https://la-hacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=101378)] | NeighborFridge (above) |
| **Hacklytics 2026, "Figma Make Most Creative Data Visualization"** (Figma Timbuk2 backpack per member) | Data-viz focus [V, [event](https://hacklytics-2026.devpost.com/)] | **40 / 234 (17%)**, 2 winners [V, [filter](https://hacklytics-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=97291)] | **FarmCast**: NOAA forecasts turned into frost warnings and crop timelines [V, [Devpost](https://devpost.com/software/the-last-human-internet)]. **BraceML**: Make used to design a dense biomechanics dashboard; also won First in Sports [V, [Devpost](https://devpost.com/software/braceml)]. |

*Totals are my gallery count, ±1. Entrant counts are each prize's Devpost filter.*

**What wins, per the evidence** [I from the rows above]:
1. **A written design story.** Every winner's write-up describes how Figma was used: moodboard, design system, Make exploration. Figma for Edu said outright that it rewards process.
2. **A specific human user**, such as elders, small farmers, students wasting food or new hikers. Design is judged as empathy, not decoration.
3. **Data made legible.** FarmCast and BraceML won by making dense data readable. That suits a satellite-data project.
4. **The design sits on a working, deployed product.** Rekindle, NeighborFridge and Grouper all have live URLs.
5. **Design winners co-win.** 4 of the 7 design-prize winners named above (Rekindle, NeighborFridge, Accent, BraceML) won at least one other prize. GoTrail, Grouper and FarmCast won only the Figma prize.

MHacks history agrees. **Wattson** won MHacks 2025's Greenprint (Sustainability) track and FREE-WiLi with a custom on-screen pet GUI [V, [Devpost](https://devpost.com/software/wattson-5btsyd)]. **SignVerse** won MHacks 2024's Accessibility track [V, [Devpost](https://devpost.com/software/signverse)]. Our 2024 researcher called its UI "very polished" ([year research](/Users/anvaytodkar/Code/mhacks/results/year-research/2024.md)). The deCluttered.ai team (Fetch.ai winner, 2025) wrote that a calm, clean design earns more trust than flashy AI ([Devpost](https://devpost.com/software/declutttered-ai), via [year research](/Users/anvaytodkar/Code/mhacks/results/year-research/2025.md)).

---

## 3. Prize value and expected competition

**Prize value [V for items; I for dollar values]:**
- **1st:** LEGO 21062 Trevi Fountain (1,880 pieces, **$159.99** retail; [Brickset](https://brickset.com/sets/21062-1/Trevi-Fountain)) plus a merch bundle. It is one set, which a team of 4 can't split.
- **Top 3:** "Figma merch bundle (7+ items)". The handbook doesn't say whether that is per team or per member [V]. I value a bundle at about $40–100 if it is per team [I].
- **Realistic team value:** 1st ≈ **$200–260**; 2nd/3rd ≈ **$40–100**. Non-cash.

**Competition: high by count, lower by quality** [I]:
- Open design prizes drew **34–50%** of all projects at LA Hacks 2026 and HackDavis 2026, and 17% for a narrower data-viz brief (§2).
- MHacks 2025 had 122 projects ([gallery](https://mhacks-2025.devpost.com/project-gallery), via [year research](/Users/anvaytodkar/Code/mhacks/results/year-research/2025.md)).
- With no requirement to enter, expect **about 40–65 entrants** at MHacks 2026 [I]. Most will be box-tickers. Perhaps 5–10 will show a Figma file, a design system and a polished deployed app [I].

---

## 4. Expected value

**Win probability [I]:**
- Baseline: 3 placing slots ÷ ~55 entrants ≈ 5% for a top-3 finish.
- With a dedicated design owner, a linked Figma design system and a deployed app, I estimate about **15–20% for top 3 and 5–8% for 1st**.

**Direct EV ≈ 0.065 × $230 + 0.11 × $70 ≈ $23** [I].

| Sponsor track (handbook face value [V]) | Rough direct EV rank [I] |
|---|---|
| Fetch.ai $1,250 / $750 / $500 cash; SpacetimeDB $1,000 / $500 / $200; Capital One $300 × 4 | High |
| Photon $700 / $300; FinchNode Apple Watch SE3 / $500; ElevenLabs Scale tier; Neon credits; Relay SF trip; FREE-WILi kits | Middle |
| **Figma Best Design**; SpaceX keyboards; Notability Pro + merch | **Low** |

**Indirect EV is the honest reason to do it** [I]:
- The $2,500 main-track prize and the $5,000 Grand Prize [V, [Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)] are scored partly on usability and presentation [V].
- Fetch.ai weights "User Experience & Presentation" at **15%** [V, [hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)].
- If 3.5 hours of design work raises the chance of a main-track win by just 2 percentage points, that alone is worth about $50, twice the direct EV.
- The co-win pattern in §2 suggests the effect is real, though I can't separate cause from correlation.
- The marginal cost of entering is zero, and the work isn't wasted, since the team ships a UI anyway.

---

## 5. Stacking

| Track | Fit | Why |
|---|---|---|
| **Sustainability (recommended main)** | Strong | Maps and climate data viz are design-heavy. NeighborFridge (food waste) and FarmCast (weather) won design prizes in this territory [V]. |
| Actually Intelligent (AI) | Good | Polished UIs win here too, but chat-first products leave less to design. Add a generative or visual results view. |
| FinTech | Good | Dashboards are design-rich, but the team prefers to avoid FinTech. |
| Beyond the Code (Hardware) | Weak–OK | Little screen UI. Design the device screen and a companion dashboard, as Wattson did [V]. |
| **Judged by an LLM (recommended fun)** | Neutral+ | Put the design rationale in the Devpost write-up. Whether the LLM sees images is [U]. |
| Dumbest Idea / Useless AI | Good | A deadpan, polished design makes a joke land harder [I]. |
| **SpaceX "Make it Legendary"** | **Strong** | Cursor is required and "The more you use Cursor, the more likely you are to win" [V, [Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)]. The Figma MCP server supports Cursor [V], so design-to-code adds visible Cursor usage [I]. Grok Imagine renders can double as visual assets [I]. |
| Fetch.ai ASI:One | Good | 15% UX & presentation [V]. The interface is ASI:One chat, so design the result page or dashboard. |
| Relay / Photon | **Tension** | The UI lives in the Relay app or iMessage, which you don't design [V track text]. You need a companion surface such as a web map, display or kiosk. |
| ElevenLabs | Good | Voice UI is design. Rekindle co-won Best UI/UX and ElevenLabs [V]. |
| SpacetimeDB | Good | Live multiplayer state is visually demoable. |
| Capital One Nessie | Good | "Reimagine the banking experience" is a design brief. |
| FinchNode | Good | Healthcare UX. |
| FREE-WILi | OK | Design the handheld's screen UI in Figma (Wattson pattern). |
| **Notability** | **Strong** | "wireframing" is a listed recommended use [V, [Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)]. Notability sketches → Figma hi-fi make a natural before/after for both write-ups. |
| Neon | Neutral | Backend, so invisible. |

**Recommended stack (no change to the verdict):** Sustainability + Judged by an LLM + SpaceX + (Fetch.ai or Relay) + **Figma Best Design** + Notability, with ElevenLabs or Neon optional. I see no reason to argue for a different main or fun pick. If the team flips to Hardware, Best Design drops to "enter only if the screen UI and companion app are designed".

---

## 6. Project sketches

### A. "Rooftop Report Card" (Sustainability; SpaceX, Fetch.ai, Figma, Notability, Judged by an LLM)
A user types an Ann Arbor address and gets a one-page report card designed like a nutrition label:
- Satellite-derived solar potential from [NASA POWER](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/).
- Nearby heat and fire signals from [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/api/map_key/).
- Estimated savings.

Grok Imagine renders the user's roof with panels (SpaceX requirement). An ASI:One agent finds incentives and drafts the contractor email (Fetch.ai).

**Design hook:** the "label" is a strong, shareable artifact. Build a small design system around it (tokens, an accessible color ramp, mobile-first) in Figma, and pull it into code through the Figma MCP server in Cursor. **Demo:** a judge's own address → label in 20 seconds → share card. Whether SpaceX accepts Earth-observation data is still [U], per the verdict.

### B. "Smoke Signal" (Sustainability; SpaceX, Relay, ElevenLabs, Figma, Judged by an LLM)
The app reads NASA FIRMS hotspots and the wind forecast to predict "smoke days" for Michigan outdoor plans. Text or call the Relay agent ("can I run outside tomorrow?"), and it answers with voice.

**Design hook:** Relay's chat UI isn't ours, so the design surface is a calm, map-first web page and an always-on lobby display. Use colorblind-safe AQI ramps and a "calm under stress" design principle written into the Figma file. This follows the FarmCast and BraceML pattern of making dense data legible [V §2].

### C. "Vampire Hunter" (hardware flip, or Sustainability with a small FREE-WILi element; FREE-WILi, SpacetimeDB, Figma, Dumbest Idea, Notability)
A FREE-WILi handheld (IR transmit and receive, 320×240 screen, per [FREE-WILi advocate](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/04-free-wili.md)) learns classroom projector and TV remotes and "slays" standby vampires in empty rooms. It has a pixel-art hunter character UI designed in Figma at the screen's exact frame size. A live campus leaderboard runs on SpacetimeDB.

**Design hook:** a character-driven device UI plus a polished leaderboard. Wattson showed that an on-device character wins at MHacks [V].

---

## 7. Red flags, rival arguments, rebuttals

| Red flag / rival argument | Rebuttal |
|---|---|
| **"The prize is a LEGO set and swag."** True: about $23 direct EV, which is bottom tier. | Agreed. I'm arguing for an add-on, not a target. Entering costs zero and the work is reused everywhere (§4). |
| **"No rubric, no named judges, no requirement text."** True [V]. | Ask at the 5:30 PM Figma workshop. Meanwhile, design to the union of MHacks' usability definition and the peer Figma briefs (§1). |
| **"Half the room will tick this box."** Likely: 34–50% at peers [V]. | Most entrants won't have a linked design system or a design story. All the peer winners did [V §2]. |
| **"Design polish eats build time."** Real risk. | Cap the budget at 3.5 hours with one owner. Get the end-to-end demo working first and freeze the UI around 6 AM. |
| **"Your stack's agent tracks have no UI to design"** (Relay, Photon advocates). | Correct for chat-only builds. Add a companion surface (Sketch B), or lead with the SpaceX + Fetch.ai path (Sketch A). |
| **"Judged by an LLM can't see design."** | Possibly [U]. Put the design rationale and screenshots in the write-up. There's no downside. |
| **"Figma Make output looks generic."** | Use Make only to explore. Ship a custom token set. Figma for Edu explicitly rewards process over Make-only output [V]. |
| **Education verification may not clear by Sunday** [V "few days"]. | Starter is enough: 3 team files, prototypes, 20 MCP calls a month [V]. |
| **Hardware flip weakens it.** | Yes. It drops to "OK" (Sketch C keeps it alive). |
| **No designer on the team is confirmed.** | The peer winners' briefs say "No design experience required" [V]. Someone with front-end skills plus a token system is enough to beat box-tickers [I]. |

---

## 8. Scorecard

| Criterion | Score | One-line justification |
|---|---|---|
| Prize value | **2** | One $160 LEGO set plus merch bundles. Non-cash, can't be split, about $23 direct EV. |
| Win probability | **4** | A large pool (about 40–65 entrants [I]) of mostly shallow entries. A deliberate design owner gives roughly 15–20% for top 3 and 5–8% for 1st [I]. |
| Integration ease | **9** | No API or keys. Figma is free for students. About 3.5 hours. The only snag is the SheerID delay. |
| Stacking potential | **9** | Orthogonal to every track. It lifts usability and presentation scoring everywhere, and Figma MCP in Cursor feeds SpaceX. Friction only with chat-only agents and hardware. |
| Demo impact | **8** | Design is the first thing a judge sees in a 3-minute table pitch or a side-by-side comparison. |
| Fit with team preferences | **8** | Keeps SpaceX central, works with Relay or Capital One, and suits a web/mobile team. No confirmed designer. |

**Overall: about 6.5/10 as an add-on.** Enter it, make design one person's job for about 3.5 hours, and link the Figma file on Devpost. Never trade a working demo or a cash-prize integration for it.

---

## Sources
- MHacks 2026 Hacker Handbook (judging format, criteria, rules): https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af
- Handbook › Tracks & Prizes (Best Design prize text, all sponsor prizes, SpaceX/Notability/Relay/Photon text): https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5 (read through Notion's public `loadCachedPageChunk` API)
- Handbook › MHacks 26 Tracks: https://safe-banon-80d.notion.site/3e424ca0c81b802b86d4ebacf0cbfc0b
- MHacks 26 schedule (Figma workshop Sat 5:30 PM, Duderstadt 3336): https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365
- MHacks live site: https://www.mhacks.org/live
- MHacks site sponsor list (source): https://github.com/mhacks/dashboard/blob/main/components/landing/sections/Sponsors.tsx
- MDredd pairwise judging: https://github.com/mhacks/MDredd
- MHacks 2025 Devpost (criteria, prizes) and gallery: https://mhacks-2025.devpost.com/ · https://mhacks-2025.devpost.com/project-gallery
- MHacks 2024 Devpost: https://mhacks-2024.devpost.com/
- Figma Education: https://www.figma.com/education/
- Figma Education verification and plan contents: https://help.figma.com/hc/en-us/articles/360041061214-Verify-your-eligibility-for-Figma-for-Education
- Figma pricing: https://www.figma.com/pricing/
- Figma plans and features: https://help.figma.com/hc/en-us/articles/360040328273-Figma-plans-and-features
- Figma Make: https://www.figma.com/make/ · https://help.figma.com/hc/en-us/articles/31304412302231-Explore-Figma-Make
- Figma MCP server guide: https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Dev-Mode-MCP-Server
- Figma MCP rate limits: https://developers.figma.com/docs/figma-mcp-server/rate-limits-access/
- LEGO 21062 Trevi Fountain (Brickset): https://brickset.com/sets/21062-1/Trevi-Fountain
- HackDavis 2026 (Figma-sponsored Best UI/UX): https://hackdavis-2026.devpost.com/ · https://hackdavis-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=101832 · https://devpost.com/software/rekindle-koiq9s
- LA Hacks 2026 (Figma Make Challenge, Best UI/UX): https://la-hacks-2026.devpost.com/ · https://docs.google.com/document/d/1jEZ_NcL3acSJh5H2YwzfTYL8gAuj73k_Bsj9Y5uVWVg · https://la-hacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=101253 · https://la-hacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=101378
- LA Hacks 2026 winners: https://devpost.com/software/neighborfridge · https://devpost.com/software/gotrail · https://devpost.com/software/grouper-fr2h1q · https://devpost.com/software/accent-cdw2qi
- Hacklytics 2026 (Figma Make data viz): https://hacklytics-2026.devpost.com/ · https://hacklytics-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=97291 · https://devpost.com/software/the-last-human-internet · https://devpost.com/software/braceml
- Fetch.ai MHacks 2026 hackpack (15% UX & presentation): https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack
- MHacks precedents: https://devpost.com/software/wattson-5btsyd · https://devpost.com/software/signverse · https://devpost.com/software/declutttered-ai
- NASA data for sketches: https://power.larc.nasa.gov/docs/services/api/temporal/hourly/ · https://firms.modaps.eosdis.nasa.gov/api/map_key/
- Internal context: /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md · /Users/anvaytodkar/Code/mhacks/results/year-research/2024.md · /Users/anvaytodkar/Code/mhacks/results/year-research/2025.md · /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/04-free-wili.md

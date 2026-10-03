# Sponsor Track Advocate — Best Use of SpacetimeDB

## Prompt given (excerpt)
> You are the advocate for the sponsor track "Best Use of SpacetimeDB" at MHacks 2026. Research the sponsor's tech and how fast a team can integrate it, what its judges reward, prize value vs competition, expected value, how it stacks with the main/fun picks and other sponsors, 2–3 winning project sketches, honest red flags, and a 1–10 scorecard. Make the strongest honest case — an impartial judge will weigh your file against eleven other sponsor advocates.

---

## Core case

**SpacetimeDB is the best cash-per-competitor track at MHacks 2026 for a software team, but only if the team builds a multi-user project from the first hour.**

- **The money is real cash, $1,700 across three places**: $1,000, $500 and $200 ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5); Devpost lists the same amounts "in cash" ([MHacks 2026 Devpost](https://mhacks-2026.devpost.com/))). Only Fetch.ai pays more cash. SpacetimeDB's **2nd place ($500)** is worth more than most other sponsors' **1st place**.
- **The pool is small, and I measured it.** SpacetimeDB has sponsored prizes at two earlier college events, both at HopHacks (JHU). I counted the Devpost opt-ins myself:
  - **HopHacks Fall 2025:** 9 of 102 projects entered, and 4 of them won ([filter](https://hophacks-fall-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=89818)).
  - **HopHacks Fall 2026 (two weeks ago):** 11 of 87 entered, and 3 won ([filter](https://hophacks-fall-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105907)).
  - **Compare SpaceX at the same 2026 event:** "Make it Legendary" drew **31 of 87** entries for **one** keyboard prize ([filter](https://hophacks-fall-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105911)).
- **The tech fits a web/TypeScript team.** Since 2.0 (Feb 2026), the server module can be written in **TypeScript**. One command (`spacetime dev --template react-ts`) scaffolds a working React and SpacetimeDB app. The official repo also ships Cursor-ready agent skills. Cursor matters because the team's favorite sponsor, SpaceX, requires it.
- **It stacks.** It works with Sustainability, the judge's main-track pick. It also works with SpaceX: a scheduled procedure pulls NASA FIRMS satellite data, and Grok runs from inside the database. Relay, Fetch.ai and Photon agents become ordinary clients of the shared state. Judged by an LLM also stacks. It **conflicts only with Neon** (both are "the backend") and with any single-user idea.

**Verdict:** enter SpacetimeDB, and make it the backbone of the team's Sustainability project. Sketch A (§6) is a live multiplayer game on real satellite fire detections, so the judges' phones become players.

- **Expected value:** about **$200**, with roughly a 35% chance of placing at all.
- **Cost:** about **6 person-hours** of SpacetimeDB-specific work. Only about 3 of those are net-new, because the team needs a backend anyway.
- **Drop it** if the idea is single-user, or if the team commits to Neon.

---

## 1. The technology

### What SpacetimeDB is (October 2026)
- **One system replaces the backend.** It is a relational database that is also the server. You upload application logic as a "module"; clients connect over WebSocket, subscribe to queries, and get updates pushed live ([llms.txt](https://spacetimedb.com/llms.txt)).
- **Mature project.** Made by Clockwork Labs; about 25k GitHub stars ([repo](https://github.com/clockworklabs/SpacetimeDB)). BitCraft Online, an MMO, runs on it ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)).
- **Releases in 2026:**
  - **2.0, Feb 20, 2026:** TypeScript modules left beta. Templates arrived for React, Next.js, Vue, Svelte, Angular, Node and others. Maincloud got a **free tier**. Procedures (outbound HTTP calls from inside the module) became a headline feature ([2.0 release](https://github.com/clockworklabs/SpacetimeDB/releases/tag/v2.0.1)).
  - **Since then:** roughly a release every 2–3 weeks. The latest is v2.10.2 (Sep 29, 2026) ([releases](https://github.com/clockworklabs/SpacetimeDB/releases), [changelog](https://spacetimedb.com/changelog)).
  - **v2.8.2 (Aug 18, 2026):** an official Claude plugin with agent skills and an MCP server ([v2.8.2](https://github.com/clockworklabs/SpacetimeDB/releases/tag/v2.8.2)).

| Building block | What it does for a hack team | Source |
|---|---|---|
| **Tables** | Typed rows. `public: true` makes a table subscribable. Primary keys, unique constraints, auto-increment. | [React quickstart](https://spacetimedb.com/docs/quickstarts/react), [TS server skill](https://github.com/clockworklabs/SpacetimeDB/blob/master/skills/typescript-server/SKILL.md) |
| **Reducers** | The only way to write data. Each call is one atomic transaction, and the caller's identity is `ctx.sender`. | [React quickstart](https://spacetimedb.com/docs/quickstarts/react), [Functions](https://spacetimedb.com/docs/functions/) |
| **Subscriptions** | Clients subscribe to tables or filtered queries. Rows land in a local cache, with insert/update/delete callbacks. | [TS client SDK](https://spacetimedb.com/docs/clients/typescript) |
| **React hooks** | `SpacetimeDBProvider`, `useTable(query)` (returns rows and re-renders on change), `useReducer` (queues calls until connected). Reconnects automatically. | [TS client SDK](https://spacetimedb.com/docs/clients/typescript) |
| **Schedule tables** | Interval or one-shot timers that call a reducer or procedure. Used for game ticks, polling and expiry. | [Schedule tables](https://spacetimedb.com/docs/tables/schedule-tables) |
| **Procedures** | Run code with outbound HTTP via `ctx.http.fetch` (30 s default timeout, 180 s max). Database access goes through explicit `ctx.withTx`. Can be scheduled. | [Procedures](https://spacetimedb.com/docs/functions/procedures) |
| **HTTP handlers (beta)** | The module serves its own HTTP routes under `/v1/database/:name/route/...`, for webhooks. | [HTTP handlers](https://spacetimedb.com/docs/functions/http-handlers/) |
| **HTTP API** | Any language can call a reducer with `POST /v1/database/:name/call/:reducer` (JSON array of arguments) or run SQL with `POST .../sql`. | [HTTP database API](https://spacetimedb.com/docs/http/database) |
| **Auth** | Sign-in through SpacetimeAuth, Clerk, Auth0 or Better Auth. Row-level security and private tables. | [llms.txt](https://spacetimedb.com/llms.txt) |

### Access, cost, platforms
- **Install:**
  - macOS and Linux: `curl -sSf https://install.spacetimedb.com | sh`
  - Windows: a PowerShell one-liner, or WSL
  - Docker image also available
  ([install](https://spacetimedb.com/install))
- **Local development needs no account.** `spacetime dev` runs a local server ([React quickstart](https://spacetimedb.com/docs/quickstarts/react)).
- **Cloud (Maincloud):**
  - Log in with GitHub or Google (`spacetime login`), then `spacetime publish <db> --server maincloud`.
  - The dashboard has live logs, a SQL console and usage stats.
  - Free-tier databases pause when idle and resume in under a second ([Maincloud](https://spacetimedb.com/docs/how-to/deploy/maincloud)).
- **Free tier** ([pricing](https://spacetimedb.com/pricing)):
  - About 3,000,000 function calls, 12.5 GB egress and 1 GB storage per month.
  - Up to 20 projects × 5 databases.
  - Far more than a 24-hour demo needs (inference).
  - The page does not say whether a credit card is required. *Unverified.* Have one person sign up at kickoff to find out.
- **License:** Business Source License 1.1, which allows a single production instance and converts to AGPL in 2031 ([LICENSE](https://github.com/clockworklabs/SpacetimeDB/blob/master/LICENSE.txt)). No issue for a hackathon.

### MHacks 2026-specific resources
- **No SpacetimeDB workshop** is on Saturday's schedule. The 1–4 PM workshop slots go to FREE-WILi, Relay, Fetch.ai, FinchNode, Capital One, Salesforce and SpaceXAI ([schedule](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365)).
- **No credits or API keys** are mentioned in the track text ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). None are needed: local development and the Maincloud free tier cost nothing.
- **Whether Spacetime staff are on site is unverified.** The sponsor expo ran 11:30 AM at Pierpont ([schedule](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365)). Ask in the MHacks Discord sponsor channels ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)).
- **This is SpacetimeDB's first MHacks.** Neither the MHacks 2024 nor the 2025 Devpost page mentions it (my check of both pages).

### Learning curve: module languages and client SDKs
- **Server module languages:** Rust, C#, **TypeScript** (runs on V8) and C++ ([language support](https://spacetimedb.com/docs/intro/language-support)). A web team should use **TypeScript** and skip Rust.
- **Client SDKs:** TypeScript (browser, Node, Bun, Deno; quickstarts for React, Next.js, Vue, Svelte, Angular, Solid, TanStack, Remix, Astro), Rust, C#/Unity, and Unreal ([language support](https://spacetimedb.com/docs/intro/language-support), [llms.txt](https://spacetimedb.com/llms.txt)).
  - **No Python, Swift or Kotlin SDK.** A Python Fetch.ai agent or a native iOS app has to use the HTTP API or a TypeScript sidecar.
- **Official starter templates** (in the [repo's templates folder](https://github.com/clockworklabs/SpacetimeDB/tree/master/templates)):
  - `react-ts`, `nextjs-ts` and `chat-react-ts`.
  - `llm-chat-ts`: a SpacetimeDB-backed LLM chat ([README](https://github.com/clockworklabs/SpacetimeDB/blob/master/templates/llm-chat-ts/README.md)).
  - `money-exchange-react-ts`, which its README calls a small demo for a hackathon: private accounts plus atomic transfers between participants ([README](https://github.com/clockworklabs/SpacetimeDB/blob/master/templates/money-exchange-react-ts/README.md)).
  - Both the LLM-chat and money-exchange templates were added in early June 2026, the week of SpacetimeDB's own NYC Launchpad Hackathon ([commit history](https://github.com/clockworklabs/SpacetimeDB/commits/master/templates/money-exchange-react-ts), [Launchpad event](https://partiful.com/e/YxvEsJDZYLbJ9KkMt2bE)).
- **AI-assisted coding:**
  - The repo's `skills/` folder has SKILL.md references for the TypeScript server, TypeScript client, CLI and core concepts. Their metadata includes `cursor_globs`, so they are built to load as **Cursor** rules ([TS server skill](https://github.com/clockworklabs/SpacetimeDB/blob/master/skills/typescript-server/SKILL.md)).
  - A Spacetime engineer built an agar.io-style multiplayer game with Claude Code, a TypeScript module and a React client in about **30 minutes** ([blog](https://spacetimedb.com/blog/building-with-claude-code)). That is the vendor's own best case.
  - Spacetime admits Convex has invested more in LLM developer experience ([Convex post](https://spacetimedb.com/blog/why-you-should-choose-convex)).
- **The real conceptual shift:**
  - Reducers can't do I/O, and module code can't read clocks or random numbers except through `ctx`. Anything that calls the outside world goes in a procedure.
  - The client never "fetches". It subscribes and reacts.
  - About an hour to absorb for someone who knows React and SQL (inference). Rust is never required.

### What makes SpacetimeDB "core" rather than incidental
The sponsor wants it "meaningfully used, not just added on the side" ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). Here is my test, based on the brief and the winners in §2:

| Essential (wins) | Incidental (loses) |
|---|---|
| Several people or devices change **the same state** at once, and everyone sees it within a frame (rooms, votes, positions, bids, claims) | One user's data stored somewhere, which any database could do |
| **Server-authoritative logic** in reducers: scoring, matching, consensus, game ticks on a schedule table | All logic on the client, with SpacetimeDB used as a key-value store |
| **AI or agents act on the same world state** as humans (procedures call the LLM; agents call reducers over HTTP) | An LLM chat that only logs messages |
| The live sync can be **seen on a second screen** during judging | A dashboard refreshed by one user |

### Realistic integration time (my estimates, TypeScript stack)

| Step | Person-hours | Net-new compared with any backend? |
|---|---|---|
| Install CLI, `spacetime login`, `spacetime dev --template react-ts`, load the skills into Cursor | 0.5 | Yes |
| Learn tables, reducers, subscriptions and `useTable`/`useReducer` from the template and cheat sheet | 1.0 | Yes |
| Schema plus 6–10 reducers for the app's real logic | 2.0 | Mostly no; any backend needs this |
| Schedule table plus a procedure that polls an external API (FIRMS, grid data) and calls the LLM | 1.0 | Partly |
| Publish to Maincloud; test with 3+ phones on venue Wi-Fi; QR "join" flow | 0.5 | Yes |
| Agent bridge: Relay or Fetch.ai process calls reducers over HTTP or the Node SDK | 1.0 | Only if those sponsors are entered |
| **Total** | **≈ 6** | **≈ 3 net-new** |

**Add 2–3 hours of buffer** if nobody has used a subscription-style backend (Firebase, Convex, Supabase Realtime) before (inference).

**Evidence that this is feasible in 24 hours:**
- Geometry Core, a 2025 winner, listed SpacetimeDB under what it learned at the event ([Devpost](https://devpost.com/software/geometry-core)).
- All three 2026 HopHacks winners shipped multiplayer within the event ([TINAG](https://devpost.com/software/this-is-not-a-game-yet), [SlopRock](https://devpost.com/software/sloprock), [Iron Glove](https://devpost.com/software/iron-glove)).

### Known gotchas (each cited)
1. **Reducers must be deterministic, with no network.** Use `ctx.timestamp` and `ctx.random()`, never `Date.now()` or `Math.random()`. Do network I/O in procedures, *before* opening `ctx.withTx` ([TS server skill](https://github.com/clockworklabs/SpacetimeDB/blob/master/skills/typescript-server/SKILL.md), [Procedures](https://spacetimedb.com/docs/functions/procedures)).
2. **Procedure and HTTP-handler callbacks are synchronous.** No `async`/`await`. Lifecycle hooks must be `export const`, or they are **silently ignored**. The module's entry file must `export default` the schema ([TS server skill](https://github.com/clockworklabs/SpacetimeDB/blob/master/skills/typescript-server/SKILL.md)).
3. **Type footguns:**
   - `u64` columns are `bigint`, so auto-increment ids are inserted as `0n`.
   - Constructing an `Identity` from a string kills the module.
   - Use `ctx.sender`, not `ctx.identity`, for the caller ([TS server skill](https://github.com/clockworklabs/SpacetimeDB/blob/master/skills/typescript-server/SKILL.md), [troubleshooting](https://spacetimedb.com/docs/troubleshooting)).
4. **Stale bindings or version mismatch.** Regenerate the bindings (or just run `spacetime dev`). Keep the CLI and SDK versions aligned ([troubleshooting](https://spacetimedb.com/docs/troubleshooting)).
5. **AI tools know the old API.** 2.0 renamed APIs (there is a 1.0→2.0 migration guide), and the TypeScript package moved from `@clockworklabs/spacetimedb-sdk` to `spacetimedb` ([upgrade guide](https://spacetimedb.com/docs/upgrade/), [TS client SDK](https://spacetimedb.com/docs/clients/typescript)). An assistant without the official skills will likely write 1.x code (inference). Load the skills at minute 0.
6. **Phones can't reach `localhost`.** The Iron Glove team called getting phone data into a local SpacetimeDB a headache ([Iron Glove](https://devpost.com/software/iron-glove)). Publish to Maincloud early and point every client at `https://maincloud.spacetimedb.com` ([Maincloud](https://spacetimedb.com/docs/how-to/deploy/maincloud)).
7. **Beta features:** HTTP handlers are beta ([HTTP handlers](https://spacetimedb.com/docs/functions/http-handlers/)). C# and C++ procedures need unstable opt-in flags; TypeScript procedures don't ([Procedures](https://spacetimedb.com/docs/functions/procedures)). The SpacetimeDB MCP server does not work against Maincloud yet ([v2.8.2](https://github.com/clockworklabs/SpacetimeDB/releases/tag/v2.8.2)).
8. **No webhook framework or agent framework of its own yet**, per Spacetime's candid comparison with Convex ([Convex post](https://spacetimedb.com/blog/why-you-should-choose-convex)). HTTP handlers now partly cover webhooks.

---

## 2. What SpacetimeDB's judges reward

### The MHacks 2026 brief (verified)
**What the sponsor asks for** ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)):
- **Core requirement:** SpacetimeDB as the *core* real-time backend, with live shared state, multiplayer interaction, or instant sync between users, agents or systems.
- **Fits it names** (well beyond games): chat and community apps, collaborative tools, social experiences, AI agent coordination, live dashboards, trading and financial apps, auctions and marketplaces, shared simulations, multiplayer productivity tools, and stream or creator tools.
- **Specific examples it would be excited by:** a real-time portfolio sim, a prediction market, a collaborative trading game, a shared ops dashboard, a multi-user planning tool, and AI systems coordinating in a persistent world state.
- **Reference projects it links:** BitCraft, Pogly (a collaborative stream overlay), Elegon and Catacomb Crawlers.

**How judging works** ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)):
- Sponsors judge their tracks at the same time as the main panel, 12:30–2:30 PM Sunday.
- Teams get 3-minute windows.
- MHacks criteria include innovation, technical complexity, usability and presentation.

### Every verified SpacetimeDB-prize winner I could find
SpacetimeDB's sponsored college prizes on Devpost are HopHacks Fall 2025 and HopHacks Fall 2026. A Devpost search for "spacetimedb" returns only 34 projects in total, and most come from those two events ([Devpost search](https://devpost.com/software/search?query=spacetimedb), my query on 2026-10-03). I read every winner's page.

| Event and prize | Winner | What it was | How SpacetimeDB was used | Other prizes |
|---|---|---|---|---|
| HopHacks F25. Prize text: most polished app using SpacetimeDB. $500+$500 credits / $300+$300 / $100+$100 ([prizes](https://hophacks-fall-2025.devpost.com/)) | [BeatBoxing](https://devpost.com/software/beatboxing) | Multiplayer boxing rhythm game in the browser; your fists, tracked by webcam, are the controllers | Low-latency multiplayer state; Rust module | **Best Overall Hack** |
| HopHacks F25 | [Geometry Core](https://devpost.com/software/geometry-core) | Bullet-hell horde-defense game | C#/.NET module, learned at the event | — |
| HopHacks F25 | [HopQuest](https://devpost.com/software/hopquest-xaqf0y) | Campus scavenger hunt: scan **physical NFC cards**, live leaderboard, organizer dashboard | Syncs physical scans to every player live; hosted on Maincloud | — |
| HopHacks F25 | [Crack The Code](https://devpost.com/software/crack-the-code-ojk243) | Teaches prompt injection: players try to extract secrets from an AI | Rust module, OpenAI, React | — |
| HopHacks F26, "choose only one" track. $500 / $200 / $100 ([prizes](https://hophacks-fall-2026.devpost.com/)) | [This is Not a Game (Yet)](https://devpost.com/software/this-is-not-a-game-yet) | **Physical arcade cabinet:** yell a fake game title, AI generates it, you play it; a second screen in the room shows every press live | Session and press tables; start/tick/press/end reducers | MLH Snowflake |
| HopHacks F26 | [SlopRock](https://devpost.com/software/sloprock) | Rock Band played by webcam hand-tracking; create or join a band and jam | Rust module holds authoritative rooms, seats, hits, scores and catalog | — |
| HopHacks F26 | [Iron Glove](https://devpost.com/software/iron-glove) | **ESP32 + IMU glove** to fly Iron Man–style over real 3D cities (CesiumJS, Google Maps) | TypeScript module with server-authoritative drones ticking at 10 Hz; client interpolation | Also used **Grok/xAI** and ElevenLabs; entered SpaceX too |

**Non-winning opt-ins:**
- **2025:** ColdTrace (logistics alerts), CareNova (healthcare command center), Royal Wars, Blood and Iron, and one entry with no SpacetimeDB in its stack ([2025 filter](https://hophacks-fall-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=89818)).
- **2026:** Unseen Echoes, Dissect, Rosterd (agent infrastructure), Last Bit Standing, Chambara, Scraps (a food-rescue map), Bitcrushed and Poses ([2026 filter](https://hophacks-fall-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105907)).

**At SpacetimeDB's own Bengaluru hackathon (Midnight Moonshot, Sep 5–6, 2026):**
- The format was 24 hours; tracks included Agents and Multiplayer products; judging was working software only, no decks ([World Tour](https://worldtour.spacetimedb.com/)).
- Published builds include The Map Room and Redflow ([Map Room](https://github.com/Piyush-sahoo/spacetime-hacks), [Redflow](https://github.com/Aryan2193/redflow)). Neither README says it placed.
  - **The Map Room:** a live map of an AI agent exploring a codebase. Procedures fetch GitHub and call models, with no separate server.
  - **Redflow:** four LLMs debate in a scheduled-procedure state machine while humans intervene live.
- They show what Spacetime's own community builds in the "AI coordination" lane.

### Patterns (inference from 7 winners, so a small sample)
1. **Six of 7 winners are games or game-like.** The serious dashboards (ColdTrace, CareNova, Scraps) did not place. A Sustainability project therefore needs a **game or social mechanic**, not just a monitoring screen.
2. **Four of 7 have a physical or embodied input** (webcam fists, NFC cards, arcade cabinet, ESP32 glove), and every one shows **many clients reacting live**. This Is Not a Game (Yet) says outright that the moving second screen is its entire SpacetimeDB story.
3. **Server-authoritative logic is named explicitly** in the write-ups: reducers for ticks, scoring and rooms. Judges read Devpost write-ups, and the winners said exactly which tables and reducers they had.
4. **SpacetimeDB winners also win elsewhere** (Best Overall, Snowflake). A strong live demo helps every judge who walks by.
5. **Caveat:** both events are HopHacks, judged by the same sponsor in a "Gaming Track" or a choose-one track. The MHacks brief is much broader and lists finance, AI coordination and dashboards (verified above). So MHacks judges *may* weigh non-games more. Unverified.

---

## 3. Prize value and expected competition

**Prize value (cash; all figures are team totals):**

| Place | Cash | Per member (4) |
|---|---|---|
| 1st | $1,000 | $250 |
| 2nd | $500 | $125 |
| 3rd | $200 | $50 |

**Against the other sponsor prizes** (handbook and Devpost):
- **Fetch.ai** pays more cash: $1,250 / $750 / $500.
- **Capital One** pays $300 / $75 / $25 *per member*, or $1,200 / $300 / $100 for four. Its 1st beats SpacetimeDB's, but SpacetimeDB's 2nd and 3rd are better.
- **Neon** pays the same headline amounts ($1,000 / $500 / $100) in **AI Gateway credits**, not cash.
- **Photon** 1st is $400 cash plus credits.
- **SpaceX** and **Figma** pay in hardware or merchandise.

([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5), [MHacks 2026 Devpost](https://mhacks-2026.devpost.com/))

**Competition data I counted (Devpost prize filters, 2026-10-03):**

| Event | Prize | Opt-ins / projects | Winners | Share of opt-ins that won |
|---|---|---|---|---|
| HopHacks Fall 2025 | SpacetimeDB (Gaming Track) | 9 / 102 (9%) | 4 | 44% |
| HopHacks Fall 2026 | SpacetimeDB (choose-one track) | 11 / 87 (13%) | 3 | 27% |
| HopHacks Fall 2026 | SpaceX "Make it Legendary" | 31 / 87 (36%) | 1 ([WaterFlow](https://devpost.com/software/waterflow-41mrqd)) | 3% |
| HopHacks Fall 2026 | ElevenLabs | 30 / 87 (34%) | 1 | 3% |
| MHacks 2025 | Fetch.ai | 14 / 122 (11%), per the Neon advocate's count ([Neon file](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/05-neon-backend.md)) | — | — |

**MHacks 2026 estimate (inference):**
- **Pushes entries down:** no workshop, and an unfamiliar paradigm. Teams don't retrofit a database, so entries are limited to teams that design for it at hour 0.
- **Pushes entries up:**
  - Here sponsor tracks are additive ("submit to as many as apply"), unlike HopHacks 2026's choose-one rule.
  - The cash is twice HopHacks'.
  - The brief explicitly invites finance and AI projects, and FinTech teams may tag it for trading apps.
  - MHacks 2025 had 122 submissions ([MHacks 2025 gallery](https://mhacks-2025.devpost.com/project-gallery)).
- **Expected opt-ins:** about **10–18**, of which maybe **5–8** use SpacetimeDB as the real core. The rest are tags on projects where it plays a minor role.

**Expected competition: medium in head count, thin at the top.** That is three cash places for perhaps 5–8 serious entries.

---

## 4. Expected value

**My probability estimates (inference)** for a team that follows §1's "essential" column and demos on several phones:

| Scenario | P(1st) | P(2nd) | P(3rd) | P(any) | EV (cash) | SpacetimeDB-specific person-hours | EV per net-new hour |
|---|---|---|---|---|---|---|---|
| Incidental use (a database behind a single-user app) | ~2% | ~3% | ~5% | ~10% | ≈ $45 | 3 | ≈ $15/h |
| **Core use, multiplayer demo (recommended)** | **~12%** | **~12%** | **~11%** | **~35%** | **≈ $200** | **6 (≈3 net-new)** | **≈ $65/h** |
| Core use plus a game mechanic plus a physical input (winner pattern) | ~16% | ~14% | ~12% | ~42% | ≈ $255 | 8 | ≈ $50/h |

**Why these numbers:**
- At the two earlier events, 27–44% of opt-ins placed.
- I discount that for MHacks' larger and broader pool, and because judges may favor games.

**Compared with siblings:**
- **FREE-WILi advocate's independent estimate for this track:** about 10–15% chance of any place, EV ≈ $170–255 ([FREE-WILi file](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/04-free-wili.md)). That overlaps my range.
- **Others:** Neon realistic EV ≈ $130 in credits ([Neon file](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/05-neon-backend.md)). Photon native-first ≈ $80 ([Photon file](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/06-photon-imessage-agents.md)). Notability ≈ $80 ([Notability file](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/03-notability-trust-the-process.md)).
- **SpaceX:** prizes are keyboards. At HopHacks 2026 the same brand drew 36% of projects for one winner. Its EV in cash terms is likely below SpacetimeDB's (inference). It stays worth entering *alongside* SpacetimeDB because the team likes it, and §5 shows they combine.
- **Fetch.ai:** probably the only sponsor with clearly higher absolute EV. It also stacks with SpacetimeDB (§5).

**Bottom line:** SpacetimeDB is likely **top-3 among the 12 sponsor tracks on cash EV**, and top-2 on EV per net-new hour *when the project is multi-user anyway* (inference).

---

## 5. Stacking

**Recommended combination:**
- **Main:** Sustainability, as the judge recommended.
- **Fun tracks:** Judged by an LLM; add Dumbest Idea only if the game is actually funny.
- **Sponsors:** SpacetimeDB, SpaceX, Relay (or Photon), Figma, Notability, and Fetch.ai optionally.
- **Drop:** Neon.

| Track | Fit with SpacetimeDB | How, concretely |
|---|---|---|
| **Sustainability (main)** | Good, *if gamified* | Shared climate or grid world state, which matches the "shared simulations" and "live dashboards" in the brief. Add a game layer (§2 pattern 1). It also fits the "Digital Garden / build something that grows" theme ([mhacks.org](https://www.mhacks.org/), as verified by the main-track judge). |
| Actually Intelligent (AI) | Good | "AI systems coordinating in a persistent world state" is in the brief. Agents call reducers, and procedures call LLMs. But the AI track is the most crowded (verdict). |
| FinTech (flip) | **Best fit with the sponsor's own examples** | Portfolio sim, prediction market and trading game are named in the brief, and the money-exchange template exists. Nessie can fund wallets. More SpacetimeDB rivals in this lane (inference). |
| Beyond the Code (Hardware) | Good if 2+ devices | ESP32 or FREE-WILi devices act as players (Iron Glove, HopQuest precedent). Weak with a single device. |
| **Judged by an LLM** | **Strong** | SpacetimeDB gives a precise architecture to write up ("N tables · M reducers · K procedures, no server"). The Map Room's README does exactly this ([Map Room](https://github.com/Piyush-sahoo/spacetime-hacks)). |
| Dumbest Idea | Good if multiplayer | Room-wide absurd shared state is a natural live gag. Two 2026 winners were comedic (TINAG, SlopRock). |
| Useless AI | Neutral | Only works if the pointless AI is multiplayer. |
| **SpaceX "Make it Legendary"** | **Good** | **Cursor** is required, and SpacetimeDB's skills ship Cursor glob metadata. **Grok** can be called from a procedure (`ctx.http.fetch`); Grok Voice has a REST TTS endpoint ([xAI Voice](https://docs.x.ai/developers/model-capabilities/audio/voice)). **"Real space data goes in"** is met by a scheduled procedure ingesting NASA FIRMS satellite detections ([FIRMS](https://www.earthdata.nasa.gov/data/tools/firms), free [MAP_KEY](https://firms.modaps.eosdis.nasa.gov/api/map_key/)). Iron Glove entered both and used Grok with SpacetimeDB ([Iron Glove](https://devpost.com/software/iron-glove)). Whether SpaceX judges accept Earth-observation data is unverified (verdict). |
| **Relay** | **Good** | A Relay agent is your own always-on process that reads Relay's WebSocket and replies through its API ([Relay docs](https://docs.relayapp.im/llms.txt)). Write it in Node with the SpacetimeDB TypeScript SDK, so it *subscribes* to world state and calls reducers. Relay asks that each `event_id` be committed durably before acknowledging it; a SpacetimeDB table with a unique `event_id` column does exactly that. |
| Fetch.ai | Good | Python uAgents can't use an SDK, but can `POST /v1/database/:db/call/:reducer` ([HTTP API](https://spacetimedb.com/docs/http/database)). The agent becomes one more player in the shared state. |
| Photon (iMessage) | OK | Same as Relay. The SpacetimeDB brief lists chat/community apps. Pick Relay *or* Photon to save hours. |
| ElevenLabs | OK | All three 2026 SpacetimeDB winners also entered ElevenLabs ([2026 ElevenLabs filter](https://hophacks-fall-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105823)). It is redundant if Grok Voice already covers voice for SpaceX. |
| FREE-WILi | OK | A device as a "player" or sensor feeding reducers via a laptop bridge. |
| Figma | Good | A live multiplayer UI is visually demoable. |
| Notability | Neutral (free) | Plan the schema and reducers in Notability; that covers its requirement. |
| Capital One (Nessie) | Only in the FinTech flip | Nessie accounts fund a SpacetimeDB market (Sketch C). |
| FinchNode | Weak | A shared care-team board is possible but forced. |
| **Neon** | **Conflict** | Both want to be *the* backend. SpacetimeDB rejects side use, and Neon wants "fullest" use. Pick SpacetimeDB: its prize is cash, Neon's is credits, and live shared state is the demo. The Neon advocate agrees on "pick one" ([Neon file](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/05-neon-backend.md)). |

**Do I argue for a different main or fun choice?**
- **Main: no.** Sustainability works, provided the project has a multiplayer game layer.
- **The sponsor's own examples tilt toward FinTech.** So if the team takes the verdict's FinTech flip, SpacetimeDB gets *stronger*, not weaker.
- **That flip need not drop SpaceX.** A prediction market whose contracts settle on satellite data (Sketch C) is a coherent finance + real-space-data project. This partly answers the verdict's finding that no advocate found one.
- **Fun: Judged by an LLM** (agree). Add **Dumbest Idea** whenever the multiplayer layer gets a laugh. A live room-wide gag is the cheapest comic feature to ship.

---

## 6. Project sketches

### A. "Hotspot": a live multiplayer citizen-science game on real satellite fire detections (recommended)
**Tracks:**
- **Main:** Sustainability.
- **Sponsors:** SpacetimeDB, SpaceX, Relay, Figma, Notability; Fetch.ai optional.
- **Fun:** Judged by an LLM.

**How it works:**
- **Data in:** a schedule table runs a procedure every few minutes. It pulls NASA FIRMS VIIRS/MODIS fire detections ([FIRMS](https://www.earthdata.nasa.gov/data/tools/firms)) and upserts `detection` rows.
- **Join:** anyone in the room scans a QR code and joins a `team` on their phone.
- **Rounds:** each round shows one detection on a satellite map tile. Players race to classify it (wildfire / agricultural burn / industrial / false alarm). Reducers record votes atomically, compute consensus and streaks, and "confirm" clusters.
- **Big screen:** a world map where confirmed fires bloom in real time, plus a live leaderboard.
- **Grok:** a procedure asks Grok for a 15-second dispatch per confirmed cluster, which plays through **Grok Voice** TTS.
- **Relay:** a Relay agent people text ("fires near Traverse City?") subscribes to `detection` rows near the texter and pings them when a new cluster is confirmed.

**Why it wins SpacetimeDB:**
- It is literally "AI systems and humans coordinating in a persistent world state" plus a "shared ops dashboard" turned into a game.
- The judge's phone is a client.
- Every SpacetimeDB primitive is visible: schedule table, procedure, reducers, subscriptions and the HTTP API.

**Why it fits Sustainability:** crowd verification of satellite climate signals.

**Risks:**
- The FIRMS MAP_KEY has rate limits; pre-cache a global feed.
- Classification from imagery may be ambiguous (inference). Frame it as consensus, not ground truth.

**SpacetimeDB-specific hours:** about 6.

### B. "Grid Garden": floors compete to keep a shared garden alive by shifting energy to clean hours
**Tracks:**
- **Main:** Sustainability; on theme for "Digital Garden".
- **Sponsors:** SpacetimeDB, Relay or Photon nudges, Figma, Notability; FREE-WILi optional; SpaceX only if NASA POWER solar data and Grok Voice are used.
- **Fun:** Judged by an LLM, plus Dumbest Idea if the garden is ridiculous.

**How it works:**
- **Weather:** live Midwest grid carbon intensity (Electricity Maps zone `US-MIDW-MISO`, free tier limited to one zone) and satellite-derived NASA POWER solar irradiance ([POWER docs](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/)). Both sources are per the Sustainability advocate and **not re-checked by me** ([Sustainability file](/Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/01-main-sustainability.md)).
- **Points:** players log actions such as "laundry moved to 2 AM." Actions taken during clean hours earn more.
- **Optional hardware:** a FREE-WILi light sensor posts readings as an extra player.
- **Garden:** a scheduled reducer "ticks" the shared garden every 10 seconds. Each floor's plot grows or wilts on the big screen.
- **Relay:** the agent texts the group chat when the grid gets clean ("Floor 3, run the dishwasher now").

**Why it wins:**
- It follows the winner pattern of HopQuest's physical-to-live leaderboard.
- It hits the event theme dead-on.

**Risks:**
- Honor-system actions; mitigate with an LLM photo check.
- The space-data link to SpaceX is weaker than in A.

### C. "Carbon Pit": a live prediction market settled by satellites (the FinTech-flip sketch; also works under Sustainability)
**Tracks:**
- **Main:** FinTech (flip) or Sustainability.
- **Sponsors:** SpacetimeDB, Capital One (FinTech flip), SpaceX, Relay (text to trade), Figma.
- **Fun:** Judged by an LLM, plus Dumbest Idea with absurd contracts.

**How it works:**
- **Contracts:** the room trades play-money contracts such as "Will FIRMS detect more than N fires in California by noon?" or "Will MISO be cleaner at 6 PM than at 6 AM?"
- **Order book:** start from the official `money-exchange-react-ts` template ([README](https://github.com/clockworklabs/SpacetimeDB/blob/master/templates/money-exchange-react-ts/README.md)). Reducers match orders atomically, and prices tick on every phone.
- **Settlement:** a scheduled procedure fetches the real data at expiry and settles every position in one transaction.
- **FinTech flip:** wallets are seeded from Nessie mock accounts.
- **Voice:** Grok Voice acts as the auctioneer.

**Why it wins SpacetimeDB:** it is the brief's own "prediction market" and "collaborative trading game" (verified wording).

**Risks:**
- The most crowded SpacetimeDB lane, since FinTech teams will build trading apps (inference).
- Keep it play money only.
- Needs a non-budgeting framing; the verdict says money ideas saturate fastest.

**My ranking for this team:** A > B > C. A keeps SpaceX strongest, B is the safest theme play, and C is the right answer only if the team flips to FinTech.

---

## 7. Red flags, rival arguments, rebuttals

**Honest weaknesses:**
1. **All-or-nothing.** Use that is off to the side scores near zero. The decision has to be made at kickoff, and today is the event (hacking started 12 PM Oct 3 ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af))).
2. **Judges' observed taste is games plus physical input** (§2). A pure Sustainability dashboard probably loses; Scraps, a food-rescue map, didn't place at HopHacks 2026.
3. **Paradigm shift and fast-moving APIs** (gotchas 1–5). AI tools default to 1.x code, which costs time if the skills aren't loaded.
4. **No workshop, and on-site mentors are unverified.** Help comes from docs and Spacetime's Discord.
5. **No Python, Swift or Kotlin SDK.** Agents in those languages go through HTTP.
6. **It costs Neon.** Neon credits are lost if Neon was in the plan.
7. **Thin evidence base.** Winner data comes from 2 events, both at HopHacks.

| Rival argument | Strength | Rebuttal |
|---|---|---|
| **Fetch.ai:** "$2,500 cash pool beats $1,700, and agents are what the team builds anyway." | Strong | True on the headline. But these are not either/or: a Fetch.ai agent becomes a *player* via one HTTP call (§5). Enter both. |
| **Neon:** "Neon is the easy add-on; SpacetimeDB demands a rewrite." | Medium | SpacetimeDB *is* the backend from hour 0, so there's no rewrite. Its prize is cash against credits. Choose one; choose SpacetimeDB when live shared state is the product. |
| **SpaceX:** "The team's bias is SpaceX; don't spend hours elsewhere." | Medium | Sketch A serves both. Cursor, Grok and real space data all run *through* SpacetimeDB. SpaceX alone is a 1-in-31 lottery for keyboards (HopHacks 2026). |
| **Capital One:** "$300 a member beats $250 a member." | Medium | Only at 1st. SpacetimeDB pays $500/$200 at 2nd/3rd, against Capital One's $300/$100 team totals. Capital One also requires FinTech, while SpacetimeDB works in any main track. |
| **Relay:** "The SF trip outclasses $1,000." | Medium | Different currencies, and the two stack. The Relay agent is a SpacetimeDB client. |
| **"Learning a new database in 24 hours is reckless."** | Medium | TypeScript modules, one-command templates and Cursor-ready skills (§1). All 7 verified winners shipped within their events. Budget about 3 net-new hours. |
| **"Main-track judges don't care about your backend."** | True | That's why the sketches are good Sustainability projects first. The multi-phone demo raises usability and presentation scores with *every* judge ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af) criteria). |
| **"Single node, memory-bound, restrictive license."** (critiques in an [HN thread](https://news.ycombinator.com/item?id=49378933)) | Weak here | Irrelevant at hackathon scale. The free tier covers about 3M calls a month. |

**Demo tactics** (inference, from the winner pattern):
- Put a QR code on the first slide so judges join from their own phones.
- Keep a second screen visibly moving.
- Spend 10 seconds in the Maincloud dashboard's live logs or SQL console to *prove* the state lives in SpacetimeDB ([Maincloud](https://spacetimedb.com/docs/how-to/deploy/maincloud)).
- Record a fallback video before 12 PM Sunday.

---

## 8. Scorecard

| Criterion | Score | Justification |
|---|---|---|
| Prize value | **7** | $1,700 real cash across 3 places. 2nd ($500) beats most sponsors' 1st. Below Fetch.ai's pool and Relay's trip. |
| Win probability | **6** | Small, shallow pools before (9 and 11 opt-ins; 27–44% placed). But MHacks is bigger, the track is additive, and judges lean toward games. |
| Integration ease | **6** | TypeScript modules, `spacetime dev` templates and Cursor skills. But a real paradigm shift, and it must be core from hour 0 (≈6 h, ≈3 net-new). |
| Stacking potential | **7** | Clean with Sustainability, SpaceX, Relay, Fetch.ai, Photon, Figma, Notability, Judged by an LLM and Dumbest Idea. Conflicts with Neon; Capital One only in the FinTech flip. |
| Demo impact | **9** | Judges' phones become live clients and a second screen moves. That is the strongest "wow" available to a software team, and the stated winning formula. |
| Fit with team's stated preferences | **7** | Keeps Sustainability and the SpaceX bias, rewards web/AI skills, and pays cash. Requires committing to a multi-user idea now. |

---

## Sources
- MHacks 2026 Tracks & Prizes (Notion; full SpacetimeDB brief, all sponsor prizes): https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5
- MHacks 2026 Hacker Handbook (dates, judging, rules): https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af
- MHacks 26 schedule (Sat; no SpacetimeDB workshop): https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365
- MHacks 2026 Devpost (prize list "Best Use of Spacetime" $1,000/$500/$200 in cash): https://mhacks-2026.devpost.com/
- MHacks site (theme): https://www.mhacks.org/
- MHacks 2025 gallery (122 submissions): https://mhacks-2025.devpost.com/project-gallery
- SpacetimeDB docs home: https://spacetimedb.com/docs/
- SpacetimeDB llms.txt (doc index, product definition): https://spacetimedb.com/llms.txt
- React quickstart: https://spacetimedb.com/docs/quickstarts/react
- TypeScript client SDK reference: https://spacetimedb.com/docs/clients/typescript
- Functions overview: https://spacetimedb.com/docs/functions/
- Procedures: https://spacetimedb.com/docs/functions/procedures
- HTTP handlers (beta): https://spacetimedb.com/docs/functions/http-handlers/
- HTTP database API: https://spacetimedb.com/docs/http/database
- Schedule tables: https://spacetimedb.com/docs/tables/schedule-tables
- Maincloud deploy: https://spacetimedb.com/docs/how-to/deploy/maincloud
- Troubleshooting: https://spacetimedb.com/docs/troubleshooting
- Language support: https://spacetimedb.com/docs/intro/language-support
- 1.0→2.0 migration guide: https://spacetimedb.com/docs/upgrade/
- Install: https://spacetimedb.com/install
- Pricing (free tier): https://spacetimedb.com/pricing
- Changelog: https://spacetimedb.com/changelog
- GitHub repo: https://github.com/clockworklabs/SpacetimeDB
- Releases (2.0 notes, v2.8.2 Claude plugin, v1.6 TS modules, v1.7 `spacetime dev`, v1.10 procedures): https://github.com/clockworklabs/SpacetimeDB/releases · https://github.com/clockworklabs/SpacetimeDB/releases/tag/v2.0.1 · https://github.com/clockworklabs/SpacetimeDB/releases/tag/v2.8.2
- TS server skill (gotchas, Cursor metadata): https://github.com/clockworklabs/SpacetimeDB/blob/master/skills/typescript-server/SKILL.md
- Templates folder: https://github.com/clockworklabs/SpacetimeDB/tree/master/templates
- LLM chat template README: https://github.com/clockworklabs/SpacetimeDB/blob/master/templates/llm-chat-ts/README.md
- Money exchange template README: https://github.com/clockworklabs/SpacetimeDB/blob/master/templates/money-exchange-react-ts/README.md
- Money exchange template history: https://github.com/clockworklabs/SpacetimeDB/commits/master/templates/money-exchange-react-ts
- LICENSE (BSL 1.1): https://github.com/clockworklabs/SpacetimeDB/blob/master/LICENSE.txt
- Blog, multiplayer game in 30 minutes with Claude Code: https://spacetimedb.com/blog/building-with-claude-code
- Blog, "Why You Should Choose Convex Over SpacetimeDB": https://spacetimedb.com/blog/why-you-should-choose-convex
- Blog index: https://spacetimedb.com/blog
- HN discussion of a third-party technical review: https://news.ycombinator.com/item?id=49378933
- SpacetimeDB Midnight Moonshot (Bengaluru): https://worldtour.spacetimedb.com/
- SpacetimeDB Launchpad Hackathon (NYC Tech Week): https://partiful.com/e/YxvEsJDZYLbJ9KkMt2bE
- The Map Room (Midnight Moonshot build): https://github.com/Piyush-sahoo/spacetime-hacks
- Redflow (Midnight Moonshot build): https://github.com/Aryan2193/redflow
- HopHacks Fall 2025 (prize text): https://hophacks-fall-2025.devpost.com/
- HopHacks Fall 2025 SpacetimeDB opt-ins: https://hophacks-fall-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=89818
- HopHacks Fall 2026 (prize text, 281 participants): https://hophacks-fall-2026.devpost.com/
- HopHacks Fall 2026 SpacetimeDB opt-ins: https://hophacks-fall-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105907
- HopHacks Fall 2026 SpaceX opt-ins: https://hophacks-fall-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105911
- HopHacks Fall 2026 ElevenLabs opt-ins: https://hophacks-fall-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105823
- Winner pages: https://devpost.com/software/beatboxing · https://devpost.com/software/geometry-core · https://devpost.com/software/hopquest-xaqf0y · https://devpost.com/software/crack-the-code-ojk243 · https://devpost.com/software/this-is-not-a-game-yet · https://devpost.com/software/sloprock · https://devpost.com/software/iron-glove · https://devpost.com/software/waterflow-41mrqd
- Devpost project search for "spacetimedb" (34 projects): https://devpost.com/software/search?query=spacetimedb
- NASA FIRMS: https://www.earthdata.nasa.gov/data/tools/firms · MAP_KEY: https://firms.modaps.eosdis.nasa.gov/api/map_key/
- NASA POWER hourly API (via Sustainability advocate): https://power.larc.nasa.gov/docs/services/api/temporal/hourly/
- Electricity Maps MISO zone (via Sustainability advocate): https://app.electricitymaps.com/datasets?zone=US-MIDW-MISO
- xAI Grok Voice API: https://docs.x.ai/developers/model-capabilities/audio/voice
- Relay docs (agent runtime, event_id durability): https://docs.relayapp.im/llms.txt
- Sibling files cited: /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/03-notability-trust-the-process.md · /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/04-free-wili.md · /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/05-neon-backend.md · /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/06-photon-imessage-agents.md · /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/01-main-sustainability.md · /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md

# Sponsor Track Advocate — Best Use of Neon Backend

## Prompt given (excerpt)
> You are the advocate for the sponsor track "Best Use of Neon Backend" at MHacks 2026. Research the sponsor's tech and how fast a team can integrate it, what its judges reward, prize value vs competition, expected value, how it stacks with the main/fun picks and other sponsors, 2–3 winning project sketches, honest red flags, and a 1–10 scorecard. Make the strongest honest case — an impartial judge will weigh your file against eleven other sponsor advocates.

---

## Core case

**Neon costs almost nothing to enter, and it rewards work the team has to do anyway.** Any software project needs a database, login, file storage, somewhere to run an API or agent, and LLM calls. Neon now sells all five as one branchable backend. Its full backend went generally available about **two weeks before MHacks** (blog dated Sept 17, 2026; changelog entry Sept 18) ([GA post](https://neon.com/blog/neon-backend-is-ga), [changelog](https://neon.com/docs/changelog)). The track is named "Neon **Backend**", and its text says Neon "has a fleet of backend tooling from database to authentication" ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)).

*Inference:* that wording points to the new services. A team that uses Neon only as Postgres will look like every other opt-in. A team that uses **Auth + Functions + Object Storage + AI Gateway + branching as a visible product feature** should be in the top tier of a medium-sized, mostly shallow pool.

**The honest weakness is the prize.** It is **AI Gateway credits, not cash**: $1,000 / $500 / $100 ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)). They can only be spent on a paid Neon plan ([prepaid credits](https://neon.com/docs/ai-gateway/prepaid-credits)). Neon is a **good add-on and a poor reason to pick a project.**

**My verdict:** enter Neon with whatever software project the team builds under Sustainability. Spend about 3 extra hours making branching visible in the product. Don't enter it alongside SpacetimeDB, and drop it if the team flips to Hardware.

---

## 1. The technology

### What Neon is in October 2026
Neon (owned by Databricks) now calls itself "a complete set of cloud backend primitives built around Lakebase Postgres". The services are Lakebase Postgres, Managed Better Auth, Data API, Functions, Object Storage and AI Gateway ([llms.txt](https://neon.com/llms.txt)). One `neon.ts` file declares the whole backend, and `neon deploy` provisions it ([backend overview](https://neon.com/docs/get-started/backend-overview), [neon.ts](https://neon.com/docs/reference/neon-ts)). Branching a project copies the whole backend, not just the database ([GA post](https://neon.com/blog/neon-backend-is-ga)).

| Service | What it gives a hack team | On Free plan? | Source |
|---|---|---|---|
| **Lakebase Postgres** | Plain Postgres. pgvector, PostGIS and TimescaleDB are included on every plan. Scales to zero. | Yes. 100 projects, 1 GB per project, 100 CU-hours per project, 10 branches per project. | [pricing](https://neon.com/pricing) |
| **Branching / snapshots / reset-from-parent** | Instant copy-on-write clones of the data. Point-in-time restore. Schema diff between branches. | Yes (1 manual snapshot on Free) | [branching](https://neon.com/docs/introduction/branching), [plans](https://neon.com/docs/introduction/plans), [llms.txt](https://neon.com/llms.txt) |
| **Managed Better Auth** | Users and sessions in a `neon_auth` schema, compatible with RLS. Each branch gets its own auth. Ready-made UI components. Shared Google OAuth credentials for testing. Organization plugin. | Yes, up to 60k MAU | [auth overview](https://neon.com/docs/auth/overview), [hackathon FAQ](https://neon.com/faqs/best-backend-hackathon-weekend-project) |
| **Data API** | A PostgREST-compatible HTTP API with JWT and RLS, so the browser can query without a server | Yes | [Data API](https://neon.com/docs/data-api/overview) |
| **Functions** | Long-running Node.js 24 functions next to the database: HTTP, WebSockets, SSE, cron and upload triggers, `waitUntil` | Yes (10 active capacity-hours, 1M invocations) | [Functions](https://neon.com/docs/compute/functions/overview), [limits](https://neon.com/docs/compute/functions/reference/runtime-limits), [websockets](https://neon.com/docs/compute/functions/websockets) |
| **Object Storage** | S3-compatible buckets that branch with the data | Yes, 5 GB | [storage](https://neon.com/docs/storage/overview) |
| **Lakebase Search** | Vector, BM25 and hybrid search through Postgres extensions. Uses the same syntax as pgvector. | Not stated | [Lakebase Search](https://neon.com/docs/ai/lakebase-search) |
| **AI Gateway** | One Neon credential for many models through an OpenAI-compatible endpoint, plus embeddings | **No: paid plan plus prepaid credits** | [AI Gateway](https://neon.com/docs/ai-gateway/overview) |

### Which "AI Gateway" the prize credits are for
The prize is credit for **Neon's own AI Gateway**, not Vercel's or Databricks'. The track text names no other provider, and Neon now sells an "AI Gateway" product with prepaid credits ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5), [AI Gateway](https://neon.com/docs/ai-gateway/overview)). *Inference*, though the match is close. The facts from Neon's docs:
- **1 credit = $1**, billed at provider list price with **no markup**. Bought credits **expire after 12 months** ([prepaid credits](https://neon.com/docs/ai-gateway/prepaid-credits)). Whether prize credits follow the same 12-month rule is **unverified**.
- **The gateway needs a paid plan** (Launch or Scale). Launch is pay-as-you-go with **no monthly minimum** ([pricing](https://neon.com/pricing)). So the winning team adds a card and pays cents to a few dollars a month for a small project (*inference* from the listed rates).
- **Soft limits:** about 200k tokens per minute and **about $20/day of spend** ([prepaid credits](https://neon.com/docs/ai-gateway/prepaid-credits)). At that cap, $1,000 lasts at least 50 days.
- **Models (catalog as of today):** GPT-5.x family, Gemini 3.x, Grok 4.6, Kimi K3, GLM and Qwen open-weight models, image generation through the Responses API, and two embedding models (Qwen3-0.6B at $0.02 per million tokens) ([models](https://neon.com/docs/ai-gateway/models)). **Grok Imagine and Grok Voice are not in the catalog.** SpaceX's Grok requirement still has to be met with xAI directly.
- **Regions:** the gateway, Functions and Object Storage run only in us-east-1, us-east-2, eu-central-1 and ap-southeast-1 ([get started](https://neon.com/docs/ai-gateway/get-started)). Create the project in us-east-2 (Ohio).

**What it's worth to a student team (inference):** this team already uses AI APIs. $1,000 of GPT-5-mini or Gemini Flash-class inference covers LLM costs for many future hackathons and side projects. It is still non-cash, held in one org, and probably expires in 12 months. I value 1st place at **about $300–500 real**, 2nd at **about $200–300**, and 3rd at **about $75**.

### Signup, cost and access
- Free plan, no credit card ([pricing](https://neon.com/pricing)). `npm i -g neon && neon auth && neon init` sets up the CLI and agent skills ([llms.txt](https://neon.com/llms.txt)).
- `neon bootstrap --template …` scaffolds working examples. Relevant ones: `realtime-chat` (Functions + Postgres + Auth, Next.js), `ai-sdk` (Functions + Postgres + AI Gateway + Object Storage) and `mastra` (agent with Postgres memory) ([Functions templates](https://neon.com/docs/compute/functions/overview)).
- **Using the AI Gateway *during* the hack costs about $5 and a card** (Launch plan plus the $5 minimum credit purchase) ([prepaid credits](https://neon.com/docs/ai-gateway/prepaid-credits)). Neon offers a "$20 free credits" promo for paid features ([pricing](https://neon.com/pricing)), but trial and sponsored accounts can't buy gateway credits self-serve ([prepaid credits](https://neon.com/docs/ai-gateway/prepaid-credits)). Whether the promo unlocks the gateway is **unverified**. Ask the Neon rep whether they hand out event credits (**unverified** that they do).
- There are Neon plugins for **Cursor** and **Grok Bot** ([Cursor plugin](https://neon.com/docs/ai/ai-cursor-plugin), [Grok Bot plugin](https://neon.com/docs/ai/ai-grok-bot-plugin)). SpaceX requires Cursor and gives "bonus points" for planning with Grok Bot ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)), so the same tools serve both tracks.

### MHacks 2026-specific resources
- Neon is a listed sponsor on [mhacks.org](https://www.mhacks.org/).
- **No Neon workshop** appears on the Saturday or Sunday schedule. Saturday has FREE-WILi, Relay, Fetch.ai, FinchNode, Capital One, SpaceXAI, Figma, Salesforce and AWS sessions ([schedule Sat](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365), [schedule Sun](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=83169850)).
- I found no published Neon rubric, mentor list or event credits. Judging runs Sunday 12:30–2:30 PM, and sponsors judge their tracks during the same window ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)).
- Whether a Neon person judges on site is **unverified**. Ask in Discord or at the expo.

### Realistic integration time (one developer; my estimates)
| Piece | Hours | Notes |
|---|---|---|
| Postgres + ORM + connection string | 0.5 | Standard Postgres ([connect](https://neon.com/faqs/best-backend-hackathon-weekend-project)) |
| Managed Better Auth (Next.js + UI components + Google OAuth) | 1–1.5 | Shared OAuth credentials skip registering an app ([FAQ](https://neon.com/faqs/best-backend-hackathon-weekend-project)) |
| Functions (Hono API or webhook, `neon deploy`) | 1.5–2 | Node 24 only ([limits](https://neon.com/docs/compute/functions/reference/runtime-limits)) |
| Object Storage + upload trigger | 1 | S3 SDK ([storage](https://neon.com/docs/storage/overview)) |
| AI Gateway | 0.5 | Point the OpenAI SDK at the branch endpoint ([AI Gateway](https://neon.com/docs/ai-gateway/overview)), plus billing setup |
| Embeddings + pgvector / Lakebase Search | 1–1.5 | ([pgvector](https://neon.com/docs/extensions/pgvector), [Lakebase Search](https://neon.com/docs/ai/lakebase-search)) |
| **Branching as a product feature** (create, compare and discard branches through the API) | 2–3 | The part that looks like "fullest use" |
| **Gross total** | **about 8–10** | |
| **Net of backend work you'd do anyway** | **about 5–6** | **Best single estimate: 6 hours** |

### Known gotchas (each cited)
1. **AI Gateway:** paid plan, $5 minimum, credential needs the `ai_gateway:invoke` scope, credentials are bound to a branch lineage, and 429s come at the TPM or daily cap ([troubleshooting](https://neon.com/docs/ai-gateway/troubleshooting), [authentication](https://neon.com/docs/ai-gateway/authentication)).
2. **Auth: a frontend and backend deployed separately are "not yet supported"**, because sessions use HTTP-only cookies ([auth roadmap](https://neon.com/docs/auth/roadmap)). Build one Next.js (or TanStack) app, not a React SPA with a separate Express server. Auth is AWS-only ([auth overview](https://neon.com/docs/auth/overview)).
3. **Functions:** Node 24 only. 15-minute limits on time-to-first-byte, heartbeat and `waitUntil`. Can be evicted at any time. Limit of 100 concurrent invocations per account. Keep the `pg` pool small ([limits](https://neon.com/docs/compute/functions/reference/runtime-limits)). Python agents (Fetch.ai uAgents) run elsewhere and call Neon over HTTP or Postgres.
4. **Free-plan limits:** 10 branches per project (more cost $1.50/branch-month on paid). Compute scales to zero after 5 minutes and can't be turned off on Free ([pricing](https://neon.com/pricing)). *Inference:* wake the database before judges reach the table.
5. **New services:** the backend GA'd mid-September, and "Realtime is coming" but has not shipped ([changelog](https://neon.com/docs/changelog)). Expect rough edges and keep fallbacks: Vercel for Functions, provider keys for the gateway.

---

## 2. What Neon's judges reward

**No precedent was found.**
- I checked 96 Devpost pages for 2024–2026 college hackathons: TreeHacks, LA Hacks, HackNYU, PennApps, HackPrinceton, HackGT, HackHarvard, HackIllinois, Technica, BostonHacks and others, found through Devpost's hackathon API. **None listed a Neon prize** (my scan, 2026-10-03; method: `devpost.com/api/hackathons?search=<name>`, then the word "Neon" on each event page).
- Devpost's own hackathon search for "neon" returned no Neon-the-company events ([API](https://devpost.com/api/hackathons?search=neon)).
- Events not on Devpost (HackMIT, Hack the North, Cal Hacks) were not checked.
- *Inference:* MHacks 2026 may be one of Neon's first college-hackathon tracks since the backend launch, so nobody has a winning template to copy.

**Closest signals:**
- **Neon's 2024 DEV challenge** paid three winners $1,000 each, all for Neon starter kits. It was judged on clarity of instructions, developer experience, applicability and usability ([challenge](https://dev.to/challenges/neon), [winners](https://dev.to/devteam/congrats-to-the-neon-open-source-starter-kit-challenge-winners-247p)). Lesson: a clear README and architecture write-up count.
- **Neon features a hackathon-born project** (NephroCompass, built on the Data API) as a case study, with a personal "built for a problem I lived" story ([blog](https://neon.com/blog/the-transplant-story-that-sparked-a-hackathon-project)).
- **Neon's current messaging is "backend for agents" plus branching.** Examples: a branch for "every PR, preview, or agent session" ([GA post](https://neon.com/blog/neon-backend-is-ga)), snapshots as agent checkpoints ([branching for agents](https://neon.com/branching/branching-for-agents)), and replayable agents ([guide](https://neon.com/guides/replayable-ai-agents)).
- **The track text** rewards "high quality and functionality, while utilizing Neon to its fullest" across a "fleet of backend tooling from database to authentication" ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)).
- **MHacks' general rubric** is innovation, technical complexity, usability and presentation ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)).

**My "fullest use" ladder (inference from the above):**
| Level | What it looks like | Likely standing among Neon opt-ins |
|---|---|---|
| 0 | Neon as a connection string | The majority; forgettable |
| 1 | + Managed Better Auth (the track names authentication) | Common floor |
| 2 | + Functions / Object Storage / AI Gateway, declared in `neon.ts` | Rare (inference). Shows the new backend. |
| 3 | + **branching as a user-visible feature**: scenario forks, agent sandboxes, one-click demo reset | Very rare. This is the story Neon's own marketing tells. |
| 4 | + a polished product with real users or real data | The winner |

---

## 3. Prize value and expected competition

**Prize (face):** $1,000 / $500 / $100 in AI Gateway credits ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)). **Realistic team value:** about $300–500, $200–300 and $75 (see §1).

**Competition data I counted (Devpost prize-filter opt-ins, 2026-10-03):**
| Event | Prize | Opt-ins / projects |
|---|---|---|
| MHacks 2025 | MLH Auth0 | 6 / 122 (5%) ([filter](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90666)) |
| MHacks 2025 | Base44 | 8 / 122 (7%) ([filter](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90546)) |
| MHacks 2025 | MLH Cloudflare | 13 / 122 (11%) ([filter](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90667)) |
| MHacks 2025 | Fetch.ai (best use) | 14 / 122 (11%) ([filter](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90535)) |
| MHacks 2025 | AgentMail | 18 / 122 (15%) ([filter](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90540)) |
| MHacks 2025 | MLH Gemini | 47 / 122 (39%) ([filter](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90668)) |
| PennApps XXVI | MLH MongoDB Atlas | 17 / 85 (20%) ([filter](https://pennapps-xxvi.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90480)) |
| HackNYU 2025 | MongoDB Atlas | 28 / 154 (18%) ([filter](https://hacknyu-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=83552)) |
| LA Hacks 2025 | MLH MongoDB Atlas | 33 / 172 (19%) ([filter](https://la-hacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=85144)) |
| LA Hacks 2026 | MLH MongoDB Atlas | 69 / 306 (23%) ([filter](https://la-hacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=98555)) |
| HackPrinceton F25 / HackGT 12 | MLH Snowflake | 9 / 194 (5%); 10 / 276 (4%) ([filter](https://hackprinceton-fall-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=92860), [filter](https://hackgt-12.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90744)) |

**My estimate (inference):** MHacks had 122 projects in 2025 ([gallery](https://mhacks-2025.devpost.com/project-gallery)).
- Expect **about 10–20 Neon opt-ins (8–15%)**. That is below MongoDB's 18–23%, because MLH promotes MongoDB, Neon has no workshop, and the prize is credits. It is above Snowflake, because any app with a database qualifies.
- Of those, perhaps **2–5 go beyond plain Postgres**.
- **Expected competition: medium.** The pool is mid-sized, but the bar to reach the top tier is low.

---

## 4. Expected value

**Neon, for a team that hits ladder level 3 (my inferred odds):** P(1st) ≈ 20%, P(2nd) ≈ 15%, P(3rd) ≈ 15%.
- Face EV ≈ 0.20×$1,000 + 0.15×$500 + 0.15×$100 ≈ **$290**.
- Realistic EV ≈ 0.20×$400 + 0.15×$250 + 0.15×$75 ≈ **$130** (range about $90–180).
- Net-new effort is about 3 hours (mostly the branching feature), so roughly **$40 per hour**. It also lifts the main-track "technical complexity" score and gives the LLM judge something concrete to read.

**Honest comparison (prizes from [Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5); odds are my inference):**
| Track | Prize form | Rough realistic EV for a strong, fitting entry | Note |
|---|---|---|---|
| Fetch.ai ASI:One | **Cash** $1,250 / $750 / $500 | Higher than Neon | Separate submission agent, Agentverse registration; 14 opt-ins in 2025 |
| SpacetimeDB | **Cash** $1,000 / $500 / $200 | Higher than Neon, *if* real-time is core | Rejects "added on the side" use; heavier paradigm shift |
| Capital One Nessie | $300 gift card × each member | Similar to Neon | One winner; FinTech-leaning |
| Photon | $400 cash + $300 credits | Similar or lower | iMessage via Spectrum only |
| **Neon** | **Credits** $1,000 / $500 / $100 | **About $130** | **Cheapest to add, and stacks with nearly every software project** |
| SpaceX / Figma / Notability / FREE-WILi / Relay | Merch, hardware, trip | Mostly non-cash; Relay's trip is high on experience | |

**Bottom line:** Neon is **not** a top-EV track by prize alone. It earns its place because the marginal cost is low and it improves the project's main-track and LLM-judge score.

---

## 5. Stacking

| Pick | Fit with Neon | Why |
|---|---|---|
| **Sustainability (judge's pick)** | **Good** | Geo and time-series data suits Postgres plus PostGIS. Scenario branching makes a strong demo (Sketch A). |
| Actually Intelligent (AI) | **Best** | Agent sandboxes on branches, the AI Gateway, and memory in Postgres are exactly Neon's agent pitch ([branching for agents](https://neon.com/branching/branching-for-agents)). |
| FinTech | Good | Ledgers and audit logs suit Postgres, and branches work as "simulate before you commit". |
| Beyond the Code (Hardware) | Weak | The hardware advocate agrees "fullest use" isn't natural there. |
| **Judged by an LLM** | **Good** | A concrete architecture section (six services, branching) is easy for an LLM judge to parse and score. |
| Dumbest Idea / Useless AI | Neutral to weak | Neon judges on "high quality and functionality". |
| **SpaceX** | **Good** | Cursor plus Neon's Cursor plugin; Grok Bot plus Neon's Grok Bot plugin for the planning bonus ([plugin](https://neon.com/docs/ai/ai-grok-bot-plugin)). Grok Imagine renders go to Object Storage. Grok Imagine/Voice must still come from xAI directly. |
| **Relay** | **Good** | Relay requires committing each `event_id` to durable storage before acknowledging a webhook ([Relay docs](https://docs.relayapp.im/llms.txt)). That is a Postgres idempotency table behind a Neon Function, with model work in `waitUntil`. |
| Fetch.ai | Good | A Python agent on Agentverse reads and writes Neon over a Function endpoint or Postgres. |
| Capital One Nessie | Good | Cache and enrich thin Nessie mock data in Postgres. |
| ElevenLabs / FinchNode / Photon | Neutral to good | Audio in Object Storage; synthetic records in Postgres; message history. |
| Figma / Notability | Orthogonal | Free add-ons. |
| **SpacetimeDB** | **Conflict** | Both want to be *the* backend. SpacetimeDB rejects being "added on the side". Pick one: SpacetimeDB if live shared state is the product, Neon otherwise. |

**Recommended stack (it doesn't change the main/fun verdict):** Sustainability + Judged by an LLM + SpaceX + **Neon** + Relay or Fetch.ai + Figma + Notability. If the team flips to AI (no climate angle), Neon gets *stronger* (Sketch C). If it flips to Hardware, drop Neon.

---

## 6. Project sketches

### A. "Fork the City": satellite-driven what-if planner for Ann Arbor (Sustainability; SpaceX, Neon, Judged by an LLM, Figma, Notability; Fetch.ai optional)
This extends the Sustainability advocate's satellite planner. Hourly **Function cron triggers** load NASA POWER irradiance and FIRMS fire/smoke detections into Postgres, and **PostGIS** joins them to parcels.

The Neon hook is **scenario branching**. "Plant 500 trees on Packard" or "30% rooftop solar in Water Hill" each **creates a Neon branch from the baseline through the API**. The intervention runs as SQL on that branch, the app compares kWh/yr, CO₂ and canopy across branches side by side, and the user keeps or discards each one.
- Grok Imagine before/after renders go to **Object Storage**. An upload trigger writes metadata to Postgres and generates captions through the **AI Gateway**.
- The planner LLM and **embeddings** (Lakebase hybrid search over A2ZERO program text) also run through the gateway, so recommendations cite their sources.
- **Managed Better Auth** plus RLS stores each user's scenarios. Cap live scenarios at about 8 (Free allows 10 branches) or pay pennies on Launch ([pricing](https://neon.com/pricing)).

**Demo moment:** press "Fork the city", get a new branch in seconds, watch the numbers change, and show the branch list in the Neon console. **Why it wins Neon:** branching *is* the feature, and it uses 5–6 services.

### B. "Leftovers": a campus free-food rescue agent you text (Sustainability; Relay, Fetch.ai, Neon, Judged by an LLM; ElevenLabs optional)
Relay's own idea list includes "Food: dining halls, free food" ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)).
1. Student orgs text a photo of leftover trays to the Relay agent.
2. A **Neon Function** receives the webhook and commits the `event_id` to Postgres before acknowledging, as Relay requires ([Relay docs](https://docs.relayapp.im/llms.txt)).
3. The photo goes to **Object Storage**. An upload trigger calls a vision model through the **AI Gateway** to estimate portions and allergens.
4. **PostGIS** matches nearby students, who text "anything near BBB?". A cron trigger expires old posts and tallies food diverted (CO₂e with a published factor, cited in the write-up).
5. **Managed Better Auth** with the Organization plugin handles multi-tenant student orgs ([llms.txt](https://neon.com/llms.txt)).
6. **Branch reset-from-parent** gives a clean demo state for every judge ([changelog](https://neon.com/docs/changelog)).

**Trade-off:** no space data, so SpaceX drops out.

### C. "Mission Sandbox": a space-data agent that can't break your data (AI main; SpaceX, Relay, Fetch.ai, Neon, Judged by an LLM)
A voice and text agent (Grok Voice for SpaceX) answers questions over real space data (CelesTrak, launch history) loaded into Postgres. **Every agent session runs on its own Neon branch.**
- The agent may create tables and write analyses.
- The user sees a **schema/data diff** ([CLI diff](https://neon.com/llms.txt)), then keeps or discards the branch.
- Snapshots make any session **replayable** ([replayable agents](https://neon.com/guides/replayable-ai-agents)).
- SQL reasoning runs on Grok 4.6 or GPT through the **AI Gateway**. Functions host the tools and the Relay webhook.

This sketch is Neon's agent-platform pitch run as a product, so it is the strongest pure-Neon idea. It sits in the more crowded AI pool, though.

---

## 7. Red flags, rival arguments, rebuttals

**Red flags (honest):**
- **The prize is non-cash credits that need a paid plan.** Expiry terms for prize credits are unverified.
- There is no workshop, published rubric or confirmed on-site judge, and no hackathon precedent on Devpost.
- The services are only weeks past GA, region-limited, and Auth can't handle a separately deployed frontend and backend.
- Using the gateway during the hack costs about $5 and needs a card.
- Backends are invisible. Without a visible branching feature, the demo looks like any other app.

| Rival argument | Strength | Rebuttal |
|---|---|---|
| "Credits aren't cash; Fetch.ai and SpacetimeDB pay real money." | **Strong** | Agreed. Neon is an add-on, not a driver. It also stacks *with* Fetch.ai. |
| "SpacetimeDB is the better backend track." | Medium | Only if live shared state is core. SpacetimeDB rejects side use, and none of the Sustainability sketches is multiplayer. Choose one; never both. |
| "Every team uses a database, so the pool is huge." | Medium | Opt-ins for comparable infrastructure prizes at MHacks 2025 were 6–18 (§3). Most will be level 0–1, and the top tier is thin. |
| "Brand-new services will break mid-hack." | Medium | Postgres and Auth are the floor. Fallbacks: Vercel for Functions, S3 for storage, provider keys for the gateway. |
| "Neon features steal hours from the product." | Weak | Auth, storage, API hosting and LLM calls are needed anyway. Only branching-as-feature (about 2–3 h) is net-new, and it also scores technical complexity. |
| "Doesn't work with Hardware." | True | Then drop Neon. The current verdict is Sustainability. |

---

## 8. Scorecard

| Criterion | Score | One-line justification |
|---|---|---|
| Prize value | **4** | $1,000 / $500 / $100 face, but non-cash, single-org credits that need a paid plan; about $300–500 real for 1st. |
| Win probability | **6** | Medium pool (about 10–20 opt-ins, inferred), mostly shallow; but no precedent and unknown judges. |
| Integration ease | **8** | Postgres in 30 min, full fleet in about 6 net hours with familiar tools; minus the paid gateway, regions and Auth architecture limits. |
| Stacking potential | **8** | Backend for any software pick: Sustainability, AI, Relay, Fetch.ai, SpaceX tooling, Nessie. Conflicts with SpacetimeDB; weak with Hardware and joke tracks. |
| Demo impact | **4** | Backends are invisible; a scenario-fork or agent-sandbox UI brings it to 6. |
| Fit with team preferences | **7** | Keeps SpaceX, Relay and Capital One open and avoids FinTech; not a track the team named. |

**Overall: about 6/10.** It is a near-free add-on for any software project the team builds, worth it only with one visible branching feature.

**Do this at the event:**
1. Ask in Discord or at the expo who judges Neon, and whether they give out gateway credits.
2. Create the project in us-east-2 and scaffold with `neon bootstrap`.
3. Write a README section listing every Neon service and why it's used.
4. Wake the database before judging, and reset the demo branch for each judge.

---

## Sources
- MHacks 2026 Tracks & Prizes (Notion): https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5
- MHacks 2026 Hacker Handbook: https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af
- MHacks 2026 schedule (Sat / Sun): https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365 · https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=83169850
- MHacks site (sponsor list): https://www.mhacks.org/
- Neon docs index: https://neon.com/llms.txt
- Neon pricing: https://neon.com/pricing · Plans: https://neon.com/docs/introduction/plans
- Neon backend GA post: https://neon.com/blog/neon-backend-is-ga · Changelog: https://neon.com/docs/changelog
- AI Gateway: https://neon.com/docs/ai-gateway/overview · https://neon.com/docs/ai-gateway/prepaid-credits · https://neon.com/docs/ai-gateway/models · https://neon.com/docs/ai-gateway/get-started · https://neon.com/docs/ai-gateway/authentication · https://neon.com/docs/ai-gateway/troubleshooting
- Backend overview: https://neon.com/docs/get-started/backend-overview · neon.ts: https://neon.com/docs/reference/neon-ts
- Functions: https://neon.com/docs/compute/functions/overview · https://neon.com/docs/compute/functions/reference/runtime-limits · https://neon.com/docs/compute/functions/websockets
- Auth: https://neon.com/docs/auth/overview · https://neon.com/docs/auth/roadmap
- Data API: https://neon.com/docs/data-api/overview · Object Storage: https://neon.com/docs/storage/overview
- Branching: https://neon.com/docs/introduction/branching · https://neon.com/branching/branching-for-agents · https://neon.com/guides/replayable-ai-agents
- Search: https://neon.com/docs/ai/lakebase-search · https://neon.com/docs/extensions/pgvector
- Plugins: https://neon.com/docs/ai/ai-cursor-plugin · https://neon.com/docs/ai/ai-grok-bot-plugin
- Neon hackathon FAQ: https://neon.com/faqs/best-backend-hackathon-weekend-project
- Neon case study (hackathon-born project): https://neon.com/blog/the-transplant-story-that-sparked-a-hackathon-project
- Neon DEV challenge (2024): https://dev.to/challenges/neon · winners: https://dev.to/devteam/congrats-to-the-neon-open-source-starter-kit-challenge-winners-247p
- Devpost hackathon API (Neon search): https://devpost.com/api/hackathons?search=neon
- MHacks 2025 gallery: https://mhacks-2025.devpost.com/project-gallery
- MHacks 2025 opt-in filters: https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90666 · …=90546 · …=90667 · …=90535 · …=90540 · …=90668
- Peer opt-in filters: https://pennapps-xxvi.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90480 · https://hacknyu-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=83552 · https://la-hacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=85144 · https://la-hacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=98555 · https://hackprinceton-fall-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=92860 · https://hackgt-12.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90744
- Relay docs: https://docs.relayapp.im/llms.txt
- Team context: /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md

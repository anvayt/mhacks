# Sponsor Track Advocate — Agents in iMessage Using Photon

## Prompt given (excerpt)
> You are the advocate for the sponsor track "Agents in iMessage Using Photon" at MHacks 2026. Research the sponsor's tech and how fast a team can integrate it, what its judges reward, prize value vs competition, expected value, how it stacks with the main/fun picks and other sponsors, 2–3 winning project sketches, honest red flags, and a 1–10 scorecard. Make the strongest honest case — an impartial judge will weigh your file against eleven other sponsor advocates.

---

## 0. The case in brief

- **What Photon is.** Photon sells infrastructure for putting AI agents inside messaging apps. Its open-source TypeScript SDK, **Spectrum** (`spectrum-ts`, MIT licence), connects one agent server to iMessage, WhatsApp, Telegram and other apps. On iMessage, Photon runs the phone lines in its own cloud. **You don't need a Mac or an Apple ID**: you need a free Photon account, a `projectId`/`projectSecret` from the dashboard, and `npm install spectrum-ts` ([intro](https://photon.codes/docs/spectrum-ts/introduction), [getting started](https://photon.codes/docs/spectrum-ts/getting-started), [pricing](https://photon.codes/pricing)).
- **Requirement to qualify (verified):** "Projects must integrate with Photon's Spectrum framework and use Spectrum to connect their agent to iMessage to qualify for the prize" ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)).
- **The best evidence: a twin event a week ago.** DivHacks 2026 (Columbia, Sept 26–27) ran this exact track with the **identical prize table**: $400 + $300 credits + interview fast-track, and $200 + $100 credits. **29 of its 65 projects (45%) opted in.** The two winners were **Nook** (a walk-home safety agent that runs entirely in iMessage) and **News Next Door** (plain-language, multilingual local news by iMessage, built on Grok + ElevenLabs) ([DivHacks 2026](https://divhacks-2026.devpost.com/), [Photon filter](https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105999)).
- **Why take it.** It is the cheapest sponsor integration on the board, about **3 hours** to a working agent. It has the best demo moment: **the judge's own phone buzzes**. It stacks cleanly with the recommended **Sustainability** main track, the team's favourite sponsor **SpaceX** (Grok is a proven pairing with Photon), ElevenLabs, Neon and **Judged by an LLM**.
- **Why not make it the centrepiece.** Cash is small: $400 for 1st, $200 for 2nd. Competition is likely **high** because adding Photon to any agent project is cheap. And the free/Pro tiers **cannot do group chats**, which are the headline use case ("participate in human conversations"). One DivHacks team wrote: "Our Photon credits were Pro, not Business, so Unsaid can't sit inside a group chat" ([unsaid](https://devpost.com/software/unsaid-zm8w5v)).
- **My recommendation:** enter Photon as a **high-leverage secondary sponsor track** on top of Sustainability + SpaceX + Judged by an LLM. Make iMessage **the product's interface, not a notification channel**. If the team drops Relay, Photon should be the team's messaging surface. If the team keeps Relay, make Relay the primary messaging surface and add Photon only once the shared agent core works (§5).

---

## 1. The technology

### 1.1 What it is

| Item | Finding | Source |
|---|---|---|
| Company/product | Photon builds infrastructure to put agents "into messaging platforms where people already communicate". Spectrum launched April 21, 2026 | [Introducing Spectrum](https://photon.codes/blog/introducing-spectrum) |
| SDK | `spectrum-ts`, TypeScript 5+, Node.js or Bun. Four primitives: Message, Space, User and Platform provider. All providers feed a single `for await (const [space, message] of app.messages)` loop | [Getting started](https://photon.codes/docs/spectrum-ts/getting-started) |
| iMessage modes | **Cloud** (`@spectrum-ts/imessage`) runs over Photon-managed lines via gRPC. **Local** (`@spectrum-ts/imessage-local`) reads the Messages database on a Mac you control, and needs Full Disk Access | [Connection & routing](https://photon.codes/docs/spectrum-ts/providers/imessage/connection-and-routing) |
| Native features (cloud) | DMs, typing indicators, tapbacks, threaded replies, edits/unsend, effects, **polls**, **chat backgrounds**, voice notes, contact cards, read receipts | [Intro](https://photon.codes/docs/spectrum-ts/introduction), [polls](https://photon.codes/docs/spectrum-ts/content/polls), [backgrounds](https://photon.codes/docs/spectrum-ts/providers/imessage/messaging-features/chat-backgrounds), [voice](https://photon.codes/docs/spectrum-ts/content/voice) |
| Location | The advanced kit can send Find My location-share requests and watch live updates. Photon says the "Share Location" button "now renders 99% of the time … on every plan" | [Locations](https://photon.codes/docs/advanced-kits/imessage/locations), [Photon blog](https://photon.codes/blog) |
| Management API | `https://spectrum.photon.codes`, HTTP Basic auth (`projectId:projectSecret`), 5 req/s per project | [API intro](https://photon.codes/docs/api-reference/introduction), [rate limit](https://photon.codes/docs/api-reference/rate-limit) |
| Traction | `spectrum-ts`: 1,888 GitHub stars and 238 forks, last push 2026-09-29; npm v12.10.1 with 250,219 downloads in the week ending 2026-10-01. The site's "4.6k" badge is probably org-wide stars (inference: the top repos sum to about 4.8k) | [GitHub API](https://api.github.com/repos/photon-hq/spectrum-ts), [org repos](https://api.github.com/orgs/photon-hq/repos), [npm downloads](https://api.npmjs.org/downloads/point/last-week/spectrum-ts) |
| AI-coding help | Photon publishes "Spectrum skills" for AI coding tools. That helps with SpaceX's "must use Cursor" rule | [Intro](https://photon.codes/docs/spectrum-ts/introduction), [skills.sh](https://www.skills.sh/photon-hq/skills/spectrum) |

### 1.2 Access, cost and plan limits (this is where the gotchas are)

| Plan | Price | Lines | Users | Groups | Source |
|---|---|---|---|---|---|
| Free | $0 | **Shared pool**: each user is texted from a number "they have never received a message from before" | **Up to 10** | **No** group creation or group events | [Pricing](https://photon.codes/pricing), [routing](https://photon.codes/docs/spectrum-ts/providers/imessage/connection-and-routing) |
| Pro | $25/mo | Shared pool | Up to 100 | No | [Pricing](https://photon.codes/pricing) |
| Business | $250/line/mo | **Dedicated** number | Unlimited (with Auto Scale) | **Full group messaging API** | [Pricing](https://photon.codes/pricing) |
| Local (open source) | $0 | Your own Mac and Apple ID | n/a | "Limited". You can send into existing group chats, but there is no group creation, tapbacks, typing indicators or backgrounds | [Pricing](https://photon.codes/pricing), [connection & routing](https://photon.codes/docs/spectrum-ts/providers/imessage/connection-and-routing), [imessage-kit](https://photon.codes/docs/opensource/imessage-kit) |

Further constraints:
- **Allowlist.** Free and Pro shared lines message only registered users. Anyone else gets `Target not allowed for this project` ([troubleshooting](https://photon.codes/docs/spectrum-ts/troubleshooting/imessage)). **Judges must be added as users before they can try the agent.** The fix is an API call: `POST /projects/{id}/users` with `type: "shared"`, then the public `GET /users/{userId}/redirect` endpoint, which "redirects to the appropriate messaging platform … via SMS deep link" ([OpenAPI spec](https://spectrum.photon.codes/openapi/json)). That makes a 1-hour "scan QR → enter number → Messages opens" onboarding page possible. On Free, the team's 4 phones leave 6 judge slots; users can be deleted to free slots.
- **Hackathon credits.** At DivHacks, Photon gave a promo code for **one month of Pro free** ([DivHacks 2026](https://divhacks-2026.devpost.com/)). **Whether MHacks gets a code is unverified.** The MHacks Tracks page mentions none, and Photon has **no workshop on the MHacks schedule** ([schedule sheet](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365)). Photon is listed as a sponsor on [mhacks.org](https://www.mhacks.org/).
- **Quotas:** 5,000 outbound messages per server per day, and 50 new conversations per line per day ([connection & routing](https://photon.codes/docs/spectrum-ts/providers/imessage/connection-and-routing)). Neither matters for a demo.
- **Runtime:** cloud iMessage uses Node-compatible gRPC, so edge or browser-worker isolates "are not supported yet". Run it on a laptop, Render, Railway or Fly, or use the webhook mode with Hono or Express ([troubleshooting](https://photon.codes/docs/spectrum-ts/troubleshooting/imessage), [webhooks](https://photon.codes/docs/webhooks/overview)).

### 1.3 Realistic integration time (my estimate; Photon-specific work only)

| Step | Hours | Note |
|---|---|---|
| A teammate creates a Photon account and project, copies credentials, and adds the 4 team phones as users | 0.3–0.5 | The team does this itself. If iMessage is registered to an email instead of a number, use [debug.photon.codes](https://debug.photon.codes) to find the right handle ([troubleshooting](https://photon.codes/docs/spectrum-ts/troubleshooting/imessage)) |
| Hello-world DM loop, cloud provider | 0.5 | Photon's own Render template claims "about 10 minutes" to a Codex agent in iMessage ([blog](https://photon.codes/blog)) |
| Wire in the LLM, `space.responding()` typing indicator, tapback handling and memory (Neon) | 1.5–2 | The agent logic itself is separate and shared with the main-track work |
| Judge QR onboarding (`POST /users` + redirect) | 1 | Avoids the allowlist failure in front of judges |
| **Core total** | **≈ 3 (range 2.5–4)** | |
| Optional: real group chat via `@spectrum-ts/imessage-local` on a teammate's Mac | +2–3 | Needs Full Disk Access and a Mac kept awake on venue Wi-Fi. Fewer features |

### 1.4 Known gotchas (verified unless marked)
1. **No groups on Free/Pro cloud.** This is the biggest trap. Design the core as DMs, or use the local Mac path for the group demo.
2. **Allowlist.** An unregistered judge is rejected. Build the onboarding page.
3. **Report Junk.** Apple shows a "Report Junk" banner on first messages from unknown numbers. Design inbound-first and keep links and media out of the first message ([deliverability](https://photon.codes/docs/best-practices/imessage-deliverability)).
4. **Android judges** get SMS/RCS fallback ([pricing](https://photon.codes/pricing)). Tapbacks arrive as text such as `Loved "…"`, which a DivHacks team had to normalise ([prepr](https://devpost.com/software/prepr-ik9ret)).
5. **SDK churn.** The SDK is at major version 12, and local iMessage moved to its own package (`imessage.config({ local: true })` no longer compiles) ([troubleshooting](https://photon.codes/docs/spectrum-ts/troubleshooting/imessage)). AI code generators may emit stale APIs, so load the Spectrum skill into Cursor.
6. **Chat backgrounds** need the cloud provider and may not show to a group member Apple treats as "unknown" ([backgrounds](https://photon.codes/docs/spectrum-ts/providers/imessage/messaging-features/chat-backgrounds)).
7. **Using raw `imessage-kit` instead of Spectrum would not qualify.** The rule says Spectrum. Whether the *local* Spectrum provider qualifies is my inference: it is Spectrum, but confirm with Photon.

---

## 2. What Photon's judges reward

### 2.1 Photon's own brief
- MHacks text (verified): agents that "naturally participate in human conversations … AI companions, multi-agent systems, or other experiences that understand social context, persist context across interactions, and seamlessly integrate AI into everyday communication" ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)).
- The DivHacks version of the same brief is more explicit about what Photon wants: AI as "a being that lives with us", "trusted to act with taste". "Build agents that don't merely assist, but participate" ([DivHacks 2026](https://divhacks-2026.devpost.com/)).
- Photon's customer stories point the same way: a college-campus matchmaker over iMessage (Ditto), finance actions with confirmation cards (Flip), and an email agent that texts you first (Slashy) ([Photon blog](https://photon.codes/blog)). These are **proactive, conversational products with no app to install**.

### 2.2 The only public winners (DivHacks 2026, n = 2; Devpost doesn't show which placed 1st)

| Winner | What it does | Why it plausibly won (my reading) |
|---|---|---|
| [**Nook**](https://devpost.com/software/nook-r37zlo) | "Walks you home, right from iMessage." Setup happens in one thread. The agent watches a live Find My feed, stays silent when the walk looks normal, and checks in when it looks off (detour, late, location goes quiet). **Tapbacks are the controls**: 👎 uneasy, ❓ call me, ‼️ alert. It escalates to calls and the user's emergency contact | iMessage *is* the product. It uses native affordances (tapbacks, location, voice), behaves proactively but with restraint, persists personal context ("a stop that's normal for you stays quiet"), and has a real stake (safety) |
| [**News Next Door**](https://devpost.com/software/news-next-door) | Plain-language, multilingual local news and zoning updates. Users subscribe, ask and translate in iMessage. Grok (xAI) summarises; ElevenLabs reads aloud | Clear social good (immigrant communities). The agent is the access channel for people who wouldn't install an app. **Built on Grok via xAI**, so it is a ready template for a SpaceX + Photon stack |

### 2.3 Patterns among the 27 other entrants (inference from project pages)
- iMessage used as a notification bolt-on did not win. Examples: Pricey ("Texting: An iMessage bot through Photon"), and BlindSpot, whose own write-up says "phone delivery verification is pending" ([Pricey](https://devpost.com/software/pricey-wy80ar), [BlindSpot](https://devpost.com/software/blindspot-x87p4j)).
- A good group-chat agent with polite @mention etiquette ([Key-o](https://devpost.com/software/keyo)) won a *main* track but not Photon. A good interface alone is not enough without a compelling "participates" story.
- At HackWashU, which had no Photon prize, one team only tested through Spectrum's **terminal** provider ([Same Moon](https://devpost.com/software/same-moon)). Under MHacks' rule, that would likely not count as connecting to iMessage (inference).

**What to build to:** (1) the whole loop happens inside a thread with no app; (2) at least two native affordances that carry meaning (tapbacks as input, polls, location, voice notes, chat background); (3) proactive but restrained behaviour, meaning the agent knows when *not* to talk; (4) memory that changes behaviour over time; (5) a real stake.

---

## 3. Prize value and expected competition

### 3.1 Prize value (team of 4)
| Place | Listed | Photon's own valuation | Realistic cash equivalent (my estimate) |
|---|---|---|---|
| 1st | $400 cash + $300 Photon credits + fast-track to final interview round | "$700" ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)) | **≈ $550–600**: $400 cash, about $50–75 for the credits (worth something only if the project lives on; $300 is about 12 months of Pro), and about $100 for the fast-track |
| 2nd | $200 cash + $100 credits | "$300" | **≈ $220** |

**Fast-track value: unverified.** Photon's /careers page returns 404 and I found no public job listing ([photon.codes/careers](https://photon.codes/careers)). It is worth real money only to a teammate who wants a role at an early-stage infra startup. Signs that it is a live, growing company: 86 public repos, an org created Sept 2025, and active weekly releases ([org](https://api.github.com/orgs/photon-hq)). Funding, headcount and pay are not verified.

### 3.2 Expected competition: **high**
- **Twin-event data (verified):** at DivHacks 2026, Photon drew 29 of 65 submissions. That **tied SpaceXAI (29)**, beat Capital One Nessie (8) and Ripple (14), and trailed only MLH Gemini (32) ([all](https://divhacks-2026.devpost.com/submissions/search), [Photon](https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105999), [SpaceX](https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105135), [Capital One](https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105134)).
- **Adjusting for MHacks (inference):** DivHacks had an on-site Photon workshop ("Build a Live iMessage AI Agent with Photon") and a free-Pro promo code. MHacks has neither on its public pages, has 12 sponsor tracks instead of 5 sponsor challenges, and has Relay competing for "text an agent" projects. I estimate **15–25% opt-in**, which is **roughly 20–40 entries** if MHacks gets 130–180 submissions (MHacks 2025 had 122 ([verdict file](/Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md)); the site advertises "1,000+ student builders" ([mhacks.org](https://www.mhacks.org/))).
- **The serious pool is much smaller:** most opt-ins are agents with an iMessage bolt-on (§2.3). I estimate 5–10 serious, native-first entries.

---

## 4. Expected value

| Scenario | P(1st) | P(2nd) | EV (cash-equiv.) | Photon-specific hours | EV per extra hour |
|---|---|---|---|---|---|
| Bolt-on (iMessage as notifier) | ~3% | ~4% | ≈ $26 | 1–2 | ≈ $15/h |
| **Native-first entry (recommended)** | **~10%** | **~10%** | **≈ $80** | **≈ 3–4** | **≈ $20–25/h** |
| Photon as the main sponsor focus, with real group chat via a local Mac | ~14% | ~12% | ≈ $105 | 6–7 | ≈ $16/h |

All probabilities are my estimates, anchored on 2 prizes, ~20–40 entrants and a ~5–10 serious tier.

**Honest comparison with other sponsor tracks (inference; their advocates hold the details):**
- **Higher headline value:** Fetch.ai ($1,250/$750/$500 cash), SpacetimeDB ($1,000/$500/$200 cash), Capital One ($300 per member = $1,200 for four; 8/65 opt-in at DivHacks), Neon ($1,000 in credits) and Relay (SF trip) ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)).
- **Photon's EV is below median in absolute dollars**, with competition about as heavy as SpaceX's.
- **Its case is marginal EV per hour plus demo spillover.** If the team is already building an agent (SpaceX/Grok, Fetch.ai and Relay all push it there), Photon costs about 3 hours. The judge's phone buzzing raises presentation scores with *every* judge, including the main-track panel, whose criteria include "usability, and presentation quality" ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)). That spillover is the part of the case I can't put a number on, and it is the reason to include Photon.

---

## 5. Stacking

| Track | Fit with Photon | Why |
|---|---|---|
| **Sustainability (main, recommended)** | **Good** | Behaviour change is a messaging problem: nudges, shared goals, timing. The "Digital Garden: build something that grows" theme ([mhacks.org](https://www.mhacks.org/)) maps onto an iMessage **chat background that grows** (Sketch A) |
| Actually Intelligent (main) | Native | But it is the most crowded pool (verdict). Photon doesn't need the AI track; it needs an agent |
| Beyond the Code (main) | OK | A sensor alerts a group chat (DivHacks' Night Owl paired a Raspberry Pi with Photon ([Night Owl](https://devpost.com/software/barn-owl-vm9n3s))). FREE-WILi can play the same role |
| FinTech (main) | Natural but off-preference | Photon's own customer Flip does money in iMessage ([blog](https://photon.codes/blog)). At DivHacks, unsaid paired Photon with Nessie and won Capital One. Split-the-bill needs groups, which means Business |
| **Judged by an LLM (fun)** | **Excellent** | A rubric-shaped README and a measured result cost nothing extra |
| Dumbest Idea / Useless AI (fun) | Good | A group-chat persona is the classic comic format. Enter only if the comedy really ships (verdict) |
| **SpaceX "Make it Legendary"** | **Strong** | Grok + Photon is proven (News Next Door, GlassLedger ([GlassLedger](https://devpost.com/software/glassledger-rzjmy0))). **Grok Imagine images become iMessage chat backgrounds or attachments**; satellite data supplies the content. Cursor is required, and Photon's skills help Cursor |
| ElevenLabs | Strong | Native iMessage **voice notes** via `voice()` ([voice](https://photon.codes/docs/spectrum-ts/content/voice)). Both DivHacks Photon winners used ElevenLabs |
| Neon | Strong | Postgres is the obvious store for "persist context across interactions" |
| Fetch.ai ASI:One | Medium | The same agent core can be registered on Agentverse, but it is a second surface to polish |
| **Relay** | **Conflict (soft)** | Same idea: "text/call your agent". Relay requires its app ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)); Photon's pitch is "no app". One agent core with two thin adapters is possible (Spectrum's `definePlatform` supports custom surfaces ([intro](https://photon.codes/docs/spectrum-ts/introduction))), but the 3-minute pitch can sell only one surface. **Pick one primary** |
| SpacetimeDB | Weak–medium | Possible as shared group state, but the sponsor wants it to be "core" |
| Figma, Notability | Free adds | No conflict |
| Capital One, FinchNode | Domain-dependent | Only with a finance or health story |

**Recommended stack (one project):** Sustainability + Photon + SpaceX + ElevenLabs (optional) + Neon (optional) + Judged by an LLM (+ Notability/Figma as free adds). This agrees with the verdict's main and fun picks, so I see no reason to argue for a different main track.

---

## 6. Winning project sketches

### A. "Grove": a household chat whose garden grows on clean sunshine (Sustainability · Photon · SpaceX · Neon · Judged by an LLM)
- **What:** an iMessage agent for a dorm suite or shared house. Each morning it reads **NASA POWER** satellite-derived solar data for Ann Arbor. The API is live with no key: I pulled Sept 20–26, 2026 daily irradiance, source FLASHFLUX ([NASA POWER](https://power.larc.nasa.gov/api/temporal/daily/point?parameters=ALLSKY_SFC_SW_DWN&community=RE&longitude=-83.74&latitude=42.28&start=20260920&end=20260926&format=JSON)). It texts first, but only in the morning: "Sunniest window is 1–3 PM. Who's doing laundry or charging? ❤️ to claim."
- **Native affordances:** tapbacks claim slots; a **poll** picks chores ([polls](https://photon.codes/docs/spectrum-ts/content/polls)); every shifted load "grows" the household garden, which a **Grok Imagine** render then sets as the **chat background** ([backgrounds](https://photon.codes/docs/spectrum-ts/providers/imessage/messaging-features/chat-backgrounds)); a Sunday **voice note** recap comes from ElevenLabs or Grok Voice.
- **Memory:** it learns who always ignores midday nudges and stops pinging them (Neon).
- **Groups:** on Free it runs as parallel DMs with shared garden state. For the demo, an optional **local-Mac group chat** shows the household view.
- **Demo moment:** a judge scans the QR code, is texted, hearts a slot, and the background changes on their phone within about 30 s.
- **Judged by an LLM:** the README reports measured kWh shifted in a simulated week against a no-nudge baseline.

### B. "Smoke Signal": a wildfire and smoke check-in agent, modelled on Nook (Sustainability/climate resilience · Photon · SpaceX · ElevenLabs)
- **What:** an agent for families or friend groups. It watches **NASA FIRMS** satellite fire detections (MODIS/VIIRS; free MAP_KEY ([Earthdata FIRMS](https://www.earthdata.nasa.gov/data/tools/firms), [FIRMS API](https://firms.modaps.eosdis.nasa.gov/api/))) near each member's location, using a Find My share request ([locations](https://photon.codes/docs/advanced-kits/imessage/locations)).
- **Behaviour:** silent by default. When a plume is upwind it checks in: "Fire 40 km NW, smoke likely tonight. 👍 if you're set with masks and filters, ❓ for a plan." No reply means one follow-up, then it notifies the person's chosen contact.
- **Extras:** a Grok Imagine plume card; ElevenLabs voice notes in the member's language.
- **Why it wins:** it copies the winning pattern exactly (Nook: proactive, restrained, tapback-driven, location-aware, real stakes) and adds satellite data for SpaceX.
- **Risk:** Michigan has few fires in October. Demo with a replay of real archived detections, labelled as a replay.

### C. "Leftover Launch": campus free-food rescue by text (Sustainability · Photon · Neon or SpacetimeDB · Judged by an LLM; the Relay-compatible variant)
- **What:** event hosts text "20 pizzas, BBB 2nd floor, until 3 PM". The agent alerts nearby subscribers, inbound-first (students join through a QR code at the dining hall).
- **Mechanics:** a ❤️ claims a portion and live counts update; a poll handles pickup slots; it tracks kg of food diverted.
- **Fit:** Relay's own idea list includes "🍽️ Food: dining halls, free food" ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). This sketch can therefore share one agent core across Photon and Relay if the team insists on both.
- **Trade-off:** it loses SpaceX, which has no space-data angle here.

**My pick:** A for the team's stated stack (SpaceX bias plus the "Digital Garden" theme). B if the team wants the safer "proven pattern" bet with Photon's judges.

---

## 7. Red flags, the best counterarguments, and rebuttals

| Counterargument (rival advocate) | Strength | Rebuttal |
|---|---|---|
| "$400 cash is among the smallest cash prizes. Fetch.ai, SpacetimeDB and Capital One pay 2–3× more." | **Strong, true** | Agreed. That is why Photon is a *secondary* track. It costs about 3 hours on top of an agent the team is already building, and its demo effect helps every other judge too |
| "45% opt-in at DivHacks means a lottery." | Strong | Most opt-ins are bolt-ons (§2.3). The winners show a clear rubric (native affordances, proactive restraint, stakes) that a disciplined team can aim at. My estimate is ~10% each for 1st and 2nd, not 7% |
| "The headline use case, group chats, isn't on the free tier." | **Strong, true** | Build DM-first, as winner Nook did. Its whole loop ran in one thread with the user plus an emergency contact. Optionally show a real group through the local Mac provider (+2–3 h). Ask Photon at the 11:30 AM sponsor expo ([schedule](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365)) whether hackathon teams can get a Business line |
| "Photon has no workshop at MHacks. Judges may be remote and judge from Devpost." | Medium (unverified either way) | Write the Devpost page and video so they work without a live demo: a screen recording of a real phone. Ask in the MHacks Discord ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)) |
| "Relay offers a trip to SF and overlaps Photon. Pick Relay." | Medium | Relay's prize is bigger as an experience, but judges must use the Relay app. Photon reaches judges in the app already on their phone. If the team stays with Relay, enter Photon only after the core is done; never split the pitch |
| "The allowlist will break the live demo." | Medium | Solved with `POST /users` + `/redirect`, about 1 hour ([OpenAPI](https://spectrum.photon.codes/openapi/json)). Pre-register judges' numbers at the table |
| "SDK churn: v12, renamed packages." | Low–medium | Pin the version and load Photon's Spectrum skill into Cursor. The docs are unusually complete, with an LLM-ready dump ([llms-full.txt](https://photon.codes/docs/llms-full.txt)) |
| "The fast-track interview is worthless." | Medium | It's worth something only to one teammate who wants a Photon role, and its value is unverified. I count it at $100, not $300 |
| "iMessage excludes Android judges." | Low | SMS/RCS fallback works, minus tapbacks. Demo on a team iPhone |

---

## 8. Scorecard (1–10)

| Criterion | Score | Justification |
|---|---|---|
| Prize value | **4** | $600 total cash across two places. 1st is worth about $550–600 realistically; credits and fast-track are soft |
| Win probability | **4** | About 20–40 entrants and only 2 prizes, but a native-first entry clears most of a bolt-on field (~10% each for 1st and 2nd) |
| Integration ease | **8** | `npm install` with free cloud lines, no Mac or Apple ID, about 3 h. Lost points for the allowlist, no groups on Free and Node-only runtime |
| Stacking potential | **8** | Pairs cleanly with Sustainability, SpaceX (Grok), ElevenLabs, Neon and Judged by an LLM. Real conflict only with Relay |
| Demo impact | **9** | The judge's own phone buzzes, they react with a tapback, and the chat background changes live. Nothing else on the board is this personal |
| Fit with team preferences | **6** | Not on the shortlist, but it fits the SpaceX bias and the Sustainability verdict. It competes with Relay, which the team is considering |

**Bottom line:** a cheap, high-impact add-on, not a jackpot. Enter it if the project has an agent, which the recommended stack does. Build iMessage-native from the first hour. Decide Photon vs Relay as the primary surface by noon.

---

## 9. Action items for Saturday morning
1. At the **11:30 AM sponsor expo** (Pierpont Connector Hall) or on Discord, ask Photon three things: whether there is a hackathon promo code (DivHacks got one month of Pro free), whether a Business line or group access is available, and whether `@spectrum-ts/imessage-local` qualifies ([schedule](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365)).
2. By about 1 PM, one teammate gets a hello-world DM working on cloud lines, with all 4 phones registered as users.
3. Build the judge onboarding QR before midnight.
4. The Devpost page and video show a real phone, never the terminal provider.

---

## Sources
- MHacks 2026 Tracks & Prizes (Photon text and prize valuation; retrieved through Notion's public page API): https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5
- MHacks 2026 Hacker Handbook (judging, sponsors evaluate in parallel, Discord): https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af
- MHacks 26 schedule (no Photon workshop; sponsor expo 11:30 AM): https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365
- MHacks site (Photon listed as sponsor; "1,000+ student builders"; Digital Garden theme): https://www.mhacks.org/
- Main/fun verdict (MHacks 2025 had 122 projects; Sustainability recommendation): /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md
- Spectrum introduction: https://photon.codes/docs/spectrum-ts/introduction
- Spectrum getting started: https://photon.codes/docs/spectrum-ts/getting-started
- iMessage connection & routing (line model, quotas, groups): https://photon.codes/docs/spectrum-ts/providers/imessage/connection-and-routing
- Inbound group events (dedicated line only): https://photon.codes/docs/spectrum-ts/providers/imessage/messaging-features/inbound-group-events
- Chat backgrounds: https://photon.codes/docs/spectrum-ts/providers/imessage/messaging-features/chat-backgrounds
- Polls: https://photon.codes/docs/spectrum-ts/content/polls
- Voice notes: https://photon.codes/docs/spectrum-ts/content/voice
- Locations (advanced kit): https://photon.codes/docs/advanced-kits/imessage/locations
- iMessage deliverability: https://photon.codes/docs/best-practices/imessage-deliverability
- iMessage troubleshooting (allowlist, runtime, local package): https://photon.codes/docs/spectrum-ts/troubleshooting/imessage
- imessage-kit (local, macOS, groups): https://photon.codes/docs/opensource/imessage-kit
- Webhooks overview: https://photon.codes/docs/webhooks/overview
- API reference intro and rate limit: https://photon.codes/docs/api-reference/introduction , https://photon.codes/docs/api-reference/rate-limit
- Spectrum OpenAPI spec (create user, redirect): https://spectrum.photon.codes/openapi/json
- Full docs dump: https://photon.codes/docs/llms-full.txt
- Pricing: https://photon.codes/pricing
- Introducing Spectrum: https://photon.codes/blog/introducing-spectrum
- Photon blog (Render 10-minute template, location reliability, customer stories): https://photon.codes/blog
- Photon careers (404): https://photon.codes/careers
- Debug line: https://debug.photon.codes
- Spectrum skills: https://www.skills.sh/photon-hq/skills/spectrum
- GitHub: https://github.com/photon-hq/spectrum-ts , https://api.github.com/repos/photon-hq/spectrum-ts , https://api.github.com/orgs/photon-hq , https://api.github.com/orgs/photon-hq/repos
- npm downloads: https://api.npmjs.org/downloads/point/last-week/spectrum-ts
- DivHacks 2026 (identical Photon prize, promo code, workshop): https://divhacks-2026.devpost.com/
- DivHacks 2026 submission counts: https://divhacks-2026.devpost.com/submissions/search , Photon https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105999 , SpaceX https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105135 , Capital One https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105134
- Photon winners: https://devpost.com/software/nook-r37zlo , https://devpost.com/software/news-next-door
- Other Photon entrants cited: https://devpost.com/software/unsaid-zm8w5v , https://devpost.com/software/keyo , https://devpost.com/software/pricey-wy80ar , https://devpost.com/software/blindspot-x87p4j , https://devpost.com/software/glassledger-rzjmy0 , https://devpost.com/software/barn-owl-vm9n3s , https://devpost.com/software/prepr-ik9ret , https://devpost.com/software/same-moon
- NASA POWER API (verified live): https://power.larc.nasa.gov/api/temporal/daily/point?parameters=ALLSKY_SFC_SW_DWN&community=RE&longitude=-83.74&latitude=42.28&start=20260920&end=20260926&format=JSON
- NASA FIRMS: https://www.earthdata.nasa.gov/data/tools/firms , https://firms.modaps.eosdis.nasa.gov/api/

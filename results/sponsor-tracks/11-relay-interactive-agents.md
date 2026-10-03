# Sponsor Track Advocate — Interactive Agents (Relay)

## Prompt given (excerpt)
> You are the advocate for the sponsor track "Interactive Agents (Relay)" at MHacks 2026. Research the sponsor's tech and how fast a team can integrate it, what its judges reward, prize value vs competition, expected value, how it stacks with the main/fun picks and other sponsors, 2–3 winning project sketches, honest red flags, and a 1–10 scorecard. Make the strongest honest case — an impartial judge will weigh your file against eleven other sponsor advocates.

---

Tags: **[V]** I verified it at the linked source on 2026-10-03. **[I]** It is my inference. **[U]** I could not verify it. I used no 2020 material.

## 0. The case in brief

- **What Relay is.** Relay is an iOS messenger for AI agents: "the simplest way to talk to your agents." Developers connect any backend to it, and people text, call and video chat with the agent in the Relay app [V] ([docs](https://docs.relayapp.im/llms.txt), [App Store](https://apps.apple.com/us/app/relay-agent-messenger/id6789704419)). It is made by **Companion, Inc.** [V] ([relayapp.im](https://relayapp.im)).
- **Who Advait is.** Advait Paliwal founded Companion [V] ([Inside Higher Ed](https://www.insidehighered.com/news/tech-innovation/artificial-intelligence/2026/02/26/agentic-ai-can-complete-whole-courses-now)). He is 22, left Brown's CS master's in 2024, and built "Einstein," the viral and controversial agent that did Canvas coursework in February 2026 [V] (same source; [Futurism](https://futurism.com/artificial-intelligence/ai-agent-canvas-homework)). He also co-founded YouLearn, which his site says has "2M+ users," and lists Friday, which it says is "Backed by Y Combinator" [V, his own claims] ([advaitpaliwal.com](https://www.advaitpaliwal.com/experience)). He writes most of Relay's docs and SDK pull requests himself [V] ([Relay-Docs PRs](https://github.com/RelayMessenger/Relay-Docs/pull/288)).
- **The decisive finding: Relay's MHacks workshop hands you two other sponsors' requirements.** Relay committed a `cookbook/mhacks-workshop` to its SDK repo early today (03:50–05:48 UTC) [V] ([README](https://raw.githubusercontent.com/RelayMessenger/Relay-SDK/main/cookbook/mhacks-workshop/README.md), [commits](https://api.github.com/repos/RelayMessenger/Relay-SDK/commits?path=cookbook/mhacks-workshop)). It takes four copy-paste prompts in any coding agent to get a character you **text and video call**, built on **Grok Imagine** (portrait plus looping 9:16 call videos), Grok for text and calls, and an **ElevenLabs** voice. SpaceX requires Cursor plus "Grok Imagine or Voice API" [V] ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). Relay supports Cursor [V] ([Cursor integration](https://docs.relayapp.im/integrations/cursor.md)). So one build can qualify for Relay, SpaceX's tooling rule and ElevenLabs. No other sponsor's onboarding does this.
- **Integration is the cheapest on the board for what you get.** The baseline (text plus call plus video) takes about **1.5–2 hours** through the workshop. A distinctive version takes about **4 hours** of Relay-specific work (§1.4).
- **The prize is an experience, not cash.** 1st is "A trip to San Francisco, a week at the Relay house, and Exclusive Relay Hoodie + Stickers + Eye Masks for each member." 2nd is the merch. Both get "a shoutout on Advait's X" [V] (handbook; [Devpost](https://mhacks-2026.devpost.com/)). Nominal value is about $2.5–4.2k for four people; I put the realistic cash-equivalent at about **$1.0–1.5k** [I] (§3). The real upside is a week with a founder whose company is hiring-stage small.
- **Competition will be high in count and thin at the top.** The workshop makes the template entry nearly free, so expect **20–50 entries** [I]. I expect only about 5–10 of them to go beyond "a character I can call" [I].
- **Red flags are real.** Relay is iOS-only (iOS 26+). It is brand-new: app v1.0 on July 25, GitHub org created July 26. Its API breaks almost daily. And **the App Store build I could see (v1.1, Sep 20) does not mention calls** (§7).
- **Recommendation.** Make Relay the team's **agent surface**, in the stack *Sustainability + Judged by an LLM + Relay + SpaceX + ElevenLabs*, with Notability as the free extra. This is Sketch A, "Ground Control." Do not also pitch Photon in the same demo. At the 1 PM workshop, settle the four open questions in §9.

---

## 1. The technology

### 1.1 What it is

| Item | Finding | Source |
|---|---|---|
| Product | An iPhone/iPad messenger where people talk to many agents "like you're texting a friend": messages, photos, files, voice notes, group chats, discovery by username, sharing by link or QR [V] | [App Store](https://apps.apple.com/us/app/relay-agent-messenger/id6789704419) |
| Maker | Companion, Inc. ("© 2026 Companion Inc."). Its LinkedIn page says founded 2025, **1 employee** [V] | [relayapp.im](https://relayapp.im), [LinkedIn](https://www.linkedin.com/company/getcompanionai), [companion.ai](https://companion.ai/) |
| Developer API | REST at `https://api.relayapp.im/v1`, Agent Token auth, about 25 typed webhook/WebSocket events. Covers messages, group chats, calls (voice and video), attachments, payments (Stripe), location, ratings, forms, buttons and rich cards [V] | [docs index](https://docs.relayapp.im/llms.txt) |
| SDKs/CLI | `@relaymessenger/sdk` (TypeScript, v0.5.0) and `relaymessenger` (Python). The CLI is `npx relaymessenger` (v0.1.17). MIT licence [V] | [SDK docs](https://docs.relayapp.im/live/sdks.md), [npm CLI](https://registry.npmjs.org/relaymessenger), [GitHub](https://api.github.com/repos/RelayMessenger/Relay-SDK) |
| Runtimes | One-command connectors for Claude Code, **Cursor**, Codex, VS Code, Gemini CLI and others. Also Vercel Chat SDK, Cloudflare, MCP, **Pipecat**, **LiveKit** and an **ElevenLabs** bridge [V] | [Integrations](https://docs.relayapp.im/integrations/index.md) |
| Calls | The agent answers by joining the call's WebRTC room within **32 seconds** of `call.created`; the packages handle SDP/ICE/TURN. An agent can also **call the person** if they added it [V] | [Calls](https://docs.relayapp.im/calls/index.md), [Call a person](https://docs.relayapp.im/calls/call-a-person.md) |
| Video | The agent publishes its own camera track from any frame source (looping video, a Simli live avatar, a renderer), up to 1080p30. It can also **read the person's camera** frame by frame for vision [V] | [Video calls](https://docs.relayapp.im/calls/video.md), [Avatars](https://docs.relayapp.im/calls/avatars.md) |
| Rive | Since 2026-10-01, a `.riv` file on the agent's card is drawn on the phone during calls and driven live (lip-sync visemes, triggers) [V] | [Rive](https://docs.relayapp.im/calls/rive.md), [changelog](https://docs.relayapp.im/changelog.md) |
| Grok recipes | Official cookbook: **Grok Voice** answers calls via Pipecat. A Grok chat agent sends **Grok Imagine** pictures and 6-second videos [V] | [Pipecat › Grok](https://docs.relayapp.im/integrations/pipecat.md), [cookbook](https://github.com/RelayMessenger/Relay-SDK/tree/main/cookbook) |
| Traction | GitHub org created 2026-07-26; Relay-SDK has 2 stars. npm `@relaymessenger/sdk` had 15,605 downloads in the week to Oct 1, and the CLI 8,393 (likely including CI) [V] | [org repos](https://api.github.com/orgs/RelayMessenger/repos?per_page=100), [npm SDK](https://api.npmjs.org/downloads/point/last-week/@relaymessenger/sdk), [npm CLI](https://api.npmjs.org/downloads/point/last-week/relaymessenger) |

### 1.2 Access and cost
- **Signup:** install the app, then `npx relaymessenger@latest login` (browser OAuth). `connect` or `agents create` makes an organization-owned agent and stores the token privately [V] ([Quickstart](https://docs.relayapp.im/start/quickstart.md), [Create an agent](https://docs.relayapp.im/agents/create-agent.md)). Team seats are free [V] ([Organization](https://docs.relayapp.im/console/organization.md)).
- **Price:** the app is free [V] ([App Store](https://apps.apple.com/us/app/relay-agent-messenger/id6789704419)). I found **no developer pricing page and no usage fees** in the docs. The only fee is 5% on payments [V] ([Payments](https://docs.relayapp.im/interactions/payments.md)). Free tier limits are [U].
- **Who can message the agent:** "People in the Relay app" is **on by default**, so judges can scan a QR code and text it. There is no allowlist chore, unlike Photon's free tier [V] ([Who can message](https://docs.relayapp.im/agents/who-can-message.md)).
- **Third-party keys (the real cost):** the workshop path needs an **xAI** key (Grok text, Grok Imagine image and video) and an **ElevenLabs** key [V] ([workshop README](https://raw.githubusercontent.com/RelayMessenger/Relay-SDK/main/cookbook/mhacks-workshop/README.md)). Every MHacks participant gets one free month of ElevenLabs Creator [V] ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). Whether xAI credits are handed out at MHacks is [U]; ask SpaceXAI.

### 1.3 Platform constraints
- **iOS 26 or later only** (iPhone 11 and newer, or iPad). Also an Apple-silicon Mac on macOS 26 [V] ([App Store](https://apps.apple.com/us/app/relay-agent-messenger/id6789704419), [9to5Mac](https://9to5mac.com/2025/09/15/ios-26-supports-these-recent-iphones-but-drops-three-models/)). I found **no Android app and no web client** [U: absence]. The team needs only **one** qualifying device to build and demo.
- **Group chats are one person plus up to six agents.** Two humans cannot share a chat ("the group would hold two people" → 403) [V] ([Limits](https://docs.relayapp.im/live/rate-limits.md), [Group chats](https://docs.relayapp.im/chats/group-chats.md)). A "matchmaker" therefore introduces people by **sharing a person's contact card**, a feature added 2026-09-30 [V] ([changelog](https://docs.relayapp.im/changelog.md)).
- **Location sharing works only one-to-one,** with at most one request per minute. You poll for position; no event fires when the person moves [V] ([Location](https://docs.relayapp.im/chats/location.md)).
- **Video from TypeScript needs `node-webcodecs`,** which is prebuilt only for macOS arm64 and Linux. An Intel Mac should use Python/Pipecat [V] ([Video calls](https://docs.relayapp.im/calls/video.md)). Node 22.22.3+ for recipes; Python 3.11+ for Pipecat [V] ([Examples](https://docs.relayapp.im/live/examples.md), [Pipecat](https://docs.relayapp.im/integrations/pipecat.md)).

### 1.4 Realistic integration time (Relay-specific work; the domain logic is shared with the main track)

| Step | Hours | Note |
|---|---|---|
| Install Relay on an iOS 26 phone; `login`; `npx skills add RelayMessenger/Relay-SDK --skill relay`; make xAI and ElevenLabs keys | 0.25 | [workshop README](https://raw.githubusercontent.com/RelayMessenger/Relay-SDK/main/cookbook/mhacks-workshop/README.md) |
| Workshop steps 1–2: Grok Imagine profile picture, then a texting agent on `grok-4.7` | 0.5 | Do it in **Cursor** so the work also counts for SpaceX |
| Workshop steps 3–4: talking/listening loop videos (`grok-imagine-video-1.5-lite`) and calls with ElevenLabs `eleven_v4_turbo`; the agent calls you when ready | 1.0 | Grok Imagine video takes "about a minute" per clip [V] ([Pipecat › Grok](https://docs.relayapp.im/integrations/pipecat.md)) |
| Relay-facing part of the real product: location request, rich cards/places, agent-initiated call trigger, `rating_request` | 1.5 | APIs are documented; my estimate [I] |
| Hardening: `event_id` dedupe store (required before ACK), always-on host or a laptop that never sleeps, call test on MGuest Wi-Fi, recorded fallback | 1.0 | [docs index onboarding](https://docs.relayapp.im/llms.txt), [Limits](https://docs.relayapp.im/live/rate-limits.md) |
| **Total** | **≈ 4 (range 3–5)** | Template-only entry: ≈ 1.5–2 h |

### 1.5 Known gotchas
1. **Calls may need an app update.** The App Store "What's New" for v1.1 (Sep 20) lists groups, voice notes, attachments and pins, **not calls** [V] ([App Store](https://apps.apple.com/us/app/relay-agent-messenger/id6789704419)). The 2026-10-02 changelog adds an error: "This person's Relay app cannot take calls yet. They need to update Relay." [V] ([Call a person](https://docs.relayapp.im/calls/call-a-person.md)). The workshop ends with "Your agent calls you," so Relay presumably has a calling build ready for today [I]. **Ask at 1 PM.**
2. **API churn.** I counted 49 changelog entries from Sep 1 to Oct 2, 14 of them tagged "Breaking change." For example, A2UI's `Browser` card was added Sep 27 and removed Sep 30, and Communities were removed [V] ([changelog](https://docs.relayapp.im/changelog.md)). **Pin the SDK/CLI versions you start with.**
3. **Docs drift.** "Migrate from Photon" still says "Relay has voice memos, not calls," which contradicts the Calls section [V] ([page](https://docs.relayapp.im/resources/migrate-from-photon.md)). Trust the workshop README and the Calls pages.
4. **The 32-second rule.** If the agent process is asleep, calls ring out [V] ([Calls](https://docs.relayapp.im/calls/index.md)).
5. **First message is a silent request.** An agent's first message to someone who hasn't added it sits in **Requests** with no notification [V] ([Message requests](https://docs.relayapp.im/agents/message-requests.md)). For the demo, have judges **text first** via QR. Then the agent may call them.
6. **Payments need the org owner to complete Stripe onboarding,** and Relay takes 5% [V] ([Payments](https://docs.relayapp.im/interactions/payments.md)). Skip them at a hackathon.

### 1.6 MHacks 2026 resources
- **Workshop: "Relay: How to Build & Ship Your First AI Agent," Sat 1:00–2:00 PM, VR Lab** [V] ([live schedule](https://www.mhacks.org/live)). The FREE-WILi workshop is reportedly at the same hour ([FREE-WILi advocate file](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/04-free-wili.md)), so split the team.
- **The MHacks-specific cookbook** exists (above). Relay is a listed sponsor [V] ([mhacks.org](https://www.mhacks.org/)). The submission rule: "Your agent must work in the Relay app." Relay's starter ideas: "Social: matchmaker," "Food: dining halls, free food," "School: classes, study spots," "Money: marketplace, trading," "Fitness: gym coach" [V] ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)).
- **No credits or promo codes** are mentioned for Relay [V: none in handbook]. None appear needed.

---

## 2. What Relay's judges reward

**No precedent exists.** I found **no other hackathon with a Relay (relayapp.im) prize or a Devpost project built on it** [V: searches returned only unrelated "Relay" products] ([search evidence: Relay-Docs](https://github.com/RelayMessenger/Relay-Docs)). The app shipped on July 25, 2026, so MHacks is plausibly Relay's first sponsored track [I]. What follows is inferred from evidence, not from past winners.

| Signal | Evidence | What it implies [I] |
|---|---|---|
| The track asks for all three modes | "text, call and video chat with in the Relay app" [V] | A text-only bot is under-delivering. Show a **call with video**. |
| The workshop builds a **character** with a face and voice | [README](https://raw.githubusercontent.com/RelayMessenger/Relay-SDK/main/cookbook/mhacks-workshop/README.md) | Personality and presence count. But every team will have the template, so **the template alone won't win**. |
| Relay ships features weekly: share a person's card (9/30), forms and list pickers (9/30), Rive in calls (10/1), ratings (10/2) | [changelog](https://docs.relayapp.im/changelog.md) | Founders like seeing new features used well. Using 2–3 Relay-native features (location, cards/places, agent-initiated call, ratings) signals depth. |
| Advait's own products: Companion.AI (an AI companion with **video calling, memory, streaks**) and Einstein (an autonomous agent that **acts**, went viral) | [Companion.AI App Store](https://apps.apple.com/us/app/companion-ai/id6755073128), [Inside Higher Ed](https://www.insidehighered.com/news/tech-innovation/artificial-intelligence/2026/02/26/agentic-ai-can-complete-whole-courses-now) | He likes agents that **do things** and feel personal, with a hook that spreads. Over 124,000 people visited Einstein's site in three days [V, same source]. |
| Prize includes an **X shoutout**; the app is a two-sided network | [Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5), [App Store](https://apps.apple.com/us/app/relay-agent-messenger/id6789704419) | A startup rewards projects that **bring real people into Relay**. Showing "N hackers texted our agent this weekend" is the strongest possible pitch to this judge. |
| Ideas list is campus life (food, study, fitness, social, money) | [Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5) | They want agents students would actually keep. |

**Who judges:** the handbook says sponsors evaluate their tracks during 12:30–2:30 PM judging [V] ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)). Whether Advait judges in person is [U]. Main-track judges score "innovation, technical complexity, usability, and presentation quality" [V] (same source).

---

## 3. Prize value and expected competition

### 3.1 Prize value (whole team of 4)

| Component | Estimate | Basis |
|---|---|---|
| Flights DTW↔SFO | ≈ $290–360 per person, ≈ $1.2–1.45k for 4 | Kayak: average round trip $290–349 by month; cheapest recent $359 [V] ([Kayak](https://www.kayak.com/flight-routes/Michigan-USMI/San-Francisco-Bay-Area-zzXIH)). **Whether Relay pays flights for all four is [U]**: the wording is "A trip to San Francisco… for each member" |
| A week of SF lodging ("Relay house") | ≈ $250–600 per person per week at hacker-house rates, ≈ $1.0–2.4k for 4 | $40/night or $250/week at the low end; Superhero Hotel $2,400 for 4 weeks [V] ([eomag](https://www.eomag.io/article/hacker-houses-san-francisco)). What the "Relay house" is, I could not find [U]. I infer it is the team's SF residence |
| Hoodie, stickers and eye masks | ≈ $50–80 per person [I] | Not priced anywhere |
| **Nominal 1st** | **≈ $2.5–4.2k** | Sum |
| **Realistic cash-equivalent 1st** | **≈ $1.0–1.5k** [I] | It isn't cash, needs a week away mid-semester, flights and dates are unconfirmed, and it comes from a one-employee company |
| **Career upside (unpriced)** | A week embedded with a founder who has shipped viral products [V], from a tiny company [V] | Plausibly the best internship/referral path of any sponsor prize here [I] |
| 2nd | Merch only, ≈ $200–320 | Handbook [V] |
| X shoutout | ≈ 12.6K followers [U: from a search-engine snippet; x.com blocked fetches] | [X profile](https://x.com/advaitpaliwal) |

### 3.2 Expected competition

| Analog | Opt-in | Source |
|---|---|---|
| MHacks 2025, AgentMail (an agent-communications startup; **$3,500 cash**) | **18 / 122 (15%)** | [filter](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90540), [prizes](https://mhacks-2025.devpost.com/) [V] |
| MHacks 2025, Fetch.ai best use | 14 / 122 (11%) | [Neon advocate's recount](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/05-neon-backend.md) |
| DivHacks 2026, Photon iMessage agents (workshop + promo code) | **29 / 65 (45%)** | [filter](https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105999) [V] |

**Pushes entries up:** an on-site workshop with copy-paste prompts that end in a working video call. Agents are the default build: 47% of MHacks 2025 projects listed an LLM [V, verdict recount] ([verdict](/Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md)). The workshop also pulls SpaceX teams, because it uses Grok Imagine.

**Pushes entries down:** iOS 26 only. The app is unknown to students. The prize is non-cash. Photon and Fetch.ai compete for the same "agent you message" projects.

**My estimate [I]:** 15–30% of submissions, which is **about 20–50 entries** if MHacks gets 130–170 projects (2025 had 122 from 380 participants [V] ([MHacks 2025](https://mhacks-2025.devpost.com/)); the 2026 site advertises "1,000+ student builders" [V] ([mhacks.org](https://www.mhacks.org/))). Of these, perhaps **5–10 go beyond the workshop template** [I]. **Expected competition: high** by count, medium among serious entries.

---

## 4. Expected value

**My win probabilities [I]:**
- A **beyond-template** entry (real data tools, agent-initiated call, video, real users during the event, demoed cleanly): P(1st) ≈ 12–18%, P(2nd) ≈ 12–15%.
- A **template** entry: ≈ 2–4% for either place.

**EV (beyond-template):** 0.15 × $1,250 + 0.13 × $260 ≈ **$190 + $35 ≈ $225 cash-equivalent**. On top of that comes the unpriced founder access.

**Compared with the other sponsor tracks (handbook prizes [V]; same-probability comparison is mine [I]):**

| Track | Team prize at 1st | EV at an identical 15% P(1st) | What it costs on top of the Sketch A stack |
|---|---|---|---|
| Fetch.ai ASI:One | $1,250 cash (+ $750 / $500) | $190 + more from 2nd and 3rd places | Agentverse registration + ASI:One submission agent; a second surface |
| SpacetimeDB | $1,000 cash (+ $500 / $200) | $150 + | A real-time backend rewrite; weak fit with a messaging agent |
| Capital One Nessie | $300 × 4 = $1,200 | $180 | Needs a finance angle; breaks SpaceX (verdict) |
| **Relay** | **≈ $1.0–1.5k realistic (≈ $2.5–4.2k nominal)** | **$150–225** | **≈ 1–2 h**, because the SpaceX/ElevenLabs work already builds the agent |
| Photon | $400 cash + $300 credits | $60 cash | It is a competing surface (§5) |
| SpaceX | Mechanical keyboards (+ a Cursor bottle raffle) | Low | Already in the stack |

**The honest read:** on pure cash EV, Relay is **mid-pack**. Fetch.ai beats it because it has three cash places. Where Relay wins is **EV per marginal hour** and **demo spillover**. Its integration is almost the same work SpaceX and ElevenLabs already require. And a live video call with a character you built is the most memorable 3-minute demo a software team can give to *any* panel, including the $2,500 main-track judges [I].

---

## 5. Stacking

| Track | Fit with Relay | Why |
|---|---|---|
| **Sustainability (main)** | **Good** | Relay's own idea, "Food: dining halls, free food," is a food-waste product. "Fitness: gym coach" plus satellite smoke/heat data is a climate-adaptation product (Sketch A). The verdict already rejected the "Relay is awkward for Sustainability" objection [V] ([verdict](/Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md)) |
| Actually Intelligent (main) | Natural | Fallback if the climate angle fails (Sketch C) |
| FinTech (main) | Possible | "Money: marketplace, trading" exists, but payments need Stripe onboarding and FinTech breaks SpaceX |
| Hardware (main) | Possible | A call can drive a device through a tool call. Untested |
| **Judged by an LLM (fun)** | **Good** | Add a measured eval of the agent's decisions to look technically sharp |
| Useless AI / Dumbest Idea (fun) | Easy add-ons | A character you video call is the cheapest way to be funny. Enter only if a real comic feature ships (verdict) |
| **SpaceX "Make it Legendary"** | **Excellent** | Relay's workshop uses Grok Imagine and Grok, and Relay has a Cursor connector. One build meets the tooling rule. SpaceX still needs "real space data" [V] ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)) |
| **ElevenLabs** | **Excellent** | The workshop's call voice is ElevenLabs. There is also an official `@relaymessenger/elevenlabs` bridge with Rive lip-sync [V] ([bridge](https://docs.relayapp.im/calls/elevenlabs.md)) |
| Notability | Neutral, free | Use it for planning; take screenshots |
| Neon | Good | The agent needs a durable `event_id` store before ACK [V] ([docs index](https://docs.relayapp.im/llms.txt)) |
| Fetch.ai | Partial | The same agent core can register on Agentverse, but that is a second surface and a second submission. Add it only if time remains |
| FREE-WILi | Optional | A call that triggers a device. Strong demo, extra risk |
| FinchNode | Possible | The "Fitness" idea, but synthetic health records feel off-topic for Sustainability |
| **Photon** | **Conflict** | Both are "text your agent" surfaces, and Relay positions itself against Photon ("Migrate from Photon") [V] ([page](https://docs.relayapp.im/resources/migrate-from-photon.md)). One 3-minute pitch can sell one surface. Pick Relay |
| Figma Best Design | Tension | Relay owns the chat UI. Only a companion surface could be designed |
| SpacetimeDB | Weak | It wants live shared state at the core. Relay chats are one person each |

**Recommended stack:** *Sustainability + Judged by an LLM + **Relay** + SpaceX + ElevenLabs + Notability*, with Neon optional. That is **3 real integrations** (Relay, xAI/Grok, ElevenLabs), all of which the Relay workshop already wires together. It fits the verdict's "3–4 real integrations" rule. I see **no reason to change the main/fun verdict**. If SpaceXAI says Earth-observation data doesn't count, Relay still works under AI (Sketch C) or Sustainability without SpaceX (Sketch B).

---

## 6. Project sketches

### A. "Ground Control": an astronaut coach you text and video call about the air outside *(Sustainability · Relay · SpaceX · ElevenLabs · Judged by an LLM · Notability)* **(recommended)**
- **Persona:** a retired-astronaut running coach, built with the workshop's Grok Imagine portrait and talking/listening loop videos. Relay's "Fitness: gym coach" idea is the frame.
- **Text:** "Can I run outside at 7 tomorrow?" The agent sends a Relay **location request** ("For One Hour") [V] ([Location](https://docs.relayapp.im/chats/location.md)). It then checks **real satellite data**: NASA FIRMS active-fire detections (MODIS/VIIRS) [V] ([Earthdata FIRMS](https://www.earthdata.nasa.gov/data/tools/firms)) and NASA POWER satellite-derived temperature [V: API exists] ([POWER API](https://power.larc.nasa.gov/docs/services/api/)). It answers with a plan and a rich card. Grok Imagine makes only the *character's* reaction images, never fake satellite imagery. That honesty point matters to judges.
- **Call:** "Coach me while I walk to class." It is a voice-and-video call with the astronaut. The killer moment is an **agent-initiated call** [V] ([Call a person](https://docs.relayapp.im/calls/call-a-person.md)): when a new fire detection or heat spike appears near a subscribed user, the agent rings them. In judging, the judge's phone rings.
- **Sustainability story:** climate adaptation. Smoke and heat days are rising, and this turns satellite data into a daily decision. Add a low-carbon nudge ("walk, the air's clean").
- **Judged by an LLM:** an eval table. Back-test the agent's "safe / not safe" calls against past ground-truth AQI days and report the accuracy.
- **Relay-native depth:** location sharing, agent-initiated call, video, a `rating_request` after each coaching call [V] ([changelog](https://docs.relayapp.im/changelog.md)), and a QR code on the table so hackers use it all weekend.
- **Risk:** the FIRMS API page showed outage notices on its area and country endpoints when I fetched it [V] ([FIRMS API](https://firms.modaps.eosdis.nasa.gov/api/)). Cache a CSV snapshot and keep NASA POWER as a fallback. Whether SpaceX judges accept Earth-observation data is [U]; ask at the 4–5 PM SpaceXAI session.

### B. "Leftovers": a free-food rescue agent, Relay's own idea *(Sustainability · Relay · ElevenLabs · Judged by an LLM · Neon; SpaceX only via Grok Imagine, without space data, so probably not)*
- Organizers text a photo of leftover trays. A vision model estimates servings and kg diverted. Opted-in students nearby get a **Place** card. Hungry students **call** "anything free near the Dude?" Each pickup ends with a **rating** card.
- **The pitch is traction:** run it on MHacks' own catering all weekend, then show the Relay judge the real count of users, chats and ratings [I: what a growth-stage founder values].
- Strongest pure-Relay fit, because the judges wrote "Food: dining halls, free food" [V] ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). It **loses SpaceX**, which is why it is not my first choice for this team.

### C. "Study Match": a voice-interview matchmaker for study partners *(AI main · Relay · Judged by an LLM · ElevenLabs · Fetch.ai optional)*
- Each student does a 3-minute **voice-call interview** with the agent. It matches students by class, schedule and complementary strengths. With consent, it introduces two people by **sharing each person's contact card**, the 2026-09-30 feature [V] ([changelog](https://docs.relayapp.im/changelog.md)). It suggests a study spot as a Place.
- This design fits Relay's "one person per chat" rule [V] ([Limits](https://docs.relayapp.im/live/rate-limits.md)). It covers two of Relay's ideas ("Social: matchmaker," "School: study spots").
- Use it only if the verdict flips to AI (no climate angle). Add a match-quality eval to clear "AI that actually solves a real problem."

---

## 7. Weaknesses, red flags and rebuttals

**Red flags (verified unless marked):**
1. **A tiny, brand-new vendor.** App v1.0 on July 25; GitHub org on July 26. Companion's LinkedIn says 1 employee. The app notes say "It's early. If something breaks, contact me through the app." ([App Store](https://apps.apple.com/us/app/relay-agent-messenger/id6789704419), [org](https://api.github.com/orgs/RelayMessenger/repos?per_page=100), [LinkedIn](https://www.linkedin.com/company/getcompanionai)).
2. **Daily breaking changes** (§1.5).
3. **iOS 26 only, and calls in the public build are unverified** (§1.3, §1.5).
4. **The workshop commoditizes the baseline.** Expect many lookalike "character you can call" entries [I].
5. **The prize is non-cash with unclear logistics.** Flights for four, dates and the "Relay house" are [U]. 2nd place is merch, and there is no 3rd.
6. **Paid third-party APIs.** Grok Imagine video generation is billed by xAI; credits are [U].

| Rival advocate's argument | Strength | Rebuttal |
|---|---|---|
| "Fetch.ai pays $2,500 in cash across three places; Relay pays a trip." | **Strong** | True on cash EV (§4). But Relay costs about 1–2 marginal hours on the recommended stack, while Fetch.ai adds a second surface and submission. Enter Fetch.ai too if the agent core is done by Sunday 6 AM; the two can share a backend. |
| "Photon reaches judges without installing an app." | Medium | The Relay judges already have Relay. For main-track judges, demo on our phone, mirrored, plus an agent-initiated call to a teammate. Relay also offers video calls with the agent's own camera, plus Rive. The Photon advocate's feature table lists no video calls, and Photon's free tier has no group chats ([Photon advocate file](/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/06-photon-imessage-agents.md)). |
| "The workshop means 40 identical entries; you can't win." | Medium | That is why Sketch A adds real data tools, an agent-initiated call, location, ratings and real weekend users. The template is our starting point, not our pitch. Lookalikes also make a differentiated entry stand out to a judge watching 40 of them [I]. |
| "Relay may not even support calls in the App Store build." | Medium | Relay's own MHacks workshop ends with the agent calling you, so a calling build must exist for today [I]. Verify at 1 PM. If calls fail, text plus voice memos still meet "work in the Relay app," at a lower win probability. |
| "API churn will break you mid-hackathon." | Medium | Pin versions at hour 1 and use only the workshop path plus documented calls/location. Don't upgrade until after judging. |
| "A one-person startup might not deliver the trip." | Low–medium [I] | The value is still positive with no trip (merch, X shoutout, founder contact). Ask about logistics at the workshop. |
| "iOS-only excludes Android teammates." | Low | One iOS 26 iPhone or an M1+ Mac on macOS 26 suffices to build and demo [V] ([App Store](https://apps.apple.com/us/app/relay-agent-messenger/id6789704419)). |

---

## 8. Scorecard

| Criterion | Score | Justification |
|---|---|---|
| Prize value | **6/10** | Nominal ≈ $2.5–4.2k but non-cash; realistic ≈ $1.0–1.5k. Founder access is a real upside; 2nd place is merch only. |
| Win probability | **4/10** | High entry count thanks to the workshop, and no precedent. A beyond-template entry has about 12–18% for 1st and about 25–30% for either place [I]. |
| Integration ease | **9/10** | Four copy-paste prompts to text plus video call; about 4 h for a distinctive build. iOS 26 and API churn cost a point. |
| Stacking potential | **9/10** | Relay's workshop uses Grok Imagine and ElevenLabs, so it doubles as SpaceX's tooling and ElevenLabs' integration. Fits Sustainability and Judged by an LLM; conflicts only with Photon and Figma. |
| Demo impact | **9/10** | A live video call with your agent, and the agent calling the judge's phone, is the strongest software demo moment on the board. |
| Fit with team preferences | **9/10** | The team named Relay. It keeps SpaceX (its top bias), avoids FinTech and allows several sponsor tracks. |

**Bottom line:** Relay isn't the biggest-cash track. It is the **hub** of the team's preferred stack. One agent built through Relay's workshop qualifies for Relay, meets SpaceX's tooling rule and enters ElevenLabs, and it gives the main-track judges a live call to remember. Enter it, build past the template, and pitch Relay as the single surface.

---

## 9. Today's action items (time-critical)
1. **Before 1 PM:** confirm one teammate has an iPhone on iOS 26 and install Relay. Create the xAI and ElevenLabs keys (claim the ElevenLabs Creator month). Open the project in **Cursor**.
2. **1–2 PM, VR Lab (Relay workshop),** two teammates attend. Ask:
   - Does the **App Store build take calls and video** today, or is a TestFlight needed?
   - Does 1st place cover **flights for all four** members, and **when** is the week?
   - **Who judges** the track, and do they want to see real usage?
   - Which **SDK/CLI version** should we pin?
3. **By 4 PM:** text, call and video all working with the persona. Pin versions.
4. **4–5 PM, SpaceXAI session:** ask whether Earth-observation data (FIRMS/POWER) counts as "space data." If not, pivot per §5.
5. **Evening:** domain tools, the agent-initiated call, the rating card, the eval, and a QR code on the table.
6. **Sunday before noon:** record a fallback video of the call and test it on MGuest Wi-Fi. Write the Devpost entry tagging Relay, SpaceX, ElevenLabs and Judged by an LLM.

---

## Sources
- MHacks 2026 Handbook › Tracks & Prizes (Relay, SpaceX, ElevenLabs, all sponsor prizes): https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5 (read through Notion's public `loadCachedPageChunkV2` API)
- MHacks 2026 Hacker Handbook (hacking times, judging process and criteria): https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af
- MHacks 2026 Devpost (Relay prize text): https://mhacks-2026.devpost.com/
- MHacks site (sponsors, "1,000+ student builders"): https://www.mhacks.org/
- MHacks live schedule (Relay workshop 1–2 PM, VR Lab): https://www.mhacks.org/live
- MHacks 2025 Devpost (380 participants, prize list): https://mhacks-2025.devpost.com/
- MHacks 2025 AgentMail opt-in filter (18 of 122): https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90540
- DivHacks 2026 Photon opt-in filter (29 of 65): https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105999
- Relay docs index: https://docs.relayapp.im/llms.txt
- Relay Quickstart: https://docs.relayapp.im/start/quickstart.md
- Relay Create an agent: https://docs.relayapp.im/agents/create-agent.md
- Relay Client SDKs: https://docs.relayapp.im/live/sdks.md
- Relay Integrations: https://docs.relayapp.im/integrations/index.md
- Relay Cursor integration: https://docs.relayapp.im/integrations/cursor.md
- Relay Pipecat (Grok Voice, Grok Imagine and ElevenLabs recipes): https://docs.relayapp.im/integrations/pipecat.md
- Relay Calls: https://docs.relayapp.im/calls/index.md
- Relay Call a person: https://docs.relayapp.im/calls/call-a-person.md
- Relay Video calls: https://docs.relayapp.im/calls/video.md
- Relay Talking avatar: https://docs.relayapp.im/calls/avatars.md
- Relay Rive in calls: https://docs.relayapp.im/calls/rive.md
- Relay ElevenLabs bridge: https://docs.relayapp.im/calls/elevenlabs.md
- Relay Limits: https://docs.relayapp.im/live/rate-limits.md
- Relay Group chats: https://docs.relayapp.im/chats/group-chats.md
- Relay Location sharing: https://docs.relayapp.im/chats/location.md
- Relay Who can message your agent: https://docs.relayapp.im/agents/who-can-message.md
- Relay Message requests: https://docs.relayapp.im/agents/message-requests.md
- Relay Payments: https://docs.relayapp.im/interactions/payments.md
- Relay Organization (free seats): https://docs.relayapp.im/console/organization.md
- Relay Examples: https://docs.relayapp.im/live/examples.md
- Relay Migrate from Photon: https://docs.relayapp.im/resources/migrate-from-photon.md
- Relay changelog: https://docs.relayapp.im/changelog.md
- Relay MHacks workshop README: https://raw.githubusercontent.com/RelayMessenger/Relay-SDK/main/cookbook/mhacks-workshop/README.md
- Relay MHacks workshop commits: https://api.github.com/repos/RelayMessenger/Relay-SDK/commits?path=cookbook/mhacks-workshop
- Relay SDK cookbook: https://github.com/RelayMessenger/Relay-SDK/tree/main/cookbook
- Relay SDK repo metadata: https://api.github.com/repos/RelayMessenger/Relay-SDK
- RelayMessenger GitHub org repos: https://api.github.com/orgs/RelayMessenger/repos?per_page=100
- Relay-Docs PR by Advait Paliwal: https://github.com/RelayMessenger/Relay-Docs/pull/288
- Relay-Docs repo: https://github.com/RelayMessenger/Relay-Docs
- npm relaymessenger CLI: https://registry.npmjs.org/relaymessenger
- npm downloads (SDK): https://api.npmjs.org/downloads/point/last-week/@relaymessenger/sdk
- npm downloads (CLI): https://api.npmjs.org/downloads/point/last-week/relaymessenger
- Relay website: https://relayapp.im
- Relay: Agent Messenger on the App Store: https://apps.apple.com/us/app/relay-agent-messenger/id6789704419
- Companion.AI on the App Store: https://apps.apple.com/us/app/companion-ai/id6755073128
- Companion website: https://companion.ai/
- Companion on LinkedIn: https://www.linkedin.com/company/getcompanionai
- Advait Paliwal, experience page: https://www.advaitpaliwal.com/experience
- Advait Paliwal on X: https://x.com/advaitpaliwal
- Inside Higher Ed on Einstein and Advait Paliwal: https://www.insidehighered.com/news/tech-innovation/artificial-intelligence/2026/02/26/agentic-ai-can-complete-whole-courses-now
- Futurism on Einstein: https://futurism.com/artificial-intelligence/ai-agent-canvas-homework
- 9to5Mac, iOS 26 device support: https://9to5mac.com/2025/09/15/ios-26-supports-these-recent-iphones-but-drops-three-models/
- Kayak, Michigan to SF Bay Area fares: https://www.kayak.com/flight-routes/Michigan-USMI/San-Francisco-Bay-Area-zzXIH
- SF hacker-house prices: https://www.eomag.io/article/hacker-houses-san-francisco
- NASA FIRMS (Earthdata): https://www.earthdata.nasa.gov/data/tools/firms
- NASA FIRMS API (outage notice seen 2026-10-03): https://firms.modaps.eosdis.nasa.gov/api/
- NASA POWER API: https://power.larc.nasa.gov/docs/services/api/
- Internal: main/fun verdict: /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md
- Internal: Photon advocate file: /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/06-photon-imessage-agents.md
- Internal: Neon advocate file (MHacks 2025 Fetch.ai opt-ins): /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/05-neon-backend.md
- Internal: FREE-WILi advocate file (workshop time clash): /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/04-free-wili.md

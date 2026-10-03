# Sponsor Track Advocate — ASI: One Agent Challenge (Fetch.ai)

## Prompt given (excerpt)
> You are the advocate for the sponsor track "ASI: One Agent Challenge (Fetch.ai)" at MHacks 2026. Research the sponsor's tech and how fast a team can integrate it, what its judges reward, prize value vs competition, expected value, how it stacks with the main/fun picks and other sponsors, 2–3 winning project sketches, honest red flags, and a 1–10 scorecard. Make the strongest honest case — an impartial judge will weigh your file against eleven other sponsor advocates.

---

## 0. The case in brief

- **The largest sponsor cash pool at MHacks 2026, paid as plain cash across three places.** Prizes are $1,250 / $750 / $500 ([Devpost prize list](https://mhacks-2026.devpost.com/); [Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). Fetch's own hackpack adds an **internship interview** to each place ([hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)). For comparison, the next-largest sponsor pools are SpacetimeDB at $1,700 cash, Neon at $1,600 in credits, and Capital One at about $1,200 in gift cards for a 4-person team at 1st place ([Devpost](https://mhacks-2026.devpost.com/)).
- **A big prize does not mean a crowded track.** I counted Devpost opt-ins at 9 events where Fetch.ai ran a sponsor prize. The median was **12%** of projects, and the mean was 17%. At **MHacks 2025, 15 of 122 projects (12%)** opted into any of Fetch's three prizes, and 3 of them won (§3). TreeHacks 2026 offered $5,000 and drew only 7%. A large prize did not bring a crowd. The likely brake is the track's hard requirements: an Agentverse-registered agent, the Chat Protocol, the full primary workflow running inside ASI:One, and a second submission through a chat agent (§1).
- **How "discoverable through ASI:One" works technically.** You write an agent, usually a Python `uAgent`, and give it the **Agent Chat Protocol** with `publish_manifest=True`. You run it as a **mailbox agent** (`mailbox=True`) so Agentverse relays messages to your laptop or server, and you connect it once through the Agentverse Inspector. Then you add a README with keywords and an `@handle`. After that, ASI:One users can `@mention` the agent or open it from its Agentverse profile, and ASI:One's search can route matching queries to it ([ASI-compatible uAgents](https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/asi-compatible-uagents); [discovery checklist](https://docs.agentverse.ai/documentation/agent-discovery/setup-guide)).
- **What has won Fetch prizes.** I verified **48 Fetch-prize winners** at 11 hackathons. The winners close the loop: a real email is sent, a payment clears, a device moves, a ticket gets filed. Most use several agents with distinct roles. About a third of the winners are health, emergency or accessibility projects. Payments show up in about a fifth. **Only 1 of the 48 is framed around sustainability** (AgriBroker, food surplus), so a climate entry would stand out on Innovation (20%). I can't tell whether the judges would favour that theme.
- **Expected value.** For an entry that meets every requirement, I estimate a **≈30% chance of placing** and **≈$250 in expected cash** (my inference, §4). That is the highest absolute EV I can find among the sponsor tracks. It costs about **6 Fetch-specific hours**, or roughly $40 per hour, in line with Neon and Notability.
- **It stacks with the recommended picks.** It fits a **Sustainability** main track, **Judged by an LLM**, Neon and FREE-WILi. A mailbox agent runs on your own laptop, so it can drive a USB device. It also fits **SpaceX**: ASI:One renders Markdown images, so Grok Imagine output can appear inside the chat. **Relay and Photon** can share the same agent core, and they cover ASI:One's weak spot, proactive push messages. It conflicts with **Useless AI** and **Dumbest Idea**.
- **My recommendation:** enter Fetch.ai as one of the team's **two main cash sponsor tracks**. Build the project's agent brain as Fetch uAgents from hour one. Don't add Fetch at hour 20.

---

## 1. The technology

### 1.1 What it is

| Item | Finding | Source |
|---|---|---|
| Ecosystem | **Agentverse** is "the open marketplace for AI Agents". You can publish agents built with uAgents "or any other agentic framework". **ASI:One** is Fetch's "agentic LLM and the discovery layer for Agentverse": when a user asks something, it "identifies the most suitable agent and routes the request" | [hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack) |
| SDK | `uagents` (Python). v0.26.0 was released on **2026-10-02**. Requires Python ≥3.10. The GitHub repo has 1,639 stars and was last pushed on 2026-10-02 | [PyPI](https://pypi.org/pypi/uagents/json), [GitHub API](https://api.github.com/repos/fetchai/uAgents) |
| Framework freedom (2026) | "You may use any framework, including Google ADK, LangGraph, CrewAI, OpenAI Agents SDK, Claude Agent SDK, uAgents, or plain Python." In 2025, the ASI:One prize asked teams to use ASI:One "as the core reasoning and decision-making engine". **The 2026 brief drops that**, so Grok, Claude or Gemini can do the reasoning | [hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack), [MHacks 2025 Fetch page](https://www.fetch.ai/events/m-hacks) |
| ASI:One LLM API | OpenAI-compatible at `https://api.asi1.ai/v1`. Models: `asi1`, `asi1-ultra` and `asi1-mini`. Supports tool calling. Public per-token prices and free-tier limits **were not found** | [ASI:One quickstart](https://innovationlab.fetch.ai/resources/docs/asione/asi-one-quickstart), [model docs](https://docs.asi1.ai/documentation/models) |
| Rich UI inside the chat | **ASI Interactive Cards** come in four kinds: Carousel, Detail, Form and Review, plus custom element trees. An agent sends them as a `MetadataContent` block with `card_kind` and `card_payload` (≤64 KB, nesting depth ≤8). The docs include a full flight-booking example | [Interactive Cards](https://innovationlab.fetch.ai/resources/docs/interactive-cards/asi-interactive-cards) |
| Images in chat | "ASI:One Chat renders **Markdown images** inside TextContent." This is how an agent can show a Grok Imagine image | [image-generation agent](https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/image-generation-agent) |
| Payments (bonus) | **Agent Payment Protocol**: RequestPayment → Commit/Reject → Complete/Cancel. Settlement can use FET, Stripe Checkout or others. "Fetch-skills" ship ready-made `chat-protocol`, `stripe-payment-protocol` and `fet-payment-protocol` packages for AI coding assistants | [Payment Protocol](https://innovationlab.fetch.ai/resources/docs/agent-transaction/agent-payment-protocol), [uAgents docs](https://uagents.fetch.ai/docs/guides/agent-payment-protocol), [Fetch-skills](https://innovationlab.fetch.ai/resources/docs/next/fetch-skills/skills-reference) |
| Agentverse MCP | The hackpack lists an MCP server (`https://mcp.agentverse.ai/sse`, lite version at `https://mcp-lite.agentverse.ai/mcp`) to "deploy your first agent on Agentverse with Claude Desktop in Under 5 Minutes". *Inference:* any MCP client, Cursor included, could use it. That helps with SpaceX's "the more you use Cursor" rule | [hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack), [Agentverse MCP docs](https://docs.agentverse.ai/documentation/advanced-usages/agentverse-mcp) |

### 1.2 How "discoverable through ASI:One" works (verified mechanics)

1. **Speak the Chat Protocol.** Import `ChatMessage`, `ChatAcknowledgement`, `TextContent`, `StartSessionContent`, `EndSessionContent` and `chat_protocol_spec` from `uagents_core.contrib.protocols.chat`. Acknowledge every message, reply with `TextContent`, and call `agent.include(chat_proto, publish_manifest=True)`. The hackpack's quickstart is about 40 lines ([hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)).
2. **Make it reachable.** There are three hosting options ([uAgent creation](https://innovationlab.fetch.ai/resources/docs/agent-creation/uagent-creation)):
   - **Hosted** on Agentverse. Runs in the browser editor, but some third-party libraries are blocked.
   - **Local** with a public endpoint. You manage uptime yourself and need Almanac registration.
   - **Mailbox** (`mailbox=True`). Your code runs locally, and Agentverse queues messages while it is offline. The Fetch docs recommend this option for ASI:One ([ASI-compatible uAgents](https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/asi-compatible-uagents)).
   
   Agents built on other frameworks register through Agentverse's "External Integration" flow. It requires a public endpoint, an Agentverse API key and a seed phrase, followed by an "Evaluate Registration" check ([launch guide](https://docs.agentverse.ai/documentation/launch-agents/launch-asi-one-compatible-u-agent)).
3. **Be findable.** Agentverse's discovery checklist has seven steps: Chat Protocol, a README ("the main document ASI:One uses to understand what your Agent does"), a custom **@handle** of up to 20 characters "so users can find and mention your Agent directly", keeping the agent running ("only active, running Agents are prioritized in search"), **at least 10 interactions**, an avatar and a description ([setup guide](https://docs.agentverse.ai/documentation/agent-discovery/setup-guide)). Ranking combines "semantic relevance, profile completeness, keyword alignment, and interaction history" ([Agentverse blog](https://agentverse.ai/blog/how-ai-agents-are-ranked), via search summary).
4. **How a judge reaches it.** From ASI:One chat, the judge either `@mentions` the handle or clicks "Chat with Agent" on the Agentverse profile ([ASI-compatible uAgents](https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/asi-compatible-uagents)). The submission asks for **ASI:One shared-chat URLs** and **Agentverse profile URLs** ([submission doc](https://docs.google.com/document/d/1UDW-X1C24hxZviFOQzjTeh0pXRNAoflMb8lhJqZP9Z0)). So judges can replay a recorded conversation even when they don't run one live.

### 1.3 Requirements, access and cost

**Mandatory**, quoted from the [hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack):
- "Register at least one agent on Agentverse"
- "Implement the Agent Chat Protocol (ACP)"
- "Be discoverable and directly usable through ASI:One"
- "Demonstrate meaningful tool execution or multi-agent orchestration"
- "Complete the primary user workflow entirely within an ASI:One conversation"
- A "public GitHub repository with instructions to run or test the project"

The challenge statement adds that the workflow must be demonstrable "without requiring a custom frontend". The README must include each agent's name and address plus the `innovationlab` and `hackathon` badges. The hackpack also lists a **3–5 min demo video** as a deliverable.

**Two submissions.** Teams submit on Devpost **and** through the **MHacks ASI:One Submission Agent** ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). Per the [submission doc](https://docs.google.com/document/d/1UDW-X1C24hxZviFOQzjTeh0pXRNAoflMb8lhJqZP9Z0):
- The lead creates the team and enters the project name, problem and GitHub URL (all required), plus an optional video URL and optional "bonus points" fields for agent-profile URLs and shared-chat URLs.
- The status reads "Submitted" only once **every teammate has joined** with the Team ID.
- *Inconsistency:* the hackpack lists the video as a deliverable, but the form marks it optional. Make the video anyway.

**Bonus considerations** ([hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)):
- multi-agent collaboration
- Payment Protocol "with a credible monetization model"
- Interactive Cards
- error handling and recovery
- real-time data and external services
- an agent that "could realistically continue operating after the hackathon"

The Payment Protocol also appears **inside the 20% "Use of Fetch.ai Technology" criterion**: "Is the Payment Protocol integrated to enable monetisation?"

**Cost:**
- Fetch gives MHacks hackers **one free month of ASI:One Pro and Agentverse Premium** with promo codes `MHACKS26` and `MHACKSAV` ([hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack); the raw page lists `"promoCode":"MHACKS26, MHACKSAV"`). *Inference:* one code is for each product.
- Free-tier quotas for mailbox and hosted agents are plan-dependent, and I could not verify them. The codes should make that moot.
- Payments can run in Stripe test mode or on FET testnet, so no real money is needed. Winners used both: LifeLink used Stripe test mode, and AgenticHire used the Dorado testnet ([LifeLink](https://devpost.com/software/lifelink-soibwr), [AgenticHire](https://devpost.com/software/agentichire-2xyk0z)).

### 1.4 MHacks 2026-specific resources

- **FetchAI workshop: Saturday 2:00 PM, Duderstadt Room 3336** ([schedule sheet](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365)). A "Zeta Pi Agentic AI Workshop" runs at 4:00 PM.
- **Judges and mentors for 2026 are not announced.** The event JSON has `"judges":[]` and `"mentors":[]` ([event page](https://www.fetch.ai/events/mhacks-2026)). In 2025, Fetch sent 2 judges and 4 mentors: Sana Wajid (Chief Development Officer / SVP Innovation Lab), Attila Bagoly (Chief AI Officer), and developer advocates ([MHacks 2025 Fetch page](https://www.fetch.ai/events/m-hacks)). *Inference:* expect Innovation Lab staff again.
- **Timing.** Hacking runs from Saturday 12 PM to Sunday 12 PM, and Devpost lists the deadline as 12:15 PM EDT. Judging is 12:30–2:30 PM Sunday. Sponsors evaluate their tracks "at the same time" as the main panel, and "to be judged for any track, your team must be present" ([Hacker Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af), [Devpost](https://mhacks-2026.devpost.com/), [Sunday schedule](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=83169850)).

### 1.5 Realistic integration time (Fetch-specific work only; my estimate)

| Step | Hours | Note |
|---|---|---|
| Create ASI:One and Agentverse accounts, redeem the codes, get an ASI:One API key | 0.25 | |
| Hello-world mailbox agent with the Chat Protocol, connected through the Inspector, and answering an `@handle` in ASI:One | 0.75–1 | Hackpack quickstart plus the [ASI-compatible guide](https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/asi-compatible-uagents) |
| Put the project's real tools (data fetchers, actuators, DB writes) behind the chat handler | ~1 | The tools themselves are main-track work. Only the wrapping counts here |
| Split into 2–3 role agents (planner / data / actuator) that talk through uAgents messages | 1–1.5 | Satisfies "multi-agent orchestration" and the bonus |
| One **Review** card (confirm the plan) and one **Form** card (parameters) | 1–1.5 | Follow the [cards example](https://innovationlab.fetch.ai/resources/docs/interactive-cards/asi-interactive-cards) |
| Agentverse profile: README with keywords, @handle, avatar, badges; generate ≥10 interactions | 0.5 | Teammates chatting with it builds interactions on the side |
| Submission: shared-chat URLs, Submission Agent team plus teammates joining, README addresses, 3–5 min video | 1 | Film the video before 11:30 AM Sunday |
| **Core total** | **≈ 6 (range 4.5–8)** | Split across 2 people, so about 3 hours each |
| Optional: Payment Protocol with the Stripe skill | +2–3 | Worth it only with a credible monetization story (§6 C) |

### 1.6 Known gotchas (verified unless marked)

- **A new SDK version came out the day before the event.** `uagents` 0.26.0 shipped on 2026-10-02 ([PyPI](https://pypi.org/pypi/uagents/json)), but the ASI-compatible guide pins `uagents==0.25.5` and `AgentChatProtocol 0.3.0` ([guide](https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/asi-compatible-uagents)). Mismatched protocol versions "break compatibility". **Pin the version the docs use.** *Inference:* 0.26.0 is untested against the docs.
- **Python 3.10–3.13 only.** "Python 3.14+ not yet supported" ([uAgent creation](https://innovationlab.fetch.ai/resources/docs/agent-creation/uagent-creation)). A 2026 winner also lost time to conda and pyenv interpreter conflicts ([AgenticHire](https://devpost.com/software/agentichire-2xyk0z)).
- **Chrome v142+ and Brave** show a Local Network Access prompt when the Inspector connects a mailbox. Click Allow ([uAgent creation](https://innovationlab.fetch.ai/resources/docs/agent-creation/uagent-creation)).
- **Hosted agents block some libraries.** An MHacks 2025 entrant hit "restrictions on python libraries" ([GamPL](https://devpost.com/software/gampl)). Debugging hosted agents was "non-trivial — logs were async" ([TA-DA](https://devpost.com/software/ta-da-intelligent-teaching-assistant)). **Use a mailbox agent on a laptop or a Render box** ([Render guide](https://innovationlab.fetch.ai/resources/docs/next/agentverse/deploy-agent-on-agentverse-via-render)).
- **ASI:One is request/response, not push.** "ASI:One treats sessions as complete after the first response". Running all agents in one `Bureau` "bypasses individual mailbox registration, causing 404s" ([Dispatch](https://devpost.com/software/dispatch-tabspl)). Design every workflow so the user asks and the agent acts, and send proactive alerts through another channel (Relay or Photon, §5).
- **Payment card timing.** "ASI:One only renders the payment card if `RequestPayment` arrives within milliseconds" ([AgenticHire](https://devpost.com/software/agentichire-2xyk0z)).
- **Address and key mix-ups.** Use your own `agent1q…` address, not the one in the docs. A 401 means you need to regenerate `ASI1_API_KEY` ([guide](https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/asi-compatible-uagents)).
- **Uptime during judging.** A mailbox agent answers only while its process runs. Keep a laptop on power and venue Wi-Fi, or deploy to Render. Keep the shared-chat URL as a recorded fallback.

---

## 2. What Fetch.ai's judges reward

### 2.1 The brief and rubric (2026, verified)

The [hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack) states the challenge as "From Intent to Action": "Most AI applications stop at conversation… The result should be more than a chatbot or a thin wrapper around an API." The rubric is unchanged from 2025 ([2025 page](https://www.fetch.ai/events/m-hacks)):

| Criterion | Weight | What the hackpack asks |
|---|---|---|
| Functionality & Technical Implementation | 25% | "Are the agents properly communicating and reasoning in real time?" |
| Use of Fetch.ai Technology | 20% | Registered on Agentverse? Chat Protocol? **Payment Protocol?** |
| Innovation & Creativity | 20% | "Solving a problem in a new or unconventional way?" |
| Real-World Impact & Usefulness | 20% | "How useful would this be to an end user?" |
| User Experience & Presentation | 15% | "Well-structured demo… smooth and intuitive user experience" |

### 2.2 MHacks 2025 Fetch winners (same sponsor and venue; 15 opt-ins, 3 winners)

| Prize | Project | What won it |
|---|---|---|
| Best Use of Fetch.ai ($1,250) | [MobiLens](https://devpost.com/software/mobilens) | Spectacles AR interface for people with paralysis, also controlled by voice. Two uAgents reachable through ASI:One. Caregiver alerts and smart-home control. **Hardware plus agents, high-stakes user** |
| Best Deployment on Agentverse ($750) | [deCluttered.ai](https://devpost.com/software/declutttered-ai) | Scans a room, prices items, generates listings, and lets agents negotiate with buyers. **Real-world action and a commerce loop** |
| Best Use of ASI:One ($500) | [Bazaar](https://devpost.com/software/bazaar-ai-agent-marketplace-fetch-ai) | Agent marketplace where tasks such as filing GitHub issues are paid in FET only after verification. **Payments with verification** |

The Devpost winner labels on each page confirm the prize names. Opt-ins were 14, 5 and 3, with a union of 15 ([gallery filter 90535](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90535), [90891](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90891), [90892](https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90892)).

### 2.3 Peer-event winners (48 verified Fetch-prize wins at 11 events; selection)

| Event | Winner | What it did, and why it fits the rubric |
|---|---|---|
| UC Berkeley AI Hackathon 2026 (Jun) | [LifeLink](https://devpost.com/software/lifelink-soibwr) (2-person team) | A nurse types "Need 5 units B+" in **ASI:One**. Hospital, discovery, center, donor, custody and payment agents source the blood, hold **Stripe** escrow and keep a hash-chained custody log. Its write-up says "no invented inventory" |
| UC Berkeley AI 2026 | [AgriBroker](https://devpost.com/software/agribroker) | "500 tomatoes under $250": orchestrator, registry and farmer agents, a deterministic optimizer and Stripe Checkout. Framed as **food-waste reduction**, the only sustainability-framed winner I found |
| DiamondHacks 2026 (Apr) | [AgenticHire](https://devpost.com/software/agentichire-2xyk0z) | "Open ASI:One and type one sentence." 5 agents write the job description, scout, rank and send **real SendGrid emails**. In the demo, emails reached "Fetch.ai Innovation Lab contributors who were judging" the event. Uses the Chat and Payment protocols with FET on testnet |
| TreeHacks 2026 (Feb) | [AgentPlace](https://devpost.com/software/agentplace) | About 24 negotiating agents for client/contractor jobs, with the **Payment Protocol** verified on-chain. Won Best Overall AI Agent ($2,500). Lesson: "the hardest part of agentic systems isn't the AI -- it's the orchestration" |
| Cal Hacks 12.0 (Oct 2025) | [Orbit](https://devpost.com/software/orbit-n97hqz) | Turns meetings and Omi-mic voice into Jira tickets, Gmail emails and Calendar events through Agentverse agents and Composio MCP. **Hardware input, real tool actions** |
| LA Hacks 2026 (Apr) | [Pols 15](https://devpost.com/software/pols-15) | A campaign toolbox run "through just a asi:1 chat". **The whole workflow happens in ASI:One** |
| UC Berkeley AI 2025 | [AlphaRescue](https://devpost.com/software/alpharescue) | Medical-emergency dispatch: uAgents assess the situation and VAPI places voice calls to notify authorities |
| UC Berkeley AI 2026 | [Vanguard Telematics](https://devpost.com/software/vanguard-telematics) | Fire-truck crash sensing on STM32 and Raspberry Pi, with uAgents. **Hardware** |

Full winner lists, each checked for a Fetch "Winner" label on the project page: [Cal Hacks 12.0](https://cal-hacks-12-0.devpost.com/project-gallery), [TreeHacks 2026](https://treehacks-2026.devpost.com/project-gallery), [LA Hacks 2026](https://la-hacks-2026.devpost.com/project-gallery), [UC Berkeley AI 2026](https://ai-hackathon-2026.devpost.com/project-gallery), [DiamondHacks 2026](https://diamondhacks-2026.devpost.com/project-gallery), [Hack@Brown 2026](https://hack-brown-2026.devpost.com/project-gallery), [Hack Dearborn 4](https://hackdearborn4.devpost.com/project-gallery), [LA Hacks 2025](https://la-hacks-2025.devpost.com/project-gallery), [UC Berkeley AI 2025](https://uc-berkeley-ai-hackathon-2025.devpost.com/project-gallery), [SpartaHack X](https://spartahack-x.devpost.com/project-gallery), [MHacks 2025](https://mhacks-2025.devpost.com/project-gallery).

### 2.4 Patterns (my tally of the 48 winners' taglines and pages; inference)

1. **Closing the loop wins.** Every detailed winner I read takes a real action: it sends email, books, pays, files a ticket or moves hardware. "Thin wrapper" is the brief's explicit anti-pattern.
2. **Several agents with distinct roles.** LifeLink, AgenticHire, AgentPlace, AgriBroker and EDFlow AI all name their agents by job. "Use of Fetch tech" (20%) rewards visible agent-to-agent traffic. AgriBroker showed "agent traces" in its demo.
3. **High-stakes domains dominate.** About **17 of 48** winners are health, emergency or accessibility projects (Haven, EDFlow, LifeLink, CareLoop ×2, Fireflai, MobiLens, Lumos, AlphaRescue, MayDay and others). About 10 are productivity or dev tools, 7 commerce, and 5 hiring.
4. **Payments help.** About **10 of 48** winners take payments (Stripe or FET). The criterion text names the Payment Protocol directly.
5. **Physical surfaces are welcome.** About 7–8 winners have a hardware, wearable or AR front end: MobiLens, Orbit, Vanguard, RIIS, Edith, Lumos, InterViewAR, Hire Vision.
6. **Showmanship that involves the judges works.** AgenticHire emailed the judges. A judge's inbox, or a device on the table, makes the action concrete.
7. **Sustainability is nearly absent** (1 of 48). That is a differentiation opportunity on Innovation (20%), not evidence that the judges dislike it.

---

## 3. Prize value and expected competition

### 3.1 Prize value (team of 4)

| Place | Cash | Per member | Extra |
|---|---|---|---|
| 1st | $1,250 | ≈ $312 | Internship interview opportunity ([hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)) |
| 2nd | $750 | ≈ $187 | Internship interview |
| 3rd | $500 | $125 | Internship interview |

The prize is cash, so face value equals realistic value. Of the 12 sponsor tracks, only Fetch, SpacetimeDB ($1,000 / $500 / $200), Photon ($400 / $200 plus credits) and FinchNode ($500 at 2nd) pay cash ([Devpost](https://mhacks-2026.devpost.com/)).

### 3.2 Expected competition: **medium**

Method: Devpost's prize filter lists the submissions that selected a prize. I took the union across each event's Fetch prizes, divided by the event's gallery size, and confirmed winners on each project page.

| Event (Fetch prize type) | Projects | Fetch opt-ins | Share | Fetch winners |
|---|---|---|---|---|
| **MHacks 2025** (3 sponsor prizes, $2,500) | 122 | 15 | **12%** | 3 |
| Cal Hacks 12.0 (3 sponsor prizes) | 699 | 83 | 12% | 6 |
| TreeHacks 2026 (sponsor prize, $5,000) | 376 | 28 | 7% | 4 |
| UC Berkeley AI 2026 (sponsor prize, $3,000) | 399 | 86 | 22% | 9 |
| DiamondHacks 2026 | 134 | 23 | 17% | 3 |
| Hack@Brown 2026 ($750 / $500) | 62 | 11 | 18% | 1 |
| Hack Dearborn 4 (Michigan, Oct 2025) | 69 | 32 | 46% | 3 |
| UC Berkeley AI 2025 | 330 | 41 | 12% | 3 |
| SpartaHack X (Michigan) | 115 | 7 | 6% | 1 |
| *LA Hacks 2025 (Fetch was a pick-one **main track**)* | 172 | 33 | 19% | 4 |
| *LA Hacks 2026 (main track plus 2 sponsor prizes)* | 306 | 99 | 32% | 11 |

Sources: each event's gallery and prize filter (links in §2.3 and Sources). Among the 9 sponsor-prize events, the **median is 12% and the mean 17%**.

**Answer to "the largest cash prize: how crowded does that make it?"** The data shows no link between pool size and crowding:
- TreeHacks put $5,000 on the table and drew 7%.
- Hack Dearborn 4, a Michigan event whose prize amounts I did not check, drew 46%.

*Inference:* opt-in tracks friction and on-site promotion, not dollars. The friction here is real: Agentverse, the Chat Protocol, an in-ASI:One workflow and a second submission.

**MHacks 2026 estimate (inference):**
- About 120–150 projects (122 in 2025).
- 12–22% Fetch opt-in, so **≈15–30 opt-ins, central 20**.
- Perhaps half of those meet every mandatory requirement. Some opt-ins only call an LLM API: [Mood Mapping](https://devpost.com/software/mood-mapping) wired an ASI1 chatbot into its own app. That leaves **≈8–12 credible rivals for 3 slots**.

Pressure is upward this year. Relay and Photon pull teams toward agents, and "about half of 2025 projects were LLM-based" (verdict file). So I call it **medium**, not low.

---

## 4. Expected value

**Base rate.** At MHacks 2025, 3 of 15 Fetch entrants won, a 20% chance per entrant. At the peer events the rate runs from 7% to 14%. A strong team adds every bonus item:
- 2–3 role agents
- Review/Form cards
- a real action in front of the judge
- clean README and video
- live data

*My estimate:* **P(1st) ≈ 10%, P(2nd) ≈ 10%, P(3rd) ≈ 10%**, so about 30% to place.

| Scenario | P(1st / 2nd / 3rd) | EV (cash) | Fetch-specific hours | EV per hour |
|---|---|---|---|---|
| Bolt-on: one agent wrapping an LLM, minimal README | 2% / 3% / 4% | ≈ $70 | 2–3 | ≈ $28/h |
| **Full-compliance, agent core from hour one (recommended)** | **10% / 10% / 10%** | **≈ $250** | **≈ 6** | **≈ $42/h** |
| Full-compliance plus Stripe Payment Protocol with a credible model | 12% / 12% / 10% | ≈ $290 | 8–9 | ≈ $34/h |

None of these include the internship interviews.

**Against the other sponsor tracks.** These are the sibling advocates' own EV estimates, which are inference:

| Track | Their estimate | Source file |
|---|---|---|
| FREE-WILi | ≈ $180–480 (kit-value dependent) | `04-free-wili.md` |
| Neon | ≈ $130 realistic, ~$40/h | `05-neon-backend.md` |
| FinchNode | ≈ $110–225 | `10-finchnode-healthtech.md` |
| Photon | ≈ $80, ~$20–25/h | `06-photon-imessage-agents.md` |
| Notability | ≈ $80, ~$40 per person-hour | `03-notability-trust-the-process.md` |
| ElevenLabs | ≈ $10–50 realistic | `02-elevenlabs.md` |
| Figma | ≈ $23 | `09-figma-best-design.md` |

The FREE-WILi advocate independently put Fetch at "~$200 – $375", and the Notability advocate called Fetch and SpacetimeDB the tracks that "win on absolute EV". **Fetch has the highest cash EV on the board.** Per hour it ties for the lead.

---

## 5. Stacking

The judge recommended **Sustainability + Judged by an LLM**, with SpaceX as the team's bias.

| Track | Fit | How it fits in one project |
|---|---|---|
| **Sustainability (main)** | **Strong** | Track text: "rethink energy, climate, and resource systems". An agent that turns climate intent into action ("run my laundry when MISO is cleanest") matches Fetch's brief, and only 1 of 48 Fetch winners was green, so it stands out |
| Actually Intelligent (main) | Strongest *thematically*, worst *crowd* | Most native, but the verdict file puts AI as the most crowded main track. Not worth switching |
| Beyond the Code (main) | Good | Mailbox agents run on your laptop and can drive USB devices. 7–8 Fetch winners had physical front ends |
| FinTech (main) | Good with Fetch, bad for the team's stack | Payment Protocol and Nessie fit, but it breaks SpaceX (verdict file) |
| **Judged by an LLM (fun)** | **Strong** | Fetch already forces a public repo, a README with agent addresses and a clean architecture, which is good material for an AI judge (*inference*) |
| Useless AI / Dumbest Idea (fun) | **Conflict** | Real-World Impact is 20%, and the brief says to "avoid simple chatbots" |
| **SpaceX: Make it Legendary** | **Good** | SpaceX needs real space data, Cursor, and Grok Imagine or the Voice API ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). The agent's data tool pulls NASA FIRMS or POWER satellite data ([Earthdata FIRMS](https://www.earthdata.nasa.gov/data/tools/firms), [POWER API](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/)). A Grok Imagine image appears **inside ASI:One** as a Markdown image ([image agent](https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/image-generation-agent)). Build in Cursor, optionally with the Agentverse MCP. Whether SpaceX accepts Earth-observation data is unverified (verdict file) |
| **Relay** | **Good, complementary** | Relay requires that "Your agent must work in the Relay app" ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). Use one agent core with two front doors. Relay handles the text, call and push that ASI:One lacks (§1.6), and ASI:One handles the discovery-and-action flow for Fetch judges. Cost: +2–3 h for the second adapter (*inference*) |
| Photon | Good, same pattern as Relay | Choose Relay or Photon as the push channel, not both, unless time allows |
| Neon | Strong, cheap | Store agent state, the action log and audit trail in Postgres. LifeLink used a shared DB the same way |
| FREE-WILi | Strong | The "actuator agent" is a local mailbox uAgent attached to the board. "A device on the table turns off" is the physical version of AgenticHire's judge email |
| SpacetimeDB | Possible, heavy | Its brief lists "AI agent coordination" and "auctions / marketplaces" ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)). It fits Sketch C, but it is a second real-time paradigm on top of Fetch |
| Capital One Nessie | Weak here | Fits only a FinTech-shaped build |
| FinchNode | Conflicts with Sustainability | It is Fetch's most-rewarded theme (health), but adding it means two main stories |
| ElevenLabs | Weak to moderate | ASI:One is a text chat. Voice belongs on the Relay call side |
| Figma / Notability | Free | The UX & Presentation criterion is 15% and benefits from design work |

**Recommended stack** (one story): Sustainability + Judged by an LLM + **Fetch.ai** + SpaceX + Relay (or Photon) + Neon + FREE-WILi (if hardware is on hand) + Figma + Notability.

**Architecture rule:** build the brain once as uAgents (planner, data, actuator), then add thin front doors for ASI:One, Relay and the web dashboard.

---

## 6. Winning project sketches

### A. "Clean Hours": an agent that shifts your power use to the cleanest grid hours and flips the switch (Sustainability · Fetch · FREE-WILi · Neon · Judged by an LLM · SpaceX optional)

- **The flow.** In ASI:One, the user types: "@cleanhours dry my laundry and pre-cool my room tonight when the grid is cleanest."
  - A **Grid agent** reads live MISO carbon intensity ([Electricity Maps](https://app.electricitymaps.com/datasets?zone=US-MIDW-MISO)). For the solar-aware version, it also reads NASA POWER satellite irradiance, which is the SpaceX hook.
  - A **Planner agent** picks the windows and returns a **Review card**: "Dryer 1:40–2:40 AM, AC 4–5 AM, saves ≈ X kg CO₂, Confirm / Edit".
  - On Confirm, an **Actuator agent** (a local mailbox uAgent) uses the **FREE-WILi** IR transmitter to switch a fan or AC. It writes a calendar hold and logs the action in **Neon**.
- **Demo moment.** A judge types the request, and the fan on the table turns off on schedule.
- **Rubric fit:**
  - real-time data (bonus)
  - multi-agent (bonus)
  - cards (bonus)
  - real action (functionality)
  - novel domain for Fetch (innovation)
- **Precedent.** It extends the sustainability advocate's "Gridlock" sketch (`../main-and-fun-tracks/01-main-sustainability.md`) and Wattson's 2025 win ([Devpost](https://devpost.com/software/wattson-5btsyd)).
- **Risk.** Hardware availability. The fallback is a smart-plug API or a simulated device with a visible state.

### B. "Smoke Signal": a wildfire-smoke and air-quality agent that acts for you (Sustainability/climate resilience · Fetch · SpaceX · Relay · Neon · Judged by an LLM)

- **The flow.** "@smokesignal I coach a U-M club team. Is Saturday's outdoor practice safe, and fix it if not."
  - A **Satellite agent** pulls **NASA FIRMS** fire detections from the MODIS/VIIRS satellites ([FIRMS](https://www.earthdata.nasa.gov/data/tools/firms)).
  - An **Air agent** pulls the **AirNow** forecast ([AirNow API](https://docs.airnowapi.org/)).
  - A **Planner** decides. If the AQI forecast crosses the threshold, it moves practice indoors, drafts and sends the roster notice, and creates the calendar change.
  - A Review card shows evidence: the hotspot map image (Grok Imagine renders a "smoke over Ann Arbor" visual beside the hard numbers) and AQI by hour.
  - **Relay** texts or calls team members proactively, which ASI:One can't do.
- **Why it wins.** It blends the theme Fetch judges reward most (health and safety: AlphaRescue, Fireflai, LifeLink) with a climate frame almost no Fetch entrant uses. It carries real space data for SpaceX.
- **Risk.** No live smoke event in October Michigan (*inference*). Demo with a replayed historical day, such as the June 2023 Canadian-smoke episode (*unverified as a dataset choice*), and say so openly.

### C. "Leftover Launch": a campus food-rescue marketplace (Sustainability · Fetch with Payment Protocol · Relay · SpacetimeDB or Neon · Judged by an LLM)

- **The flow.**
  - Dining halls and event hosts post surplus food: "@leftoverlaunch 40 sandwiches at Pierpont until 3 PM."
  - A **Host agent** lists it, a **Matcher agent** finds nearby students or food pantries, and a **Claim agent** reserves portions.
  - A refundable $1 no-show deposit runs through the **Stripe Payment Protocol** ([Fetch-skills](https://innovationlab.fetch.ai/resources/docs/next/fetch-skills/skills-reference)). That is the "credible monetization model" bonus.
  - **Relay** pings students. Relay's own idea list includes "Food: dining halls, free food" ([Tracks & Prizes](https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5)).
  - **SpacetimeDB** can hold the live claims board.
- **Precedent.** It reuses AgriBroker's winning pattern (orchestrator, registry, sellers, Stripe, food waste) ([Devpost](https://devpost.com/software/agribroker)).
- **Trade-off.** It drops SpaceX. Pick it only if the team ranks Relay and SpacetimeDB above SpaceX.

*My pick:* **B** if the team is all-in on SpaceX. **A** if a FREE-WILi board or another IR target is confirmed by Saturday afternoon.

---

## 7. Red flags, the best counterarguments, and rebuttals

| Rival argument | Rebuttal |
|---|---|
| **"Agents are everywhere, so Fetch will be the most crowded track."** | The measured median is 12% opt-in, and 12% at MHacks 2025 specifically. Most AI-agent projects never register on Agentverse. The requirements gate the field. I still rate it medium, not low |
| **"Too many hoops: Agentverse, the Chat Protocol, the in-ASI:One workflow, a second submission, a video."** | True, and it is the main cost. It comes to about 6 hours, and most of that is the agent logic you need anyway. The 2 PM Saturday workshop, Fetch-skills and the hackpack quickstart cut the ramp |
| **"The ASI:One chat UI makes a weak demo and drags down the main-track pitch."** | Only Fetch's *primary workflow* must run in ASI:One. The main-track demo can use a dashboard or Relay. Interactive Cards (Review, Form, Carousel) turn the chat into a real UI, and a physical or inbox action carries the room |
| **"Live demo fragility: the mailbox agent depends on your laptop and venue Wi-Fi."** | Valid. Mitigations: deploy to Render, `@handle` direct mention, a recorded shared-chat URL in the submission, and the video. Judges can replay all of these |
| **"It's a crypto company; FET payments look sketchy."** | Payments are bonus-only, and Stripe test mode is a first-class rail. Winners used both |
| **"Split three ways, 3rd is only $500."** | Three cash slots means the highest *probability* of some cash on the board, and even 3rd beats most sponsor 1sts in cash terms |
| **"Fetch judges reward health and commerce, not climate."** | Real uncertainty: 1 of 48 winners was green. The rubric is domain-neutral, though, and Sketch B deliberately borrows the health and safety signal |
| **"New SDK release the day before."** | Pin `uagents==0.25.5`, the version the ASI guide uses, and test the Inspector connection by 3 PM Saturday |
| **"Fetch was not on the team's shortlist."** | It doesn't displace SpaceX or Relay. It plugs into both and adds the biggest sponsor cash pool to the same project |

**Honest red flags I can't rebut:**
1. 2026 judges are unannounced.
2. Free-tier quotas are unverified.
3. The exact Submission Agent deadline isn't stated. Assume Devpost's 12 PM Sunday.
4. My win probabilities rest on n = 15 at MHacks 2025 plus peer events.

---

## 8. Scorecard (1–10)

| Dimension | Score | One-line justification |
|---|---|---|
| Prize value | **9** | Largest sponsor cash pool ($2,500), three cash places, plus internship interviews |
| Win probability | **6** | ≈30% to place for a full-compliance entry. Estimated 15–30 opt-ins, about 8–12 credible, for 3 slots. MHacks 2025 had 3 winners among 15 entrants |
| Integration ease | **6** | About 6 hours of Python-only work with several moving parts (mailbox, Chat Protocol, cards, two submissions), plus an SDK release the day before |
| Stacking potential | **7** | Native with Sustainability, Judged by an LLM, Neon and FREE-WILi; workable with SpaceX and Relay; conflicts with the two joke tracks and with FinchNode/Capital One in this stack |
| Demo impact | **6** | A chat UI is plain on its own. Cards plus a real action (device or inbox) lift it, as AgenticHire showed |
| Fit with team preferences | **7** | Not on the shortlist, but it strengthens the SpaceX and Relay picks, needs no FinTech, and suits a software-strong team |

**Unweighted mean ≈ 6.8.**

---

## 9. Action items for Saturday (today, Oct 3)

1. **By 12:30 PM:** one teammate creates ASI:One and Agentverse accounts and redeems `MHACKS26` / `MHACKSAV`. Pin `uagents==0.25.5` on Python 3.12.
2. **12:30–2:00 PM:** run the hackpack quickstart as a mailbox agent and get an `@handle` reply in ASI:One. Only then design the role agents.
3. **2:00 PM:** attend the **FetchAI workshop (Duderstadt 3336)**. Ask three questions:
   - Who judges?
   - Do shared-chat URLs count for "bonus points"?
   - Is the video mandatory?
4. **By 6 PM:** the end-to-end flow works in ASI:One with one real action. Add the Review card next.
5. **Overnight:** README with addresses and badges; ≥10 interactions; optional Stripe payment.
6. **Sunday by 11:30 AM:** record the 3–5 min video, share the chat URL, submit through the Submission Agent and have all teammates join, then submit on Devpost (deadline 12 PM).

---

## Sources

**Fetch.ai and MHacks primary sources**
- Fetch.ai MHacks 2026 hackpack (requirements, rubric, bonus, codes, quickstart): https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack
- Fetch.ai MHacks 2026 event page (prizes; judges and mentors empty): https://www.fetch.ai/events/mhacks-2026
- Fetch.ai MHacks 2025 event page (judges, mentors, 2025 prize criteria): https://www.fetch.ai/events/m-hacks
- Fetch submission process doc (Submission Agent fields, Team ID, status): https://docs.google.com/document/d/1UDW-X1C24hxZviFOQzjTeh0pXRNAoflMb8lhJqZP9Z0
- MHacks 2026 Tracks & Prizes: https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5
- MHacks 2026 Hacker Handbook (judging 12:30–2:30, presence rule): https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af
- MHacks 2026 Devpost (full prize list, deadline): https://mhacks-2026.devpost.com/
- MHacks 2026 schedule, Saturday (FetchAI workshop 2 PM): https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365
- MHacks 2026 schedule, Sunday (judging, closing): https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=83169850

**Fetch.ai technical docs**
- ASI-compatible uAgents guide: https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/asi-compatible-uagents
- uAgent creation and hosting options: https://innovationlab.fetch.ai/resources/docs/agent-creation/uagent-creation
- Launching an ASI:One-compatible agent (External Integration): https://docs.agentverse.ai/documentation/launch-agents/launch-asi-one-compatible-u-agent
- Agent discovery setup guide: https://docs.agentverse.ai/documentation/agent-discovery/setup-guide
- How AI agents are ranked (Agentverse blog): https://agentverse.ai/blog/how-ai-agents-are-ranked
- ASI Interactive Cards: https://innovationlab.fetch.ai/resources/docs/interactive-cards/asi-interactive-cards
- Image-generation agent (Markdown images in ASI:One): https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/image-generation-agent
- ASI:One quickstart: https://innovationlab.fetch.ai/resources/docs/asione/asi-one-quickstart
- ASI:One models: https://docs.asi1.ai/documentation/models
- Agent Payment Protocol (Innovation Lab): https://innovationlab.fetch.ai/resources/docs/agent-transaction/agent-payment-protocol
- Agent Payment Protocol (uAgents docs): https://uagents.fetch.ai/docs/guides/agent-payment-protocol
- Fetch-skills reference: https://innovationlab.fetch.ai/resources/docs/next/fetch-skills/skills-reference
- Agentverse MCP: https://docs.agentverse.ai/documentation/advanced-usages/agentverse-mcp
- Deploy agent via Render: https://innovationlab.fetch.ai/resources/docs/next/agentverse/deploy-agent-on-agentverse-via-render
- uagents on PyPI (v0.26.0, 2026-10-02): https://pypi.org/pypi/uagents/json
- uAgents GitHub repo stats: https://api.github.com/repos/fetchai/uAgents

**Winners and opt-in data (Devpost)**
- MHacks 2025 gallery: https://mhacks-2025.devpost.com/project-gallery
- MHacks 2025 Fetch prize filters: https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90535 · https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90891 · https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90892
- MobiLens: https://devpost.com/software/mobilens
- deCluttered.ai: https://devpost.com/software/declutttered-ai
- Bazaar: https://devpost.com/software/bazaar-ai-agent-marketplace-fetch-ai
- Cal Hacks 12.0 gallery: https://cal-hacks-12-0.devpost.com/project-gallery (filters 91876, 92086, 92087)
- TreeHacks 2026 gallery: https://treehacks-2026.devpost.com/project-gallery (filter 96836)
- LA Hacks 2026 gallery: https://la-hacks-2026.devpost.com/project-gallery (filters 98455, 101252, 101584)
- LA Hacks 2025 gallery: https://la-hacks-2025.devpost.com/project-gallery (filter 84607)
- UC Berkeley AI Hackathon 2026: https://ai-hackathon-2026.devpost.com/ and https://ai-hackathon-2026.devpost.com/project-gallery (filter 103363)
- UC Berkeley AI Hackathon 2025 gallery: https://uc-berkeley-ai-hackathon-2025.devpost.com/project-gallery (filter 87889)
- DiamondHacks 2026 gallery: https://diamondhacks-2026.devpost.com/project-gallery (filter 99096)
- Hack@Brown 2026 gallery: https://hack-brown-2026.devpost.com/project-gallery (filter 95586)
- Hack Dearborn 4 gallery: https://hackdearborn4.devpost.com/project-gallery (filters 91220, 91221, 91222)
- SpartaHack X gallery: https://spartahack-x.devpost.com/project-gallery (filters 83344, 83348, 83349)

**Individual winner pages**
- LifeLink: https://devpost.com/software/lifelink-soibwr
- AgriBroker: https://devpost.com/software/agribroker
- AgenticHire: https://devpost.com/software/agentichire-2xyk0z
- AgentPlace: https://devpost.com/software/agentplace
- Orbit: https://devpost.com/software/orbit-n97hqz
- Pols 15: https://devpost.com/software/pols-15
- AlphaRescue: https://devpost.com/software/alpharescue
- Vanguard Telematics: https://devpost.com/software/vanguard-telematics

**Pages cited for gotchas**
- GamPL: https://devpost.com/software/gampl
- TA-DA: https://devpost.com/software/ta-da-intelligent-teaching-assistant
- Dispatch: https://devpost.com/software/dispatch-tabspl
- Mood Mapping: https://devpost.com/software/mood-mapping
- Wattson (2025 sustainability/hardware precedent): https://devpost.com/software/wattson-5btsyd

**Data sources for the sketches**
- NASA FIRMS: https://www.earthdata.nasa.gov/data/tools/firms
- NASA POWER hourly API: https://power.larc.nasa.gov/docs/services/api/temporal/hourly/
- Electricity Maps, MISO zone: https://app.electricitymaps.com/datasets?zone=US-MIDW-MISO
- AirNow API: https://docs.airnowapi.org/

**Local files relied on (sibling research; their claims carry their own citations)**
- `/Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md`
- `/Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/01-main-sustainability.md`
- `/Users/anvaytodkar/Code/mhacks/results/year-research/2025.md`
- `/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/02-elevenlabs.md`
- `/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/03-notability-trust-the-process.md`
- `/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/04-free-wili.md`
- `/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/05-neon-backend.md`
- `/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/06-photon-imessage-agents.md`
- `/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/09-figma-best-design.md`
- `/Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/10-finchnode-healthtech.md`

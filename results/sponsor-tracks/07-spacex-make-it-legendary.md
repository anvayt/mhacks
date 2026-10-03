# Sponsor Track Advocate — Make it Legendary (SpaceX)

## Prompt given (excerpt)
> You are the advocate for the sponsor track "Make it Legendary (SpaceX)" at MHacks 2026. Research the sponsor's tech and how fast a team can integrate it, what its judges reward, prize value vs competition, expected value, how it stacks with the main/fun picks and other sponsors, 2–3 winning project sketches, honest red flags, and a 1–10 scorecard. Make the strongest honest case — an impartial judge will weigh your file against eleven other sponsor advocates.

Tags: **[V]** I verified it myself (fetched the page, called the API, or counted it). **[R]** reported by a secondary source I could not open directly. **[I]** my inference. **[U]** unverified, so ask on site.

---

## 0. The case in brief

- **Who the sponsor is [V].** "SpaceXAI" is SpaceX's AI division. SpaceX acquired xAI on Feb 2, 2026 and rebranded it as SpaceXAI in July 2026 ([Wikipedia: SpaceXAI](https://en.wikipedia.org/wiki/SpaceXAI)). SpaceX also bought **Cursor**: the $60B deal closed Aug 14, 2026, and Cursor "is being integrated into the SpaceXAI team" ([Wikipedia: Cursor](https://en.wikipedia.org/wiki/Cursor_(company))). So the rule "must be built with Cursor" is the sponsor asking you to use **its own** editor. Grok, Grok Imagine, Grok Voice, Grok Bot and Cursor are all one company now.
- **The exact rules [V]** ([Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)):
  - "Real space data goes in and a legendary project comes out."
  - "To be eligible, your project must be built with Cursor. **The more you use Cursor, the more likely you are to win.** You must also use the Grok Imagine or Voice API in your project."
  - "Bonus points, if you use Grok Bot for project planning and team collaboration."
  - The brief also mentions "enormous public datasets, decades of missions, and a literature no human can read all of."
  - Prize: "SpaceXAI Mechanical Keyboards." Every entrant goes into a raffle for a Cursor Owala bottle.
- **Honest verdict on the team's lean.** The lean is right for the wrong reason if the reason is the prize. Unverified, the keyboards are worth maybe $400–1,000 for four people, and there is likely one winner. That puts SpaceX in the **bottom third of sponsor tracks on dollar expected value**. The lean is right if the reason is **domain**:
  - Space gives a software team free, rich, real-time data and a demo that looks like mission control.
  - Integration is cheap: Cursor costs nothing extra, and Grok Imagine is about $0.04 per image.
  - SpaceX shares one voice agent with Relay. Relay's own docs list Grok as a supported "brain."
  - It carries visibility with the company that now owns Grok, X and Cursor.
- **The condition for winning.** Space has to be the **core** of the product, not a garnish. At the closest twin event, DivHacks 2026, **45% of projects (29 of 65) opted in** [V]. Only 18 of those even mentioned Grok on their Devpost page [V]. The Grand Prize winner opted in, but it used Grok Bot and Gemini instead of the Grok Imagine or Voice API, and it did **not** win the SpaceXAI prize [V]. Garnish entries are numerous and lose.
- **Recommended play.** Keep the verdict's **Sustainability + Judged by an LLM**. Build **"Overpass"** (§6A): satellite fire detections plus the live orbits of the satellites that made them, behind a Grok Voice agent you can call in Relay.
  - Overpass turns the verdict's open risk ("does Earth-observation data count as space data?") into a non-issue. The product computes real spacecraft orbits and pass times, so it is unambiguously space data.
  - Still ask at the SpaceXAI session, **Sat 4–5 PM, Duderstadt VR Lab** [V] ([schedule](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365)).
- **Scorecard:** prize 3 · win probability 4 · integration ease 8 · stacking 7 · demo impact 8 · fit with team preferences 9.

---

## 1. The technology

### 1.1 What each required piece is
| Piece | What it is | Access and cost | Evidence |
|---|---|---|---|
| **Cursor** (required) | AI code editor, now a SpaceXAI subsidiary | A free Hobby tier exists. The 1-year free Pro deal for students may have ended (sources conflict) [R]. SpaceXAI handed out **free Cursor Pro months** at HackCMU and at a HackPrinceton build night [R]. MHacks has not announced codes [U]. | [Wikipedia: Cursor](https://en.wikipedia.org/wiki/Cursor_(company)), [student-deal status](https://whichai.fyi/blog/cursor-student-discount-2026/), [HackCMU X post](https://x.com/SERobinsonJr/status/2099897963938263072), [Princeton event](https://www.princeton.edu/events/2026/spacexai-x-hackprinceton-grok-bot-build-night) |
| **Grok Imagine API** (one of two options) | Image and video generation. `grok-imagine-image-2.0` and `grok-imagine-video-1.5`. Endpoints: `POST /v1/images/generations`, `/v1/images/edits` (up to 5 reference images), `/v1/videos/generations` (async, up to 15 s). | **$0.04 per image** and **$0.08 per second of video** [V] | [Imagine guide](https://docs.x.ai/docs/guides/image-generations), [pricing](https://docs.x.ai/developers/pricing) |
| **Grok Voice API** (the other option) | Realtime speech-to-speech agent over WebSocket (`wss://api.x.ai/v1/realtime?model=grok-voice-latest`). Supports custom function calling, server-side web/X search, collections and **remote MCP**, 20+ languages, voice cloning, and ephemeral tokens for browsers. Also offers TTS and STT. | Speech-to-speech **$0.08/min** + $0.004 per text input. TTS $15 per 1M characters [V] | [Voice agent docs](https://docs.x.ai/developers/model-capabilities/audio/voice-agent), [Voice overview](https://docs.x.ai/developers/model-capabilities/audio/voice), [pricing](https://docs.x.ai/developers/pricing) |
| **Grok Bot** (bonus points) | "A team of always-on agents" tied to Cursor. **Team Bots** are one shared bot the whole team chats with in the Grok Bot app or **Slack**. Teammates link Slack to their Cursor accounts. | It launched for top-tier plans. Access later extended to **Cursor Pro ($20/mo)** with a free trial [R] | [MacRumors](https://www.macrumors.com/2026/08/11/grok-bot-macos-ios/), [9to5Mac](https://9to5mac.com/2026/09/04/spacexai-expands-grok-bot-to-ipad-as-access-expands-to-cheaper-plans/), [Team Bots docs](https://docs.x.ai/grok-bot/team-bots) |

**xAI API signup:** you create an account at console.x.ai and "load it with credits to start using the API." It is OpenAI-SDK-compatible at `https://api.x.ai/v1` [V] ([quickstart](https://docs.x.ai/docs/tutorial)). I found no free tier [V, absence]. SpaceXAI handed out **Grok API credits** at HackCMU [R] and at DivHacks ("All entrants receive Cursor and Grok credits") [V] ([DivHacks](https://divhacks-2026.devpost.com/)). Whether it does so at MHacks is [U], so check the Sponsor Expo or the Grok Bot booth.

The worst case without credits is cheap [I]: 150 images ($6) + 60 voice minutes ($5) + text calls is about **$15 total**.

### 1.2 "Real space data": what is usable today (I probed every endpoint on 2026-10-03)
| Source | What you get | Access / limits | Status |
|---|---|---|---|
| **r/SpaceX API** (`api.spacexdata.com`) | SpaceX launches, cores, Starlink | — | ❌ **Down.** It returns Cloudflare **525**, and the GitHub repo is **archived** (last push Aug 2024) [V] ([repo](https://github.com/r-spacex/SpaceX-API)). Many teams will try this first and lose an hour. |
| **Launch Library 2** (The Space Devs) | Every launch (735 past SpaceX launches), upcoming launches, agencies, pads | No key needed. **15 requests/hour per IP** [V] ([throttle endpoint](https://ll.thespacedevs.com/2.3.0/api-throttle/)). The venue Wi-Fi probably shares one public IP across hundreds of hackers [I], so cache from minute one. `lldev.thespacedevs.com` also responds [V]. | ✅ |
| **CelesTrak GP/TLE** | Live orbital elements for ISS, Starlink, and Earth-observation satellites (Terra, Aqua, Landsat 8/9, Sentinel-2A/B/C in `GROUP=resource`; Suomi NPP, NOAA-20/21 in `GROUP=weather`) [V] | No key. Data refreshes every 2 h. Repeated downloads earn a **403, then a firewall ban**. "Active and Starlink GROUP data now restrict to one download per update cycle" [V] ([formats & policy](https://celestrak.org/NORAD/documentation/gp-data-formats.php)). The Starlink group is 4.7 MB and took 14 s [V]. | ✅ (download once, cache) |
| **CelesTrak SOCRATES** | Close-approach (conjunction) reports | Public page [V] ([SOCRATES](https://celestrak.org/SOCRATES/)) | ✅ |
| **NASA FIRMS** | Active-fire detections **per satellite** (`VIIRS_SNPP_NRT`, `VIIRS_NOAA20_NRT`, `VIIRS_NOAA21_NRT`, `MODIS_NRT`, `LANDSAT_NRT`). Ultra-real-time data arrives "in less than 60 seconds of satellite fly over for much of the US and Canada" [V] | Free MAP_KEY, 5,000 transactions per 10 min [V] ([area API](https://firms.modaps.eosdis.nasa.gov/api/area/), [Earthdata](https://www.earthdata.nasa.gov/data/tools/firms)) | ✅ |
| **api.nasa.gov** (NeoWs, APOD…) | Asteroids, picture of the day, etc. | `DEMO_KEY` showed `x-ratelimit-limit: 10` and APOD returned **500** during my test [V]. Register a free key. | ⚠️ |
| **JPL SBDB Close-Approach API** | Asteroid close approaches (17 within 0.05 au in the next 30 days) | No key [V] ([cad.api](https://ssd-api.jpl.nasa.gov/cad.api?dist-max=0.05&date-min=now&date-max=%2B30)) | ✅ |
| **NOAA SWPC** | Space weather (planetary Kp index) | No key [V] ([Kp JSON](https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json)) | ✅ |
| **NASA Exoplanet Archive (TAP)** | 40,194 rows in `ps` | No key [V] ([TAP](https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+count(*)+from+ps&format=json)) | ✅ |
| **NASA ADS** | The "literature no human can read all of": astronomy and space-science papers | Needs a free account and token. My test without one returned 401 [V]. Daily quotas are per endpoint, e.g. 5,000 [V] ([ADS dev API](https://github.com/adsabs/adsabs-dev-api)). | ✅ (sign up first) |
| **wheretheiss.at**, **NASA Image Library** | ISS position, NASA imagery | No key [V] ([ISS](https://api.wheretheiss.at/v1/satellites/25544), [images](https://images-api.nasa.gov/search?q=starship&media_type=image)) | ✅ |
| **SpaceX's own Starlink numbers** | Starlink performed **207,152 collision-avoidance maneuvers** from Dec 2025 to May 2026, per SpaceX's FCC semiannual report as covered by the press [R] | Press coverage ([Space.com](https://www.space.com/space-exploration/satellites/every-spacex-starlink-satellite-has-to-dodge-a-collision-almost-weekly-and-experts-fear-the-worst), [Zetik](https://www.zetik.com/news/article/story_id-p008-163673)) | ✅ (cite the filing) |

For orbit math, use **satellite.js** (SGP4). It is at v7.1.0 and was pushed Sept 28, 2026 [V] ([npm](https://registry.npmjs.org/satellite.js/latest), [GitHub](https://github.com/shashwatak/satellite-js)).

### 1.3 Realistic integration time (SpaceX-specific work, one developer who knows web and AI APIs) [I]
| Task | Hours |
|---|---|
| Cursor on all 4 laptops, a `.cursor/rules` file, and the repo; Grok Bot Team Bot in Slack for planning | 0.5–1 |
| xAI console, credits, API key | 0.25 (plus booth time if credits are handed out) |
| **Grok Imagine:** one REST call, prompt template, UI card, "AI illustration" label | 1–1.5 |
| **Grok Voice** through the LiveKit `xai` plugin (`livekit-agents[xai]`) with 3–4 function tools ([LiveKit plugin](https://docs.livekit.io/agents/models/realtime/plugins/spacexai/)) | 3–4 |
| …or a raw browser WebSocket with ephemeral tokens instead | 4–6 |
| Space data: CelesTrak + satellite.js next-pass (2–3), FIRMS (1), LL2 (0.5), ADS (1) | 2–5 |
| Devpost "How we used Cursor / Grok / Grok Bot" section with screenshots | 0.5 |
| **Minimum qualifying entry** (Cursor + Imagine + one data source) | **≈ 3** |
| **Winner-grade entry** (Voice agent + Imagine + 2–3 space sources) | **≈ 8–10**, much of which *is* the product |

My single number for the integration overhead is **≈ 5 hours**.

### 1.4 Known gotchas
1. **The r/SpaceX API is dead** (525 error, repo archived) [V]. Use LL2 for launches and CelesTrak for Starlink.
2. **Shared-IP rate limits** [I, mechanism V]: LL2 allows 15/hour per IP, CelesTrak bans repeat downloads, and NASA's DEMO_KEY allows 10. At a venue, everyone may share an IP. Pull every dataset once into a local JSON or database cache in hour 1.
3. **Ask how Cursor usage is judged** [U]. Nothing says how "the more you use Cursor" is measured. The DivHacks SpaceXAI winner never mentioned Cursor on its Devpost page [V] ([NOVA](https://devpost.com/software/nova-hzgjy0)), so a Devpost mention alone is probably not the test [I]. Do all of the following and ask at the 4 PM session:
   - Have every teammate code in Cursor from minute one.
   - Commit often.
   - Keep `.cursor/rules` in the repo.
   - Screenshot Agent sessions for the Devpost.
4. **Generative images next to real data are a trust risk** [I]. SpaceX engineers will notice fake "satellite imagery." Label every Grok Imagine output as an illustration, and never present it as a measurement.
5. **Grok Voice conflicts with ElevenLabs** (two voice engines). Pick Grok Voice for this build and see §5.
6. **Browser WebSockets cannot send auth headers.** Use xAI ephemeral tokens (`POST /v1/realtime/client_secrets`) or keep the voice session on a server through LiveKit [R] ([ephemeral tokens](https://docs.x.ai/developers/model-capabilities/audio/ephemeral-tokens)).

### 1.5 MHacks-specific resources [V]
SpaceXAI is the most visible sponsor on the schedule:
- **Grok Bot Photo Booth**, Sat 2–6 PM, Duderstadt Atrium.
- **"SpaceXAI: 🚀 Build Your Entire Internship Application Stack in 30 Minutes,"** Sat 4–5 PM, Duderstadt VR Lab.
- **Grok Bot Coffee Cart**, Sun 9 AM, BBB.

Sources: [Sat schedule](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365), [Sun schedule](https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=83169850), [live page](https://www.mhacks.org/live). The SpaceX logo is in the [mhacks.org](https://www.mhacks.org/) sponsor strip. The handbook mentions no API keys or credits [V] ([Handbook](https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af)).

---

## 2. What SpaceXAI's judges reward

### 2.1 The brief itself
Three signals stand out [I]:
1. **Space must be the input:** "real space data goes in."
2. **Cursor usage is explicitly scored on a sliding scale.** This is the only sponsor that rewards a *process* that strongly.
3. **"A literature no human can read all of"** hints at research and retrieval over papers and mission records, i.e. NASA ADS and NTRS.

"Legendary" invites ambition and showmanship.

### 2.2 Same sponsor, same track name, one week ago: DivHacks 2026 (Columbia, Sept 26–27, 220 participants) [V]
- **Brief:** "Make it Legendary with SpaceXAI." Build "with Cursor using Grok technology" for "a real-world challenge faced by humanity" (public health, sustainability, education). There was **no space-data requirement**. All entrants got Cursor and Grok credits. Prize: custom Cursor keyboards **for each winning team member** ([DivHacks](https://divhacks-2026.devpost.com/)).
- **Opt-ins:** 29 of 65 submissions (**45%**) ([SpaceXAI filter](https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105135), [all](https://divhacks-2026.devpost.com/submissions/search)). My audit of all 29 project pages: **18 mention Grok, 15 mention Cursor, and 11 never mention Grok at all.**
- **Winner: [NOVA](https://devpost.com/software/nova-hzgjy0)** connects low-income NYC families with K–5 STEM programs by ZIP code. Its strengths:
  - **565 real programs** from NYC OpenData.
  - A **seven-stage enrichment pipeline** that covers 95 of 111 providers, with **138 automated tests**.
  - An "evidence-based" rule: a program is labeled "Free" only when the city says so.
  - A **"Grok-powered chatbot with voice capabilities"** in about 20 languages.
  - A warm, parent-first design.
  - It is not technically flashy. Grok supports the product rather than starring in it.
- **The instructive loser: [Julia's Time Machine](https://devpost.com/software/julia-s-time-machine)** took **Grand Prize 1st** and opted into SpaceXAI. It was built in Cursor by "three Grokbot agents" (builder, designer, reviewer), but it used **Gemini** for the imagery, not Grok Imagine or Voice. It did **not** win SpaceXAI. Inference: the Grok Imagine/Voice requirement is real, and Grok Bot process points cannot replace it.
- **Pattern [I]:** the judges picked real data handled rigorously, a specific underserved user, and Grok voice in service of access. They did not pick the flashiest project.

### 2.3 HackCMU 2026 (Sept 11–12, ~900 hackers) [R]
- According to an X post I could not open (HTTP 402; seen through search snippets), SpaceXAI staff attended: a "Community & Education Lead" and a "Grok Voice & Starlink Lead." They handed out Cursor Pro months and Grok API credits.
- The SpaceXAI track was won by **Gotchu**, a campus task marketplace used over iMessage or a phone call. It used the Grok Responses API with tool calling, **Grok Voice for calls that continue in iMessage**, and optional Grok image/video previews ([X post](https://x.com/SERobinsonJr/status/2099897963938263072)).
- The track does not appear on HackCMU's Devpost prize list [V] ([HackCMU](https://hack-cmu-2026.devpost.com/)), so I could not confirm the winner myself.
- **Pattern [I]:** the winner was a multi-agent build in which **voice is the interface** and **Grok is used several ways**.

### 2.4 SpaceXAI's own hackathon criteria [V]
The SpaceXAI Grokathon (SF, Aug 8, 2026, judged by "Members of our Technical Staff") scored on two things ([Grokathon](https://spacexai-grokathon.devpost.com/)):
- **Usefulness:** "Would a real person want this tomorrow? Solve an actual problem for someone specific."
- **Beauty:** "Taste, craft, and attention to detail. The demo should feel considered, not assembled."

### 2.5 What this means for MHacks [I]
- Pick **one specific user** with a real need.
- Use **real space data handled rigorously**, with provenance on every number.
- Make **Grok Voice the interface**, add **Grok Imagine as a clearly labeled flourish**, and keep **visible, heavy Cursor and Grok Bot usage**.
- Make it polished and "considered."
- Space-themed toys with no user will lose to NOVA-style rigor. Rigor with no space core will be ineligible or weak.
- SpaceXAI also sends recruiting staff to hackathons: a "SpaceXAI, Talent Engineering" judge appears at Hack the North 2026 [V] ([HTN](https://hackthenorth2026.devpost.com/)).

---

## 3. Prize value and expected competition

### 3.1 Prize value (team of 4)
| Item | Listed | My realistic value |
|---|---|---|
| 1st | "SpaceXAI Mechanical Keyboards" [V]. DivHacks gave keyboards "for each winning team member" [V] | Retail price unknown [U]. Custom mechanical keyboards run from under $50 to over $250 ([Keychron range](https://www.keychron.com/collections/custom-keyboards)). Assume **$100–250 each, so ≈ $400–1,000 for the team** [I] |
| Raffle | A Cursor Owala bottle for every entrant [V] | About $30–40 retail [I]. Odds unknown |
| Intangibles | Visibility with SpaceXAI, which owns Grok, X and Cursor, and whose staff run recruiting-flavored sessions | Real but unquantifiable. Worth the most to teammates who want SpaceX, xAI or Cursor internships [I] |

The track has a **single winner** (Instagram slide: "1st"; DivHacks: "1 winner" [V]). There is **no cash**.

### 3.2 Expected competition: **medium** (headcount high, serious pool small)
- **Upper anchor:** DivHacks drew a 45% opt-in with no domain filter [V].
- **The MHacks filter:** "real space data goes in" removes most generic apps [I].
- **Pull factors** [I]:
  - It is the most visible sponsor on the schedule (photo booth, workshop, coffee cart).
  - Every team already uses an AI editor.
  - Grok Imagine costs $0.04.
- **My estimate [I]:** **10–20% opt-in, about 15–30 entries** at 130–180 submissions (MHacks 2025 had 122, per the [verdict file](/Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md)). Of those, perhaps **5–10 are space-native**. The rest garnish a non-space app with an APOD image.

---

## 4. Expected value

| Scenario | P(win) [I] | Value | EV | SpaceX-specific hours | EV per hour |
|---|---|---|---|---|---|
| Garnish (an APOD or ISS widget plus one Imagine call) | ~2% | ~$600 | ≈ $12 | ~2–3 | ≈ $5/h |
| **Space-native, recommended (Overpass)** | **~10–14%** | ~$600 | **≈ $60–85** | ~5 | **≈ $12–17/h** |
| Max-SpaceX (Hardware Skyward with an owner, or Orbital Commons) | ~15–18% | ~$600 | ≈ $90–110 | ~8+ | ≈ $12/h |

**Honest comparison** (handbook prizes [V], [Tracks & Prizes](https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5)):
- **Fetch.ai** ($1,250 / $750 / $500 cash, 3 winners), **SpacetimeDB** ($1,000 / $500 / $200 cash), and **Capital One** ($300 per member, ≈ $1,200) all have **higher dollar EV** at similar odds.
- **Relay's** SF trip and **Photon's** $400 cash plus interview fast-track are better in experience or career terms.
- SpaceX sits with **Figma, Notability and FREE-WILi** in the "goods" tier.
- **So SpaceX should never displace a cash track that fits the same project.** It almost never has to. It conflicts with few tracks (§5), and its requirements (use Cursor, call Grok) cost little.
- **The real cost is the domain constraint.** "Space data in" decides the project idea. That cost is worth paying only if the space idea is *also* the best main-track idea. Overpass is built to make that true.

---

## 5. Stacking: one coherent project

| Track | Fit with SpaceX | Why |
|---|---|---|
| **Sustainability** (main, verdict pick) | **Good, if Earth observation plus orbits** | FIRMS fire detections come from 5 satellites. Their live orbits are on CelesTrak [V]. "When does the next satellite see my area?" is both climate and space. Pure Earth-observation data is "plausible," not certain [U]. Ask on Saturday. |
| Actually Intelligent (AI) | Natural | A research and voice agent over "a literature no human can read all of" (ADS). Bigger pool, though (the verdict counts 47% LLM projects) |
| Beyond the Code (Hardware) | **Most space-native** | "Skyward," a servo pointer tracking satellites through the ceiling (Hardware advocate). Needs an electronics owner by noon |
| FinTech | Conflict, with one narrow bridge | The only coherent bridge I found: **parametric wildfire insurance**. A FIRMS detection near an insured address triggers a Nessie payout. It is real space data in and Capital One in, but "legendary" is a stretch and Nessie's data is thin (verdict) [I] |
| **Judged by an LLM** (fun) | **Strong** | A rubric-shaped Devpost, a measured evaluation (§6A) and provenance on every number are exactly what an LLM judge can score |
| Dumbest Idea / Useless AI | Only for a comic variant | "Legendary" tolerates showmanship, but it clashes with Sustainability's seriousness |
| **Relay** | **Strong, documented** | Relay's LiveKit page lists **"Brains: Grok — Supported by LiveKit: xAI plugin"** [V] ([Relay × LiveKit](https://docs.relayapp.im/integrations/livekit.md)). One Grok Voice agent then satisfies both sponsors. Relay video calls can stream any frame source as the agent's camera [V] ([Relay llms.txt](https://docs.relayapp.im/llms.txt)), so the agent can show a live orbit view. Not tested end to end [U]. Spike it in hours 1–2. |
| Photon | Good (alternative to Relay) | Grok plus Photon won Photon's DivHacks prize ([News Next Door](https://devpost.com/software/news-next-door)) [V]. Don't build both messaging surfaces. |
| Fetch.ai | Good | A Grok-backed agent on Agentverse can schedule watches or file alerts ([hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack)). Adds about 3–4 h |
| Neon | Good | Caches TLEs, FIRMS and LL2 data, which also fixes the rate-limit gotcha. Neon has a Cursor plugin and a Grok Bot plugin ([Cursor](https://neon.com/docs/ai/ai-cursor-plugin), [Grok Bot](https://neon.com/docs/ai/ai-grok-bot-plugin)) |
| SpacetimeDB | Good for Sketch B | Shared live orbital state and a multiplayer mission control. Pick Neon *or* SpacetimeDB |
| Figma | Good | The Figma MCP server runs inside Cursor, which adds Cursor usage (Figma advocate's finding) |
| Notability | Free add | Notability holds the planning notes, Grok Bot runs task coordination, and the two don't overlap |
| FREE-WILi | Good for Hardware | A handheld that beeps when a satellite passes |
| ElevenLabs | **Conflict** if Grok Voice is the voice | I recommend Grok Voice: both SpaceXAI winners centered on voice, and it doubles with Relay. That forfeits ElevenLabs |
| FinchNode | Weak | Only through a heat-health angle |

**Recommended stack** [I]: **Sustainability + Judged by an LLM + SpaceX + Relay + Neon + Figma + Notability**. Add Fetch.ai if a fourth teammate is free. That is 4–5 real integrations and one story, matching the verdict's "3–4 real integrations + free extras."

**Do I argue for a different main track?** No, provided the team builds Overpass. The flips:
- A hardware owner by noon → Hardware + Skyward. This gives the highest SpaceX odds.
- No climate idea the team likes → AI + Sketch C.

---

## 6. Project sketches

### A. "Overpass": the satellites watching your sky, on call (Sustainability · SpaceX · Relay · Neon · Judged by an LLM · Figma · Notability) — **my pick**
- **User:** someone with family or property in a fire-prone area, or a Michigan resident under smoke from distant wildfires. Pick one named person for the pitch.
- **What it does:**
  1. Ingests NASA FIRMS detections per satellite (VIIRS on Suomi NPP, NOAA-20 and NOAA-21; MODIS on Terra and Aqua) [V].
  2. Propagates those **same five spacecraft** from CelesTrak TLEs with satellite.js [V].
  3. The core screen reads: "VIIRS on **NOAA-21** detected this fire at 01:32. **NOAA-20 passes over it again in 47 min**." FIRMS ultra-real-time data lands in under 60 s of fly-over for much of the US and Canada [V], so the agent can say "watching for the next pass" and then report it.
  4. **Grok Voice agent**, callable in **Relay** (LiveKit `xai` plugin). Its tools are `fires_near(place)`, `next_pass(sat, place)`, `explain_detection(confidence, FRP)` and `cite(query)`. `cite` uses NASA ADS abstracts to answer questions like "how small a fire can VIIRS see?" That covers the brief's "literature no human can read all of."
  5. **Grok Imagine** draws a clearly labeled illustrated "pass postcard" (the satellite over your region at the predicted time). It goes into the Relay chat after the call. It is never shown as data.
- **Eval (for Judged by an LLM and the main-track judges):**
  - On 30 scripted questions, compare Grok with tools against Grok without tools. Measure numeric accuracy and citation validity.
  - Also report the predicted pass times against the timestamps of real FIRMS detections.
- **Demo:** a judge calls the agent in Relay and says "Is anything burning near Yosemite?" The agent shows a live globe and names the satellite and its next pass. A postcard arrives in the chat.
- **Why it wins SpaceX:** it is unambiguously real space data (orbits plus instruments), every number has a source like NOVA's, and it is voice-first like Gotchu. The orbit view is "legendary." It is built in Cursor, planned in Grok Bot, and backed by commits and screenshots.

### B. "Orbital Commons": who is crowding the sky? (Sustainability framed as "space sustainability," or AI · SpaceX · SpacetimeDB · Judged by an LLM)
- **What it is:** a 3D globe of the CelesTrak catalog plus SOCRATES conjunctions [V]. The pitch is "orbit is a finite shared resource."
  - Headline fact: Starlink performed **207,152 avoidance maneuvers in six months** [R].
  - The planet tie-in: the climate satellites that measure Earth (Terra, Aqua, Landsat, Sentinel-2) fly in these crowded orbits [V].
- **Grok Voice** acts as an "orbital traffic controller" you can interrupt: "Show everything within 5 km of Landsat 9 tomorrow."
- **Grok Imagine** renders a labeled "orbit in 2040" scenario video.
- **SpacetimeDB** gives a shared, multiplayer view (SpacetimeDB lists "live dashboards" and "shared simulations").
- **Trade-off:** this is the strongest SpaceX-judge appeal (Starlink is SpaceX's own data). It is the weakest Sustainability fit, because the track text is "for lasting impact on our planet." Use it if the team prefers AI as the main track.

### C. "Mission Memory": decades of missions, answerable out loud (AI main · SpaceX · Fetch.ai or Relay · Neon · Judged by an LLM)
- **What it is:** a voice research agent over Launch Library 2 (every launch and pad), NASA ADS papers and NASA imagery.
  - Example question: "Why did Falcon 9's landing success rate change after 2017? Cite papers."
- **Grok Imagine** produces labeled "mission patch" cards. A Fetch.ai agent emails a weekly launch-and-paper digest.
- **Trade-off:** this is the most literal reading of the brief, and it is purely software. It sits in the crowded AI pool, so the team needs a hard evaluation (citation accuracy against an ungrounded baseline).

---

## 7. Red flags, the best counterarguments, and rebuttals

| Rival's argument | Severity | Rebuttal |
|---|---|---|
| **"Keyboards and a bottle raffle. Fetch.ai pays $1,250 cash."** (Fetch.ai, SpacetimeDB, Capital One) | **High, and true** | Conceded on dollars (§4). But tracks don't exclude each other: Overpass also enters Relay, Neon, Fetch.ai and Figma. SpaceX's marginal cost is about 5 h, and most of that work is the product. The prize is not the reason to anchor on SpaceX. The domain, the demo and the visibility are. |
| **"Earth-observation data may not count as space data."** (verdict) | Medium | Overpass adds live spacecraft orbits and per-satellite provenance, which is space data under any reading. Ask at Sat 4 PM regardless. |
| **"The Cursor scoring is opaque, and the team might prefer other tools."** | Medium | It is the sponsor's own product, so assume it is weighted heavily. Code everything in Cursor, keep `.cursor/rules`, and screenshot Agent sessions. Use Grok Bot (bonus) for the plan. This costs nothing in hours, only in habits. |
| **"45% opted in at DivHacks, so it's crowded."** (Photon advocate) | Medium | DivHacks had no domain filter, and 11 of its 29 entrants never mentioned Grok [V]. MHacks's space requirement cuts the field, and garnish entries lose (the Grand Prize winner did). |
| **"Grok Voice kills the ElevenLabs entry."** (ElevenLabs advocate) | Low–medium | True if Voice is chosen. The alternative is Imagine for SpaceX and ElevenLabs for audio. I still prefer Grok Voice: both SpaceXAI winners were voice-forward, and it doubles with Relay. |
| **"Data APIs will break at the venue."** | Medium | They will if you aren't careful: the r/SpaceX API is dead, and LL2, CelesTrak and DEMO_KEY have per-IP limits [V]. Cache everything in Neon in hour 1. |
| **"xAI credits cost money."** | Low | About $15 in the worst case. Credits were handed out at HackCMU and DivHacks, so ask at the Grok Bot booth. |
| **"Generated images on a science app look fake."** | Medium | Label them as illustrations, keep them out of the data view, and use them only for share and postcard moments. |
| **"It drops Capital One, a team favorite."** | Medium | Correct for the recommended build. The parametric-insurance bridge (§5) exists if the team insists, at the cost of a weaker "legendary" story. |

**Non-issue:** some may object to the brand politics of Grok or X. Judging is by SpaceXAI staff, and nothing in the rules makes it relevant.

---

## 8. Scorecard (1–10)

| Criterion | Score | Justification |
|---|---|---|
| Prize value | **3** | Goods only, probably one winner. Keyboards ≈ $400–1,000 for the team (unverified), plus a bottle raffle. The intangible SpaceXAI visibility is real but soft. |
| Win probability | **4** | ≈10–14% for a space-native build against 15–30 entrants (5–10 serious). ≈2% for a garnish. |
| Integration ease | **8** | Cursor costs nothing extra. Imagine is one REST call at $0.04. Voice is documented through LiveKit. The data is free, though with rate-limit traps. |
| Stacking potential | **7** | Fits Sustainability (via orbits), AI, Hardware, Relay (documented Grok brain), Photon, Neon, SpacetimeDB, Figma, Notability and Judged by an LLM. Conflicts with FinTech and ElevenLabs (if Voice), and it dictates the domain. |
| Demo impact | **8** | Live orbits, a named satellite, a voice agent you can call and a postcard in chat. "Legendary" is easy to show in 3 minutes. |
| Fit with team preferences | **9** | It is the team's top sponsor and keeps the verdict's Sustainability + Judged by an LLM. Its only cost is Capital One. |

Total: **39/60**. I recommend entering, and anchoring on it **only** with the space-native design.

---

## 9. Saturday checklist
1. **Before 12 PM:**
   - Install Cursor on all 4 laptops and set up a shared repo with `.cursor/rules`.
   - Create a Grok Bot Team Bot in Slack for the task plan.
   - Create the xAI console account and request a FIRMS MAP_KEY, an ADS token and an api.nasa.gov key.
2. **At the Sponsor Expo (11:30):** ask SpaceXAI about Grok API credits and Cursor Pro codes.
3. **12–2 PM:**
   - Cache the CelesTrak `resource` and `weather` groups, plus LL2 and FIRMS data, in Neon.
   - Spike Relay → LiveKit → Grok Voice with one tool.
4. **4 PM, VR Lab:** ask the SpaceXAI team:
   - Does Earth-observation data plus orbital data qualify?
   - How is Cursor usage measured?
   - Do they want Imagine, Voice or both?
5. **Devpost:**
   - A "How we used Cursor / Grok Voice / Grok Imagine / Grok Bot" section with screenshots.
   - The evaluation table.
   - Data provenance for every number.

*Note on scope:* per the relayed user instruction to skip the second 2020 item, I used no 2020-dated material. All precedents here are from 2025–26.

---

## Sources
- MHacks Handbook › Tracks & Prizes (SpaceX text, all sponsor prizes, Relay ideas; read through Notion's public `loadCachedPageChunk` API): https://safe-banon-80d.notion.site/3ed24ca0c81b80579aeff03edfa88af5
- MHacks 2026 Hacker Handbook: https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af
- MHacks schedule, Saturday (CSV export): https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365
- MHacks schedule, Sunday: https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=83169850
- MHacks live page: https://www.mhacks.org/live · Home (sponsor logos): https://www.mhacks.org/
- Main/fun verdict: /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md
- SpaceXAI: https://en.wikipedia.org/wiki/SpaceXAI
- Cursor acquisition: https://en.wikipedia.org/wiki/Cursor_(company)
- Cursor student-deal status (conflicting reports): https://whichai.fyi/blog/cursor-student-discount-2026/
- xAI Grok Imagine guide: https://docs.x.ai/docs/guides/image-generations
- xAI Voice overview: https://docs.x.ai/developers/model-capabilities/audio/voice
- xAI Voice Agent (speech-to-speech): https://docs.x.ai/developers/model-capabilities/audio/voice-agent
- xAI ephemeral tokens: https://docs.x.ai/developers/model-capabilities/audio/ephemeral-tokens
- xAI pricing: https://docs.x.ai/developers/pricing · Models: https://docs.x.ai/docs/models
- xAI quickstart (credits, OpenAI compatibility): https://docs.x.ai/docs/tutorial
- Grok Bot Team Bots: https://docs.x.ai/grok-bot/team-bots
- Grok Bot launch: https://www.macrumors.com/2026/08/11/grok-bot-macos-ios/
- Grok Bot access expansion: https://9to5mac.com/2026/09/04/spacexai-expands-grok-bot-to-ipad-as-access-expands-to-cheaper-plans/
- LiveKit SpaceXAI/xAI realtime plugin: https://docs.livekit.io/agents/models/realtime/plugins/spacexai/
- Relay × LiveKit (Grok listed as a brain): https://docs.relayapp.im/integrations/livekit.md · Relay docs index: https://docs.relayapp.im/llms.txt
- DivHacks 2026: https://divhacks-2026.devpost.com/
- DivHacks all submissions: https://divhacks-2026.devpost.com/submissions/search
- DivHacks SpaceXAI opt-ins: https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105135
- NOVA (DivHacks SpaceXAI winner): https://devpost.com/software/nova-hzgjy0
- Julia's Time Machine (DivHacks Grand Prize, not SpaceXAI): https://devpost.com/software/julia-s-time-machine
- News Next Door (Grok + Photon winner): https://devpost.com/software/news-next-door
- HackCMU SpaceXAI visit and Gotchu (X post, seen through search snippets only): https://x.com/SERobinsonJr/status/2099897963938263072
- HackCMU 2026 Devpost: https://hack-cmu-2026.devpost.com/
- SpaceXAI × HackPrinceton Grok Bot Build Night: https://www.princeton.edu/events/2026/spacexai-x-hackprinceton-grok-bot-build-night
- SpaceXAI Grokathon (criteria, judges): https://spacexai-grokathon.devpost.com/
- Hack the North 2026 (SpaceXAI Talent Engineering judge): https://hackthenorth2026.devpost.com/
- Fetch.ai MHacks hackpack: https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack
- Neon Cursor and Grok Bot plugins: https://neon.com/docs/ai/ai-cursor-plugin · https://neon.com/docs/ai/ai-grok-bot-plugin
- r/SpaceX API repo (archived): https://github.com/r-spacex/SpaceX-API · endpoint tested: https://api.spacexdata.com/v5/launches/latest
- Launch Library 2 throttle: https://ll.thespacedevs.com/2.3.0/api-throttle/ · launches: https://ll.thespacedevs.com/2.3.0/launches/upcoming/?limit=1&mode=list
- CelesTrak GP formats and usage policy: https://celestrak.org/NORAD/documentation/gp-data-formats.php
- CelesTrak groups: https://celestrak.org/NORAD/elements/gp.php?GROUP=resource&FORMAT=json · https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=json · https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=json
- CelesTrak SOCRATES: https://celestrak.org/SOCRATES/
- NASA FIRMS area API: https://firms.modaps.eosdis.nasa.gov/api/area/ · MAP_KEY: https://firms.modaps.eosdis.nasa.gov/api/map_key/
- Earthdata FIRMS: https://www.earthdata.nasa.gov/data/tools/firms
- NASA APIs: https://api.nasa.gov/
- JPL Close-Approach API: https://ssd-api.jpl.nasa.gov/cad.api?dist-max=0.05&date-min=now&date-max=%2B30
- NOAA SWPC Kp: https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json
- Where the ISS at: https://api.wheretheiss.at/v1/satellites/25544
- NASA Exoplanet Archive TAP: https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+count(*)+from+ps&format=json
- NASA ADS API: https://github.com/adsabs/adsabs-dev-api
- NASA Image Library: https://images-api.nasa.gov/search?q=starship&media_type=image
- satellite.js: https://registry.npmjs.org/satellite.js/latest · https://github.com/shashwatak/satellite-js
- Starlink avoidance maneuvers: https://www.space.com/space-exploration/satellites/every-spacex-starlink-satellite-has-to-dodge-a-collision-almost-weekly-and-experts-fear-the-worst · https://www.zetik.com/news/article/story_id-p008-163673
- Custom keyboard price range: https://www.keychron.com/collections/custom-keyboards

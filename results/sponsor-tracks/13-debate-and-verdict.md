# Sponsor Tracks — Debate & Verdict

## Prompt given (excerpt)
> You are the impartial judge of the sponsor-track debate. Read all twelve sponsor advocate files in full, stage the debate on paper (tiering, head-to-heads among the contenders, an expected-value table, a stacking analysis of which sponsors fit one coherent project, and an honest look at the team's lean toward SpaceX, Relay, and Capital One), rank every sponsor track without ruling any out unexplained, and recommend a core sponsor stack plus optional bolt-ons.

Tags: **[V]** I checked it myself today (2026-10-03) at the linked source. **[A]** An advocate reported it with a citation, and I did not re-check it. **[I]** Inference or estimate (mine unless attributed). **[U]** Unverified, so ask on site.

Scope: I read all twelve advocate files in full. I also read the main/fun verdict (`../main-and-fun-tracks/07-debate-and-verdict.md`). Per the relayed user note, I skipped the second 2020 item and used no 2020-dated material. Every precedent below is from 2025–26.

---

## 0. Verdict in brief

- **Core stack (build the project around these): Relay + SpaceX "Make it Legendary" + Fetch.ai ASI:One.** It sits on the recommended **Sustainability + Judged by an LLM** pick, and I see no reason to change that pick.
- **Optional bolt-ons, in priority order:**
  1. ElevenLabs: free, because it is already in Relay's workshop build.
  2. Figma Best Design: about 3.5 h of design work by one person.
  3. Capital One Nessie: only as a load-bearing "parametric payout" feature, and only if the core works end to end by about midnight.
  4. Notability: only if the team gets a free Pro code at the expo.
- **The project.** One satellite wildfire and smoke agent, which I'll call "Overpass", following the SpaceX advocate's name.
  - **Data.** It ingests NASA FIRMS detections from each satellite and propagates the orbits of the satellites that made them.
  - **Relay.** You text it, video-call it, and it calls *you* when something new is detected.
  - **ASI:One.** The same tool layer is exposed to ASI:One so a user can set up a watch and have the agent act.
  - Six of the twelve advocates independently put FIRMS at the center of their best sketch (Fetch.ai, Photon, SpaceX, SpacetimeDB, Figma, Relay). That convergence is the strongest coherence signal in the debate.
- **Hours:** about 16 person-hours of sponsor-specific work for the core and about 20 with ElevenLabs and Figma. The ceiling is about 26 if Capital One and Notability are added.
- **EV:** about **$490 in sponsor prizes for core + ElevenLabs + Figma**, rising to about $565 with the Capital One feature [I]. That is roughly what a cash-maximizing stack would earn (§3), so the team does **not** have to give up its preferences to chase money.
- **Confidence: about 55%.** The biggest single risk is verified: Relay's public App Store build (v1.1) does not mention calls ([App Store][RL-AS]). The flip conditions are in §6.
- **On the team's lean:**
  - **Keep SpaceX**, but for the domain and the demo, not the keyboards.
  - **Keep Relay** as the hub, after confirming calls at the 1 PM workshop.
  - **Demote Capital One** from "build around" to "conditional bolt-on." It does not fit a satellite-data project natively.

---

## 1. Tier list (all twelve, with a steelman for each)

Ranking criterion: **value to this team under Sustainability + Judged by an LLM.** That means expected prize value, adjusted for how well the track fits *one* coherent project, plus the team's stated preferences. The standalone EV order is different; see §3.

### Tier 1: build around these

| # | Track | Steelman (the best honest case) | Why it ranks here |
|---|---|---|---|
| 1 | **Relay (Interactive Agents)** | Relay's MHacks cookbook was committed early today. It takes four prompts to get a character you text and video-call, built on **Grok Imagine** (`grok-imagine-image-2.0`, `grok-imagine-video-1.5-lite`), a Grok text brain and an **ElevenLabs** voice [V] ([README][RL-WS], [commits][RL-WSC]). One build therefore carries SpaceX's tooling and ElevenLabs. Realistic 1st-place value is about $1.0–1.5k (SF trip plus a week at the Relay house) [A/I], and the founder access can't be priced. An agent that rings the judge's phone is the strongest software demo on the board. | Team lean + hub of the stack + EV ≈ $175 [I]. Risks: iOS 26 only, and calls are missing from the public build notes [V] ([App Store][RL-AS]). |
| 2 | **SpaceX "Make it Legendary"** | Rules [V] ([Tracks & Prizes][TP]): "Real space data goes in", "must be built with Cursor", "must also use the Grok Imagine or Voice API". SpaceX owns xAI (acquired Feb 2, 2026) and Cursor (Aug 14, 2026) [V] ([Wikipedia][WP-SX]). Space data is free and rich. Fresh precedent the SpaceX advocate *didn't* use: **WaterFlow**, an environmental satellite-imagery hydrology explorer with Grok as a no-invented-data explainer, won SpaceXAI and an environmental prize at HopHacks Fall 2026 [V] ([WaterFlow][WF]). NOVA, a rigorous real-data product with Grok voice, won at DivHacks [V] ([NOVA][NOVA]). Both reward exactly the Sustainability-plus-real-data framing. | The team's top preference and the domain anchor. Dollar EV is low (≈ $70 for keyboards [I]), but its requirements are mostly product work the team does anyway. |
| 3 | **Fetch.ai ASI:One** | The largest cash pool: $1,250 / $750 / $500 [V] ([Devpost][DP]). At MHacks 2025 its three prizes drew 14, 5 and 3 opt-ins of 122 [V] ([filter 90535][F25a], [90891][F25b], [90892][F25c]). Hard requirements filter out casual entrants. Winners take real actions, and only 1 of 48 verified winners was green [A], so a climate agent stands out. | The highest cash EV that fits an agent project (≈ $180 [I]). Not a team pick, but it adds a second front door to the same brain. |

### Tier 2: cheap bolt-ons that ride the core

| # | Track | Steelman | Why it ranks here |
|---|---|---|---|
| 4 | **ElevenLabs** | The Relay workshop's call voice is already ElevenLabs `eleven_v4_turbo` [V] ([README][RL-WS]), so entering costs about 1 h of polish. MHacks also runs a separate **[MLH] Best Use of ElevenLabs** (wireless earbuds), which the ElevenLabs advocate missed [V] ([Devpost][DP]). The Devpost listing also settles that advocate's open question: the Pro-tier perk goes to the **Grand Prize** team [V] ([Devpost][DP]). | Small EV (≈ $40), close to zero marginal cost. |
| 5 | **Capital One Nessie** | The prize is $300 / $75 / $25 Giftogram per member, three places [V] ([Devpost][DP]). That is about $1,200 near-cash for 1st. The API is up over HTTPS and refuses plain HTTP [V] ([probe][NS-API]). The "Best Use of Nessie" opt-in rate was 8 of 65 at DivHacks 2026 [V] ([filter][DV-C1]). Recent winners weren't bank apps [A]. | Team lean and good money, but it fits a satellite-fire project only as a parametric-payout feature (§4). EV as a bolt-on is ≈ $75 [I]. It could become core only under the energy/FinTech flips (§6). |
| 6 | **Figma Best Design** | The workshop is Sat 5:30 PM, Duderstadt 3336 [V] ([schedule][SCH]). The prize is a LEGO architecture set plus merch, with merch for 2nd and 3rd [V] ([Devpost][DP]). The design work raises usability and presentation scores with every panel [I]. | Direct EV ≈ $23 [A]. Overpass has a real UI to design: the live globe, which is also streamed as the agent's video "camera". |

### Tier 3: strong tracks, wrong shape for this project

| # | Track | Steelman | Why it ranks here |
|---|---|---|---|
| 7 | **SpacetimeDB** | The best cash per competitor: $1,000 / $500 / $200 [V] ([Devpost][DP]). HopHacks Fall 2026 had 11 of 87 opt-ins and 3 winners [V] ([filter][HH-ST]), against 31 of 87 for SpaceX's one prize [V] ([filter][HH-SX]). | It must be the *core* of a *multi-user* product, and 6 of 7 winners were game-like [A]. Relay chats are one person each [A], so in this stack SpacetimeDB would be forced in. It is the top pick in the alternative "multiplayer" stack (§6). |
| 8 | **FREE-WILi** | The least-contested prize: 5 of 122 entered at MHacks 2025, and 2 won (Wattson and Gestura; winner labels [V] ([Wattson][WAT], [Gestura][GES], [filter][F25-FW])). Wattson won Greenprint (Sustainability) too [V]. | It needs a hardware owner, and the team's hardware experience is unknown. It fits an energy idea (IR off-switch), not a satellite-fire agent. The new Hardware main track will widen its pool [I]. Top pick under the Hardware flip. |
| 9 | **Neon** | Neon's full backend (Auth, Functions, Storage, AI Gateway, branching) went GA about two weeks ago [A]. Few opt-ins will go beyond a connection string [A/I]. | The prize is credits [V] ([Devpost][DP]). There is no precedent, workshop or rubric [A]. It needs about 3 net-new hours of branching-as-a-feature to compete, which Overpass doesn't need, and it conflicts with SpacetimeDB. |

### Tier 4: skip unless a condition changes

| # | Track | Steelman | Why it ranks here |
|---|---|---|---|
| 10 | **Notability** | No code: tag it on Devpost and add 2+ screenshots [V] ([Tracks & Prizes][TP]). It fits every track. | **The advocate's "cheapest track" claim leaves out the cost.** Pro is $79.99/yr, and the individual plans show no free trial [V] ([pricing][NOT-P]). If the team has to buy Pro, its ≈ $40–80 gross EV nets to about zero or below [I]. Enter only with an expo code or a teammate's existing Pro. |
| 11 | **Photon iMessage** | Its twin event a week ago drew 29 of 65 [V] ([filter][DV-PH]). Judges' own phones buzz, and no app install is needed. | It is the same surface as Relay, and the pitch can sell only one [A]. At DivHacks, 18 of the 29 SpaceXAI entrants also entered Photon [V] (my overlap count of [DV-SX] and [DV-PH]). It is the **fallback surface** if Relay calls fail. |
| 12 | **FinchNode** | The keyless demo API is live, with 12 synthetic scenarios including `pediatric-asthma` and `polypharmacy-senior` [V] ([scenarios][FN-API]). 2nd place is $500 cash [V] ([Devpost][DP]). | It is a domain conflict under Sustainability. The one coherent bridge in this stack, smoke risk for an asthmatic child, would make the main pitch about health. It is a top-3 pick only under the AI flip [A]. |

---

## 2. Head-to-heads among the contenders

### 2.1 Relay vs Photon: which messaging surface?
- **Where Relay holds up.**
  - The cookbook is real and was updated today [V] ([commits][RL-WSC]).
  - It bundles Grok Imagine and ElevenLabs, so it is the natural hub for SpaceX and ElevenLabs.
  - Its prize is the largest non-cash prize. The team named it.
- **Where Relay overreaches.**
  - "One build can qualify for SpaceX" is true only for the *tooling* half. SpaceX also needs Cursor and "real space data" [V] ([Tracks & Prizes][TP]).
  - The workshop hands Grok Imagine to every attendee. That **raises the number of garnish SpaceX entries**, which hurts SpaceX odds a little [I].
  - Most important: the public App Store build (v1.1, Sep 20) lists groups, voice notes and attachments, **not calls**, and requires iOS 26 [V] ([App Store][RL-AS]).
- **Where Photon holds up.**
  - Verified twin-event data: 29 of 65 opted in [V] ([filter][DV-PH]).
  - Judges don't need to install anything.
  - Grok + Photon has won before [A] ([News Next Door][NND]).
- **Where Photon overreaches.**
  - The "~10% for each place" odds against 20–40 entrants are optimistic.
  - The free tier has no group chats and only 10 allowlisted users [A].
- **Ruling: Relay is primary and Photon is the contingency.** Settle it at the 1 PM Relay workshop: do calls and video work on today's build? If not, switch to Photon by 4 PM. The data and tool layer don't change.

### 2.2 Fetch.ai vs SpacetimeDB: which cash track?
- Both advocates claim the top EV (≈ $250 and ≈ $200).
- **Where they overreach.**
  - Fetch's "≈30% to place" stretches MHacks 2025's base rate. That rate was 3 prizes ÷ 15 entrants = 20% [V counts], and 2026 adds agent pull from Relay and Photon.
  - SpacetimeDB's "≈35%" leans on HopHacks Fall 2026, where it was a **choose-one track** [V] ([HopHacks][HH]). A choose-one track concentrates committed entrants. MHacks is additive, so expect more tag-ons and a less predictable top [I].
  - I haircut both to ≈ 22–27% to place and ≈ $150–180 EV.
- **Fit decides it.** Fetch adds a second front door (ASI:One) to the same tools: "@overpass watch my parents' place; tell me before it's bad." That fits the brief, which calls for real actions and multi-agent work [A] ([hackpack][FH]). SpacetimeDB needs a multi-user product. Its own sketch, "Hotspot", asks untrained players to classify FIRMS thermal anomalies from map tiles. That is a gamified gimmick a Sustainability judge may discount [I].
- **Ruling: Fetch.ai.** Two cautions:
  - Fetch costs about 7–8 h in this stack, more than the 6 h claimed. That covers a Python uAgent next to a TypeScript Relay agent, ASI:One as a second surface, and the second submission, which every teammate must join [A] ([submission doc][FSUB]).
  - Give it one owner from hour one.

### 2.3 SpaceX vs Capital One: which team lean sets the domain?
They pull in opposite directions, and only one can set the domain.
- **SpaceX's case.** Satellite data gives a "legendary" demo.
  - Per-satellite FIRMS detections plus CelesTrak orbits are unambiguously space data [A].
  - Both data sources answered live today. The FIRMS 24-hour NOAA-20 CSV downloaded with no key, and CelesTrak's `weather` group returned 200 [V] ([FIRMS CSV][FIRMS-CSV], [CelesTrak][CT]).
- **Capital One's case.** Its best Sustainability fit is "Payback," a home-electrification money agent [A]. Two problems:
  - Its "space data" would be NASA POWER irradiance, which is weak for SpaceX [I].
  - The advocate admits "carbon footprint from transactions" is a familiar idea [A].
- **Ruling: SpaceX sets the domain.** Capital One enters as a parametric fire payout: a FIRMS detection within X km of an insured address triggers a Nessie deposit, and Relay calls the user. It reads and writes Nessie, and it is a feature, not a widget. It is also the "finance + real space data" bridge the main/fun verdict said nobody had found. The SpaceX advocate sketched it; the Nessie advocate built its Sketch B on the same idea; insurance and climate risk were among the verified peer FinTech winners [A] ([verdict][VER]).

### 2.4 ElevenLabs vs Grok Voice: who speaks on calls?
- The SpaceX advocate wants Grok Voice because SpaceXAI winners were voice-forward [A].
- But SpaceX accepts Grok **Imagine *or* Voice** [V] ([Tracks & Prizes][TP]), and the tested Relay path is Grok Imagine + Grok brain + ElevenLabs voice [V] ([README][RL-WS]).
- **Ruling: follow the workshop path.** It qualifies for SpaceX through Imagine and enters ElevenLabs for free. At the 4 PM SpaceXAI session, ask whether they *prefer* Voice. Switching later costs only the ≈ $40 ElevenLabs EV.

### 2.5 FREE-WILi vs Figma: which cheap differentiator?
- FREE-WILi has far better odds: 2 winners among 5 entrants in 2025 [V].
- It also has three costs:
  - Hardware ownership.
  - Unconfirmed loaners [A].
  - Its Relay workshop clashes: both are at 1 PM [V] ([schedule][SCH]).
- In a satellite-fire product, a handheld "pass beeper" would be a gimmick.
- **Ruling: Figma** in this stack. FREE-WILi returns under the Hardware flip or an energy-domain project.

---

## 3. Expected-value table (all twelve)

Prize values are verified from the handbook and Devpost [V] ([TP], [DP]). Realistic values and probabilities are my judgments [I], after trimming advocate figures where §2 found overreach. "Hours" means sponsor-specific person-hours for a best-use-grade entry. **Column 6 is the EV inside the recommended Overpass plan.** "—" means not entered.

| Track | Prize (face) | Realistic team value | Realistic P (strong, fitting entry) | Hours | EV standalone | EV in recommended plan |
|---|---|---|---|---|---|---|
| Fetch.ai | $1,250 / $750 / $500 cash + internship interviews [A] | Face value | 7% / 7% / 8% (≈22% to place) | 6–8 | **≈ $180** (advocate: $250) | ≈ $180 (core) |
| SpacetimeDB | $1,000 / $500 / $200 cash | Face value | 9% / 9% / 9% *if core and multi-user* | 6 (≈3 net-new) | **≈ $155** (advocate: $200) | — |
| Capital One | $300 / $75 / $25 Giftogram per member | ≈ $1,200 / $300 / $100 | Core: 10 / 11 / 12%. Bolt-on: 4 / 6 / 8% | 4 | ≈ $165 as core (advocate: $200) | ≈ $75 (bolt-on, conditional) |
| Relay | SF trip + week at Relay house + merch / merch | ≈ $1,200 / ≈ $250 [A/I] | 12% / 12% beyond-template | 4 | **≈ $175** (advocate: $225) | ≈ $175 (core) |
| FREE-WILi | Kit per member, up to 4 | $600 (OG) – $1,600 (FW2) [A] | ≈ 20% (pool widened by the Hardware track) | 5 + hardware owner | ≈ $120–320 (advocate: $180–480) | — |
| Neon | $1,000 / $500 / $100 AI Gateway credits | ≈ $400 / $250 / $75 [A] | 12% / 12% / 12% | 3 net (6 gross) | ≈ $85 (advocate: $130) | — |
| ElevenLabs | 3 mo Scale per member; plus MLH earbuds | Credits ≈ $300–500 real; earbuds | ≈ 8% sponsor; ≈ 3% MLH | ≈ 1 on the Relay path | ≈ $40 | ≈ $40 (bolt-on) |
| Photon | $400 + $300 credits (+ fast-track) / $200 + $100 credits | ≈ $550 / ≈ $220 [A] | 9% / 9% | 3 | ≈ $70 (advocate: $80) | — (fallback surface) |
| SpaceX | Mechanical keyboards (likely one per member) + Owala raffle | ≈ $400–1,000 [A/I]; HopHacks gave "4 Cursor keyboards" [V] ([HH]) | ≈ 12% space-native | ≈ 5 (mostly product work) | ≈ $70 | ≈ $70 (core) |
| Notability | 1 yr Pro + 4 merch pieces per member | ≈ $150–400 [A] | ≈ 15% | 1.5–2 | ≈ $40 gross; **≈ −$40 net if Pro must be bought** ($79.99, no trial [V]) | ≈ $40 only with a free code |
| FinchNode | Apple Watch SE3 / $500 cash / dev plan | $249 (or $996 if per member [U]) / $500 / ≈ $0 | 13% / 13% / 12% as a bolt-on; higher if focused | 4 | ≈ $100–130 (AI main) | — |
| Figma | LEGO set + merch / merch / merch | ≈ $230 / $70 / $70 [A] | 6% 1st; ≈ 11% 2nd/3rd | 3.5 | ≈ $23 + main-track spillover | ≈ $23 (bolt-on) |

**What the table says**
1. **Sponsor EV is small next to the main-track prizes.** Any track winner gets $2,500 and the Grand Prize is $5,000 [V] ([DP]). One extra point of main-track probability is worth about $25, more than several sponsor tracks [I]. Spend sponsor hours where they also make the main demo better (Relay, SpaceX, Figma), not where they only tick a box.
2. **The preference-aligned stack ties the cash-max stack.**
   - Recommended plan (core + ElevenLabs + Figma): ≈ $490, or ≈ $565 with Capital One.
   - A "cash-max" plan (Fetch + SpacetimeDB core + Capital One core) would earn about $500.
   - The cash-max plan drops SpaceX and Relay and forces a multiplayer, FinTech-leaning product [I]. The team doesn't have to trade its preferences for money.
3. **The best EV per hour is ElevenLabs** on the Relay path (≈ $40/h), then Relay (≈ $45/h) and Fetch (≈ $25/h). Notability is ≈ $25/h *only* with a free code; otherwise it is negative.

---

## 4. Stacking analysis: what shares one coherent project

### 4.1 The spine: "Overpass" (Sustainability · Judged by an LLM)
- **One brain, a shared tool layer:**
  - `fires_near(place)` uses FIRMS, per satellite.
  - `next_look(place)` uses CelesTrak TLEs and SGP4 to say which satellite sees the area next.
  - `smoke_outlook(place)` uses an air-quality forecast, as in the Fetch.ai and Figma "Smoke Signal" sketches [A].
  - `create_watch` and `notify`.
- **Three doors onto that brain:**
  1. **Relay.** Text, video call (the live globe as the agent's camera), and the agent calls you when a new detection appears [A] ([Relay advocate][S11]).
  2. **ASI:One.** Set up a watch, confirm a Review card, and the agent acts by sending the alert email or calendar change [A] ([Fetch advocate][S01]).
  3. **A Figma-designed web globe** for main-track judges.
- **Grok Imagine** makes only the agent's face and clearly labeled "pass postcards." It never stands in for satellite data [A].
- **Sustainability framing.** Satellites watch the forests and air that a warming climate puts at risk, and the agent turns that into an action. That is a climate-resilience story; frame it as protecting forest and community resources.
  - *Risk:* the track text leans "rethink energy, climate, and resource systems" [V] ([TP]). Adaptation reads weaker than mitigation [I], so put the emissions and resource framing in the first 20 seconds of the pitch.
- **Judged by an LLM.** An eval table: grounded vs ungrounded answers on scripted questions, and predicted next-look times against real FIRMS timestamps. The SpaceX advocate proposed it [A].

### 4.2 Fit of each sponsor with the spine

| Sponsor | Fit | Why (and the checkbox test: would that sponsor's judge see through it?) |
|---|---|---|
| SpaceX | **Native** | Space data *is* the product. Cursor and Grok Imagine are already in the build. It passes the checkbox test, and WaterFlow-style rigor won before [V] ([WF]). |
| Relay | **Native** | It is the main interface, and the agent-initiated call is the demo moment. Passes. |
| Fetch.ai | **Natural second door** | The same tools with a real action (alert, calendar), done entirely inside ASI:One. It passes only if ASI:One gets a *complete* workflow with a Review card, not a thin wrapper [A] ([FH]). |
| ElevenLabs | **Native by construction** | It is the call voice. It passes only if voice is central (it is: calls). A token TTS button would fail [A]. |
| Figma | **Natural** | The globe and the alert cards are real UI. It passes if the Figma file shows a design system and matches the shipped UI [A]. |
| Capital One | **Stretch, but coherent** | A parametric payout: a detection near an insured address triggers a Nessie deposit, the balance is read back, and the agent calls the user. It reads and writes Nessie [A]. **It fails the checkbox test if it is only a balance widget** [A]. |
| Notability | Orthogonal | It never touches the product. Fine if Pro is free. |
| FinchNode | Stretch | Smoke risk for the `pediatric-asthma` patient [V] ([FN-API]). Coherent, but it turns the pitch toward health and doubles up with Capital One. Pick at most **one** domain bolt-on. |
| Neon | Bolt-on | It could cache FIRMS and TLE data and store Relay's `event_id`s [A]. "Fullest use" needs branching, which this product doesn't need, so a Neon judge would likely see through it [I]. |
| SpacetimeDB | **Checkbox** | A shared watch map can be done without it. SpacetimeDB says it wants to be "meaningfully used, not just added on the side" [V] ([TP]). |
| FREE-WILi | Checkbox in this spine | A "satellite overhead" desk beacon is a gimmick. It is real only in an energy or hardware project. |
| Photon | **Conflict** | A second texting surface. Choose Relay *or* Photon. |

### 4.3 Hard conflicts and time clashes
- **Platform**
  - Relay needs **iOS 26** (iPhone or M1+ Mac) [V] ([RL-AS]). Confirm a teammate has one before noon.
  - Photon on Free/Pro has no groups and a 10-user allowlist [A].
- **Mutually exclusive pairs**
  - Relay ⟂ Photon (surface).
  - SpacetimeDB ⟂ Neon (backend).
  - Grok Voice ⟂ ElevenLabs (soft).
  - Capital One ⟂ FinchNode (domain, in one pitch).
- **Requirements**
  - Fetch needs a second submission through the Submission Agent, and every teammate must join [A] ([FSUB]).
  - SpaceX needs Cursor throughout ("the more you use Cursor…") [V] ([TP]).
  - Teams must be present to be judged for any track, and sponsors judge concurrently during the 12:30–2:30 PM window [A] ([HB]). With five or more tracks, assign one person to greet each sponsor.
- **Workshop clashes (Saturday)** [V] ([SCH]):
  - Relay vs FREE-WILi at 1 PM.
  - Fetch.ai vs FinchNode at 2 PM.
  - SpaceXAI at 4 PM; Figma at 5:30 PM.
  - The recommended stack loses nothing to these clashes.

---

## 5. The team's lean: SpaceX, Relay, Capital One

### SpaceX "Make it Legendary": **KEEP, as the domain anchor, not for the prize**
- **The prize is weak.** Keyboards for probably one team, worth ≈ $400–1,000 [A/I].
- **The field is crowded on paper.** Twin events drew 45% (29 of 65 at DivHacks) and 36% (31 of 87 at HopHacks) [V] ([DV-SX], [HH-SX]).
- **The case for keeping it:**
  - MHacks's "real space data" rule thins the field.
  - Both verified winners were rigorous real-data products with Grok as a helper: NOVA [V] ([NOVA]) and WaterFlow [V] ([WF]). WaterFlow was environmental and satellite-based, which is the Sustainability framing.
  - It costs about 5 hours, most of which is product work.
- **Garnish loses.** At HopHacks, the SpacetimeDB winner Iron Glove also entered SpaceX and did not win it [V] (it appears in both filters; its winner label is SpacetimeDB only ([Iron Glove][IG])).
- **Still open:** whether Earth-observation data alone counts [U]. Overpass's orbit propagation hedges that. Ask at the SpaceXAI session, 4 PM, VR Lab [V] ([SCH]).

### Relay: **KEEP, as the hub, with a 4 PM go/no-go**
- **Strengths:**
  - The best marginal value on the board. Its workshop already wires in Grok Imagine and ElevenLabs [V] ([RL-WS]).
  - The team named it.
  - Its prize has the most upside.
- **Honest risks:**
  - The public build doesn't list calls [V] ([RL-AS]).
  - The vendor is one person, and its API breaks often [A].
  - The workshop template commoditizes the baseline, so the entry must go past it. The agent-initiated call and real data tools do that.
- **Go/no-go:** if calls and video aren't working on a teammate's phone by **4 PM**, switch the surface to **Photon** and keep everything else.

### Capital One Nessie: **DEMOTE to a conditional bolt-on; don't build around it**
- **Strengths:** good near-cash money ($1,200 for 1st, three places [V]) and a medium field [A].
- **The problem:** it doesn't fit satellite fire data natively, and the Sustainability version that does fit ("Payback") weakens SpaceX [I].
- **How to enter anyway:** build the parametric-payout feature (≈ 4 h, read + write) **only if** the Overpass core works end to end by about midnight.
  - Seed your own data. A fresh key starts empty [A], and ATMs and branches are DC-area only [A].
  - Badge every Nessie number in the UI [A].
- **Promote Capital One to core only under a flip** (§6): an energy/money project, or FinTech with SpaceX dropped.

---

## 6. Recommendation

### Core stack: Relay + SpaceX + Fetch.ai, on Sustainability + Judged by an LLM

| Role | Sponsor | Sponsor-specific hours | Owner |
|---|---|---|---|
| Interface and demo | Relay | ≈ 4 | P1 (has an iOS 26 iPhone) |
| Data and domain | SpaceX (Cursor + Grok Imagine + FIRMS/CelesTrak) | ≈ 5 | P2 |
| Second door, cash | Fetch.ai (uAgent wrapping the shared tools, ASI:One Review card, Submission Agent) | ≈ 7 | P3 |
| **Core subtotal** | | **≈ 16** | |

### Optional bolt-ons (in order)

| Bolt-on | Hours | Condition |
|---|---|---|
| ElevenLabs | ≈ 1 | Free on the Relay workshop path. Drop it only if SpaceXAI says Grok Voice is strongly preferred. |
| Figma Best Design | ≈ 3.5 | P4 owns design. Freeze the UI by about 6 AM Sunday [A]. |
| Capital One (parametric payout) | ≈ 4 | Only if the core works end to end by about midnight. |
| Notability | ≈ 1.5 | Only with a free Pro code or an existing Pro account (no free trial [V]). |
| **Total** | **≈ 20 (core + ElevenLabs + Figma); ≈ 26 at most** | |

**Not entered, with reasons:**
- SpacetimeDB: needs a multi-user core.
- Neon: not worth "fullest use" here.
- FREE-WILi: no confirmed hardware owner, and it doesn't fit this spine.
- Photon: fallback surface only.
- FinchNode: domain conflict.

### Today's timeline (Sat Oct 3) [V schedule: [SCH]]

| Time | Action |
|---|---|
| 11:30 AM, Sponsor Expo | Ask Notability for Pro codes, SpaceXAI for xAI credits, Capital One whether a parametric climate payout counts as "best use", and Photon for a promo code in case it's needed. |
| 12 PM | Cursor on every laptop. Cache FIRMS and CelesTrak data in hour 1, since several space-data APIs limit requests per IP [A]. |
| 1 PM | Relay workshop, two people. Ask whether calls and video work on the App Store build. |
| 2 PM | Fetch.ai workshop, P3. Pin the `uagents` version the docs use [A]. |
| 4 PM | SpaceXAI session. Ask whether EO + orbit data counts, and whether they prefer Imagine or Voice. **Relay go/no-go.** |
| 5:30 PM | Figma workshop, P4. |
| About 6 PM | Fetch go/no-go: ASI:One end to end with one real action, or drop it and give P3 to Capital One or polish. |

### Confidence: about 55%
- The ranking at the top (Relay, SpaceX, Fetch) is fairly robust.
- Exact EVs are soft. They rest on small samples: 2 SpacetimeDB events, 2 SpaceX twin events, and no Relay precedent.

### What would flip it
1. **Relay calls fail or no one has iOS 26 →** Photon replaces Relay. Same spine; Photon + Grok has a verified win [A] ([NND]).
2. **SpaceXAI says Earth-observation and orbit data don't count →** keep the spine for Sustainability and drop SpaceX. That frees the domain: switch to an energy agent ("Payback"/"Clean Hours"), with **Capital One promoted to core**, plus Relay and Fetch. Add FREE-WILi if a hardware owner appears.
3. **A confirmed electronics owner plus FREE-WILi loaners by 2 PM →** add FREE-WILi to an energy variant, or take the verdict's Hardware flip (Skyward) [A] ([VER]).
4. **The team values cash over preferences and wants a multiplayer product →** use the "cash-max" stack: SpacetimeDB core + Fetch + Capital One. Use FinTech main only under the verdict's conditions. Avoid the wildfire prediction market, which is a reputational risk [I].
5. **No climate idea the team likes →** AI main. FinchNode moves to tier 1 ("Second Look") [A] ([S10]).

---

## 7. What I verified myself (claims checked against advocates)

| Claim | Advocate | My check | Result |
|---|---|---|---|
| Prize tables for all 12 sponsors, including Capital One 2nd/3rd and SpacetimeDB "in cash" | All | [Devpost][DP], [Tracks & Prizes][TP] | Holds. New finds: Grand Prize gets ElevenLabs Pro, and there is an MLH Best Use of ElevenLabs. |
| MHacks 2025: Fetch opt-ins 14 / 5 / 3; FREE-WiLi 5 of 122 with 2 winners | Fetch, FREE-WILi | Devpost filters and winner labels | Holds. |
| DivHacks 2026: SpaceXAI 29/65, Photon 29/65, Capital One 8/65 | SpaceX, Photon, Nessie | Devpost filters | Holds. 18 of the 29 SpaceX entrants also entered Photon. |
| HopHacks F26: SpacetimeDB 11/87, SpaceX 31/87 | SpacetimeDB | Devpost filters | Holds. It was a **choose-one** track there. 3 of the 11 also entered SpaceX. |
| SpaceX's SpaceXAI winner precedent | SpaceX (NOVA only) | [WaterFlow][WF], [NOVA][NOVA] | WaterFlow (environmental, satellite) also won. That strengthens Sustainability + SpaceX. |
| Relay workshop uses Grok Imagine and ElevenLabs | Relay | [README][RL-WS], [commits][RL-WSC] | Holds. |
| Relay calls in the public build | Relay (flagged) | [App Store][RL-AS] | v1.1 notes omit calls. The risk is real. |
| Notability is near-free | Notability | [pricing][NOT-P] | Overreach. Pro is $79.99/yr with no individual trial. |
| Nessie HTTPS only | Nessie | Live probe | Holds: HTTPS 200; HTTP connection refused. |
| FinchNode keyless demo | FinchNode | Live probe | Holds: 12 scenarios. |
| FIRMS and CelesTrak usable | Several | Live probes | Holds: the keyless 24 h FIRMS CSV and CelesTrak both returned 200. |
| Workshop times | Several | [Schedule][SCH] | Holds, including the 1 PM and 2 PM clashes. |

---

## Sources

**MHacks 2026 (official)**
- [TP] Tracks & Prizes: https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5 (read through Notion's public `loadCachedPageChunkV2` API)
- [DP] MHacks 2026 Devpost (prize list, deadline Oct 4 12:15 PM EDT): https://mhacks-2026.devpost.com/
- [SCH] Saturday schedule: https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365
- [HB] 2026 Hacker Handbook (judging window, presence rule; via advocates): https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af

**Devpost opt-in and winner checks**
- [F25a] MHacks 2025 Fetch.ai filter 90535: https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90535
- [F25b] MHacks 2025 Fetch.ai filter 90891: https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90891
- [F25c] MHacks 2025 Fetch.ai filter 90892: https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90892
- [F25-FW] MHacks 2025 FREE-WiLi filter: https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90539
- MHacks 2025 all submissions (122): https://mhacks-2025.devpost.com/submissions/search
- [WAT] Wattson: https://devpost.com/software/wattson-5btsyd
- [GES] Gestura: https://devpost.com/software/gestura-9oaugq
- [DV] DivHacks 2026: https://divhacks-2026.devpost.com/
- [DV-SX] DivHacks SpaceXAI filter: https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105135
- [DV-PH] DivHacks Photon filter: https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105999
- [DV-C1] DivHacks Capital One filter: https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105134
- [HH] HopHacks Fall 2026 (prize texts; choose-one track; "4 Cursor keyboards"): https://hophacks-fall-2026.devpost.com/
- [HH-ST] HopHacks F26 SpacetimeDB filter: https://hophacks-fall-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105907
- [HH-SX] HopHacks F26 SpaceX filter: https://hophacks-fall-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105911
- [WF] WaterFlow (HopHacks SpaceXAI + environmental winner): https://devpost.com/software/waterflow-41mrqd
- [NOVA] NOVA (DivHacks SpaceXAI winner): https://devpost.com/software/nova-hzgjy0
- [IG] Iron Glove (HopHacks SpacetimeDB winner): https://devpost.com/software/iron-glove
- [NND] News Next Door (DivHacks Photon winner, Grok; via Photon advocate): https://devpost.com/software/news-next-door

**Sponsor technology checks**
- [RL-WS] Relay MHacks workshop README: https://raw.githubusercontent.com/RelayMessenger/Relay-SDK/main/cookbook/mhacks-workshop/README.md
- [RL-WSC] Relay workshop commits: https://api.github.com/repos/RelayMessenger/Relay-SDK/commits?path=cookbook/mhacks-workshop
- [RL-AS] Relay on the App Store: https://apps.apple.com/us/app/relay-agent-messenger/id6789704419
- [WP-SX] Wikipedia, SpaceXAI: https://en.wikipedia.org/wiki/SpaceXAI
- [NOT-P] Notability pricing: https://notability.com/pricing
- [NS-API] Nessie API probe: https://api.nessieisreal.com/atms
- [FN-API] FinchNode demo scenarios: https://api.finchnode.com/demo/v1/scenarios
- [FIRMS-CSV] NASA FIRMS NOAA-20 VIIRS 24 h CSV (keyless): https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_USA_contiguous_and_Hawaii_24h.csv
- [CT] CelesTrak weather-satellite GP data: https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=json
- [FH] Fetch.ai MHacks 2026 hackpack (via Fetch advocate): https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack
- [FSUB] Fetch submission process doc (via Fetch advocate): https://docs.google.com/document/d/1UDW-X1C24hxZviFOQzjTeh0pXRNAoflMb8lhJqZP9Z0

**Team research files (claims carry their own citations)**
- [VER] Main/fun verdict: /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md
- [S01] /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/01-fetchai-asi-one-agent-challenge.md
- /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/02-elevenlabs.md
- /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/03-notability-trust-the-process.md
- /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/04-free-wili.md
- /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/05-neon-backend.md
- /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/06-photon-imessage-agents.md
- /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/07-spacex-make-it-legendary.md
- /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/08-spacetimedb.md
- /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/09-figma-best-design.md
- [S10] /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/10-finchnode-healthtech.md
- [S11] /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/11-relay-interactive-agents.md
- /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/12-capital-one-nessie.md

[TP]: https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5
[DP]: https://mhacks-2026.devpost.com/
[SCH]: https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365
[HB]: https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af
[F25a]: https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90535
[F25b]: https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90891
[F25c]: https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90892
[F25-FW]: https://mhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90539
[WAT]: https://devpost.com/software/wattson-5btsyd
[GES]: https://devpost.com/software/gestura-9oaugq
[DV-SX]: https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105135
[DV-PH]: https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105999
[DV-C1]: https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105134
[HH]: https://hophacks-fall-2026.devpost.com/
[HH-ST]: https://hophacks-fall-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105907
[HH-SX]: https://hophacks-fall-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105911
[WF]: https://devpost.com/software/waterflow-41mrqd
[NOVA]: https://devpost.com/software/nova-hzgjy0
[IG]: https://devpost.com/software/iron-glove
[NND]: https://devpost.com/software/news-next-door
[RL-WS]: https://raw.githubusercontent.com/RelayMessenger/Relay-SDK/main/cookbook/mhacks-workshop/README.md
[RL-WSC]: https://api.github.com/repos/RelayMessenger/Relay-SDK/commits?path=cookbook/mhacks-workshop
[RL-AS]: https://apps.apple.com/us/app/relay-agent-messenger/id6789704419
[WP-SX]: https://en.wikipedia.org/wiki/SpaceXAI
[NOT-P]: https://notability.com/pricing
[NS-API]: https://api.nessieisreal.com/atms
[FN-API]: https://api.finchnode.com/demo/v1/scenarios
[FIRMS-CSV]: https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_USA_contiguous_and_Hawaii_24h.csv
[CT]: https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=json
[FH]: https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack
[FSUB]: https://docs.google.com/document/d/1UDW-X1C24hxZviFOQzjTeh0pXRNAoflMb8lhJqZP9Z0
[VER]: /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md
[S01]: /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/01-fetchai-asi-one-agent-challenge.md
[S10]: /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/10-finchnode-healthtech.md
[S11]: /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/11-relay-interactive-agents.md

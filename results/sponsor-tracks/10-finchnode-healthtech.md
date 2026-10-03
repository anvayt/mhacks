# Sponsor Track Advocate — FinchNode (HealthTech)

## Prompt given (excerpt)
> You are the advocate for the sponsor track "FinchNode (HealthTech)" at MHacks 2026. Research the sponsor's tech and how fast a team can integrate it, what its judges reward, prize value vs competition, expected value, how it stacks with the main/fun picks and other sponsors, 2–3 winning project sketches, honest red flags, and a 1–10 scorecard. Make the strongest honest case — an impartial judge will weigh your file against eleven other sponsor advocates.

---

## TL;DR: the case in six lines

1. **This is the easiest sponsor integration on the board.** FinchNode's public demo API needs **no account and no key**, accepts browser requests from any origin (CORS is open to all), and serves 12 named synthetic patients. I called it live on 2026-10-03: `/scenarios` returned 12 scenarios, and the 78-year-old polypharmacy patient returned 14 medications, 40 labs and 30 vitals, coded in RxNorm and LOINC [FN-API-SCEN, FN-POLY]. There is also a **keyless MCP server**, so an LLM agent can call FinchNode tools in minutes [FN-MCP].
2. **The data is good enough to carry a real demo.** In the polypharmacy record, eGFR (a kidney-function score) falls from 39 to 31 over 18 months, potassium rises to 4.9 on lisinopril plus a potassium supplement, and she takes apixaban (an anticoagulant) with aspirin. The apixaban label says that combination raises bleeding risk [FN-POLY, OFDA-APIX]. A medication-safety agent can find real, checkable flags in this record.
3. **It is the only health outlet at MHacks 2026.** No main track covers health, but 12% of MHacks 2025 projects (15 of 122) opted into the Health track [SUS-01]. *Inference:* those teams can only go to FinchNode this year. Because entry requires "a working FinchNode integration," expect about **8–18 real entrants, which is medium competition**.
4. **The prize is modest but has two useful places.** 1st is an Apple Watch SE 3 (from $249 [APPLE]; whether it's one per team or one per member is **unverified**). **2nd is $500 cash.** Both come with "3 Months free finchnode development plan," a plan name that does not appear on FinchNode's public pricing (Free $0 / Pro $99/mo) [HB-T, FN-LLMS]. Realistic EV: **about $110–225** for about 4 hours of integration work.
5. **Stacking is the honest weak spot.** FinchNode fits the **AI** main track naturally, but the judge picked **Sustainability**. The only Sustainability-compatible version is the heat-health project in Sketch A. It combines CDC's heat-and-medication guidance, satellite land-surface temperature for SpaceX, and FinchNode med lists. It is coherent, but Sustainability judges may see it as a health project.
6. **Scorecard:** Prize value 4 · Win probability 7 · Integration ease 9 · Stacking potential 6 · Demo impact 7 · Fit with team preferences 5.

---

## 1. The technology

### What FinchNode is
- It is a **patient-authorized EHR (electronic health record) API**: "read-only patient access in the United States." A patient signs in at their own health system (Epic/MyChart, Oracle Health, athenahealth, eClinicalWorks, MEDITECH, Veradigm, Medicare Blue Button) and consents. Your app then reads normalized records through one API [FN-HOME, FN-SITEMAP].
- Records come back as **normalized JSON derived from FHIR R4** (FHIR is the standard format for health-record data), in 10 categories: demographics, medications, conditions, allergies, vitals, labs, immunizations, encounters, documents/notes, and claims. Every record keeps its source and codes (RxNorm, LOINC) [FN-DOCS, FN-POLY].
- **Limits:** read-only, US-only. No write-back to the EHR, no scheduling, no provider-side bulk pulls [FN-HOME, FN-LLMS].
- **Company identity is unverified.** The site, legal pages and blog name no founders, legal entity or location. The footer says only "FinchNode · Read-only · United States · Consent-first." The newest blog post is dated August 2026 [FN-BLOG]. *Inference:* this is a young company, and MHacks may be one of its first hackathon sponsorships (see §2).

### Three ways in

| | **Demo** (no account) | **Sandbox** (free account) | **Production** |
|---|---|---|---|
| Key | None | `ck_test_…` | `ck_live_…` |
| Base URL | `https://api.finchnode.com/demo/v1` | `https://api.finchnode.com/api/v1` | same as sandbox |
| Data | 12 fixed synthetic scenarios | Synthetic patients **you create** with `simulate` (up to 25, purged after 7 days) | Real consenting patients |
| Extras | Simulated Connect session, FHIR search, OpenAPI, keyless MCP | Hosted Connect flow, **signed webhooks**, **change feed**, **sandbox controls** (`records.advance`, `consent.revoke`, `consent.expire`, `source.fail`), conformance runs, TEFCA sandbox, authenticated MCP (14 tools), short-lived per-patient agent credentials | Real EHRs |
| Rate limit | 120 req/min **per network address** | 300 req/min per key | 300 req/min per key |

Sources: [FN-ENV, FN-DEMO, FN-QS, FN-CTRL, FN-MCP, FN-MCPT, FN-AGENT, FN-TEFCA, FN-LLMS]. The demo response headers I received show `access-control-allow-origin: *` and `ratelimit-limit: 120` [FN-API-SCEN].

**Cost:** $0. The Free plan includes "a synthetic sandbox included with every account," hosted consent, scheduled sync and signed webhooks. Pro is $99/month for up to 5 production apps [FN-LLMS].

### The 12 demo scenarios (verified by calling `/scenarios`, 2026-10-03)

| Scenario | What it contains / exercises |
|---|---|
| `baseline-adult` (38) | Type 2 diabetes + hypertension; 2 meds, 2 labs. The default patient. |
| **`polypharmacy-senior`** (78) | **14 active meds, CKD stage 3, atrial fibrillation, heart failure, 40 labs, 30 vitals over two years.** `records.advance` removes a medication (sandbox only). |
| `pediatric-asthma` (9) | Growth vitals across 8 visits, controller and rescue inhalers, partial immunizations, 2 acute visits |
| `multi-source-overlap` (40) | Same patient at Northstar and Quillhaven, with duplicate records under different IDs and dates, plus one unit difference |
| `sparse-record` (30) | Demographics and one visit, every other category empty |
| `messy-coding` (63) | Free-text meds without RxNorm, missing values, weight in pounds, glucose in mmol/L |
| `rate-limited`, `consent-revoked`, `consent-partial`, `source-unavailable` | Error behavior: 429 / 410 / 403 / partial sync |
| `connect-cancelled`, `connect-failed` | Connect sessions that end with no patient |

Source: [FN-API-SCEN]. The polypharmacy details come from my own pull of [FN-POLY]. Its trends: creatinine 1.4→1.7 mg/dL, eGFR 39→31, potassium 4.3→4.9 mmol/L, A1c 7.4→6.8%, hemoglobin 11.4 g/dL (low). Medications include apixaban, aspirin 81 mg, furosemide, metoprolol, lisinopril, potassium chloride, metformin, sertraline and trazodone. Allergies: sulfonamide (high severity) and contrast media. The `documents` and `claims` categories are **empty** in the demo [FN-POLY].

### MCP: the fast path for an agent
- **Demo MCP** at `https://api.finchnode.com/demo/mcp` needs no auth. I ran `tools/list` and it returned 14 tools, including `list_demo_scenarios`, `get_demo_health_record`, `search_demo_fhir` and `simulate_demo_connect`. A `tools/call` for the polypharmacy patient's allergies came back correctly [FN-MCP].
- **Gotcha:** the per-category demo tools (`get_demo_medications` etc.) "always return `baseline-adult`." Use `get_demo_health_record` with a `scenario` instead [FN-MCP].
- The **authenticated MCP** has 14 tools that mirror REST, including `simulate_connect_session` and `trigger_sandbox_event` [FN-MCPT]. FinchNode's docs give one-line setup for Claude Code, Codex and Cursor [FN-MCP]. Cursor matters because the SpaceX track requires it [HB-T].
- FinchNode's docs are all available as Markdown, plus `llms-full.txt` and `openapi.yaml`, so coding agents can read them. A FinchNode coding-agent plugin is announced but "isn't published yet" [FN-PLUGIN].

### MHacks 2026 resources
- **Workshop, today (Sat Oct 3), 2:00–3:00 PM, Duderstadt VR Lab:** "FinchNode: From Health Data to Healthcare Apps with FinchNode." They will walk through "accessing synthetic patient records through our public demo API and using that data in a simple prototype, then discuss ideas you can build for the FinchNode challenge. No prior healthcare experience is needed." [LIVE, SCHED]
- No credits, keys or mentors are listed beyond that, and none are needed. Judging is Sun Oct 4, 12:30–2:30 PM: 3-minute pitches, with sponsors judging their own tracks at the same time, and **the team must be present** [HB].

### Realistic integration time (one owner)

| Step | Hours |
|---|---|
| Read demo docs and pull the polypharmacy record (curl / `fetch`) | 0.5 |
| Wire records into the app: meds, labs, allergies, conditions with RxNorm/LOINC codes; trend charts | 1.0–1.5 |
| **"Best use" depth:** sandbox account and key, `connect/sessions` → `simulate`, poll `simulation.state`, webhook receiver (signature check, 5-second ack), `records.advance` live during the demo | 1.5–2.0 |
| Consent/error states: `consent-revoked` (410), `consent-partial` (403), `source-unavailable` | 0.5 |
| **Total** | **3.5–4.5 → best single estimate: 4 h** |

The demo-only version takes about 1.5 hours. The extra 2.5 hours buy the webhook, change-feed and consent features. Those are what separate "used FinchNode" from "best use of FinchNode" (§2).

### Known gotchas
1. **The demo rate limit is per IP address.** If many teams on MGuest Wi-Fi share a public IP, 120 requests a minute could run out during the 2 PM workshop rush. *Inference:* venue NAT is unverified. **Fix:** cache the fixed demo JSON locally (the records never change), or use a sandbox key (300 per minute, per key) [FN-API-SCEN, FN-LLMS].
2. **Sandbox controls don't work on the demo.** The `controls` field in `/scenarios` "describe[s] the authenticated FinchNode sandbox; the accountless demo cannot perform them" [FN-OPENAPI]. The live "new lab arrives" moment needs a free account.
3. **Poll `simulation.state`, not `status`.** For some scenarios, `status` reads `completed` before the simulation finishes [FN-QS].
4. **Keys must stay server-side.** The docs say never put one in a browser or mobile app [FN-ENV]. Webhooks need a public HTTPS URL that answers within 5 seconds [FN-LLMS], so use a deployed backend or a tunnel.
5. **The data is thin in places.** Only 6 patients have records. There are no clinical notes or claims in the demo [FN-POLY]. Teams can't do a "summarize the doctor's notes" project with this data.
6. **Medical-advice risk.** Any LLM output about medications will draw judge scrutiny. Ground every flag in a cited source (openFDA labels [OFDA-APIX, OFDA-MET], CDC guidance [CDC-MED]) and frame the output as "for review with your clinician."
7. **Health data and model providers.** FinchNode warns that before an agent sends records to a model provider, you should check that your agreements cover health data [FN-MCP]. This doesn't apply to synthetic data, but say so in the pitch, because it shows judges the team understands the issue.

---

## 2. What this sponsor's judges reward

**Official text** (Tracks & Prizes; the track's real title is "Build Better Personalized Healthcare with FinchNode"):
> "Build an app that makes healthcare easier for patients, clinicians, or care teams using the FinchNode API. Projects should demonstrate a working FinchNode integration using our synthetic demo health records." [HB-T]

**No FinchNode prize history found.** Devpost's site search returned 403. My web-search budget was exhausted, so I couldn't search beyond that. I checked the Devpost pages of DivHacks 2026, PennApps XXVI, Hack the North 2026, HackRice 16 and Bitcamp 2026, and none mentions FinchNode [DP-CHECK]. This doesn't prove FinchNode never sponsored elsewhere, but I can cite no past FinchNode winners.

**What FinchNode itself emphasizes** (*inference from its own materials*):
- **Consent and provenance are core.** The tagline is "Consent-first." Docs cover revocation, partial consent, freshness and stale sources. Their blog includes "How to normalize FHIR data across EHRs without losing the source" and "Build a longitudinal patient record with TypeScript" [FN-HOME, FN-BLOG, FN-SITEMAP].
- **They built scenarios to be exercised.** Each scenario ships with an `exercises` list: pagination past 25 records, MedicationDispense alongside MedicationRequest, reference ranges on every lab, unit mismatches, dedupe across sources [FN-API-SCEN]. A project that handles `multi-source-overlap` or `messy-coding` correctly is speaking FinchNode's own language.
- **Agents are a stated use case.** FinchNode offers an MCP server, delegated per-patient agent credentials, and an upcoming coding-agent plugin [FN-MCP, FN-AGENT, FN-PLUGIN]. An agent that reads records through scoped credentials is a showcase of their product.
- **The workshop pitch is "health data → working healthcare app"** [LIVE]. That favors a finished product over a data viewer. FinchNode already ships its own Visualizer (FHIR bundle, reference graph, JSON inspector) [FN-VIS], so **don't build another record viewer**.

**Proxy evidence: what health projects won at MHacks** (from our year research):

| Year / prize | Winner | Why it won |
|---|---|---|
| 2025 Lifeline (Health) | Dementia Assistant: AR face recognition plus live transcript | Specific user, working demo, a real technical gap closed [Y25] |
| 2024 Health Track | NurseNotes: nurse voice notes → structured SOAP(IE) reports | Narrow user and a vivid statistic ("41% of an average nurse's shift is spent doing paperwork"); simple and worked end to end [Y24] |
| 2024 Google 2nd ($700) | Healthcare Helper: AI intake interview → doctor summary and flags | A clinician-facing output from a patient conversation [Y24] |
| 2023 Social Impact | CogniCare: Alzheimer's companion | A specific vulnerable group [Y23] |
| 2023 MLH Streamlit | Pinpoint Ai: ER misdiagnosis helper grounded in vetted PDFs | **Grounded** LLM rather than raw chat [Y23] |

**The rubric to play to** (*inference*): (1) a named user and a care moment ("78-year-old on 14 meds whose daughter manages her care"); (2) FinchNode data that **changes what happens**, not just what's displayed; (3) a live event in the demo: a new lab arrives via `records.advance` → webhook → the app acts; (4) consent shown on screen, plus graceful handling when consent is revoked; (5) every clinical flag cites its source. The MHacks-wide criteria (innovation, technical complexity, usability, presentation) [HB] line up with this.

---

## 3. Prize value and expected competition

| Place | Official | Realistic value to a 4-person team |
|---|---|---|
| 1st | "Apple Watch SE3 + 3 Months free finchnode development plan" [HB-T] | **$249** if one watch [APPLE]; **$996** if one per member (**unverified**; the text doesn't say "per member," unlike FREE-WILi's "for each team member" [HB-T]). The plan is worth **~$0** in practice, because the Free tier already includes sandbox and one production app. Nominally ≤ $297 if it equals Pro at $99/mo [FN-LLMS]. |
| 2nd | "500 cash for second place + 3 Months free finchnode development plan" [HB-T] | **$500 cash.** That is more liquid than 1st place unless the watch is per member. |
| 3rd | "3 Months free finchnode development plan" [HB-T] | **~$0** practical, plus a résumé line |

**Expected competition: medium** (*inference*):
- **Baseline interest:** 15 of 122 MHacks 2025 projects (12%) opted into Lifeline (Health) [SUS-01].
- **This year's routing:** with no health main track, FinchNode is the only health-themed prize, so health teams have one place to go. A required working integration filters out box-tickers. The 2 PM workshop and "no prior healthcare experience is needed" pull in extra teams [LIVE].
- **Estimate:** about **8–18 real entrants**, assuming roughly 120–150 submissions. That is more than FREE-WILi's 5 of 122 in 2025 [FW-04], and fewer than the AI-agent sponsor tracks (Fetch.ai, ElevenLabs, Relay, SpaceX).

---

## 4. Expected value

All probabilities are my inference. They assume the team builds a focused health project with sandbox-level integration (the 4-hour version).

| | P(1st) | P(2nd) | P(3rd) | EV (one watch, plan = $0) | EV (watch per member) |
|---|---|---|---|---|---|
| **Focused FinchNode-first project (Sketch B)** | 0.18 | 0.17 | 0.15 | 0.18×249 + 0.17×500 ≈ **$130** | 0.18×996 + 85 ≈ **$265** |
| **FinchNode as one of several sponsors (Sketch A)** | 0.13 | 0.13 | 0.12 | ≈ **$97** | ≈ **$195** |
| Demo-API-only bolt-on | 0.05 | 0.06 | 0.08 | ≈ $42 | ≈ $80 |

**Best single number: about $110–225 EV**, which is **~$28–55 per integration hour** at 4 hours.

**Compared with sibling advocates' estimates:** Neon realistic EV ≈ $130 [NEON-05]; Photon native-first ≈ $80 at ~$20–25/h [PHOTON-06]; Notability ≈ $80 at ≈ $40/person-hour [NOTA-03]. FinchNode lands in the same band in raw dollars. Its edge is **probability**: about a 50% chance of placing for a focused team, with the $500 cash prize sitting at 2nd. The big-pool tracks (Fetch.ai $1,250/$750/$500; SpacetimeDB $1,000/$500/$200; Capital One $300 per member [HB-T]) have higher ceilings and more competition.

**Spillover value:** a concrete health user and a grounded flag ("eGFR 31 and falling, on metformin; the label contraindicates it below 30" [FN-POLY, OFDA-MET]) helps any main-track pitch on "real problem" and usability [HB].

---

## 5. Stacking

### Main track fit

| Main track | Fit | Why |
|---|---|---|
| **Actually Intelligent (AI)** | **Natural** | "AI that actually solves a real problem" [HB-T]. A grounded medication-safety agent is exactly that. Downside: AI is likely the most crowded main track (about 47% of 2025 projects listed an LLM tool [VERDICT]). |
| **Sustainability** (the judge's pick) | **Possible, but only via climate-health** | Heat is a climate impact. CDC lists diuretics, beta blockers, ACE inhibitors/ARBs, SSRIs/SNRIs, anticholinergics and others as raising heat-illness risk, and singles out older patients on multiple medications [CDC-MED]. The polypharmacy patient takes four of those classes (furosemide, metoprolol, lisinopril, sertraline) [FN-POLY]. Risk: the Sustainability text says "energy, climate, and resource systems" [HB-T], and judges may score theme adherence down. The Sustainability advocate called heat-health "a stretch" [SUS-01]. |
| Beyond the Code (Hardware) | Good | A medication-adherence device. The Hardware advocate already sketched a FREE-WILi + FinchNode build [HW-03]. |
| FinTech | Poor | The demo has no claims or coverage data [FN-POLY]. Health-cost ideas would rely on Nessie's mock banking, not health data. |

**My position as advocate:** FinchNode is strongest under **AI** (Sketch B). If the team keeps **Sustainability**, FinchNode is still enterable through **Sketch A**, which is also the only design that puts Sustainability, SpaceX and FinchNode in one project. I would not flip the main track for FinchNode alone. The verdict's flip "No climate angle → AI" [VERDICT] is where FinchNode becomes a top-3 sponsor pick.

### Fun tracks
- **Judged by an LLM: good.** A grounded, cited, well-documented health agent is easy for an LLM judge to recognize as technically sharp.
- **Dumbest Idea / Useless AI: conflict.** Joking about synthetic sick patients reads badly to a health sponsor. The Useless AI advocate reached the same conclusion [UAI-04].

### Other sponsors

| Sponsor | With FinchNode | Notes |
|---|---|---|
| **Relay** | **Strong** | Relay's own idea list includes "🏋️ Fitness: gym coach" [HB-T]. A care agent you text or call is a natural fit. Relay agents run on your backend via webhook/WebSocket, so the backend can call FinchNode. An agent's first message to a new user is held as a request until the user replies [RELAY]. |
| **Fetch.ai** | Good | An Agentverse agent that turns "is my mom okay in this heat?" into record lookup → risk → action [HB-T]. Needs the extra ASI:One submission [HB-T]. |
| **ElevenLabs** | Good | A clear, slow voice for older patients. |
| **Photon (iMessage)** | Good | A caregiver group chat where the agent posts alerts. |
| **Neon** | Good | Store imported records, the change cursor and alert history in Postgres. |
| **SpacetimeDB** | OK | A live shared care-team board (patient, daughter and nurse see the same alert state). A stretch as "core real-time backend." |
| **SpaceX** | **Only via Sketch A** | Satellite land-surface temperature. ECOSTRESS images Earth's surface temperature from the **International Space Station** at 70 m resolution, with urban-heat applications [ECO]. Requires Cursor + Grok Imagine or Voice [HB-T]. Whether SpaceX judges accept Earth observation as "space data" is **unverified**; ask at the SpaceXAI session (4–5 PM) [LIVE, VERDICT]. |
| FREE-WILi | Hardware only | Sketch C. |
| Figma / Notability | Neutral, near-free | |
| **Capital One Nessie** | **Conflict** | No coherent money angle in this data. |

---

## 6. Project sketches

### Sketch A: "HeatCheck": climate-heat medication-risk agent *(Sustainability · Judged by an LLM · FinchNode · SpaceX · Relay · ElevenLabs/Grok Voice · Neon)*
- **User:** an adult daughter managing a 78-year-old parent's care during a heat wave.
- **What it does:**
  1. **Satellite heat:** a pre-processed ECOSTRESS land-surface-temperature tile for the demo city [ECO], plus the NWS HeatRisk 7-day level (0–4) [NWS-HR], gives "how hot *her* block gets."
  2. **FinchNode:** the patient's meds and conditions, with RxNorm codes mapped to CDC's heat-risk classes [CDC-MED, FN-POLY]. For the demo's 14 medications, a hand-made lookup table is enough.
  3. **Risk score and plan:** "HeatRisk orange + diuretic + beta blocker + CKD → call today." The plan follows CDC's advice to review medication plans on HeatRisk orange/red/magenta days [CDC-MED]. It never says "stop your medication."
  4. **Action:** the agent texts or calls through Relay, speaks in a Grok Voice or ElevenLabs voice, and logs the check-in to Neon.
- **The live moment:** `records.advance` on the sandbox patient → `records.updated` webhook → the agent re-scores and sends a new text on stage [FN-CTRL].
- **Honest problems:** it's October in Michigan, so live HeatRisk will read green. Ship a "replay a July heat wave" mode and label it. ECOSTRESS access (Earthdata login, file format) is **unverified**, so budget 2–3 hours, or cut the satellite tile if it isn't working by midnight.
- **Why it can win FinchNode:** the FinchNode data drives the decision, and the demo shows consent, webhooks and a live record change.

### Sketch B: "Second Look": callable medication-safety agent *(AI main · Judged by an LLM · FinchNode · Relay · Fetch.ai · ElevenLabs · Neon)* ← **highest FinchNode win probability**
- **User:** the same caregiver, or the patient, asking "my doctor added X, is that okay?"
- **What it does:** it pulls the polypharmacy record (FinchNode REST or MCP), then runs **deterministic checks first and the LLM second**. Examples:
  - **Renal:** eGFR trending 39→31; metformin is contraindicated below 30 per its label [FN-POLY, OFDA-MET]. Flag "approaching threshold; ask at next visit."
  - **Bleeding:** apixaban + aspirin; the label says aspirin "increases the risk of bleeding" [OFDA-APIX].
  - **Allergy cross-check** against the sulfonamide allergy (high severity) [FN-POLY].
  - **Potassium trend** (4.3→4.9) alongside lisinopril and a potassium supplement [FN-POLY]. Phrase it as a trend for review, not a diagnosis.

  The LLM writes a plain-language brief for the patient and a one-screen summary for the clinician. Every line links to the record ID and the label section it came from.
- **FinchNode depth:** a sandbox Connect session, a **delegated agent credential** scoped to `medications` + `labs` for 15 minutes [FN-AGENT], handling of `consent-partial` (403) and `consent-revoked` (410), and dedupe of `multi-source-overlap` [FN-SCEN].
- **Eval for the AI track and the LLM judge:** run all 6 record scenarios and show which flags fired against a hand-labeled answer key.
- **Why it wins:** a named user, grounded output, live consent behavior, and the product's own agent features. That is "best use," not "used it."

### Sketch C: "Shake & Check": pill-bottle adherence device *(Hardware · FinchNode · FREE-WILi · Relay · ElevenLabs)*
- Built on the Hardware advocate's sketch [HW-03]. The FREE-WILi accelerometer detects a pill-bottle shake, and the app matches it to the FinchNode med list and schedule. A missed dose or a wrong bottle triggers a spoken warning plus a caregiver text through Relay.
- **Use only if** the verdict's Hardware flip happens (a confirmed electronics owner by noon) [VERDICT]. Otherwise skip it.

---

## 7. Red flags, rival arguments, rebuttals

| Rival argument | Strength | Rebuttal |
|---|---|---|
| "The prize is small: one $249 watch, and the dev plan is worth nothing." | **Strong** | True for 1st if it's one watch. But 2nd is **$500 cash**, so the prize curve is flat and a top-2 finish pays. EV per hour (~$28–55) matches Neon, Photon and Notability (§4). |
| "It breaks the judge's Sustainability pick." | **Strong** | Only Sketch A survives Sustainability, and theme-fit risk is real. If the team won't commit to heat-health, take FinchNode only under the AI flip. |
| "Unknown company with no hackathon record; you can't know what they reward." | Medium | Correct, and §2 marks it. Their docs and scenario `exercises` say plainly what they value (consent, provenance, normalization, agents). A young company also tends to reward teams that use its newest features (MCP, agent credentials) *(inference)*. |
| "Health draws a crowd of polished pre-med teams." | Medium | Expect 8–18 entrants (*inference*). The required working integration filters out box-tickers, and depth of the 4-hour version (webhooks, consent states) is rare. |
| "LLM health advice is a liability judges will attack." | Medium | Deterministic checks first, label citations on every flag, "review with your clinician" framing, synthetic data only. This is also what wins the LLM-judged fun track. |
| "Demo rate limit and Wi-Fi." | Low | Cache the fixed JSON; sandbox keys get 300/min per key [FN-LLMS]. |
| "Data is fake and thin: 6 patients, no notes." | Low–Medium | Six patients is enough for one strong story. Polypharmacy alone has 2 years of trends [FN-POLY]. Avoid note-summarizing ideas. |

**Red flags to settle at the 2 PM workshop:** (1) Is the Apple Watch one per team or one per member? (2) What exactly is the "development plan"? (3) Is a sandbox-key integration (simulated patients) acceptable as "our synthetic demo health records"? *Inference:* yes, since both are synthetic, but confirm. (4) Who judges, and will they come to our table during the 12:30–2:30 PM window? [HB]

---

## 8. Scorecard

| Criterion | Score | One-line justification |
|---|---|---|
| Prize value | **4** | $249 watch (if one per team) and $500 cash for 2nd; the dev plan is ~$0 in practice because the Free tier covers hackathon needs. |
| Win probability | **7** | Medium field (~8–18), three places, and a required integration that filters out box-tickers; no prior FinchNode winners to calibrate against. |
| Integration ease | **9** | No key, open CORS, keyless MCP, verified live; about 1.5 h for the demo-only version, 4 h for the full "best use" version. |
| Stacking potential | **6** | Excellent with AI, Relay, Fetch.ai, ElevenLabs, Photon, Neon and Judged by an LLM; Sustainability only via heat-health; conflicts with Capital One and both joke tracks. |
| Demo impact | **7** | A live `records.advance` → webhook → agent call is a strong 3-minute moment; health stakes are clear. |
| Fit with team preferences | **5** | Fits Relay and the team's appetite for several sponsors; reaches SpaceX only through Sketch A; doesn't stack with Capital One. |

**Bottom line:** FinchNode is a **cheap, high-probability, mid-value** sponsor track. With the judge's Sustainability pick, enter it **only if** the team builds Sketch A (heat-health). Under an AI main track, it belongs in the top tier of sponsor picks, built as Sketch B.

---

## Sources
- [HB-T] MHacks 2026 Tracks & Prizes (FinchNode text, prizes, other sponsor texts; read via Notion's public page API): https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5
- [HB] MHacks 2026 Hacker Handbook (judging times, 3-minute pitches, sponsors judge concurrently, must be present): https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af
- [LIVE] MHacks live schedule (FinchNode workshop 2–3 PM, VR Lab, with summary): https://www.mhacks.org/live
- [SCHED] MHacks schedule sheet, Saturday: https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365 · Sunday: https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=83169850
- [FN-HOME] FinchNode home: https://finchnode.com/
- [FN-LLMS] FinchNode llms.txt (plans, demo vs production, rate limits): https://finchnode.com/llms.txt
- [FN-DOCS] FinchNode docs: https://finchnode.com/docs
- [FN-DEMO] Demo API docs: https://finchnode.com/docs/get-started/demo-api
- [FN-API-SCEN] Live demo scenario list (called 2026-10-03): https://api.finchnode.com/demo/v1/scenarios
- [FN-OPENAPI] Demo OpenAPI spec: https://api.finchnode.com/demo/v1/openapi.json
- [FN-POLY] Live polypharmacy record (called 2026-10-03): https://api.finchnode.com/demo/v1/users/patient-demo-polypharmacy/records
- [FN-QS] Quickstart: https://finchnode.com/docs/get-started/quickstart
- [FN-ENV] Environments and keys: https://finchnode.com/docs/get-started/environments-and-keys
- [FN-MCP] MCP server: https://finchnode.com/docs/ai-agents/mcp-server (demo endpoint tested: https://api.finchnode.com/demo/mcp)
- [FN-MCPT] MCP tools: https://finchnode.com/docs/api/mcp-tools
- [FN-AGENT] Delegated agent credentials: https://finchnode.com/docs/ai-agents/agent-credentials
- [FN-PLUGIN] Coding-agent plugin: https://finchnode.com/docs/ai-agents/coding-agent-plugin
- [FN-CTRL] Sandbox controls: https://finchnode.com/docs/testing/sandbox-controls
- [FN-SCEN] Scenarios: https://finchnode.com/docs/testing/scenarios
- [FN-TEFCA] TEFCA sandbox API: https://finchnode.com/docs/tefca/developer-api
- [FN-BLOG] FinchNode blog: https://finchnode.com/blog
- [FN-VIS] FinchNode Visualizer: https://finchnode.com/tools/finchnode-visualizer
- [FN-SITEMAP] FinchNode sitemap (integrations, docs and blog index): https://finchnode.com/sitemap.xml
- [APPLE] Apple Watch SE 3 price ("From $249"): https://www.apple.com/shop/buy-watch/apple-watch-se
- [CDC-MED] CDC, Heat and Medications – Guidance for Clinicians: https://www.cdc.gov/heat-health/hcp/clinical-guidance/heat-and-medications-guidance-for-clinicians.html
- [NWS-HR] NWS HeatRisk: https://www.wpc.ncep.noaa.gov/heatrisk/
- [ECO] NASA JPL ECOSTRESS: https://ecostress.jpl.nasa.gov/
- [OFDA-APIX] openFDA apixaban label (section 7.3, aspirin and bleeding): https://api.fda.gov/drug/label.json?search=openfda.generic_name:"apixaban"&limit=1
- [OFDA-MET] openFDA metformin-containing label (contraindicated at eGFR below 30): https://api.fda.gov/drug/label.json?search=openfda.generic_name:"metformin+hydrochloride"&limit=1
- [RELAY] Relay developer docs index: https://docs.relayapp.im/llms.txt
- [DP-CHECK] Devpost pages checked for "FinchNode" (none found): https://divhacks-2026.devpost.com/ · https://pennapps-xxvi.devpost.com/ · https://hackthenorth2026.devpost.com/ · https://hackrice-16.devpost.com/ · https://bitcamp-2026.devpost.com/ (Devpost software search returned 403: https://devpost.com/software/search?query=finchnode)
- [SUS-01] Sustainability advocate (MHacks 2025 Lifeline 15/122 from Devpost prize filters): /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/01-main-sustainability.md · gallery: https://mhacks-2025.devpost.com/project-gallery
- [VERDICT] Main/fun debate and verdict: /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md
- [HW-03] Hardware advocate: /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/03-main-beyond-the-code-hardware.md
- [UAI-04] Useless AI advocate: /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/04-fun-useless-ai.md
- [FW-04] FREE-WILi advocate (5 of 122 entrants in 2025): /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/04-free-wili.md
- [NEON-05] Neon advocate EV: /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/05-neon-backend.md
- [PHOTON-06] Photon advocate EV: /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/06-photon-imessage-agents.md
- [NOTA-03] Notability advocate EV: /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/03-notability-trust-the-process.md
- [Y23] 2023 year research (CogniCare, Pinpoint Ai): /Users/anvaytodkar/Code/mhacks/results/year-research/2023.md · https://devpost.com/software/cognicare-companion-app-for-memory-support · https://devpost.com/software/pinpoint-ai
- [Y24] 2024 year research (NurseNotes, Healthcare Helper): /Users/anvaytodkar/Code/mhacks/results/year-research/2024.md · https://devpost.com/software/nursenotes · https://devpost.com/software/healthcare-helper
- [Y25] 2025 year research (Dementia Assistant): /Users/anvaytodkar/Code/mhacks/results/year-research/2025.md · https://devpost.com/software/dementia-assistant

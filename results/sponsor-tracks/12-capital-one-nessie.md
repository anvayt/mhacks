# Sponsor Track Advocate — Best Use of Nessie (Capital One)

## Prompt given (excerpt)
> You are the advocate for the sponsor track "Best Use of Nessie (Capital One)" at MHacks 2026. Research the sponsor's tech and how fast a team can integrate it, what its judges reward, prize value vs competition, expected value, how it stacks with the main/fun picks and other sponsors, 2–3 winning project sketches, honest red flags, and a 1–10 scorecard. Make the strongest honest case — an impartial judge will weigh your file against eleven other sponsor advocates.

Legend: **[V]** = I verified it myself on 2026-10-03 (live request, page or Devpost recount). **[I]** = my inference or estimate. No 2020 material is used here.

---

## 0. The case in brief

- **The prize is bigger than the brief said, and it is close to cash.** The handbook and Devpost now list three places [V] ([Tracks & Prizes][TP], [Devpost][DP]):
  - 1st: $300 Giftogram per team member.
  - 2nd: $75 per member.
  - 3rd: $25 per member.
  - Each place also gets "one premium swag item for each participant".
  - For a team of four, that is **$1,200 / $300 / $100**.
  - The 2nd and 3rd places were added overnight: Notion shows those blocks edited around 01:17 EDT today [V].
  - Giftogram lets the recipient choose from "140,000+ brands", Amazon included ([Giftogram][GG]). So treat it as about face value.
- **Nessie is alive and in heavy use this season, but it was rebuilt, and the old tutorials are wrong** [V]:
  - HTTPS works. Plain HTTP refuses the connection.
  - Every fresh key starts with zero customers and zero merchants, so you seed your own data.
  - The system-wide data shows 4,568 accounts and 1,651 bills, 1,615 of them created in Sept 2026. The new backend is in active hackathon use.
- **Nessie does *not* mean you have to pick the FinTech main track.** It is a sponsor track you add on top of any main track ([Handbook][HB]: "On top of your main track, submit to as many sponsor tracks as apply"). Recent Capital One winners were:
  - a trucking-logistics tool,
  - a social-planning iMessage agent,
  - a tenant/landlord escrow tool,
  - a financial life-sim game.
  
  None of them were plain bank apps (§2).
- **Competition is medium.** Capital One drew a median of **18%** of submissions across 14 peer events. It drew **12%** at the two Sept 2026 events that, like MHacks, call it "Best Use of Nessie" [V] (§3). About 40% of Nessie entries are budgeting or spend-tracker clones [I], so a differentiated project has three places to aim at.
- **My recommendation:** keep the judge's **Sustainability** main track and make Nessie the money layer of an energy project (Sketch A). That keeps Relay and Judged by an LLM, and keeps SpaceX in play if SpaceX accepts satellite Earth data. **FinTech main + Nessie gains about $75 in Nessie EV but costs about as much in main-track EV and drops SpaceX.** It is worth it only under the judge's flip condition (§5).

---

## 1. The technology

### What it is
Nessie is "Capital One's Hackathon REST API. Build banking apps with mock customer data, ATM locations, and peer-to-peer transactions" ([nessieisreal.com][NR], page meta) [V].

The MHacks brief says it gives "access to mock financial data including accounts, merchants, bills, and peer-to-peer transactions… We want to see projects that creatively integrate Nessie's endpoints to empower users and improve their financial lives" ([Tracks & Prizes][TP]) [V].

### Access and cost
- **Signup:** one teammate signs in with GitHub on nessieisreal.com. Per the getting-started page, this gives "your own API key and customer sandbox" ([getting started][GS]) [V].
- **Auth:** the key goes in the query string, `?key=…` (OpenAPI `securitySchemes: ApiKeyAuth, in: query` ([spec][SPEC])) [V].
- **Cost:** free. I found no pricing page; the site is a free Capital One sandbox [I].
- **Platform constraints:** none. It is plain REST/JSON from any language.

### Endpoints (current spec, v1.0.0, OpenAPI 3.0.3 ([spec][SPEC])) [V]
- **Customers and accounts:** `GET/POST /customers`, `GET/PUT /customers/{id}`, `GET/POST /customers/{id}/accounts`, `GET/PUT/DELETE /accounts/{id}`.
- **Money movement:** `GET/POST /accounts/{id}/bills | deposits | withdrawals | loans`, plus per-object PUT/DELETE.
- **Merchants:** `GET/POST /merchants`, `GET/PUT /merchants/{id}`.
- **Read-only reference data:** `/atms`, `/branches`.
- **Read-only, system-wide "analyst" data:** `/enterprise/customers`, `/enterprise/deposits`, and others. You "can perform GET requests to read all data in the system, but you cannot add, modify, or delete any data" ([getting started][GS]).
- **The spec is incomplete.** It omits purchases and account transfers, but the live routes exist: `GET /accounts/x/purchases` returned 200 `[]`, and `GET /accounts/x/transfers` returned 404 "No transfers found for this account" [V]. I did not test any POST (I did not write to a third-party service).

### Live health check (my requests, 2026-10-03) [V]
| Probe | Result |
|---|---|
| `https://api.nessieisreal.com/atms?key=…` | 200. Cold call 1.3–1.9 s, then **0.12–0.7 s** over 5 samples per endpoint |
| `http://api.nessieisreal.com/atms` | **Connection refused.** HTTPS only |
| `https://api.nessieisreal.com` (no path or key) | 403 `Missing Authentication Token` (AWS API Gateway style). `/atms` with no key returns 502 |
| `/customers`, `/merchants` with a fresh key | **`[]`**. Your sandbox starts empty |
| `/atms` | **13 ATMs, all in Arlington, VA** |
| `/branches` | 207 branches in MD/VA/DC. **None in Michigan** |
| `/enterprise/accounts` | 4,568 accounts (2,143 checking, 1,264 savings, 1,161 credit card). 1.16 MB, about 5.5 s |
| `/enterprise/bills` | 1,651 bills: 25 dated Aug 2026, **1,615 Sept 2026**, 11 Oct 2026 |
| `/enterprise/transfers` | 275 transfers, 228 of them in Sept 2026 |
| `/enterprise/customers` | 1,328 customers. The top city is Blacksburg (705), which matches VTHacks 14 [I] |
| `/enterprise/deposits` | **502 after ~26 s** (gateway timeout) |
| Old `/data` reset route | 403. Gone |
| Key validation | GETs returned 200 even with made-up key strings. Data is still scoped per key. Don't rely on this; sign in properly |

**Verdict on health:** the API is up and actively used by other hackathons this month. The *built-in* data is thin: 13 ATMs and DC-area branches. The *system-wide* data is large but made of other teams' test records ("Scurry sample campus market", "QA Arrendador"). **Plan to seed your own customer, accounts, merchants, bills and purchases** [V/I].

### SDKs
The site lists iOS, Android, Ruby and JavaScript SDKs ([SDK page][SDK]) [V]. On GitHub they are stale:
- JavaScript: last push May 2024.
- Python: Dec 2022.
- Go: 2018.
- Ruby: 2015.

([GitHub org API][GHO]) [V]. The new backend uses UUID `_id`s; the 13 legacy ATMs still have old Mongo IDs [V]. *Inference:* skip the SDKs and write a ~40-line `fetch` wrapper.

### MHacks-specific resources [V]
- **No Nessie workshop is scheduled.** Capital One's Saturday slot is "**CapOne: Nintendo Smash Event**", 3:00 PM, Duderstadt Room 3336 ([schedule, Sat][SCH1]).
- That event has its own prize: "1st: $150 gift card + Premium Swag Package" (the line is cut off in the handbook) ([Tracks & Prizes][TP]).
- The **Sponsor Expo is at 11:30 AM** in Pierpont Connector Hall ([schedule][SCH1]). That is the best chance to ask Capital One reps what they will judge on.
- No API credits are needed. No mentor list for Capital One is published.

### Realistic integration time: **≈ 4 hours** (one person) [I]
| Task | Hours |
|---|---|
| GitHub sign-in, key, first successful call | 0.25 |
| Seed script: 1 customer → checking/savings/credit accounts → 15–25 merchants (Ann Arbor geocodes) → 90 days of purchases and recurring bills | 1.25 |
| Read path: balances, bills, purchases → the app's core calculation | 1.0 |
| Write path: create an account or transfer, update a bill (the "both ways" use that won VTHacks, §2) | 0.75 |
| Fixture fallback, cache, and a "Powered by Capital One Nessie" badge where the data appears | 0.5 |

A bolt-on (read-only, cosmetic) takes about 1.5 hours, but it is unlikely to win (§4).

### Known gotchas
1. HTTPS only (`http://` is refused).
2. The spec has no purchase or transfer routes.
3. The SDKs are stale.
4. Sandboxes start empty.
5. ATMs and branches are DC-area only, so local maps need seeded merchants.
6. `/enterprise/*` is slow and can time out. Never call it live in the demo.
7. **Everything you write can be read by every other team** through `/enterprise`. Use fake data only.
8. There is no reset route. Namespace your seed data so a re-seed doesn't pile up duplicates.

[V for each; the fixes are I]

---

## 2. What Capital One's judges reward

**Stated criteria.** MHacks lists no Capital One-specific rubric. The general MHacks rubric is "innovation, technical complexity, usability, and presentation quality" in a 3-minute pitch, with sponsors judging their tracks at the same time ([Handbook][HB]) [V]. At HackGT 12, Capital One said "Judging will be based on the project's creativity, complexity, and completeness" ([HackGT 12][HGT]) [V].

**One key difference at MHacks.** Elsewhere Capital One says Nessie is *optional*: "You can optionally take advantage of… Nessie" (DivHacks 2026, Bitcamp 2026, TAMUhack 2026). HackTX 2025 says "usage of this API is completely optional" ([DivHacks 2026][DV26], [Bitcamp 2026][BC26], [TAMUhack 2026][TH26], [HackTX 2025][HTX]) [V]. The MHacks brief asks for projects that "leverage" Nessie and "creatively integrate Nessie's endpoints" ([Tracks & Prizes][TP]) [V]. **At MHacks, Nessie use is the core criterion, not an extra** [I].

### Capital One winners I verified (2025–26 season)
| Event | Winner | What it is | Nessie use |
|---|---|---|---|
| VTHacks 14 (Sept 2026), "Best Use of Nessie" | [LoadCheck][LC] | True profit per load for owner-operator truckers, with cash-shortfall prevention | **Reads** balance, bills and 90 days of purchases. **Writes** an advance deposit and its repayment bill. The team added a Capital One badge in four places in the UI because judges "only saw" the integration in body text ([PR #34][PR34]) |
| DivHacks 2026, "Best Use of Nessie" | [unsaid][UN] | An iMessage agent that negotiates group plans (budget, diet, commute) with friends' agents, so "nobody finds out whose budget set the ceiling" | **Light:** pulls "what you usually spend" from Nessie to propose a budget. Built with Photon, Grok, Cursor |
| DivHacks 2026 | [RentEscrow][RE] | Escrow for disputed rent and verified repairs | Nessie sandbox plus the XRPL testnet |
| HackRice 16 | [Larp City][LARP] | A game that lets you "live your financial future": a financial life-sim | Lists "nessi". Also uses ElevenLabs, Pixi.js |
| TAMUhack 2026 | [Drift][DR] | Monte Carlo goal planner | "producing customer profiles using Capital One's API, Nessie" |
| Bitcamp 2026 | [cryptX][CX] | Hardware Solana ledger (Arduino) with fraud detection | None (Nessie was optional) |
| HackGT 12 (2025) | [HR Audit][HRA] | Multi-agent fraud detection plus voice banking by phone (Twilio) | "voice banking system, powered by Twilio and the Capital One Nessie API" |
| HackGT 12 | [I'd Rather Scroll][IRS] | Turns study notes into "reels" | None. Judging can be loose |
| HackHarvard 2025 | [C2Pay][C2] | Adaptive MFA for risky payments (C2PA, TEE) | None |
| Technica 2025 | [Personal Cart Roaster][PCR] | A Chrome extension that roasts your impulse buy out loud (ElevenLabs) | None |
| Technica 2025 | [Resale Radar][RR] | Pricing advice for resale sellers | None |
| MHacks 2023, "Best Financial Hack" | [ZenStock][ZS] | News-sentiment stock insights | Lists Nessie |

**Pattern [I]:**
1. **The user is specific, and the money is a means, not the product.** Examples: truckers, renters, friends planning a night out.
2. **There is an agent, voice or simulation layer on top of the money data.** Examples: unsaid, HR Audit, Larp City, Drift.
3. **Nessie is visible and used in both directions** (LoadCheck).
4. **Plain budgeting apps don't win, even though they dominate the field.** At VTHacks 14, "Safe to Spend", "Orbit", "Money Map", "Hokie Wallet" and "Floatline" all lost to LoadCheck ([VTHacks 14 Nessie entries][VTF]).
5. **Humor can win.** Personal Cart Roaster did. So Capital One is *not* strictly a no-joke track, although Nessie must now be load-bearing.

---

## 3. Prize value and expected competition

### Prize value (team of 4) [V]
| Place | Listed | Cash-equivalent |
|---|---|---|
| 1st | $300 Giftogram × 4 + swag | **≈ $1,200** (Giftogram lets you pick from 140k+ brands ([GG])) |
| 2nd | $75 × 4 + swag | ≈ $300 |
| 3rd | $25 × 4 + swag | ≈ $100 |
| Side: Smash event | $150 gift card + swag package | ≈ $150 (a game event, not a hack; unrelated to the project) |

Per member, MHacks's $300 matches TAMUhack/Bitcamp ($300) and beats DivHacks 2026, VTHacks 14 and HackRice 16 ($250, a single winner) ([TH26], [BC26], [DV26], [VT14], [HR16]) [V]. **MHacks is the only event I found that pays three places** [V across the events checked].

### Competition: what the data says (my Devpost recounts of unique projects per prize filter) [V]
| Event | Capital One prize name | Opt-ins / total | % |
|---|---|---|---|
| VTHacks 14 (Sept 2026) | **Best Use of Nessie** | 21 / 176 | 11.9% |
| DivHacks 2026 | **The Best Use of Nessie** | 8 / 65 | 12.3% |
| HackGT 12 | Best Financial Hack | 34 / 276 | 12.3% |
| HackHarvard 2025 | Best Financial Hack | 20 / 160 | 12.5% |
| HackUTD 2025 | Capital One | 48 / 366 | 13.1% |
| WEHack 2026 | Capital One Challenge | 14 / 95 | 14.7% |
| Bitcamp 2026 | Best Financial Hack | 35 / 222 | 15.8% |
| Technica 2025 | Best Financial Hack | 25 / 127 | 19.7% |
| TAMUhack 2026 | Capital One Challenge | 34 / 171 | 19.9% |
| HackRice 16 | Best Financial Hack (event also had a Finance track) | 26 / 119 | 21.8% |
| HackTX 2025 | Best Capital One Hack | 51 / 225 | 22.7% |
| SwampHacks XI | Best Finance Hack | 28 / 112 | 25.0% |
| BostonHacks 2025 | Best Financial Hack subtrack | 13 / 52 | 25.0% |
| DivHacks 2025 | Best Financial Hack | 18 / 62 | 29.0% |

The median is **17.7%**. Both events that use the "Best Use of Nessie" name landed at about **12%** [V]. Filter links are in Sources.

### MHacks 2026 estimate: **medium** [I]
- **Expected entries: 12–30**, most likely about 20. That assumes 10–18% of roughly 120–180 submissions (MHacks 2025 had 122 ([verdict][VER])). The opt-in rate is pulled down by:
  - the Nessie-required wording,
  - 12 sponsor tracks plus 6 MLH prizes competing for attention ([Devpost][DP]).
  
  It is pulled up by:
  - a FinTech main track,
  - SpacetimeDB's and Relay's money prompts ([Tracks & Prizes][TP]).
- **Serious contenders: about 6–12.** At VTHacks 14, 3 of 21 Nessie entries had nothing to do with finance (ToolCab, TrueCost, Spare). About 10 were spend trackers or budgeting apps ([VTF]). At HackRice 16, about 10 of 26 were cash-flow or budgeting apps ([HRF]).
- **Theme gap:** none of the 55 Nessie entries at VTHacks 14, DivHacks 2026 and HackRice 16 was about energy, climate or sustainability, judging by taglines ([VTF], [DVF], [HRF]). **A Sustainability-framed Nessie project would stand alone in the Nessie pool** [I].

---

## 4. Expected value

All probabilities are my estimates [I]. They assume 3 places, about 6–12 serious entrants, and a capable team of 4 that makes Nessie load-bearing. Prizes for a team of 4: $1,200 / $300 / $100.

| Scenario | P(1st) | P(2nd) | P(3rd) | EV | Nessie hours | EV per hour |
|---|---|---|---|---|---|---|
| Bolt-on (read-only balance widget) | 4% | 6% | 8% | ≈ $75 | 1.5 | ≈ $50 |
| **Sketch A: Sustainability main, Nessie read + write** | **12%** | **13%** | **13%** | **≈ $200** | **4** | **≈ $50** |
| Sketch C: FinTech-native, differentiated, Nessie at the core | 18% | 15% | 13% | ≈ $275 | 4–5 | ≈ $60 |

**Compared with sibling advocates' published estimates** (in their files):
- Neon realistic ≈ $130 ([Neon][S05]).
- Photon ≈ $80 ([Photon][S06]).
- Notability ≈ $80 ([Notability][S03]).
- Figma ≈ $23 ([Figma][S09]).
- The Relay advocate put Nessie at ≈ $180 ([Relay][S11]).

The Fetch.ai and SpacetimeDB files weren't available when I wrote this. Their face values are higher ($1,250 and $1,000 cash for 1st) ([TP]).

**Reading [I]:** Nessie's EV is among the highest of the "use our API" tracks. Its payout is near-cash, not credits; compare Neon's AI Gateway credits and ElevenLabs' tiers. It has three podium spots, and the field fills up with clones. Only Fetch.ai and SpacetimeDB plausibly beat it on raw EV, and both are contested by the agent and real-time crowds.

---

## 5. Does Nessie imply FinTech main? Is FinTech + Nessie worth it?

**No, it does not imply FinTech main.**
- The rules make sponsor tracks independent of the main track ([HB]).
- Capital One's MHacks brief asks for projects that "improve their financial lives", not finance *products* ([TP]).
- Winners this season framed themselves as logistics (LoadCheck), social planning (unsaid), housing (RentEscrow) and a game (Larp City). DivHacks 2026's own tracks were city-themed ("Move Smarter", "Live Better", "Know Your City", "Hack the City"), and Nessie still awarded two prizes there ([DV26], [DVF]) [V].
- The one real constraint: the project must make a person's money better *through Nessie data or actions*. An energy-bills project does that.

**Is FinTech + Nessie worth the crowding? Not as stated. Here is a rough ledger [I]:**
| Effect of switching main track Sustainability → FinTech | Δ EV |
|---|---|
| Nessie: from Sketch A ($200) to Sketch C ($275) | **+ ≈ $75** |
| Main track: the pool grows from ~10–20% to ~15–25% of submissions ([verdict][VER]); P($2,500) drops ≈ 2–3 points | **− ≈ $50–75** |
| SpaceX "Make it Legendary": becomes incoherent with finance ([verdict][VER]) | − (keyboards plus the team's top preference) |
| SpacetimeDB / Relay "Money": easier fit (prediction market, portfolio sim, marketplace ([TP])) | + (but both can also fit Sustainability: SpacetimeDB lists "live dashboards", "shared simulations") |
| Idea saturation: ~40% of Nessie entries are budgeting apps ([VTF], [HRF]) | Risk: lands on FinTech too |

**Bottom line:** the Nessie gain from going FinTech roughly cancels the main-track loss, and it costs SpaceX. So **I agree with the judge: Sustainability main, and add Nessie to it.**
- FinTech + Nessie becomes right only if the team *independently* drops SpaceX **and** commits to the Capital One + SpacetimeDB + Relay stack with a non-budgeting idea (Sketch C).
- In that world Nessie is the anchor sponsor. It is the one prize whose judges and the FinTech main judges reward the same project.

---

## 6. Stacking

| Track | Fit with Nessie | Why |
|---|---|---|
| **Sustainability (main)** | **Good (Sketch A/B)** | Utility and gas bills plus fuel purchases are energy data. Nessie writes (a savings "green fund", transfers) turn advice into action |
| FinTech (main) | Native | Same judges' language. But see §5 |
| Actually Intelligent (main) | OK | An agent over Nessie data (unsaid, HR Audit pattern). Judges may read it as FinTech in disguise ([AI advocate][AI]) |
| Beyond the Code (main) | Weak–OK | cryptX (hardware) won Capital One at Bitcamp, but Nessie wasn't required there ([CX]) |
| **Judged by an LLM (fun)** | **Good** | Deterministic money math and a clear write-up score well with an LLM judge [I] |
| Dumbest Idea / Useless AI (fun) | Possible, off-mission | Personal Cart Roaster won Capital One with a joke ([PCR]). At MHacks, Nessie must be load-bearing. Fine as a free extra entry; don't build for it |
| **Relay** | **Good** | Relay suggests "💸 Money" ([TP]). Text or call your money/energy agent |
| **Photon** | Good | unsaid won Nessie with Photon iMessage ([UN]) |
| **Fetch.ai** | Good | "complete transactions" is in Fetch's brief ([TP]) |
| SpacetimeDB | Good in FinTech, OK in Sustainability | "trading / financial-style apps… portfolio sim, prediction market" ([TP]) |
| Neon | Good | Cache and enrich Nessie data in Postgres ([Neon][S05]) |
| ElevenLabs | Good | Voice banking (HR Audit), roasting (Cart Roaster) |
| Figma | Good | "Reimagine the banking experience" is a design brief ([Figma][S09]) |
| Notability | Neutral | Free to add |
| **SpaceX** | **Conditional** | Only through satellite Earth data. NASA POWER solar data comes from CERES satellites ([NASA POWER][NP]), and the verdict notes FIRMS is MODIS/VIIRS ([VER]). Whether SpaceX accepts Earth-observation data is **unverified**; ask at the SpaceXAI session (Sat 4 PM, VR Lab ([SCH1])). Also requires Cursor and Grok Imagine/Voice ([TP]). unsaid already combined Grok + Cursor with a Nessie win ([UN]) |
| FinchNode | Conflict | A different domain |
| FREE-WILi | Weak | A smart-meter reading could feed Sketch A, but that adds hardware risk |

---

## 7. Project sketches

### Sketch A (recommended): "Payback": your bank data, turned into a home-electrification plan that funds itself
**Main:** Sustainability. **Sponsors:** Nessie, Relay (or Photon), SpaceX *if* EO data counts, Neon optional, Figma. **Fun:** Judged by an LLM.

1. **Seed** a realistic student or young-family household in Nessie:
   - 90 days of DTE-style utility bills, gas-station purchases, a car loan, checking/savings.
   - Ann Arbor merchants with geocodes.
2. **Read** bills and purchases to compute the household's energy spend and an emissions estimate. Keep the math deterministic, the way LoadCheck did ([LC]).
3. **Space data:** pull NASA POWER's CERES-derived solar irradiance for the address ([NP]) to size rooftop solar. Compare a heat pump and an EV against the user's *actual* bills, and give a payback period in months.
4. **Act:** the user texts or calls the agent (Relay; Grok Voice if going for SpaceX) and says "do it". The agent **writes to Nessie**:
   - opens a "Green Fund" savings account,
   - schedules a recurring transfer sized so the upgrade is funded by the projected bill savings,
   - updates the bill's expected amount.
5. **Demo beat:** a live call. "Your gas bill and fuel purchases are $X a month. A heat pump pays back in N months. I've opened your Green Fund at $40 a month." Then refresh the Nessie-backed dashboard, with a "Powered by Capital One Nessie" badge on every Nessie-sourced figure (the LoadCheck lesson ([PR34])).

**Why it wins Nessie [I]:**
- It uses Nessie both ways.
- No other entry in the Nessie pool is about energy (§3).
- The user benefit is concrete.

**Why it fits Sustainability:** it rethinks household "energy… and resource systems", the track's own words ([TP]).

**Risk:** "carbon footprint from transactions" is a familiar idea. The writes and the payback math are what make this different.

### Sketch B: "Ember Fund": a wildfire and heat shock buffer
**Main:** Sustainability (climate adaptation) or FinTech. **Sponsors:** Nessie, SpaceX (NASA FIRMS active-fire detections, satellite-derived ([VER])), Relay, Fetch.ai.

- Watch FIRMS detections near the user.
- When the risk rises, the agent calls the user and moves money from checking into an evacuation buffer.
- It pauses non-essential bills (Nessie `PUT /bills/{id}`) and drafts a documented inventory of valuables.

This follows the winning pattern of **InsureFire/Embers** (LA Hacks 2025 FinTech) ([InsureFire][IF], via [verdict][VER]).

**Weakness:**
- It is a weaker Sustainability fit than A (it's adaptation, not "rethinking" systems).
- Branches and ATMs are DC-area only ([V]), so skip "nearest branch" features.

### Sketch C (only if SpaceX is dropped): "Pot": group money that negotiates itself
**Main:** FinTech. **Sponsors:** Nessie, SpacetimeDB (live shared pot and negotiation state), Relay or Photon, Fetch.ai.

- Each member's agent knows that member's Nessie spending baseline.
- The agents privately negotiate a group plan or shared purchase.
- They settle through Nessie transfers. SpacetimeDB keeps everyone's view in sync in real time.

This is unsaid's proven Nessie-winning idea ([UN]), extended with real settlement and live state.

**Risk:** it is close to a recent winner, and FinTech means the team gives up SpaceX.

---

## 8. Red flags, rival counterarguments, rebuttals

| Counterargument | Strength | Rebuttal |
|---|---|---|
| "Nessie's data is thin and fake. Every team demos the same mock bank." | **Strong, true** [V] | Agreed: sandboxes start empty and ATMs are 13 Arlington rows. Seeding your own realistic household (1.25 h) *is* the differentiator. Most entrants show raw sandbox data |
| "Nessie drags you into FinTech, the crowded track." | Medium | Not required (§5). This season's winners were logistics, social, housing and a game. Sketch A stays in Sustainability |
| "It breaks the SpaceX stack." | **Strong for C, partial for A/B** | In A/B, SpaceX hinges on Earth-observation data counting as "real space data". That is unverified, so ask at 4 PM. If SpaceX says no, the team picks between SpaceX and Nessie; it doesn't lose both |
| "2nd and 3rd are tiny ($75/$25 per member)." | True | EV is driven by 1st place. Even so, 3 places beat the one or two winners at every peer event I checked (DivHacks 2026, HackGT 12 and Technica 2025 had 2) |
| "The API could fail mid-demo." | Medium | It was up with 0.12–0.7 s warm latency [V]. But `/enterprise/deposits` timed out, there are 1–2 s cold starts, and loose key handling could be "fixed" mid-weekend. Cache responses, keep a fixture fallback (LoadCheck did ([LC])), and never call `/enterprise` live |
| "Fetch.ai and SpacetimeDB pay real cash, 3–4× more." | Strong on face value | Those are contested by the large agent and real-time crowds. Nessie pays $1,200 near-cash with a medium field, and it stacks *with* both |
| "Sponsor judging is a lottery (I'd Rather Scroll won)." | Medium | It's true for 2025's optional-Nessie format. MHacks' wording makes Nessie use the axis, which rewards deliberate integration |
| "Your writes are visible to every other team via `/enterprise`." | Low (mock data) | Use fake names. Mention it in Q&A as a sign you understood the API's permission model |

---

## 9. Scorecard (1–10)

| Criterion | Score | Justification |
|---|---|---|
| Prize value | **7** | $1,200 near-cash for 1st (Giftogram), plus $300/$100 for 2nd/3rd. Below Fetch.ai/SpacetimeDB cash, above every credits or merch prize |
| Win probability | **6** | About 12–30 entrants, about 6–12 serious, three places. The field is full of budgeting clones, so a differentiated project has a real chance [I] |
| Integration ease | **7** | Plain REST with a query key, about 4 h for load-bearing use. Points lost for stale SDKs, an incomplete spec, empty sandboxes and DC-only geodata |
| Stacking potential | **6** | Native to FinTech, and works in Sustainability through bills. Good with Relay, Photon, Fetch.ai, Neon, Figma, Judged by an LLM. Conditional on SpaceX, conflicts with FinchNode |
| Demo impact | **5** | Mock bank numbers don't wow on their own. The agent call plus a live Nessie write supplies the impact (Sketch A) |
| Fit with team preferences | **6** | The team named Capital One, and Nessie doesn't force FinTech. It is in tension with SpaceX unless Earth-observation data is accepted |

---

## 10. Recommendation

1. **Enter Nessie on top of the judge's Sustainability + Judged by an LLM pick, using Sketch A.**
2. At the **11:30 AM Sponsor Expo**, ask Capital One:
   - Does a sustainability project with load-bearing Nessie qualify for "Best Use"?
   - Do they value writes (accounts and transfers) as much as reads?
3. At the **4 PM SpaceXAI session**, ask whether CERES or FIRMS satellite data counts as "real space data". If not, keep Nessie and Relay and drop SpaceX, or vice versa, depending on the team's preference.
4. **Do not switch to FinTech main for Nessie's sake.** Switch only under the judge's flip (no SpaceX, plus a Capital One + SpacetimeDB + Relay stack with a non-budgeting idea). Then Sketch C makes Nessie the anchor.
5. **Implementation:**
   - One teammate signs in with GitHub and gets the key.
   - Use HTTPS only.
   - Seed a realistic household with a script.
   - Read *and* write.
   - Badge every Nessie-sourced figure.
   - Cache everything and keep a fixture fallback.

---

## Sources
- MHacks 2026 Tracks & Prizes (Nessie text, prizes 1st/2nd/3rd, Smash event prize, SpacetimeDB/Relay/SpaceX/Fetch.ai texts): https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5 (block data via https://safe-banon-80d.notion.site/api/v3/loadCachedPageChunkV2)
- MHacks 2026 Hacker Handbook (hours, judging, rubric, sponsor-track rule): https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af
- MHacks 2026 schedule, Saturday: https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365 ; Sunday: https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=83169850
- MHacks 2026 Devpost (prize list, deadline): https://mhacks-2026.devpost.com/
- Nessie site: https://nessieisreal.com/ ; getting started (bundle): https://nessieisreal.com/assets/GettingStarted-6xGdEJuW.js ; SDK page (bundle): https://nessieisreal.com/assets/SDK-CN63sozN.js ; OpenAPI spec: https://nessieisreal.com/nessie-openapi-spec.yaml
- Nessie API (live probes): https://api.nessieisreal.com/atms , /branches , /customers , /merchants , /accounts/{id}/purchases , /accounts/{id}/transfers , /enterprise/accounts , /enterprise/customers , /enterprise/merchants , /enterprise/bills , /enterprise/transfers , /enterprise/deposits
- Nessie GitHub org repos: https://api.github.com/orgs/nessieisreal/repos?sort=pushed ; https://github.com/nessieisreal/nessie-javascript-sdk
- Giftogram: https://www.giftogram.com/
- NASA POWER data sources (CERES): https://power.larc.nasa.gov/docs/methodology/data/sources/
- LoadCheck: https://devpost.com/software/loadcheck ; PR #34: https://github.com/VTHACKATHON/VTHACKS/pull/34
- unsaid: https://devpost.com/software/unsaid-zm8w5v ; RentEscrow: https://devpost.com/software/rentescrow-nthfwb ; GlassLedger: https://devpost.com/software/glassledger-rzjmy0 ; Fit Check: https://devpost.com/software/adaptive-room-planner
- Larp City: https://devpost.com/software/temp-6yaocn ; Drift: https://devpost.com/software/pff ; cryptX: https://devpost.com/software/cryptx-zceo69
- HR Audit: https://devpost.com/software/the-hr-audit ; I'd Rather Scroll: https://devpost.com/software/i-d-rather-scroll ; C2Pay: https://devpost.com/software/c2pay
- Personal Cart Roaster: https://devpost.com/software/personal-cart-roaster ; Resale Radar: https://devpost.com/software/resale-radar ; ZenStock: https://devpost.com/software/zenstock ; InsureFire: https://devpost.com/software/insurefire
- Event pages: https://divhacks-2026.devpost.com/ , https://vthacks-14.devpost.com/ , https://hackrice-16.devpost.com/ , https://th26.devpost.com/ , https://bitcamp-2026.devpost.com/ , https://hackgt-12.devpost.com/ , https://hacktx2025.devpost.com/ , https://wehack2026.devpost.com/ , https://bostonhacks-2025.devpost.com/ , https://hackutd-2025.devpost.com/
- Opt-in filters (prize id) and totals (`/submissions/search`):
  - VTHacks 14: https://vthacks-14.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105779
  - DivHacks 2026: https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105134
  - HackRice 16: https://hackrice-16.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105613
  - Bitcamp 2026: https://bitcamp-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=100340
  - TAMUhack 2026: https://th26.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=95627
  - WEHack 2026: https://wehack2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=100263
  - SwampHacks XI: https://swamphacks-xi.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=95098
  - HackTX 2025: https://hacktx2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=91653
  - BostonHacks 2025: https://bostonhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=91248
  - DivHacks 2025: https://divhacks-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=91094
  - HackUTD 2025: https://hackutd-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=92982
  - HackGT 12: https://hackgt-12.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=90502
  - HackHarvard 2025: https://hackharvard-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=91184
  - Technica 2025: https://technica-2025.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=92626
- Team research files: /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md ; /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/02-main-actually-intelligent-ai.md ; sibling advocates /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/03-notability-trust-the-process.md , 05-neon-backend.md , 06-photon-imessage-agents.md , 09-figma-best-design.md , 11-relay-interactive-agents.md

[TP]: https://safe-banon-80d.notion.site/Tracks-Prizes-3ed24ca0c81b80579aeff03edfa88af5
[HB]: https://safe-banon-80d.notion.site/2026-Hacker-Handbook-3ca24ca0c81b80fb8adee2e26c8508af
[SCH1]: https://docs.google.com/spreadsheets/d/1xqlEyBnKWjYVSMndQPVHYGluyV9PajB5AZdA9BDa5_Q/edit?gid=473102365
[DP]: https://mhacks-2026.devpost.com/
[NR]: https://nessieisreal.com/
[GS]: https://nessieisreal.com/assets/GettingStarted-6xGdEJuW.js
[SDK]: https://nessieisreal.com/assets/SDK-CN63sozN.js
[SPEC]: https://nessieisreal.com/nessie-openapi-spec.yaml
[GHO]: https://api.github.com/orgs/nessieisreal/repos?sort=pushed
[GG]: https://www.giftogram.com/
[NP]: https://power.larc.nasa.gov/docs/methodology/data/sources/
[LC]: https://devpost.com/software/loadcheck
[PR34]: https://github.com/VTHACKATHON/VTHACKS/pull/34
[UN]: https://devpost.com/software/unsaid-zm8w5v
[RE]: https://devpost.com/software/rentescrow-nthfwb
[LARP]: https://devpost.com/software/temp-6yaocn
[DR]: https://devpost.com/software/pff
[CX]: https://devpost.com/software/cryptx-zceo69
[HRA]: https://devpost.com/software/the-hr-audit
[IRS]: https://devpost.com/software/i-d-rather-scroll
[C2]: https://devpost.com/software/c2pay
[PCR]: https://devpost.com/software/personal-cart-roaster
[RR]: https://devpost.com/software/resale-radar
[ZS]: https://devpost.com/software/zenstock
[IF]: https://devpost.com/software/insurefire
[HGT]: https://hackgt-12.devpost.com/
[DV26]: https://divhacks-2026.devpost.com/
[BC26]: https://bitcamp-2026.devpost.com/
[TH26]: https://th26.devpost.com/
[HTX]: https://hacktx2025.devpost.com/
[VT14]: https://vthacks-14.devpost.com/
[HR16]: https://hackrice-16.devpost.com/
[VTF]: https://vthacks-14.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105779
[DVF]: https://divhacks-2026.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105134
[HRF]: https://hackrice-16.devpost.com/submissions/search?prize_filter%5Bprizes%5D%5B%5D=105613
[VER]: /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/07-debate-and-verdict.md
[AI]: /Users/anvaytodkar/Code/mhacks/results/main-and-fun-tracks/02-main-actually-intelligent-ai.md
[S03]: /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/03-notability-trust-the-process.md
[S05]: /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/05-neon-backend.md
[S06]: /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/06-photon-imessage-agents.md
[S09]: /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/09-figma-best-design.md
[S11]: /Users/anvaytodkar/Code/mhacks/results/sponsor-tracks/11-relay-interactive-agents.md

# Submission checklist: Hidden Rent, MHacks 2026

**Devpost closes Oct 4, 12:15 PM EDT. Our target is 11:30 AM.** The long write-up (story, numbers, sources) is in [DEVPOST.md](DEVPOST.md). This page covers *which prizes to tick, what each one requires, and what to type where*. Tick a box when it is done.

Rule for every track: claim only what we can demo. Don't tick prizes we didn't integrate, because judges check.

---

## 0. Blockers (do these first)

- [ ] **Make the GitHub repo public** (we'll do this later, but **before 11:30**). Lead: GitHub → `anvayt/mhacks` → Settings → *Change visibility* → Public. ASI:One requires a public repo, and Devpost judges click the link. The git history was scanned for every key in `.env` and none of them appear, so it is safe to open. `.env` and the agent seed are git-ignored.
- [ ] **Demo video, 3–5 minutes** on YouTube (unlisted is fine), link in Devpost. **ASI:One requires it**, and Devpost judges watch it. Show the web report → iMessage → ASI:One chat. Script: [PITCH.md](PITCH.md).
- [ ] **Live URLs filled in below** (from the Fly/Vercel deploy, see `DEPLOY.md`). No localhost and no tunnel links anywhere in Devpost.
- [ ] **All 4 teammates added to the Devpost project** (each person accepts the invite).
- [ ] **ASI:One Submission Agent done by everyone** (section 2, ASI:One). The team stays *Incomplete* until every member joins.

| What | URL |
|---|---|
| Website (Vercel) | `TODO` |
| API (Fly) | `TODO` |
| iMessage onboarding / QR card | `TODO` (+ `/card` for the printable QR) |
| GitHub | https://github.com/anvayt/mhacks |
| Agentverse profile | https://agentverse.ai/agents/details/agent1qth4ez7uam253n3aeuq9c56pnruw0e99vznlx3pupvahcxd84pfsghrfyum/profile |
| Demo video | `TODO` |

---

## 1. Which prizes to tick

| Prize | Tick it? | Why |
|---|---|---|
| **Sustainability** (main track) | **YES, primary** | Predicts avoidable heating/cooling energy, cost and CO₂ per home. Our whole pitch. |
| FinTech (main track) | Only if Devpost lets us pick more than one main track | "Hidden rent" is a cost-of-living number, but Sustainability is the stronger fit. If the form allows one, pick Sustainability. |
| Actually Intelligent | Only if multiple main tracks are allowed (and after FinTech) | Real ML model plus two agents, but it isn't the main story. |
| **ASI:One Agent Challenge** (Fetch.ai) | **YES** | Registered agent with Chat Protocol and a full workflow in ASI:One. Needs the extra Submission Agent step. |
| **Agents in iMessage using Photon** | **YES** | Built on Photon Spectrum (`spectrum-ts`) and iMessage, with persistent context. |
| **Notability** | **YES, but only after someone actually uses Notability Pro** | Easy to qualify: real use plus 2 screenshots plus a note. Steps below. |
| Best Design (Figma) | Only if P3 has a real Figma file | Needs a link to the actual frames. |
| Judged by an LLM | Yes | Free entry. The write-up must be plain and honest, no hidden instructions to the judge. |
| MLH .Tech domain | Optional | Only if we register e.g. `hiddenrent.tech` *and* point it at Vercel before submitting (~15 min). |
| ElevenLabs (sponsor + MLH) | **No** | Voice was cut. Nothing in the shipped app uses it. |
| Make it Legendary (SpaceXAI) | **No** | Needs Grok **Imagine or Voice** plus space data. We use Grok *vision* on bill photos, and the satellite stretch was a NO-GO. |
| Gemini (MLH) | No | Bill photos use xAI, not Gemini. |
| Neon / Spacetime / Tiger Data | No | Our storage is SQLite. |
| Capital One Nessie, Solana, FinchNode, FREE-WILi, Relay, Presage | No | Not integrated. |
| Beyond the Code (hardware), Useless AI, Dumbest Idea | No | Wrong category. |

---

## 2. Per-track requirements and what to write

### Sustainability (main)

- [ ] Paste the *Adherence to Theme* paragraph from DEVPOST.md. Impact metric: **verified, weather-normalized CO₂ avoided at the same home**. Picking an efficient home doesn't count as a reduction, and we say so.
- [ ] Demo shows the grade, $/yr, CO₂, and a priced improvement marked *projected if completed*.
- [ ] Have numbers ready: Church St **$265/yr** vs S Forest **$2,179/yr** (same building type); model error **29.2%** on real meters (`model/results/SIGNOFF.md`).

### ASI:One Agent Challenge (Fetch.ai)

Requirements from the [hackpack](https://www.fetch.ai/events/hackathons/mhacks-2026/hackpack), with our status:

- [x] At least one agent registered on Agentverse: **Hidden Rent** (`hidden-rent-mhacks`), `agent1qth4ez7uam253n3aeuq9c56pnruw0e99vznlx3pupvahcxd84pfsghrfyum`
- [x] Implements the Agent Chat Protocol (manifest published)
- [x] Meaningful tool execution: calls our API → ML model for grade/cost/CO₂, lists priced improvements, and runs the fast-forward savings simulation
- [x] README has the agent name and address, plus both required badges (`innovationlab`, `hackathon`), in the repo README and `asi-agent/README.md`
- [ ] **Agent running on Fly** (not a laptop). Then **stop the local `asi-agent` on the laptop** so only one copy uses the identity.
- [ ] **Discoverable in ASI:One**: search "Hidden Rent" in ASI:One, or open the Agentverse profile → *Chat with Agent*
- [ ] **Full workflow inside one ASI:One chat** against the deployed API: `1514 Morton Ave, Ann Arbor, MI` → answer questions → `options` → `try 1` → `ff 30`. Then **share the chat and save the shared-chat URL** (bonus field).
- [ ] Public GitHub repo (blocker 0)
- [ ] Demo video, 3–5 min (blocker 0). Make sure the ASI:One chat is in it.
- [ ] **Submission Agent** ([sign up](https://asi1.ai/auth/signup?returnTo=%2Ffestival%2Fmhacks2026%2Fdashboard%3Futm_source%3Dmhacks2026)):
  1. **Lead** messages the MHacks Submission Agent → *Create team (I'm the lead)*
  2. Fill in: project name **Hidden Rent**; lead name + email; team size **4**; problem statement (below); GitHub URL; table number; video URL; **Agentverse profile URL** (table above); **ASI:One shared chat URL**; agents built **1**
  3. Confirm, then post the **Team ID** in the group chat
  4. **Each teammate** chats with the Submission Agent → *Join with Team ID* → enters their details. Status must read **Submitted**, not Incomplete.
- [ ] In Devpost, paste the *Fetch.ai ASI:One* section of DEVPOST.md, **after fixing its stale lines** (section 4).

Problem statement to paste:
> Ann Arbor renters can compare rent but not the heating and cooling bill that comes with a home. Hidden Rent predicts a specific home's yearly heating/cooling cost, A–F grade and CO₂ from public building, weather and meter data, then turns it into questions for the landlord and a savings plan, in ASI:One, iMessage or on the web.

How they judge, and what to show: functionality 25% (it works live), Fetch tech 20% (Agentverse + Chat Protocol; we did **not** build the Payment Protocol, so don't claim it), innovation 20%, real-world impact 20%, UX/demo 15%.

### Agents in iMessage using Photon

- [x] Uses Photon **Spectrum** (`spectrum-ts` in `agent/package.json`) to connect the agent to iMessage. This is the hard requirement.
- [x] Persists context across conversations: saved home with answers and history, daily habit streak, and *Continue in iMessage* from the web report (carries the session ref).
- [ ] Agent running on Fly. Text it once after deploy to confirm a reply.
- [ ] **Photon Free allows only ~10 allowlisted numbers.** Either add the judges' numbers or demo from a team phone. Reprint the QR card from the onboarding `/card` URL.
- [ ] In Devpost, say "built on Photon Spectrum (`spectrum-ts`)" in plain words and link `agent/`. Include an iMessage screenshot.

### Notability (Trust the Process)

Rules: build with **Notability Pro at some point during the hackathon**, tag "Notability" in Built With, and add a short note on how we used it with **at least 2 screenshots**.

- [ ] Someone actually uses Notability Pro now, for real work we need anyway. Good options: pitch outline and judge Q&A prep, a hand-sketched grade-card wireframe, or a demo-flow diagram.
- [ ] Take **2+ screenshots** of those pages and add them to the Devpost gallery.
- [ ] Add **Notability** to Built With.
- [ ] Add a note to Devpost, edited to match what you actually did:
  > **How we used Notability Pro:** we used Notability Pro to plan our pitch and demo flow and to sketch the report-card layout before building it (screenshots in the gallery).

### Best Design (Figma), only if P3 confirms

- [ ] P3 pastes the Figma file link (view access: *anyone with the link*) into Devpost *Try it out*.
- [ ] Add 2–3 frame screenshots (grade card, range bar, compare view, map) next to the matching live-site screenshots.

### Judged by an LLM

- [ ] Nothing extra. Keep the write-up factual: no hidden text and no instructions to the judging model.

### .Tech domain (optional)

- [ ] Claim the free MLH .tech code → register `hiddenrent.tech` (or similar) → add it as a domain on the Vercel project → wait until it loads → put it in Devpost. Skip it if we're short on time.

---

## 3. Devpost form fields

- **Name:** Hidden Rent
- **Tagline:** See the heating and cooling costs behind a rental listing, then turn questions into a plan for a better home.
- **Story:** copy DEVPOST.md from *Inspiration* through *What's next*. **Leave out** the *Sponsor and integration audit* and *Submission fields and human TODOs* sections, remove every `TODO`, and replace any local or tunnel URL.
- **Built with:** Python, scikit-learn, XGBoost, LightGBM, pandas, FastAPI, SQLite, TypeScript, Next.js, React, MapLibre GL, Photon Spectrum, xAI Grok, Fetch.ai uAgents, Agentverse, ASI:One, Fly.io, Vercel. Add Notability and Figma **only if used**.
- **Try it out links:** website, GitHub, Agentverse profile, iMessage onboarding.
- **Video:** the 3–5 min link.
- **Gallery** (aim for 6+): grade/report card, compare view (Church vs Forest), city map, iMessage conversation, ASI:One conversation, plus 2 Notability screenshots (and Figma frames if used).
- **Prizes:** exactly the YES rows in section 1.
- **Table number:** `TODO`

---

## 4. Stale lines in DEVPOST.md to fix before pasting

- [ ] *What it does*: "handing an open web session over to iMessage is not built yet". **It's built** (*Continue in iMessage* on the report page). Rewrite the sentence.
- [ ] *Fetch.ai ASI:One* section: replace "local preview", "not yet complete" and the `make asi-agent` localhost run instructions with the live Agentverse/ASI:One flow, once the deployed rehearsal passes.
- [ ] *Submission fields and human TODOs*: replace the "temporary tunnel" / "Reprint the QR card after any tunnel restart" notes with the Fly onboarding URL.
- [ ] Any `TODO P1/P2/P3/P4` markers: resolve or delete.

## 5. Final 5-minute check before Submit

- [ ] Open every Devpost link in a private window: site loads, repo is public, video plays.
- [ ] Type a demo address on the live site and get a grade (Morton / Church / Forest).
- [ ] Text the iMessage agent and get a reply.
- [ ] Send one message to Hidden Rent in ASI:One and get a reply.
- [ ] ASI:One Submission Agent status reads **Submitted**.
- [ ] Hit **Submit** on Devpost (a draft doesn't count), then screenshot the confirmation.

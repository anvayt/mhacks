# Hidden Rent: presentation and Devpost strategy

**Status:** P4 strategy, Oct 4, 2026, ~7:45 AM. It informs `docs/PITCH.md` and `docs/DEVPOST.md`; it doesn't replace them. Items marked **❓** depend on something not yet confirmed (public URL, real-phone run, web animation, map polish, video). Check them before relying on a beat.

**Research base:**
- The team's own winner analyses (in git history at `1680192` and `e9ae429`):
  - `results/pivot-round2/01-mhacks-winner-anatomy.md`: all 18 MHacks top winners 2020–2025, plus every sustainability winner.
  - `results/pivot-round2/02-peer-sustainability-winners.md`: 20 peer winners and 351 entrants in sustainability pools.
  - `results/main-and-fun-tracks/06-fun-judged-by-an-llm.md`.
  - `results/SUMMARY.md` and `results/year-research/*`.
- Devpost's judges and video guides, and a judging-table write-up (§9).

---

## 1. What wins, in ten rules (and what each means for us)

| # | What the evidence says | Source | What we do |
|---|---|---|---|
| 1 | **Broad problem, specific demo.** Every MHacks top winner (2020–25) fixed something a judge has done this month, then demoed it with one user, one object, one number. The test: can a judge say "I have that" within 5 s and *see* the effect within 20 s? | Winner anatomy §1, §4, §8 | Open with rent (everyone's paid a winter bill) and show the $1,914 gap within 20 s |
| 2 | **A "watch it happen" moment, ideally one the judge takes part in.** FocusFlow (2024 runner-up): the page reacts to *your* gaze. SunLite (2021 1st): text a time, the bulb glows. Participatory demos draw judges. | Winner anatomy §2, §5.2 | The judge taps the answer and the grade locks; the judge picks the fix and the marker moves; ❓ the judge's phone buzzes |
| 3 | **One technical core you built, nameable in one sentence (an LLM call isn't a core).** V²/R won the 2024 Grand Prize with its own circuit solver and no LLM. | Winner anatomy §5.3 | "A heating and cooling model built on DOE simulations and checked against 101 Ann Arbor buildings' real meters, plus a question picker that asks what narrows your range most." Stress that **no LLM invents the numbers** |
| 4 | **One hard number on screen.** And: **no MHacks sustainability winner ever showed a measured impact.** That's an opening. | Winner anatomy §3, §5.4, §6.6 | Big numbers: **$1,914/yr gap**, **699 kg CO₂/yr** (windows), **101 buildings validated**, **25,704 buildings scored** |
| 5 | **A local hook makes a broad problem concrete** (V²/R's EECS 215 lab, FarmX's Michigan farms, F.L.U.D.D's SE Michigan floods). | Winner anatomy §5.5 | Ann Arbor's **Green Rental Housing** ordinance (in force Jan 6, 2026), real Ann Arbor addresses, U-M renters |
| 6 | **It must work live end to end; cut what doesn't, and say so.** BoundaryML's rubric listed "does it demo live" first; Sportable (3rd, 2020) won while saying its classifier was cut. | Winner anatomy §5.6 | Pre-stage every slow step; drop any beat not verified that morning; one honest line about limits |
| 7 | **Well-rounded beats spiky.** 2021 judges praised 1st and 3rd as "well-rounded"; Devpost judges say balance all criteria and avoid "extremely back-end heavy" projects with no UI. | Winner anatomy §5.7; Devpost judges | Each beat shows ≥2 criteria (§3); the UI carries the story |
| 8 | **Pairwise judging (MDredd, likely in 2026):** judges pick between two tables, and an empty table can count as a strike. | `year-research/2025.md`, SUMMARY | **Two people at the table at all times**; the problem must land instantly against the table next door |
| 9 | **Avoid saturated shapes.** Footprint calculators, eco-chatbots, recycling and food-waste apps went ~0 for 14 in MHacks' 2024–25 sustainability pools. The winning peer shape is **address in → personal decision out from public data** (Watt's Up, Chilladelphia, ZoneZero…). | Winner anatomy §6–7; peer winners TL;DR | Never call it a "calculator" or "chatbot". It's **"the energy bill a listing doesn't show, at the moment you decide where to live"** |
| 10 | **Storytelling and the write-up matter.** "Storytelling component is huge"; "ambiguity is a red flag". MHacks 16 winners' Devposts ran a median ~505 words vs ~379 for non-winners; 22 of 30 2024 winners had a video; an MLH judge favored a video filmed in real life. | Devpost judges; SUMMARY | A ~600–900 word Devpost with rubric headers and a measured-results table; a <3 min video with real phone footage |

**How Hidden Rent scores on the winner filter** (anatomy §8):
- **Pass:** I-have-that, a recurring problem (every monthly bill, and every apartment search), visible within 20 s, built core, measured number, resource system (home heating).
- **Not saturated:** home heating and cooling was absent from the 2024–25 pools.

That's 7 of 7 (frequency is monthly rather than weekly). By the anatomy file's account (§3, an inference), past MHacks sustainability winners were tangible but technically thin, with no measured impact. Those are the two gaps we fill.

---

## 2. Positioning

- **One-liner:** *Rent is on the listing. The energy bill isn't. Hidden Rent shows it before you sign, and shows which fix cuts the most carbon.*
- **The story:** Sam is choosing between two similar Ann Arbor apartments. One costs **$265** a year to heat and cool, the other **$2,179** (model estimates, heating + cooling only). Sam answers one question and the grade locks. Sam picks a fix and sees **699 kg CO₂** less a year, labelled "projected". Zoom out: **25,704** buildings scored.
- **The differentiator:** **uncertainty you can watch shrink.** A calculator gives one fake-precise number; we give an honest range that your answers lock. Honesty is the interaction, not a disclaimer.
- **The technical proof:** checked against **real meters of 101 Ann Arbor buildings** (median seasonal gas error 7.4% using a building's other years; 28.7% for the blended model on buildings it never saw). Put both on the panel; say "checked against real meters" aloud.
- **The sustainability proof:** CO₂ and dollars side by side; fixes ranked by CO₂ avoided per net dollar; tied to a real city ordinance; buildings are ~68% of Ann Arbor's emissions.
- **The quality bar** (PLAN.md §0, from Watt's Up, HackPrinceton F25 Best Overall): address → personal answer in seconds, own model, money + carbon in one view, home → city map, polished visual demo. **We match every element.**
- **Biggest risk:** live reliability (public URL ❓, real-phone Phase 2 ❓, no backup video yet) and **over-explaining caveats**. Spoken caveats make strong numbers sound weak. Put caveats in on-screen labels, Devpost and Q&A.

---

## 3. Demo beats scored (1–5; for Reliability, 5 = least likely to fail; for Time, 5 = cheapest)

| Beat | Innov | Tech | Usab | Theme | Interact | Spectacle | Memor | Reliab | Time | Value |
|---|---|---|---|---|---|---|---|---|---|---|
| **Battle reveal** ($265 vs $2,179) | 4 | 3 | 4 | 4 | 2 | 5 | 5 | 5 | 5 | ★★★★★ |
| **Judge locks the grade** (Arrowwood, "Central AC") ❓animation | 5 | 4 | 5 | 3 | 5 | 4 | 4 | 5 | 4 | ★★★★★ |
| **Judge picks a fix**, ghost marker (Morton: 699 kg, $125) | 4 | 4 | 4 | 5 | 4 | 4 | 4 | 4 | 4 | ★★★★½ |
| **City zoom-out** (25,704 scored) ❓polish | 3 | 4 | 3 | 5 | 2 | 5 | 4 | 4 | 5 | ★★★★ |
| **Judge's phone buzzes** ❓tunnel/slots | 5 | 4 | 5 | 3 | 5 | 4 | 5 | 2 | 2 | ★★★★ if it works, else cut |
| Team phone, judge answers by text ❓real-phone run | 4 | 4 | 5 | 3 | 4 | 3 | 4 | 3 | 3 | ★★★½ |
| Judge's own address ❓cold latency | 5 | 4 | 5 | 4 | 5 | 4 | 5 | 2 | 3 | ★★★½ (when warm) |
| "Checked against real meters" panel | 2 | 5 | 1 | 3 | 1 | 2 | 3 | 5 | 4 | ★★★ (one sentence) |
| Landlord email draft | 3 | 2 | 4 | 4 | 2 | 3 | 3 | 5 | 4 | ★★★ |
| Monthly bill check | 3 | 4 | 3 | 4 | 2 | **1** | 2 | 4 | 3 | ★★ → Q&A |
| Phase 2 accounts, reminders, Calendar | 4 | 4 | 3 | 4 | 2 | 1 | 2 | 3 | 2 | ★★ → Devpost |

**Change from the current `PITCH.md` draft:** drop the live bill beat ("66% below… inside the noise, not verified") from the 3-minute arc. It's honest but anticlimactic: the opposite of rule 2. Keep it for Q&A and Devpost.

---

## 4. Recommended 3-minute arc (modules; show → reaction → explain)

| Time | Module | What happens | Criteria shown | Look at |
|---|---|---|---|---|
| 0:00–0:20 | **A. Battle** | Already on screen. *"Two similar Ann Arbor apartments. One costs $265 a year to heat and cool, the other $2,179. The listing shows neither."* Pause. | Innovation, Theme, Usability | The gap |
| 0:20–0:50 | **B. You lock the grade** | *"You're the renter. One question."* The judge taps **Central AC**; A–B → **B 🔒**. *"Your answers shrink the range. We show what we don't know, then help you find out."* | Usability, Tech, Innovation | Grade badge |
| 0:50–1:05 | **C. Proof** | *"Built on 18,756 DOE-simulated Michigan homes, checked against 101 real Ann Arbor buildings' meters. No language model invents the numbers."* | Tech | Evidence panel |
| 1:05–1:35 | **D. You pick the fix** | Morton. *"Which would you ask your landlord for?"* The judge toggles windows → marker moves, **699 kg CO₂ and $125 a year, projected**, +4 Green Rental Housing points; landlord email ready. | Theme, Tech, Usability | Ghost marker |
| 1:35–1:55 | **E. Zoom out** | City map. *"25,704 Ann Arbor buildings scored. Buildings are about 68% of the city's emissions. Renters choosing with this pressures the leakiest ones."* | Theme, Tech (scale) | Map |
| 1:55–2:35 | **F. Phone** (best available) | **F1 ❓** the judge scans the QR, texts an address, their phone buzzes. **F2 ❓** team phone, the judge answers one question by text. **F3** a 10 s screenshot strip: *"same thing in iMessage, no app."* | Innovation, Usability | Phone held up |
| 2:35–2:55 | **G. It remembers you** | *"Next month it texts: still at this address? Send your bill, and we check it against the weather."* (Spoken only.) | Usability, Theme | — |
| 2:55–3:00 | **Close** | *"Know the hidden cost. Ask better questions. Fix what matters."* Point at the QR card. | — | Card |

**Adapting:**
- Engaged judge: replace A with **their address** if fresh lookups are fast ❓.
- Technical judge: C gets +15 s, cut G.
- Sustainability judge: D shows two fixes ranked by CO₂ per $, cut G.
- Shaky phone: F becomes F3 (10 s).

**Rules:**
- Read **live** numbers (Arrowwood has shown B/70 and B/73).
- Keep "predicted" and "projected if completed" as on-screen labels.
- Never say "92.6% accurate".
- One speaker per beat; hand-offs on the module boundaries.

## 5. 90-second fallback
Battle (20 s) → judge locks the grade (25 s) → judge picks a fix (25 s) → map + "checked against 101 real buildings' meters" (15 s) → close (5 s). **No Wi-Fi:** the backup video with the same five beats, labelled "Recorded demo" ❓.

---

## 6. The table (pairwise judging means the first 5 seconds matter)

- **Two people at the table at all times** from 12:30 to 3:00 (MDredd absences may count as strikes).
- **Big screen loops the battle** between judges: "$265 vs $2,179 a year: same kind of apartment." That's what stops people walking past.
- **A printed card:** "What's your apartment's hidden rent? Scan to check yours" plus the QR (❓ a working URL; otherwise drop the QR and keep the line).
- **One visual at a time.** Close every other tab; pre-load the battle, Arrowwood (at the question), Morton (saved home, at the toggle), the Yard map, and the phone thread.
- **Pre-stage everything slow** (Judging-table advice: mock slow calls, pre-fill forms). Run `make demo-warm` before 12:30; no typing during the pitch.
- **Energy:** "pitch with fire" (Devpost judges). Enthusiasm reads as conviction in a 3-minute window.

---

## 7. Devpost (written for human judges *and* the LLM judge)

**Format:** ~600–900 words (winners' median ~505; LLM judges favor thorough but penalize filler). Headers mirror the rubric so humans and the LLM can find each criterion. **Numbers, not adjectives.** No hidden or prompt-injection text (disqualification risk).

**Outline:**
1. **Tagline (one line):** "The energy bill a rental listing doesn't show."
2. **Inspiration (2–3 sentences):** Sam and the two apartments; Ann Arbor's Green Rental Housing law; buildings ≈ 68% of the city's emissions.
3. **What it does (bullets):** address or link → grade, $ range, CO₂; answers lock the grade; fixes ranked by CO₂ per $; city map; the same in iMessage; monthly bill check.
4. **Innovation:** honest uncertainty as the interaction; decision-time transparency nobody gives renters; web and iMessage on one backend; projected vs verified kept separate.
5. **Technical complexity:** the core in one paragraph (model, validation, question picker), then the architecture (link the README diagram), then the numbers.
6. **What we measured (table):**

   | Metric | Value | Basis |
   |---|---|---|
   | Seasonal gas error, metered path | 7.4% median | 101 Ann Arbor buildings, a building's other years |
   | Seasonal gas error, blended model on unseen buildings | 28.7% median | held-out buildings |
   | Buildings scored | 25,704 of 35,007 footprints | city layer |
   | Tests | API 616 passed (2 skipped), agent 70, browser smoke 444, Phase 2 check 16/16 | wave 7 verification |
   | Example result | $265 vs $2,179/yr; windows −699 kg CO₂ and −$125/yr (projected) | real addresses, `demo/DEMO_PICKS.md` |

7. **Usability:** three steps (paste, answer, choose); mobile-ready; iMessage with no app; accessibility notes (P3 to confirm what's true).
8. **Adherence to theme:** CO₂ next to $, Green Rental Housing points, city-scale targeting, never counting projected savings as achieved.
9. **Challenges and what we learned:** small rentals lack local meter data → we show ranges; bill checks are noisy → "early signal" vs "verified".
10. **Limitations (say them plainly):** heating + cooling only; predicted grades aren't official inspections; cooling less validated; some fixes unpriced.
11. **What's next:** landlord/city view, real-meter validation for small rentals.
12. **Built with**, plus links: GitHub (README with an architecture diagram at the top), the video, the live URL ❓.

**Track ticks:** Sustainability; Judged by an LLM; Photon (iMessage via Spectrum is load-bearing); Figma only if the designs exist. Tick only sponsors we really used.

## 8. Demo video (backup + Devpost)
- **Under 3 minutes; the elevator pitch in the first seconds; don't speed up the audio** (Devpost video guide).
- Same beats as §5, with a voiceover. Show **a real phone filmed in real life** receiving a reply (an MLH judge favored real-life footage).
- **Say the key numbers out loud** in case the LLM judge reads a transcript.
- Upload to YouTube, set visibility so judges can watch, link it on Devpost, and keep a local copy for no-Wi-Fi.

---

## 9. Sources
- Winner research (team, in git history): `results/pivot-round2/01-mhacks-winner-anatomy.md`, `02-peer-sustainability-winners.md` (commit `1680192`); `results/SUMMARY.md`, `results/year-research/2021–2025.md`, `results/main-and-fun-tracks/06-fun-judged-by-an-llm.md` (commit `e9ae429`). Underlying sources (Devpost galleries, MHacks rules, MDredd) are cited inside those files.
- [How to win a hackathon: advice from 5 seasoned judges](https://info.devpost.com/blog/hackathon-judging-tips) (Devpost)
- [6 tips for making a winning hackathon demo video](https://info.devpost.com/blog/6-tips-for-making-a-hackathon-demo-video) (Devpost)
- [Understanding hackathon submission and judging criteria](https://info.devpost.com/blog/understanding-hackathon-submission-and-judging-criteria) (Devpost)
- [How to win a hackathon: notes from the judging table](https://daily.dev/posts/how-to-win-a-hackathon-notes-from-the-judging-table-wttxezbgq) (daily.dev)
- Facts about Hidden Rent: `demo/DEMO_PICKS.md`, `docs/WAVE7_VERIFICATION.md`, `docs/PITCH.md`, `notes/integration.md`, `PLAN.md`.

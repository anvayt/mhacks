<!--
P4 public Devpost draft, Oct 4, 2026 (~8:15 AM). Paste everything between the two "PASTE" markers into Devpost.
Facts come from docs/DEVPOST.md (fact-checked evidence log), demo/DEMO_PICKS.md, docs/WAVE7_VERIFICATION.md and notes/*.md.
Structure follows docs/PRESENTATION_STRATEGY.md §7: rubric-visible, numbers not adjectives, honest limitations, no hidden text.
Before posting: fill every [TODO], drop media into each 🎞 slot, delete this comment and the "Recording checklist" at the end.
-->

<!-- ===== PASTE START ===== -->

# Hidden Rent

**Rent is on the listing. The energy bill isn't.**

Hidden Rent makes the hidden energy cost of renting visible, so renters can choose better homes, push for the fixes that cut the most carbon, and keep the habits that lower their bills.

## 🎬 Watch the 3-minute demo
[TODO: YouTube link]

**What you'll see:** 0:00 two similar apartments, $265 vs $2,179 a year · 0:20 one answer locks the grade · 0:50 how we know it works · 1:05 pick a fix and watch the projected score move · 1:35 every building in Ann Arbor · 1:55 the same thing in iMessage · 2:35 it remembers you: monthly check-ins and a daily habit streak.

---

## Inspiration

Renters compare rent, bedrooms and location, but not what a place costs to heat and cool, until the first winter bill. In Ann Arbor, most households rent and buildings are about two-thirds of the city's emissions. Since January 2026, the **Green Rental Housing** ordinance requires landlords to earn efficiency points. We wanted to give renters the information, and the leverage, to use it.

---

## What it does: feature by feature

### 1. 🏠 The Hidden Rent report
Paste an Ann Arbor address or a listing link. In seconds you get the home's predicted **heating and cooling cost** as a range, an **A–F grade**, its **CO₂**, and how it ranks against same-type homes across the city.

🎞 *[TODO: 5-second clip, address typed → report appears]*

**Try it:** `2322 Arrowwood Trl, Ann Arbor, MI`

### 2. 🔒 Lock in your grade
We don't pretend to know everything about your unit. The grade starts as a range, and Hidden Rent asks **only the questions that narrow it most** (heating fuel, windows, air conditioning). Answer one, and watch the range shrink until the grade locks.

🎞 *[TODO: clip, "Central AC" tapped → A–B becomes B 🔒]*

**Example:** 2322 Arrowwood Trl starts at **A–B**; answering "Central AC" locks it at **B**.

### 3. ⚔️ Listing battle
Two listings side by side, one clear winner. **624 Church St** is predicted at **$265 a year** to heat and cool; **1022 S Forest Ave** at **$2,179**. That's a **$1,914 a year** difference that neither listing shows.

🎞 *[TODO: clip, the two cards and the gap]*

### 4. 🔧 Fix it: see the impact before you commit
Hidden Rent suggests improvements ranked by **CO₂ avoided per dollar**. Pick one and a **projected** marker moves on your leaderboard bar. Your current grade stays put until real bills prove the change. One tap drafts an email to your landlord, with the Green Rental Housing points each fix earns.

🎞 *[TODO: clip, windows toggled → ghost marker moves; landlord email]*

**Example:** at 1514 Morton Ave (gas heat, single-pane windows), upgrading the windows is projected to save **699 kg of CO₂ and $125 a year**, worth **4 Green Rental Housing points**.

### 5. 🗺️ Every building in Ann Arbor
Zoom out from one home to the whole city: **25,704 buildings scored**, shaded by grade, with leaderboards. Only buildings in the city's public energy benchmarking are named; everything else is aggregated by area.

🎞 *[TODO: clip, map fly-out from one building to the city]*

### 6. 💬 Hidden Rent in iMessage: no app
Text an address to our agent (built on **Photon Spectrum**) and run the same interview by iMessage, with the same numbers. Start on the web and tap **"Continue in iMessage"**, and the conversation picks up your exact report.

🎞 *[TODO: real phone filmed in real life, text an address → grade arrives; answer a question]*

### 7. 📅 Monthly check-in: did your bill actually drop?
Hidden Rent remembers your home. Each month it asks if you still live there; if you've moved, your history is kept and you start a fresh baseline. Send your bill (photo or typed numbers) and we compare your gas use with **what the weather predicts**. A mild month doesn't count as a saving, and an uncertain result is labelled an early signal, not verified savings.

🎞 *[TODO: clip, typed bill → "X% vs normal for this weather"]*

### 8. 🔥 Daily habit streak
Pick a daily habit from your commitments. Reply **"done"** to a reminder (or text "done today") and your streak grows: **"Day 4 🔥, best 6. See you tomorrow."** Badges at 3 and 7 days, and an opt-in **habit-streak leaderboard** under an alias. Reminders are opt-in, at most one a day, "stop" works any time. Streaks are self-reported, so we never count them as carbon saved.

🎞 *[TODO: clip, reminder → "done" → Day N 🔥]*

### 9. 📤 Share card
Share your home's grade, rank and hidden cost as an image, with a QR code so friends can check theirs.

🎞 *[TODO: screenshot]*

---

## Why it matters

**Innovation.** Energy tools give one falsely precise number, after you've moved in. Hidden Rent works at the moment of decision, turns uncertainty into the interaction (your answers lock the grade), and closes the loop by checking real bills against the weather, keeping **current**, **projected** and **verified** separate.

**Technical complexity.** No language model invents our numbers. City footprints, census data, local weather and Michigan prices feed our own heating and cooling model, with paths for metered buildings, large unmetered buildings, and small buildings modeled from **18,756 DOE-simulated Michigan homes**. We checked it against **real meters at 101 Ann Arbor buildings**. One backend serves the web and the iMessage agent.

**Usability.** An address is enough; no account is needed for a grade. Plain questions, phone browser or iMessage, every assumption sourced, and states labelled in words, not just colors.

**Sustainability.** **CO₂ next to dollars** everywhere; fixes ranked by **carbon avoided per dollar** and tied to a city ordinance; a map of the leakiest buildings. Our impact metric is **verified, weather-normalized CO₂ avoided at the same home**. Moving or pledging never counts as savings.

---

## How we built it
- **Model (Python):** weather-normalized fits on Ann Arbor's public meter data; ResStock-based models for small buildings; PRISM and Open-Meteo weather; EIA Michigan prices; EPA and eGRID2023 carbon factors.
- **API (FastAPI + SQLite):** estimates, questions, sessions, accounts and saved homes, comparisons, the city layer, bills, commitments and projections, leaderboards, reminders and habit streaks.
- **Web (Next.js, React, MapLibre):** report, battle, leaderboard with a projected marker, city map, share card.
- **iMessage (TypeScript, Photon Spectrum):** the full conversation, including grade, answers, commitments, monthly check-ins, bills and streaks. It only repeats numbers the API returns.
- **Bill photos:** xAI Grok reads the bill; two reads must agree, and the API validates them before any comparison.

## What we measured
| | Result |
|---|---|
| Seasonal gas error vs real Ann Arbor meters (101 buildings) | **7.4%** median for buildings with their own meter history; **[TODO P1: 29.2%]** for our blended model on buildings it never saw |
| Buildings scored | **25,704** of 35,007 city footprints |
| Example: two similar apartments | **$265 vs $2,179 a year** (a $1,914 gap) |
| Example: one fix | **699 kg CO₂ and $125 a year** saved, projected |
| Automated checks | **633** API tests, **79** agent tests, **444** browser smoke checks, Phase 2 end-to-end check **16/16** |

## Challenges, accomplishments and what we learned
Address points miss buildings and garages inflate sizes, so we added matching and plausibility checks and ask for unit size when unsure. The hardest part was **honesty under uncertainty**: a range that shrinks, a projection that never pretends to be achieved, a bill result that says "early signal" when weather noise outweighs the change. We're proud that a renter can go from a listing to a locked grade, a ranked fix, a landlord email and a monthly bill check, on the web or entirely by iMessage, with every number traceable to data. We learned that uncertainty can be a feature, not a disclaimer.

## Limitations
- Covers **heating and cooling only**, not hot water, appliances or a full utility tariff; prices are Michigan averages.
- Real-meter validation is on larger buildings; small rentals are modeled from DOE simulations, so ranges are wider there.
- Grades are predictions, not official Green Rental Housing inspections.
- Bill checks are gas-only and often within the model's noise today, so we label them early signals; verified reductions need more months of evidence.
- Some fixes don't have a modeled effect yet and appear as tips without numbers.

## What's next
Collect consenting renters' bills across a full winter to measure real reductions, add modeled effects for more fixes, and offer landlords and the city a view of which buildings to fix first.

## Built with
Python · scikit-learn · XGBoost · pandas · FastAPI · SQLite · TypeScript · Next.js · React · MapLibre GL · Photon Spectrum · xAI Grok · NREL ResStock · City of Ann Arbor GIS and benchmarking data · U.S. Census · PRISM · Open-Meteo · EIA · EPA eGRID

**Try it:** [TODO: public URL, only if it works] · **Code:** https://github.com/anvayt/mhacks

<!-- ===== PASTE END ===== -->

---

## Recording checklist (internal; delete before posting)

**Overall video (under 3:00).** Pitch in the first seconds, voiceover, don't speed up audio, say the key numbers aloud, and film the phone in real life (`PRESENTATION_STRATEGY.md` §8).

| Clip | Feature | Shot | Length | Source to use |
|---|---|---|---|---|
| 1 | Report | Type `2322 Arrowwood Trl` → report | 5 s | live web |
| 2 | Lock grade | Tap "Central AC" → B 🔒 | 5 s | live web |
| 3 | Battle | Church vs Forest cards, hold on the gap | 5 s | live `/compare` (read the live numbers) |
| 4 | Fix it | Morton saved home, toggle windows, ghost marker, landlord email | 8 s | live board |
| 5 | Map | Fly out from The Yard to the city | 5 s | live `/map` |
| 6 | iMessage | Real phone: text address → grade; answer one question | 10 s | phone filmed in real life |
| 7 | Monthly | Typed bill → weather comparison | 6 s | live (say "hypothetical bill") |
| 8 | Habit streak | Reminder → "done" → "Day N 🔥" | 6 s | phone or terminal |
| 9 | Share card | Screenshot | — | live web |

**Before posting, confirm:**
- [ ] P1 approves the blended-model figure (**29.2%** per `model/results/SIGNOFF.md`; older docs say 28.7%)
- [ ] Re-run checks on the commit we demo; update the test counts in "What we measured" (633/79 are from the habit-streak branch notes; 444 smoke is from `97aec36`)
- [ ] Read live battle numbers and Forest's range on the day
- [ ] The web header shows the habit streak (`883fb07`); the "Continue in iMessage" handoff works on a real phone (`5bc5ee3`)
- [ ] A real bill photo has worked before we show the photo path; otherwise show typed numbers
- [ ] Public URL works before adding it; QR card reprinted after any tunnel restart
- [ ] Tracks: Sustainability, Judged by an LLM, Photon. Figma only with a real file
- [ ] Team names and roles added

<!--
Devpost draft, Oct 4, 2026: the team's story version merged with the fact-checked P4 draft. Sections follow Devpost's
fields in order; paste each into its box. Facts come from docs/DEVPOST.md, demo/DEMO_PICKS.md, model/README.md, the code.
Corrected from the story version: sign-in is a texted code (OAuth is only the optional Google Calendar reminders);
reminders are opt-in and at most one a day; the monthly check is the gas bill; Grok is voice + Imagine + bill photos.
Before posting: fill every [TODO], drop media into each 🎞 slot, delete this comment and the checklist at the end.
-->

<!-- ===== PASTE START ===== -->

# Hidden Rent

**Rent is on the listing. The energy bill isn't.**

Hidden Rent makes the hidden energy cost of renting visible, so renters can choose better homes, push for the fixes that cut the most carbon, and turn lower bills into a habit.

## 🎬 Watch the 3-minute demo
[TODO: YouTube link]

---

## Inspiration

I used to leave my heater on all day by accident: I'd leave my apartment at 7 AM, get back at 1 AM, and watch my DTE bill climb month after month without knowing why. Living in an older building showed me how much heat simply leaks out. Heating is the biggest hidden cost of renting, and nobody sees it until the first winter bill arrives. We built Hidden Rent so students like me can make saving on it a subconscious habit instead of an occasional good intention.

It matters beyond one apartment. In Ann Arbor, **54.5% of households rent** and **buildings make up about 68% of the city's emissions**. Since January 2026, the city's **Green Rental Housing** ordinance requires landlords to earn efficiency points. We wanted renters to have the information, and the leverage, to use it.

We also wanted the app to have character. The bold, editorial design is inspired by sites like [mhacks.org](https://www.mhacks.org) and [nousresearch.com](https://nousresearch.com): a cut-out collage look in black, white, red and blue, a homepage where you tap a house to start, and a grade screen whose red/blue split moves with your score.

---

## What it does

**1. 🏠 Your Hidden Rent score.** Paste an Ann Arbor address or a listing link. A short questionnaire asks **only the questions that narrow the estimate most** (heating fuel, windows, air conditioning), then reveals the home's predicted **heating and cooling cost**, its **CO₂**, and an **A–F grade** that ranks it against **same-type homes across the city**. *Example: 2322 Arrowwood Trl starts at A–B; answering "Central AC" locks it at B.*

🎞 *[TODO: clip, address → questions → grade]*

**2. ⚔️ Listing battle.** Two listings side by side. **624 Church St** is predicted at **$265 a year** to heat and cool; **1022 S Forest Ave** at **$2,179**: a **$1,914 a year** gap neither listing shows.

**3. 🔧 Pledge commitments and see the impact first.** Sign in with your phone (Hidden Rent texts you a code through **Photon**) and pledge one-time fixes or repeated habits. Each one shows how much it would change your **energy use, bill, CO₂ and score** before you commit. Fixes are ranked by **CO₂ avoided per dollar**, and one tap drafts an email to your landlord with the Green Rental Housing points each fix earns. *Example: at 1514 Morton Ave, upgrading the windows is projected to save **699 kg of CO₂ and $125 a year**, worth **4 Green Rental Housing points**.*

🎞 *[TODO: clip, pick a fix → projected score moves]*

**4. 💬 An AI agent in iMessage keeps you on track.** Our agent, built on **Photon Spectrum**, texts you reminders for what you pledged. If you committed to turning the heat down before you leave in the morning, it checks in and you reply "done". Your **daily habit streak** grows ("Day 4 🔥, best 6"), and you can climb an opt-in streak leaderboard under an alias. Reminders are opt-in, at most one a day, and "stop" works any time. The whole report also works by text: send an address and get the same numbers, with no app.

🎞 *[TODO: real phone filmed in real life, reminder → "done" → Day N 🔥]*

**5. 📅 Monthly check-in: did your bill actually go down, and stay down?** Each month the agent asks for your new gas bill (a photo or typed numbers) and compares your use with **what the weather predicts**, so a mild month doesn't count as a saving. If you've moved, your old home's history is kept and you start a fresh baseline. That's the game: **how consistently can you answer the texts so your energy use not only goes down, but stays down, month after month?**

**6. 🎧 Watch your report.** Your report read aloud by **Grok Voice** over **Grok Imagine** clips of your building type. The script is built from our API's numbers, so Grok never invents a figure.

**7. 🗺️ Every building in Ann Arbor.** Zoom out to the whole city: **25,704 buildings scored**, shaded by grade, with leaderboards. Only buildings in the city's public energy benchmarking are named; everything else is grouped by area.

---

## How we built it

- **Web (Next.js, React, MapLibre):** questionnaire, grade reveal, listing battle, commitments with projected scores, leaderboards, city map. Every animation respects reduced-motion settings.
- **iMessage agent (TypeScript, Photon Spectrum):** texted sign-in codes, the full report by text, commitment reminders, monthly bill check-ins and habit streaks. It only repeats numbers our API returns.
- **API (FastAPI + SQLite):** estimates, sessions, accounts and saved homes, bills, commitments and projections, leaderboards, reminders.
- **Model (Python, scikit-learn, XGBoost):** our own heating and cooling model. Ann Arbor buildings with public meter data use weather-normalized fits on their own history. Smaller buildings use an **XGBoost model trained on 18,756 DOE-simulated Michigan homes** (NREL ResStock), calibrated to real Ann Arbor meters. Carbon uses EPA and eGRID2023 factors; prices are EIA Michigan averages.
- **Data:** [NREL ResStock](https://resstock.nrel.gov) · [City of Ann Arbor GIS: building footprints and energy benchmarking](https://a2maps.a2gov.org) · U.S. Census ACS · [PRISM](https://prism.oregonstate.edu) and [Open-Meteo](https://open-meteo.com) weather · [EIA](https://www.eia.gov) prices · EPA eGRID.
- **xAI Grok:** Grok Voice narration, Grok Imagine clips, and Grok vision to read bill photos (two reads must agree, and the API validates them before any comparison).

## What we measured
| | Result |
|---|---|
| Seasonal gas error vs real Ann Arbor meters (101 buildings) | **7.4%** median for buildings with their own meter history; **[TODO P1: 29.2%]** for our blended model on buildings it never saw |
| Buildings scored | **25,704** of 35,007 city footprints |
| Two similar apartments | **$265 vs $2,179 a year** (a $1,914 gap) |
| One fix | **699 kg CO₂ and $125 a year** saved, projected |

---

## Challenges we ran into

- We wanted **SpacetimeDB** to make the game more real-time, so you could see other renters checking in live. It would have meant a major rewrite of the existing architecture, so we left it out.
- **Messy city data:** address points miss buildings and garages inflate floor areas, so we added footprint matching and plausibility checks, and ask for the unit's size when we're unsure.
- **Honesty under uncertainty:** the grade starts as a range that shrinks as you answer; a projection never pretends to be achieved; a bill result says "early signal" when weather noise outweighs the change.

## Accomplishments that we're proud of

- **The UI design!** A distinct visual identity down to small details: the tap-the-house intro, fact slides with sourced numbers, and a grade screen whose red/blue split eases to your score.
- We used **Grok** to make reports feel alive: **Grok Voice** reads each report aloud and **Grok Imagine** generated the clips behind it.
- A renter can go from a listing to a grade, a ranked fix, a landlord email, daily reminders and a monthly bill check, on the web or entirely by iMessage, and **every number traces back to data**. No language model invents our numbers.

## What we learned

Uncertainty can be a feature, not a disclaimer: showing a range and letting your answers lock the grade earned more trust than a falsely precise number. We also learned that habits stick when the reminder comes to you. A text you answer in two seconds beats an app you have to remember to open.

## What's next for Hidden Rent

Collect consenting renters' bills across a full winter to measure real, weather-normalized reductions; model the effect of more fixes; bring in real-time check-ins (the SpacetimeDB idea); and give landlords and the city a view of which buildings to fix first.

## Limitations
- Heating and cooling only, not hot water, appliances or a full utility tariff; prices are Michigan averages.
- Grades are predictions, not official Green Rental Housing inspections.
- Bill checks are gas-only and often within the model's noise after one month, so we label them early signals.
- Streaks are self-reported, so we never count them as carbon saved.

## Built with
Python · scikit-learn · XGBoost · pandas · FastAPI · SQLite · TypeScript · Next.js · React · MapLibre GL · Photon Spectrum · xAI Grok (Voice, Imagine, vision) · Cursor · Vercel · Fly.io · NREL ResStock · City of Ann Arbor GIS and benchmarking data · U.S. Census · PRISM · Open-Meteo · EIA · EPA eGRID

**Try it:** https://hidden-rent-mhacks.vercel.app · **Code:** https://github.com/anvayt/mhacks

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

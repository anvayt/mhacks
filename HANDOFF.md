# MHacks 2026: Chat Handoff (Sat Oct 3, 2026, ~6 PM EDT)

A summary of a strategy and build session with Claude, written to paste into other chats as context. The full research is in `results/SUMMARY.md` and the folders it links. This file records what changed or was decided **after** that research.

## 1. Event facts (verified Sat afternoon)

- **Hacking:** Sat Oct 3, 12 PM → Sun Oct 4, 12 PM EDT. **Treat 12:00 PM Sunday as the hard deadline** (Devpost says 12:15).
- **Judging:** Sun 12:30–3:00 PM, Duderstadt **Basement**, 3-minute table pitches, judged repeatedly by different judges. MDredd pairwise judging may be used, where missed visits count as strikes.
- **Criteria** (equal weight): Innovation, Technical Complexity, Usability (includes accessibility), Adherence to Theme. Event theme: "Digital Garden."
- **Prizes:** Grand $5,000; each main track $2,500 (Sustainability, AI, FinTech, Beyond the Code); Fetch.ai $1,250/$750/$500; SpacetimeDB $1,000/$500/$200; Neon (AI Gateway credits); Photon $400/$200; Capital One Nessie gift cards; FREE-WILi kits; Relay (SF trip); SpaceXAI keyboards; Figma; Notability; ElevenLabs.
  - **MLH prizes the original research missed:** ElevenLabs (earbuds), .Tech Domain (mic + domain), Tiger Data (Stream Deck Mini), Gemini API (swag), Solana, Presage.
- **Devpost registrations:** 49 as of 2 PM Sat. MHacks 2025 ended at 380. Most people register late; check again around 9 PM. A small field would favor low-entry sponsor prizes.
- **Remaining schedule:**
  - SpaceXAI 4–5 PM is a recruiting talk ("Build Your Entire Internship Application Stack"), not a rules Q&A. Ask about "real space data" at the Grok Bot booth (Atrium) instead.
  - Photon 5–6 PM, Figma 5:30–6:30 PM, dinner 7–9 PM (The Grove).

## 2. Verdict on the original plan (`results/SUMMARY.md`)

- **The track picks are sound:** Sustainability; Judged by an LLM (+ Dumbest Idea if the joke feature ships); sponsors FREE-WILi, Fetch.ai, Relay, ElevenLabs, SpaceX. Keep them.
- **Weak spots found:**
  1. **The forecast ignored wind.** MISO wind is about the same size as solar (13.9 GW wind vs 15.6 GW solar at 1:55 PM Sat). Clean night hours come from wind, not sun.
  2. **A free, keyless, real-time MISO data source exists:** `https://public-api.misoenergy.org/api/FuelMix` (5-minute fuel mix, wind and solar listed separately). **Timestamps are EST (UTC−5), not EDT.** Skip negative `Imports`. Intensity computed from it was ~311 g/kWh at 1:55 PM Sat.
  3. **Relay calls:** the App Store build is still v1.1 (Sep 20), with no calls. Relay's Oct 2 changelog says a call fails with `422`, code `1005`, if the person's app can't take calls. Have a fallback ready (text + voice note).
  4. **The scope is too big** (5 sponsors, 2 fun tracks, Figma, 3 Fetch agents). In-person MHacks almost never gives one project two prizes. Cut to one Fetch agent; drop Notability; Figma only if someone is idle.
  5. **P2 and P4 are overloaded.** Have an end-to-end version working with fake data by about 7 PM, not just at midnight.
  6. **The "Team research files" list in SUMMARY.md** points to `/Users/anvaytodkar/...` paths that don't exist in this repo.
- **Weekend-only demo gap:** DTE's time-of-day rate is weekday-only, so the money angle won't show live on Sunday.

## 3. Data and time gotchas

- **GOES-19 file paths** use the UTC year and **day of year**: Sat = `2026/276`, Sun = `2026/277`. **The UTC day rolls over at 8 PM EDT Saturday.** Build paths from `datetime.now(timezone.utc)` with `%Y/%j/%H`. DSR files post about 17–20 minutes after each scan.
- **EIA-930** data is in UTC and runs about 9 hours behind. Use it for history and the backtest only.
- **Open-Meteo** (free, no key): forecasts of 100 m wind, sunlight and temperature. Request `timezone=UTC`.
- **Backtest window:** roughly Sep 19 – Oct 2 (days 262–275).

## 4. Tech stack (agreed)

- **Python** for the brain: FastAPI + an asyncio control loop, data ingest, forecast (xarray, pyproj, pvlib, numpy, XGBoost), scheduler, SQLite, FREE-WILi driver (OneWili or legacy `freewili`), Fetch `uagents`.
- **TypeScript (Node 22)** for Fern on Relay (`@relaymessenger/sdk`, ElevenLabs package, Grok) and for the dashboard (Vite or plain HTML + Chart.js).
- **SQL** (SQLite) for storage.
- **Optional, only after everything else works:** a C/C++ → WASM app on the FREE-WILi.
- **Rule:** only the Python brain touches data and hardware. Everything else calls its HTTP API (`/forecast`, `/plan`, `/actuate`, `/garden`, `/impact`, `/demo/clean-now`). Every data source has a fake mode (`USE_FAKE=1`) that reads saved real responses from `fixtures/`.
- **Cursor** for all coding (SpaceX requires it and scores usage).

## 5. Forecast model + scheduler design (the user owns these)

**Forecast**, built in versions that each work on their own:
- **v0:** hourly profile (median by local hour) + a live offset that fades over about 3 hours. This is the baseline.
- **v1:** add wind and solar terms from Open-Meteo, converted to megawatts.
- **ML version:** an XGBoost model that predicts all 24 hours ahead in one model, using hour of day, weekday, hours ahead, the current deviation from normal, a wind index, sunlight and temperature. Monotonic constraints so more sun or wind never predicts a dirtier grid. Falls back to scikit-learn's gradient boosting if XGBoost won't load.
- **GOES correction:** satellite sunlight ÷ forecast sunlight, applied to the next 0–3 hours.
- **Backtest:** last 7 days, trained only on earlier data. Report the forecast's error against v0, and grams saved compared with a fixed 6 PM start and with the best possible ("oracle") schedule.

**Scheduler:**
- 15-minute slots, everything in UTC.
- **Non-interruptible loads** (dryer): try every start time, keep the cheapest block that ends before the deadline.
- **Interruptible loads** (EV): take the cheapest slots and merge neighbors into segments.
- **Baseline** is "now" or a habit time. `g_saved = kWh × (baseline_avg − chosen_avg)`.
- **Re-planning:** compare the current plan re-scored on the new forecast; only move it if the new option is better by at least 5 g/kWh. A started plan is locked.
- **Verification:** re-score finished plans with logged measurements. Only verified grams grow the garden.

**Contracts:**
- Forecast in: `[{time ISO-Z, g_per_kwh}]`, every 15 min, no gaps.
- Plan out: `{plan_id, device, start, end, segments, predicted_g_per_kwh, default_start, default_g_per_kwh, g_saved_vs_default, why}`.

**Code status** (on disk, **not committed**, untested):
- `cleanhours/models.py` and `cleanhours/scheduler.py`: schedule, window_average, should_replan, verify.
- `requirements.txt`; a local `.venv` (git-ignored).
- **Not yet written:** `ml_forecast.py`, `synthetic.py`, the tests.
- XGBoost on macOS needs `brew install libomp`.

**Ideas raised but not built:** cost-aware modes (greenest / cheapest / balanced, with a carbon-price weight); Google Calendar write, then free/busy read.

## 6. Strategy: why past MHacks winners won

The mechanisms behind past winners: (1) a visible moment in the first 10 seconds; (2) one hard thing the team built itself (trained policy, circuit solver, LSTM, NeRF); (3) a specific person + a number + a local hook; (4) choosing a thin pool and being the most tangible entry in it (Wattson won 2025 Sustainability out of 15 entries); (5) sponsor tech that's essential to the product; (6) honest scope. The Clean Hours gap: the forecaster's proof (backtest, sealed prediction) must be on screen, and the build must stay focused.

## 7. Demo design (interactive, planned ahead)

- **Props on the table:** a real fern under an IR-controlled LED grow light; the FREE-WILi showing an LED grid meter (by LED count, so it's colorblind-safe); a phone on a stand; prompt cards for the judge to pick from; a **sealed envelope** with Saturday night's prediction for Sunday afternoon plus the git commit hash; a QR code to a `cleanhours.tech` page.
- **Judge actions:** pick a card → Fern plans it, a calendar event appears, the phone rings, the judge says yes, **the light turns on** → open the envelope and compare prediction vs actual → turn a **"make it cloudy" what-if knob** (clearly labeled) to watch the clean window move.
- **Two branches:** if the grid is clean at judging time, "run it now"; if it's dirty, "wait until X" with the reason. Both are real behavior.
- **Two lengths:** 3 minutes and 30 seconds. Change the opening for each sponsor judge.
- **Every beat has a fallback** (hotspot, cached data, voice note instead of a call, a simulated device, a dashboard slider). A reset hotkey restores the starting state between judges.
- **Logistics:** check sound in the basement; hood the plant so the light is visible; power strip; two people at the table.
- **Timeline:** start logging real runs tonight; ~10 PM Sat commit the sealed prediction; 6 AM Sun freeze features; film the real-life demo video; rehearse 10+ times; set up the table by 12:15 PM.

## 8. Critiques raised and the responses

- **"It's only a marginal optimization."**
  - Shifting a dryer saves roughly 100–150 g per run.
  - **Average intensity can point the wrong way:** in MISO, coal is the dominant marginal fuel at night (Thind et al. 2017, ES&T).
  - **Fixes:** optimize for **surplus renewables and avoiding peaks** (real-time price, or LMP, plus wind/solar share), with average intensity only as a tiebreaker; target **big flexible loads** (EVs, heating/cooling); show **aggregation** (many homes acting as a virtual power plant).
- **"If it already exists, it's over."** Prior art:

  | Product | What it does | Overlaps with |
  |---|---|---|
  | Apple Clean Energy Charging | iPhones charge when the grid is cleaner | Shift |
  | Google Nest Renew "Energy Shift" | Thermostats shift heating/cooling, using WattTime | Thermal battery |
  | Sense | Tracks "always-on" home load | Cut |
  | Google, Windows Update, Green Software Foundation SDK, carbon-aware Kubernetes | Carbon-aware compute | Compute |

  Existing products don't automatically sink a hackathon project (NurseNotes, V²/R and Wattson all had commercial cousins); what sinks it is a judge naming the incumbent before you do. **Positioning:** *"Apple does this for iPhones and Google for Nest thermostats; nobody does it for renters and the ordinary appliances they own."* Add a Related work section to Devpost and say it in the pitch. Don't claim the forecast beats WattTime.

- **Correction:** idle/standby load is about **5–10%** of US household electricity (EIA estimate cited by Sense). The ~23% figure is from an NRDC study of California homes; use the conservative range.

## 9. Ideas evaluated

- **Rejected:**
  - **Carbon-aware compute:** big incumbents, and a 2024 MHacks MLH winner did data-center load shifting.
  - **Plug-and-play GPU energy tool:** U-M's own **Zeus** (NSDI '23, `pip install zeus-ml`, 15–76% energy reduction) does this; Macs can't demo it; it contradicts the "daily life" goal.
- **Pivot candidates considered:**
  - Thermal battery (pre-cool/pre-heat; ⚠️ Nest Renew)
  - Clean Commute
  - Leftovers (food rescue; loses SpaceX)
  - Smoke Shield (adaptation)
  - **Skip the Dryer** (satellite drying forecast that eliminates the load)
  - **Lights Out for Birds** (peak fall migration this week; uses Cornell's BirdCast; data access unverified)
  - **Rain Hours** (hold water use before heavy rain to reduce combined sewer overflows)
  - **Roommate Meter** (split the bill by measured per-person use)
  - **Swap at the Dining Hall** (menu-based food swaps; biggest per-action impact)
  - **Bill X-Ray** (utility data analysis that verifies savings)
  - Plus a long list in the chat.
- **Leading direction (decide by ~7 PM Sat): Clean Hours for renters, "Cut + Skip + Shift (+ Split)":**
  - **Cut** idle power: "I'm leaving" / Goodnight button, calendar away mode.
  - **Skip** the dryer when the satellite says laundry will air-dry.
  - **Shift** what remains to surplus clean power.
  - **Split** the bill between roommates by measured use (optional Capital One angle).
  - Needs power-monitoring smart plugs (e.g., TP-Link Kasa with `python-kasa`); buy them tonight.
- **Daily-life features agreed as valuable:** morning "carbon weather" text, calendar events, routines, everyday equivalents (from the EPA calculator, sourced), weekly receipt, accessible by design.

## 10. Open checks and next steps

- [ ] Team decision on direction by ~7 PM Sat.
- [ ] Quick checks:
  - BirdCast data access
  - Whether U-M dining menus are accessible programmatically and already carbon-labeled
  - US prior art for Skip the Dryer and Rain Hours
  - Any roommate bill-splitter that uses measured usage
  - MISO real-time price (LMP) endpoint
- [ ] Buy: power-monitoring smart plugs, a power strip, an IR LED strip, a small fern.
- [ ] Start the MISO 5-minute logger now.
- [ ] Finish `ml_forecast.py` + tests; save fixtures; commit the `cleanhours/` code.
- [ ] Register `cleanhours.tech` (MLH .Tech prize).
- [ ] Update `results/SUMMARY.md` with the fixes above (MISO endpoint, wind term, re-baselined gates).

## 11. Working preferences (from this chat)

- The user owns the **forecast model and scheduler**, and prefers **step-by-step walkthroughs** (outline the pipeline → how to code each piece → link it up later) over Claude writing code unasked.
- Wants the product to feel **built into daily life**, and is wary of **marginal impact** and **existing products**. Test every idea against both.
- Wants **honest critiques** and **current, sourced data**.

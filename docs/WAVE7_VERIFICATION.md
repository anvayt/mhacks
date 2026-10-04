# Wave 7 verification

Final integrated code: `de8ccdbe014dea2f421b5582c72bd9d3bb3e9e64` on `dev`. Run date: October 4, 2026. API **8060**, production web **3006**, P1's existing model **8001**. Tests used scratch session/account/calibration SQLite databases and `USE_MOCKS=1` for fictional phone onboarding. Model estimates were real; no real iMessages or Calendar events were sent. No model process was started, stopped, restarted or rebuilt.

## Results

| Check | Result |
|---|---|
| `cd api && uv run pytest -q` | **616 passed, 2 skipped**; opt-in live checks remain skipped. |
| `cd agent && npm test` | **70 passed**. |
| `cd agent && npm run typecheck` | Passed. |
| `cd web && npm ci && npm run build` | Passed; production build/start used for the browser run. Existing audit findings remain below. |
| `API_BASE_URL=http://localhost:8060 make phase2-check` | Final run **16/16**. |
| `scripts/web-smoke.sh all`, API 8060/web 3006, all five demo addresses | **433 passed, 0 warnings, 0 failures; 0 HTTP 429s; 37 guarded browser requests, peak 25/minute**. |
| First complete browser run, before the final harness repeat | 350 passing assertions, nine legacy warnings, zero failures; zero 429s. 37 guarded browser requests, peak 22/minute. Final repeat above supersedes this assertion count. |
| Agent key and browser isolation | Agent client sends a configured valid key on every API call; browser requests contain no `X-Agent-Key`. Only a nonempty matching key bypasses the guard. |
| Guard/launcher changes | `RATE_LIMIT_PER_MIN=120` default; suggestions/plain positions exempt; any `catalog_ids` position counted. Three-photo/ten-minute cap and streamed body cap unchanged. Production web build/start in the launcher. |
| Scripted real-API terminal conversation | Passed; exact transcript below. Stop followed by remind-now yields no reminder. |

Smoke checks use the reviewed harness (`5c57464` provenance plus integration adjustments). Oracle/setup API calls use the agent key loaded through `uv run --env-file /Users/anvaytodkar/Code/mhacks/.env`; that key is never injected into browser calls. The browser exercises its public budget. The first full run's warnings are recorded as warnings, not promoted into passes or omitted from the result.

The verified five addresses are 2322 Arrowwood Trl, 624 Church St, 1022 S Forest Ave, 615 S Main St and 1514 Morton Ave, all Ann Arbor. W2 consumes W1's returned estimate/session on moves without a second estimate; the solid current bar stays fixed while the what-if marker moves. Placeholder actions remain tips. Provisional bill results do not replace current grade.

## Merge and conflict resolutions

Branches merged: public-demo `b369a65`, W1 int-flow `5ffd90a`, reviewed W2 int-board `d1f3054`, reviewed W3 int-map-compare `17fd15f`, Phase 2 agent `d9a7442` and backup-video `4e3b134`. W2/W3's reviewed heads merged cleanly. Integration preserved all API routers, the identical browser API client and combined environment examples. The app-level custom-CSS declaration is kept; the duplicate map declaration is removed. The integration adds the every-request agent key fix and the configurable guard/production-launcher change.

## Known limitations after verification

- npm audit reports **MapLibre critical, Next.js moderate and PostCSS high** findings in the locked dependency tree. The map's address popup uses `setText`, not `setHTML`; this is not a blanket mitigation. No broad major-version upgrade was attempted at freeze. Patch/review before unrestricted production deployment.
- P1 look-alikes and unsupported effect inputs remain pending. Gas bill noise floors are broad (about 92–118% in documented runs), verified boards can be empty, and verified impact is gas-only. These checks are not proof of achieved renter savings.
- Meaningfully calibrated homes still lack projections from the updated baseline. Saved heat-included homes can have mismatched rank bases; W2 hides the inconsistent rank with an explanation. Calendar creation lacks durable cross-restart idempotency, and unknown reminder delivery fails closed for manual receipt recovery.
- The session-preserving web-to-iMessage link remains an open request. Public onboarding abuse cap, a working final tunnel URL, real-phone Phase 2, a genuine consenting bill-photo run, P1's artifact/results sign-off and a final playable video are not established here.

## Exact final terminal transcript

Source capture: `/tmp/wave7-agent-transcript-final.txt`. The gas/single-pane answers and February bill below are illustrative demo inputs for the real API/model, not verified facts or a genuine Morton meter submission. AC was skipped. `do 1` runs the projection as part of acceptance; `done 1` records only reported completion. The hypothetical February bill predates this commitment and cannot verify its impact.

```text
Hidden Rent: terminal (no texts sent); API http://localhost:8060
Type an address, or /quit. Terminal account uses a fictional phone unless AGENT_TERMINAL_PHONE is set.
You> 1514 Morton Ave, Ann Arbor, MI
Hidden Rent> 🏠 1514 MORTON AVE, ANN ARBOR, MI, 48104
Single-Family Detached, 2,753 sq ft, built around 1938 (neighborhood median)
Grade B–F: answer a few questions to lock it in · score 50/100 (predicted)
More efficient than 47% of Ann Arbor rentals
+$0/mo hidden rent vs a typical same-size unit
Heating + cooling a year: $1,198–$14,599, most likely $2,117
Winter $999 · Spring $478 · Summer $305 · Fall $336
CO₂: about 11.4 t a year
Typical error per season vs real Ann Arbor gas meters: at least 30%

Is the heat gas or electric, or included in your rent?
1) Gas  2) Electric  3) Heat is included in my rent
Reply with a number or the answer.
You> gas
Hidden Rent> Grade B–D: answer a few questions to lock it in · score 50/100 (predicted)
Heating + cooling a year: $1,198–$3,070, most likely $2,117 (was $1,198–$14,599)

What air conditioning does the unit have?
1) No AC  2) Window/room AC  3) Central AC  4) Heat pump
Reply with a number or the answer.
You> skip
Hidden Rent> Skipped.
Grade B–D: answer a few questions to lock it in · score 50/100 (predicted)
Heating + cooling a year: $1,198–$3,070, most likely $2,117

Are the windows single-, double- or triple-pane?
1) Single-pane  2) Double-pane  3) Triple-pane
Reply with a number or the answer.
You> single pane
Hidden Rent> Grade C 🔒 · score 45/100 (predicted)
Heating + cooling a year: $1,283–$3,070, most likely $2,185 (was $1,198–$3,070)

Grade locked in. Send another listing to compare, or after move-in text me a photo of your bill.
Hidden Rent> Your home and answers are saved. Say "options" for commitments.
You> save
Hidden Rent> Your home is saved. Say "options" for commitments.
You> options
Hidden Rent> Your options (effects are projected if completed):
1) Add storm windows or double-pane windows — landlord: $125/yr less, 699 kg CO₂/yr less, 4 GRH points.
2) Turn the heat down at night and when you're out — renter. Tip only; this model can't price its effect here.
Never set the heat below 64°F (18°C) while anyone is home, asleep included: the World Health Organization's health-based minimum indoor temperature for cold seasons (keep it warmer for babies, older adults and anyone unwell).
3) Send your landlord the drafted email: add storm windows or double-pane windows — renter→landlord. Tip only; this model can't price its effect here.
4) Seal drafts (renters: weatherstrip windows and doors) — landlord. Tip only; this model can't price its effect here.
5) Insulate the attic to R-50 — landlord. Tip only; this model can't price its effect here.
6) Insulate the walls — landlord. Tip only; this model can't price its effect here.
7) Switch to a cold-climate heat pump — landlord. Tip only; this model can't price its effect here.
Reply "do 1" or "do 1 and 3"; add "by YYYY-MM-DD" for a target date. Tips can be accepted but are excluded from the projection.
You> do 1
Hidden Rent> Accepted: Add storm windows or double-pane windows.
Projected if completed: grade C (current grade C), about $125/yr less and 699 kg CO₂/yr less. Your current grade hasn't changed.
When finished, say "done 1" using the option number. Optional: "reminders weekly" or "add to calendar" (Calendar needs a target date).
You> done 1
Hidden Rent> Reported complete: Add storm windows or double-pane windows. Your current grade is unchanged; bills can verify a reduction later.
You> checkin
Hidden Rent> Still at 1514 MORTON AVE, ANN ARBOR, MI, 48104? Reply yes or moved.
You> yes
Hidden Rent> Send this month’s bill photo, or type "120 therms", "120 ccf", or "$85" (estimated from your bill amount). Without dates I use the last full month; you can add start/end dates.
You> 120 therms 2026-02-01 to 2026-02-28
Hidden Rent> 📄 Your bill is within the normal range for this weather (-66% vs expected, inside our typical ±118% error).
🔥 1-month streak below normal
🏅 weather beater
This bill suggests grade A, but one bill is inside normal month-to-month variation, so your grade stays C. Early signal only.
This is not a verified reduction. Reported work needs a full later billing period beyond the model's error.

🔧 Top fixes:
1) ENERGY STAR low-e storm windows or windows: saves $125/yr, 699 kg CO₂/yr less, +4 GRH pts → grade C
2) Cold-climate heat pump (all-electric heat and cooling): costs $15,400 ($4,000 rebate), +35 GRH pts
3) Air sealing (blower-door tested): $500 rebate, +9 GRH pts
Green Rental Housing points: 0 → 61 (Ann Arbor requires 70)
I drafted an email to your landlord ↓

Subject: Energy upgrades for 1514 MORTON AVE, ANN ARBOR, MI, 48104

Hi,

I rent 1514 MORTON AVE, ANN ARBOR, MI, 48104. Hidden Rent (estimates from NREL ResStock and local weather) suggests these upgrades:

1. ENERGY STAR low-e storm windows or windows: about $125/yr less to heat and cool, 699 kg less CO2 a year; +4 Green Rental Housing points (Energy Efficient Windows)
2. Cold-climate heat pump (all-electric heat and cooling): +35 Green Rental Housing points (Electricity is the Primary Type of Energy Used for Space Heating (15) + Medium-Efficiency Cold-Climate Heat Pump with Electric Backup Heat (20)); rebate $4,000
3. Air sealing (blower-door tested): +9 Green Rental Housing points (Air Sealing); rebate $500

Ann Arbor's Green Rental Housing ordinance (in effect since Jan 6, 2026) asks rentals to reach 70 checklist points at inspection (110 after Jul 5, 2028). From what I know of the unit, it has 0 confirmed points; these fixes would bring it to 61.

Could we talk about scheduling them?

Thanks,
You> stop
Hidden Rent> Proactive reminders stopped. I'll still answer when you text me.
You> remind-now
Hidden Rent> No reminder is available. Reminders may be paused, stopped, or switched off.
You> /quit
```

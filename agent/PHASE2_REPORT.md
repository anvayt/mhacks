# P4 Phase 2 real-API handoff

Branch: `p4/phase2-real`, based on `origin/dev` wave 6 (`534f67a`). Changes are confined to `/agent`. No API, web or model code changed; no iMessage or real Calendar event was sent.

## Implemented

- Real API client with `X-Agent-Key` for account, property, bill, commitment, projection, reminder and Calendar calls.
- Normalized phone/email account resolution, shared concurrent cache, web ref adoption, exact six-digit web login and verbatim login errors; `/me` rehydration of current home and pending check-in.
- Saved answered sessions, separate move baselines/history, numbered commitments, reported completion, projected-if-completed wording, no effect numbers on tips, unchanged thermostat safety note.
- Monthly check-in, therms/ccf/dollar amounts, last full month by default, photos, provisional bill signals and separate verification. Unsaved replacement reports must be saved before a property bill can be recorded.
- One serialized five-minute iMessage reminder poller, server policy enforcement, durable delivery receipts and acknowledgement retry, stop/pause/resume, explicit checkin/remind-now CLI commands. Terminal mode never consumes queued texts as delivered.
- Calendar connection and dated accepted-commitment events; failures preserve commitments; per-process duplicate suppression.
- Matching, explicitly labeled mock endpoints; deterministic terminal mode; no new dependency.

## Files

`src/api.ts`, `accounts.ts`, `conversation.ts`, `phase2Replies.ts`, `replies.ts`, `agent.ts`, `transport.ts`, `reminders.ts`, `env.ts`, `mockApi.ts`, `mockPhase2.ts`, `onboard.ts`; `scripts/checkin.ts`; `package.json`, `.env.example`, `README.md`; `test/phase2.test.ts`, `aftermovein.test.ts`, `replies.test.ts`; this report.

## Validation

- `npm test`: **69 passed**. `npm run typecheck`: passed. `git diff --check`: passed.
- Tests cover every new intent, six-digit regex, normalized/numeric-email identity, ref and unit-size property isolation, restart rehydration, opt-in/stop/pause, provisional wording, tips, Calendar isolation/repeat suppression, all agent-key endpoints, root env precedence, comma/date/unit parsing, receipt durability/idempotent acknowledgement/recovery. Existing Phase 1 tests remain passing.
- Independent **real API** checks on port 8040: web login rejects five-digit intent without a confirm call; mixed-case six-digit login succeeds; web polling reaches verified with a token (never printed); bad-code message is repeated verbatim; all eight relevant requests carry the key. `USE_MOCKS=1` kept auth onboarding on the sms mock path. Separate real API checks confirm stop/pause survive inbound replies and restart, and ordinary replies still work after stop.
- Full **real API/model terminal conversation passed** after P1 restored its existing model server. Morton → gas → skip AC → single panes → grade lock → save → options → accept windows → projected result → reported done → check-in → hypothetical February bill → fixes/email → stop. No cached/seeded estimates were substituted. The agent did not start, stop or rebuild the model.
- Real current: **C, score 45**, annual **$2,185**, P10–P90 **$1,283–$3,070**; same-type rank **11,610/21,173**, city percentile **41.8%**. Window projection: **C, score 56**, **$125/year** and **699 kg CO₂/year** less; ghost rank **9,286**, city percentile **52.4%**. Current stays fixed.
- The **hypothetical** 120-therm bill for February 1–28, 2026 returned **66% below weather-normal**, noise floor **118.3%**, streak **1**, `verified: false`; its `bill_regrade` snapshot is **provisional A, score 94**, annual p50 **$1,283**. The current grade stays **C/45** and rank **11,610**; `/me.pending_checkin` becomes null. This past bill does not demonstrate post-commitment impact. Stop blocks `remind-now` while ordinary inbound replies continue.
- The first earlier live attempt correctly reported `503 model_unavailable` while port 8001 was offline. That availability blocker is now resolved.
- Isolated API: `SESSIONS_DB=/tmp/a16-s.sqlite`, `APP_DB=/tmp/a16-a.sqlite`, `CALIBRATE_DB=/tmp/a16-c.sqlite`, `USE_MOCKS=1`; a temporary launcher caps model concurrency at two. Credentials came from the canonical root `.env` using `uv run --env-file`, without printing them.

## Environment additions

- `AGENT_API_KEY`: match the API key; empty example placeholders fall through to root `.env`.
- `AGENT_TERMINAL_PHONE`: defaults to fictional `+12025550164`.
- `REMINDER_RECEIPTS`: optional; default git-ignored `../data/agent-reminder-receipts.json`, mode 600.

Existing `API_BASE_URL`, Photon credentials, `AGENT_TERMINAL`, `USE_MOCK_API`, and onboarding `USE_MOCKS` remain. Real API is the default.

## Full real-API terminal transcript

Captured against API 8040 and P1's restored server, with one inbound message at a time. The gas/single-pane interview answers and the 120-therm February bill are demonstration inputs, not verified facts or meter evidence for Morton. AC was skipped rather than invented. All numeric results below came from live API responses.

```text
> agent
> tsx src/agent.ts

Hidden Rent: terminal (no texts sent); API http://localhost:8040
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

## Full terminal flow with mock data

**Everything below is labeled demo data; its figures are not verified Morton measurements.** This separate mock run exercised the complete dialog before the real model was restored; the real transcript above supersedes it for live numeric evidence.

```text
> agent
> tsx src/agent.ts

Hidden Rent: terminal (no texts sent); API MOCK / demo data
Type an address, or /quit. Terminal account uses a fictional phone unless AGENT_TERMINAL_PHONE is set.
> You> 1514 Morton Ave, Ann Arbor, MI
Hidden Rent> [demo data, not a real estimate]
🏠 1514 Morton Ave, Ann Arbor, MI
Multi-Family with 2 - 4 Units, 850 sq ft (estimated), built 1962
Grade B–D: answer a few questions to lock it in · score 68/100 (predicted)
More efficient than 71% of Ann Arbor rentals
+$22/mo hidden rent vs a typical same-size unit
Heating + cooling a year: $760–$1,960, most likely $1,360
Winter $843 · Spring $163 · Summer $218 · Fall $136
CO₂: about 2.1 t a year

How big is the unit in sq ft? It's usually on the listing. (Or say skip.)
> You> 850
Hidden Rent> [demo data, not a real estimate]
🏠 1514 Morton Ave, Ann Arbor, MI
Multi-Family with 2 - 4 Units, 850 sq ft, built 1962
Grade B–D: answer a few questions to lock it in · score 68/100 (predicted)
More efficient than 71% of Ann Arbor rentals
+$22/mo hidden rent vs a typical same-size unit
Heating + cooling a year: $760–$1,960, most likely $1,360
Winter $843 · Spring $163 · Summer $218 · Fall $136
CO₂: about 2.1 t a year

Is the heat gas or electric, or included in your rent?
1) Gas  2) Electric  3) Heat is included in my rent
Reply with a number or the answer.
> You> gas
Hidden Rent> [demo data, not a real estimate]
Grade B–C: answer a few questions to lock it in · score 68/100 (predicted)
Heating + cooling a year: $980–$1,740, most likely $1,360 (was $760–$1,960)

Are the windows single-, double- or triple-pane?
1) Single-pane  2) Double-pane  3) Triple-pane
Reply with a number or the answer.
> You> single
Hidden Rent> [demo data, not a real estimate]
Grade B–C: answer a few questions to lock it in · score 68/100 (predicted)
Heating + cooling a year: $1,120–$1,600, most likely $1,360 (was $980–$1,740)

Is the unit on the ground floor, a middle floor or the top floor?
1) Ground floor  2) Middle floor  3) Top floor
Reply with a number or the answer.
> You> top
Hidden Rent> [demo data, not a real estimate]
Grade B 🔒 · score 68/100 (predicted)
Heating + cooling a year: $1,220–$1,500, most likely $1,360 (was $1,120–$1,600)

Grade locked in. Send another listing to compare, or after move-in text me a photo of your bill.
Hidden Rent> Your home and answers are saved. Say "options" for commitments.
> You> save
Hidden Rent> [demo data, not a real estimate]
Your home is saved. Say "options" for commitments.
> You> options
Hidden Rent> [demo data, not a real estimate]
Your options (effects are projected if completed):
1) Upgrade single-pane windows — landlord: $125/yr less, 699 kg CO₂/yr less, 4 GRH points.
2) Air sealing — landlord. Tip only; this model can't price its effect here.
3) Thermostat setback — renter. Tip only; this model can't price its effect here.
Never set below 64°F (WHO minimum for healthy adults); keep vulnerable people warmer.
Reply "do 1" or "do 1 and 3"; add "by YYYY-MM-DD" for a target date. Tips can be accepted but are excluded from the projection.
> You> do 1 by 2026-11-01
Hidden Rent> [demo data, not a real estimate]
Accepted: window upgrade (target 2026-11-01).
Projected if completed: grade B (current grade B), about $125/yr less and 699 kg CO₂/yr less. Your current grade hasn't changed.
When finished, say "done 1" using the option number. Optional: "reminders weekly" or "add to calendar" (Calendar needs a target date).
> You> add to calendar
Hidden Rent> [demo data, not a real estimate]
[mock Calendar — no Google event]
Connect Calendar: https://example.com/calendar-demo
After connecting, reply "calendar connected". Your commitments are already saved.
> You> calendar connected
Hidden Rent> [demo data, not a real estimate]
Mock Calendar reminder: window upgrade
> You> done 1
Hidden Rent> [demo data, not a real estimate]
Reported complete: window upgrade. Your current grade is unchanged; bills can verify a reduction later.
> You> checkin
Hidden Rent> [demo data, not a real estimate]
Still at 1514 Morton Ave, Ann Arbor, MI? Reply yes or moved.
> You> yes
Hidden Rent> [demo data, not a real estimate]
Send this month’s bill photo, or type "120 therms", "120 ccf", or "$85" (estimated from your bill amount). Without dates I use the last full month; you can add start/end dates.
> You> 120 therms
Hidden Rent> [demo data, not a real estimate]
📄 Your bill is within the normal range for this weather (-12% vs expected, inside our typical ±100% error).
🔥 1-month streak below normal
🏅 weather beater
This bill suggests grade A, but one bill is inside normal month-to-month variation, so your grade stays B. Early signal only.
This is not a verified reduction. Reported work needs a full later billing period beyond the model's error.

🔧 Top fixes:
1) Air sealing (blower-door tested): saves $160/yr, 410 kg CO₂/yr less, $500 rebate, +9 GRH pts → grade B
2) Cold-climate heat pump: costs $120/yr more to run, 900 kg CO₂/yr less, costs $15,400 ($4,000 rebate), +35 GRH pts → grade B
3) ENERGY STAR low-e storm windows: +4 GRH pts
Green Rental Housing points: 48 → 74 (Ann Arbor requires 70)
I drafted an email to your landlord ↓

Subject: Energy fixes for 1514 Morton Ave, Ann Arbor, MI

Hi,

I'm a tenant at 1514 Morton Ave, Ann Arbor, MI. Air sealing and attic insulation would cut heating costs and earn points toward Ann Arbor's Green Rental Housing requirement. DTE rebates cover part of the cost. Could we talk about scheduling them?

Thanks,
> You> stop
Hidden Rent> [demo data, not a real estimate]
Proactive reminders stopped. I'll still answer when you text me.
> You> remind-now
Hidden Rent> [demo data, not a real estimate]
Reminders are stopped or paused.
>
```

## Remaining work and API gaps

1. The requested real Morton conversation is now verified. The team lead/Bittermoss still owns real-phone delivery checks; this branch never starts Photon in terminal mode.
2. The API projects from the original session after a meaningful bill regrade. The agent saves commitments but withholds that stale projection.
3. The Calendar API lacks durable create idempotency and does not fill `Commitment.calendar_event_id`; per-process suppression prevents repeats, but after restart the operator must inspect Calendar before repeating creation.
4. The saved heat-included snapshot/ranking issue remains in P2. The agent presents the API's renter cooling-only bill and building explanation; it does not invent corrected rankings.
5. Reminder `sending` receipts after a crash fail closed for all proactive sends. Check whether delivery occurred, then mark that ID delivered for acknowledgement or remove it only if definitely unsent. This does not claim distributed exactly-once delivery. Run one sender process; manual non-demo CLI sends must not run alongside it.

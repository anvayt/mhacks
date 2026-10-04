# P2-FF: "⏩ Fast-forward" demo control (simulated days, savings adding up)

```yaml
id: P2-FF
title: Fast-forward simulation (API + board control + agent command)
owner: P2              # lead-assigned across /api, /web (board) and /agent
status: done           # dev 5410f1c
branch: p2/fast-forward
type: build
checkpoint: lead beta test
depends_on: [P2 habit streak (dev 883fb07), /projection what-if, /forecast history]
blocks: []
services_touched: [/api, /web (web/app/board/*, web/app/leaderboard.tsx), /agent]
services_read: [P1 /hc/estimate (via /projection's what-if), Open-Meteo 1991-2020 archive cache (forecast.py)]
contract_change: additive   # POST /simulate/fast-forward; /projection delta gains a heating/cooling split
```

## Goal
A demo control that shows what keeping your commitments adds up to over 1 day, 1 week, 1 month (and up to 365 days)
— clearly a **simulation**, never real usage. It reuses the board's own look; nothing it shows is ever stored.

## Honesty rules (PLAN §0, NEW_CHANGES §16; non-negotiable)
- Every simulated number sits next to the label **"Simulated · projected if you keep your commitments"**.
- Savings come only from `/projection`'s composed what-if (P1's model, one run, effects don't add). The day-by-day
  split is a typical-year (1991-2020) weather weighting of that annual delta; it never changes the annual total.
- Placeholders (`pending_model`, tips) contribute **0** and are listed in `not_modeled`.
- Writes nothing: no habit check-ins, bills, impact records, snapshots, projections, board rows. The real habit
  streak, the current grade, the "You" bar/marker, the rank and the page gradient never move.
- The simulated streak is "Day N 🔥 (simulated)" = real current streak + days, assuming a check-in every day.

## API: `POST /simulate/fast-forward`
Body `{property_id | session_id, days: 1-365, catalog_ids?: [...]}`.
- `property_id`: owner's bearer or agent key (`commitments._home`). Commitments = `catalog_ids` if given (the web
  sends accepted + toggled), else the home's accepted/completed ones. `session_id`: anonymous like the other
  `?session_id` routes; commitments = `catalog_ids`.
- Savings: `commitments.what_if` delta (`usd_saved_yr` renter's $, `co2_kg_saved_yr`) plus its heating/cooling $ split.
  Day weight = the day's typical heating degree-days (P1's base: HDD60 gas / HDD55 electric, or the metered fit's)
  ÷ the typical year's, and likewise for cooling (CDD65), from forecast.py's cached Open-Meteo 1991-2020 daily means
  at the home's cell. So October days save less than January days; 365 days from today sum to the annual delta
  (± rounding). CO₂ follows the building's heating/cooling $ split.
- Returns `{label: "simulated_projected_if_kept", label_text, method, start_date, days: [{date, usd_saved,
  kg_co2_saved, cumulative_usd, cumulative_kg, habit_day}], totals: {days, end_date, usd_saved, kg_co2_saved},
  annual: {usd_saved_yr, co2_kg_saved_yr}, commitments: [{catalog_id, title, modeled}], modeled, not_modeled,
  real_habit_streak, simulated_habit_streak}`. Errors: 422 `bad_days` / `missing_input` / `unknown_action`,
  404 `not_found` / `property_not_found`, 401/403, 503 `model_unavailable` / `forecast_unavailable`.
- Counted by the public rate limiter like `/projection` (it can run the model).

## Web: where and how (P3's design, no new visual language)
- **Where:** inside the board's **Commitments** section, right after the choice buttons and the
  "projected if completed" card, before the Commit/Target date row. Same for anonymous and signed-in visitors.
- **Structure** (existing classes): `h3.eyebrow` "⏩ Fast-forward"; a `.choice-row` of four
  `button.control.choice` — **1 day · 1 week · 1 month · Reset** — the active one `aria-pressed="true"` (P3's blue
  pressed state). Counters reuse P3's big-number style (`--font-display`, the `ranking-number` look) at a size that
  fits two side by side at 375 px; small captions use `.eyebrow` / `.board-note`. New rules only in
  `web/app/board/fast-forward.module.css` (counter size, two-column grid).
- **States:**
  1. *Nothing modeled selected* (no toggled or accepted commitment with model numbers): buttons disabled, note
     "Pick a modeled commitment to see savings add up."
  2. *Ready:* buttons enabled; note "Simulated · projected if you keep your commitments. Nothing is saved."
  3. *Running:* one request; buttons disabled; "Fast-forwarding…".
  4. *Result:* counters "$X saved" and "Y kg CO₂ avoided" count up (≤ 1.5 s) from the previous result; below:
     "Jan 4, 2027 · simulated", "Day N 🔥 (simulated)", and the label line. Tips listed as "Not modeled: …".
  5. *Reset:* clears the result and the pressed state; back to the real view (nothing else changed).
  6. *Error:* the API's message in the board's existing `.status .error` style with a retry.
- **Copy:** buttons "1 day", "1 week", "1 month", "Reset"; counters "$X saved" / "Y kg CO₂ avoided"; footnote
  "Typical-weather days (1991-2020): a January day saves more than an October day."
- **Accessibility:** real `<button>`s with `aria-pressed`; an `aria-live="polite"` sentence with the final numbers
  ("Simulated: after 30 days, about $X and Y kg CO₂, projected if you keep your commitments."); the animated digits
  are `aria-hidden` so screen readers hear only the final sentence; `prefers-reduced-motion: reduce` → no counting,
  final numbers at once. Focus stays on the pressed button.
- **Gradient:** unchanged. The page gradient already follows the "projected if completed" ghost when a modeled
  commitment is toggled; fast-forwarding doesn't change rank, so it doesn't move the gradient.

## Agent: `fast forward <days>` / `ff <days>`
One reply, numbers only from the API: "Simulation, not real usage: if you keep <titles>, in <N> days you'd save
about $X and Y kg CO₂ (projected). Your real streak stays N." Uses the saved home's accepted commitments; with
none modeled: "Nothing to fast-forward yet: none of your commitments has modeled savings. Say "options" and pick one
with numbers." 1-365 days, else a usage hint.

## Done when
- [x] Tests: 365-day weighting sums to the annual delta (± rounding), October < January per day, nothing written to
      any table, placeholders give 0, auth (property needs owner/agent; session anonymous), rate-limited path.
- [x] Live on :8081: 1514 Morton Ave (gas + single-pane, windows) 1/7/30/365 days, 365 ≈ projection's annual delta;
      1022 S Forest Ave (heat pump); Arrowwood (only placeholders → "pick a modeled commitment").
- [x] Board screenshots before/after a 30-day fast-forward (375 px works); `npm run build`, agent tests, API tests,
      `make phase2-check` 16/16; dev fast-forwarded; contract-changes entry.

## Handoff
- dev `5410f1c`: `api/app/simulate.py` (+ the `/projection` delta split in `app/commitments.py`, rate limit in
  `app/public_guard.py`); `web/app/board/fast-forward.tsx` + `.module.css`, mounted in `web/app/leaderboard.tsx`;
  agent `ff <days>` (`conversation.ts`, `phase2Replies.ts` `fastForwardText`, `api.ts` `checkFastForward`).
- Live (:8081, P1 on :8001): 1514 Morton Ave, gas + single-pane, windows: 1 / 7 / 30 / 365 days = $0.15 / $0.94 /
  $6.48 / $125.00 and 0.86 / 5.26 / 36.26 / 699.0 kg, vs /projection's $125 and 699 kg a year (January $23.56 vs
  October $5.95). 1022 S Forest Ave, electric + heat pump: $0.88 / $5.19 / $49.03 / $1,111 vs $1,111 and 2,509 kg a
  year. 2322 Arrowwood Trl: placeholders only, so $0 and "Pick a modeled commitment to see savings add up."
- By design, the page gradient doesn't move: a simulation never changes rank.

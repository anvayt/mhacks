```yaml
id: P4-02
title: iMessage interview loop (estimate → questions → answers), API numbers only
owner: P4
status: review
branch: p4/interview-loop
type: build
checkpoint: 1:00 AM GO/NO-GO (link → card → one texted answer → narrower range)
depends_on: [P4-01, P2-04]    # P2-04 (/answer, sessions, questions, grade) not served yet → mocked inside /agent
blocks: []
merges: []
services_touched:
  - /agent
services_read:
  - /api POST /estimate (real, dev @ 4602d55), POST /answer (PLAN.md §10; not served yet)
contract_change: none
```

## Goal
Turn the one-shot reply into a conversation: a link or address gets the estimate, then the agent asks the API's questions one at a time, sends each answer to the API, and texts back the narrower range and grade ("locked 🔒" once the API says so). Every number comes from an API response (PLAN.md §0 rule 4).

## Inputs (what I can rely on)
- Real `POST /estimate` (integration notes): building, bill p50 (heating + cooling), heating_cooling.accuracy; `session_id`, grade, questions, p10/p90 still null/empty. 422 codes: missing_input, needs_address (+hint), not_found, not_a_home, bad_unit_sqft; 503 model_unavailable / lookup_unavailable.
- Team decision (P2-04): a multi-unit listing with an estimated size asks "How big is the unit in sq ft? (or say skip)" first; `/estimate` takes `unit_sqft`.
- `POST /answer {session_id, question_id, answer}` → same shape (§10): not served yet → mock.

## Outputs (what I expose)
- Per-conversation state in `/agent` (session id, pending question, pending needs-address).
- Mock API `USE_MOCK_API=1` (in `/agent/src/mockApi.ts`) shaped to §10 + the integration's additive fields, labelled "demo data" in every reply.

## Steps
- [x] API client for /estimate and /answer with typed errors
- [x] Conversation state machine: new estimate · unit-size question · API questions · needs-address follow-up · welcome
- [x] Reply wording: grade/percentile/hidden rent/badges only when the API returns them; accuracy wording from `accuracy.basis` ("at least" on the ResStock path), gas error only for gas heat, year built marked as a neighborhood median when it is one (integration minor)
- [x] Mock API for /answer + questions (USE_MOCK_API)
- [x] Tests for the loop and the wording

## Done when
- [ ] (unit-tested with real response bodies; not run against a live /api) Against the real /estimate: address → reply; unit-size answer → second /estimate with unit_sqft → updated numbers
- [x] Against the mock: link → grade span + first question → answers → narrower range → "locked 🔒"
- [x] `npm test` (25), `npm run typecheck` pass; no invented numbers

## Handoff (fill in when done; DEV_STRATEGY #1)
- **What changed** (branch `p4/interview-loop` @ `12ca2de`, off `dev` `57d779e`; not merged yet): `agent/src/api.ts` (typed /estimate + /answer client), `agent/src/conversation.ts` (per-chat interview state), `agent/src/mockApi.ts` (USE_MOCK_API), `agent/src/replies.ts` (card + short update + question wording), `agent/src/agent.ts` wired to it. Tests: 25 pass.
- **Flow:** link/address → full card → if `sqft_estimated`, "How big is the unit in sq ft? (or say skip)" → second `/estimate` with `unit_sqft` and "(was …)" → API `questions` one at a time (number or text answer; unclear → re-ask) → `POST /answer` → short update (grade, range, badges) → "Grade B 🔒 … Grade locked in" when `locked`. `needs_address` → API hint shown, next text used as the address. Other 422/503 messages passed through as the API words them.
- **Integration minor fixed:** accuracy says "at least X%" when `accuracy.basis` says so (ResStock path); the gas-meter error is not shown for electric heat; a census year reads "built around 1965 (neighborhood median)". The old "grade and questions coming soon" line is gone.
- **Verified:** unit tests (real /estimate response bodies and error shapes from the integration notes); the agent process end to end in the terminal with `USE_MOCK_API=1` (link → grade B–D → unit size → 3 answers → $760–$1,960 narrowing to $1,220–$1,500 → Grade B 🔒).
- **Not verified:** a live `/api` (uv isn't installed on this laptop and the model needs its ~1 h build) and a real phone on this version.
- **Mocked:** `/answer`, sessions, grade, questions (P2-04 not served). With the real API today, `session_id` is null so no questions are asked; the unit-size step works. If `/answer` 404s, the reply says answers can't refine yet. Mock replies always start with "[demo data, not a real estimate]"; never demo with `USE_MOCK_API=1` without saying so.
- **Gaps:** chat state is in memory (restart = fresh chats); no web↔iMessage session ref code yet (no web handoff carries one).
- **Next:** P2-04 owner: serve `/answer` in the §10 shape (`questions[].options` as strings or `{value,label}`; `locked`); then run the loop on a real phone against the real API. P4 1–5 AM list: bill photo → `/calibrate`, badge/streak texts, landlord email.

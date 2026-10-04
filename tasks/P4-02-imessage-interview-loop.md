```yaml
id: P4-02
title: iMessage interview loop (estimate → questions → answers), API numbers only
owner: P4
status: in-progress
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
- [ ] API client for /estimate and /answer with typed errors
- [ ] Conversation state machine: new estimate · unit-size question · API questions · needs-address follow-up · welcome
- [ ] Reply wording: grade/percentile/hidden rent/badges only when the API returns them; accuracy wording from `accuracy.basis` ("at least" on the ResStock path), gas error only for gas heat, year built marked as a neighborhood median when it is one (integration minor)
- [ ] Mock API for /answer + questions (USE_MOCK_API)
- [ ] Tests for the loop and the wording

## Done when
- [ ] Against the real /estimate: address → reply; unit-size answer → second /estimate with unit_sqft → updated numbers
- [ ] Against the mock: link → grade span + first question → answers → narrower range → "locked 🔒"
- [ ] `npm test`, `npm run typecheck` pass; no invented numbers

## Handoff (fill in when done; DEV_STRATEGY #1)

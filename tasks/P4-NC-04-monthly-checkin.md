```yaml
id: P4-NC-04
title: Monthly check-in (manual trigger for the demo)
owner: P4
status: todo
branch: p4/monthly-checkin
type: build
checkpoint: NEW_CHANGES Phase 2 (after the existing P4 flow is verified on a real phone)
depends_on: [P4-NC-01, P4-NC-03]
blocks: []
merges: []
services_touched:
  - /agent
services_read:
  - /api POST /checkins/trigger {user_id} (or P4 decides from /me)
  - /api existing POST /calibrate
contract_change: additive   # endpoints proposed in NEW_CHANGES.md §10; P2 owns final shapes
```

## Goal
A documented manual trigger (`npm run checkin -- <phone>`) sends one allowlisted phone "Still at ‹address›?" (D9). Yes → asks for this month's bill → existing bill flow. Moved → P4-NC-03. No reply → nothing more (follow-up rules belong to P4-NC-05).

## Inputs (what I can rely on)
- NEW_CHANGES.md (design, decisions D1–D17, invariants I1–I8). Existing `/agent` flows (P4-01..P4-03).
- P2 endpoints below are **not served yet** → exact-contract mocks in `/agent/src/mockApi.ts` behind `USE_MOCK_API=1`; request filed in `notes/requests.md`.

## Outputs (what I expose)
- Conversation behavior in `/agent/src/conversation.ts`; mocks in `/agent/src/mockApi.ts`.

## Steps
- [ ] `scripts/checkin.ts` using Spectrum to message an existing DM space
- [ ] Dialog state: awaiting check-in answer
- [ ] Never sends at night (local hour check)

## Done when
- [ ] Trigger → message on a real phone
- [ ] Yes → bill flow; moved → address flow
- [ ] `npm test` + `npm run typecheck` pass; all existing P4 tests still pass
- [ ] No invented numbers; projected vs current vs verified wording correct (NEW_CHANGES §16)

## Handoff (fill in when done; DEV_STRATEGY #1)
- What changed (files, endpoints)
- How to use it / run it
- Known gaps, TODOs, anything mocked that still needs to be real
- Who needs to act next (`blocks` owners)

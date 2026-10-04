```yaml
id: P4-NC-03
title: Address change (moved → archive → new baseline)
owner: P4
status: todo
branch: p4/address-change-flow
type: build
checkpoint: NEW_CHANGES Phase 2 (after the existing P4 flow is verified on a real phone)
depends_on: [P4-NC-01]
blocks: []
merges: []
services_touched:
  - /agent
services_read:
  - /api POST /properties {user_id, address|url, unit_sqft?} → {property_id, estimate}
  - /api POST /properties/{id}/activate
contract_change: additive   # endpoints proposed in NEW_CHANGES.md §10; P2 owns final shapes
```

## Goal
"I moved" (or "moved" in reply to the check-in) asks for the new address, creates the new property, archives the old one with history, and runs a fresh estimate. Reductions never carry across a move (I4).

## Inputs (what I can rely on)
- NEW_CHANGES.md (design, decisions D1–D17, invariants I1–I8). Existing `/agent` flows (P4-01..P4-03).
- P2 endpoints below are **not served yet** → exact-contract mocks in `/agent/src/mockApi.ts` behind `USE_MOCK_API=1`; request filed in `notes/requests.md`.

## Outputs (what I expose)
- Conversation behavior in `/agent/src/conversation.ts`; mocks in `/agent/src/mockApi.ts`.

## Steps
- [ ] Detect "moved" intents; ask for the new address
- [ ] Create property, then continue with the normal estimate/interview flow
- [ ] Mocks behind `USE_MOCK_API`

## Done when
- [ ] Old home stays in history (mock), new home becomes current
- [ ] The interview restarts cleanly for the new home
- [ ] `npm test` + `npm run typecheck` pass; all existing P4 tests still pass
- [ ] No invented numbers; projected vs current vs verified wording correct (NEW_CHANGES §16)

## Handoff (fill in when done; DEV_STRATEGY #1)
- What changed (files, endpoints)
- How to use it / run it
- Known gaps, TODOs, anything mocked that still needs to be real
- Who needs to act next (`blocks` owners)

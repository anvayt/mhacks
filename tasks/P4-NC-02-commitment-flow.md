```yaml
id: P4-NC-02
title: Commitment flow (ranked suggestions → accept → projected effect)
owner: P4
status: todo
branch: p4/commitment-flow
type: build
checkpoint: NEW_CHANGES Phase 2 (after the existing P4 flow is verified on a real phone)
depends_on: [P4-NC-01]
blocks: []
merges: []
services_touched:
  - /agent
services_read:
  - /api GET /commitments/suggested/{property_id}
  - /api POST /commitments {user_id, property_id, catalog_id}
  - /api PATCH /commitments/{id} {status}
  - /api POST /projection {property_id, commitment_ids[]} → current vs projected, label projected_if_completed
contract_change: additive   # endpoints proposed in NEW_CHANGES.md §10; P2 owns final shapes
```

## Goal
After the grade (or on "commitments"), show the top 2–3 commitments ranked by CO₂ avoided per net $, let the renter accept/dismiss by number, and show the PROJECTED effect with correct wording (NEW_CHANGES §9, I5). Completing one marks it reported; it never changes the current grade.

## Inputs (what I can rely on)
- NEW_CHANGES.md (design, decisions D1–D17, invariants I1–I8). Existing `/agent` flows (P4-01..P4-03).
- P2 endpoints below are **not served yet** → exact-contract mocks in `/agent/src/mockApi.ts` behind `USE_MOCK_API=1`; request filed in `notes/requests.md`.

## Outputs (what I expose)
- Conversation behavior in `/agent/src/conversation.ts`; mocks in `/agent/src/mockApi.ts`.

## Steps
- [ ] Commitment list text: CO₂ and $ side by side, who acts, GRH points; only API numbers
- [ ] Accept/dismiss by number or name; "done 1" marks completed (reported)
- [ ] Projection text always says "projected" / "if completed"
- [ ] Mocks behind `USE_MOCK_API`

## Done when
- [ ] Wording tests: never "your new grade" for a projection
- [ ] Null projected fields are omitted, never $0
- [ ] Accept → projection → done flows in the terminal with mocks
- [ ] `npm test` + `npm run typecheck` pass; all existing P4 tests still pass
- [ ] No invented numbers; projected vs current vs verified wording correct (NEW_CHANGES §16)

## Handoff (fill in when done; DEV_STRATEGY #1)
- What changed (files, endpoints)
- How to use it / run it
- Known gaps, TODOs, anything mocked that still needs to be real
- Who needs to act next (`blocks` owners)

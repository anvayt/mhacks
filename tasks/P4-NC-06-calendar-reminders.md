```yaml
id: P4-NC-06
title: Google Calendar reminders (STRETCH)
owner: P4
status: todo
branch: p4/calendar-reminders
type: build
checkpoint: NEW_CHANGES Phase 2 (after the existing P4 flow is verified on a real phone)
depends_on: ['P4-NC-05']
blocks: []
merges: []
services_touched:
  - /agent
services_read:
  - /api POST /calendar/connect
  - /api POST /calendar/reminders
  - /api DELETE /calendar/reminders/{id}
contract_change: additive   # endpoints proposed in NEW_CHANGES.md §10; P2 owns final shapes
```

## Goal
Offer a Calendar event when a commitment is accepted and Calendar is connected. Stretch: cut first if it threatens reliability; a failure never blocks accepting a commitment.

## Inputs (what I can rely on)
- NEW_CHANGES.md (design, decisions D1–D17, invariants I1–I8). Existing `/agent` flows (P4-01..P4-03).
- P2 endpoints below are **not served yet** → exact-contract mocks in `/agent/src/mockApi.ts` behind `USE_MOCK_API=1`; request filed in `notes/requests.md`.

## Outputs (what I expose)
- Conversation behavior in `/agent/src/conversation.ts`; mocks in `/agent/src/mockApi.ts`.

## Steps
- [ ] Offer + confirm text
- [ ] Fallback to iMessage reminders on any failure

## Done when
- [ ] Calendar failure → commitment still accepted
- [ ] `npm test` + `npm run typecheck` pass; all existing P4 tests still pass
- [ ] No invented numbers; projected vs current vs verified wording correct (NEW_CHANGES §16)

## Handoff (fill in when done; DEV_STRATEGY #1)
- What changed (files, endpoints)
- How to use it / run it
- Known gaps, TODOs, anything mocked that still needs to be real
- Who needs to act next (`blocks` owners)

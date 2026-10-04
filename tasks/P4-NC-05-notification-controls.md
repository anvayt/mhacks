```yaml
id: P4-NC-05
title: Notification and reminder controls (opt-in, capped, stop/pause)
owner: P4
status: todo
branch: p4/notification-controls
type: build
checkpoint: NEW_CHANGES Phase 2 (after the existing P4 flow is verified on a real phone)
depends_on: [P4-NC-02, P4-NC-04]
blocks: []
merges: []
services_touched:
  - /agent
services_read:
  - /api user reminder_prefs (via /me or a new PATCH /me/{user_id})
  - /api existing GET /forecast/{session_id} (cold-snap alerts)
contract_change: additive   # endpoints proposed in NEW_CHANGES.md §10; P2 owns final shapes
```

## Goal
Opt-in task reminders within NEW_CHANGES §9.6 / D4: max one proactive text a day, never at night, auto-pause after 2 unanswered, "stop"/"pause"/"resume" any time. Optional weather alerts from P2's /forecast count toward the cap.

## Inputs (what I can rely on)
- NEW_CHANGES.md (design, decisions D1–D17, invariants I1–I8). Existing `/agent` flows (P4-01..P4-03).
- P2 endpoints below are **not served yet** → exact-contract mocks in `/agent/src/mockApi.ts` behind `USE_MOCK_API=1`; request filed in `notes/requests.md`.

## Outputs (what I expose)
- Conversation behavior in `/agent/src/conversation.ts`; mocks in `/agent/src/mockApi.ts`.

## Steps
- [ ] "stop"/"pause"/"resume" commands
- [ ] Cap and quiet-hours guard shared by every proactive send
- [ ] Reminder opt-in after accepting a commitment

## Done when
- [ ] Guard unit tests (cap, quiet hours, auto-pause)
- [ ] "stop" immediately blocks proactive sends; replies still work
- [ ] `npm test` + `npm run typecheck` pass; all existing P4 tests still pass
- [ ] No invented numbers; projected vs current vs verified wording correct (NEW_CHANGES §16)

## Handoff (fill in when done; DEV_STRATEGY #1)
- What changed (files, endpoints)
- How to use it / run it
- Known gaps, TODOs, anything mocked that still needs to be real
- Who needs to act next (`blocks` owners)

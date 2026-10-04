```yaml
id: P4-NC-01
title: Account-aware sender (phone → account → current home)
owner: P4
status: todo
branch: p4/account-aware-sender
type: build
checkpoint: NEW_CHANGES Phase 2 (after the existing P4 flow is verified on a real phone)
depends_on: []
blocks: ['P4-NC-02', 'P4-NC-03', 'P4-NC-04']
merges: []
services_touched:
  - /agent
services_read:
  - /api POST /auth/phone {phone, session_id?} → {user_id, created, current_property_id}
  - /api GET /me/{user_id} → {current_property_id, properties[]}
contract_change: additive   # endpoints proposed in NEW_CHANGES.md §10; P2 owns final shapes
```

## Goal
Every inbound sender resolves to one Hidden Rent account (NEW_CHANGES §5, D5). A known phone with a current home is greeted "Welcome back, still at ‹address›?"; an unknown phone gets the normal welcome. A "(ref id)" first text links that web session to the account.

## Inputs (what I can rely on)
- NEW_CHANGES.md (design, decisions D1–D17, invariants I1–I8). Existing `/agent` flows (P4-01..P4-03).
- P2 endpoints below are **not served yet** → exact-contract mocks in `/agent/src/mockApi.ts` behind `USE_MOCK_API=1`; request filed in `notes/requests.md`.

## Outputs (what I expose)
- Conversation behavior in `/agent/src/conversation.ts`; mocks in `/agent/src/mockApi.ts`.

## Steps
- [ ] `src/accounts.ts`: resolve sender → account (cache per chat; normalized handle via `normalizePhone`, raw handle when it's an email)
- [ ] Greeting for known phones; unchanged welcome for new ones
- [ ] Pass `session_id` on the first "(ref id)" text to link the web session
- [ ] Rehydrate dialog state after an agent restart from `/me` (D8)
- [ ] Mocks in `src/mockApi.ts` behind `USE_MOCK_API`

## Done when
- [ ] Same phone in different formats → same account (unit test)
- [ ] Two quick first messages → one account (mock enforces I1)
- [ ] Restart → returning user still greeted with their home
- [ ] Existing Phase 1 flows unchanged (all prior tests pass)
- [ ] `npm test` + `npm run typecheck` pass; all existing P4 tests still pass
- [ ] No invented numbers; projected vs current vs verified wording correct (NEW_CHANGES §16)

## Handoff (fill in when done; DEV_STRATEGY #1)
- What changed (files, endpoints)
- How to use it / run it
- Known gaps, TODOs, anything mocked that still needs to be real
- Who needs to act next (`blocks` owners)

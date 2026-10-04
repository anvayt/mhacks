```yaml
id: P2-04
title: Real /estimate and /answer endpoints
owner: P2
status: todo
branch: p2/estimate-answer
type: build
checkpoint: 1:00 AM GO/NO-GO
depends_on: [P2-01, P2-02, P2-03, P1 model]
blocks: [P3, P4]
merges: []
services_touched:
  - /api
services_read:
  - /model predict + question picker (P1)
contract_change: additive   # bill.seasonal {winter, spring, summer, fall} each {p10, p50, p90}; per-season is what users expect (PLAN.md §1 note)
```

## Goal
`POST /estimate` (url or address) and `POST /answer` in the PLAN.md §10 shape, plus `bill.seasonal`. Use P1's model when it's ready; until then use a stand-in inside `/api` behind one switch (DEV_STRATEGY #4).

## Done when
- [ ] Link or address → full §10 response, sessions persisted (SQLite), answers narrow the range; the 1 AM end-to-end path works

## Handoff (fill in when done; DEV_STRATEGY #1)
- What changed (files, endpoints)
- How to use it / run it
- Known gaps, TODOs, anything mocked that still needs to be real
- Who needs to act next (`blocks` owners)

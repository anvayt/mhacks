```yaml
id: P2-05
title: /calibrate, /fixes, /compare + badge rules
owner: P2
status: todo
branch: p2/calibrate-fixes-compare
type: build
checkpoint: 5:00 AM checkpoint
depends_on: [P2-04]
blocks: [P3, P4]
merges: []
services_touched:
  - /api
services_read:
  - /model (calibration fit, fix simulator)
  - Green Rental Housing checklist (PLAN.md §4)
contract_change: none
```

## Goal
The after-move-in and comparison endpoints in the §10 shapes, plus the badge rules from PLAN.md §5 as simple functions on API fields.

## Done when
- [ ] Each endpoint returns its §10 shape from real computations; badges appear in `/estimate`, `/answer`, `/calibrate`

## Handoff (fill in when done; DEV_STRATEGY #1)
- What changed (files, endpoints)
- How to use it / run it
- Known gaps, TODOs, anything mocked that still needs to be real
- Who needs to act next (`blocks` owners)

```yaml
id: P2-08
title: (Stretch) Satellite "snow melts first on leaky roofs" test
owner: P2
status: todo
branch: p2/snow-melt
type: research
checkpoint: 3:00 AM go/no-go
depends_on: [P2-01]
blocks: []
merges: []
services_touched:
  - /api
services_read:
  - Sentinel-2 imagery from last winter (external)
contract_change: none
```

## Goal
Only if everything else is on track: check whether last winter's satellite imagery shows roofs losing snow faster (a heat-leak signal). Enables the SpaceX track only if it works and we've used Cursor.

## Done when
- [ ] A go/no-go note with evidence by 3 AM

## Handoff (fill in when done; DEV_STRATEGY #1)
- What changed (files, endpoints)
- How to use it / run it
- Known gaps, TODOs, anything mocked that still needs to be real
- Who needs to act next (`blocks` owners)

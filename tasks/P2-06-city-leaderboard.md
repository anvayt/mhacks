```yaml
id: P2-06
title: City batch scoring → /city + /leaderboard
owner: P2
status: todo
branch: p2/city-leaderboard
type: build
checkpoint: 5:00 AM checkpoint
depends_on: [P2-01, P2-04]
blocks: [P3]
merges: []
services_touched:
  - /api
services_read:
  - Cached footprints (P2-01), /model predict (P1)
  - Ann Arbor benchmarking FeatureServer (only buildings we may name)
contract_change: none
```

## Goal
Score every residential footprint once, serve it as GeoJSON for the map, and build leaderboards (name only buildings in the city's public benchmarking data; aggregate the rest by block or neighborhood).

## Done when
- [ ] `/city` returns every residential footprint with score, grade and excess $/sq ft; `/leaderboard` returns best + worst blocks; both cached and fast

## Handoff (fill in when done; DEV_STRATEGY #1)
- What changed (files, endpoints)
- How to use it / run it
- Known gaps, TODOs, anything mocked that still needs to be real
- Who needs to act next (`blocks` owners)

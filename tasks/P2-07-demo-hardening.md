```yaml
id: P2-07
title: Demo hardening: caching + offline demo listings
owner: P2
status: todo
branch: p2/demo-hardening
type: build
checkpoint: 8:00 AM FEATURE FREEZE
depends_on: [P2-04, P2-05, P2-06]
blocks: []
merges: []
services_touched:
  - /api
services_read: []
contract_change: none
```

## Goal
The demo must never depend on a live external API: cache geocoder/footprint/census results and precompute 5 demo listings so the whole flow works with Wi-Fi off.

## Also
- Geocoder fallback: when the Census geocoder moves an address (e.g. Ashley Mews → S Ashley St, ~450 m) and the 250 m city-point guard rejects it, fall back to the city's own mailing-address point for that street line.

## Done when
- [ ] With the network disabled, all 5 demo listings return full responses on every endpoint

## Handoff (fill in when done; DEV_STRATEGY #1)
- What changed (files, endpoints)
- How to use it / run it
- Known gaps, TODOs, anything mocked that still needs to be real
- Who needs to act next (`blocks` owners)

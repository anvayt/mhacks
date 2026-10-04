```yaml
id: P2-02b
title: Map links (Google/Apple), more listing sites, map short-link resolution
owner: P2
status: in-progress
branch: p2/listing-maps          # off p2/listing-parser (extends listing.py)
type: build
checkpoint: 1:00 AM GO/NO-GO
depends_on: [P2-02]
blocks: [P2-04]
merges: []
services_touched:
  - /api
services_read:
  - Map short-link redirects (external; one HEAD/GET-no-body redirect hop, 3 s timeout, cached)
contract_change: none
```

## Goal
Accept the links people actually share: Google Maps and Apple Maps (full and short links, incl. iMessage location shares), plus Trulia, Realtor.com, Homes.com and HotPads listing URLs. Map links also yield coordinates, so P2-04 can skip geocoding.

## Inputs (what I can rely on)
- `api/app/listing.py` from P2-02 (`parse_listing_url`, pure, no network).

## Outputs (what I expose)
- `parse_listing_url(url)` stays **pure** (no network) and gains: Google Maps (`/maps/place/<addr>/@lat,lon`, `?q=`, `?query=`, `/maps/search/`), Apple Maps (`maps.apple.com/?address=…&ll=…&q=…`), Trulia, Realtor.com, Homes.com, HotPads. Result adds optional `lat`, `lon` (additive).
- `resolve_link(url)` in `api/app/links.py`: **only** for allowlisted map short-link hosts (e.g. `maps.app.goo.gl`, `goo.gl/maps`, `maps.apple/p`), follows redirects without downloading page bodies, 3 s timeout, on-disk cache; then calls `parse_listing_url` on the final URL. Any other host → never touches the network.
- Zumper, Rent.com, Craigslist, Facebook Marketplace (no address in URL) → `needs_address: true` with a hint when possible.

## Done when
- [ ] Tests for every format using real-shaped URLs (verified against public examples); short-link resolver tested with the network mocked, plus one optional live test (skipped by default)
- [ ] `parse_listing_url` still makes zero network calls (socket-blocking test stays green)
- [ ] All existing P2-02 tests still pass

## Handoff (fill in when done; DEV_STRATEGY #1)
- What changed (files, endpoints)
- How to use it / run it
- Known gaps, TODOs, anything mocked that still needs to be real
- Who needs to act next (`blocks` owners)

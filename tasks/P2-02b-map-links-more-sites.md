```yaml
id: P2-02b
title: Map links (Google/Apple), more listing sites, map short-link resolution
owner: P2
status: review
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

## Team decisions (Oct 3)
- Normalize Zillow `#4` / `APT-4` units to `Unit 4` so all sites match (follow-up after the current build).

## Done when
- [x] Tests for every format using real-shaped URLs (verified against public examples); short-link resolver tested with the network mocked, plus one optional live test (skipped by default)
- [x] `parse_listing_url` still makes zero network calls (socket-blocking test stays green)
- [x] All existing P2-02 tests still pass

## Handoff (fill in when done; DEV_STRATEGY #1)
- **What changed:** branch `p2/listing-maps` (commits 9f7d600 + 931c10b verifier fixes, pushed; not merged; based on `p2/listing-parser`). `api/app/listing.py` (extended, still pure), new `api/app/links.py`, `api/tests/test_listing.py` (extended), new `api/tests/test_links.py`. No endpoints, no new deps (`links.py` uses `httpx`, already in P2-01's `pyproject.toml`).
- **How to use:** `parse_listing_url(text)` (pure) or `resolve_link(text)` (same dict + `"resolved_url"`; only map short links touch the network). Keys as P2-02, plus for map links with coordinates: `lat`, `lon`, `coords_only`. `coords_only: true` means coordinates but address `None`. Then `needs_address` is `false` only for an unnamed explicit point (Google dropped pin, `q=`/`query=lat,lon`, `loc:`, Apple `ll=`/`coordinate=` with no name, iMessage `CL.loc.vcf`): safe to look the footprint up by point. A named pin (`hint` set; may be a business or a whole city, e.g. `maps.app.goo.gl/N7Qqbomd6kmiEfst6` is the Ann Arbor city centre) or a bare map view (`/maps/@lat,lon,z`, `center=`) has `needs_address: true` with `lat`/`lon` kept for a one-tap "use this pin". Map links without coordinates have no `lat`/`lon` keys, so use `r.get("lat")`. A link followed by punctuation (`…/AbC.`, `(…/AbC)`) is found without it. New `source` values: `google_maps`, `apple_maps`, `trulia`, `realtor`, `homes`, `hotpads`, `zumper`, `rent`, `craigslist`, `facebook`.
  - Address from URL: Trulia `/home/`, `/building/` (name prefix dropped), `/p/…--id`; Realtor.com `/realestateandhomes-detail/` and `/rentals/details/` (`Street_City_ST_ZIP_M…`); Homes.com `/property/<slug>/<id>/`; HotPads `<slug>-<id>/pad|building` (listing titles like `3-bed-10-bath-2850-…` are rejected). Google Maps `/place/`, `/search/`, `/dir/` (destination), `?q= ?query= ?daddr= ?destination=`; Apple Maps `?address= ?q=`, `/place?address=`, `/search?query=`, `/directions?destination=`. Place-name prefixes ("Apple Inc., 1 Apple Park Way, …") and ", United States" are dropped.
  - Coordinates: Google pin `!3d/!4d`, then coordinate text (`q=42.28,-83.74`, `loc:`), then bare views `/maps/@lat,lon,17z` and `center=`. Apple `coordinate=`, `ll=`, including iMessage `CL.loc.vcf` vCards (`\,` unescaped).
  - Hint only (`needs_address: true`): Zumper and Rent.com slugs (`"715 Arbor St, Ann Arbor, MI"`), Craigslist region (`"Ann Arbor, MI"`), Facebook Marketplace (no hint).
  - `resolve_link` allowlist: `maps.app.goo.gl/*`, `goo.gl/maps/*`, `maps.apple/*`. Each hop is a GET read for headers only (Apple's short links 404 on HEAD, checked live). 3 s timeout, at most 5 hops, redirects followed by hand. It stops at the first URL off the allowlist and parses it without fetching, which also unwraps `consent.google.com?continue=`. Results are cached in `<repo>/data/short_link_cache.json` (git-ignored). Failures and dead links are not cached and return the short link's `needs_address` result with `resolved_url: None`.
- **Run tests:** `cd api && uv run --no-project --python 3.12 --with pytest --with httpx python -m pytest -q` gives `119 passed, 1 skipped` (44 from P2-02 unchanged). The live test: `RUN_LIVE=1 … -k live` (it resolves a real `maps.apple/p/…`, a real `maps.app.goo.gl/…`, and a city short link followed by `.`; it passed on Oct 3).
- **Known gaps:** Google `/maps/place/<name>` with no `!3d/!4d` pin gives no coordinates, because the `@` there is the viewport centre (25 km off at zoom 10 in a real link). Google `/dir/` data blocks (`!1d lon!2d lat`) aren't parsed, so only the destination text is used. Non-US map addresses come back `needs_address` with the place text as hint. Trulia `/building/` takes the rightmost house number, so a street like "W 8 Mile Rd" would lose its number. Realtor.com URLs were checked on its sister site highrises.com, because realtor.com blocks our crawler. Craigslist hints only cover `KNOWN_CITIES` regions. No mocks.
- **Next:** P2-04 should call `resolve_link(text)` (not `parse_listing_url`) in `POST /estimate`. If `address`, geocode it (`lat`/`lon` may also be there to skip geocoding). If `coords_only` and not `needs_address`, look up the footprint by `lat`/`lon`. If `needs_address`, ask the user and show `hint`; when `lat`/`lon` are present, also offer "use this pin" (then look up by point).

### QUESTIONS FOR THE TEAM
1. Zumper and Rent.com slugs often hold a street address, but the task says hint-only, and Zumper p238's slug names a different street than its listing. I kept them hint-only (the safe default). Should P2-04 geocode the hint without asking the user?
2. Settled after verification (safest reversible option): bare map views and named pins (cities, businesses) now return `needs_address: true` with `lat`/`lon` kept, so P2-04 asks before scoring them. Only unnamed explicit points skip the question. If that's too many prompts, P2-04 could auto-accept a named pin whose hint isn't a city; tell P2 and the rule moves into `_map_result`.

```yaml
id: P2-02
title: Listing URL → address parser (Zillow, Redfin, Apartments.com)
owner: P2
status: review
branch: p2/listing-parser
type: build
checkpoint: 10:30 PM checkpoint
depends_on: []
blocks: [P2-04]
merges: []
services_touched:
  - /api
services_read: []
contract_change: none
```

## Goal
Turn a pasted listing link into a street address **from the URL text only, never by fetching or scraping the page** (PLAN.md §4 step 1).

## Inputs (what I can rely on)
- Nothing from other tasks. Pure string parsing.

## Outputs (what I expose)
- `api/app/listing.py`: `parse_listing_url(url) -> {"address": str | None, "unit": str | None, "zip": str | None, "source": "zillow"|"redfin"|"apartments"|"unknown", "needs_address": bool, "hint": str | None}`.
  - Zillow: `/homedetails/123-Main-St-APT-4-Ann-Arbor-MI-48104/12345_zpid/` → `123 Main St Apt 4, Ann Arbor, MI 48104`
  - Redfin: `/MI/Ann-Arbor/123-Main-St-48104/unit-4/home/12345` → `123 Main St Unit 4, Ann Arbor, MI 48104`
  - Apartments.com: usually a property name, not a street (`/the-courtyards-ann-arbor-mi/abc123/`) → `needs_address: true` with `hint: "The Courtyards, Ann Arbor, MI"`.
  - Anything else → `needs_address: true`.

## Steps
- [x] Parsers for the three sites (unit numbers, ZIP, state, city names with hyphens)
- [x] `tests/test_listing.py` with 10+ real-shaped URLs, including units, short links and junk input

## Done when
- [x] All tests pass; no network calls anywhere in the module

## Handoff (fill in when done; DEV_STRATEGY #1)
- **What changed:** branch `p2/listing-parser` (commits c196308 + 0b40885 verifier fix, pushed; not merged). New files only: `api/app/__init__.py` (empty), `api/app/listing.py`, `api/tests/test_listing.py`. No endpoints, no deps beyond stdlib, no mocks.
- **How to use:** `from app.listing import parse_listing_url` → dict exactly as in Outputs above. `address` includes the unit (`"549 Longshore Dr Apt A, Ann Arbor, MI 48105"`), `unit` is `"Apt A"` / `"Unit C1"` / `"#4"`, `zip` may be None (Zillow `/b/` and Apartments.com slugs have no ZIP). Also accepts a URL inside a sentence (iMessage text). Handles Zillow `/homedetails/…_zpid/`, `/homes/…_rb/`, `/b/` building pages; Redfin `/<ST>/<City>/<street>-<zip>/[unit-x/]home|apartment/<id>`; Apartments.com `/<slug>/<id>/`, including unit listings where the unit comes after the state (`/1218-washtenaw-ct-ann-arbor-mi-unit-1/9r3c5n5/` → `1218 Washtenaw Ct Unit 1, Ann Arbor, MI`; free text after `unit` like `unit-3-bedroom-15-bath` is dropped, street kept); mobile domains, no scheme, query strings, fragments, `%23`/`#` units.
- **Run tests:** `cd api && uv run --no-project --with pytest python -m pytest tests/test_listing.py -q` → `44 passed`.
- **Known gaps:** short links (`redf.in/…`) and `/homedetails/<id>_zpid/` with no slug return `needs_address: true, hint: None` (expanding them needs a network call, which is out of scope). Property-name slugs only split off the city for cities in `KNOWN_CITIES` (Ann Arbor area + a few MI cities); otherwise the hint is e.g. `"Willow Tree Apartments Southfield, MI"`. Zillow slugs with a bare unit and no APT/UNIT/# marker aren't detected. Street/city split for cities outside `KNOWN_CITIES` uses the last street suffix, so a city like "St Clair Shores" would need adding to the list.
- **Next:** P2-04 calls `parse_listing_url(url)` in `POST /estimate`; if `needs_address` is true, ask the user for the address (show `hint` when present) or try geocoding the hint.

```yaml
id: P2-02
title: Listing URL → address parser (Zillow, Redfin, Apartments.com)
owner: P2
status: in-progress
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
- [ ] Parsers for the three sites (unit numbers, ZIP, state, city names with hyphens)
- [ ] `tests/test_listing.py` with 10+ real-shaped URLs, including units, short links and junk input

## Done when
- [ ] All tests pass; no network calls anywhere in the module

## Handoff (fill in when done; DEV_STRATEGY #1)
- What changed (files, endpoints)
- How to use it / run it
- Known gaps, TODOs, anything mocked that still needs to be real
- Who needs to act next (`blocks` owners)

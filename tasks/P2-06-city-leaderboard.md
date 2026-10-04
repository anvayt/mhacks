```yaml
id: P2-06
title: City batch scoring → /city + /leaderboard
owner: P2
status: done
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
- [x] `/city` returns every residential footprint with score, grade and excess $/sq ft; `/leaderboard` returns best + worst blocks; both cached and fast

## Handoff (Oct 4, ~3 AM; merged into `dev` at `fd8c31c` via `p2/merge-wave2`)
- **What changed:** `api/scripts/score_city.py` scored 25,670 residential footprints with P1's model (`api/data/city_scores.csv`, run log `city_scores.json`); `api/app/city.py` `GET /city` (GeoJSON, gzip ~3.6 MB, props `score, grade, excess_usd_per_sqft, type`), `GET /leaderboard?scope=city|neighborhood` (named only for public benchmarking buildings; block groups / tracts with ≥ 5 buildings), `city_costs(building_type)`, now also the peer set for `/estimate` scores.
- **How to run:** `cd api && uv sync && uv run python scripts/fetch_footprints.py` (once), P1's model on :8001 (`make -C model dashboard`), `uv run uvicorn app.main:app --port 8000`; tests `uv run pytest -q` (377 pass). Rescore: `uv run python scripts/score_city.py`, then restart the API.
- **Gaps:** scores use P1's defaults (no renter answers); neighborhoods are census tracts; P3's richer citywide layer (LiDAR height, matched address) is in progress.
- **Next:** P3 reads `/city` and `/leaderboard`.

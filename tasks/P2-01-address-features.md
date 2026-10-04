```yaml
id: P2-01
title: Address → building features (geocoder + Ann Arbor footprints + year built)
owner: P2
status: in-progress
branch: p2/address-features
type: build
checkpoint: 10:30 PM checkpoint
depends_on: []
blocks: [P2-04, P2-06]
merges: []
services_touched:
  - /api
services_read:
  - US Census geocoder (external)
  - Ann Arbor BuildingFootprints FeatureServer (external, cached to /data/)
  - Census ACS B25035 median year built (external)
contract_change: none
```

## Goal
Given any Ann Arbor street address, return the building features the bill model needs (PLAN.md §4 step 2, §6). This is the 10:30 PM checkpoint for P2: "address → features works".

## Inputs (what I can rely on)
- Census geocoder (no key): <https://geocoding.geo.census.gov/geocoder/>. The `geographies/onelineaddress` call also returns the census block group.
- Ann Arbor footprints (35,110 polygons, no key): <https://a2maps.a2gov.org/a2arcgis/rest/services/OSI/BuildingFootprints/FeatureServer/0>, with fields `ABG_BLD_HG` (height), `STORIES`, `Struc_Type` and `PackedPin`.
- ACS table B25035, median year built per block group (Census API or Census Reporter).

## Outputs (what I expose)
- `api/app/geo/features.py`: `get_features(address) -> dict` (below), plus a CLI: `uv run python -m app.geo.features "<address>"`.
- A minimal FastAPI app (`api/app/main.py`) with `GET /health` and `GET /debug/features?address=…`. The debug endpoint is internal only and not part of §10.
- Features dict (ResStock column names so the model can consume them directly):
  - `in.sqft`: **houses** use footprint area × stories. **Multi-unit buildings** use the unit sq ft if given (from the listing or the renter), else building floor area ÷ estimated units.
  - `in.geometry_stories`: `STORIES`, else height ÷ ~3 m.
  - `in.geometry_building_type_recs`: `Struc_Type` mapped to ResStock categories (Single-Family Detached / Single-Family Attached / Multi-Family with 2 - 4 Units / Multi-Family with 5+ Units / Mobile Home).
  - `in.vintage`: year built → ResStock decade bins (year from the listing if given, else the block-group median).
  - `in.county_name`: `MI, Washtenaw County`.
  - Plus `lat`, `lon`, `footprint_geojson`, `building_sqft`, `is_multi_unit`, `est_units`, `year_built`, `year_built_source`, `block_group_geoid`, and `sources` (where each value came from).

## Steps
- [ ] `api/` project skeleton: `pyproject.toml` (Python 3.12, uv), `app/__init__.py`, `app/main.py`, `README.md`
- [ ] `scripts/fetch_footprints.py`: page through the FeatureServer once → `/data/a2_footprints.geojson` (root `/data/` is git-ignored)
- [ ] `geo/footprints.py`: load the cache, spatial index, point-in-polygon (nearest within ~25 m as fallback)
- [ ] `geo/geocode.py`: Census geocoder with block group, with a local response cache
- [ ] `geo/census.py`: block-group median year built (B25035), cached
- [ ] `geo/features.py`: assemble the dict, compute area in a projected CRS (UTM 17N), map types and vintage
- [ ] `tests/test_features.py`: 3 real Ann Arbor addresses (a house, a 2–4 unit, a large apartment building) → sane stories, type and floor area
- [ ] `/health` + `/debug/features`

## Done when
- [ ] `uv run python -m app.geo.features "500 S State St, Ann Arbor, MI"` prints a full features dict
- [ ] `curl 'localhost:8000/debug/features?address=…'` returns the same
- [ ] Tests pass; works offline after the first footprint download
- [ ] No secrets committed; every value lists its source (PLAN.md §0)

## Handoff (fill in when done; DEV_STRATEGY #1)
- What changed (files, endpoints)
- How to use it / run it
- Known gaps, TODOs, anything mocked that still needs to be real
- Who needs to act next (`blocks` owners)

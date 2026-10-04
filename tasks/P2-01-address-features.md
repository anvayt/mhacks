```yaml
id: P2-01
title: Address → building features (geocoder + Ann Arbor footprints + year built)
owner: P2
status: review
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
- [x] `api/` project skeleton: `pyproject.toml` (Python 3.12, uv), `app/__init__.py`, `app/main.py`, `README.md`
- [x] `scripts/fetch_footprints.py`: page through the FeatureServer once → `/data/a2_footprints.geojson` (root `/data/` is git-ignored)
- [x] `geo/footprints.py`: load the cache, spatial index, point-in-polygon (nearest within ~25 m as fallback)
- [x] `geo/geocode.py`: Census geocoder with block group, with a local response cache
- [x] `geo/census.py`: block-group median year built (B25035), cached
- [x] `geo/features.py`: assemble the dict, compute area in a projected CRS (UTM 17N), map types and vintage
- [x] `tests/test_features.py`: 3 real Ann Arbor addresses (a house, a 2–4 unit, a large apartment building) → sane stories, type and floor area
- [x] `/health` + `/debug/features`

## Done when
- [x] `uv run python -m app.geo.features "500 S State St, Ann Arbor, MI"` prints a full features dict
- [x] `curl 'localhost:8000/debug/features?address=…'` returns the same
- [x] Tests pass; works offline after the first footprint download
- [x] No secrets committed; every value lists its source (PLAN.md §0)

## Follow-up (team decisions Oct 3, ~9:20 PM; branch p2/address-features)
- [ ] **Townhouse rule:** classify row/attached homes as `Single-Family Attached` (ResStock category) instead of small multi-family.
- [ ] **Stories snapping:** snap `in.geometry_stories` to the nearest ResStock 2024.2 MI category (1–15, 20, 21, 35); keep the raw count in `stories_raw`.
- **FOR MERGE (tell P1/Dennis):** `in.geometry_stories` is snapped to ResStock's categories (e.g. 26-story Tower Plaza → 21 or 35, nearest). If P1's model treats stories as a number instead, use `stories_raw`. Decide at merge.

## Handoff (fill in when done; DEV_STRATEGY #1)
**Branch `p2/address-features` @ 2731a80, pushed. Not merged into dev.** All "Done when" items pass (12 tests).

**Verifier fixes (2731a80)**
- Units = max(residential addresses inside the footprint, `"<street> UNIT n"` rows of any TYPE for the street line that located the footprint). Fixes towers read as SFD: 721 S Forest Ave (Verve) -> MF 5+, 218 units, 1,800 sq ft; 2901 Northbrook Pl -> 202 units, 831; 1770 Broadway St -> 106 units, 1,219. `sources.est_units` says which count won.
- `in.sqft` outside the ResStock 2024.2 MI range (MF min 322, SFD max 5,587, per verifier's parquet check) adds a `warnings` entry; multi-unit without caller `unit_sqft` then uses the MI renter MF median 854 sq ft (n=2,628), `sqft_estimated` true. 405 S Main St 50 -> 854, 727 Miller Ave 110 -> 854 (both still report wrong stories, 2 and 1).

**What changed** (all under `/api`)
- `pyproject.toml` + `uv.lock` (py3.12; fastapi, uvicorn, httpx, shapely, pyproj, pandas; pytest dev), `README.md`, empty `app/__init__.py`
- `app/main.py`: `GET /health`, `GET /debug/features?address=&unit_sqft=&year_built=` (404 on unknown address; internal, not §10)
- `app/geo/features.py`: `get_features(address, unit_sqft=None, year_built=None) -> dict` + CLI; mappers `vintage()`, `building_type()`
- `app/geo/footprints.py` (lookup, UTM 17N area, units, stories-from-height), `geocode.py` (Census geocoder, disk cache), `census.py` (ACS B25035)
- `scripts/fetch_footprints.py`: downloads city BuildingFootprints (35,007) **and MailingAddress (65,138 points, owner fields not downloaded)** to `/data/`
- `tests/test_features.py`

**How to use**: `cd api && uv sync && uv run python scripts/fetch_footprints.py` (once, ~20 s) then `uv run python -m app.geo.features "912 Mary St, Ann Arbor, MI"` or `uv run uvicorn app.main:app --port 8000`. P2-04: `from app.geo.features import get_features`; the `in.*` keys go straight to the model, `lat/lon/footprint_geojson/building_sqft/year_built` fill §10 `building`. Raises `LookupError` (no geocode / no footprint within 25 m).

**Deviations from this task file (data said otherwise)**
- `in.county_name` is `Washtenaw County` (exact string in the ResStock 2024.2 MI parquet), not `MI, Washtenaw County`.
- `Struc_Type` only has Residential (32,572) / Commercial / Public / Office, so it can't give SF vs MF. Type comes from **the number of residential mailing addresses inside the footprint** (city MailingAddress layer, which lists units like `... UNIT 101`): 1 → SFD, 2–4 → MF 2-4, 5+ → MF 5+. Commercial/Office/Public with 0 residential addresses → type `null`, `in.sqft` `null`, `warnings` set. SFA and Mobile Home are never produced.
- Stories from height: `ABG_BLD_HG` is in **feet**; uses a least-squares fit on footprints with both fields (≈11.1 ft/story + 1.4 ft), not "÷ 3 m".
- Year built via **Census Reporter** (ACS 2020-2024 5-yr), because api.census.gov now redirects keyless calls to missing_key. Fallback BG → tract → county.
- `500 S State St` is the UM LSA Building (Public), so it returns the non-home case.
- Multi-unit `in.sqft` = building floor area ÷ unit count; includes hallways, so it runs high. Below 322 it falls back to the 854 median (above).

**Known gaps**: 2020+ builds bin to `2010s` (no ResStock bin); footprint area may include attached garages; a few tall buildings have odd `STORIES` (e.g. The Standard = 2); geocode cache is per-address on first use (network needed once per new address); no offline demo fixtures (team decision: testing after merge).

**Who acts next**: P2-04 (`/estimate`: call `get_features`, decide what to do with `null` type), P2-06 (city batch: reuse `footprints._index()` / unit counts).

# Hidden Rent API (`/api`)

FastAPI backend. Python 3.12, managed with [uv](https://docs.astral.sh/uv/).

## Run

```bash
cd api
uv sync                                   # install deps (+ pytest)
uv run python scripts/fetch_footprints.py # once: ~36 MB of city GIS data -> ../data/ (git-ignored), ~20 s
uv run uvicorn app.main:app --reload --port 8000
```

- `GET /health` → `{"status": "ok"}`
- `GET /debug/features?address=...&unit_sqft=...&year_built=...` (internal, not part of PLAN.md §10) → building features; 404 if the address can't be geocoded or has no Ann Arbor footprint within 25 m.

CLI, same output: `uv run python -m app.geo.features "912 Mary St, Ann Arbor, MI" [--unit-sqft 850] [--year-built 1965]`

Tests: `uv run pytest -q` (real-address tests skip until the footprint cache exists).

## Address → features (`app/geo/`)

| Step | Module | Source (cached in `../data/`) |
|---|---|---|
| Geocode, 2020 block GEOID | `geocode.py` | US Census geocoder, `geocode_cache.json` |
| Footprint, stories, units | `footprints.py` | City of Ann Arbor BuildingFootprints + MailingAddress FeatureServers (`scripts/fetch_footprints.py`) |
| Median year built | `census.py` | ACS 2020-2024 5-year B25035 via Census Reporter (block group → tract → county), `acs_b25035_washtenaw.json` |
| Assemble ResStock-named dict | `features.py` | ResStock 2024.2 MI baseline category strings |

Only the first lookup of a new address needs the network; everything else is offline.

**How values are derived** (each response also has a `sources` dict):
- **Footprint**: the city's mailing-address point for the address (sits inside the building) if within 250 m of the geocode, else the geocoded point; containing footprint, else nearest within 25 m, preferring footprints that hold a mailing address (houses over garages).
- **Stories** (`in.geometry_stories`, string like ResStock): `STORIES`, else from `ABG_BLD_HG` (feet) with a least-squares fit on the ~15k footprints that have both (≈11.1 ft/story + 1.4 ft; 85% exact, 99% within one story). Then snapped to the nearest ResStock 2024.2 MI category (1–15, 20, 21, 35; ties go down), e.g. Tower Plaza 26 → 21. The unsnapped count is `stories_raw` (and is what `building_sqft` uses).
- **Units / type** (`in.geometry_building_type_recs`): `Struc_Type` is only Residential/Commercial/Office/Public, so the type comes from counting residential ("General Mailing") addresses inside the footprint: 1 → Single-Family Detached, 2–4 → Multi-Family with 2 - 4 Units, 5+ → Multi-Family with 5+ Units. A Residential footprint with no address = 1 unit. Non-residential footprint with no residential address → `null` type and sq ft, plus a warning. **Townhouse rule first** (`townhouse_row()`): a Residential footprint with 2+ residential addresses, each its own house number (2841, 2843, … Hardwick Rd), no `UNIT` rows, ≤ 3 stories → Single-Family Attached (also side-by-side duplexes, as in RECS 2020); `in.sqft` = floor area ÷ townhouses. `sources` says which rule fired. Mobile Home is never produced.
- **Sq ft** (`in.sqft`): footprint area in UTM 17N × stories for houses; for multi-unit: `unit_sqft` if given, else building floor area ÷ units (`sqft_estimated: true`; includes hallways, so it runs high).
- **Vintage** (`in.vintage`): `year_built` if given, else block-group median year built; binned `<1940`, `1940s` … `2010s` (2020+ → `2010s`, ResStock has no later bin).
- **County** (`in.county_name`): `Washtenaw County` (exact ResStock 2024.2 string).

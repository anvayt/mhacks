# House schema (suggestions)

Light suggestions for how to hold house/building data across `/model`, `/api` and `/web`, and how the map widget
pairs LiDAR footprints with street addresses. The reference implementation is `web/scripts/build_map_fixture.py`.

## 1. Sources

| Data | Service (public, no key) | Fields used | Local cache | Created by |
|---|---|---|---|---|
| Building footprints + LiDAR height | `https://a2maps.a2gov.org/a2arcgis/rest/services/OSI/BuildingFootprints/FeatureServer/0` | `OBJECTID, ABG_BLD_HG, Struc_Type, Bldg_Name, PackedPin, STORIES, FacilityID` | `model/data/raw/arcgis/a2_footprints.geojson` (P1 checkout) | `footprints()` → P1's `model.data_sources.arcgis.fetch_all` |
| Mailing addresses | `https://a2maps.a2gov.org/a2arcgis/rest/services/MailingAddress/FeatureServer/0` | `PROPSTREET, TYPE`, point geometry | `web/scripts/.cache/a2_mailing_addresses.json` | `mailing_addresses()` |
| Census block-group outline | TIGERweb `tigerWMS_ACS2023/MapServer/10` | `GEOID`, polygon | none (one request per run) | `block_group()` |
| Block-group year built, heating fuel | ACS 5-year via Census Reporter | B25037, B25035, B25040 | P1's census cache | P1's `estimate_hc` |

All queries ask for WGS84 (`outSR=4326`), page by `resultOffset` in `OBJECTID` order, and cache the raw response.
The city's footprint metadata says the polygons and average heights come from 2009 countywide LiDAR and 2005–08
orthoimagery, updated since then from construction plans and newer imagery. So "LiDAR height" really means
"city-recorded height, originally from LiDAR".

## 2. Regenerating everything

```bash
cd ../mhacks-heating-cooling          # a P1 checkout with trained model artifacts
PYTHONPATH=. .venv/bin/python ../mhacks-map-widget/web/scripts/build_map_fixture.py
```

- If a cache file is missing, it's downloaded: footprints ~23 MB (18 pages of 2,000), addresses 65,138 rows
  (66 pages of 1,000). To refresh, delete the cache file and run again.
- Outputs: `web/public/data/a2-buildings.geojson` (every footprint, for the map) and `web/mocks/map/912-mary-st.json`
  (the selected home's payload).
- The city services return 403 to Python's default user agent, so send a browser-like `User-Agent`.
- Given the same cached inputs, the outputs are identical: the fetches are ordered, and the similar-homes sample
  uses a fixed seed (`seed=0`). The live services do change over time, so record the fetch date if a number
  matters (see §6).

## 3. Pairing LiDAR footprints with addresses (lat/lon, degrees)

Both layers are in WGS84 degrees and are compared in degrees. No projection is needed at this scale.

1. Load every footprint polygon and build a shapely `STRtree` over them.
2. For each mailing-address point `(lon, lat)`:
   - **Inside:** `tree.query(point, predicate="within")`. If it hits, the address belongs to the first footprint returned.
   - **Snap:** otherwise `tree.query_nearest(point, max_distance=ADDR_SNAP_DEG)` with `ADDR_SNAP_DEG = 1.1e-4`.
     Some address points sit a few metres off the roof (P2-01 saw 5–11 m).
   - **None:** otherwise the address is dropped.
3. Normalize to a street line: strip everything after ` UNIT | APT | STE | #`, then title-case words that don't
   start with a digit (`"912 MARY ST UNIT 2"` → `"912 Mary St"`).
4. Per footprint, count street lines. The label is the most common line (`Counter.most_common(1)`; ties go to the
   first one seen, in `OBJECTID` order). `units` is the total count of addresses.
5. The selected home's footprint is the one containing its geocoded point, else the nearest footprint (no distance cap).

**Degree conversions at Ann Arbor (42.28° N).** 1° of latitude ≈ 110,574 m. 1° of longitude ≈ 111,320 × cos(42.28°)
≈ 82,370 m. So `1.1e-4°` is about 12 m north–south and about 9 m east–west: the snap zone is a slightly squashed
circle, which is fine for a hackathon. For a true radius in metres, divide the longitude difference by
`cos(lat)` before measuring.

**Areas** (footprint sq ft) use a local equirectangular projection (`x · 111,320 · cos 42.28°`, `y · 110,574`),
which is within 0.5% across the city.

**Result on the current cache:** 25,994 of 35,007 footprints got an address, including 24,427 of 32,572
Residential ones. Most unmatched residential footprints look like garages and outbuildings.

**Known differences from P2-01** (`api/app/geo/footprints.py`): P2 counts only `TYPE = "General Mailing"` for
units and also uses `... UNIT n` rows on the same street line. This script counts every `TYPE`. Pick one rule
before integration, and run it in one place (§6).

## 4. Suggested data structures

Key buildings by `OBJECTID` **within a dated snapshot**. `FacilityID` (`BLD-001317`) looks stable but isn't unique:
471 values repeat. Keep it and the centroid so footprints can be re-matched after a refresh.

```ts
/** One city footprint: the unit of the map, scoring and leaderboards. */
interface Building {
  id: number;                    // footprint OBJECTID in snapshot `snapshot`
  snapshot: string;              // e.g. "a2_footprints@2026-10-03"
  facility_id: string | null;    // city FacilityID (not unique; for re-matching only)
  parcel_pin: string | null;     // PackedPin
  footprint: GeoJSON.Polygon | GeoJSON.MultiPolygon;
  center: [lon: number, lat: number];
  footprint_sqft: number;
  height_ft: Sourced<number | null>;   // ABG_BLD_HG
  stories: Sourced<number | null>;     // see "floors" below
  structure_type: "Residential" | "Commercial" | "Office" | "Public";
  addresses: string[];           // normalized street lines, most common first
  units: number;                 // count of mailing addresses matched
}

/** One mailing address (one row per unit) and the building it was matched to. */
interface Address {
  street: string;                // raw PROPSTREET, e.g. "912 MARY ST UNIT 2"
  street_line: string;           // normalized, e.g. "912 Mary St"
  type: string;                  // TYPE, e.g. "General Mailing"
  point: [lon: number, lat: number];
  building_id: number | null;
  match: "within" | "snapped" | "none";
}

/** Any value shown to a user carries where it came from (PLAN.md §0). */
interface Sourced<T> {
  value: T;
  source: string;                // human-readable, e.g. "city footprint record (STORIES)"
  kind: "city_record" | "lidar" | "census" | "listing" | "renter" | "model" | "default";
}

/** A home relative to the selected one, e.g. for a ranking. */
interface RankedBuilding {
  id: number;                    // Building.id
  rank: number;
  score: number;                 // whatever the ranking sorts by, with its unit in `rule`
  address: string;
  center: [lon: number, lat: number];
}
```

The map payload (`MapWidgetData` in `components/hidden-rent-map/types.ts`) is a flattened view of these.
`similar.items` would become `RankedBuilding[]` once ranking exists.

**Floors.** The city's `STORIES` is filled in for only 12,430 of 32,572 residential footprints (38%). Where it's
missing, P1 estimates height ÷ 10 ft. Store which one you used in `stories.kind` (`city_record` or `lidar`).
Don't filter on exact floor count, which silently drops 62% of homes; prefer `height_ft` and `footprint_sqft`,
which are present for nearly every footprint.

## 5. Mocks and the switch to the backend

`web/components/hidden-rent-map/data.ts` serves the fixture unless `NEXT_PUBLIC_USE_MOCKS=0`. With it set to `0`,
it calls the proposed `GET /map/{session_id}`. The citywide layer is a static file now (`buildings_url`); later it
should come from P2's `/city`.

## 6. Before this goes beyond the hackathon

- Run the pairing in one place (P2's `/api` data pipeline) and have `/web` only read its output.
- Write a small manifest next to each cache: service URL, query, fetch time, record count, sha256.
- Keep the snap distance in metres, not degrees.
- Add a test with known pairs, e.g. 912 Mary St → footprint 1317 (`BLD-001317`), 23.7 ft.

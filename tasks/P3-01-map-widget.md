```yaml
id: P3-01
title: Map widget that explains the data science to a layman (LiDAR building, census block, ResStock answers)
owner: P3
status: review
branch: p3/map-widget
type: build
checkpoint: 5:00 AM checkpoint
depends_on: [P2-04]                # real data comes from /api later; built against a fixture from P1's model
blocks: []                         # a later P3 task integrates it into the report-card flow
merges: []
services_touched:
  - /web
services_read:
  - /model (P1, branch p1/heating-cooling): estimate_hc, resstock_frame.parquet, cached footprints
  - Census TIGERweb block-group outline (external, no key; fetched once by the fixture script). No leakage-model data.
  - OpenFreeMap positron basemap (external, no key)
contract_change: additive          # proposed GET /map/{session_id}; see notes/contract-changes.md
```

## Goal
A standalone React/TypeScript component, `<HiddenRentMap>`, that lets a renter who has never heard of regression see
*why* their estimate is what it is: the building measured by LiDAR, the census block it sits in, and how each survey
answer narrows the comparison against ResStock's simulated Michigan homes. Built in isolation; integrated into the app later.

## Inputs (what I can rely on)
- No backend endpoint yet. `web/mocks/map/912-mary-st.json` is built from **real** pipeline outputs by
  `web/scripts/build_map_fixture.py` (P1's `estimate_hc`, ResStock frame, city footprints with LiDAR height,
  ACS block group). Nothing is typed in by hand.

## Outputs (what I expose)
- `web/components/hidden-rent-map/`: `HiddenRentMap`, `getMapWidgetData(sessionId)`, `demoMapData`, and the
  `MapWidgetData` type (`types.ts`), which is the payload shape the backend should serve.
- Preview page: `/dev/map` (`?chapter=building|block|answers&step=0..3`).

## Steps
- [x] Fixture builder from P1's model and cached public data (every number traceable to a source)
- [x] MapLibre 3D map: unit extruded to LiDAR height among real neighbor footprints; dashed block-group outline; camera per chapter
- [x] Chapter 1 "The building": LiDAR height, footprint × floors ≈ floor area, unit size, in plain words
- [x] Chapter 2 "The block": census median year built vs Michigan's 1977 energy code timeline; gas/electric split → the assumption we start from
- [x] Chapter 3 "Your answers": look-alike homes as dots that fade as answers rule them out; middle-8-in-10 bar; estimate marker; season bars; per-answer $ change and home count
- [x] Controlled or uncontrolled `chapter` / `step` props for integration; keyboard tabs; `aria-live` readout; reduced-motion; WebGL fallback text
- [x] Typecheck + `next build` pass; Playwright click-through of all three answers

## Done when
- [x] `/dev/map` renders all three chapters with the fixture; answering 3 questions narrows 218 → 29 look-alike homes
- [x] Single switch for mocks (`NEXT_PUBLIC_USE_MOCKS`, default on)
- [x] No secrets; every displayed number comes from the fixture's cited sources (sources panel in the widget)

## Handoff (DEV_STRATEGY #1)
- **What changed (all in /web, branch `p3/map-widget`):** `components/hidden-rent-map/`: `HiddenRentMap` (map-only
  widget), `MapStory` (facts, look-alike dots, questions; goes **below** the map), `MapCanvas`, `LookalikeStrip`,
  `types.ts`, `data.ts`, `format.ts`, CSS module, `index.ts`. `app/dev/map/{page,preview}.tsx` (preview with a
  hover-test address list). `mocks/map/912-mary-st.json`, `public/data/a2-buildings.geojson` (all 35,007 city
  footprints with LiDAR height + matched mailing address, 10 MB), `scripts/build_map_fixture.py`, `HOUSE_SCHEMA.md`.
  Deps: `maplibre-gl@5`, `@types/geojson` (dev).
- **The map:** opens on all of Ann Arbor; views City / Similar / Block / Building. Every footprint is drawn in 3D at
  its height; the selected home is always highlighted (cost colour + pin); `similar.items` are shown as dots with
  links back to the selected home. Hover is two-way: `highlightId` in, `onHoverBuilding(id)` out (address tooltip).
- **Use it:** `<HiddenRentMap data step focus onFocusChange highlightId onHoverBuilding />` and, under it,
  `<MapStory data step onStepChange onFocus />` (see `app/dev/map/preview.tsx`). Data: `getMapWidgetData(sessionId)`.
- **Rebuild data:** `web/HOUSE_SCHEMA.md` §2 (one command from a P1 heating-cooling checkout; missing caches are
  downloaded). Sources, address↔footprint pairing (degrees) and suggested types are in the same file.
- **Mocks still to replace:** fixture while `NEXT_PUBLIC_USE_MOCKS` ≠ `0`; otherwise `GET /map/{session_id}`
  (proposal, notes/contract-changes.md). The citywide layer should move to P2's `/city`.
- **Known gaps:** `similar.items` is a labelled random test sample, not a ranking. Address matching counts every
  `TYPE` (P2-01 counts only "General Mailing"); pick one rule. `STORIES` exists for only 38% of residential
  footprints. The basemap is fetched live from OpenFreeMap. No leakage-model data is used.
- **Who acts next:** P2 (`/map/{session_id}`, `/city`), P1 (look-alike cloud), P3 (integrate into the report card).

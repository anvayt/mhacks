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
- **What changed (all in /web):** `components/hidden-rent-map/{HiddenRentMap,MapCanvas,LookalikeStrip}.tsx`,
  `types.ts`, `data.ts`, `format.ts`, `hidden-rent-map.module.css`, `index.ts`; `app/dev/map/page.tsx`;
  `mocks/map/912-mary-st.json`; `scripts/build_map_fixture.py`. Deps: `maplibre-gl@5`, `@types/geojson` (dev).
- **Use it:** `import { HiddenRentMap, getMapWidgetData } from "@/components/hidden-rent-map"`, then
  `<HiddenRentMap data={await getMapWidgetData(sessionId)} />`. For the interview flow, drive it with
  `step` / `onStepChange` (0 = public record only; step *i* = after *i* answers) and `chapter` / `onChapterChange`.
  It fills its parent's height (min 640 px; stacks under 860 px wide).
- **Rebuild the fixture:** see the docstring in `web/scripts/build_map_fixture.py` (runs with P1's venv, ~6 s, offline).
- **Mocks still to replace:** `data.ts` returns the 912 Mary St fixture while `NEXT_PUBLIC_USE_MOCKS` ≠ `0`. With it
  set to `0`, it fetches `GET {NEXT_PUBLIC_API_BASE_URL}/map/{session_id}`. That endpoint is a **proposal**
  (notes/contract-changes.md) and doesn't exist yet.
- **Known gaps:** the demo plays canned answers (each step's `answer_label`); in the real flow, `steps` should grow
  from `/answer` responses. The look-alike filter is the PLAN §6.2 question-picker idea, done in the fixture script;
  P1 should own it (notes/requests.md). The basemap is fetched live from OpenFreeMap, which the offline demo may need cached.
  Multiset dot-matching across steps needs the step-0 cloud unsampled (≤ 400 homes); otherwise it shows the current step only.
- **Who acts next:** P2 (serve `MapWidgetData`), P1 (expose the look-alike cloud), P3 (integrate into the report card).

# API contract changes
<!-- - proposal (none|additive|breaking), proposer, acks: P1 [ ] P2 [ ] P3 [ ] P4 [ ] -->
- **additive**, P3 (P3-01 map widget), acks: P1 [ ] P2 [ ] P3 [x] P4 [ ]
  - New `GET /map/{session_id}` → `MapWidgetData` (shape in `web/components/hidden-rent-map/types.ts` on `p3/map-widget`; example `web/mocks/map/912-mary-st.json`).
  - Contents: building footprint + LiDAR `height_ft` + stories/floor area/unit size (each with a source); ~160 m of neighbor footprints with `height_ft`; block-group polygon + ACS median year built + gas/electric heat shares; `steps[]` (public record, then one per answered question), each with P1's estimate (annual + seasons + typical error) and the look-alike cloud (`count`, sorted `usd_yr` sample ≤ 400, p10/p50/p90); `sources[]`.
  - Nothing in §10 changes; the widget just reads more.
- **additive**, P2 (integration, dev `4602d55`), acks: P1 [ ] P2 [x] P3 [ ] P4 [ ]
  - `POST /estimate` request: optional `unit_sqft` (100–10,000, otherwise 422 `bad_unit_sqft`).
  - Response: `building.address`, `building.sqft_estimated`, `building.year_built_source`, `bill.seasonal{winter,spring,summer,fall}`, `bill.covers` (heating + cooling only), `heating_cooling` (P1's full `estimate_hc` answer).
  - Errors: 422 `{detail:{code,message}}` with codes `missing_input`, `needs_address` (+`hint`), `not_found`, `not_a_home`, `bad_unit_sqft`; 503 `model_unavailable` / `lookup_unavailable`.
  - Fields with no source yet are null or empty: `session_id`, p10/p90, `co2_t`, score/grade/percentiles/`hidden_rent_usd_mo`, `badges`, `questions` (filled by P2-03 and P2-04).

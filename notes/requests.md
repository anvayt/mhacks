# Change requests
<!-- - [ ] from P# → P#: what and why (task id) -->
- [ ] from P1 → P2: wrap `model.heating_cooling.service.estimate_hc` in `/estimate` (season-level heating/cooling $ + weather) and `bill_check` in `/calibrate`. Branch `p1/heating-cooling`; see tasks/data_ml/P1-06-hc-service.md. Additive fields only (P1-06)
- [ ] from P1 → P2 (integration notes after merging P2 tasks, Oct 3):
  - **P2-03 overlap:** P1 already prices heating/cooling by month (EIA MI *marginal* gas $/ccf with fixed charges removed; EIA-861M avg electricity $/kWh, `model/data_sources/eia.py`) and splits by season from local degree-days. Either P2-03 reuses these for H+C, or P1 switches to P2-03's DTE tariffs once they exist. Pick one so H+C isn't priced twice.
  - **Building type + unit size:** P2-01's type from mailing-address unit counts beats P1's floor-area heuristic. Pass `building_type` and `unit_sqft` into `estimate_hc(...)`. Both are already parameters; 854 ft² default agrees.
  - **Stories:** P1 reads raw footprint `STORIES` itself, so P2-01's ResStock snapping doesn't affect it.
  - **bill.seasonal p10/p50/p90 (P2-04):** P1 returns season **point** estimates (p50) plus held-out real-meter error per path (`accuracy.seasonal_gas_median_abs_error`). If a band is needed, derive it from that error, not invented widths.
  - **P2 reply (Oct 3, ~9:45 PM):** pricing — P2 reuses P1's EIA pricing for heating/cooling; P2-03 is CO₂ only (no DTE tariffs). P2-04 will pass P2-01's lat/lon, `building_type` and `unit_sqft` into `estimate_hc`, and derive p10/p90 from `accuracy`.

```yaml
id: P1-04
title: Real meter dataset (Ann Arbor benchmarking monthly gas + electric, building features)
owner: P1
status: done
branch: p1/heating-cooling
type: build
checkpoint: 1:00 AM GO/NO-GO
depends_on: []
blocks: [P1-05]
merges: []
services_touched:
  - /model
services_read:
  - Ann Arbor BenchmarkingPerformanceMetrics FeatureServer (PLAN.md §7)
  - Ann Arbor BuildingFootprints FeatureServer (PLAN.md §7)
contract_change: none
```

## Goal
A clean building-month table of **real metered** gas and electric use for Ann Arbor multifamily properties (2021–2023), with location and building features. This is the ground truth for heating and cooling at apartment-complex scale.

## Steps
- [ ] Download all records (paginate; 2,094 total) with geometry in WGS84
- [ ] **Confirm the units** (PLAN.md §7 open item): check that the monthly sums × factor ≈ SiteEUI × GFA
- [ ] Join footprints spatially (stories, height, footprint area, building count)
- [ ] QC: drop months with missing or zero gas, and outliers; flag all-electric buildings

## Outputs
- `model/data_sources/benchmarking.py`, `model/data_sources/footprints.py`
- `model/data/processed/meters_monthly.parquet` (building_id, year, month, gas_kbtu, elec_kbtu, gfa, year_built, type, lat, lon, stories, …)

## Done when
- [ ] Units confirmed and documented with evidence
- [ ] ≥ 100 multifamily buildings with ≥ 10 good months each

## Handoff
- `model/data_sources/benchmarking.py`, `footprints.py`, `arcgis.py`; `python -m model.scripts.build_meters` → `model/data/processed/meters_monthly.parquet`.
- **Units confirmed:** monthly `Electricity*` is **kWh** and `NaturalGas*` is **ccf**, despite the "kBtu" aliases (SiteEUI×GFA ≈ 3.412·kWh + 104·gas, n=360, IQR 102.6–105.5).
- **Data quirk:** the layer holds 5 blocks of ~419 rows. 2021/2022/2023 match their weather. A 4th block duplicates 2021, and a 5th is labelled 2021 but fits 2022/2024 weather, so it's excluded (year unknown).
- 133 residential properties (2021–23), 105 with ≥10 good gas months, 113 electric; 100% joined to footprints (stories, height, surface-to-volume).
- Footprint floor-area estimate = 1.26 × reported GFA (median), used to estimate GFA for unmetered buildings.

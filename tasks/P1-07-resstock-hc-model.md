```yaml
id: P1-07
title: ResStock heating/cooling per-degree-day model with renter answers (small buildings + cross-check)
owner: P1
status: in-progress
branch: p1/heating-cooling
type: build
checkpoint: 1:00 AM GO/NO-GO
depends_on: [P1-02, P1-03, P1-05]
blocks: [P1-06]
merges: []
services_touched:
  - /model
services_read:
  - NREL ResStock 2024.2 MI (cached by P1-02)
contract_change: none
```

## Goal
Ann Arbor's meters only cover properties of 10,000 ft² and up. This task covers houses, duplexes and small apartment buildings by learning heating and cooling **per degree-day** from 18,756 simulated Michigan homes. Local weather rescales the estimate, and renter answers sharpen it. It's calibrated to real meters where the two datasets overlap (multifamily).

## Rules (grounding)
- Inputs are only things a renter can know before signing: window panes, floor level, foundation, cooling type, occupants. Air leakage, insulation R-values and furnace efficiency stay hidden; they are used only in `leakage_analysis.py`, and those results are labelled simulation.
- Multifamily calibration factors come from real meters (`model/results/resstock_hc_validation.json`).

## Done when
- [x] `model/hc/resstock_model.py` trained: gas heating median APE 0.25 → 0.21 with answers; cooling 0.38 → 0.32
- [x] Calibration to meters: heating ×1.14, cooling ×0.63 (multifamily)
- [x] Leakage question answered (`model/hc/leakage_analysis.py`)
- [ ] ResStock monthly timeseries check of the degree-day seasonal split (NREL per-building timeseries, sample of Washtenaw homes)

## Handoff
- See P1-05/P1-06 handoffs; results in `model/results/resstock_hc_validation.json` and `leakage_analysis.json`.

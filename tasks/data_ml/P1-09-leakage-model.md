```yaml
id: P1-09
title: Air-leakage (blower-door) model for Ann Arbor homes without a test
owner: P1
status: in-progress
branch: p1/leakage-model           # off p1/heating-cooling (needs its building features); worktree ../mhacks-leakage
type: build
checkpoint: 5:00 AM checkpoint
depends_on: [P1-06]                # heating-cooling interface (footprints, building features, climate)
blocks: []
merges: []
services_touched:
  - /model                         # new: model/leakage/ (does not change the heating/cooling service)
services_read:
  - NYSERDA Residential Statewide Baseline Study, Single-Family On-Site Inspections (data.ny.gov 8wa7-87p5, public, no key)
  - NYSERDA Residential Building Stock Assessment 2018 On-Site (data.ny.gov 3drn-bhzv, public zip)
  - LBNL ResDB: raw data is NOT public (contact-only). Use only its published regression/summary results, and request access.
  - NEEA RBSA 2022: registration + no-redistribution terms. Out of scope unless a human registers.
  - NREL ResStock 2024.2 MI (simulated infiltration; prior/comparison only, never a test set)
  - model.heating_cooling (footprints, ACS year built, climate) for Ann Arbor features
contract_change: none
```

## Goal
Predict a home's air leakage (blower-door result: ACH50 or CFM50 per ft²) from information available for **any** Ann Arbor
house without a test, and estimate how well that generalizes. Inputs are public-record / footprint features from the
heating-cooling interface (year built, floor area, stories, LiDAR height/volume, footprint shape, climate). The output is a
point estimate per house plus an honest held-out error.

## Rules
- **Real measurements only as ground truth.** Blower-door tests from public datasets. Simulated leakage (ResStock) can be
  a baseline or prior but is never a test target.
- **No landlord / renter survey answers as inputs.** Evaluation must use only features that exist for every Ann Arbor
  house (no window panes, no foundation answer, no "drafty?" answer).
- **Rigor** (same standard as P1-05): log target; tuning by inner CV on the reported metric; outer CV measures only;
  baselines (median, published ResDB regression if reproducible); one-SE rule.
- **Generalizability is the test.** Grouped CV by region/county (homes from held-out regions), plus a cross-dataset test
  (train on one survey, test on the other) when both have usable leakage. Report the gap vs random CV.
- **Features must be computable for Ann Arbor houses.** Dataset-only fields (siding colour, survey answers) can be used
  for analysis, never in the served model.

## Steps
- [ ] Download and cache the NY datasets; harmonize leakage units (CFM50, ACH50, test type), clean, document exclusions
- [ ] Check the ResDB publications for a reproducible published regression (coefficients) to use as an external baseline
- [ ] Feature map: NY fields ↔ Ann Arbor-available features (year built, conditioned area, stories, ceiling height → volume, climate)
- [ ] Model families: baseline median, median/linear regressions (lasso, ridge, elastic net), RF, XGBoost, small neural net (MLP); nested CV, grouped by region
- [ ] Cross-dataset generalization test; ResStock-prior comparison
- [ ] Apply to Ann Arbor houses (footprints + ACS/benchmarking year built) → table + `predict_leakage(...)`
- [ ] Results JSON + README section; handoff

## Done when
- [ ] Held-out (grouped) error reported for every family vs the baseline, with the chosen model and its settings
- [ ] `model/leakage/` predicts leakage for an Ann Arbor lat/lon or address using only public features
- [ ] Honest statement of applicability: dataset region/era/house types vs Ann Arbor rentals

## Handoff

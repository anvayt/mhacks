```yaml
id: P1-05
title: Heating + cooling energy and cost model (seasonal, building-level)
owner: P1
status: review
branch: p1/heating-cooling
type: build
checkpoint: 1:00 AM GO/NO-GO
depends_on: [P1-02, P1-03, P1-04]
blocks: [P1-06]
merges: []
services_touched:
  - /model
services_read:
  - EIA Michigan monthly residential gas + electric prices (no key: hist_xls / EIA-861M)
contract_change: none
```

## Goal
For any building location, return **point estimates of heating and cooling energy and cost per season**, grounded in real meters.

## Method
1. **PRISM (Princeton Scorekeeping Method) per building:** fit a change-point model `use = base + βh·HDD(τh) + βc·CDD(τc)` to monthly gas and electric use. Heating = the HDD part of gas. Cooling = the CDD part of electric.
2. **Cross-building models** (to predict buildings with no meters): multiple linear regression, random forest and XGBoost on building-month rows. Features: weather (HDD/CDD/tmean from P1-03) + building (year built, GFA, stories, footprint, type). Targets: gas and electric intensity per sq ft per month. Use **group k-fold by building** and report held-out error.
3. Heating = predicted gas − predicted baseload (the same model at HDD=0). Cooling = predicted elec − elec at CDD=0.
4. Dollars: EIA Michigan monthly residential prices (cite them). Per-unit = building × unit sq ft / GFA.
5. ResStock (P1-02) heating/cooling intensities as the fallback and sanity check for small buildings.

## Outputs
- `model/hc/train.py`, `model/hc/predict.py`, artifacts in `model/artifacts/` (git-ignored except small JSON)
- `model/results/hc_validation.json` (held-out R², MAE, per model)

## Done when
- [ ] Held-out metrics for MLR vs RF vs XGBoost reported; the best one is chosen
- [ ] Seasonal heating/cooling $ for 5 real Ann Arbor complexes look plausible vs RECS/EIA

## Handoff
- Code: `model/hc/changepoint.py` (PRISM scorekeeping fits), `model/hc/train.py` (monthly-panel MLR/RF/XGBoost, kept for comparison), `model/hc/building_model.py` (building-level, used in serving).
- **Metered buildings:** per-building change-point fits on real meters: gas median R² **0.961** (n=108), CV(RMSE) 0.13. Out-of-year test (fit 2 yrs, predict the 3rd): annual gas median error **4.2%** (p90 15%).
- **Unmetered ≥10k ft²:** building-level models, repeated 5-fold CV. Heating: MLR median APE **0.34** vs 0.42 null. Cooling: RF 0.40 vs 0.41 null, so features barely help cooling. Honest limit: building-to-building spread is ~3× within the same vintage.
- Prices (`model/data_sources/eia.py`): gas = EIA MI **marginal** $/ccf by month (revenue~volume regression, R² 0.99, fixed charges removed). Electricity = EIA-861M average $/kWh by month (the marginal fit isn't identifiable because of seasonal rates).
- Results: `model/results/hc_validation.json`, `building_model_validation.json`, `leakage_analysis.json`.

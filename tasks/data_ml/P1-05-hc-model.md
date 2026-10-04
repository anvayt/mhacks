```yaml
id: P1-05
title: Heating + cooling energy and cost model (seasonal, building-level)
owner: P1
status: done
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
- `model/heating_cooling/train.py`, `model/heating_cooling/predict.py`, artifacts in `model/artifacts/` (git-ignored except small JSON)
- `model/results/hc_validation.json` (held-out R², MAE, per model)

## Done when
- [ ] Held-out metrics for MLR vs RF vs XGBoost reported; the best one is chosen
- [ ] Seasonal heating/cooling $ for 5 real Ann Arbor complexes look plausible vs RECS/EIA

## Handoff
- Code: `model/heating_cooling/changepoint.py`, `train.py` (monthly panel, for comparison), `building_model.py` (served), `validate.py`.
- Metered: gas median R² 0.961 (n=108). Out-of-year annual error 4.2%; seasonal 7.4%.
- Unmetered ≥10k ft²: blend of the ridge/MLR heating model + calibrated ResStock = **28.3%** seasonal median error on held-out real buildings (null 35.4%). Cooling is weak (features ≈ median).
- Prices: EIA MI marginal gas $/ccf by month (R² 0.99); EIA-861M average electricity $/kWh by month.
- Results: `model/results/{building_model_validation,hc_validation,validation_real,leakage_analysis}.json`.

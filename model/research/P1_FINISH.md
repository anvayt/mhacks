# P1 finishing pass: additive capabilities

Worktree `mhacks-p1`, model port 8011, API port 8061. The live model checkout and service are not modified. Built artifacts, processed data, results, raw/weather caches and the Python environment were copied from `mhacks-integration`; no cold rebuild is run. Tracked derived files on this branch therefore reflect that copied live build, rather than a different historical training. See `results/finish/source_copy.json` for hashes.

## Bill noise and signed errors

Existing `/hc/bill_check` requests retain their old numbers. New clients discover `/hc/capabilities` and opt in with `noise_basis=within_building`. `/api/calibrate` negotiates that option; an old model without capabilities keeps the old behavior. `estimate_error_floor` always retains the former floor, with `noise_basis` and `noise_detail` explaining the new one. Fractions at the model layer become percentages in `/calibrate`.

The new temporal error is `actual / prediction - 1`, matching the direction of the bill comparison. Prediction is each metered building's change-point fit using only its other calendar years. We refitted all **1,985** saved gas month predictions and reproduced them exactly (maximum absolute difference **0 ccf**). Source: `results/uncertainty_additive.json`, `out_of_year_audit`; calculation: `heating_cooling/uncertainty.py` from the copied `meters_weather.parquet` and `heldout_monthly.parquet`.

The winter p90 absolute residual is **25.1584%**, from **514 months / 67 buildings**. Spring **35.7275%**, summer **49.2151%**, fall **41.4256%** (same JSON, `within_building_gas.by_season`). No threshold was chosen to make a demo bill pass. This is pooled temporal variability; on unmetered paths it is a transferred component, **not** validation of that particular home's baseline or removal of cross-building bias. Month rows are repeated observations within properties, not independent homes. Meaningful is an anomaly flag, not causal attribution to an intervention.

The old winter floors are **16.4% metered, 92.5% blend and 118.3% ResStock** in this copied live build (`results/validation_real.json`). In particular, the new temporal floor is higher on the metered path: monthly variability should not be confused with an aggregated seasonal error. Zero or negative-use/invalid prediction rows are excluded as documented in the script.

`accuracy.signed_error_quantiles` is additive and leaves the API's current band calculation alone. It reports signed empirical p10/p50/p90 by path, fuel and season/calendar month. Its definition is `prediction / actual - 1` (positive means overprediction). To derive actual-use bounds from this definition requires inversion and reversing quantiles, not simply multiplying by `(1 + error)`. These are errors in total utility meters, not certified heating/cooling-only coverage guarantees.

Each model month also adds `heating.usd_exact` and `cooling.usd_exact`, before rounding; original rounded fields are unchanged.

Reproduce the uncertainty tables without downloading or rebuilding models:

```bash
.venv/bin/python -m model.heating_cooling.uncertainty
.venv/bin/python -m pytest model/tests/test_uncertainty.py -q
```

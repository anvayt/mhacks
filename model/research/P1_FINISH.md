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

## Effects and clouds

`/hc/capabilities` advertises supported params and path/fuel/building-type restrictions. Optional effects compose as remaining-load factors, followed by one delivered-heat fuel conversion. Defaults are unchanged. Source details, simulation holdout and the worked Morton example are in `results/EFFECTS.md` and `results/effects_example_morton.json`. The user approved preserving physical heat-pump prices when a cost-increasing fuel switch violates dollar subadditivity; load-reduction-only scenarios still satisfy subadditivity. Never cap a physical bill to manufacture savings.

Metered and electric paths keep new effects as placeholders. Multifamily/mobile roofs have no supported attic combinations in this stock, including top-floor units; R-50 on supported single-family attic cohorts uses R-49 training support, with attic presence explicitly assumed. A behavior-only thermostat setback receives no smart-device rebate or GRH equipment points. Professional whole-home air sealing is distinguished from renter weatherstripping.

`/hc/lookalikes` supplies simulated same-type, rented Michigan peers filtered by era, size and supplied answers, priced with the address's existing weather and EIA prices. It returns actual full-pool counts and quantiles plus a sorted display sample capped at 400. `/map` uses capability discovery and caches answer-prefix clouds; old servers retain the honest empty response. These are simulations, not measured nearby homes or calibrated uncertainty bands.

`year_built` overrides the prior when provided; `cooling_code=0` yields zero cooling with heating computed exactly as if the cooling answer were omitted. This fixes the explicitly requested formerly out-of-distribution no-AC input. Existing API requests already omit that code, preserving their baseline numbers.

## Live acceptance evidence

`results/finish/live_smoke.json` and `.log` were recorded by `scripts/finish_smoke.py` against isolated ports 8011/8061. The actual API's Morton footprint estimate is **2,753 ft²**, distinct from the separate 1,500-ft² worked scenario in `effects_example_morton.json`. After gas + single-pane answers its annual heating/cooling estimate is **$2,185, grade C**.

| Morton action | Before | Projected annual bill | Annual savings |
|---|---|---:|---:|
| Professional whole-home air sealing | placeholder | $1,967 | $218 |
| Accessible attic R-50 (modeled at R-49) | placeholder | $2,075 | $110 |
| Wall insulation | placeholder | $1,785 | $400 |
| Gas-to-heat-pump | placeholder | $3,837 | **−$1,652** |
| Behavior-only thermostat setback | placeholder | $2,133 | $52 |
| Four load reductions together | unavailable | $1,506 | $679 |
| All five including heat pump | unavailable | $2,544 | **−$359** |

Source for every cell: the live smoke JSON's `morton_answers`, `morton_suggested` and `morton_projection_*`. These are projected model outputs, not realized savings. Load reductions alone save $679 versus $780 summed individually. The cost-increasing fuel switch has the user-approved physical dollar interaction documented above; no artificial cap is imposed. Current grade/bill is unchanged by projections.

A **hypothetical typed 80-therm February 2026 bill** is **77.3% below** this model's weather-normal expectation. Legacy floor **118.3% / meaningful false** becomes temporal floor **25.2% / meaningful true**; `estimate_error_floor` keeps 118.3%. Source: `morton_calibrate`, `morton_bill_legacy`, `morton_bill_within`. This is an anomaly demonstration, not proof that an intervention worked or an actual utility record.

Morton's map has **34 → 32 → 17** simulated peers (public record → gas → single pane); final p10/p50/p90 are **$1,530 / $2,448 / $3,631**. Source: `morton_map.steps`. Arrowwood selects `metered` and all new commitments remain honest placeholders. An empty genuine peer cohort remains empty; the current web's generic empty copy still says pending model data.

Legacy compatibility: **75/75** endpoint comparisons pass for five demo addresses plus 20 deterministic city samples, across `/hc/estimate`, `/hc/bill_check`, `/hc/weather` (`results/finish/compatibility.json`). Old numeric JSON tokens, including representation, match; additive fields are allowed. The current input contract's explicit new no-AC behavior is tested separately. Sign-off reproduces all source predictions with zero observed drift and corrects the stale blend headline to **29.2%**; see `results/SIGNOFF.md`.

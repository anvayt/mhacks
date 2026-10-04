# Opt-in commitment effects

These are projected scenarios, never verified savings, new baseline measurements, or observed insulation at an address. Existing requests do not run this code. The existing baseline artifacts are unchanged.

## Evidence and limits

`effects_envelope.json` is a separate, small monotone log-linear heating-intensity surrogate fitted to the **13,380 gas-heated Michigan ResStock 2024.2** simulations with complete inputs. A fixed random 80/20 split (seed 20261004) leaves **2,676** test homes: log-intensity R² **0.6773649284**, median absolute percentage error **21.51357066%**. Those numbers come from `python -m model.heating_cooling.train_effects` and validate prediction on simulated baseline homes, **not causal retrofit effects**. No real before/after retrofit validation is available.

The processed input SHA256 and raw ResStock input SHA256 are recorded in the JSON. Public attributes, window panes, foundation, floor level, roof insulation, and attic type are control variables; the effect variables are ACH50, ceiling R, wall R, and heating AFUE. Including roof insulation and attic type matters: a ceiling value of zero in the processed frame often means *no attic*, not an uninsulated attic. The extra controls come from aligned rows in the copied raw baseline file. No new baseline model was trained.

Raw gas-stock attic counts (from the copied raw ResStock `in.geometry_attic_type`, recorded in `effects_envelope.json`) show **778** 2–4-unit, **1,619** 5+-unit and **675** mobile homes, all with attic type `None`. A top-floor answer does not create counterfactual support. Single-family detached has **6,560 vented**, **426 unvented**, **245 finished/cathedral**, and **3,220 None**; attached has **323 vented**, **39 unvented**, **26 finished/cathedral**, and **430 None**. Only vented/unvented homes establish accessible-attic support and baseline R. Each selected vintage cohort must contain at least 30 such homes. The complete-input fitting sample is smaller for multifamily (443 and 993 homes), so the artifact stores raw and training counts separately. `None` and finished/cathedral configurations are never treated as uninsulated attics in the effect baseline.

For each address, baseline hidden variables are the median of gas simulations of its building type and a ±20-year vintage cohort around the nearest decade, with at least 30 simulated homes; otherwise the whole type is used. These are explicit stock assumptions. They are not inspection results, blower-door tests, or hidden values inferred from a bill. The ±20-year/30-home rules and the tiny fixed regression ridge (0.0001 coefficient penalty) are analyst choices recorded in the training code.

| Input | Scenario, source and limitation |
|---|---|
| `air_sealing=true` | ACH50 × 0.75, bounded by the training minimum. [EPA ENERGY STAR's modeling assumptions](https://www.energystar.gov/saveathome/seal_insulate/methodology) use a 25% infiltration reduction; [NREL/TP-5500-85625](https://www.nrel.gov/docs/fy24osti/85625.pdf) reports 25–30% conventional leakage reductions. This means professional whole-home sealing; it is **not** an effect estimate for renter-only weatherstripping. |
| `attic_r=50` | Hold other inputs fixed and raise ceiling insulation. The [ResStock 2024.2 source](https://data.openei.org/s3_viewer?bucket=oedi-data-lake&prefix=nrel-pds-building-stock%2Fend-use-load-profiles-for-us-building-stock%2F2024%2Fresstock_tmy3_release_2%2F) supports R-49, so R-50 is represented conservatively as R-49 rather than extrapolated. Assumes an accessible attic. Only single-family attached/detached types have supported vented/unvented attic cohorts. Multifamily and mobile homes remain placeholders even with a top-floor answer. The baseline ceiling R is the median only among actual vented/unvented attics in that cohort; actual attic presence at the requested home is still an explicit, unconfirmed assumption. |
| `wall_insulated=1` | Raise wall R to the positive-insulation median of the same stock cohort (never remove existing insulation). Target R and baseline R are returned. Source is the same ResStock input. |
| `heat_pump=true` | Convert **remaining gas heat** to delivered heat: `ccf × (103.7 / 3.412) × AFUE / COP` gives heating electricity in kWh. AFUE is the ResStock cohort median, not an inspected furnace. COP **2.75** is the engineering assumption in [Consumers Energy's 2021 Michigan cold-climate evaluation, Appendix B Table B-4](https://www.michigan.gov/mpsc/-/media/Project/Websites/mpsc/workgroups/EWR_Collaborative/2023/2021CI-and-Res-CCHP-Initiatives-Comprehensive-Evaluation-20220826.pdf), not a measured Michigan-wide seasonal mean. [DOE/NREL slide 5](https://www.energy.gov/sites/default/files/2021-09/2-Tom-ASHP.pdf) defines delivered-heat COP; [NEEP's product-list discussion](https://neep.org/blog/checking-neep-ccashp-product-list) gives cold-climate performance context. The conversion uses the same EIA heat-content constants and monthly EIA prices as the existing service. Assumes all heating is displaced; no equipment sizing, backup, ducts, or cooling improvement is modeled. It is **not resistance-heat pricing**. |
| `setpoint_delta_f=-2` | An eight-hour/day setback from an assumed 68°F; clamp to the project's 64°F floor. [DOE's February 2024 guidance](https://content.govdelivery.com/accounts/USEERE/bulletins/3883189) supplies the 68–70°F occupied starting point and eight-hour setback context. The floor follows the existing project's rounded interpretation of [WHO Housing and health guidelines, 2018](https://www.who.int/publications/i/item/9789241550376). Interpolate monthly HDD55/HDD60 to a lower heating balance point and apply one-third of that load reduction. This is an explicit load-share approximation, not a learned thermostat intervention. Rebound and heat-pump backup are absent. |

All new effects currently support **gas, unmetered** paths only. `metered` requests retain their baseline and return a reason in `effects.not_modeled`: measured energy cannot identify that property's envelope or validate a retrofit response. Electric homes retain the existing separately supported behavior; this module makes no new electric-envelope claim. Unknown/invalid parameters return a placeholder reason. Cooling and non-heating gas remain unchanged.

## Composition

Heating demand factors multiply once; gas-to-heat-pump conversion occurs after the combined remaining load, once. This gives subadditive heating-load savings and, when all interventions reduce the same energy cost, subadditive dollar savings. Dropping a parameter restores that effect because every request begins from the original baseline. There is no mutable projected-state cache.

**A universal dollar sum-of-parts cap is physically wrong when a heat pump increases the price of delivered heat.** Envelope work then saves more dollars under the expensive fuel. This interaction is reported rather than hidden with an invented cap. The model can therefore show a gas heat pump increasing the bill; clients must preserve the sign. No heating fuel is converted a second time, and cooling is not repriced as resistance heat.

## Reproduction

From an isolated checkout with copied baseline data and its matching environment:

```bash
.venv/bin/python -m model.heating_cooling.train_effects
.venv/bin/python -m pytest model/tests/test_effects.py -q
```

`effects_example_morton.json` records a 1,500-ft² single-pane, gas-heated 1514 Morton Ave scenario using the copied baseline, city/Census and weather caches. Its example was computed directly in-process with all outbound requests explicitly disabled; no server on :8001 was contacted. It includes exact per-effect assumptions, rounded annual output and dollar differences. The root integration report supplies endpoint examples after routing these inputs through the isolated :8011 server.

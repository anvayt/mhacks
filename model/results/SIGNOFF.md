# P1 copied-artifact validation sign-off

Generated 2026-10-04T12:14:32.266030+00:00; PASS in 2.838 seconds. Machine-readable evidence: [finish/signoff.json](finish/signoff.json); command output: [finish/signoff.log](finish/signoff.log).

## Reproduction and scope

From this checkout's repository root:

```bash
.venv/bin/python -m model.scripts.signoff > model/results/finish/signoff.log
```

This audit **recomputed predictions**, not only the displayed summaries: `validate.heldout_rows("gas")` and `heldout_rows("elec")` regenerate held-out monthly/seasonal predictions in memory using the copied ResStock artifact, saved nested-CV meter-model OOF predictions, copied meter targets/weather and other-calendar-year change-point refits. Fold calibration, baseload, null and blend predictions are recalculated. Saved baseline regressors are not retrained. Every numeric prediction column is compared to its saved parquet with rtol=1e-12 and atol=1e-8; rounded published summaries must match exactly. It never calls `validate.main`, `seasonal_check`, `weather_check`, the demo stack or any server. HTTP/socket access is blocked. Writes are limited to this report and `finish/signoff.json` (shell redirection supplies the log).

## Headline numbers from the copied live build

| Gas metric path | Recomputed median absolute error | Requested headline | Drift | Finite building-year-seasons / buildings |
|---|---:|---:|---:|---:|
| metered | 7.4% | 7.4% | +0.0 pp | 647 / 66 |
| blend | 29.2% | 28.7% | +0.5 pp | 800 / 101 |
| resstock | 29.9% | 29.9% | +0.0 pp | 800 / 101 |

The blend headline **28.7% is stale for the copied live artifacts**: the reproducible number is **29.2%**, a +0.5 percentage-point difference. Use 29.2% for this artifact set; no metric was adjusted to recover the requested value. The 7.4% and 29.9% headlines match. The seasonal gas dataset has 800 rows across 101 buildings; the table counts each path's finite predictions rather than assigning all rows to the metered path.

These metrics compare **total metered gas** (heating plus non-heating base use), not directly metered heating-only consumption or dollar bills. They are pooled building-season-year summaries, not independent household trials. Metered means a building's other years train its change-point model; unmetered paths use building-held-out OOF predictions. No new confidence interval or causality claim is implied. Metered properties are large Ann Arbor buildings; these validation errors do not establish performance on small houses.

## New bill noise basis is a different quantity

The historical winter ResStock p90 absolute estimate error remains **118.3%**, computed as `abs(predicted / actual - 1)` across seasonal building predictions. It measures cross-building estimate error.

The additive temporal noise floor is **25.158403% in winter**, recomputed as p90 `abs(actual / held-out same-building monthly prediction - 1)` from 514 months in 67 buildings. It matches `uncertainty_additive.json`; its all-month value is 38.501899%. This changes both the comparison and denominator, so it is **not an improvement from 118.3% to 25.2% in overall model accuracy**. Transfer to an unmetered renter is a pooled temporal component: unknown home-level bias remains, and this alone does not validate savings caused by a commitment. Prior serving behavior remains available; activation is separately capability/parameter gated.

## Artifact and runtime consistency

heat_gas: elastic_net (artifact, selected validation family, serving weights and OOF column agree); cool_elec: baseline_median (artifact, selected validation family, serving weights and OOF column agree).

Python **3.14.6**. Libraries: numpy 2.5.3, pandas 3.0.6, pyarrow 25.0.1, scipy 1.18.1, scikit-learn 1.9.1, xgboost 3.4.1, lightgbm 4.7.0, rasterio 1.5.2, shapely 2.1.2, requests 2.34.2, fastapi 0.142.2, uvicorn 0.54.0.

Checks:

- `gas_seasonal_summary_matches`: PASS
- `elec_seasonal_summary_matches`: PASS
- `gas_monthly_summary_matches`: PASS
- `elec_monthly_summary_matches`: PASS
- `new_noise_floor_matches`: PASS
- `source_hashes_match`: PASS
- `source_inputs_unchanged_during_run`: PASS
- `prediction_rows_match`: PASS
- `families_match`: PASS

Hashes below are recomputed from this isolated checkout and compared with the root agent's read-only copy manifest [finish/source_copy.json](finish/source_copy.json). The audit does not reopen or modify the live checkout. Baseline input hashes are checked again after recomputation to prove this script did not modify them. New uncertainty artifact SHA-256: `04f580d90e4e640802869b7b8477c5afe9abb6fd35a2a4473a95df77722db869`. Audit script SHA-256: `16819739013d2cb3b169e1eac20f01c2e454da8adafcd6c9bbdb08d210d9949e`.

| Input | SHA-256 | Matches copy manifest |
|---|---|---|
| `model/artifacts/bldg_cool_elec.pkl` | `d7267723b25e72bb2c506ab96720d0ec2da8008d2748ca060c81d455d9fffa9d` | yes |
| `model/artifacts/bldg_heat_elec.pkl` | `46550c0f42543eb744667343fc4bc1452b3a1e7c39811a83edb103756592fa44` | yes |
| `model/artifacts/bldg_heat_gas.pkl` | `b43b3f311db2e986b6e595576fdb5e34a5d30856bbbc26075c097e3532429d26` | yes |
| `model/artifacts/hc_elec.pkl` | `9105c91f0b5fc735a5a0e9348a20a74c50eff0929b82ca7dd9a663daa107a060` | yes |
| `model/artifacts/hc_gas.pkl` | `37af52fa0fa058f7435ebe676f082b3c0d18ba7b9598cbebec1695c7cd45b1b1` | yes |
| `model/artifacts/leakage.pkl` | `2cc359d7d703e4d39da77d4dc689422dfa3bd767e7207b698eb100c2e8badf90` | yes |
| `model/artifacts/resstock_hc.pkl` | `ab8e7ca885cbfc4c1d9e27a212768c5511cc131ce235c827fd49110c4b30580b` | yes |
| `model/data/processed/building_targets.parquet` | `190e332b9202223f5744411c714182225ae8c7468201d8d09c0e8b6ca69b7bd6` | yes |
| `model/data/processed/buildings_hc.csv` | `f53a50032a639d96848158e42f3f31fdd46ad46bd8702a21ba4e2ba6b3e53449` | yes |
| `model/data/processed/buildings_hc.parquet` | `21f9d6e78e041ed97b711006615831916818f547f9574737e080128da742a356` | yes |
| `model/data/processed/changepoints.parquet` | `5f7c7d5fb669c6a2027e92ac54e03e4b0c03eaa1b67c9d30cd67f6c08d1af726` | yes |
| `model/data/processed/leakage_ann_arbor.csv` | `4d065a5738e709860ef518f0fb1b5a65da79141f07008627b272cf7b4b152544` | yes |
| `model/data/processed/leakage_ann_arbor.parquet` | `334231e407d3579503c91f35e0dffeaad987bc4e1b6d208c850764e7b259ba57` | yes |
| `model/data/processed/meters_monthly.parquet` | `80013fa12a70f4bcb6436b82acdd6eb9abe3646638c61e3bf35df9c2ee39fa70` | yes |
| `model/data/processed/meters_weather.parquet` | `7981ef4f54bc68beee5bdd4436611bac345d4f81884233f27a50bc7870330b1a` | yes |
| `model/data/processed/normal_weather_buildings.parquet` | `ae08fb320c7f7111ad00f5f61da53a82714ae40c6ebbe87d4585b25962d1ee51` | yes |
| `model/data/processed/prices_mi.json` | `45fba8d145833589ffabbc899b0fa2a4732ad53721ef951f91e3c30dab530196` | yes |
| `model/data/processed/resstock_frame.parquet` | `649c3c08eadb8b9034160cf1cf1fe7f00da9eb9fd5a3edd9c25a651a6ff1278e` | yes |
| `model/results/blend_weights.json` | `5fea4300042e8638599a098b3a669bdb950f461a1eb698d191593134d9479c63` | yes |
| `model/results/building_model_validation.json` | `3194bbf8198147da990852ba8f083d2478e8c264c7e4f5f5306b2ad58833125a` | yes |
| `model/results/hc_validation.json` | `5fcb322bb66ecc8c835741bbebdd9df4acaad417c718e5bfba64d3a84a179f29` | yes |
| `model/results/heldout_elec.parquet` | `4f7548ff6dcc9006dfca265c23dba1e3fda3517a9bd218fdefd8ab3cd8825253` | yes |
| `model/results/heldout_gas.parquet` | `9a178eaa40625f5e946f21931efe93255fbc95759b1f9cde823a8361ac77cbee` | yes |
| `model/results/heldout_monthly.parquet` | `187241dedcfbb1d14c7f0fb8c5ff465ceb4ce1c062acc6c41294661769892bdb` | yes |
| `model/results/heldout_seasonal.parquet` | `088921b62e7d188f247c99bb016aba77420a087593a00e2980ddbcc8d019c346` | yes |
| `model/results/leakage_analysis.json` | `efac9fe6b7fcd0d10c6bdd404348d65eddf032637865859022c2db4f2a47597e` | yes |
| `model/results/leakage_validation.json` | `df073de8a7b13a92cd1d1f13757bfdc1e1ca3dfd855dc2910f731d45339e65ed` | yes |
| `model/results/meters_summary.json` | `0d31ba7b04fa5149df8a578d2f6d54ded9552db26462104bec1f03d9bcd9319b` | yes |
| `model/results/oof_cool_elec.parquet` | `c3b04dc533dc71f890796bd8db02e98a9a49997a31d2d0042510cd6e22db99fd` | yes |
| `model/results/oof_heat_gas.parquet` | `69e6cf7f87ec2165b4c9602878ccc6ec68a13bdebb510695b0e3c97f94641b7e` | yes |
| `model/results/resstock_hc_validation.json` | `4b92725eefe0a5e5c1b9585495612b7ff0faf32703ee00ea33146220edd74aa7` | yes |
| `model/results/resstock_reproduce.json` | `b1ccda9ec77cbabe2595fa09ad701b441387b8bdad928dee7a445ef041c9ea9b` | yes |
| `model/results/validation_real.json` | `74aa1680f15f7f922c9b184714386b29f4edd3bb58bacff79a324242f5e882be` | yes |

## Limits

This is a reproduction/sign-off of the copied pipeline's saved validation scheme, not a new independent test set or a new scientific validation of upgrades. It relies on saved nested-CV OOF predictions rather than rerunning expensive nested model selection. Existing split/calibration design is reproduced, not independently redesigned or proved leakage-free. NOAA/weather accuracy values are not re-downloaded or revalidated. New counterfactual effects, endpoint compatibility and live API acceptance are separate tests owned by the integration lead. The live :8001 server and live checkout are untouched.

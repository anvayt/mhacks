# Heating + cooling estimates per location (P1-01 research)

**Bottom line.** For any Ann Arbor address we return a point estimate of **heating $ and cooling $ for each of the four seasons** (and per year), for one apartment. It comes with the energy (gas ccf, electric kWh) and the weather that drives it: mean temperature, heating degree-days (HDD) and cooling degree-days (CDD) at the building's 800 m PRISM cell. It works for a typical year, a past year, or the next 12 months (forecast). It is as local as the data allows: the **building itself** (real meters when the city has them), not the zip code.

Code: `model/hc/service.py` (`estimate_hc`). Dev server: `uvicorn model.hc.server:app --port 8001`. Every number below comes from a file in `model/results/`.

## 1. What "PRISM" means here (both meanings are used)

| | What it is | How we use it |
|---|---|---|
| **PRISM climate data** (Oregon State PRISM Climate Group) | Gridded temperature at 800 m. Monthly time series 1895→present plus 1991–2020 normals. Free web service (`services.nacse.org/prism/data/get/us/800m/tmean/YYYYMM`) and normals over HTTP (`data.prism.oregonstate.edu/normals/...`). Each file can be downloaded at most twice per 24 h, so we download once, crop to Michigan, and cache. | The **local temperature level** for each building, month by month. |
| **PRISM, the Princeton Scorekeeping Method** (Fels 1986, *Energy and Buildings* 9:5–18) | Change-point regression: `use/day = α + βh·HDD(τh)/day + βc·CDD(τc)/day` with fitted balance points τ. | Splits each metered building's gas and electricity into **baseload / heating / cooling**. |

## 2. Data (all public, no keys; every external call is cached and logged to `model/data/cache/requests.log`)

| Data | Use | Notes |
|---|---|---|
| City of Ann Arbor energy benchmarking, monthly gas + electric, 2021–2023 ([FeatureServer](https://utility.arcgis.com/usrsvcs/servers/1e3bed4240284b40b0c4fea6f8cb4522/rest/services/OSI/BenchmarkingPerformanceMetrics/FeatureServer/0)) | **Ground truth**: 133 residential properties, polygons | **Units are not what the aliases say:** electricity is **kWh** and gas is **ccf** (SiteEUI×GFA ≈ 3.412·kWh + 104·gas, n=360 building-years, IQR 102.6–105.5 kBtu/unit). The layer holds 5 blocks of ~419 rows: one duplicates 2021, and one is labelled 2021 but its monthly pattern fits 2022/2024 weather, so it's excluded. |
| Ann Arbor building footprints (35,007; LiDAR height, stories, building names) | Building features: floor area, stories, height, envelope surface-to-volume, number of buildings in a complex | Parcel ids are mostly blank; **apartment complexes are grouped by building name** ("Greenbrier Apartments"). Footprint×stories ≈ 1.26 × reported floor area (median), used to estimate floor area for unmetered buildings. |
| PRISM 800 m tmean, monthly 2021-01→2026-08 + 1991–2020 normals | Local temperature level | ~95 MB cropped |
| Open-Meteo: ERA5 daily 1991→today, 16-day forecast, ECMWF SEAS5 51-member seasonal ensemble | Daily shape (degree-days need daily data), forecast | One cached series per 0.1° cell, appended incrementally |
| NREL ResStock 2024.2 Michigan (18,756 simulated homes) | Small buildings, renter answers, cross-check, default unit size (854 ft², 5+ unit median) | Simulation; calibrated to the meters for multifamily |
| EIA Michigan residential prices (gas N3010MI3 + volume N3010MI2; electricity EIA-861M) | Dollars, by month | See §5 |
| US Census geocoder + ACS 5-yr via Census Reporter (B25037 renter median year built; B25040 heating fuel) | Address → lat/lon + block group; year built and heating fuel for unmetered buildings | One request per county |
| NOAA NCEI 1991–2020 station normals (Ann Arbor U of Mich `USC00200230`, Ann Arbor Muni AP `USW00094889`) | Independent check of our degree-days | |

## 3. Weather at the building (P1-03)

Each month, every reanalysis day is shifted so that the monthly mean matches the PRISM 800 m cell (delta-method downscaling). Degree-days are then summed **daily** at bases 50/55/60/65 °F (heating) and 65/70/75 °F (cooling). The typical year averages degree-days over the 30 years 1991–2020, never computing them from an average temperature. Forecast = 16-day forecast → SEAS5 (degree-days per ensemble member, then averaged) → normals.

**Check against NOAA normals** (`results/validation_real.json`):

| Station | HDD65 NOAA / ours | CDD65 NOAA / ours | Winter HDD | Fall HDD |
|---|---|---|---|---|
| Ann Arbor U of Mich (urban) | 6,500.6 / 6,453 (−0.7%) | 653.1 / 656.5 (+0.5%) | −0.2% | −1.9% |
| Ann Arbor Muni Airport (open field) | 6,741.6 / 6,471 (−4.0%) | 519.6 / 644 (+24%) | −1.8% | −8.4% |

The urban station matches within 2.5% in every season. The airport is a cold open-field site (radiational cooling) that PRISM's 800 m grid smooths over. Our sampling was checked against rasterio and is exact; PRISM itself puts the two cells only 0.02–0.08 °C apart. **Honest limit:** within the city, weather varies little in the data we have (HDD65 range 6,418–6,598 across 591 apartment buildings, ±1.4%; CDD ±6%). Most of the apartment-scale signal comes from the **building**, not the weather. Weather localization matters more across Michigan, and over time (past year vs typical year vs forecast).

## 4. Energy models (P1-05, P1-07)

**Routing in `estimate_hc`, most grounded first:**

1. **metered**: the address is inside a benchmarked property with a good fit. That building's own PRISM change-point model from real monthly meters is used.
   - Gas fits: median R² **0.961**, CV(RMSE) 0.13, n=108.
   - Out-of-year test (fit 2 years, predict the 3rd): annual gas median error **4.2%** (p90 15%). Seasonal gas median error **7.4%** (winter 6.5%, summer 15%).
2. **meter_model+resstock**: unmetered apartment building ≥ 10,000 ft². This is the geometric mean of (a) a regression trained on 101 metered buildings and (b) meter-calibrated ResStock. Held-out seasonal gas median error on real buildings never seen in training:

   | path | median abs error | winter | p90 winter | median signed |
   |---|---|---|---|---|
   | blend (served) | **28.3%** | 27.8% | 94% | −2.3% |
   | ResStock (calibrated) | 29.6% | 30.0% | 117% | +2.1% |
   | meter-trained regression | 31.2% | 30.0% | 86% | −6.7% |
   | null (median slope) | 35.4% | 35.1% | 142% | +0.3% |

   Model choice (building level, repeated 5-fold CV, `results/building_model_validation.json`):
   - **Heating intensity:** multiple regression (ridge) 0.34 median APE, random forest 0.34, XGBoost 0.34, null 0.42.
   - **Cooling intensity:** random forest 0.40, null 0.41. Building features barely predict cooling.
   - The monthly-panel versions (`results/hc_validation.json`) were worse at building level (heating MAPE 0.33–0.42) and are kept only for comparison.
3. **resstock**: smaller buildings (houses, 2–4 units), where Ann Arbor has no meters. A per-degree-day XGBoost on ResStock with optional renter answers.
   - **Accuracy with answers:** heating median APE improves from 0.248 (public record only) to 0.211 with all 5 answers; cooling from 0.380 to 0.319.
   - **Inputs:** only answers a renter can know before signing (window panes, floor level, foundation, cooling type, occupants). Air leakage and insulation R-values are *not* inputs, because a renter can't know them.
   - **Multifamily calibration to meters:** heating ×1.14 (metered median 0.0618 vs ResStock 0.0541 ccf per 1,000 ft² per HDD60). Cooling ×0.63 (0.815 vs 1.298 kWh per 1,000 ft² per CDD65); ResStock over-predicts apartment cooling.

**Heating fuel:** for metered buildings it is read from the meters (a gas heating response vs an electric one). Otherwise it is the block-group majority from ACS B25040 (the share is returned). Electric-heat intensity uses the median of only 8 all-electric metered buildings, so it is weak.

## 5. Dollars (EIA, Michigan residential, last 24 months: 2024-08 → 2026-07)

- **Gas:** EIA's monthly "average price" includes fixed customer charges, so it nearly doubles in summer ($1.88/ccf in June vs $0.97 in January). Heating is *extra* gas, so we use the **marginal** price. A regression of monthly revenue on volume gives slope **$9.06/Mcf** (R² 0.99) and fixed ≈ $54.6M/month statewide. The monthly marginal price is (revenue − fixed)/volume: **$0.77–0.97/ccf**.
- **Electricity:** the same regression has a negative intercept (summer peak rates are confounded with volume), so marginal can't be separated from fixed. We use EIA-861M average $/kWh by month: **$0.190–0.219/kWh**.

## 6. Can bills reveal a leaky building? (`results/leakage_analysis.json`)

**Real meters (39–126 buildings, 2021–2023):**
- **A degree-day model predicts a building's next year well:** annual gas within 4.2% median. Deviations above about 15% are real changes.
- **"Uses more heat than similar buildings for the weather" is a stable trait:** year-to-year correlation of the deviation from peers is **0.95–0.98**. **94%** of the variance is persistent, and 90% of buildings stay on the same side of the peer median all 3 years.
- **Real spread within a vintage:** P90/P10 ≈ **3×** (1960–79: 3.1×; 2000+: 3.2×).
- **What the meters can't say:** *why* (air leakage vs boiler vs thermostat policy).

**Simulation only (ResStock):**
- Air leakage is the dominant hidden driver of heating. Dropping it costs 0.116 R²; wall/ceiling insulation, windows and furnace efficiency each cost ≤ 0.014.
- A heating-per-HDD figure (one winter bill) raises R² for log(ACH50) from 0.42 to 0.57. A "leaky" flag (ACH50 ≥ 20) is right 80% of the time vs a 41% base rate, but catches only 47% of leaky homes.

**Recommendation:** say "uses X% more heat than similar buildings for the weather". Do **not** claim "this unit is leaky" except as a clearly labelled simulation-based guess.

**Bill check (`bill_check`):** the noise floor is the p90 winter error *of the path used*. That's 16% for metered buildings. For unmetered ones it is 94%: a single bill only marks a building unusual at about 2× the expectation. For unmetered buildings, a renter's real bill is the most valuable thing we can get, which argues for using it to recalibrate (`/calibrate`).

## 7. Sanity numbers (typical year, 854 ft² apartment, `data/processed/buildings_hc.csv`, 591 Ann Arbor apartment buildings/complexes)

Median heating ≈ **$313/yr**, cooling ≈ **$65/yr** (IQR heating $271–332, cooling $57–83; 108 metered, 464 blend, 19 ResStock). Example metered complex, GreenBrier Campus (850 ft², typical year): heating $356, cooling $73, winter alone $188. The ResStock cross-check gives $401/$80.

## 8. Known gaps
- Cooling is the weakest part: per-building cooling fits have median R² 0.54, and building features barely beat the median.
- Benchmarked properties are ≥ 10,671 ft². Small rentals rely on simulation (ResStock); the only real-meter check of that path is on large buildings.
- Unit allocation is by floor-area share. It ignores unit position; `floor_level` affects only the ResStock half of the estimate.
- Footprint coverage = City of Ann Arbor only. Weather and ResStock work statewide.
- Prices: statewide EIA averages, not DTE tariff schedules.

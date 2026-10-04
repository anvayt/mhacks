# /model: heating + cooling estimates (P1 data/ML)

For an Ann Arbor location this returns a **point estimate of heating and cooling cost and energy for each season**
(winter = Dec–Feb, spring = Mar–May, summer = Jun–Aug, fall = Sep–Nov) for one apartment. It also returns the weather
that drives the estimate (mean temperature, heating/cooling degree-days at the building's 800 m PRISM cell), how the
number was computed, and its measured accuracy against real utility meters.

How the models work and how well they do: [`research/heating_cooling.md`](research/heating_cooling.md), and the
"Model performance" section of the dashboard.

## 1. Set up once (downloads everything, then works from local files)

Run from the repo root (macOS needs `brew install libomp` first for xgboost/lightgbm):

```bash
make -C model setup     # .venv + requirements (Python 3.12)
make -C model build     # downloads all source data once, trains, validates, pre-scores Ann Arbor
make -C model test      # 7 tests
make -C model dashboard # heating/cooling server (model.heating_cooling.server) → http://localhost:8001/dashboard (API docs /docs)
make -C model stop
```

`make build` downloads, then caches under `model/data/` (git-ignored):

| Data | Covers | Stored at |
|---|---|---|
| City of Ann Arbor energy benchmarking (monthly gas + electricity, 2021–23) | all reporting properties | `data/raw/arcgis/a2_benchmarking.geojson` |
| City of Ann Arbor building footprints (35,007) | whole city | `data/raw/arcgis/a2_footprints.geojson` |
| PRISM 800 m monthly mean temperature + 1991–2020 normals | Michigan (cropped) | `data/raw/prism/tmean/*.tif` |
| Open-Meteo ERA5 daily temperature 1991 → today | every 0.1° cell used so far (covers Ann Arbor's metered buildings) | `data/cache/openmeteo_full/*.parquet` |
| NREL ResStock 2024.2 Michigan (18,756 homes) | Michigan | `data/raw/resstock/` |
| EIA Michigan residential gas + electricity prices | Michigan | `data/raw/eia/`, `data/processed/prices_mi.json` |
| ACS 5-yr block-group year built + heating fuel | Washtenaw County | `data/cache/census/` |

Trained models go to `artifacts/*.pkl` (git-ignored, rebuilt by `make build`). Small derived tables and every
validation result are committed: `data/processed/*`, `results/*`.

## 2. Get an estimate

### Python (preferred inside the repo)

```python
from model.heating_cooling.service import estimate_hc

e = estimate_hc(
    lat=42.2680, lon=-83.7743,     # or address="2000 Pauline Blvd, Ann Arbor, MI 48103"
    unit_sqft=800,                 # the apartment's size; default 854 ft² (ResStock MI median 5+ unit) or the whole building
    mode="normal",                 # "normal" = typical year (1991–2020) | "forecast" = next 12 months | 2023 (a past year)
    answers={"window_panes": 1, "floor_level": 2},   # optional; codes: GET /hc/answers
    heating_fuel=None,             # "gas" | "electric" to override the lookup
    building_type=None,            # e.g. "Multi-Family with 5+ Units" to override the guess
)
e["seasons"]   # 4 dicts, one per season
e["annual"]    # yearly totals
```

### HTTP (`make -C model dashboard`, port 8001)

| Endpoint | Returns |
|---|---|
| `GET /hc/estimate?address=…` or `?lat=…&lon=…` (+ `unit_sqft`, `mode`, `heating_fuel`, `building_type`, `block_group`, `window_panes`, `floor_level`, `foundation_code`, `cooling_code`, `occupants`) | the `estimate_hc` result below |
| `GET /hc/weather?lat=&lon=&mode=` | monthly + seasonal temperature, HDD, CDD at the PRISM cell |
| `GET /hc/bill_check?year=&month=&gas_ccf=&unit_sqft=&address=` (or `lat`, `lon`) | a real gas bill vs what that month's weather predicts |
| `GET /hc/buildings` | the 591 pre-scored Ann Arbor apartment buildings (same as `buildings_hc.csv`) |
| `GET /hc/metered`, `GET /hc/metered/{building_id}` | metered properties; monthly actual vs model for one |
| `GET /hc/heldout?fuel=gas` or `elec` | held-out predicted-vs-actual **energy** rows for every estimate path |
| `GET /hc/validation` | every validation result file |
| `GET /hc/answers` | renter answers the model accepts, with their codes |

### What comes back

```jsonc
{
  "seasons": [                       // winter, spring, summer, fall
    {"season": "winter", "months": [1, 2, 12],
     "heating": {"usd": 170.0, "gas_ccf": 189.3, "electric_kwh": 0.0},
     "cooling": {"usd": 0.0, "electric_kwh": 0.0},
     "total_usd": 170.0,
     "weather": {"tmean_f": 26.4, "hdd65": 3486.0, "cdd65": 0.0, "hdd60": 3034.0}}
  ],
  "annual": {"heating_usd", "cooling_usd", "total_usd", "gas_ccf", "electric_kwh", "hdd65", "cdd65", "tmean_f"},
  "months": [                        // 12 rows, chronological (forecast mode starts at the current month)
    {"month": 1, "year": null, "days": 31,
     "heating": {"usd", "gas_ccf", "electric_kwh"}, "cooling": {"usd", "electric_kwh"}, "total_usd",
     "weather": {"tmean_f", "hdd65", "hdd60", "cdd65", "basis"},
     "accuracy": {"gas_median_abs_error", "gas_bias", "elec_median_abs_error", "elec_bias"}}   // held-out, this month + path
  ],
  "method": "metered" | "meter_model+resstock" | "resstock",     // estimate path, see §3
  "building": {"name", "gfa_ft2", "year_built", "stories", "buildings_on_property", "heating_fuel", "building_type",
               "...": "each has a *_source field saying where it came from"},
  "unit_sqft", "unit_sqft_source", "mode",
  "model_detail": {"equation", "intensities" or "gas_fit"/"elec_fit", "unit_share", "degree_days_year"},  // the arithmetic
  "accuracy": {"seasonal_gas_median_abs_error": {"all", "winter", "spring", "summer", "fall"}, "basis"},
  "cross_check_resstock": {"heating_usd", "cooling_usd"},       // when method != "resstock"
  "location": {"lat", "lon", "matched_address", "block_group"},
  "weather_source", "prices", "sources"
}
```

Seasons and annual are plain sums of the 12 months (the model computes month by month). A single month is less certain
than a season: on held-out real meters the median error of a month's total gas is 11.4% for metered buildings and 32%
for unmetered ones (vs 7.4% / 28.7% per season). Low-use months (spring and summer gas, spring and fall cooling) are the
least reliable, and unmetered winter electricity is biased about −17%. In forecast mode, months beyond about 2 weeks
come from the seasonal-forecast ensemble mean or normals, so month-to-month detail isn't a skilful forecast.
Per-month errors: `results/validation_real.json` → `monthly_gas_vs_real_meters`, `monthly_elec_vs_real_meters`.

Units: gas in **ccf** (1 ccf ≈ 1.04 therms), electricity in **kWh**, money in **USD**. Building totals are scaled to
the unit by floor area.

**Dollars are a conversion, not a prediction.** `usd` = the estimated energy × the Michigan statewide residential
price for that month (US EIA: gas at the marginal price with fixed charges removed, derived by regression from EIA
revenue and volume; electricity at the EIA-861M average price). Present them as "≈ $X at EIA Michigan prices". No
bill data exists for any building. The model estimates **energy**, and every accuracy figure refers to energy.

### Whole-city table: no calls needed

`data/processed/buildings_hc.csv` has 591 Ann Arbor apartment buildings/complexes (108 metered, the rest estimated),
typical year, 854 ft² unit. Columns: `id, method, name, lat, lon, gfa_ft2, year_built, unit_sqft, heating_usd_yr,
cooling_usd_yr, winter_usd, spring_usd, summer_usd, fall_usd, hdd65, cdd65, tmean_f`.
Regenerate it with `python -m model.heating_cooling.score_buildings`.

## 3. Estimate paths (chosen automatically, most grounded first)

1. **`metered`**: the location is inside an Ann Arbor benchmarked property. It uses that building's own change-point
   fit on its 2021–23 monthly meters: `use = base·days + slope·HDD(τ) [+ slope·CDD(τ)]`. Held-out seasonal error:
   gas 7.4%, electricity 4.5%.
2. **`meter_model+resstock`**: an unmetered multifamily building of 10,000 ft² or more. It takes a weighted geometric
   mean of two intensities: (a) a model trained on the metered buildings (heating: a tuned random forest; cooling:
   their median, because no model beat it), and (b) ResStock calibrated to the meters. Weights are in
   `results/blend_weights.json`. Held-out seasonal error is about 29% for gas and 30% for electricity.
3. **`resstock`**: a smaller building. It uses the ResStock model alone (plus renter answers); this path is trained
   on simulation.

Model selection, tuning and every metric: `results/building_model_validation.json` (nested CV, one-standard-error
rule) and `results/validation_real.json` (held-out vs real meters, with every parameter estimated in-fold).

## 4. Network use at run time

After `make build`, these are the only calls an estimate can make:

| Call | When | Avoid it by |
|---|---|---|
| US Census geocoder | an `address=` that hasn't been looked up before (each address is cached permanently) | passing `lat`/`lon` |
| Open-Meteo forecast + seasonal | `mode="forecast"` only; cached 6 h / 24 h; the stale copy is used if offline | `mode="normal"` or a year |
| Open-Meteo archive (append new days) | at most once a day per cell; on failure the cached series is used | nothing needed (never blocks) |

PRISM, footprints, benchmarking, ResStock, EIA, ACS and the trained models are always read locally. Every real network
request is logged to `data/cache/requests.log`.

**Limitations:**
- With `lat`/`lon` input there's no block group unless the caller passes `block_group` (/api does). For an *unmetered* building, year built then falls back to the
  median of the metered buildings and heating fuel to gas; pass `heating_fuel` if you know it.
- A point outside the 0.1° weather cells already cached triggers one archive download for that cell.
- Footprints cover the City of Ann Arbor only.

## 5. Layout

| Path | What |
|---|---|
| `data_sources/` | cached clients: ResStock, benchmarking, footprints, PRISM, Open-Meteo, EIA, Census (`http.py` logs requests) |
| `climate.py` | weather at the 800 m PRISM cell: typical year, past year, forecast; seasonal aggregation |
| `heating_cooling/changepoint.py` | change-point (Princeton Scorekeeping) fits |
| `heating_cooling/modelsel.py`, `building_model.py` | model families, nested CV, one-SE selection, final fits |
| `heating_cooling/resstock_model.py` | ResStock per-degree-day XGBoost + renter answers, calibrated to meters |
| `heating_cooling/validate.py`, `leakage_analysis.py` | NOAA check; held-out real-meter checks; the leakage question |
| `heating_cooling/service.py`, `server.py`, `dashboard.html` | `estimate_hc` and friends; FastAPI app; explorer UI |
| `scripts/build_all.py` | what `make build` runs |
| `scripts/reproduce_resstock.py` | 10:30 PM checkpoint (R² 0.548 → 0.764) |

## 6. Air leakage (blower-door) model for Ann Arbor houses (P1-09)

Predicts a house's air leakage, meaning its **blower-door result (CFM50: airflow at 50 Pa)**, without a test, from
public data only. No landlord or renter survey answers are used, in training or in evaluation.

```python
from model.leakage.predict import predict_leakage
predict_leakage(lat=42.2756, lon=-83.7408)      # or address="…"
# → {"estimate": {"cfm50", "cfm50_per_ft2", "ach50_at_8ft_ceiling"}, "inputs": {... each with a source},
#    "in_training_range", "scope_note", "model", "accuracy"}
```

`make -C model leakage` trains it and writes `data/processed/leakage_ann_arbor.{parquet,csv}`: one row per Ann Arbor
residential building with an address (17,286 rows; 15,416 one-to-four-unit houses get an estimate).

**Training data (real tests):** 947 blower-door tests from NYSERDA's public New York home surveys (2014–15 RSBS and
2018 RBSA, data.ny.gov `8wa7-87p5`, `3drn-bhzv`), in climate zones 4–6, after QC (completed test at about 50 Pa,
ACH50 0.5–60). LBNL ResDB raw data isn't public (contact-only) and NEEA RBSA requires registration, so neither is used.

**Inputs** (available for every Ann Arbor house):
- **Year built:** in Ann Arbor, the ACS block-group renter median, because per-house year built isn't public.
- **Floor area:** footprint × stories.
- **Stories:** recorded where present, otherwise from LiDAR height (87.7% accurate on labelled houses).
- **Home type:** number of city mailing addresses inside the footprint.
- **Climate zone.**

**How it was tested** (`results/leakage_validation.json`): target log(CFM50/ft²); hyperparameters tuned by inner
GroupKFold by region; the outer test holds out one of 10 NY regions at a time. Median absolute error on CFM50:

| | Error |
|---|---|
| Random forest (chosen; neural net, XGBoost tie at 23.7–23.8%; linear models 24.6–25.0%) | **23.6%** |
| Baseline (median) | 42.9% |
| ResStock lookup by vintage (simulated) | 39.4%, and biased 33% too leaky |
| Train on the 2014–15 survey → test on 2018 / reverse | 26.0% / 24.3% |
| With Ann Arbor's real year-built uncertainty (block-group median vs true; typically ±12 years) | **27.3%** |
| With no year built at all | 32.3% |

Extra survey-only fields (foundation, style, ceiling height) didn't improve it (23.7%).

**Limitations for Ann Arbor:**
- **New York houses, not Michigan ones.** Same climate zones, but Ann Arbor isn't in the training data.
- **Floor area is overstated.** Footprints include garages and porches: the median detached floor area is 2,741 ft² vs
  2,010 ft² in training. That biases per-ft² and ACH50 low (about 18% if true area is 25% lower); total CFM50 is much
  less affected.
- **Predictions are compressed.** Block-group year built hides individual houses' age, so the leakiest houses are
  under-flagged.
- **1–4 unit homes only.** Buildings with 5+ units get no estimate.

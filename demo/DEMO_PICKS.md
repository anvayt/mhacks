# Real demo picks — verified October 4, 2026

These are real Ann Arbor addresses verified against the running API, not invented listings. All dollar estimates cover **heating and cooling only**, not total utilities or rent. Current listing availability, asking rent, actual conditioned unit size and equipment were not independently checked. The answers below are explicitly illustrative renter scenarios.

API capture revision: `fd8c31c0b40148b1940d9dddd36c4fdfd6bf3691` (`origin/dev` at capture). Requests ran sequentially against an isolated API on `127.0.0.1:8020`, using the already-running model at `localhost:8001`; the API caps simultaneous model estimates at four. Nothing was rebuilt. The raw captures preserve actual session IDs, request bodies, HTTP status and full response bodies. All selected calls returned HTTP 200. Every final pick's model point falls inside the exact matching `/city` footprint.

## Proposed final five

Do **not** change `demo/addresses.txt` yet. Proposed addresses, in rehearsal order:

| Address | Purpose | Verified public-record result |
|---|---|---|
| **2322 Arrowwood Trl** | Grade lock | B, possible A–B; one `Central AC` answer locks B; $470/year p50 |
| **624 Church St** | Primary battle winner: ArborBlu | A, score 97; $265/year p50; 1,198 estimated ft² |
| **1022 S Forest Ave** | Primary battle comparator and F map example | Predicted F, score 4, **unlocked A–F**; $2,179/year p50; 1,328 estimated ft² |
| **615 S Main St** | Top-2% map + public leaderboard + actual meter path: The Yard | A, live score 100; city score 99.76145; $143/year p50 |
| **1514 Morton Ave** | Typed bill calibration and a priced fix | Gas + single-pane illustrative scenario: windows save $125/year, 699 kg CO₂/year |

All addresses above are in Ann Arbor, MI. `619 E University Ave` (Z Place) is an additional nearby battle alternate, outside the proposed five. Area estimates at Arrowwood and the apartment buildings include possible common/garage space; Morton uses gross footprint area × stories. These are matched-size public-record scenarios, not verified equal-size rental listings.

## 1. Grade lock — 2322 Arrowwood Trl

One question is sufficient, satisfying the target of at most two answers. The starting span contains two grades. The annual dollar interval retains model uncertainty after the **answer-driven grade** locks.

| Step | Illustrative user text | Score / grade | Grade span | Annual p10 / p50 / p90 | Locked |
|---|---|---|---|---|---|
| Public record | `2322 Arrowwood Trl, Ann Arbor, MI` | 70 / B | A–B | $326 / $470 / $505 | false |
| Answer 1 | `Central AC` | 70 / B | B | $435 / $470 / $505 | true |

Exact API question: **“What air conditioning does the unit have?”** Suggested response copy after the answer: **“Grade locked: B. Estimated heating + cooling: $435–$505/year, with a $470 midpoint.”** This is narration derived from the API, not a captured iMessage exchange.

`Central AC` is a plausible scripted answer, **not a verified fact about this home**. The metered path uses Arrowwood Hills Cooperative's property-wide meter data across 66 buildings, allocated by floor area; this is not a meter reading from this individual townhouse.

Exact captured requests:

```json
{
  "method": "POST",
  "path": "/estimate",
  "json": {
    "address": "2322 Arrowwood Trl, Ann Arbor, MI"
  }
}
```
```json
{
  "method": "POST",
  "path": "/answer",
  "json": {
    "session_id": "afef745d26",
    "question_id": "cooling_code",
    "answer": "Central AC"
  }
}
```
Trimmed response progression:

```json
[
  {
    "step": "public_record",
    "session_id": "afef745d26",
    "score": 70,
    "grade": "B",
    "grade_span": [
      "A",
      "B"
    ],
    "locked": false,
    "annual": {
      "p10": 326,
      "p50": 470.0,
      "p90": 505
    },
    "grade_band_usd": {
      "p10": 352,
      "p50": 470.0,
      "p90": 470
    }
  },
  {
    "step": "central_ac",
    "session_id": "afef745d26",
    "score": 70,
    "grade": "B",
    "grade_span": [
      "B"
    ],
    "locked": true,
    "annual": {
      "p10": 435,
      "p50": 470.0,
      "p90": 505
    },
    "grade_band_usd": {
      "p10": 470,
      "p50": 470.0,
      "p90": 470
    }
  }
]
```

Full ordered captures: [initial estimate](picks/grade/01-estimate.json), [answer](picks/grade/02-answer.json).

## 2. Listing battles — nearby, same building type, matched estimated size

All three pairs return **`confident: true`** because the API's annual p10–p90 intervals do not overlap. All use **Multi-Family with 5+ Units**. Distances below are straight-line WGS84 geodesic distances between the model's points inside the selected footprints; they are not walking routes or sourced neighborhood boundaries. Size difference is `(larger / smaller − 1) × 100`.

| Priority | A → B | Estimated ft² A / B | Size difference | Distance | Annual p50 A / B | Gap |
|---|---|---|---|---|---|---|
| **Primary** | 624 Church St → 1022 S Forest Ave | 1,198 / 1,328 | 10.85% | 533.7 m | $265 / $2,179 | **$1,914/year** |
| Nearby alternate | 619 E University Ave → 1022 S Forest Ave | 1,435 / 1,328 | 8.06% | 569.8 m | $194 / $2,179 | **$1,985/year** |
| Citywide alternate | 615 S Main St → 1022 S Forest Ave | 1,412 / 1,328 | 6.33% | 1,311.6 m | $143 / $2,179 | **$2,036/year** |

Prefer ArborBlu for the primary demonstration: the meter path reports $238/year heating and $26 cooling; independently rounded components differ by $1 from its $265 total. The Yard is also positive-heat ($140 heating), while Z Place has only $16 heating and is a secondary alternative. Do not imply the Yard pair shares a neighborhood. The Forest estimate infers electric heat from block-group data; it is not an observed equipment record. Its unlocked A–F span remains visible even though the currently returned cost intervals are disjoint.

Suggested primary reveal: **“For these public-record size estimates, predicted heating and cooling differ by $1,914 a year. The returned ranges do not overlap.”** No claim about equal rent, vacancy or full utility bills is supported.

### 624 Church St vs 1022 S Forest Ave

```json
{
  "method": "POST",
  "path": "/compare",
  "json": {
    "listings": [
      {
        "address": "624 Church St, Ann Arbor, MI"
      },
      {
        "address": "1022 S Forest Ave, Ann Arbor, MI"
      }
    ]
  }
}
```
```json
{
  "a": {
    "annual": {
      "p10": 221,
      "p50": 265.0,
      "p90": 285
    },
    "grade": "A",
    "badges": [
      "top-10-efficient",
      "battle-winner"
    ]
  },
  "b": {
    "annual": {
      "p10": 301,
      "p50": 2179.0,
      "p90": 5154
    },
    "grade": "F",
    "grade_span": [
      "A",
      "B",
      "C",
      "D",
      "F"
    ]
  },
  "winner": "a",
  "diff_usd_yr": 1914,
  "confident": true
}
```
Full capture: [compare/01-arborblu-forest.json](picks/compare/01-arborblu-forest.json).

### 619 E University Ave vs 1022 S Forest Ave

```json
{
  "method": "POST",
  "path": "/compare",
  "json": {
    "listings": [
      {
        "address": "619 E University Ave, Ann Arbor, MI"
      },
      {
        "address": "1022 S Forest Ave, Ann Arbor, MI"
      }
    ]
  }
}
```
```json
{
  "a": {
    "annual": {
      "p10": 16,
      "p50": 194.0,
      "p90": 208
    },
    "grade": "A",
    "badges": [
      "top-10-efficient",
      "battle-winner"
    ]
  },
  "b": {
    "annual": {
      "p10": 301,
      "p50": 2179.0,
      "p90": 5154
    },
    "grade": "F",
    "grade_span": [
      "A",
      "B",
      "C",
      "D",
      "F"
    ]
  },
  "winner": "a",
  "diff_usd_yr": 1985,
  "confident": true
}
```
Full capture: [compare/02-zplace-forest.json](picks/compare/02-zplace-forest.json).

### 615 S Main St vs 1022 S Forest Ave

```json
{
  "method": "POST",
  "path": "/compare",
  "json": {
    "listings": [
      {
        "address": "615 S Main St, Ann Arbor, MI"
      },
      {
        "address": "1022 S Forest Ave, Ann Arbor, MI"
      }
    ]
  }
}
```
```json
{
  "a": {
    "annual": {
      "p10": 130,
      "p50": 143.0,
      "p90": 154
    },
    "grade": "A",
    "badges": [
      "top-10-efficient",
      "battle-winner"
    ]
  },
  "b": {
    "annual": {
      "p10": 301,
      "p50": 2179.0,
      "p90": 5154
    },
    "grade": "F",
    "grade_span": [
      "A",
      "B",
      "C",
      "D",
      "F"
    ]
  },
  "winner": "a",
  "diff_usd_yr": 2036,
  "confident": true
}
```
Full capture: [compare/03-yard-forest.json](picks/compare/03-yard-forest.json).

## 3. City A/F contrast and public leaderboard

The selected pair is The Yard / 615 S Main St and 1022 S Forest Ave, both **Multi-Family with 5+ Units**. The live estimates use the same city footprint geometry as their scored features; the model point is inside each selected polygon. The API rounds live scores to integers, while `/city` retains its batch percentile precision.

| Address | City OBJECTID | Live grade / score | `/city` grade / score | City block group |
|---|---|---|---|---|
| 615 S Main St | 50892 | A / 100 | A / 99.76145 | 261614006001 |
| 1022 S Forest Ave | 22547 | F / 4 | F / 4.246183 | 261614005002 |

The Yard qualifies for “top 2%” at either score precision. Forest's F is a **predicted public-record point estimate with an unlocked A–F span**, not a confirmed building defect. Name only the public benchmarked property on the leaderboard. Forest appears in the **anonymous block-group aggregate**, not as a named landlord or building.

Exact relevant entries from `GET /leaderboard?scope=city`:

```json
{
  "best": {
    "benchmark_id": "A2BLD-00025",
    "name": "The Yard",
    "score": 99.76,
    "grade": "A",
    "cost_per_sqft": 0.1013,
    "building_count": 1,
    "predicted": true,
    "source": "https://utility.arcgis.com/usrsvcs/servers/1e3bed4240284b40b0c4fea6f8cb4522/rest/services/OSI/BenchmarkingPerformanceMetrics/FeatureServer/0"
  },
  "worst_blocks": {
    "geoid": "261614005002",
    "area_type": "block_group",
    "building_count": 149,
    "score": 2.59,
    "excess_usd_per_sqft": 1.7811,
    "predicted": true
  }
}
```

Forest's own block **261614005002** is present with **149 buildings**. The neighborhood-scope counterpart is Census tract `26161400500` (875 buildings), rather than an informal neighborhood name.

Evidence: [The Yard estimate](picks/city/01-estimate-yard.json), [Forest estimate](picks/city/02-estimate-forest.json), [complete city leaderboard response](picks/city/03-leaderboard-city.json), [complete neighborhood leaderboard response](picks/city/04-leaderboard-neighborhood.json), [exact selected `/city` features](picks/city/05-city-selected-excerpt.json). The selected feature file is explicitly an excerpt. The complete 25,670-feature HTTP body is also preserved as [gzip-compressed GeoJSON](picks/city/06-city-full-response.geojson.gz), with [request/status/headers and checksum metadata](picks/city/06-city-full-response.metadata.json). Decompress with `gzip -dc demo/picks/city/06-city-full-response.geojson.gz > /tmp/demo-city.geojson`; the decompressed bytes are the exact original HTTP body.

## 4. “Real meters” example — The Yard

`POST /estimate {"address":"615 S Main St, Ann Arbor, MI"}` returns:

```json
{
  "heating_cooling": {
    "method": "metered",
    "building": {
      "name": "The Yard",
      "address": "615 S. Main",
      "benchmarking_id": "A2BLD-00025",
      "year_built": 2015,
      "year_built_source": "Ann Arbor benchmarking",
      "fit": {
        "gas_r2": 0.906,
        "elec_r2": 0.575
      }
    },
    "annual": {
      "heating_usd": 140.0,
      "cooling_usd": 3.0,
      "total_usd": 143.0,
      "gas_ccf": 154.4,
      "electric_kwh": 14.0,
      "hdd65": 6481.0,
      "cdd65": 641.0,
      "tmean_f": 49.0
    }
  },
  "city_csv_benchmark_name": "The Yard"
}
```

The City of Ann Arbor's [public benchmarking FeatureServer](https://utility.arcgis.com/usrsvcs/servers/1e3bed4240284b40b0c4fea6f8cb4522/rest/services/OSI/BenchmarkingPerformanceMetrics/FeatureServer/0) names this property **The Yard**, ID `A2BLD-00025`. The response identifies the `metered` path, using the property's 2021–23 meter fit; the captured detailed fit has 34 gas observations (R² ≈ 0.906) and 36 electric observations (R² ≈ 0.575). Unit cost is an allocated typical-year prediction, not a current tenant bill. The API-reported 7.4% held-out seasonal gas error describes this model path, not measured error on this unit's current bill.

## 5. Bill/calibration/fixes — 1514 Morton Ave

**A real bill photo was not supplied. Photo ingestion and OCR remain unverified.** This flow demonstrates typed calibration with **hypothetical** values. It must not be narrated as a real tenant bill, a real savings streak or a verified weather-adjusted outcome.

Fresh sequence: `/estimate` → illustrative `Gas` answer → illustrative `Single-pane` answer → typed `/calibrate` → `/fixes`. No fixes were requested earlier in this final capture session, so calibration's badges do not inherit exploratory fix state.

| Step | Grade | Annual p10 / p50 / p90 |
|---|---|---|
| Public record | C | $1,198 / $2,117 / $14,599 |
| Illustrative `Gas` | C | $1,198 / $2,117 / $3,070 |
| Illustrative `Single-pane` | C | $1,283 / $2,185 / $3,070 |

Exact answer texts are `Gas` to **“Is the heat gas or electric?”**, then `Single-pane` to **“Are the windows single-, double- or triple-pane?”** The equipment assumptions are plausible but unverified. The month below is deliberately hypothetical: **150 therms and 400 kWh, January 1–31, 2026**.

Exact captured calibration request and trimmed actual response:

```json
{
  "method": "POST",
  "path": "/calibrate",
  "json": {
    "session_id": "1d07ee17b7",
    "therms": 150,
    "kwh": 400,
    "start": "2026-01-01",
    "end": "2026-01-31"
  }
}
```
```json
{
  "pct_vs_expected_for_weather": -67.6,
  "streak_months": 1,
  "actual_gas_ccf": 144.6,
  "expected_gas_ccf": 446.9,
  "noise_floor": 118.3,
  "meaningful": false,
  "badges": [
    "weather-beater"
  ],
  "note": "Gas only: electricity (kWh) isn't compared with the weather yet."
}
```

The actual endpoint returns −67.6%, streak 1 and `weather-beater`, but **`meaningful: false`** with a 118.3% noise floor. Show that uncertainty; do not present the percentage as a meaningful verified saving. The electricity input is echoed but not weather-compared. Calibration checks the bill against weather; in this API revision it does not change the saved annual energy prediction.

Exact fixes request and model-priced item:

```json
{
  "method": "GET",
  "path": "/fixes/1d07ee17b7"
}
```
```json
[
  {
    "item": "ENERGY STAR low-e storm windows or windows",
    "grh_points": 4,
    "grh_item": "Energy Efficient Windows",
    "cost_usd": null,
    "rebate_usd": null,
    "cost_note": "Low-e storm windows cost $60-$200 per window installed (DOE Energy Saver). DTE pays $15 per replacement window in homes it heats (2026).",
    "sources": [
      "https://www.a2gov.org/media/dxxnmkyt/green-rental-housing-checklist.pdf",
      "http://web.archive.org/web/20260501010625/https://www.energy.gov/energysaver/do-it-yourself-savings-project-install-exterior-storm-windows-low-e-coating",
      "https://www.dteenergy.com/us/en/residential/save-money-energy/rebates-and-offers/insulation-and-windows.html"
    ],
    "unpriced": false,
    "co2_kg_saved": 699,
    "usd_saved_yr": 125,
    "new_grade": "C"
  }
]
```

This produces a model-priced **$125/year**, **699 kg CO₂/year** window improvement, **+4 GRH points**, with grade remaining **C**. The API has no total installed cost or total rebate (`null`), so do not claim payback, a fully costed retrofit or an unlocked B grade. Air sealing, attic insulation and the gas-to-electric heat-pump option remain unpriced here.

Ordered full captures: [estimate](picks/bill/01-estimate.json), [Gas](picks/bill/02-answer-heating_fuel.json), [Single-pane](picks/bill/03-answer-window_panes.json), [hypothetical typed calibration](picks/bill/04-calibrate-hypothetical.json), [fixes](picks/bill/05-fixes.json), [session after fixes](picks/bill/06-session-after-fixes.json). The returned landlord email is a draft only; it was not sent.

## Rehearsal and provenance

- [Machine-readable verification](picks/verification.json) contains actual request ordering, pair distance/area calculations, exact city score CSV rows and all five geometry matches.
- Every normal capture file is an envelope containing `request`, `status` and the unmodified parsed JSON `response`. The explicitly named city excerpt omits unrelated features; the separate gzip file retains the full original city body. No mock response or hand-edited model number is present.
- Start fresh sessions when rehearsing live. Replace recorded `session_id` values in later requests with the preceding live response's ID; the recorded IDs belong to an isolated capture database. This directory supplies evidence for future replay fixtures; it does not implement an offline replay mode.
- Grades can change if the peer table or model changes. These captures use dev's 25,670-row scoring table, before the separately proposed full city-layer branch's 25,704-row revision. Recheck after that merge.
- The endpoint's bands are reported model intervals, not formal guarantees of the actual annual bill. Retain the range and public-record assumptions in narration.

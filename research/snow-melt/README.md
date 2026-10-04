# Roof snow loss versus real metered heating: NO-GO

**Question:** During December 2025–March 2026, did Ann Arbor buildings whose roofs lost snow faster than nearby ground have higher gas heating per square foot per heating degree-day?

**Verdict: NO-GO because the test has no eligible real-meter pairs, not because a zero correlation was measured.** Clear imagery exists, but the roof-interior requirement removes the metered sample. Spearman rho, p-value and bootstrap CI are **not estimable**. No `/snow` endpoint or map layer was added; grades and scores are unchanged.

**Devpost sentence:** “We explored satellite roof snow loss, but the roofs with usable Sentinel-2 pixels did not overlap our metered validation set, so we kept the signal out of Hidden Rent.”

## Results and provenance

All counts below come from the linked machine-readable outputs, derived by [pipeline.py](pipeline.py) and [analyze.py](analyze.py). They are observations or analysis choices, not product claims. Input file hashes and source paths are in [input_manifest.json](results/input_manifest.json). Repository inputs are from `dev` revision `5bc5ee3`.

| Stage | Observed result | Where the number comes from |
|---|---:|---|
| Cached city footprints / scored P2 footprints | 35,007 / 25,704 | [geometry summary](results/geometry_summary.json), hashed `api/data/city_scores.csv` |
| Roof plan area ≥1,500 m² | 622, including 143 scored footprints | [geometry summary](results/geometry_summary.json); threshold from the user brief |
| Nonempty roof after a 20 m inward buffer | 194 | [geometry summary](results/geometry_summary.json) |
| At least 3 native 20 m pixel centers inside that buffer | 52 roofs; 4 present in P2's scored table | [eligible pixels](results/eligible_roof_pixels.csv), [validation counts](results/validation.json) |
| P1 `method == metered` records / gas-quality-eligible properties | 110 / 86 | [meter summary](results/meter_summary.json), [meter targets](results/meter_targets.csv) |
| Winter NOAA snow-depth coverage / screened snowfall days | 121 daily depths / 19 event dates | [NOAA observations](results/noaa_daily_long.csv), [events](results/events.csv) |
| STAC bbox items / unique acquisitions on tile 17TKG | 165 / 54 | [scene manifest](results/scene_manifest.json); overlapping tiles and repeated processing are not independent scenes |
| Acquisitions in the post-event windows / usable local dates | 28 / 10 | [scene quality](results/scene_quality.csv); no source-access errors |
| Paired roof/ground observations | 302 across all 52 eligible roofs | [snow observations](results/snow_observations.csv) |
| Usable roof-event curves / roofs with a snow-loss index | 30 / 27 | [event metrics](results/event_metrics.csv), [building metrics](results/building_metrics.csv) |
| Independent metered validation pairs | **0** | [meter join](results/meter_join.csv), [validation](results/validation.json) |
| Predicted-cost pairs | **1** | [building metrics](results/building_metrics.csv); footprint 26402 only |

The first usable post-event image was **December 12, 2025**, after the **December 10** event. The **December 17** scene had **51 usable roofs** and **95.82%** locally clear SCL pixels in the study rectangle, despite high whole-tile cloud cover. These dates/counts/fractions are in [scene_quality.csv](results/scene_quality.csv). Thus the failure is not “no clear winter scenes.”

| Validation | Independent n | Spearman rho | Two-sided p | Bootstrap 95% CI |
|---|---:|---|---|---|
| Primary: meter-fitted heating / ft² / HDD60, ≥50% property roof coverage | **0** | Not estimable | Not estimable | Not estimable |
| Meter-fitted heating, any property roof coverage | **0** | Not estimable | Not estimable | Not estimable |
| Raw cold-month gas / ft² / HDD60 sensitivity | **0** | Not estimable | Not estimable | Not estimable |
| Secondary: P2 predicted heating+cooling cost / ft² | **1** | Not estimable | Not estimable | Not estimable |

Source: [validation.json](results/validation.json). Null statistics are intentional; they are not zero-valued findings. No permutations or bootstraps can estimate the primary test with this sample. The implementation supports the prespecified **9,999 permutations** and **10,000 bootstrap draws**, seed **20261004**, when a nonconstant sample is available; these are analysis settings, not counts of experiments run on this empty cohort.

### Why the sample disappears

Among roofs associated with P1's metered properties, **62** exceed the requested area cutoff. Only **one** has a nonempty 20 m inset; its interior is approximately **112 m²**, smaller than one native **400 m²** SWIR pixel. See `roof_inventory.csv`, `meter_targets.csv` and [geometry diagnostics](results/geometry_diagnostics.json). Large floor area does not imply a broad roof: many apartment footprints are long and narrow.

| Inward buffer | Roofs with ≥3 native pixel centers | Meter properties passing gas QC, before any cloud/curve filtering |
|---|---:|---:|
| 0 m (edge-mixed diagnostic; not acceptable primary evidence) | 612 | 33 |
| 10 m (more permissive geometry-only sensitivity) | 213 | 1 |
| **20 m (primary)** | **52** | **0** |

Source: [geometry_sensitivity.csv](results/geometry_sensitivity.csv). Even interpreting “one pixel” as the 10 m display grid cannot meet the required sample of **20** metered properties. Upsampling does not add roof detail. We did not relax the rules until a favorable correlation appeared.

The eligible roofs are **32 Public, 15 Commercial and 5 Office** by the city's `Struc_Type`, not a representative rental-home sample ([geometry diagnostics](results/geometry_diagnostics.json)). Four overlap P2's scored-home table; only one has an eligible curve, and its city structure class is Commercial while its P2 type is Multi-Family with 5+ Units. That source-label mismatch is another reason not to present the secondary comparison as validation of rental efficiency. This research does not repair or silently relabel the product's source table.

## Data and method

The choices were written down in [ANALYSIS_PLAN.md](ANALYSIS_PLAN.md) before roof snow extraction and correlations. Numeric coverage thresholds below are documented analyst choices unless a source is named.

1. **Events and imagery.** NOAA GHCN-Daily station **USC00200230**, **ANN ARBOR U OF MICH**, at **42.2981, −83.6639**, supplies SNOW and SNWD in millimeters. We reject quality-flagged/missing values. An event requires positive snowfall plus either snowfall and existing depth ≥25 mm, or a depth increase ≥25 mm. The threshold screens material events at roughly the depth record's inch precision. Scenes are 1–10 calendar days later and stop before the next event. Consecutive snowfall dates can leave no observation window. Dates refer to daily station reporting, not exact storm end times. [NOAA station list](https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt), [station file](https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/USC00200230.dly), [format/flags](https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt).
2. **Spatial support.** We read public COG windows from [Element 84 Earth Search](https://earth-search.aws.element84.com/v1), collection `sentinel-2-l2a`. Tile **17TKG** covers the cached city bounds; other overlapping tiles are excluded to avoid duplicates. [City footprint polygons](https://a2maps.a2gov.org/a2arcgis/rest/services/OSI/BuildingFootprints/FeatureServer/0) are read from the hashed cache. Footprint plan area is measured in UTM **EPSG:32617**. Keep area ≥1,500 m² and ≥3 native 20 m centers inside a 20 m inward buffer. B03 is 10 m, B11/SCL 20 m: bilinear B11 and nearest-neighbor SCL are aligned to B03. The output grid is 10 m, but effective SWIR detail remains 20 m. [Copernicus products](https://sentiwiki.copernicus.eu/web/s2-products).
3. **Snow and masks.** `NDSI = (B03 − B11)/(B03 + B11)`; snow is `NDSI > 0.4`. The conventional threshold is documented in the [NASA MODIS snow ATBD, pp. 15–16](https://modis.gsfc.nasa.gov/data/atbd/atbd_mod10.pdf). This is a transferred screening threshold, not a validated roof classifier or a reproduction of the full MODIS algorithm. Keep SCL **4, 5, 11** only; mask water, cloud/shadow/cirrus, uncertain and invalid samples, plus invalid reflectance. [Copernicus SCL table](https://sentiwiki.copernicus.eu/web/s2-processing). Roof coverage must be ≥80% clear with ≥3 clear native centers.
4. **Ground control and curve.** A **20–80 m ring** excludes all city buildings plus a **10 m margin**. Require ≥50% clear ring coverage and ≥25 clear 10 m samples. Each curve needs ≥2 clear dates separated by ≥2 days and ≥50% ground snow on its first clear date. Same-day satellites are averaged. The index is the trapezoidal integral of `(ground snow fraction − roof snow fraction)`, divided by observed duration; average eligible events equally. Positive means less persistent roof snow relative to ground. Do not extrapolate missing endpoints or call a single scene a melt speed. The ring controls common weather only partially; it does not control plowing, trees or surface materials.
5. **Real-meter join and target.** A footprint must lie >50% inside exactly one public benchmark property polygon, following [P1's existing spatial join](../../model/data_sources/footprints.py). Multiple roofs belonging to one meter property are area-weighted into **one** independent row. The primary test requires usable roofs represent ≥50% of that property's mapped roof area. P1's `building_targets.parquet` gives baseline-separated `heat_ccf`; intensity is `heat_ccf / gfa_ft2 / hdd_ref`, where `hdd_ref` uses **60°F**. Require `method=metered`, positive valid target, `gas_r2 ≥0.7` (P1's established gas-quality rule), and ≥12 valid gas months. We check monthly validity/outlier/other-fuel flags, rather than treating predicted dollars as meters. [Target derivation](../../model/heating_cooling/building_model.py), [public benchmarking source](https://utility.arcgis.com/usrsvcs/servers/1e3bed4240284b40b0c4fea6f8cb4522/rest/services/OSI/BenchmarkingPerformanceMetrics/FeatureServer/0).
6. **Inference and gate.** Spearman uses average tied ranks; p is a two-sided permutation test with add-one correction; uncertainty is a property-bootstrap percentile CI. These tests are implemented without adding SciPy to the project; [SciPy's Spearman documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html) also recommends permutation inference for small samples. GO requires **positive rho, p <0.05, n ≥20** on the primary real-meter test (user's gate). Predicted-cost comparisons cannot trigger GO. An empty or constant sample yields null statistics.

### Radiometric QA: an offset was already applied

Legacy COG metadata advertised an offset of **−0.1**, although `earthsearch:boa_offset_applied=True`. Applying that again produced implausible negative surface reflectances. We independently compared **100×100-pixel** windows in both B03 and B11 against the same acquisitions in Collection 1 on **2025-12-12, 2026-01-26 and 2026-02-15**. All **60,000 valid compared pixels** differed by exactly **1,000 DN**: the legacy COGs were already shifted. Final reflectance therefore uses **0.0001 × DN with no second offset** for these flagged legacy scenes. The correction changes optical measurements, not the zero-overlap geometry result.

The complete audit is [radiometry_audit.json](results/radiometry_audit.json), reproduced by [audit_radiometry.py](audit_radiometry.py). Final raster caches have a `radiometry-v2` suffix so the discarded double-offset pass cannot be reused. This metadata inconsistency is also reported in [Earth Search issue 66](https://github.com/Element84/earth-search/issues/66); the [provider documentation](https://github.com/Element84/earth-search#gainoffset-in-items-after-jan-25-2022) alone was insufficient, so the pixel comparison is the evidence for our correction.

## Figures

- [Scene with roof outlines and NDSI](figures/scene_ndsi.png): the usable scene covering the most eligible roofs, selected independently of energy values; detail shows the first usable footprint by ID.
- [Observed roof/ground curves](figures/melt_curves.png): examples with the most clear dates, including an explicitly excluded curve. Lines interpolate observations, not unobserved daily measurements.
- [Validation scatter](figures/validation_scatter.png): the metered panel explicitly has no points; the secondary panel shows its single actual pair. No trend line or invented CI.
- [Sample attrition](figures/sample_attrition.png): why large nominal roof area does not provide enough clean Sentinel-2 roof pixels.

## Confounders and limits

Roof color/material, pitch and snow sliding, rooftop equipment/exhaust, shading, attic ventilation, and whether a building is occupied can all affect snow persistence without measuring insulation. Wind redistribution, tree canopy and plowed parking/roads can bias the ground ring. Atmospheric correction, SCL snow/cloud confusion, geolocation and footprint vintage also matter. A roof can already be bare at the first clear image; this index is not a measured time-to-melt or direct thermal image.

P1's **4,788 monthly rows cover 2021–2023**, while imagery covers the later **2025–2026 winter** ([meter_summary.json](results/meter_summary.json)). Building use, occupancy, equipment or roofs may have changed. The heating target is fitted to real gas meters after separating baseline use; it is not directly metered roof heat loss. Raw winter gas includes hot water/cooking. Shared-property meters cannot be treated as separate rooftop observations. These temporal and ecological limits would remain even if the sample gate passed.

## Reproduce and handoff

From the repo root:

```bash
bash research/snow-melt/run.sh
```

This creates only `research/snow-melt/.venv`, its ignored `cache/`, and research outputs. It has its own [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock); `pyarrow` is included solely to read P1's parquet tables. The runner reads the existing root `data/` or sibling `../mhacks-integration` cache; absent caches are fetched from the public city services. It reads tracked model tables without importing model code. It makes no localhost requests and starts no server or demo process. **Port 8001 is untouched.** No secrets or keys are needed.

For local re-analysis after data collection, `cd research/snow-melt && uv run --frozen python analyze.py`. Tests: `uv run --frozen python -m unittest discover -p 'test_*.py'`. The test log, run metadata and result tables are under `results/`. Full imagery/cache files are excluded from git; exact scene IDs and asset URLs are committed. Public source revisions may change; compare hashes and manifests when reproducing later.

The **9:00 data-access checkpoint** and **10:00 validation checkpoint** were completed early; [run metadata](results/run_metadata.json) records completion before the **10:30 GO/NO-GO deadline**. Handoff branch: `p2/snow-melt` only. No API/web/agent/model files were changed. No one needs to integrate an endpoint; the Devpost owner can use the sentence above or omit the stretch. A future study would need finer roof imagery, contemporaneous meters and roof/occupancy controls.

PLAN §9 ties the optional SpaceX track to a successful signal **and Cursor usage**. This NO-GO does not qualify the feature; this branch's Codex execution does not establish Cursor usage. No sponsor-eligibility claim is made.

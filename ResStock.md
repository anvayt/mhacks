ResStock is a dataset from the US Department of Energy's National Renewable Energy Laboratory (NREL). It contains **simulated** homes, not metered ones. NREL builds a statistically representative sample of US housing, simulates each home's hourly energy use with a physics model (EnergyPlus), and publishes the results.

**What we use:** the 2024.2 release, Michigan baseline file (PLAN.md §7). It's about a 60 MB parquet on public S3 with no key needed.
- **Size:** 18,756 simulated Michigan homes, each with a sampling weight. About 14,341 of them are gas-heated.
- **Inputs (`in.*`):** what each home is like, including square footage, vintage (e.g. `<1940`, `1970s`), building type (single-family detached, multifamily 2–4 units, multifamily 5+, mobile home), stories, windows, insulation, air leakage, heating fuel, cooling type, county and weather file.
- **Outputs (`out.*`):** annual energy by end use and fuel. That includes `out.natural_gas.heating...`, `out.electricity.cooling...`, `out.electricity.heating...`, bill columns and emissions.

**How the project uses it:**
1. **The 10:30 PM checkpoint.** The bill model from PLAN.md was reproduced on it: R² 0.548 with public-record features, rising to 0.764 with 6 renter-answerable features.
2. **A fallback for small buildings.** Ann Arbor's real meter data only covers large buildings, at least 10,671 ft² in our training set. Most rentals are houses, duplexes and small multifamily, so ResStock provides heating and cooling intensities for those. The plan is to calibrate it against the real meters.
3. **Unit-size default.** The median 5+ unit multifamily apartment in ResStock is 854 ft². That gives a citable default unit size when a listing doesn't say.

**Caveats:**
- It's simulated, which is why the real Ann Arbor meters stay the primary source.
- It uses typical-year (TMY3) weather from 31 Michigan weather stations. Washtenaw County homes all use the "Ann Arbor Muni AP" weather file.
- NREL has flagged the 2024.2 bill columns as inconsistent, so dollars should come from our own pricing of kWh and therms, not its `out.bills` columns.
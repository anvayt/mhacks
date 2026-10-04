```yaml
id: P1-01
title: Research heating + cooling utility estimates per location (PRISM)
owner: P1
status: done
branch: p1/heating-cooling
type: research
checkpoint: 1:00 AM GO/NO-GO
depends_on: [P1-02, P1-03, P1-04, P1-05, P1-06, P1-07]   # umbrella: research done here, build split into subtasks
blocks: []                    # feeds the bill model's monthly/seasonal split (PLAN.md §6, §8 P1 list) and P2's /estimate
merges: []
services_touched:
  - /model
services_read:
  - PRISM Climate Group data (external, prism.oregonstate.edu)
  - NASA POWER API (external, fallback; PLAN.md §7)
  - NREL ResStock 2024.2 MI parquet (external; PLAN.md §7)
  - Ann Arbor benchmarking FeatureServer (external; PLAN.md §7)
contract_change: none
```

## Goal
Find and prototype a defensible way to get **one heating estimate and one cooling estimate (USD/yr, plus the underlying therms/kWh) for any location** (lat/lon in Michigan, Ann Arbor first). The output is a single number per location per end use, not a P10–P90 range. This gives the bill model a weather-driven heating/cooling baseline and the per-season split that renters expect (PLAN.md §1 note: per-season is what users expect for utility estimates).

## Research questions
"PRISM" could mean two things, and both may be useful. Check both:
1. **PRISM climate data** (Oregon State PRISM Climate Group): gridded 800 m / 4 km daily, monthly and 30-year normal temperatures.
   - Which product, resolution and license? Can we get it with no key and no login (bulk download or web service)? File format (BIL/GeoTIFF) and size for Michigan?
   - Derive heating degree-days and cooling degree-days at a point (base 65°F / 18.3°C) from daily or monthly normals. Compare with NASA POWER `HDD18_3`/`CDD18_3` for Ann Arbor (42.28, -83.74).
   - Is 800 m resolution worth it over NASA POWER (~50 km) for Ann Arbor-scale variation, or does it only matter across the state?
2. **PRISM, the Princeton Scorekeeping Method** (Fels, 1986): a degree-day regression `use = base + β_h·HDD(τ_h) + β_c·CDD(τ_c)` with fitted balance-point temperatures.
   - Can we fit it on Ann Arbor benchmarking monthly gas/electric (PLAN.md §6.3) to get typical heating slope and cooling slope per sq ft? This overlaps with the real-meter check, so reuse it.
3. **Turning degree-days into dollars:** pick one path and justify it.
   - (a) Heating/cooling intensity (kWh or therms per sq ft per degree-day) from ResStock end-use columns (`out.natural_gas.heating.*`, `out.electricity.cooling.*`) × local HDD/CDD × sq ft.
   - (b) PRISM-scorekeeping slopes from real meters × local normal HDD/CDD.
   - Prices: DTE gas and electric tariffs or EIA Michigan average prices (cite rate and date).
4. Per-season split: is HDD/CDD weighting by month good enough for "winter heating $ / summer cooling $"?

## Inputs (what I can rely on)
- Nothing from other tasks. All sources are public (PLAN.md §7). If PRISM can't be downloaded without a login, use NASA POWER and say so.

## Outputs (what I expose)
- `/model/research/heating_cooling.md`: findings, the chosen method, sources with URLs and access dates, and Ann Arbor numbers vs at least one independent check (EIA RECS Midwest or a real DTE bill).
- `/model/heating_cooling.py`: prototype `estimate_heating_cooling(lat, lon, sqft=None) -> {"heating": {"usd_yr", "therms_yr", "kwh_yr"}, "cooling": {"usd_yr", "kwh_yr"}, "hdd", "cdd", "source"}`. One value per field, no network calls at request time (cache grids or normals locally).
- A short recommendation: use this as a direct input to the bill model, as the monthly/seasonal splitter, or both.

## Steps
- [ ] Check access, license and format for PRISM normals (tmean/tmin/tmax, monthly and daily); note it in the research doc
- [ ] Compute HDD/CDD for Ann Arbor from PRISM and from NASA POWER; compare
- [ ] Read up on the Princeton Scorekeeping Method; decide if fitting it on the benchmarking data is worth the time tonight
- [ ] Choose the degree-day → energy → USD path (3a or 3b) and the tariff source
- [ ] Prototype `estimate_heating_cooling` and run it for 3–5 Ann Arbor points + 1–2 other Michigan cities
- [ ] Sanity check against an independent number (RECS or a real bill); write the research doc

## Done when
- [ ] `estimate_heating_cooling(42.28, -83.74)` returns one heating and one cooling estimate with cited inputs
- [ ] Research doc recommends a method with trade-offs, and lists every source with a URL
- [ ] Runs offline from cached data
- [ ] No secrets committed; every number has a cited source (PLAN.md §0 rules)

## Handoff
- Write-up with every number and source: `model/research/heating_cooling.md` (branch `p1/heating-cooling` @ ddbed97).
- Answer: seasonal heating/cooling $ per apartment from (1) the building's own real meters via PRISM change-point fits, (2) a blend of a meter-trained regression and meter-calibrated ResStock for unmetered complexes, (3) ResStock for small buildings. Weather at the 800 m PRISM cell; past year, typical year or forecast.
- Grounding: degree-days within 2.5% of NOAA 1991–2020 normals (U-M station) in every season. Held-out seasonal gas error is 7.4% (metered) and 28.3% (unmetered blend).
- Leakage: "uses X% more heat than peers for the weather" is a stable, real-meter-backed trait (94% persistent). Attributing it to air leakage is simulation-only.

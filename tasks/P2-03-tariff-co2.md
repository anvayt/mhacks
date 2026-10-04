```yaml
id: P2-03
title: CO₂ module (reuse P1's EIA pricing for heating/cooling $)
owner: P2
status: done
branch: p2/tariff-co2
type: build
checkpoint: 1:00 AM GO/NO-GO
depends_on: []
blocks: [P2-04, P2-05]
merges: []
services_touched:
  - /api
services_read:
  - DTE residential tariffs, EIA Michigan prices, EPA + eGRID factors (external, cited)
contract_change: none
```

## Team decision (Oct 3, ~9:45 PM)
**Reuse P1's EIA pricing** for heating/cooling dollars (`model/data_sources/eia.py`: EIA MI marginal gas $/ccf by month, EIA-861M electricity $/kWh); P2 does **not** build DTE tariffs. This task shrinks to CO₂ factors only (gas 5.306 kg CO₂/therm per EPA; electricity at the eGRID RFCM rate), applied to P1's gas_ccf / electric_kwh.

## Goal (original, superseded by the decision above)
Price energy ourselves (ResStock 2024.2's bill columns are flagged as inconsistent; PLAN.md §6.1) and convert energy to CO₂.

## Outputs (what I expose)
- `api/app/pricing.py`: `price(therms, kwh, months=None) -> usd` (DTE gas + electric, fixed charges, cited rate and date); `co2_kg(therms, kwh)` (gas 5.306 kg/therm per EPA; electricity at the eGRID RFCM rate); `seasonal_split(annual, hdd_by_month, cdd_by_month)` → winter/spring/summer/fall.

## Done when
- [x] Every rate and factor cited with a URL and date in code comments + `api/README.md`; unit tests for a known bill

## Handoff (Oct 4, ~3 AM; merged into `dev` at `fd8c31c` via `p2/merge-wave2`)
- **What changed:** `api/app/co2.py`: `co2_kg(gas_ccf, kwh)` and `co2_t(heating_cooling, bill)` → `{p10, p50, p90}` t/yr. Gas 5.306 kg/therm (EPA GHG Emission Factors Hub 2025), 1.037 therm/ccf (EIA), electricity 0.4403 kg/kWh (eGRID2023 RFCM); URLs in the module docstring and `api/README.md`. Wired into every `/estimate` and `/answer` body (`co2_t`) and `/fixes` (`co2_kg_saved`). Pricing per the team decision: P1's EIA prices, no DTE tariffs.
- **How to run:** `cd api && uv sync && uv run python scripts/fetch_footprints.py` (once), P1's model on :8001 (`make -C model dashboard`), `uv run uvicorn app.main:app --port 8000`; tests `uv run pytest -q` (377 pass). Tests: `tests/test_fixes.py` (known amounts).
- **Gaps:** heating + cooling energy only (base electricity, hot water not modelled); p10/p90 scale with the bill band (P1 gives one point estimate).
- **Next:** nothing blocking; P4 can text `co2_t.p50`.

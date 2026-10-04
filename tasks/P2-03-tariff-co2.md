```yaml
id: P2-03
title: Tariff + CO₂ module (energy → $ and CO₂)
owner: P2
status: todo
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

## Goal
Price energy ourselves (ResStock 2024.2's bill columns are flagged as inconsistent; PLAN.md §6.1) and convert energy to CO₂.

## Outputs (what I expose)
- `api/app/pricing.py`: `price(therms, kwh, months=None) -> usd` (DTE gas + electric, fixed charges, cited rate and date); `co2_kg(therms, kwh)` (gas 5.306 kg/therm per EPA; electricity at the eGRID RFCM rate); `seasonal_split(annual, hdd_by_month, cdd_by_month)` → winter/spring/summer/fall.

## Done when
- [ ] Every rate and factor cited with a URL and date in code comments + `api/README.md`; unit tests for a known bill

## Handoff (fill in when done; DEV_STRATEGY #1)
- What changed (files, endpoints)
- How to use it / run it
- Known gaps, TODOs, anything mocked that still needs to be real
- Who needs to act next (`blocks` owners)

```yaml
id: P1-02
title: Download ResStock MI and reproduce R² ≈ 0.55 / 0.76 (10:30 PM checkpoint)
owner: P1
status: done
branch: p1/heating-cooling          # shared P1 branch for P1-01..06 (one agent, sequential commits)
type: build
checkpoint: 10:30 PM
depends_on: []
blocks: [P1-05]
merges: []
services_touched:
  - /model
services_read:
  - NREL ResStock 2024.2 MI parquet (external; PLAN.md §7)
contract_change: none
```

## Goal
Get the NREL ResStock 2024.2 Michigan baseline file locally and reproduce the PLAN.md §6 feasibility numbers. This hits the 10:30 PM checkpoint ("model numbers reproduced") and gives P1-05 simulated heating/cooling end-use data for small buildings that the real meters don't cover.

## Inputs
- ResStock MI parquet (public S3, no key). URL in PLAN.md §7.

## Outputs
- `model/data_sources/resstock.py`: `download()` and `load(gas_only=True)`, cached under `model/data/raw/` (git-ignored)
- `model/scripts/reproduce_resstock.py`: prints R², MAE, P10–P90 width and coverage for both feature sets
- `model/results/resstock_reproduce.json`: the numbers

## Steps
- [ ] Download and cache the parquet
- [ ] Run the PLAN.md §6 starter script with a fixed seed; record results
- [ ] Also fit heating-only (`out.natural_gas.heating...`) and cooling (`out.electricity.cooling...`) targets for P1-05

## Done when
- [ ] `python -m model.scripts.reproduce_resstock` prints R² ≈ 0.55 / 0.76 (±0.03) and saves the JSON
- [ ] No secrets; numbers cite ResStock 2024.2

## Handoff
- Branch `p1/heating-cooling` (commit 242cb0b). `model/data_sources/resstock.py` (cached download), `model/scripts/reproduce_resstock.py`.
- Result (`model/results/resstock_reproduce.json`): bill R² **0.548** (public record) → **0.764** (+6 answers); P10–P90 coverage 0.78/0.74, so conformal calibration is still needed (PLAN §8).
- Also fitted gas-heating (R² 0.65 → 0.85) and cooling (0.13 → 0.16) targets.
- Next: none for the checkpoint; ResStock is developed further in P1-07.

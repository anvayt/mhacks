```yaml
id: P1-08
title: Merge p1/heating-cooling into dev
owner: P1
status: done
branch: p1/heating-cooling
type: merge
checkpoint: 1:00 AM GO/NO-GO
depends_on: [P1-02, P1-03, P1-04, P1-05, P1-06, P1-07]
blocks: []
merges: [P1-02, P1-03, P1-04, P1-05, P1-06, P1-07]
services_touched:
  - /model
services_read: []
contract_change: none
```

## Merge section
- Tasks merged: P1-02 … P1-07, all on `p1/heating-cooling`. Only `/model/` is touched, so no conflicts are expected.
- Historical integration plan used a cold build. **Do not repeat that during the demo:** PRISM rate limits and cross-machine training drift were observed. Use the copied built artifacts and isolated ports for verification.
- Rollback: revert the merge commit (nothing outside `/model`).

## Handoff
- **Original merge completed:** `p1/heating-cooling` through `82d314a` and `p1/leakage-model` at `f482992` merged into dev `4602d55`. The old todo status was stale; this task is complete.
- **Additive finishing pass:** `p1/finish` is pushed and fast-forwarded into dev at `ebb4631`; it adds capability-negotiated bill residuals, commitment scenarios, look-alike clouds, signed errors, no-AC handling, exact monthly prices and a year override. It does not rebuild or alter the running :8001 service. See [notes/P1.md](../../notes/P1.md) for supported scopes and open limits.
- **Evidence:** 75/75 exact legacy numeric-token HTTP comparisons, 16/16 Phase 2 live API checks, 63 model tests; artifact sign-off reproduces saved predictions exactly. Full API suite: 675 passed, 2 skipped. The suite includes current dev through `0ea901a`; original P1-08 completion and this finishing pass do not claim a live swap.

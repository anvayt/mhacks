```yaml
id: P1-08
title: Merge p1/heating-cooling into dev
owner: P1
status: todo
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
- Integration test: `python -m model.scripts.build_all` from a clean checkout, then `curl 'localhost:8001/hc/estimate?address=…'` returns 4 seasons.
- Rollback: revert the merge commit (nothing outside `/model`).

## Handoff

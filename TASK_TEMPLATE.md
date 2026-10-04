# Task template

Copy to `tasks/<id>-<short-name>.md` (e.g. `tasks/P2-03-estimate-endpoint.md`). One task = one agent = one branch.
Keep it short; an agent with zero context should be able to start from this file + PLAN.md.

---

```yaml
id: P2-03                     # <owner>-<nn>
title: Real /estimate endpoint
owner: P2                     # P1 model · P2 api · P3 web · P4 agent
status: todo                  # todo | in-progress | blocked | review | done
branch: p2/estimate-endpoint
type: build                   # build | merge | fix | research
checkpoint: 1:00 AM GO/NO-GO  # PLAN.md §8 checkpoint this must land before
depends_on: [P1-02, P2-01]    # tasks that must be done (or mocked) first
blocks: [P3-04, P4-02]        # tasks waiting on this one
merges: []                    # type: merge only — task ids being integrated
services_touched:             # dirs/services you WRITE to; must be your own unless type: merge
  - /api
services_read:                # things you call or import but must not edit
  - /model (artifacts/quantile_models.pkl)
  - Census geocoder (external)
contract_change: none         # none | additive | breaking (breaking needs all consumers' ack, DEV_STRATEGY #3)
```

## Goal
One or two sentences: what exists when this is done, and why the demo needs it.

## Inputs (what I can rely on)
- From `depends_on`: exact files, endpoints or fields, and whether they're real or mocked.

## Outputs (what I expose)
- Endpoints / files / functions others can use, with the PLAN.md §10 shape they follow.

## Steps
- [ ] ...
- [ ] ...

## Done when
- [ ] Concrete, checkable criteria (e.g. `curl -X POST /estimate -d '{"address": ...}'` returns §10 shape with real p10/p50/p90)
- [ ] Tests / contract check pass
- [ ] No secrets committed; every displayed number has a cited source (PLAN.md §0 rules)

## Merge section (type: merge only)
- Tasks merged: `merges` ids, and their branches
- Order of merging and conflicts expected (files touched by more than one task)
- Integration test: the end-to-end path that must work after the merge (e.g. link → card → one texted answer)
- Rollback: what to revert if the merge breaks the demo

## Handoff (fill in when done; DEV_STRATEGY #1)
- What changed (files, endpoints)
- How to use it / run it
- Known gaps, TODOs, anything mocked that still needs to be real
- Who needs to act next (`blocks` owners)

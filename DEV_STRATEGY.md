# Development flow
0. Don't touch work other agents are working, agents work on their own parts
1. Integration: when done, create a summary markdown for other agents to read to understand what was touched, what is needed to integrate with other parts (tasks are broken down in parallel, ensure independence until merge steps)
2. Ownership: each agent owns one dir (P1 `/model`, P2 `/api`, P3 `/web`, P4 `/agent`) on its own branch/worktree; never edit another's dir — request changes in `notes/requests.md` instead.
3. Contract is law: PLAN.md §10 API contract is the only coupling. Changing it needs a note in `notes/contract-changes.md` + all consumers ack'd; additive fields only after freeze.
4. Mocks first: consumers build against P2's mock JSON (`/api/fixtures/`), so no agent ever blocks on another.
5. Status board: each agent keeps `notes/<P#>.md` (doing / done / blocked-on / what I expose). Read all of them before starting a task.
6. Shared files (PLAN.md, `.env.example`, root configs): one owner (P2), others propose; small commits, rebase on main often, merge only when your tests + contract check pass.
7. Integration gate: at each §8 checkpoint, one agent runs the end-to-end demo path against real (not mock) services and logs breakages to the owning agent's notes.
8. Branches: `main` = docs/coordination only (PLAN, DEV_STRATEGY, TASK_TEMPLATE, `tasks/`, `notes/`); `dev` = integration code, must always run the demo; tasks branch `p<#>/<task>` off `dev` and merge back via a `type: merge` task. Never edit docs off `main` or code on `main`.
9. Worktrees: repo root stays on `main` as the shared coordination folder; each agent works in `git worktree add ../mhacks-<task> -b p<#>/<task> dev` and reads/writes `tasks/` + `notes/` via the root's absolute path (live, no merging). Agents on other machines commit notes straight to `main` and `git fetch` before each task.
10. Freeze: at 8 AM merge `dev` → `main` so the submitted repo has code + docs on one branch.

# Backup demo recorder

Six real Hidden Rent web/API beats at **1280×720** and **390×844**, sequentially. Default mode is a rehearsal: screenshots and a JSON pass/blocked/fail report, **no video**. `--record` is explicit; wait for the team lead's merged-web signal before using it. No mock estimate responses, route interception, or recorded session IDs are substituted.

Only `demo/video/` and the `demo-video` Makefile target belong to this branch. The web/API/model are unchanged.

## Run

Prepare Chromium once (Playwright is pinned; npx does not change the app's dependencies):

```bash
npx --yes --package=playwright@1.63.0 playwright install chromium
```

With the merged real web and API already running:

```bash
make demo-video
# Defaults: BASE_URL=http://localhost:3000 API=http://localhost:8000
BASE_URL=http://localhost:3005 API=http://localhost:8051 make demo-video
```

The web must have been started with `NEXT_PUBLIC_API_BASE_URL` matching `API` and `NEXT_PUBLIC_USE_MOCKS=0`. The recorder checks the origin of every browser POST. Use a dedicated API with throwaway `APP_DB`, `SESSIONS_DB`, and `CALIBRATION_DB`; the video adds fictional accounts and hypothetical bills. **Never point its setup at the team's real account database.**

The bill's `bill_signal` requires a saved property. For that beat, run the isolated API with **`USE_MOCKS=1`** (this mocks Photon onboarding only; estimates, projections and bill checks remain real), then give the recorder the same agent key through the existing env-file loader. This local-only setup does not open SMS links, send messages, opt in to reminders, or contact Calendar. Reserved fictional numbers `+12025550181` and `+12025550182` are used for the two viewports.

From this worktree's `api/`, with the team's canonical env file already present:

```bash
BASE_URL=http://localhost:3005 API=http://localhost:8051 \
  VIDEO_LOCAL_AUTH=1 USE_MOCKS=1 \
  uv run --env-file /Users/anvaytodkar/Code/mhacks/.env \
  bash ../demo/video/run.sh --dry-run
```

The agent key stays in Node, never browser storage. Only the throwaway user's bearer token enters localStorage. Auth responses, headers, codes, tokens, and storage are never logged or saved. Without local mock-auth setup, beat 5 is **blocked**, rather than silently downgrading to an anonymous bill with no saved signal.

**After the lead says merged dev is ready**, use the same command with `--record`, or:

```bash
BASE_URL=http://localhost:3000 API=http://localhost:8000 \
  VIDEO_LOCAL_AUTH=1 USE_MOCKS=1 \
  make demo-video VIDEO_ARGS=--record
```

The Makefile version needs `AGENT_API_KEY` already loaded securely into the process environment. Do not put the key in a command argument or committed file. It also needs an isolated mock-auth API, as above; port numbers alone do not guarantee isolation.

Outputs are under the git-ignored `demo/video/out/<mode>-<timestamp>/`:

- A viewport screenshot per step and on each failure.
- `report.json`: exact API-returned grade, range, rank, dollar gap, projection, bill uncertainty and map count, plus per-beat timing/status.
- Record mode only: `backup-desktop.webm`, `backup-mobile.webm`; matching `.mp4` when ffmpeg is installed. The file names become **`INCOMPLETE-*`** if any beat fails. The command exits nonzero for blocked/failed beats, including a missing early-signal assertion.

Optional environment settings: `VIEWPORTS=desktop` or `mobile` (default both), `HEADED=1`, `PAUSE_MS=3500` (record default; dry-run 500), and `TIMEOUT_MS=120000`. A browser run is sequential; `/compare` itself makes two model requests. Keep the isolated API's model concurrency at two and do not run another video process alongside it. Warm the API first so the recording spends its time on results rather than network waits.

The recorder neither starts nor stops the model. If `:8001` is unavailable, ask P1 to restore it. It never runs any model build or stop target.

## Beats and honesty

1. **1514 Morton Ave**: address → Gas → Single-pane → sign-in **Skip for now** → predicted grade/range → same-type rank. Equipment answers are labeled illustrative. Optional unit-size prompts are skipped, retaining public-record estimates.
2. **624 Church St vs 1022 S Forest Ave**: actual `/compare` winner, annual gap and uncertainty. No hard-coded $1,914 claim; current API results are recorded.
3. **2322 Arrowwood Trl**: Central AC → B locked. Both the API lock and one-grade span are asserted; the annual dollar range remains. If the live model changes this pick, the beat fails visibly.
4. **Morton windows**: model-priced window option → ghost marker, `projected_if_completed`, and background shift. The solid bars' visible contents must stay unchanged. Pending-model tips are never selected.
5. **Morton monthly bill**: save the answered session to a fictional local account; type **120 therms, February 1–28, 2026**. The caption calls it a **hypothetical bill**, and the assertions require an early signal and `verified: false`. This is not a real tenant bill or proof of savings. February is deliberate; last month's low heating load can make the comparison unusable.
6. **615 S Main St / The Yard**: current API grade A and score ≥98, footprint **50892**, real `/map`, and >30,000 city footprints; building focus → city zoom-out. Public-meter predictions allocate property data; they are not a unit's actual bill. Empty look-alikes remain empty.

Selectors use accessible role, label and visible text. Map-only structural checks read P3's existing `data-building-id` and `data-city-count` attributes; no styling classes or pixel clicks drive the recording. Captions are browser-only overlays and do not alter product code.

## Dry-run evidence (October 4, 2026, 03:59 EDT)

Tested web: isolated temporary integration of `p3/int-flow` **5735ccb**, `p3/int-board` **421dcfa**, and `p3/int-map-compare` **d8e555a**, served on `:3005`. API: dev **534f67a**, port `:8051`, isolated `/tmp/video-{a,s,c}.sqlite`, `USE_MOCKS=1`, model slots capped at two. These preview web merges are not in this deliverable branch.

Both viewport runs completed their diagnostics and exited **1**, as expected for an unavailable model:

| Beat | Desktop | Mobile | Evidence |
|---|---|---|---|
| Address → grade/rank | BLOCKED | BLOCKED | Address input/submission works; `/estimate` returns 503 `model_unavailable`. |
| Listing battle | BLOCKED | BLOCKED | Both card inputs/submission work; `/compare` returns 422 with per-listing `model_unavailable`. |
| Arrowwood grade lock | BLOCKED | BLOCKED | Address input/submission works; `/estimate` returns 503. |
| Window ghost | BLOCKED | BLOCKED | Depends on the unavailable real Morton session. |
| Monthly bill/signal | BLOCKED | BLOCKED | Depends on the unavailable real Morton session. |
| City map | BLOCKED | BLOCKED | The Yard `/estimate` returns 503. |

**No complete real beat has passed yet.** The browser successfully rendered both layouts, exercised real request/error paths, produced 19 screenshots plus the JSON report, and preserved the script's nonzero failure status. No success-path selectors after estimate, real bill signal, map loading, or final video are claimed as verified. Those must be rerun when P1 restores `:8001` and the web merge is approved. Syntax checks (`node --check`, `bash -n`) and `--help` pass. ffmpeg is installed, but final MP4 conversion awaits final recording.

Local evidence: `out/dry-run-2026-10-04T07-59-18-798Z/`. This directory is intentionally untracked. The durable status above does not depend on these local files surviving.

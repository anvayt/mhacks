# MHacks 2026: Hidden Rent

Hidden Rent shows the energy bill a rental listing doesn't. The plan, the API contract (§10) and every team rule live
in `PLAN.md` on `main`; this branch (`dev`) holds the code: `/model` (P1), `/api` (P2), `/agent` (P4), `/web` (P3, landing screen so far).

## Run the demo

The launcher needs the existing Python/Node dependencies and city cache. Prepare these once while online:

```bash
(cd api && uv sync && uv run python scripts/fetch_footprints.py)
(cd web && npm ci)
(cd agent && npm ci)
```

Point `MODEL_DIR` at the checkout with P1's **already-built** artifacts and matching processed data; it defaults to
`../mhacks-integration`. The launcher never builds or retrains the model.

```bash
AGENT_TERMINAL=1 make demo       # terminal chat, real API estimates, no iMessages
# In a second terminal, from the same checkout:
make demo-warm                  # five real estimates, one forecast session per weather cell
make demo-check                 # isolated API/model with outbound Python networking blocked
```

`make demo` starts or reuses the healthy model on `:8001`, then API `:8000`, web `:3000`, onboarding `:8787`, and
finally the agent. Open [the website](http://localhost:3000). Without both Photon credentials the agent always
uses terminal chat; with both credentials, plain `make demo` uses Photon. Set `AGENT_TERMINAL=1` to force terminal
chat. The terminal provider may download its `tuichat` binary from GitHub on first use, so launch it once online.

Environment variables already set in the shell take precedence over literal assignments in root `.env`, then
`agent/.env`. Files are parsed without executing shell code; `$VARIABLE` interpolation is not supported. No
credential values are printed. For example: `MODEL_DIR=/path/to/built/checkout AGENT_TERMINAL=1 make demo`.
A reused service retains its existing environment and code; the launcher does not reconfigure or restart it.
A listening port whose health check fails stops startup and is left alone.

Ctrl-C stops only process groups created by this launcher, including npm/tsx/Next children. Reused services stay
running. Logs, ownership records, and warm/check JSON responses go under git-ignored `data/demo/<run>/`; override
with `DEMO_LOG_DIR=/path/to/logs`. Agent terminal output is recorded with the system `script` utility. Runtime
prerequisites are Bash, curl, make, npm, ps, lsof, script, and the existing `api/.venv`; no packages are added.

`demo/addresses.txt` is the editable five-address list. `make demo-warm` makes requests sequentially, saves the
real responses, and reports annual heating/cooling costs and weather cells. It calls
`GET /forecast/{session_id}` once for the first returned session in each distinct model weather cell; later
listings in that cell are reported as already checked. Cell coordinates come from model inputs/location before
falling back to building coordinates. HTTP 404 is
reported as a skip, so this also works before the session/forecast branch is merged. Other failed responses or
invalid estimate shapes make the command fail. `API_BASE_URL` and `DEMO_ADDRESSES` can target another local API/list.
The saved JSON is diagnostic output; it is never replayed as an API fixture.

`make demo-check` starts fresh isolated processes on `:18000` and `:18001`, using this checkout's API cache and
`MODEL_DIR`'s existing model cache. Both Python processes receive a socket guard that rejects non-loopback DNS
and connections; an external `httpx` request verifies the guard first. A second real pass through the address list
reports working estimates and any blocked external hosts in `outbound.jsonl`. Changing proxies in this shell
cannot restrict the already-running model on `:8001`, which is why the check uses a separate model process and
leaves the demo/shared server untouched. Override `DEMO_CHECK_API_PORT` / `DEMO_CHECK_MODEL_PORT` if needed.

This is a Python-process offline simulation, not an OS firewall or certification of every endpoint. A forecast
404 is a skip, not a successful offline forecast. The forecast implementation on `p2/forecast` requests live
Open-Meteo daily forecasts on each call; warming its disk history alone does not remove that dependency. Cache
misses may still require Census geocoding/Census Reporter, city GIS, or the model's weather/EIA sources. The check
reports attempts even if an existing cached fallback succeeds. Photon/iMessage, tunnels, browser assets, dependency
installation, and first-use tuichat downloads still need separate network checks. No real messages are sent by
warm/check; validate the launcher with `AGENT_TERMINAL=1`.
Run `bash scripts/test-demo.sh` for the bounded cleanup, dotenv, and forecast-cell regression checks; these use no real model calls or messages.

## Run the whole thing

Needs Python 3 + [uv](https://docs.astral.sh/uv/), Node 20+, and on macOS `brew install libomp` (xgboost/lightgbm).
Secrets go only in git-ignored `.env` files; every variable name is in [`.env.example`](.env.example).

| Piece | Port | Set up once | Start |
|---|---|---|---|
| `/model` heating + cooling (P1) | 8001 | `make -C model setup && make -C model build && make -C model leakage` (first build downloads ~1 h of PRISM/ResStock/city/weather data, then works from `model/data/`; PRISM allows each grid twice a day per IP, so copy `model/data/raw/prism/` from a teammate instead of re-downloading) | `make -C model dashboard` |
| `/api` FastAPI (P2) | 8000 | `cd api && uv sync && uv run python scripts/fetch_footprints.py` (~30 s, city GIS into `/data/`) | `cd api && uv run uvicorn app.main:app --port 8000` |
| `/agent` iMessage agent (P4) | | `cd agent && npm ci && cp .env.example .env` (Photon creds for real iMessage) | `cd agent && npm run agent` (no creds or `AGENT_TERMINAL=1`: terminal chat) |
| onboarding page (P4) | 8787 | same as `/agent` | `cd agent && npm run onboard` |
| `/web` Next.js (P3) | 3000 | `cd web && npm ci` | `cd web && npm run dev` |

`make -C model build` (and `leakage`) rewrite committed files under `model/data/processed/` and `model/results/`
with this machine's retrain. Don't commit them (P1 owns them), but keep them while you serve from this machine: the
server reads them together with the git-ignored models in `model/artifacts/` trained in the same build, so dropping
only one side mixes two trainings.

Start order: model, then api, then agent / web. `/api` calls the model over HTTP at `MODEL_BASE_URL` (default
`http://localhost:8001`); the agent calls `/api` at `API_BASE_URL` and the web form at `NEXT_PUBLIC_API_BASE_URL`
(both default `http://localhost:8000`; `/api` allows the browser origin in `WEB_ORIGINS`, default `http://localhost:3000`).
The web "start by iMessage" link opens P4's onboarding page (`NEXT_PUBLIC_ONBOARD_URL`, default `http://localhost:8787`).

```bash
curl -s localhost:8000/estimate -H 'content-type: application/json' -d '{"address": "912 Mary St, Ann Arbor, MI"}'
curl -s localhost:8000/estimate -H 'content-type: application/json' \
  -d '{"url": "https://www.zillow.com/homedetails/1514-Morton-Ave-Ann-Arbor-MI-48104/12345_zpid/"}'
```

Tests (each from the repo root):

```bash
make -C model test                       # needs make -C model build and make -C model leakage first
(cd api && uv run pytest -q)             # /estimate end-to-end tests skip unless the model server is up
(cd agent && npm test && npm run typecheck)
(cd web && npm run build)                # type-checks /web; it has no tests yet
```

`POST /estimate` today returns real `building` fields and heating + cooling `bill` p50s (annual, per season, per month,
from P1's model; `heating_cooling` has P1's full answer). Not yet filled (null/empty): `session_id`, `bill` p10/p90,
`co2_t`, score/grade/percentiles/hidden rent, badges, questions. Errors are 422
`{"detail": {"code", "message"}}` with codes `missing_input`, `needs_address` (+ `hint`), `not_found` (outside Ann
Arbor), `not_a_home`, `bad_unit_sqft` (outside 100–10,000); 503 when the model or the address lookup is down or errors.

## Research (`results/` on `main`)

Start with `results/pivot-round2/00-synthesis.md` (why Hidden Rent). `results/SUMMARY.md` is the earlier, superseded "Clean Hours" plan.

| Folder | Contents |
|---|---|
| `year-research/` | Past MHacks winners, how they won, and what judges said (2020–2025) |
| `main-and-fun-tracks/` | One advocate per track, plus the judge's verdict (`07`) |
| `sponsor-tracks/` | One advocate per sponsor track, plus the judge's verdict (`13`) |
| `final-debate/` | Full transcript of the main vs fun vs sponsor debate |
| `ideation/` | An earlier set of alternative ideas |

Every file opens with the prompt its agent was given, and every factual claim cites its source.

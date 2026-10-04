# MHacks 2026: Hidden Rent

Hidden Rent shows the energy bill a rental listing doesn't. The plan, the API contract (§10) and every team rule live
in `PLAN.md` on `main`; this branch (`dev`) holds the code: `/model` (P1), `/api` (P2), `/agent` (P4), and the integrated `/web` (P3).

## Make commands

Everything runs from the `dev` branch, at the repo root.

| Command | What it does |
|---|---|
| `make install` | One-time setup: Python/Node deps, city GIS, trained model. Put `model-data.zip` (from the team share) in the repo root first, or it downloads (~1 h) and trains. |
| `make demo` | Start model, API, web, onboarding and the chat agent. |
| `make demo-warm` | Pre-warm demo estimates and maps (second terminal). |
| `make demo-warm-city` | Pre-warm whole-city caches (~2 min, once). |
| `make demo-public` | Public HTTPS tunnels for the demo (needs `brew install cloudflared`). |
| `make demo-check` | Offline check of API + model. |
| `make data-bundle` | Write `model-data.zip` (data + trained model) to share with the team. |
| `make -C model build` | Retrain the model on this machine. |

## Run the demo

```bash
AGENT_TERMINAL=1 make demo       # terminal chat, real API estimates, no iMessages
# In a second terminal, from the same checkout:
make demo-warm                  # estimates + each map, forecast per weather cell, city layer
make demo-warm-city             # whole-city caches for judges' own addresses (~2 min, once per checkout)
make demo-check                 # isolated API/model with outbound Python networking blocked
```

`make demo-warm-city` (`api/scripts/warm_city.py`) warms what a judge's **own** Ann Arbor address can hit
beyond the five demo addresses, one request at a time with a 0.3 s pause: for each of the 4 model weather cells
holding a scored home, P1's `/hc/estimate` (typical and forecast) and `/hc/weather?mode=forecast` (timed; GETs
only, the `:8001` process is never started or restarted), plus that cell's Open-Meteo 1991–2020 history and
last-good 7-day forecast; the TIGERweb outline of all 145 block groups `/map` can hit (scored homes' block groups
plus every block group touching the city's bounds); and the ACS table if missing. It writes this checkout's
git-ignored `data/`, so run it from the `make demo` checkout. Only the Census geocoder stays cold: one
~0.3–0.9 s call per never-seen address. Measured Oct 4 on 12 new addresses across the city (N Campus area,
Burns Park, Water Hill, Ann Arbor Hills, south side, west side): first `/map` 0.21–0.69 s → 0.04–0.06 s,
first `/forecast` in a new cell up to 2.7 s → 0.6 s (the live Open-Meteo forecast), `/estimate` 0.5–1.2 s
(geocoder) either way, 0.17–0.23 s on a repeat.

`make demo` starts or reuses the healthy model on `:8001`, then API `:8000`, web `:3000`, onboarding `:8787`, and
finally the agent. Open [the website](http://localhost:3000). Without both Photon credentials the agent always
uses terminal chat; with both credentials, plain `make demo` uses Photon. Set `AGENT_TERMINAL=1` to force terminal
chat. Terminal mode uses the agent's plain-text prompt and does not initialize Photon or send messages.
The supervisor builds the web and runs `npm run start` in production, including after public URL changes;
development StrictMode must not double the demo's board requests.

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
404 is a skip, not a successful offline forecast. Forecast requests try live Open-Meteo first, then use a saved
last-good response with `stale_as_of` when at least three future days remain. Warming history alone is insufficient. Cache
misses may still require Census geocoding/Census Reporter, city GIS, or the model's weather/EIA sources. The check
reports attempts even if an existing cached fallback succeeds. Photon/iMessage, tunnels, browser assets, dependency
installation still need separate network checks. No real messages are sent by
warm/check; validate the launcher with `AGENT_TERMINAL=1`.
Run `bash scripts/test-demo.sh` for the bounded cleanup, dotenv, and forecast-cell regression checks; these use no real model calls or messages.

## Run the demo publicly

On demo morning, from the same checkout in each terminal:

1. Have P1 bring up the **already-built** model on `:8001`; confirm `curl http://localhost:8001/hc/answers`.
2. Set private `AGENT_API_KEY` in `.env` (also used by the agent), real Photon credentials, and `USE_MOCKS=0`.
   Run `AGENT_TERMINAL=1 make demo` for a safe rehearsal; use plain `make demo` for the team's authorized live
   iMessage agent. Keep that terminal open.
3. In another terminal, run `make demo-public`. If needed, install its only additional prerequisite with
   `brew install cloudflared`. It starts three account-free HTTPS tunnels, writes **URLs only** to git-ignored
   `data/demo/public.env`, and asks the existing demo supervisor to restart its API, web, and onboarding with them.
   It never restarts the model or agent. It prints the judge URL and terminal QR. **Reprint P4's `/card`** at the
   printed onboarding URL each time: quick-tunnel URLs change on restart (NEW_CHANGES §13 R4).
   **If the judge URL returns HTTP 530** (or the launcher fails its reachability check), the network is blocking
   Cloudflare's edge port 7844 (both `--protocol quic` and `http2` use it). Ctrl-C, run `make demo-public-check`
   (TCP reachability of `region1.v2.argotunnel.com:7844` and `localhost.run:22` only; it opens no tunnel and
   prints which provider will work), then either `TUNNEL=localhostrun make demo-public` or switch the laptop to
   a phone hotspot and rerun `make demo-public`. `TUNNEL=localhostrun` uses `ssh -R` over port 22 to
   [localhost.run](https://localhost.run) (no account; first run adds its host key to `~/.ssh/known_hosts`), with
   the same three URLs → `public.env` → supervisor restart → judge URL + QR flow; its `https://<id>.lhr.life`
   URLs also change on every run.
4. Run `make demo-warm`, `make demo-warm-city`, then `make demo-check`. Warming reports timings for every estimate and session map,
   one forecast per weather cell, and `/city` once. Maps warm the cached TIGERweb block-group outline. Check also
   exercises these routes under the existing isolated-process outbound guard; a model-down failure is not a pass.
5. Open the printed **judge URL on a phone**, test the listing and sign-in flows, and keep the launch terminals open.

`make demo-public` can also start API/web/onboarding itself when all three ports are free. It does not start the
model or agent. Ctrl-C then closes its tunnels and those three owned services. When connected to `make demo`,
Ctrl-C instead asks that supervisor to restore local URLs, leaving its services and agent running. Tunnels use
loopback origins. Reused or independently started services are never restarted: stop them through their own
terminals, then use this checkout's `make demo`. Commands use a cooperative mailbox, **never stored PID files as
permission to kill**. A crashed supervisor may leave `data/demo/services.lock` (or `public.lock`); inspect the
ports/old launcher first, then remove only the stale directory. A second public launcher is refused.

The API uses a single-process in-memory public budget: **120 expensive requests per IP per minute** by default
(configure `RATE_LIMIT_PER_MIN`), and
**3 bill photos per IP per 10 minutes** (each photo runs two paid vision calls). These are demo operating budgets,
not model accuracy thresholds. Estimate, answer, compare, calibrate, map, forecast and model-calling property,
projection and fixes routes share the budget; web-login starts also count. Read-only suggestions and current
position reads do not count, but position requests with `catalog_ids` do because they calculate a projection. `429` uses
`detail.code=slow_down`, renter-facing copy and `Retry-After`. Only a constant-time match to a **nonempty**
`AGENT_API_KEY` bypasses rate limits; bearer sign-in does not. The byte cap applies even to agent requests:
**8 MiB base64 photo**, **8 MiB + 64 KiB total JSON**, counted while streaming regardless of Content-Length.
Oversize requests get `413 bill_too_large`, inviting a smaller photo or typed numbers. Budgets reset on restart
and are per API worker; use the launcher's single worker for this demo, not a distributed deployment.

CORS allows listed origins only, never wildcard credentials. The public launcher adds the web tunnel to
`WEB_ORIGINS`, sets `WEB_ORIGIN` for Calendar's return link, and enables `PUBLIC_TUNNEL=1`. Only then does the
API trust Cloudflare's `CF-Connecting-IP`, and only from its loopback peer; it runs with `--no-proxy-headers`
so untrusted forwarded headers cannot change that trust check. Do not expose that loopback socket through
another proxy while this mode is enabled. With `TUNNEL=localhostrun` the launcher writes
`PUBLIC_TUNNEL=localhostrun` instead: localhost.run would pass a visitor's own `CF-Connecting-IP` through, so no
client-IP header is trusted and **all public visitors share one budget** (the agent's key still bypasses it). If
judges see "slow down", set a higher `RATE_LIMIT_PER_MIN` in `.env` before `make demo`. `/health` stays HTTP 200 for API liveness and returns
`{"status":"ok"|"degraded","model":{"available":true|false}}` after a two-second `/hc/answers` check.

Public tunnels do **not** fix onboarding `/join` abuse: that separate `:8787` route is P4-owned and still needs
its NEW_CHANGES §13 R5/D17 cap before unrestricted sharing. Real Google OAuth also needs a matching registered
redirect URI; random API tunnel URLs do not update Google Console automatically. Tunnel HTTP checks establish
reachability, not successful model estimates or merged web screens. The branch starts at dev `534f67a`; use the
integrated web and a working model for the final phone rehearsal. Nothing in warm/check/public sends texts,
allowlists phones, or creates Calendar events.

### Public-demo verification (Oct 4, 2026)

`cd api && uv run pytest -q`: **588 passed, 2 skipped** (the opt-in integration checks), one existing
Starlette/httpx deprecation warning. `bash scripts/test-demo.sh` passes dotenv safety, owned-group cleanup,
selective restart, per-session map warming and per-weather-cell forecast warming. Shell syntax and diff checks pass.

`API_BASE_URL=http://localhost:8050 make demo-warm`, with the real model after P1 restored `:8001`:

| Address | Annual heating + cooling p50 | Estimate | Map |
|---|---:|---:|---:|
| 2322 Arrowwood Trl | $470 | 0.183 s | 0.667 s |
| 624 Church St | $265 | 0.247 s | 0.233 s |
| 1022 S Forest Ave | $2,179 | 0.213 s | 0.190 s |
| 615 S Main St | $143 | 0.230 s | 0.235 s |
| 1514 Morton Ave | $2,117 | 0.182 s | 0.228 s |

One forecast warmed in **1.559 s**; four same-cell requests were skipped as intended. `/city` warmed in
**0.025 s** (its first load was 1.230 s). Result: **5 estimates, 5 maps, 1 forecast, city; 0 failures**.
The earlier model-down pass honestly returned five `503 model_unavailable`; no model process was started,
stopped, rebuilt or replaced by this task.

`make demo-public` was run with installed cloudflared and isolated application databases. All three local
services started, then restarted with the captured public settings. Cloudflare edge TCP connections on
port 7844 timed out (`DialContext ... i/o timeout`), so the web URL returned **HTTP 530** and the launcher failed its
reachability check. Generated URLs (now closed, **not working judge URLs**):

- Web: `https://relations-gasoline-profits-professor.trycloudflare.com`
- API: `https://oem-governor-driver-investment.trycloudflare.com`
- Onboarding: `https://disks-movement-bobby-vpn.trycloudflare.com`

Runtime logs: `/tmp/mhacks-public-live/`; successful warm responses: `/tmp/mhacks-public-warm-restored/`.
Cleanup removed its tunnels, listeners on 8000/3000/8787, locks and public.env while leaving the separately
owned 8050 API intact. A second local-only lifecycle test used the supervisor mailbox to apply public settings
and restore local settings; CORS changed to the public origin and back, with the three services still running.
No `/join`, Photon send, Google event or real-phone operation was called. A working tunnel network and P4's
onboarding abuse cap remain required before the final public phone rehearsal.

## Run the whole thing

Needs Python 3.12, Node 20+, and on macOS `brew install libomp` (xgboost/lightgbm). [uv](https://docs.astral.sh/uv/) is optional.

Setup is `make install` (see [Make commands](#make-commands)).
Secrets go only in git-ignored `.env` files; every variable name is in [`.env.example`](.env.example).

| Piece | Port | Set up once | Start |
|---|---|---|---|
| `/model` heating + cooling (P1) | 8001 | `make install` | `make -C model dashboard` |
| `/api` FastAPI (P2) | 8000 | `make install` | `cd api && uv run uvicorn app.main:app --port 8000` |
| `/agent` iMessage agent (P4) | | `make install` (Photon creds for real iMessage go in `agent/.env`) | `cd agent && npm run agent` (no creds or `AGENT_TERMINAL=1`: terminal chat) |
| onboarding page (P4) | 8787 | same as `/agent` | `cd agent && npm run onboard` |
| `/web` Next.js (P3) | 3000 | `make install` | `cd web && npm run dev` |

Model build outputs (`model/artifacts/`, `model/data/processed/`, the generated files in `model/results/`) are
git-ignored and travel in `model-data.zip` as one set: the server reads them together, so never mix files from two
trainings. To retrain on this machine: `make -C model build`.

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
make -C model test                       # needs make install (builds the model) first
(cd api && uv run pytest -q)             # /estimate end-to-end tests skip unless the model server is up
(cd agent && npm test && npm run typecheck)
(cd web && npm run build)                # type-checks /web; it has no tests yet
```

`POST /estimate` returns a saved `session_id`, building fields, heating + cooling bill ranges, CO₂, predicted
score/grade/percentiles/hidden rent, badges and answerable questions (`heating_cooling` contains P1's full answer).
`POST /answer` updates that session; `GET /session/{id}` resumes it. The web, map, comparison, monthly bill and
saved-home flows use the real API. Unmodeled commitment effects and pending look-alikes stay empty rather than
inventing numbers. See `api/README.md` for the endpoint contract and `notes/integration.md` on `main` for final
verification and remaining limits. Errors are 422
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

## ASI:One agent

Hidden Rent also has an isolated Fetch.ai chat-protocol uAgent in [`asi-agent/`](asi-agent/README.md). It uses an Agentverse mailbox and ASI:One only for intent parsing; every bill, grade and savings figure comes from the existing API. It does not launch or manage the demo stack.

```bash
API_BASE_URL=http://localhost:8000 make asi-agent
make asi-agent-test
```

Load existing keys through `ASI_ENV_FILE` (default `/Users/anvaytodkar/Code/mhacks/.env`): `AGENTVERSE_API_KEY`, `ASI_ONE_API_KEY`, `AGENT_API_KEY`. Set `WEB_BASE_URL` and `ONBOARD_URL` when public URLs are available; until then report links are labelled local previews. See [verification status](asi-agent/VERIFICATION.md), the agent address and exact ASI:One test steps before claiming sponsor integration.

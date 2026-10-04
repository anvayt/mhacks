# MHacks 2026: Hidden Rent

Hidden Rent shows the energy bill a rental listing doesn't. The plan, the API contract (§10) and every team rule live
in `PLAN.md` on `main`; this branch (`dev`) holds the code: `/model` (P1), `/api` (P2), `/agent` (P4), `/web` (P3, landing screen so far).

## Run the whole thing

Needs Python 3 + [uv](https://docs.astral.sh/uv/), Node 20+, and on macOS `brew install libomp` (xgboost/lightgbm).
Secrets go only in git-ignored `.env` files; every variable name is in [`.env.example`](.env.example).

| Piece | Port | Set up once | Start |
|---|---|---|---|
| `/model` heating + cooling (P1) | 8001 | `make -C model setup && make -C model build` (first build downloads ~1 h of PRISM/ResStock/city/weather data, then works from `model/data/`) | `make -C model dashboard` |
| `/api` FastAPI (P2) | 8000 | `cd api && uv sync && uv run python scripts/fetch_footprints.py` (~30 s, city GIS into `/data/`) | `cd api && uv run uvicorn app.main:app --port 8000` |
| `/agent` iMessage agent (P4) | | `cd agent && npm ci && cp .env.example .env` (Photon creds for real iMessage) | `cd agent && npm run agent` (no creds or `AGENT_TERMINAL=1`: terminal chat) |
| onboarding page (P4) | 8787 | same as `/agent` | `cd agent && npm run onboard` |
| `/web` Next.js (P3) | 3000 | `cd web && npm ci` | `cd web && npm run dev` |

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
make -C model test                       # needs make -C model build first
(cd api && uv run pytest -q)             # /estimate end-to-end tests skip unless the model server is up
(cd agent && npm test && npm run typecheck)
(cd web && npm run build)                # type-checks /web; it has no tests yet
make -C model leakage && make -C model test   # P1-09 leakage tests need its model trained first
```

`POST /estimate` today returns real `building` fields and heating + cooling `bill` p50s (annual, per season, per month,
from P1's model; `heating_cooling` has P1's full answer). Not yet filled (null/empty): `session_id`, `bill` p10/p90,
`co2_t`, score/grade/percentiles/hidden rent, badges, questions. Errors are 422
`{"detail": {"code", "message"}}` with codes `missing_input`, `needs_address` (+ `hint`), `not_found` (outside Ann
Arbor), `not_a_home`; 503 when the model or the address lookup is down.

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

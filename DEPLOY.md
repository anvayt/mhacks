# Deploying Hidden Rent (no laptop required)

| Piece | Where | URL |
|---|---|---|
| Website (`web/`, Next.js) | Vercel project `hidden-rent-mhacks` (team "anvayt's projects") | https://hidden-rent-mhacks.vercel.app |
| API + P1 model (`api/`, `model/`) | Fly app `hidden-rent-api-mhacks`, region `ord` | https://hidden-rent-api-mhacks.fly.dev |
| iMessage agent + onboarding page + ASI:One agent (`agent/`, `asi-agent/`) | Fly app `hidden-rent-agents-mhacks`, region `ord` | https://hidden-rent-agents-mhacks.fly.dev (QR card: `/card`) |

Everything deploy-related lives in `deploy/`: one Dockerfile, one `fly.toml` and one bash supervisor
(`*-start.sh`, exits when any child dies so Fly restarts the machine) per Fly app, plus `stage.sh`
(builds the context and runs `fly deploy`) and `secrets.sh` (pushes secrets from `.env`).

## Redeploy (one command each)

```sh
# API: needs the trained model (model/artifacts, model/data, model/results) and data/ caches, which are not in git.
MODEL_SRC=/path/to/checkout-with-trained-model DATA_SRC=/path/to/mhacks/data bash deploy/stage.sh api --yes
# Agents (iMessage + onboarding + ASI:One)
bash deploy/stage.sh agents --yes
# Website
cd web && vercel deploy --prod --yes
```

`stage.sh` copies the repo (minus `.git`, `.env*`, `node_modules`, venvs, `web/`) to a temp dir, adds the
trained files for `api`, writes an explicit `.dockerignore`, refuses to continue if a `.env` landed in the
context, then runs `fly deploy --remote-only` from there. Env (non-secret) lives in `deploy/*.fly.toml`.
The model runs with the exact pins its pickles were trained with (`deploy/model-requirements.txt`, Python
3.14.6); the API keeps its own Python 3.12 venv via `uv`.

Vercel production env: `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_ONBOARD_URL` (`vercel env ls production`).
The project was created and deployed from `web/` with the CLI (`vercel link --yes --project hidden-rent-mhacks`
in `web/`), not from a Git integration; `web/.vercel/` is local link state and is git-ignored.

## Secrets

Never commit or print values. `bash deploy/secrets.sh /path/to/.env` reads `PHOTON_PROJECT_ID`,
`PHOTON_PROJECT_SECRET`, `XAI_API_KEY`, `AGENTVERSE_API_KEY`, `ASI_ONE_API_KEY` from the file, generates a
fresh shared `AGENT_API_KEY` for both apps, and sets `ASI_AGENT_SEED` from `asi-agent/.runtime/agent.seed`
(same seed = same Agentverse address `agent1qth4ez7uam253n3aeuq9c56pnruw0e99vznlx3pupvahcxd84pfsghrfyum`).
It pipes everything into `fly secrets import --stage`; the next deploy (or `fly secrets deploy -a <app>`)
applies them.

- Rotate everything: edit `.env`, rerun `secrets.sh`, then `fly secrets deploy -a hidden-rent-api-mhacks && fly secrets deploy -a hidden-rent-agents-mhacks`.
- Rotate one: `fly secrets set NAME=value -a <app>` (type it into a prompt, not shell history: `read -s v; fly secrets set NAME="$v" -a <app>`).
- The two apps must share the same `AGENT_API_KEY`; `secrets.sh` guarantees that.
- Not set on purpose: `ELEVENLABS_API_KEY`, `XAI_API_KEY_BACKUP`, `DATABASE_URL`, `GOOGLE_*` (calendar stays in demo mode).

## Operate

```sh
fly status -a hidden-rent-api-mhacks            # machines + health checks
fly logs -a hidden-rent-api-mhacks              # live logs (both apps: agents app shows "Spectrum started" and the ASI mailbox registration)
fly releases -a hidden-rent-api-mhacks          # release history
fly deploy -a hidden-rent-api-mhacks --image <image from fly releases>   # roll back to an earlier image, no rebuild
fly machine restart <id> -a hidden-rent-api-mhacks                        # data on the /data volume persists
fly ssh console -a hidden-rent-api-mhacks       # shell in the machine; sqlite files under /data
```

Persistent state: volume `data` (1 GB) on each app, mounted at `/data`: `sessions.sqlite`, `app.sqlite`,
`calibrate.sqlite` (API); `agent-reminder-receipts.json` and the ASI agent's runtime dir (agents). The
repo's `data/` caches (footprints, geocodes, Open-Meteo, TIGERweb outlines) are baked into the API image;
new cache entries written at runtime live on the machine's ephemeral disk.

Warm the public API after a deploy (same scripts as the local demo):

```sh
API_BASE_URL=https://hidden-rent-api-mhacks.fly.dev make demo-warm
API_BASE_URL=https://hidden-rent-api-mhacks.fly.dev MODEL_BASE_URL=https://hidden-rent-api-mhacks.fly.dev make demo-warm-city
```

Rate limiting on Fly keys visitors by the `Fly-Client-IP` header (set and overwritten by Fly's proxy) when
`FLY_APP_NAME` is present (`api/app/public_guard.py`); `RATE_LIMIT_PER_MIN=600` in `deploy/api.fly.toml`.

## Cost (approximate, Fly list prices)

- API: shared-cpu-2x, 2 GB RAM, always on: about $11/month.
- Agents: shared-cpu-1x, 1 GB RAM, always on: about $6/month.
- Two 1 GB volumes: about $0.30/month. Outbound bandwidth: $0.02/GB.
- Vercel Hobby: $0.

About $18/month, under $1/day. Remote builds use Fly's free builder.

## Destroy after the hackathon

```sh
fly apps destroy hidden-rent-api-mhacks --yes      # also deletes its volume
fly apps destroy hidden-rent-agents-mhacks --yes
vercel project rm hidden-rent-mhacks --yes
```

Only one process may hold the ASI agent identity: when the Fly agents app is up, stop any local
`python asi-agent/agent.py`; when running locally again, scale the Fly app down first
(`fly scale count 0 -a hidden-rent-agents-mhacks`).

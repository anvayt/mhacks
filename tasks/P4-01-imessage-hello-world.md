```yaml
id: P4-01
title: Photon iMessage hello-world + judge QR onboarding page
owner: P4
status: in-progress
branch: p4/imessage-hello-world
type: build
checkpoint: 10:30 PM (a judge's phone can text the agent)
depends_on: []                # Photon account + project credentials (human step, see Steps)
blocks: [P4-02]               # interview loop over iMessage builds on this agent
merges: []
services_touched:
  - /agent
services_read:
  - Photon Spectrum Cloud (spectrum-ts 12.10.1, @spectrum-ts/imessage)
  - Photon management API https://spectrum.photon.codes (POST /projects/{id}/users, GET /users/{id}/redirect)
contract_change: none
```

## Goal
A Spectrum iMessage agent that answers anyone who texts it, plus a QR-code onboarding page so a judge can allowlist their own number and open Messages with the first text pre-filled. This is the PLAN.md §8 10:30 PM checkpoint for P4: "A judge's phone can text the agent".

## Inputs (what I can rely on)
- Photon free plan: shared line pool, up to 10 allowlisted users, DMs only (no groups). Unregistered numbers get `Target not allowed for this project`.
- No dependency on `/api` yet; the hello-world never says a number (PLAN.md §0 rule 4).

## Outputs (what I expose)
- `/agent/src/agent.ts`: the agent loop (`npm run agent`). Replies to every inbound DM with a short Hidden Rent welcome. Falls back to Spectrum's terminal provider when `AGENT_TERMINAL=1` or Photon credentials are missing (mock switch, DEV_STRATEGY #4).
- `/agent/src/onboard.ts`: onboarding server (`npm run onboard`, port 8787): `GET /` phone form, `POST /join` → Photon `POST /users` (type `shared`) → 302 to Photon's SMS deep link, `GET /qr.svg` QR of `PUBLIC_URL`. `USE_MOCKS=1` skips Photon and redirects to a fake `sms:` link.
- `/agent/scripts/add-user.ts`: `npm run add-user -- +15551234567 Name` to allowlist team phones.
- Env names (in `/agent/.env.example`): `PHOTON_PROJECT_ID`, `PHOTON_PROJECT_SECRET` (PLAN.md §10), plus agent-only `PUBLIC_URL`, `ONBOARD_PORT`, `USE_MOCKS`, `AGENT_TERMINAL`.

## Steps
- [ ] Human: create a Photon account + project at https://app.photon.codes, copy Project ID + Secret into `/agent/.env`
- [ ] Agent loop on `spectrum-ts` cloud iMessage, with the terminal fallback
- [ ] Onboarding server: form → create shared user → redirect into Messages; QR at `/qr.svg`
- [ ] `add-user` script; allowlist the 4 team phones
- [ ] Unit tests for phone normalization and the onboarding handler (mocked Photon)
- [ ] Expose the onboarding server publicly (tunnel) so a phone off the laptop can open it

## Done when
- [ ] A phone that has never texted the agent scans the QR, enters its number, taps Send in Messages, and gets the welcome reply
- [ ] `npm test` passes; `npm run typecheck` passes
- [ ] No secrets committed (`.env` git-ignored; only `.env.example` names)

## Handoff (fill in when done; DEV_STRATEGY #1)
- What changed (files, endpoints)
- How to use it / run it
- Known gaps, TODOs, anything mocked that still needs to be real
- Who needs to act next (`blocks` owners)

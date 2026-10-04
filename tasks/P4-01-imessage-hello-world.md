```yaml
id: P4-01
title: Photon iMessage hello-world + judge QR onboarding page
owner: P4
status: done
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
- `/agent/scripts/add-user.ts`: `npm run add-user -- +15551234567 Name` to allowlist team phones (prints the line to text).
- `/agent/scripts/doctor.ts`: `npm run doctor` checks credentials and lists allowlisted phones. `GET /card` is a printable QR table card.
- Env names (in `/agent/.env.example`): `PHOTON_PROJECT_ID`, `PHOTON_PROJECT_SECRET` (PLAN.md §10), plus agent-only `PUBLIC_URL`, `ONBOARD_PORT`, `USE_MOCKS`, `AGENT_TERMINAL`.

## Steps
- [x] Human: create a Photon account + project at https://app.photon.codes, copy Project ID + Secret into `/agent/.env`
- [x] Agent loop on `spectrum-ts` cloud iMessage, with the terminal fallback
- [x] Onboarding server: form → create shared user → redirect into Messages; QR at `/qr.svg`
- [x] `add-user` script; allowlisted the test iPhone (remaining team phones: run `npm run add-user` per phone)
- [x] Unit tests for phone normalization and the onboarding handler (mocked Photon)
- [ ] Expose the onboarding server publicly (tunnel) so a phone off the laptop can open it (not done; non-blocking, see Handoff)

## Done when
- [x] A real allowlisted iPhone texts the agent and gets the welcome reply (verified Oct 3)
- [ ] Same flow starting from the QR code on a public URL (blocked on the tunnel; non-blocking)
- [x] `npm test` passes (13/13); `npm run typecheck` passes
- [x] No secrets committed (`.env` git-ignored; only `.env.example` names)

## Handoff (fill in when done; DEV_STRATEGY #1)
- **What changed:** new `/agent`, merged into `dev` at `48172ae` (from `p4/imessage-hello-world`). `src/agent.ts` (Spectrum loop; answers text and pasted-link `richlink` messages), `src/onboard.ts` (onboarding server + printable `/card`), `src/photon.ts` (Photon users API + phone normalization), `src/replies.ts` (reply text), `scripts/add-user.ts`, `scripts/doctor.ts`, tests in `test/`. See `/agent/README.md`.
- **How to run:** `cd agent && npm install && cp .env.example .env` (fill Photon creds) → `npm run doctor` → `npm run add-user -- <phone>` per teammate → `npm run agent` + `npm run onboard`. For judges: tunnel `:8787` (`cloudflared tunnel --url http://localhost:8787`), set `PUBLIC_URL`, print `/card`.
- **Verified on a real phone (Oct 3, reported by P4 from their Mac):**
  - Real Photon credentials validated: the agent connects to Spectrum Cloud iMessage.
  - Real iPhone inbound message validated: allowlisted iPhone → Photon → agent on the Mac.
  - Real outbound reply validated: agent → Photon → iPhone; the phone received the Hidden Rent welcome.
  - Pasted listing link (Zillow/Redfin) from the iPhone: received by the agent and answered (not ignored as a link preview). Passed.
  - Plain Ann Arbor street address from the iPhone: received and answered correctly. Passed.
- **Verified in code:** 13 unit tests + typecheck; onboarding server in mock mode (form, `/join` redirect, bad-number 400, `/card`, `/qr.svg`); clear errors for bad credentials against live spectrum.photon.codes.
- **Not verified:** the onboarding page (`npm run onboard`) with real Photon, and the QR flow from a phone. The QR still points at `localhost`; no public tunnel has been set up or tested.
- **Remaining non-blocking gaps:**
  - Public tunnel / QR onboarding URL: still localhost. Needed before judges scan the QR, and the web's "Continue in iMessage" button links to this page (P2 decision, Oct 3).
  - Agent replies say no numbers (PLAN.md §0 rule 4) until P4-02 calls `/estimate`.
  - Address detection needs a street type (St, Ave, Rd…); other text gets the welcome.
  - No contact-card share after the first exchange (Photon deliverability tip). Free plan caps at 10 allowlisted phones.
- **Next:** P4-02 interview loop over iMessage against P2-04's `/estimate` + `/answer` (mock inside `/agent` until it lands). Not started.

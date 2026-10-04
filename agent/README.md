# /agent: Hidden Rent iMessage agent (P4)

A Photon Spectrum (`spectrum-ts` 12.10.1) agent that answers iMessages, plus a QR onboarding page so judges can allowlist their own phone.

## Setup (once)
1. Create a free Photon account + project at <https://app.photon.codes>. Copy the **Project ID** and **Secret** from project Settings.
2. `cp .env.example .env` and fill in `PHOTON_PROJECT_ID` / `PHOTON_PROJECT_SECRET`. Never commit `.env`.
3. `npm install` (Node 20+).
4. Allowlist each teammate's phone: `npm run add-user -- +17345550123 Ada`.
   If a phone still gets no reply, text <https://debug.photon.codes> from it and allowlist the handle it reports.

## Run
| Command | What it does |
|---|---|
| `npm run agent` | Agent loop on iMessage. Replies to every inbound DM. |
| `npm run onboard` | Onboarding page on `:8787`: `GET /` form, `POST /join`, `GET /qr.svg` |
| `npm test` / `npm run typecheck` | Unit tests (Photon mocked) / types |

Judges' phones can't reach `localhost`, so expose the onboarding page with a tunnel and set `PUBLIC_URL` to it before printing the QR:
```bash
brew install cloudflared
cloudflared tunnel --url http://localhost:8787   # prints https://<random>.trycloudflare.com
# put that URL in PUBLIC_URL, restart `npm run onboard`, open /qr.svg and print it
```

## Judge flow
Scan QR → enter number → server calls Photon `POST /projects/{id}/users` (`type: "shared"`) → 302 to Photon's `GET /users/{id}/redirect` → Messages opens with "Hi Hidden Rent! What's my apartment's hidden rent?" pre-filled → judge taps Send → agent replies.
The opener is text-only and the judge texts first (inbound-first), which avoids Apple's "Report Junk" banner.

## Mocks (DEV_STRATEGY #4)
| Switch | Stands in for |
|---|---|
| `AGENT_TERMINAL=1` (or no Photon creds) | iMessage → Spectrum's terminal chat provider |
| `USE_MOCKS=1` (or no Photon creds) | Photon user API → fake user + plain `sms:` link |

## Limits (Photon free plan)
- 10 allowlisted users total (team phones included). Delete old users in the dashboard to free slots.
- DMs only; no group chats on the shared pool.
- Android numbers get SMS/RCS fallback.
- The agent says no numbers yet (PLAN.md §0 rule 4). P4-02 wires it to `/estimate` and `/answer`.

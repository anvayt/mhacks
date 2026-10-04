```yaml
id: P4-03
title: Website→iMessage handoff, judge onboarding hardening, after-move-in (bill photo → /calibrate → /fixes)
owner: P4
status: done
branch: p4/interview-loop
type: build
checkpoint: 5:00 AM checkpoint
depends_on: [P4-02, P2-04, P2-05]   # GET /session/{id}, /calibrate, /fixes not served yet → mocked inside /agent
blocks: []
merges: []
services_touched:
  - /agent
services_read:
  - /api GET /session/{id}, POST /calibrate, GET /fixes/{session_id} (PLAN.md §10)
  - Photon management API (users, redirect)
contract_change: none
```

## Goal
Finish P4's remaining code from PLAN.md §8: the web → iMessage handoff (P2 moved `/imessage/start` to P4), a sturdy printable QR card, and the after-move-in loop (bill photo → weather check → streak → fixes → landlord email). Numbers only from the API.

## Done when
- [x] `PUBLIC_URL/?session=<id>` → pre-filled first text "(ref <id>)" → agent resumes with `GET /session/{id}`
- [x] `/card`: QR scales inside the card (viewBox only), mobile layout, print styles; no tunnel URL in source
- [x] Bill photo → `POST /calibrate` → "% above/below normal for this weather", streak, badges → `GET /fixes` → fixes + landlord email
- [x] Exact-contract mocks behind `USE_MOCK_API`; contract breaks logged
- [x] `npm test` (40) + `npm run typecheck` pass

## Handoff (DEV_STRATEGY #1)
- **Merged:** `dev` @ `9cd8915`.
- **What changed:** `agent/src/handoff.ts` (session id format, "(ref id)" opener, parser), `agent/src/onboard.ts` (`?session=` hidden field → opener; `/card` responsive + print, QR viewBox-only, HTML escaping), `agent/src/photo.ts` (HEIC → JPEG via optional `heif2jpeg`, falls back to the original bytes), `agent/src/conversation.ts` (bill photo, `fixes`/`landlord` command at any point, `skip`), `agent/src/api.ts` + `mockApi.ts` (session, calibrate, fixes).
- **Verified:** unit tests; real HEIC (26 MB macOS wallpaper) → JPEG; agent process in the terminal (handoff resume → answer → fixes); onboarding server smoke test (session field, `(ref web123)` opener, viewBox-only QR, PUBLIC_URL on the card); real-Photon startup error path unchanged.
- **Not verified:** a real photo sent over iMessage (Spectrum attachment `read()` on a real line), and any of this against a live /api.
- **Assumptions to confirm (notes/requests.md):** `pct_vs_expected_for_weather` is in percent (-12 = 12% below normal); `streak_months` counts consecutive months below normal; `questions[].options` are strings or `{value,label}`.
- **Cut (optional):** ElevenLabs "call me and explain my bill". Calls need Photon SIP voice lines plus the ElevenLabs key (on a teammate's laptop) and add a second real-time system to keep up for the demo; the text flow covers the same story. Not started.
- **Next:** P2 serves `/answer`, `GET /session/{id}`, `/calibrate`, `/fixes`; P3 links `?session=`; then turn `USE_MOCK_API` off and run on a real phone.

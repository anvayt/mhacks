```yaml
id: P2-04
title: Real /estimate and /answer endpoints
owner: P2
status: todo
branch: p2/estimate-answer
type: build
checkpoint: 1:00 AM GO/NO-GO
depends_on: [P2-01, P2-02, P2-03, P1 model]
blocks: [P3, P4]
merges: []
services_touched:
  - /api
services_read:
  - /model predict + question picker (P1)
contract_change: additive   # bill.seasonal {winter, spring, summer, fall} each {p10, p50, p90}; per-season is what users expect (PLAN.md §1 note)
```

## Goal
`POST /estimate` (url or address) and `POST /answer` in the PLAN.md §10 shape, plus `bill.seasonal`. Use P1's model when it's ready; until then use a stand-in inside `/api` behind one switch (DEV_STRATEGY #4).

## Team decisions (Oct 3, ~9:20 PM)
- **Non-home addresses** (office, City Hall: type/sqft null from P2-01) → friendly error: "That doesn't look like a home. Send a residential address or listing."
- **Unit size:** `/estimate` accepts optional `unit_sqft` (additive request field). Web form has an optional "Unit size (sq ft, it's on the listing)" field; in iMessage, if a multi-unit listing has no size, the **first question** is "How big is the unit in sq ft? (or say skip)". If skipped, use P2-01's estimate (floor area ÷ units, or the 854 sq ft ResStock MI renter median when implausible) and label the size "estimated".
- **Links without an address** (`needs_address` with a hint): ask the renter to confirm the address; never auto-geocode the hint.

## More team decisions (Oct 3, ~9:45 PM)
- **Use P1's model:** `/estimate` wraps `model.hc.service.estimate_hc(lat, lon, unit_sqft, building_type, answers, …)` (pass P2-01's lat/lon so it isn't geocoded twice, plus `building_type` and `unit_sqft`); `/calibrate` wraps `bill_check`. Per-season values are P1's point estimates (p50); p10/p90 come from P1's held-out real-meter error (`accuracy.*`), never invented widths.
- **Score, grade, percentile ("top X%")** are computed here in P2-04, using P1's pre-scored table of 591 Ann Arbor apartment buildings (`model/data/processed/buildings_hc.csv`) as the comparison set.
- **Townhouses:** always ask for the unit size (P2-01 floor areas include garages, so SFA sq ft runs 1.25–3× high); `sqft_estimated` is already true for them.
- **`POST /imessage/start` moves to P4:** P4-01 already built the onboarding server (`/agent/src/onboard.ts`: phone form → Photon `POST /users` → Messages deep link). The web "Continue in iMessage" button links to P4's onboarding page instead; P2 doesn't duplicate it.

## Website + iMessage flow (both channels share one session)
- Web has two buttons: **"Check it here"** (web report) and **"Continue in iMessage"**.
- "Continue in iMessage": web collects the phone number → `POST /imessage/start {phone, session_id?}` (P2, server-side; Photon secret never in the browser) → calls Photon `POST /projects/{projectId}/users/` (`type: "shared"`) → returns Photon's public `GET https://spectrum.photon.codes/users/{userId}/redirect?msg=<prefilled>` URL → browser opens Messages with the agent's number and a pre-filled text containing a short ref code for the session → user taps Send (inbound-first, so no "Report Junk" banner).
- Agent replies include a link back to the web report: `GET /session/{id}` (additive) returns the current estimate for that page.
- Contract additions for §10 (additive): request field `unit_sqft`; `GET /session/{id}`; `POST /imessage/start`.

## Done when
- [ ] Link or address → full §10 response, sessions persisted (SQLite), answers narrow the range; the 1 AM end-to-end path works

## Handoff (fill in when done; DEV_STRATEGY #1)
- What changed (files, endpoints)
- How to use it / run it
- Known gaps, TODOs, anything mocked that still needs to be real
- Who needs to act next (`blocks` owners)

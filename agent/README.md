# Hidden Rent iMessage agent (P4)

The agent calls the real API by default. Photon Spectrum handles iMessage; terminal mode never initializes Photon or sends texts. All predicted, projected and verified numbers come from the API.

## Setup and run

From `agent/`, run `npm ci`. Set `API_BASE_URL` (default `http://localhost:8000`) and `AGENT_API_KEY` to the API's key. Environment variables win, then nonempty values in `agent/.env`, then the root `.env`. Blank placeholders in `.env.example` do not hide root credentials. No keys or bill images are logged.

| Command | Behavior |
|---|---|
| `npm run agent` | iMessage with Photon credentials; terminal otherwise |
| `AGENT_TERMINAL=1 npm run agent` | Plain terminal chat; real API, no Photon |
| `AGENT_TERMINAL=1 USE_MOCK_API=1 npm run agent` | Entire API simulated; every response labeled demo data |
| `npm run checkin -- <phone>` | Queue a monthly check-in, then send only if `/reminders/due` permits it |
| `npm run remind-now -- <phone>` | Explicit demo reminder; bypasses clock/cap on the API but respects stop/pause; does not call `/sent` |
| `npm run onboard` | QR onboarding page on `:8787`; `GET /card` is printable |
| `npm run doctor` | Check Photon credentials and allowlisted phones |
| `npm run add-user -- <phone> [name]` / `remove-user` | Manage the Photon allowlist |
| `npm test` / `npm run typecheck` | Tests with mocked external calls / TypeScript checks |

For a real phone, configure `PHOTON_PROJECT_ID` and `PHOTON_PROJECT_SECRET`, allowlist the phone, and have its user text first. `PUBLIC_URL` points at the publicly reachable onboarding page; `/?session=<id>` carries the web report into the opener as `(ref <id>)`. `USE_MOCKS=1` affects onboarding only; it does **not** mock the heating API. `USE_MOCK_API=1` mocks the full API. Default: off.

Terminal identity defaults to the fictional `+12025550164`; override with `AGENT_TERMINAL_PHONE`. Do not use a real person's phone for automated checks. Terminal mode does not poll/consume the global reminder queue; the explicit CLI commands preview locally without acknowledging a text as delivered.

## Conversation

| Input | API and response |
|---|---|
| First inbound from a phone/email | Cached, normalized `POST /auth/phone`; `GET /me` rehydrates the current home and pending check-in. Every inbound records `/reminders/inbound`. A new `(ref id)` is passed to auth even on a cached account. |
| `login 123456` | Exact six-digit intent, case-insensitive; `/auth/web/confirm`; original API error message on failure |
| Link/address | `/estimate` for a new account; `/properties` for a known home, archiving its old baseline/history |
| Answers / option numbers / `skip` | `/answer`; the API controls the grade range and locking. Estimated unit size is asked first. |
| Locked interview / `save` | `/properties {user_id, session_id}` adopts the answered session |
| `options` / `what can I do` | Suggested commitments. Modeled options show API $/yr, kg CO₂/yr and GRH points; placeholders are tips with no effect numbers. Thermostat safety note is quoted unchanged. |
| `do 1 and 3 by 2026-11-01` | Accept commitments; target date optional. Only modeled selections enter `/projection`: **projected if completed**, current grade unchanged. |
| `done 1` / `dismiss 1` | Update the commitment for that displayed option. A restart requires `options` again; the agent never guesses list order. Completion is reported, not verified. |
| `done` / `did it` / `did it today` / `✅` / `yes` answering a task reminder; `done today` any time | `POST /habits/{user_id}/checkin` (the reminder's day and commitment from `/reminders/inbound` `replying_to`) → “Day N 🔥, best B. See you tomorrow.” with API numbers. `done 1` still completes commitment 1. |
| `streak` | `GET /habits/{user_id}`: current and best daily habit streak |
| `remind-now task` | Demo task reminder (`/reminders/demo-send {kind: task}`; needs a commitment with a target date) so a bare `done` can answer it |
| `checkin` → `yes` | Inbound demo trigger asks “Still at …?” then requests a bill |
| `120 therms`, `120 ccf`, `$85` | `/calibrate` with saved property and session. Missing dates mean the last full calendar month. CCF uses `gas_unit: ccf`; dollars use `amount_usd`, labeled **estimated from your bill amount**. Explicit dates: `120 therms 2026-09-01 to 2026-09-30`. |
| Bill photo | In-memory JPEG/base64 (HEIC conversion when available), `/calibrate`, then fixes and a landlord email. Vision errors invite typing the numbers. No image is persisted. |
| Bill result | Weather comparison, API streak/badges. Provisional `bill_signal` is an early signal; the current grade stays unchanged. Only non-provisional bill regrades change the stated current grade. Verification is separate. |
| `moved` | Ask for a new address; separate baseline, old history archived; pending check-in cleared by the API |
| `stop` / `pause` / `resume` or `start` | Persist server controls; inbound messages still receive replies and do not clear stop/pause |
| `reminders weekly` / `daily` / `monthly` (optional `at 10`) | Opt in through `/me` preferences; server validates the local hour |
| `add to calendar` | Return OAuth URL; after connecting, say `calendar connected`. Creates events only for accepted commitments with a target date; failures never undo a commitment. Mock Calendar is labeled. |
| `fixes` / `landlord` | Existing model-priced fixes + copyable landlord email |

A replacement web session or corrected unit-size estimate is detached from the old property until saved. Billing asks for `save` first instead of attaching a bill to the wrong home. Every API call sends the configured `X-Agent-Key`, including public estimate and answer routes, so concurrent texters do not share the public visitor rate limit. The key stays on the agent server.

## Reminder delivery and restart behavior

Only one iMessage agent process should run. One serialized poller runs immediately and every five minutes, sending the API's `text_hint` verbatim. `/reminders/due` owns NEW_CHANGES §9.6/D4: opt-in, user timezone/quiet hours, at most one proactive text per day, stop/pause, and automatic pause after two unanswered messages. Manual non-demo check-ins use the same queue and guards. Stop does not disable replies.

After a transport succeeds, a durable delivered receipt is saved before `/reminders/{id}/sent`. If acknowledgement fails, future polls retry the acknowledgement, never the text, and do not send new reminders while caps are stale. Failed transport leaves the reminder queued. Receipts contain only reminder IDs/statuses, in git-ignored `data/agent-reminder-receipts.json` with mode `600`; `REMINDER_RECEIPTS` can override that path.

A crash between starting and confirming a transport leaves a `sending` receipt. All proactive sends fail closed until the operator checks delivery: mark it `delivered` if the text arrived (the next poll retries `/sent`), or remove only that ID if it definitely did not. This is conservative recovery, not a distributed exactly-once guarantee. Never delete the file merely to restart. Do not run the manual sender concurrently with the main agent; ask the existing agent `checkin`/`remind-now` instead when demonstrating.

Dialog state stays in memory. `/me` is fetched on each inbound so an externally triggered pending check-in is visible without restarting. Auth resolution is cached for process lifetime (concurrent messages share one request); fresh ref openers invalidate only the ref association. Durable accounts, property history, bills, commitments, notification controls and grades live in the API.

## Known API boundaries

- A projection after a meaningful `bill_regrade` still uses the original session baseline. Commitments remain saveable; the agent withholds that stale projection until the API supports it.
- Calendar creation is not durably idempotent and the API does not populate `Commitment.calendar_event_id`. The agent prevents repeat creation during a process lifetime. After a restart, inspect Calendar before repeating the command.
- Calendar mock mode on the real API still requires following its callback URL; `calendar connected` does not bypass that check.
- The heat-included API correctly exposes renter cooling-only bills and building CO₂/grades. An existing API issue in saved-property snapshot ranking needs P2; the agent does not compute a replacement ranking.
- Real-phone delivery is for Bittermoss/the team lead to validate. This branch's development checks send no iMessages.

See [PHASE2_REPORT.md](PHASE2_REPORT.md) for validation and terminal evidence.

# Board integration

The board uses the shared `hr_session_id`, `hr_property_id`, `hr_user_id`, and `hr_token` handoff. It preserves P3's classes, blue/red bars, and fixed “You” bar. Current and projected figures remain separate. No peer or commitment fixtures remain.

| Screen/action | API |
| --- | --- |
| Saved home and current report | `GET /me/{user_id}`, `/session/{session_id}`, `/properties/{property_id}/history` |
| Current placement and nearby bars | `GET /leaderboard/position/{property_id}` or `/leaderboard/position?session_id=…` |
| Anonymous ghost rank | `GET /leaderboard/position?session_id=…&catalog_ids=…` |
| Public hall of fame / aggregated blocks | `GET /leaderboard` |
| Verified board / honest empty state | `GET /leaderboard?board=verified_cut` (`demo:true` is labelled “demo data”) |
| Modeled choices and unpriced tips | `GET /commitments/suggested/{property_id}` or `/commitments/suggested?session_id=…` |
| What-if | `POST /projection` with property or session and selected catalog IDs |
| Commit / reported Done | `POST /commitments`, `PATCH /commitments/{id}` |
| Optional calendar | `POST /calendar/connect`, open returned `auth_url`, then `POST /calendar/reminders`; mock mode labelled |
| Move | Signed `POST /properties {user_id,address|url}`; anonymous `POST /estimate`; save new IDs and open `/survey?session_id=…` |
| Monthly check | `POST /calibrate` with session, optional property, dates, and therms/ccf, amount, or JPEG; optional kWh |
| Fixes / copyable draft | `GET /fixes/{session_id}`; copying never sends the email |

## Live verification (October 4, 2026)

Isolated API `:8031`, web `:3002`, separate temporary databases. API bootstrap caps all model requests at two; existing model `:8001` was reused. Phone confirmation used the authorized mock flow on a fictional test handle. No real text or calendar event was sent.

- 1514 Morton Ave, explicit gas + single pane: current score 45, grade span B–D, rank 11,610/21,173, $2,185/yr (P10–P90 $1,283–$3,070). Window projection: score 56, rank 9,286, $2,060/yr, $125/yr and 699 kg CO₂/yr saved. Signed and anonymous paths both worked. The actual bar value and height remained unchanged; dashed overlay and background changed.
- 2322 Arrowwood Trl, 850 sq ft: score 71, A–B, rank 634/2,213, $326/yr; all suggested savings were unmodeled and untoggleable. Adopting this session preserved its ID and score.
- Remaining live browser reports: 555 E William St score 14, A–F, rank 911/1,060; 715 Arbor St score 56, A–F, rank 549/1,258; 2200 Fuller Ct score 36, C–D, rank 680/1,060.
- Hypothetical bill inputs, **not actual bills**: September 2026 80 therms → 77.1 CCF and 180.4% above weather normal; July 80 CCF → 80.0 CCF. August $100 → 99.6 CCF, `estimated_from_amount:true`, with the API's EIA/DTE conversion note. Distinct periods avoided deduplication. Each was provisional/unverified, and current grade/rank stayed unchanged. Fixes and draft copying worked.
- Blank PNG test fixture → 12,283-character JPEG data URL through the browser canvas. Deliberately disabled vision returned `vision_unavailable` and typed fallback; restored configured vision returned real `422 unreadable_bill`, `is_utility_bill:false`, and null usage. No successful bill OCR or real bill verification is claimed.
- Commit, reported Done, mock calendar connect/reminder, saved move to 715 Arbor (old homes archived), `needs_address`, `not_a_home`, browser-simulated API outage and Retry recovery passed. At 375 px, current and ghost views had no horizontal overflow. `npm run build` passed.

Screenshots on the test host: `/tmp/w2-morton-anonymous-mobile-ghost.png`, `/tmp/w2-morton-mobile.png`, `/tmp/w2-arrowwood-anonymous.png`, `/tmp/w2-morton-80therms.png`, `/tmp/w2-morton-amount.png`, `/tmp/w2-photo-unavailable.png`, `/tmp/w2-api-down.png`, `/tmp/w2-api-recovered.png`, `/tmp/w2-not-a-home.png`, `/tmp/w2-needs-address.png`, `/tmp/w2-moved-survey-handoff.png`, and one `/tmp/w2-<address>.png` per remaining address. Raw non-auth responses are in `/tmp/w2-evidence/`; login credentials are not committed.

## API / merge follow-up

- After a meaningful bill regrade, the API projection still starts from the older session. The board clears local ghosts and disables calibrated-baseline what-ifs rather than presenting a stale comparison. API projection needs the latest real snapshot baseline before this can be enabled.
- For signed heat-included homes, initial/questionnaire snapshots currently store the renter's cooling-only `bill.annual`, while rank should use `bill.building_annual`. If these disagree, the board shows the actual model bill/grade and an unavailable-rank explanation instead of inventing a corrected rank. The API snapshot basis needs correction.
- W1 owns the `/signin` and `/survey` destination screens. W2 supplies links, IDs, and callbacks without editing those screens. No frontend scores, ranks, annual savings, or verified board entries are mocked.

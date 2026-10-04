# ASI integration verification

Status at **09:00 EDT, October 4, 2026**: Agentverse registration, profile, mailbox round trip, and ASI:One intent parsing are verified. The full address → answers → options → simulation mailbox rehearsal is blocked because the live model is stopped. **Keep the sponsor checkbox unchecked until that final rehearsal passes.**

- Independent uv project, pinned uagents 0.23.7 / uagents-core 0.4.11.
- 31 mocked tests passed: fallback intent, ASI allowlist validation, API-only wording, placeholders, negative savings, sender isolation, simulation selection, API error passthrough, X-Agent-Key on requests, chat acknowledgement and sequential/concurrent retry dedupe.
- API regression suite: **672 passed, 5 skipped**. Three direct-model live tests were deliberately skipped by using an unavailable model URL (the task forbids direct model calls); the other two are opt-in network/vision tests. Public GIS fixtures were copied into this worktree's ignored test cache, with no live databases copied.
- Real public API `/estimate` succeeded for 1514 Morton Ave; raw response in `evidence/morton-estimate.json`.
- Second local uAgent conversation: `evidence/local-chat.json` / `.log`. This is **local HTTP transport**, not an ASI:One or mailbox success claim.
- Agentverse registration and protocol-manifest publication succeeded: `evidence/mailbox-registration.json`, `evidence/mailbox-server.log`. The authenticated profile read returned **200**, name **Hidden Rent**, handle **hidden-rent-mhacks**, mailbox type and README present (`evidence/public-profile.json`).
- Agentverse's mailbox HEAD readiness probe returned **200**. The ASI:One `asi1` API returned **200** and classified a free-form upgrade request as `{"command":"options"}` (`evidence/credentials-check.json`). The model generated no renter-facing reply or energy number.
- A second local uAgent sent through the real Agentverse mailbox and received the API's exact **503** message: “Our cost model is starting up. Try again in a minute.” (`evidence/mailbox-chat.json`, `evidence/mailbox-client.log`). This proves transport and error passthrough; the transcript deliberately says `pass: false` for the incomplete product rehearsal.
- Public website/onboarding URLs are not yet available; returned localhost links are explicitly labelled local previews.
- The lead had stopped the localhost services. With explicit permission, only FastAPI on **8000** was restarted; its `/health` returned **200**. The API then reported its model dependency unavailable. **8001, web and onboarding were not started, stopped or contacted directly.**

The registered public address (not a secret): `agent1qth4ez7uam253n3aeuq9c56pnruw0e99vznlx3pupvahcxd84pfsghrfyum`. Its identity seed is private and not included here. Registration evidence is separate from the address itself.

Remaining human check: after P1 restores the model, run the mailbox client with `--asi-intent`, then select Hidden Rent in ASI:One and repeat the conversation. ASI:One UI discovery/indexing is not established by the transport test. No new account was created; existing keys were saved to the owner's ignored `.env` (mode 600) and are never included in this evidence.

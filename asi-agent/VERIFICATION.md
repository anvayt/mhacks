# ASI integration verification

Status: implementation and local checks complete; Agentverse/ASI:One credentials are being supplied by the lead. **Sponsor checkbox remains unchecked until live mailbox + ASI intent verification succeeds.**

- Independent uv project, pinned uagents 0.23.7 / uagents-core 0.4.11.
- 31 mocked tests passed: fallback intent, ASI allowlist validation, API-only wording, placeholders, negative savings, sender isolation, simulation selection, API error passthrough, X-Agent-Key on requests, chat acknowledgement and sequential/concurrent retry dedupe.
- API regression suite: **672 passed, 5 skipped**. Three direct-model live tests were deliberately skipped by using an unavailable model URL (the task forbids direct model calls); the other two are opt-in network/vision tests. Public GIS fixtures were copied into this worktree's ignored test cache, with no live databases copied.
- Real public API `/estimate` succeeded for 1514 Morton Ave; raw response in `evidence/morton-estimate.json`.
- Second local uAgent conversation: `evidence/local-chat.json` / `.log`. This is **local HTTP transport**, not an ASI:One or mailbox success claim.
- Public website/onboarding URLs are not yet available; returned localhost links are explicitly labelled local previews.
- Live model and demo services were not started, stopped or restarted. Only public port-8000 API calls were made.

The installation's public address (not a secret): `agent1qth4ez7uam253n3aeuq9c56pnruw0e99vznlx3pupvahcxd84pfsghrfyum`. Its identity seed is private and not included here. An address is not proof of registration.

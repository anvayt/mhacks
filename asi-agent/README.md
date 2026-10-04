# Hidden Rent for ASI:One

A Fetch.ai uAgent using the standard Agent Chat Protocol, an Agentverse mailbox, and ASI:One's OpenAI-compatible intent API. All energy, bill, grade, carbon and improvement figures come from the existing Hidden Rent API. No model, website, iMessage agent or API source/dependency changes are needed.

## Run

From this repository's root, using the existing credentials file:

```bash
uv sync --project asi-agent --frozen
API_BASE_URL=http://localhost:8000 make asi-agent
# Equivalent:
API_BASE_URL=http://localhost:8000 uv run --project asi-agent \
  --env-file /Users/anvaytodkar/Code/mhacks/.env python asi-agent/agent.py
```

`ASI_ENV_FILE` overrides the Makefile's credentials-file path. Never print the file or put a key in a command argument. Required names: `AGENTVERSE_API_KEY` (register the mailbox under the existing account), `AGENT_API_KEY` (sent as X-Agent-Key on **every** API call). `ASI_ONE_API_KEY` enables ASI:One intent parsing; if absent/unavailable, deterministic intent matching keeps the conversation working. Default documented ASI model: `asi1`; optionally set `ASI_ONE_MODEL`.

Set `WEB_BASE_URL` and `ONBOARD_URL` to the team's current public website and onboarding origins when available. Until then, links use localhost and explicitly say **local preview**. No public deployment/tunnel is created by this agent. Links preserve the API session: `/share?session=`, `/compare?a=`, and onboarding `/?session=`. The grade route is deliberately not used as a session link.

The agent's inspector listens **only on 127.0.0.1:8130**. The advertised delivery endpoint is Agentverse's mailbox, not this local HTTP server. The agent must remain running for replies. It never starts/stops the demo stack or calls the model port directly. An API-only registration policy avoids on-chain wallet transactions.

Identity lives in `asi-agent/.runtime/agent.seed` (directory mode 700, file mode 600, git-ignored). **Preserve this file when moving the service** or it becomes a different agent address. Conversation state is per sender in memory and disappears on restart. Runtime files stay in `.runtime`; no key/seed is committed. `--address` prints only the public agent address without running or registering anything.

## ASI:One / Agentverse setup

The service publishes `AgentChatProtocol` using `include(protocol, publish_manifest=True)`. Startup registers the agent with `mailbox=True`, profile description, keyword/tag metadata, and the public `PROFILE.md`. Registration uses the same challenge/signature helper as the uAgents inspector, with the existing account's Agentverse API key. The default requested handle is `hidden-rent-mhacks` (`ASI_AGENT_HANDLE` overrides it if unavailable).

Registered profile: **Hidden Rent** (`hidden-rent-mhacks`), address `agent1qth4ez7uam253n3aeuq9c56pnruw0e99vznlx3pupvahcxd84pfsghrfyum`. The address belongs to the lead's private runtime seed; a fresh clone without that seed creates a different agent.

Look for both the mailbox registration success and protocol-manifest publication in the logs. A printed address alone does **not** prove registration or discovery. Evidence and exact verification status are in [VERIFICATION.md](VERIFICATION.md).

For the lead after registration:

1. Open [Agentverse](https://agentverse.ai), find **Hidden Rent** in your agents or search its exact address, and open its profile. Confirm it has the mailbox and chat-protocol capability.
2. Click **Chat with Agent** to open [ASI:One](https://asi1.ai) with this agent. Alternatively use ASI:One's agent search / @mention and select **Hidden Rent**; use the exact address if name indexing has not caught up. Do not assume typing an unselected name invokes it.
3. Send `1514 Morton Ave, Ann Arbor, MI`. Answer the numbered question. The response carries predicted grade/range, score, cost range, carbon and report links.
4. Say `options`, then `try` followed by the number of a priced option, then `ff 30`. Confirm that effects say **projected if completed**, simulation says **not real usage**, and the current grade is unchanged. Tips cannot be selected into the simulation.
5. Verify the agent's receive/reply log alongside ASI:One. Name-search indexing and the ASI:One UI interaction require a human check; a transport test alone does not prove them.

No new user account is created. The developer's existing account/API keys are required. No resident phone numbers, login, reminders, bill images or real messages are sent through this integration.

## Conversation and numeric contract

- Address/link → `POST /estimate`; option answer → `POST /answer` for the sender's session and current question.
- `options` → `GET /commitments/suggested?session_id=`. Every API request carries X-Agent-Key. Placeholder figures are omitted even if a malformed response includes them.
- `try 2` / `try 2 and 4` select anonymous what-if catalog IDs in memory. `ff 30` → `POST /simulate/fast-forward` with those IDs. Nothing is accepted/completed on the renter's behalf; no account or verified impact is created.
- API `detail.message` is returned verbatim. Connection failures have a fixed message. Failed requests retain the previous conversation state.
- ASI:One sees the user's text and current question/options, **never the estimate body**. It may return only an exact input address/link, an allowlisted option value, or a command. Invented figures, extra fields, unknown values and invented listings are rejected. Numeric command arguments and option indices are parsed deterministically. Invalid/unavailable ASI output falls back to regex matching using the iMessage agent's address/option rules.
- Replies are fixed Python formatters, not LLM-generated text. Prices are rounded for display; the top-percent line is the percentage complement of API `percentile_city`, not a new rank/model. Missing numeric fields remain absent. Negative savings are explicitly **cost increases**. “Locked” comes only from the API, not the LLM or the agent.

## Tests and reproducible live check

```bash
make asi-agent-test
# Check mailbox readiness and real ASI intent parsing, without printing credentials:
uv run --project asi-agent --env-file /Users/anvaytodkar/Code/mhacks/.env \
  python asi-agent/verify_access.py
# After starting the mailbox agent:
uv run --project asi-agent --env-file /Users/anvaytodkar/Code/mhacks/.env \
  python asi-agent/chat_client.py --asi-intent --output asi-agent/evidence/mailbox-chat.json
```

The second local test uAgent sends to the registered target's Agentverse mailbox, while replies return to the test client's loopback HTTP endpoint on **8131**. It records the exact conversation and exits. It does not contact any real recipient. Its seed is also private/ignored. It uses the Almanac HTTP registration API, not paid on-chain registration.

For an explicitly local transport test before credentials are available, run `agent.py --local-test`, then `chat_client.py --local --output asi-agent/evidence/local-chat.json`. This exercises real uAgent envelopes and the live public Hidden Rent API, **but is not evidence of Agentverse registration or ASI:One use**. Stop only that local test agent before starting mailbox mode on its own port.

## Official sources checked October 4, 2026

- [uAgents framework](https://uagents.fetch.ai/docs) and [ASI:One-compatible chat example](https://uagents.fetch.ai/docs/examples/asi-1): ChatMessage, TextContent, ChatAcknowledgement, chat_protocol_spec and manifest publication.
- [Agentverse mailboxes](https://uagents.fetch.ai/docs/agentverse/mailbox): local agent delivery without a public endpoint.
- [Agentverse README guidelines](https://docs.agentverse.ai/documentation/agent-discovery/readme-guidelines) and [Marketplace](https://docs.agentverse.ai/documentation/getting-started/agentverse-marketplace): profile/README discovery and Chat with Agent.
- [ASI:One quickstart](https://docs.asi1.ai/documentation/getting-started/quickstart): `https://api.asi1.ai/v1/chat/completions`, documented model `asi1`, Bearer API key and OpenAI-compatible response.
- [Fetch.ai MHacks hackpack](https://www.fetch.ai/events/hackathons/m-hacks/hackpack): event integration guidance. Technical verification does not establish prize eligibility or guarantee search ranking.
- Implementation compatibility is pinned in this directory's `uv.lock` (uagents 0.23.7, uagents-core 0.4.11). Programmatic mailbox registration follows the installed framework's `Agent` inspector `/connect` handler and `uagents.mailbox.register_in_agentverse` helper.

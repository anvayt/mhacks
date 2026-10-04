#!/usr/bin/env bash
# Push secrets from a .env file to both Fly apps without printing any value:
#   bash deploy/secrets.sh [/path/to/.env]
# Generates a fresh shared AGENT_API_KEY every run (rotation = rerun). Reads the ASI agent seed
# from $ASI_SEED_FILE (default asi-agent/.runtime/agent.seed next to the .env) so the Agentverse
# address stays the same. Only the key names below ever leave the file.
set -euo pipefail
ENV_FILE=${1:-$(dirname "${BASH_SOURCE[0]}")/../.env}
ASI_SEED_FILE=${ASI_SEED_FILE:-$(dirname "$ENV_FILE")/asi-agent/.runtime/agent.seed}
API_APP=${API_APP:-hidden-rent-api-mhacks}
AGENTS_APP=${AGENTS_APP:-hidden-rent-agents-mhacks}
pick() { grep -E "^($1)=" "$ENV_FILE"; }  # literal KEY=value lines, as fly secrets import expects
agent_key="AGENT_API_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
{ pick 'PHOTON_PROJECT_ID|PHOTON_PROJECT_SECRET|XAI_API_KEY'; echo "$agent_key"; } \
  | fly secrets import -a "$API_APP" --stage >/dev/null
{ pick 'PHOTON_PROJECT_ID|PHOTON_PROJECT_SECRET|AGENTVERSE_API_KEY|ASI_ONE_API_KEY'; echo "$agent_key"
  echo "ASI_AGENT_SEED=$(tr -d '[:space:]' < "$ASI_SEED_FILE")"; } \
  | fly secrets import -a "$AGENTS_APP" --stage >/dev/null
echo "secrets staged on $API_APP and $AGENTS_APP (deploy or fly secrets deploy to apply)"

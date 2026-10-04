"""Check existing credentials without logging tokens, headers or error bodies."""
import asyncio
from datetime import datetime, timezone
import json
import os
from pathlib import Path

import httpx
from uagents_core.config import AgentverseConfig

from intents import IntentParser


async def main():
    result = {'checked_at': datetime.now(timezone.utc).isoformat()}
    root = Path(__file__).resolve().parent
    registration_path = root / '.runtime' / 'registration.json'
    registration = json.loads(registration_path.read_text()) if registration_path.exists() else {}
    result['registered_address'] = registration.get('address')
    async with httpx.AsyncClient(timeout=25) as client:
        try:
            response = await client.head(AgentverseConfig().mailbox_endpoint,
                headers={'x-uagents-address': registration.get('address', '')})
            result['mailbox_readiness_status'] = response.status_code
        except httpx.HTTPError as error:
            result['agentverse_error'] = type(error).__name__

    class StatusTransport(httpx.AsyncHTTPTransport):
        async def handle_async_request(self, request):
            try:
                response = await super().handle_async_request(request)
                result['asi_status'] = response.status_code
                return response
            except httpx.HTTPError as error:
                result['asi_error'] = type(error).__name__
                raise

    parser = IntentParser(transport=StatusTransport())
    result['asi_model'] = os.getenv('ASI_ONE_MODEL', 'asi1')
    result['asi_intent'] = await parser.parse('Could you show me which upgrades I should consider for my rental?')
    result['asi_live_calls_accepted'] = parser.llm_successes
    path = root / 'evidence' / 'credentials-check.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return 0 if result.get('mailbox_readiness_status') == 200 and result['asi_intent'] == {'command': 'options'} and parser.llm_successes else 1


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))

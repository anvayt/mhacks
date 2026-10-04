"""Hidden Rent's ASI:One chat-protocol uAgent. Only its own loopback port is used."""
import argparse
import asyncio
import logging
import os
from pathlib import Path
import secrets
from collections import defaultdict
from datetime import datetime, timezone
from uuid import uuid4

from uagents import Agent, Context, Protocol
from uagents import asgi
from uagents.mailbox import AgentverseConnectRequest, register_in_agentverse
from uagents.registration import AlmanacApiRegistrationPolicy
from uagents.resolver import RulesBasedResolver
from uagents_core.identity import Identity
from uagents_core.registration import AgentProfile, AgentRegistrationPolicy, RegistrationRequest
from uagents_core.contrib.protocols.chat import ChatMessage, ChatAcknowledgement, TextContent, chat_protocol_spec

from conversation import Conversations

ROOT = Path(__file__).resolve().parent
RUNTIME = Path(os.getenv('ASI_RUNTIME_DIR', str(ROOT / '.runtime'))).resolve()
DESCRIPTION = 'Predicted Ann Arbor rental heating/cooling costs, grades, carbon and landlord questions. API-grounded figures; ASI:One intent parsing. Sustainability, housing, energy, Hidden Rent, Zillow rentals.'
TAGS = ['sustainability', 'housing', 'energy', 'Ann Arbor', 'hidden rent', 'rental energy bill']


class NoRegistration(AgentRegistrationPolicy):
    """Local transport checks must not publish a throwaway agent."""
    async def register(self, *args, **kwargs):
        pass


def seed_for(name='agent'):
    RUNTIME.mkdir(mode=0o700, parents=True, exist_ok=True)
    RUNTIME.chmod(0o700)
    path = RUNTIME / (name + '.seed')
    if not path.exists():
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, 'w') as file:
            file.write(secrets.token_hex(32))
    path.chmod(0o600)
    return path.read_text().strip()


def protocol_for(conversations):
    protocol = Protocol(spec=chat_protocol_spec)
    # Small bounded dedupe avoids repeating an API action after transport retries.
    seen = {}
    sender_locks = defaultdict(asyncio.Lock)

    @protocol.on_message(ChatMessage)
    async def message(ctx: Context, sender: str, msg: ChatMessage):
        await ctx.send(sender, ChatAcknowledgement(timestamp=datetime.now(timezone.utc), acknowledged_msg_id=msg.msg_id))
        content = '\n'.join(item.text for item in msg.content if isinstance(item, TextContent)).strip()
        if not content:
            return
        key = (sender, str(msg.msg_id))
        async with sender_locks[sender]:
            if key in seen:
                response = seen[key]
            else:
                try:
                    response = await conversations.reply(sender, content)
                except Exception:
                    ctx.logger.error('Chat processing failed; no private request or credentials logged')
                    response = 'Hidden Rent could not finish this request. Please try again.'
                if len(seen) >= 500:
                    seen.pop(next(iter(seen)))
                seen[key] = response
        await ctx.send(sender, ChatMessage(timestamp=datetime.now(timezone.utc), msg_id=uuid4(),
                       content=[TextContent(type='text', text=response)]))
        ctx.logger.info('Chat reply sent; figures from Hidden Rent API')

    @protocol.on_message(ChatAcknowledgement)
    async def acknowledged(ctx: Context, sender: str, msg: ChatAcknowledgement):
        ctx.logger.info('Chat acknowledgement received')

    return protocol


def build_agent(local=False):
    seed = seed_for()
    os.chdir(RUNTIME)  # uAgents' state files remain in this private, ignored directory.
    asgi.HOST = '127.0.0.1'  # Inspector only. No public /submit endpoint is advertised in mailbox mode.
    client_address = Identity.from_seed(seed_for('test-client'), 0).address if local else None
    agent = Agent(name='Hidden Rent', seed=seed, port=8130, mailbox=not local,
        endpoint='http://127.0.0.1:8130/submit' if local else None,
        resolve=RulesBasedResolver({client_address: 'http://127.0.0.1:8131/submit'}) if local else None,
        registration_policy=NoRegistration() if local else AlmanacApiRegistrationPolicy(),
        description=DESCRIPTION, handle=os.getenv('ASI_AGENT_HANDLE', 'hidden-rent-mhacks'),
        metadata={'tags': TAGS, 'keywords': TAGS}, readme_path=str(ROOT / 'PROFILE.md'),
        publish_agent_details=not local, store_message_history=False, handle_messages_concurrently=True)
    conversations = Conversations()
    agent.include(protocol_for(conversations), publish_manifest=not local)

    @agent.on_event('startup')
    async def startup(ctx):
        ctx.logger.info('Hidden Rent address: %s', agent.address)
        if local:
            ctx.logger.info('LOCAL TRANSPORT TEST: no mailbox or ASI discovery claim')
            return
        profile = AgentProfile(description=DESCRIPTION, readme=(ROOT / 'PROFILE.md').read_text(),
            starter_prompts=['1514 Morton Ave, Ann Arbor, MI', 'What is the hidden energy cost of my Ann Arbor rental?', 'options'])
        details = RegistrationRequest(address=agent.address, name=agent.name,
            handle=os.getenv('ASI_AGENT_HANDLE', 'hidden-rent-mhacks'), agent_type='mailbox',
            profile=profile, endpoints=agent.info.endpoints, protocols=list(agent.protocols), metadata=agent.metadata)
        try:
            result = await asyncio.wait_for(register_in_agentverse(
                request=AgentverseConnectRequest(user_token=os.environ['AGENTVERSE_API_KEY'], agent_type='mailbox'),
                identity=Identity.from_seed(seed, 0), prefix='agent', agentverse=agent.agentverse, agent_details=details), timeout=30)
            if result.success:
                ctx.logger.info('MAILBOX REGISTRATION VERIFIED: Hidden Rent profile registered')
                (RUNTIME / 'registration.json').write_text(__import__('json').dumps({
                    'address': agent.address, 'registered_at': datetime.now(timezone.utc).isoformat(),
                    'mailbox': True, 'protocols': list(agent.protocols)}))
            else:
                ctx.logger.error('Mailbox registration rejected; verify the existing Agentverse key and handle')
        except Exception:
            ctx.logger.error('Mailbox registration unavailable; no token or server error body logged')

    return agent


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--local-test', action='store_true', help='Local transport only; no registration')
    parser.add_argument('--address', action='store_true', help='Print this installation\'s public agent address only')
    args = parser.parse_args()
    if args.address:
        print(Identity.from_seed(seed_for(), 0).address)
    else:
        if not args.local_test and not os.getenv('AGENTVERSE_API_KEY'):
            raise SystemExit('AGENTVERSE_API_KEY is missing. Add it to the existing .env and launch with uv --env-file.')
        if not os.getenv('AGENT_API_KEY'):
            raise SystemExit('AGENT_API_KEY is required on every Hidden Rent API call.')
        logging.basicConfig(level=logging.INFO)
        build_agent(args.local_test).run()

"""Second local uAgent acceptance client. --local bypasses Agentverse explicitly."""
import argparse
import asyncio
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from uuid import uuid4

from uagents import Agent, Context, Protocol
from uagents import asgi
from uagents.registration import AlmanacApiRegistrationPolicy
from uagents.resolver import RulesBasedResolver
from uagents_core.identity import Identity
from uagents_core.contrib.protocols.chat import ChatMessage, ChatAcknowledgement, TextContent, chat_protocol_spec

from agent import ROOT, RUNTIME, NoRegistration, seed_for


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--local', action='store_true')
    parser.add_argument('--target')
    parser.add_argument('--asi-intent', action='store_true', help='Use a free-form options request requiring the ASI intent parser')
    parser.add_argument('--output', default=str(ROOT / 'evidence' / 'chat-transcript.json'))
    args = parser.parse_args()
    target = args.target or Identity.from_seed(seed_for(), 0).address
    output = Path(args.output).resolve()
    client_dir = RUNTIME / 'client'
    client_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(client_dir)
    asgi.HOST = '127.0.0.1'
    client = Agent(name='Hidden Rent acceptance client', seed=seed_for('test-client'), port=8131,
        endpoint='http://127.0.0.1:8131/submit', publish_agent_details=False,
        resolve=RulesBasedResolver({target: 'http://127.0.0.1:8130/submit'}) if args.local else None,
        registration_policy=NoRegistration() if args.local else AlmanacApiRegistrationPolicy())
    protocol = Protocol(spec=chat_protocol_spec)
    transcript = {'transport': 'local HTTP only' if args.local else 'Agentverse mailbox outbound; local client reply endpoint',
                  'target': target, 'started_at': datetime.now(timezone.utc).isoformat(), 'messages': [], 'pass': False}
    stage, answered, sent, seen, done = 'estimate', 0, False, set(), asyncio.Event()

    async def send(ctx, text):
        transcript['messages'].append({'role': 'user', 'text': text})
        print('USER:', text, flush=True)
        await ctx.send(target, ChatMessage(timestamp=datetime.now(timezone.utc), msg_id=uuid4(), content=[TextContent(type='text', text=text)]))

    @client.on_interval(period=5)
    async def begin(ctx):
        nonlocal sent
        if not sent:
            sent = True
            await send(ctx, '1514 Morton Ave, Ann Arbor, MI')

    @protocol.on_message(ChatAcknowledgement)
    async def ack(ctx, sender, msg):
        pass

    @protocol.on_message(ChatMessage)
    async def reply(ctx: Context, sender: str, msg: ChatMessage):
        nonlocal stage, answered
        if sender != target or str(msg.msg_id) in seen:
            return
        seen.add(str(msg.msg_id))
        await ctx.send(sender, ChatAcknowledgement(timestamp=datetime.now(timezone.utc), acknowledged_msg_id=msg.msg_id))
        text = '\n'.join(c.text for c in msg.content if isinstance(c, TextContent))
        transcript['messages'].append({'role': 'agent', 'text': text})
        print('AGENT:', text, end='\n\n', flush=True)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(transcript, indent=2) + '\n')
        if stage == 'estimate':
            if 'Predicted' not in text or 'Web report:' not in text:
                done.set(); return
            options = re.findall(r'^(\d+)\) (.+)$', text, re.M)
            if options and answered < 4:
                choice = next((n for n, label in options if re.search(r'gas|single|central', label, re.I)), options[0][0])
                answered += 1
                await send(ctx, choice)
            else:
                stage = 'options'
                await send(ctx, 'Could you show me which upgrades I should consider for my rental?' if args.asi_intent else 'options')
        elif stage == 'options':
            priced = re.findall(r'^(\d+)\) .*\$[\d,.]+/year saved', text, re.M)
            if priced:
                stage = 'select'
                await send(ctx, 'try ' + priced[0])
            else:
                stage = 'ff'
                await send(ctx, 'ff 30')
        elif stage == 'select':
            stage = 'ff'
            await send(ctx, 'ff 30')
        elif stage == 'ff':
            transcript['pass'] = ('imulated' in text and 'Web report:' in text and
                                  any('projected if completed' in m['text'].lower() for m in transcript['messages'] if m['role'] == 'agent'))
            transcript['finished_at'] = datetime.now(timezone.utc).isoformat()
            output.write_text(json.dumps(transcript, indent=2) + '\n')
            done.set()

    client.include(protocol, publish_manifest=False)

    async def finish():
        try:
            await asyncio.wait_for(done.wait(), timeout=240)
            print('PASS' if transcript['pass'] else 'FAIL', 'chat transcript:', output, flush=True)
        except asyncio.TimeoutError:
            print('FAIL: no complete chat exchange within the test timeout', flush=True)
        # Stop only this acceptance client's listener. Do not await the uAgents
        # runner from a child task: its shutdown cancels all event-loop tasks.
        while client._server.server is None:
            await asyncio.sleep(0.05)
        client._server.server.should_exit = True

    asyncio.get_event_loop().create_task(finish())
    client.run()
    return 0 if transcript['pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

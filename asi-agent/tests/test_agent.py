import asyncio
from copy import deepcopy
import json
from uuid import uuid4
from datetime import datetime, timezone

import httpx
import pytest

from api_client import HiddenRentAPI, ApiError
from conversation import Conversations
from intents import IntentParser, fallback, validate
from replies import estimate_text, suggestions_text, simulation_text

QUESTION = {'id': 'window_panes', 'text': 'How many window panes?', 'options': [
    {'value': 1, 'label': 'Single pane'}, {'value': 2, 'label': 'Double pane'}]}
EST = {'session_id': 'test-session', 'building': {'address': 'Test fixture', 'sqft_estimated': True},
       'grade': 'C', 'grade_span': ['B', 'C'], 'locked': False, 'score': 57, 'percentile_city': .837,
       'hidden_rent_usd_mo': 19, 'co2_t': {'p50': 3.2}, 'bill': {'annual': {'p10': 701, 'p50': 1003, 'p90': 1807}},
       'questions': [QUESTION], 'answers': {}}
SUGGESTIONS = [{'catalog_id': 'window_upgrade', 'title': 'Windows', 'who_acts': 'landlord', 'grh_points': 4,
                'pending_model': False, 'projected': {'usd_saved_yr': 219, 'co2_kg_saved_yr': 601}},
               {'catalog_id': 'attic_insulation', 'title': 'Attic', 'pending_model': True, 'rebate_usd': 999999,
                'projected': {'usd_saved_yr': 999999, 'co2_kg_saved_yr': 999999}, 'note': 'invented $999999'}]


def run(coro):
    return asyncio.run(coro)


@pytest.mark.parametrize('text,intent', [
    ('1514 Morton Ave, Ann Arbor, MI', {'address': '1514 Morton Ave, Ann Arbor, MI'}),
    ('Check https://www.zillow.com/example/', {'url': 'https://www.zillow.com/example/'}),
    ('2', {'answer': 2}), ('double', {'answer': 2}), ('skip', {'answer': 'skip'}),
    ('options', {'command': 'options'}), ('ff 30', {'command': 'ff', 'days': 30}),
    ('ff 999', {'command': 'bad_days'}), ('try 1 and 3', {'command': 'select', 'options': [1, 3]}),
    ('reset', {'command': 'reset'}), ('99', {'command': 'help'}),
])
def test_fallback(text, intent):
    assert fallback(text, QUESTION) == intent


@pytest.mark.parametrize('candidate', [
    {'address': '999 Invented Ave'}, {'url': 'https://evil.example'}, {'answer': 99},
    {'answer': True}, {'grade': 'A', 'annual_usd': 10}, {'command': 'ff', 'days': 999},
    {'answer': 2, 'explanation': '$10/year'}, {'command': 'reset'},
])
def test_llm_untrusted_output_rejected(candidate):
    assert validate(candidate, 'my windows are double glazed', QUESTION) is None


def test_asi_only_classifies_and_no_estimate_in_prompt():
    def handler(req):
        assert req.url == 'https://api.asi1.ai/v1/chat/completions'
        body = json.loads(req.content)
        assert body['model'] == 'asi1'
        assert 'p50' not in req.content.decode() and 'annual_usd' not in req.content.decode()
        return httpx.Response(200, json={'choices': [{'message': {'content': '{"answer":2}'}}]})
    parser = IntentParser(key='test-not-secret', transport=httpx.MockTransport(handler))
    assert run(parser.parse('There are two sheets of glass', QUESTION)) == {'answer': 2}
    assert parser.llm_successes == 1


@pytest.mark.parametrize('mode', ['unavailable', 'invalid_json', 'invented'])
def test_llm_falls_back(mode):
    def handler(req):
        if mode == 'unavailable':
            raise httpx.ConnectError('offline')
        value = 'not json' if mode == 'invalid_json' else '{"address":"999 Invented Ave","annual_usd":10}'
        return httpx.Response(200, json={'choices': [{'message': {'content': value}}]})
    parser = IntentParser(key='test', transport=httpx.MockTransport(handler))
    assert run(parser.parse('What can help this rental?', QUESTION)) == {'command': 'help'}


def test_reply_numbers_only_from_api_fields():
    text = estimate_text(EST, QUESTION)
    for value in ('$701', '$1,003', '$1,807', '$19', '3.2', '57/100', 'Top 16.3%'):
        assert value in text
    assert 'predicted' in text and 'Grade B–C' in text and 'estimated' in text
    blank = estimate_text({'building': {}, 'bill': {}, 'co2_t': {}})
    assert '$' not in blank and '%' not in blank and 'tonnes' not in blank
    locked = estimate_text({**EST, 'locked': True})
    assert '🔒 locked' in locked


def test_tips_never_borrow_catalog_figures_and_negative_cost_honest():
    text = suggestions_text(SUGGESTIONS)
    assert '999999' not in text and '999,999' not in text
    assert 'Tip only' in text and '$219/year saved' in text and 'projected if completed' in text
    bad = deepcopy(SUGGESTIONS[0]); bad['projected']['usd_saved_yr'] = -145
    assert 'costs $145/year more' in suggestions_text([bad])


def test_simulation_requires_label_and_never_claims_verified():
    assert 'No savings are claimed' in simulation_text({'totals': {'usd_saved': 999}})
    text = simulation_text({'label': 'simulated_projected_if_kept', 'commitments': [{'title': 'Windows', 'modeled': True}],
                           'totals': {'days': 30, 'usd_saved': 13, 'kg_co2_saved': 5}})
    assert '$13 saved' in text and '30 days' in text and 'No savings are verified' in text


class FakeAPI:
    def __init__(self):
        self.calls = []

    async def request(self, method, path, body=None):
        self.calls.append((method, path, body))
        await asyncio.sleep(0)  # Exercise overlapping transport retries while API I/O is pending.
        if path == '/estimate':
            return {**deepcopy(EST), 'session_id': body.get('address', 'url')}
        if path == '/answer':
            return {**deepcopy(EST), 'session_id': body['session_id'], 'locked': True, 'answers': {QUESTION['id']: body['answer']}}
        if path.startswith('/commitments/suggested'):
            return {'commitments': deepcopy(SUGGESTIONS)}
        if path == '/simulate/fast-forward':
            return {'label': 'simulated_projected_if_kept', 'commitments': [{'title': 'Windows', 'modeled': bool(body['catalog_ids'])}],
                    'totals': {'days': body['days'], 'usd_saved': 13, 'kg_co2_saved': 5}}
        raise AssertionError(path)


def test_sender_isolation_state_answers_options_and_ff():
    async def scenario():
        api = FakeAPI(); chats = Conversations(api, IntentParser(key=''))
        a = await chats.reply('alice', '1514 Morton Ave')
        b = await chats.reply('bob', '912 Mary St')
        assert 'share?session=1514%20Morton%20Ave' in a and 'share?session=912%20Mary%20St' in b and 'watch?session=1514%20Morton%20Ave' in a
        assert 'Local preview links' in a and '/?session=' in a and '/compare?a=' in a
        answer = await chats.reply('alice', '2')
        assert '🔒 locked' in answer and 'How many window panes' not in answer
        assert chats.states['bob'].question == QUESTION
        await chats.reply('alice', 'options')
        assert 'cannot enter' in await chats.reply('alice', 'try 2')
        await chats.reply('alice', 'try 1')
        assert 'Simulation, not real usage' in await chats.reply('alice', 'ff 30')
        assert api.calls[-1][2] == {'session_id': '1514 Morton Ave', 'days': 30, 'catalog_ids': ['window_upgrade']}
        await chats.reply('alice', 'reset')
        assert chats.states['alice'].estimate is None and chats.states['bob'].estimate is not None
    run(scenario())


def test_api_error_passthrough_and_key_on_every_call():
    def handler(req):
        assert req.headers['x-agent-key'] == 'test-key'
        return httpx.Response(422, json={'detail': {'code': 'not_a_home', 'message': 'Exact API message.'}})
    async def scenario():
        api = HiddenRentAPI(agent_key='test-key', transport=httpx.MockTransport(handler))
        chats = Conversations(api, IntentParser(key=''))
        assert await chats.reply('a', '1514 Morton Ave') == 'Exact API message.'
        with pytest.raises(ApiError, match='Exact API message'):
            await api.request('GET', '/commitments/suggested?session_id=test')
    run(scenario())


@pytest.mark.parametrize('concurrent', [False, True])
def test_protocol_ack_and_text_reply_without_end_session(concurrent):
    from agent import protocol_for
    from uagents_core.contrib.protocols.chat import ChatMessage, ChatAcknowledgement, TextContent
    class Log:
        def info(self, *args): pass
        def error(self, *args): pass
    class Context:
        logger = Log()
        sent = []
        async def send(self, sender, message): self.sent.append((sender, message))
    async def scenario():
        chats = Conversations(FakeAPI(), IntentParser(key=''))
        proto = protocol_for(chats)
        handler = proto._signed_message_handlers[ChatMessage.build_schema_digest(ChatMessage)]
        ctx = Context()
        msg = ChatMessage(timestamp=datetime.now(timezone.utc), msg_id=uuid4(), content=[TextContent(type='text', text='1514 Morton Ave')])
        if concurrent:
            await asyncio.gather(handler(ctx, 'alice', msg), handler(ctx, 'alice', msg))
        else:
            await handler(ctx, 'alice', msg)
            await handler(ctx, 'alice', msg)
        assert len(chats.api.calls) == 1
        assert isinstance(ctx.sent[0][1], ChatAcknowledgement)
        responses = [m for _, m in ctx.sent if isinstance(m, ChatMessage)]
        assert len(responses) == 2
        assert all(isinstance(c, TextContent) for c in responses[0].content)
    run(scenario())


def test_clear_input_cannot_be_overridden_by_llm():
    def handler(req):
        raise AssertionError('LLM should not be called for an unambiguous answer/address')
    parser = IntentParser(key='test', transport=httpx.MockTransport(handler))
    assert run(parser.parse('double', QUESTION)) == {'answer': 2}
    assert run(parser.parse('1514 Morton Ave', QUESTION)) == {'address': '1514 Morton Ave'}

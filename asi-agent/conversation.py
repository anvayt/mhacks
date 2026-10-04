"""One ordered in-memory conversation per cryptographically identified sender."""
import asyncio
import os
from dataclasses import dataclass, field
from urllib.parse import urlencode

from api_client import ApiError, HiddenRentAPI
from intents import IntentParser
from replies import WELCOME, estimate_text, links, question_text, simulation_text, suggestions_text


@dataclass
class State:
    estimate: dict | None = None
    suggestions: list = field(default_factory=list)
    selected: list[str] = field(default_factory=list)

    @property
    def question(self):
        if not self.estimate or self.estimate.get('locked'):
            return None
        known = self.estimate.get('answers', {})
        return next((q for q in self.estimate.get('questions', []) if q.get('id') not in known), None)


class Conversations:
    def __init__(self, api=None, parser=None, web_base=None, onboard_base=None):
        self.api = api or HiddenRentAPI()
        self.parser = parser or IntentParser()
        self.web_base = web_base or os.getenv('WEB_BASE_URL', 'http://localhost:3000')
        self.onboard_base = onboard_base or os.getenv('ONBOARD_URL', 'http://localhost:8787')
        self.states = {}
        self.locks = {}

    async def reply(self, sender, text):
        async with self.locks.setdefault(sender, asyncio.Lock()):
            state = self.states.setdefault(sender, State())
            if len(text) > 4000:
                return 'Please send just the listing link, address, answer or command.'
            intent = await self.parser.parse(text, state.question)
            try:
                message = await self._handle(state, intent)
            except ApiError as exc:
                message = str(exc)  # API detail.message passes through without LLM rewriting.
            if state.estimate and state.estimate.get('session_id'):
                message += '\n\n' + links(state.estimate['session_id'], self.web_base, self.onboard_base)
            return message

    async def _handle(self, s, intent):
        if 'address' in intent or 'url' in intent:
            est = await self.api.request('POST', '/estimate', intent)
            s.estimate, s.suggestions, s.selected = est, [], []
            return estimate_text(est, s.question)
        command = intent.get('command')
        if command == 'reset':
            s.estimate, s.suggestions, s.selected = None, [], []
            return 'This agent has forgotten your conversation. Existing API report links remain valid.\n' + WELCOME
        if command == 'bad_days':
            return 'Use the fast-forward day range shown by the API: send ff followed by a valid day count.'
        if not s.estimate:
            return WELCOME
        sid = s.estimate['session_id']
        if 'answer' in intent and s.question:
            est = await self.api.request('POST', '/answer', {'session_id': sid, 'question_id': s.question['id'], 'answer': intent['answer']})
            s.estimate, s.suggestions, s.selected = est, [], []
            return estimate_text(est, s.question)
        if command == 'options':
            result = await self.api.request('GET', '/commitments/suggested?' + urlencode({'session_id': sid}))
            s.suggestions = result.get('commitments', [])
            return suggestions_text(s.suggestions)
        if command == 'select':
            indices = intent['options']
            if not s.suggestions or any(i < 1 or i > len(s.suggestions) for i in indices):
                return 'Say options first, then choose numbers from that list.'
            selected = [s.suggestions[i - 1] for i in dict.fromkeys(indices)]
            if any(x.get('pending_model') or not x.get('projected') for x in selected):
                return 'Tips without modeled effects cannot enter the simulation. Choose options with priced effects.'
            s.selected = [x['catalog_id'] for x in selected]
            return 'Selected a what-if only: ' + '; '.join(x['title'] for x in selected) + '.\nProjected if completed; nothing is saved as a commitment. Send ff followed by days.'
        if command == 'ff':
            result = await self.api.request('POST', '/simulate/fast-forward', {'session_id': sid, 'days': intent['days'], 'catalog_ids': s.selected})
            return simulation_text(result)
        return question_text(s.question) if s.question else 'Say options for improvements, or send another rental listing.'

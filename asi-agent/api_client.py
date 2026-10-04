"""The sole source of energy, grade and simulation figures is Hidden Rent's API."""
import os

import httpx


class ApiError(Exception):
    pass


class HiddenRentAPI:
    def __init__(self, base_url=None, agent_key=None, transport=None):
        self.base_url = (base_url or os.getenv('API_BASE_URL', 'http://localhost:8000')).rstrip('/')
        self.key = agent_key if agent_key is not None else os.getenv('AGENT_API_KEY', '')
        self.transport = transport

    async def request(self, method, path, body=None):
        async with httpx.AsyncClient(base_url=self.base_url, timeout=180, transport=self.transport,
                                     headers={'X-Agent-Key': self.key}, follow_redirects=False) as client:
            try:
                response = await client.request(method, path, json=body)
            except httpx.HTTPError:
                raise ApiError("Hidden Rent's API is unavailable. Please try again shortly.") from None
        try:
            data = response.json()
        except ValueError:
            raise ApiError('The API returned an unreadable response. Please try again.') from None
        if response.is_error:
            detail = data.get('detail', {}) if isinstance(data, dict) else {}
            message = detail.get('message') if isinstance(detail, dict) else None
            raise ApiError(message or 'The API could not complete that request. Please try again.')
        if not isinstance(data, dict):
            raise ApiError('The API returned an unexpected response. Please try again.')
        return data

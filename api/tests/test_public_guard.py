import asyncio

import httpx
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app import public_guard
from app.public_guard import PublicGuard


@pytest.fixture
def guarded(monkeypatch):
    monkeypatch.delenv('AGENT_API_KEY', raising=False)
    monkeypatch.delenv('PUBLIC_TUNNEL', raising=False)
    app = FastAPI()
    now = [1000.0]
    app.add_middleware(PublicGuard, limit=3, photo_limit=1, clock=lambda: now[0])

    @app.api_route('/{path:path}', methods=['GET', 'POST'])
    async def echo(request: Request, path: str):
        return {'body': (await request.body()).decode()}

    return TestClient(app), now


def test_per_ip_and_window(guarded):
    client, now = guarded
    assert [client.post('/estimate', json={}).status_code for _ in range(4)] == [200, 200, 200, 429]
    r = client.post('/answer', json={})
    assert r.json()['detail']['code'] == 'slow_down' and r.headers['retry-after'] == '60'
    assert client.get('/city').status_code == 200
    assert client.get('/health').status_code == 200
    now[0] += 60
    assert client.post('/estimate', json={}).status_code == 200


@pytest.mark.parametrize('path', ['/estimate', '/answer', '/compare', '/calibrate', '/projection', '/properties', '/auth/web/start'])
def test_post_routes_limited(guarded, path):
    client, _ = guarded
    assert [client.post(path, json={}).status_code for _ in range(4)][-1] == 429


@pytest.mark.parametrize('path', ['/map/a', '/forecast/a', '/commitments/suggested/a', '/leaderboard/position/a'])
def test_get_routes_limited(guarded, path):
    client, _ = guarded
    assert [client.get(path).status_code for _ in range(4)][-1] == 429


def test_only_valid_nonempty_key_bypasses(guarded, monkeypatch):
    client, _ = guarded
    assert [client.post('/estimate', headers={'X-Agent-Key': 'anything'}, json={}).status_code for _ in range(4)][-1] == 429
    monkeypatch.setenv('AGENT_API_KEY', 'test-key')
    assert client.post('/estimate', headers={'X-Agent-Key': 'wrong'}, json={}).status_code == 429
    for _ in range(8):
        assert client.post('/calibrate', headers={'X-Agent-Key': 'test-key'}, json={'bill_image_base64': 'photo'}).status_code == 200


def test_photo_limit_is_stricter_and_uses_parsed_key(guarded):
    client, now = guarded
    assert client.post('/calibrate', json={'note': 'bill_image_base64'}).status_code == 200
    assert client.post('/calibrate', content='{"bill_image_\\u0062ase64":"photo"}').status_code == 200
    r = client.post('/calibrate', json={'bill_image_base64': 'another'})
    assert r.status_code == 429 and r.headers['retry-after'] == '600'
    now[0] += 60
    assert client.post('/calibrate', json={'therms': 80}).status_code == 200
    assert client.post('/calibrate', json={'bill_image_base64': 'another'}).status_code == 429
    now[0] += 600
    assert client.post('/calibrate', json={'bill_image_base64': 'another'}).status_code == 200


def test_cf_header_only_with_explicit_loopback_trust(monkeypatch):
    guard = PublicGuard(None)
    headers = {b'cf-connecting-ip': b'203.0.113.1', b'x-forwarded-for': b'203.0.113.2'}
    assert guard.visitor({'client': ('127.0.0.1', 10)}, headers) == '127.0.0.1'
    monkeypatch.setenv('PUBLIC_TUNNEL', '1')
    assert guard.visitor({'client': ('127.0.0.1', 10)}, headers) == '203.0.113.1'
    assert guard.visitor({'client': ('192.0.2.1', 10)}, headers) == '192.0.2.1'
    assert guard.visitor({'client': ('127.0.0.1', 10)}, {b'x-forwarded-for': b'203.0.113.2'}) == '127.0.0.1'
    for _ in range(30): assert guard.allow('203.0.113.1', False)
    assert not guard.allow('203.0.113.1', False)
    assert guard.allow('203.0.113.2', False)


def test_cap_even_for_agent_and_declared_length(guarded, monkeypatch):
    client, _ = guarded
    monkeypatch.setattr(public_guard, 'MAX_BODY', 100)
    monkeypatch.setattr(public_guard, 'MAX_PHOTO', 50)
    monkeypatch.setenv('AGENT_API_KEY', 'test-key')
    r = client.post('/calibrate', headers={'X-Agent-Key': 'test-key'}, json={'bill_image_base64': 'x' * 51})
    assert r.status_code == 413 and r.json()['detail']['code'] == 'bill_too_large'
    assert client.post('/estimate', content='x' * 101).status_code == 413
    assert client.post('/estimate', json={'address': 'small'}).status_code == 200


@pytest.mark.parametrize('length', [None, b'1'])
def test_cap_actual_chunked_bytes_even_with_lying_length(monkeypatch, length):
    monkeypatch.setattr(public_guard, 'MAX_BODY', 10)
    called = []
    async def downstream(scope, receive, send): called.append(True)
    chunks = iter([{'type': 'http.request', 'body': b'123456', 'more_body': True},
                   {'type': 'http.request', 'body': b'123456', 'more_body': False}])
    outputs = []
    async def receive(): return next(chunks)
    async def send(event): outputs.append(event)
    headers = [] if length is None else [(b'content-length', length)]
    asyncio.run(PublicGuard(downstream)({'type': 'http', 'headers': headers, 'method': 'POST', 'path': '/calibrate'}, receive, send))
    assert outputs[0]['status'] == 413 and not called


def test_health_model_available_and_down(monkeypatch):
    from app.main import app
    client = TestClient(app)
    monkeypatch.setattr(httpx, 'get', lambda *a, **k: httpx.Response(200))
    assert client.get('/health').json() == {'status': 'ok', 'model': {'available': True}}
    def down(*args, **kwargs): raise httpx.ConnectError('offline')
    monkeypatch.setattr(httpx, 'get', down)
    assert client.get('/health').json() == {'status': 'degraded', 'model': {'available': False}}


def test_cors_has_explicit_origin_without_credentials():
    from app.main import app
    from fastapi.middleware.cors import CORSMiddleware
    cors = next(m for m in app.user_middleware if m.cls is CORSMiddleware)
    assert '*' not in cors.kwargs['allow_origins']
    assert cors.kwargs['allow_credentials'] is False


def test_deep_json_returns_readable_error(guarded, monkeypatch):
    client, _ = guarded
    def too_deep(*args, **kwargs):
        raise RecursionError('nested JSON')
    with monkeypatch.context() as patch:
        patch.setattr(public_guard.json, 'loads', too_deep)
        r = client.post('/calibrate', content='[[[0]]]')
    assert r.status_code == 422 and r.json()['detail']['code'] == 'bad_bill'


def test_lone_surrogate_does_not_crash_guard(guarded):
    client, _ = guarded
    r = client.post('/calibrate', content='{"bill_image_base64":"\\ud800"}')
    assert r.status_code == 200  # Endpoint owns base64 validation; middleware only budgets/caps.

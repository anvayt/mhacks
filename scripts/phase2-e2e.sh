#!/usr/bin/env bash
# Phase 2 contract check. Uses a fictional phone by default; does not send messages.
# API_BASE_URL=http://localhost:8000 AGENT_API_KEY=... make phase2-check
# Override PHASE2_TEST_PHONE only for a disposable account: this check moves it.
# The API must already be running. No model process is started or contacted directly.
set -euo pipefail
command -v python3 >/dev/null || { echo 'FAIL python3 is required (standard library only).' >&2; exit 1; }
command -v curl >/dev/null || { echo 'FAIL curl is required.' >&2; exit 1; }
exec python3 - <<'PY'
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote, urlsplit

BASE = os.environ.get('API_BASE_URL', 'http://localhost:8000').rstrip('/')
KEY = os.environ.get('AGENT_API_KEY', '')
PHONE = os.environ.get('PHASE2_TEST_PHONE', '+12025550199')  # NANPA fictional 555-0199
TIMEOUT = os.environ.get('PHASE2_TIMEOUT_SECONDS', '240')
parts = urlsplit(BASE)
if parts.scheme not in ('http', 'https') or not parts.netloc or parts.username or parts.password or parts.query or parts.fragment:
    sys.exit('FAIL API_BASE_URL must be an HTTP(S) base URL without credentials, query, or fragment.')
try:
    assert float(TIMEOUT) > 0 and math.isfinite(float(TIMEOUT))
except (ValueError, AssertionError):
    sys.exit('FAIL PHASE2_TIMEOUT_SECONDS must be a positive finite number.')
if '\r' in KEY or '\n' in KEY:
    sys.exit('FAIL AGENT_API_KEY cannot contain a newline.')


class CheckFailed(Exception):
    pass


def require(condition, message):
    if not condition:
        raise CheckFailed(message)


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


state = {}
results = []
routes = None


def api(method, path, body=None, auth='agent'):
    # Headers and responses remain in a private temporary directory. Credentials
    # never enter curl's argument list, logs, or the pass/fail table.
    headers = ['Content-Type: application/json', 'Accept: application/json']
    if auth == 'agent':
        require(bool(KEY), 'AGENT_API_KEY is unset; agent-only requests need X-Agent-Key')
        headers.append('X-Agent-Key: ' + KEY)
    elif auth == 'web':
        require(state.get('token'), 'web login did not yield a token')
        headers.append('Authorization: Bearer ' + state['token'])
    header_file = temp / 'headers'
    header_file.write_text('\n'.join(headers) + '\n')
    header_file.chmod(0o600)
    response_file = temp / 'response'
    cmd = ['curl', '--silent', '--show-error', '--connect-timeout', '5', '--max-time', TIMEOUT,
           '--request', method, '--header', '@' + str(header_file), '--output', str(response_file),
           '--write-out', '%{http_code}', BASE + path]
    if body is not None:
        cmd += ['--data-binary', '@-']
    result = subprocess.run(cmd, input=json.dumps(body) if body is not None else None,
                            text=True, capture_output=True)
    if result.returncode:
        raise CheckFailed(f'API connection failed (curl exit {result.returncode}); check API_BASE_URL and server logs')
    status = int(result.stdout) if result.stdout.isdigit() else 0
    try:
        data = json.loads(response_file.read_text())
    except (ValueError, OSError):
        data = None
    if status == 404:
        raise CheckFailed('HTTP 404: not merged yet, or referenced record is missing')
    if status not in (200, 201):
        # Only a machine error code is printed, never a server message containing
        # a phone, token, bill, or exact private address.
        detail = data.get('detail') if isinstance(data, dict) else None
        code = detail.get('code') if isinstance(detail, dict) else None
        safe = code if isinstance(code, str) and re.fullmatch(r'[a-z_]{1,60}', code) else 'request_failed'
        raise CheckFailed(f'HTTP {status}: {safe}')
    require(isinstance(data, (dict, list)), 'response was not a JSON object or array')
    return data


def run(name, method, route, fn, needs=()):
    try:
        canonical = lambda path: re.sub(r'\{[^}]+\}', '{}', path)
        available = routes is None or any(canonical(path) == canonical(route) and method.lower() in verbs
                                         for path, verbs in routes.items())
        if not available:
            raise CheckFailed(f'not merged yet: {method} {route} is absent from OpenAPI (would return 404)')
        missing = [key for key in needs if not state.get(key)]
        require(not missing, 'blocked by an earlier failure: missing ' + ', '.join(missing))
        detail = fn()
        results.append(('PASS', name, detail))
    except (CheckFailed, KeyError, TypeError, ValueError, IndexError) as exc:
        detail = str(exc) if isinstance(exc, CheckFailed) else f'response shape mismatch ({type(exc).__name__})'
        results.append(('FAIL', name, detail))
    print(f'{results[-1][0]:4} | {name:28} | {results[-1][2]}', flush=True)


def ident(obj, *keys):
    for key in keys:
        if isinstance(obj, dict) and obj.get(key):
            return str(obj[key])
    raise CheckFailed('response is missing ' + '/'.join(keys))


def endpoint_id(value):
    return quote(str(value), safe='')


def auth_start():
    d = api('POST', '/auth/web/start', {'phone': PHONE}, auth=None)
    state['login_id'] = ident(d, 'login_id', 'id')
    state['login_code'] = ident(d, 'code', 'login_code')
    return 'login challenge created; code and phone withheld'


def auth_confirm():
    d = api('POST', '/auth/web/confirm', {'phone': PHONE, 'code': state['login_code']})
    require(d.get('user_id') or d.get('confirmed') or d.get('status') == 'confirmed', 'confirmation not acknowledged')
    if d.get('user_id'):
        state['confirmed_user_id'] = str(d['user_id'])
    return 'agent confirmed the test login'


def auth_poll():
    d = api('GET', '/auth/web/' + endpoint_id(state['login_id']), auth=None)
    state['token'] = ident(d, 'token', 'access_token')
    return 'web bearer token received; token withheld'


def phone_login():
    first = api('POST', '/auth/phone', {'phone': PHONE})
    second = api('POST', '/auth/phone', {'phone': PHONE})
    user = ident(first, 'user_id')
    require(user == ident(second, 'user_id'), 'same phone produced different users')
    require(not second.get('created'), 'second phone login incorrectly created another user')
    if state.get('confirmed_user_id'):
        require(state['confirmed_user_id'] == user, 'web and phone login resolved different users')
    state['user_id'] = user
    return 'two calls returned the same user'


def save_property():
    d = api('POST', '/properties', {'user_id': state['user_id'], 'address': '1514 Morton Ave, Ann Arbor, MI'})
    state['property_id'] = ident(d, 'property_id')
    e = d['estimate']
    state['session_id'] = ident(e, 'session_id')
    require(d.get('active') is True, 'new property is not active')
    require(number(e['bill']['annual']['p50']), 'estimate lacks annual p50')
    state['estimate'] = e
    return f"1514 Morton: grade {e['grade']}, annual ${e['bill']['annual']['p50']:,.0f}"


def me():
    d = api('GET', '/me/' + endpoint_id(state['user_id']), auth='web')
    require(d['current_property_id'] == state['property_id'], 'web account has the wrong current property')
    require(any(ident(p, 'id', 'property_id') == state['property_id'] for p in d['properties']), 'property is absent from account history')
    return f"web authorization works; {len(d['properties'])} property record(s)"


def suggested():
    d = api('GET', '/commitments/suggested/' + endpoint_id(state['property_id']))
    state['suggestions'] = d['commitments']
    require(any(c.get('catalog_id') == 'window_upgrade' for c in state['suggestions']), 'window_upgrade is missing from suggestions')
    return f"{len(state['suggestions'])} suggestions; window_upgrade present"


def accept():
    d = api('POST', '/commitments', {'user_id': state['user_id'], 'property_id': state['property_id'], 'catalog_id': 'window_upgrade'})
    require(d.get('status') == 'accepted', 'commitment was not accepted')
    state['commitment_id'] = ident(d, 'id', 'commitment_id')
    return 'window_upgrade accepted'


def projection():
    selected = [state['commitment_id']]
    # The commitments API also accepts catalog IDs for what-if previews. Include
    # one advertised placeholder to exercise honesty rather than only an empty list.
    placeholder = next((x['catalog_id'] for x in state.get('suggestions', [])
                        if x.get('pending_model') and x.get('catalog_id') != 'window_upgrade'), None)
    if placeholder:
        selected.append(placeholder)
    d = api('POST', '/projection', {'property_id': state['property_id'], 'commitment_ids': selected})
    require(d.get('label') == 'projected_if_completed', 'projection is missing projected_if_completed label')
    current, initial = d['current'], state['estimate']
    require(current['score'] == initial['score'] and current['grade'] == initial['grade'], 'projection changed current score/grade')
    require(current['bill_annual'] == initial['bill']['annual'], 'projection changed current annual bill')
    require(isinstance(d.get('not_modeled'), list), 'projection must list placeholders in not_modeled')
    ids = {x if isinstance(x, str) else x.get('catalog_id', x.get('commitment_id')) for x in d['not_modeled']}
    if placeholder:
        require(placeholder in ids, 'advertised placeholder is missing from not_modeled')
    window = next((x for x in state.get('suggestions', []) if x.get('catalog_id') == 'window_upgrade'), {})
    if window.get('pending_model'):
        require('window_upgrade' in ids or state['commitment_id'] in ids, 'pending window_upgrade is missing from not_modeled')
    saved = api('GET', '/session/' + endpoint_id(state['session_id']))
    require(saved['score'] == initial['score'] and saved['bill']['annual'] == initial['bill']['annual'], 'projection overwrote the current session')
    state['projection'] = d
    return f"current {current['grade']} unchanged; projected_if_completed; {len(d['not_modeled'])} not modeled"


def position():
    d = api('GET', '/leaderboard/position/' + endpoint_id(state['property_id']))
    c = d['current']
    require(c['score'] == state['estimate']['score'] and c['grade'] == state['estimate']['grade'], 'position current differs from estimate')
    require(number(c['rank']) and number(c['of']) and 1 <= c['rank'] <= c['of'], 'invalid current rank')
    require(d.get('projected') and d['projected'].get('label') == 'projected_if_completed', 'accepted projection has no labelled ghost marker')
    return f"current {c['grade']}, rank {c['rank']}/{c['of']}; labelled projected ghost"


def calibrate():
    d = api('POST', '/calibrate', {'session_id': state['session_id'], 'property_id': state['property_id'],
                                 'therms': 150, 'kwh': 400, 'start': '2026-01-01', 'end': '2026-01-31'})
    state['bill_id'] = ident(d, 'bill_id')
    snap = d.get('snapshot') or {}
    require(snap.get('source') == 'bill_regrade', 'calibration snapshot source is not bill_regrade')
    require(snap.get('property_id') == state['property_id'], 'bill snapshot belongs to a different property')
    state['snapshot_id'] = ident(snap, 'id')
    require(d.get('verified') is False and d.get('impact') is None, 'accepted-but-uncompleted commitment must not produce verified impact')
    require(number(d.get('pct_vs_expected_for_weather')), 'missing weather-normalized percent')
    return f"HYPOTHETICAL bill: {d['pct_vs_expected_for_weather']}%; bill_regrade; verified=false"


def history():
    d = api('GET', '/properties/' + endpoint_id(state['property_id']) + '/history')
    require(any(x.get('id') == state['bill_id'] for x in d['bills']), 'saved bill is missing from history')
    require(any(x.get('id') == state['snapshot_id'] and x.get('source') == 'bill_regrade' for x in d['snapshots']), 'bill snapshot is missing from history')
    require(not any(x.get('source') == 'projection' for x in d['snapshots']), 'projection was incorrectly stored as a snapshot')
    state['history'] = d
    return f"{len(d['snapshots'])} snapshots, {len(d['bills'])} bills, {len(d['impact'])} verified impacts"


def checkin():
    d = api('POST', '/checkins/trigger', {'user_id': state['user_id']})
    require(d.get('message_hint') == 'still_at_address' and d.get('property_id') == state['property_id'], 'check-in did not target the current property')
    return 'still_at_address for the current property; no message sent'


def reminder():
    d = api('POST', '/reminders/demo-send', {'user_id': state['user_id'], 'kind': 'checkin'})
    require(d.get('kind') == 'checkin' and d.get('property_id') == state['property_id'] and d.get('reminder_id'), 'demo reminder is missing its check-in facts')
    return 'check-in reminder returned; /sent not called; no message sent'


def calendar():
    d = api('POST', '/calendar/connect', {'user_id': state['user_id']})
    require(isinstance(d.get('auth_url'), str) and d['auth_url'], 'Calendar did not provide auth_url')
    return 'authorization URL returned; mock=' + str(bool(d.get('mock'))).lower() + '; URL not opened'


def moved():
    d = api('POST', '/properties', {'user_id': state['user_id'], 'address': '912 Mary St, Ann Arbor, MI'})
    new_id = ident(d, 'property_id')
    require(new_id != state['property_id'] and d.get('active') is True, 'move did not create a new active property')
    account = api('GET', '/me/' + endpoint_id(state['user_id']))
    require(account.get('current_property_id') == new_id, 'moved account still points at the old property')
    old = next((p for p in account['properties'] if ident(p, 'id', 'property_id') == state['property_id']), None)
    require(old is not None and old.get('active') is False, 'old property was not archived')
    require(sum(p.get('active') is True for p in account['properties']) == 1, 'account has multiple active homes')
    retained = api('GET', '/properties/' + endpoint_id(state['property_id']) + '/history')
    for key in ('snapshots', 'bills', 'impact', 'commitments'):
        before = {x['id'] for x in state['history'][key]}
        after = {x['id'] for x in retained[key]}
        require(before <= after, 'moving lost old ' + key)
    new_history = api('GET', '/properties/' + endpoint_id(new_id) + '/history')
    require(not new_history['impact'] and not new_history['bills'], 'moving carried old evidence to the new property')
    return '912 Mary active; Morton archived; all old history retained; no impact carried across'


print('Phase 2 check: disposable account; typed bill values are HYPOTHETICAL; no texts/events sent.')
print('STATUS | STEP                         | RESULT')
with tempfile.TemporaryDirectory(prefix='hidden-rent-phase2-') as directory:
    temp = Path(directory)
    try:
        routes = api('GET', '/openapi.json', auth=None)['paths']
    except (CheckFailed, KeyError, TypeError):
        pass  # Individual requests still report concrete transport/HTTP failures.
    run('web login start', 'POST', '/auth/web/start', auth_start)
    run('web login confirm (agent)', 'POST', '/auth/web/confirm', auth_confirm, ('login_code',))
    run('web login token', 'GET', '/auth/web/{id}', auth_poll, ('login_id',))
    run('phone login idempotency', 'POST', '/auth/phone', phone_login)
    run('save Morton property', 'POST', '/properties', save_property, ('user_id',))
    run('web account /me', 'GET', '/me/{user_id}', me, ('user_id', 'property_id', 'token'))
    run('suggested commitments', 'GET', '/commitments/suggested/{property_id}', suggested, ('property_id',))
    run('accept window_upgrade', 'POST', '/commitments', accept, ('user_id', 'property_id'))
    run('projection honesty', 'POST', '/projection', projection, ('property_id', 'commitment_id', 'estimate', 'session_id'))
    run('leaderboard ghost marker', 'GET', '/leaderboard/position/{property_id}', position, ('property_id', 'estimate', 'projection'))
    run('bill and new snapshot', 'POST', '/calibrate', calibrate, ('property_id', 'session_id'))
    run('property history', 'GET', '/properties/{id}/history', history, ('property_id', 'bill_id', 'snapshot_id'))
    run('manual check-in', 'POST', '/checkins/trigger', checkin, ('user_id', 'property_id'))
    run('demo reminder', 'POST', '/reminders/demo-send', reminder, ('user_id', 'property_id'))
    run('Calendar connect', 'POST', '/calendar/connect', calendar, ('user_id',))
    run('move and preserve history', 'POST', '/properties', moved, ('user_id', 'property_id', 'history'))
failed = sum(status != 'PASS' for status, _, _ in results)
print(f'RESULT: {len(results) - failed} passed, {failed} failed. Missing Phase 2 routes fail until merged.')
sys.exit(1 if failed else 0)
PY

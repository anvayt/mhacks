"""Live evidence against the isolated P1 model/API; never starts or stops servers."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = os.getenv('P1_API_URL', 'http://localhost:8061').rstrip('/')
MODEL = os.getenv('P1_MODEL_URL', 'http://localhost:8011').rstrip('/')
OUT = Path(__file__).resolve().parents[1] / 'results' / 'finish' / 'live_smoke.json'
ACTIONS = ['air_sealing', 'attic_insulation', 'wall_insulation', 'heat_pump', 'thermostat_setback']


def call(base, path, body=None):
    headers = {'Content-Type': 'application/json'}
    if base == API and os.getenv('AGENT_API_KEY'):
        headers['X-Agent-Key'] = os.environ['AGENT_API_KEY']
    req = Request(base + path, data=None if body is None else json.dumps(body).encode(), headers=headers)
    with urlopen(req, timeout=240) as response:
        return json.load(response)


def main():
    result = {'created_at': datetime.now(timezone.utc).isoformat(), 'api': API, 'model': MODEL,
              'bill_note': 'Hypothetical typed 80-therm bill, not a real submitted utility bill.'}
    initial = call(API, '/estimate', {'address': '1514 Morton Ave, Ann Arbor, MI'})
    sid = initial['session_id']
    result['morton_initial'] = initial
    steps = []
    for q, answer in [('heating_fuel', 'gas'), ('window_panes', 'single pane')]:
        steps.append(call(API, '/answer', {'session_id': sid, 'question_id': q, 'answer': answer}))
    result['morton_answers'] = steps
    current = steps[-1]
    result['morton_suggested'] = call(API, '/commitments/suggested?' + urlencode({'session_id': sid}))
    entries = {row['catalog_id']: row for row in result['morton_suggested']['commitments']}
    for action in ACTIONS:
        assert not entries[action]['pending_model'], (action, entries[action]['method'])
    for label, actions in [('all', ACTIONS), ('load_only', [a for a in ACTIONS if a != 'heat_pump'])]:
        projection = call(API, '/projection', {'session_id': sid, 'commitment_ids': actions})
        assert not projection['not_modeled'], projection['not_modeled']
        assert projection['current']['bill_annual']['p50'] == current['bill']['annual']['p50']
        assert projection['label'] == 'projected_if_completed'
        result['morton_projection_' + label] = projection
    session = call(API, '/session/' + sid)
    assert session['bill'] == current['bill'], 'Projection changed current estimate'
    bill = {'session_id': sid, 'therms': 80, 'gas_unit': 'therms', 'start': '2026-02-01', 'end': '2026-02-28'}
    result['bill_request'] = bill
    result['morton_calibrate'] = call(API, '/calibrate', bill)
    mp = session['model_params']
    params = {'year': 2026, 'month': 2, 'gas_ccf': result['morton_calibrate']['actual_gas_ccf'],
              'lat': mp['lat'], 'lon': mp['lon'], 'unit_sqft': mp['unit_sqft']}
    result['morton_bill_legacy'] = call(MODEL, '/hc/bill_check?' + urlencode(params))
    result['morton_bill_within'] = call(MODEL, '/hc/bill_check?' + urlencode({**params, 'noise_basis': 'within_building'}))
    result['morton_map'] = call(API, '/map/' + sid)
    assert result['morton_map']['steps'][-1]['lookalikes']['count'] > 0, 'No live Morton peers'
    arrow = call(API, '/estimate', {'address': '2322 Arrowwood Trl, Ann Arbor, MI'})
    result['arrowwood'] = arrow
    result['arrowwood_suggested'] = call(API, '/commitments/suggested?' + urlencode({'session_id': arrow['session_id']}))
    assert arrow['heating_cooling']['method'] == 'metered'
    assert all(row['pending_model'] for row in result['arrowwood_suggested']['commitments'])
    OUT.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS live isolated smoke; evidence:', OUT)
    print('Morton', current['building']['sqft'], 'sqft; annual', current['bill']['annual']['p50'], 'grade', current['grade'])
    for action in ACTIONS:
        print(action, json.dumps(entries[action]['projected']))
    print('Combined', result['morton_projection_all']['delta'])
    print('Load-only', result['morton_projection_load_only']['delta'])
    for field in ['noise_floor', 'estimate_error_floor', 'meaningful', 'pct_vs_expected_for_weather']:
        print('Bill', field, result['morton_calibrate'][field])
    print('Map cloud', result['morton_map']['steps'][-1]['lookalikes']['count'])
    print('Arrowwood: metered, all new effects remain placeholders')


if __name__ == '__main__':
    main()

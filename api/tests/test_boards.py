"""Opt-in privacy, verified evidence, demo gating and read-only placement."""
import copy
from datetime import date
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
import numpy as np
from app import accounts, bills, boards, calibrate, city, commitments, db, score, sessions
from app.main import app
from scripts import seed_demo_board

class Today(date):
    @classmethod
    def today(cls):
        return cls(2026,10,4)

@pytest.fixture
def records(monkeypatch,tmp_path):
    d={k:{} for k in ('users','properties','estimates','snapshots','impacts','tasks','projections')}
    monkeypatch.setattr(boards,'date',Today)
    monkeypatch.delenv('DEMO_SEED',raising=False)
    monkeypatch.setattr(db,'DB_PATH',tmp_path/'app.sqlite')
    monkeypatch.setattr(calibrate,'DB',tmp_path/'calibrate.sqlite')
    monkeypatch.setattr(accounts,'list_users',lambda:list(d['users'].values()))
    monkeypatch.setattr(accounts,'get_property',d['properties'].get)
    monkeypatch.setattr(accounts,'current_property',lambda uid:d['properties'].get(d['users'][uid]['current_property_id']))
    monkeypatch.setattr(sessions,'get',d['estimates'].get)
    monkeypatch.setattr(bills,'list_snapshots',lambda pid:d['snapshots'].get(pid,[]))
    monkeypatch.setattr(bills,'list_impact',lambda pid:d['impacts'].get(pid,[]))
    monkeypatch.setattr(commitments,'list_commitments',lambda property_id=None,user_id=None:d['tasks'].get(property_id,[]))
    monkeypatch.setattr(commitments,'latest_projection',d['projections'].get)
    monkeypatch.setattr(city,'city_costs',lambda kind:[1,2,3,4,5])
    monkeypatch.setattr(score,'peer_costs',lambda kind:np.array([1,2,3,4,5]))  # all-city percentile_city
    d['authorize_calls']=[]
    def authorize(request,uid):
        d['authorize_calls'].append(uid)
        if request.headers.get('Authorization')!='Bearer '+uid:
            raise HTTPException(403,{'code':'forbidden','message':'That home belongs to another account.'})
    monkeypatch.setattr(accounts,'authorize',authorize)
    def add(n,opt_in=True,baseline=2000,avoided=100,building_id=None):
        uid,pid,sid=f'secret-user-{n}',f'secret-property-{n}',f'session-{n}'
        d['users'][uid]={'id':uid,'alias':f'Tree {n}','phone_number':'+17345559876','display_name':'Private Legal Name','leaderboard_opt_in':opt_in,'current_property_id':pid}
        d['properties'][pid]={'id':pid,'user_id':uid,'address':f'{n} Private Street','active':True,'building_id':n if building_id is None else building_id,'session_id':sid}
        d['estimates'][sid]={'session_id':sid,'building':{'sqft':1000,'type':'house'},'bill':{'annual':{'p50':3000}},'score':50,'grade':'C','model_params':{'block_group':'261614004003'}}
        d['snapshots'][pid]=[{'id':f'baseline-{n}','property_id':pid,'source':'initial_estimate','co2_kg_yr':{'p50':baseline},'created_at':'2026-01-01'}]
        d['impacts'][pid]=[{'id':f'impact-{n}','property_id':pid,'baseline_snapshot_id':f'baseline-{n}','period':{'start':'2026-02-01','end':'2026-02-28'},'co2_kg_avoided':avoided,'commitment_ids':[f'commitment-{n}']}]
        return uid,pid,sid
    d['add']=add
    return d

def test_default_unchanged(records,monkeypatch):
    original={'best':[{'name':'Public benchmark'}],'worst_blocks':[{'geoid':'261614004003'}]}
    monkeypatch.setattr(city,'_leaderboard',lambda scope:original)
    for path in ['/leaderboard','/leaderboard?scope=neighborhood']:
        assert TestClient(app).get(path).json()==original

def test_verified_cut_own_baseline_opt_in_no_pii(records):
    records['add'](1,baseline=2000);records['add'](2,baseline=1000);records['add'](3,opt_in=False,avoided=5000)
    r=TestClient(app).get('/leaderboard?board=verified_cut');body=r.json()
    assert r.status_code==200
    assert [(e['alias'],e['value']) for e in body['entries']]==[('Tree 2',10),('Tree 1',5)]
    assert body['empty_reason'] is None
    assert all(e['evidence']=='verified' and e['demo'] is False for e in body['entries'])
    for private in ['Private','secret-user','secret-property','+17345559876','session-']:
        assert private not in r.text

def test_only_matching_verified_impact_not_reported_projected_duplicate_or_cross_home(records):
    _,pid,_=records['add'](1);good=records['impacts'][pid][0]
    records['impacts'][pid]+=[copy.deepcopy(good),{**good,'property_id':'old-home'},{**good,'baseline_snapshot_id':'other'},
                              {**good,'evidence':'projected'},{**good,'evidence':'reported'},{**good,'verified':False}]
    assert boards.board_result('co2_avoided')['entries'][0]['value']==100
    records['properties'][pid]['active']=False
    assert boards.board_result('verified_cut')['entries']==[]

def test_bill_regrade_does_not_reset_baseline_but_moving_does(records):
    uid,pid,_=records['add'](1)
    records['snapshots'][pid].append({'id':'new','property_id':pid,'source':'bill_regrade','co2_kg_yr':{'p50':10},'created_at':'2026-03-01'})
    assert boards.board_result('verified_cut')['entries'][0]['value']==5
    records['users'][uid]['current_property_id']='new-home'
    records['properties']['new-home']={**records['properties'][pid],'id':'new-home','session_id':'new-session'}
    b=boards.board_result('verified_cut');assert b['entries']==[] and b['empty_reason']

def test_ytd_excludes_previous_year_and_future(records):
    _,pid,_=records['add'](1);g=records['impacts'][pid][0]
    records['impacts'][pid]+=[{**g,'period':{'start':'2025-01-01','end':'2025-01-31'}},{**g,'period':{'start':'2026-11-01','end':'2026-11-30'}}]
    assert boards.board_result('co2_avoided')['entries'][0]['value']==100

def test_neighborhood_minimum_five_distinct_homes(records):
    for i in range(1,5):records['add'](i)
    assert boards.board_result('neighborhood')['entries']==[]
    records['add'](5,building_id=1)
    assert boards.board_result('neighborhood')['entries']==[]
    records['add'](6)
    e=boards.board_result('neighborhood')['entries']
    assert len(e)==1 and e[0]['home_count']==5 and e[0]['co2_kg_avoided']==500
    assert e[0]['geoid']=='26161400400' and e[0]['area_type']=='census_tract' and 'alias' not in e[0]

def test_streak_existing_session_store_and_gaps(records):
    _,_,sid=records['add'](1)
    for month,pct in [(1,-10),(3,-12),(4,-4)]:calibrate.record(sid,2026,month,pct)
    e=boards.board_result('streak')['entries'][0]
    assert e['value']==2 and e['evidence']=='bill_checks_with_verified_impact'
    calibrate.record(sid,2026,5,0)
    assert boards.board_result('streak')['entries']==[]

def test_followthrough_verified_or_ledger_and_accepted_history(records):
    _,pid,_=records['add'](1)
    records['tasks'][pid]=[{'id':'commitment-1','property_id':pid,'status':'completed','evidence':'reported'},
      {'id':'verified','property_id':pid,'status':'completed','evidence':'verified'},
      {'id':'reported','property_id':pid,'status':'completed','evidence':'reported'},
      {'id':'dismissed','property_id':pid,'status':'dismissed','accepted_at':'2026-01-01'},
      {'id':'suggested','property_id':pid,'status':'suggested','evidence':'projected'}]
    assert boards.board_result('follow_through')['entries'][0]['value']==25

def test_missing_baseline_empty_and_alias_safety(records):
    uid,pid,_=records['add'](1);records['users'][uid]['alias']='+1 734 555 9876'
    assert boards.board_result('verified_cut')['entries'][0]['alias']=='Anonymous renter'
    records['snapshots'][pid]=[];b=boards.board_result('verified_cut');assert b['entries']==[] and b['empty_reason']

def test_demo_seed_gating_idempotence_and_every_entry_flagged(records,monkeypatch):
    with pytest.raises(SystemExit):seed_demo_board.seed()
    monkeypatch.setenv('DEMO_SEED','1');assert seed_demo_board.seed()==seed_demo_board.seed()==6
    for kind in boards.BOARDS:
        entries=boards.board_result(kind)['entries'];assert entries
        assert all(e['demo'] is True and e['evidence']=='demo' for e in entries)
        assert all(e.get('alias','Demo ').startswith('Demo ') for e in entries)
    monkeypatch.delenv('DEMO_SEED')
    for kind in boards.BOARDS:assert boards.board_result(kind)['entries']==[]

def test_scope_coverage_and_errors(records):
    records['add'](1);c=TestClient(app)
    b=c.get('/leaderboard?board=verified_cut&scope=neighborhood').json();assert b['scope']=='neighborhood' and b['coverage']=='city'
    for path,code in [('/leaderboard?board=bad','bad_board'),('/leaderboard?board=verified_cut&scope=bad','bad_scope')]:
        r=c.get(path);assert r.status_code==422 and r.json()['detail']['code']==code

def test_position_projection_read_only_and_no_pii(records):
    uid,pid,sid=records['add'](1)
    records['projections'][pid]={'property_id':pid,'projected':{'bill_annual':{'p50':1000},'score':90},'label':'projected_if_completed'}
    before=copy.deepcopy(records['estimates'][sid])
    r=TestClient(app).get('/leaderboard/position/'+pid,headers={'Authorization':'Bearer '+uid});b=r.json();assert r.status_code==200
    assert b['current']=={'score':50,'grade':'C','percentile_city':.5,'rank':3,'of':5}
    assert b['projected']=={'rank':1,'percentile_city':.9,'score':90,'label':'projected_if_completed'}
    assert all(set(bar)=={'rank','score','cost_per_sqft'} for bar in b['neighbors'])
    assert records['estimates'][sid]==before and records['authorize_calls']==[uid]
    assert 'Private Street' not in r.text and 'secret-user' not in r.text and 'secret-property' not in r.text

def test_position_without_pending_or_crossproperty_projection(records):
    uid,pid,_=records['add'](1);c=TestClient(app)
    for p in [None,{'property_id':pid,'pending_model':True,'projected':None},{'property_id':'other','projected':{'bill_annual':{'p50':1}}}]:
        records['projections'][pid]=p
        assert c.get('/leaderboard/position/'+pid,headers={'Authorization':'Bearer '+uid}).json()['projected'] is None

def test_position_authorization_and_missing_errors(records):
    uid,pid,_=records['add'](1);c=TestClient(app)
    assert c.get('/leaderboard/position/'+pid).status_code==403
    assert c.get('/leaderboard/position/missing').status_code==404
    records['estimates'].clear()
    assert c.get('/leaderboard/position/'+pid,headers={'Authorization':'Bearer '+uid}).status_code==404

def test_position_ties_midpoint_and_competition_rank(records,monkeypatch):
    uid,pid,_=records['add'](1);monkeypatch.setattr(city,'city_costs',lambda kind:[1,3,3,5])
    b=TestClient(app).get('/leaderboard/position/'+pid,headers={'Authorization':'Bearer '+uid}).json()
    assert b['current']=={'score':50,'grade':'C','percentile_city':.5,'rank':2,'of':4}

def test_position_reads_latest_real_snapshot_never_projection_snapshot(records):
    uid,pid,_=records['add'](1)
    records['snapshots'][pid]+=[{'id':'bill','property_id':pid,'source':'bill_regrade','bill_annual':{'p50':2000},'created_at':'2026-03-01'},
                              {'id':'fake','property_id':pid,'source':'projection','bill_annual':{'p50':1},'created_at':'2026-04-01'}]
    b=TestClient(app).get('/leaderboard/position/'+pid,headers={'Authorization':'Bearer '+uid}).json()
    assert b['current_source']=='bill_regrade' and b['current']['score']==70 and b['current']['rank']==2


def test_streak_and_commitment_flags_without_impact_do_not_publish(records):
    _,pid,sid=records['add'](1)
    calibrate.record(sid,2026,1,-30)
    records['tasks'][pid]=[{'id':'c','property_id':pid,'status':'completed','evidence':'verified'}]
    records['impacts'][pid]=[]
    for kind in ['streak','follow_through']:
        b=boards.board_result(kind)
        assert b['entries']==[] and b['empty_reason']

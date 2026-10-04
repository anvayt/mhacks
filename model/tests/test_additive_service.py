"""Additive serving paths use copied warm state; no service process is contacted."""
import pytest
from model.heating_cooling.service import estimate_hc

MORTON={'lat':42.26241,'lon':-83.72838,'unit_sqft':1500,'block_group':'261614004003',
        'building_type':'Single-Family Detached'}

@pytest.mark.parametrize('fuel',['gas','electric'])
def test_no_ac_zeros_cooling_without_changing_heat(fuel):
    a=estimate_hc(**MORTON,heating_fuel=fuel)
    b=estimate_hc(**MORTON,heating_fuel=fuel,answers={'cooling_code':0})
    assert a['annual']['heating_usd']==b['annual']['heating_usd']
    assert b['annual']['cooling_usd']==0
    for x,y in zip(a['months'],b['months']):
        assert x['heating']==y['heating']
        assert y['cooling']['usd_exact']==y['cooling']['electric_kwh']==0


def test_year_override_and_zero_effects():
    a=estimate_hc(**MORTON)
    b=estimate_hc(**MORTON,changes={'air_sealing':False,'setpoint_delta_f':0})
    assert a['annual']==b['annual'] and a['months']==b['months']
    c=estimate_hc(**MORTON,year_built=2005)
    assert c['building']['year_built']==2005 and c['building']['year_built_source']=='caller override'
    assert sum(m['heating']['usd_exact']+m['cooling']['usd_exact'] for m in a['months'])==pytest.approx(a['annual']['total_usd'],abs=.5)


def test_heat_pump_reports_changed_fuel_and_sources():
    b=estimate_hc(**MORTON,heating_fuel='gas',changes={'heat_pump':True})
    assert b['building']['heating_fuel']=='electric' and b['building']['baseline_heating_fuel']=='gas'
    assert b['annual']['gas_ccf']==0 and b['annual']['electric_kwh']>0
    assert b['effects']['applied'][0]['sources']

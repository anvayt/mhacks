import numpy as np
import pandas as pd
import pytest
from model.heating_cooling import uncertainty, service


def test_residual_uses_expected_denominator_and_seasons():
    d=pd.DataFrame({'fuel':['gas']*3,'actual':[50,100,150],'metered':[100,100,100],
                    'month':[1,2,12],'building_id':['a','b','c']})
    r=uncertainty.temporal_summary(d)
    assert r['by_season']['winter']['p90_abs_residual_fraction']==.5
    assert r['by_season']['winter']['n_buildings']==3
    assert r['by_estimate_path']['resstock']['transfer_to_unmetered'] is True


def test_signed_quantiles_preserve_sign_and_filter_invalid():
    d=pd.DataFrame({'actual':[100,100,100,0],'p':[50,100,150,0],'building_id':['a','b','c','d']})
    s=uncertainty.signed_summary(d,'p')
    assert s['p10']==pytest.approx(-.4) and s['p90']==pytest.approx(.4)
    assert s['p50']==0 and s['n_months_or_seasons']==3


def test_no_future_year_leakage_in_saved_residuals():
    # The analysis re-fit every held-out year from the other years and matched every saved prediction.
    p=uncertainty.products()
    assert p['out_of_year_audit']['rows_checked']>0
    assert p['out_of_year_audit']['max_absolute_ccf_difference']==0


def test_bill_noise_opt_in_keeps_legacy_numbers(monkeypatch):
    est={'location':{'lat':1,'lon':2},'method':'resstock',
         'seasons':[{'season':'winter','weather':{'hdd60':100},'heating':{'gas_ccf':100}}]}
    monkeypatch.setattr(service,'estimate_hc',lambda **kw: est)
    monkeypatch.setattr(service,'_res',lambda:{'gas_base_ccf_per_1000ft2_day':0,
        'validation':{'real':{'seasonal_gas_vs_real_meters':{'p90_abs_pct_error_winter':{'resstock':1.183}}}}})
    monkeypatch.setattr(service.climate,'monthly_weather_years',lambda *a:pd.DataFrame([
        {'month':2,'hdd60':100,'days':28,'hdd65':120,'tmean_c':0}]))
    monkeypatch.setattr(uncertainty,'bill_noise',lambda *a:{'p90_abs_residual_fraction':.25,'basis':'fixture','limitation':'fixture'})
    old=service.bill_check(2026,2,50,1000,lat=1,lon=2)
    new=service.bill_check(2026,2,50,1000,lat=1,lon=2,noise_basis='within_building')
    assert old['noise_floor']==1.183 and old['meaningful'] is False
    assert new['noise_floor']==.25 and new['meaningful'] is True
    assert new['estimate_error_floor']==1.183 and new['expected_gas_ccf']==old['expected_gas_ccf']==100
    with pytest.raises(ValueError):service.bill_check(2026,2,50,1000,noise_basis='bad')

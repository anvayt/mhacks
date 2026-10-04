"""Counterfactual contract tests: no servers, no network and no baseline retraining."""
import copy
import json

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from model.heating_cooling import effects


@pytest.fixture
def frames():
    monthly = pd.DataFrame({'month': [1, 2, 7], 'year': [2023]*3,
                            'heat_ccf': [100., 80., 0.], 'heat_kwh': [0., 0., 0.], 'cool_kwh': [0., 0., 120.]})
    weather = pd.DataFrame({'hdd60': [900., 650., 0.], 'hdd55': [750., 510., 0.]})
    context = {'method': 'resstock', 'fuel': 'gas', 'btype': 'Single-Family Detached',
               'feat': {'year_built': 1959, 'unit_sqft': 1500}, 'answers': {'window_panes': 1}}
    return monthly, weather, context


@pytest.fixture
def surrogate(monkeypatch):
    artifact = {'method': 'test simulation surrogate', 'test': {'n': 100, 'r2_log': .7},
                'attic_supported_btypes': ['Single-Family Detached', 'Single-Family Attached'],
                'attic_minimum_cohort_n': 30,
                'coefficients': {'log_ach50': .4, 'minus_log1p_ceiling_r': .1, 'minus_log1p_wall_r': .15},
                'bounds': {'ach50': {'min': 1, 'max': 50}, 'wall_r': {'min': 0, 'max': 19},
                           'ceiling_r': {'min': 0, 'max': 49}},
                'cohorts': {'Single-Family Detached': {'all': {'ach50': 20., 'wall_r': 0., 'ceiling_r': 13.,
                    'heating_afue': 80., 'insulated_wall_r': 11., 'n': 100, 'attic_n': 80,
                    'attic_ceiling_r': 19., 'attic_type_counts': {'Vented Attic': 80, 'None': 20}}}}}
    monkeypatch.setattr(effects, '_artifact', lambda: artifact)
    return artifact


@pytest.mark.parametrize('changes', [None, {}, {'air_sealing': False, 'attic_r': 0, 'wall_insulated': 0,
                                               'heat_pump': None, 'setpoint_delta_f': 0}])
def test_defaults_exact_noop_without_loading_artifacts(frames, monkeypatch, changes):
    monkeypatch.setattr(effects, '_artifact', lambda: pytest.fail('Default path must not load effects'))
    m, w, c = frames
    out, meta = effects.apply_effects(m, w, c, changes)
    assert out is m
    assert meta['applied'] == [] and meta['not_modeled'] == []


@pytest.mark.parametrize('name,value', [('air_sealing', True), ('attic_r', 50), ('wall_insulated', 1), ('setpoint_delta_f', -2)])
def test_load_effect_reduces_heating_only_and_preserves_input(frames, surrogate, name, value):
    m, w, c = frames
    original = m.copy(deep=True)
    out, meta = effects.apply_effects(m, w, c, {name: value})
    assert 0 < out.heat_ccf.sum() < m.heat_ccf.sum()
    assert np.array_equal(out.cool_kwh, m.cool_kwh)
    assert np.array_equal(out.heat_kwh, m.heat_kwh)
    assert_frame_equal(m, original)
    assert meta['applied'][0]['sources'] and meta['applied'][0]['method']
    json.dumps(meta, allow_nan=False)


def test_joint_savings_subadditive_and_removing_params_reverses(frames, surrogate):
    m, w, c = frames
    changes = {'air_sealing': True, 'attic_r': 50, 'wall_insulated': 1, 'setpoint_delta_f': -2}
    total = m.heat_ccf.sum()
    standalone = sum(total - effects.apply_effects(m, w, c, {k: v})[0].heat_ccf.sum() for k, v in changes.items())
    joint, _ = effects.apply_effects(m, w, c, changes)
    assert 0 < total - joint.heat_ccf.sum() < standalone
    smaller, _ = effects.apply_effects(m, w, c, {'air_sealing': True})
    assert smaller.heat_ccf.sum() > joint.heat_ccf.sum()
    restored, _ = effects.apply_effects(m, w, c, {})
    assert_frame_equal(m, restored)
    reverse_order, _ = effects.apply_effects(m, w, c, dict(reversed(list(changes.items()))))
    assert np.allclose(joint.heat_ccf, reverse_order.heat_ccf)


def test_gas_heatpump_uses_delivered_heat_and_cop_once(frames, surrogate):
    m, w, c = frames
    out, meta = effects.apply_effects(m, w, c, {'air_sealing': True, 'heat_pump': True})
    sealed, _ = effects.apply_effects(m, w, c, {'air_sealing': True})
    assert out.heat_ccf.sum() == 0
    expected = sealed.heat_ccf * effects.KWH_PER_CCF * .8 / 2.75
    assert np.allclose(out.heat_kwh, expected)
    assert out.heat_kwh.sum() < (sealed.heat_ccf * effects.KWH_PER_CCF * .8).sum()  # not resistance
    assert np.array_equal(out.cool_kwh, m.cool_kwh)
    assert meta['heating_fuel_after'] == 'electric'
    assert 'increase' in meta['assumptions'][-1]


def test_floor_clamped_without_reward_below_64(frames, surrogate):
    m, w, c = frames
    floor, fm = effects.apply_effects(m, w, c, {'setpoint_delta_f': -4})
    lower, lm = effects.apply_effects(m, w, c, {'setpoint_delta_f': -20})
    assert_frame_equal(floor, lower)
    assert lm['applied'][0]['assumptions']['setback_indoor_f'] == 64
    assert np.isfinite(lower.heat_ccf).all()


@pytest.mark.parametrize('path,fuel', [('metered', 'gas'), ('resstock', 'electric')])
def test_unsupported_metered_or_electric_is_honest_noop(frames, monkeypatch, path, fuel):
    m, w, c = frames
    c.update(method=path, fuel=fuel)
    monkeypatch.setattr(effects, '_artifact', lambda: pytest.fail('Unsupported path must not load artifacts'))
    out, meta = effects.apply_effects(m, w, c, {'air_sealing': True, 'heat_pump': True})
    assert out is m and meta['applied'] == [] and len(meta['not_modeled']) == 2


def test_attic_training_range_and_existing_insulation(frames, surrogate):
    m, w, c = frames
    out, meta = effects.apply_effects(m, w, c, {'attic_r': 50})
    assert meta['applied'][0]['assumptions']['modeled_r'] == 49
    unchanged, _ = effects.apply_effects(m, w, c, {'attic_r': 7})
    assert_frame_equal(unchanged, m)
    surrogate['cohorts']['Single-Family Detached']['all']['wall_r'] = 19
    unchanged, _ = effects.apply_effects(m, w, c, {'wall_insulated': 1})
    assert_frame_equal(unchanged, m)


@pytest.mark.parametrize('btype', ['Multi-Family with 2 - 4 Units', 'Multi-Family with 5+ Units', 'Mobile Home'])
def test_unsupported_types_remain_unmodeled_even_top_floor(frames, surrogate, btype):
    m, w, c = frames
    c['btype'] = btype
    surrogate['cohorts'][c['btype']] = copy.deepcopy(surrogate['cohorts']['Single-Family Detached'])
    unchanged, meta = effects.apply_effects(m, w, c, {'attic_r': 50})
    assert unchanged is m and meta['not_modeled'][0]['param'] == 'attic_r'
    c['answers']['floor_level'] = 2
    out, meta = effects.apply_effects(m, w, c, {'attic_r': 50})
    assert out is m and meta['not_modeled'] and not meta['applied']


@pytest.mark.parametrize('changes', [{'nonsense': 1}, {'attic_r': 1000}, {'air_sealing': 'false'},
                                    {'setpoint_delta_f': float('nan')}, {'setpoint_delta_f': 2}])
def test_bad_or_unknown_effects_are_not_silently_applied(frames, surrogate, changes):
    m, w, c = frames
    out, meta = effects.apply_effects(m, w, c, changes)
    assert out is m and meta['applied'] == [] and meta['not_modeled']


def test_real_small_surrogate_has_provenance_and_monotone_coefficients():
    artifact = effects._artifact()
    assert artifact['n_gas_homes'] == artifact['train_n'] + artifact['test']['n']
    assert len(artifact['source_sha256']) == 64
    assert artifact['test']['r2_log'] > 0
    for k, v in artifact['coefficients'].items():
        if k in ('log_ach50', 'minus_log1p_wall_r', 'minus_log1p_ceiling_r', 'minus_log_afue'):
            assert v >= 0


def test_attic_baseline_excludes_absent_attics(frames, surrogate):
    m, w, c = frames
    cohort = surrogate['cohorts'][c['btype']]['all']
    cohort['ceiling_r'] = 0  # all-stock median can be zero because many homes have no attic
    out, meta = effects.apply_effects(m, w, c, {'attic_r': 50})
    assert meta['applied'][0]['assumptions']['baseline_r'] == 19
    assert meta['applied'][0]['assumptions']['attic_cohort_n'] == 80
    cohort['attic_n'] = 0
    cohort['attic_ceiling_r'] = None
    out, meta = effects.apply_effects(m, w, c, {'attic_r': 50})
    assert out is m and meta['not_modeled']


def test_actual_attic_support_counts_and_exclusions():
    artifact = effects._artifact()
    assert set(artifact['attic_supported_btypes']) == {'Single-Family Detached', 'Single-Family Attached'}
    assert artifact['attic_raw_gas_counts']['Multi-Family with 2 - 4 Units'] == {'None': 778}
    assert artifact['attic_raw_gas_counts']['Multi-Family with 5+ Units'] == {'None': 1619}
    assert artifact['attic_raw_gas_counts']['Mobile Home'] == {'None': 675}
    for btype in artifact['attic_supported_btypes']:
        assert artifact['cohorts'][btype]['all']['attic_n'] >= 30

"""Opt-in heating counterfactuals. No changes means the original frame is untouched.

Envelope ratios come from a separate monotone ResStock surrogate, not a retrofit
trial. Multiplicative composition applies to the remaining heat load exactly once.
Actual envelope/HVAC details are unknown: report the assumptions, never verification.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache

import numpy as np
import pandas as pd

from model.paths import RESULTS

RESSTOCK = 'https://data.openei.org/s3_viewer?bucket=oedi-data-lake&prefix=nrel-pds-building-stock%2Fend-use-load-profiles-for-us-building-stock%2F2024%2Fresstock_tmy3_release_2%2F'
AIR_SEALING = 'https://www.energystar.gov/saveathome/seal_insulate/methodology'
NREL_SEALING = 'https://www.nrel.gov/docs/fy24osti/85625.pdf'
NEEP = 'https://neep.org/blog/checking-neep-ccashp-product-list'
DOE_COP = 'https://www.energy.gov/sites/default/files/2021-09/2-Tom-ASHP.pdf'
MI_COP = 'https://www.michigan.gov/mpsc/-/media/Project/Websites/mpsc/workgroups/EWR_Collaborative/2023/2021CI-and-Res-CCHP-Initiatives-Comprehensive-Evaluation-20220826.pdf'
WHO = 'https://www.who.int/publications/i/item/9789241550376'
DOE_THERMOSTAT = 'https://content.govdelivery.com/accounts/USEERE/bulletins/3883189'
PATHS = ['resstock', 'meter_model+resstock']
HEAT_PUMP_COP = 2.75  # Consumers Energy 2021 evaluation, Appendix B Table B-4, engineering assumption.
KWH_PER_CCF = 103.7 / 3.412  # Same EIA gas heat-content conversion as the baseline service.

SUPPORTED_PARAMS = {
    'air_sealing': {'supported': True, 'paths': PATHS, 'fuels': ['gas'], 'type': 'boolean',
                    'method': 'resstock_envelope_surrogate', 'sources': [RESSTOCK, AIR_SEALING, NREL_SEALING],
                    'ach50_reduction_fraction': .25},
    'attic_r': {'supported': True, 'paths': PATHS, 'fuels': ['gas'], 'type': 'number',
                'method': 'resstock_envelope_surrogate', 'sources': [RESSTOCK],
                'max_modeled_r': 49, 'building_types': ['Single-Family Detached', 'Single-Family Attached'],
                'note': 'Single-family stock with vented/unvented attic support only; actual attic presence is assumed, not observed. R-50 uses R-49 support.'},
    'wall_insulated': {'supported': True, 'paths': PATHS, 'fuels': ['gas'], 'type': 'boolean',
                       'method': 'resstock_envelope_surrogate', 'sources': [RESSTOCK]},
    'heat_pump': {'supported': True, 'paths': PATHS, 'fuels': ['gas'], 'type': 'boolean',
                  'method': 'delivered_heat_over_cop', 'sources': [MI_COP, NEEP, DOE_COP, RESSTOCK],
                  'seasonal_cop': HEAT_PUMP_COP,
                  'note': 'Michigan engineering COP assumption, not a measured COP at this home; electricity may cost more.'},
    'setpoint_delta_f': {'supported': True, 'paths': PATHS, 'fuels': ['gas'], 'type': 'number',
                         'method': 'degree_day_setback_scenario', 'sources': [WHO, DOE_THERMOSTAT],
                         'baseline_indoor_f': 68, 'minimum_indoor_f': 64, 'setback_hours_per_day': 8},
}


@lru_cache(maxsize=1)
def _artifact():
    return json.loads((RESULTS / 'effects_envelope.json').read_text())


def _cohort(artifact, context):
    groups = artifact['cohorts'].get(context.get('btype'))
    if not groups:
        return None
    year = context.get('feat', {}).get('year_built')
    key = str(int(round(float(year) / 10) * 10)) if year is not None and math.isfinite(float(year)) else 'all'
    return dict(groups.get(key, groups['all']), vintage_band=key if key in groups else 'all')


def _active(changes):
    return {k: v for k, v in (changes or {}).items() if v is not None and v is not False and v != 0}


def apply_effects(monthly: pd.DataFrame, weather: pd.DataFrame, context: dict,
                  changes: dict | None) -> tuple[pd.DataFrame, dict]:
    """Apply opt-in scenarios to building totals before service scales to the unit.

    Caller reruns the unchanged baseline on each request. Never feed an already
    projected frame back here: removing a parameter then restores that effect.
    """
    selected = _active(changes)
    metadata = {'label': 'projected_if_completed', 'applied': [], 'not_modeled': []}
    if not selected:
        return monthly, metadata
    for name in list(selected):
        if name not in SUPPORTED_PARAMS:
            metadata['not_modeled'].append({'param': name, 'reason': 'unsupported effect parameter'})
            del selected[name]
    if context.get('method') not in PATHS or context.get('fuel') != 'gas':
        reason = ('Metered energy does not identify this property\'s envelope or HVAC; no validated retrofit response.'
                  if context.get('method') == 'metered' else 'Effects are supported only for unmetered gas heating.')
        metadata['not_modeled'].extend({'param': k, 'reason': reason} for k in selected)
        return monthly, metadata
    if not selected:
        return monthly, metadata
    try:
        artifact = _artifact()
        cohort = _cohort(artifact, context)
    except (FileNotFoundError, KeyError, ValueError):
        cohort = None
    if cohort is None:
        metadata['not_modeled'].extend({'param': k, 'reason': 'No supported envelope stock cohort is available.'} for k in selected)
        return monthly, metadata
    metadata['basis'] = artifact['method']
    metadata['validation'] = {'simulation_holdout': artifact['test'], 'real_retrofit_validation': None}
    metadata['baseline_envelope'] = {k: cohort[k] for k in ('ach50', 'wall_r', 'ceiling_r', 'heating_afue', 'n', 'vintage_band')}
    metadata['assumptions'] = ['Envelope values are Michigan stock medians, not measurements of this home.',
                               'Cooling and non-heating gas savings are not modeled.',
                               'Effects are scenarios, not verified impact or new baseline grades.']
    factor = np.ones(len(monthly))
    coef = artifact['coefficients']
    for name, value in selected.items():
        info = SUPPORTED_PARAMS[name]
        item = {'param': name, 'method': info['method'], 'sources': info['sources'], 'assumptions': {}}
        if name in ('air_sealing', 'wall_insulated', 'heat_pump') and value not in (True, 1):
            metadata['not_modeled'].append({'param': name, 'reason': 'Use a boolean true/false value.'})
            continue
        if name == 'air_sealing':
            before = cohort['ach50']
            after = max(artifact['bounds']['ach50']['min'], before * .75)
            single = math.exp(coef['log_ach50'] * math.log(after / before))
            item['assumptions'] = {'ach50_before': before, 'ach50_after': after,
                                   'reduction_fraction': .25, 'scope': 'whole-home professional air sealing, not weatherstrip-only'}
        elif name in ('attic_r', 'wall_insulated'):
            field = 'ceiling_r' if name == 'attic_r' else 'wall_r'
            if name == 'attic_r':
                try:
                    target = float(value)
                except (TypeError, ValueError):
                    target = float('nan')
                if not math.isfinite(target) or target < 0 or target > 50:
                    metadata['not_modeled'].append({'param': name, 'reason': 'Supported attic target is 0–50; R-50 uses R-49 training support.'})
                    continue
                if (context.get('btype') not in artifact.get('attic_supported_btypes', [])
                        or cohort.get('attic_n', 0) < artifact.get('attic_minimum_cohort_n', 30)
                        or cohort.get('attic_ceiling_r') is None):
                    metadata['not_modeled'].append({'param': name, 'reason': 'No supported single-family vented/unvented attic cohort; top-floor answers cannot establish attic support for multifamily/mobile homes.'})
                    continue
            else:
                target = cohort['insulated_wall_r']
            before = cohort['attic_ceiling_r'] if name == 'attic_r' else cohort[field]
            after = max(before, min(target, artifact['bounds'][field]['max']))
            single = math.exp(coef['minus_log1p_' + field] * (math.log1p(before) - math.log1p(after)))
            item['assumptions'] = {'baseline_r': before, 'requested_r': target, 'modeled_r': after,
                                   'scope': 'assumes an accessible vented/unvented attic at this single-family home; actual presence is unobserved' if name == 'attic_r' else 'insulated-stock median wall R; existing insulation is not removed'}
            if name == 'attic_r':
                item['assumptions'].update(attic_cohort_n=cohort['attic_n'],
                                           attic_type_counts=cohort['attic_type_counts'],
                                           baseline_r_source='median among vented/unvented attics only; excludes None and finished/cathedral roofs')
        elif name == 'setpoint_delta_f':
            try:
                delta = float(value)
            except (TypeError, ValueError):
                delta = float('nan')
            if not math.isfinite(delta) or delta > 0:
                metadata['not_modeled'].append({'param': name, 'reason': 'Only finite heating setbacks (negative °F) are supported.'})
                continue
            delta = max(delta, -4.)  # 68°F baseline → minimum64°F, per existing project WHO safety policy.
            if not {'hdd55', 'hdd60'} <= set(weather.columns):
                metadata['not_modeled'].append({'param': name, 'reason': 'HDD55/HDD60 are required for the setback scenario.'})
                continue
            hdd60, hdd55 = weather.hdd60.to_numpy(float), weather.hdd55.to_numpy(float)
            changed = hdd60 + (-delta / 5) * (hdd55 - hdd60)
            ratio = np.divide(changed, hdd60, out=np.ones(len(weather)), where=hdd60 > 0)
            single = 1 - (1 - np.clip(ratio, 0, 1)) * (8 / 24)
            item['assumptions'] = {'baseline_indoor_f': 68, 'setback_indoor_f': 68 + delta,
                                   'effective_delta_f': delta, 'minimum_indoor_f': 64, 'setback_hours_per_day': 8,
                                   'method_note': 'Linear interpolation between monthly HDD55/HDD60; eight-hour load-share approximation, no rebound or backup-heat model.'}
        else:  # fuel conversion happens after the joint heat-load reduction, once.
            item['assumptions'] = {'seasonal_cop': HEAT_PUMP_COP, 'afue': cohort['heating_afue'] / 100,
                                   'afue_source': 'same-type/vintage ResStock gas-home median',
                                   'cop_source': 'Michigan Consumers Energy 2021 evaluation, Appendix B Table B-4 (assumption, not field measurement)',
                                   'ccf_to_therms': 1.037, 'kwh_per_ccf': KWH_PER_CCF,
                                   'scope': 'all space heating displaced; no modeled backup, capacity limits, ducts or cooling improvement'}
            metadata['applied'].append(item)
            continue
        factor *= single
        item['heating_factor'] = float(np.average(np.broadcast_to(single, len(monthly)), weights=monthly.heat_ccf)) if monthly.heat_ccf.sum() > 0 else 1.
        metadata['applied'].append(item)
    if not metadata['applied']:
        return monthly, metadata
    out = monthly.copy(deep=True)
    out['heat_ccf'] = out.heat_ccf * factor
    if any(i['param'] == 'heat_pump' for i in metadata['applied']):
        out['heat_kwh'] = out.heat_kwh + out.heat_ccf * KWH_PER_CCF * (cohort['heating_afue'] / 100) / HEAT_PUMP_COP
        out['heat_ccf'] = 0.
        metadata['heating_fuel_after'] = 'electric'
        metadata['assumptions'].append('A gas-to-heat-pump scenario may increase the bill at Michigan EIA rates; do not label a negative dollar delta as savings.')
    metadata['composition'] = 'Joint multiplicative remaining-load factors, then one delivered-heat fuel conversion; no sum of separate dollar deltas.'
    metadata['sum_of_parts_condition'] = 'Subadditive for beneficial independent load reductions; a fuel switch that raises energy prices can violate dollar subadditivity, so no universal dollar cap is claimed.'
    return out, metadata

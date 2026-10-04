"""Additive uncertainty products from saved out-of-year / out-of-building meter predictions.

No baseline model is retrained. Fractional errors, not percentages. Temporal residuals use
actual/predicted - 1 (the direction of bill_check); estimate errors use predicted/actual - 1.
"""
from __future__ import annotations

import json
from functools import lru_cache
import numpy as np
import pandas as pd
from model import climate
from model.paths import PROCESSED, RESULTS

PATHS = ('metered', 'meter_model', 'resstock', 'blend', 'null')
METHOD_PATH = {'metered': 'metered', 'meter_model+resstock': 'blend', 'resstock': 'resstock'}
BASIS = ('p90 absolute (actual gas / same-building prediction - 1), each calendar year held out '
         'of that building\'s weather change-point fit; Ann Arbor utility meters 2021–2023. '
         'This measures temporal variability, not cross-building prediction bias.')


def signed_summary(frame: pd.DataFrame, prediction: str) -> dict:
    error = frame[prediction] / frame.actual - 1
    error = error[(frame.actual > 0) & np.isfinite(error)]
    return {'n_months_or_seasons': len(error), 'n_buildings': int(frame.loc[error.index, 'building_id'].nunique()),
            'p10': float(error.quantile(.1)) if len(error) else None,
            'p50': float(error.quantile(.5)) if len(error) else None,
            'p90': float(error.quantile(.9)) if len(error) else None}


def temporal_summary(months: pd.DataFrame) -> dict:
    d = months[(months.fuel == 'gas') & (months.actual > 0) & (months.metered > 0)].copy()
    d['season'] = d.month.map(climate.MONTH_TO_SEASON)
    d['residual_fraction'] = d.actual / d.metered - 1
    d = d[np.isfinite(d.residual_fraction)]
    def stats(g):
        return {'p90_abs_residual_fraction': float(g.residual_fraction.abs().quantile(.9)),
                'n_months': len(g), 'n_buildings': int(g.building_id.nunique())}
    return {'basis': BASIS, 'residual_definition': 'actual / out_of_year_same_building_prediction - 1',
            'all': stats(d), 'by_season': {s: stats(g) for s, g in d.groupby('season')},
            'by_calendar_month': {str(int(m)): stats(g) for m, g in d.groupby('month')},
            'by_estimate_path': {p: {'source_path': 'metered', 'temporal_component_only': True,
                'transfer_to_unmetered': p != 'metered',
                'limitation': 'No own-home baseline for unmetered homes; cross-building level bias remains.' if p != 'metered' else
                              'Pooled across metered properties; not a personalized prediction interval.'}
                for p in METHOD_PATH.values()}}


def audit_out_of_year(months: pd.DataFrame) -> dict:
    """Re-fit each building excluding the tested year and compare to the copied held-out rows."""
    from model.heating_cooling import changepoint
    w = pd.read_parquet(PROCESSED / 'meters_weather.parquet')
    stored = months[(months.fuel == 'gas') & months.metered.notna()]
    checked, max_diff = 0, 0.0
    for bid, g in stored.groupby('building_id'):
        whole = w[(w.building_id == bid) & w.gas_ok & ~w.gas_ccf_outlier]
        for year, test in g.groupby('year'):
            fit = changepoint.fit(whole[whole.year != year], 'gas_ccf', heating=True, cooling=False)
            assert fit is not None and fit.r2 >= .7, (bid, year)
            actual = whole[whole.year == year].copy()
            actual['recomputed'] = fit.predict(actual).total.to_numpy()
            merged = test.merge(actual[['month', 'recomputed']], on='month', validate='one_to_one')
            diff = np.abs(merged.metered - merged.recomputed)
            max_diff = max(max_diff, float(diff.max()))
            checked += len(merged)
    assert checked == len(stored) and max_diff < 1e-7, (checked, len(stored), max_diff)
    return {'rows_checked': checked, 'max_absolute_ccf_difference': max_diff,
            'method': 'Refit gas change-point on other calendar years using cached meters_weather; no network.'}


@lru_cache(maxsize=1)
def products() -> dict:
    p = RESULTS / 'uncertainty_additive.json'
    return json.loads(p.read_text()) if p.exists() else {}


def bill_noise(method: str, season: str) -> dict | None:
    temporal = products().get('within_building_gas', {})
    stats = temporal.get('by_season', {}).get(season)
    if not stats:
        return None
    path = METHOD_PATH[method]
    return {**stats, 'basis': temporal['basis'], **temporal['by_estimate_path'][path]}


def signed_quantiles(method: str) -> dict | None:
    path = METHOD_PATH[method]
    d = products().get('signed_error_quantiles', {})
    if not d:
        return None
    return {'definition': d['definition'], 'unit': 'fraction', 'path': path,
            'seasonal': {fuel: values[path] for fuel, values in d['seasonal'].items()},
            'monthly': {fuel: values[path] for fuel, values in d['monthly'].items()},
            'band_note': 'For error = prediction/actual - 1, actual bounds invert and reverse the error quantiles. '
                         'These are empirical total-meter errors, not calibrated H+C-only prediction intervals.'}


def main():
    months = pd.read_parquet(RESULTS / 'heldout_monthly.parquet')
    seasons = pd.read_parquet(RESULTS / 'heldout_seasonal.parquet')
    signed = {'definition': 'prediction / actual - 1; signed, positive means overprediction',
              'unit': 'fraction', 'seasonal': {}, 'monthly': {}}
    for label, data, group in [('seasonal', seasons, 'season'), ('monthly', months, 'month')]:
        for fuel, frame in data.groupby('fuel'):
            signed[label][fuel] = {p: {'all': signed_summary(frame, p),
                'by_season' if group == 'season' else 'by_calendar_month':
                {str(k): signed_summary(g, p) for k, g in frame.groupby(group)}} for p in PATHS}
    out = {'within_building_gas': temporal_summary(months), 'signed_error_quantiles': signed,
           'out_of_year_audit': audit_out_of_year(months),
           'sources': ['City of Ann Arbor public monthly utility benchmarking 2021–2023',
                       'heldout_monthly.parquet and heldout_seasonal.parquet from copied live build',
                       'model/heating_cooling/validate.py: heldout_rows; changepoint.py: fit']}
    (RESULTS / 'uncertainty_additive.json').write_text(json.dumps(out, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'temporal_noise': out['within_building_gas'], 'audit': out['out_of_year_audit']}, indent=2))


if __name__ == '__main__':
    main()

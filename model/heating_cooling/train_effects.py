"""Fit a separate monotone envelope surrogate; never retrain the baseline.

Run: .venv/bin/python -m model.heating_cooling.train_effects
Cross-sectional simulation counterfactual, not a causal retrofit study.
"""
from __future__ import annotations
import hashlib
import json
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear
from sklearn.model_selection import train_test_split
from model.paths import PROCESSED, RESULTS, RAW

ACCESSIBLE_ATTICS = ['Vented Attic', 'Unvented Attic']
SINGLE_FAMILY = ['Single-Family Detached', 'Single-Family Attached']

ENVELOPE = ['log_ach50', 'minus_log1p_wall_r', 'minus_log1p_ceiling_r', 'minus_log_afue']


def design(f):
    x = pd.DataFrame({
        'intercept': 1., 'log_sqft': np.log(f.sqft), 'vintage': (f.year_built - 1970) / 50,
        'stories': f.stories, 'occupants': f.occupants.fillna(f.occupants.median()),
        'renter': f.renter, 'low_e': f.low_e, 'log1p_roof_r': np.log1p(f.roof_r),
        'log_ach50': np.log(f.ach50), 'minus_log1p_wall_r': -np.log1p(f.wall_r),
        'minus_log1p_ceiling_r': -np.log1p(f.ceiling_r), 'minus_log_afue': -np.log(f.heating_afue / 100),
    }, index=f.index)
    for c in ('btype', 'window_panes', 'foundation_code', 'floor_level', 'attic_type'):
        x = pd.concat([x, pd.get_dummies(f[c].astype(str), prefix=c, dtype=float, drop_first=True)], axis=1)
    return x.astype(float)


def fit(x, y):
    # Fixed tiny ridge stabilizes collinear stock features; no tuning on the holdout.
    lo = np.array([0. if c in ENVELOPE else -np.inf for c in x.columns])
    a = np.vstack([x.to_numpy(), np.eye(x.shape[1]) * .01])
    b = np.r_[y, np.zeros(x.shape[1])]
    result = lsq_linear(a, b, bounds=(lo, np.full(len(lo), np.inf)), tol=1e-10)
    if not result.success:
        raise RuntimeError(result.message)
    return result.x


def main():
    source = PROCESSED / 'resstock_frame.parquet'
    raw = pd.read_parquet(source)
    raw_source = RAW / 'resstock' / 'MI_baseline_metadata_and_annual_results.parquet'
    source_rows = pd.read_parquet(raw_source, columns=['in.sqft', 'in.insulation_roof', 'in.geometry_attic_type'])
    if len(source_rows) != len(raw) or not np.array_equal(source_rows['in.sqft'].astype(float).to_numpy(), raw.sqft.to_numpy()):
        raise ValueError('Raw and processed ResStock rows do not align; cannot attach roof/attic controls.')
    raw['roof_r'] = source_rows['in.insulation_roof'].astype(str).str.extract(r'R-(\d+)')[0].astype(float).fillna(0).to_numpy()
    raw['attic_type'] = source_rows['in.geometry_attic_type'].astype(str).to_numpy()
    f = raw[(raw.heating_fuel == 'Natural Gas') & (raw.heat_gas_per_hdd > 0)].dropna(
        subset=['sqft', 'year_built', 'stories', 'ach50', 'wall_r', 'ceiling_r', 'heating_afue']).copy()
    x, y = design(f), np.log(f.heat_gas_per_hdd.to_numpy(dtype=float))
    tr, te = train_test_split(np.arange(len(f)), test_size=.2, random_state=20261004)
    beta = fit(x.iloc[tr], y[tr])
    pred = x.iloc[te].to_numpy() @ beta
    test = {'n': len(te), 'r2_log': float(1 - np.mean((pred-y[te])**2)/np.var(y[te])),
            'median_abs_pct_error': float(np.median(np.abs(np.exp(pred-y[te])-1))*100)}
    full = fit(x, y)
    coefficients = dict(zip(x.columns, full.tolist()))
    cohorts = {}
    for btype, group in f.groupby('btype'):
        subsets = [('all', group)]
        for vintage in range(1920, 2030, 10):
            subset = group[(group.year_built-vintage).abs() <= 20]
            if len(subset) >= 30:  # analyst minimum for a local stock median
                subsets.append((str(vintage), subset))
        cohorts[btype] = {}
        for vintage, sub in subsets:
            values = sub[['ach50', 'wall_r', 'ceiling_r', 'heating_afue']].median().to_dict()
            insulated = sub.loc[sub.wall_r > 0, 'wall_r']
            if insulated.empty:
                insulated = group.loc[group.wall_r > 0, 'wall_r']
            attics = sub[sub.attic_type.isin(ACCESSIBLE_ATTICS)]
            values.update(attic_n=int(len(attics)),
                          attic_type_counts={str(k): int(v) for k, v in sub.attic_type.value_counts().items()},
                          attic_ceiling_r=float(attics.ceiling_r.median()) if len(attics) else None,
                          n=int(len(sub)), insulated_wall_r=float(insulated.median()),
                          sqft_min=float(sub.sqft.min()), sqft_max=float(sub.sqft.max()))
            cohorts[btype][vintage] = values
    out = {
        'method': 'monotone log-linear surrogate of ResStock MI baseline; simulation only, not measured retrofit savings',
        'source': 'NREL ResStock 2024.2 Michigan baseline, existing processed resstock_frame.parquet',
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'raw_source_sha256': hashlib.sha256(raw_source.read_bytes()).hexdigest(),
        'n_gas_homes': len(f), 'train_n': len(tr), 'test': test, 'seed': 20261004,
        'features': x.columns.tolist(), 'coefficients': coefficients, 'cohorts': cohorts,
        'attic_supported_btypes': [b for b in SINGLE_FAMILY if cohorts[b]['all']['attic_n'] >= 30],
        'attic_types_modeled': ACCESSIBLE_ATTICS,
        'attic_minimum_cohort_n': 30,
        'attic_raw_gas_counts': {str(b): {str(k): int(v) for k, v in g.attic_type.value_counts().items()}
                                 for b, g in raw[raw.heating_fuel == 'Natural Gas'].groupby('btype')},
        'attic_training_gas_counts': {str(b): {str(k): int(v) for k, v in g.attic_type.value_counts().items()}
                                      for b, g in f.groupby('btype')},
        'bounds': {c: {'min': float(f[c].min()), 'max': float(f[c].max())}
                   for c in ('ach50','wall_r','ceiling_r','heating_afue')},
        'caveats': ['Cross-sectional baseline simulations are not paired retrofit simulations.',
                    'Holdout accuracy validates simulated heating intensity, not causal intervention effects.',
                    'Envelope values are stock medians, not a blower-door test or insulation survey.',
                    'Only gas/non-metered scenarios are supported; cooling savings are not claimed.',
                    'R-50 is represented by R-49, the highest ceiling insulation in the training stock.',
                    'Attic scenarios require single-family type and at least 30 cohort homes with vented/unvented attics.',
                    'A top-floor answer cannot supply missing attic support for multifamily/mobile homes.',
                    'Attic baseline R excludes attic_type=None and finished/cathedral roof configurations.'],
    }
    (RESULTS / 'effects_envelope.json').write_text(json.dumps(out, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'n': len(f), 'test': test, 'envelope_coefficients': {c: coefficients[c] for c in ENVELOPE}}, indent=2))


if __name__ == '__main__':
    main()

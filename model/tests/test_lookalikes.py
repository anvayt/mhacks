"""Synthetic matching/pricing fixtures: no weather downloads or server needed."""
import json

import numpy as np
import pandas as pd
import pytest

from model.heating_cooling import lookalikes as la, service as hc

TYPE = "Multi-Family with 2 - 4 Units"


@pytest.fixture
def pool(monkeypatch):
    d = pd.DataFrame({"btype": [TYPE] * 8, "renter": [1] * 8, "year_built": [1965] * 8,
                      "sqft": [850] * 8, "heating_fuel": ["Natural Gas", "Electricity"] * 4,
                      "window_panes": [1, 1, 2, 2, 2, 2, 2, 2], "floor_level": [0, 0, 1, 1, 2, 2, 2, 2],
                      "cooling_code": [2, 2, 2, 2, 0, 0, 2, 2], "heat_gas_per_hdd": np.arange(1, 9) / 100,
                      "heat_elec_per_hdd": np.arange(1, 9) / 10, "cool_per_cdd": np.arange(1, 9) / 10})
    d.loc[6, "renter"] = 0
    d.loc[7, "year_built"] = 2005
    monkeypatch.setattr(la, "_frame", lambda: d)
    monkeypatch.setattr(la, "_weather_prices", lambda lat, lon: (100, 10, 20))
    monkeypatch.setattr(hc, "_res", lambda: {"resstock": {"calibration": {"heat_gas": 2, "heat_elec": 3, "cool": 4}}})
    return d


def call(**kwargs):
    return la.lookalikes(42.27, -83.74, 850, TYPE, year_built=1965, **kwargs)


def test_cumulative_answers_narrow_real_pool_and_do_not_mutate(pool):
    original = pool.copy(deep=True)
    clouds = [call(), call(heating_fuel="gas"), call(heating_fuel="gas", answers={"window_panes": 2}),
              call(heating_fuel="gas", answers={"window_panes": 2, "floor_level": 2})]
    assert [c["count"] for c in clouds] == [6, 3, 2, 1]
    assert all(c["pool_size"] == 8 for c in clouds)
    assert "simulation spread" in clouds[0]["rule"] and "window_panes=2" in clouds[-1]["rule"]
    pd.testing.assert_frame_equal(pool, original)


def test_price_equation_matches_p3_fixture_and_scaling(pool):
    values = la.price_cloud(pool.iloc[:2], 42.27, -83.74, 850, TYPE)
    # Gas: .01*2*100 + .1*4*20; electric: .2*3*10 + .2*4*20. Both × .85.
    assert values.tolist() == pytest.approx([8.5, 18.7])
    assert la.price_cloud(pool.iloc[:2], 42.27, -83.74, 1700, TYPE) == pytest.approx(values * 2)
    house = la.price_cloud(pool.iloc[:2], 42.27, -83.74, 850, "Single-Family Detached")
    assert house.tolist() == pytest.approx([2.55, 8.5])


def test_empty_is_json_safe_never_widened(pool):
    cloud = call(answers={"window_panes": 3})
    assert {k: cloud[k] for k in ("count", "usd_yr", "p10", "p50", "p90")} == {
        "count": 0, "usd_yr": [], "p10": None, "p50": None, "p90": None}
    json.dumps(cloud, allow_nan=False)


def test_summary_uses_full_pool_quantiles_sorted_bounded_sample():
    x = la.summarize_cloud([*range(1001), float("nan"), float("inf"), -1])
    assert x["count"] == 1001 and len(x["usd_yr"]) == 400
    assert x["usd_yr"] == sorted(x["usd_yr"]) and x["usd_yr"][0] == 0 and x["usd_yr"][-1] == 1000
    assert (x["p10"], x["p50"], x["p90"]) == (100, 500, 900)


def test_year_and_size_edges_are_p3_rules(pool):
    pool.loc[:, "year_built"] = [1949, 1950, 1979, 1980, 1965, 1965, 1965, 1965]
    pool.loc[:, "sqft"] = [850, 552, 1275, 850, 551, 1276, 850, 850]
    assert call()["count"] == 3


def test_missing_answers_unchanged_and_unsupported_disclosed(pool):
    base = call()
    skipped = call(answers={"window_panes": None, "unavailable_model_feature": 1})
    assert skipped["usd_yr"] == base["usd_yr"]
    assert "No matching filter available for: unavailable_model_feature" in skipped["rule"]


def test_no_year_uses_existing_model_lookup(pool, monkeypatch):
    monkeypatch.setattr(la, "_year", lambda lat, lon, bg: (1965, "ACS test year"))
    cloud = la.lookalikes(42.27, -83.74, 850, TYPE, block_group="261614005003")
    assert cloud["count"] == 6 and "ACS test year" in cloud["rule"]


@pytest.mark.parametrize("kwargs", [{"unit_sqft": -1}, {"building_type": "Office"}, {"heating_fuel": "oil"},
                                    {"lat": float("nan")}, {"answers": {"window_panes": float("inf")}}])
def test_invalid_inputs_rejected(pool, kwargs):
    with pytest.raises(ValueError):
        la.lookalikes(**{"lat": 42.27, "lon": -83.74, "unit_sqft": 850, "building_type": TYPE,
                         "year_built": 1965, **kwargs})

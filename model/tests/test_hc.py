"""Run: python -m pytest model/tests -q  (needs artifacts: python -m model.scripts.build_all)"""
import numpy as np
import pandas as pd
import pytest

from model import climate
from model.hc import changepoint
from model.hc.service import bill_check, estimate_hc

AA = (42.2808, -83.7430)


def test_changepoint_recovers_known_slope():
    rng = np.random.default_rng(0)
    w = climate.monthly_weather_normal(*AA)
    df = pd.concat([w.assign(year=y) for y in (1, 2)], ignore_index=True)
    df["gas"] = 50 * df.days + 2.0 * df.hdd60 + rng.normal(0, 20, len(df))
    f = changepoint.fit(df, "gas", heating=True, cooling=False)
    assert f.tau_h == 60 and abs(f.beta_h - 2.0) < 0.1 and f.r2 > 0.99


def test_normal_weather_plausible():
    s = climate.seasonal(climate.monthly_weather_normal(*AA)).set_index("season")
    assert 5800 < s.hdd65.sum() < 7200          # Ann Arbor ~6,500 HDD65
    assert s.loc["winter", "tmean_f"] < 32 < s.loc["summer", "tmean_f"]


@pytest.mark.parametrize("mode", ["normal", "forecast", 2023])
def test_estimate_shape(mode):
    e = estimate_hc(lat=AA[0], lon=AA[1], unit_sqft=850, mode=mode)
    assert [s["season"] for s in e["seasons"]] == ["winter", "spring", "summer", "fall"]
    for s in e["seasons"]:
        assert s["heating"]["usd"] >= 0 and s["cooling"]["usd"] >= 0
        assert {"tmean_f", "hdd65", "cdd65"} <= set(s["weather"])
    win = next(s for s in e["seasons"] if s["season"] == "winter")
    summ = next(s for s in e["seasons"] if s["season"] == "summer")
    assert win["heating"]["usd"] > summ["heating"]["usd"] and summ["cooling"]["usd"] >= win["cooling"]["usd"]
    assert e["method"] in {"metered", "meter_model+resstock", "resstock"} and e["sources"]


def test_unit_scaling_linear():
    a = estimate_hc(lat=AA[0], lon=AA[1], unit_sqft=500)["annual"]["total_usd"]
    b = estimate_hc(lat=AA[0], lon=AA[1], unit_sqft=1000)["annual"]["total_usd"]
    assert abs(b / a - 2) < 0.02


def test_bill_check_detects_high_bill():
    ok = bill_check(2023, 1, 1.0, 850, lat=AA[0], lon=AA[1])
    exp = ok["expected_gas_ccf"]
    hi = bill_check(2023, 1, exp * 1.6, 850, lat=AA[0], lon=AA[1])
    assert hi["pct_vs_expected_for_weather"] > 0.5 and hi["meaningful"]

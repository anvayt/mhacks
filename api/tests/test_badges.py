"""Pure badge rules: only supplied evidence earns a badge (PLAN.md §5)."""

from copy import deepcopy

import pytest

from app.badges import BADGES, badges


def test_badge_catalog():
    assert set(BADGES) == {"double-pane-club", "top-10-efficient", "leak-hunter", "weather-beater",
                           "grade-jumper", "battle-winner"}
    assert all(set(b) == {"label", "emoji", "rule"} and all(b.values()) for b in BADGES.values())


@pytest.mark.parametrize("est", [
    {}, {"answers": None, "heating_cooling": None, "score": None, "grade": None},
    {"answers": {}, "heating_cooling": {"inputs": None, "model_detail": None}},
    {"answers": {"window_panes": "unknown"}, "score": "unknown", "grade": "unknown"},
    {"answers": [], "heating_cooling": [], "score": True, "grade": []},
    {"answers": {"window_panes": float("inf")}, "score": float("nan")},
])
def test_missing_or_unknown_fields_earn_nothing(est):
    assert badges(est) == []


@pytest.mark.parametrize("value,earned", [(1, False), (1.99, False), (2, True), (3, True),
                                          ("2", True), (None, False), (True, False)])
def test_double_pane_club(value, earned):
    assert ("double-pane-club" in badges({"answers": {"window_panes": value}})) == earned


@pytest.mark.parametrize("hc", [
    {"inputs": {"window_panes": 2}},
    {"model_detail": {"renter_answers_used": {"window_panes": 3}}},
])
def test_window_panes_from_model_inputs(hc):
    assert badges({"answers": None, "heating_cooling": hc}) == ["double-pane-club"]
    # An explicit renter answer takes precedence over a stale/default model input.
    assert badges({"answers": {"window_panes": 1}, "heating_cooling": hc}) == []


@pytest.mark.parametrize("score,earned", [(0, False), (89.99, False), (90, True), (100, True), (None, False)])
def test_top_10_efficient(score, earned):
    assert ("top-10-efficient" in badges({"score": score})) == earned


def test_leak_hunter_requires_using_fixes():
    assert badges({}, used_fixes=True) == ["leak-hunter"]
    assert badges({}, used_fixes=False) == []


@pytest.mark.parametrize("pct,earned", [(-20, True), (-0.01, True), (0, False), (10, False),
                                        (None, False), ("unknown", False)])
def test_weather_beater(pct, earned):
    assert ("weather-beater" in badges({}, calibration={"pct_vs_expected_for_weather": pct})) == earned


@pytest.mark.parametrize("calibration", [None, {}, {"streak_months": 4}])
def test_missing_calibration(calibration):
    assert badges({}, calibration=calibration) == []


@pytest.mark.parametrize("previous,current,earned", [
    ("F", "D", True), ("D", "C", True), ("C", "B", True), ("B", "A", True),
    ("F", "A", True), ("A", "A", False), ("B", "C", False), (None, "A", False),
    ("F", None, False), ("E", "A", False), ("F", "B–C", False),
])
def test_grade_jumper(previous, current, earned):
    assert ("grade-jumper" in badges({"grade": current}, previous_grade=previous)) == earned


def test_all_rules_are_pure_and_do_not_award_a_battle_win():
    est = {"answers": {"window_panes": 2}, "score": 95, "grade": "A", "badges": ["existing"]}
    calibration = {"pct_vs_expected_for_weather": -12}
    original = deepcopy((est, calibration))
    assert badges(est, calibration=calibration, used_fixes=True, previous_grade="C") == [
        "double-pane-club", "top-10-efficient", "leak-hunter", "weather-beater", "grade-jumper",
    ]
    assert (est, calibration) == original

"""Badge rules from PLAN.md §5; IDs are shared by the web and iMessage clients."""

from math import isfinite

BADGES = {
    "double-pane-club": {"label": "Double-pane club", "emoji": "🪟", "rule": "window_panes >= 2"},
    "top-10-efficient": {"label": "Top 10% efficient", "emoji": "🌟", "rule": "score >= 90"},
    "leak-hunter": {"label": "Leak hunter", "emoji": "🔍", "rule": "used_fixes is true"},
    "weather-beater": {"label": "Weather-beater", "emoji": "🌤️",
                       "rule": "calibration.pct_vs_expected_for_weather < 0"},
    "grade-jumper": {"label": "Grade jumper", "emoji": "📈", "rule": "grade is better than previous_grade"},
    "battle-winner": {"label": "Battle winner", "emoji": "🏆",
                      "rule": "Selected by /compare for the lower annual p50; ties select listing a"},
    "habit-3": {"label": "3-day habit streak", "emoji": "🔥", "rule": "best daily habit streak >= 3 (app/habits.py)"},
    "habit-7": {"label": "7-day habit streak", "emoji": "🗓️", "rule": "best daily habit streak >= 7 (app/habits.py)"},
}
HABIT_BADGES = (("habit-3", 3), ("habit-7", 7))
GRADES = ("A", "B", "C", "D", "F")


def _mapping(value) -> dict:
    return value if isinstance(value, dict) else {}


def _number(value) -> float | None:
    # Interview answers may be numeric strings. Unknown answers and missing model fields earn no badge.
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if isfinite(number) else None


def badges(est: dict, *, calibration: dict | None = None, used_fixes: bool = False,
           previous_grade: str | None = None) -> list[str]:
    """Return earned IDs without changing the estimate; /compare awards battle-winner separately."""
    earned = []
    hc = _mapping(est.get("heating_cooling"))
    detail = _mapping(hc.get("model_detail"))
    panes = None
    for inputs in (est.get("answers"), hc.get("inputs"), detail.get("renter_answers_used")):
        panes = _number(_mapping(inputs).get("window_panes"))
        if panes is not None:
            break
    if panes is not None and panes >= 2:
        earned.append("double-pane-club")
    score = _number(est.get("score"))
    if score is not None and score >= 90:
        earned.append("top-10-efficient")
    if used_fixes:
        earned.append("leak-hunter")
    pct = _number(_mapping(calibration).get("pct_vs_expected_for_weather"))
    if pct is not None and pct < 0:
        earned.append("weather-beater")
    grade = est.get("grade")
    if grade in GRADES and previous_grade in GRADES and GRADES.index(grade) < GRADES.index(previous_grade):
        earned.append("grade-jumper")
    return earned


def habit_badges(best) -> list[str]:
    """Daily habit badges stay earned once the best streak reaches them (self-reported check-ins, not savings)."""
    best = _number(best)
    return [b for b, days in HABIT_BADGES if best is not None and best >= days]

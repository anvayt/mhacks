"""GET /forecast/{session_id} (app/forecast.py) with P1's model and Open-Meteo monkeypatched. Bodies follow
model/heating_cooling/service.py (estimate_hc months[], model_detail; weather() monthly records) and Open-Meteo's
daily JSON."""

import datetime as dt
import json
import math

import httpx
import pytest
from fastapi.testclient import TestClient

from app import forecast, sessions
from app.main import app

client = TestClient(app)
SID = "s-forecast-test"
JAN = [f"2027-01-{d:02d}" for d in range(10, 17)]
JUL = [f"2027-07-{d:02d}" for d in range(10, 17)]
OFFSET_C = 0.3  # PRISM 800 m minus reanalysis, deg C (model/climate.py local_offset_c)


def _history() -> dict:
    """1991-2020 daily means: about -5 C mid-January and 25 C mid-July, plus a +-4 C spread across years."""
    n = (dt.date(2020, 12, 31) - dt.date(1991, 1, 1)).days + 1
    days = [dt.date(1991, 1, 1) + dt.timedelta(i) for i in range(n)]
    return {"time": [d.isoformat() for d in days], "temperature_2m_mean": [
        round(10 - 15 * math.cos(2 * math.pi * (d.timetuple().tm_yday - 15) / 365) + (d.year - 2005.5) * 0.3, 2)
        for d in days]}


HISTORY = _history()


def _hdd60(t_c: float) -> float:
    return max(60 - ((t_c + OFFSET_C) * 9 / 5 + 32), 0)


def _bodies(dates: list[str], tmean: float, month: int, heat_usd: float, cool_usd: float, hdd60: float, cdd65: float):
    """(P1 /hc/estimate?mode=forecast, P1 /hc/weather?mode=forecast, Open-Meteo forecast) for one month in use."""
    hc = {"mode": "forecast", "method": "resstock", "unit_sqft": 850.0,
          "model_detail": {"method": "resstock", "heating_fuel": "gas", "unit_ft2": 850.0},
          "months": [{"month": month, "year": 2027, "days": 31,
                      "heating": {"usd": heat_usd, "gas_ccf": 99.0, "electric_kwh": 0},
                      "cooling": {"usd": cool_usd, "electric_kwh": 0}, "total_usd": heat_usd + cool_usd,
                      "weather": {"tmean_f": 25.0, "hdd65": hdd60 + 155, "cdd65": cdd65, "hdd60": hdd60}}],
          "accuracy": {"monthly_forecast_note": "beyond ~2 weeks, monthly weather comes from the seasonal-forecast "
                                                "ensemble mean or normals; month-to-month detail is not a skilful forecast"}}
    wx = {"lat": 42.2808, "lon": -83.743, "mode": "forecast", "monthly": [
        {"year": 2027, "month": month, "days": 31, "hdd50": hdd60 - 155, "hdd55": hdd60 - 77.5, "hdd60": hdd60,
         "hdd65": hdd60 + 155, "cdd65": cdd65, "cdd70": cdd65 / 2, "cdd75": cdd65 / 4, "tmean_c": -4.0,
         "level_source": "7d observed/forecast, 24d SEAS5 ensemble, 0d PRISM normal", "local_offset_c": OFFSET_C}]}
    fc = {"latitude": 42.3, "longitude": -83.7, "daily": {
        "time": dates, "temperature_2m_mean": [tmean] * 7,
        "temperature_2m_min": [tmean - 5] * 7, "temperature_2m_max": [tmean + 5] * 7}}
    return hc, wx, fc


@pytest.fixture(autouse=True)
def session(monkeypatch, tmp_path):
    monkeypatch.setattr(forecast, "DATA_DIR", tmp_path)  # the 1991-2020 history's disk cache
    forecast._history.cache_clear()
    sessions.save({"session_id": SID, "building": {"lat": 42.2808, "lon": -83.743, "address": "1514 Morton Ave"},
                   "answers": {}, "model_params": {"lat": 42.2808, "lon": -83.743, "unit_sqft": 850.0,
                                                   "building_type": "Multi-Family with 5+ Units",
                                                   "block_group": "261614001001", "window_panes": None}})


def _serve(monkeypatch, bodies, down: str = ""):
    hc, wx, fc = bodies
    calls = []

    def get(url, params=None, timeout=None):
        calls.append((url, params))
        if down and url.startswith(down):
            raise httpx.ConnectError("down")
        body = {f"{forecast.MODEL_BASE_URL}/hc/estimate": hc, f"{forecast.MODEL_BASE_URL}/hc/weather": wx,
                forecast.FORECAST: fc, forecast.ARCHIVE: {"daily": HISTORY}}[url]
        return httpx.Response(200, json=body, request=httpx.Request("GET", url))

    monkeypatch.setattr(forecast.httpx, "get", get)
    return calls


def test_days_apportion_the_months_dollars(monkeypatch):
    # the forecast month's degree-days are exactly these 7 days', so the week must get all of the month's $130
    hdd = 7 * _hdd60(-5.0)
    calls = _serve(monkeypatch, _bodies(JAN, -5.0, 1, heat_usd=130, cool_usd=0, hdd60=hdd, cdd65=0))
    r = client.get(f"/forecast/{SID}")
    assert r.status_code == 200, r.text
    out = r.json()
    assert [d["date"] for d in out["days"]] == JAN
    assert all(d["heating_usd"] == pytest.approx(130 / 7, abs=0.01) and d["cooling_usd"] == 0 for d in out["days"])
    w = out["week"]
    assert w["heating_usd"] == round(sum(d["heating_usd"] for d in out["days"]), 2)
    assert w["heating_usd"] == pytest.approx(130, abs=0.05) and w["total_usd"] == w["heating_usd"]
    assert abs(w["vs_normal_pct"]) <= 5 and out["alerts"] == []  # a typical mid-January week
    est = next(p for u, p in calls if u.endswith("/hc/estimate"))
    assert est["mode"] == "forecast" and est["block_group"] == "261614001001" and "window_panes" not in est


def test_cold_snap_and_costly_week_fire(monkeypatch):
    _serve(monkeypatch, _bodies(JAN, -15.0, 1, heat_usd=130, cool_usd=0, hdd60=1100, cdd65=0))
    out = client.get(f"/forecast/{SID}").json()
    types = [a["type"] for a in out["alerts"]]
    assert types.count("cold_snap") == 7 and "costly_week" in types and "heat_wave" not in types
    assert out["week"]["vs_normal_pct"] > 30
    assert out["alerts"][0]["detail"].startswith(f"Low of {out['days'][0]['low_f']}°F")


def test_heat_wave_fires(monkeypatch):
    _serve(monkeypatch, _bodies(JUL, 32.0, 7, heat_usd=0, cool_usd=40, hdd60=0, cdd65=300))
    out = client.get(f"/forecast/{SID}").json()
    types = {a["type"] for a in out["alerts"]}
    assert "heat_wave" in types and "cold_snap" not in types
    assert out["week"]["cooling_usd"] > 0 and out["week"]["heating_usd"] == 0


def test_unknown_session_is_404():
    r = client.get("/forecast/no-such-session")
    assert r.status_code == 404 and r.json()["detail"]["code"] == "not_found"


@pytest.mark.parametrize("down,code", [(forecast.MODEL_BASE_URL, "model_unavailable"),
                                       (forecast.FORECAST, "forecast_unavailable"),
                                       (forecast.ARCHIVE, "forecast_unavailable")])
def test_down_is_503(monkeypatch, down, code):
    _serve(monkeypatch, _bodies(JAN, -5.0, 1, heat_usd=130, cool_usd=0, hdd60=1100, cdd65=0), down=down)
    r = client.get(f"/forecast/{SID}")
    assert r.status_code == 503 and r.json()["detail"]["code"] == code


def test_metered_bases_come_from_the_buildings_own_fit():
    hc = {"method": "metered", "model_detail": {"heating_fuel": "electric", "gas_fit": {"tau_h": None},
                                                 "elec_fit": {"tau_h": 55.0, "tau_c": 70.0}}}
    assert forecast._bases(hc) == (55, 70)


FETCHED_AT = "2027-01-10T13:00:00+00:00"


def _clock(monkeypatch, value: str):
    monkeypatch.setattr(forecast, "_now", lambda: dt.datetime.fromisoformat(value))


def _warm(monkeypatch):
    _clock(monkeypatch, FETCHED_AT)
    bodies = _bodies(JAN, -5.0, 1, heat_usd=130, cool_usd=0, hdd60=7 * _hdd60(-5.0), cdd65=0)
    _serve(monkeypatch, bodies)
    response = client.get(f"/forecast/{SID}")
    assert response.status_code == 200, response.text
    path = forecast.DATA_DIR / "openmeteo_forecast_42.30_-83.70.json"
    return bodies, response.json(), path


def test_success_saves_raw_forecast_per_grid_cell_with_fetch_time(monkeypatch):
    bodies, out, path = _warm(monkeypatch)
    assert "stale_as_of" not in out
    saved = json.loads(path.read_text())
    assert saved == {"fetched_at": FETCHED_AT, "response": bodies[2]}
    assert not list(forecast.DATA_DIR.glob("*.tmp"))


@pytest.mark.parametrize("error", [httpx.ConnectError("offline"), httpx.ReadTimeout("timeout")])
def test_network_failure_uses_last_good_timestamp_and_drops_past_days(monkeypatch, error):
    bodies, live, path = _warm(monkeypatch)
    original = path.read_bytes()
    _clock(monkeypatch, "2027-01-12T13:00:00+00:00")
    _serve(monkeypatch, bodies)
    get = forecast.httpx.get
    def offline(url, **kwargs):
        if url == forecast.FORECAST:
            raise error
        return get(url, **kwargs)
    monkeypatch.setattr(forecast.httpx, "get", offline)
    r = client.get(f"/forecast/{SID}")
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["stale_as_of"] == FETCHED_AT
    assert out["days"] == live["days"][2:]
    assert out["week"]["total_usd"] == round(sum(d["heating_usd"] + d["cooling_usd"] for d in out["days"]), 2)
    assert path.read_bytes() == original  # using an old forecast never makes it look freshly fetched
    _clock(monkeypatch, "2027-01-13T13:00:00+00:00")
    assert client.get(f"/forecast/{SID}").json()["stale_as_of"] == FETCHED_AT
    assert path.read_bytes() == original


@pytest.mark.parametrize("now,status,remaining", [
    ("2027-01-14T13:00:00+00:00", 200, JAN[4:]),  # exactly 3 valid days, including today
    ("2027-01-15T04:59:59+00:00", 200, JAN[4:]),  # still Jan 14 in Open-Meteo's New York timezone
    ("2027-01-15T05:00:00+00:00", 503, None),     # midnight New York: only 2 days remain
    ("2027-01-17T13:00:00+00:00", 503, None),
])
def test_cached_forecast_needs_three_days_using_local_calendar(monkeypatch, now, status, remaining):
    bodies, _, _ = _warm(monkeypatch)
    _clock(monkeypatch, now)
    _serve(monkeypatch, bodies, down=forecast.FORECAST)
    r = client.get(f"/forecast/{SID}")
    assert r.status_code == status, r.text
    if status == 200:
        assert [d["date"] for d in r.json()["days"]] == remaining
    else:
        assert r.json()["detail"]["code"] == "forecast_unavailable"


def test_null_temperature_does_not_count_toward_three_remaining_days(monkeypatch):
    bodies, _, path = _warm(monkeypatch)
    saved = json.loads(path.read_text())
    saved["response"]["daily"]["temperature_2m_min"][-1] = None
    path.write_text(json.dumps(saved))
    _clock(monkeypatch, "2027-01-14T13:00:00+00:00")
    _serve(monkeypatch, bodies, down=forecast.FORECAST)
    r = client.get(f"/forecast/{SID}")
    assert r.status_code == 503 and r.json()["detail"]["code"] == "forecast_unavailable"


def test_failed_fetch_cannot_use_another_grid_cells_cache(monkeypatch):
    bodies, _, _ = _warm(monkeypatch)
    s = sessions.get(SID)
    s["model_params"]["lat"] = 42.4
    sessions.save(s)
    _serve(monkeypatch, bodies, down=forecast.FORECAST)
    r = client.get(f"/forecast/{SID}")
    assert r.status_code == 503 and r.json()["detail"]["code"] == "forecast_unavailable"


@pytest.mark.parametrize("bad", ["{", {"response": {}},
    {"fetched_at": FETCHED_AT, "response": {"daily": {"time": JAN, "temperature_2m_mean": [1],
         "temperature_2m_min": [0], "temperature_2m_max": [2]}}},
    {"fetched_at": "not-a-date", "response": {}}])
def test_corrupt_or_truncated_cache_is_friendly_503(monkeypatch, bad):
    bodies, _, path = _warm(monkeypatch)
    path.write_text(bad if isinstance(bad, str) else json.dumps(bad))
    _serve(monkeypatch, bodies, down=forecast.FORECAST)
    r = client.get(f"/forecast/{SID}")
    assert r.status_code == 503 and r.json()["detail"]["code"] == "forecast_unavailable"


def test_fresh_success_replaces_cache_and_clears_stale_marker(monkeypatch):
    bodies, _, path = _warm(monkeypatch)
    _clock(monkeypatch, "2027-01-12T13:00:00+00:00")
    bodies[2]["daily"]["temperature_2m_mean"] = [-7] * 7
    _serve(monkeypatch, bodies)
    r = client.get(f"/forecast/{SID}")
    assert r.status_code == 200 and "stale_as_of" not in r.json()
    assert json.loads(path.read_text()) == {"fetched_at": "2027-01-12T13:00:00+00:00", "response": bodies[2]}


def test_invalid_live_response_preserves_last_good_cache(monkeypatch):
    bodies, _, path = _warm(monkeypatch)
    before = path.read_bytes()
    bodies[2]["daily"]["temperature_2m_mean"] = []
    _serve(monkeypatch, bodies)
    r = client.get(f"/forecast/{SID}")
    assert r.status_code == 503 and r.json()["detail"]["code"] == "forecast_unavailable"
    assert path.read_bytes() == before

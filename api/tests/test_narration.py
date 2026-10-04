"""GET /narration/{id}/script and /narration/{id} (api/app/narration.py). xAI TTS is faked; no network."""

import httpx
import pytest
from fastapi.testclient import TestClient

from app import narration, sessions
from app.main import app

client = TestClient(app)
BODY = {"session_id": "nar1", "grade": "C", "grade_span": ["B", "C", "D"], "locked": False,
        "building": {"address": "1514 MORTON AVE, ANN ARBOR, MI, 48104", "type": "Single-Family Detached"},
        "bill": {"annual": {"p10": 1198, "p50": 2117.0, "p90": 3460}}, "hidden_rent_usd_mo": 42,
        "co2_t": {"p10": 6.45, "p50": 11.39, "p90": 18.5}, "answers": {},
        "questions": [{"id": "heating_fuel", "text": "Is the heat gas or electric, or included in your rent?"}]}


@pytest.fixture(autouse=True)
def fakes(monkeypatch, tmp_path):
    monkeypatch.setattr(sessions, "DB", str(tmp_path / "sessions.sqlite"))
    monkeypatch.setattr(narration, "CACHE", tmp_path / "narration")
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    calls = []

    def fake_post(url, json, headers, timeout):
        calls.append(json)
        if json["text"] == "fail":
            raise httpx.ConnectError("down")
        return httpx.Response(200, content=b"ID3" + b"\0" * 2000, request=httpx.Request("POST", url))
    monkeypatch.setattr(narration.httpx, "post", fake_post)
    sessions.save(BODY)
    return calls


def test_script_reads_the_sessions_numbers():
    text = client.get("/narration/nar1/script").json()["text"]
    assert text.startswith("Here's your Hidden Rent report for 1514 Morton Ave.")
    assert "It grades B to D, most likely a C." in text
    assert "about $1,200 to $3,500 a year to heat and cool" in text
    assert "$40 a month of hidden rent" in text
    assert "about 11 tons of CO2" in text
    assert "Ask the landlord: is the heat gas or electric" in text
    assert text.endswith("This is a prediction, not a bill.")
    assert 40 <= len(text.split()) <= 70


def test_script_variants():
    s = {**BODY, "grade_span": ["A"], "grade": "A", "hidden_rent_usd_mo": -15, "co2_t": {"p50": 3.21},
         "questions": [], "answers": {"heating_fuel": "included"}}
    text = narration.script(s)
    assert "It earns an A." in text and "grades" not in text
    assert "a year to cool, and your landlord pays the heat" in text
    assert "$20 a month less than similar homes" in text  # round(15, -1): ties go to even, 20
    assert "about 3.2 tons" in text
    assert "last winter's gas bills" in text


def test_audio_is_mp3_and_cached(fakes):
    r = client.get("/narration/nar1")
    assert r.status_code == 200 and r.headers["content-type"] == "audio/mpeg" and r.content.startswith(b"ID3")
    assert fakes[0]["voice_id"] == "eve" and fakes[0]["language"] == "en" and "1514 Morton Ave" in fakes[0]["text"]
    again = client.get("/narration/nar1")
    assert again.content == r.content and len(fakes) == 1  # second play: no xAI call


def test_unknown_session_404():
    assert client.get("/narration/nope").status_code == 404
    assert client.get("/narration/nope/script").status_code == 404


def test_xai_failure_503(monkeypatch):
    monkeypatch.setattr(narration, "script", lambda s: "fail")
    r = client.get("/narration/nar1")
    assert r.status_code == 503 and r.json()["detail"]["code"] == "narration_unavailable"

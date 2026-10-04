"""GET /narration/{id}/script and GET /narration/{id} ("Watch your report"): the session's stored estimate read aloud
by xAI Grok Voice (docs.x.ai text-to-speech: POST /v1/tts, raw MP3 bytes, 24 kHz / 128 kbps by default).

The script is a fixed template filled from the session body; no model writes any number. MP3s are cached next to
the sessions DB (the /data volume on Fly), keyed by sha256(script + voice), so repeat plays never call xAI.
"""

import hashlib
import logging
import os
from pathlib import Path

import httpx
from fastapi import APIRouter
from fastapi.responses import FileResponse

from app import sessions
from app.estimate import EXPIRED, _fail

XAI_TTS_URL = "https://api.x.ai/v1/tts"
VOICE = "eve"
CACHE = Path(sessions.DB).parent / "narration"
UNAVAILABLE = "Narration isn't available right now. The captions have the full report."
log = logging.getLogger(__name__)
router = APIRouter()


def _usd(x: float) -> str:
    return f"${round(x, -1 if x < 1000 else -2):,.0f}"  # spoken: "about $1,200", not "$1,198"


def script(s: dict) -> str:
    b, bill = s["building"], s["bill"]
    street = b.get("address", "this home").split(",")[0].title()
    span = s.get("grade_span") or [s["grade"]]
    g = f"{'an' if s['grade'] in 'AEF' else 'a'} {s['grade']}"
    grade = f"It earns {g}." if len(span) == 1 else f"It grades {span[0]} to {span[-1]}, most likely {g}."
    a = bill["annual"]
    heat_included = (s.get("answers") or {}).get("heating_fuel") == "included"
    what = "to cool, and your landlord pays the heat" if heat_included else "to heat and cool"
    parts = [f"Here's your Hidden Rent report for {street}.", grade,
             f"Expect about {_usd(a['p10'])} to {_usd(a['p90'])} a year {what}."]
    hr = s.get("hidden_rent_usd_mo")
    if hr is not None:
        parts.append(f"That's about {_usd(hr)} a month of hidden rent versus similar homes." if hr > 0 else
                     f"That's about {_usd(-hr)} a month less than similar homes." if hr < 0 else
                     "That's about the same as similar homes.")
    if (co2 := (s.get("co2_t") or {}).get("p50")) is not None:
        parts.append(f"It emits about {co2:.0f} tons of CO2 a year." if co2 >= 10 else
                     f"It emits about {co2:.1f} tons of CO2 a year.")
    q = (s.get("questions") or [{}])[0].get("text")
    parts.append(f"Ask the landlord: {q[0].lower() + q[1:]}" if q else
                 "Ask the landlord for last winter's gas bills.")
    parts.append("This is a prediction, not a bill.")
    return " ".join(parts)


def _session(session_id: str) -> dict:
    if (s := sessions.get(session_id)) is None:
        raise _fail(404, "not_found", EXPIRED)
    return s


@router.get("/narration/{session_id}/script")
def get_script(session_id: str) -> dict:
    return {"text": script(_session(session_id))}


@router.get("/narration/{session_id}")
def get_narration(session_id: str) -> FileResponse:
    text = script(_session(session_id))
    path = CACHE / f"{hashlib.sha256((text + VOICE).encode()).hexdigest()}.mp3"
    if not path.exists():
        key = os.environ.get("XAI_API_KEY")
        if not key:
            raise _fail(503, "narration_unavailable", UNAVAILABLE)
        try:
            r = httpx.post(XAI_TTS_URL, json={"text": text, "voice_id": VOICE, "language": "en"},
                           headers={"Authorization": f"Bearer {key}"}, timeout=60)
            r.raise_for_status()
        except httpx.HTTPError as e:
            log.warning("xAI TTS failed: %r", e)
            raise _fail(503, "narration_unavailable", UNAVAILABLE)
        if not r.content:
            raise _fail(503, "narration_unavailable", UNAVAILABLE)
        CACHE.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_bytes(r.content)
        tmp.replace(path)  # atomic: a concurrent play never reads half a file
    return FileResponse(path, media_type="audio/mpeg")

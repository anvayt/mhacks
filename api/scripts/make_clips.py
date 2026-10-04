"""One-off: generate the illustrative "Watch your report" clips with Grok Imagine (docs.x.ai video generation).

    cd api && uv run --env-file ../.env python scripts/make_clips.py [category ...]

Writes N candidates per category to web/public/clips/<category>.<i>.mp4 (silent H.264, +faststart) and .jpg (first
frame); look at them and rename the best to <category>.mp4/.jpg. Nothing calls video generation at runtime.
Cost: each poll result carries usage.cost_in_usd_ticks (1 tick = 1e-10 USD); a 10 s 1080p clip was $2.50 (Oct 2026).
"""
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

API = "https://api.x.ai/v1"
MODEL = "grok-imagine-video-1.5"  # docs.x.ai video generation, Oct 2026
SECONDS = 10
CANDIDATES = int(os.environ.get("CANDIDATES", "2"))
OUT = Path(__file__).resolve().parents[2] / "web" / "public" / "clips"

# ResStock building types (building["type"]) -> clip; the same map lives in web/app/watch/page.tsx
SUBJECTS = {
    "house": "a classic two-story wooden Craftsman house with a deep front porch, gabled roof and brick chimney",
    "duplex": "a two-story side-by-side duplex house with two matching front doors, a shared porch and a brick chimney",
    "apartment": "a four-story red-brick apartment building with tall rows of windows and a rooftop vent stack",
}
STYLE = ("Cinematic high-end painterly illustration, like a hand-painted animated film background, rich brushwork, "
         "clean straight architecture, not photorealistic. {s}, seen from across a quiet tree-lined residential street "
         "in Ann Arbor, Michigan, with mature maples and old sidewalks. Slow steady camera push-in toward the home. The "
         "seasons pass in one continuous shot: deep winter at dusk with falling snow and white furnace steam curling "
         "from the chimney and vents under cool blue light; the snow melts into a green spring with budding trees; "
         "then a hot bright summer afternoon with heat shimmer rising off the roof under warm golden-orange light. "
         "Warm amber glow in the windows throughout. No text, no words, no letters, no numbers, no signs, no people, "
         "no cars, no logos.")


def generate(cat: str, i: int, key: str) -> float:
    h = {"Authorization": f"Bearer {key}"}
    r = httpx.post(f"{API}/videos/generations", headers=h, timeout=60, json={
        "model": MODEL, "prompt": STYLE.format(s=SUBJECTS[cat][0].upper() + SUBJECTS[cat][1:]), "duration": SECONDS,
        "aspect_ratio": "16:9", "resolution": "1080p", "generate_audio": False})
    r.raise_for_status()
    rid = r.json()["request_id"]
    print(cat, i, "started", rid, flush=True)
    for _ in range(120):  # ~15 min
        time.sleep(8)
        d = httpx.get(f"{API}/videos/{rid}", headers=h, timeout=60).json()
        if d.get("status") == "done":
            break
        if d.get("status") in ("failed", "expired"):
            raise RuntimeError(f"{cat}: {d.get('status')}")
    else:
        raise TimeoutError(cat)
    secs = d["video"].get("duration") or SECONDS
    cost = (d.get("usage") or {}).get("cost_in_usd_ticks", 0) / 1e10
    raw = OUT / f"{cat}.{i}.raw.mp4"
    raw.write_bytes(httpx.get(d["video"]["url"], timeout=180, follow_redirects=True).content)
    mp4, jpg = OUT / f"{cat}.{i}.mp4", OUT / f"{cat}.{i}.jpg"
    # silent, source resolution, CRF 20 capped at ~5 Mbps (~6.5 MB per 10 s); Safari/iOS need yuv420p + faststart
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-an", "-c:v", "libx264", "-crf", "20",
                    "-maxrate", "5M", "-bufsize", "10M", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", mp4], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-frames:v", "1", "-q:v", "3", jpg], check=True)
    raw.unlink()
    print(cat, i, "done", f"{mp4.stat().st_size / 1e6:.2f} MB", f"{secs}s ${cost:.2f}", flush=True)
    return cost


if __name__ == "__main__":
    key = os.environ.get("XAI_API_KEY_BACKUP") or os.environ["XAI_API_KEY"]
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(c, i) for c in (sys.argv[1:] or SUBJECTS) for i in range(1, CANDIDATES + 1)]
    total = 0.0
    with ThreadPoolExecutor(len(jobs)) as pool:
        for (cat, i), fut in [(j, pool.submit(generate, *j, key)) for j in jobs]:
            try:
                total += fut.result()
            except Exception as e:  # report and keep the others
                print(cat, i, "FAILED", repr(e)[:300], flush=True)
    print(f"total ${total:.2f}", flush=True)

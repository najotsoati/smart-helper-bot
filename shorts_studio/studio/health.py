"""'Tizimni tekshirish': checks every dependency and API key with a tiny, (nearly) free request."""

import asyncio
import shutil
import subprocess
import tempfile
from pathlib import Path

import anthropic
import edge_tts

from . import config, net, youtube


def _ffmpeg() -> str:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("ffmpeg o'rnatilmagan (https://ffmpeg.org/download.html)")
    filters = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    encoders = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
    missing = [n for n, ok in (("subtitles (libass)", " subtitles " in filters),
                               ("libx264", "libx264" in encoders),
                               ("qtrle", "qtrle" in encoders)) if not ok]
    if missing:
        raise RuntimeError("ffmpeg'da yo'q: " + ", ".join(missing) + " (to'liq build o'rnating)")
    return subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout.split("\n")[0]


def _claude() -> str:
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY, max_retries=1)
    model = client.models.retrieve(config.CLAUDE_MODEL)
    return model.display_name


def _pexels() -> str:
    r = net.request("GET", "https://api.pexels.com/videos/search", params={"query": "ocean", "per_page": 1},
                    headers={"Authorization": config.PEXELS_API_KEY}, attempts=1, timeout=15)
    return f"{r.json().get('total_results', 0)} ta 'ocean' videosi"


def _openai() -> str:
    net.request("GET", f"https://api.openai.com/v1/models/{config.IMAGE_MODEL}",
                headers={"Authorization": f"Bearer {config.OPENAI_API_KEY}"}, attempts=1, timeout=15)
    return config.IMAGE_MODEL


def _elevenlabs() -> str:
    r = net.request("GET", "https://api.elevenlabs.io/v1/user/subscription",
                    headers={"xi-api-key": config.ELEVENLABS_API_KEY}, attempts=1, timeout=15)
    d = r.json()
    return f"{d.get('character_count', '?')}/{d.get('character_limit', '?')} belgi ishlatilgan"


def _youtube_key() -> str:
    net.request("GET", "https://www.googleapis.com/youtube/v3/videoCategories",
                params={"part": "snippet", "regionCode": "US", "key": config.YOUTUBE_API_KEY}, attempts=1, timeout=15)
    return "ishlayapti"


def _edge() -> str:
    async def speak():
        with tempfile.TemporaryDirectory() as d:
            await edge_tts.Communicate("Test.", config.DEFAULT_EDGE_VOICE).save(str(Path(d) / "t.mp3"))
    asyncio.run(speak())
    return config.DEFAULT_EDGE_VOICE


def _channel() -> str:
    if not youtube.CLIENT_SECRET.exists():
        raise RuntimeError("client_secret.json yo'q")
    if not youtube.connected():
        raise RuntimeError("kanal hali ulanmagan")
    return youtube.channel()["title"]


CHECKS = [
    # name, required, needs key, function
    ("ffmpeg", True, True, _ffmpeg),
    ("Claude (Anthropic)", True, bool(config.ANTHROPIC_API_KEY), _claude),
    ("Microsoft ovozlari (edge-tts)", True, True, _edge),
    ("Pexels (stok video)", False, bool(config.PEXELS_API_KEY), _pexels),
    ("OpenAI (AI chizmalar)", False, bool(config.OPENAI_API_KEY), _openai),
    ("ElevenLabs (ovoz)", False, bool(config.ELEVENLABS_API_KEY), _elevenlabs),
    ("YouTube API kaliti (trendlar)", False, bool(config.YOUTUBE_API_KEY), _youtube_key),
    ("YouTube kanali (yuklash, analitika)", False, True, _channel),
]


def run_all() -> list[dict]:
    results = []
    for name, required, has_key, fn in CHECKS:
        if not has_key:
            results.append({"name": name, "ok": False, "required": required, "detail": ".env faylida kalit yo'q"})
            continue
        try:
            results.append({"name": name, "ok": True, "required": required, "detail": fn()})
        except Exception as e:
            results.append({"name": name, "ok": False, "required": required, "detail": str(e)[:300]})
    return results

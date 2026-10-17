"""'Tizimni tekshirish': checks every dependency and API key with a tiny, (nearly) free request."""

import asyncio
import shutil
import subprocess
import tempfile
from pathlib import Path

import anthropic
import httpx
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


def _openrouter() -> str:
    from . import openrouter

    return openrouter.key_info()


def _pexels() -> str:
    r = net.request("GET", "https://api.pexels.com/videos/search", params={"query": "ocean", "per_page": 1},
                    headers={"Authorization": config.PEXELS_API_KEY}, attempts=1, timeout=15)
    return f"{r.json().get('total_results', 0)} ta 'ocean' videosi"


def _pixabay() -> str:
    r = net.request("GET", "https://pixabay.com/api/videos/", params={"key": config.PIXABAY_API_KEY, "q": "ocean",
                    "per_page": 3}, attempts=1, timeout=15)
    return f"{r.json().get('totalHits', 0)} ta 'ocean' videosi"


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
        raise RuntimeError("client_secret.json yuklanmagan")
    state = youtube.status()
    if state != "connected":
        raise RuntimeError({"expired": "ulanish muddati tugagan, 'Kanalni ulash' tugmasini qayta bosing",
                            "missing": "kanal hali ulanmagan"}[state])
    return youtube.channel()["title"]


CHECKS = [
    # name, required, config key it needs (None = always run), function
    ("ffmpeg", True, None, _ffmpeg),
    ("Claude (Anthropic) — yoki OpenRouter", False, "ANTHROPIC_API_KEY", _claude),
    ("OpenRouter (bepul AI) — yoki Claude", False, "OPENROUTER_API_KEY", _openrouter),
    ("Microsoft ovozlari (edge-tts)", True, None, _edge),
    ("Pixabay (stok video)", False, "PIXABAY_API_KEY", _pixabay),
    ("Pexels (stok video)", False, "PEXELS_API_KEY", _pexels),
    ("OpenAI (AI chizmalar)", False, "OPENAI_API_KEY", _openai),
    ("ElevenLabs (ovoz)", False, "ELEVENLABS_API_KEY", _elevenlabs),
    ("YouTube API kaliti (trendlar)", False, "YOUTUBE_API_KEY", _youtube_key),
    ("YouTube kanali (yuklash, analitika)", False, None, _channel),
]


def explain(e: Exception) -> str:
    """Plain-language reason for the usual failures."""
    text = str(e).lower()
    if "credit balance is too low" in text:
        return ("Anthropic API balansi tugagan. console.anthropic.com → Settings → Billing'da kredit sotib oling "
                "(Claude ilovasi obunasi API'ga kirmaydi).")
    if "insufficient_quota" in text or "billing_hard_limit" in text:
        return "OpenAI balansi tugagan. platform.openai.com → Billing'da balansni to'ldiring."
    if isinstance(e, httpx.TransportError):
        try:
            host = e.request.url.host
        except RuntimeError:  # no request attached
            host = "xizmat"
        return (f"Internet aloqasi uzildi: {host} bilan ulanib bo'lmadi ({type(e).__name__}). Internet yoki "
                f"xizmat vaqtincha javob bermadi, qayta urinib ko'ring. Takrorlansa, bu xizmat sizning "
                f"tarmog'ingizdan ochilmayotgan bo'lishi mumkin: Tizim → Tekshirish'da qaysi qator ✗ ekanini ko'ring.")[:500]
    response = getattr(e, "response", None)
    status = getattr(e, "status_code", None) or getattr(response, "status_code", None)
    hint = {
        401: "Kalit noto'g'ri (401). Nusxa olishda xato bo'lmaganini tekshiring yoki yangi kalit yarating.",
        403: "Ruxsat yo'q (403): kalit, balans, model yoki hudud cheklovi.",
        429: "Limit tugagan (429): biroz kuting yoki balansni / tarif limitini tekshiring.",
    }.get(status)
    if not hint:
        return f"{type(e).__name__}: {e}"[:400]
    return f"{hint} Xizmat javobi: {_service_message(response)}"[:500]


def _service_message(response) -> str:
    """The provider's own error text, e.g. OpenRouter's reason for a 403."""
    if response is None:
        return "-"
    try:
        err = response.json().get("error", {})
        if isinstance(err, dict):
            meta = err.get("metadata") or {}
            return " ".join(str(x) for x in (err.get("message"), meta.get("raw"), meta.get("reasons")) if x)
        return str(err)
    except Exception:
        return response.text[:300]


def _check(name: str, required: bool, key: str | None, fn) -> dict:
    if key and not getattr(config, key):
        return {"name": name, "ok": False, "required": required, "detail": "kalit kiritilmagan"}
    try:
        return {"name": name, "ok": True, "required": required, "detail": fn()}
    except Exception as e:
        return {"name": name, "ok": False, "required": required, "detail": explain(e)}


def run_all() -> list[dict]:
    return [_check(*c) for c in CHECKS]


def run_for_key(key: str) -> dict | None:
    """Re-test just the service a freshly saved key belongs to."""
    lookup = {"ELEVENLABS_VOICE_ID": "ELEVENLABS_API_KEY", "OPENROUTER_MODEL": "OPENROUTER_API_KEY"}.get(key, key)
    return next((_check(*c) for c in CHECKS if c[2] == lookup), None)

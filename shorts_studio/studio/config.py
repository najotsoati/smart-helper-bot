"""Settings loaded from environment variables (or a .env file next to app.py)."""

import os
from pathlib import Path

from dotenv import load_dotenv, set_key, unset_key

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
load_dotenv(ENV_FILE)

ASSETS = ROOT / "assets"
FONTS_DIR = ASSETS / "fonts"
MUSIC_DIR = ASSETS / "music"
MASCOT_DIR = ASSETS / "mascot"
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
CACHE_DIR = OUTPUT_DIR / ".cache"  # drawings and stock clips, reused by retries and A/B variants

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # only used for drawing illustrations
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gpt-image-1")
IMAGE_QUALITY = os.getenv("IMAGE_QUALITY", "medium")  # low | medium | high
ILLUSTRATION_STYLE = os.getenv(
    "ILLUSTRATION_STYLE",
    "Bold, colorful 2D cartoon illustration with thick clean outlines and soft cel shading, dramatic lighting, "
    "high contrast, one clear subject, vertical 9:16 composition with the subject in the upper two-thirds, "
    "no text, no letters, no numbers, no watermark.",
)
MATCH_THRESHOLD = int(os.getenv("MATCH_THRESHOLD", "80"))  # minimum picture-vs-narration score (0-100)
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")  # "Adam"

CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-5-5")

# Keys the panel can edit (Tizim tab): name -> (label, where to get it)
EDITABLE_KEYS = {
    "ANTHROPIC_API_KEY": ("Claude (Anthropic)", "https://console.anthropic.com/settings/keys"),
    "PEXELS_API_KEY": ("Pexels (stok video)", "https://www.pexels.com/api/"),
    "OPENAI_API_KEY": ("OpenAI (AI chizmalar)", "https://platform.openai.com/api-keys"),
    "ELEVENLABS_API_KEY": ("ElevenLabs (ovoz)", "https://elevenlabs.io/app/settings/api-keys"),
    "ELEVENLABS_VOICE_ID": ("ElevenLabs ovoz ID (ixtiyoriy)", "https://elevenlabs.io/app/voice-library"),
    "YOUTUBE_API_KEY": ("YouTube API kaliti (trendlar)", "https://console.cloud.google.com/apis/credentials"),
}


def save_key(name: str, value: str) -> None:
    """Write a key to .env and apply it right away (no restart needed)."""
    if name not in EDITABLE_KEYS:
        raise ValueError(f"unknown key {name}")
    value = value.strip()
    ENV_FILE.touch(exist_ok=True)
    if value:
        set_key(ENV_FILE, name, value)
        os.environ[name] = value
    else:
        unset_key(ENV_FILE, name)
        os.environ.pop(name, None)
    defaults = {"ELEVENLABS_VOICE_ID": "pNInz6obpgDQGcFmaJgB"}
    globals()[name] = value or defaults.get(name, "")


def masked(name: str) -> str:
    value = globals().get(name, "")
    if not value:
        return ""
    return value[:4] + "…" + value[-4:] if len(value) > 12 else "••••"

WIDTH, HEIGHT, FPS = 1080, 1920, 30

# Free Microsoft neural voices (edge-tts). Energetic storytelling voices work best for facts.
EDGE_VOICES = {
    "Andrew (male, warm)": "en-US-AndrewMultilingualNeural",
    "Brian (male, energetic)": "en-US-BrianMultilingualNeural",
    "Christopher (male, deep)": "en-US-ChristopherNeural",
    "Ava (female, bright)": "en-US-AvaMultilingualNeural",
    "Emma (female, friendly)": "en-US-EmmaMultilingualNeural",
    "Ryan (male, British)": "en-GB-RyanNeural",
}
DEFAULT_EDGE_VOICE = "en-US-AndrewMultilingualNeural"

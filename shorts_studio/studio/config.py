"""Settings loaded from environment variables (or a .env file next to app.py)."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

ASSETS = ROOT / "assets"
FONTS_DIR = ASSETS / "fonts"
MUSIC_DIR = ASSETS / "music"
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")  # "Adam"

CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-5-5")

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

"""Settings from environment variables or the .env file next to the repo root."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv(path):
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv(ROOT / ".env")


def _list(name, default=""):
    return [x.strip() for x in os.environ.get(name, default).split(",") if x.strip()]


DATA_DIR = Path(os.environ.get("STUDIO_DATA_DIR", ROOT / "data"))

PANEL_USER = os.environ.get("PANEL_USER", "admin")
PANEL_PASSWORD = os.environ.get("PANEL_PASSWORD", "")
AGENT_TOKEN = os.environ.get("AGENT_TOKEN", "")
PUBLIC_URL = os.environ.get("PUBLIC_URL", "")

OPENROUTER_API_KEY = "".join(os.environ.get("OPENROUTER_API_KEY", "").split())
# Empty = pick the free models OpenRouter lists right now.
OPENROUTER_MODELS = _list("OPENROUTER_MODELS")
# Optional paid model for the writer and director (better jokes), e.g. a top model on OpenRouter.
OPENROUTER_STRONG_MODELS = _list("OPENROUTER_STRONG_MODELS")
OPENROUTER_DAILY_FREE = int(os.environ.get("OPENROUTER_DAILY_FREE", "50"))

XAI_API_KEY = "".join(os.environ.get("XAI_API_KEY", "").split())
XAI_MODEL = os.environ.get("XAI_MODEL", "grok-4-1-fast-non-reasoning")
# Use Grok first for the creative steps when its key is set (XAI_FIRST=no keeps it as backup only).
XAI_FIRST = os.environ.get("XAI_FIRST", "yes").strip().lower() not in ("no", "0", "false")

# Voice: "edge" (free) or "elevenlabs" (Sticky's Liam voice, paid plan for monetised channels).
TTS_PROVIDER = os.environ.get("TTS_PROVIDER", "edge")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")

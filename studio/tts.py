"""English voices: one MP3 per spoken line, saved into the project's audio folder.

edge-tts is free; ElevenLabs keeps Sticky's channel voice (Liam).  Blender reads
MP3 directly, so no conversion is needed.
"""

import asyncio

import httpx
from mutagen.mp3 import MP3

from . import config, vocab


class TTSError(Exception):
    pass


def _edge(text, voice, path):
    import edge_tts

    async def run():
        await edge_tts.Communicate(text, voice, rate="+6%").save(str(path))
    asyncio.run(run())


def _elevenlabs(text, voice_id, path):
    if not config.ELEVENLABS_API_KEY:
        raise TTSError("ELEVENLABS_API_KEY is not set")
    r = httpx.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                   params={"output_format": "mp3_44100_128"},
                   headers={"xi-api-key": config.ELEVENLABS_API_KEY},
                   json={"text": text, "model_id": config.ELEVENLABS_MODEL},
                   timeout=120)
    if r.status_code >= 400:
        raise TTSError(f"ElevenLabs HTTP {r.status_code}: {r.text[:200]}")
    path.write_bytes(r.content)


def voice_lines(sb, audio_dir, provider=None, only_missing=True):
    """Create audio for every line and store file name and length in the storyboard."""
    provider = provider or config.TTS_PROVIDER
    audio_dir.mkdir(parents=True, exist_ok=True)
    for ln in sb["lines"]:
        path = audio_dir / f"{ln['id']}.mp3"
        same = ln.get("voiced_text") == ln["text"] and ln.get("voiced_by") == provider
        if not (only_missing and path.exists() and same):
            el_id, edge_voice = vocab.VOICES.get(ln["speaker"], vocab.VOICES["sticky"])
            if provider == "elevenlabs":
                _elevenlabs(ln["text"], el_id, path)
            else:
                _edge(ln["text"], edge_voice, path)
        ln["file"] = path.name
        ln["seconds"] = round(MP3(str(path)).info.length, 2)
        ln["voiced_text"] = ln["text"]
        ln["voiced_by"] = provider
    return sb

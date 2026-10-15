"""English voices: one MP3 per spoken line, saved into the project's audio folder.

edge-tts is free; ElevenLabs keeps Sticky's channel voice (Liam).  Blender reads
MP3 directly, so no conversion is needed.
"""

import asyncio

import httpx
from mutagen.mp3 import MP3

from . import config, store, vocab


class TTSError(Exception):
    pass


def edge_voice(speaker):
    chosen = store.settings().get("voices", {}).get(speaker)
    return chosen or vocab.VOICES.get(speaker, vocab.VOICES["sticky"])[1]


def _edge(text, voice, path, mood="normal"):
    import edge_tts
    rate, pitch, volume = vocab.MOODS.get(mood, vocab.MOODS["normal"])

    async def run():
        await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=volume).save(str(path))
    asyncio.run(run())


SAMPLE = "Payday! I'm rich! ... Wait. Where did all my money go?"


def sample(voice, mood, folder):
    """Audition clip for the voices page; cached per voice and mood."""
    if voice not in vocab.VOICE_CHOICES or mood not in vocab.MOODS:
        raise TTSError("unknown voice or mood")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{voice}_{mood}.mp3"
    if not path.exists():
        _edge(SAMPLE, voice, path, mood)
    return path


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
        el_id = vocab.VOICES.get(ln["speaker"], vocab.VOICES["sticky"])[0]
        who = el_id if provider == "elevenlabs" else edge_voice(ln["speaker"])
        stamp = f"{provider}|{who}|{ln.get('mood', 'normal')}|{ln['text']}"
        if not (only_missing and path.exists() and ln.get("voiced") == stamp):
            if provider == "elevenlabs":
                _elevenlabs(ln["text"], el_id, path)
            else:
                _edge(ln["text"], who, path, ln.get("mood", "normal"))
        ln["file"] = path.name
        ln["seconds"] = round(MP3(str(path)).info.length, 2)
        ln["voiced"] = stamp
    return sb

"""Text-to-speech with word-level timestamps (for synced captions).

Uses ElevenLabs when ELEVENLABS_API_KEY is set (most human-sounding), otherwise free edge-tts.
Each scene is voiced separately so scene boundaries are exact.
"""

import asyncio
import base64
import re
from dataclasses import dataclass
from pathlib import Path

import edge_tts
import httpx

from . import config
from .ffmpeg import probe_duration, run


@dataclass
class Word:
    text: str
    start: float
    end: float


@dataclass
class VoicedScene:
    audio: Path
    duration: float
    words: list[Word]


async def _edge(text: str, voice: str, rate: str, out: Path) -> list[Word]:
    communicate = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    words: list[Word] = []
    with out.open("wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 1e7  # 100-nanosecond ticks
                words.append(Word(chunk["text"], start, start + chunk["duration"] / 1e7))
    return words


def _elevenlabs(text: str, out: Path) -> list[Word]:
    r = httpx.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{config.ELEVENLABS_VOICE_ID}/with-timestamps",
        headers={"xi-api-key": config.ELEVENLABS_API_KEY},
        json={
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.35, "similarity_boost": 0.8, "style": 0.45},
        },
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    out.write_bytes(base64.b64decode(data["audio_base64"]))

    align = data["alignment"]
    words: list[Word] = []
    current, start = "", None
    for ch, s, e in zip(
        align["characters"], align["character_start_times_seconds"], align["character_end_times_seconds"]
    ):
        if ch.isspace():
            if current:
                words.append(Word(current, start, end))
            current, start = "", None
            continue
        if start is None:
            start = s
        current += ch
        end = e
    if current:
        words.append(Word(current, start, end))
    return words


def voice_scene(text: str, out_dir: Path, index: int, voice: str, rate: str = "+12%") -> VoicedScene:
    raw = out_dir / f"voice_{index:02d}.mp3"
    if config.ELEVENLABS_API_KEY and voice == "elevenlabs":
        words = _elevenlabs(text, raw)
    else:
        words = asyncio.run(_edge(text, voice, rate, raw))

    # Normalise to wav and cut trailing silence down to a tight gap so the pacing stays fast.
    wav = out_dir / f"voice_{index:02d}.wav"
    end = (words[-1].end + 0.12) if words else probe_duration(raw)
    run(["ffmpeg", "-y", "-i", str(raw), "-t", f"{end:.3f}", "-ar", "44100", "-ac", "1", str(wav)])
    return VoicedScene(wav, probe_duration(wav), [w for w in words if re.search(r"\w", w.text)])


def silent_scene(text: str, out_dir: Path, index: int) -> VoicedScene:
    """Offline stand-in for tests: silence with evenly spaced fake word timings."""
    tokens = text.split()
    per_word = 0.36
    words = [Word(t, i * per_word, (i + 1) * per_word) for i, t in enumerate(tokens)]
    duration = len(tokens) * per_word + 0.12
    wav = out_dir / f"voice_{index:02d}.wav"
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{duration:.3f}", str(wav)])
    return VoicedScene(wav, duration, words)

"""Fakti, the cartoon host: lip-synced from the voice track, rendered as two transparent videos
(a big full-body version for host scenes and a small round badge for the rest of the video).

Replace the PNGs in assets/mascot/ (same file names, square, transparent) to use your own character."""

import random
import wave
from array import array
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

from . import config
from .ffmpeg import run

BIG = 860
BADGE = 230
POSES = ["closed", "half", "open", "blink", "surprised_closed", "surprised_open"]


def _levels(voice_wav: Path, fps: int) -> list[float]:
    """Loudness per video frame, scaled to 0-1."""
    with wave.open(str(voice_wav)) as w:
        rate, channels = w.getframerate(), w.getnchannels()
        samples = array("h", w.readframes(w.getnframes()))
    if channels > 1:
        samples = samples[::channels]
    hop = rate // fps
    levels = []
    for i in range(0, len(samples), hop):
        chunk = samples[i:i + hop]
        levels.append((sum(s * s for s in chunk) / max(len(chunk), 1)) ** 0.5)
    peak = sorted(levels)[int(len(levels) * 0.95)] if levels else 1
    return [min(v / (peak or 1), 1.0) for v in levels]


def timeline(voice_wav: Path, surprised: list[tuple[float, float]], fps: int = config.FPS) -> list[str]:
    """One pose name per frame."""
    poses = []
    for v in _levels(voice_wav, fps):
        poses.append("closed" if v < 0.12 else "half" if v < 0.45 else "open")
    # hold each mouth shape >= 2 frames so it doesn't flicker
    for i in range(1, len(poses) - 1):
        if poses[i] != poses[i - 1] and poses[i] != poses[i + 1]:
            poses[i] = poses[i - 1]
    for i in range(len(poses)):
        t = i / fps
        if any(a <= t < b for a, b in surprised):
            poses[i] = "surprised_closed" if poses[i] == "closed" else "surprised_open"
    # blink for 4 frames every 2.5-4.5 s
    i = int(fps * random.uniform(1.5, 3))
    while i < len(poses) - 4:
        for k in range(4):
            if not poses[i + k].startswith("surprised"):
                poses[i + k] = "blink"
        i += int(fps * random.uniform(2.5, 4.5))
    return poses


def _badge(pose: Image.Image) -> Image.Image:
    """Round yellow badge with the character's face."""
    size, ring = BADGE, 9
    badge = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)
    draw.ellipse((0, 0, size - 1, size - 1), fill=(255, 255, 255, 255))
    draw.ellipse((ring, ring, size - 1 - ring, size - 1 - ring), fill=(255, 229, 0, 255))
    face = pose.crop((140, 150, 860, 870)).resize((size - 2 * ring, size - 2 * ring), Image.LANCZOS)
    circle = Image.new("L", face.size, 0)
    ImageDraw.Draw(circle).ellipse((0, 0, face.size[0] - 1, face.size[1] - 1), fill=255)
    face.putalpha(ImageChops.multiply(face.getchannel("A"), circle))
    badge.alpha_composite(face, (ring, ring))
    return badge


def _encode(frames: list[str], images: dict[str, Path], out: Path, fps: int) -> Path:
    """Run-length encode the pose sequence into a concat list, then a transparent .mov."""
    listing = out.with_suffix(".txt")
    lines, i = [], 0
    while i < len(frames):
        j = i
        while j < len(frames) and frames[j] == frames[i]:
            j += 1
        lines.append(f"file '{images[frames[i]].name}'\nduration {(j - i) / fps:.4f}\n")
        i = j
    lines.append(f"file '{images[frames[-1]].name}'\n")  # concat demuxer needs the last file repeated
    listing.write_text("".join(lines))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-vf", f"fps={fps},format=argb",
         "-c:v", "qtrle", str(out)])
    return out


def build(voice_wav: Path, surprised: list[tuple[float, float]], work: Path) -> tuple[Path, Path]:
    frames = timeline(voice_wav, surprised)
    big, badge = {}, {}
    for pose in POSES:
        src = Image.open(config.MASCOT_DIR / f"{pose}.png").convert("RGBA").resize((1000, 1000), Image.LANCZOS)
        big[pose] = work / f"mascot_big_{pose}.png"
        src.resize((BIG, BIG), Image.LANCZOS).save(big[pose])
        badge[pose] = work / f"mascot_badge_{pose}.png"
        _badge(src).save(badge[pose])
    return (_encode(frames, big, work / "mascot_big.mov", config.FPS),
            _encode(frames, badge, work / "mascot_badge.mov", config.FPS))

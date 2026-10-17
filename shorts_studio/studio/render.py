"""ffmpeg rendering: punchy scene clips, captions, progress bar, sound design and music ducking."""

import os
import random
from pathlib import Path

from . import config
from .ffmpeg import run

W, H, FPS = config.WIDTH, config.HEIGHT, config.FPS
# Intermediate shots: fast. Final upload file: high quality, since YouTube re-compresses it anyway.
DRAFT = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(FPS)]
FINAL = ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
         "-r", str(FPS)]

GRADIENTS = [
    ("0x0f0c29", "0x7b2ff7"),
    ("0x000428", "0x004e92"),
    ("0x200122", "0xff0844"),
    ("0x0b3d0b", "0x00c9a7"),
    ("0x1f1c2c", "0xf7971e"),
]


MOVES = ["push_in", "pan_right", "tilt_up", "pull_out", "pan_left"]


def _motion(duration: float, move: str = "push_in", punch: float = 0.10, dim: bool = False,
            shake: bool = False) -> str:
    """Cover-crop to 9:16 with a quick 'punch' zoom on the cut, then a camera move:
    push_in / pull_out (slow zoom), pan_left / pan_right, tilt_up. `shake` adds a subtle handheld wobble.
    `dim` blurs and darkens the shot so an infographic on top stays readable."""
    d = f"{duration:.3f}"
    drift = {"push_in": f"0.07*t/{d}", "pull_out": f"0.07*(1-t/{d})"}.get(move, "0.02")
    z = f"(1.12*(1+{punch}*max(0\\,1-t/0.2)+{drift}))"  # 12% overscan leaves room to pan
    x, y = "(iw-ow)/2", "(ih-oh)/2"
    if move == "pan_right":
        x = f"(iw-ow)*(0.15+0.7*t/{d})"
    elif move == "pan_left":
        x = f"(iw-ow)*(0.85-0.7*t/{d})"
    elif move == "tilt_up":
        y = f"(ih-oh)*(0.85-0.7*t/{d})"
    if shake:
        x = f"clip({x}+5*sin(11*t)+3*sin(6.7*t)\\,0\\,iw-ow)"
        y = f"clip({y}+4*sin(9.3*t+1)\\,0\\,ih-oh)"
    look = "boxblur=18:2,eq=brightness=-0.22:saturation=0.9" if dim else "eq=contrast=1.07:saturation=1.22"
    return (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"scale=w='trunc({W}*{z}/2)*2':h='trunc({H}*{z}/2)*2':eval=frame,crop={W}:{H}:x='{x}':y='{y}',"
        f"{look},fps={FPS},setsar=1,format=yuv420p"
    )


def clip_segment(src: Path, src_duration: float, duration: float, out: Path, move: str = "push_in",
                 punch: float = 0.10, dim: bool = False) -> Path:
    max_offset = max(src_duration - duration - 0.2, 0)
    offset = random.uniform(0, min(max_offset, 4.0))
    run(
        ["ffmpeg", "-y", "-stream_loop", "-1", "-ss", f"{offset:.2f}", "-i", str(src), "-t", f"{duration:.3f}",
         "-vf", _motion(duration, move, punch, dim), "-an", *DRAFT, str(out)]
    )
    return out


def image_segment(image: Path, duration: float, out: Path, move: str = "push_in", punch: float = 0.10,
                  dim: bool = False) -> Path:
    """A still illustration brought to life: punch zoom, a camera move and a handheld wobble."""
    run(["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", str(image), "-t", f"{duration:.3f}",
         "-vf", _motion(duration, move, punch, dim, shake=True), *DRAFT, str(out)])
    return out


MASCOT_BACKDROP = ("0x0f2027", "0x2c7a7b")  # teal, so the purple host pops


def gradient_segment(duration: float, out: Path, index: int, punch: float = 0.10,
                     colors: tuple[str, str] | None = None) -> Path:
    c0, c1 = colors or GRADIENTS[index % len(GRADIENTS)]
    src = f"gradients=s={W}x{H}:c0={c0}:c1={c1}:x0=0:y0=0:x1={W}:y1={H}:speed=0.03:r={FPS}"
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", src, "-t", f"{duration:.3f}",
         "-vf", _motion(duration, "push_in" if index % 2 == 0 else "pull_out", punch), *DRAFT, str(out)])
    return out


def concat(parts: list[Path], out: Path, reencode_audio: bool = False) -> Path:
    listing = out.with_suffix(".txt")
    listing.write_text("".join(f"file '{p.name}'\n" for p in parts))
    codec = ["-c:a", "pcm_s16le"] if reencode_audio else ["-c", "copy"]
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), *codec, str(out)])
    return out


def finish(
    base_video: Path,
    voice: Path,
    ass_file: Path,
    sfx_events: list[tuple[Path, float, float]],
    total: float,
    out: Path,
    music: Path | None,
    mascot: tuple[Path, Path] | None = None,
    host_ranges: list[tuple[float, float]] = (),
) -> Path:
    """Overlay the host, burn captions + progress bar, and mix voice, sound effects (file, start time,
    volume) and ducked music. The big host shows during `host_ranges`, the round badge the rest of the time."""
    work = out.parent
    inputs = ["-i", base_video.name, "-i", voice.name]
    for path, _, _ in sfx_events:
        inputs += ["-i", str(path)]
    next_idx = 2 + len(sfx_events)
    music_idx = None
    if music:
        music_idx = next_idx
        next_idx += 1
        inputs += ["-stream_loop", "-1", "-i", str(music.resolve())]

    fonts = Path(os.path.relpath(config.FONTS_DIR, work)).as_posix()
    video_in = "[0:v]"
    filters = []
    if mascot:
        big, badge = mascot
        inputs += ["-i", big.name, "-i", badge.name]
        on = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in host_ranges) or "0"
        filters += [
            # gentle bob so the host never looks frozen
            f"[0:v][{next_idx}:v]overlay=x=(W-w)/2:y='500+10*sin(2*PI*1.3*t)':enable='{on}':eof_action=pass[h1]",
            f"[h1][{next_idx + 1}:v]overlay=x=36:y=200:enable='not({on})':eof_action=pass[h2]",
        ]
        video_in = "[h2]"
    filters += [
        f"{video_in}subtitles={ass_file.name}:fontsdir={fonts}[cap]",
        f"color=c=0xFFE500:s={W}x14:r={FPS}[bar]",
        f"[cap][bar]overlay=x='-w+w*t/{total:.3f}':y=H-h:shortest=1,format=yuv420p[v]",
        "[1:a]asplit=2[vo][key]",
    ]
    mix = ["[vo]"]
    for i, (_, start, volume) in enumerate(sfx_events):
        ms = int(max(start, 0) * 1000)
        filters.append(f"[{2 + i}:a]aformat=sample_rates=44100:channel_layouts=mono,"
                       f"adelay={ms}|{ms},volume={volume}[s{i}]")
        mix.append(f"[s{i}]")
    if music_idx is not None:
        filters.append(f"[{music_idx}:a]aformat=sample_rates=44100:channel_layouts=mono,"
                       f"volume=0.22,atrim=0:{total:.3f}[mus]")
        filters.append("[mus][key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[duck]")
        mix.append("[duck]")
    else:
        filters.append("[key]anullsink")
    filters.append(
        f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,"
        f"loudnorm=I=-14:TP=-1.5:LRA=11,atrim=0:{total:.3f}[a]"
    )

    # Run inside the job folder so the subtitles filter gets short relative paths (no escaping issues).
    run(
        ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", "[v]", "-map", "[a]",
         *FINAL, "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-t", f"{total:.3f}",
         "-movflags", "+faststart", out.name],
        cwd=work,
    )
    return out

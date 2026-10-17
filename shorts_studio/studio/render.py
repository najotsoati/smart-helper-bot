"""ffmpeg rendering: punchy scene clips, captions, progress bar, sound design and music ducking."""

import os
import random
from pathlib import Path

from . import config
from .ffmpeg import run

W, H, FPS = config.WIDTH, config.HEIGHT, config.FPS
ENCODE = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS)]

GRADIENTS = [
    ("0x0f0c29", "0x7b2ff7"),
    ("0x000428", "0x004e92"),
    ("0x200122", "0xff0844"),
    ("0x0b3d0b", "0x00c9a7"),
    ("0x1f1c2c", "0xf7971e"),
]


def _motion(duration: float, zoom_in: bool) -> str:
    """Cover-crop to 9:16, a quick 'punch' zoom on the cut, then a slow push in (or pull out)."""
    drift = f"0.07*t/{duration:.3f}" if zoom_in else f"0.07*(1-t/{duration:.3f})"
    z = f"(1+0.10*max(0\\,1-t/0.2)+{drift})"
    return (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"scale=w='trunc({W}*{z}/2)*2':h='trunc({H}*{z}/2)*2':eval=frame,crop={W}:{H},"
        f"eq=contrast=1.07:saturation=1.22,fps={FPS},setsar=1,format=yuv420p"
    )


def clip_segment(src: Path, src_duration: float, duration: float, out: Path, zoom_in: bool) -> Path:
    max_offset = max(src_duration - duration - 0.2, 0)
    offset = random.uniform(0, min(max_offset, 4.0))
    run(
        ["ffmpeg", "-y", "-stream_loop", "-1", "-ss", f"{offset:.2f}", "-i", str(src), "-t", f"{duration:.3f}",
         "-vf", _motion(duration, zoom_in), "-an", *ENCODE, str(out)]
    )
    return out


def gradient_segment(duration: float, out: Path, index: int) -> Path:
    c0, c1 = GRADIENTS[index % len(GRADIENTS)]
    src = f"gradients=s={W}x{H}:c0={c0}:c1={c1}:x0=0:y0=0:x1={W}:y1={H}:speed=0.03:r={FPS}"
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", src, "-t", f"{duration:.3f}",
         "-vf", _motion(duration, index % 2 == 0), *ENCODE, str(out)])
    return out


def concat(parts: list[Path], out: Path, reencode_audio: bool = False) -> Path:
    listing = out.with_suffix(".txt")
    listing.write_text("".join(f"file '{p.name}'\n" for p in parts))
    codec = ["-c:a", "pcm_s16le"] if reencode_audio else ["-c", "copy"]
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), *codec, str(out)])
    return out


def make_sfx(work: Path) -> tuple[Path, Path]:
    whoosh = work / "sfx_whoosh.wav"
    impact = work / "sfx_impact.wav"
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anoisesrc=d=0.42:c=pink:a=0.6:r=44100",
         "-af", "highpass=f=700,lowpass=f=7000,afade=t=in:d=0.3:curve=exp,afade=t=out:st=0.3:d=0.12,volume=0.9",
         "-ac", "1", str(whoosh)])
    run(["ffmpeg", "-y", "-f", "lavfi",
         "-i", "aevalsrc='0.9*sin(2*PI*(45+140*exp(-18*t))*t)*exp(-5*t)':d=0.8:s=44100",
         "-ac", "1", str(impact)])
    return whoosh, impact


def finish(
    base_video: Path,
    voice: Path,
    ass_file: Path,
    cut_times: list[float],
    total: float,
    out: Path,
    music: Path | None,
) -> Path:
    work = out.parent
    whoosh, impact = make_sfx(work)

    inputs = ["-i", base_video.name, "-i", voice.name, "-i", impact.name]
    # whoosh slightly before each cut so it "pulls" into the next shot
    cuts = [t for t in cut_times if t > 0.3]
    for _ in cuts:
        inputs += ["-i", whoosh.name]
    music_idx = None
    if music:
        music_idx = 3 + len(cuts)
        inputs += ["-stream_loop", "-1", "-i", str(music.resolve())]

    fonts = Path(os.path.relpath(config.FONTS_DIR, work)).as_posix()
    filters = [
        f"[0:v]subtitles={ass_file.name}:fontsdir={fonts}[cap]",
        f"color=c=0xFFE500:s={W}x14:r={FPS}[bar]",
        f"[cap][bar]overlay=x='-w+w*t/{total:.3f}':y=H-h:shortest=1,format=yuv420p[v]",
        "[2:a]volume=0.55[imp]",
    ]
    sfx_labels = ["[imp]"]
    for i, t in enumerate(cuts):
        ms = int(max(t - 0.25, 0) * 1000)
        filters.append(f"[{3 + i}:a]adelay={ms}|{ms},volume=0.35[w{i}]")
        sfx_labels.append(f"[w{i}]")
    filters.append("[1:a]asplit=2[vo][key]")
    mix = ["[vo]", *sfx_labels]
    if music_idx is not None:
        filters.append(f"[{music_idx}:a]volume=0.22,atrim=0:{total:.3f}[mus]")
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
         *ENCODE, "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-t", f"{total:.3f}",
         "-movflags", "+faststart", out.name],
        cwd=work,
    )
    return out

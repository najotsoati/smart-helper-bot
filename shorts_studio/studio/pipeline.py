"""End-to-end: script -> voice -> footage -> captions/graphics -> sound design -> final 9:16 video."""

import json
import math
import random
import re
import shutil
import time
from pathlib import Path
from typing import Callable

from . import captions, config, graphics, render, sfx, visuals
from .ffmpeg import probe_duration, run
from .script import Scene, ShortScript
from .voice import Word, silent_scene, voice_scene

Progress = Callable[[str, float], None]

MAX_SHOT = 2.8  # seconds; longer scenes get split into several shots so the picture keeps changing
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".ogg"}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "short"


def new_job_dir(topic: str) -> Path:
    job = config.OUTPUT_DIR / f"{time.strftime('%Y%m%d-%H%M%S')}-{_slug(topic)}"
    job.mkdir(parents=True)
    return job


def pick_music(mood: str) -> Path | None:
    """assets/music/<mood>/*.mp3 first, then any track in assets/music/."""
    for folder in (config.MUSIC_DIR / mood, config.MUSIC_DIR):
        tracks = sorted(p for p in folder.glob("*") if p.suffix.lower() in AUDIO_EXT)
        if tracks:
            return random.choice(tracks)
    return None


def _graphic_events(scene: Scene, start: float, end: float) -> list[str]:
    if scene.graphic_type == "counter" and scene.counter_value:
        return graphics.counter(start, end, scene.counter_value, scene.counter_prefix, scene.counter_suffix,
                                scene.graphic_label)
    if scene.graphic_type == "compare" and (scene.compare_a_value or scene.compare_b_value):
        return graphics.compare(start, end, scene.compare_a_label, scene.compare_a_value,
                                scene.compare_b_label, scene.compare_b_value, scene.graphic_label)
    return []


def make_video(
    script: ShortScript,
    job: Path,
    voice: str = config.DEFAULT_EDGE_VOICE,
    rate: str = "+12%",
    music: bool = True,
    series: str = "",
    offline: bool = False,
    progress: Progress = lambda step, pct: None,
) -> Path:
    (job / "script.json").write_text(script.model_dump_json(indent=2))
    work = job / "work"
    work.mkdir(exist_ok=True)
    scenes = script.scenes

    # 1. Voice, scene by scene
    voiced = []
    for i, scene in enumerate(scenes):
        progress(f"Ovoz: {i + 1}/{len(scenes)}", 0.03 + 0.2 * i / len(scenes))
        if offline:
            voiced.append(silent_scene(scene.narration, work, i))
        else:
            voiced.append(voice_scene(scene.narration, work, i, voice, rate))
    voice_track = render.concat([v.audio for v in voiced], work / "voice.wav", reencode_audio=True)
    total = probe_duration(voice_track)

    # 2. Timeline: global word timings, titles, graphics, sound effects
    words: list[captions.TimedWord] = []
    titles: list[tuple[float, float, str]] = []
    extra: list[str] = []
    sfx_events: list[tuple[Path, float, float]] = [(sfx.get("impact", work), 0.0, 0.55)]
    scene_starts: list[float] = []
    last_ding = -10.0
    t = 0.0
    for scene, v in zip(scenes, voiced):
        scene_starts.append(t)
        shifted = [Word(w.text, w.start + t, w.end + t) for w in v.words]
        marked = captions.mark_emphasis(shifted, scene.emphasis)
        words += marked
        graphic = _graphic_events(scene, t, t + v.duration)
        extra += graphic
        if scene.on_screen_text.strip() and not graphic:
            titles.append((t, t + min(v.duration, 2.2), scene.on_screen_text))
        if scene.beat == "twist" and t > 2:
            sfx_events.append((sfx.get("riser", work), t - 1.6, 0.45))
            sfx_events.append((sfx.get("drop", work), t, 0.6))
        # a "ding" on the first number of a scene, at most one every 3 s
        number = next((w for w in marked if w.emphasis and re.search(r"\d", w.text)), None)
        if number and not graphic and number.start - last_ding > 3:
            sfx_events.append((sfx.get("ding", work), number.start, 0.3))
            last_ding = number.start
        t += v.duration

    # 3. Footage: gather candidates, let Claude look at them and pick, then cut
    shots_per_scene = []
    for scene, v in zip(scenes, voiced):
        steady = scene.graphic_type != "none"  # don't cut away under an infographic
        shots_per_scene.append(1 if steady else max(1, math.ceil(v.duration / MAX_SHOT)))

    picked: list[list[visuals.Candidate]] = [[] for _ in scenes]
    if not offline and config.PEXELS_API_KEY:
        used: set[int] = set()
        pool = []
        for i, (scene, n) in enumerate(zip(scenes, shots_per_scene)):
            progress(f"Video qidirilmoqda: {i + 1}/{len(scenes)} ({scene.visual_query})", 0.25 + 0.15 * i / len(scenes))
            cands = visuals.candidates_for(scene.visual_query, min(n + 3, 6), used)
            used |= {c.id for c in cands}
            pool.append((scene.narration, n, cands))
        progress("Claude eng yaxshi kadrlarni tanlayapti...", 0.42)
        picked = visuals.choose(pool)

    segments: list[Path] = []
    shot = 0
    for i, (scene, v) in enumerate(zip(scenes, voiced)):
        progress(f"Montaj: sahna {i + 1}/{len(scenes)}", 0.45 + 0.35 * i / len(scenes))
        n = shots_per_scene[i]
        clips = picked[i]
        start = scene_starts[i]
        dim = scene.graphic_type != "none"
        punch = 0.18 if scene.beat == "twist" else 0.10
        for k in range(n):
            length = v.duration / n
            if start > 0.3:
                sfx_events.append((sfx.get("whoosh", work), start - 0.25, 0.32))
            out = work / f"shot_{shot:03d}.mp4"
            if clips:
                c = clips[k] if k < len(clips) else random.choice(clips)
                src = visuals.download(c.url, work / f"src_{c.id}.mp4")
                render.clip_segment(src, c.duration, length, out, zoom_in=shot % 2 == 0, punch=punch, dim=dim)
            else:
                render.gradient_segment(length, out, shot, punch)
            segments.append(out)
            start += length
            shot += 1
    base = render.concat(segments, work / "base.mp4")

    # 4. Captions + final mix
    progress("Yakuniy render: subtitr, grafika, effektlar, musiqa", 0.85)
    ass = work / "captions.ass"
    ass.write_text(captions.build_ass(words, titles, total, extra, series), encoding="utf-8")
    track = pick_music(script.mood) if music else None
    final = render.finish(base, voice_track, ass, sfx_events, total, work / "final.mp4", track)

    video = job / "video.mp4"
    final.replace(video)
    run(["ffmpeg", "-y", "-ss", "0.6", "-i", str(video), "-frames:v", "1", "-q:v", "3", str(job / "cover.jpg")])
    title = f"{series}: {script.title}" if series else script.title
    meta = {
        "title": title,
        "description": script.description + "\n\n" + " ".join("#" + h.lstrip("#") for h in script.hashtags),
        "pinned_comment": script.pinned_comment,
        "duration": round(total, 1),
        "mood": script.mood,
        "music": track.name if track else None,
    }
    (job / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    shutil.rmtree(work, ignore_errors=True)  # downloaded clips and temp renders can be hundreds of MB
    progress("Tayyor!", 1.0)
    return video

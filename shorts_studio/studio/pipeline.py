"""End-to-end: script -> voice -> footage -> captions -> final 9:16 video."""

import json
import math
import random
import re
import shutil
import time
from pathlib import Path
from typing import Callable

from . import captions, config, render, visuals
from .ffmpeg import probe_duration, run
from .script import ShortScript
from .voice import Word, silent_scene, voice_scene

Progress = Callable[[str, float], None]

MAX_SHOT = 2.8  # seconds; longer scenes get split into several shots so the picture keeps changing


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "short"


def new_job_dir(topic: str) -> Path:
    job = config.OUTPUT_DIR / f"{time.strftime('%Y%m%d-%H%M%S')}-{_slug(topic)}"
    job.mkdir(parents=True)
    return job


def make_video(
    script: ShortScript,
    job: Path,
    voice: str = config.DEFAULT_EDGE_VOICE,
    music: bool = True,
    offline: bool = False,
    progress: Progress = lambda step, pct: None,
) -> Path:
    (job / "script.json").write_text(script.model_dump_json(indent=2))
    work = job / "work"
    work.mkdir(exist_ok=True)

    # 1. Voice, scene by scene
    voiced = []
    for i, scene in enumerate(script.scenes):
        progress(f"Ovoz: {i + 1}/{len(script.scenes)}", 0.05 + 0.25 * i / len(script.scenes))
        if offline:
            voiced.append(silent_scene(scene.narration, work, i))
        else:
            voiced.append(voice_scene(scene.narration, work, i, voice))
    voice_track = render.concat([v.audio for v in voiced], work / "voice.wav", reencode_audio=True)
    total = probe_duration(voice_track)

    # 2. Timeline: global word timings, scene starts, shot cuts
    words: list[captions.TimedWord] = []
    titles: list[tuple[float, float, str]] = []
    scene_starts: list[float] = []
    t = 0.0
    for scene, v in zip(script.scenes, voiced):
        scene_starts.append(t)
        shifted = [Word(w.text, w.start + t, w.end + t) for w in v.words]
        words += captions.mark_emphasis(shifted, scene.emphasis)
        if scene.on_screen_text.strip():
            titles.append((t, t + min(v.duration, 2.2), scene.on_screen_text))
        t += v.duration

    # 3. Footage
    used: set[int] = set()
    segments: list[Path] = []
    cut_times: list[float] = []
    shot = 0
    for i, (scene, v) in enumerate(zip(script.scenes, voiced)):
        progress(f"Video: {i + 1}/{len(script.scenes)} ({scene.visual_query})", 0.3 + 0.5 * i / len(script.scenes))
        n_shots = max(1, math.ceil(v.duration / MAX_SHOT))
        lengths = [v.duration / n_shots] * n_shots
        clips = []
        if not offline and config.PEXELS_API_KEY:
            clips = visuals.find_clips(scene.visual_query, n_shots, used)
            if len(clips) < n_shots:  # broaden: drop the first word of the query
                broader = " ".join(scene.visual_query.split()[1:]) or scene.visual_query
                clips += visuals.find_clips(broader, n_shots - len(clips), used)
        start = scene_starts[i]
        for k, length in enumerate(lengths):
            cut_times.append(start)
            out = work / f"shot_{shot:03d}.mp4"
            if k < len(clips):
                vid_id, url, src_dur = clips[k]
                src = visuals.download(url, work / f"src_{vid_id}.mp4")
                render.clip_segment(src, src_dur, length, out, zoom_in=shot % 2 == 0)
            elif clips:  # reuse this scene's footage rather than dropping to a plain background
                vid_id, url, src_dur = random.choice(clips)
                render.clip_segment(work / f"src_{vid_id}.mp4", src_dur, length, out, zoom_in=shot % 2 == 0)
            else:
                render.gradient_segment(length, out, shot)
            segments.append(out)
            start += length
            shot += 1
    base = render.concat(segments, work / "base.mp4")

    # 4. Captions + final mix
    progress("Montaj: subtitr, effektlar, musiqa", 0.85)
    ass = work / "captions.ass"
    ass.write_text(captions.build_ass(words, titles, total), encoding="utf-8")
    tracks = sorted(p for p in config.MUSIC_DIR.glob("*") if p.suffix.lower() in {".mp3", ".wav", ".m4a", ".ogg"})
    track = random.choice(tracks) if music and tracks else None
    final = render.finish(base, voice_track, ass, cut_times, total, work / "final.mp4", track)

    video = job / "video.mp4"
    final.replace(video)
    run(["ffmpeg", "-y", "-ss", "0.6", "-i", str(video), "-frames:v", "1", "-q:v", "3", str(job / "cover.jpg")])
    meta = {
        "title": script.title,
        "description": script.description + "\n\n" + " ".join("#" + h.lstrip("#") for h in script.hashtags),
        "pinned_comment": script.pinned_comment,
        "duration": round(total, 1),
        "music": track.name if track else None,
    }
    (job / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    shutil.rmtree(work, ignore_errors=True)  # downloaded clips and temp renders can be hundreds of MB
    progress("Tayyor!", 1.0)
    return video

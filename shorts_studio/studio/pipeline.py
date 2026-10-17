"""End-to-end: script -> voice -> visuals (host / drawings / footage, match-checked) -> captions/graphics
-> sound design -> final 9:16 video."""

import json
import math
import random
import re
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path
from typing import Callable

from . import captions, config, graphics, illustrate, mascot, render, sfx, visuals
from .ffmpeg import probe_duration, run
from .script import Scene, ShortScript
from .voice import Word, silent_scene, voice_scene

Progress = Callable[[str, float], None]

MAX_SHOT = 2.8  # seconds; longer stock scenes get split into several shots so the picture keeps changing
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


def plan_visuals(scenes: list[Scene], mode: str, host: bool, offline: bool) -> list[str]:
    """Decide per scene: "mascot", "illustration", "stock" or "gradient" (nothing available)."""
    can_draw = bool(config.OPENAI_API_KEY) and not offline
    can_film = visuals.available() and not offline
    kinds = []
    for s in scenes:
        if s.visual_type == "mascot" and host and s.graphic_type == "none":
            kinds.append("mascot")
            continue
        want = {"illustration": "illustration", "stock": "stock"}.get(mode, s.visual_type)
        if want == "mascot":  # host turned off: show the sentence instead
            want = "illustration"
        if want == "illustration" and not can_draw:
            want = "stock"
        if want == "stock" and not can_film:
            want = "illustration" if can_draw else "gradient"
        kinds.append(want)
    return kinds


def _draw_prompt(scene: Scene) -> str:
    return scene.image_prompt or f"A picture that clearly shows: {scene.narration}"


def _try_draw(prompt: str) -> Path | None:
    try:
        return illustrate.draw(prompt)
    except Exception as e:  # one failed drawing shouldn't sink the whole video
        print(f"illustration failed: {e}")
        return None


def _try_review(items: list[tuple[int, str, Path]]) -> dict:
    try:
        return illustrate.review(items)
    except Exception as e:
        print(f"match review failed: {e}")
        return {}


def choose_visuals(scenes: list[Scene], durations: list[float], visual_mode: str, host: bool, offline: bool,
                   progress: Progress) -> dict:
    """Decide host / drawing / footage per scene and make sure each picture matches its line.
    Returns a JSON-able plan that a second (A/B) render can reuse without paying for it again."""
    kinds = plan_visuals(scenes, visual_mode, host, offline)
    shots = [1 if k != "stock" or s.graphic_type != "none" else max(1, math.ceil(d / MAX_SHOT))
             for k, s, d in zip(kinds, scenes, durations)]
    scores: list[int | None] = [None] * len(scenes)
    issues: list[str] = [""] * len(scenes)
    clips: list[list[visuals.Candidate]] = [[] for _ in scenes]
    drawings: dict[int, Path] = {}

    stock_idx = [i for i, k in enumerate(kinds) if k == "stock"]
    if stock_idx:
        used: set[int] = set()
        pool = []
        for n, i in enumerate(stock_idx):
            progress(f"Video qidirilmoqda: {n + 1}/{len(stock_idx)} ({scenes[i].visual_query})",
                     0.2 + 0.12 * n / len(stock_idx))
            try:
                cands = visuals.candidates_for(scenes[i].visual_query, min(shots[i] + 3, 6), used)
            except Exception as e:  # bad key or stock site down: the scene falls back to a drawing / background
                cands = []
                issues[i] = f"Stok video: {e}"[:200]
            used |= {c.id for c in cands}
            pool.append((scenes[i].narration, shots[i], cands))
        progress("Claude stok videolarni ko'rib, eng moslarini tanlayapti...", 0.33)
        picked, picked_scores = visuals.choose(pool)
        for i, chosen, score in zip(stock_idx, picked, picked_scores):
            clips[i], scores[i] = chosen, score
            no_match = not chosen or (score is not None and score < config.MATCH_THRESHOLD)
            if no_match and config.OPENAI_API_KEY and not offline:
                kinds[i] = "illustration"  # stock can't show this line well enough: draw it instead
                shots[i] = 1
            elif not chosen:
                kinds[i] = "gradient"

    draw_idx = [i for i, k in enumerate(kinds) if k == "illustration"]
    if draw_idx:
        progress(f"AI chizmalar chizilmoqda ({len(draw_idx)} ta)...", 0.38)
        prompts = {i: _draw_prompt(scenes[i]) for i in draw_idx}
        with ThreadPoolExecutor(max_workers=4) as pool_ex:
            for i, path in zip(draw_idx, pool_ex.map(
                    lambda i: _try_draw(prompts[i]), draw_idx)):
                if path:
                    drawings[i] = path
                else:
                    kinds[i] = "stock" if clips[i] else "gradient"
                    scores[i] = None if not clips[i] else scores[i]
        draw_idx = [i for i in draw_idx if i in drawings]
        progress("Claude chizmalarni matnga mosligini tekshiryapti...", 0.5)
        review = _try_review([(i + 1, scenes[i].narration, drawings[i]) for i in draw_idx]) if draw_idx else {}
        weak = [i for i in draw_idx if review.get(i + 1) and review[i + 1].score < config.MATCH_THRESHOLD]
        for i in draw_idx:
            if review.get(i + 1):
                scores[i], issues[i] = review[i + 1].score, review[i + 1].issue
        if weak:
            progress(f"{len(weak)} ta chizma {config.MATCH_THRESHOLD}% dan past, qayta chizilmoqda...", 0.55)
            with ThreadPoolExecutor(max_workers=4) as pool_ex:
                redrawn = dict(zip(weak, pool_ex.map(
                    lambda i: _try_draw(review[i + 1].better_prompt), weak)))
            redrawn = {i: p for i, p in redrawn.items() if p}
            second = _try_review([(i + 1, scenes[i].narration, p) for i, p in redrawn.items()]) if redrawn else {}
            for i in redrawn:
                if second.get(i + 1) and second[i + 1].score > (scores[i] or 0):  # keep the better version
                    drawings[i], scores[i], issues[i] = redrawn[i], second[i + 1].score, second[i + 1].issue

    return {
        "kinds": kinds,
        "clips": [[asdict(c) for c in cs] for cs in clips],
        "drawings": {str(i): str(p) for i, p in drawings.items()},
        "scores": scores,
        "issues": issues,
    }

def hook_variant(script: ShortScript) -> ShortScript | None:
    """Same video with the runner-up hook, for A/B testing. None if there's no different hook."""
    current = script.scenes[0].narration.strip().lower()
    alt = next((h for h in script.hook_candidates if h.strip().lower() != current), None)
    if not alt:
        return None
    variant = script.model_copy(deep=True)
    variant.scenes[0].narration = alt
    variant.scenes[0].emphasis = []
    return variant


def make_video(
    script: ShortScript,
    job: Path,
    voice: str = config.DEFAULT_EDGE_VOICE,
    rate: str = "+12%",
    music: bool = True,
    series: str = "",
    visual_mode: str = "mixed",
    host: bool = True,
    offline: bool = False,
    progress: Progress = lambda step, pct: None,
    plan: dict | None = None,
    variant: str = "a",
) -> Path:
    """Render one video into `job`. Variant "b" writes video_b.mp4 / meta_b.json and should get the
    plan of variant "a" so it reuses the same pictures."""
    suffix = "" if variant == "a" else f"_{variant}"
    (job / f"script{suffix}.json").write_text(script.model_dump_json(indent=2))
    work = job / f"work{suffix}"
    work.mkdir(exist_ok=True)
    scenes = script.scenes

    # 1. Voice, scene by scene
    voiced = []
    for i, scene in enumerate(scenes):
        progress(f"Ovoz: {i + 1}/{len(scenes)}", 0.03 + 0.15 * i / len(scenes))
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
    scene_ranges = [(s, s + v.duration) for s, v in zip(scene_starts, voiced)]

    # 3. Visuals: decide host / drawing / footage per scene, then make sure each one matches its line
    if plan is None:
        plan = choose_visuals(scenes, [v.duration for v in voiced], visual_mode, host, offline, progress)
        (job / "plan.json").write_text(json.dumps(plan, indent=2))
    kinds, scores, issues = list(plan["kinds"]), plan["scores"], plan["issues"]
    clips = [[visuals.Candidate(**c) for c in cs] for cs in plan["clips"]]
    drawings = {int(i): Path(p) for i, p in plan["drawings"].items()}
    shots = [1 if k != "stock" or s.graphic_type != "none" else max(1, math.ceil(v.duration / MAX_SHOT))
             for k, s, v in zip(kinds, scenes, voiced)]

    host_ranges = [scene_ranges[i] for i, k in enumerate(kinds) if k == "mascot"]
    # twist scenes always look surprised, whatever the script says
    emotions = [(a, b, "surprised" if s.beat == "twist" else s.host_emotion)
                for (a, b), s in zip(scene_ranges, scenes)]

    segments: list[Path] = []
    shot = 0
    for i, (scene, v) in enumerate(zip(scenes, voiced)):
        progress(f"Montaj: sahna {i + 1}/{len(scenes)}", 0.6 + 0.22 * i / len(scenes))
        start = scene_starts[i]
        dim = scene.graphic_type != "none"
        punch = 0.18 if scene.beat == "twist" else 0.10
        for k in range(shots[i]):
            length = v.duration / shots[i]
            if start > 0.3:
                sfx_events.append((sfx.get("whoosh", work), start - 0.25, 0.32))
            out = work / f"shot_{shot:03d}.mp4"
            if kinds[i] == "stock":
                c = clips[i][k] if k < len(clips[i]) else random.choice(clips[i])
                src = visuals.download(c)
                move = "push_in" if shot % 2 == 0 else "pull_out"
                render.clip_segment(src, c.duration, length, out, move, punch, dim)
            elif kinds[i] == "illustration":
                move = "push_in" if dim else render.MOVES[i % len(render.MOVES)]
                render.image_segment(drawings[i], length, out, move, punch, dim)
            elif kinds[i] == "mascot":
                render.gradient_segment(length, out, shot, punch, colors=render.MASCOT_BACKDROP)
            else:
                render.gradient_segment(length, out, shot, punch)
            segments.append(out)
            start += length
            shot += 1
    base = render.concat(segments, work / "base.mp4")

    # 4. Host, captions + final mix
    progress("Yakuniy render: maskot, subtitr, grafika, effektlar, musiqa", 0.85)
    host_track = mascot.build(voice_track, emotions, work) if host else None
    ass = work / "captions.ass"
    ass.write_text(captions.build_ass(words, titles, total, extra, series, host_ranges, badge=host), encoding="utf-8")
    track = pick_music(script.mood) if music else None
    final = render.finish(base, voice_track, ass, sfx_events, total, work / "final.mp4", track,
                          host_track, host_ranges)

    video = job / f"video{suffix}.mp4"
    final.replace(video)
    run(["ffmpeg", "-y", "-ss", "0.6", "-i", str(video), "-frames:v", "1", "-q:v", "3",
         str(job / f"cover{suffix}.jpg")])

    match = [
        {"scene": i + 1, "visual": kinds[i], "score": scores[i], "issue": issues[i]}
        for i in range(len(scenes))
    ]
    scored = [m["score"] for m in match if m["score"] is not None]
    title = f"{series}: {script.title}" if series else script.title
    meta = {
        "title": title,
        "description": script.description + "\n\n" + " ".join("#" + h.lstrip("#") for h in script.hashtags),
        "pinned_comment": script.pinned_comment,
        "duration": round(total, 1),
        "mood": script.mood,
        "music": track.name if track else None,
        "match_average": round(sum(scored) / len(scored)) if scored else None,
        "match": match,
        "hook": script.scenes[0].narration,
        "topic": script.topic,
        "variant": variant,
    }
    (job / f"meta{suffix}.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    shutil.rmtree(work, ignore_errors=True)  # downloaded clips and temp renders can be hundreds of MB
    progress("Tayyor!", 1.0)
    return video

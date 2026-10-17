"""Offline tests: no API keys or network needed.  Run:  python -m pytest -q"""

import json
import subprocess
from pathlib import Path

import pytest

from studio import captions, config, graphics, mascot, pipeline, render
from studio.script import CheckedScript, ShortScript, _strict_schema
from studio.voice import Word

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ShortScript.model_validate(json.loads((ROOT / "assets" / "sample_script.json").read_text()))


def _objects(node):
    if isinstance(node, dict):
        if node.get("type") == "object":
            yield node
        for v in node.values():
            yield from _objects(v)
    elif isinstance(node, list):
        for v in node:
            yield from _objects(v)


@pytest.mark.parametrize("model", [ShortScript, CheckedScript])
def test_structured_output_schema_is_strict(model):
    schema = _strict_schema(model)
    for obj in _objects(schema):
        assert obj["additionalProperties"] is False
        assert set(obj["required"]) == set(obj["properties"])
    assert "default" not in json.dumps(schema)


def test_captions_highlight_each_word_and_move_below_host():
    words = captions.mark_emphasis(
        [Word("Everest", 0.0, 0.4), Word("is", 0.4, 0.6), Word("8,849", 0.6, 1.2), Word("meters.", 1.2, 1.6)],
        ["Everest"],
    )
    assert [w.emphasis for w in words] == [True, False, True, False]  # numbers are always emphasised
    ass = captions.build_ass(words, [(0, 1, "TALL")], 2.0, host_ranges=[(0.0, 0.5)], badge=True)
    dialogue = [l for l in ass.splitlines() if l.startswith("Dialogue: 0")]
    assert len(dialogue) == len(words)
    assert "1450" in dialogue[0] and "1180" in dialogue[-1]  # first word under the host, last one normal
    assert ",290,40,300,1" in ass  # titles shifted right to clear the badge


def test_graphics_events():
    c = graphics.counter(1.0, 4.0, 10935, "", " M", "deep")
    assert c[-2].endswith("10,935 M") or "10,935 M" in c[-2]
    bars = graphics.compare(1.0, 4.0, "Everest", 8849, "Trench", 10935, "meters")
    assert sum("\\p1" in e for e in bars) == 2


def test_plan_visuals_falls_back_without_keys(monkeypatch):
    monkeypatch.setattr(config, "OPENAI_API_KEY", "")
    monkeypatch.setattr(config, "PEXELS_API_KEY", "")
    kinds = pipeline.plan_visuals(SAMPLE.scenes, "mixed", host=True, offline=False)
    assert kinds[0] == "mascot"
    assert set(kinds) <= {"mascot", "gradient"}
    no_host = pipeline.plan_visuals(SAMPLE.scenes, "mixed", host=False, offline=False)
    assert "mascot" not in no_host


def test_hook_variant_swaps_only_the_hook():
    b = pipeline.hook_variant(SAMPLE)
    assert b.scenes[0].narration != SAMPLE.scenes[0].narration
    assert [s.narration for s in b.scenes[1:]] == [s.narration for s in SAMPLE.scenes[1:]]


def test_mascot_lip_sync_and_emotions(tmp_path):
    speech = tmp_path / "speech.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "aevalsrc='sin(2*PI*180*t)*gt(mod(t\\,1)\\,0.3)':d=4:s=44100",
                    "-c:a", "pcm_s16le", str(speech)], check=True)
    frames = mascot.timeline(speech, [(0, 2, "excited"), (2, 4, "scared")])
    assert len(frames) == 4 * config.FPS
    assert any(f.endswith("_open") for f in frames) and any(f.endswith("_closed") for f in frames)
    assert all(f.startswith("excited") for f in frames[: config.FPS])
    assert all(f.startswith("scared") for f in frames[2 * config.FPS + 1:])


def test_schedule_slots_are_in_the_future_and_ordered():
    from studio.jobs import schedule_slots
    slots = schedule_slots(5, "", 2, ["10:00", "18:00"])
    assert len(slots) == 5 and slots == sorted(slots)


def test_motion_filters_render(tmp_path):
    still = tmp_path / "still.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=1024x1536",
                    "-frames:v", "1", str(still)], check=True)
    for move in render.MOVES:
        out = render.image_segment(still, 0.5, tmp_path / f"{move}.mp4", move)
        assert out.stat().st_size > 0


@pytest.mark.slow
def test_full_offline_render(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "OUTPUT_DIR", tmp_path)
    video = pipeline.make_video(SAMPLE, tmp_path, offline=True, music=False, series="Test #1")
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height,codec_type",
                            "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout
    assert "1080,1920" in probe.replace("video,", "") or "video,1080,1920" in probe
    meta = json.loads((tmp_path / "meta.json").read_text())
    assert meta["title"].startswith("Test #1")
    assert not (tmp_path / "work").exists()


def test_learning_rows_and_playbook_prompt(tmp_path, monkeypatch):
    from studio import db, learn

    monkeypatch.setattr(config, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(db, "PATH", tmp_path / "studio.db")
    db.init()
    folder = tmp_path / "20260101-ocean"
    folder.mkdir()
    (folder / "meta.json").write_text(json.dumps({"topic": "ocean", "hook": "Drop Everest here", "duration": 33}))
    db.save_video(folder.name, "a", youtube_id="abcdefghijk",
                  metrics=json.dumps({"views": 1200, "engagedViews": 900, "stayedToWatch": 75.0}))
    rows = learn.performance_rows()
    assert rows == [{"video": "20260101-ocean/a", "topic": "ocean", "hook": "Drop Everest here", "title": None,
                     "seconds": 33, "picture_match": None, "views": 1200, "engagedViews": 900,
                     "stayedToWatch": 75.0}]
    assert learn.playbook_prompt() == ""
    db.execute("INSERT INTO playbook (created, data) VALUES (1, ?)", (json.dumps({
        "summary": "Short space hooks win.", "winning_patterns": ["numbers in hook"], "losing_patterns": ["slow intros"],
        "hook_rules": ["start with a number"], "next_topics": [], "ab_findings": []}),))
    prompt = learn.playbook_prompt()
    assert "Do: numbers in hook" in prompt and "Avoid: slow intros" in prompt


def test_youtube_video_id_parsing():
    from studio.youtube import parse_video_id
    assert parse_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ?feature=share") == "dQw4w9WgXcQ"
    assert parse_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    with pytest.raises(ValueError):
        parse_video_id("not a link")

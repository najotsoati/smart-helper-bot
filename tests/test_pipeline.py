import json
import sys
import types
from pathlib import Path

from studio import blender_script, checker
from studio.storyboard import normalize, timeline, total_seconds, to_table

SAMPLE = json.loads((Path(__file__).parent / "sample_storyboard.json").read_text())


class Rec:
    """Stands in for stickman_tools.py: records every call."""

    def __init__(self):
        self.calls, self.POSES = [], {}

    def __getattr__(self, name):
        def f(*a, **k):
            self.calls.append((name, a, k))
            if name in ("say", "phone_say"):
                return a[1] + 30
            if name in ("caption", "music", "sfx"):
                return types.SimpleNamespace(volume=1.0, keyframe_insert=lambda *a, **k: None)
            if name == "_strips":
                return []
        return f


def fake_blender(st):
    obj = types.SimpleNamespace(location=types.SimpleNamespace(y=0), keyframe_insert=lambda *a, **k: None)
    scene = types.SimpleNamespace(frame_end=0, render=types.SimpleNamespace(filepath=""), frame_set=lambda f: None)
    bpy = types.SimpleNamespace(
        data=types.SimpleNamespace(texts={"stickman_tools.py": types.SimpleNamespace(as_module=lambda: st)},
                                   objects={"Set_Blanket": obj,
                                            "Bill_1_Label": types.SimpleNamespace(data=types.SimpleNamespace(body=""))}),
        context=types.SimpleNamespace(scene=scene),
        path=types.SimpleNamespace(abspath=lambda p: p),
        app=types.SimpleNamespace(driver_namespace={}))
    aud = types.SimpleNamespace(Sound=types.SimpleNamespace(
        file=lambda p: types.SimpleNamespace(length=44100, specs=(44100, 1))))
    sys.modules["bpy"], sys.modules["aud"] = bpy, aud
    return bpy


def run_script(sb):
    st = Rec()
    bpy = fake_blender(st)
    src = blender_script.generate(sb, audio_dir="studio_audio/abc")
    exec(compile(src, "video_test.py", "exec"), {"__name__": "__main__"})
    return st, bpy, src


def test_sample_passes_checker():
    sb = normalize(SAMPLE)
    res = checker.check(sb)
    assert res["errors"] == [], res
    assert 15 < res["seconds"] < 30


def test_timeline_stretches_for_lines():
    sb = normalize(SAMPLE)
    for ln in sb["lines"]:
        ln["seconds"] = 3.0
    tl = timeline(sb)
    first = tl[0]
    assert first["line_start"] == 1 + 3
    assert first["end"] == first["line_end"] + 6
    assert tl[1]["start"] == first["end"]
    assert total_seconds(sb) > 20
    assert "open_zoom" in to_table(sb)


def test_generated_script_runs_and_uses_tools():
    st, bpy, src = run_script(SAMPLE)
    names = [c[0] for c in st.calls]
    assert names[0] == "clear_animation"
    # the title comes before the first camera call
    assert names.index("title") < names.index("cut")
    assert names.count("cut") == len(SAMPLE["shots"])
    assert "bounce" in names and "flat" in names and "phone_on" in names and "music" in names
    assert bpy.context.scene.render.filepath == "//My Salary Lasted 5 Minutes.mp4"
    marks = bpy.app.driver_namespace["studio_marks"]
    assert marks["end"] == bpy.context.scene.frame_end > 300
    assert marks["starts"] == sorted(marks["starts"])
    # after the fall Sticky gets up before the next standing shot
    i_flat = [i for i, n in enumerate(names) if n == "flat"]
    assert len(i_flat) == 2


def test_checker_catches_bad_words():
    bad = normalize({"title": "X", "lines": [{"id": "S01", "speaker": "sticky", "text": "hi"}],
                     "shots": [{"camera": "drone", "pose": "dance", "line": "S09", "sfx": ["boing"]}]})
    errs = " ".join(checker.check(bad)["errors"])
    for word in ("drone", "dance", "S09", "boing"):
        assert word in errs


def test_checker_flags_too_long():
    sb = normalize({"title": "X", "lines": [],
                    "shots": [{"camera": "wide", "seconds": 4.0, "action": "walk"} for _ in range(16)]})
    assert any("under" in e for e in checker.check(sb)["errors"])


def test_safe_video_name():
    sb = normalize({"title": "a", "video_name": 'Is This "Rich"? 💸 / no', "shots": []})
    assert sb["video_name"] == "Is This Rich no"

from studio import editor, vocab
from studio.storyboard import normalize

from .test_pipeline import SAMPLE, run_script


def boring():
    lines = [{"id": "S01", "speaker": "sticky", "text": "word " * 14, "seconds": 5.0},
             {"id": "S02", "speaker": "sticky", "text": "ok", "seconds": 0.8}]
    shots = [{"camera": "medium", "seconds": 2.0, "line": "S01"},
             {"camera": "medium", "seconds": 2.0, "line": "S02"},
             {"camera": "medium", "seconds": 2.0}, {"camera": "wide", "seconds": 2.0},
             {"camera": "face", "seconds": 2.0}]
    return {"title": "BORING", "hook_text": "NOBODY TELLS YOU THIS", "music": "sneaky",
            "lines": lines, "shots": shots}


def test_hook_is_forced():
    sb = editor.polish(boring())
    h = sb["shots"][0]
    assert h["camera"] == "open_zoom" and h["action"] == "punch"
    assert h["caption"]["text"] == "NOBODY TELLS YOU THIS"
    assert h["sfx"][0]["name"] == "whoosh" and h["seconds"] <= 1.8


def test_no_repeat_cameras_and_music_stop():
    sb = editor.polish(boring())
    cams = [s["camera"] for s in sb["shots"]]
    assert all(a != b for a, b in zip(cams, cams[1:]))
    assert sum(1 for s in sb["shots"] if s.get("music_stop")) == 1


def test_long_shot_gets_extra_cuts():
    sb = editor.polish(boring())
    assert sb["shots"][0]["coverage"] == []          # the opener zooms on its own
    long_one = normalize(boring())
    long_one["shots"][0]["camera"] = "room_push"
    sb = editor.polish(long_one)
    assert sb["shots"][0]["coverage"], "a 5 s shot must be cut"
    assert sb["shots"][2]["coverage"] == []          # 2 s shots stay as they are


def test_music_rotates():
    name, (f, _) = editor.pick_music("sneaky", ["musiqa_03_sneaky.wav"])
    assert f != "musiqa_03_sneaky.wav"
    name, (f, _) = editor.pick_music("sneaky", ["musiqa_01.wav", "musiqa_02_epic.wav"])
    assert f == "musiqa_03_sneaky.wav"
    pool = editor.music_pool({"music": ["musiqa_09_funk.wav"]})
    assert pool["musiqa_09_funk"] == ("musiqa_09_funk.wav", 0.12)
    hist = [v[0] for k, v in vocab.MUSIC.items() if v[0]]
    name, (f, _) = editor.pick_music(None, hist, {"music": ["musiqa_09_funk.wav"]})
    assert f == "musiqa_09_funk.wav"                 # never used yet


def test_polished_script_runs_with_new_actions():
    sb = normalize(SAMPLE)
    for ln in sb["lines"]:
        ln["seconds"] = 3.2
    sb["shots"][1]["action"] = "bills_chase"
    sb["shots"][1]["label"] = "rent"
    sb["shots"][3]["action"] = "money_fly"
    sb["shots"][4]["action"] = "knock"
    sb["shots"][6]["action"] = "fly_buzz"
    sb["shots"][2]["seconds"] = 4.0
    sb = editor.polish(sb, history=["musiqa_03_sneaky.wav"])
    st, bpy, src = run_script(sb)
    names = [c[0] for c in st.calls]
    assert names.count("cut") > len(sb["shots"])      # automatic extra cuts happened
    assert "run" in names and "flutter" in names
    assert bpy.data.objects["Bill_1_Label"].data.body == "RENT"
    assert 'st.music("//musiqa_03_sneaky.wav"' not in src


def _sb(**kw):
    sb = {"title": "T", "hook_text": "HOOK", "music": "sneaky",
          "lines": [{"id": "S01", "speaker": "sticky", "text": "hi", "seconds": 1.0}],
          "shots": [{"camera": "medium", "seconds": 2.0, "line": "S01"}, {"camera": "wide", "seconds": 2.0},
                    {"camera": "face", "seconds": 2.0, "action": "fall_flat"}, {"camera": "floor", "seconds": 2.0},
                    {"camera": "medium", "seconds": 2.0, "action": "knock"}, {"camera": "face", "seconds": 2.0}]}
    sb.update(kw)
    return sb


def test_hook_styles():
    sb = editor.polish(_sb(hook_style="number"))
    assert sb["shots"][0]["camera"] == "crash_zoom" and sb["shots"][0]["caption"]["pos"] == "big"
    sb = editor.polish(_sb(hook_style="vs", cast=["rick"]))
    assert sb["shots"][0]["camera"] == "two_shot" and sb["shots"][0]["labels"] == ["POOR", "RICH"]
    sb = editor.polish(_sb(hook_style="pov"))
    assert sb["shots"][0]["caption"]["text"].startswith("POV: ")
    sb = editor.polish(_sb(hook_style="question"))
    assert sb["shots"][0]["caption"]["text"].endswith("?") and sb["end_text"]
    n = len(_sb()["shots"])
    sb = editor.polish(_sb(hook_style="flash_forward"))
    assert len(sb["shots"]) == n + 1
    assert sb["shots"][0]["caption"]["text"] == "HOW DID THIS HAPPEN?"
    assert sb["shots"][1]["sfx"][0]["name"] == "rewind"


def test_set_fitting():
    sb = editor.polish(_sb(set="kitchen"))
    assert all(s.get("action") != "knock" for s in sb["shots"])
    sb = editor.polish(_sb(shots=[{"camera": "rick_face", "seconds": 2.0}, {"camera": "two_shot", "seconds": 2.0},
                                  {"camera": "face", "seconds": 2.0, "action": "dino_roar"}]))
    cams = [s["camera"] for s in sb["shots"]]
    assert "rick_face" not in cams and "two_shot" not in cams
    assert sb["shots"][2]["action"] == "shiver"


def test_new_sets_and_rick_render():
    for set_name in vocab.SETS:
        sb = editor.polish(_sb(set=set_name, hook_style="vs", cast=["rick"]))
        sb["shots"][1]["rick"] = {"pose": "cheer", "action": "tip_hat", "eyes": "money"}
        st, bpy, src = run_script(sb)
        names = [c[0] for c in st.calls]
        assert "use" in names and "tip_hat" in names, set_name
        for name in vocab.SET_INFO[set_name]["on"]:
            assert f"on({name!r}, 1)" in src or f'on("{name}", 1)' in src, (set_name, name)
    town = editor.polish(_sb(set="town"))
    st, bpy, src = run_script(town)
    assert "B = 132.05" in src and "X = 132.1" in src


def test_set_rotation():
    assert editor.pick_set("kitchen", ["none", "bed"]) == "kitchen"
    new = editor.pick_set("none", ["town", "none"])
    assert new not in ("none", "town")
    hist = list(vocab.SET_INFO)
    assert editor.pick_set("none", hist) == hist[0] or editor.pick_set("none", hist) != "none"
    sb = editor.polish(_sb(set="none"), set_history=["kitchen", "none"])
    assert sb["set"] not in ("none", "kitchen")
    sb = editor.polish(_sb(set="none"), set_history=None)          # own script: keep it
    assert sb["set"] == "none"


def test_phone_only_when_story_needs_it():
    sb = normalize(_sb())
    assert sb["holds_phone"] is False
    st, bpy, src = run_script(sb)
    assert "st.apply_pose('stand', 1" in src and "hand_phone(1," not in src
    sb = normalize(_sb(shots=[{"camera": "phone_screen", "seconds": 2.0}]))
    assert sb["holds_phone"] is True


def test_auto_acting_and_new_actions_render():
    sb = _sb(shots=[{"camera": "face", "seconds": 2.0, "mouth": "scream"},
                    {"camera": "medium", "seconds": 2.0, "mouth": "scream"},
                    {"camera": "medium_wide", "seconds": 2.0, "mouth": "sad"},
                    {"camera": "medium", "seconds": 2.0, "action": "facepalm"},
                    {"camera": "face", "seconds": 2.0},
                    {"camera": "wide", "seconds": 2.5, "action": "dance"},
                    {"camera": "medium", "seconds": 2.0, "action": "count_money"},
                    {"camera": "face", "seconds": 2.0, "action": "tired"},
                    {"camera": "medium", "seconds": 2.0, "action": "head_shake"},
                    {"camera": "wide", "seconds": 2.0, "action": "strut"},
                    {"camera": "medium", "seconds": 2.0, "action": "flex"},
                    {"camera": "face", "seconds": 2.0, "action": "panic"}])
    sb = editor.polish(sb)
    poses = [s.get("pose") for s in sb["shots"][:3]]
    assert poses[0] and poses[1] and poses[0] != poses[1]
    assert poses[2] in vocab.ACTING["sad"]
    st, bpy, src = run_script(sb)
    names = [c[0] for c in st.calls]
    applied = {c[1][0] for c in st.calls if c[0] == "apply_pose"}
    assert {"panic", "count_a", "count_b", "head_l", "head_r", "cheer"} <= applied
    assert "walk" in names and "hop" in names
    i_face = src.index("st.snap('facepalm'")
    assert "st.squint(c0, 1.0)" in src[i_face:]          # eyes open again after the facepalm
    assert all(k in st.POSES for k in vocab.CUSTOM_POSES)   # every new pose is registered in the script


def test_every_library_action_and_pose_renders():
    from studio import blender_script, library
    acts = list(library.ACTION_LIB)
    poses = list(library.POSE_LIB)
    for chunk in range(0, len(acts), 20):
        shots = [{"camera": "medium_wide", "seconds": 2.0, "action": a} for a in acts[chunk:chunk + 20]]
        st, bpy, src = run_script(normalize({"title": "A", "set": "town", "lines": [], "shots": shots}))
        assert src.count("act(c0, e, [(") == len(shots)
    shots = [{"camera": "medium", "seconds": 1.0, "pose": p} for p in poses]
    st, bpy, src = run_script(normalize({"title": "P", "lines": [], "shots": shots}))
    snapped = {c[1][0] for c in st.calls if c[0] == "snap"}
    assert set(poses) - {poses[0]} <= snapped | {"stand"}
    assert len(library.POSE_LIB) >= 100 and len(library.ACTION_LIB) >= 100

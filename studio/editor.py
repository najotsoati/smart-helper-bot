"""The editor: code that makes every storyboard hold attention, whatever model wrote it.

Runs after the director.  It never touches the spoken lines, only the cutting:
- shot 1 is a real hook (moving camera, text hook, sound, a hit, the line at once);
- no camera repeats back to back;
- long shots get automatic extra cuts every ~1.7 s (the Blender script places them);
- a music stop on the twist when the director forgot one;
- the music rotates, so the same track does not play video after video.
"""

from . import vocab
from .storyboard import normalize, timeline

MOVING_OPENERS = ("open_zoom", "crash_zoom", "room_push", "phone_push", "two_shot")
ROOM_CAMS = ["medium", "face", "medium_wide", "wide"]
NO_COVERAGE = {"floor", "end_card", "extreme_closeup", "crash_zoom", "open_zoom", "two_shot"}


def music_pool(assets=None):
    """name -> (file, volume): the template's tracks plus any musiqa_*.wav the laptop reported."""
    pool = {k: v for k, v in vocab.MUSIC.items() if v[0]}
    for f in (assets or {}).get("music", []):
        name = f.rsplit(".", 1)[0]
        if not any(v[0] == f for v in pool.values()):
            pool[name] = (f, 0.12)
    return pool


def pick_music(wanted, history, assets=None):
    pool = music_pool(assets)
    recent = list(history or [])[-2:]
    if wanted in pool and pool[wanted][0] not in recent:
        return wanted, pool[wanted]
    used_at = {f: i for i, f in enumerate(history or [])}
    name = min(pool, key=lambda n: used_at.get(pool[n][0], -1))
    return name, pool[name]


def polish(sb, history=None, assets=None):
    sb = normalize(sb)
    shots = sb["shots"]
    if not shots:
        return sb
    fit_to_set(sb)

    # 1) the hook
    h = shots[0]
    if h["camera"] not in MOVING_OPENERS:
        h["camera"] = "open_zoom"
    h["seconds"] = min(h["seconds"], 1.8)
    h["line_at"] = min(float(h.get("line_at") or 0), 0.1)
    if not (h.get("caption") or {}).get("text"):
        h["caption"] = {"text": str(sb.get("hook_text") or sb["title"]), "color": "red", "pos": "top"}
    if not any(float(s.get("at", 0)) <= 0.2 for s in h["sfx"]):
        h["sfx"].insert(0, {"name": "whoosh", "at": 0.0})
    if h.get("action", "none") == "none":
        h["action"] = "punch"
    h.setdefault("eyes", "wide")
    apply_hook_style(sb)
    shots = sb["shots"]

    # 2) no camera twice in a row (phone screens may repeat: they show new content)
    for i in range(1, len(shots)):
        prev, cur = shots[i - 1]["camera"], shots[i]["camera"]
        if cur == prev and cur not in ("phone_screen", "phone_push", "floor"):
            shots[i]["camera"] = next(c for c in ROOM_CAMS if c != prev)

    # 3) music stop on the twist
    if len(shots) >= 5 and not any(s.get("music_stop") for s in shots):
        t = shots[round(len(shots) * 0.55)]
        t["music_stop"] = True
        if not t["sfx"]:
            t["sfx"].append({"name": "boom", "at": 0.0})

    # 4) automatic extra cuts inside long shots
    lying = False
    for sh, t in zip(shots, timeline(sb)):
        if sh.get("action") == "fall_flat":
            lying = True
        elif lying and sh["camera"] not in ("floor", "phone_screen", "phone_push"):
            lying = False
        length = (t["end"] - t["start"]) / vocab.FPS
        if lying or sh["camera"] in NO_COVERAGE or length <= 2.2:
            sh["coverage"] = []
            continue
        kind = "phone" if sh["camera"] in ("phone_screen", "phone_push") else "room"
        sh["coverage"] = [c for c in vocab.COVERAGE[kind] if c != sh["camera"]] or vocab.COVERAGE[kind]

    make_loop(sb)

    # 5) music that was not used in the last two videos
    name, (f, vol) = pick_music(sb.get("music"), history, assets)
    sb["music"], sb["music_file"], sb["music_volume"] = name, f, vol
    return sb


# ---------------------------------------------------------------------------
# Hook styles that break out right now in stickman / money Shorts (vidIQ outliers, Oct 2026):
# "Rich vs Poor" comparisons, "POV:" situations, one shocking number, a question to the viewer,
# and very short looping gags.  The hook maker picks one; the editor builds its first seconds.
HOOK_STYLES = {
    "number": "one shocking number on screen, crash zoom into Sticky's face",
    "vs": "Sticky (poor) vs Rick (rich) side by side with POOR / RICH labels",
    "pov": "\"POV: ...\" a situation everyone lived through",
    "question": "a direct question to the viewer, answered only at the end",
    "flash_forward": "start with the disaster at the end, then rewind: \"HOW DID THIS HAPPEN?\"",
}


def apply_hook_style(sb):
    """Turn shot 1 into the chosen hook style.  Runs inside polish()."""
    style = sb.get("hook_style")
    shots = sb["shots"]
    h = shots[0]
    text = str(sb.get("hook_text") or sb["title"])
    if style == "number":
        h["camera"] = "crash_zoom"
        h["caption"] = {"text": text, "color": "red", "pos": "big"}
        h["sfx"] = [{"name": "boom", "at": 0.0}] + [x for x in h["sfx"] if x["name"] != "whoosh"]
        h["eyes"] = "wide"
    elif style == "vs" and "rick" in sb.get("cast", []):
        h["camera"] = "two_shot"
        h["caption"] = {"text": text, "color": "red", "pos": "top"}
        h["labels"] = ["POOR", "RICH"]
        h.setdefault("rick", {"pose": "cheer", "action": "tip_hat"})
    elif style == "pov":
        if not text.upper().startswith("POV"):
            text = "POV: " + text
        h["caption"] = {"text": text, "color": "black", "pos": "top"}
    elif style == "question":
        if not text.endswith("?"):
            text += "?"
        h["caption"] = {"text": text, "color": "red", "pos": "top"}
        if not sb.get("end_text"):
            sb["end_text"] = ["WHAT WOULD YOU DO?", "TELL ME BELOW"]
    elif style == "flash_forward" and len(shots) >= 4:
        peak = next((s for s in shots[len(shots) // 3:] if s.get("music_stop") or s.get("action") in
                     ("fall_flat", "flatten", "money_fly", "bills_chase", "coin_rain", "dino_roar")), shots[-2])
        tease = {k: v for k, v in peak.items() if k not in ("line", "coverage", "music_stop")}
        tease.update(seconds=1.4, caption={"text": "HOW DID THIS HAPPEN?", "color": "red", "pos": "top"},
                     sfx=[{"name": "boom", "at": 0.0}], props=list(peak.get("props", [])))
        h["sfx"] = [{"name": "rewind", "at": 0.0}] + [x for x in h["sfx"] if x["name"] != "whoosh"]
        h["caption"] = {"text": "EARLIER...", "color": "black", "pos": "top"}
        shots.insert(0, tease)
    return sb


def fit_to_set(sb):
    """Drop gags the chosen set cannot show (no door, no Rick, no dinosaurs)."""
    info = vocab.SET_INFO.get(sb["set"], vocab.SET_INFO["none"])
    rick = "rick" in sb.get("cast", [])
    for sh in sb["shots"]:
        if sh.get("action") in ("knock", "bills_chase") and not info["door"]:
            sh["action"] = "money_fly" if sh["action"] == "bills_chase" else "punch"
        if sh.get("action") == "dino_roar" and sb["set"] != "prehistoric":
            sh["action"] = "shiver"
        if sh["camera"] in ("two_shot", "rick_face") and not rick:
            sh["camera"] = "medium_wide"
        if not rick:
            sh.pop("rick", None)       # Rick may still speak, off screen
    return sb


def make_loop(sb):
    """Very short videos (under 20 s) end on the opening picture so the replay is seamless."""
    from .storyboard import total_seconds
    if len(sb["shots"]) >= 3 and total_seconds(sb) < 20 and sb["shots"][-1]["camera"] != "end_card":
        sb["shots"][-1]["camera"] = sb["shots"][0]["camera"] if sb["shots"][0]["camera"] not in (
            "crash_zoom", "open_zoom") else "face"
    return sb

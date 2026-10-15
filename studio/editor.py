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

MOVING_OPENERS = ("open_zoom", "crash_zoom", "room_push", "phone_push")
ROOM_CAMS = ["medium", "face", "medium_wide", "wide"]
NO_COVERAGE = {"floor", "end_card", "extreme_closeup", "crash_zoom", "open_zoom"}


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

    # 5) music that was not used in the last two videos
    name, (f, vol) = pick_music(sb.get("music"), history, assets)
    sb["music"], sb["music_file"], sb["music_volume"] = name, f, vol
    return sb

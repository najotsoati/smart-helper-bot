"""Rule checker: code, not AI.  Errors block the render, warnings are advice.

The rules come from the channel's pre-publish checklist (shorts-director-brain)
and from mistakes that already cost a render in the Blender template.
"""

from . import vocab
from .storyboard import line_map, timeline, total_seconds

FACE_CAMERAS = {"face", "face_phone_up", "extreme_closeup", "open_zoom"}
PHONE_CAMERAS = {"phone_screen", "phone_push"}
MOVING_CAMERAS = {"open_zoom", "room_push", "face", "extreme_closeup", "phone_push"}


def check(sb, extra_sfx=()):
    errors, warnings = [], []

    def need(value, allowed, what, where):
        if value is not None and value not in allowed:
            errors.append(f"{where}: unknown {what} '{value}'")

    if not sb.get("shots"):
        return {"errors": ["No shots"], "warnings": [], "seconds": 0}

    need(sb.get("set"), vocab.SETS, "set", "video")
    need(sb.get("backdrop"), vocab.BACKDROPS, "backdrop", "video")
    if not sb.get("music_file"):
        need(sb.get("music"), vocab.MUSIC, "music", "video")
    if len(sb.get("title", "")) > 46:
        errors.append("Title is longer than 46 characters (two lines of 23)")

    lines = line_map(sb)
    for ln in sb["lines"]:
        need(ln["speaker"], vocab.VOICES, "speaker", f"line {ln['id']}")
        need(ln.get("mood"), vocab.MOODS, "mood", f"line {ln['id']}")
        if not ln["text"]:
            errors.append(f"line {ln['id']}: empty text")
        elif len(ln["text"]) > 220:
            warnings.append(f"line {ln['id']}: very long line, split it")
    used = set()

    tl = timeline(sb)
    for i, (sh, t) in enumerate(zip(sb["shots"], tl), 1):
        w = f"shot {i}"
        need(sh["camera"], vocab.CAMERAS, "camera", w)
        need(sh.get("pose"), vocab.POSES, "pose", w)
        need(sh.get("eyes"), vocab.EYES, "eyes", w)
        need(sh.get("mouth"), vocab.MOUTHS, "mouth", w)
        need(sh.get("brows"), vocab.BROWS, "brows", w)
        need(sh.get("look"), vocab.LOOKS, "look", w)
        need(sh.get("action"), vocab.ACTIONS, "action", w)
        need(sh.get("fx"), vocab.FX, "fx", w)
        for p in sh["props"]:
            need(p, vocab.PROPS, "prop", w)
        for s in sh["sfx"]:
            need(s.get("name"), set(vocab.SFX) | set(extra_sfx), "sfx", w)
            if float(s.get("at", 0)) > sh["seconds"] + 2:
                warnings.append(f"{w}: sfx '{s.get('name')}' starts after the shot")
        if sh.get("line"):
            if sh["line"] not in lines:
                errors.append(f"{w}: line '{sh['line']}' does not exist")
            elif sh["line"] in used:
                errors.append(f"{w}: line '{sh['line']}' is used twice")
            used.add(sh["line"])
        cap = sh.get("caption")
        if cap:
            need(cap.get("color"), vocab.CAPTION_COLORS, "caption color", w)
            need(cap.get("pos"), vocab.CAPTION_POS, "caption pos", w)
            words = len(cap.get("text", "").split())
            if words > 7:
                warnings.append(f"{w}: caption has {words} words; keep it to 2 short lines")
            if cap.get("pos") == "big" and sh["camera"] in FACE_CAMERAS:
                warnings.append(f"{w}: a big caption over a face close-up covers the face")
        if sh.get("phone_text") and sh["camera"] not in PHONE_CAMERAS:
            warnings.append(f"{w}: phone_text only shows on a phone camera; it will be ignored")
        length = (t["end"] - t["start"]) / vocab.FPS
        if sh["seconds"] < 0.4:
            errors.append(f"{w}: shorter than 0.4 s")
        busy = (sh.get("action") in ("walk", "shiver", "tears") or sh["camera"] in MOVING_CAMERAS
                or bool(sh.get("coverage")))
        if length > 3.0 and not busy:
            warnings.append(f"{w}: {length:.1f} s without a cut or motion; something should change every 2-3 s")
        if length > 4.5 and not sh.get("coverage"):
            warnings.append(f"{w}: {length:.1f} s is a long hold; split it into two shots")

    for ln in sb["lines"]:
        if ln["id"] not in used:
            warnings.append(f"line {ln['id']} is never used in a shot")

    first = sb["shots"][0]
    if first["camera"] not in MOVING_CAMERAS and first.get("action", "none") == "none":
        warnings.append("Frame 1 is static: start with open_zoom / room_push or an action")
    if not first.get("caption") and not sb.get("title"):
        warnings.append("No text hook on screen in the first shot")
    if tl[0]["line_start"] is not None and tl[0]["line_start"] > 7:
        warnings.append("The first spoken line should start by frame 6")

    sec = total_seconds(sb)
    if sec > vocab.MAX_SECONDS:
        errors.append(f"Video is {sec:.1f} s; Shorts must stay under {vocab.MAX_SECONDS} s")
    elif sec < vocab.MIN_SECONDS:
        warnings.append(f"Video is only {sec:.1f} s")

    last_line_end = max((t["line_end"] or 0) for t in tl)
    if last_line_end and sb["shots"][-1]["camera"] != "end_card":
        tail = (tl[-1]["end"] - last_line_end) / vocab.FPS
        if tail > 1.6:
            warnings.append(f"The video runs {tail:.1f} s after the last line; end within about 1 s of the payoff")

    return {"errors": errors, "warnings": warnings, "seconds": sec}

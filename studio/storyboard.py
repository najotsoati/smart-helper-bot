"""Storyboard: the per-shot table the director writes and Blender builds.

A storyboard is a plain dict (stored as JSON):

{
  "title": "LEFT ON READ",            # on-screen title, upper case
  "video_name": "Left On Read",       # file name of the MP4 (no emoji, no \\/:*?"<>|)
  "set": "none" | "bed" | "armchair",
  "backdrop": "room",
  "music": "sneaky",
  "holds_phone": true,                # Sticky holds his phone in phone-type poses
  "lines": [{"id": "S01", "speaker": "sticky", "text": "Payday!", "file": "S01.mp3", "seconds": 0.9}],
  "shots": [{
      "camera": "open_zoom", "seconds": 2.0,
      "line": "S01", "line_at": 0.2,             # optional spoken line, starts 0.2 s into the shot
      "pose": "cheer", "eyes": "money", "mouth": "grin", "brows": "surprised", "look": "camera",
      "action": "bounce", "shake": false, "music_stop": false,
      "caption": {"text": "$1,200", "color": "gold", "pos": "big"},
      "phone_text": ["SALARY", "$1,200"],        # only on phone cameras
      "props": ["sweat"], "fx": "lines",
      "sfx": [{"name": "whoosh", "at": 0.0}]
  }],
  "end_text": ["WHO REALLY OWNS", "YOUR PHONE?"],  # optional, shown on an end_card shot
  "upload": {"title": "...", "description": "...", "hashtags": ["#shorts"]}
}

The shot length is max(seconds, end of its line + 0.2 s), exactly as the Blender
script lays shots end to end, so the timeline here matches the render.
"""

import re

from . import vocab

LINE_PAD = 6          # frames after a line before the next cut
DEFAULT_LINE_SECONDS_PER_WORD = 0.38   # estimate before the voice exists


def safe_filename(name):
    name = re.sub(r'[\\/:*?"<>|]', "", name or "").strip()
    name = re.sub(r"[^\x20-\x7E]", "", name)   # no emoji
    name = re.sub(r"\s+", " ", name).strip()
    return name[:80] or "Untitled"


def estimate_line_seconds(text):
    words = max(1, len((text or "").split()))
    return round(0.35 + words * DEFAULT_LINE_SECONDS_PER_WORD, 2)


def normalize(sb):
    """Fill defaults so later stages never meet a missing key.  Does not validate."""
    sb = dict(sb or {})
    sb.setdefault("title", "STICKY")
    sb["title"] = str(sb["title"]).upper()
    sb["video_name"] = safe_filename(sb.get("video_name") or sb["title"].title())
    sb.setdefault("set", "none")
    sb.setdefault("backdrop", "room")
    sb.setdefault("music", "sneaky")
    sb.setdefault("holds_phone", True)
    lines = []
    for i, ln in enumerate(sb.get("lines") or []):
        ln = dict(ln)
        ln.setdefault("id", f"L{i + 1:02d}")
        ln["speaker"] = str(ln.get("speaker", "sticky")).lower()
        ln["text"] = str(ln.get("text", "")).strip()
        lines.append(ln)
    sb["lines"] = lines
    shots = []
    for sh in sb.get("shots") or []:
        sh = dict(sh)
        sh.setdefault("camera", "medium")
        sh["seconds"] = float(sh.get("seconds") or 2.0)
        sh.setdefault("line_at", 0.15)
        sh.setdefault("pose", None)
        sh.setdefault("action", "none")
        sh["props"] = list(sh.get("props") or [])
        sh["sfx"] = [s if isinstance(s, dict) else {"name": s, "at": 0.0} for s in (sh.get("sfx") or [])]
        if isinstance(sh.get("caption"), str):
            sh["caption"] = {"text": sh["caption"]}
        if sh.get("caption"):
            sh["caption"] = {"text": str(sh["caption"].get("text", "")),
                             "color": sh["caption"].get("color", "black"),
                             "pos": sh["caption"].get("pos", "top")}
        shots.append(sh)
    sb["shots"] = shots
    return sb


def line_map(sb):
    return {ln["id"]: ln for ln in sb.get("lines", [])}


def line_frames(ln):
    sec = ln.get("seconds") or estimate_line_seconds(ln.get("text"))
    return int(round(sec * vocab.FPS))


def timeline(sb):
    """List of dicts {start, end, line_start, line_end} in frames, frame 1 based."""
    lines = line_map(sb)
    out, cursor = [], 1
    for sh in sb["shots"]:
        start = cursor
        end = start + int(round(sh["seconds"] * vocab.FPS))
        ls = le = None
        if sh.get("line") in lines:
            ls = start + int(round(float(sh.get("line_at") or 0) * vocab.FPS))
            le = ls + line_frames(lines[sh["line"]])
            end = max(end, le + LINE_PAD)
        out.append({"start": start, "end": end, "line_start": ls, "line_end": le})
        cursor = end
    return out


def total_seconds(sb):
    tl = timeline(sb)
    return round((tl[-1]["end"] - 1) / vocab.FPS, 2) if tl else 0.0


def to_table(sb):
    """Human readable table, one row per shot (for the panel and the AI reviewer)."""
    lines = line_map(sb)
    rows = []
    for sh, t in zip(sb["shots"], timeline(sb)):
        a, b = (t["start"] - 1) / vocab.FPS, (t["end"] - 1) / vocab.FPS
        ln = lines.get(sh.get("line"))
        said = f'{ln["speaker"]}: "{ln["text"]}"' if ln else ""
        cap = (sh.get("caption") or {}).get("text", "")
        sfx = ",".join(s["name"] for s in sh["sfx"])
        rows.append(f"{a:5.1f}-{b:5.1f}s | {sh['camera']} | {sh.get('pose') or '-'} | {sh.get('action')} | "
                    f"{said} | caption: {cap} | sfx: {sfx}")
    return "\n".join(rows)

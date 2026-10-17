"""Stock footage from Pexels (free API key: https://www.pexels.com/api/), picked by Claude's eyes."""

from dataclasses import dataclass
from pathlib import Path

import httpx
from pydantic import BaseModel, Field

from . import config

API = "https://api.pexels.com/videos/search"


@dataclass
class Candidate:
    id: int
    url: str
    duration: float
    thumb: str


def _pick_file(video: dict) -> dict | None:
    """Best mp4 rendition: portrait-friendly, at least 720p, not a giant 4K download."""
    files = [f for f in video.get("video_files", []) if f.get("file_type") == "video/mp4" and f.get("height")]
    good = [f for f in files if 1280 <= max(f["width"], f["height"]) <= 2560]
    if not good:
        good = files
    if not good:
        return None
    return min(good, key=lambda f: (f["width"] > f["height"], abs(max(f["width"], f["height"]) - 1920)))


def search(query: str, limit: int, exclude: set[int]) -> list[Candidate]:
    results: list[Candidate] = []
    seen = set(exclude)
    for orientation in ("portrait", None):
        params = {"query": query, "per_page": 15, "size": "medium"}
        if orientation:
            params["orientation"] = orientation
        r = httpx.get(API, params=params, headers={"Authorization": config.PEXELS_API_KEY}, timeout=30)
        r.raise_for_status()
        for video in r.json().get("videos", []):
            if video["id"] in seen or video.get("duration", 0) < 3 or not video.get("image"):
                continue
            f = _pick_file(video)
            if f:
                seen.add(video["id"])
                results.append(Candidate(video["id"], f["link"], float(video["duration"]), video["image"]))
            if len(results) >= limit:
                return results
    return results


def candidates_for(query: str, limit: int, exclude: set[int]) -> list[Candidate]:
    found = search(query, limit, exclude)
    if len(found) < limit:  # broaden: drop the first word of the query
        broader = " ".join(query.split()[1:])
        if broader:
            found += search(broader, limit - len(found), exclude | {c.id for c in found})
    return found


class ScenePick(BaseModel):
    scene: int
    picks: list[int] = Field(description="Chosen candidate numbers, best first")
    match: int = Field(description="0-100: how clearly the best pick shows what the narration says")


class Picks(BaseModel):
    scenes: list[ScenePick]


def choose(scenes: list[tuple[str, int, list[Candidate]]]) -> tuple[list[list[Candidate]], list[int | None]]:
    """Show Claude every candidate thumbnail and let it pick the clips that literally match each line.

    `scenes` is a list of (narration, shots_needed, candidates). Returns the picks per scene and a 0-100
    match score per scene (None when unknown). Falls back to search order on any error.
    """
    from .script import ask_json  # local import: script.py doesn't depend on visuals

    fallback = [cands[:n] for _, n, cands in scenes]
    unknown: list[int | None] = [None] * len(scenes)
    if not config.ANTHROPIC_API_KEY or not any(c for _, _, c in scenes):
        return fallback, unknown

    content: list[dict] = [{
        "type": "text",
        "text": (
            "You are the editor of a viral fact Short. For each scene pick the stock clips (by number) "
            "whose thumbnail best shows what the narration says. Prefer dramatic, close, high-contrast, "
            "clearly lit shots with one obvious subject; avoid text overlays, watermarks, boring wide shots "
            "and anything that contradicts the line. Never pick the same number twice. Also score 0-100 how "
            "clearly your best pick shows what the sentence says (90+ instantly obvious, under 80 a viewer "
            "would be confused); be honest, a low score means the scene will be drawn instead."
        ),
    }]
    for i, (narration, n, cands) in enumerate(scenes):
        if not cands:
            continue
        content.append({"type": "text", "text": f"\nSCENE {i + 1} (pick {n}): \"{narration}\""})
        for k, c in enumerate(cands):
            content.append({"type": "text", "text": f"Candidate {i + 1}.{k + 1}:"})
            content.append({"type": "image", "source": {"type": "url", "url": c.thumb}})
    content.append({"type": "text", "text": "Return picks as candidate numbers after the dot (e.g. 3 for 2.3)."})

    try:
        result = ask_json(content, Picks, effort="low", system="You pick stock footage for short videos.")
    except Exception:
        return fallback, unknown

    chosen = list(fallback)
    scores = list(unknown)
    used: set[int] = set()
    by_scene = {p.scene: p.picks for p in result.scenes}
    for p in result.scenes:
        if 1 <= p.scene <= len(scenes):
            scores[p.scene - 1] = p.match
    for i, (_, n, cands) in enumerate(scenes):
        picks = [cands[k - 1] for k in by_scene.get(i + 1, []) if 1 <= k <= len(cands)]
        picks = [c for c in picks if c.id not in used]
        picks += [c for c in cands if c not in picks and c.id not in used]  # top up if Claude picked too few
        chosen[i] = picks[:n]
        used |= {c.id for c in chosen[i]}
    return chosen, scores


def download(url: str, out: Path) -> Path:
    if out.exists():
        return out
    with httpx.stream("GET", url, timeout=120, follow_redirects=True) as r:
        r.raise_for_status()
        with out.open("wb") as f:
            for chunk in r.iter_bytes(1 << 16):
                f.write(chunk)
    return out

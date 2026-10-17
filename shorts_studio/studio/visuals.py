"""Stock footage from Pexels (free API key: https://www.pexels.com/api/)."""

from pathlib import Path

import httpx

from . import config

API = "https://api.pexels.com/videos/search"


def _pick_file(video: dict) -> dict | None:
    """Best mp4 rendition: portrait-friendly, at least 720p, not a giant 4K download."""
    files = [f for f in video.get("video_files", []) if f.get("file_type") == "video/mp4" and f.get("height")]
    good = [f for f in files if 1280 <= max(f["width"], f["height"]) <= 2560]
    if not good:
        good = files
    if not good:
        return None
    return min(good, key=lambda f: (f["width"] > f["height"], abs(max(f["width"], f["height"]) - 1920)))


def find_clips(query: str, count: int, used: set[int]) -> list[tuple[int, str, float]]:
    """Return up to `count` (video_id, url, duration) not used earlier in this video."""
    results: list[tuple[int, str, float]] = []
    for orientation in ("portrait", None):
        params = {"query": query, "per_page": 15, "size": "medium"}
        if orientation:
            params["orientation"] = orientation
        r = httpx.get(API, params=params, headers={"Authorization": config.PEXELS_API_KEY}, timeout=30)
        r.raise_for_status()
        for video in r.json().get("videos", []):
            if video["id"] in used or video.get("duration", 0) < 3:
                continue
            f = _pick_file(video)
            if f:
                used.add(video["id"])
                results.append((video["id"], f["link"], float(video["duration"])))
            if len(results) >= count:
                return results
    return results


def download(url: str, out: Path) -> Path:
    with httpx.stream("GET", url, timeout=120, follow_redirects=True) as r:
        r.raise_for_status()
        with out.open("wb") as f:
            for chunk in r.iter_bytes(1 << 16):
                f.write(chunk)
    return out

"""Learn from the channel's own results: Claude compares how each uploaded Short performed and writes a
playbook (what hooks/topics work, what to avoid). New scripts and topic ideas are written with it."""

import json
import time

from pydantic import BaseModel, Field

from . import config, db

MIN_VIDEOS = 3


class Playbook(BaseModel):
    summary: str = Field(description="2-3 sentences: what this audience rewards, in plain words")
    winning_patterns: list[str] = Field(description="Concrete patterns from the best videos (hooks, topics, pacing)")
    losing_patterns: list[str] = Field(description="Concrete patterns from the weakest videos to stop doing")
    hook_rules: list[str] = Field(description="Rules for the next hooks, based on the data")
    next_topics: list[str] = Field(description="5 topics to make next, doubling down on what works")
    ab_findings: list[str] = Field(description="What A/B hook pairs showed, empty if none")


def performance_rows() -> list[dict]:
    rows = []
    for v in db.query("SELECT * FROM videos WHERE metrics IS NOT NULL"):
        suffix = "" if v["variant"] == "a" else f"_{v['variant']}"
        meta_file = config.OUTPUT_DIR / v["dir"] / f"meta{suffix}.json"
        if not meta_file.exists():
            continue
        meta = json.loads(meta_file.read_text())
        rows.append({
            "video": f"{v['dir']}/{v['variant']}",
            "topic": meta.get("topic"),
            "hook": meta.get("hook"),
            "title": meta.get("title"),
            "seconds": meta.get("duration"),
            "picture_match": meta.get("match_average"),
            **json.loads(v["metrics"]),
        })
    return rows


def update_playbook() -> dict:
    from .script import ask_json

    rows = performance_rows()
    if len(rows) < MIN_VIDEOS:
        raise RuntimeError(f"Kamida {MIN_VIDEOS} ta yuklangan va statistikasi bor video kerak (hozir {len(rows)} ta)")
    prompt = (
        "These are this channel's fact Shorts with their YouTube Analytics. Key retention signals: "
        "stayedToWatch (% of viewers who didn't swipe away), averageViewPercentage (can exceed 100 when "
        "people rewatch the loop), then views and subscribersGained. Rows with the same folder and variant "
        "a/b are an A/B test of two hooks on the same video. Find what separates winners from losers. "
        "Be specific to this data, not generic advice; say when the sample is too small to be sure.\n\n"
        + json.dumps(rows, ensure_ascii=False, indent=1)
    )
    playbook = ask_json(prompt, Playbook, effort="high")
    data = playbook.model_dump()
    db.execute("INSERT INTO playbook (created, data) VALUES (?, ?)", (time.time(), json.dumps(data)))
    return data


def playbook_prompt() -> str:
    """Extra instructions for the script writer, from the latest playbook (empty if none yet)."""
    try:
        p = db.latest_playbook()
    except Exception:
        return ""
    if not p:
        return ""
    lines = ["\n\nWHAT WORKS ON THIS CHANNEL (from its own analytics; follow it unless it contradicts the facts):",
             p["summary"]]
    lines += [f"- Do: {x}" for x in p["winning_patterns"] + p["hook_rules"]]
    lines += [f"- Avoid: {x}" for x in p["losing_patterns"]]
    return "\n".join(lines)

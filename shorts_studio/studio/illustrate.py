"""Custom illustrations (OpenAI image API) and Claude's picture-vs-narration match check."""

import base64
import io
from pathlib import Path

import httpx
from PIL import Image
from pydantic import BaseModel, Field

from . import config


def draw(prompt: str, out: Path) -> Path:
    """Draw one vertical illustration in the channel's fixed style."""
    if not config.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")
    r = httpx.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {config.OPENAI_API_KEY}"},
        json={
            "model": config.IMAGE_MODEL,
            "prompt": f"{prompt}\n\nStyle: {config.ILLUSTRATION_STYLE}",
            "size": "1024x1536",
            "quality": config.IMAGE_QUALITY,
            "n": 1,
        },
        timeout=180,
    )
    r.raise_for_status()
    out.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"]))
    return out


def thumbnail_b64(image: Path, max_side: int = 768) -> str:
    """Small JPEG for review requests, so a dozen images stay well under the API's request size limit."""
    with Image.open(image) as im:
        im = im.convert("RGB")
        im.thumbnail((max_side, max_side))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


class SceneMatch(BaseModel):
    scene: int
    score: int = Field(description="0-100: how clearly a viewer would connect this picture to the sentence")
    issue: str = Field(description="What's wrong or missing, empty if score >= 90")
    better_prompt: str = Field(description="An improved drawing prompt that would score 95+, no text in image")


class MatchReport(BaseModel):
    scenes: list[SceneMatch]


def review(items: list[tuple[int, str, Path]]) -> dict[int, SceneMatch]:
    """Score how well each drawn picture shows its narration. `items` is (scene_number, narration, image)."""
    from .script import ask_json

    content: list[dict] = [{
        "type": "text",
        "text": (
            "You check pictures for a fact Short. A viewer hears the sentence while seeing the picture. "
            "Score 0-100 how clearly and correctly the picture shows what the sentence says (right subject, "
            "right action, scale or comparison visible when the sentence is about size, nothing contradicting "
            "it, no garbled text). 90+ means instantly obvious; under 80 means a viewer would be confused."
        ),
    }]
    for number, narration, image in items:
        content.append({"type": "text", "text": f"\nSCENE {number}: \"{narration}\""})
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": thumbnail_b64(image)},
        })
    report = ask_json(content, MatchReport, effort="low", system="You review visuals for short videos.")
    return {m.scene: m for m in report.scenes}

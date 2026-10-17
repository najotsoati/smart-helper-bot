"""Viral fact-Shorts script writer powered by Claude."""

import json

import anthropic
from pydantic import BaseModel, Field

from . import config

SYSTEM_PROMPT = """You are the head writer of a fact-Shorts channel with 10M+ subscribers \
(YouTube Shorts, TikTok, Instagram Reels). You write narration that people cannot scroll past.

Retention rules you never break:
1. HOOK (first sentence, max 12 words, spoken in under 3 seconds). Open mid-action with the most \
shocking, specific, visual claim. No greetings, no "Did you know", no "In this video", no "Here are". \
Good hooks create a curiosity gap or contradict common sense: \
"Your body glows in the dark. You just can't see it." / \
"This ocean is so deep, Everest would vanish inside it."
2. Every sentence must earn the next one. Use open loops ("but that's not the strangest part"), \
escalation (each fact crazier than the last) and concrete numbers, comparisons and images \
("a blue whale's heart is the size of a small car", never "very big").
3. Short, punchy spoken English. 4-14 words per sentence. Contractions. No lists read aloud, \
no filler, no "interesting", "amazing", "incredible".
4. One sentence per scene. A new scene every 2-3 seconds so the picture changes constantly.
5. Payoff near the end, then the LAST sentence must flow naturally back into the hook, \
so when the video loops the viewer doesn't notice the restart \
(e.g. last line "...and that's exactly why" + hook "your body glows in the dark").
6. Only true, verifiable facts. If a popular "fact" is a myth, either skip it or use the myth \
as the twist ("Goldfish don't have 3-second memories. They remember for months.").
7. No call to action like "subscribe" or "like" in the narration.

For each scene also give:
- visual_query: 2-4 concrete English words for a stock-video search that will literally show \
the sentence (things that exist on Pexels: "deep ocean dark", "human heart beating", \
"lightning storm night"). Never abstract words.
- emphasis: 1-2 words copied exactly from the narration that should pop on screen \
(numbers and the most surprising word).
- on_screen_text: a 1-4 word big title for the scene (like "8 MINUTES" or "NOT A MYTH"), \
or empty string when the captions are enough. Use it on at most half the scenes.
"""


class Scene(BaseModel):
    narration: str = Field(description="One spoken sentence")
    visual_query: str
    emphasis: list[str]
    on_screen_text: str


class ShortScript(BaseModel):
    topic: str
    hook_candidates: list[str] = Field(description="3 different hook ideas, best first")
    scenes: list[Scene] = Field(description="Scene 1 narration is the chosen hook")
    title: str = Field(description="YouTube Shorts title, under 60 characters, curiosity gap, 1 emoji max")
    description: str = Field(description="2 short lines for the video description")
    hashtags: list[str] = Field(description="5-8 hashtags without the # sign")
    pinned_comment: str = Field(description="A question that makes people reply in the comments")


class TopicIdea(BaseModel):
    topic: str
    hook: str
    why_it_works: str


class TopicIdeas(BaseModel):
    ideas: list[TopicIdea]


def _client() -> anthropic.Anthropic:
    if not config.ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is not set (add it to shorts_studio/.env)")
    return anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def _ask(prompt: str, schema: type[BaseModel], effort: str = "high") -> BaseModel:
    response = _client().beta.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        thinking={"type": "adaptive"},
        output_config={
            "effort": effort,
            "format": {"type": "json_schema", "schema": _strict_schema(schema)},
        },
        # On a safety decline, re-run on Anthropic's recommended fallback model.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{"role": "user", "content": prompt}],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("Claude declined this topic, try another one")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Script was cut off, try again")
    text = next(b.text for b in response.content if b.type == "text")
    return schema.model_validate(json.loads(text))


def _strict_schema(model: type[BaseModel]) -> dict:
    """Pydantic JSON schema with additionalProperties=false everywhere (required by structured outputs)."""
    schema = model.model_json_schema()

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "object":
                node["additionalProperties"] = False
                node["required"] = list(node.get("properties", {}))
            node.pop("title", None)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(schema)
    return schema


def write_script(topic: str, seconds: int = 45) -> ShortScript:
    words = int(seconds * 2.7)  # ~2.7 spoken words per second at a slightly fast pace
    scenes = max(8, seconds // 3)
    prompt = (
        f"Write a {seconds}-second fact Short about: {topic}\n\n"
        f"Target about {words} words of narration in {scenes - 2}-{scenes + 2} scenes. "
        "First brainstorm 3 hooks and put the strongest first in hook_candidates; "
        "scene 1 narration must be that hook. Make sure the last line loops into the hook."
    )
    return _ask(prompt, ShortScript)


def suggest_topics(niche: str = "", count: int = 8) -> list[TopicIdea]:
    prompt = (
        f"Give {count} fact-Short topics that are proven to go viral right now"
        + (f" in the niche: {niche}" if niche else " (mix space, human body, animals, history, psychology, ocean)")
        + ". Prefer topics with a shocking, visual, easy-to-film core fact. "
        "For each: the topic, the hook you would open with, and one line on why it works."
    )
    return _ask(prompt, TopicIdeas, effort="medium").ideas

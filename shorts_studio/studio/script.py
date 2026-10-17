"""Viral fact-Shorts script writer powered by Claude (plus web fact-checking)."""

import json
from typing import Literal

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
5. Exactly one TWIST scene about two thirds in (the most surprising turn), then a payoff. \
The LAST sentence must flow naturally back into the hook, so when the video loops the viewer \
doesn't notice the restart (e.g. last line "...and that's exactly why" + hook "your body glows in the dark").
6. Only true, verifiable facts with correct numbers. If a popular "fact" is a myth, either skip it \
or use the myth as the twist ("Goldfish don't have 3-second memories. They remember for months.").
7. No call to action like "subscribe" or "like" in the narration.

The channel has a cartoon host called Fakti (a friendly purple creature) and custom illustrations.
For each scene also give:
- visual_type, the single most important choice, because the picture must clearly show what is being said:
  * "mascot": Fakti talks straight to camera. Use it ONLY for scene 1 (the hook), the twist scene \
and the last scene. Fakti introduces, reacts, and closes the loop; facts are shown with pictures.
- host_emotion: Fakti's face for this scene (shown big in mascot scenes, in a corner badge otherwise): \
"excited" for amazing facts and the hook, "surprised" for the twist, "scared" for creepy or dangerous \
facts, "pointing" when introducing something to look at, "neutral" otherwise.
  * "illustration": a custom drawing. Use it when the fact is impossible or boring to film: inside the \
body, microscopic, space scales, prehistoric/historic events, hypothetical or exaggerated comparisons.
  * "stock": real footage. Use it when real video of the subject looks spectacular (animals, nature, \
weather, cities, machines) and a stock site will certainly have it.
- image_prompt: what to draw so the picture literally shows the sentence: the subject, what it's doing, \
setting, camera angle, and a scale cue if the fact is about size. Concrete and visual, 1-2 sentences, \
no text or numbers in the image. Write it for every non-mascot scene (stock scenes use it as a backup). \
Empty string for mascot scenes.
- visual_query: 2-4 concrete English words for a stock-video search that will literally show \
the sentence (things that exist on Pexels: "deep ocean dark", "human heart beating", \
"lightning storm night"). Never abstract words.
- emphasis: 1-2 words copied exactly from the narration that should pop on screen \
(numbers and the most surprising word).
- on_screen_text: a 1-4 word big title for the scene (like "8 MINUTES" or "NOT A MYTH"), \
or empty string. Use it on at most a third of the scenes, never on a graphic scene.
- beat: "twist" for the single twist scene, "payoff" for the scene right after it, else "normal".
- graphic: animated infographics beat stock footage for numbers. Use them on 1-2 scenes:
  * "counter": one big number counting up (counter_value, counter_prefix like "$", \
counter_suffix like " KM" or "x", graphic_label: 1-4 words under the number).
  * "compare": two bars side by side (compare_a_label/value vs compare_b_label/value, \
same unit, graphic_label names the unit, e.g. "METERS"). Perfect for "X is bigger than Y".
  * "none" for every other scene (set numeric fields to 0 and texts to "").
"""

Mood = Literal["mysterious", "epic", "scary", "uplifting", "funny"]


class Scene(BaseModel):
    narration: str = Field(description="One spoken sentence")
    visual_query: str
    emphasis: list[str]
    on_screen_text: str
    visual_type: Literal["mascot", "illustration", "stock"] = "stock"
    host_emotion: Literal["neutral", "excited", "surprised", "scared", "pointing"] = "neutral"
    image_prompt: str = ""
    beat: Literal["normal", "twist", "payoff"] = "normal"
    graphic_type: Literal["none", "counter", "compare"] = "none"
    graphic_label: str = ""
    counter_value: float = 0
    counter_prefix: str = ""
    counter_suffix: str = ""
    compare_a_label: str = ""
    compare_a_value: float = 0
    compare_b_label: str = ""
    compare_b_value: float = 0


class ShortScript(BaseModel):
    topic: str
    mood: Mood = Field("mysterious", description="Background music mood that fits the story")
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


class FactCheck(BaseModel):
    scene: int = Field(description="1-based scene number")
    verdict: Literal["correct", "fixed", "removed"]
    note: str = Field(description="What was wrong and the corrected fact, in one short line")
    source: str = Field(description="URL of the best source, or empty")


class CheckedScript(BaseModel):
    script: ShortScript
    checks: list[FactCheck] = Field(description="Only scenes that contain a factual claim")


def _client() -> anthropic.Anthropic:
    if not config.ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is not set (add it to shorts_studio/.env)")
    return anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY, max_retries=4)


def _check_stop(response) -> None:
    if response.stop_reason == "refusal":
        raise RuntimeError("Claude declined this request, try another topic")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Claude's answer was cut off, try again")


def ask_json(content, schema: type[BaseModel], effort: str = "high", system: str = SYSTEM_PROMPT) -> BaseModel:
    """One structured-output call. `content` is a prompt string or a list of content blocks."""
    response = _client().beta.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=16000,
        system=system,
        thinking={"type": "adaptive"},
        output_config={
            "effort": effort,
            "format": {"type": "json_schema", "schema": _strict_schema(schema)},
        },
        # On a safety decline, re-run on Anthropic's recommended fallback model.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{"role": "user", "content": content}],
    )
    _check_stop(response)
    text = next((b.text for b in response.content if b.type == "text"), None)
    if text is None:
        raise RuntimeError("Claude returned no text, try again")
    return schema.model_validate(json.loads(text))


def _strict_schema(model: type[BaseModel]) -> dict:
    """Pydantic JSON schema with additionalProperties=false everywhere (required by structured outputs)."""
    schema = model.model_json_schema()

    def walk(node):
        """`node` is always a schema (never a `properties` mapping, whose keys are field names)."""
        if isinstance(node, list):
            for value in node:
                walk(value)
            return
        if not isinstance(node, dict):
            return
        node.pop("title", None)
        node.pop("default", None)
        if node.get("type") == "object":
            node["additionalProperties"] = False
            node["required"] = list(node.get("properties", {}))
        for key, value in node.items():
            if key in ("properties", "$defs"):
                for sub in value.values():
                    walk(sub)
            elif isinstance(value, (dict, list)):
                walk(value)

    walk(schema)
    return schema


def write_script(topic: str, seconds: int = 35) -> ShortScript:
    words = int(seconds * 2.7)  # ~2.7 spoken words per second at a slightly fast pace
    scenes = max(8, seconds // 3)
    prompt = (
        f"Write a {seconds}-second fact Short about: {topic}\n\n"
        f"Target about {words} words of narration in {scenes - 2}-{scenes + 2} scenes. "
        "First brainstorm 3 hooks and put the strongest first in hook_candidates; "
        "scene 1 narration must be that hook. Make sure the last line loops into the hook."
    )
    from .learn import playbook_prompt  # local import: learn.py uses ask_json from this module

    return ask_json(prompt + playbook_prompt(), ShortScript)


def suggest_topics(niche: str = "", count: int = 8, trending: list[str] | None = None) -> list[TopicIdea]:
    prompt = (
        f"Give {count} fact-Short topics that are proven to go viral right now"
        + (f" in the niche: {niche}" if niche else " (mix space, human body, animals, history, psychology, ocean)")
        + ". Prefer topics with a shocking, visual, easy-to-film core fact. "
        "For each: the topic, the hook you would open with, and one line on why it works."
    )
    if trending:
        prompt += (
            "\n\nThese Shorts are outperforming their channels in this niche right now "
            "(views far above subscriber count). Find the patterns and suggest fresh angles on them, "
            "don't copy them:\n- " + "\n- ".join(trending)
        )
    from .learn import playbook_prompt

    return ask_json(prompt + playbook_prompt(), TopicIdeas, effort="medium").ideas


def fact_check(script: ShortScript) -> CheckedScript:
    """Verify every claim on the web, then return a corrected script plus a per-scene report."""
    client = _client()
    numbered = "\n".join(f"{i + 1}. {s.narration}" for i, s in enumerate(script.scenes))
    question = (
        "Fact-check this Short's narration with web searches. For every scene with a factual claim, "
        "say whether it's correct, and if not give the corrected fact with numbers and a source URL. "
        "Be strict about numbers and popular myths.\n\n" + numbered
    )
    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 8}]
    messages = [{"role": "user", "content": question}]
    report_parts: list[str] = []
    for _ in range(5):  # resume if the server-side search loop pauses
        response = client.beta.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=16000,
            thinking={"type": "adaptive"},
            output_config={"effort": "medium"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            tools=tools,
            messages=messages,
        )
        _check_stop(response)
        report_parts += [b.text for b in response.content if b.type == "text"]
        if response.stop_reason != "pause_turn":
            break
        messages = [messages[0], {"role": "assistant", "content": response.content}]
    report = "\n".join(report_parts)

    prompt = (
        "Here is a Short script as JSON and a web fact-check report. Return the script with every "
        "wrong fact corrected (keep the style, length, hook and loop; rewrite or drop a scene only "
        "if the claim is false and can't be fixed; keep emphasis/graphic numbers consistent with "
        "the narration) and the per-scene check list.\n\n"
        f"SCRIPT:\n{script.model_dump_json()}\n\nFACT-CHECK REPORT:\n{report}"
    )
    return ask_json(prompt, CheckedScript, effort="low")


def try_fact_check(script: ShortScript) -> tuple[ShortScript, list[FactCheck], str]:
    """Fact-check, but never lose the script: if checking fails (e.g. web search is turned off for
    the Anthropic organization), return the unchecked draft and a warning to show."""
    try:
        checked = fact_check(script)
        return checked.script, checked.checks, ""
    except Exception as e:
        return script, [], f"Faktlarni tekshirib bo'lmadi, ssenariy tekshirilmagan holda qoldi. Sabab: {e}"[:400]

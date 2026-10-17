"""OpenRouter (https://openrouter.ai): one key for many models, including free ones.

Used instead of Claude when an OpenRouter key is set and no Anthropic key is (or LLM_PROVIDER=openrouter).
Free model ids change often, so by default the best currently-free model is picked from OpenRouter's own
list. Free models have no web search (no fact-checking) and daily request limits."""

import json
import re
import time

import httpx
from pydantic import BaseModel, ValidationError

from . import config, net

# preferred models, best first, when picking a free one automatically (the free catalog changes often)
PREFERENCE = ["inkling", "nemotron-3-ultra", "gpt-oss-120b", "nemotron-3-super", "deepseek", "qwen3",
              "gemma-4-31b", "gemma", "llama", "qwen", "mistral", "glm"]
VISION_PREFERENCE = ["inkling", "gemma-4-31b", "gemma-4", "gemma", "qwen", "llama", "mistral"]
# free but not chat models: they can't write a script
NOT_CHAT = ("embed", "rerank", "safety", "guard", "moderation", "whisper", "tts", "transcri")
_models_cache: tuple[float, list[dict]] = (0.0, [])


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://127.0.0.1",  # identifies the app in OpenRouter's dashboard
        "X-Title": "Shorts Studio",
    }


def _models() -> list[dict]:
    global _models_cache
    fetched, models = _models_cache
    if not models or time.time() - fetched > 3600:
        r = net.request("GET", f"{config.OPENROUTER_BASE_URL}/models", headers=_headers(), timeout=30)
        models = r.json().get("data", [])
        _models_cache = (time.time(), models)
    return models


def _is_free(m: dict) -> bool:
    p = m.get("pricing", {})
    return str(p.get("prompt", "1")) in ("0", "0.0") and str(p.get("completion", "1")) in ("0", "0.0")


def ranked_models(vision: bool = False) -> list[str]:
    """Free chat models, best first; the one set in the panel (if any) goes first."""
    chosen = config.OPENROUTER_VISION_MODEL if vision else config.OPENROUTER_MODEL
    free = [m for m in _models() if _is_free(m) and not any(w in m["id"].lower() for w in NOT_CHAT)
            and "text" in m.get("architecture", {}).get("output_modalities", ["text"])]
    if vision:
        free = [m for m in free if "image" in m.get("architecture", {}).get("input_modalities", [])]
    order = VISION_PREFERENCE if vision else PREFERENCE

    def rank(m: dict):
        mid = m["id"].lower()
        family = next((i for i, name in enumerate(order) if name in mid), len(order))
        return family, -int(m.get("context_length") or 0)

    ids = [m["id"] for m in sorted(free, key=rank)]
    if chosen:
        ids = [chosen] + [i for i in ids if i != chosen]
    if not ids:
        raise RuntimeError("OpenRouter'da hozir mos bepul model topilmadi" + (" (rasmni tushunadigan)" if vision else ""))
    return ids


def pick_model(vision: bool = False) -> str:
    return ranked_models(vision)[0]


def _to_openai_content(content) -> str | list[dict]:
    """Anthropic-style content blocks -> OpenAI-style parts."""
    if isinstance(content, str):
        return content
    parts = []
    for block in content:
        if block["type"] == "text":
            parts.append({"type": "text", "text": block["text"]})
        elif block["type"] == "image":
            src = block["source"]
            url = src["url"] if src["type"] == "url" else f"data:{src['media_type']};base64,{src['data']}"
            parts.append({"type": "image_url", "image_url": {"url": url}})
    return parts


def _extract_json(text: str) -> dict:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)  # reasoning models may prepend their thoughts
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    if fenced:
        text = fenced.group(1)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("javobda JSON yo'q")
    return json.loads(text[start:end + 1])


def ask_json(content, schema: type[BaseModel], json_schema: dict, system: str) -> BaseModel:
    """Ask for JSON; if a free model is overloaded, rate-limited or unavailable, move on to the next one."""
    vision = not isinstance(content, str) and any(b["type"] == "image" for b in content)
    instructions = (
        f"{system}\n\nReply with ONLY one JSON object (no markdown, no comments) that matches this JSON schema "
        f"exactly, with every required field filled in:\n{json.dumps(json_schema)}"
    )
    failures = []
    for model in ranked_models(vision)[:MAX_MODELS]:
        try:
            return _ask_model(model, instructions, content, schema)
        except _ModelUnavailable as e:
            failures.append(f"{model}: {e}")
    raise RuntimeError("Bepul modellar hozir band yoki ishlamayapti, birozdan keyin qayta urinib ko'ring. "
                       + " | ".join(failures)[:600])


MAX_MODELS = 4  # how many free models to try before giving up


class _ModelUnavailable(Exception):
    """This model can't answer right now (busy, rate-limited, region, removed): try another one."""


def _ask_model(model: str, instructions: str, content, schema: type[BaseModel]) -> BaseModel:
    messages = [{"role": "system", "content": instructions},
                {"role": "user", "content": _to_openai_content(content)}]
    last_error = ""
    for attempt in range(2):  # one retry with the validation error fed back
        try:
            r = net.request(
                "POST", f"{config.OPENROUTER_BASE_URL}/chat/completions", headers=_headers(), timeout=300,
                attempts=2,
                json={"model": model, "messages": messages, "response_format": {"type": "json_object"},
                      "max_tokens": 12000},
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 402):  # bad key / no credit: no other model will do better
                raise
            raise _ModelUnavailable(f"HTTP {e.response.status_code}") from e
        data = r.json()
        if "error" in data:
            err = data["error"]
            raise _ModelUnavailable(err.get("message", str(err)) if isinstance(err, dict) else str(err))
        if not data.get("choices"):
            raise _ModelUnavailable("bo'sh javob")
        text = data["choices"][0]["message"].get("content") or ""
        try:
            return schema.model_validate(_extract_json(text))
        except (ValueError, ValidationError) as e:
            last_error = str(e)[:1500]
            messages += [{"role": "assistant", "content": text},
                         {"role": "user", "content": f"That JSON was invalid: {last_error}\nSend the corrected JSON only."}]
    raise _ModelUnavailable(f"to'g'ri JSON qaytarmadi: {last_error[:200]}")


def key_info() -> str:
    r = net.request("GET", f"{config.OPENROUTER_BASE_URL}/key", headers=_headers(), attempts=1, timeout=15)
    d = r.json().get("data", {})
    tier = "bepul tarif" if d.get("is_free_tier") else "balans bor"
    return f"{tier}; matn modeli: {pick_model()}"

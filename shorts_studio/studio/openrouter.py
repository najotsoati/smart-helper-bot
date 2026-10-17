"""OpenRouter (https://openrouter.ai): one key for many models, including free ones.

Used instead of Claude when an OpenRouter key is set and no Anthropic key is (or LLM_PROVIDER=openrouter).
Free model ids change often, so by default the best currently-free model is picked from OpenRouter's own
list. Free models have no web search (no fact-checking) and daily request limits."""

import json
import re
import time

from pydantic import BaseModel, ValidationError

from . import config, net

# preferred families, best first, when picking a free model automatically
PREFERENCE = ["deepseek", "qwen", "llama", "gemini", "gemma", "mistral", "glm", "kimi"]
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


def pick_model(vision: bool = False) -> str:
    chosen = config.OPENROUTER_VISION_MODEL if vision else config.OPENROUTER_MODEL
    if chosen:
        return chosen
    free = [m for m in _models() if _is_free(m)]
    if vision:
        free = [m for m in free if "image" in m.get("architecture", {}).get("input_modalities", [])]
    if not free:
        raise RuntimeError("OpenRouter'da hozir mos bepul model topilmadi" + (" (rasmni tushunadigan)" if vision else ""))

    def rank(m: dict):
        mid = m["id"].lower()
        family = next((i for i, name in enumerate(PREFERENCE) if name in mid), len(PREFERENCE))
        return family, -int(m.get("context_length") or 0)

    return min(free, key=rank)["id"]


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
    vision = not isinstance(content, str) and any(b["type"] == "image" for b in content)
    model = pick_model(vision)
    instructions = (
        f"{system}\n\nReply with ONLY one JSON object (no markdown, no comments) that matches this JSON schema "
        f"exactly, with every required field filled in:\n{json.dumps(json_schema)}"
    )
    messages = [{"role": "system", "content": instructions},
                {"role": "user", "content": _to_openai_content(content)}]
    last_error = ""
    for attempt in range(2):  # one retry with the validation error fed back
        r = net.request(
            "POST", f"{config.OPENROUTER_BASE_URL}/chat/completions", headers=_headers(), timeout=300,
            json={"model": model, "messages": messages, "response_format": {"type": "json_object"},
                  "max_tokens": 12000},
        )
        data = r.json()
        if "error" in data:
            raise RuntimeError(f"OpenRouter: {data['error'].get('message', data['error'])}")
        text = data["choices"][0]["message"].get("content") or ""
        try:
            return schema.model_validate(_extract_json(text))
        except (ValueError, ValidationError) as e:
            last_error = str(e)[:1500]
            messages += [{"role": "assistant", "content": text},
                         {"role": "user", "content": f"That JSON was invalid: {last_error}\nSend the corrected JSON only."}]
    raise RuntimeError(f"{model} to'g'ri JSON qaytarmadi: {last_error[:300]}")


def key_info() -> str:
    r = net.request("GET", f"{config.OPENROUTER_BASE_URL}/key", headers=_headers(), attempts=1, timeout=15)
    d = r.json().get("data", {})
    tier = "bepul tarif" if d.get("is_free_tier") else "balans bor"
    return f"{tier}; matn modeli: {pick_model()}"

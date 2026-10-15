"""Chat client for OpenRouter and xAI (both speak the OpenAI chat format).

Providers are tried in order; a model that fails, is rate limited or returns
broken JSON is skipped and the next one is used.  Usage is counted per day so
the panel can show how much of the free OpenRouter quota is left.
"""

import json
import re
import time

import httpx

from . import config, store


class LLMError(Exception):
    pass


_free_cache = {"at": 0.0, "models": []}


def free_models():
    """Free chat models OpenRouter lists now (they change often), biggest context first."""
    if time.time() - _free_cache["at"] < 6 * 3600 and _free_cache["models"]:
        return _free_cache["models"]
    try:
        r = httpx.get("https://openrouter.ai/api/v1/models", timeout=30)
        rows = r.json().get("data", [])
    except (httpx.HTTPError, ValueError):
        return _free_cache["models"]
    free = [m for m in rows if m.get("id", "").endswith(":free")
            and str(m.get("pricing", {}).get("prompt", "1")) in ("0", "0.0")
            and "text" in str(m.get("architecture", {}).get("output_modalities", ["text"]))]
    free.sort(key=lambda m: m.get("context_length") or 0, reverse=True)
    _free_cache.update(at=time.time(), models=[m["id"] for m in free[:5]])
    return _free_cache["models"]


def _candidates(strong=False):
    out = []
    models = list(config.OPENROUTER_MODELS) or (free_models() if config.OPENROUTER_API_KEY else [])
    if strong:
        models = list(config.OPENROUTER_STRONG_MODELS) + models
    if config.OPENROUTER_API_KEY:
        for m in models:
            out.append(("openrouter", "https://openrouter.ai/api/v1/chat/completions", config.OPENROUTER_API_KEY, m))
    if config.XAI_API_KEY:
        out.append(("xai", "https://api.x.ai/v1/chat/completions", config.XAI_API_KEY, config.XAI_MODEL))
    return out


def _extract_json(text):
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m:
        text = m.group(1).strip()
    start = min([i for i in (text.find("{"), text.find("[")) if i >= 0], default=-1)
    if start > 0:
        text = text[start:]
    return json.loads(text)


def chat(system, user, want_json=True, strong=False, temperature=0.8, log=None):
    """Return parsed JSON (or text).  `log` collects which model answered."""
    tried, bad_key = [], set()
    for provider, url, key, model in _candidates(strong):
        if provider in bad_key:
            continue
        body = {"model": model, "temperature": temperature,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        if want_json:
            body["response_format"] = {"type": "json_object"}
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        if provider == "openrouter":
            headers.update({"HTTP-Referer": config.PUBLIC_URL or "http://localhost", "X-Title": "Shorts Studio"})
        for attempt in range(2):
            try:
                r = httpx.post(url, json=body, headers=headers, timeout=120)
                store.count_usage(provider, model, r.status_code)
                if r.status_code in (401, 403):
                    bad_key.add(provider)
                    name = "OPENROUTER_API_KEY" if provider == "openrouter" else "XAI_API_KEY"
                    tried.append(f"{provider}: kalit qabul qilinmadi (HTTP {r.status_code}) - .env dagi {name} ni tekshiring")
                    break
                if r.status_code == 429:
                    tried.append(f"{model}: rate limited")
                    break
                if r.status_code >= 400:
                    tried.append(f"{model}: HTTP {r.status_code} {r.text[:160]}")
                    if r.status_code == 400 and "response_format" in r.text and "response_format" in body:
                        body.pop("response_format")
                        continue
                    break
                text = r.json()["choices"][0]["message"]["content"] or ""
                result = _extract_json(text) if want_json else text
                if log is not None:
                    log.append(f"{provider}:{model}")
                return result
            except (ValueError, KeyError, IndexError) as e:
                tried.append(f"{model}: bad answer ({e.__class__.__name__})")
                time.sleep(1)
            except httpx.HTTPError as e:
                tried.append(f"{model}: {e.__class__.__name__}")
                break
    if not tried:
        raise LLMError("No AI key is set. Put OPENROUTER_API_KEY or XAI_API_KEY into .env")
    raise LLMError("All models failed: " + "; ".join(tried[-6:]))

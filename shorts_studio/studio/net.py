"""HTTP with retries: transient network errors, 429 and 5xx are retried with exponential backoff."""

import time
from pathlib import Path

import httpx

RETRY_STATUS = {408, 409, 425, 429, 500, 502, 503, 504}


def request(method: str, url: str, attempts: int = 4, **kwargs) -> httpx.Response:
    kwargs.setdefault("timeout", 60)
    for attempt in range(attempts):
        try:
            r = httpx.request(method, url, **kwargs)
            if r.status_code not in RETRY_STATUS or attempt == attempts - 1:
                r.raise_for_status()
                return r
            wait = float(r.headers.get("retry-after", 0) or 0) or 2 ** (attempt + 1)
        except httpx.TransportError:
            if attempt == attempts - 1:
                raise
            wait = 2 ** (attempt + 1)
        time.sleep(min(wait, 30))
    raise RuntimeError("unreachable")


def download(url: str, out: Path, attempts: int = 4) -> Path:
    if out.exists() and out.stat().st_size > 0:
        return out
    tmp = out.with_suffix(out.suffix + ".part")
    for attempt in range(attempts):
        try:
            with httpx.stream("GET", url, timeout=120, follow_redirects=True) as r:
                r.raise_for_status()
                with tmp.open("wb") as f:
                    for chunk in r.iter_bytes(1 << 16):
                        f.write(chunk)
            tmp.replace(out)
            return out
        except (httpx.TransportError, httpx.HTTPStatusError):
            if attempt == attempts - 1:
                raise
            time.sleep(2 ** (attempt + 1))
    return out

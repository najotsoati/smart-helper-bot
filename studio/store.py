"""Projects on disk: data/projects/<id>/project.json plus audio/ and the MP4.

One small JSON file per project is enough for one person and keeps the server
light (2 GB RAM).  Writes go through a temp file so a crash never leaves half a file.
"""

import datetime as dt
import json
import os
import re
import threading
import uuid

from . import config

_lock = threading.Lock()

# Project states, in order.
STATES = ["draft", "hooks", "script", "storyboard", "voiced", "queued", "rendering", "done", "failed"]


def _projects_dir():
    p = config.DATA_DIR / "projects"
    p.mkdir(parents=True, exist_ok=True)
    return p


def project_dir(pid):
    if not re.fullmatch(r"[a-f0-9]{12}", pid or ""):
        raise KeyError(pid)
    return _projects_dir() / pid


def _write_json(path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def create(brief):
    pid = uuid.uuid4().hex[:12]
    d = project_dir(pid)
    (d / "audio").mkdir(parents=True)
    now = dt.datetime.now().isoformat(timespec="seconds")
    p = {"id": pid, "created": now, "updated": now, "state": "draft", "brief": brief,
         "hooks": [], "hook": None, "script": None, "storyboard": None, "check": None,
         "review": None, "log": [], "error": None}
    _write_json(d / "project.json", p)
    return p


def load(pid):
    return json.loads((project_dir(pid) / "project.json").read_text(encoding="utf-8"))


def save(p):
    with _lock:
        p["updated"] = dt.datetime.now().isoformat(timespec="seconds")
        _write_json(project_dir(p["id"]) / "project.json", p)
    return p


def all_projects():
    out = []
    for d in _projects_dir().iterdir():
        f = d / "project.json"
        if f.exists():
            try:
                out.append(json.loads(f.read_text(encoding="utf-8")))
            except ValueError:
                continue
    return sorted(out, key=lambda p: p["created"], reverse=True)


def delete(pid):
    import shutil
    shutil.rmtree(project_dir(pid), ignore_errors=True)


# --- AI usage per day (for the free-quota meter) ---

def _usage_file():
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    return config.DATA_DIR / "usage.json"


def count_usage(provider, model, status):
    with _lock:
        f = _usage_file()
        data = json.loads(f.read_text()) if f.exists() else {}
        day = dt.date.today().isoformat()
        d = data.setdefault(day, {})
        key = f"{provider}:{model}"
        d[key] = d.get(key, 0) + 1
        if status == 429:
            d["rate_limited"] = d.get("rate_limited", 0) + 1
        for old in sorted(data)[:-30]:
            data.pop(old)
        _write_json(f, data)


def usage_today():
    f = _usage_file()
    data = json.loads(f.read_text()) if f.exists() else {}
    return data.get(dt.date.today().isoformat(), {})


# --- panel settings (e.g. chosen voices) ---

def settings():
    f = config.DATA_DIR / "settings.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def save_settings(data):
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with _lock:
        _write_json(config.DATA_DIR / "settings.json", data)

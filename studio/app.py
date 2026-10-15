"""Shorts Studio web panel and the render-agent API.

Run:  uvicorn studio.app:app --host 0.0.0.0 --port 8080
The panel is protected with PANEL_USER / PANEL_PASSWORD, the agent API with AGENT_TOKEN.
"""

import json
import secrets
import threading
import traceback
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates

from . import blender_script, checker, config, llm, roles, store, tts, vocab
from .storyboard import normalize, timeline, total_seconds

app = FastAPI(title="Shorts Studio", docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
basic = HTTPBasic()


def panel_auth(cred: HTTPBasicCredentials = Depends(basic)):
    if not config.PANEL_PASSWORD:
        raise HTTPException(503, "Set PANEL_PASSWORD in .env first")
    ok = secrets.compare_digest(cred.username.encode(), config.PANEL_USER.encode()) and \
        secrets.compare_digest(cred.password.encode(), config.PANEL_PASSWORD.encode())
    if not ok:
        raise HTTPException(401, "Wrong login", headers={"WWW-Authenticate": "Basic"})


def agent_auth(request: Request):
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if not config.AGENT_TOKEN or not secrets.compare_digest(token.encode(), config.AGENT_TOKEN.encode()):
        raise HTTPException(401, "Bad agent token")


# ---------- background work: AI calls take 10-60 s, the page refreshes meanwhile ----------

def run_bg(pid, label, fn):
    p = store.load(pid)
    if p.get("busy"):
        return
    p["busy"], p["error"] = label, None
    store.save(p)

    def work():
        p = store.load(pid)
        models = []
        try:
            fn(p, models)
            if models:
                p["log"].append(f"{label}: {', '.join(models)}")
        except Exception as e:   # shown on the project page
            p["error"] = f"{label}: {e}"
            p["log"].append(traceback.format_exc(limit=3)[-600:])
        p["busy"] = None
        store.save(p)
    threading.Thread(target=work, daemon=True).start()


def _check(p):
    sb = p["storyboard"]
    p["check"] = checker.check(sb)
    return p["check"]


def step_hooks(p, log):
    p["hooks"] = roles.make_hooks(p["brief"], log=log)
    p["state"] = "hooks"


def step_script(p, log):
    p["script"] = roles.write_script(p["brief"], p["hook"], log=log)
    p["state"] = "script"


def step_direct(p, log):
    sb = roles.direct(p["script"], p["brief"], log=log)
    sb.setdefault("upload", (p["script"] or {}).get("upload"))
    p["storyboard"], p["state"], p["review"] = sb, "storyboard", None
    _check(p)


def step_own(p, log):
    p["storyboard"] = roles.direct_own_script(p["brief"]["own_script"], log=log)
    p["state"], p["review"] = "storyboard", None
    _check(p)


def step_review(p, log):
    p["review"] = roles.review(p["storyboard"], _check(p), log=log)


def step_revise(p, log):
    notes = (p.get("review") or {}).get("fix", []) + (p.get("check") or {}).get("errors", [])
    p["storyboard"] = roles.revise(p["storyboard"], notes, log=log)
    p["review"] = None
    _check(p)


def step_voice(p, log):
    sb = tts.voice_lines(p["storyboard"], store.project_dir(p["id"]) / "audio")
    p["storyboard"] = sb
    p["state"] = "voiced"
    _check(p)


# ---------------------------------- pages ----------------------------------

def page(request, name, **ctx):
    return templates.TemplateResponse(request, name, ctx)


@app.get("/", response_class=HTMLResponse, dependencies=[Depends(panel_auth)])
def home(request: Request):
    usage = store.usage_today()
    used = sum(v for k, v in usage.items() if k.startswith("openrouter:"))
    return page(request, "home.html", projects=store.all_projects()[:30], used=used,
                limit=config.OPENROUTER_DAILY_FREE, rate_limited=usage.get("rate_limited", 0))


@app.get("/new", response_class=HTMLResponse, dependencies=[Depends(panel_auth)])
def new_form(request: Request):
    return page(request, "new.html")


@app.post("/new", dependencies=[Depends(panel_auth)])
def new_create(topic: str = Form(...), genre: str = Form("comedy sketch"), seconds: int = Form(35),
               notes: str = Form("")):
    p = store.create({"topic": topic.strip(), "genre": genre, "seconds": max(15, min(seconds, 58)),
                      "notes": notes.strip()})
    run_bg(p["id"], "Hook", step_hooks)
    return RedirectResponse(f"/p/{p['id']}", 303)


@app.get("/own", response_class=HTMLResponse, dependencies=[Depends(panel_auth)])
def own_form(request: Request):
    return page(request, "own.html")


@app.post("/own", dependencies=[Depends(panel_auth)])
def own_create(text: str = Form(...)):
    text = text.strip()
    p = store.create({"topic": text.splitlines()[0][:80] if text else "Own script", "own_script": text})
    try:
        sb = json.loads(text)   # a finished storyboard JSON skips the AI completely
        if isinstance(sb, dict) and sb.get("shots"):
            p = store.load(p["id"])
            p["storyboard"], p["state"] = normalize(sb), "storyboard"
            _check(p)
            store.save(p)
            return RedirectResponse(f"/p/{p['id']}", 303)
    except ValueError:
        pass
    run_bg(p["id"], "Rejissyor", step_own)
    return RedirectResponse(f"/p/{p['id']}", 303)


@app.get("/p/{pid}", response_class=HTMLResponse, dependencies=[Depends(panel_auth)])
def project(request: Request, pid: str):
    try:
        p = store.load(pid)
    except (KeyError, FileNotFoundError):
        raise HTTPException(404)
    sb = p.get("storyboard")
    rows = []
    if sb:
        lines = {ln["id"]: ln for ln in sb["lines"]}
        for i, (sh, t) in enumerate(zip(sb["shots"], timeline(sb)), 1):
            rows.append({"n": i, "a": (t["start"] - 1) / 30, "b": (t["end"] - 1) / 30, "sh": sh,
                         "line": lines.get(sh.get("line"))})
    video = (store.project_dir(pid) / "video.mp4").exists()
    return page(request, "project.html", p=p, rows=rows, video=video,
                seconds=total_seconds(sb) if sb else 0,
                sb_json=json.dumps(sb, ensure_ascii=False, indent=1) if sb else "",
                tts_provider=config.TTS_PROVIDER)


@app.post("/p/{pid}/do/{action}", dependencies=[Depends(panel_auth)])
async def project_action(pid: str, action: str, request: Request):
    form = await request.form()
    p = store.load(pid)
    go = RedirectResponse(f"/p/{pid}", 303)
    if p.get("busy"):
        return go
    if action == "hooks":
        run_bg(pid, "Hook", step_hooks)
    elif action == "pick_hook":
        custom = (form.get("custom") or "").strip()
        p["hook"] = {"text_hook": custom, "spoken_hook": custom, "premise": custom} if custom \
            else p["hooks"][int(form.get("i", 0))]
        store.save(p)
        run_bg(pid, "Ssenariy", step_script)
    elif action == "script":
        run_bg(pid, "Ssenariy", step_script)
    elif action == "save_script":
        p["script"] = json.loads(form.get("script_json") or "{}")
        store.save(p)
    elif action == "direct":
        run_bg(pid, "Rejissyor", step_direct)
    elif action == "save_storyboard":
        try:
            p["storyboard"] = normalize(json.loads(form.get("sb_json") or "{}"))
            p["error"] = None
            if p["state"] in ("voiced", "done", "failed"):
                p["state"] = "storyboard"
            _check(p)
        except ValueError as e:
            p["error"] = f"JSON xato: {e}"
        store.save(p)
    elif action == "review":
        run_bg(pid, "Tekshiruvchi", step_review)
    elif action == "revise":
        run_bg(pid, "Tuzatish", step_revise)
    elif action == "voice":
        run_bg(pid, "Ovoz", step_voice)
    elif action == "queue":
        if _check(p)["errors"]:
            p["error"] = "Tekshiruvchi xatolarini tuzating, keyin renderga yuboring"
        elif p["state"] not in ("voiced", "done", "failed", "rendering"):
            p["error"] = "Avval ovoz yarating"
        else:
            p["state"], p["error"], p["agent_msg"] = "queued", None, "Noutbuk agentini kutyapti"
        store.save(p)
    elif action == "delete":
        store.delete(pid)
        return RedirectResponse("/", 303)
    return go


@app.get("/p/{pid}/audio/{name}", dependencies=[Depends(panel_auth)])
def project_audio(pid: str, name: str):
    return _audio(pid, name)


@app.get("/p/{pid}/video.mp4", dependencies=[Depends(panel_auth)])
def project_video(pid: str):
    f = store.project_dir(pid) / "video.mp4"
    if not f.exists():
        raise HTTPException(404)
    p = store.load(pid)
    return FileResponse(f, media_type="video/mp4", filename=f"{p['storyboard']['video_name']}.mp4")


@app.get("/p/{pid}/script.py", dependencies=[Depends(panel_auth)])
def project_script(pid: str):
    p = store.load(pid)
    return HTMLResponse(blender_script.generate(p["storyboard"]), media_type="text/plain")


@app.get("/settings", response_class=HTMLResponse, dependencies=[Depends(panel_auth)])
def settings(request: Request):
    return page(request, "settings.html", c=config, free=llm.free_models() if config.OPENROUTER_API_KEY else [],
                usage=store.usage_today(), vocab_text=vocab.vocabulary_text())


@app.get("/voices", response_class=HTMLResponse, dependencies=[Depends(panel_auth)])
def voices(request: Request):
    chosen = {sp: tts.edge_voice(sp) for sp in vocab.VOICES}
    return page(request, "voices.html", chosen=chosen, choices=vocab.VOICE_CHOICES, moods=list(vocab.MOODS),
                provider=config.TTS_PROVIDER, sample_text=tts.SAMPLE)


@app.get("/voices/sample.mp3", dependencies=[Depends(panel_auth)])
def voice_sample(voice: str, mood: str = "normal"):
    try:
        path = tts.sample(voice, mood, config.DATA_DIR / "voice_samples")
    except tts.TTSError as e:
        raise HTTPException(400, str(e))
    return FileResponse(path, media_type="audio/mpeg")


@app.post("/voices", dependencies=[Depends(panel_auth)])
async def voices_save(request: Request):
    form = await request.form()
    st = store.settings()
    st["voices"] = {sp: form[sp] for sp in vocab.VOICES if form.get(sp) in vocab.VOICE_CHOICES}
    store.save_settings(st)
    return RedirectResponse("/voices?saved=1", 303)


def _audio(pid, name):
    if "/" in name or "\\" in name or not name.endswith(".mp3"):
        raise HTTPException(404)
    f = store.project_dir(pid) / "audio" / name
    if not f.exists():
        raise HTTPException(404)
    return FileResponse(f, media_type="audio/mpeg")


# ------------------------------ render agent API ------------------------------

@app.get("/api/agent/next", dependencies=[Depends(agent_auth)])
def agent_next():
    queued = [p for p in store.all_projects() if p["state"] == "queued"]
    if not queued:
        return JSONResponse({"job": None})
    p = sorted(queued, key=lambda p: p["updated"])[0]
    p["state"], p["agent_msg"] = "rendering", "Agent oldi"
    store.save(p)
    sb = p["storyboard"]
    return {"job": {"id": p["id"], "video_name": sb["video_name"], "seconds": total_seconds(sb),
                    "script": blender_script.generate(sb, audio_dir="studio_audio/" + p["id"]),
                    "audio": [ln["file"] for ln in sb["lines"] if ln.get("file")]}}


@app.get("/api/agent/{pid}/audio/{name}", dependencies=[Depends(agent_auth)])
def agent_audio(pid: str, name: str):
    return _audio(pid, name)


@app.post("/api/agent/{pid}/status", dependencies=[Depends(agent_auth)])
async def agent_status(pid: str, request: Request):
    data = await request.json()
    p = store.load(pid)
    p["agent_msg"] = str(data.get("message", ""))[:500]
    if data.get("state") == "failed":
        p["state"], p["error"] = "failed", "Render: " + p["agent_msg"]
    store.save(p)
    return {"ok": True}


@app.post("/api/agent/{pid}/video", dependencies=[Depends(agent_auth)])
async def agent_video(pid: str, file: UploadFile = File(...)):
    d = store.project_dir(pid)
    tmp = d / "video.part"
    with tmp.open("wb") as out:
        while chunk := await file.read(1 << 20):
            out.write(chunk)
    tmp.replace(d / "video.mp4")
    p = store.load(pid)
    p["state"], p["agent_msg"] = "done", "Tayyor"
    store.save(p)
    return {"ok": True}

"""Shorts Studio web panel.  Run:  uvicorn app:app --reload  then open http://127.0.0.1:8000"""

import json
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from studio import config, pipeline, trends
from studio.script import ShortScript, fact_check, suggest_topics, write_script

app = FastAPI(title="Shorts Studio")
app.mount("/output", StaticFiles(directory=config.OUTPUT_DIR), name="output")

STATIC = Path(__file__).parent / "static"
executor = ThreadPoolExecutor(max_workers=1)  # one render at a time keeps the machine responsive
jobs: dict[str, dict] = {}
lock = threading.Lock()


class IdeasRequest(BaseModel):
    niche: str = ""
    trending: list[str] = []


class TrendsRequest(BaseModel):
    niche: str = ""


class ScriptRequest(BaseModel):
    topic: str
    seconds: int = 35
    factcheck: bool = True


class RenderRequest(BaseModel):
    script: ShortScript
    voice: str = config.DEFAULT_EDGE_VOICE
    rate: str = "+12%"
    music: bool = True
    series: str = ""


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/config")
def get_config():
    voices = dict(config.EDGE_VOICES)
    if config.ELEVENLABS_API_KEY:
        voices = {"ElevenLabs (eng jonli)": "elevenlabs", **voices}
    music = [p for p in config.MUSIC_DIR.rglob("*") if p.suffix.lower() in pipeline.AUDIO_EXT]
    return {
        "voices": voices,
        "claude": bool(config.ANTHROPIC_API_KEY),
        "pexels": bool(config.PEXELS_API_KEY),
        "youtube": bool(config.YOUTUBE_API_KEY),
        "elevenlabs": bool(config.ELEVENLABS_API_KEY),
        "music_tracks": len(music),
    }


@app.post("/api/trends")
def get_trends(req: TrendsRequest):
    try:
        return trends.outliers(req.niche)
    except Exception as e:  # surface API/key problems to the panel
        raise HTTPException(500, str(e))


@app.post("/api/ideas")
def ideas(req: IdeasRequest):
    try:
        return [i.model_dump() for i in suggest_topics(req.niche, trending=req.trending)]
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/script")
def script(req: ScriptRequest):
    try:
        draft = write_script(req.topic, req.seconds)
        if not req.factcheck:
            return {"script": draft.model_dump(), "checks": []}
        checked = fact_check(draft)
        return {"script": checked.script.model_dump(), "checks": [c.model_dump() for c in checked.checks]}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/render")
def render(req: RenderRequest):
    job_id = uuid.uuid4().hex[:10]
    job_dir = pipeline.new_job_dir(req.script.topic)
    with lock:
        jobs[job_id] = {"status": "queued", "step": "Navbatda...", "progress": 0.0, "dir": job_dir.name}

    def progress(step: str, pct: float):
        with lock:
            jobs[job_id].update(status="running", step=step, progress=pct)

    def work():
        try:
            pipeline.make_video(req.script, job_dir, voice=req.voice, rate=req.rate, music=req.music,
                                series=req.series.strip(), progress=progress)
            with lock:
                jobs[job_id].update(status="done", step="Tayyor!", progress=1.0)
        except Exception as e:
            with lock:
                jobs[job_id].update(status="error", step=str(e)[:600])

    executor.submit(work)
    return {"job_id": job_id}


@app.get("/api/jobs/{job_id}")
def job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, "job not found")
    with lock:
        return dict(jobs[job_id])


@app.get("/api/videos")
def videos():
    out = []
    for d in sorted(config.OUTPUT_DIR.iterdir(), reverse=True):
        meta = d / "meta.json"
        if d.is_dir() and (d / "video.mp4").exists() and meta.exists():
            out.append({"dir": d.name, **json.loads(meta.read_text())})
    return out

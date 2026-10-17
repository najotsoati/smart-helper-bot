"""Shorts Studio web panel.  Run:  uvicorn app:app  then open http://127.0.0.1:8000"""

import json
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from studio import config, db, health, jobs, learn, pipeline, trends, youtube
from studio.script import ShortScript, suggest_topics, try_fact_check, write_script


@asynccontextmanager
async def lifespan(_app: FastAPI):
    jobs.start()
    yield


app = FastAPI(title="Shorts Studio", lifespan=lifespan)
app.mount("/output", StaticFiles(directory=config.OUTPUT_DIR), name="output")
STATIC = Path(__file__).parent / "static"


class Settings(BaseModel):
    voice: str = config.DEFAULT_EDGE_VOICE
    rate: str = "+12%"
    music: bool = True
    series: str = ""
    visual_mode: str = "mixed"  # mixed | illustration | stock
    host: bool = True
    ab: bool = False  # also render the runner-up hook as video_b.mp4
    upload: bool = False
    seconds: int = 35
    factcheck: bool = True


class TopicRequest(BaseModel):
    niche: str = ""
    trending: list[str] = []


class ScriptRequest(BaseModel):
    topic: str
    seconds: int = 35
    factcheck: bool = True


class RenderRequest(BaseModel):
    script: ShortScript
    settings: Settings = Settings()


class Schedule(BaseModel):
    start: str = ""  # YYYY-MM-DD, empty = today
    per_day: int = 1
    times: list[str] = ["18:00"]


class BatchRequest(BaseModel):
    topics: list[str]
    settings: Settings = Settings()
    schedule: Schedule | None = None


class KeyUpdate(BaseModel):
    name: str
    value: str = ""


class ClientSecret(BaseModel):
    content: str


def local_only(request: Request) -> None:
    """Secrets can only be changed from the computer the panel runs on."""
    host = request.client.host if request.client else ""
    if host not in ("127.0.0.1", "::1", "localhost"):
        raise HTTPException(403, "Kalitlarni faqat panel ishlayotgan kompyuterning o'zidan o'zgartirish mumkin")


class VideoRef(BaseModel):
    dir: str
    variant: str = "a"
    publish_at: str = ""  # ISO datetime, empty = upload now as private
    url: str = ""


def _guard(fn, *args, **kwargs):
    """Run a call and turn any failure into an error message the panel can show."""
    try:
        return fn(*args, **kwargs)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, health.explain(e))


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
        "claude": bool(config.llm_provider()),
        "llm": config.llm_provider(),
        "pexels": bool(config.PEXELS_API_KEY or config.PIXABAY_API_KEY),
        "youtube": bool(config.YOUTUBE_API_KEY),
        "elevenlabs": bool(config.ELEVENLABS_API_KEY),
        "openai": bool(config.OPENAI_API_KEY),
        "channel": youtube.connected(),
        "channel_status": youtube.status(),
        "client_secret": youtube.CLIENT_SECRET.exists(),
        "match_threshold": config.MATCH_THRESHOLD,
        "music_tracks": len(music),
    }


@app.post("/api/check")
def check():
    return health.run_all()


@app.get("/api/keys")
def keys():
    return [
        {"name": k, "label": label, "help": url, "set": bool(getattr(config, k)), "masked": config.masked(k)}
        for k, (label, url) in config.EDITABLE_KEYS.items()
    ]


@app.post("/api/keys", dependencies=[Depends(local_only)])
def save_key(req: KeyUpdate):
    if req.name not in config.EDITABLE_KEYS:
        raise HTTPException(400, "Noma'lum kalit")
    config.save_key(req.name, req.value)
    return {"saved": True, "check": health.run_for_key(req.name) if req.value.strip() else None}


@app.post("/api/youtube/client_secret", dependencies=[Depends(local_only)])
def upload_client_secret(req: ClientSecret):
    _guard(youtube.save_client_secret, req.content.encode())
    return {"saved": True}


@app.post("/api/trends")
def get_trends(req: TopicRequest):
    return _guard(trends.outliers, req.niche)


@app.post("/api/ideas")
def ideas(req: TopicRequest):
    return _guard(lambda: [i.model_dump() for i in suggest_topics(req.niche, trending=req.trending)])


@app.post("/api/script")
def script(req: ScriptRequest):
    def work():
        draft = write_script(req.topic, req.seconds)
        if not req.factcheck:
            return {"script": draft.model_dump(), "checks": [], "warning": ""}
        checked, checks, warning = try_fact_check(draft)
        return {"script": checked.model_dump(), "checks": [c.model_dump() for c in checks], "warning": warning}

    return _guard(work)


@app.post("/api/render")
def render(req: RenderRequest):
    return {"job_id": jobs.submit(req.script.topic, req.settings.model_dump(), script=req.script.model_dump())}


@app.post("/api/batch")
def batch(req: BatchRequest):
    topics = [t.strip() for t in req.topics if t.strip()]
    if not topics:
        raise HTTPException(400, "Mavzular ro'yxati bo'sh")
    if req.settings.upload and req.schedule and not youtube.connected():
        raise HTTPException(400, "Rejalashtirish uchun avval YouTube kanalini ulang")
    schedule = req.schedule.model_dump() if req.schedule else None
    return {"batch_id": jobs.submit_batch(topics, req.settings.model_dump(), schedule)}


@app.get("/api/jobs/{job_id}")
def job(job_id: str):
    row = db.get_job(job_id)
    if not row:
        raise HTTPException(404, "job not found")
    return {k: row[k] for k in ("id", "topic", "status", "step", "progress", "dir", "batch_id")}


@app.get("/api/jobs")
def job_list(limit: int = 40):
    rows = db.query("SELECT id, batch_id, topic, status, step, progress, dir, params, created FROM jobs "
                    "ORDER BY created DESC LIMIT ?", (limit,))
    for r in rows:
        r["publish_at"] = json.loads(r.pop("params") or "{}").get("publish_at")
    return rows


@app.get("/api/videos")
def videos():
    uploads = {(r["dir"], r["variant"]): r for r in db.query("SELECT * FROM videos")}
    out = []
    for d in sorted(config.OUTPUT_DIR.iterdir(), reverse=True):
        if not d.is_dir() or d.name.startswith("."):
            continue
        for variant, suffix in (("a", ""), ("b", "_b")):
            meta, video = d / f"meta{suffix}.json", d / f"video{suffix}.mp4"
            if not (meta.exists() and video.exists()):
                continue
            up = uploads.get((d.name, variant), {})
            out.append({
                "dir": d.name, "variant": variant, "video": f"/output/{d.name}/{video.name}",
                "cover": f"/output/{d.name}/cover{suffix}.jpg", **json.loads(meta.read_text()),
                "youtube_id": up.get("youtube_id"), "publish_at": up.get("publish_at"),
                "metrics": json.loads(up["metrics"]) if up.get("metrics") else None,
            })
    return out


@app.post("/api/youtube/connect", dependencies=[Depends(local_only)])
def yt_connect():
    return {"channel": _guard(youtube.connect)}


@app.post("/api/youtube/upload")
def yt_upload(ref: VideoRef):
    suffix = "" if ref.variant == "a" else f"_{ref.variant}"
    folder = config.OUTPUT_DIR / ref.dir
    if not (folder / f"video{suffix}.mp4").exists():
        raise HTTPException(404, "video topilmadi")
    meta = json.loads((folder / f"meta{suffix}.json").read_text())
    # browsers send "...Z", which datetime.fromisoformat only accepts from Python 3.11
    publish_at = datetime.fromisoformat(ref.publish_at.replace("Z", "+00:00")).astimezone() if ref.publish_at else None
    vid = _guard(youtube.upload, folder / f"video{suffix}.mp4", meta, publish_at)
    db.save_video(ref.dir, ref.variant, youtube_id=vid, publish_at=ref.publish_at or None,
                  uploaded=datetime.now().timestamp())
    return {"youtube_id": vid}


@app.post("/api/youtube/link")
def yt_link(ref: VideoRef):
    """Attach a video you uploaded by hand, so its analytics are tracked too."""
    vid = _guard(youtube.parse_video_id, ref.url)
    db.save_video(ref.dir, ref.variant, youtube_id=vid)
    return {"youtube_id": vid}


@app.post("/api/youtube/refresh")
def yt_refresh():
    return {"updated": _guard(youtube.refresh_all_metrics)}


@app.post("/api/learn")
def learn_now():
    return _guard(learn.update_playbook)


@app.get("/api/playbook")
def playbook():
    return db.latest_playbook() or {}

"""Background job queue backed by SQLite: single videos and batches (topic -> script -> fact-check ->
render -> optional A/B variant -> optional upload/schedule). Queued jobs survive a server restart."""

import json
import threading
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from . import config, db, pipeline, youtube
from .script import ShortScript, try_fact_check, write_script

_executor = ThreadPoolExecutor(max_workers=1)  # one render at a time keeps the machine responsive
_started = threading.Event()


def start() -> None:
    """Create tables and re-queue jobs that were waiting when the server stopped."""
    if _started.is_set():
        return
    _started.set()
    db.init()
    for row in db.query("SELECT id FROM jobs WHERE status='queued' ORDER BY created"):
        _executor.submit(_run, row["id"])


def submit(topic: str, settings: dict, script: dict | None = None, batch_id: str | None = None,
           publish_at: str | None = None) -> str:
    job_id = uuid.uuid4().hex[:10]
    params = {"settings": settings, "script": script, "publish_at": publish_at}
    db.add_job(job_id, topic, params, batch_id)
    _executor.submit(_run, job_id)
    return job_id


def schedule_slots(count: int, start_day: str, per_day: int, times: list[str]) -> list[str]:
    """`count` publish times: `per_day` videos a day at the given local HH:MM times, from `start_day`."""
    times = sorted(times)[:per_day] or ["18:00"]
    day = datetime.fromisoformat(start_day) if start_day else datetime.now()
    now = datetime.now()
    slots = []
    while len(slots) < count:
        for hhmm in times:
            h, m = map(int, hhmm.split(":"))
            slot = day.replace(hour=h, minute=m, second=0, microsecond=0)
            if slot > now + timedelta(minutes=30) and len(slots) < count:
                slots.append(slot.astimezone().isoformat())
        day += timedelta(days=1)
    return slots


def submit_batch(topics: list[str], settings: dict, schedule: dict | None = None) -> str:
    batch_id = uuid.uuid4().hex[:8]
    slots = schedule_slots(len(topics), schedule.get("start", ""), schedule.get("per_day", 1),
                           schedule.get("times", ["18:00"])) if schedule else [None] * len(topics)
    for topic, slot in zip(topics, slots):
        submit(topic, settings, batch_id=batch_id, publish_at=slot)
    return batch_id


def _run(job_id: str) -> None:
    job = db.get_job(job_id)
    if not job or job["status"] != "queued":
        return
    params, settings = job["params"], job["params"]["settings"]

    def progress(step: str, pct: float):
        db.update_job(job_id, status="running", step=step, progress=pct)

    warning = ""
    try:
        if params.get("script"):
            script = ShortScript.model_validate(params["script"])
        else:
            progress("Ssenariy yozilmoqda...", 0.01)
            script = write_script(job["topic"], settings.get("seconds", 35))
            if settings.get("factcheck", True):
                progress("Faktlar internetdan tekshirilmoqda...", 0.02)
                script, _, warning = try_fact_check(script)

        job_dir = pipeline.new_job_dir(script.topic)
        db.update_job(job_id, dir=job_dir.name)
        render_args = dict(
            voice=settings.get("voice") or config.DEFAULT_EDGE_VOICE,
            rate=settings.get("rate", "+12%"),
            music=settings.get("music", True),
            series=settings.get("series", "").strip(),
            visual_mode=settings.get("visual_mode", "mixed"),
            host=settings.get("host", True),
        )
        video = pipeline.make_video(script, job_dir, progress=progress, **render_args)
        db.save_video(job_dir.name, "a")
        voice_note = json.loads((job_dir / "meta.json").read_text()).get("voice_note")
        if voice_note:
            warning = f"{warning} ⚠ {voice_note}".strip()

        variant_b = pipeline.hook_variant(script) if settings.get("ab") else None
        if variant_b:
            progress("A/B: ikkinchi hook bilan variant yasalmoqda...", 0.9)
            plan = json.loads((job_dir / "plan.json").read_text())
            pipeline.make_video(variant_b, job_dir, plan=plan, variant="b", progress=lambda s, p: None,
                                **render_args)
            db.save_video(job_dir.name, "b")

        if settings.get("upload"):
            progress("YouTube'ga yuklanmoqda...", 0.95)
            publish_at = (datetime.fromisoformat(params["publish_at"].replace("Z", "+00:00"))
                          if params.get("publish_at") else None)
            meta = json.loads((job_dir / "meta.json").read_text())
            vid = youtube.upload(video, meta, publish_at)
            db.save_video(job_dir.name, "a", youtube_id=vid, publish_at=params.get("publish_at"),
                          uploaded=datetime.now().timestamp())

        db.update_job(job_id, status="done", step=f"Tayyor! {warning}".strip(), progress=1.0)
    except Exception as e:
        traceback.print_exc()
        from .health import explain  # local import: health imports youtube, which imports db

        db.update_job(job_id, status="error", step=explain(e)[:600])

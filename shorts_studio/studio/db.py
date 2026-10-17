"""SQLite store for jobs, uploaded videos and analytics, so nothing is lost when the server restarts."""

import json
import sqlite3
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from . import config

PATH = config.OUTPUT_DIR / "studio.db"
_lock = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    batch_id TEXT,
    topic TEXT,
    status TEXT,          -- queued | running | done | error
    step TEXT,
    progress REAL DEFAULT 0,
    dir TEXT,
    params TEXT,          -- JSON: render settings, script, schedule
    created REAL,
    updated REAL
);
CREATE TABLE IF NOT EXISTS videos (
    dir TEXT,
    variant TEXT DEFAULT 'a',
    youtube_id TEXT,
    publish_at TEXT,
    uploaded REAL,
    metrics TEXT,         -- JSON from YouTube Analytics
    metrics_updated REAL,
    PRIMARY KEY (dir, variant)
);
CREATE TABLE IF NOT EXISTS playbook (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created REAL,
    data TEXT             -- JSON: what works on this channel
);
"""


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        with conn:  # commit on success, roll back on error
            yield conn
    finally:
        conn.close()


def init() -> None:
    with _lock, _connect() as conn:
        conn.executescript(SCHEMA)
        # anything "running" when the server stopped can't be resumed mid-render
        conn.execute(
            "UPDATE jobs SET status='error', step='Server qayta ishga tushdi, ishni qaytadan boshlang' "
            "WHERE status='running'"
        )


def execute(sql: str, args: tuple = ()) -> None:
    with _lock, _connect() as conn:
        conn.execute(sql, args)


def query(sql: str, args: tuple = ()) -> list[dict[str, Any]]:
    with _lock, _connect() as conn:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]


def add_job(job_id: str, topic: str, params: dict, batch_id: str | None = None, dir_name: str = "") -> None:
    now = time.time()
    execute(
        "INSERT INTO jobs (id, batch_id, topic, status, step, progress, dir, params, created, updated) "
        "VALUES (?, ?, ?, 'queued', 'Navbatda...', 0, ?, ?, ?, ?)",
        (job_id, batch_id, topic, dir_name, json.dumps(params), now, now),
    )


def update_job(job_id: str, **fields) -> None:
    fields["updated"] = time.time()
    cols = ", ".join(f"{k}=?" for k in fields)
    execute(f"UPDATE jobs SET {cols} WHERE id=?", (*fields.values(), job_id))


def get_job(job_id: str) -> dict | None:
    rows = query("SELECT * FROM jobs WHERE id=?", (job_id,))
    if not rows:
        return None
    row = rows[0]
    row["params"] = json.loads(row["params"] or "{}")
    return row


def save_video(dir_name: str, variant: str, **fields) -> None:
    existing = query("SELECT 1 FROM videos WHERE dir=? AND variant=?", (dir_name, variant))
    if not existing:
        execute("INSERT INTO videos (dir, variant) VALUES (?, ?)", (dir_name, variant))
    if fields:
        cols = ", ".join(f"{k}=?" for k in fields)
        execute(f"UPDATE videos SET {cols} WHERE dir=? AND variant=?", (*fields.values(), dir_name, variant))


def latest_playbook() -> dict | None:
    rows = query("SELECT data, created FROM playbook ORDER BY id DESC LIMIT 1")
    return {**json.loads(rows[0]["data"]), "created": rows[0]["created"]} if rows else None

"""Your YouTube channel: OAuth connection, uploads with scheduling, and per-video analytics.

Setup (once): Google Cloud console -> APIs & Services -> enable "YouTube Data API v3" and
"YouTube Analytics API" -> Credentials -> Create OAuth client ID -> "Desktop app" -> download JSON as
shorts_studio/client_secret.json. Then press "Kanalni ulash" in the panel.

Note: until your API project passes YouTube's free API audit, videos uploaded through the API are locked
to private. Uploading still works (you publish them in YouTube Studio); scheduling needs the audit."""

import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from . import config, db

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]
CLIENT_SECRET = config.ROOT / "client_secret.json"
TOKEN = config.ROOT / "youtube_token.json"
METRICS = "views,engagedViews,averageViewPercentage,averageViewDuration,likes,comments,shares,subscribersGained"
FALLBACK_METRICS = "views,averageViewPercentage,averageViewDuration,likes,comments,shares,subscribersGained"


def _credentials() -> Credentials | None:
    if not TOKEN.exists():
        return None
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json())
    return creds if creds.valid else None


def connect() -> str:
    """Opens the Google consent page in the browser (run the panel on your own computer)."""
    if not CLIENT_SECRET.exists():
        raise RuntimeError("client_secret.json topilmadi (README'dagi 'YouTube kanalini ulash' bo'limiga qarang)")
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
    creds = flow.run_local_server(port=0, open_browser=True)
    TOKEN.write_text(creds.to_json())
    return channel()["title"]


def connected() -> bool:
    try:
        return _credentials() is not None
    except Exception:
        return False


def _youtube():
    creds = _credentials()
    if not creds:
        raise RuntimeError("YouTube kanali ulanmagan")
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def channel() -> dict:
    items = _youtube().channels().list(part="snippet,statistics", mine=True).execute().get("items", [])
    if not items:
        raise RuntimeError("Bu Google hisobida YouTube kanali yo'q")
    c = items[0]
    return {"id": c["id"], "title": c["snippet"]["title"], "subscribers": c["statistics"].get("subscriberCount")}


def upload(video: Path, meta: dict, publish_at: datetime | None = None) -> str:
    """Upload a finished video. With `publish_at` it's scheduled (private until then). Returns the video id."""
    tags = re.findall(r"#(\w+)", meta.get("description", ""))
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": False}
    if publish_at:
        status["publishAt"] = publish_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    body = {
        "snippet": {
            "title": meta["title"][:100],
            "description": meta.get("description", "")[:5000],
            "tags": tags[:15],
            "categoryId": "27",  # Education
        },
        "status": status,
    }
    request = _youtube().videos().insert(
        part="snippet,status", body=body, media_body=MediaFileUpload(str(video), chunksize=-1, resumable=True)
    )
    response = None
    while response is None:
        _, response = request.next_chunk()
    return response["id"]


def parse_video_id(url_or_id: str) -> str:
    m = re.search(r"(?:shorts/|v=|youtu\.be/)([\w-]{11})", url_or_id)
    if m:
        return m.group(1)
    if re.fullmatch(r"[\w-]{11}", url_or_id.strip()):
        return url_or_id.strip()
    raise ValueError("YouTube havolasini tanib bo'lmadi")


def fetch_metrics(video_ids: list[str], since: date | None = None) -> dict[str, dict]:
    """Lifetime analytics per video (YouTube Analytics lags ~2 days behind)."""
    if not video_ids:
        return {}
    creds = _credentials()
    if not creds:
        raise RuntimeError("YouTube kanali ulanmagan")
    analytics = build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False)
    start = (since or date.today() - timedelta(days=365)).isoformat()
    out: dict[str, dict] = {}
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i + 50]
        for metrics in (METRICS, FALLBACK_METRICS):  # engagedViews isn't available on every channel
            try:
                resp = analytics.reports().query(
                    ids="channel==MINE", startDate=start, endDate=date.today().isoformat(),
                    metrics=metrics, dimensions="video", filters="video==" + ",".join(chunk),
                ).execute()
                break
            except Exception:
                if metrics == FALLBACK_METRICS:
                    raise
        headers = [h["name"] for h in resp.get("columnHeaders", [])]
        for row in resp.get("rows", []):
            rec = dict(zip(headers, row))
            vid = rec.pop("video")
            if rec.get("views") and rec.get("engagedViews") is not None:
                # share of people who kept watching instead of swiping away
                rec["stayedToWatch"] = round(100 * rec["engagedViews"] / rec["views"], 1)
            out[vid] = rec
    return out


def refresh_all_metrics() -> int:
    rows = db.query("SELECT dir, variant, youtube_id FROM videos WHERE youtube_id IS NOT NULL")
    metrics = fetch_metrics([r["youtube_id"] for r in rows])
    now = datetime.now().timestamp()
    for r in rows:
        if r["youtube_id"] in metrics:
            db.save_video(r["dir"], r["variant"], metrics=json.dumps(metrics[r["youtube_id"]]), metrics_updated=now)
    return len(metrics)

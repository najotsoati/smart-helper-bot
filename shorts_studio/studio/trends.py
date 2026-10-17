"""Find "outlier" Shorts: recent videos with far more views than their channel has subscribers.
Needs a free YouTube Data API v3 key (https://console.cloud.google.com -> APIs -> YouTube Data API v3)."""

from datetime import datetime, timedelta, timezone

from . import config, net

API = "https://www.googleapis.com/youtube/v3"


def _get(path: str, **params) -> dict:
    return net.request("GET", f"{API}/{path}", params={**params, "key": config.YOUTUBE_API_KEY}, timeout=30).json()


def outliers(niche: str, days: int = 30, limit: int = 12) -> list[dict]:
    if not config.YOUTUBE_API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY is not set (add it to shorts_studio/.env)")
    after = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    search = _get(
        "search", part="snippet", q=f"{niche or 'facts'} #shorts", type="video", videoDuration="short",
        order="viewCount", publishedAfter=after, relevanceLanguage="en", maxResults=50,
    )
    ids = [item["id"]["videoId"] for item in search.get("items", [])]
    if not ids:
        return []
    videos = _get("videos", part="snippet,statistics", id=",".join(ids))["items"]
    channel_ids = sorted({v["snippet"]["channelId"] for v in videos})
    subs = {
        c["id"]: int(c["statistics"].get("subscriberCount", 0) or 0)
        for c in _get("channels", part="statistics", id=",".join(channel_ids[:50]))["items"]
    }
    rows = []
    for v in videos:
        views = int(v["statistics"].get("viewCount", 0))
        channel_subs = subs.get(v["snippet"]["channelId"], 0)
        rows.append({
            "title": v["snippet"]["title"],
            "channel": v["snippet"]["channelTitle"],
            "views": views,
            "subscribers": channel_subs,
            # views per subscriber; floor at 1k subs so brand-new channels don't dominate on noise
            "score": round(views / max(channel_subs, 1000), 1),
            "url": f"https://www.youtube.com/shorts/{v['id']}",
            "thumbnail": v["snippet"]["thumbnails"].get("high", v["snippet"]["thumbnails"]["default"])["url"],
        })
    rows.sort(key=lambda r: r["score"], reverse=True)
    return rows[:limit]

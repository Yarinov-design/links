import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API_KEY = os.environ["YOUTUBE_API_KEY"]
HANDLE = os.environ.get("YOUTUBE_HANDLE", "@Yarinov_Clips2009")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "assets", "youtube-data.json")

def get_json(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

def api_url(endpoint, **params):
    params["key"] = API_KEY
    return f"https://www.googleapis.com/youtube/v3/{endpoint}?" + urllib.parse.urlencode(params)

def parse_iso_duration(duration):
    # Simple ISO8601 parser for PT#H#M#S
    hours = minutes = seconds = 0
    num = ""
    time_part = duration.split("T", 1)[-1] if "T" in duration else duration
    for ch in time_part:
        if ch.isdigit():
            num += ch
        else:
            if ch == "H":
                hours = int(num or 0)
            elif ch == "M":
                minutes = int(num or 0)
            elif ch == "S":
                seconds = int(num or 0)
            num = ""
    total = hours * 3600 + minutes * 60 + seconds
    if hours:
        label = f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        label = f"{minutes}:{seconds:02d}"
    return total, label

def main():
    channel = get_json(api_url(
        "channels",
        part="snippet,contentDetails",
        forHandle=HANDLE
    ))
    if not channel.get("items"):
        raise SystemExit("Channel not found")

    channel_item = channel["items"][0]
    uploads_playlist = channel_item["contentDetails"]["relatedPlaylists"]["uploads"]
    channel_url = f"https://www.youtube.com/{HANDLE}"

    playlist_items = get_json(api_url(
        "playlistItems",
        part="snippet,contentDetails",
        playlistId=uploads_playlist,
        maxResults="18"
    ))

    items = playlist_items.get("items", [])
    video_ids = [
        item["contentDetails"]["videoId"]
        for item in items
        if item.get("contentDetails", {}).get("videoId")
    ]
    if not video_ids:
        payload = {
            "channel_handle": HANDLE,
            "channel_url": channel_url,
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "videos": [],
            "shorts": [],
        }
        with open(OUT_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return

    videos_data = get_json(api_url(
        "videos",
        part="contentDetails,snippet",
        id=",".join(video_ids[:18])
    ))

    details_by_id = {item["id"]: item for item in videos_data.get("items", [])}

    videos = []
    shorts = []

    for item in items:
        snippet = item.get("snippet", {})
        video_id = item.get("contentDetails", {}).get("videoId")
        if not video_id or video_id not in details_by_id:
            continue

        detail = details_by_id[video_id]
        duration_seconds, duration_label = parse_iso_duration(
            detail.get("contentDetails", {}).get("duration", "PT0S")
        )

        thumb = (
            snippet.get("thumbnails", {}).get("high", {}).get("url")
            or snippet.get("thumbnails", {}).get("medium", {}).get("url")
            or snippet.get("thumbnails", {}).get("default", {}).get("url")
            or f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
        )

        entry = {
            "id": video_id,
            "title": snippet.get("title", ""),
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "short_url": f"https://www.youtube.com/shorts/{video_id}",
            "thumbnail": thumb,
            "published": snippet.get("publishedAt", ""),
            "duration": duration_label,
            "seconds": duration_seconds,
        }

        title = (snippet.get("title") or "").lower()
        desc = (snippet.get("description") or "").lower()

        # Best-effort Shorts heuristic:
        # YouTube's Data API does not expose a dedicated "is_short" flag.
        if duration_seconds <= 180 and ("#shorts" in title or "#shorts" in desc):
            shorts.append(entry)
        else:
            videos.append(entry)

    payload = {
        "channel_handle": HANDLE,
        "channel_url": channel_url,
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "videos": videos[:3],
        "shorts": shorts[:3],
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()

"""Download a video link with yt-dlp (video + metadata + subtitles if present)."""
from __future__ import annotations

import json
from pathlib import Path


def download(url: str, out_dir: Path, *, max_height: int = 1080) -> tuple[Path, dict]:
    import yt_dlp

    out_dir.mkdir(parents=True, exist_ok=True)
    opts = {
        "format": f"bv*[height<={max_height}][ext=mp4]+ba[ext=m4a]/b[height<={max_height}]/b",
        "merge_output_format": "mp4",
        "outtmpl": str(out_dir / "source.%(ext)s"),
        "noplaylist": True,
        "writeinfojson": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en.*", "hi"],
        "subtitlesformat": "srt/vtt/best",
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
    video = out_dir / "source.mp4"
    if not video.exists():
        candidates = sorted(out_dir.glob("source.*"))
        candidates = [c for c in candidates if c.suffix not in {".json", ".srt", ".vtt"}]
        if not candidates:
            raise RuntimeError("yt-dlp finished but no video file was written")
        video = candidates[0]
    meta = {
        "id": info.get("id"),
        "title": info.get("title"),
        "uploader": info.get("uploader"),
        "duration": info.get("duration"),
        "webpage_url": info.get("webpage_url", url),
        "upload_date": info.get("upload_date"),
        "license": info.get("license"),
    }
    (out_dir / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return video, meta

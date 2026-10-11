#!/usr/bin/env python3
"""
Autonomous YouTube publishing pipeline.

Rules:
  - At most 2 videos per US calendar day at peak traffic:
      14:00 ET (weekday afternoon) and 20:00 ET (prime time).
  - Only videos with AI quality score >= 90 are uploaded.
  - One topic = one video, forever (sheet + in-batch).
  - Topic is taken ~90% from on-screen first-frame text or the first spoken
    sentence (audio clip), not from the filename.
  - Gemini writes SEO title, description, and tags.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import traceback
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import cv2
import pytz
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials as UserCredentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    genai = None


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "15jAt6HUoOrucNA-79y8u7hunq7vUUIBMrTOOeiG-618")
SHEET_RANGE = os.getenv("SHEET_RANGE", "Sheet1!A:L")
RAW_FOLDER_ID = os.getenv("RAW_FOLDER_ID", "1-YtW4xKp1qg1TzebJI5qlIjNKzuo_r_J")
PROCESSED_FOLDER_ID = os.getenv("PROCESSED_FOLDER_ID", "1ftCj1FCSAEdE3qD2HM_1R83zhCwUIiOf")

LOCAL_VIDEO_DIR = Path(os.getenv("LOCAL_VIDEO_DIR", "videos"))
WORK_DIR = Path(os.getenv("WORK_DIR", "work"))
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "client_secret.json")
YOUTUBE_TOKEN_FILE = os.getenv("YOUTUBE_TOKEN_FILE", "youtube_token.json")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
CHANNEL_NICHE = os.getenv("CHANNEL_NICHE", "personal finance and business")
MAX_VIDEOS_PER_DAY = int(os.getenv("MAX_VIDEOS_PER_DAY", "2"))
MIN_QUALITY_SCORE = int(os.getenv("MIN_QUALITY_SCORE", "90"))
DRY_RUN = os.getenv("DRY_RUN", "false").lower() in {"1", "true", "yes"}

# US YouTube peak traffic (America/New_York)
US_TZ = pytz.timezone("America/New_York")
DAY_SLOT_HOUR = int(os.getenv("DAY_SLOT_HOUR", "14"))    # 2:00 PM ET
NIGHT_SLOT_HOUR = int(os.getenv("NIGHT_SLOT_HOUR", "20"))  # 8:00 PM ET

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}

DRIVE_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

SHEET_HEADERS = [
    "Logged At (UTC)",
    "Source File",
    "Source Id",
    "Title",
    "Description",
    "Tags",
    "Topic",
    "Score",
    "Status",
    "Scheduled For (ET)",
    "YouTube Video ID",
    "Notes",
]


@dataclass
class VideoCandidate:
    name: str
    source: str
    path: Path | None = None
    drive_id: str | None = None
    topic: str = ""
    title: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    score: int = 0
    reason: str = ""
    skip: bool = False
    source_text: str = ""


@dataclass
class PipelineResult:
    title: str
    source_file: str
    status: str
    scheduled_et: str
    youtube_id: str
    notes: str


def load_service_account():
    if not Path(CREDENTIALS_FILE).exists():
        raise FileNotFoundError(
            f"{CREDENTIALS_FILE} missing. Write secrets.GOOGLE_CREDENTIALS_JSON to this file."
        )
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=DRIVE_SCOPES
    )
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)
    return sheets, drive


def load_youtube_client():
    token_json = os.getenv("YOUTUBE_TOKEN_JSON")
    if token_json:
        Path(YOUTUBE_TOKEN_FILE).write_text(token_json)
    if not Path(YOUTUBE_TOKEN_FILE).exists():
        print("⚠️  YouTube OAuth token missing — metadata will be logged without upload.")
        return None
    data = json.loads(Path(YOUTUBE_TOKEN_FILE).read_text())
    creds = UserCredentials.from_authorized_user_info(data, YOUTUBE_SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        Path(YOUTUBE_TOKEN_FILE).write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def ensure_sheet_headers(sheets) -> None:
    result = (
        sheets.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A1:L1")
        .execute()
    )
    values = result.get("values", [])
    if not values or values[0] != SHEET_HEADERS:
        sheets.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range="Sheet1!A1",
            valueInputOption="RAW",
            body={"values": [SHEET_HEADERS]},
        ).execute()


def normalize_topic(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    stop = {
        "the", "a", "an", "of", "and", "or", "to", "in", "on", "for", "with",
        "your", "you", "how", "why", "what", "this", "that",
    }
    words = [w for w in text.split() if w not in stop]
    return " ".join(words[:8])


def load_sheet_state(sheets) -> tuple[set[str], set[str]]:
    """Return (file/id/title keys, normalized topics already used)."""
    result = (
        sheets.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=SHEET_RANGE)
        .execute()
    )
    rows = result.get("values", [])[1:]
    keys: set[str] = set()
    topics: set[str] = set()
    for row in rows:
        while len(row) < 12:
            row.append("")
        status = row[8].upper()
        # Dry runs and failures must remain eligible for a later live retry.
        if status not in {"DRY_RUN", "FAILED"}:
            for idx in (1, 2, 3):
                if row[idx].strip():
                    keys.add(row[idx].strip().lower())
        topic_key = normalize_topic(row[6] or row[3])
        if topic_key and status not in {
            "IGNORED", "FAILED", "LOW_QUALITY", "DUPLICATE_TOPIC", "DRY_RUN"
        }:
            topics.add(topic_key)
    return keys, topics


def count_scheduled_for_date(sheets, et_date: str) -> int:
    result = (
        sheets.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=SHEET_RANGE)
        .execute()
    )
    rows = result.get("values", [])[1:]
    n = 0
    for row in rows:
        while len(row) < 12:
            row.append("")
        status = row[8].upper()
        scheduled = row[9]
        if status in {"SCHEDULED", "UPLOADED", "PUBLISHED"} and scheduled.startswith(et_date):
            n += 1
    return n


def append_sheet_row(sheets, row: list[str]) -> None:
    sheets.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="Sheet1!A1",
        valueInputOption="USER_ENTERED",
        body={"values": [row]},
    ).execute()


def list_drive_videos(drive) -> list[VideoCandidate]:
    query = f"'{RAW_FOLDER_ID}' in parents and mimeType contains 'video/' and trashed = false"
    items: list[dict] = []
    page_token = None
    while True:
        resp = (
            drive.files()
            .list(
                q=query,
                pageSize=50,
                fields="nextPageToken, files(id, name)",
                pageToken=page_token,
            )
            .execute()
        )
        items.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return [VideoCandidate(name=f["name"], source="drive", drive_id=f["id"]) for f in items]


def list_local_videos() -> list[VideoCandidate]:
    LOCAL_VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    out: list[VideoCandidate] = []
    for p in sorted(LOCAL_VIDEO_DIR.rglob("*")):
        if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS:
            out.append(VideoCandidate(name=p.name, source="local", path=p))
    return out


def download_drive_file(drive, file_id: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    request = drive.files().get_media(fileId=file_id)
    with dest.open("wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    return dest


def move_drive_to_processed(drive, file_id: str) -> None:
    drive.files().update(
        fileId=file_id,
        addParents=PROCESSED_FOLDER_ID,
        removeParents=RAW_FOLDER_ID,
        fields="id, parents",
    ).execute()


def extract_first_frame(video_path: Path, dest: Path) -> Path | None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video_path))
    ok, frame = cap.read()
    if not ok:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 24)
        ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        return None
    cv2.imwrite(str(dest), frame)
    return dest


def extract_audio_clip(video_path: Path, dest: Path, seconds: int = 20) -> Path | None:
    """First ~20s of audio for the opening spoken sentence / transcript."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-t", str(seconds), "-vn", "-ac", "1", "-ar", "16000",
        str(dest),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=60)
        if dest.exists() and dest.stat().st_size > 0:
            return dest
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as exc:
        print(f"  ⚠️  audio clip skipped: {exc}")
    return None


def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")
    if genai is None:
        raise ImportError("google-generativeai is not installed.")
    genai.configure(api_key=api_key)


def _parse_json_blob(text: str) -> dict[str, Any]:
    text = (text or "").strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    else:
        brace = re.search(r"\{.*\}", text, re.DOTALL)
        if brace:
            text = brace.group(0)
    return json.loads(text)


def analyze_video_with_gemini(
    candidate: VideoCandidate,
    frame_path: Path | None,
    audio_path: Path | None,
) -> VideoCandidate:
    configure_gemini()
    model = genai.GenerativeModel(GEMINI_MODEL)
    prompt = f"""You are a senior YouTube SEO strategist for a {CHANNEL_NICHE} channel (US audience).

PRIMARY EVIDENCE (use this for ~90% of the topic):
- On-screen text in the FIRST FRAME (OCR). Prefer the first sentence / hook text.
- The FIRST SPOKEN SENTENCE in the attached audio clip (transcript).
Filename is weak evidence only: {candidate.name}

Quality bar: score 0-100. Below {MIN_QUALITY_SCORE} means IGNORE (blurry, clickbait-only, off-niche, duplicate-feeling, no clear hook).

Return STRICT JSON only:
{{
  "source_text": "exact OCR line or first spoken sentence you used",
  "topic": "canonical 3-7 word topic derived from source_text",
  "title": "SEO title under 70 chars, numbers/curiosity, no spam CAPS",
  "description": "Hook paragraph, 2 value paragraphs, timestamps if useful, CTA, then 5 hashtags",
  "tags": ["up to 12 SEO tags"],
  "score": 0,
  "reason": "one sentence",
  "skip": false
}}
Set skip=true if quality is below the bar or topic cannot be read from frame/audio.
"""
    parts: list[Any] = [prompt]
    if frame_path and frame_path.exists():
        try:
            parts.append(genai.upload_file(str(frame_path), mime_type="image/jpeg"))
        except Exception as exc:
            print(f"  ⚠️  frame upload failed: {exc}")
    if audio_path and audio_path.exists():
        try:
            mime = "audio/mpeg" if audio_path.suffix.lower() == ".mp3" else "audio/wav"
            parts.append(genai.upload_file(str(audio_path), mime_type=mime))
        except Exception as exc:
            print(f"  ⚠️  audio upload failed: {exc}")

    response = model.generate_content(parts)
    data = _parse_json_blob(response.text or "{}")
    candidate.source_text = str(data.get("source_text") or "")
    candidate.topic = str(data.get("topic") or candidate.source_text or candidate.name)
    candidate.title = str(data.get("title") or candidate.topic)[:100]
    candidate.description = str(data.get("description") or candidate.topic)
    tags = data.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    candidate.tags = [str(t)[:30] for t in tags][:12]
    candidate.score = int(data.get("score") or 0)
    candidate.reason = str(data.get("reason") or "")
    candidate.skip = bool(data.get("skip")) or candidate.score < MIN_QUALITY_SCORE
    return candidate


def rank_sequence(candidates: list[VideoCandidate]) -> list[VideoCandidate]:
    ranked = sorted(candidates, key=lambda c: c.score, reverse=True)
    ordered: list[VideoCandidate] = []
    leftover = ranked[:]
    while leftover:
        if not ordered:
            ordered.append(leftover.pop(0))
            continue
        last = normalize_topic(ordered[-1].topic)
        pick_idx = 0
        for i, c in enumerate(leftover):
            if normalize_topic(c.topic) != last:
                pick_idx = i
                break
        ordered.append(leftover.pop(pick_idx))
    return ordered


def next_open_slots(already_today: int, now_et: datetime | None = None) -> list[datetime]:
    now_et = now_et or datetime.now(US_TZ)
    today = now_et.date()

    def slots_for(d) -> list[datetime]:
        day = US_TZ.localize(datetime(d.year, d.month, d.day, DAY_SLOT_HOUR, 0, 0))
        night = US_TZ.localize(datetime(d.year, d.month, d.day, NIGHT_SLOT_HOUR, 0, 0))
        return [day, night]

    remaining: list[datetime] = []
    future_today = [s for s in slots_for(today) if s > now_et + timedelta(minutes=15)]
    skip = already_today
    for s in future_today:
        if skip > 0:
            skip -= 1
            continue
        remaining.append(s)
    # Fill remaining daily quota on the next US day (still max 2 per day later).
    if len(remaining) < MAX_VIDEOS_PER_DAY:
        remaining.extend(slots_for(today + timedelta(days=1)))
    return remaining[:MAX_VIDEOS_PER_DAY]


def to_youtube_publish_at(et_dt: datetime) -> str:
    utc = et_dt.astimezone(timezone.utc)
    return utc.strftime("%Y-%m-%dT%H:%M:%SZ")


def upload_to_youtube(youtube, video_path: Path, candidate: VideoCandidate, publish_at_rfc3339: str) -> str:
    body = {
        "snippet": {
            "title": candidate.title[:100],
            "description": candidate.description[:5000],
            "tags": candidate.tags,
            "categoryId": "22",
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at_rfc3339,
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(str(video_path), chunksize=8 * 1024 * 1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"    upload {int(status.progress() * 100)}%")
    return response["id"]


def materialize_file(drive, candidate: VideoCandidate) -> Path:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    if candidate.source == "local" and candidate.path:
        return candidate.path
    dest = WORK_DIR / candidate.name
    print(f"  📥 Downloading Drive file {candidate.name} ...")
    return download_drive_file(drive, candidate.drive_id, dest)


def log_row(sheets, c: VideoCandidate, status: str, slot_label: str = "", yt_id: str = "", notes: str = "") -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    append_sheet_row(
        sheets,
        [
            now,
            c.name,
            c.drive_id or "",
            c.title,
            (c.description or "")[:500],
            ", ".join(c.tags),
            c.topic,
            str(c.score),
            status,
            slot_label,
            yt_id,
            notes or c.reason,
        ],
    )


def run() -> int:
    print("=" * 64)
    print("🚀 YouTube Auto-Publish  |  2/day US peaks  |  score>=90  |  1 topic")
    print("=" * 64)

    sheets, drive = load_service_account()
    youtube = None if DRY_RUN else load_youtube_client()
    if not DRY_RUN and youtube is None:
        raise RuntimeError(
            "YOUTUBE_TOKEN_JSON is required for a live publish run. "
            "Use the workflow dry_run input only when intentionally skipping uploads."
        )
    ensure_sheet_headers(sheets)

    logged, used_topics = load_sheet_state(sheets)
    print(f"📊 Known files: {len(logged)}  |  used topics: {len(used_topics)}")

    candidates = list_local_videos() + list_drive_videos()
    print(f"📁 Found {len(candidates)} video(s).")

    fresh: list[VideoCandidate] = []
    for c in candidates:
        if c.name.lower() in logged or (c.drive_id or "").lower() in logged:
            print(f"  ⏭️  duplicate file: {c.name}")
            continue
        fresh.append(c)

    if not fresh:
        print("⚠️  No new videos. Idle.")
        return 0

    analyzed: list[VideoCandidate] = []
    pipeline_failures: list[str] = []
    for c in fresh:
        print(f"\n🧠 Analyzing: {c.name}")
        try:
            local_path = materialize_file(drive, c)
            c.path = local_path
            frame = extract_first_frame(local_path, WORK_DIR / f"{local_path.stem}_frame.jpg")
            audio = extract_audio_clip(local_path, WORK_DIR / f"{local_path.stem}_open.mp3")
            analyze_video_with_gemini(c, frame, audio)
            print(f"  source_text: {c.source_text[:120]}")
            print(f"  topic={c.topic!r}  score={c.score}")

            if c.score < MIN_QUALITY_SCORE or c.skip:
                print(f"  🛑 LOW QUALITY (<{MIN_QUALITY_SCORE}): {c.reason}")
                log_row(sheets, c, "LOW_QUALITY", notes=c.reason)
                continue

            topic_key = normalize_topic(c.topic)
            if not topic_key:
                print("  🛑 empty topic — ignore")
                log_row(sheets, c, "IGNORED", notes="empty topic")
                continue
            if topic_key in used_topics:
                print(f"  🛑 DUPLICATE TOPIC '{c.topic}'")
                log_row(sheets, c, "DUPLICATE_TOPIC", notes=f"topic already used: {topic_key}")
                continue

            used_topics.add(topic_key)
            analyzed.append(c)
            print(f"  ✅ queued: {c.title}")
        except Exception as exc:
            failure = f"analysis failed for {c.name}: {type(exc).__name__}: {exc}"
            pipeline_failures.append(failure)
            print(f"  ❌ {failure}")
            traceback.print_exc()
            try:
                log_row(
                    sheets,
                    c,
                    "FAILED",
                    notes=f"Analysis failed ({type(exc).__name__}); see GitHub Actions log.",
                )
            except Exception as log_exc:
                pipeline_failures.append(
                    f"could not log analysis failure for {c.name}: {type(log_exc).__name__}"
                )
                print(f"  ❌ Could not log failure to Google Sheet: {log_exc}")
                traceback.print_exc()

    if not analyzed:
        print("⚠️  No video passed quality + unique-topic gates.")
        for failure in pipeline_failures:
            print(f"PIPELINE_FAILURE: {failure}")
        return 1 if pipeline_failures else 0

    sequenced = rank_sequence(analyzed)
    print("\n📑 Sequence (highest score first, unique topics):")
    for i, c in enumerate(sequenced, 1):
        print(f"  {i}. [{c.score}] {c.topic} — {c.title}")

    now_et = datetime.now(US_TZ)
    today_str = now_et.strftime("%Y-%m-%d")
    already = count_scheduled_for_date(sheets, today_str)
    print(f"\n📅 US {today_str}: {already}/{MAX_VIDEOS_PER_DAY} already booked.")
    slots = next_open_slots(already, now_et)
    to_publish = sequenced[: len(slots)]

    results: list[PipelineResult] = []
    for candidate, slot_et in zip(to_publish, slots):
        rfc = to_youtube_publish_at(slot_et)
        slot_label = slot_et.strftime("%Y-%m-%d %H:%M %Z")
        yt_id = ""
        status = "SCHEDULED"
        notes = candidate.reason
        print(f"\n📤 {candidate.title}\n   {slot_label}  ({rfc})")
        try:
            if DRY_RUN or youtube is None:
                status = "DRY_RUN"
                notes = "No YouTube token or DRY_RUN — sheet only."
                print(f"   ⚠️  {notes}")
            else:
                yt_id = upload_to_youtube(youtube, candidate.path, candidate, rfc)
                print(f"   🎉 youtube id={yt_id}")
                if candidate.source == "drive" and candidate.drive_id:
                    move_drive_to_processed(drive, candidate.drive_id)
            log_row(sheets, candidate, status, slot_label, yt_id, notes)
            results.append(
                PipelineResult(candidate.title, candidate.name, status, slot_label, yt_id, notes)
            )
        except Exception as exc:
            failure = f"publish failed for {candidate.name}: {type(exc).__name__}: {exc}"
            pipeline_failures.append(failure)
            print(f"   ❌ {failure}")
            traceback.print_exc()
            log_row(
                sheets,
                candidate,
                "FAILED",
                slot_label,
                "",
                f"Publish failed ({type(exc).__name__}): {str(exc)[:400]}",
            )
            results.append(
                PipelineResult(candidate.title, candidate.name, "FAILED", slot_label, "", str(exc)[:200])
            )

    print("\n" + "=" * 64)
    print("📋 RUN REPORT")
    print("=" * 64)
    if not results:
        print("Nothing scheduled.")
    for r in results:
        print(f"- {r.status:12} | {r.scheduled_et:24} | {r.title}")
        if r.youtube_id:
            print(f"  https://youtu.be/{r.youtube_id}")
    print("=" * 64)
    for failure in pipeline_failures:
        print(f"PIPELINE_FAILURE: {failure}")
    return 1 if pipeline_failures else 0


if __name__ == "__main__":
    try:
        sys.exit(run())
    except Exception as e:
        print(f"❌ Critical Error in Pipeline: {e}")
        traceback.print_exc()
        sys.exit(1)

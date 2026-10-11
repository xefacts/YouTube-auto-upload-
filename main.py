#!/usr/bin/env python3
"""
Autonomous YouTube publishing pipeline.

Workflow:
  1. Scan local videos/ folder and Google Drive Raw_Videos.
  2. Skip files already logged in Google Sheets (no reposts).
  3. Extract first-frame text + filename via Gemini; generate title, description, tags.
  4. Rank leftover videos and pick the best next ones.
  5. Schedule up to 2 videos per US calendar day (day slot + night slot, ET).
  6. Upload via YouTube Data API v3 with publishAt, log results, print a report.
"""

from __future__ import annotations

import io
import json
import os
import re
import sys
import traceback
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
# Configuration (override with environment variables in GitHub Actions)
# ---------------------------------------------------------------------------
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "15jAt6HUoOrucNA-79y8u7hunq7vUUIBMrTOOeiG-618")
SHEET_RANGE = os.getenv("SHEET_RANGE", "Sheet1!A:L")
MAIN_FOLDER_ID = os.getenv("MAIN_FOLDER_ID", "1x1DpEkCpxF8TqDHL1Tz1DM8Ikudix8Az")
RAW_FOLDER_ID = os.getenv("RAW_FOLDER_ID", "1-YtW4xKp1qg1TzebJI5qlIjNKzuo_r_J")
PROCESSED_FOLDER_ID = os.getenv("PROCESSED_FOLDER_ID", "1ftCj1FCSAEdE3qD2HM_1R83zhCwUIiOf")

LOCAL_VIDEO_DIR = Path(os.getenv("LOCAL_VIDEO_DIR", "videos"))
WORK_DIR = Path(os.getenv("WORK_DIR", "work"))
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "client_secret.json")
YOUTUBE_TOKEN_FILE = os.getenv("YOUTUBE_TOKEN_FILE", "youtube_token.json")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
CHANNEL_NICHE = os.getenv("CHANNEL_NICHE", "human psychology / self-improvement")
PRIVACY_STATUS = os.getenv("YOUTUBE_PRIVACY", "private")  # private until scheduled
MAX_VIDEOS_PER_DAY = int(os.getenv("MAX_VIDEOS_PER_DAY", "2"))
DRY_RUN = os.getenv("DRY_RUN", "false").lower() in {"1", "true", "yes"}

# US peak windows in America/New_York (ET)
US_TZ = pytz.timezone("America/New_York")
DAY_SLOT_HOUR = int(os.getenv("DAY_SLOT_HOUR", "12"))    # 12:00 ET lunch / midday
NIGHT_SLOT_HOUR = int(os.getenv("NIGHT_SLOT_HOUR", "19"))  # 19:00 ET prime time

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


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------
@dataclass
class VideoCandidate:
    name: str
    source: str  # "local" | "drive"
    path: Path | None = None
    drive_id: str | None = None
    topic: str = ""
    title: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    score: int = 0
    reason: str = ""
    skip: bool = False


@dataclass
class PipelineResult:
    title: str
    source_file: str
    status: str
    scheduled_et: str
    youtube_id: str
    notes: str


# ---------------------------------------------------------------------------
# Google clients
# ---------------------------------------------------------------------------
def load_service_account():
    if not Path(CREDENTIALS_FILE).exists():
        raise FileNotFoundError(
            f"{CREDENTIALS_FILE} missing. In GitHub Actions write secrets.GOOGLE_CREDENTIALS_JSON to this file."
        )
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=DRIVE_SCOPES
    )
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)
    return sheets, drive


def load_youtube_client():
    """YouTube uploads require user OAuth, not a service account."""
    token_json = os.getenv("YOUTUBE_TOKEN_JSON")
    if token_json:
        Path(YOUTUBE_TOKEN_FILE).write_text(token_json)
    if not Path(YOUTUBE_TOKEN_FILE).exists():
        print("⚠️  youtube_token.json / YOUTUBE_TOKEN_JSON nahi mila — uploads DRY log mode mein chalenge.")
        return None
    data = json.loads(Path(YOUTUBE_TOKEN_FILE).read_text())
    creds = UserCredentials.from_authorized_user_info(data, YOUTUBE_SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        Path(YOUTUBE_TOKEN_FILE).write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


# ---------------------------------------------------------------------------
# Google Sheets
# ---------------------------------------------------------------------------
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


def load_logged_keys(sheets) -> set[str]:
    """Return lowercased source filenames + titles already in the sheet."""
    result = (
        sheets.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=SHEET_RANGE)
        .execute()
    )
    rows = result.get("values", [])[1:]  # skip header
    keys: set[str] = set()
    for row in rows:
        while len(row) < 12:
            row.append("")
        # B source file, C source id, D title
        for idx in (1, 2, 3):
            if row[idx].strip():
                keys.add(row[idx].strip().lower())
    return keys


def count_scheduled_for_date(sheets, et_date: str) -> int:
    """How many videos already scheduled/uploaded for this US calendar date."""
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


# ---------------------------------------------------------------------------
# Drive + local scanning
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Frame extraction
# ---------------------------------------------------------------------------
def extract_first_frame(video_path: Path, dest: Path) -> Path | None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video_path))
    ok, frame = cap.read()
    if not ok:
        # try a later frame if the first is black/empty
        cap.set(cv2.CAP_PROP_POS_FRAMES, 15)
        ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        return None
    cv2.imwrite(str(dest), frame)
    return dest


# ---------------------------------------------------------------------------
# Gemini analysis
# ---------------------------------------------------------------------------
def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    if genai is None:
        raise ImportError("google-generativeai is not installed.")
    genai.configure(api_key=api_key)


def _parse_json_blob(text: str) -> dict[str, Any]:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    else:
        brace = re.search(r"\{.*\}", text, re.DOTALL)
        if brace:
            text = brace.group(0)
    return json.loads(text)


def analyze_video_with_gemini(candidate: VideoCandidate, frame_path: Path | None) -> VideoCandidate:
    configure_gemini()
    model = genai.GenerativeModel(GEMINI_MODEL)
    prompt = f"""You are a YouTube growth strategist for a {CHANNEL_NICHE} channel targeting a US audience.

Analyze this video. Filename: {candidate.name}

From on-screen text in the first frame (if provided) and the filename, extract the core topic.
Then produce high-CTR metadata.

Return STRICT JSON only, no markdown:
{{
  "topic": "short topic phrase",
  "title": "YouTube title under 70 chars, curiosity + benefit, no ALL CAPS spam",
  "description": "2-4 short paragraphs with a hook, value, CTA, and 3-5 hashtags at the end",
  "tags": ["tag1", "tag2", "... up to 12 tags"],
  "score": 1-100 integer of expected US-audience performance,
  "reason": "one sentence why this score",
  "skip": false
}}
Set skip=true only if the content is duplicate-looking, low quality, or off-niche.
"""
    parts: list[Any] = [prompt]
    if frame_path and frame_path.exists():
        try:
            uploaded = genai.upload_file(str(frame_path), mime_type="image/jpeg")
            parts.append(uploaded)
        except Exception as exc:
            print(f"  ⚠️  Frame upload failed ({exc}); filename-only analysis.")

    response = model.generate_content(parts)
    data = _parse_json_blob(response.text or "{}")
    candidate.topic = str(data.get("topic") or candidate.name)
    candidate.title = str(data.get("title") or candidate.topic)[:100]
    candidate.description = str(data.get("description") or candidate.topic)
    tags = data.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    candidate.tags = [str(t)[:30] for t in tags][:12]
    candidate.score = int(data.get("score") or 50)
    candidate.reason = str(data.get("reason") or "")
    candidate.skip = bool(data.get("skip"))
    return candidate


def rank_sequence(candidates: list[VideoCandidate]) -> list[VideoCandidate]:
    """Highest score first; light diversity so similar topics are not back-to-back."""
    ranked = sorted(candidates, key=lambda c: c.score, reverse=True)
    ordered: list[VideoCandidate] = []
    leftover = ranked[:]
    while leftover:
        if not ordered:
            ordered.append(leftover.pop(0))
            continue
        last_topic = ordered[-1].topic.lower()
        pick_idx = 0
        for i, c in enumerate(leftover):
            if c.topic.lower() not in last_topic and last_topic not in c.topic.lower():
                pick_idx = i
                break
        ordered.append(leftover.pop(pick_idx))
    return ordered


# ---------------------------------------------------------------------------
# US scheduling — 2 slots / day (midday + prime time ET)
# ---------------------------------------------------------------------------
def next_open_slots(already_today: int, now_et: datetime | None = None) -> list[datetime]:
    """Return remaining publish datetimes in ET for today, then fill tomorrow if needed."""
    now_et = now_et or datetime.now(US_TZ)
    today = now_et.date()

    def slots_for(d) -> list[datetime]:
        day = US_TZ.localize(datetime(d.year, d.month, d.day, DAY_SLOT_HOUR, 0, 0))
        night = US_TZ.localize(datetime(d.year, d.month, d.day, NIGHT_SLOT_HOUR, 0, 0))
        return [day, night]

    remaining: list[datetime] = []
    today_slots = slots_for(today)
    # drop slots that already passed, then skip ones already booked today
    future_today = [s for s in today_slots if s > now_et + timedelta(minutes=10)]
    skip = already_today
    for s in future_today:
        if skip > 0:
            skip -= 1
            continue
        remaining.append(s)

    if len(remaining) < MAX_VIDEOS_PER_DAY:
        remaining.extend(slots_for(today + timedelta(days=1)))

    return remaining[:MAX_VIDEOS_PER_DAY]


def to_youtube_publish_at(et_dt: datetime) -> str:
    """YouTube publishAt must be RFC3339 UTC."""
    utc = et_dt.astimezone(timezone.utc)
    return utc.strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# YouTube upload
# ---------------------------------------------------------------------------
def upload_to_youtube(youtube, video_path: Path, candidate: VideoCandidate, publish_at_rfc3339: str) -> str:
    body = {
        "snippet": {
            "title": candidate.title[:100],
            "description": candidate.description[:5000],
            "tags": candidate.tags,
            "categoryId": "22",  # People & Blogs — adjust if needed
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


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
def materialize_file(drive, candidate: VideoCandidate) -> Path:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    if candidate.source == "local" and candidate.path:
        return candidate.path
    dest = WORK_DIR / candidate.name
    print(f"  📥 Downloading Drive file {candidate.name} ...")
    return download_drive_file(drive, candidate.drive_id, dest)


def run() -> int:
    print("=" * 60)
    print("🚀 YouTube Auto-Publish Pipeline")
    print("=" * 60)

    sheets, drive = load_service_account()
    youtube = None if DRY_RUN else load_youtube_client()
    ensure_sheet_headers(sheets)

    logged = load_logged_keys(sheets)
    print(f"📊 Sheet already has {len(logged)} unique keys (files/titles/ids).")

    candidates = list_local_videos() + list_drive_videos()
    print(f"📁 Found {len(candidates)} video(s) (local + Drive).")

    fresh: list[VideoCandidate] = []
    for c in candidates:
        key_name = c.name.lower()
        key_id = (c.drive_id or "").lower()
        if key_name in logged or (key_id and key_id in logged):
            print(f"  ⏭️  Skip duplicate: {c.name}")
            continue
        fresh.append(c)

    if not fresh:
        print("⚠️  Koi nayi video nahi mili. Pipeline idle.")
        return 0

    analyzed: list[VideoCandidate] = []
    for c in fresh:
        print(f"\n🧠 Analyzing: {c.name}")
        try:
            local_path = materialize_file(drive, c)
            frame = extract_first_frame(local_path, WORK_DIR / f"{local_path.stem}_frame.jpg")
            c.path = local_path
            analyze_video_with_gemini(c, frame)
            if c.skip:
                print(f"  🛑 AI skip: {c.reason}")
                now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                append_sheet_row(
                    sheets,
                    [
                        now,
                        c.name,
                        c.drive_id or "",
                        c.title,
                        c.description[:500],
                        ", ".join(c.tags),
                        c.topic,
                        str(c.score),
                        "IGNORED",
                        "",
                        "",
                        c.reason,
                    ],
                )
                continue
            print(f"  ✅ {c.title}  (score={c.score})")
            analyzed.append(c)
        except Exception as exc:
            print(f"  ❌ Analysis failed for {c.name}: {exc}")
            traceback.print_exc()

    if not analyzed:
        print("⚠️  Analysis ke baad koi upload-worthy video nahi bachi.")
        return 0

    sequenced = rank_sequence(analyzed)
    print("\n📑 Suggested sequence:")
    for i, c in enumerate(sequenced, 1):
        print(f"  {i}. [{c.score:3d}] {c.title}")

    now_et = datetime.now(US_TZ)
    today_str = now_et.strftime("%Y-%m-%d")
    already = count_scheduled_for_date(sheets, today_str)
    remaining_today = max(0, MAX_VIDEOS_PER_DAY - already)
    print(f"\n📅 US date {today_str}: already {already}/{MAX_VIDEOS_PER_DAY} booked.")

    slots = next_open_slots(already, now_et)
    to_publish = sequenced[: len(slots)]
    if remaining_today == 0 and slots:
        print("  Today full hai — extra slots kal ke liye assign honge.")

    results: list[PipelineResult] = []
    for candidate, slot_et in zip(to_publish, slots):
        rfc = to_youtube_publish_at(slot_et)
        slot_label = slot_et.strftime("%Y-%m-%d %H:%M %Z")
        yt_id = ""
        status = "SCHEDULED"
        notes = candidate.reason
        print(f"\n📤 {candidate.title}")
        print(f"   slot: {slot_label}  ({rfc})")

        try:
            if DRY_RUN or youtube is None:
                status = "DRY_RUN"
                notes = "No YouTube OAuth token or DRY_RUN=true — metadata logged only."
                print(f"   ⚠️  {notes}")
            else:
                yt_id = upload_to_youtube(youtube, candidate.path, candidate, rfc)
                print(f"   🎉 YouTube id={yt_id}")
                if candidate.source == "drive" and candidate.drive_id:
                    move_drive_to_processed(drive, candidate.drive_id)
                    print("   🚚 Moved Drive file → Processed_Videos")

            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            append_sheet_row(
                sheets,
                [
                    now,
                    candidate.name,
                    candidate.drive_id or "",
                    candidate.title,
                    candidate.description[:500],
                    ", ".join(candidate.tags),
                    candidate.topic,
                    str(candidate.score),
                    status,
                    slot_label,
                    yt_id,
                    notes,
                ],
            )
            results.append(
                PipelineResult(
                    title=candidate.title,
                    source_file=candidate.name,
                    status=status,
                    scheduled_et=slot_label,
                    youtube_id=yt_id,
                    notes=notes,
                )
            )
        except Exception as exc:
            print(f"   ❌ Upload failed: {exc}")
            traceback.print_exc()
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            append_sheet_row(
                sheets,
                [
                    now,
                    candidate.name,
                    candidate.drive_id or "",
                    candidate.title,
                    candidate.description[:500],
                    ", ".join(candidate.tags),
                    candidate.topic,
                    str(candidate.score),
                    "FAILED",
                    slot_label,
                    "",
                    str(exc)[:500],
                ],
            )
            results.append(
                PipelineResult(
                    title=candidate.title,
                    source_file=candidate.name,
                    status="FAILED",
                    scheduled_et=slot_label,
                    youtube_id="",
                    notes=str(exc)[:200],
                )
            )

    print("\n" + "=" * 60)
    print("📋 RUN REPORT")
    print("=" * 60)
    if not results:
        print("Koi video schedule/upload nahi hui.")
    else:
        for r in results:
            print(f"- {r.status:10} | {r.scheduled_et:22} | {r.title}")
            if r.youtube_id:
                print(f"  https://youtu.be/{r.youtube_id}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(run())
    except Exception as e:
        print(f"❌ Critical Error in Pipeline: {e}")
        traceback.print_exc()
        sys.exit(1)

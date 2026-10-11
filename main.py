#!/usr/bin/env python3
"""
Autonomous YouTube publishing pipeline.

Rules (do not change):
  - Niche: personal finance and business.
  - At most 2 videos per US calendar day, published at the 2:00 PM ET and
    8:00 PM ET peak slots.
  - Only videos with an AI quality score >= 90 are published.
  - One topic = one video, forever (Google Sheet history + in-batch).
  - The topic is taken from the on-screen first-frame text or from the first
    spoken line (first seconds of audio), never from the filename.
  - Gemini writes the SEO title, description and tags.
  - All video/history data is stored in the Google Sheet.

Modes:
  python main.py                 # normal run (DRY_RUN env decides upload vs. sheet only)
  python main.py --doctor        # network preflight (sheet, drive, Gemini, YouTube token)
  python main.py --validate-credentials   # offline credential shape check
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
import traceback
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

import cv2
import pytz
import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials as UserCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "15jAt6HUoOrucNA-79y8u7hunq7vUUIBMrTOOeiG-618")
SHEET_RANGE = os.getenv("SHEET_RANGE", "Sheet1!A:L")
SHEET_TAB = (os.getenv("SHEET_TAB") or "").strip()
RAW_FOLDER_ID = os.getenv("RAW_FOLDER_ID", "1-YtW4xKp1qg1TzebJI5qlIjNKzuo_r_J")
PROCESSED_FOLDER_ID = os.getenv("PROCESSED_FOLDER_ID", "1ftCj1FCSAEdE3qD2HM_1R83zhCwUIiOf")

LOCAL_VIDEO_DIR = Path(os.getenv("LOCAL_VIDEO_DIR", "videos"))
WORK_DIR = Path(os.getenv("WORK_DIR", "work"))
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "client_secret.json")
YOUTUBE_TOKEN_FILE = os.getenv("YOUTUBE_TOKEN_FILE", "youtube_token.json")

# "auto" lets the pipeline discover a working Flash model for the API key
# (see GEMINI_MODEL_PREFERENCES). Set GEMINI_MODEL to pin an exact model id.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "auto")
GEMINI_API_BASE = os.getenv("GEMINI_API_BASE", "https://generativelanguage.googleapis.com")
GEMINI_API_VERSION = os.getenv("GEMINI_API_VERSION", "v1beta")
# Bounded fallback: every extra model costs another API request (free-tier quotas).
MAX_GEMINI_MODEL_ATTEMPTS = int(os.getenv("MAX_GEMINI_MODEL_ATTEMPTS", "4"))
GEMINI_MODEL_PREFERENCES = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash",
    "gemini-3-flash",
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
]

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

# Statuses that mean "this source file / this topic is already used".
COMMITTED_STATUSES = {"SCHEDULED", "UPLOADED", "PUBLISHED"}
# Statuses that must stay retryable in later runs.
RETRYABLE_STATUSES = {"DRY_RUN", "FAILED", "IGNORED", "LOW_QUALITY", "DUPLICATE_TOPIC"}

RETRYABLE_HTTP_STATUS = {408, 429, 500, 502, 503, 504}


# ---------------------------------------------------------------------------
# Secret hygiene
# ---------------------------------------------------------------------------
_FILE_SECRETS_CACHE: list[str] | None = None


def _file_secret_values() -> list[str]:
    """Secrets read from the credential files (cached - they do not change mid-run)."""
    global _FILE_SECRETS_CACHE
    if _FILE_SECRETS_CACHE is not None:
        return _FILE_SECRETS_CACHE
    values: set[str] = set()
    for path in (CREDENTIALS_FILE, YOUTUBE_TOKEN_FILE):
        try:
            raw = Path(path).read_text()
        except OSError:
            continue
        if raw and len(raw) >= 8:
            values.add(raw)
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            continue
        values.update(_iter_strings(parsed))
    _FILE_SECRETS_CACHE = sorted((v for v in values if len(v) >= 8), key=len, reverse=True)
    return _FILE_SECRETS_CACHE


def secret_values() -> list[str]:
    """Every literal secret string we know about, for log redaction."""
    values: set[str] = set()
    for name in (
        "GEMINI_API_KEY",
        "YOUTUBE_TOKEN_JSON",
        "GOOGLE_CREDENTIALS_JSON",
        "YOUTUBE_CLIENT_ID",
        "YOUTUBE_CLIENT_SECRET",
        "YOUTUBE_REFRESH_TOKEN",
    ):
        value = os.getenv(name)
        if value and len(value) >= 8:
            values.add(value)
    values.update(_file_secret_values())
    return sorted((v for v in values if len(v) >= 8), key=len, reverse=True)


def _iter_strings(node: Any) -> Iterable[str]:
    if isinstance(node, str):
        if len(node) >= 8:
            yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _iter_strings(value)
    elif isinstance(node, (list, tuple)):
        for value in node:
            yield from _iter_strings(value)


def sanitize(text: Any) -> str:
    """Redact known secrets from anything we print (never log secret values)."""
    out = str(text)
    for secret in secret_values():
        out = out.replace(secret, "[REDACTED]")
    return out


def describe_exception(exc: BaseException) -> str:
    """Short, sanitized, one-line description of an exception for logs/annotations."""
    message = sanitize(str(exc)).replace("\n", " ").strip()
    if isinstance(exc, HttpError):
        status = getattr(exc.resp, "status", None)
        return f"HttpError {status}: {message[:400]}"
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        body = sanitize(exc.response.text)[:400].replace("\n", " ")
        return f"HTTP {exc.response.status_code}: {body}"
    return f"{type(exc).__name__}: {message[:400]}" if message else type(exc).__name__


def gemini_label() -> str:
    """Which Gemini model this run actually used (for the run summary)."""
    return getattr(_GEMINI_CLIENT, "model", "") or GEMINI_MODEL


def annotate(level: str, title: str, message: str) -> None:
    """Emit a sanitized GitHub Actions annotation (or a plain line outside CI)."""
    safe = sanitize(message)
    if os.getenv("GITHUB_ACTIONS") == "true" and os.getenv("PIPELINE_QUIET_ANNOTATIONS") != "1":
        escaped = safe.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print(f"::{level} title={title}::{escaped}")
    else:
        print(f"[{level}] {title}: {safe}")


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def retry_call(
    fn: Callable[[], Any],
    *,
    label: str,
    attempts: int = 4,
    base_delay: float = 2.0,
    retry_on: set[int] = RETRYABLE_HTTP_STATUS,
) -> Any:
    """Call fn() with backoff on transient Google API / network failures."""
    last_exc: BaseException | None = None
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - classified below
            status = None
            if isinstance(exc, HttpError):
                status = getattr(exc.resp, "status", None)
            elif isinstance(exc, requests.HTTPError) and exc.response is not None:
                status = exc.response.status_code
            retryable = status in retry_on or isinstance(
                exc, (requests.ConnectionError, requests.Timeout)
            )
            last_exc = exc
            if not retryable or attempt == attempts:
                raise
            delay = base_delay * (2 ** (attempt - 1))
            print(f"  ↩️  {label}: transient error ({describe_exception(exc)}); retry in {delay:.0f}s")
            time.sleep(delay)
    raise last_exc  # pragma: no cover - defensive


def parse_json_object(raw: str, label: str) -> dict:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is not valid JSON ({exc.msg} at position {exc.pos}).") from None
    if not isinstance(data, dict):
        raise ValueError(f"{label} must be a JSON object, got {type(data).__name__}.")
    return data


def key_paths(node: Any, prefix: str = "") -> list[str]:
    """Field names only (never values) - used to diagnose secret shapes safely."""
    paths: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            paths.append(path)
            paths.extend(key_paths(value, path))
    elif isinstance(node, (list, tuple)):
        for item in node:
            paths.extend(key_paths(item, f"{prefix}[]"))
    return paths


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Google credentials
# ---------------------------------------------------------------------------
def load_service_account(credentials_file: str | None = None):
    path = Path(credentials_file or CREDENTIALS_FILE)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} is missing. Write the GOOGLE_CREDENTIALS_JSON secret to {path} first."
        )
    creds = service_account.Credentials.from_service_account_file(str(path), scopes=DRIVE_SCOPES)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)
    return sheets, drive


def service_account_summary(credentials_file: str | None = None) -> str:
    """Human-readable (non-secret) summary of the service account."""
    path = Path(credentials_file or CREDENTIALS_FILE)
    if not path.exists():
        return f"{path} is missing"
    data = parse_json_object(path.read_text(), str(path))
    kind = data.get("type", "?")
    email = str(data.get("client_email", ""))
    project = str(data.get("project_id", ""))
    if "@" in email:
        local, _, domain = email.partition("@")
        masked = f"{local[:2]}***@{domain}"
    else:
        masked = "(no client_email)"
    return f"type={kind} project={project or '?'} account={masked}"


# --- YouTube OAuth token ---------------------------------------------------
TOKEN_FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "refresh_token": ("refresh_token", "refreshtoken", "refresh_token_value"),
    "client_id": ("client_id", "clientid", "oauth_client_id"),
    "client_secret": ("client_secret", "clientsecret", "oauth_client_secret"),
    "token": ("token", "access_token", "accesstoken"),
    "token_uri": ("token_uri", "tokenuri"),
    "scopes": ("scopes", "scope"),
}


def extract_token_fields(data: dict) -> dict[str, Any]:
    """Pull OAuth fields out of whatever shape the secret is stored in.

    Supports the canonical authorized-user JSON, the Google "installed"/"web"
    client-secret files, "access_token" only blobs and common key aliases.
    Searches nested objects, so ``{"installed": {...}}`` works too.
    """
    found: dict[str, Any] = {}
    for field_name, aliases in TOKEN_FIELD_ALIASES.items():
        value = _find_field(data, aliases)
        if value is not None:
            found[field_name] = value

    env_fallbacks = {
        "client_id": "YOUTUBE_CLIENT_ID",
        "client_secret": "YOUTUBE_CLIENT_SECRET",
        "refresh_token": "YOUTUBE_REFRESH_TOKEN",
    }
    for field_name, env_name in env_fallbacks.items():
        if not found.get(field_name) and os.getenv(env_name):
            found[field_name] = os.getenv(env_name, "").strip()
    return found


def _find_field(node: Any, aliases: Iterable[str]) -> Any:
    alias_set = {alias.replace("-", "_").lower() for alias in aliases}
    if isinstance(node, dict):
        for key, value in node.items():
            if str(key).replace("-", "_").lower() in alias_set:
                if isinstance(value, str) and value.strip():
                    return value.strip()
                if isinstance(value, (list, tuple)) and value:
                    return list(value)
        for value in node.values():
            found = _find_field(value, aliases)
            if found is not None:
                return found
    elif isinstance(node, (list, tuple)):
        for item in node:
            found = _find_field(item, aliases)
            if found is not None:
                return found
    return None


def read_youtube_token_payload() -> dict | None:
    """Return the parsed YOUTUBE_TOKEN_JSON (env first, then the token file)."""
    raw = os.getenv("YOUTUBE_TOKEN_JSON") or ""
    if raw.strip():
        payload = parse_json_object(raw, "YOUTUBE_TOKEN_JSON")
    else:
        path = Path(YOUTUBE_TOKEN_FILE)
        if not path.exists():
            return None
        payload = parse_json_object(path.read_text(), str(path))
    # Mirror the secret to disk so google-auth tooling can reuse it.
    try:
        Path(YOUTUBE_TOKEN_FILE).write_text(json.dumps(payload))
    except OSError:
        pass
    return payload


def youtube_credential_candidates(payload: dict | None) -> list[tuple[str, dict[str, Any]]]:
    """Every credential combination we can try, most canonical first.

    The environment secrets (YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET /
    YOUTUBE_REFRESH_TOKEN) and the YOUTUBE_TOKEN_JSON payload may each hold part
    of the puzzle - e.g. a refresh token minted with a *different* OAuth client
    than the client file stored in YOUTUBE_TOKEN_JSON. Each candidate is a
    (label, fields) pair so a working combination can be reported exactly.
    """
    from_payload = extract_token_fields(payload or {})
    from_env: dict[str, Any] = {}
    for field, env_name in (
        ("client_id", "YOUTUBE_CLIENT_ID"),
        ("client_secret", "YOUTUBE_CLIENT_SECRET"),
        ("refresh_token", "YOUTUBE_REFRESH_TOKEN"),
        ("token", "YOUTUBE_ACCESS_TOKEN"),
    ):
        value = (os.getenv(env_name) or "").strip()
        if value:
            from_env[field] = value

    combos: list[tuple[str, dict[str, Any]]] = []
    sources = (("YOUTUBE_TOKEN_JSON", from_payload), ("split secrets", from_env))
    for label, fields in sources:
        if fields.get("refresh_token") or fields.get("token"):
            combos.append((label, dict(fields)))
    for client_label, client_fields in sources:
        for token_label, token_fields in sources:
            if client_label == token_label:
                continue
            merged: dict[str, Any] = {}
            for field in ("client_id", "client_secret", "token_uri"):
                if client_fields.get(field):
                    merged[field] = client_fields[field]
            for field in ("refresh_token", "token"):
                if token_fields.get(field):
                    merged[field] = token_fields[field]
            if merged.get("refresh_token") or merged.get("token"):
                combos.append((f"{client_label} client + {token_label} token", merged))

    unique: list[tuple[str, dict[str, Any]]] = []
    seen: set[tuple] = set()
    for label, fields in combos:
        signature = (
            fields.get("client_id"),
            fields.get("client_secret"),
            fields.get("refresh_token"),
            fields.get("token"),
        )
        if signature in seen:
            continue
        seen.add(signature)
        unique.append((label, fields))
    return unique


def build_youtube_credentials(fields: dict[str, Any]) -> UserCredentials:
    return UserCredentials(
        token=fields.get("token"),
        refresh_token=fields.get("refresh_token"),
        token_uri=fields.get("token_uri") or "https://oauth2.googleapis.com/token",
        client_id=fields.get("client_id"),
        client_secret=fields.get("client_secret"),
        scopes=YOUTUBE_SCOPES,
    )


def resolve_youtube_credentials(payload: dict | None) -> tuple[UserCredentials, str]:
    """Return the first credential combination that can actually authenticate."""
    candidates = youtube_credential_candidates(payload)
    if not candidates:
        raise RuntimeError(
            "No YouTube OAuth credentials found: set YOUTUBE_TOKEN_JSON or the split "
            "secrets YOUTUBE_CLIENT_ID + YOUTUBE_CLIENT_SECRET + YOUTUBE_REFRESH_TOKEN."
        )
    problems: list[str] = []
    for label, fields in candidates:
        has_token = bool(fields.get("token"))
        has_refresh = bool(fields.get("refresh_token"))
        if not has_token and not has_refresh:
            continue
        if has_refresh:
            missing = [f for f in ("client_id", "client_secret") if not fields.get(f)]
            if missing:
                problems.append(f"{label}: refresh_token present but missing {', '.join(missing)}")
                continue
        try:
            creds = build_youtube_credentials(fields)
            if not creds.token or creds.expired:
                if not creds.refresh_token:
                    problems.append(f"{label}: access token expired and no refresh_token")
                    continue
                retry_call(lambda: creds.refresh(Request()), label=f"youtube token refresh ({label})")
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{label}: {describe_exception(exc)}")
            continue
        return creds, label
    detail = " | ".join(problems[:4]) or "no usable credentials"
    tried = ", ".join(label for label, _ in candidates) or "none"
    raise RuntimeError(
        "YouTube credentials could not authenticate (combinations tried: "
        + tried
        + "; "
        + detail
        + "). A refresh token must be minted by the channel owner with the same OAuth client; "
        "an invalid_grant error means the refresh token was revoked, expired (OAuth consent "
        "screen still in Testing expires refresh tokens after 7 days) or belongs to a different "
        "client. Re-mint it with tools/get_youtube_token.py or the OAuth 2.0 Playground and "
        "update YOUTUBE_TOKEN_JSON / YOUTUBE_REFRESH_TOKEN."
    )


def token_diagnosis(payload: dict | None, *, live: bool) -> tuple[bool, str]:
    """(usable, message) about the YouTube credential *shape* (no network calls)."""
    candidates = youtube_credential_candidates(payload)
    complete = [
        label
        for label, fields in candidates
        if fields.get("refresh_token") and fields.get("client_id") and fields.get("client_secret")
    ]
    if complete:
        return True, (
            "refresh_token + client_id + client_secret available (from "
            + ", ".join(complete[:2])
            + ")"
        )
    if any(fields.get("token") for _, fields in candidates):
        return True, (
            "access_token only (no refresh_token): uploads work only until that access token expires"
        )
    payload = payload or {}
    if str(payload.get("type", "")).lower() == "service_account":
        return False, (
            "YOUTUBE_TOKEN_JSON contains a *service account* key. YouTube uploads need a "
            "user OAuth token, not a service account."
        )
    if not payload and not candidates:
        return (not live), "YOUTUBE_TOKEN_JSON is not set and no split YouTube secrets are set"
    shape = ", ".join(key_paths(payload)) or "(no fields)"
    partial = ", ".join(f"{label}: {', '.join(sorted(f for f, v in fields.items() if v))}" for label, fields in candidates) or "none"
    return False, (
        "no refresh_token and no access_token available. YOUTUBE_TOKEN_JSON fields: "
        + shape
        + f"; candidate credentials: {partial}. Fix it either way: (a) add/refresh the "
        "YOUTUBE_REFRESH_TOKEN secret with a refresh token minted for this OAuth client "
        "(OAuth 2.0 Playground with scope youtube.upload) - the pipeline combines the split "
        "secrets automatically, or (b) replace YOUTUBE_TOKEN_JSON with the authorized-user "
        "JSON printed by tools/get_youtube_token.py (Desktop OAuth client)."
    )


def load_youtube_client():
    """Build a YouTube Data API client from the stored OAuth credentials."""
    payload = read_youtube_token_payload()
    split_present = any(
        (os.getenv(name) or "").strip()
        for name in ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN")
    )
    if payload is None and not split_present:
        print("⚠️  YouTube OAuth token missing — metadata will be logged without upload.")
        return None

    usable, message = token_diagnosis(payload, live=True)
    if not usable:
        raise RuntimeError(f"Cannot build the YouTube client. {message}")

    creds, label = resolve_youtube_credentials(payload)
    print(f"🔑 YouTube credential: authenticated using {label}.")

    scopes = extract_token_fields(payload or {}).get("scopes")
    if isinstance(scopes, str):
        scopes = [s for s in scopes.split() if s]
    if scopes and "https://www.googleapis.com/auth/youtube.upload" not in scopes:
        print(f"⚠️  token scopes {scopes} do not list youtube.upload; upload may fail with 403")
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


# ---------------------------------------------------------------------------
# Google Sheet plumbing (tab is discovered, never assumed)
# ---------------------------------------------------------------------------
_SHEET_TAB_CACHE: str | None = SHEET_TAB or None


def resolve_sheet_tab(sheets, *, refresh: bool = False) -> str:
    """Find the tab that holds the video history. Never raises."""
    global _SHEET_TAB_CACHE
    if _SHEET_TAB_CACHE and not refresh:
        return _SHEET_TAB_CACHE

    fallback = SHEET_TAB or (SHEET_RANGE.split("!", 1)[0] if "!" in SHEET_RANGE else "Sheet1")
    try:
        meta = retry_call(
            lambda: sheets.spreadsheets()
            .get(
                spreadsheetId=SPREADSHEET_ID,
                fields="properties.title,sheets.properties.title",
            )
            .execute(),
            label="spreadsheet metadata",
        )
        titles = [
            sheet["properties"]["title"]
            for sheet in meta.get("sheets", [])
            if sheet.get("properties", {}).get("title")
        ]
        print(f"📗 Spreadsheet '{meta.get('properties', {}).get('title', '?')}' tabs: {titles}")
        chosen = SHEET_TAB if SHEET_TAB in titles else ""
        if not chosen:
            chosen = _match_tab_by_header(sheets, titles) or ""
        if not chosen and fallback in titles:
            chosen = fallback
        if not chosen and titles:
            chosen = titles[0]
        if not chosen:
            chosen = fallback
    except Exception as exc:  # noqa: BLE001 - discovery must never be fatal
        annotate("warning", "Sheet discovery", f"could not read spreadsheet metadata ({describe_exception(exc)}); using {fallback}")
        chosen = fallback
    _SHEET_TAB_CACHE = chosen
    return chosen


def _match_tab_by_header(sheets, titles: list[str]) -> str | None:
    for title in titles:
        try:
            result = (
                sheets.spreadsheets()
                .values()
                .get(spreadsheetId=SPREADSHEET_ID, range=f"'{title}'!A1:L1")
                .execute()
            )
        except Exception:  # noqa: BLE001
            continue
        row = (result.get("values") or [[]])[0]
        if row and row[0].strip().lower() == SHEET_HEADERS[0].strip().lower():
            print(f"📄 Using existing pipeline tab '{title}'.")
            return title
    return None


def sheet_range(a1: str = "A:L") -> str:
    tab = _SHEET_TAB_CACHE or SHEET_TAB or (
        SHEET_RANGE.split("!", 1)[0] if "!" in SHEET_RANGE else "Sheet1"
    )
    return f"'{tab}'!{a1}"


def ensure_sheet_headers(sheets) -> None:
    resolve_sheet_tab(sheets)
    result = retry_call(
        lambda: sheets.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=sheet_range("A1:L1"))
        .execute(),
        label="sheet header read",
    )
    values = result.get("values", [])
    if not values or values[0] != SHEET_HEADERS:
        retry_call(
            lambda: sheets.spreadsheets()
            .values()
            .update(
                spreadsheetId=SPREADSHEET_ID,
                range=sheet_range("A1"),
                valueInputOption="RAW",
                body={"values": [SHEET_HEADERS]},
            )
            .execute(),
            label="sheet header write",
        )
        print("🧾 Header row written.")


def sheet_rows(sheets) -> list[list[str]]:
    result = retry_call(
        lambda: sheets.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=sheet_range("A:L"))
        .execute(),
        label="sheet read",
    )
    rows = result.get("values", [])[1:]
    padded: list[list[str]] = []
    for row in rows:
        row = list(row)
        while len(row) < len(SHEET_HEADERS):
            row.append("")
        padded.append(row)
    return padded


def append_sheet_row(sheets, row: list[str]) -> None:
    retry_call(
        lambda: sheets.spreadsheets()
        .values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range=sheet_range("A1"),
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [row]},
        )
        .execute(),
        label="sheet append",
    )


def load_sheet_state(sheets) -> tuple[set[str], set[str]]:
    """Return (file/id/title keys, normalized topics already used)."""
    return state_from_rows(sheet_rows(sheets))


def state_from_rows(rows: list[list[str]]) -> tuple[set[str], set[str]]:
    keys: set[str] = set()
    topics: set[str] = set()
    for row in rows:
        status = row[8].strip().upper()
        if status not in RETRYABLE_STATUSES:
            for idx in (1, 2, 3):
                if row[idx].strip():
                    keys.add(row[idx].strip().lower())
        topic_key = normalize_topic(row[6] or row[3])
        if topic_key and status not in RETRYABLE_STATUSES:
            topics.add(topic_key)
    return keys, topics


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
            sanitize(notes or c.reason),
        ],
    )


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


# ---------------------------------------------------------------------------
# Slot scheduling (2:00 PM ET / 8:00 PM ET, max 2 per US day)
# ---------------------------------------------------------------------------
def slot_key(moment: datetime) -> str:
    """Stable sheet key for a slot, e.g. '2026-10-11 14'."""
    return f"{moment.strftime('%Y-%m-%d')} {moment.hour:02d}"


SLOT_LABEL_FORMATS = (
    "%Y-%m-%d %H:%M %Z",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%SZ",
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M",
)


def parse_slot_label(label: str, tz=pytz.timezone("America/New_York")) -> datetime | None:
    """Parse the 'Scheduled For (ET)' cell, tolerating Sheets date coercion."""
    text = (label or "").strip()
    if not text:
        return None
    for fmt in SLOT_LABEL_FORMATS:
        try:
            parsed = datetime.strptime(text, fmt)
        except ValueError:
            continue
        if parsed.tzinfo is None:
            return tz.localize(parsed)
        return parsed.astimezone(tz)
    iso = re.search(r"(\d{4})-(\d{2})-(\d{2})[ T](\d{1,2}):(\d{2})", text)
    if iso:
        year, month, day, hour, minute = (int(g) for g in iso.groups())
        return tz.localize(datetime(year, month, day, hour, minute))
    us = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})[ ,]+(\d{1,2}):(\d{2})", text)
    if us:
        month, day, year, hour, minute = (int(g) for g in us.groups())
        return tz.localize(datetime(year, month, day, hour, minute))
    return None


def booked_slot_keys(rows: list[list[str]], tz=pytz.timezone("America/New_York")) -> set[str]:
    keys: set[str] = set()
    for row in rows:
        if row[8].strip().upper() not in COMMITTED_STATUSES:
            continue
        parsed = parse_slot_label(row[9], tz)
        if parsed:
            keys.add(slot_key(parsed))
    return keys


def count_scheduled_for_date(rows: list[list[str]], et_date: str) -> int:
    return sum(1 for key in booked_slot_keys(rows) if key.startswith(et_date))


def slots_for_day(day, tz=US_TZ) -> list[datetime]:
    return [
        tz.localize(datetime(day.year, day.month, day.day, DAY_SLOT_HOUR, 0, 0)),
        tz.localize(datetime(day.year, day.month, day.day, NIGHT_SLOT_HOUR, 0, 0)),
    ]


def next_open_slots(
    already_today: int = 0,
    now_et: datetime | None = None,
    booked_slots: Iterable[str] | None = None,
) -> list[datetime]:
    """Next open 2:00 PM / 8:00 PM ET slots (max MAX_VIDEOS_PER_DAY per US day).

    ``booked_slots`` holds explicit slot keys already present in the sheet, so a
    slot is never handed out twice. ``already_today`` is the legacy counter used
    when no explicit keys are available.
    """
    now_et = now_et or datetime.now(US_TZ)
    today = now_et.date()
    booked = {str(key).strip() for key in (booked_slots or ()) if str(key).strip()}
    explicit = bool(booked)
    per_day = Counter(key.split(" ")[0] for key in booked)

    picks: list[datetime] = []
    for offset in range(3):
        day = today + timedelta(days=offset)
        day_iso = day.strftime("%Y-%m-%d")
        used = per_day.get(day_iso, 0) + (already_today if offset == 0 and not explicit else 0)
        quota = max(0, MAX_VIDEOS_PER_DAY - used)
        if quota == 0:
            continue
        for slot in slots_for_day(day):
            if slot_key(slot) in booked:
                continue
            if offset == 0 and slot <= now_et + timedelta(minutes=15):
                continue
            picks.append(slot)
            quota -= 1
            if quota == 0 or len(picks) >= MAX_VIDEOS_PER_DAY:
                break
        if len(picks) >= MAX_VIDEOS_PER_DAY:
            break
    return picks[:MAX_VIDEOS_PER_DAY]


def to_youtube_publish_at(et_dt: datetime) -> str:
    utc = et_dt.astimezone(timezone.utc)
    return utc.strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Drive
# ---------------------------------------------------------------------------
def list_drive_videos(drive) -> list[VideoCandidate]:
    query = f"'{RAW_FOLDER_ID}' in parents and mimeType contains 'video/' and trashed = false"
    items: list[dict] = []
    page_token = None
    while True:
        resp = retry_call(
            lambda page_token=page_token: drive.files()
            .list(
                q=query,
                pageSize=50,
                fields="nextPageToken, files(id, name)",
                pageToken=page_token,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            .execute(),
            label="drive list",
        )
        items.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    print(f"   Drive raw folder: {len(items)} file(s)")
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
    request = drive.files().get_media(fileId=file_id, supportsAllDrives=True)
    with dest.open("wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    return dest


def move_drive_to_processed(drive, file_id: str) -> None:
    retry_call(
        lambda: drive.files()
        .update(
            fileId=file_id,
            addParents=PROCESSED_FOLDER_ID,
            removeParents=RAW_FOLDER_ID,
            fields="id, parents",
            supportsAllDrives=True,
        )
        .execute(),
        label="drive move",
    )


def materialize_file(drive, candidate: VideoCandidate) -> Path:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    if candidate.source == "local" and candidate.path:
        return candidate.path
    dest = WORK_DIR / candidate.name
    print(f"  📥 Downloading Drive file {candidate.name} ...")
    return download_drive_file(drive, candidate.drive_id, dest)


# ---------------------------------------------------------------------------
# Media extraction
# ---------------------------------------------------------------------------
MAX_FRAME_WIDTH = int(os.getenv("MAX_FRAME_WIDTH", "1280"))


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
    height, width = frame.shape[:2]
    if width > MAX_FRAME_WIDTH:
        scale = MAX_FRAME_WIDTH / float(width)
        frame = cv2.resize(frame, (MAX_FRAME_WIDTH, int(height * scale)), interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(dest), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
    return dest if dest.exists() else None


def extract_audio_clip(video_path: Path, dest: Path, seconds: int = 20) -> Path | None:
    """First ~20s of audio for the opening spoken sentence / transcript."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-t", str(seconds), "-vn", "-ac", "1", "-ar", "16000", "-b:a", "64k",
        str(dest),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=180)
        if dest.exists() and dest.stat().st_size > 0:
            return dest
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as exc:
        detail = ""
        if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
            detail = sanitize(exc.stderr.decode(errors="replace"))[-200:].replace("\n", " ")
        print(f"  ⚠️  audio clip skipped: {describe_exception(exc)} {detail}".strip())
    return None


# ---------------------------------------------------------------------------
# Gemini (REST - independent of the deprecated google-generativeai package)
# ---------------------------------------------------------------------------
class GeminiError(RuntimeError):
    pass


class GeminiQuotaError(GeminiError):
    """Gemini quota / billing limits - do not retry, do not hammer other models."""


class GeminiClient:
    def __init__(self, api_key: str, model: str | None = None, base: str = GEMINI_API_BASE):
        self.api_key = api_key
        self.base = base.rstrip("/")
        self.requested_model = (model or "").strip() or GEMINI_MODEL
        self.model = "" if self.requested_model == "auto" else self.requested_model
        self.session = requests.Session()
        self.session.headers.update({"x-goog-api-key": api_key, "Content-Type": "application/json"})

    # -- HTTP ---------------------------------------------------------------
    def _request(self, method: str, url: str, *, payload: dict | None = None, label: str) -> dict:
        def call():
            resp = self.session.request(method, url, json=payload, timeout=180)
            if resp.status_code >= 400:
                raise requests.HTTPError(
                    f"{resp.status_code} {self._error_message(resp)}", response=resp
                )
            return resp.json()
        try:
            # 429 is excluded on purpose: quota errors are not transient and
            # retrying them burns the daily request budget.
            return retry_call(
                call,
                label=label,
                attempts=4,
                base_delay=2.5,
                retry_on={408, 500, 502, 503, 504},
            )
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "?"
            message = self._error_message(exc.response)
            if status == 429 or "quota" in message.lower() or "RESOURCE_EXHAUSTED" in message:
                raise GeminiQuotaError(
                    f"Gemini quota/limit reached ({status}): {message}"
                ) from None
            raise GeminiError(f"Gemini API error ({status}): {message}") from None

    @staticmethod
    def _error_message(resp: requests.Response | None) -> str:
        if resp is None:
            return "no response"
        try:
            data = resp.json()
        except ValueError:
            return sanitize(resp.text)[:400]
        error = data.get("error") if isinstance(data, dict) else None
        if isinstance(error, dict):
            return sanitize(error.get("message") or json.dumps(error))[:400]
        return sanitize(json.dumps(data))[:400]

    # -- Models -------------------------------------------------------------
    def list_models(self) -> list[str]:
        url = f"{self.base}/{GEMINI_API_VERSION}/models"
        data = self._request("GET", url, label="gemini list models")
        names = []
        for item in data.get("models", []):
            name = str(item.get("name", "")).removeprefix("models/")
            if not name:
                continue
            methods = item.get("supportedGenerationMethods") or []
            if methods and "generateContent" not in methods:
                continue
            names.append(name)
        return names

    def resolve_model(self) -> str:
        if self.model:
            return self.model
        available: list[str] = []
        try:
            available = self.list_models()
            print(f"   Gemini models available for this key: {len(available)}")
        except Exception as exc:  # noqa: BLE001 - fall back to trying candidates
            print(f"   ⚠️  could not list Gemini models ({describe_exception(exc)}); trying candidates")
        for candidate in GEMINI_MODEL_PREFERENCES:
            if candidate in available or not available:
                self.model = candidate
                return self.model
        if available:
            flash = [m for m in available if "flash" in m and "lite" not in m and "image" not in m]
            self.model = (flash or available)[0]
            return self.model
        self.model = GEMINI_MODEL_PREFERENCES[0]
        return self.model

    # -- Generation ---------------------------------------------------------
    def _candidate_models(self) -> list[str]:
        """The resolved model first, then a few fallbacks (bounded on purpose:
        each extra model costs another API request)."""
        self.resolve_model()
        models = [self.model]
        models.extend(m for m in GEMINI_MODEL_PREFERENCES if m != self.model)
        return models[:MAX_GEMINI_MODEL_ATTEMPTS]

    def generate(
        self,
        parts: list[dict],
        *,
        json_mode: bool = True,
        max_output_tokens: int | None = None,
        temperature: float = 0.6,
    ) -> str:
        errors: list[str] = []
        quota_fallbacks = 0
        for model in self._candidate_models():
            json_mode_enabled = json_mode
            while True:
                generation_config: dict[str, Any] = {"temperature": temperature}
                if json_mode_enabled:
                    generation_config["responseMimeType"] = "application/json"
                if max_output_tokens:
                    generation_config["maxOutputTokens"] = max_output_tokens
                url = f"{self.base}/{GEMINI_API_VERSION}/models/{model}:generateContent"
                payload = {
                    "contents": [{"role": "user", "parts": parts}],
                    "generationConfig": generation_config,
                }
                try:
                    data = self._request("POST", url, payload=payload, label=f"gemini generate ({model})")
                except GeminiError as exc:
                    message = str(exc)
                    errors.append(f"{model}: {sanitize(message)[:200]}")
                    if isinstance(exc, GeminiQuotaError):
                        # Quotas are per model, so exactly one lighter model is tried
                        # before giving up - hammering every model would burn more budget.
                        if quota_fallbacks < 1:
                            quota_fallbacks += 1
                            print(f"   ⚠️  {model}: quota limit; trying one lighter model")
                            break
                        raise
                    if json_mode_enabled and ("responseMimeType" in message or "response_mime_type" in message):
                        print(f"   ⚠️  {model} rejected JSON mode; retrying as plain text")
                        json_mode_enabled = False
                        continue
                    print(f"   ⚠️  {model} failed ({sanitize(message)[:120]}); trying the next model")
                    break
                self.model = model
                return self._text_from_response(data)
        raise GeminiError("every Gemini model failed -> " + " | ".join(errors[:4]))

    @staticmethod
    def _text_from_response(data: dict) -> str:
        candidates = data.get("candidates") or []
        if not candidates:
            feedback = data.get("promptFeedback") or {}
            raise GeminiError(
                f"Gemini returned no candidates (blockReason={feedback.get('blockReason', 'none')})"
            )
        candidate = candidates[0]
        texts = [
            str(part.get("text", ""))
            for part in candidate.get("content", {}).get("parts", [])
            if part.get("text")
        ]
        text = "\n".join(t for t in texts if t).strip()
        if not text:
            raise GeminiError(
                f"Gemini returned no text (finishReason={candidate.get('finishReason', 'unknown')})"
            )
        return text


_GEMINI_CLIENT: GeminiClient | None = None


def configure_gemini() -> GeminiClient:
    global _GEMINI_CLIENT
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")
    if _GEMINI_CLIENT is None or _GEMINI_CLIENT.api_key != api_key:
        _GEMINI_CLIENT = GeminiClient(api_key)
    return _GEMINI_CLIENT


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


def _inline_part(path: Path, mime_type: str) -> dict:
    return {
        "inlineData": {
            "mimeType": mime_type,
            "data": base64.b64encode(path.read_bytes()).decode("ascii"),
        }
    }


def analyze_video_with_gemini(
    candidate: VideoCandidate,
    frame_path: Path | None,
    audio_path: Path | None,
    client: GeminiClient | None = None,
) -> VideoCandidate:
    client = client or configure_gemini()
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
    parts: list[dict] = [{"text": prompt}]
    if frame_path and frame_path.exists():
        try:
            parts.append(_inline_part(frame_path, "image/jpeg"))
            print(f"   frame attached: {frame_path.name} ({frame_path.stat().st_size // 1024} KB)")
        except OSError as exc:
            print(f"  ⚠️  frame attach failed: {describe_exception(exc)}")
    if audio_path and audio_path.exists():
        mime = "audio/mpeg" if audio_path.suffix.lower() == ".mp3" else "audio/wav"
        try:
            parts.append(_inline_part(audio_path, mime))
            print(f"   audio attached: {audio_path.name} ({audio_path.stat().st_size // 1024} KB)")
        except OSError as exc:
            print(f"  ⚠️  audio attach failed: {describe_exception(exc)}")

    raw = client.generate(parts)
    try:
        data = _parse_json_blob(raw)
    except json.JSONDecodeError as exc:
        raise GeminiError(f"Gemini did not return JSON ({exc.msg}); first 200 chars: {sanitize(raw)[:200]}") from None

    candidate.source_text = str(data.get("source_text") or "")
    candidate.topic = str(data.get("topic") or candidate.source_text or candidate.name)
    candidate.title = str(data.get("title") or candidate.topic)[:100]
    candidate.description = str(data.get("description") or candidate.topic)
    tags = data.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    candidate.tags = [str(t)[:30] for t in tags][:12]
    try:
        candidate.score = int(data.get("score") or 0)
    except (TypeError, ValueError):
        candidate.score = 0
    candidate.reason = str(data.get("reason") or "")
    candidate.skip = bool(data.get("skip")) or candidate.score < MIN_QUALITY_SCORE
    return candidate


# ---------------------------------------------------------------------------
# YouTube upload
# ---------------------------------------------------------------------------
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
    attempt = 0
    while response is None:
        try:
            status, response = request.next_chunk()
        except HttpError as exc:
            status_code = getattr(exc.resp, "status", None)
            if status_code in RETRYABLE_HTTP_STATUS and attempt < 4:
                attempt += 1
                delay = min(2 ** attempt, 30)
                print(f"    ↩️  upload hiccup ({describe_exception(exc)}); retry in {delay}s")
                time.sleep(delay)
                continue
            raise
        if status:
            print(f"    upload {int(status.progress() * 100)}%")
    return response["id"]


# ---------------------------------------------------------------------------
# Doctor / credential validation
# ---------------------------------------------------------------------------
def validate_credentials() -> int:
    """Offline structural check of the two JSON secrets (no values printed)."""
    failures = 0
    try:
        service = parse_json_object(Path(CREDENTIALS_FILE).read_text(), "GOOGLE_CREDENTIALS_JSON")
    except (OSError, ValueError) as exc:
        annotate("error", "Credential validation", f"GOOGLE_CREDENTIALS_JSON problem: {exc}")
        return 1
    if str(service.get("type", "")) != "service_account":
        annotate("error", "Credential validation", "GOOGLE_CREDENTIALS_JSON must be a service-account key")
        failures += 1
    else:
        missing = {"client_email", "private_key", "token_uri"} - set(service)
        if missing:
            annotate(
                "error",
                "Credential validation",
                "service-account JSON is missing required fields: " + ", ".join(sorted(missing)),
            )
            failures += 1
        else:
            print(f"✅ GOOGLE_CREDENTIALS_JSON: {service_account_summary()}")

    payload = read_youtube_token_payload()
    usable, message = token_diagnosis(payload, live=not DRY_RUN)
    if usable:
        print(f"✅ YOUTUBE_TOKEN_JSON: {message}")
        if payload is None or not extract_token_fields(payload).get("refresh_token"):
            annotate("warning", "Credential validation", f"{message} (uploads may stop working)")
    else:
        # A dry run never uploads, so a broken token is only a warning there;
        # live runs cannot continue without a usable token.
        level = "warning" if DRY_RUN else "error"
        suffix = " Dry run: warning only, uploads stay disabled until this is fixed." if DRY_RUN else ""
        annotate(level, "Credential validation", f"{message}{suffix}")
        if not DRY_RUN:
            failures += 1
    return 1 if failures else 0


def doctor() -> int:
    """Network preflight; returns non-zero when the requested mode cannot run."""
    mode = "dry-run (no uploads)" if DRY_RUN else "LIVE (uploads allowed)"
    print("=" * 64)
    print(f"🩺 Preflight doctor — mode: {mode}")
    print("=" * 64)
    fatal = 0

    # 1) service account / sheet
    try:
        sheets, drive = load_service_account()
        print(f"✅ service account loaded: {service_account_summary()}")
    except Exception as exc:  # noqa: BLE001
        annotate("error", "Doctor: Google credentials", describe_exception(exc))
        return 1

    try:
        tab = resolve_sheet_tab(sheets, refresh=True)
        result = retry_call(
            lambda: sheets.spreadsheets()
            .values()
            .get(spreadsheetId=SPREADSHEET_ID, range=f"'{tab}'!A1:L")
            .execute(),
            label="sheet read",
        )
        values = result.get("values", [])
        header = values[0] if values else []
        rows = max(0, len(values) - 1)
        print(f"✅ Google Sheet reachable: tab '{tab}', {rows} data row(s)")
        if header and header[:4] != SHEET_HEADERS[:4]:
            print(f"   header row is '{header[:3]}...' (pipeline writes its own 12-column header)")
    except Exception as exc:  # noqa: BLE001
        annotate("error", "Doctor: Google Sheet", f"cannot read the history sheet ({describe_exception(exc)})")
        fatal += 1

    # 2) drive folders
    try:
        listing = retry_call(
            lambda: drive.files()
            .list(
                q=f"'{RAW_FOLDER_ID}' in parents and trashed = false",
                pageSize=5,
                fields="files(id, name)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            .execute(),
            label="drive raw folder",
        )
        print(f"✅ Drive raw folder reachable ({len(listing.get('files', []))} item(s) in first page)")
    except Exception as exc:  # noqa: BLE001
        annotate(
            "error",
            "Doctor: Drive raw folder",
            f"cannot list RAW_FOLDER_ID ({describe_exception(exc)}). Share the folder with the service account "
            "(Editor) and check RAW_FOLDER_ID.",
        )
        fatal += 1
    try:
        meta = retry_call(
            lambda: drive.files()
            .get(fileId=PROCESSED_FOLDER_ID, fields="id, name, capabilities(canAddChildren)", supportsAllDrives=True)
            .execute(),
            label="drive processed folder",
        )
        can_add = (meta.get("capabilities") or {}).get("canAddChildren")
        print(f"✅ Drive processed folder '{meta.get('name', '?')}' (canAddChildren={can_add})")
        if can_add is False:
            annotate("warning", "Doctor: Drive processed folder", "service account cannot add files there")
    except Exception as exc:  # noqa: BLE001
        annotate(
            "warning",
            "Doctor: Drive processed folder",
            f"cannot read PROCESSED_FOLDER_ID ({describe_exception(exc)}); uploaded files will stay in Raw.",
        )

    # 3) Gemini
    try:
        client = configure_gemini()
        model = client.resolve_model()
        probe = ""
        try:
            text = client.generate(
                [{"text": "Reply with the single word: OK"}], json_mode=False, max_output_tokens=512
            )
            probe = f"probe reply {sanitize(text)[:20]!r}"
        except GeminiError as exc:
            # Newer Flash models spend the output budget on thinking tokens, so an
            # empty answer on a tiny probe still proves the model is reachable.
            if "returned no text" in str(exc):
                probe = "model answered (probe hit the output-token cap)"
            else:
                raise
        print(f"✅ Gemini reachable (model '{model}', {probe})")
        annotate("notice", "Doctor: Gemini", f"model={model} {probe}")
    except Exception as exc:  # noqa: BLE001
        annotate("error", "Doctor: Gemini", f"Gemini not usable ({describe_exception(exc)})")
        fatal += 1

    # 4) YouTube token
    payload = read_youtube_token_payload()
    fields = extract_token_fields(payload or {})
    if payload is None and not any(fields.values()):
        level = "warning" if DRY_RUN else "error"
        annotate(level, "Doctor: YouTube token", "YOUTUBE_TOKEN_JSON is not set")
        fatal += 0 if DRY_RUN else 1
    else:
        payload = payload or {}
        print(f"🔎 YOUTUBE_TOKEN_JSON fields: {', '.join(k for k, v in fields.items() if v) or '(none)'}")
        candidates = youtube_credential_candidates(payload)
        print(f"🔎 YouTube credential combinations: {[label for label, _ in candidates] or 'none'}")
        usable, message = token_diagnosis(payload, live=not DRY_RUN)
        if usable:
            try:
                _creds, label = resolve_youtube_credentials(payload)
                print(f"✅ YouTube credentials authenticate (from {label}).")
                annotate("notice", "Doctor: YouTube token", f"authenticated using {label}")
            except Exception as exc:  # noqa: BLE001
                level = "warning" if DRY_RUN else "error"
                annotate(level, "Doctor: YouTube token", describe_exception(exc))
                fatal += 0 if DRY_RUN else 1
        else:
            level = "warning" if DRY_RUN else "error"
            annotate(level, "Doctor: YouTube token", message)
            fatal += 0 if DRY_RUN else 1

    # 5) ffmpeg
    if not _have_ffmpeg():
        annotate("warning", "Doctor: ffmpeg", "ffmpeg not found; audio (first spoken line) analysis will be skipped")
    else:
        print("✅ ffmpeg available")

    print("=" * 64)
    print("❌ preflight found blocking problems" if fatal else "✅ preflight passed")
    print("=" * 64)
    return 1 if fatal else 0


def _have_ffmpeg() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True, timeout=30)
        return True
    except Exception:  # noqa: BLE001
        return False


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
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


def run() -> int:
    print("=" * 64)
    print("🚀 YouTube Auto-Publish  |  2/day US peaks  |  score>=90  |  1 topic")
    print(f"   mode: {'DRY RUN (no uploads)' if DRY_RUN else 'LIVE'}")
    print("=" * 64)

    sheets, drive = load_service_account()
    resolve_sheet_tab(sheets)
    youtube = None if DRY_RUN else load_youtube_client()
    if not DRY_RUN and youtube is None:
        raise RuntimeError(
            "YOUTUBE_TOKEN_JSON is required for a live publish run. "
            "Use the workflow dry_run input only when intentionally skipping uploads."
        )
    ensure_sheet_headers(sheets)

    rows = sheet_rows(sheets)
    logged, used_topics = state_from_rows(rows)
    booked = booked_slot_keys(rows)
    print(f"📊 Known files: {len(logged)}  |  used topics: {len(used_topics)}  |  booked slots: {len(booked)}")

    candidates = list_local_videos() + list_drive_videos(drive)
    print(f"📁 Found {len(candidates)} video(s).")

    fresh: list[VideoCandidate] = []
    for c in candidates:
        if c.name.lower() in logged or (c.drive_id or "").lower() in logged:
            print(f"  ⏭️  duplicate file: {c.name}")
            continue
        fresh.append(c)

    if not fresh:
        print("⚠️  No new videos. Idle.")
        annotate(
            "notice",
            "Pipeline summary",
            f"No new videos. files={len(logged)} topics={len(used_topics)} gemini={gemini_label()}",
        )
        return 0

    analyzed: list[VideoCandidate] = []
    problems: list[str] = []
    for c in fresh:
        print(f"\n🧠 Analyzing: {c.name}")
        try:
            local_path = materialize_file(drive, c)
            c.path = local_path
            frame = extract_first_frame(local_path, WORK_DIR / f"{local_path.stem}_frame.jpg")
            audio = extract_audio_clip(local_path, WORK_DIR / f"{local_path.stem}_open.mp3")
            if frame is None:
                print("  ⚠️  first frame could not be extracted (video may be unreadable)")
            analyze_video_with_gemini(c, frame, audio)
            print(f"  source_text: {sanitize(c.source_text)[:120]}")
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
        except GeminiQuotaError as exc:
            failure = f"Gemini quota exhausted: {describe_exception(exc)}"
            problems.append(failure)
            print(f"  ❌ {failure}")
            # A warning: the run itself can still succeed when other videos were
            # analysed (the exit code decides the job result).
            annotate(
                "warning",
                "Gemini quota exhausted",
                "The Gemini API quota for this key (all tried models) is used up, so no video "
                "could be analysed. Wait for the quota to reset, use a lighter model "
                "(GEMINI_MODEL) or raise the quota/billing in Google AI Studio.",
            )
            try:
                log_row(sheets, c, "FAILED", notes="Gemini quota exhausted; retried on the next run.")
            except Exception as log_exc:  # noqa: BLE001
                problems.append(f"could not log quota failure for {c.name}: {describe_exception(log_exc)}")
            break
        except Exception as exc:
            failure = f"analysis failed for {c.name}: {describe_exception(exc)}"
            problems.append(failure)
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
                problems.append(f"could not log analysis failure for {c.name}: {describe_exception(log_exc)}")
                print(f"  ❌ Could not log failure to Google Sheet: {describe_exception(log_exc)}")

    if not analyzed:
        print("⚠️  No video passed quality + unique-topic gates.")
        for failure in problems:
            print(f"PIPELINE_FAILURE: {failure}")
        if problems:
            annotate("error", "Pipeline failed", f"no usable video; first problem: {problems[0]}")
            return 1
        annotate("notice", "Pipeline summary", "no video passed the quality/topic gates")
        return 0

    sequenced = rank_sequence(analyzed)
    print("\n📑 Sequence (highest score first, unique topics):")
    for i, c in enumerate(sequenced, 1):
        print(f"  {i}. [{c.score}] {c.topic} — {c.title}")

    now_et = datetime.now(US_TZ)
    today_str = now_et.strftime("%Y-%m-%d")
    already = count_scheduled_for_date(rows, today_str)
    print(f"\n📅 US {today_str}: {already}/{MAX_VIDEOS_PER_DAY} already booked.")
    slots = next_open_slots(already_today=already, now_et=now_et, booked_slots=booked)
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
                log_row(sheets, candidate, status, slot_label, yt_id, notes)
            else:
                yt_id = upload_to_youtube(youtube, candidate.path, candidate, rfc)
                print(f"   🎉 youtube id={yt_id}")
                # Log the committed slot before any follow-up work, so a later
                # failure can never re-upload the same file.
                log_row(sheets, candidate, status, slot_label, yt_id, notes)
                if candidate.source == "drive" and candidate.drive_id:
                    try:
                        move_drive_to_processed(drive, candidate.drive_id)
                        print("   📦 moved to Processed folder")
                    except Exception as move_exc:  # noqa: BLE001
                        problems.append(
                            f"drive move failed for {candidate.name}: {describe_exception(move_exc)}"
                        )
                        print(f"   ⚠️  drive move failed: {describe_exception(move_exc)}")
            results.append(
                PipelineResult(candidate.title, candidate.name, status, slot_label, yt_id, notes)
            )
        except Exception as exc:
            failure = f"publish failed for {candidate.name}: {describe_exception(exc)}"
            problems.append(failure)
            print(f"   ❌ {failure}")
            traceback.print_exc()
            try:
                log_row(
                    sheets,
                    candidate,
                    "FAILED",
                    slot_label,
                    "",
                    f"Publish failed ({type(exc).__name__}): {str(exc)[:400]}",
                )
            except Exception as log_exc:  # noqa: BLE001
                problems.append(f"could not log publish failure for {candidate.name}: {describe_exception(log_exc)}")
            results.append(
                PipelineResult(candidate.title, candidate.name, "FAILED", slot_label, "", f"{type(exc).__name__}")
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
    for problem in problems:
        print(f"PIPELINE_FAILURE: {problem}")

    scheduled = [r for r in results if r.status in {"SCHEDULED", "UPLOADED"}]
    failed_publishes = [r for r in results if r.status == "FAILED"]
    if failed_publishes:
        annotate("error", "Pipeline failed", problems[0] if problems else "a video could not be published")
        return 1
    if problems:
        annotate(
            "warning",
            "Pipeline warnings",
            f"{len(problems)} non-fatal problem(s); first: {problems[0]}",
        )
    summary = (
        f"mode={'dry-run' if DRY_RUN else 'live'} files={len(candidates)} fresh={len(fresh)} "
        f"queued={len(analyzed)} scheduled={len(scheduled)} gemini={gemini_label()}"
    )
    if problems:
        summary += f" warnings={len(problems)}"
    annotate("notice", "Pipeline summary", summary)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="YouTube auto-publish pipeline")
    parser.add_argument("--doctor", action="store_true", help="run the network preflight checks")
    parser.add_argument(
        "--validate-credentials",
        action="store_true",
        help="offline structural check of the JSON secrets",
    )
    args = parser.parse_args(argv)
    if args.doctor:
        return doctor()
    if args.validate_credentials:
        return validate_credentials()
    return run()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"❌ Critical Error in Pipeline: {describe_exception(e)}")
        traceback.print_exc()
        annotate("error", "Pipeline failed", f"critical error: {describe_exception(e)}")
        sys.exit(1)

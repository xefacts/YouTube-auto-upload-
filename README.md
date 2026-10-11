# YouTube Auto-Upload Pipeline

Python + GitHub Actions pipeline that:

Niche: **personal finance and business**. All upload history and metadata live in the Google Sheet.

1. Scans `videos/` **and** a Google Drive `Raw_Videos` folder
2. Extracts the first frame and asks **Gemini** for topic, title, description, tags, and a quality score
3. Deduplicates against **Google Sheets** (filename, Drive id, title)
4. Ranks leftover videos so similar topics are not back-to-back
5. Schedules **exactly 2 videos per US day** at YouTube peak traffic: **14:00 ET** and **20:00 ET**
6. Uploads only videos with **AI score ≥ 90**; ignores low quality
7. **One topic = one video** (never two videos on the same topic)
8. Topic comes from first-frame OCR text or the first spoken sentence (~90%), not the filename
9. Gemini writes SEO title, description, and tags; YouTube `publishAt` + Sheets report

## Setup

### Secrets (GitHub → Settings → Secrets and variables → Actions)

| Secret | Purpose |
| --- | --- |
| `GOOGLE_CREDENTIALS_JSON` | Service-account JSON with access to Drive + the spreadsheet |
| `GEMINI_API_KEY` | Gemini API key |
| `YOUTUBE_TOKEN_JSON` | OAuth **user** token (`authorized_user` JSON). YouTube does **not** accept service accounts for uploads. |

Share the Drive folders and the Sheet with the service-account email.

### Local / first-time YouTube OAuth

Create a Desktop OAuth client in Google Cloud, enable YouTube Data API v3, then generate `youtube_token.json` once on a machine with a browser and paste it into `YOUTUBE_TOKEN_JSON`.

### Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY=...
# place client_secret.json and optionally youtube_token.json in the repo root
python main.py
```

`DRY_RUN=true` logs metadata to Sheets without calling YouTube.

### Sheet columns

Logged At (UTC) · Source File · Source Id · Title · Description · Tags · Topic · Score · Status · Scheduled For (ET) · YouTube Video ID · Notes

Status values: `SCHEDULED`, `DRY_RUN`, `IGNORED`, `FAILED`.

## Schedule

GitHub Actions cron: `0 13,22 * * *` (before the two ET publish windows). Manual **Run workflow** is also enabled.

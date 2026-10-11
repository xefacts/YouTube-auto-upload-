# YouTube Auto-Upload Pipeline

GitHub Actions + Python. Niche: **personal finance and business**.  
Saari video history Google Sheet mein rehti hai.

## GitHub par kya chalta hai

Workflow: `.github/workflows/youtube_pipeline.yml`

| Trigger | Kab |
| --- | --- |
| Cron `0 16 * * *` | US afternoon slot se pehle (2:00 PM ET) |
| Cron `0 23 * * *` | US prime-time slot se pehle (8:00 PM ET) |
| **Actions → Run workflow** | Manual (optional Dry run) |

Har run:

1. Drive `Raw_Videos` + local `videos/` scan
2. Pehla frame + pehli 20s audio → Gemini
3. Score **&lt; 90** ignore
4. Same **topic** pehle Sheet mein ho to skip
5. Roz max **2** videos: **14:00 ET** aur **20:00 ET**
6. SEO title / description / tags AI
7. YouTube `publishAt` + Sheet log

## Secrets

Repo → **Settings → Secrets and variables → Actions**

| Secret | Required | Purpose |
| --- | --- | --- |
| `GOOGLE_CREDENTIALS_JSON` | yes | Service account (Drive + Sheet) |
| `GEMINI_API_KEY` | yes | Gemini |
| `YOUTUBE_TOKEN_JSON` | for real upload | YouTube user OAuth JSON |

Service-account email ko Sheet aur Drive folders (Raw + Processed) **Editor** share karein.

Sheet: `15jAt6HUoOrucNA-79y8u7hunq7vUUIBMrTOOeiG-618`

Columns: Logged At · Source File · Source Id · Title · Description · Tags · Topic · Score · Status · Scheduled For (ET) · YouTube Video ID · Notes

Status: `SCHEDULED`, `DRY_RUN`, `LOW_QUALITY`, `DUPLICATE_TOPIC`, `IGNORED`, `FAILED`

## YouTube token (ek dafa)

Google Cloud mein YouTube Data API v3 + Desktop OAuth client. Local machine par token banao, JSON `YOUTUBE_TOKEN_JSON` secret mein paste karo. Service account se YouTube upload nahi hota.

## Local

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=...
# client_secret.json (+ optional youtube_token.json) repo root par
python main.py
```

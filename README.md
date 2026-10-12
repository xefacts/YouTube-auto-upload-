# YouTube Auto-Upload Pipeline

GitHub Actions + Python. Niche: **personal finance and business**.
Saari video history Google Sheet mein rehti hai.

## Rules (fixed)

| Rule | Value |
| --- | --- |
| Niche | personal finance and business |
| Videos per US day | max **2** |
| Slots | **14:00 ET** and **20:00 ET** |
| Quality gate | AI score **< 8.5/10 (85/100) → ignore** |
| Topics | one topic = one video (Sheet history + in-batch) |
| Topic source | first-frame on-screen text or first spoken line (not the filename) |
| Metadata | Gemini writes title / description / tags |
| History | Google Sheet `15jAt6HUoOrucNA-79y8u7hunq7vUUIBMrTOOeiG-618` |

## How runs are triggered

| Trigger | Uploads? | Notes |
| --- | --- | --- |
| `schedule` (cron `0 16,23 * * *`) | yes (live) | runs before the 14:00/20:00 ET slots |
| **Actions → Run workflow** (`workflow_dispatch`) | only if `dry_run` is unchecked | the checkbox defaults to **dry run** |
| `repository_dispatch` (`event_type=publish`) | yes, unless `client_payload[dry_run]=true` | works with a token that only has `contents: write` |
| `push` to `main` / `arena/**` | **never** | always a dry run, keeps merges safe |

Manual dry run from the command line (Arena/GitHub App token):

```bash
gh api -X POST repos/OWNER/REPO/dispatches \
  -f event_type=publish -f client_payload[dry_run]=true
```

Live run:

```bash
gh api -X POST repos/OWNER/REPO/dispatches \
  -f event_type=publish -f client_payload[dry_run]=false
```

> `gh workflow run ...` needs the `Actions: write` permission. The Arena GitHub App
> connection only has `contents: write`, so it returns *403 Resource not accessible
> by integration*. Use the Actions UI button or the `repository_dispatch` calls above.

## What a run does

1. Read the Sheet history (used files, used topics, booked slots).
2. Scan Drive `Raw_Videos` + local `videos/`.
3. First frame (OCR) + first 20s audio (first spoken line) → Gemini.
4. Score **< 85 (8.5/10)** → `LOW_QUALITY`; known topic → `DUPLICATE_TOPIC`.
5. Pick the next open **14:00 / 20:00 ET** slots (max 2 per US day).
6. Gemini SEO title / description / tags → YouTube `publishAt` (private until then).
7. Log every decision in the Sheet; uploaded Drive files move to `Processed`.

Dry runs write `DRY_RUN` rows and never upload, and `DRY_RUN`/`FAILED` rows stay
retryable on the next run.

## Secrets

Repo → **Settings → Secrets and variables → Actions**

| Secret | Required | Purpose |
| --- | --- | --- |
| `GOOGLE_CREDENTIALS_JSON` | yes | Service account (Drive + Sheet) |
| `GEMINI_API_KEY` | yes | Gemini |
| `YOUTUBE_TOKEN_JSON` | yes for live runs | YouTube user OAuth JSON |

`YOUTUBE_TOKEN_JSON` must contain the OAuth fields (`client_id`, `client_secret`,
`refresh_token`); aliases and nested `installed`/`web` client files are understood
too, but only a refresh token keeps working long term. Two ways to provide it:

1. **Regenerate the JSON** locally with a Desktop OAuth client:

   ```bash
   pip install google-auth-oauthlib
   python tools/get_youtube_token.py --client-secret client_secret_xxx.json
   ```

2. **Split secrets** (no local tooling): keep `YOUTUBE_TOKEN_JSON` as-is (it
   already carries `client_id`/`client_secret`) and add
   `YOUTUBE_REFRESH_TOKEN` (a refresh token minted for the *same* OAuth client,
   e.g. via the OAuth 2.0 Playground with the `youtube.upload` scope).
   `YOUTUBE_CLIENT_ID` / `YOUTUBE_CLIENT_SECRET` are also honoured as overrides.

   The pipeline tries every combination of payload/split client credentials and
   refresh tokens, so a refresh token minted with a *different* OAuth client than
   the one stored in `YOUTUBE_TOKEN_JSON` still works. `invalid_grant` means the
   refresh token itself is dead: it was revoked, it expired (consent screen still
   in **Testing** expires refresh tokens after 7 days) or it belongs to a deleted
   client - mint a fresh one.

Service-account email ko Sheet aur Drive folders (Raw + Processed) **Editor** share karein.

Sheet: `15jAt6HUoOrucNA-79y8u7hunq7vUUIBMrTOOeiG-618`

Columns: Logged At · Source File · Source Id · Title · Description · Tags · Topic · Score · Status · Scheduled For (ET) · YouTube Video ID · Notes

Status: `SCHEDULED`, `DRY_RUN`, `LOW_QUALITY`, `DUPLICATE_TOPIC`, `IGNORED`, `FAILED`

## Diagnostics

Each run performs two preflight steps before the pipeline:

* `python main.py --validate-credentials` – offline JSON shape check (field **names**
  only, never values).
* `python main.py --doctor` – live checks: Sheet/tab access, Drive raw + processed
  folders, Gemini model discovery + a tiny probe, YouTube token refresh, ffmpeg.

A broken YouTube token is only a warning in dry-run mode (dry runs never upload)
and a hard error in live mode. The free Gemini tier allows only **20 requests per
model per day**, so the pipeline spends one request per video plus one doctor
probe; pin a lighter model with the `GEMINI_MODEL` repository variable
(Settings -> Secrets and variables -> Actions -> Variables) when the quota is
tight, or enable billing. Failures are reported as GitHub check annotations
and in the run's job summary; secret values are redacted from every log line.

## Dependencies

`requirements.txt` is a fully pinned CPython 3.11 runtime lock (including
transitive dependencies). The workflow installs the wheel-only lock without
running pip's backtracking resolver, then runs `pip check` and the rule tests.
Gemini is called over the REST API, so the deprecated `google-generativeai`
package is no longer needed; the model is auto-discovered for the API key
(`GEMINI_MODEL=auto`, override with a concrete model id if required).

## Local

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=...
# client_secret.json (+ optional youtube_token.json) repo root par
python main.py --validate-credentials
python main.py --doctor
DRY_RUN=true python main.py
```

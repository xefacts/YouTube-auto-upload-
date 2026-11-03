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
| History | Google Sheet (id lives in the `SPREADSHEET_ID` secret, never in the repo) |

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
| `SPREADSHEET_ID` | yes | Google Sheet id that stores run history |
| `RAW_FOLDER_ID` | yes | Drive folder with new videos (Raw) |
| `PROCESSED_FOLDER_ID` | yes | Drive folder uploaded videos move to (Processed) |
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

Sheet: the spreadsheet whose id you stored in the `SPREADSHEET_ID` secret.

Columns: Logged At · Source File · Source Id · Title · Description · Tags · Topic · Score · Status · Scheduled For (ET) · YouTube Video ID · Notes

Status: `SCHEDULED`, `DRY_RUN`, `LOW_QUALITY`, `DUPLICATE_TOPIC`, `IGNORED`, `FAILED`

## Public repository

This repo is meant to be **public**. The source deliberately contains **no
Google resource ids and no credentials**:

* The sheet/folder ids come only from `SPREADSHEET_ID`, `RAW_FOLDER_ID` and
  `PROCESSED_FOLDER_ID` secrets — `main.py` refuses to run (`--doctor` exits
  non-zero, a plain run raises the missing NAMES, never values) until all
  three are set.
* Credential files (`client_secret*.json`, `*_token.json`, `*.log`) are
  git-ignored; never commit them.
* Tests enforce both rules (config guard + regex-shape guard), so a hardcoded
  id cannot come back in unnoticed.

Before you flip the visibility switch, make sure **every credential that ever
appeared in an old commit or branch has been revoked/rotated** in Google Cloud
Console — deleting or overwriting files does not erase git history.

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

## Troubleshooting

### Job fails in ~2 seconds with "recent account payments have failed"

The Actions job never starts, so nothing in the repo can fix it. Open
**Settings → Billing & plans** (user settings, not the repo) and either settle the
failed payment or raise the Actions spending limit. Until then every scheduled,
dispatched and push run fails instantly, and no dry-run result is produced.

### `invalid_grant: Bad Request` on the YouTube token

Google refuses the refresh token. The pipeline now prints the diagnosis with the
error, and it always comes down to one of:

1. **The token was minted with a different OAuth client** than the
   `client_id` / `client_secret` used at runtime — the most common cause. In the
   [OAuth 2.0 Playground](https://developers.google.com/oauthplayground) open the
   gear icon and tick **Use your own OAuth credentials** *before* step 1, then use
   that same client id/secret in `YOUTUBE_CLIENT_ID` / `YOUTUBE_CLIENT_SECRET`.
   `python tools/get_youtube_token.py --client-secret client_secret_xxx.json`
   cannot hit this trap because it uses one client for both steps.
2. **Consent screen still in Testing** — refresh tokens expire after 7 days. Move
   the app to Production or re-mint weekly.
3. **Revoked / recreated client** — check
   <https://myaccount.google.com/permissions> and the Cloud Console credentials
   list.

A dead refresh token can only be replaced, never repaired. Secrets are never
printed: the doctor log shows `client_id=fp:…` / `refresh_token=fp:…`
fingerprints (first 12 hex chars of the SHA-256) so you can confirm which secret
CI actually loaded:

```bash
# fingerprint only - the secret itself is never typed or echoed
tr -d '\n' < refresh_token.txt | sha256sum | cut -c1-12
```

(A trailing newline is ignored, so a value pasted into a file and the value read
from the secret produce the same fingerprint.)

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
export SPREADSHEET_ID=...        # sheet id (GitHub secret ka saathi)
export RAW_FOLDER_ID=...         # Raw drive folder id
export PROCESSED_FOLDER_ID=...   # Processed drive folder id
# client_secret.json (+ optional youtube_token.json) repo root par
python main.py --validate-credentials
python main.py --doctor
DRY_RUN=true python main.py
```

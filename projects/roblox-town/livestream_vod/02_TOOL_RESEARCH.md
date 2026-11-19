# Cloud VOD processors — what actually works on an 18-hour public YouTube VOD

Checked **2026-11-16** against vendor docs/pricing pages. Each row states its own
verification status; anything I could not read in a first-party page is marked
`UNVERIFIED (needs a probe)` and must not be promised to the user as fact.

## 1. The three jobs, and who can do each

| Job | Needs | Candidates that can do it **without** an upload |
|---|---|---|
| **A. Understand** (timestamped evidence: transcript, events, banners) | public URL ingest + timestamped output | **Gemini API (verified)** · VideoDB (verified ingest) · TwelveLabs (not checked) |
| **B. Extract** (only approved ranges → MP4 files) | range-limited clip export from a URL | **Apify YouTube Video Clipper (verified)** · VideoDB timelines (verified API, limits unverified) · ClipSDK (verified, but 3 h cap kills it) |
| **C. Edit** (assembly, captions, mix, 9:16) | full timeline | my own pipeline (pack already built) — no vendor needed |

## 2. Comparison table

| Tool | Imports public YouTube URL? | Max length / file limits | Pricing (verified) | Export options | Verdict here |
|---|---|---|---|---|---|
| **Gemini API — video understanding** | **Yes**, `{"type":"video","uri":"<youtube url>"}` | Free tier: **8 h of YouTube video per day**; paid tier: no length limit. Per request, 1M-context models handle ~3 h at low media res, so an 18 h VOD **must** be windowed with `start_offset`/`end_offset`. Feature is in **preview, currently no charge for the URL path** | Tokens: ~100 tok/s at low media res (66/frame + audio), transcript layer billed as text | No video export — evidence only (JSON text) | **Primary verification engine.** `content_layers: ["transcript"]` → cheap timestamped speech; `["frames"]` + `start_offset/end_offset` → visual proof of a banner. Two-source rule satisfied |
| **Apify — `fractalai/youtube-video-clipper`** | **Yes**, `videoUrl` + clip list | **20 clips per run, ≤10 min each**; 360p/480p/720p/1080p; stream-copy (no re-encode) | Per-event: **1080p $1.50/clip, 720p $1.20, 480p $1.00**; free plan up to **3 clips/month**. (The 360p "primary" event is listed at $1.40 — the table is internally inconsistent, so confirm the console's cost preview before the paid run) | MP4 URL per clip + thumbnail URL | **Primary range extractor.** 9 clips ≈ $13.50 @1080p |
| **VideoDB** | **Yes**, `coll.upload(url="https://www.youtube.com/watch?v=…")`, also via MCP | Max single-video duration **not documented in the pages I could verify** → probe with one short test. Storage/processing metered in credits | Free account: **$20 credits, 50 uploads**; then pay for storage + processing (rates unverified here) | `video.generate_stream(timeline=…)` → playable HLS/MP4; clip/reframe/subtitle tools | **Best single-vendor alternative** if its 18 h ingest works. Cheaper for iterative cutting, but it is the one key fact we cannot state yet |
| **ClipSDK** | Yes (YouTube, Twitch, Kick, Drive…) | 48 h accepted, **but beyond 3 h only the first 3 h are clipped** | **$0.03 per source-minute**, clips included | MP4 + SRT, 1–20 clips, 10–90 s | **Rejected** for this VOD: hour 6+ is unreachable |
| **Opus Clip / Vizard / Klap / 2short / OpenShorts** | Yes (link ingest) | Free tiers 30–60 min/month of *processing*, watermark, short clip caps (Vizard 720p; OpenShorts 60 min first video then 20 min/month) | $9.90–$29/month | 9:16 clips with burned captions | **Rejected as the engine**, useful only as a sanity check of which 60 s a stranger would pick. Minutes are far too scarce for 18 h and they re-cut, not hand us clean ranges |
| **Descript** | Web editor: paste a YouTube link + it transcribes. **API/MCP: YouTube URLs unsupported** | "Split anything longer than **15 h**" — an 18 h file will not auto-transcribe. Media-minutes metered: Free 60 min, Hobbyist 10 h, Creator 30 h, Business 40 h | $16–$50/seat/mo yearly, $24–$65 monthly | MP4/SRT/timeline XML to Premiere/FCP | **Not viable** as ingest for 18 h; fine later if you want transcript-based trimming of the *extracted windows* |
| **api.video** | No YouTube import (upload/URL-to-MP4 only) | 30 GiB, **1440 min (24 h)** per video | Encoding free; storage $0.00285/min/mo; delivery $0.0017/min; AI transcription $0.10/min | HLS + MP4 download | Only after extraction — redundant with my encoder |
| **Mux / Cloudinary fetch** | Do not accept YouTube as an ingest source (ToS) | — | — | — | **Out of scope** |
| **YouTube Studio (owner route)** | n/a — you already have it | Studio trims/saves new videos; **Clips are 5–60 s**; a stream this long is awkward to edit in Studio | free | new video / clip link | Cheapest *legal* path for small moments **if you own the channel**; use it for a 60 s sanity check, not for 6 windows |

## 3. Recommendation

1. **Verify with Gemini** (no footage moves): transcript pass over the first ~3 h, then frame
   probes on 2–4 candidate windows. Output: timestamps + verbatim on-screen text.
2. **Extract with Apify** (only the approved 6–9 windows): 1080p, ≤10 min each.
3. **Assemble locally** with the existing pack (`ray.py` renderer, TTS, SFX, caption engine).
4. Keep **VideoDB** as plan B if you would rather not pay per clip and would accept one probe
   upload to prove 18 h ingest.

## 4. Facts I could *not* verify (do not quote these as settled)

- VideoDB maximum source duration and its per-minute rates.
- Apify's true 360p price (primary-event row contradicts the resolution rows).
- Whether Gemini's YouTube-URL path accepts `start_offset` on an **18 h** source with windows
  deep into the timeline (documented for uploaded files; URL path is preview). The S1 command
  in `00_WORKFLOW.md` is written to fail loudly if a window is refused — that failure is the
  evidence we need, and it costs nothing on the free tier.
- YouTube ToS position for third-party downloads: Apify/ClipSDK fetch the stream themselves.
  **If you do not own this channel, the defensible route is metadata + transcript only, or
  Studio clips made by the channel owner.** That decision is yours and it changes nothing in
  the story pack — only which column the EDL's `verification` values come from.

## 5. Sources

- Gemini video understanding (YouTube URLs, limits, `start_offset`/`end_offset`, `content_layers`, token maths) — https://ai.google.dev/gemini-api/docs/video-understanding
- Apify YouTube Video Clipper (input schema, 20 clips × 10 min) — https://apify.com/fractalai/youtube-video-clipper
- Apify pricing events (1080p/720p/480p, free tier) — https://apify.com/fractalai/youtube-video-clipper/pricing
- VideoDB SDK / agent docs (YouTube `upload(url=…)`, `generate_stream`, free credits) — https://github.com/video-db/skills · https://docs.videodb.io
- ClipSDK (48 h accept, first-3-h clipping, $0.03/source-min) — https://clipsdk.com/
- Descript limits (15 h transcribe ceiling, media minutes, no API YouTube import) — https://www.descript.com/pricing
- api.video limits (30 GiB / 1440 min, pricing) — vendor pricing summary, 2026-06
- Opus/Vizard/Klap/2short/OpenShorts free-tier minutes — https://www.openshorts.app/platforms/youtube

# Cloud-first VOD workflow — 18h livestream → shorts

**Source VOD:** https://www.youtube.com/live/qSyo5d-dVzA (public)
**Target:** vertical shorts cut from the *first two completed missions*, sourced from the livestream.
**Hard rules this workflow obeys**

1. The 18-hour file is **never** downloaded to a phone, laptop or this sandbox.
2. No gameplay event is called "a fact" until it has a timestamp from a named source.
3. Every scene row carries `verification` = `UNVERIFIED` / `PARTIAL` / `VERIFIED` + `evidence_ref`.
4. Only the approved time ranges are ever extracted (a few 10-minute windows, not the VOD).
5. Story, narration, captions, sound design and cut instructions are delivered **in full**
   even while the footage is still unverified.

---

## 0. Division of labour (why two of these steps are yours)

| Who | Can do | Cannot do |
|---|---|---|
| Me (this agent) | story, EDL, caption text, sound design, TTS narration, render/QC scripts, assembly instructions | reach `youtube.com` or `generativelanguage.googleapis.com` — my sandbox network only opens GitHub / npm / PyPI |
| You | paste 3 small text blobs, run 2 commands, approve cost | must not upload 18h of video anywhere |

So the pipeline is: **I write every artifact → you execute 2 cloud calls → I finish the EDL with real timecodes.**

---

## 1. Stage map

| # | Stage | Tool (verified) | Output | Cost | Download? |
|---|---|---|---|---|---|
| S0 | Inventory: title, chapters, duration, game name | YouTube page + auto-chapters (you copy/paste) | `evidence/s0_meta.md` | free | none |
| S1 | **Transcript scan** of chosen windows | Gemini API, `content_layers: ["transcript"]`, `start_offset`/`end_offset` | `evidence/s1_*.json` — timestamped speech | free tier: 8 h of YouTube video/day | none |
| S2 | Mission-boundary detection | me, from S1 | `03_EDL_M01_M02.csv` fills `src_in`/`src_out` | free | none |
| S3 | **Visual confirmation** of candidate beats | Gemini API, `content_layers: ["frames"]`, 1–2 fps, `media_resolution: low`, only the candidate windows (20–40 min total) | `evidence/s3_*.json` | ~80k tokens per 20 min of frames (cents) | none |
| S4 | Range extraction — **only** approved windows | Apify `fractalai/youtube-video-clipper` (max 20 clips × 10 min/run) **or** VideoDB `generate_stream(timeline)` | 6–12 MP4s, named by source timecode | Apify: $1.50/clip @1080p, $1.20 @720p; free tier 3 clips | cloud only, clips land in cloud storage |
| S5 | Assembly | EDL + caption sheet + my TTS + skill SFX | 1080×1920 shorts | TTS/SFX already in the pack | final MP4 only |
| S6 | QC + publish | contact sheet, loudness −14 LUFS, title/desc | deliverables | free | final MP4 |

**Gate between S3 and S4:** a range is only extracted after it has an `edl_id` and a
`verification` value of at least `PARTIAL`. Nothing else is ever pulled.

---

## 2. The verification ladder (this is the part that keeps us honest)

| Status | Meaning | Minimum requirement |
|---|---|---|
| `UNVERIFIED` | idea / template row | no source yet — timecodes say `TBC` |
| `PARTIAL` | one source agrees | transcript timestamp **or** a frame screenshot, never both missing |
| `VERIFIED` | two independent looks agree | transcript line at `HH:MM:SS` **and** the frame pass at the same second (±3 s) confirms what is on screen |

A row may be marked `VERIFIED` from a single frame source **only** when the frame shows
unambiguous on-screen text (e.g. a "MISSION COMPLETE" banner) and that banner is quoted
verbatim in `evidence_ref`.

---

## 3. Exact commands (you run these two)

Everything runs from the project folder; nothing downloads the VOD.

```bash
# 0. one-time
pip install google-genai requests

# 1. transcript scan of the first ~3 hours (where two missions almost always live)
python scripts/verify_vod.py --url "https://www.youtube.com/live/qSyo5d-dVzA" \
  --mode transcript --start 0 --end 10800 --out evidence/s1_0_3h.json

# 2. frame probe of whatever windows S2 flags (example window)
python scripts/verify_vod.py --url "https://www.youtube.com/live/qSyo5d-dVzA" \
  --mode frames --start 1430 --end 1610 --fps 2 \
  --ask "List every on-screen mission banner, objective tick and boss/completion UI with MM:SS." \
  --out evidence/s3_1430_1610.json
```

Paste both JSON files back into the chat (they are text, a few KB). I then:
fill real timecodes into the EDL, mark each row `PARTIAL`/`VERIFIED`, and emit the final
Apify/VideoDB request with only the surviving ranges.

```bash
# 3. extraction (only after I hand you the approved manifest)
python scripts/request_clips_apify.py --manifest footage_requests_m01_m02.csv --dry-run
python scripts/request_clips_apify.py --manifest footage_requests_m01_m02.csv --quality 1080p
```

---

## 4. Inputs I still need from you (text only — no uploads)

| # | Item | Why | Format |
|---|---|---|---|
| A | VOD title, game name, description/chapters as text | S0 baseline; tells me what a "mission" is in this game | paste |
| B | The two mission names, in your words | so the EDL is about *your* two missions, not guesses | paste |
| C | Channel ownership: yes/no | if yes, YouTube Studio's own trim/clip tools become the cheapest legal source; if no, we stay on metadata-only claims | 1 word |
| D | One Gemini API key (free tier is enough for S1) | the only way this sandbox can "see" the VOD | env var, never pasted here |

Without A–D this stays at `UNVERIFIED` — and that is what the EDL ships as, by design.

---

## 5. Budget for the first two missions (worst case, verified pricing)

| Line | Qty | Unit | Cost |
|---|---|---|---|
| Gemini S1 transcript windows | 18 h | free tier | $0.00 |
| Gemini S3 frame probes | ~40 min of frames | ~160k tokens | ≈ $0.05–0.15 |
| Apify 1080p windows | 6 × ≤10 min | $1.50/clip | $9.00 |
| Apify 1080p spare windows | 2 | $1.50/clip | $3.00 |
| **Total** | | | **≈ $12** (or $9.60 at 720p) |

Cheaper route if you prefer one vendor: VideoDB (YouTube ingest + `generate_stream` timeline
export), free account = $20 credits / 50 uploads — enough for this job, but its maximum
single-video duration is **not documented in the pages I could verify**, so it must be
probed with one cheap test upload before we commit (see `02_TOOL_RESEARCH.md`).

---

## 6. What is deliberately *not* in this plan

- No full-VOD download, no torrent, no "send me the file".
- No claim like "at 4:32:10 the player beats the boss" until `evidence/` holds a line proving it.
- No stock footage pretending to be your stream; b-roll is only ever our own generated pack.
- No re-use of the Hiccup Town characters as if they appeared in the VOD.

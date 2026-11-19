# Livestream VOD pack — cloud-first, no full download

> ⚠️ **SUPERSEDED (2026-11-16):** Budget ab **$0.00** hai. Paid workflow (Apify + Gemini)
> **removed** kar diya gaya hai. Active workflow ab hai:
> **`zero_budget_gta6/`** — complete $0 workflow, free transcript, Roman Hindi story,
> editing timeline, captions + sound design. Neeche wale docs reference ke liye hain.

Source: `https://www.youtube.com/live/qSyo5d-dVzA` (public, 18 h)
Goal: two vertical shorts from the **first two completed missions**.

This folder is additive. The existing blocky production pack
(`../REPORT.md`, `ray.py`, `story_town.py`, `out/hiccup_town_v3_1080p.mp4` on Drive) is
untouched and still builds.

## Files

| File | What it is | State |
|---|---|---|
| `00_WORKFLOW.md` | the practical pipeline: 7 stages, gates, who runs what, budget | **complete** |
| `01_FOOTAGE_REQUIREMENTS.md` | exact footage spec: formats, ≤10 min clips, 9 clips total, crop safety, rejection rules | **complete** |
| `02_TOOL_RESEARCH.md` | what can import the public VOD + process ranges, with verified limits/prices/export and sources | **complete** |
| `03_EDL_M01_M02.csv` | 22-row EDL, M1 = 52 s, M2 = 48 s, every row `UNVERIFIED` with `src_in/src_out = TBC` | **structure complete, timecodes blocked** |
| `04_STORY_NARRATION_CAPTIONS.md` | series spine, slot dictionary, full narration, caption rules, end cards, honest fallback | **complete** |
| `05_SOUND_DESIGN.csv` | 24 cues mapped to real files in `../ref/skill/blocky-shorts/assets/sfx/` | **complete** |
| `footage_requests_m01_m02.csv` | the only file the extractor reads; all rows `BLOCKED` until verified | **complete** |
| `scripts/verify_vod.py` | Gemini YouTube-URL verifier (transcript window / frame window) | **runnable** |
| `scripts/request_clips_apify.py` | range-only extractor, dry-run + cost estimate, refuses unapproved rows | **runnable, dry-run tested** |
| `evidence/` | where the JSON proof files land; every EDL row points here | empty (expected) |

## Status board

| Item | Status | Blocked on |
|---|---|---|
| Workflow + footage requirements | done | — |
| Tool research (limits, pricing, export) | done | two vendor facts flagged as unverified (see `02_TOOL_RESEARCH.md` §4) |
| Story / narration / captions / sound design | done | slot values only |
| EDL structure for M1 + M2 | done | real timecodes |
| Real timecodes + `VERIFIED` marks | **blocked** | one Gemini transcript pass (free) |
| Footage clips | **blocked** | approved ranges (then ≈ $9–13 at Apify) |

## What unblocks everything

1. VOD title + game name + description/chapters (text).
2. The two mission names in your words.
3. Channel ownership yes/no.
4. A Gemini API key in your shell (`export GEMINI_API_KEY=...`) — the commands are in
   `00_WORKFLOW.md` §3. Paste back the two small JSON files; no video ever moves.

## Rules this pack follows

- No 18-hour download, anywhere.
- No scene in the EDL without an `evidence_ref`.
- Narration slots that stay empty get deleted, not filled with guesses.
- Only the approved 9 windows (≈ 0.8 % of the VOD) are ever extracted.

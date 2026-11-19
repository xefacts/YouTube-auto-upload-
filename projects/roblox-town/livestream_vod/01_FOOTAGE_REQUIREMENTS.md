# Exact footage requirements — first two completed missions

Everything below is the *specification of the footage we need*, not a claim that it exists.
Status of every row today: **UNVERIFIED** (no timestamp has been proven yet).

## 1. Accepted delivery formats (S4 output)

| Field | Requirement | Why |
|---|---|---|
| Container / codec | MP4, H.264 High, yuv420p, AAC 48 kHz stereo | stream-copy friendly, no generational loss |
| Resolution | **1080×1920 after crop**; source 1920×1080 or 2560×1440 accepted | vertical re-frame needs ≥1080 px on the short side |
| Source resolution of the clip | 1080p preferred, 720p acceptable | below 720p the crop looks soft in 9:16 |
| Frame rate | keep source (30 or 60). No frame-rate conversion | 60 fps gameplay slowed to 50% for the "clutch" beat |
| Clip length | **≤ 10 min per clip** (hard limit of the extractor); target 20–90 s of *usable* material inside each | cut in-house, buy time once |
| Naming | `m{mission}_w{window}_{src_in}_{src_out}.mp4`, e.g. `m01_w2_01-14-20_01-24-20.mp4` | timecode survives renaming |
| Timecode format | `HH:MM:SS.mmm` from VOD start, ±0.5 s | must match the EDL column exactly |
| Audio | untouched original track (no music, no gain) | narration is mixed later; original game audio is the accent layer |
| Watermarks | none added; overlay text from the stream itself is fine | overlay text is evidence, not dirt |

## 2. Quantity budget (keeps the bill near $10)

| Item | Count | Max length each | Purpose |
|---|---|---|---|
| M1 windows | 3 | 10 min | cold open / escalation / completion |
| M2 windows | 3 | 10 min | setup / fail-or-clutch / completion |
| Safety windows | 2 | 10 min | fallback if a beat turns out to sit outside its window |
| Title/idle window | 1 (optional) | 2 min | stream intro, for a 2-second "we are live" sting |
| **Total** | **≤ 9 clips** | | ≈ 90 min of source, out of 18 h (**0.8 % of the VOD**) |

## 3. Content requirements per window (what must be inside the frame)

Marked ● = must be visible, ○ = nice to have.

| # | Element | Why the edit needs it |
|---|---|---|
| 1 | ● The exact moment the mission completes (banner, checklist tick, reward pop) | this is the only hard proof a mission *completed*; without it the mission is `UNVERIFIED` |
| 2 | ● Player character + HUD legible in a 9:16 crop | if the HUD sits at the frame edge it gets cropped away |
| 3 | ● The 15 s before completion (final action) | that is the payoff shot |
| 4 | ○ The failure/retry 1–3 min before completion | gives the short its "will he make it" middle act |
| 5 | ○ A reaction (voice, jump, chat pop) after completion | end-card beat |
| 6 | ○ Mission name/title card on screen | lets us caption it verbatim instead of inventing a name |
| 7 | ● No third-party music under the segment if possible | licensing when we re-publish |

## 4. Crop safety (checked before extraction)

For every proposed window we require one **still frame** (in the S3 evidence JSON) so I can
confirm:

- action stays inside the central 56 % of the 16:9 frame (that is all a 9:16 crop keeps at 1:1 scale),
- HUD/counters are not straddling the crop line,
- captions/banners are not cut by the vertical reframe,
- no facecam overlay sitting exactly where the bottom-third caption goes.

If a beat fails crop safety we either re-frame with a pan keyframe or drop the beat — decided
per row, never silently.

## 5. Rejection criteria (a clip is sent back if…)

1. Timecode in the filename disagrees with the EDL by more than ±1 s.
2. Resolution below 720p on the short side, or the clip was re-encoded twice.
3. The file is longer than 10 min (extractor limit) or contains a jump-cut/ad splice.
4. Audio has been ducked, normalised or replaced.
5. The clip covers a range we did not request (bandwidth + ToS scope creep).

## 6. Machine-readable manifest

`footage_requests_m01_m02.csv` holds the current request rows. Every row is
`UNVERIFIED` with `TBC` timecodes until S1/S2 fill them in — that file is the only thing the
extractor ever reads, so an unverified row physically cannot be pulled.

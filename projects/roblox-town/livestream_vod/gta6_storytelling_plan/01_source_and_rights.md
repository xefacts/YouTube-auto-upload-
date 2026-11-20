# 01 — Source Footage and Usage Rights (Section I)

## 1. What the footage is

| Item | Value | Evidence |
|---|---|---|
| Parts | 22 files named `Grand Theft Auto 6 - Part N - ...(1080P_60FPS)-partNN.mp4` | Drive listing (v3 build) |
| Resolution / FPS | 1920×1080, 60 fps (per filename) | Filename; Drive metadata confirms 1920×1080 |
| Length | part01 = 152.616 s; other parts assumed ~152.6 s; total ≈ 55.9 min | Drive `get_file` on part01 |
| Size | part01 = 53,176,061 bytes (≈53 MB) | Drive `get_file` |
| Drive owner | `ihsanulhaqsaleemi3@gmail.com` (our account), not shared | Drive `get_file` |
| Declared origin | IShowSpeed livestream VOD `qSyo5d-dVzA`, title "PLAYING GTA 6 EARLY ACCESS GAMEPLAY", channel IShowSpeed, dated Nov 18, 2026 | `zero_budget_gta6/README.md` |
| Who uploaded/ripped the part files | **Not documented** | — |

Note: the Drive part names say "Grand Theft Auto 6 - Part 1 - The Beginning". That is a title on a re-upload, not
proof of the original rights holder.

## 2. Rights status (per brief Part 13)

| Check | Result |
|---|---|
| Owner identified | Partly. The stream is by IShowSpeed (per local notes). The owner of the part-file copies is not documented. |
| Written permission to reuse for commentary and public upload | **Missing.** Only a verbal statement is on record: "Speed ke clips ke rights unke paas hain" (2026-11-16). Not written, not verifiable. |
| License or commercial-use terms | **Missing.** |
| Permission covers early-access (embargoed) material | **Unknown.** |
| Attribution and watermark intact | Source has no watermark removal; the stream watermark is not checked. |
| Other people visible (face cam, chat, PII) | Face cam exists per earlier notes. Chat and third-party names not reviewed. |
| Music in source | Unknown; game audio and possible copyrighted music not checked. The brief forbids music. |

**Overall: UNVERIFIED — HOLD.** No clip may be edited or published until decision 1 in the README is resolved.

## 3. Risks to flag before any use

1. **No documented permission.** The brief requires it before editing.
2. **Early-access material.** Publisher embargo or EULA may apply even when the streamer has permission. This is a legal
   question. Get advice before publishing.
3. **Stream capture method.** Local notes say the platform's terms restrict recording streams (`06_LIMITATIONS.md` §4).
   The part files already exist, but how they were produced is unknown. Document the method or drop it.
4. **Concealment.** Earlier v2/v3 blurred the face cam and muted the audio. The brief says do not blur to hide the source or
   owner. Privacy blur is different, but it must be disclosed.
5. **Public links.** v2 (`1h_dE9Kxl5mevKuF_29T6bd5zBCmwbFLA`) and v3 (`1uVfMBKA8ZExk-NOiFbPs64-sRyW72v1z`) are public
   `anyoneWithLink` readers and contain third-party footage. Recommend restricting them until rights are settled. Not changed in this turn.
6. **Date conflict.** Search results dated after 2026-11-16 describe the GTA VI launch (Nov 19, 2026). Today is Nov 16.
   Verify the current status from official sources before stating any launch facts in the video.

## 4. Allowed paths (from the brief)

- (a) Written license or permission from the rights holder, saved in `docs/` or this folder, with date and scope.
- (b) Footage owned by the creator, or licensed stock, or creator-supplied clips with written terms.
- (c) No third-party gameplay: original visuals only (cards, mission timelines, diagrams, maps drawn from verified text).

## 5. Next steps if the rights are cleared

1. Save the written permission here as `RIGHTS_PERMISSION.md` (date, scope, territory, expiry).
2. Re-download any needed part by Drive ID and check duration and resolution.
3. Fill `F_clip_selection_log.csv` per part, one row per candidate clip, frame- and audio-checked.
4. Check each clip for: HUD and subtitles, on-screen mission titles, face cam, chat, music, profanity, and sensitive content.

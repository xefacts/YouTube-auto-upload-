# GTA VI Storytelling Video (25–30 min) — Production Plan

**Status: PLANNING PACKAGE ONLY. No production started.**
The brief says: deliver the plan, then wait for approval before editing. This folder is that package.
Date of analysis: 2026-11-16 (UTC).

## Blocking issues (production cannot start until these are resolved)

1. **Footage rights are not documented.** The only source footage in the workspace is IShowSpeed's stream
   (`youtube.com/live/qSyo5d-dVzA`, title "PLAYING GTA 6 EARLY ACCESS GAMEPLAY"). The only permission on record is a verbal
   statement from the account owner. No written license, permission email, or channel-owner confirmation is in the repo.
   See `01_source_and_rights.md`.
2. **The mission chronology is not verified.** No official Rockstar mission list was found. Mission names and order
   can only come from the footage itself (on-screen HUD titles and original game dialogue). That review has not been done.
   See `02_story_and_chronology.md`.
3. **Two brief conflicts need a decision** (listed below): the ElevenLabs requirement vs. the $0 budget, and the caption rule.

## Section status (A–K from the brief)

| Section | Deliverable | Status |
|---|---|---|
| A | Topic and story analysis | Done (verified facts only) — `02_story_and_chronology.md` |
| B | Full mission chronology | **BLOCKED** — needs footage review. Framework only. |
| C | Complete 25–30 min script | **BLOCKED** — depends on B. Band structure and story questions only, in `03_script_voice_visual_plan.md`. No script text written. |
| D | ElevenLabs V4 multi-speaker voiceover | **BLOCKED** — depends on C. See the budget conflict below. |
| E | Character voice bible | Draft — `03_script_voice_visual_plan.md` §E |
| F | Clip selection spreadsheet | Skeleton, 22 source parts, all content columns `NOT REVIEWED` — `F_clip_selection_log.csv` |
| G | Scene-by-scene editing timeline | **BLOCKED** — depends on F |
| H | Visual and sound design instructions | Draft — `03_script_voice_visual_plan.md` §H |
| I | Copyright and source report | Done — `01_source_and_rights.md` |
| J | Thumbnail concept | Draft — `03_script_voice_visual_plan.md` §J |
| K | Final quality-control report | Checklist only — `04_quality_control.md` |

## Decisions needed from you (reply with a number or your own answer)

1. **Footage authorization.** Choose one:
   - (a) Written permission from IShowSpeed or the rights holder covering commentary reuse and public upload, saved to the repo.
   - (b) Replace the source with footage you own or have a written license for (own recording, licensed stock, or creator-provided clips).
   - (c) Use no third-party gameplay: original explainer visuals only (cards, timelines, diagrams). The brief allows this.
   Without (a), (b), or (c), nothing gets edited.
2. **Early-access footage.** The stream is labeled "early access". Publishers often restrict early footage with embargo or
   EULA terms, even when the streamer has permission. Confirm you are comfortable with the legal position, or choose (b)/(c).
3. **Blur and mute policy.** The earlier v2/v3 videos blurred the face cam and muted the original audio. Brief Part 13 says
   do not blur to hide ownership or the source. If the face cam must be hidden, blur it only for privacy and say so in the
   description. Confirm which you want.
4. **Voice system.** The brief asks for ElevenLabs V4 tags. ElevenLabs is a paid service, and the budget is $0.00.
   The plan uses Arena voices only (the approved voice tool). Confirm this. V4-style emotion tags will be dropped or
   replaced with plain-text delivery direction, unless you approve a paid tier.
5. **Caption rule.** The brief says no word captions by default, only occasional one-word labels ("WAIT", "IMPORTANT").
   Earlier videos used one English word on every line. Confirm the brief's default (occasional labels), which is the plan below.
6. **Length.** The source is about 56 minutes (22 parts, about 152.6 s each). The brief target is 25–30 min, preferably ~28.
   The plan assumes 28 min. Confirm.

## Things to fix in existing work before reuse

- The public Drive links for v2 and v3 (`anyoneWithLink` reader) contain third-party footage. Under the brief, that is
  distribution without documented permission. Consider making them private until decision 1 is resolved. This was not changed in this turn.
- v2/v3 narration was written from low-resolution contact sheets. Mission names and story claims in those scripts were never
  verified against footage. Do not reuse that narration without re-review.
- The source parts were removed locally by an earlier cleanup. Re-download by Drive ID if needed (IDs are in `F_clip_selection_log.csv`).

## Sources used (no paid tools; $0 budget)

- Release date and launch status: Rockstar-linked trade reporting, see `02_story_and_chronology.md` §Sources.
- Source footage metadata: Google Drive connector (`get_file` on part01; 1920×1080, 152.616 s, 53,176,061 bytes).
- Local project notes: `projects/roblox-town/livestream_vod/zero_budget_gta6/README.md` and `06_LIMITATIONS.md`.

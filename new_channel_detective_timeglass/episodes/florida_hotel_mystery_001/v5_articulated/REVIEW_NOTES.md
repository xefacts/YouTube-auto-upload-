# Florida locked suite — V8 restrained edit / text / sound review

**Current private review:** 38.5 s, vertical **720 × 1280**, fictional dramatization. [Owner-only Drive review](https://drive.google.com/file/d/1mMPhUgqU5bmmKR0PELSFdR-7Z2X4MI80/view?usp=drivesdk). This is not a native-4K master, verified real incident, or YouTube release.

## Corrections requested after V7

- **Text:** Inspected the user's Drive `Text` folder screenshots and a sample video for their bold, compact, color-accented type hierarchy. V8 uses its own cream/amber two-level typography and short 1–2-word **story-cue cards**, shown briefly near estimated narration beats. None of the reference footage, faces, logos, audio or text graphics were reused. The supplied narration has **not** been independently transcribed word-for-word, so these are **not verbatim subtitles**. They avoid uncertain year, exact watch time, alleged motive and guilt. For true word-synced captions, obtain an approved transcript or direct listening audit first; edit `CUES` in `render_v8.py`.
- **Grounding/continuity:** Removed V7's awkward balcony crouch, walking key and hand gesture pointed away from the suite handle. The investigator now stands on the balcony tile rather than overlapping the railing; the corridor, wife and partner stand with both shoes on the carpet, and their positions remain fixed throughout each shot. Only a few matching key-pose cuts remain (watch, wife, partner, thread); no limb warp, sprite slide, ambient character wobble or constantly moving camera. Existing composited stills used for the desk examination are retained. The adult cast identities remain consistent with V5/V6/V7.
- **Motion:** Cut most shot zoom/focal travel by roughly 50–66%, eliminated the V7 camera oscillation and rapid match-key dissolves. The dramatic window-to-hotel pullback remains the strongest intentional camera move, after narration finishes.
- **Sound:** A fresh original, non-melodic dark filtered-wind/rain/percussion mix keeps Adam's selected VO forward. A longer wood creak leads into a clearly timed door slam at **6.24 s**; brass latch clicks hit the **15.96 s** state cut; the visual-only ending gets a stronger atmospheric rise/low impact instead of falling silent. No audio, music, voices or door effects were copied from the reference folder. It does not purport to be a recording of a real incident.

Visual QA checked a multi-frame sheet and full-resolution feet/rail/door compositions; FFmpeg decoded all frames and audio of the exported MP4 without error. Timing of short text cues is based on *rough earlier ASR/storyboard ranges* rather than a newly verified spoken transcript. The last line of the supplied edited VO still needs approval. Higher-resolution art would be required for a genuinely detailed 4K finish; an upscale of this review is not native 4K.

V7 and earlier image/script assets remain as reproducible history. The prior generated V7 video was moved to **recoverable Drive Trash after V8 uploaded and owner-only permissions were verified**; the user-provided VO and source reference files are never removed. Local MP4s and `render_cache/` are ignored build outputs.

Rebuild from repository root:

```sh
python -m venv .venv
.venv/bin/pip install numpy pillow scipy opencv-python-headless imageio-ffmpeg
.venv/bin/python new_channel_detective_timeglass/episodes/florida_hotel_mystery_001/v5_articulated/render_v8.py
```

Output: `v5_articulated/FLORIDA_V8_RESTRAINED_TYPE_AND_SOUND_PRIVATE_REVIEW_720x1280.mp4`.

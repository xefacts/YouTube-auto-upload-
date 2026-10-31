# Emu War — stable camera / restrained sound final (v5)

**Latest exports:** `Emu_War_Stable_Final_v5_8K_Portrait.mp4` and `Emu_War_Stable_Final_v5_1080p_Preview.mp4`, both 48.00 seconds at 30 fps. The 4320 × 7680 8K file is **upscaled** from mostly 768 × 1376 AI-generated stills, *not native 8K source detail*. The 1080 × 1920 preview is for compatible playback. MP4s are delivered on Drive; the repository tracks the editable sources.

## Response to the stable-camera correction

- 35 unique, narration-ordered stills (no image reused). **28 shots hold the camera completely steady**; only seven shots move: a gentle road lateral, an emu-field follow, skyward and downward setting/time tilts, two restrained fence-line pans, and the final quiet ease-out. There is **no zoom on every image**. Five five-frame dissolves are used at major transitions only; the rest are purposeful pose/action cuts. The 1932 date appears only in the opening.
- More images were **not** added merely to increase a shot count: the existing 35 distinct stills already cover the voiceover beats. The opening, withdrawal, farmers' damaged crops, returned small team, Meredith's report, continuing birds, news reaction, 1934 supplies, bounty claims, fencing and unresolved ending remain matched to the unchanged English narration.
- `NOVEMBER 1932` is moved farther inside the opening frame's title-safe area. `REPORTED 986` is re-laid out below the report clip, and `EMU WAR` is set wholly inside the printed sheet away from the worker's hands. `CLAIMS 57,000+` is still on an illustrative ledger; `YEAR 1934` exists within the generated supply still. The editorial typography is **baked into graded image stills before video movement**, not independently rendered as extra timed subtitles. Five examples appear in `text_baked_stills/`.
- **Improved original non-melodic sound bed:** gentler filtered wind, only four small synthesized *emu-inspired* distant bird textures, and restrained wheat/report/newsprint/ledger/wire gestures. The bed automatically and smoothly **ducks beneath the actual spoken narration**, and never adds a musical track. These are *not real emu field recordings*; using no music is a production choice for the user's halal-conscious preference, **not a religious ruling or certification**. No imported samples or reference audio are used.

The source ZIP includes all 35 required scene PNGs from earlier version directories, the editor, narration, fonts with their licenses, sound, five final in-image-text examples and a shot contact sheet. All visual documents and people are illustrations, **not archival records**. `57,000+` refers to bounty **claims**, not a verified bird count. Character movement comes from changes between separately generated poses and occasional whole-image camera moves, **not** hand-rigged or individually drawn character frames.

## Re-render

From the repository root:

```bash
python -m venv .venv
.venv/bin/pip install pillow numpy imageio-ffmpeg
.venv/bin/python past_detour_emu_1932/final_image_edit_v5/render_stable.py
```

The reproducible generated `staged/` JPEGs and `natural_cues.wav` are not tracked in Git; the delivered ZIP includes the WAV for independent review. Historical facts/source notes are in `../phase2/README.md`; the audit of supplied Text/Train references is in `../final_image_edit/REFERENCE_AUDIT.md`.

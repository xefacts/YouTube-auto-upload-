# Emu War — final image edit v3 (more scene motion and naturalistic sound)

**Deliverables:** `Emu_War_Final_v3_8K_Portrait.mp4` and `Emu_War_Final_v3_1080p_Preview.mp4`, 48.00 seconds at 24 fps in portrait 4320 × 7680 and 1080 × 1920. **8K is an upscaled export** from AI-generated image stills (mostly 768 × 1376), *not* native 8K source detail. MP4s are delivered on Drive, not in Git. This version supersedes `final_image_edit_v2/`.

## Changes in this final pass

- The `NOVEMBER 1932` opener is shown **only once**. The later return uses a distinct new field angle; the earlier repeating opening still has been removed. Each of the **39 video shots uses a different still** (no repeated scene images).
- Ten additional generated image stills (nos. 31–40) provide a changed team-return angle, damaged wheat gestures, report reaction, two different emu poses, a print-shop reaction, a *different* field after the sky transition, wire-tool detail, fence walk, and a close final bird. The edit pans/tracks/zooms across still images with eased whole-image camera moves; no independently rigged/hand-animated characters. The camera rises through the sky and descends into the later farm setting around 26–27 seconds.
- A subtle consistent grade (warm highlights, cool muted shadows, slightly restrained saturation) is applied to each image **before** editorial text is permanently baked into the selected stills. `text_baked_stills/` includes five finished stills showing the final treatment. The date is only on the opener; `REPORTED 986`, `EMU WAR`, and `CLAIMS 57,000+` are each typeset onto their respective scene images rather than placed as timed video overlays. `YEAR 1934` already exists inside the generated supply still. These are **illustrative documents**, not actual period records, and `57,000+` refers to bounty **claims**, not a precise verified bird count. There are **no extra subtitles**.
- The Phase 2 spoken English narration and historical story are unchanged. The original low non-melodic sound design uses soft air/wheat/newsprint/wire cues and four quiet, irregular **emu-inspired synthesized guttural calls** around bird scenes; they are **not authentic emu field recordings**. There is **no music, melody, song, imported soundtrack or sampled wildlife audio**. This follows a halal-conscious production preference but is **not a religious ruling/certification**.

## Re-render

The source ZIP mirrors the repository's relative paths and includes the previous stills required by this standalone v3 renderer, the ten new stills, narration, fonts with licenses, and a contact sheet. From the repository root:

```bash
python -m venv .venv
.venv/bin/pip install pillow numpy imageio-ffmpeg
.venv/bin/python past_detour_emu_1932/final_image_edit_v3/render_final.py
.venv/bin/python past_detour_emu_1932/final_image_edit_v3/render_final.py --8k
```

`staged/` and `natural_cues.wav` are reproducible by-products. The illustrations are visual reconstructions, not archival footage. The earlier reference audit is in `../final_image_edit/REFERENCE_AUDIT.md`; historical facts, source citation and limitations are in `../phase2/README.md`.

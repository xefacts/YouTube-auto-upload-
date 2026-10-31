# Emu War — refined 8K image edit (v2)

**Main deliverable:** `Emu_War_Refined_Final_8K_Portrait.mp4`: 48 seconds, 24 fps, 4320 × 7680 portrait (upscaled 8K export). A 1080 × 1920 compatibility preview is also delivered separately. The underlying AI image sources are mostly 768 × 1376, so the export has **8K dimensions, not native 8K detail**.

This updates the prior `final_image_edit/` cut in response to feedback; it does not add a new story. The same Phase 2 English narration is used. Ten additional **AI-generated adjacent stills** in `images_new/` supply actual pose and expression changes: a soldier's breath, a walking step, a farmer's hand gesture, a report-pointing hand, emu positions, a newsprint page turn, clerk and ledger gestures, wire-post action, and a quieter final look. Camera movement remains whole-image movement with ease-in/out; the characters are **not rigged or drawn frame by frame**. The 34 shot beats are matched to narration, and one geographic/time transition travels up through a generated sky plate and down into a new field setting.

**No spoken-word subtitle/caption layer.** The few contextual words are baked into selected **image stills before rendering**: `NOVEMBER 1932` in sky/plaster, `REPORTED 986` on an illustrative report, `EMU WAR` on illustrative newsprint, `CLAIMS 57,000+` on an illustrative ledger, plus the generated shop wall's `YEAR 1934`. These are script facts/established nickname, not authentic scanned documents. Type was adjusted for contrast and paper curvature. Nothing from the uploaded Text/Train references was copied into the film; their review is in `../final_image_edit/REFERENCE_AUDIT.md`.

## Sound design

The original Phase 2 narration MP3 is retained, but the earlier Foley-heavy mix is replaced with a **much quieter original effects-only track** (`restrained_effects.wav`). It consists of a low wind bed and only five small dry situational rustles/contacts at report, field, newsprint, ledger and fence moments; there is **no musical or melodic track** and no imported audio samples. The narrator remains dominant. This is a production choice informed by the user's preference, not a religious ruling or certification.

## Re-render

The renderer needs the new stills here, the earlier `final_image_edit/images_new` and fonts, Phase 1 opening field, Phase 2 report/fence scene stills and `phase2/audio/narration.mp3` in this repository. From the repository root:

```bash
python -m venv .venv
.venv/bin/pip install pillow numpy imageio-ffmpeg
.venv/bin/python past_detour_emu_1932/final_image_edit_v2/render_refined.py
.venv/bin/python past_detour_emu_1932/final_image_edit_v2/render_refined.py --8k
```

The original AI scene PNGs and current alternate stills are source assets; `staged/` is reproducible editorial JPEG output. Large MP4 exports are intentionally ignored by the repository and delivered separately. Historical facts and illustrated-scene disclosures remain in `../phase2/README.md`.

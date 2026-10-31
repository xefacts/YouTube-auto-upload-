# Emu War — revised final image edit (8K portrait)

**Deliverables:** `Emu_War_Image_Edit_8K_Portrait.mp4` and a smaller `Emu_War_Image_Edit_1080p_preview.mp4`. Both are 48 seconds, 24 fps, portrait 9:16, H.264/AAC. The 8K file is **4320 × 7680 pixels** (portrait equivalent of 8K UHD). The generated images are approximately 768 × 1376; the 8K file is a carefully rendered **upscale**, not native 8K detail. Some phones/players may not decode 8K H.264, so a 1080 × 1920 preview is supplied too.

This revised cut supersedes the **captioned Phase 3 video**, which the user rejected. It does **not** add or rewrite narration, story, music or sound effects: audio was stream-copied from the original Phase 2 Short. Demuxed AAC SHA-256 for both new exports and the Phase 2 source: `2f8684983c4320f8f1a9f9ea26cd92dd747d7e80ac409679bd2a7669ecb660e6`.

The new batch contains ten scene/sky images and nine alternate pose/expression images. The film uses ten of those scenes and eight pose variants, plus three previously generated Emu War stills; `12_departure_farther.png` is an unused optional alternate. Characters are never rigged or drawn frame by frame. Instead, alternate AI stills show a soldier glancing, farmers changing expression/gesture, emus moving apart, a newspaper changing angle, a hand moving on a ledger, fence-wire work, and a final head turn. Every shot uses its own eased whole-image virtual-camera path, and one transition tilts skyward and descends into a changed year/location.

**No extra captions.** Only contextual type rasterized **inside selected scene images before editing**: `NOVEMBER 1932` on sky/plaster, `986` on the report, `EMU WAR` on a blank broadsheet, the scene's existing `YEAR 1934` on the supply wall, and `57,000+` on the ledger. These are already in the unchanged script or established historical nickname/figures. Typography is not a timed dialogue overlay. The on-image broadsheet/ledger are AI reconstructions, not authentic archival documents; generated realistic-looking Wheatbelt backgrounds are not original historical photographs.

## Reproduce

From the repository root, with the Phase 2 video and earlier episode images present:

```bash
python -m venv .venv
.venv/bin/pip install pillow imageio-ffmpeg
.venv/bin/python past_detour_emu_1932/final_image_edit/render_image_master.py
.venv/bin/python past_detour_emu_1932/final_image_edit/render_image_master.py --8k
```

The source ZIP delivered alongside the videos includes the necessary earlier stills and Phase 2 MP4 to make this edit reproducible. The ten initial and nine alternate image files are in `images_new/`; staged typeset JPEGs are reproducible outputs of the render script. Font files and OFL licenses are in `fonts/`. Historical claims and English script are documented in the separate `phase2/README.md` and [Britannica's Emu War article](https://www.britannica.com/topic/Emu-War). The full 16-reference technique review is in `REFERENCE_AUDIT.md`.

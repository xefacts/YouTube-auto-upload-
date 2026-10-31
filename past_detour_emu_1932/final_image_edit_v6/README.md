# Emu War — faster image-pose edit (v6)

**Current outputs:** `Emu_War_Fast_Images_Final_v6_8K_Portrait.mp4` (4320 × 7680) and `Emu_War_Fast_Images_Final_v6_1080p_Preview.mp4` (1080 × 1920), both 48.00 seconds at 30 fps with the **same original English narration**. The 8K export is an **upscale from mostly 768 × 1376 AI images, not native 8K image detail**. MP4s are delivered separately on Drive.

## Specific corrections

- **Removed the indoor wheat/table sequence entirely.** The old `03_farmers_petition_wall`, `13_farmer_petition_gesture`, and `32_farmer_wheat_close` images are **not used** in this version. Three new outdoor farm-damage pose stills (46–48) show farmers seeing damaged crops, appealing and examining flattened stalks, aligned with the same narration.
- Added **ten separately generated still images**: three farmer/crop poses, three consecutive running-emu poses (49–51), two turning-emu poses (52–53), one changed soldier-team gesture and one wire/fence action. There are **41 non-repeated source stills**. Near-adjacent bird poses use four-frame (~133 ms) image-to-image blends plus eased horizontal camera tracking to convey quick movement while keeping the bird's head within frame. This is **animation-like motion assembled from AI-generated images**, *not* a separately rigged or hand-drawn character animation, live bird footage or a one-click video model.
- Faster scene rhythm remains mapped to the narration beats: withdrawal, outdoor crop damage, returning team, reported 986, continuing emu migration, newsprint, later 1934 assistance/claims, physical fencing and a quiet ending. Most shots move by an eased track/tilt rather than zooming on every image. The sky-up/down geographic and time transition is retained. Seven short blends are used only between related poses or settings; this is a 30 fps image-camera edit, not physical 3D-camera footage.
- The few words are printed into graded **source stills before video movement**, not timed caption overlays: `NOVEMBER 1932` only in the opener, illustrative `REPORTED 986` and `CLAIMS 57,000+`, in-scene `EMU WAR` newsprint and the generated supply wall's `YEAR 1934`. `57,000+` means bounty **claims**, not an exact verified count of birds. The illustrated papers are not actual 1932 records.
- No music or imported samples. The previous original non-melodic wind / wheat / paper / wire sound with four soft **synthesized emu-inspired** calls remains under an unchanged narrator using smooth speech-based ducking; these sounds are **not authentic field recordings**. This honors the user's halal-conscious preference but is **not a religious ruling/certification**.

Images and portrayed people are AI illustrative reconstructions, not archival footage. No supplied reference footage, narration, soundtrack, logos or watermarks were copied. `images_new/` contains the ten new stills; `v6_new_images_contact.jpg`, `v6_timeline_audit.jpg`, and `v6_bird_pose_audit.jpg` make the pose and crop checks reviewable.

## Re-render

From the repository root with Pillow, NumPy and `imageio-ffmpeg` installed:

```bash
python -m venv .venv
.venv/bin/pip install pillow numpy imageio-ffmpeg
.venv/bin/python past_detour_emu_1932/final_image_edit_v6/render_fast_images.py
```

The renderer stages graded JPEGs and generates `natural_cues.wav`. It reads the earlier generated image sources and font licenses in this repository; the delivered source ZIP retains the same relative paths. Historical citations and visual caveats are in `../phase2/README.md`, and supplied visual references are audited in `../final_image_edit/REFERENCE_AUDIT.md`.

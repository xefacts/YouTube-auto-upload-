# Florida locked suite — V7 ten-key cinematic-motion private review

**Current review:** 38.5 seconds, vertical **720 × 1280**. [Open the owner-only V7 review](https://drive.google.com/file/d/18sTJQm4QG-m5tu2PTdYdt_Dm7yDfPmLP/view?usp=drivesdk). The Drive link is not public; other people need the owner's permission. This is a fictional dramatization, **not** a verified account of a real case, a native-4K master, or a YouTube release.

## Ten new movement images, all used in this cut

The ten `assets/v7_*.png` images are distinct keyed action poses of the *same* four established adult characters. None introduces a new identity or a copied real person's image.

1. `v7_businessman_watch_lift.png` — lift of pocket watch in suite.
2. `v7_businessman_watch_lower.png` — surprised backward shift.
3. `v7_investigator_walk_step.png` — corridor walking stride.
4. `v7_investigator_handle_brace.png` — tension beat at suite door.
5. `v7_investigator_balcony_crouch.png` — **upper-body/hand insert only**; the full-length crouch reads as unsupported, so it is intentionally cropped above its legs. Do not show this sprite full-body.
6. `v7_investigator_thread_inspect.png` — thread lifted to eye level.
7. `v7_wife_step_back.png` — defensive step in corridor.
8. `v7_wife_hand_to_mouth.png` — restrained shocked reaction.
9. `v7_partner_case_open.png` — open document case.
10. `v7_partner_glance_away.png` — closes case and glances aside.

`render_v7.py` makes short softened pose changes, anchored shoe-ground positions, an investigator walk-in, subtle handheld/dolly drift over the existing photo plates, a deliberate balcony close insert, brief focal transitions and a dark edge falloff. These changes add editorial momentum while preserving the V6 latch-state cut, door-close and lock SFX, selected Adam narration and visual-only hotel pullback. The 2D ink-and-cel characters have dimensional 2.5D shading, localized body-part image warps and matching alternate poses; this is **not** a rigged 3D simulation or fully hand-drawn in-between animation. The door handle is reached toward, not physically turned in a continuous simulation.

The movie file was fully decoded with FFmpeg, and an extracted multi-frame contact sheet was visually inspected. The exact selected narration words/ending trim still need an independent audit before publication; avoid assigning historical dates, time-of-death or guilt from the dramatization. Higher-resolution source art, rather than an upscale of this 720p review, is needed for a native-4K finish. No YouTube upload or modification of an existing channel occurred.

The older V6 review was moved to **recoverable Drive Trash** after V7 uploaded and owner-only permissions were verified. Its source renderer/assets, along with the user's selected voice, are retained. Video MP4s and `render_cache/` are ignored disposable local outputs; older source project scripts/images are retained for reproduction.

From repository root, rebuild with:

```sh
python -m venv .venv
.venv/bin/pip install numpy pillow scipy opencv-python-headless imageio-ffmpeg
.venv/bin/python new_channel_detective_timeglass/episodes/florida_hotel_mystery_001/v5_articulated/render_v7.py
```

Output: `v5_articulated/FLORIDA_V7_TEN_MOTION_KEYS_PRIVATE_REVIEW_720x1280.mp4`.

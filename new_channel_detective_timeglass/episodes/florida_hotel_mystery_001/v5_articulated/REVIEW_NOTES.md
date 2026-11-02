# Florida locked suite — V6 character and latch private review

**Current review:** 38.5 seconds, vertical **720 × 1280**, fictional dramatization. This is an iterative private review, **not** a native-4K master or a verified account of a real incident. No YouTube upload or change to the existing channel.

Private Drive review (owner-only): https://drive.google.com/file/d/1qhuKrl5PWaCd7W19Vpj-V1bjCz0_ToU-/view?usp=drivesdk . A recipient needs the owner's permission; this is not a public link.

## What changed since V5B

- The recurring illustrated investigator now walks into the photographic hotel corridor and changes to a matching reach pose near the suite-door handle. This suggests an attempted test of the door; the hand does **not** visibly grasp or turn a physically simulated handle. The awkward floating-foot suite-desk overlay remains excluded.
- The balcony latch now has two matching photographic states: clearly retracted, then engaged. The state change is an edited cut rather than a continuous mechanical simulation. Quiet, timed brass/handle clicks were added at the reach and lock-state cut; the previously matched door-close creak/slam is retained.
- The same character masters anchor the four adult roles (businessman, investigator, wife, partner), with matching alternate poses, repeated hair/outfits/faces and proportions. Localized warps move heads, torsos, arms/hands and legs over the original 2D cel-shaded art. Shading and independent hotel-plate camera motion give a 2.5D appearance, **not** rigged 3D models or fully hand-drawn frame-by-frame animation.

The established selected Adam voice edit is used with the procedural rain/creak/door-close/impact soundtrack; no sounds are presented as recordings of a real incident. The visual-only closing pullback is retained. The exact narration words and ending trim have not been independently re-transcribed in this revision; higher-resolution source art and a VO audit are needed before a 4K finish. Upscaling this 720p review would not make it native 4K. Avoid treating any on-screen watch time, date, or person as verified historical evidence.

`render_v5.py` imports the earlier V4 timing/camera/audio helper and uses existing photographic hotel plates; it does **not** depend on old V3/V4 MP4 exports. Prior assistant-generated previews were moved to recoverable Drive Trash after their replacements uploaded; source images, project scripts and the user-selected voice were preserved. `render_cache/` and the local rendered MP4 are ignored disposable outputs.

From the repository root, rebuild with:

```sh
python -m venv .venv
.venv/bin/pip install numpy pillow scipy opencv-python-headless imageio-ffmpeg
.venv/bin/python new_channel_detective_timeglass/episodes/florida_hotel_mystery_001/v5_articulated/render_v5.py
```

Output: `v5_articulated/FLORIDA_V6_CHARACTER_AND_LATCH_PRIVATE_REVIEW_720x1280.mp4`.

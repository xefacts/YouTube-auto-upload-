# Florida locked suite — V4 image-motion review

**Status:** 38.5-second vertical 720 × 1280 private review, not the final 4K master. This **supersedes V3** for character appearance and motion method. It does not affect the user's other channel or YouTube. The mystery remains fictional/unverified and is identified as such at the opening.

## Latest direction implemented

- No manual cutout/limb/face/door animation. The video is edited from original **complete scene images** and alternative image states. Movement is camera crop/pan/zoom, hard editorial pose cuts, a very short blur to hide discontinuities, and sound. It is *not* AI video generation or frame-by-frame character animation; do not present it as such.
- All on-screen adult roles (businessman, wife, partner, investigator) are attractive, mature American characters with distinct identities and 1940s costume choices. They are visibly 2D cel-drawn against realistic, dark Florida-hotel plates. The businessman has two states (upright/slumped), wife has two head/hand poses, investigator has suite and balcony action scenes. Same wardrobe/hair/facial designs are carried across their appearances. No actor or suspect is identified as the killer.
- The door uses open / half-shut / closed **generated scene images** with a creak and slam. The short transition between edited AI images still has perspective differences and should be reviewed; no manually drawn door or geometric puppet has been added. The balcony door is shown by a camera move on a still, not a fake sliding latch.
- Selected `../audio/voice_edit_1934.mp3` is retained. Original procedural door, rain, footsteps, impacts and air are mixed over the earlier restrained draft bed, without stock or reference sounds. The ending's visual-only amber-window-to-whole-hotel pullback remains the strongest camera beat.

The earlier Adam VO was associated with this Florida fictional story, but no fresh word-by-word listening transcript was obtained in this pass. The supplied already-trimmed voice edit has the earlier uncertain waveform ending cut. Thus the overlays avoid precise claims of year, watch time, cause, and guilt. Before final 4K approval, audit the exact voice words and cut and refine the image-state door continuity. 720p review footage upscaled to 4K would not be native 4K detail.

## Files and rebuild

- `assets/`: nine generated scene states used in the edit. Background plates are reused from `../v3_dark2d/assets/` (tracked); reference/source videos are not used in this cut.
- `render_image_motion.py`: reproducible editor and original sound design. Install `numpy pillow imageio-ffmpeg` in `.venv`, then run `.venv/bin/python render_image_motion.py` from the repo root. `render_cache/` and MP4s are ignored; the review MP4 is in the workspace and a private Drive folder.

# Florida locked suite — V5 2.5D character-motion review

**Status:** 38.5-second vertical **720 × 1280 private review**, not a finished/native-4K master. V5 supersedes V3/V4 video drafts. The story is fictional/unverified. No YouTube upload or change to the existing channel.

## Current direction

- Four canonical adult American role designs, each with a matching alternate full-body pose: businessman/watch, investigator/crouch, wife/hand to collar, partner/document case. The repeated outfits, hair, faces and proportions are based on the same character masters. The 2D ink-and-cel art has dimensional 2.5D shading; it is **not a 3D model**.
- Subtle localized 2D image warps animate head, torso, both arms/hands and legs from those original character images; larger actions use alternate matching pose images. This is **not a fully hand-drawn frame-by-frame production**. Photography-style hotel plates remain the setting. No copied reference footage or people.
- The hand examining the watch in the suite comes from the established, directly illustrated V4 scene rather than floating an isolated crouching sprite over the tabletop. The balcony action uses the new character master/pose. Wife and partner show role-specific hand/body changes. The **V5B** door close has a replacement foreground-door image that matches the preceding half-closed perspective more closely, accompanied by creak/slam SFX. Minor keyframe differences remain, so do not describe this as a physical 3D door simulation.
- Existing selected Adam voice edit is used with original procedural rain/creak/door-close/impact soundtrack; no purported real incident sounds. The closing camera pullback is retained.
- Exact VO words and ending cut were not independently re-transcribed in this turn. The on-screen edit avoids asserting watch time, date or guilt. The 4K finish requires higher-resolution artwork/voice audit; simply upscaling this review is not native 4K.

`render_v5.py` imports the prior V4 shot/timing/audio helper and uses V3 realistic plates, but does **not** embed old V3/V4 video files. The old V4 MP4 and previous private-review videos were removed or moved to Drive trash after V5 was created, leaving reference/source images and the selected voice available for future improvement. `render_cache/` is disposable and ignored.

Rebuild: `python -m venv .venv && .venv/bin/pip install numpy pillow scipy opencv-python-headless imageio-ffmpeg && .venv/bin/python render_v5.py` from repo root.

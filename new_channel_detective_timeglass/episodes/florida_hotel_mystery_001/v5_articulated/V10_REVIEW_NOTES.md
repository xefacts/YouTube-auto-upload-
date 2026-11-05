# Florida V10 — owner-only fictional flashback private review

**Private review (owner only):** https://drive.google.com/file/d/1prUiB_gUgylZxia4K698I5ackFf6hhMB/view?usp=drivesdk. 41.000 s, 24 fps, 2160 × 3840 **upscaled** H.264 / stereo AAC; 86,316,296 bytes. The source art is approximately 768 × 1376, **not native 4K detail**. Not published to YouTube. The previous [V9](https://drive.google.com/file/d/1yZxC2zq6tkuUWoopIiQLJ7jQbifyk5oq/view?usp=drivesdk) remains in the private folder for comparison; it has not been trashed.

- At 2.20–4.23 s the businessman recoils from an **unidentified, anonymous** armed silhouette in an original generated, hand-painted-style keyframe. A short procedural muzzle flash and synchronized fictional gunshot occur once at 3.34 s; he exclaims in alarm, followed by a stylized voiced villain-like laugh. There is **no wound, blood, impact shot or named suspect**. 4.23–5.20 s returns to the previous slumped businessman beat. This is an interpretation of a fictional case, not a claim of documented murder footage.
- New speech assets: `assets/businessman_alarm.wav` and `assets/anonymous_villain_laugh.wav`. The latter is a generated spoken “Ha! Ha! Ha!” performance, not a recorded natural laugh or user-supplied real-world sound. They sit under the complete selected Adam VO and do not replace or truncate its last spoken line. The original full source and processed VO are unchanged; their timing and every shot after 5.20 s remain V9 timing.
- The selected **PRISM** detective remains on the first balcony frame and in the other detective scenes. No bottom text or purported word-synced transcript was added. All Train and Train 2 reference videos/screenshots are for style/context only; no frames or audio were reused.
- QA: 984 frames decoded without errors; `ffprobe` reports 41.000 s, H.264 2160 × 3840 at 24 fps and 2-channel AAC. Extracted contact frames inspected at 2.4 s, 3.375 s, 4.4 s, 12.68 s and 36.75 s. SHA-256 of private review file: `7adec83156628592c1f01f384c50bb2e55a42ddd0576355e14a112fbcaa80c64`. Drive file and parent-folder permissions each contain **only the owner**, checked after upload.
- A first 4K transcode using V9's Lanczos+unsharp/veryfast settings was killed by memory limits **after the 1080p frame render completed**. The reproducible V10 script now uses a bounded-memory bicubic, single-threaded, no-lookahead upscaling encode. The second MP4 encoded and fully decoded. This is not a claim of high-resolution drawn animation: the flashback is a painted keyframe with camera motion, short flash, reaction and sound design.

Rebuild with `tooling/creative/video-requirements.txt` installed into `.venv-video`:

```sh
.venv-video/bin/python new_channel_detective_timeglass/episodes/florida_hotel_mystery_001/v5_articulated/render_v10.py
```

No auto-upload or public sharing is part of the build. Toolchain setup and license/runtime caveats are in `tooling/creative/README.md`.

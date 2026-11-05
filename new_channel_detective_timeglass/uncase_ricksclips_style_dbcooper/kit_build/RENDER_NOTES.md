# D.B. Cooper remake — render notes

- The user approved the contact sheet and full render on 2026-11-05.
- Final spec: 65.5 seconds, 1,965 frames, 30 fps, 1080×1920 MP4. The WebGL engine renders at 720×1280 for reliable software-rendering throughput; `finish.sh` upscales with Lanczos to the required vertical 1080p output.
- `voice.wav` is the narration source and is kept unchanged. `mix.py` is a local compatibility implementation because the supplied `cartoon-short-kit.zip` contains no `mix.py`; it synthesizes an original quiet mystery music bed and timed sound effects and mixes them under the existing narration.
- The render runs from this directory: `AWS_EXECUTION_ENV=AWS_Lambda_nodejs22.x RESUME=1 node render.mjs frames 0-1964`.
- `finish.sh` uses the bundled `imageio-ffmpeg` executable, encodes at 30 fps, and runs video/audio QA.
- The final MP4 is for private review. Do not publish it or make it public without separate approval.
- The reported workflow video was not found in the user's “Ricks Clips” Drive folder; no claim is made that it was watched.

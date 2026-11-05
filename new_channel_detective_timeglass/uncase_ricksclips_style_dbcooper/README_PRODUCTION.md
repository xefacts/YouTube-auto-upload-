# UNCASE — D.B. Cooper short (private review)

This project is a **code-built 3D toon animation**, not a generated-still slideshow. Three.js builds the sets, props, lighting, shadows, camera moves and ink-outline passes; original flat cartoon characters are drawn in code and animated in those 3D environments. Playwright captures the WebGL frames, captions are composited in a separate canvas, and FFmpeg encodes the vertical video. The visual grammar follows broad traits in the supplied references—expressive simple characters, saturated storybook sets, dark outlines and narration-led captions—without copying their characters, logos, footage, dialogue or compositions.

## Current build

The production pipeline is in `kit_build/`. It is a 65.5-second story with 15 original shots, 1,965 frames at 30 fps. The real-time WebGL engine renders internally at 720×1280 for practical software-rendering throughput; `finish.sh` upscales to the required 1080×1920 output with Lanczos. Captions are included.

The render requires the prepared 48 kHz, 16-bit mono `voice.wav` as a local input; audio is intentionally not committed. The supplied ZIP did not contain the referenced `mix.py`, so `kit_build/mix.py` is the project's local implementation: it preserves the voice samples and adds a subdued original mystery bed and timed procedural effects.

```bash
cd kit_build
npm ci
python3 -m venv .venv
.venv/bin/pip install numpy imageio-ffmpeg pillow
# Place the approved narration at voice.wav (48 kHz, 16-bit PCM, mono).
.venv/bin/python mix.py voice.wav mix_raw.wav
AWS_EXECUTION_ENV=AWS_Lambda_nodejs22.x node render.mjs frames 0-1964
bash finish.sh
```

Run all commands from `kit_build/`; `render.mjs` resolves `web/` relative to its working directory. Set `RESUME=1` to skip frame files already rendered. The final MP4 and frame sequence are generated locally and ignored by Git; publish/upload the finished video only after separate approval.

## Story and visual direction

- Original sets: 1971 airport, aircraft cabin, passenger exchange, stormy jump, FBI search room, Columbia River recovery site and evidence archive.
- Original characters and camera staging; no definitive likeness is claimed for the unidentified hijacker.
- Narration begins immediately; short outlined captions remain visible in the composition.
- Factual claims are source-conscious. The FBI redirected resources in 2016 but did not identify Cooper or prove his fate; the recovered ransom money does not establish where he landed or whether he survived.
- No user-provided reference footage or public video is copied into the edit. The workflow video itself was not available for review when this project was prepared.

The narration and primary sources are documented in `SCRIPT_AND_SOURCES.md`. Generated media, narration files and personal Drive assets are excluded from this source PR.

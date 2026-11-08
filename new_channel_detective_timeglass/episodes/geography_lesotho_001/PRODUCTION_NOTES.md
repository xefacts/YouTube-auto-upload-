# Lesotho — A Kingdom in the Sky

One original vertical geography short, 45 seconds, 720 × 1280 / 24 fps, H.264 + AAC. No Train 2 video footage, audio, logo, voice or animation is used in the finished cut. The reference files were studied only for format and editorial pacing. The Florida project is unaffected.

## Narration

Look closely at southern Africa. That patch isn't a lake. It's another country.

This is Lesotho. Completely surrounded by South Africa, yet completely independent.

How did it stay separate? Basotho leaders defended their mountain homeland as neighboring powers expanded.

It later came under British rule, and became independent in 1966.

And the map hides its greatest secret. Lesotho is the only independent country entirely above one thousand meters.

Even its lowest point is about fourteen hundred meters above sea level.

One country inside another. A kingdom in the sky.

## Fact checks and assets

- [Encyclopaedia Britannica — Lesotho](https://www.britannica.com/summary/Lesotho): independent state enclaved within South Africa; Basotho history, British protection/territory, independence in 1966.
- [BBC — Nine things about Lesotho](https://www.bbc.com/news/articles/czdnv6gpezjo): entirely surrounded by South Africa, the only independent state entirely above 1,000 m; lowest point approximately 1,400 m.
- Political boundaries: [johan/world.geo.json](https://github.com/johan/world.geo.json), a GeoJSON conversion of Natural Earth public-domain map data. Simplified polygons are intended for storytelling-scale geography, not surveying.
- Scenic image: newly generated *illustrative* highlands image, not a claimed documentary photograph of a particular place; credited as such in the video. Do not present it as actual satellite imagery.
- Narration: locally synthesized original reading using [CMU Flite](https://github.com/festvox/flite), `rms` voice. Flite's COPYING explicitly permits commercial use with attribution conditions. This is a synthetic narrator, not the voice in any reference video. The voice is functional but less natural than a professional actor or neural narration.
- Atmosphere, hits, pings and sweeps: original procedural audio generated in `build_video.py`; no third-party audio samples or music.

## Rebuild

The renderer is `build_video.py`; assets and temporary renders live under ignored `work/geography_lesotho/`. The delivered MP4 is ignored by the repository's global `*.mp4` rule, but is available in this workspace and in the private Drive review copy. The source GeoJSON and generated still are not included in Git; they are maintained as production assets in the workspace. Dependencies: Pillow, NumPy, imageio-ffmpeg and a locally compiled Flite binary for voice regeneration. The script uses the existing per-sentence WAVs on rerun.

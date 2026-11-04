# V3 — flat atlas edit | private review, not published

**The previous V2 is rejected. This is the replacement.** `FLORIDA_KEYS_FLAT_ATLAS_V3_PRIVATE_1080x1920.mp4` is an original 62.90-second vertical geography explainer (1080×1920, 30 fps, 1,887 distinct authored frames, H.264/AAC stereo, ~−16.4 LUFS integrated, true peak limited to −1.5 dBFS target). It contains **no 3D globe**. This is an owner-only review master, not a YouTube upload, and does not touch the separate Florida mystery episode.

## Reference analysis and creative decisions

`analyze_refs.py` processed **all 12,571 decoded frames** of **all nine supplied clips**, outputting nine per-frame CSVs, a `summary.json`, and 2-second private contact sheets. See `REFERENCE_FORENSICS_V3.md` for methods, limits, clip-by-clip readout, and differences between observed cameras, hard-cut estimates and overlays. Five relevant geography references use detailed *flat* relief maps and camera recrops, not a globe; the four editing-screen clips were assessed as editing references, not footage or overlays to copy. Reference video/audio/pixels do not appear here.

## 17 narration beats, 11 shot regimes

- 00–06.65: **Mercator** relief world/Atlantic atlas, continuous ease into Florida. Florida pin is transformed in flat map space, not fixed on screen.
- 06.65–10.50: independently illustrated regional map; coastline-focused flat camera recrop, land highlight and separate cloud pass.
- 10.50–13.97: illustrated coral/limestone cross-section insert, subtle local push.
- 13.97–17.75: lower-islands map with a warm selection and continued pan.
- 17.75–26.05: reef cross-section with **high/low sea-level line motion**; title and line reverse on the spoken geology beats.
- 26.05–37.17: closer island map; independent key beacons and shallow-shelf cue, camera push along the chain; glowing line **draws on in 3.1 s** in sync with the highway sentence.
- 37.17–40.87: original illustrated bridge aerial, vertical tracking reveal.
- 40.87–52.30: map returns; Key West focus, then Florida Bay and Straits callouts, distinct camera scales and ocean contours.
- 52.30–55.65: regional pullback; 55.65–59.16 geological insert; 59.16–62.90 regional closing pullback.

Captions are split from each recorded narration line into ~four-word phrases and timed proportionately to its actual recorded WAV start/end; non-speech gaps are caption-free. Continuous interpolated camera transforms and short match dissolves link map scales, with hard editorial insert cuts when a geological diagram changes the medium. There is no repeated static 3D-sphere shot.

## Narrative checks / limitations

NOAA describes the upper Keys' exposed fossil reefs; farther west limestone, carbonate sand/mud and shifting sea level matter as well. The Overseas Highway connects **many, not all** islands; the chain continues beyond Key West toward Dry Tortugas. The cyan route is an **illustrative editorial trace**, not an exact surveyed Overseas Highway/polyline. The world-scale Mercator atlas is georeferenced, but the custom local relief plates, reef cross-section, bridge aerial, island positions, labels and local line are **illustrations, not survey imagery or a source of factual coordinates**. Cloud drift is atmospheric texture, not present-day weather. Claims should be fact-checked and local plates replaced with validated GIS before publishing as a geographically exact map.

## Rights and provenance

- **World flat relief:** public-domain Natural Earth relief tiles distributed by [`msupino/NavigationApp`](https://github.com/msupino/NavigationApp/tree/main/docs/relief) (`docs/relief/index.json`, `z0-4.pack`; zoom 4 tiles). `build_flat_atlas.py` composites them into 4,096² Mercator. Land color is blended with NASA Blue Marble day texture, originally NASA/Reto Stöckli and Robert Simmon, mirrored in [`Depal-Jakub/orbital-bloom`](https://github.com/Depal-Jakub/orbital-bloom/blob/main/ASSET_INVENTORY.md). Day SHA-256 `d4dc80a6ef571939d0abe04a9bed3d3d1e6cd63e59514be1c5e43a6b069e6f1e`. NASA content is credited, not NASA endorsement.
- **Wide and closer Keys, cross-section, and bridge:** newly generated original illustrative plates in `assets/` (not excerpts from the competitor videos). Optional wide land selection is an independent alpha layer. The local map and inserted reef/bridge are conceptual illustrations, not GIS-verified sources.
- **Voice:** original script in `generate_v3_narration.py`, synthesized locally with Kokoro-82M q8 ONNX weights from `kokoro-q8-shards@1.0.0` (reassembled and SHA-256 verified as `fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478`) and the `am_michael` Apache-2.0 voice tensor from `kokoro-local-runtime@0.1.0`; ONNX style input compatibility is handled in source. Model is delivered separately in owner-only Drive. Runtime's MIT, Apache-2.0 and third-party notices are preserved in `assets/v3_licenses/`. No reference-voice sampling, transcript copying or voice cloning.
- **Sound:** the recorded CC0 surf track at `assets/v2_ambient/ambience_waves_cc0.ogg` originates from SamsterBirdies, “Calm ocean waves”, [Freesound 578524](https://freesound.org/s/578524/), also acknowledged in [`Karelisio/Somna`](https://github.com/Karelisio/Somna). It is tucked beneath narration; no copied reference audio.
- Typeface DM Sans and Anton are in the sibling `assets/fonts` folder and included in the editor archive; follow their OFL notices from the upstream font distributions. References remain in the user's private Drive and are not shipped in the source kit.

## Rebuild / editing material

From the extracted source root: `python -m venv .venv && .venv/bin/pip install -r new_channel_detective_timeglass/train2_geography_study/requirements-v3.txt`. Rename the separately delivered `KOKORO_Q8_ONNX_APACHE2_V3_VERIFIED.onnx` to `work/tts_models/kokoro-q8.onnx` (the source kit already includes `voices-v1.0.bin` at that relative path), or run `setup_v3_voice.py` to reconstruct the verified model and three voices from npm. `python new_channel_detective_timeglass/train2_geography_study/generate_v3_narration.py` generates the original narration WAV and word-phrase timing JSON, then `python new_channel_detective_timeglass/train2_geography_study/render_geography_v3.py` renders the master. The source archive already includes both staged WAVs and timing JSON to make editorial changes *without* re-synthesizing voice. `v3_maps.py` contains only flat map assets; no dependency on the rejected globe renderer. Original licensed atlas/plates, editable alpha layers, narration, mix, analysis CSVs and Python motion/graphics are included. Source kit is separate from the MP4 and model to stay below transfer limits.

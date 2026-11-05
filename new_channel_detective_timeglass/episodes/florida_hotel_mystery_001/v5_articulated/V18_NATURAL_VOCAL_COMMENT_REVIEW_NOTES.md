# Florida mystery V18 — owner-only review

**Correction to V17.** The previous procedural rumble and “EXPLAIN THE THREAD” close were rejected. V18 instead keeps the original selected narration and story while using recorded environmental effects, one pre-existing non-musical character exclamation, and a direct animated **COMMENT BELOW** card in the final **1.95 seconds**. No YouTube upload or live channel change.

## Cut / ending

- `FLORIDA_V18_NATURAL_VOCAL_COMMENT_PRIVATE_REVIEW_1080x1920.mp4` — 39.25 s, 942 decodable frames, 1080×1920 at 24 fps, H.264/AAC, 20,386,319 bytes. SHA-256 `8da748a127b1b481eae1a74b89ab7e6279fbca2d9d577cde2621dfc7f7577878`.
- `FLORIDA_V18_COMMENT_ENDCARD_1080x1920.png` — full-resolution original text-designed image, SHA-256 `0fc8ffad1193000dbf2dedb34d01139420d2981eaaa6e275d5571a95ee88387c`. It uses the established illustrated room backplate with the **original fiber and thread clue photographs**; no invented evidence. “WHO LEFT THE THREAD?” anchors two large sequential reveals: **COMMENT**, then **BELOW**. End still and final decoded frames were inspected at phone scale. Center typography stays clear of the bottom/right Shorts controls. This is not native 3D; characters and earlier V17 dark death shot stay unchanged.

## Natural/vocal sound design

The primary V18 mix does **not** reuse V17’s procedurally generated noise bed. It loops and crossfades actual field-recorded rain and wind at low level, adds occasional real thunder and stone footfalls for the hotel weather/footsteps, uses a field-recorded gunshot transient and a wood impact for the death beat, and keeps the project’s existing brief voiced businessman alarm. The final image gets a single tactile wood/card settle, not a drum sting. No instruments, melody, sung vocal, regular beat, or extra narration was added. A separate `V18_NATURAL_VOCAL_SOUND_DESIGN_STEM.wav` contains these ambience/effect/vocal-alarm layers **without the narrator** at in-mix gain, for inspection or remixing.

The chosen selected `voice_full_1934_edit.mp3` is decoded to 48 kHz at its original start/time/speed/gain, without word edits or re-recording. Lossy AAC encoding is unavoidable in the review MP4. Source duration is 36.4955 s; the effects continue quietly under the animated ending and fade at the tail. Integrated loudness is ~−22.8 LUFS, peak ~−6.8 dBFS; narrator gain deliberately remains untouched. Decoded high-pass correlations to the selected voice at 0.5, 12.5, 26.5, 34.7, 35.95 s were 0.982, 0.977, 0.971, 0.989, 0.927 (the recorded sounds explain the lower correlations than narration-only V16). All 942 video frames decoded without errors.

### Recording provenance / licensing caveat

The recorded effects are sourced from two GitHub-rehosted audio libraries with documented **CC0** provenance, not from unlicensed sample rips. This is a source-library license note, **not** a religious-permissibility certification. Copyright/attribution should be reconfirmed at publication if required by the publisher.

- Rain light: rubberduck, “40 CC0 water / splash / slime SFX”; rain heavy: Ylmir, “Rain (loopable)”; wind: SketchMan3, “Wind whoosh loop”; thunder: rubberduck, “100 CC0 SFX #2”; stone step: sfxmint, “Concrete Single Footstep 12.” Rehost path and credit file: https://github.com/nahuelcio/ymmo/tree/main/client/public/audio and https://github.com/nahuelcio/ymmo/blob/main/client/public/audio/CREDITS.txt . Repo credits list each as CC0.
- Shot: Félix Blume, “Rifle gunshot, one shot” (a field recording, used editorially for the illustrated gunshot, not a factual claim about its pictured weapon); wood impact: Kenney `impactPlank_medium_000`. Rehost: https://github.com/defaultuser233/tides-of-rlyeh/tree/main/assets/sounds ; provenance https://github.com/defaultuser233/tides-of-rlyeh/blob/main/assets/SOUND_SOURCES.md and https://github.com/defaultuser233/tides-of-rlyeh/blob/main/assets/MANIFEST.md . **Do not substitute** `shot_smg.ogg` from that repo; its present version is CC BY 3.0 and was deliberately excluded.
- `assets/businessman_alarm.wav` was already a tracked character-voice performance in this project. No generated villain laugh was used.

**Religious caveat:** No software can promise 100% halal status for a soundtrack or video. Views differ about sound effects and portrayal; the user should get a ruling from a qualified scholar they trust if certainty is needed. A prior narration-only V17 alternate remains available if preferred. This version is meant to follow the user’s natural-recordings/non-musical-voice production preference, not to make a universal ruling.

Run `render_v18.py` from this directory with the project's video dependencies to recreate the MP4, endcard PNG and local unversioned WAV stem. Large MP4/WAV intermediates stay outside Git.

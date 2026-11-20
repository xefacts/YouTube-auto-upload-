# GTA 6 story video — final build (zero budget)

- `story_hi.json` — 28 beats x 30 s, [start_second_in_source, Hindi narration].
- `captions_en.json` — English caption text per beat (shown one word at a time).
- `build_final.py` — offline Hindi TTS (espeak-ng), 1-word English captions (Noto Sans Bold), 30 s per beat, concat.
- `tts_espeak.py` — standalone TTS test helper.

Source footage (22 split parts from Drive "Gta 6" folder) is NOT committed (1.6 GB).
Final encode used 2-pass libx264 680k video / 96k AAC to fit the 100 MB upload limit: 1920x1080, 14:00, 82 MB.

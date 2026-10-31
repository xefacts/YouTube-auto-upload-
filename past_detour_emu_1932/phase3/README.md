# Emu War — Phase 3 final caption pass

**Final video:** `Emu_War_1932_Final_Phase3_Short.mp4` — 48 seconds, portrait 720 × 1280, H.264/AAC. This is a caption-and-motion finishing pass on the existing **Phase 2 video**, not a new episode. The narration, Foley, scene order, historical claims and imagery are unchanged. No new speech, effects, music, scene image, character or story text was added.

## What changed

- 18 exact-script, phrase-synced English caption cues burned into the Phase 2 picture; also supplied as editable `captions_final.ass` and `captions_final.srt`.
- Readable modern high-contrast caption boxes, a restrained mint highlight on one **existing spoken word** per cue, a 160 ms text pop, and a small 180 ms underline draw. These are the only added hand-built animations; no character or background was animated independently.
- Cue starts were set against the isolated narration waveform using 10 ms RMS speech/pause boundaries, not the 12 scene-edit boundaries. The render script asserts the complete caption wording is verbatim the Phase 2 voiceover. The line wrapping is title-safe on the 720 px-wide frame.

The original AAC audio stream is **stream-copied, not remixed**. Validation: the demuxed audio from both the Phase 2 input and final Phase 3 file has SHA-256 `2f8684983c4320f8f1a9f9ea26cd92dd747d7e80ac409679bd2a7669ecb660e6`. Both videos have 48-second duration and 720 × 1280, 24 fps H.264 picture. The original Phase 2 editorial headings remain visible behind the new spoken-word captions.

## Re-render

Put the original Phase 2 MP4 at `../phase2/Emu_War_1932_Phase2_Short.mp4` relative to this folder, then from the repository root:

```bash
python -m venv .venv
.venv/bin/pip install pillow imageio-ffmpeg
.venv/bin/python past_detour_emu_1932/phase3/render_phase3.py
```

The source ZIP delivered with the final video includes the Phase 2 input MP4, this script, and both caption tracks. Other source images/audio remain in the separate Phase 2 delivery. Historical source and AI-visual-reconstruction disclosure are in `../phase2/README.md`.

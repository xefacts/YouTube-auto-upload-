# Villisca Short — Batch 1 review (2026-11-01)

**Scope:** the first three original illustrated keyframes and a **14.0-second 1080×1920 camera/type/audio animatic**, not the final Short. User requested images in three batches; batch 2 and 3 have not been made. No YouTube upload or live-channel edit.

## Chosen user voice-over

The user selected the earlier file in Drive's **Voice over** folder: `ElevenLabs_2026-11-01T19_34_15_Adam - American, Dark and Tough_eleven_v4.mp3` (Drive file ID `1DJYvo9n9FW-u4r9LP40SqJTiusARcplO`), ~39.24s. The second ~39s file in that folder was NOT used. The user clarified that the **final spoken line** should be removed, leaving a visual-only clue ending. Waveform/silence inspection puts the last phrase after a short pause at ~36.13s of the source; `voice_edit_batch1.mp3` cuts at 35.96s, speeds by 1.075×, filters sub-bass/very high frequencies, compresses lightly, normalizes and adds a very short tail fade. Result ~33.50s. **This cut is based on amplitude boundaries, not a verified speech transcription or listening audition**; the user should approve the last-word cut when hearing it. The edited voice is for assembly; the 14s preview contains only its opening excerpt.

## Original Batch 1 images

1. `01_church_departure.png` — evening church exterior with exactly two adult and six child 2D anonymous reconstruction figures over a photorealistic 1912-Iowa-like setting; calm opening.
2. `02_house_arrival.png` — the same illustrated group at a fictional period house at dusk, realistic background, controlled staging and negative space for type.
3. `03_silent_morning.png` — the **same house architecture** next morning, no family in frame, one 2D period neighbor figure knocking; unease is conveyed without violence.

These depict **illustrative reconstructions** of the case, not historically authenticated likenesses or the real church/house. The characters are part of generated stills, not individually hand-rigged animation. Generated camera motion and editorial type make the 14s animatic, but no frame-by-frame character acting has been claimed. The next batches must introduce new character poses, evidence and trial scenes, not stretch these same three stills over the entire Short.

## Reference study and style choices

The user's two unique `Text` portfolio videos were reviewed via extracted frames: a 56s vertical before/after portrait edit and a 48s landscape typography/portfolio reel. They inform **selective word emphasis, condensed display typography, dark green/ivory/lime hierarchy, fast editorial resets and subject/background depth**, not a reproduction of their people, footage, logos, audio, watermarks or rounded portfolio-frame wrappers. This animatic uses original generated images and typeset type layers. The preview uses three different push/truck camera paths and restrained text beats (`TWO SISTERS`, `THE WALK HOME`, `NO ANSWER`), not extra full-sentence subtitles.

## Audio and historical boundaries

`original_percussion_breath_bed.mp3` is a **fully synthetic, original 38-second non-melodic** bed built from noise-shaped hand-drum-like pulses, airy breath-like swells and cinematic impacts. No instruments, sampled song, authentic field sound, imitation of victim voices or third-party music was used. A sharp dramatic impact is **not** presented as a historical gunshot; the actual Villisca murders involved an ax. No gun image/audio is included. The audio is voice-led, with percussion/air under the narrator; monitor the final mix on a phone before approval. The user allowed wordless vocal/percussion-style sound; an actual shouted “aah” is not fabricated as a victim cry.

## End-plan / later batches

Batch 2: neighbor's unanswered door -> eight-victim non-graphic evidence tableau -> family ax + unsuccessful bloodhounds / disturbed evidence, with new 2D poses and original photographic backgrounds. Batch 3: 1917 recanted confession -> hung jury and acquittal -> ~4–5s **visual-only** unsolved clues after the edited VO, using complete factual words on-screen rather than inventing a culprit. Actual timings will be revised after the end cut is approved. Story evidence is in `../PRODUCTION_CARD.md`.

### Build inputs

- `render_batch1.py` regenerates motion/type and the compact MP4 from the three PNGs, type layers, edited VO and percussion bed; uses Pillow + imageio-ffmpeg. It removes its own temporary scene clips after rendering.
- `../audio/build_soundbed.py` regenerates the non-melodic bed. The edited voice is derived from the user's Drive file, not synthetic or stored with the unmodified original in Git.
- Preview file: `BATCH1_REVIEW_1080x1920.mp4`. It is a **private review animatic**, not a publish-ready episode.

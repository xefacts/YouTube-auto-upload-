# The Emu War (1932) — Phase 1 Short

**Finished video:** `Emu_War_1932_Phase1_Short.mp4` — 52 seconds, portrait 720 × 1280, 24 fps, H.264/AAC, English narration and original effects-only sound design. No music.

The film is edited from **seven original AI-generated scene images**, with cuts and subtle whole-image camera movement. The farmer, soldiers and emus are 2D simplified characters against realistic-looking Western Australian Wheatbelt settings. No character was rigged, independently drawn, or animated frame by frame. The three additional AI-generated images in `images/00_*` were style/character references used to build the scene images. The user-provided Rome character sheet informed the broad simplified illustration language only; it is not included, copied, or shown in the Short. The new cast wears period-specific 1932 clothing, not Roman costumes.

## Narration script

> In 1932, Australia sent soldiers after birds. The birds did not follow the plan. Around twenty thousand emus had moved into Western Australia's wheat-growing districts. Farmers, already struggling, asked for help. A tiny army team arrived with two Lewis guns. At first, the emus stood together in a field. The soldiers aimed. Then the birds scattered into smaller groups. At a waterhole, one gun jammed and the flock ran again. They even tried firing from a truck, but the rough ground made it hard to aim. By December, the operation had killed hundreds of emus, but not enough to solve the farmers' problem. Newspapers called it the Emu War. It was never a formal war. So who really won: the soldiers, the emus, or the headline?

Voiceover in `audio/narration.mp3` uses the previously selected English historical-narrator voice for a similar feel, **not an imitation or clone of the reference MP4**. `audio/original_foley.wav` is programmatically synthesized wind, wheat-rustle, a dry mechanism click and road bumps; it contains no melody or imported audio samples.

## Source / historical caveats

- Encyclopaedia Britannica, [“Emu War”](https://www.britannica.com/topic/Emu-War), consulted 31 October 2026. The event was a short-lived wildlife-control operation in Western Australia in November–December 1932, not a formally declared war. Major G. P. W. Meredith and two other soldiers were sent with two Lewis guns. Emus scattered; one gun jammed near a water source; a truck tactic proved ineffective on rough terrain. Meredith reported 986 emus killed, but this did not solve the larger crop-damage issue.
- “Around twenty thousand” describes the approximate size of the emu migration cited in the source; it is **not** the number engaged or killed. “Hundreds killed” is intentional: the film does **not** claim zero casualties or that the whole Australian army was involved.
- All photographic-looking environments, cast, weapons, vehicles and events in the video are **AI visual reconstructions**, not archival evidence. Clothing, terrain, bird placement and prop shapes are interpretive rather than verified depictions of any specific encounter. The character Edith is fictional and is not identified as an actual participant. No violence is shown.

## Re-render

From the repository root:

```bash
python -m venv .venv
.venv/bin/pip install pillow numpy imageio-ffmpeg
.venv/bin/python past_detour_emu_1932/render_phase1.py
```

The render script generates the non-melodic Foley deterministically, creates twelve branded image-edit beats from the scene stills, applies only crop/zoom camera moves, then muxes the narration and audio into the MP4. It requires the scene PNGs and narration MP3 in this folder. A local ffmpeg binary is supplied by `imageio-ffmpeg`. The on-screen text consists of editorial summary cards, **not word-synchronized closed captions**.

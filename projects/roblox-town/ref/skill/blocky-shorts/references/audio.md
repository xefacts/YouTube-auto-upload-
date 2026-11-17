# Voice-over, sound effects and music

## Contents
1. Voice-over paths (pick one)
2. ElevenLabs in the web app (most common)
3. ElevenLabs via API (fully automatic)
4. Getting exact timing
5. Other voice sources
6. Sound effects
7. Music
8. Mix levels

---

## 1. Voice-over paths
| path | when | steps |
|---|---|---|
| **A. User makes the VO in ElevenLabs (web app)** | default: no API key needed | `bs.py script` → user pastes `build/vo_script.txt` into ElevenLabs → downloads MP3 → uploads it → save as `<project>/audio/vo.mp3` → `bs.py align` |
| **B. ElevenLabs API** | the user gives an API key and `api.elevenlabs.io` is reachable | `elevenlabs.py tts <project> --voice ID` → `bs.py align <project> --alignment build/el_alignment.json` (exact timing) |
| **C. No voice yet** | first drafts, silent animatic, captions-only videos | `bs.py estimate <project>` (estimated pacing). Re-time later when the VO arrives |

The VO must say the story's lines exactly, in order. If the user's VO differs (a changed word, an added "uh"), edit the lines in `story.json` to match before aligning.

## 2. ElevenLabs web app — instructions to give the user
1. Open ElevenLabs → **Text to Speech**.
2. **Voice:** a warm, slightly deadpan storyteller works best (male or female, mid-pitch, conversational, not "announcer"). Search the Voice Library for narration or storytelling voices. Try 2–3 voices on the first line before committing.
3. **Model:** *Eleven v3* or newer for the most expressive delivery. These models use **audio tags** in square brackets, like `[pause]`, `[whispers]`, `[excited]`, `[sighs]`, `[drawn out]`, `[rushed]`, plus ellipses and line breaks for pacing. **They don't support `<break>` tags.** *Multilingual v2 / Flash* support `<break time="0.3s" />` instead. `bs.py script` writes both versions:
   - `build/vo_script.txt`: one paragraph per shot (line breaks = natural pauses). For v3/v4.
   - `build/vo_script_v2_breaks.txt`: with `<break>` tags between shots. For v2/Flash.
4. **Settings:** speed about 1.05–1.15 (these shorts are brisk). Stability is the main dial: lower is more expressive, higher is more consistent. If a line comes out wrong, regenerate just that line.
5. **Optional audio tags** (v3+): `[pause]` before reveals, `[whispers]` for "He forgot one thing.", `[sighs]` before the final dry line. Don't overuse them: one or two per script. **Tags must not appear in story.json lines**; they're only for the TTS input.
6. Download **MP3**, upload it to the chat, and save it as `<project>/audio/vo.mp3`.
7. Tip: leave a clear short pause between shots (the line breaks do this). The aligner uses pauses as anchors.

## 3. ElevenLabs API (automatic path)
```bash
export ELEVENLABS_API_KEY=...            # the user provides it; never print it or write it into files
python3 scripts/elevenlabs.py voices     # pick a voice_id
python3 scripts/elevenlabs.py tts <project> --voice <voice_id> --model eleven_multilingual_v2 --speed 1.08
python3 scripts/bs.py align <project> --alignment build/el_alignment.json
```
This calls `POST /v1/text-to-speech/{voice_id}/with-timestamps`, which returns the audio plus character-level timing, so the captions sync exactly. In Claude's cloud sandbox outbound domains can be blocked. If the call can't reach the host, say so and fall back to path A. (On claude.ai, allowed domains are a setting under Settings → Capabilities on paid individual plans, or the org admin's settings on Team/Enterprise.)

Other API helpers:
- `elevenlabs.py align <project>`: **forced alignment** (`POST /v1/forced-alignment`) of a VO made in the web app → exact timing for path A too.
- `elevenlabs.py sfx <project> --name whoosh --prompt "fast airy cartoon whoosh" --seconds 0.6`: generates a custom sound effect (`POST /v1/sound-generation`, 0.5–30 s) and saves it to `<project>/sfx/whoosh.mp3`, which overrides the built-in sound.

## 4. Getting timing
`bs.py align <project>` picks the best source available:
1. `--alignment file.json`: ElevenLabs timestamps or forced-alignment JSON. **Exact.**
2. `--srt file.srt`: any subtitle file (from ElevenLabs Speech-to-Text, CapCut auto-captions, etc.). Good.
3. Nothing: **energy-based alignment.** It detects pauses in the voice and matches them to punctuation and line ends. On a clean narration it's typically within ~0.1 s on most lines, but it can slip on unusual pacing. Always look at the printed table and the preview sheet, and nudge lines if needed. It works on a *clean voice track* only (no music under it).

The output is `build/timing.json`. You can hand-edit `start`/`end` values if one line is off, then re-run `render.mjs check`.

## 5. Other voice sources
- **The user's own voice:** record on a phone in a quiet room, one take, slight pauses between shots. Same alignment path.
- **Any TTS** (other services, OS voices): export MP3/WAV → path A.
- **Multiple characters:** narration is the style's default. For dialogue, generate each character's lines with a different voice, join the clips in story order into one `vo.mp3` (any audio editor, or ask Claude to concatenate them with ffmpeg), and use `say` FX bubbles plus `talk` actions.

## 6. Sound effects
Sound is automatic: every punch, flip, sign, stamp, clap, slam, whip and crash places its own sound (see `library.md` §8 for the names). The built-in pack (`assets/sfx/`) is synthesized and original, so it's free of licensing issues. To upgrade:
- Drop better files into `<project>/sfx/` with the same names (`whoosh.wav`, `clap.mp3`, `clap_2.mp3` for variants…).
- Sources: ElevenLabs Sound Effects (text-to-SFX), or any royalty-free library the user is licensed for. Remind the user to check each library's license for commercial use.
- Prompt ideas for ElevenLabs SFX: "fast cartoon whoosh, airy, short", "deep cinematic boom then sparkle tail", "single crisp hand clap, dry", "rubber stamp thud on paper", "cartoon pop, bubbly", "magical bright ding", "wooden gavel hit, courtroom".

## 7. Music
Optional, but it adds a lot: a light, quirky, low-energy bed (pizzicato, soft synths, lo-fi). Save it as `<project>/audio/music.mp3`. The mixer loops it, ducks it under the voice automatically, and fades it out at the end. Sources the user is licensed for: YouTube Audio Library, platform-native sounds (TikTok/Shorts let you add music at upload; then leave it out here), ElevenLabs Music, or paid libraries. Don't use copyrighted songs.

## 8. Mix levels (defaults)
`bs.py mix <project> [--vo-db 0] [--sfx-db 0] [--music-db -20]`. When a voice is present, SFX are automatically sat under it. The master is normalized to −14 LUFS (the usual target for Shorts/TikTok/Reels) with a −1 dBTP ceiling.
Common fixes: SFX too loud → `--sfx-db -4`; music too loud → `--music-db -24`; one sound too loud → set `"gain": 0.5` on that FX in story.json, run `render.mjs check` (to refresh events.json), then `mix` again.

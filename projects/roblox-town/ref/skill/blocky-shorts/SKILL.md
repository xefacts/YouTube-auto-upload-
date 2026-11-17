---
name: blocky-shorts
description: Makes vertical 9:16 3D comedy shorts with blocky toy-like characters — the "In this town, when you yawn… day turns to night" storytime style seen on YouTube Shorts, TikTok and Reels. Takes the user from a one-line idea to a finished MP4. Claude writes the script, plans every shot, exports a voice-over script for ElevenLabs, syncs the user's voice-over, adds sound effects and music, and renders everything with code (Three.js in headless Chrome + ffmpeg). Use this skill whenever someone wants an animated short or storytime video from an idea, a Roblox-style or blocky-character animation, a "make a video like this" request for this kind of reel, or wants to fix or improve a blocky short made earlier, even if they don't name the skill.
---

# Blocky Shorts

Turns an idea into a finished vertical comedy short: an absurd rule, a character exploiting it, chaos, and a deadpan button line. Blocky characters, fast cuts on every phrase, constant camera motion, bold word-by-word captions, pop-in graphics and punchy sound effects.

Everything is code: a data-driven 3D engine (`engine/`) renders a `story.json` storyboard frame by frame, and Python scripts handle timing, sound and the final encode. The same `story.json` always produces the same video, so every piece of feedback becomes a precise edit followed by a re-render.

```
idea ─► script (lines) ─► story.json ─► voice-over ─► timing.json ─► preview sheets ─► frames ─► mix ─► final.mp4
         you + user        you            user/API      bs.py align    render.mjs      render.mjs  bs.py   bs.py encode
```

## Ground rules
- **Show the script before you build.** Rewriting text is cheap; re-rendering is slow. Get approval on the script and shot plan, then on a preview sheet, then render.
- **Look at your own output.** After every preview, open `build/preview/sheet.jpg` with the Read tool and check it against `references/qa-and-iteration.md`. Don't report success on a video you haven't looked at.
- **The first result is a draft.** Tell the user what to look at and invite specific feedback ("shot 4 is too dark", "make the ending punchier"). Iteration is the normal workflow.
- **Original content.** When the user shares a reference video, copy its format, never its script, characters or jokes. No real brands, logos or people.

## Paths
`SKILL` = this skill's folder. Work on a writable copy of the project, never inside the skill folder: `PROJ=~/blocky/<slug>` (or the session's working directory). All commands run from `SKILL`:
- `node scripts/render.mjs <check|preview|frames|eval> <PROJ> …`: the 3D side (needs Chrome)
- `python3 scripts/bs.py <init|script|estimate|align|mix|encode> <PROJ> …`: timing, audio, encoding
- `python3 scripts/elevenlabs.py …`: optional ElevenLabs API helper

If the skill folder is read-only, copy the whole skill to a writable place first (`cp -r SKILL ~/blocky-shorts`) and work from the copy.

## Workflow

### 0. Setup (once per session)
```bash
bash scripts/setup.sh          # checks node, ffmpeg, numpy, Chrome; installs what it can
python3 scripts/bs.py init $PROJ
```

### 1. Idea → script
Read `references/story-formula.md`. Pick a strong rule (physical, triggered by an everyday action, exploitable, contagious). Write the narration as caption chunks of 1–3 words with `*highlights*`, grouped into shots, with a one-line visual note per shot. Show it to the user with the estimated length and ask for approval or edits. If the user just says "go", choose the best version yourself and say so.

### 2. Script → story.json
Read `references/storyboard.md` (format) and `references/library.md` (every set, character option, action, prop, camera move and FX that exists). Then write `$PROJ/story.json`. Copy patterns from `examples/clap-town/story.json`. Style DNA to follow (measured from the reference format):
- **Cut every 0.5–1.5 s**, on the words: 1–3 lines per shot.
- **Every shot moves.** Default to a slow `push` (dolly-in about 20% across the shot), and mix in `crane-up`, `track`, `orbit`, a `whip` between subjects, and a `crash` zoom at the end.
- **Punch-in** (`punch` FX) and/or `shake` on every punchline word; a `mood` flip when the rule fires.
- **Vary shot sizes and angles**: establishing high → full → medium → close; low angle for authority, high angle for crowds.
- **Pop-in graphics** for results: `sign` (bans/rules), `stamp` (verdicts), `bulb` (ideas), `icon` (zzz, !, ?), `title` ("3 YEARS LATER").
- **Different sets for the rule-of-three beats**, so each beat reads instantly.
- The ending is a callback, usually a `crash` into a deadpan face, plus a `glint`.

Then validate: `node scripts/render.mjs check $PROJ` and fix every warning.

### 3. Voice-over
Read `references/audio.md`. Run `python3 scripts/bs.py script $PROJ` and give the user the text from `build/vo_script.txt` with short ElevenLabs instructions (voice type, model, speed about 1.1, download MP3, upload it here). Then:
- **user uploads an MP3** → save it as `$PROJ/audio/vo.mp3` → `python3 scripts/bs.py align $PROJ` (or with `--alignment`/`--srt` for exact timing)
- **user gives an API key** → `python3 scripts/elevenlabs.py tts $PROJ --voice <id>` → `bs.py align $PROJ --alignment build/el_alignment.json`
- **no VO yet** → `python3 scripts/bs.py estimate $PROJ` and continue. The video plays with captions and SFX, and can be re-timed when a VO arrives.

Check the printed timing table. If the narrator said something different from a line, edit the line to match and align again.

### 4. Preview and fix
```bash
node scripts/render.mjs check   $PROJ     # warnings + build/events.json (sound cues)
node scripts/render.mjs preview $PROJ     # build/preview/sheet.jpg — 3 frames per shot, takes seconds
```
Read the sheet image and go through the checklist in `references/qa-and-iteration.md`. Fix framing, expressions and timing in story.json, then re-preview until it's clean. Send the sheet to the user when their opinion on look/framing would help before the long render.

### 5. Render
```bash
node scripts/render.mjs frames $PROJ --budget 240     # repeat until it prints DONE (resumable)
```
About 1 frame/second on a 2-core CPU (a 30 s video at 30 fps takes about 15 min). Use `--gpu` on a machine with a real GPU. If timing changed since the last render, delete `build/frames` first.

### 6. Sound + encode
```bash
node scripts/render.mjs check $PROJ           # refresh events.json if story.json changed
python3 scripts/bs.py mix $PROJ               # VO + auto SFX + optional audio/music.mp3 (ducked), −14 LUFS
python3 scripts/bs.py encode $PROJ            # → $PROJ/out/<title>.mp4
```
Verify the final file (extract 2–3 frames, check duration and audio) and deliver it. In the reply: one or two lines on what was made, and the 2–3 most useful things the user could ask to change next.

### 7. Iterate
Map feedback to edits using the table in `references/qa-and-iteration.md`. Re-preview after every change, re-render only what changed, then remix and re-encode.

## Improving the skill itself
This skill gets better each time it's used. When the user asks for something the engine can't do yet (a new set, prop, action, expression, overlay), extend the engine as described in `references/library.md` §9, test it with a preview, and keep the change. If the user wants these improvements permanently, they can ask Claude to update the skill and re-upload it.

## Files
- `engine/`: renderer (`js/engine.js` timeline + camera + compositor; `characters.js`, `faces.js`, `poses.js`, `sets.js`, `props.js`, `overlays.js`); vendored three.js; fonts (OFL)
- `scripts/`: `render.mjs`, `bs.py`, `elevenlabs.py`, `sfx_synth.py`, `setup.sh`
- `assets/sfx/`: 27 original synthesized sound effects
- `references/`: `story-formula.md`, `storyboard.md`, `library.md`, `audio.md`, `qa-and-iteration.md`
- `examples/clap-town/`: complete working story

# Quality checks, iteration and troubleshooting

## Look before you render (preview sheets)
`node scripts/render.mjs preview <project>` renders 3 frames per shot (start/middle/end) at half resolution into `build/preview/sheet.jpg` in seconds. **Open it with the Read tool and actually look.** Red bars mark cuts. For a specific moment: `--times 4.2,4.4,4.6`. For an even sweep: `--every 0.5`.

Check every shot for:
- [ ] Subject framed: face visible and not cut off at the top, not hidden behind furniture, a podium or another actor
- [ ] Caption readable and not covering the face (captions sit at 72.5% height; move the subject up with `"look": [0,-0.5,0]`, or shift the caption with `style.caption.y`)
- [ ] Faces show the intended expression at the key line
- [ ] Night looks like night; day flips back where intended
- [ ] Signs/stamps don't cover the subject's face (sign = top quarter)
- [ ] Every shot has movement (default `push`); some shots should be bigger moves (whip, crane, track, crash)
- [ ] Shot sizes vary: wide → medium → close rhythm, not five mediums in a row
- [ ] Nothing pokes through anything (actors inside desks, the camera inside a crowd)
- [ ] `render.mjs check` shows **no warnings**

## After the full render
1. Extract a few frames from the final MP4 and look at them: `ffmpeg -ss 5 -i out/x.mp4 -frames:v 1 /tmp/f.png`
2. Confirm the duration and the audio stream: `ffprobe -v error -show_entries format=duration:stream=codec_type out/x.mp4`
3. Check that the caption sync matches the voice at 2–3 points (compare `build/timing.json` with the audio).
4. Only then tell the user it's done.

## Turning feedback into fixes
Users rarely speak in engine terms. Ask for the **time stamp or shot number** when the feedback is vague ("which moment?"), then map it:

| user says | change |
|---|---|
| "too zoomed in", "can't see him" | camera `shot` one size wider, or `from` another side |
| "boring", "too static" | bigger `move` (`crane-up`, `orbit-right`, `track-*`), add `punch` on the key word, `whip` between subjects |
| "make it faster/snappier" | split lines into shorter chunks (more cuts), faster VO speed (re-generate VO), fewer lines per shot |
| "captions out of sync" | re-run `bs.py align` (with `--alignment` if possible), or hand-edit `build/timing.json` for one line |
| "the joke doesn't land" | rewrite the line (story-formula.md), highlight the hinge word, add a beat: `...` + `punch` + `mood` flip or `stamp` |
| "characters look the same" | different `preset`, `shirt` colors, `hat`/`hair`, `shirtDesign` |
| "too dark at night" | more lamps in frame, closer shot (the camera fill light helps), `style.brightness: 1.1` |
| "sound effects too loud / annoying" | `bs.py mix --sfx-db -5`, or `"sfx": false` on that FX |
| "I want X (a new place/prop/action)" | check library.md first. If missing, extend the engine (library.md §9) and preview |

Re-render only what changed: delete just the affected frame range from `build/frames/` (or the whole folder if timing changed), then run `frames` again. It skips existing frames.

**When timing changes (new VO, edited lines), all frames are invalid:** `rm -rf build/frames` before re-rendering.

## Rendering long videos inside a tool time limit
`render.mjs frames` is resumable. In environments where one command can only run a few minutes, run it with `--budget 240` (seconds) and repeat the same command until it prints `DONE`. Speed is roughly 1 frame/second at 720×1280 on a 2-core CPU (software WebGL). On a machine with a real GPU, add `--gpu` (several times faster). `--workers 2` helps on machines with 4+ cores.

## Troubleshooting
| symptom | fix |
|---|---|
| `No Chrome/Chromium found` | `bash scripts/setup.sh`, or set `CHROME_PATH=/path/to/chrome` |
| `Engine error: ...` | the message names the file/line; usually invalid JSON in story.json (trailing comma, comments) |
| `Need Node 22+` | upgrade Node, or `npm i ws` inside `scripts/` |
| black or empty frames | WebGL failed: run without `--gpu` (software rendering), or update Chrome |
| `timing.json has N lines but story has M` | lines changed after alignment: re-run `bs.py align` or `bs.py estimate` |
| alignment clearly wrong | the VO doesn't match the lines (changed words), or there's music in the VO track. Fix the lines, use a clean voice, or use `--alignment`/`--srt` |
| ElevenLabs `Cannot reach` | the sandbox blocks the domain. Use the web-app path (A), or allow the domain in settings |
| very slow render | use `--scale` only for previews (final renders must be full size). Shorten the video, or use `--gpu` locally |

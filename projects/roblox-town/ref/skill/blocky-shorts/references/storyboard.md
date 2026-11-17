# story.json — the storyboard format

One JSON file drives the whole video. The engine reads it and renders deterministically, so the same file always gives the same frames. Read `library.md` for every name you can use.

## Top level (comments are explanations only; real JSON can't contain them)
```jsonc
{
  "title": "Clap Town",
  "logline": "one sentence, for humans",
  "fps": 30,
  "width": 720, "height": 1280,
  "speed": 1.0,            // only for estimated timing (no voice-over yet): >1 = faster narration
  "lead": 0, "tail": 0.6,  // seconds of silence before the first line / after the last
  "seed": 0,               // changes the random extras' looks
  "style": {
    "caption": { "size": 50, "y": 0.725, "anim": "pop|bounce|rise|none", "uppercase": false,
                 "color": "#fff", "highlight": "#ffdc1f", "stroke": 9 },
    "captions": true, "clapBursts": true, "saturate": 1.18, "contrast": 1.06, "vignette": 0.42,
    "progress": false, "cutSfx": false, "blurSamples": 10
  },
  "cast": { "hero": { "preset": "kid", "shirt": "#1fbf6a" }, "mayor": { "preset": "mayor" } },
  "shots": [ ... ]
}
```

## Lines = narration = captions = timing
Every shot has `lines`: the narration split into the caption chunks shown on screen, usually 1–3 words each.
- `*word*` highlights in yellow. A line fully wrapped (`"*Night.*"`) shows entirely in yellow.
- A line can be an object: `{ "text": "...", "dur": 0.8, "pause": 0.2, "nocap": true }`. `dur` and `pause` only matter without a voice-over. `nocap` hides the caption.
- A silent beat: `{ "text": "", "dur": 0.6 }`. If there is a voice-over, it needs a real pause there.
- **The voice-over must say exactly these lines, in this order.** `bs.py script` exports them for ElevenLabs. If the narrator changes a word, edit the line to match before aligning.

A shot starts when its first line starts and ends when the next shot's first line starts. The cut lands on the word, which is the editing rhythm of the reference style.

## Time references (`at`, `until`)
Used by actions, FX, camera whip/crash and prop moves. All are relative to the shot:
| form | meaning |
|---|---|
| `0.4` | 0.4 s after the shot starts |
| `"clap..."` | when that line starts (case/punctuation-insensitive; a partial match works) |
| `"clap...+0.1"` / `"Oops.-0.08"` | offset from the line |
| `"#2"` | third line of the shot |
| `"start"`, `"mid"`, `"end"`, `"end-0.3"` | shot boundaries |

## Shot
```json
{
  "set": "plaza", "setOpts": { "stage": true }, "mood": "day",
  "lines": ["So the mayor", "banned", "*clapping.*"],
  "cast": {
    "mayor": { "spot": "podium", "face": "front", "expr": "smirk", "hold": "gavel",
               "do": [ { "do": "slam", "at": "banned-0.25", "dur": 0.75, "times": 2 },
                       { "expr": "angry", "at": "clapping." } ] }
  },
  "extras": { "walkers": 8,
              "crowd": { "n": 28, "rows": 4, "center": [0,0,16], "yaw": 180, "spacing": 2.7, "aisle": true,
                         "expr": "smile", "do": [ { "do": "clap", "at": "Oops.", "high": true, "expr": "happy" } ] } },
  "props": [ { "type": "rooster", "spot": "post", "yaw": -40 } ],
  "camera": { "on": "mayor", "shot": "medium", "angle": "low", "from": "front-right", "move": "push" },
  "fx": [ { "shake": 0.12, "at": "banned+0.05" },
          { "sign": { "text": "NO\nCLAPPING", "icon": "clap" }, "at": "clapping." } ],
  "in": "cut", "out": null, "hold": 0, "dur": null, "captions": true
}
```

### cast entry
| key | meaning |
|---|---|
| `spot` / `at` | where they stand (a spot name, or `[x, y, z]`) |
| `face` | `front` (toward camera, default), `back`, `left`, `right`, degrees, another actor's name, or `[x, z]` |
| `base` | `idle` (default) / `sit` / `lie` / `float`. Seat/bed spots set this automatically |
| `seat`, `bed`, `recline` | override seat height / bed height / recline amount |
| `expr` | starting expression |
| `hold` | held prop: `"phone"` or `{ "type": "gavel", "arm": "L" }` |
| `hidden` | start invisible (then `{"do": "appear"}`) |
| `tint` | tint the skin a color, e.g. `"#e8432f"` |
| `do` | timeline list: `{ "do": "<action>", "at": ..., "dur": ..., ...params }`, or `{ "expr": "shock", "at": ... }` |

The same cast name keeps the same look in every shot. Each shot sets its own positions, so cheat freely between shots (move actors and hide extras), the way real animators do.

### extras
- `walkers: n`: people strolling across the background zone of the set.
- `crowd`: a block of people, by default facing the set's crowd direction (plaza: toward the stage). `do` gives the whole crowd actions/expressions with slight random offsets.

### camera
See `library.md` §5. Default when omitted: on the first actor, `full`, eye level, from the front, slow `push`.

### fx
See `library.md` §7. Each FX can carry `"sfx"`, `"gain"`, `"sfxOffset"`.

## Worked example
`examples/clap-town/story.json` is a complete 9-shot short that uses most features. Copy its patterns.

## Common mistakes
- A time reference that doesn't match a line (typo): check warns `time ref "..." not found` and falls back to the shot start.
- A whole story in one shot: the reference style cuts on almost every line or two. Aim for 1–3 lines per shot.
- Three people in a `medium`: in 9:16 they won't fit. Use `full`, or frame one and `whip` to the others.
- Actors standing inside furniture: use the set's spots, or check positions in a preview.
- Lines edited after the voice-over was aligned: re-run `bs.py align`, because the line count must match `timing.json`.

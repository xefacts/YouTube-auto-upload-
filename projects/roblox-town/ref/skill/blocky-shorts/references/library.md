# Library — everything the engine can build

Names here are exact. If something you need is missing, see "Extending" at the bottom. Don't invent names: unknown names produce warnings in `render.mjs check`, and the thing silently falls back to a default.

## Contents
1. Sets and spots
2. Characters: presets, look options, expressions
3. Actions (body animation)
4. Props and animals
5. Camera: shot sizes, angles, sides, moves, whip, crash
6. Moods and transitions
7. FX: overlays and graphics
8. Sound events
9. Extending the engine

---

## 1. Sets and spots
Every set faces the camera from +z ("front"). A **spot** is a named place: `"spot": "sofa"`. Spots marked *(seat)* sit the actor down automatically. *(bed)* lays the actor down.

| set | what it is | spots |
|---|---|---|
| `plaza` | town square with fountain, lamps, benches, palms/pines, ocean, hills. `setOpts: {"stage": true}` adds a stone stage + wooden lectern | center, front, left, right, fountain, bench *(seat)*, podium (on stage), far |
| `street` | road, sidewalks, crosswalk, row of houses (windows light up at night), parked cars, traffic light | sidewalk, center, road, left, right, door, crosswalk |
| `living_room` | sofa (left, facing right), TV on right wall, rug, coffee table, lamp, shelf, window | sofa *(seat)*, sofa2 *(seat)*, center, tv, window, door |
| `bedroom` | bed (head toward back wall), nightstand + alarm clock, wardrobe, window, poster | bed *(bed)*, bedside, center, window, door |
| `classroom` | 6 desks, chalkboard on the front wall (behind camera), bulletin board, windows. `setOpts: {"board": "FRACTIONS\n3/8 + 5/12 = ?"}` | desk1…desk6 *(seat)*, teacher, board, center |
| `office` | 6 desks with glowing monitors, office chairs, city-view window, water cooler | desk1…desk6 *(seat, facing monitors)*, center, cooler, window |
| `farm` | grass, red barn, fence, hay bales, trees | barn, field, center, post (top of a fence post — put a rooster there), fence |
| `clinic` | dentist/doctor room: reclined chair, overhead lamp, cabinets, poster | chair *(seat, reclined)*, doctor, center, door |
| `studio` | seamless colored backdrop (`setOpts: {"color": "#3a7bd5"}`) for talking-heads, title moments, abstract gags | center, left, right |

Positions can always be given directly: `"at": [x, y, z]`. In the plaza, the fountain is at the origin and the camera side is +z; actors usually stand around z = 6–10.

## 2. Characters

### Presets (`"preset": "..."`)
`kid` `girl` `boy` `dad` `mom` `grandma` `grandpa` `teacher` `mayor` `boss` `worker` `chef` `doctor` `dentist` `cop` `farmer` `gamer` `noob` `king` `robot` `villain`

Any cast name that isn't defined gets a random but consistent look, which is handy for extras (`"s1"`, `"kid2"`).

### Look options (override any preset)
```json
"hero": { "preset": "kid", "skin": "#f5cd30", "shirt": "#1fbf6a", "shirtDesign": "stripe", "accent": "#ffffff",
          "pants": "#2b4fb8", "shoes": "#ffffff", "sleeves": "long|short|none", "bottom": "pants|shorts|skirt",
          "hat": "cap", "hatColor": "#e8352e", "hair": "short", "hairColor": "#2a1a0e",
          "extras": ["glasses"], "beard": "#3b2716", "expr": "smile" }
```
- **shirtDesign**: `plain` `stripe` `stripes` `number:7` `letter:A` `star` `heart` `suit` (lapels + tie in `accent`) `hoodie` `overalls` `coat` (lab coat) `police` `chef` `tie` `skull` `tank`
- **hat**: `cap` `cap_back` `beanie` `top` `fedora` `hard` `crown` `chef` `police` `cowboy` `party` `bunny` (a hat hides the hair)
- **hair**: `short` `spiky` `bob` `pony` `long` `buns` `bun` `afro` `mohawk` `bald`
- **extras** (drawn on the face): `glasses` `shades` `stache` `blush` `freckles`
- **body add-ons**: `"beard": color`, `"bowtie": color`, `"suspenders": color`, `"backpack": color`, `"cape": color`, `"headphones": color`, `"mask": true` (surgical), `"antenna": true`

### Expressions (`"expr"` or `{"expr": "shock", "at": ...}`)
`smile` `grin` `happy` `laugh` `smirk` `surprised` `shock` `scared` `sad` `cry` `angry` `furious` (red face) `sleepy` `asleep` `yawn` `strain` (red, sweating, holding it in) `sus` `love` `dead` `wink` `nervous` `blank` `evil` `cool` `disgust` `proud` `dizzy` `cringe` `talk`

Blinking is automatic (`"blink": false` turns it off). The mouth moves on its own during `talk`, `eat` and speech bubbles.

## 3. Actions
Put actions in an actor's `do` list: `{ "do": "clap", "at": "clap...", "dur": 0.6 }`. `at` is a time reference (see storyboard.md). `dur` is in seconds, or use `until`. Add `"hold": true` to freeze the final pose.

**Movement:** `walk` `run` `sneak` `slide` (each takes `"to": [x,y,z]` or a spot or another actor; duration comes from distance if omitted), `turn` (`"to": "front" | degrees | actor`). Actors face where they walk, then face the end direction (`"face"`).
**Base state:** `sit` `stand` `lie` `float`. Spots with seats/beds set these automatically.
**Visibility:** `appear` (pops in with a sound), `vanish` (pops out), `show`, `hide`.

| action | looks like | params |
|---|---|---|
| `clap` | hands meet repeatedly (sound on every clap) | `rate` (4.5), `high` (above head), `burst` (comic lines on the first claps; `"all"` for every clap) |
| `wave` | one arm waving | `arm`: `L`/`R` |
| `point` | arm points | `dir`: forward/up/left/right/side, `arm` |
| `cheer` | both arms up, bouncing | |
| `jump` | hop (boing sound) | |
| `dance` | arm pumps, hip sway | |
| `bow` | bends forward | |
| `slam` | raise + slam (gavel/fist, impact sound) | `times`, `arm` |
| `facepalm` `shrug` `think` `salute` `flex` `hug` `kneel` | as named | |
| `yawn` | arms up, yawn face | |
| `stretch` | arms up, rising | |
| `tremble` | holding it in, shaking with arms half up | |
| `shake` | small body shake | |
| `scared` | arms up shielding face, trembling | |
| `cry` | hands to face, sobbing | |
| `laugh` | leaning back, bouncing | |
| `nod` `headshake` | head only | |
| `look` | turns head | `yaw` (radians, + = actor's left), `down` |
| `talk` | gestures + mouth moves | |
| `hold` / `show` | arm(s) forward (combine with `"hold": "phone"` in the cast entry) | |
| `fall` / `faint` | topples over (thud), dead/dizzy face | `dir`: back/forward |
| `spin` | full spin | |
| `panic` | flailing, running in place | |
| `type` | typing on a keyboard | |
| `eat` | hand to mouth repeatedly | |
| `sleepstand` | asleep standing, head drooping | |
| `pose` | raw joint values (advanced) | `pose: { "aR": [-2.6, 0.5, 0], ... }` |

**Held items:** in a cast entry, `"hold": "phone"` or `{"type": "gavel", "arm": "R"}`.

## 4. Props and animals
Placed per shot: `"props": [{ "type": "chicken", "at": [4.5, 2.6, 2], "yaw": -30, "scale": 1, "color": "#8a3a1e" }]`
Movement: `"move": { "to": [x,y,z], "at": "line text", "dur": 1.5 }`.

`bulb` `phone` `book` `paper` (`text`) `cup` `pizza` `trophy` `money` `gavel` `mic` `balloon` `cake` `alarm` (shaking alarm clock) `laptop` `sign` (`text`, a 3D signpost) `box` `ball` `car` (wheels spin; front faces +x, so use `yaw`) `chicken` `rooster` `dog` (wagging) `cat` `tv` `table` `chair` `podium` `bed` `tree` `rock` `sword`

## 5. Camera
```json
"camera": { "on": "hero", "shot": "medium", "angle": "eye", "from": "front-right", "move": "push", "amount": 0.22 }
```
- **on**: actor name, list of actors (`["a","b"]`, framed together), `"crowd"`, a spot name, or a point `[x,y,z]`
- **shot**: `extreme` (face) · `close` (head + shoulders) · `medium` (waist up, the workhorse) · `cowboy` · `full` (whole body) · `wide` · `establishing`
- **angle**: `eye` · `low` (heroic/authority, looks up) · `high` · `top` (near overhead) · `worm`
- **from**: side relative to where the subject faces: `front` `front-left` `front-right` `left` `right` `behind` `behind-left` `behind-right`, or degrees. `side` adds a small extra angle (default 10°).
- **move** (over the whole shot): `push` (default, slow dolly-in; this is what the reference style uses on almost every shot) · `pull` · `static` · `zoom-in` · `zoom-out` · `crane-up` · `crane-down` · `track-left` · `track-right` · `orbit-left` · `orbit-right` · `handheld`. `amount` scales it, `ease`: inout/in/out/linear.
- **whip** pan to another subject mid-shot, with motion blur: `"whip": { "to": "b", "at": "contagious.", "dur": 0.26, "shot": "medium" }`
- **crash** zoom (accelerating, motion blur, settles with a jolt) for endings: `"crash": { "at": "Oops.", "dur": 0.35, "shot": "close" }`
- **fine control**: `"look": [0, 0.5, 0]` nudges the aim, `"offset": [x,y,z]` nudges the camera, `"fov": 50`, `"roll": 5` (Dutch tilt), `"raw": { "from": {"pos":[],"look":[],"fov":50}, "to": {...} }` for a fully manual move.
- **punch** and **shake** are FX (section 7).

Vertical video is narrow: 2–3 people side by side already need `full`. When a shot looks cramped, go one size wider rather than moving actors.

## 6. Moods and transitions
- `"mood": "day" | "sunset" | "night"` per shot. Change it instantly with `{"mood": "night", "at": "..."}`, or flicker with `{"flicker": ["day","night"], "at": 0, "every": 0.22, "until": "end"}`. At night, lamps, windows, screens and the fountain light up, and stars and a moon appear.
- Shot entry `"in"`: `cut` (default) · `flash` (white flash) · `fade` (from black) · `zoom` (radial zoom-blur) · `whip` (horizontal smear) · `glitch`. Exit: `"out": "fade"`.
- Explicit motion-blur window: `"blur": ["line text", "end"]`.

## 7. FX (overlays and graphics)
All FX live in the shot's `fx` list and take `at` (default: shot start).

| fx | what it does | sound |
|---|---|---|
| `{"punch": 0.2}` | fast zoom-in that holds (emphasis) | swish |
| `{"shake": 0.12, "dur": 0.28}` | camera shake (≥0.08 = impact) | impact |
| `{"mood": "night"}` / `{"flicker": [...]}` | lighting change | night_hit / day_chime |
| `{"bulb": "hero"}` | 3D light bulb pops above the head | ding |
| `{"sparkle": "hero"}` | sparkles around the head (or bulb) | sparkle |
| `{"glint": "hero"}` | one star glint near the face (great final beat) | sparkle |
| `{"burst": "hero"}` | comic impact lines at the hands | — |
| `{"sign": {"text": "NO\nYAWNING", "icon": "yawn", "slash": true}, "until": "end"}` | pop-in warning card at the top. Add `"instant": true` to carry it into the next shot without re-popping | pop |
| `{"stamp": "DENIED!"}` | rubber stamp slams in with screen shake | stamp |
| `{"icon": "zzz", "on": "hero", "dur": 1.2}` | floating icon above a head (or `"pos": [0.5, 0.3]` screen fraction) | depends on icon |
| `{"say": "Hello?", "on": "hero", "dur": 1.4}` | speech bubble; the actor's mouth moves | blip |
| `{"title": "3 YEARS LATER", "dur": 1.0, "style": "card" or "banner"}` | full-screen title card / top banner | whoosh / pop |
| `{"flash": true}` / `{"fade": "in"\|"out", "dur": 0.4}` | white flash / black fade | flash |
| `{"sfx": "boing", "gain": 0.8}` | just a sound at that moment | — |

**Icons** (vector, no emoji font needed): `exclaim` `question` `interrobang` `zzz` `anger` `heart` `sweat` `dots` `note` `dollar` `star` `skull` `check` `cross` `stop` `fire` `bulb` `clap` `yawn` `sneeze` `laugh` `face` `sleep` `clock` `phone`. Any other string is drawn as an emoji if the machine has an emoji font.

## 8. Sound events
The engine writes `build/events.json` (time, sound name, gain). `bs.py mix` places a file for each event. Lookup order: `<project>/sfx/<name>.(wav|mp3|…)` (yours win), then the built-in pack in `assets/sfx/`. Variants `name_1.wav`, `name_2.wav` are picked at random.

Built-in names: `whoosh` `whoosh_long` `swish` `pop` `pop_small` `poof` `ding` `sparkle` `clap` (3 variants) `applause` `impact` `thud` `stamp` `night_hit` `day_chime` `flash` `boing` `blip` `alert` `boop` `snore` `grr` `tick` `glitch` `riser`

Every action/FX takes `"sfx": "name"` to swap its sound, `"sfx": false` to silence it, and `"gain": 0.6`. `style.cutSfx: true` adds a soft tick on every cut (`style.cutGain`).

## 9. Extending the engine
The engine is plain JavaScript in `engine/js/`, and Claude can add to it on request:
- new set → `sets.js` (copy a similar set; return `group`, `spots`, `setMood`)
- new prop/animal → `props.js` · new action → `poses.js` (`ACTIONS`) · new expression → `faces.js` (`EXPRESSIONS`, plus a drawing case for new eye/mouth types) · new hat/hair/shirt print → `characters.js` · new overlay → `overlays.js`, then wire it in `engine.js` (`frame()` for drawing, `events()` for its sound).

After any engine change, run `render.mjs check` and a `preview` before rendering.

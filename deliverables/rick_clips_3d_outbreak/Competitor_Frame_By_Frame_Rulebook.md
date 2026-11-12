# Rick Clips Competitor Frame-by-Frame Analysis & 3-Skill Visual Rulebook

Analyzed **all 10 competitor HD videos** from Google Drive `Rick clips` folder frame-by-frame at native 30 fps (`17,745 frames` inspected via OpenCV phase correlation, Canny/ink chromaticity, Laplacian DOF variance, HSV colorimetry, Hough head-proportion measurement, and Whisper word-timestamp transcription), combined with:
1. `Skill/cartoon-short-kit (1).zip` (`Three.js` inked 3D worlds + `toon.ts` 2D bean-head cards + `audio.py`/`mix.py`)
2. `Skill/SKILL.md` (`cartoon-audio-short` — 1080x1920 @ 30fps, music & SFX locked at 50% / -6.0 dB of voice gated RMS)
3. `3D shorts free skills/3d-story-shorts.zip` (`kit.js`, `char.js`, `props.js`, `dress.js`, `Full.jsx` — busy dressed 3D sets, `#351f22` ink outlines, word-synced events & 1-word pop captions)

## 1. Frame-by-Frame Telemetry Across All 10 Competitor Videos

| # | Competitor Video | Res / FPS | Dur (s) | Cam Moving % | Mean Speed (px/f) | Hard Cuts | Mean Lum | Contrast | Saturation | Measured Ink Hex |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | An Unstoppable Spear vs an Unbreakable Shield | `1080x1920` @ `30` | 45.0 | **75.7%** | 3.15 | 1 | 127.7 | 46.0 | 0.45 | `#31211b` |
| 2 | Levels of Pirate Cannonballs | `1080x1920` @ `30` | 63.5 | **82.3%** | 4.88 | 5 | 123.8 | 45.3 | 0.49 | `#391d18` |
| 3 | The Ancient Jar That Warned an Empire | `1080x1920` @ `30` | 64.8 | **87.5%** | 3.01 | 1 | 112.5 | 45.9 | 0.41 | `#3a231f` |
| 4 | The Job Nobody Wants in Japan | `1080x1920` @ `30` | 60.5 | **93.7%** | 4.24 | 0 | 131.3 | 52.9 | 0.44 | `#1f192e` |
| 5 | The Town Built Around a Button | `1080x1920` @ `30` | 65.5 | **87.3%** | 3.72 | 0 | 122.2 | 45.0 | 0.46 | `#271e2a` |
| 6 | The Window That Breaks Japan_s Gambling Law | `1080x1920` @ `30` | 45.0 | **77.3%** | 1.35 | 0 | 86.8 | 53.9 | 0.52 | `#331e2b` |
| 7 | This Shape Saved Roller Coasters | `1080x1920` @ `30` | 63.2 | **86.8%** | 4.62 | 1 | 105.4 | 45.0 | 0.48 | `#22292c` |
| 8 | What the Grave Bell Really Meant | `1080x1920` @ `30` | 59.5 | **84.3%** | 3.67 | 0 | 106.8 | 49.7 | 0.52 | `#311a29` |
| 9 | Why Perfect Railroads Don_t Work | `1080x1920` @ `30` | 65.2 | **88.2%** | 4.97 | 1 | 116.8 | 50.4 | 0.49 | `#3c1f27` |
| 10 | Your Brain_s Secret Idea Zone | `1080x1920` @ `30` | 39.1 | **83.3%** | 2.48 | 1 | 65.7 | 49.6 | 0.50 | `#341c13` |

### Aggregate Medians & Hard Production Rules
- **Output Format**: `1080x1920` (`9:16` vertical), `30 fps`, H.264 High Profile (`yuv420p`).
- **Continuous 3D Camera Motion**: Camera moves on **85.5%** of all frames (range `75.7%–93.7%`), median translation `3.70 px/frame` at 1080p using smootherstep / monotone-cubic (`warpU`) glides + slow push-in creep on holds (zero frozen frames).
- **Hard Cuts**: Median **1–1 hard cut per minute** (4 of 10 videos have `0` hard cuts!). Prefer continuous 3D camera travel through doorways/windows/aisles and short cream/flash transitions on major time jumps.
- **Ink Outlines**: Warm dark espresso-plum ink **`#351f22`** (competitor median `#331e26`, never harsh `#000000`). Applied to all 3D world edges (inverted hull + crease edges) AND weighted thick-thin rings around 2D characters.
- **Color & Lighting**: Mean luminance `114.7/255`, std contrast `47.8`, mean HSV saturation **0.48** (rich painted flat-with-wear textures + 3-band toon shading + warm key light + cool blue/navy shadow fill + soft lamp/window bloom).
- **Character Spec (Measured on Close/Medium Frames)**:
  - Large pale warm-ivory oval/bean head (`#f8f5ec`) with soft directional crescent shadow (`#dad4ca`) on the side away from the key light.
  - Head outline thickness `~1.5–2.2%` of head width in `#2a1d21` / `#351f22`.
  - Rounded pill/bean torso (`2-tone` shaded modern jacket/hoodie/vest — no Roman tunic skirts), single-stroke dark ink limbs, round ink-disc hands, grounded shoes + soft multiply contact shadow blob.
  - Characters fill **38–58% of frame height** in medium shots; `"YOU"` uses authentic Rick-Clips **over-the-shoulder foreground back-of-head framing** + close prop interaction + dynamic 3rd-person survival staging.
- **Captions & Diegetic Text**:
  - All 3D labels live physically inside the world (`AISLE 4`, `SOUP`, `BIOLOGICAL EMERGENCY`, `INVENTORY SYSTEM`, `DELIVERY ENTRANCE`).
  - Competitor videos use crisp 1–2 word white bold pop captions (`Arial Black`, thick `#1a1414` stroke) at `~68%` frame height. Both **Captioned Master** and **Clean Master** are produced.
- **Audio Mix Rule (`SKILL.md`)**:
  - User's `cartesia_2026-11-10T09_33_50Z_Ronald_sonic-3.6_en-US.wav` (`334.40s`) is **100% unedited in timing**.
  - Synthesized suspense score bed and frame-synced foley/SFX sit at **50% (-6.0 dB gated RMS) of the voice level**, mastered to `-14 LUFS` / `-1.0 dBTP`.

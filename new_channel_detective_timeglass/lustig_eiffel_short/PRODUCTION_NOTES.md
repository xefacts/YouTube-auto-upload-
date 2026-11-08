# Short #3 — Production Notes (final)

**Title:** The Man Who Sold the Eiffel Tower
**Deliverable:** 1080x1920 · 90 fps · 5,178 frames · 57.53 s · −14.0 LUFS · H.264 High, BT.709

## What shipped
- 9 shots, one VO line each, camera + light + text system derived from the approved 10-shot storyboard
  (S3/S4 storyboard beats merged into one "the tower is being sold for scrap" shot to keep the read tight).
- VO: single narrator take, 9 clips, placed on the timeline with 0.30 s lead / 0.80 s tail.
- Text layer: karaoke captions (sentence level, auto-fit), 1925 counter + SECRET MEETING, THE TOWER label,
  THE BRIBE + THE BUYER + gold money arrow, HE VANISHES, THE PERFECT ALIBI, HE DOES IT AGAIN,
  1925→1935 rolling counter + CAUGHT, FAKE HUNDREDS, SOLD TWICE · ADMITTED ONCE, honesty label.
- Music: 104 bpm curious march that hard-stops on "Lustig vanishes", clock tick + drone under the alibi,
  march returns for the repeat, tense brake + siren for 1935, warm resolve under the payoff. −6 dB under voice.

## Pipeline (all in this repo)
| step | file | notes |
|---|---|---|
| VO | `prod/vo/*.mp3` | 9 clips |
| timeline | `prod/build_timeline.py` | trims silence, lays voice, derives shot lengths at 90 fps, writes `work/timeline.json` + `web/timeline.js` |
| story | `prod/web/story.js` | shots, cameras (fractional keys → any fps), props (papers slide, bribe crosses, door, sticker), cast poses |
| world | `prod/web/main.js` | suite / street / booth, Eiffel with X-bracing, overlay (title, counter, chips, labels, arrow, captions) |
| render | `prod/render_prod.mjs` | 3D at 612x1088 (sc=0.85), captions at 1080x1920, composited → 1080x1920 JPEG |
| audio | `prod/audio_build.py` | music + SFX, ducked under voice, normalised |
| encode | `prod/encode.sh` | 6 x 863-frame segments, crf 18, concat, mux, BT.709 limited range |

## Gotchas worth keeping
- Headless Chromium needs `LD_LIBRARY_PATH=/tmp/al2023/lib` (libnspr/libnss shipped inside
  `node_modules/@sparticuz/chromium/bin/al2023.tar.br`; extract it with node's `zlib.brotliDecompressSync` + `tar`).
- Swiftshader is the bottleneck: ~2.5 s/frame at 1080p, ~1.0–1.9 s/frame at 612x1088. Render the 3D at 0.85
  and captions at 1.5 — text stays razor sharp at 1080p.
- `--disable-web-security` is already in the chromium args, so the compositing `toDataURL` is clean.
- Do not call `floor()` on time-dependent values; motion helpers are normalised to 60 fps (`MPF`) so the same
  story code renders identically at 60/90/120 fps.

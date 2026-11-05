# Ricks Clips — pre-production research (5 Nov 2026)

## Channel identification

The user confirmed the intended reference is **Ricks Clips**, YouTube handle `@RicksClips3000`: https://www.youtube.com/@RicksClips3000 . The channel's discoverable description says Rick does voiceovers. One official Short located in search is **“Why Humans Can't Pick Random Numbers”**: https://www.youtube.com/shorts/TgyHSIttwdM . Search snapshot dated 14 Oct 2026 displayed 8.3M views and 158K likes; those counts are dynamic and should not be repeated as current metrics.

A third-party YouTube analysis video, not an official channel source, describes Ricks Clips as 2D cartoon characters in a bright 3D world telling strange true-history stories, and claims 24 Shorts / 184M views over 26 days: https://www.youtube.com/watch?v=X5WZeO9gIkE . Treat the description/statistics as that creator's claims, not verified channel-wide facts. Direct fetch of the public YouTube channel and Short pages returned HTTP 401, so we could not watch the public pages directly.

The user then provided a private Drive folder, `Rick clips`, containing eight reference MP4s, which were downloaded for private analysis. Its Drive URL and identifiers are intentionally omitted from this public-facing note. Drive metadata confirms all eight are vertical 1080×1920, 30 fps, and 39.1–64.9 seconds long. Sampled six frames across each clip (not a complete frame-by-frame audit). Visual observations across the sample set: simple round-headed, expressive cartoon characters with bold outlines and restrained facial features staged in colorful, richly detailed, depth-rich 3D-looking environments; the result reads as 2D/2.5D characters in 3D scenes rather than realistic character animation. The subject-specific setting changes with the narration (e.g. ships/cannonballs, castles/ancient artifacts, Japanese workplaces/gambling, railways, sleep/brain). Captions are large bold white text with a dark outline near bottom center, generally a short phrase or one/two words. Shots sampled at different points show scene and setting changes throughout. Mouth expressions are visible, but still-frame samples cannot establish precise viseme timing; audio was not human-listened/transcribed here.

**Important format distinction:** the supplied eight references are Shorts, roughly 40–65 seconds. A 19:20 runtime is not represented by those examples; if intended literally, it would be a major long-form adaptation with substantially more original story and scenes. Confirm whether the target is a 19:20 minute-long video or a 19–20 second/other duration, and confirm language before production. UNCASE's standing niche is true-crime / unsolved cases; do not silently switch it to unrelated general history.

## GitHub skills and tools inspected

1. `Flaxa-Technologies/ricks-clips-nextjs-studio`: https://github.com/Flaxa-Technologies/ricks-clips-nextjs-studio . Cloned for read-only inspection to `work/github_research/ricks-clips-nextjs-studio` (ignored research workspace; no code was run). Although its description name-checks Ricks Clips, the repository describes itself as a mathematical motion-graphics documentary/transitions studio, contains a Blinkit documentary dossier/script, and cites other documentary-motion references. There is **no LICENSE file**, so do not copy, ship, or build on its code/assets as though they were open source. It is not demonstrated to be an official Ricks Clips repo and is not the right tool for the requested character-led animation.
2. `studioigor/3d-animator-skill`: https://github.com/studioigor/3d-animator-skill . Cloned for inspection to `work/github_research/3d-animator-skill` and not yet installed or executed. Its LICENSE is MIT. Its documented features include character rigging, open-motion-capture workflow, facial blendshape curves/lip sync, eye/head/emotion animation, Blender application, and animation QA. It is a general technical animation skill, not a Ricks Clips style pack. Attribute and retain the MIT license if any of its code is reused; separately respect each mocap/model asset license.

Environment check: `blender` and system `ffmpeg` are not currently on PATH. An isolated `.venv` was created for reference-media analysis and contains Pillow plus `imageio-ffmpeg` (FFmpeg wrapper); no Blender installation was detected. A production plan needs a reviewed/approved toolchain and a feasible render-length/quality target before committing to a long render.

## Safe creative direction

If approved, use only broad, non-exclusive format traits: fast, clear voice-over; a surprising historical/crime hook; bright stylized 3D sets; expressive **original** characters; visual changes synchronized to narration; and a sourced factual payoff. Do not reproduce Ricks Clips' scripts, exact jokes, distinctive characters/character likenesses, scene compositions, thumbnail art, or voice. For UNCASE, keep true-crime ethics: documented facts versus uncertainty clearly separated, no graphic/sensational treatment, and no unsupported accusations of living people.

## Production gate still open

- Choose or approve the story/topic (a sourced cold case such as D. B. Cooper could fit the existing UNCASE niche).
- Confirm whether `19.20` means exactly **19 minutes 20 seconds**.
- Confirm narration language (English, Urdu, or another language).
- Then research sources, write an original script, lock narration/timing, create original scene/character assets, make a short visual test, and only then plan a full render.

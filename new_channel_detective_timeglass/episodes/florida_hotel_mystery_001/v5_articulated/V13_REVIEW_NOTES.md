# Florida Mystery V13 — owner-only review (2026-11-03)

**Review video:** https://drive.google.com/file/d/15Q_WOa9o46ufk9NSKq-HldI6rBHDmiWM/view?usp=drivesdk

**Status:** uploaded to “Florida Mystery — Current Private Review”; both video and folder were checked to have **one owner-only permission**, no public link. **Not uploaded to YouTube.**

- 36.500 s / 24 fps / 876 of 876 decoded frames; H.264 4320×7680 vertical **8K-size upscale** from 1080×1920 animation and smaller illustrated source art. This is **not native-detail 8K**. Stereo AAC 48 kHz; 100,322,204 bytes; SHA-256 `85c52dedc1988a9d7900174dba8004fd45fceb8d06e01c880571466b085ac794`.
- Complete selected 36.4955 s processed voice asset is uncut. Source/exported speech correlation after high-pass filtering: 0.921–0.987 at sampled early, middle, final and final-word windows. There is actual sound at 35.95–36.25 s and silence after ~36.3 in source: a terminal “p” could **not be verified as independent of the final spoken word**, so none was excised. Do not blindly trim it.
- User-provided suspense music under and dynamically ducked around voice, crossfaded in its natural tail; user's single gunshot at ~3.34 s, dying-man scream attack around the same instant, low distant laugh and discrete material foley. R128: approx −18.6 LUFS integrated, −2.6 dBFS true peak, LRA 3.4 LU. Supplied audio and its usage/monetization rights are **not cleared or asserted** here; this review is private.
- Flashback fictional blood accents authored in `assets/v13_blood_marks.svg` (and PNG raster from the same master), applied on consistent suit art after the shot and through falling/collapse. Non-graphic; no asserted true-case evidence or culprit.
- Five individually readable clue proofs: fiber on coat → thread on rail → bolt across gap → suite door → footprints to balcony; each has a dedicated large crop and a purposeful SVG-animated red ring, then an unzoomed two-column dossier board with each picture, short label and ring visible concurrently. `assets/v13_clue_ink.svg` is the editable vector path master; `render_v13.py` traces its cubic curves per frame without imported reference-video graphics.
- No top-screen headings over characters. Sparse short editorial captions are positioned **within** the lower visual zone only when needed (door, bolt, thread); the close-up cards already identify themselves, so no duplicated footer caption. No invented word-synced transcript. PRISM is the previously selected slate-blue detective, with restrained source-plane camera motion and refined key edges; shoe positions are not tweened.
- Reference analysis: `TRAIN2_V13_REFERENCE_ANALYSIS.md` (oldest three and newest three Train 2 videos plus Text screenshots). Their pixels, voices, sound, logos and copy were not used in the Florida video.

## Re-rendering

The editable cut is `render_v13.py` and depends on preceding `render_v12.py` / `render_v11.py`, the checked-in original art and SVGs, and the **user-supplied private** MP3s under ignored `work/v12_user_sfx/` using these exact filenames:

- `hitslab-tension-suspense-mystery-629029.mp3`
- `freesound_community-single-gunshot-54-40780.mp3`
- `universfield-male-death-scream-123078.mp3`
- `dragon-studio-evil-laugh-with-reverb-423668.mp3`

Recreate `.venv-video` with `tooling/creative/video-requirements.txt` before invoking `.venv-video/bin/python render_v13.py`. The tracked 11 KB blood PNG is a deterministic raster of the editable SVG (resvg-js v2.6.2), eliminating a runtime Node/browser dependency. Generated MP4s, local supplied samples and render cache are intentionally untracked/ignored. Do not publish or monetize without explicit owner approval and rights review.

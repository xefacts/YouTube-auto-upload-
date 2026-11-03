# Local creative toolchain — private research / motion-graphics reviews

The user's 2026-11-03 phone screenshots are in Drive **Master train**, not **Train** (which contains video examples). The screenshots show a **proposal**, not a single installable GitHub workflow: case research → writer/reviewer agents → structured script/storyboard → OpenFilm, Remotion or MoviePy/FFmpeg render → human review. OpenFilm is explicitly named in the vector/graphics layer. This directory pins an installable subset; it does **not** silently train a model, scrape copyrighted footage, infer guilt, or publish to YouTube.

## Install and verify

```sh
python3 -m venv .venv-video
.venv-video/bin/pip install -r tooling/creative/video-requirements.txt
python3 -m venv .venv
.venv/bin/pip install -r tooling/creative/agent-requirements.txt
npm ci --prefix tooling/creative
bash tooling/creative/doctor.sh
```

Python environments are separate because the CrewAI dependency tree's `pdfplumber` needs Pillow >=12.2 while MoviePy 2.2.1 requires Pillow <12. Do not mix them. Video/agent environments and `node_modules` are ignored; the npm lockfile is tracked. The `doctor.sh` script only links local ffmpeg/ffprobe into ignored `work/bin` and inspects the environment.

| Project (upstream) | Installed here | Purpose / license |
|---|---|---|
| [openfilm/openfilm](https://github.com/openfilm/openfilm) | npm `openfilm@0.2.7`; CLI manual + doctor tested | Editable HTML/CSS/SVG animation timeline; MIT. **Chromium not present** in this sandbox: Studio/browser renders are not verified and first-run browser download may fail under network restrictions. |
| [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | Python `.venv`, `crewai==1.15.34`, import + pip check passed | Writer/reviewer orchestration; MIT. Needs an approved LLM provider and keys before running agents; no accounts or keys have been supplied or stored. |
| [remotion-dev/remotion](https://github.com/remotion-dev/remotion) | npm `remotion@4.0.540`, package load passed | React motion graphics (React/ReactDOM pinned). **Conditional free/commercial license**: individual and organizations up to 3 employees generally eligible; other for-profit use requires a company license. No Remotion-rendered video claimed. |
| [Zulko/moviepy](https://github.com/Zulko/moviepy) | Python `.venv-video`, `moviepy==2.2.1`, import passed | Scripted timeline/edit assembly; MIT. |
| [opencv/opencv](https://github.com/opencv/opencv) | `opencv-python-headless==5.0.0.93`, import passed | Camera moves, masks, image analysis; Apache-2.0. |
| [svgdotjs/svg.js](https://github.com/svgdotjs/svg.js) | npm `@svgdotjs/svg.js@3.2.8`, package load passed | Editable vector overlays/diagrams; MIT. |
| [yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp) | Python `.venv-video`, CLI version checked | Research **metadata** from sources you have rights to access; Unlicense. No third-party footage/audio may be reused without permission; YouTube is not reachable from this sandbox. |
| [adbar/trafilatura](https://github.com/adbar/trafilatura) | Python `.venv-video`, `trafilatura==2.3.1`, import passed | Extract source text for human fact-checking; Apache-2.0. Use only permitted sources; retain citations. |

`@ffprobe-installer/ffprobe` and `imageio-ffmpeg` are runtime dependencies. The screenshots also mention Manim (attempted but **not installed**: missing system Cairo/pkg-config), AnimateAnyone (requires large licensed models/GPU, not installed), LoRA training (no authorized dataset/GPU), and various generic/possibly erroneous repo names. These are not represented as working installs. No training on private Drive references or real-case records occurred.

## Review-gated workflow

1. Research a topic using licensed/authorized sources; record URL, publisher, date, quotation and uncertainty. Do not let a model invent citations.
2. Draft **fictional** script or verified factual script with separately marked hypotheses. Human-check evidence and audience-sensitive language; CrewAI may organize the roles but cannot replace verification.
3. Create a shot list with exact scene duration and asset provenance. Use original art, not Train/Train 2 sample media; use SVG.js/Remotion/OpenFilm only if required by the shot. Existing Florida renderer uses Pillow/OpenCV/FFmpeg, not a disguised OpenFilm render.
4. Render locally with MoviePy/FFmpeg or the proven episode renderer; check full VO/last line, frame continuity, decodability, size versus native-source detail, licensing and unlicensed/graphic elements.
5. Upload **owner-only private review** after QA. Do not invoke any publishing workflow or change permissions without approval.

Florida V11 (full selected VO ending exactly with the video, PRISM, fictional flashback and original moving clue collage) rebuild:

```sh
.venv-video/bin/python new_channel_detective_timeglass/episodes/florida_hotel_mystery_001/v5_articulated/render_v11.py
```

The video output is ignored and is 2160 × 3840 **upscaled** from smaller source art; source stills, two generated performances and the renderer are tracked. V10 remains available as an earlier comparison cut. The Train screenshots are user-supplied research references, not to be copied into the final video.

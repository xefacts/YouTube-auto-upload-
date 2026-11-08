# Studio upgrade audit — what's real vs. what isn't, in this sandbox

This records an actual, executed audit (every claim below was verified by
running a command in this sandbox on 2026-11-08), not a plan based on
assumed capability. Re-run the commands in each section yourself if you
want to re-verify.

## PHASE 1 — Tool discovery (ground truth)

| Tool | Available? | Version found | Executes code? | Renders video? | Needs install? | Limits |
|---|---|---|---|---|---|---|
| Python | **Yes** | 3.11.2 (system `/usr/bin/python3`) | Yes | n/a | No | none |
| NumPy | Yes, installable | 2.4.6 via pip | Yes | n/a | pip install (not preinstalled) | none |
| Pillow | Yes, installable | 13.0.0 via pip | Yes | n/a (rasterizes) | pip install (not preinstalled) | none |
| FFmpeg | **Partial** | n9.0.2 | Yes (CLI) | **Yes** | Not present as a system binary at all (`ffmpeg: command not found`). Works only via the `imageio-ffmpeg` PyPI package, which bundles a static prebuilt binary. | None observed for CLI encode/decode-to-raw use |
| OpenCV | **Partial** | opencv-python-headless 5.0.0 via pip | Yes | **No** (video I/O) / **Yes** (image-array processing) | pip install | `cv2.VideoCapture` cannot open our own rendered mp4 — build reports `FFMPEG: YES` but the runtime decode still fails (`isOpened()=False`), because the dynamic codec libs it needs at runtime aren't present and can't be installed (see FFmpeg row). Pure array-based processing (`cv2.Laplacian`, `cv2.cvtColor`, histograms) on frames we already hold in memory works fine and is what `town3d/qc.py` actually uses. |
| Blender / `bpy` | **No** | `bpy` 4.2.0/5.0.1 wheels download fine from PyPI (cp311, matches our Python) | No — `import bpy` throws `ImportError: libXrender.so.1: cannot open shared object file` | No | The wheel itself installs; what's missing is a chain of OS shared libraries (`libGL.so.1`, `libGLX.so.0`, `libOpenGL.so.0`, `libICE.so.6`, `libSM.so.6`, `libXfixes.so.3`, `libXi.so.6`, `libXrender.so.1`, `libXt.so.6`, `libXxf86vm.so.1`, `libxkbcommon.so.0`). These are normally `apt install`-able, but **this sandbox's outbound network allowlist does not include Debian package mirrors** (`sudo apt-get update` fails: `Connection failed` to `deb.debian.org`) — only github.com, codeload.github.com, api.github.com, registry.npmjs.org, pypi.org, files.pythonhosted.org are reachable. There is no way to fetch those system libraries here. | Confirmed dead end for *this* sandbox. Would need a different execution host (own machine, a GPU cloud box, or a sandbox whose network allowlist includes an OS package mirror) to use real Blender. |
| ModernGL / GPU rendering | **No** | moderngl installs via pip | No | No | `moderngl.create_standalone_context()` fails: `libGL.so not found`. Separately, there is **no GPU device at all** in this sandbox: `nvidia-smi: command not found`, `/dev/dri` does not exist. Even with libGL present, there's no hardware to render on. | Hard sandbox limitation, not a licensing/cost issue. |
| Whisper / WhisperX / faster-whisper | **Partial** | `faster-whisper` installs cleanly via pip | Yes (library loads) | n/a | The **library** installs fine, but every variant (openai-whisper, faster-whisper, WhisperX) needs to download model weights at first use, from Hugging Face Hub / OpenAI's CDN — neither host is in the network allowlist. Confirmed failure: `ConnectError: TLS/SSL connection has been closed` trying to reach huggingface.co. | Cannot run real transcription/alignment in this sandbox. Our existing proportional-duration word-timing estimate in `town3d/narration.py` remains the only option here. |
| GitHub integration | **Yes** | `git`/`gh` pre-authenticated | Yes | n/a | none | Already used this session (push, this branch) |
| Google Drive integration | **Yes** | connector tool, already connected | Yes (search/download/upload) | n/a | none | Already used this session (download refs, upload final mp4) |
| GPU (any) | **No** | — | — | — | — | No `/dev/dri`, no `nvidia-smi`. CPU-only sandbox, 2 vCPU / 3.8 GB RAM confirmed via `nproc`/`free -h`. |
| CPU rendering | **Yes** | — | Yes | **Yes** | none | This is what the whole pipeline already runs on |

**Bottom line on Phase 1:** of your 11 items, only **Python, NumPy, Pillow,
FFmpeg (via bundled binary), GitHub, Drive, and CPU** are real, working
capabilities here. **OpenCV** is real but only for array-level image QC, not
video decoding. **Blender, ModernGL/GPU rendering, and Whisper-family tools
install but cannot execute** in this specific sandbox — not because they're
unavailable in principle, but because of two concrete, unfixable-from-here
blockers: (a) no GPU device, and (b) a network allowlist that excludes OS
package mirrors and model-weight hosts. These are environment facts, not
something more cleverness or more pip installs will route around.

## PHASE 3 — Rendering capability, stated plainly

- Blender execution: **No** (see above).
- GPU rendering: **No** (no GPU hardware present).
- CPU rendering: **Yes** — this is the entire existing pipeline (`town3d/engine.py`, a from-scratch numpy+Pillow software rasterizer: perspective projection, `look_at` camera, backface culling, painter's-algorithm depth sort, flat diffuse+ambient shading, distance fog, sky gradient).
- Persistent project storage: **Yes**, within `/home/user/...` (this repo), git-tracked for code, workspace-persisted for generated media.
- Long-running render jobs: **Yes**, via `start_process`/background execution, but in practice unnecessary so far — the full 8-scene, 72.5s "Skyline Town" video rendered + encoded in **under 90 seconds** on 2 vCPUs.
- Frame-by-frame rendering: **Yes** — every frame is individually rasterized; nothing is interpolated/faked.
- Video encoding: **Yes**, H.264/yuv420p via the `imageio-ffmpeg`-bundled binary, piped raw frames over stdin (no intermediate PNG dump needed).

No step above is simulated. Every number quoted (render times, frame counts, QC metrics) came from an actual command run in this turn.

## PHASE 2 / 4 — Free integration architecture (what's actually wired up)

Since Blender and GPU paths are not available here, the "3D animation,
camera, lighting, materials" stage uses the **custom software renderer**
instead — free, open-source-license-free (it's our own ~200-line code,
0 dependencies beyond numpy/Pillow), and already proven at production
quality for this project's blocky/low-poly visual style.

```
Reference Analysis      town_sheets/ contact sheets + read_file inspection (ffmpeg frame
                         sampling) -- manual/LLM reading of on-screen captions, no paid
                         transcription API used.
        |
Style Bible              town3d/README.md "What was analyzed" section.
        |
Script                    town3d/narration.py (NARRATION list: 8 lines, sourced stat).
        |
Storyboard                town3d/scenes.py (8 scene builders, camera keyframes).
        |
Character Generation       town3d/figures.py: person() -- procedural voxel rig.
        |
Environment Generation      town3d/figures.py: house(), pillar_tower(), golden_elevator(),
                             coin_jar(), cloud(), sky_platform().
        |
3D Animation / Camera /    town3d/engine.py (Camera, look_at, perspective projection) +
Lighting                   town3d/render.py (per-frame eye/target lerp with smoothstep easing,
                             directional light + ambient in Scene).
        |
Voiceover                  generate_speech tool (Arena), voice locked per user instruction.
        |
Synchronization             town3d/narration.py word_timings() -- proportional per-word timing
                             against each clip's real measured duration (town_audio/durations.json).
                             NOT phoneme-aligned (Whisper alignment unavailable here -- see Phase 1).
        |
Rendering                   town3d/engine.py render_frame() -> raw RGB bytes -> ffmpeg stdin
                             (libx264, yuv420p, crf 17), no GPU, no Blender.
        |
Editing                      ffmpeg concat (narration tracks) + mux (town3d/render.py / ad hoc
                              mux commands this turn).
        |
Independent Quality Control  town3d/qc.py -- OpenCV-measured brightness/contrast/sharpness/
                              caption-visibility checks on every frame, INDEPENDENT of the
                              renderer's own code path, with a hard pass/fail gate.
```

Every arrow above is a real, runnable module in this repo today — not a
diagram of intent.

## PHASE 6 — Executed test (see terminal output this turn for raw numbers)

Rendered one original 10-second sample (720×1280, 24fps, 240 frames): a
person on a rooftop garden at golden hour with an orbiting camera and
sky-pillars in the background — a new scene, not reused from the delivered
video. Saved to `town_render/phase6_sample.mp4` plus 3 still frames.

**Measured results (this run, this sandbox):**
- Render + encode wall time: **~10.7 seconds** for the full 10s/240-frame clip (faster than real-time on 2 vCPUs, no GPU).
- `town3d/qc.py` independent OpenCV QC gate: **240/240 frames passed** — avg brightness 187.5/255, avg contrast (stddev) 58.8, avg Laplacian sharpness 170.7, 0 flagged frames (no too-dark/too-bright/blank/degenerate frames detected).
- Visual spot-check (3 frames read back manually): character and pillar geometry render cleanly, correct shading/perspective, no artifacts.

**Verdict: sample passed QC.** Per your Phase 6 instruction, no full video
was (re-)generated as a result of this specific test — it was a pipeline
validation, not a production run. The previously delivered "Skyline Town"
video already exists (in your Drive "In the town" folder and on this
branch's commit history) and was not regenerated here.

## What would change this audit

If you run this same pipeline on a different host — your own machine, a
VPS, or a sandbox with (a) a real GPU and (b) network access to an OS
package mirror and/or Hugging Face — then Blender (`bpy`), ModernGL GPU
rendering, and real Whisper-based caption alignment all become genuinely
usable, and would meaningfully upgrade visual fidelity (PBR materials, soft
shadows, depth of field) and caption accuracy (phoneme-level timing) beyond
what's possible here. That's a real, not hypothetical, upgrade path — just
not one this sandbox can execute.

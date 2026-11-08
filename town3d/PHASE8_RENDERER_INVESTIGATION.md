# Phase 8 — Professional Open-Source Renderer Investigation

## 1. Candidates investigated (desk research, before cloning anything)

Checked via the GitHub API (`gh api repos/<owner>/<repo>`, live data, not
memory) on 2026-11-08:

| Candidate | License | Last push | Stars | Headless CPU path on a GH Actions runner? | Verdict |
|---|---|---|---|---|---|
| `blender/blender` | GPL family (GitHub shows `NOASSERTION` because of Blender's compound license file, but the project is GPL-2.0-or-later) | 2026-11-07 (yesterday) | 21,753 | **Yes** — official portable Linux build is a self-contained CLI binary (`blender -b ...`), no system package installation needed | **Shortlisted** |
| `blender/cycles` | Apache-2.0 | 2026-11-04 | — | Ships *inside* the Blender build above; not used standalone | Covered via Blender, not separately |
| `mrdoob/three.js` | MIT | 2026-11-08 (today) | 117,855 | Needs a GPU/WebGL context (browser or headless-Chrome-with-GPU-flags); GitHub's standard runners have **no GPU** | **Not shortlisted for this sandbox/CI path** — right tool for a browser-delivered interactive experience, wrong tool for CPU-only headless frame rendering |
| `gkjohnson/three-gpu-pathtracer` | MIT | 2026-11-08 (today) | 2,033 | Same GPU/WebGL dependency as three.js, plus it specifically wants a path-tracing-capable GPU for reasonable speed | **Not shortlisted**, same reason |
| `bardia-ardakanian/blender-headless-render` | MIT | 2026-07-29 | 0 | Yes in principle — it's a thin wrapper around `blender -b --python <script>`, the same primitive used directly below | **Investigated, not adopted as a dependency** (see note) |

**Note on `blender-headless-render`:** this repo is a small personal utility
(a couple of Python scripts calling the same `blender -b --python` CLI
pattern this project already needed). Pulling in a 0-star, infrequently
updated third-party repo for something this thin would add an external
dependency without adding real capability — the exact pattern (`blender -b
-noaudio --python-exit-code 1 -P scene.py -- ...`) was implemented directly
in this project's own `.github/workflows/blender_render_test.yml` and
`blender_test/scene.py`, which is fully inspectable, debuggable, and
version-controlled in this repo, consistent with "do not clone or install
every project blindly."

**Three.js / three-gpu-pathtracer were not cloned or installed at all** —
they were ruled out on the single hard fact that this sandbox and GitHub's
standard hosted runners have no GPU, which is a precondition both projects
assume for acceptable performance. Blender/Cycles was the only candidate
that offers a genuine CPU rendering path, which matches our actual
available hardware — this is why it was chosen for real testing instead of
the others, not because of star count (three.js has 54× more stars than
Blender's GitHub mirror and was still not selected).

## 2. Re-verifying old assumptions (per instruction: don't assume, test)

- **`import bpy` locally in the Arena sandbox:** still fails (re-confirmed
  earlier this project) — required Linux system libraries (libGL, libX11,
  etc.) are absent, and this sandbox's `pip install` cannot install system
  packages. This has not changed.
- **GPU availability, locally or on GitHub Actions:** still absent.
  GitHub's hosted runners are documented and billed as CPU-only; no GPU
  flag or option was found or assumed.

## 3. GitHub Actions feasibility — real test, not installation-only

Two full runs were executed on `arena/0abc33e0-youtube-auto-upload`
(`.github/workflows/blender_render_test.yml`, triggered by `push`, since
`workflow_dispatch` only registers for the default branch, which this
session deliberately never touches):

| Run | Result | What it actually proved |
|---|---|---|
| `42465344459` (first run) | Render step reported ✓ but **zero PNG frames existed** and the encode step failed with ffmpeg exit 127 | **False positive** — Blender silently swallowed a Python exception (an empty `${{ inputs.frames }}` on a `push` trigger crashed the argv parser) and exited 0 anyway. ffmpeg is **not** preinstalled on `ubuntu-latest`. |
| `42467173155` (after fixes) | **All steps genuinely passed**: checkout → system info → download official Blender 4.2.7 Linux build → verify headless → render (Cycles, CPU) → install ffmpeg → encode MP4 → upload artifact → commit sample frames back to git | **Confirmed working end-to-end.** Total job time 3m10s–3m36s across the two successful runs, most of it (observed from timing, not from unavailable logs) spent downloading/extracting the ~300MB official Blender tarball and running `apt-get update`. |

Both `gh run view <id> --log` and `--log-failed` fail from this sandbox with
an `EOF` connecting to `results-receiver.actions.githubusercontent.com`,
and `gh run download` fails the same way against
`productionresultssa32.blob.core.windows.net` — **neither host is in this
sandbox's network allowlist**, so full raw step logs and the official
artifact zip cannot be pulled directly into the agent sandbox. This is a
sandbox limitation, not a GitHub Actions limitation. Worked around by
having the workflow itself commit a few representative rendered PNG frames
straight into the git branch (`blender_test/verified_output/`, with
`[skip ci]` to avoid a trigger loop) — git/codeload.github.com **is** in
the allowlist, so those real frames were pulled back in and inspected.

### What was actually inspected (not just "the step said success")

`blender_test/verified_output/frame_0001.png`, `frame_0007.png`,
`frame_0012.png` — genuine Cycles CPU renders of the test scene in
`blender_test/scene.py` (a simple placeholder character + two box
"buildings" + floating square "windows"/props), with an **animated camera**
across the 12 frames (buildings visibly pan out of frame between frame 1
and frame 12, confirming the animation actually ran, not just a static
frame repeated). Visible in the real pixels, not claimed:

- **Real soft shadows** with correct penumbra falloff under the character
  and the floating props — qualitatively softer/more physically plausible
  than this project's own blob-shadow approximation in `engine2.py`.
- **Smooth curved geometry** (a rounded cylinder-capped head) — something
  the NumPy/Pillow renderer cannot produce at all (it only has flat-faced
  polygons; the closest approximation is the `_octagon_xz` beveled-box
  trick, which is still faceted, not curved).
- Correct ambient/contact shading and physically-based light falloff.

This is a deliberately minimal placeholder test scene (it was not built to
look good — it was built to prove the pipeline works), so it is **not**
directly compared frame-for-frame against the polished Phase 5 NumPy/Pillow
sample; the comparison that matters here is capability, not finished art.

## 4. Renderer selection, based on the actual measured evidence above

| Dimension | NumPy/Pillow (`engine2.py`) | Blender/Cycles via GitHub Actions |
|---|---|---|
| Shadow quality (actually observed) | Fixed-shape blob approximation | Real soft shadows with correct penumbra |
| Geometry (actually observed) | Flat-faced, beveled boxes only | True curved primitives (cylinders etc.) |
| Round-trip latency | Seconds, in-sandbox, fully interactive | ~3–4 min per job (mostly Blender download + apt-get), off-sandbox, requires a push + poll cycle |
| Debuggability from this agent | Full (stdout, exceptions, immediate re-run) | Partial — full logs/artifacts blocked by sandbox network allowlist; must rely on hard-coded checks (`test -f frame_0001.png`) and the verified-frame-commit workaround |
| Asset reuse across scenes | Already implemented (`character.py`, `environment.py` as importable, reusable modules) | Would need to be (re)implemented as Blender Python (`bpy`) scene-building code — not yet done beyond the placeholder test scene |
| Cost | Free, unlimited, local | Free for this **public** repo (GitHub Actions minutes are unlimited on public repos), but artifact/log storage still has a 500MB account-level quota on the Free plan and nothing here assumes that is unlimited |

**Decision:** Blender via GitHub Actions is **confirmed technically
feasible** and demonstrably produces higher-fidelity shadows and geometry
than the custom renderer. It is **not** switched to as the primary renderer
in this delivery, for three honest reasons: (1) the placeholder test scene
has not been rebuilt into the actual character/environment/camera/animation
system this project already has working and validated in Python — that is
new, non-trivial `bpy` scripting work, not a configuration change; (2) the
per-iteration feedback loop (push → wait ~3–4 min → poll → work around
blocked log/artifact fetching) is far slower than the sub-second local
iteration this project has been using to find and fix real bugs (e.g. the
near-plane clipping bug and the camera-swing bug caught this session); (3)
per the standing instruction, retain the existing renderer as a fallback
regardless.

**Recommendation:** keep `engine2.py` as the primary renderer for continued
fast local iteration, and treat Blender-via-GitHub-Actions as a **validated,
ready-to-build-on secondary pipeline** for a future pass that specifically
needs shadow/geometry fidelity beyond what the CPU/NumPy path can do — the
GitHub Actions plumbing (Blender download, headless invocation, ffmpeg
install, artifact handling, verified-frame retrieval workaround) is now
proven and reusable; what remains is porting `character.py`/`environment.py`
to `bpy` scene-building calls, which was out of scope for this feasibility
pass.

## 5. Rendering job manager, QC split, and production pipeline

Not implemented this round. Per the final video requirements section of the
brief, these are real, non-trivial systems (a persistent job table with
retry/resumption, a dual technical/artistic QC gate, and a full
script→storyboard→...→QC pipeline) that should be built once a renderer
choice is locked in for full production, rather than built twice (once
against the NumPy engine's per-frame API and again against a `bpy` job
model) before that choice is made. This is flagged here as planned,
unbuilt work, not claimed as done.

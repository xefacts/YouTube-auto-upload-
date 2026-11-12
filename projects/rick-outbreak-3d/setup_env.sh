#!/usr/bin/env bash
# ============================================================================
# setup_env.sh — restore the /tmp render environment after a sandbox wipe.
# The movie pipeline (render_full_v3.mjs, verify_v3_*.mjs, build_v3_audio.py)
# expects these absolute paths, all under /tmp:
#
#   /tmp/chromium                  (chrome-headless-shell binary, SwiftShader)
#   /tmp/libEGL.so /tmp/libGLESv2.so /tmp/libvk_swiftshader.so
#   /tmp/al2023/lib/...            (shared libs for the chromium build)
#   /tmp/fonts/                    (fonts for DOM text overlays)
#   /tmp/studio_env/node/          (npm project with playwright-core)
#   /tmp/studio_env/bin/ffmpeg     (+ ffprobe)
#   /tmp/rick_study/v3/            (audio + render outputs)
#
# Sources (only allowlisted hosts are used):
#   - registry.npmjs.org : playwright-core, @sparticuz/chromium (v153),
#                          @ffmpeg-installer/ffmpeg, @ffprobe-installer/ffprobe
#   - pypi.org / files.pythonhosted.org : numpy scipy soundfile pedalboard
#
# Usage:  bash projects/rick-outbreak-3d/setup_env.sh
# ============================================================================
set -euo pipefail

echo "[setup] 1/5 playwright-core (node)…"
mkdir -p /tmp/studio_env/node /tmp/studio_env/bin /tmp/rick_study/v3 /tmp/spcwd /tmp/ffinst
cd /tmp/studio_env/node
[ -d node_modules/playwright-core ] || npm install playwright-core --no-audit --no-fund

echo "[setup] 2/5 chromium + swiftshader + al2023 libs (from @sparticuz/chromium)…"
if [ ! -x /tmp/chromium ]; then
  cd /tmp/spcwd
  [ -f sparticuz-chromium-*.tgz ] || npm pack @sparticuz/chromium --silent
  rm -rf package && tar xzf sparticuz-chromium-*.tgz
  node -e '
    const zlib=require("zlib"),fs=require("fs");
    const dec=(s,d)=>fs.writeFileSync(d,zlib.brotliDecompressSync(fs.readFileSync(s)));
    dec("/tmp/spcwd/package/bin/chromium.br","/tmp/chromium");
    dec("/tmp/spcwd/package/bin/swiftshader.tar.br","/tmp/swiftshader.tar");
    dec("/tmp/spcwd/package/bin/fonts.tar.br","/tmp/fonts.tar");
    dec("/tmp/spcwd/package/bin/al2023.tar.br","/tmp/al2023.tar");
  '
  chmod +x /tmp/chromium
  tar -xf /tmp/swiftshader.tar -C /tmp
  mkdir -p /tmp/fonts /tmp/al2023
  tar -xf /tmp/fonts.tar -C /tmp/fonts
  tar -xf /tmp/al2023.tar -C /tmp/al2023
fi
LD_LIBRARY_PATH=/tmp/al2023/lib:/tmp /tmp/chromium --version

echo "[setup] 3/5 ffmpeg + ffprobe (npm installers)…"
if [ ! -x /tmp/studio_env/bin/ffmpeg ]; then
  cd /tmp/ffinst
  [ -f package.json ] || npm init -y >/dev/null
  npm install @ffmpeg-installer/ffmpeg @ffprobe-installer/ffprobe --no-audit --no-fund
  cp "$(node -e 'console.log(require("@ffmpeg-installer/ffmpeg").path)')" /tmp/studio_env/bin/ffmpeg
  cp "$(node -e 'console.log(require("@ffprobe-installer/ffprobe").path)')" /tmp/studio_env/bin/ffprobe
  chmod +x /tmp/studio_env/bin/ffmpeg /tmp/studio_env/bin/ffprobe
fi

echo "[setup] 4/5 python audio deps…"
python3 - <<'PY' || pip3 install --break-system-packages numpy scipy soundfile pedalboard
import numpy, scipy, soundfile, pedalboard
print("py deps already present")
PY

echo "[setup] 5/5 done. Verify with:"
echo "  node projects/rick-outbreak-3d/verify_v3_geometry.mjs   # 35/35 expected"
echo "  python3 projects/rick-outbreak-3d/build_v3_audio.py     # from repo root"

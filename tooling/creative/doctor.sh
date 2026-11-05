#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
mkdir -p work/bin
ln -sfn "$(.venv-video/bin/python -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')" work/bin/ffmpeg
ln -sfn "$PWD/tooling/creative/node_modules/@ffprobe-installer/linux-x64/ffprobe" work/bin/ffprobe
if ! PATH="$PWD/work/bin:$PATH" tooling/creative/node_modules/.bin/openfilm doctor; then
  echo "OpenFilm doctor reported an incomplete runtime (browser not installed here)." >&2
fi
.venv-video/bin/pip check
.venv/bin/pip check
npm ls --prefix tooling/creative --depth=0

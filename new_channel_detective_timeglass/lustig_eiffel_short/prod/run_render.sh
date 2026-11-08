#!/bin/bash
# Render a list of frame ranges sequentially, resumable.
# usage: ./run_render.sh <tag> <range1> [range2 ...]
cd "$(dirname "$0")"
TAG=$1; shift
export LD_LIBRARY_PATH=/tmp/al2023/lib
for R in "$@"; do
  echo "=== [$TAG] $R ==="
  RESUME=1 node render_prod.mjs /tmp/frames "$R" 0.85 1.5 0.93 || echo "FAILED $R"
done
echo "=== [$TAG] all done ==="

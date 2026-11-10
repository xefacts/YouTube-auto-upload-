#!/usr/bin/env bash
# Fetch a Piper voice (open-source VITS, rhasspy/piper) from a public GitHub
# mirror that keeps the .onnx files as real blobs (no LFS, no HuggingFace).
#   ./fetch_voice.sh en_US/ryan/medium
set -euo pipefail
VOICE="${1:-en_US/ryan/medium}"          # <lang>/<name>/<quality>
DEST="$(cd "$(dirname "$0")" && pwd)"
REPO="https://github.com/jaredsbror/glowing-umbrella"
SRC="piper/piper-voices/${VOICE%%/*}/${VOICE}"
TMP="$(mktemp -d)"
git clone --filter=blob:none --no-checkout --depth 1 "$REPO" "$TMP"
cd "$TMP"
git sparse-checkout init --cone
git sparse-checkout set "$SRC"
git checkout --quiet
cp "$SRC"/*.onnx "$SRC"/*.onnx.json "$DEST"/
rm -rf "$TMP"
ls -lh "$DEST"/*.onnx | tail -2

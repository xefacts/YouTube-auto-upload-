"""Locate and call ffmpeg. Order: $FFMPEG_BINARY -> PATH -> imageio-ffmpeg bundle."""
from __future__ import annotations

import os
import shutil
import subprocess
from functools import lru_cache


@lru_cache(maxsize=1)
def ffmpeg_path() -> str:
    env = os.environ.get("FFMPEG_BINARY")
    if env:
        return env
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # pragma: no cover - only when nothing is installed
        raise RuntimeError(
            "ffmpeg not found. Install ffmpeg, set FFMPEG_BINARY, or pip install imageio-ffmpeg"
        ) from exc


def run(args: list[str]) -> subprocess.CompletedProcess:
    """Run ffmpeg with the given args. Raises RuntimeError with the tail of stderr on failure."""
    cmd = [ffmpeg_path(), "-hide_banner", "-nostdin", "-y", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed ({proc.returncode}): {proc.stderr[-1500:]}")
    return proc

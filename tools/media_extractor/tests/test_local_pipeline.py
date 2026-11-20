"""Offline self-test: builds a synthetic clip (2 colour scenes + 3 beeps at known times),
runs the pipeline on the local file and checks scenes, sound events and outputs.

Run:  python3 -m unittest discover -s tests -v   (from tools/media_extractor)
"""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from media_extractor.ffmpeg import ffmpeg_path  # noqa: E402
from media_extractor.pipeline import process  # noqa: E402

SR = 44100
BEEPS = [2.0, 5.0, 7.5]          # seconds
SCENE_CUT = 4.0                  # colour change at 4s
DURATION = 9.0


def make_fixture(tmp: Path) -> Path:
    # audio: silence with 3 short 1 kHz beeps
    t = np.arange(int(SR * DURATION)) / SR
    audio = np.zeros_like(t)
    for b in BEEPS:
        mask = (t >= b) & (t < b + 0.15)
        audio[mask] = 0.8 * np.sin(2 * np.pi * 1000 * t[mask])
    wav = tmp / "beeps.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((audio * 32767).astype(np.int16).tobytes())
    video = tmp / "fixture.mp4"
    # video: red for 4s then blue for 5s (hard cut), muxed with the beeps
    subprocess.run(
        [
            ffmpeg_path(), "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-t", str(SCENE_CUT), "-i", "color=c=red:s=640x360:r=30",
            "-f", "lavfi", "-t", str(DURATION - SCENE_CUT), "-i", "color=c=blue:s=640x360:r=30",
            "-i", str(wav),
            "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]",
            "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-shortest", str(video),
        ],
        check=True,
    )
    return video


class LocalPipelineTest(unittest.TestCase):
    def test_pipeline_on_local_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            video = make_fixture(tmp)
            out = tmp / "out"
            manifest = process(str(video), out)

            self.assertEqual(manifest["status"], "done")
            for name in ["source.mp4", "audio.wav", "audio.mp3", "manifest.json"]:
                self.assertTrue((out / name).exists(), name)

            # sound events: each beep should be found within 0.1 s
            found = [e["t"] for e in manifest["events"]]
            for b in BEEPS:
                self.assertTrue(any(abs(f - b) < 0.1 for f in found), f"beep at {b}s not found in {found}")

            # scene cut: a detection within 0.5 s of the colour change
            cuts = [s["t"] for s in manifest["scenes"]]
            self.assertTrue(any(abs(c - SCENE_CUT) < 0.5 for c in cuts), f"scene cut not found in {cuts}")
            self.assertTrue(all((out / "keyframes" / s["keyframe"]).exists() for s in manifest["scenes"]))

            # SFX clips written
            clips = list((out / "sfx").glob("*.wav"))
            self.assertEqual(len(clips), len(manifest["events"]))

            saved = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["files"]["video"], "source.mp4")


if __name__ == "__main__":
    unittest.main()

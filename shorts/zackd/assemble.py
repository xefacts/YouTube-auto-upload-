"""Mux rendered frames + mix into the final vertical mp4."""
from __future__ import annotations
import argparse, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", default=os.path.join(HERE, "..", "out", "build"))
    ap.add_argument("--out", default=os.path.join(HERE, "..", "out", "tap_your_card.mp4"))
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--size", default="1080:1920")
    ap.add_argument("--audio", default=None)
    ap.add_argument("--crf", default="18")
    args = ap.parse_args()
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    frames = os.path.join(args.build, "frames")
    audio = args.audio or os.path.join(args.build, "mix.wav")
    cmd = [ff, "-y", "-framerate", str(args.fps), "-i", os.path.join(frames, "f_%05d.jpg")]
    if os.path.exists(audio):
        cmd += ["-i", audio]
    cmd += ["-vf", f"scale={args.size}:flags=lanczos", "-c:v", "libx264", "-profile:v", "high",
            "-pix_fmt", "yuv420p", "-crf", args.crf, "-preset", "medium", "-g", str(args.fps * 2)]
    if os.path.exists(audio):
        cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-movflags", "+faststart", args.out]
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)
    print("wrote", args.out, os.path.getsize(args.out) / 1e6, "MB")

if __name__ == "__main__":
    main()

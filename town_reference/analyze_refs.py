import cv2, numpy as np, subprocess, json, os, sys, wave, struct
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SRC_DIR = "/home/user/YouTube-auto-upload-/town_reference"
FRAME_DIR = os.path.join(SRC_DIR, "frames")
AUDIO_DIR = os.path.join(SRC_DIR, "audio")

videos = [f for f in os.listdir(SRC_DIR) if f.endswith(".mp4")]
videos.sort()

def ffprobe_text(path):
    p = subprocess.run([FFMPEG, "-i", path, "-hide_banner"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    return p.stderr.decode("utf-8", errors="ignore")

def parse_streams(text):
    info = {"video": None, "audio": None, "duration": None, "bitrate": None}
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("Duration:"):
            parts = line.split(",")
            info["duration"] = parts[0].replace("Duration:", "").strip()
            for p in parts:
                if "bitrate" in p:
                    info["bitrate"] = p.strip()
        if "Stream" in line and "Video:" in line:
            info["video"] = line
        if "Stream" in line and "Audio:" in line:
            info["audio"] = line
    return info

def extract_audio_wav(path, out_wav):
    cmd = [FFMPEG, "-y", "-i", path, "-vn", "-ac", "1", "-ar", "16000", "-f", "wav", out_wav]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def audio_envelope(wav_path, win_sec=0.5):
    if not os.path.exists(wav_path):
        return None
    with wave.open(wav_path, 'rb') as w:
        sr = w.getframerate()
        n = w.getnframes()
        raw = w.readframes(n)
    data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    win = int(sr * win_sec)
    if win <= 0 or len(data) == 0:
        return None
    n_win = len(data) // win
    rms = []
    for i in range(n_win):
        seg = data[i*win:(i+1)*win]
        rms.append(float(np.sqrt(np.mean(seg**2)) + 1e-9))
    rms = np.array(rms)
    silence_thresh = 0.02
    silence_windows = int(np.sum(rms < silence_thresh))
    return {
        "duration_s": round(len(data)/sr, 2),
        "mean_rms": round(float(np.mean(rms)), 4),
        "max_rms": round(float(np.max(rms)), 4),
        "min_rms": round(float(np.min(rms)), 4),
        "pct_silence_windows": round(100*silence_windows/len(rms), 1),
        "n_windows": len(rms),
        "window_sec": win_sec,
    }

def detect_shots(path, sample_fps=2.0, diff_thresh=18.0, max_frames_cap=4000):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    step = max(1, int(round(fps / sample_fps)))
    prev_small = None
    cuts = []  # timestamps in seconds
    idx = 0
    sampled = 0
    brightness_vals = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % step == 0:
            sampled += 1
            small = cv2.resize(frame, (64, 64))
            small_gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(np.float32)
            brightness_vals.append(float(small_gray.mean()))
            if prev_small is not None:
                diff = float(np.mean(np.abs(small_gray - prev_small)))
                if diff > diff_thresh:
                    cuts.append(round(idx / fps, 2))
            prev_small = small_gray
            if sampled > max_frames_cap:
                break
        idx += 1
    cap.release()
    duration = total_frames / fps if fps else 0
    return {
        "fps": round(fps, 3), "total_frames": total_frames, "width": width, "height": height,
        "duration_s": round(duration, 2), "cuts_detected": cuts, "n_cuts": len(cuts),
        "mean_brightness_0_255": round(float(np.mean(brightness_vals)) if brightness_vals else 0, 1),
        "brightness_std": round(float(np.std(brightness_vals)) if brightness_vals else 0, 1),
    }

def extract_frame_at(path, t_sec, out_jpg, scale_w=480):
    cmd = [FFMPEG, "-y", "-ss", str(max(0, t_sec)), "-i", path, "-frames:v", "1",
           "-vf", f"scale={scale_w}:-1", out_jpg]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

results = {}
for v in videos:
    vid_id = os.path.splitext(v)[0]
    path = os.path.join(SRC_DIR, v)
    print("Processing", v, flush=True)
    text = ffprobe_text(path)
    streams = parse_streams(text)
    shots = detect_shots(path)
    wav_path = os.path.join(AUDIO_DIR, vid_id + ".wav")
    extract_audio_wav(path, wav_path)
    audio = audio_envelope(wav_path)
    if os.path.exists(wav_path):
        os.remove(wav_path)  # keep only JSON summary, not raw wav

    vid_frame_dir = os.path.join(FRAME_DIR, vid_id)
    os.makedirs(vid_frame_dir, exist_ok=True)
    duration = shots["duration_s"]
    cuts = shots["cuts_detected"]
    # choose representative timestamps: start, evenly spaced sample of cuts (cap 10), end
    cap_n = 10
    if len(cuts) > cap_n:
        idxs = np.linspace(0, len(cuts)-1, cap_n).astype(int)
        chosen_cuts = sorted(set(cuts[i] for i in idxs))
    else:
        chosen_cuts = cuts
    timestamps = [0.3] + [c + 0.25 for c in chosen_cuts] + [max(0.3, duration - 0.5)]
    timestamps = sorted(set(round(t, 2) for t in timestamps if 0 <= t < duration))
    saved = []
    for t in timestamps:
        fname = f"t{t:.2f}.jpg".replace(".", "_", 1)
        out_jpg = os.path.join(vid_frame_dir, fname)
        extract_frame_at(path, t, out_jpg)
        if os.path.exists(out_jpg):
            saved.append({"t": t, "file": os.path.relpath(out_jpg, SRC_DIR)})

    results[vid_id] = {
        "file": v, "ffprobe": streams, "shots": shots, "audio": audio,
        "frames_saved": saved,
    }
    print(f"  -> {shots['n_cuts']} cuts, duration {duration}s, {len(saved)} frames saved", flush=True)

with open(os.path.join(SRC_DIR, "analysis_summary.json"), "w") as f:
    json.dump(results, f, indent=2)
print("DONE")

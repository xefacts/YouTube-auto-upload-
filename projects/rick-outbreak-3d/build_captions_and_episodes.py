#!/usr/bin/env python3
"""
Encodes directly from the lossless 10,032-frame MJPEG segments (concat_raw.txt + master_audio.wav):
  1) Outbreak_RickClips_3D_Full_Clean_1080x1920.mp4     (1080x1920 SAR 1:1 DAR 9:16, 30fps, <85 MB)
  2) Outbreak_RickClips_3D_Full_Captioned_1080x1920.mp4 (with native 1080p Rick-Clips ASS pop-captions, <85 MB)
  3) 5 standalone YouTube Shorts Episodes (Ep01..Ep05, 1080x1920, 30fps)
  4) Final_Master_1080p_Frames_Sheet.jpg (16-frame 1080p verification contact sheet)
"""
import json
import os
import re
import subprocess
from PIL import Image, ImageDraw

FFMPEG     = "/tmp/studio_env/bin/ffmpeg"
WORDS_JSON = "projects/rick-outbreak-3d/data/words.json"
OUT_DIR    = "/tmp/rick_study/out"
CONCAT_RAW = os.path.join(OUT_DIR, "concat_raw.txt")
MASTER_WAV = os.path.join(OUT_DIR, "master_audio.wav")
CLEAN_MP4  = os.path.join(OUT_DIR, "Outbreak_RickClips_3D_Full_Clean_1080x1920.mp4")
CAP_MP4    = os.path.join(OUT_DIR, "Outbreak_RickClips_3D_Full_Captioned_1080x1920.mp4")
ASS_PATH   = os.path.join(OUT_DIR, "outbreak_rick_captions.ass")

DANGER_WORDS = {
    "emergency", "alert", "biological", "neurological", "outbreak", "infected",
    "screams", "falls", "collide", "deadbolt", "slams", "shouting", "shutters",
    "apart", "flickering", "neither", "help", "barricade", "clatter", "broken",
    "glass", "arm", "clicking", "creature", "impact", "abandon", "alive", "shaking",
}
GOLD_WORDS = {
    "four", "two", "three", "10", "one", "1", "2", "half", "hour",
    "water", "protein", "peanut", "butter", "soup", "aisle", "flashlight", "strap",
}

def fmt_ass_time(sec):
    sec = max(0.0, float(sec))
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def build_ass():
    with open(WORDS_JSON) as f:
        data = json.load(f)
    words = data["words"]

    phrases = []
    cur = []
    for w in words:
        cur.append(w)
        tok = w["word"]
        char_len = sum(len(x["word"]) for x in cur)
        if len(cur) >= 3 or tok.endswith((".", "!", "?", ",", ";", ":")) or char_len >= 16:
            phrases.append(cur)
            cur = []
    if cur:
        phrases.append(cur)

    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: RickPop,DejaVu Sans,76,&H00F8FAFF,&H000000FF,&H00221F35,&H78120C14,-1,0,0,0,100,100,1.2,0,1,8.5,3.5,5,70,70,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    for idx, ph in enumerate(phrases):
        t0 = ph[0]["start"]
        t1 = ph[-1]["end"] + 0.06
        if idx + 1 < len(phrases):
            t1 = min(t1, phrases[idx + 1][0]["start"] - 0.01)
        if t1 <= t0 + 0.04:
            t1 = t0 + 0.08

        styled_tokens = []
        for w in ph:
            raw = w["word"]
            clean = re.sub(r"[^a-z0-9]", "", raw.lower())
            disp = raw.upper()
            if clean in DANGER_WORDS:
                styled_tokens.append(r"{\c&H004A57FF&}" + disp + r"{\c&H00F8FAFF&}")
            elif clean in GOLD_WORDS:
                styled_tokens.append(r"{\c&H0048CFFF&}" + disp + r"{\c&H00F8FAFF&}")
            else:
                styled_tokens.append(disp)

        text_body = " ".join(styled_tokens)
        tag = r"{\an5\pos(540,1375)\fscx84\fscy84\t(0,80,\fscx106\fscy106)\t(80,150,\fscx100\fscy100)}"
        lines.append(f"Dialogue: 0,{fmt_ass_time(t0)},{fmt_ass_time(t1)},RickPop,,0,0,0,,{tag}{text_body}\n")

    with open(ASS_PATH, "w") as f:
        f.writelines(lines)
    print(f"Generated {len(phrases)} Rick-Clips pop-caption events -> {ASS_PATH}")

def main():
    build_ass()

    print("1/4 Encoding 1080x1920 Clean Master (SAR 1:1 DAR 9:16, <85 MB)...")
    subprocess.run([
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", CONCAT_RAW,
        "-i", MASTER_WAV,
        "-vf", "scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p",
        "-c:v", "libx264", "-preset", "veryfast", "-tune", "animation",
        "-crf", "23", "-maxrate", "2050k", "-bufsize", "4100k", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        CLEAN_MP4,
    ], check=True)
    print(f"Clean Master complete -> {CLEAN_MP4} ({os.path.getsize(CLEAN_MP4)/1048576:.1f} MB)")

    print("2/4 Encoding 1080x1920 Captioned Master (native 1080p ASS pop-captions, <85 MB)...")
    subprocess.run([
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", CONCAT_RAW,
        "-i", MASTER_WAV,
        "-vf", f"scale=1080:1920:flags=lanczos,setsar=1,ass={ASS_PATH}:fontsdir=/usr/share/fonts/truetype/dejavu,format=yuv420p",
        "-c:v", "libx264", "-preset", "veryfast", "-tune", "animation",
        "-crf", "23", "-maxrate", "2050k", "-bufsize", "4100k", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        CAP_MP4,
    ], check=True)
    print(f"Captioned Master complete -> {CAP_MP4} ({os.path.getsize(CAP_MP4)/1048576:.1f} MB)")

    print("3/4 Slicing 5 standalone YouTube Shorts Episodes (1080x1920, 30fps)...")
    episodes = [
        ("Ep01_Emergency_Alert_and_Street_Chaos_1080x1920.mp4",      0.00,  62.66),
        ("Ep02_Locked_Doors_and_Shutters_Down_1080x1920.mp4",       62.66, 127.60),
        ("Ep03_Missing_Deliveries_and_Ration_Count_1080x1920.mp4", 127.90, 176.88),
        ("Ep04_Woman_At_The_Glass_and_Back_Door_1080x1920.mp4",    176.88, 252.00),
        ("Ep05_Broken_Window_Breach_and_Survival_1080x1920.mp4",   252.20, 334.40),
    ]
    for fname, s0, s1 in episodes:
        ep_out = os.path.join(OUT_DIR, fname)
        subprocess.run([
            FFMPEG, "-y",
            "-ss", f"{s0:.2f}", "-to", f"{s1:.2f}",
            "-i", CAP_MP4,
            "-c:v", "libx264", "-preset", "veryfast", "-tune", "animation",
            "-crf", "21", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            ep_out,
        ], check=True)
        print(f"Episode ready -> {fname} ({os.path.getsize(ep_out)/1048576:.1f} MB)")

    print("4/4 Extracting 16 verification stills -> Final_Master_1080p_Frames_Sheet.jpg...")
    sample_dir = os.path.join(OUT_DIR, "verify_frames")
    os.makedirs(sample_dir, exist_ok=True)
    times = [2.2, 14.0, 37.0, 53.1, 68.6, 77.0, 95.0, 136.0, 142.0, 152.0, 196.6, 217.5, 233.0, 273.0, 296.0, 331.0]
    imgs = []
    for idx, ts in enumerate(times):
        fp = os.path.join(sample_dir, f"f_{idx:02d}.jpg")
        subprocess.run([
            FFMPEG, "-y", "-ss", f"{ts:.2f}", "-i", CAP_MP4,
            "-frames:v", "1", "-q:v", "2", fp
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        imgs.append((ts, Image.open(fp)))

    cols, rows = 8, 2
    tw, th = 270, 480
    sheet = Image.new("RGB", (cols * tw, rows * (th + 32)), (16, 18, 24))
    draw = ImageDraw.Draw(sheet)
    for idx, (ts, im) in enumerate(imgs):
        r, c = divmod(idx, cols)
        sheet.paste(im.resize((tw - 6, th - 6), Image.Resampling.LANCZOS), (c * tw + 3, r * (th + 32) + 30))
        draw.text((c * tw + 10, r * (th + 32) + 8), f"t = {ts:.1f}s (1080x1920)", fill=(248, 242, 228))

    sheet_out = "deliverables/rick_clips_3d_outbreak/Final_Master_1080p_Frames_Sheet.jpg"
    sheet.save(sheet_out, quality=93)
    print(f"ALL DONE! Saved {sheet_out}")

if __name__ == "__main__":
    main()

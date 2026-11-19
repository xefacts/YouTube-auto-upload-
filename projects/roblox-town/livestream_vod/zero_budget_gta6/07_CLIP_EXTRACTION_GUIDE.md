# Clip Extraction Guide — YouTube Studio Clips (FREE, official)

**Rights status:** User ne confirm kiya hai ke Speed ke clips ke rights unke paas hain.
**Budget:** $0.00 — YouTube Studio Clips bilkul free hai.

> ⚠️ **Timing:** Stream abhi LIVE hai (13 h in). Clips tabhi ban sakte hain jab stream
> **end** ho aur VOD process ho jaye. Pehle stream end hone do.

---

## Step 1: Stream end hone do

- Stream end hone ke baad YouTube VOD process karega (30 min – 2 h)
- VOD pe "Show transcript" available hoga tabhi

## Step 2: Transcript se timestamps nikalo

- `01_FREE_TRANSCRIPT_GUIDE.md` ke 4 methods mein se koi ek use karo
- Transcript mein "mission complete" / "mission failed" dhoondho
- Pehle do **completed** missions ke exact timestamps note karo
- Transcript is chat mein paste karo → main verify karke final timestamps dunga

## Step 3: YouTube Studio Clips banao (har moment ke liye)

1. YouTube Studio kholo (studio.youtube.com) — channel owner account se
2. **Content** → VOD select karo
3. Video player mein desired timestamp pe jao
4. Player ke neeche **"Clip"** button (scissors icon) pe click karo
5. Start/end time select karo (5–60 seconds per clip)
6. Clip ka title do (e.g. "Mission 1 Complete")
7. **Share** → clip ka link copy karo
8. Clip download karo (clip page pe download option, ya screen record)

**Har clip ke liye ye repeat karo:**
- Hook (stream opening, 5–10 s)
- Mission 1: start, attempts, fail, clutch, complete (5 clips × 5–10 s)
- Mission 2: start, complication, clutch, complete (4 clips × 5–10 s)
- Payoff (5 s)

**Total: ~11 clips, har ek 5–60 s. Sab free.**

## Step 4: Clips Drive pe upload karo

1. Google Drive pe folder banao: "Speed GTA6 Clips"
2. Saare clips upload karo
3. Folder ka link ya file IDs is chat mein bhejo
4. Ya clips workspace mein upload karo (Arena file upload)

## Step 5: Main assembly karunga

Clips milte hi main:
1. Clips Drive se download karunga (download_file)
2. `scripts/assemble_video.py` se 1080×1920 video banaunga
3. Voiceover + SFX mix karunga
4. Final video Drive pe upload karunga
5. **Public link dunga**

## Step 6: Voiceover (aapka step)

Do options:
- **Apni awaz record karo** (OBS/phone) — `narration.txt` padho, MP3 bhejo
- **edge-tts** (apne machine pe): `pip install edge-tts` → narration.txt se MP3 banao

Voiceover milne ke baad main mix karunga.

---

## Clip naming (Drive pe upload karte waqt)

```
01_hook.mp4
02_m1_start.mp4
03_m1_attempts.mp4
04_m1_fail.mp4
05_m1_clutch.mp4
06_m1_complete.mp4
07_m2_start.mp4
08_m2_complication.mp4
09_m2_clutch.mp4
10_m2_complete.mp4
11_payoff.mp4
```

Ye naming `assemble_video.py` ke manifest se match karegi.

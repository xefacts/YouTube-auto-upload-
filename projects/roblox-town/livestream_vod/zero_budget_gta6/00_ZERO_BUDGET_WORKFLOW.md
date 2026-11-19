# ZERO-BUDGET WORKFLOW — IShowSpeed GTA 6 VOD → cinematic short

**TOTAL APPROVED BUDGET: $0.00**
**Source:** `https://www.youtube.com/live/qSyo5d-dVzA`
**Verified metadata (fetched 2026-11-16):**
- Title: 🔴PLAYING GTA 6 EARLY ACCESS GAMEPLAY GET IN HERE!
- Channel: IShowSpeed (62.7M subscribers)
- Date: Nov 18, 2026 · Status: **LIVE** (started ~12 h ago, 133,143 watching)
- YouTube game tag: Grand Theft Auto VI (2026)
- Description: donation/merch links only — **no chapters**

> ⚠️ **Is pack ka status:** ye paid workflow (`../00_WORKFLOW.md` — Apify + Gemini) ko
> **replace** karta hai. Apify extraction aur Gemini API dono is workflow mein **nahi** hain.
> Purane docs reference ke liye rakhe hain, lekin active workflow ye wala hai.

---

## 1. The one hard truth (pehle ye samajh lo)

| Fact | Status |
|---|---|
| Stream abhi **LIVE** hai | ✅ verified (YouTube page) |
| Live stream ka caption track abhi **exist nahi karta** | ✅ verified — timedtext endpoint ne HTTP 500 diya |
| Captions tabhi bante hain jab stream **end** ho aur YouTube VOD process kare | ✅ YouTube behaviour |
| "GTA 6 Early Access" — asal game kya hai | ❓ **UNVERIFIED** (title ka claim hai; GTA 6 officially release nahi hua — content transcript/visual check se hi confirm hoga) |
| Pehle do completed missions ke naam/timestamps | ❓ **UNVERIFIED** — transcript ke bina koi bhi timestamp dena jhoot hoga |

**Iska matlab:** abhi ke liye main mission analysis nahi kar sakta — koi bhi agent nahi kar
sakta, kyunki data hi abhi exist nahi karta. Ye workflow usi din ke liye hai jab captions
available ho jayein. Tab tak har jagah `TBC` (to be confirmed) likha rahega, aur ye
**by design** hai.

---

## 2. Complete workflow ($0.00)

```
STEP 0  Stream end hone ka intezaar
        └─ YouTube VOD process hone do (usually 30 min – 2 h after stream ends)
        └─ Cost: $0 · Time: wait

STEP 1  FREE transcript nikalo (4 methods — sab verified free, §4 dekho)
        └─ Method A: YouTube player → "..." → "Show transcript" (browser, $0)
        └─ Method B: youtube-transcript-api (Python, MIT, no API key, $0)
        └─ Method C: yt-dlp --skip-download --write-auto-subs (Unlicense, $0)
        └─ Method D: free website (youtubetotranscript.com etc., $0)
        └─ Output: timestamped text (HH:MM:SS + line)
        └─ Cost: $0.00

STEP 2  Transcript paste karo is chat mein (ya evidence/ folder mein save karo)
        └─ Main (agent) mission boundaries identify karunga:
           "mission complete" / "mission failed" / objective lines dhoondh kar
        └─ Pehle do COMPLETED missions ke exact timestamps likhunga
        └─ Cost: $0.00

STEP 3  Manual visual verification (YouTube pe, free)
        └─ Har candidate timestamp pe video kholo, ±10 s check karo:
           □ Mission banner dikha? (on-screen text verbatim likho)
           □ HUD/objective match karta hai transcript se?
           □ 9:16 crop mein action safe hai?
        └─ Jo pass kare → VERIFIED. Jo fail → discard.
        └─ Cost: $0.00 (sirf aapka time)

STEP 4  Footage decide karo (3 options — §5 mein honest comparison)
        └─ Option 1: YouTube Studio Clips — sirf agar channel aapka hai (free, official)
        └─ Option 2: OBS se specific windows record karo (free, ToS/copyright flag)
        └─ Option 3: Original B-roll (apni gameplay / free stock / text cards) — safest
        └─ Cost: $0.00

STEP 5  Story + narration (Roman Hindi) — 02_STORY_ROMAN_HINDI.md
        └─ Slots transcript se fill hote hain (mission names, moments)
        └─ Cost: $0.00

STEP 6  Voiceover — edge-tts (free, no API key) YA apni awaz record karo
        └─ edge-tts: pip install edge-tts → hi-IN / ur-PK voices
        └─ Roman Hindi ke liye: Devanagari text TTS ke liye, Roman Hindi captions ke liye
        └─ Cost: $0.00

STEP 7  Edit — DaVinci Resolve (free, no watermark) YA CapCut desktop (free)
        └─ Timeline: 03_EDITING_TIMELINE.csv (beat-by-beat)
        └─ Captions: 04_CAPTIONS_SOUND.md
        └─ Sound design: 04_CAPTIONS_SOUND.md + repo ka existing SFX pack
        └─ Cost: $0.00

STEP 8  Export + QC
        └─ 1080×1920, 30 fps, H.264, −14 LUFS
        └─ Contact sheet check, caption timing check
        └─ Cost: $0.00
```

**Total: $0.00** — har step pe cost zero hai, aur har tool ka free status §4/05 mein verify kiya gaya hai.

---

## 3. What you get from this pack

| File | Kya hai |
|---|---|
| `01_FREE_TRANSCRIPT_GUIDE.md` | Transcript nikaalne ke 4 free methods, step-by-step |
| `02_STORY_ROMAN_HINDI.md` | Original cinematic story (Roman Hindi) — structure + slots |
| `03_EDITING_TIMELINE.csv` | Beat-by-beat editing timeline + manual verification checklist |
| `04_CAPTIONS_SOUND.md` | Caption text (Roman Hindi) + sound design instructions |
| `05_FREE_TOOLS_VERIFIED.md` | Har tool ka free-status verification (sources ke saath) |
| `06_LIMITATIONS.md` | Har limitation, seedhi bhasha mein |
| `scripts/get_transcript.py` | Transcript fetcher (user apne machine pe chalata hai, $0) |

---

## 4. Free tools — verification summary (detail: 05_FREE_TOOLS_VERIFIED.md)

| Tool | Kaam | Free status | Evidence |
|---|---|---|---|
| YouTube "Show transcript" | Transcript dekhna | ✅ Free (YouTube ka hissa) | YouTube player feature |
| youtube-transcript-api | Transcript download (Python) | ✅ MIT, no API key | PyPI + GitHub |
| yt-dlp | Captions download (CLI) | ✅ Unlicense, open source | GitHub (187k stars) |
| DaVinci Resolve | Video editing | ✅ Free, no watermark, UHD 60fps | Blackmagic (Studio $295 alag hai) |
| CapCut desktop | Video editing (easy) | ✅ Free, no watermark (desktop) | ByteDance |
| OBS Studio | Screen recording | ✅ GPLv2, open source | obsproject.com |
| edge-tts | Voiceover (TTS) | ✅ MIT, no API key | PyPI + GitHub |
| FFmpeg | Audio/video processing | ✅ Open source | ffmpeg.org (repo mein already hai) |

**Koi paid trial nahi. Koi subscription nahi. Koi credit card nahi.**

---

## 5. Footage options — honest comparison

| Option | Cost | Legal/ToS status | Quality | Verdict |
|---|---|---|---|---|
| **YouTube Studio Clips** | $0 | ✅ Official, allowed | 5–60 s clips, 720p+ | **Best — lekin sirf agar channel aapka hai.** Ye IShowSpeed ka channel hai, isliye aapke liye available nahi hoga (unless aap khud Speed ho 😄) |
| **OBS screen record** (specific windows) | $0 | ⚠️ YouTube ToS technically downloading/recording ko mana karta hai; copyright Speed ka content hai — fair use commentary ke liye typically OK, lekin guarantee nahi | Source quality (1080p) | **Practical $0 path**, lekin risk flag ke saath. Sirf approved windows record karo, poora VOD kabhi nahi |
| **Original B-roll** | $0 | ✅ 100% safe | Aapki marzi | **Safest.** Apni GTA gameplay, free stock (Pexels/Pixabay), ya text/graphic cards. Story narration ke saath ye bhi cinematic lagta hai |
| Apify / paid extractor | ❌ | — | — | **REMOVED** (budget $0) |
| Gemini API | ❌ | — | — | **REMOVED** (budget $0) |

**Recommendation:** Pehle Option 3 (original B-roll) se video banao — ye 100% safe hai aur
story-driven video mein kaafi hota hai. Agar aapko asli stream footage chahiye, to Option 2
(OBS, sirf verified windows) — risk samajh ke.

---

## 6. What I still need from you

1. **Stream end hone ke baad** transcript (Method A/B/C/D — `01_FREE_TRANSCRIPT_GUIDE.md`)
   — paste kar do is chat mein, ya `evidence/` folder mein save kar do.
2. Channel ownership: ye channel aapka hai ya nahi? (Studio Clips option ke liye)
3. Voiceover preference: edge-tts (AI voice) ya apni awaz?

Transcript milte hi main:
- Pehle do completed missions ke **exact timestamps** likhunga
- Story ke slots fill karunga (mission names, moments)
- Editing timeline ko real timecodes se bharunga
- Har beat ko VERIFIED mark karunga (manual check ke baad)

**Tab tak har timestamp `TBC` rahega — aur ye jhoot na bolne ka tareeqa hai.**

# Free Tools — Verification Table

**Rule:** koi bhi tool use karne se pehle verify karo ke feature genuinely free hai.
Har tool ke liye neeche evidence diya gaya hai (verified 2026-11-16).

---

## Transcript tools

| Tool | Free? | Evidence | Limits |
|---|---|---|---|
| **YouTube "Show transcript"** | ✅ Free | YouTube player ka built-in feature, koi payment nahi | Stream end + VOD processing ke baad hi available |
| **youtube-transcript-api** | ✅ Free (MIT) | PyPI + GitHub (jdepoix/youtube-transcript-api). "No API key needed" | Captions hone chahiye; rate limit unofficial |
| **yt-dlp** | ✅ Free (Unlicense) | GitHub (187k+ stars). "100% free and open source, no subscriptions" | `--skip-download` use karo taake video download na ho |
| **youtubetotranscript.com** | ✅ Free | Website pe "100% free, no signup" | Rate limit ho sakta hai; bada transcript slow ho sakta hai |
| **tools.scoreroute.com** | ✅ Free | "No signup, no API key, no daily limit, 100% free" | CORS proxy; kabhi kabhi slow |

## Editing tools

| Tool | Free? | Evidence | Limits |
|---|---|---|---|
| **DaVinci Resolve** | ✅ Free | Blackmagic Design. "No watermark, no time limit, exports up to UHD 60fps". Studio ($295) alag product hai — free version mein core editing/color/audio/Fusion sab hai | Free version: 8-bit encode, no HW-accelerated H.264 (slow export), no noise reduction. Humare kaam ke liye kaafi hai |
| **CapCut desktop** | ✅ Free | ByteDance. "Desktop version exports without a watermark on the free tier" | Kuch AI features ke liye account sign-in; long-form ke liye limited |
| **FFmpeg** | ✅ Free (open source) | ffmpeg.org. Repo mein already use ho raha hai | CLI hai — learning curve |
| **Kdenlive / Shotcut** | ✅ Free (open source) | KDE / MLT projects | DaVinci/CapCut se kam polished |

## Recording / capture tools

| Tool | Free? | Evidence | Limits |
|---|---|---|---|
| **OBS Studio** | ✅ Free (GPLv2) | obsproject.com. "Completely free for all purposes, including commercial use" | YouTube ToS gray area (recording) — sirf specific windows, poora VOD kabhi nahi |

## Voiceover (TTS)

| Tool | Free? | Evidence | Limits |
|---|---|---|---|
| **edge-tts** | ✅ Free (MIT) | PyPI + GitHub (rany2/edge-tts). "Without needing Edge, Windows, or an API key" | Internet chahiye (Microsoft endpoint); rate limit ho sakta hai; Roman Hindi ke liye Devanagari text behtar hai |
| **Apni awaz** | ✅ Free | Phone/OBS se record karo | Sab se natural, lekin time lagta hai |

## Music / SFX

| Tool | Free? | Evidence | Limits |
|---|---|---|---|
| **YouTube Audio Library** | ✅ Free | YouTube Studio ke andar built-in | Har track ka license alag — attribution wale tracks check karo |
| **Repo SFX pack** | ✅ Free (local) | `../ref/skill/blocky-shorts/assets/sfx/` — 29 cues, already in repo | Sirf SFX, music nahi |

---

## ❌ REMOVED tools (paid — budget $0 ke against)

| Tool | Kyun removed |
|---|---|
| **Apify** (youtube-video-clipper) | $1.50/clip @1080p — paid. Budget $0 hai |
| **Gemini API** | Paid tier / API key required. Budget $0 hai |
| **VideoDB** | Credits-based ($20 free, phir paid). Max duration unverified |
| **ClipSDK** | $0.03/min + 3h clip limit — 18h VOD ke liye useless |
| **Descript** | 15h transcribe ceiling — 18h VOD exceed karta hai |
| **Opus / Vizard / Klap** | Free quota 30–60 min/month — 18h VOD ke liye useless |

**Inme se koi bhi tool is workflow mein use nahi hota. Koi paid trial nahi. Koi subscription nahi.**

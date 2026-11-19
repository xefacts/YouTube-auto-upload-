# FREE Transcript Guide — $0.00, 4 verified methods

**Source video:** `https://www.youtube.com/live/qSyo5d-dVzA` (videoId: `qSyo5d-dVzA`)

> ⚠️ **Timing:** stream abhi LIVE hai. Captions tabhi available honge jab stream **end** ho
> aur YouTube VOD process kar le (usually 30 min – 2 h). Agar abhi transcript nahi milta,
> to ye normal hai — stream end hone ke baad dobara try karo.

---

## Method A — YouTube player (sab se easy, $0)

1. Video kholo: https://www.youtube.com/live/qSyo5d-dVzA
2. Player ke neeche **"..."** (three dots) pe click karo
3. **"Show transcript"** select karo
4. Transcript panel khulega — har line pe timestamp hoga
5. Copy karo → is chat mein paste kar do (ya `.txt` file mein save karo)

**Free status:** ✅ YouTube ka built-in feature. Koi account, koi payment nahi.
**Limit:** transcript lamba ho sakta hai (18 h stream) — pehle 30–60 min ka hissa copy karna
kaafi hai, kyunki pehle do missions shuru mein honge.

---

## Method B — youtube-transcript-api (Python, $0)

```bash
pip install youtube-transcript-api
python scripts/get_transcript.py --video qSyo5d-dVzA --out evidence/transcript.json
```

Ya ek line mein:

```python
from youtube_transcript_api import YouTubeTranscriptApi
t = YouTubeTranscriptApi.get_transcript("qSyo5d-dVzA")
for line in t:
    print(f"[{line['start']:.0f}s] {line['text']}")
```

**Free status:** ✅ MIT license, open source, **no API key**, no payment.
**Source:** https://pypi.org/project/youtube-transcript-api · https://github.com/jdepoix/youtube-transcript-api
**Limit:** captions hone chahiye (stream end + processing ke baad). Auto-generated captions bhi milte hain.

---

## Method C — yt-dlp (CLI, $0)

```bash
# Sirf captions download karo — video DOWNLOAD NAHI HOTA
yt-dlp --skip-download --write-auto-subs --sub-langs en --sub-format vtt \
  -o "evidence/captions.%(ext)s" "https://www.youtube.com/live/qSyo5d-dVzA"
```

**Free status:** ✅ Unlicense, open source, GitHub pe 187k+ stars.
**Source:** https://github.com/yt-dlp/yt-dlp
**Note:** `--skip-download` flag zaroor use karo — ye video download nahi karta, sirf captions.
Ye humare "never download the entire livestream" rule ke andar hai.

---

## Method D — Free website ($0)

Browser mein koi bhi free transcript site kholo, video URL paste karo, transcript copy karo.
Examples (sab free, no signup):
- youtubetotranscript.com
- tools.scoreroute.com/tools/youtube-transcript-extractor

**Free status:** ✅ Free tier, no API key, no signup (verified 2026-11-16).
**Limit:** kuch sites pe rate limit hota hai; 18 h VOD ka transcript bada ho sakta hai —
pehle 1 ghante ka hissa kaafi hai.

---

## Transcript milne ke baad kya karna hai

1. Transcript ko `evidence/` folder mein save karo (`.txt` ya `.json`)
2. Is chat mein paste kar do (ya bata do ke file save ho gayi hai)
3. Main agent:
   - "mission complete" / "mission failed" / objective lines dhoondhunga
   - Pehle do **completed** missions ke exact timestamps likhunga
   - Story ke slots fill karunga
   - Editing timeline ko real timecodes se bharunga

## Kya dhoondhna hai transcript mein

| Search term | Kyun |
|---|---|
| "mission complete" / "mission passed" | Mission completion ka signal |
| "mission failed" / "wasted" | Fail points (story ke liye) |
| "objective" / "go to" / "deliver" | Mission objective |
| Speed ki reactions ("let's gooo", "no way") | Cinematic moments |
| Chat spam ("W", "L", "clip it") | Audience reaction (agar chat replay available ho) |

**Note:** Speed English mein bolta hai, isliye transcript English mein hoga. Story Roman Hindi
mein hogi (02_STORY_ROMAN_HINDI.md) — ye translation ka kaam main karunga.

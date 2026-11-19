# Captions (Roman Hindi) + Sound Design

## 1. Caption rules

| Rule | Value |
|---|---|
| Language | Roman Hindi (Latin script) |
| Case | UPPERCASE |
| Chars per line | ≤ 18, max 2 lines, max 7 words |
| Highlight | exactly one word per caption in brand yellow `#FFD24A` |
| Position | baseline at 81.5% frame height |
| Timing | cut ke 40 ms baad appear, next cut se 100 ms pehle gayab |
| Numbers | digits, never spelled out |
| Slot captions | slot khaali ho to caption bhi delete (guess mat bharo) |

## 2. Caption text (beat-by-beat, Roman Hindi)

| Beat | Caption | Highlight word |
|---|---|---|
| B01 | SPEED GTA 6 MEIN GHUS GAYA | GTA 6 |
| B02 | MISSION 1: {{MISSION_1_NAME}} | {{MISSION_1_NAME}} |
| B03 | HAR BAAR FAIL | FAIL |
| B04 | PHIR EK PAL AAYA | PAL |
| B05 | MISSION COMPLETE | COMPLETE |
| B06 | MISSION 2: {{MISSION_2_NAME}} | {{MISSION_2_NAME}} |
| B07 | SAB BIGAAD DIYA | BIGAAD |
| B08 | HAAR NAHI MAANI | HAAR |
| B09 | MISSION 2 COMPLETE | COMPLETE |
| B10 | DO MISSIONS. EK STREAM. | STREAM |
| B11 | MISSION 3 → | 3 |

## 3. Sound design

### Music
| Item | Detail |
|---|---|
| Source | YouTube Audio Library (YouTube Studio ke andar, free) |
| Type | Tense/cinematic bed, instrumental |
| Level | −26 dB narration ke neeche |
| Ducking | Fail moments pe bed out (200 ms), clutch pe wapas in |
| Note | Har track ka license check karo — kuch tracks attribution maangte hain |

### SFX (repo ke existing skill pack se — sab free, local files)

| Beat | SFX file | Timing | Gain | Note |
|---|---|---|---|---|
| B01 | `impact.wav` | 0 ms | −3 dB | Black → frame cut pe hit |
| B02 | `whoosh.wav` | 0 ms | −9 dB | Push-in ke saath |
| B03 | `tick.wav` ×3 | 0/400/800 ms | −12 dB | 3 fail cuts ke saath match |
| B04 | `riser.wav` | 0 ms | −6 dB | Peak cut pe hona chahiye |
| B05 | `ding.wav` | +4 ms | −2 dB | Banner land hone pe |
| B05 | `sparkle.wav` | +90 ms | −10 dB | Tail only |
| B06 | `whoosh.wav` | 0 ms | −9 dB | Mission 1 jaisa (series feel) |
| B07 | `grr.wav` | +80 ms | −12 dB | Ek instance only |
| B08 | `riser.wav` | 0 ms | −6 dB | Peak cut pe |
| B09 | `ding.wav` | +4 ms | −2 dB | Banner pe |
| B09 | `sparkle.wav` | +90 ms | −10 dB | Tail |
| B10 | `stamp.wav` | +60 ms | −5 dB | "Do missions" pe |
| B11 | `swish.wav` | 0 ms | −8 dB | End card slide |

**SFX location:** `../ref/skill/blocky-shorts/assets/sfx/` (29 cues, already in repo, $0)

### Voiceover
| Item | Detail |
|---|---|
| Tool | edge-tts (free, MIT, no API key) |
| Command | `edge-tts --voice hi-IN-NeerjaNeural --text "..." --write-media vo.mp3` |
| Roman Hindi note | TTS ke liye Devanagari text use karo; captions Roman Hindi mein rakho |
| Alternative | Apni awaz record karo (OBS/phone) — sab se natural |

## 4. Mix checklist

- [ ] Narration −14 LUFS integrated
- [ ] Music bed narration ke neeche, kabhi narration ko cover na kare
- [ ] SFX peaks narration se takrayein nahi (ducking check)
- [ ] Har caption timing narration se match karta hai
- [ ] End card pe music tail nahi (clean cut)

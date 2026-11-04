#!/usr/bin/env python3
"""Natural short-form narration from a local Apache-2.0 Kokoro ONNX model.
No sample, transcript, or speaker identity taken from user reference videos.
Model/voices are reconstructed from npm package assets by setup_v3_voice.py.
"""
from pathlib import Path
import hashlib,wave,json,math
import numpy as np
from scipy.signal import resample_poly
from kokoro_onnx import Kokoro
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;CACHE=HERE/'render_cache';CACHE.mkdir(exist_ok=True)
MODEL=ROOT/'work/tts_models/kokoro-q8.onnx';VOICES=ROOT/'work/tts_models/voices-v1.0.bin'
SHA='fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478'
LINES=[
 'Why do the Florida Keys curve away from the mainland?',
 'Follow the coastline south, and the land keeps going.',
 'Not as one peninsula, but as a sweeping arc of islands.',
 'But the upper Keys are ancient coral reefs turned to stone.',
 'Farther west, limestone and sand shaped a different kind of key.',
 "Long before today's shoreline, warmer seas covered this shallow platform.",
 'When the ice age lowered the water, old reefs were exposed.',
 'Then the sea rose again, leaving a necklace of low islands.',
 "See the pale turquoise around them? That's the shallow shelf beneath the water.",
 'The Overseas Highway follows part of this chain.',
 "Bridges link many islands, but the road doesn't reach every one.",
 'Key West is famous, yet the island chain continues beyond it.',
 "Look to one side and you'll find Florida Bay.",
 'On the other side, deeper water opens toward the Straits of Florida.',
 "The curve wasn't carved by a single break in the land.",
 'It took reefs, sediment, and seas that moved up and down.',
 'But on the map, the islands tell a much older story.',
]
VOICE=CACHE/'v3_kokoro_voice.wav';TIMES=CACHE/'v3_voice_timing.json';RATE=48000

def generate(force=False):
 if not force and VOICE.exists() and TIMES.exists():
  data=json.loads(TIMES.read_text())
  if [x['text'] for x in data]==LINES:return data
 assert MODEL.exists() and VOICES.exists(),'Run setup_v3_voice.py to assemble the offline model'
 with MODEL.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==SHA
 k=Kokoro(str(MODEL),str(VOICES))
 if len(k.sess.get_inputs()[1].shape)==2:
  old=k._style_for;k._style_for=lambda v,n:old(v,n)[None,:]
 clips=[];rows=[];position=.28
 for i,text in enumerate(LINES):
  samples,rate=k.create(text,voice='am_michael',speed=1.14,lang='en-us',sentence_pause=.10,clause_pause=.07)
  samples=resample_poly(samples.astype(np.float32),RATE,rate)
  # Preserve phrasing; 18 ms edge fades prevent clicks, no pitch alteration.
  f=min(int(.018*RATE),len(samples)//6)
  samples[:f]*=np.linspace(0,1,f);samples[-f:]*=np.linspace(1,0,f)
  start=position;end=start+len(samples)/RATE
  rows.append(dict(index=i,text=text,start=round(start,5),end=round(end,5)))
  clips.append(samples)
  position=end+(.18 if i not in (4,9,13,17) else .35)
  print(i,round(start,2),round(end,2),text,flush=True)
 n=math.ceil((position+.58)*RATE);out=np.zeros(n,np.float32)
 for row,a in zip(rows,clips):
  at=round(row['start']*RATE);out[at:at+len(a)]+=a
 with wave.open(str(VOICE),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE)
  w.writeframes(np.int16(np.clip(out,-.99,.99)*32767).tobytes())
 TIMES.write_text(json.dumps(rows,indent=2)+'\n')
 print('duration',len(out)/RATE,'words',sum(len(x.split()) for x in LINES),flush=True)
 return rows
if __name__=='__main__':generate()

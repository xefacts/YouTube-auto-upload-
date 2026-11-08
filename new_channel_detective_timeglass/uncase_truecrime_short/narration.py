#!/usr/bin/env python3
"""Offline, original Kokoro narration; no cloning, credentials, or paid API."""
from pathlib import Path
import json,hashlib,wave
import numpy as np
from scipy.signal import resample_poly
from kokoro_onnx import Kokoro
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent/'assets';OUT.mkdir(exist_ok=True)
MODEL=ROOT/'work/tts_models/kokoro-q8.onnx';VOICES=ROOT/'work/tts_models/voices-v1.0.bin'
EXPECTED='fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478'
BLOCKS=[
'August 21, 1911. The Louvre shut. By morning, the Mona Lisa was gone—and no one knew when.',
'The blank wall raised no alarm: paintings came down for photos and cleaning. So the absence looked routine.',
'Then the clue: Peruggia had worked inside, fitting protective glass. Investigators questioned him, but found no link. The trail went cold.',
'Two years later, he wrote Florence dealer Alfredo Geri, offering the painting. Geri called Uffizi director Giovanni Poggi. They checked it—and alerted police.',
'Your turn: if this was patriotism, why offer it for sale? Peruggia said he wanted to return it to Italy. The offer left motive in doubt.',
'In 1914, he was convicted and sentenced to one year and fifteen days. The Mona Lisa returned to the Louvre.',
'Final twist: the theft helped make a famous painting a global icon. Motive? Peruggia claimed patriotism; the sale suggested another possibility. What do you think—belief, profit, or both?'
]
def main():
 assert MODEL.exists() and VOICES.exists(),'Run train2_geography_study/setup_v3_voice.py first'
 h=hashlib.sha256(MODEL.read_bytes()).hexdigest();assert h==EXPECTED,h
 k=Kokoro(str(MODEL),str(VOICES))
 if len(k.sess.get_inputs()[1].shape)==2:
  old=k._style_for;k._style_for=lambda v,n:old(v,n)[None,:]
 clips=[];rows=[];rate_out=48000;pos=.28
 for i,text in enumerate(BLOCKS):
  # Measured, lightly dramatic pacing: pause before the midpoint viewer question and verdict.
  speed=(1.04 if i in (0,4,6) else 1.09)
  a,rate=k.create(text,voice='am_michael',speed=speed,lang='en-us',sentence_pause=.19,clause_pause=.12)
  a=resample_poly(a.astype(np.float32),rate_out,rate)
  fade=min(int(.02*rate_out),len(a)//8);a[:fade]*=np.linspace(0,1,fade);a[-fade:]*=np.linspace(1,0,fade)
  start=pos;end=start+len(a)/rate_out
  rows.append({'index':i,'text':text,'start':round(start,4),'end':round(end,4),'words':len(text.split())})
  clips.append(a);pos=end+(.29 if i in (0,2,3,4,5) else .36)
 n=int((pos+.8)*rate_out);audio=np.zeros(n,np.float32)
 for row,a in zip(rows,clips):
  at=round(row['start']*rate_out);audio[at:at+len(a)]+=a
 audio=np.tanh(audio*1.05)*.92
 with wave.open(str(OUT/'narration.wav'),'wb') as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate_out);f.writeframes(np.int16(audio*32767).tobytes())
 (OUT/'narration_timing.json').write_text(json.dumps(rows,indent=2)+'\n')
 print('words',sum(r['words'] for r in rows),'voice seconds',round(pos,2),'blocks',len(rows))
 for r in rows:print(r['start'],r['end'],r['text'])
if __name__=='__main__':main()

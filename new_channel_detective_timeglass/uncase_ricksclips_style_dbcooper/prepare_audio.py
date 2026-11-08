#!/usr/bin/env python3
"""Assemble the selected original TTS performance, sync map, phrase captions and subtle procedural bed."""
from pathlib import Path
import math,re,subprocess,wave,json
import numpy as np
from imageio_ffmpeg import get_ffmpeg_exe
ROOT=Path(__file__).resolve().parent;A=ROOT/'assets';FF=get_ffmpeg_exe();SR=48000;GAP=.08
CHUNKS=[
 ('vo_01_hook.mp3','One hijacker vanished with two hundred thousand dollars. Years later, only fifty-eight hundred came back.',5),
 ('vo_02_name.mp3','On November twenty-fourth, nineteen seventy-one, a man using the name Dan Cooper boarded Northwest Orient Flight Three-O-Five. The press later called him D.B.',0),
 ('vo_03_demands.mp3','He claimed his briefcase held a bomb and demanded four parachutes and two hundred thousand dollars.',1),
 ('vo_04_seattle.mp3','In Seattle, he released all thirty-six passengers, kept the crew aboard, and ordered the plane south.',2),
 ('vo_05_jump.mp3','Somewhere between Seattle and Reno, Cooper lowered the rear stairs and jumped into a stormy night.',3),
 ('vo_06_search.mp3','The FBI considered more than eight hundred suspects—but never proved who he was.',4),
 ('vo_07_money.mp3','Then, in nineteen eighty, a boy found fifty-eight hundred dollars from the ransom. Serial numbers matched. But the money did not show where Cooper landed, or whether he survived.',5),
 ('vo_08_close.mp3','After forty-five years, the FBI redirected its resources. The identity is still unknown. Did Cooper die in the jump—or escape? The evidence cannot settle it.',6),
]
def decode(path):
 r=subprocess.run([FF,'-hide_banner','-loglevel','error','-i',str(path),'-f','s16le','-acodec','pcm_s16le','-ac','1','-ar',str(SR),'pipe:1'],capture_output=True,check=True)
 return np.frombuffer(r.stdout,dtype='<i2').astype(np.float32)/32768

def trim(x):
 win=int(.01*SR);q=x[:len(x)//win*win].reshape(-1,win);rms=np.sqrt(np.mean(q*q,axis=1)+1e-12);a=np.where(rms>.008)[0]
 if not len(a):return x
 return x[max(0,int(a[0]*win-.025*SR)):min(len(x),int((a[-1]+1)*win+.11*SR))]

def weight(w):return max(1,len(re.findall(r'[aeiouy]+',re.sub(r'[^A-Za-z]','',w).lower())))
def groups(text):
 out=[];cur=[]
 for w in text.split():
  cur.append(w)
  if len(cur)>=1 or re.search(r'[.!?,;—]$',w):out.append(' '.join(cur));cur=[]
 if cur:out.append(' '.join(cur))
 return out

def ts(v):
 ms=max(0,round(v*1000));return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'

def main():
 pieces=[];timeline=[];caps=[];pos=0
 for i,(file,text,scene) in enumerate(CHUNKS):
  x=trim(decode(A/file));dur=len(x)/SR;timeline.append({'clip':i,'text':text,'scene':scene,'start':round(pos,4),'end':round(pos+dur,4),'duration':round(dur,4)});pieces.append(x);pos+=dur
  gs=groups(text);ws=[sum(weight(w) for w in g.split()) for g in gs];span=max(.1,dur-.12);cur=pos-dur+.06
  for g,w in zip(gs,ws):
   d=span*w/(sum(ws) or 1);caps.append({'start':round(cur,4),'end':round(cur+d,4),'text':g});cur+=d
  if i<len(CHUNKS)-1:pieces.append(np.zeros(int(GAP*SR),np.float32));pos+=GAP
 voice=np.concatenate(pieces);n=len(voice);
 with wave.open(str(ROOT/'voice_only.wav'),'wb') as vf:vf.setnchannels(1);vf.setsampwidth(2);vf.setframerate(SR);vf.writeframes(np.int16(np.clip(voice,-1,1)*32767).tobytes())
 t=np.arange(n)/SR;rng=np.random.default_rng(1971);noise=rng.normal(0,1,n).astype(np.float32);low=np.empty_like(noise);low[0]=noise[0]
 for k in range(1,n):low[k]=.992*low[k-1]+.008*noise[k]
 bed=.007*np.sin(2*np.pi*47*t)+.003*np.sin(2*np.pi*71*t+.2*np.sin(t*.12))+(low-.15*np.roll(low,2500))*.0035
 for row in timeline[1:]:
  start=int(row['start']*SR);L=int(.42*SR);k=np.arange(L);env=np.exp(-k/(.12*SR));ph=2*np.pi*np.cumsum(58-16*k/L)/SR;end=min(n,start+L);bed[start:end]+=.018*np.sin(ph[:end-start])*env[:end-start]
 peak=float(np.max(np.abs(voice))) or 1;voice*=min(1,.82/peak);mix=np.clip(voice+bed,-.92,.92);st=np.stack([mix,mix*.985],axis=1)
 with wave.open(str(ROOT/'master_mix.wav'),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes(np.int16(st*32767).tobytes())
 (ROOT/'audio_timeline.json').write_text(json.dumps({'duration':round(n/SR,4),'sample_rate':SR,'clips':timeline,'captions':caps},indent=2)+'\n')
 (ROOT/'CAPTIONS_APPROX.srt').write_text('\n'.join(y for i,c in enumerate(caps,1) for y in [str(i),f"{ts(c['start'])} --> {ts(c['end'])}",c['text'],'']),encoding='utf-8')
 print('audio',round(n/SR,3),'s; chunks',len(timeline),'caption beats',len(caps))
if __name__=='__main__':main()

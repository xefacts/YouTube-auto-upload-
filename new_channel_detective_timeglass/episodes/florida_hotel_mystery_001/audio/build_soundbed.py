"""Generate a draft original non-melodic percussion/breath-like air bed.
For the unverified fictional Florida hotel mystery VO, not the Villisca case.
No sampled music, melody, weapon or purported historical field recording.
"""
from pathlib import Path
import subprocess
import numpy as np
import soundfile as sf
import imageio_ffmpeg
SR=48000
DUR=38.0
rng=np.random.default_rng(1912)
n=int(SR*DUR)
out=np.zeros((n,2),dtype=np.float32)

def lay(t,mono,amp=1,pan=0):
    start=int(t*SR)
    if start>=n:return
    mono=np.asarray(mono,dtype=np.float32)[:n-start]*amp
    a=np.sqrt((1-pan)/2);b=np.sqrt((1+pan)/2)
    out[start:start+len(mono),0]+=mono*a
    out[start:start+len(mono),1]+=mono*b

def smooth_noise(length,window):
    z=rng.standard_normal(length)
    return np.convolve(z,np.ones(window)/window,mode='same').astype(np.float32)

# Wide quiet air, rhythm-free: implies atmosphere rather than musical pitch.
base=rng.standard_normal(n).astype(np.float32)
for ch,shift in enumerate((0,853)):
    x=np.roll(base,shift)
    low=np.convolve(x,np.ones(140)/140,mode='same')
    env=np.linspace(.55,1,n,dtype=np.float32)
    out[:,ch]+=(low*env*0.002)

# Hand-drum-style hits built from decaying broadband noise, no pitched instruments.
for i,t in enumerate(np.arange(.35,DUR-.5,.75)):
    length=int(SR*.23); tt=np.arange(length)/SR
    hit=rng.standard_normal(length).astype(np.float32)
    hit=np.convolve(hit,np.ones(19)/19,mode='same')
    env=np.exp(-tt*25)*np.clip(tt*350,0,1)
    strength=.08 if t<9.5 else (.14 if t<20 else .18)
    if i%4==0:strength*=1.35
    lay(t,hit*env,strength,pan=(-.22 if i%2 else .22))
    if i%4==2 and t>9:
        tick=rng.standard_normal(int(SR*.055)).astype(np.float32)
        tick*=np.exp(-np.arange(len(tick))/SR*100)
        lay(t+.38,tick,.003,pan=.45)

# Breathy tension swells: noise envelopes, not fake victim vocalization.
for t,l,amp in [(8.7,1.2,.012),(17.1,1.0,.010),(25.5,1.3,.014),(32.3,2.5,.018)]:
    L=int(SR*l); tt=np.linspace(0,1,L)
    air=rng.standard_normal(L).astype(np.float32)
    air=np.convolve(air,np.ones(16)/16,mode='same')
    env=np.sin(np.pi*tt)**2
    lay(t,air*env,amp,-.35)

# Short cinematic impacts for turns, not gunshots and not historical audio.
for t,amp in [(10.0,.19),(18.2,.12),(23.3,.13),(32.2,.16)]:
    L=int(SR*.34);tt=np.arange(L)/SR
    z=rng.standard_normal(L).astype(np.float32)
    z=np.convolve(z,np.ones(10)/10,mode='same')
    env=np.exp(-tt*15)*np.minimum(1,tt*750)
    lay(t,z*env,amp,.0)

# End with a dry visual-clues pulse; no melodic resolution.
for t in (34.0,35.5,37.0):
    L=int(SR*.26);tt=np.arange(L)/SR
    z=np.convolve(rng.standard_normal(L),np.ones(25)/25,mode='same')
    lay(t,z*np.exp(-tt*16),.22,0)

out=np.tanh(out*2.5)
out[:int(.3*SR)]*=np.linspace(0,1,int(.3*SR))[:,None]
out[-int(.35*SR):]*=np.linspace(1,0,int(.35*SR))[:,None]
root=Path(__file__).parent
wav=root/'percussion_air_draft.wav'
sf.write(wav,out,SR,subtype='PCM_16')
ff=imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-i',str(wav),'-c:a','libmp3lame','-b:a','192k',str(root/'percussion_air_draft.mp3')],check=True)
wav.unlink(missing_ok=True)
print('peak',np.max(np.abs(out)),'RMS',np.sqrt(np.mean(out*out)),'duration',DUR)

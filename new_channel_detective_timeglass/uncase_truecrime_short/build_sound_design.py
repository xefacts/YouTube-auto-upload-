#!/usr/bin/env python3
"""Procedural original suspense bed and restrained transition impacts, no samples."""
from pathlib import Path
import numpy as np,wave
A=Path(__file__).resolve().parent/'assets';A.mkdir(exist_ok=True)
rate=48000;duration=68.0;n=int(rate*duration);t=np.arange(n)/rate
rng=np.random.default_rng(1911)
# Low, quiet tonal atmosphere; slowly shifting harmonic bed, not a borrowed music track.
drone=(.13*np.sin(2*np.pi*47*t)+.075*np.sin(2*np.pi*71*t+.4*np.sin(t*.09))+ .045*np.sin(2*np.pi*94*t))
# Gentle band-limitedish air: smooth random control curve and highpassed grain kept very low.
noise=rng.normal(0,1,n).astype(np.float32)
# one-pole highpass then low amplitude; avoid harsh static.
for i in range(1,n):noise[i]=.965*noise[i-1]+.035*noise[i]
air=(noise-np.mean(noise))*.018
mix=drone+air
# Sparse soft documentary impacts on key cuts: fast attack + long dark decay, not a heartbeat loop.
for at,amp in [(0,.10),(8.1,.06),(15.5,.07),(24.6,.11),(35.3,.09),(44.6,.08),(52.8,.10),(61.7,.07)]:
 k=np.arange(int(rate*1.1));env=np.exp(-k/(rate*.29));freq=42+7*np.exp(-k/(rate*.14))
 phase=2*np.pi*np.cumsum(freq)/rate
 thump=amp*np.sin(phase)*env
 start=int(at*rate);mix[start:start+len(k)]+=thump
# rise tension around midpoint question without masking speech.
for at in (34.4,):
 length=int(rate*1.15);k=np.arange(length);env=np.sin(np.linspace(0,np.pi/2,length))**2
 mix[int(at*rate):int(at*rate)+length]+=.06*env*np.sin(2*np.pi*38*k/rate)
# stereo slight decorrelation, normalized peak under -15 dBFS before mix.
st=np.stack([mix,np.roll(mix,173)*.94],axis=1);st=np.clip(st,-.18,.18)
with wave.open(str(A/'sound_design.wav'),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(rate);f.writeframes(np.int16(st*32767).tobytes())
print('Wrote original stereo bed',duration,'s; peak',float(np.max(np.abs(st))))

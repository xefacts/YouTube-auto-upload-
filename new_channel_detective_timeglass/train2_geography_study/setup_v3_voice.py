#!/usr/bin/env python3
"""Reconstruct Kokoro q8 from npm release; verify weights before synthesis.

These npm archives are redistributed by independent packages. The ONNX model
and voice assets originate from Apache-2.0 Kokoro. License and notices are
packaged with the V3 editor kit; no reference voice has been used or cloned.
"""
from pathlib import Path
import hashlib,io,tarfile,urllib.request
import numpy as np
ROOT=Path(__file__).resolve().parents[2];CACHE=ROOT/'work/tts_models';CACHE.mkdir(parents=True,exist_ok=True)
MODEL_URL='https://registry.npmjs.org/kokoro-q8-shards/-/kokoro-q8-shards-1.0.0.tgz'
VOICES_URL='https://registry.npmjs.org/kokoro-local-runtime/-/kokoro-local-runtime-0.1.0.tgz'
SHA='fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478'

def download(url,name):
 dest=CACHE/name
 if dest.exists() and dest.stat().st_size>10000:return dest
 tmp=dest.with_suffix('.download');urllib.request.urlretrieve(url,tmp);tmp.replace(dest)
 return dest

def main():
 weights=download(MODEL_URL,'kokoro-q8-shards-1.0.0.tgz')
 voice=download(VOICES_URL,'kokoro-local-runtime-0.1.0.tgz')
 model=CACHE/'kokoro-q8.onnx'
 with tarfile.open(weights) as tg,model.open('wb') as out:
  for i in range(6):
   src=tg.extractfile('package/kokoro-q8.part%d.bin'%i)
   assert src is not None
   while True:
    b=src.read(1048576)
    if not b:break
    out.write(b)
 with model.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
 if actual!=SHA:
  model.unlink();raise ValueError('model checksum mismatch: '+actual)
 with tarfile.open(voice) as tg:
  tensors={}
  for name in ('am_michael','am_puck','af_heart'):
   src=tg.extractfile('package/voices/'+name+'.bin')
   assert src is not None
   tensors[name]=np.frombuffer(src.read(),dtype='<f4').reshape(510,256)
  with (CACHE/'voices-v1.0.bin').open('wb') as f:np.savez(f,**tensors)
 print('Verified ONNX',model.stat().st_size,'bytes; 3 Apache-2.0 voice tensors')
if __name__=='__main__':main()

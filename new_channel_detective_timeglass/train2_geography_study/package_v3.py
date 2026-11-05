#!/usr/bin/env python3
"""Bundle the complete owner-only V3 editing kit, excluding copyrighted refs.
Final MP4 and q8 ONNX model are intentionally delivered as separate files.
"""
from pathlib import Path
import hashlib,zipfile
ROOT=Path(__file__).resolve().parents[2]
ST=Path(__file__).resolve().parent
OUT=ROOT/'work/train2_study/FLORIDA_KEYS_V3_EDITABLE_SOURCE_OWNER_ONLY.zip'
OUT.parent.mkdir(parents=True,exist_ok=True)
files=[]
for filename in ('README.md','REFERENCE_FORENSICS_V3.md','V3_PRODUCTION_NOTES.md','V3_QA_REPORT.md',
                 'analyze_refs.py','build_flat_atlas.py','setup_v3_voice.py','generate_v3_narration.py',
                 'v3_maps.py','render_geography_v3.py','package_v3.py','requirements-v3.txt'):
 files.append(ST/filename)
for filename in ('v3_world_relief_4096.png','v3_wide_base.png','v3_region_glow_rgba.png',
                 'florida_gulf_relief_backplate.png','florida_keys_macro_relief.png',
                 'keys_reef_cross_section.png','keys_overseas_bridge_aerial.png',
                 'globe_nasa/earth-day-2048.jpg','globe_nasa/earth-clouds-2048.jpg',
                 'v2_ambient/ambience_waves_cc0.ogg'):
 files.append(ST/'assets'/filename)
files.extend(sorted((ST/'assets/v3_licenses').glob('*.txt')))
files.extend(sorted((ST.parent/'assets/fonts').glob('*')))
for name in ('v3_kokoro_voice.wav','v3_voice_surf_mix.wav','v3_voice_timing.json'):
 files.append(ST/'render_cache'/name)
files.extend((ROOT/'work/relief/index.json',ROOT/'work/relief/z0-4.pack',ROOT/'work/tts_models/voices-v1.0.bin'))
files.extend(sorted((ROOT/'work/train2_study/reference_forensics').glob('*every_frame.csv')))
files.append(ROOT/'work/train2_study/reference_forensics/summary.json')
assert len(files)==len(set(files)) and all(x.is_file() for x in files)
start='START_HERE.txt'
message='''FLORIDA KEYS V3 — ORIGINAL FLAT-ATLAS EDITABLE KIT\nPRIVATE REVIEW / NOT PUBLISHED\n\nRead new_channel_detective_timeglass/train2_geography_study/V3_PRODUCTION_NOTES.md.\nThis archive includes code, layered map plates, relief inputs, fonts/licenses,\nvoice WAV and mix WAV, beat timings, and 9 per-frame analysis CSVs. The\nfinished 62.90-second MP4 and verified Apache-2.0 q8 ONNX voice model are\nseparate owner-only files. Source refs are not embedded in this archive.\nRun from the extracted root with requirements-v3.txt installed.\n'''
manifest=[]
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 z.writestr(start,message)
 for f in files:
  rel=f.relative_to(ROOT).as_posix()
  manifest.append(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+rel)
  z.write(f,rel)
 z.writestr('SHA256SUMS.txt','\n'.join(manifest)+'\n')
print(OUT,OUT.stat().st_size,'bytes',len(files),'files')
assert OUT.stat().st_size<100*1024*1024

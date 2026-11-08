#!/usr/bin/env python3
"""Build one portable editing/source ZIP (excluding large ONNX model weights)."""
from pathlib import Path
import hashlib,zipfile
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
files=[]
files.extend(HERE/n for n in ['README.md','PRODUCTION_NOTES.md','QA_REPORT.md','SCRIPT_AND_SOURCES.md','YOUTUBE_DESCRIPTION.txt','CAPTIONS_APPROX_WORD_TIMED.srt','render_short.py','narration.py','build_sound_design.py','package_source_kit.py','UNCASE_MONA_LISA_THEFT_PRIVATE_REVIEW_1080x1920.mp4'])
files.extend(sorted((HERE/'assets').glob('*')))
files.extend([ROOT/'tooling/truecrime_creator/README.md',ROOT/'tooling/truecrime_creator/topic_finder.py',ROOT/'tooling/truecrime_creator/topic_candidates.csv'])
files.extend(sorted((ROOT/'tooling/truecrime_creator/skills').glob('*.md')))
files.extend([ROOT/'tooling/creative/README.md',ROOT/'tooling/creative/video-requirements.txt',ROOT/'tooling/creative/agent-requirements.txt',ROOT/'tooling/creative/package.json',ROOT/'tooling/creative/package-lock.json'])
files.append(ROOT/'new_channel_detective_timeglass/train2_geography_study/setup_v3_voice.py')
files.extend(sorted((ROOT/'new_channel_detective_timeglass/train2_geography_study/assets/v3_licenses').glob('*.txt')))
fonts=ROOT/'new_channel_detective_timeglass/assets/fonts'
files.extend([fonts/'Anton-Regular.ttf',fonts/'DMSans.ttf',fonts/'OFL-Anton.txt',fonts/'OFL-DMSans.txt'])
files=[p for p in files if p.is_file()]
assert len(files)>25 and all(p.stat().st_size>0 for p in files)
out=HERE/'UNCASE_MONA_LISA_EDITABLE_SOURCE_KIT.zip';rows=[]
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
 for p in files:
  rel=p.relative_to(ROOT).as_posix();z.write(p,rel);rows.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+rel)
 z.writestr('SHA256SUMS.txt','\n'.join(rows)+'\n')
print(out,out.stat().st_size,'bytes',len(files)+1,'entries')

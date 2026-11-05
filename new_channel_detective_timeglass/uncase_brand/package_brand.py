#!/usr/bin/env python3
from pathlib import Path
import zipfile,hashlib
R=Path(__file__).resolve().parent
ROOT=R.parents[1]
F=ROOT/'new_channel_detective_timeglass/assets/fonts'
files=['README.md','BRAND_GUIDELINES.md','CHANNEL_DESCRIPTION_COPY.txt','CHANNEL_TAGS_COPY.txt','DELIVERY.md','build_brand.py','PROFILE_UPLOAD_800x800.png','PROFILE_MASTER_1600.png','PROFILE_CIRCLE_98px_PREVIEW.png','BANNER_UPLOAD_2560x1440.jpg','BANNER_MASTER_5120x2880_RESAMPLED.jpg','BANNER_MOBILE_SAFE_PREVIEW.png','BANNER_DESKTOP_STRIP_PREVIEW.jpg','00_BRAND_OVERVIEW.png','art/banner_backplate.png']
paths=[R/n for n in files]+[F/'Anton-Regular.ttf',F/'DMSans.ttf',F/'OFL-Anton.txt',F/'OFL-DMSans.txt']
assert all(p.is_file() for p in paths)
out=R/'UNCASE_PRIVATE_TRUE_CRIME_BRAND_KIT.zip';rows=[]
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for p in paths:
  rel=p.relative_to(ROOT).as_posix();z.write(p,rel);rows.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+rel)
 z.writestr('SHA256SUMS.txt','\n'.join(rows)+'\n')
print(out,out.stat().st_size,len(paths)+1)

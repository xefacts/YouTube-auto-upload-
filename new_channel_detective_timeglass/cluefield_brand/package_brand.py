from pathlib import Path
import zipfile,hashlib
r=Path(__file__).resolve().parent
include=['README.md','BRAND_GUIDELINES.md','CHANNEL_DESCRIPTION_COPY.txt','CHANNEL_TAGS_COPY.txt','DELIVERY.md','build_brand.py','PROFILE_UPLOAD_800x800.png','PROFILE_MASTER_1600.png','PROFILE_CIRCLE_98px_PREVIEW.png','BANNER_UPLOAD_2560x1440.jpg','BANNER_MASTER_5120x2880_RESAMPLED.jpg','BANNER_MOBILE_SAFE_PREVIEW.png','BANNER_DESKTOP_STRIP_PREVIEW.jpg','00_BRAND_OVERVIEW.png','art/banner_backplate.png','art/profile_portrait.png']
out=r/'CLUEFIELD_PRIVATE_BRAND_REVIEW_KIT.zip'; sums=[]
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for name in include:
  p=r/name;sums.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+name);z.write(p,name)
 z.writestr('SHA256SUMS.txt','\n'.join(sums)+'\n')
print(out,out.stat().st_size,len(include)+1)

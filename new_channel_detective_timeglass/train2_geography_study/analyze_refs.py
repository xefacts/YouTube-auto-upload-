#!/usr/bin/env python3
"""Every-frame *measurement* of user-owned reference clips; never reuses their frames.
Outputs CSV and contact sheets to ignored work/. Measurements are heuristics,
not a claim to have recovered proprietary editing files or exact layer transforms.
"""
from pathlib import Path
import glob,cv2,numpy as np,csv,os,json,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
REF=ROOT/'google_drive';OUT=ROOT/'work/train2_study/reference_forensics';OUT.mkdir(parents=True,exist_ok=True)
files=sorted(REF.glob('*.mp4'))
assert len(files)==9,(len(files),'Need all nine originals')
summary=[]
for f in files:
 cap=cv2.VideoCapture(str(f));fps=cap.get(cv2.CAP_PROP_FPS);n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));w=int(cap.get(3));h=int(cap.get(4))
 name=''.join(c if c.isalnum() else '_' for c in f.name[:24]);csvpath=OUT/(name+'_every_frame.csv');rows=[]
 prev=None;prev_gray=None;last_analysis=None;stills=[];strong=[]
 for idx in range(n):
  ok,bgr=cap.read();
  if not ok:break
  small=cv2.resize(bgr,(144,256),interpolation=cv2.INTER_AREA)
  gray=cv2.cvtColor(small,cv2.COLOR_BGR2GRAY)
  hsv=cv2.cvtColor(small,cv2.COLOR_BGR2HSV)
  # Black caption band and white gutter are measured separately; camera fit
  # excludes the bottom 22% to reduce subtitle/GUI text false tracks.
  crop=gray[:200]
  shiftx=shifty=scale=confidence=0.
  if last_analysis is not None and idx%3==0:
   pts=cv2.goodFeaturesToTrack(last_analysis,maxCorners=110,qualityLevel=.012,minDistance=8)
   if pts is not None and len(pts)>8:
    p2,status,_=cv2.calcOpticalFlowPyrLK(last_analysis,crop,pts,None,winSize=(17,17),maxLevel=3)
    if p2 is not None and np.count_nonzero(status)>=7:
     A,mask=cv2.estimateAffinePartial2D(pts[status.ravel()==1],p2[status.ravel()==1],method=cv2.RANSAC,ransacReprojThreshold=2.6)
     if A is not None and mask is not None and mask.sum()>=7:
      shiftx=float(A[0,2])/144*576/3;shifty=float(A[1,2])/256*1024/3
      scale=float(np.sqrt(A[0,0]**2+A[0,1]**2)-1)/3
      confidence=float(mask.mean())
   last_analysis=crop.copy()
  elif last_analysis is None:last_analysis=crop.copy()
  # estimated frame change, color palette and white caption activity (not OCR)
  if prev is not None:
   diff=cv2.absdiff(small,prev);delta=float(np.mean(diff))
   hist1=cv2.calcHist([small],[0,1],None,[16,16],[0,256,0,256]);hist2=cv2.calcHist([prev],[0,1],None,[16,16],[0,256,0,256]);hcor=float(cv2.compareHist(hist1,hist2,cv2.HISTCMP_CORREL))
   edge1=cv2.Canny(gray,60,145);edge0=cv2.Canny(prev_gray,60,145)
   edelta=float(np.mean(edge1!=edge0))
   # Hard cuts or large jumps: threshold intentionally conservative; zoom whip
   # transitions can be counted as a visual reset rather than an edit cut.
   cut=int((delta>27 and hcor<.67) or (delta>38 and edelta>.21))
   if cut and (not strong or idx-strong[-1]>round(fps*.23)):strong.append(idx)
  else:delta=hcor=edelta=cut=0
  caption=float(((hsv[192:230,20:124,2]>165)&(hsv[192:230,20:124,1]<70)).mean())
  rows.append([idx,round(idx/fps,3),round(delta,2),round(hcor,3),round(edelta,3),cut,
               round(shiftx,3),round(shifty,3),round(scale,6),round(confidence,2),
               round(float(hsv[:,:,1].mean()),1),round(caption,3)])
  if idx%max(1,round(2*fps))==round(.5*fps):
   im=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)).resize((180,320),Image.Resampling.LANCZOS)
   stills.append((idx/fps,im))
  prev=small;prev_gray=gray
 cap.release()
 with csvpath.open('w',newline='') as out:
  wr=csv.writer(out);wr.writerow(['frame','seconds','rgb_abs_delta','blue_green_hist_corr','edge_churn','cut_candidate','camera_dx_px','camera_dy_px','camera_scale_delta','motion_inliers','mean_saturation','subtitle_white_fraction']);wr.writerows(rows)
 sheet=Image.new('RGB',(6*180,math.ceil(len(stills)/6)*348),(7,23,32));d=ImageDraw.Draw(sheet)
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
 for i,(t,im) in enumerate(stills):
  x=i%6*180;y=i//6*348;sheet.paste(im,(x,y));d.text((x+8,y+321),f'{t:.1f}s',font=font,fill='white')
 sheet.save(OUT/(name+'_2s_contact.jpg'),quality=87)
 valid=np.asarray(rows,dtype=float)
 # Scene cut intervals are approximate; optical-flow reports are per frame.
 sc=valid[(valid[:,9]>.65)&(valid[:,2]<26)&(np.abs(valid[:,6])+np.abs(valid[:,7])>.07)]
 summary.append(dict(name=f.name,frames=len(rows),fps=fps,dimensions=[w,h],duration=round(len(rows)/fps,2),
                     cut_candidates=[round(v/fps,2) for v in strong],mean_cut_interval=round(len(rows)/fps/max(1,len(strong)+1),2),
                     stable_motion_samples=int(len(sc)),mean_drift_px_frame=[round(float(np.median(sc[:,6])),2),round(float(np.median(sc[:,7])),2)] if len(sc) else [0,0],
                     median_abs_zoom_per_frame=round(float(np.median(np.abs(sc[:,8]))),5) if len(sc) else 0,
                     median_saturation=round(float(np.median(valid[:,10])),1),subtitle_white_active_pct=round(float(np.mean(valid[:,11]>.025)*100),1),
                     csv=str(csvpath.relative_to(ROOT)),contact=str((OUT/(name+'_2s_contact.jpg')).relative_to(ROOT))))
 print(name,len(rows),'cut candidates',len(strong),flush=True)
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')

#!/usr/bin/env python3
"""Rank manually researched case candidates; never scrapes or asserts case truth."""
import csv,argparse
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('csv_file',nargs='?',default=str(Path(__file__).with_name('topic_candidates.csv')));p.add_argument('--min-score',type=float,default=24);a=p.parse_args()
keys=['evidence_score','story_score','ethics_score','visual_score','short_score','source_score','brand_fit_score']
with open(a.csv_file,encoding='utf-8-sig',newline='') as f:
 rows=list(csv.DictReader(f))
for r in rows:
 try:
  scores=[float(r[k]) for k in keys];total=sum(scores)
 except (ValueError,KeyError):continue
 if min(scores)<0 or max(scores)>5:raise SystemExit(f"Scores must be 0–5: {r.get('case_title')}")
 r['_score']=total
for r in sorted((x for x in rows if '_score' in x and x['_score']>=a.min_score),key=lambda x:x['_score'],reverse=True):
 print(f"{r['_score']:>4.0f}/35  {r['case_title']}  [{r['case_status']}] — {r['hook_or_question']}")

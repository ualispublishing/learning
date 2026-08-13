#!/usr/bin/env python3
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MEAN=re.compile(r'(?m)^Meaning:\s*(.+?)\s*$')
POS=re.compile(r'(?m)^Part of speech:\s*(.+?)\s*$')
RANK=re.compile(r'(?m)^Rank:\s*(\d+)\s*$')
with (ROOT/'arabic_top1000.csv').open(encoding='utf-8-sig',newline='') as f:
    rows=list(csv.DictReader(f))[:100]
out=[]
for i,r in enumerate(rows,1):
    back=r.get('Back','')
    def grab(rx):
        m=rx.search(back); return m.group(1).strip() if m else ''
    out.append({'rank':int(grab(RANK) or i),'front':r.get('Front',''),'meaning':grab(MEAN),'part_of_speech':grab(POS)})
path=ROOT/'audit/arabic_top100_second_pass_snapshot.json'
path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'rows':len(out),'rank_start':out[0]['rank'],'rank_end':out[-1]['rank']},ensure_ascii=False))

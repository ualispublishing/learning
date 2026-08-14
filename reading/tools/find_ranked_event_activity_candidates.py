#!/usr/bin/env python3
from __future__ import annotations
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reading/audit/final_arabic_event_activity_rank_candidates.json';RANK_RE=re.compile(r'\bRank:\s*(\d+)')
NEED=('event','occasion','activity','festival','function','ceremony')
items=[]
for name in ('arabic_top1000.csv','arabic_top3000.csv'):
 with (ROOT/name).open(encoding='utf-8',newline='') as f:
  for row in csv.DictReader(f):
   back=row.get('Back','') or '';m=RANK_RE.search(back)
   if not m:continue
   low=back.lower();hits=[x for x in NEED if re.search(r'\b'+re.escape(x)+r's?\b',low)]
   if hits:items.append({'rank':int(m.group(1)),'front':row.get('Front',''),'source_file':name,'hits':hits,'back_excerpt':back[:500]})
# reader usage of candidate ids
ids={f"ar-r{x['rank']}" for x in items};usage={tid:{'new':[],'review':[]} for tid in ids}
for level in ('a1','a2','b1','b2','c1','c2'):
 p=ROOT/f'reading/arabic/{level}/passages.jsonl'
 for line in p.read_text(encoding='utf-8').splitlines():
  if not line.strip():continue
  r=json.loads(line)
  for t in r.get('new_lexical_targets',[]):
   if isinstance(t,dict) and t.get('id') in usage:usage[t['id']]['new'].append({'level':level,'passage_id':r['id'],'form':t.get('form'),'sense':t.get('intended_sense')})
  for t in r.get('review_lexical_targets',[]):
   if isinstance(t,dict) and t.get('id') in usage:usage[t['id']]['review'].append({'level':level,'passage_id':r['id'],'form':t.get('form')})
for x in items:x['reader_usage']=usage[f"ar-r{x['rank']}"]
payload={'candidates':items,'count':len(items)};OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(payload,ensure_ascii=False))

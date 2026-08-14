#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reading/audit/final_arabic_event_replacement_usage.json';IDS=('ar-r593','ar-r834')
usage={x:{'new':[],'review':[],'questions':[]} for x in IDS}
for level in ('a1','a2','b1','b2','c1','c2'):
 p=ROOT/f'reading/arabic/{level}/passages.jsonl'
 for line in p.read_text(encoding='utf-8').splitlines():
  if not line.strip():continue
  r=json.loads(line)
  for t in r.get('new_lexical_targets',[]):
   if isinstance(t,dict) and t.get('id') in usage:usage[t['id']]['new'].append({'level':level,'passage_id':r['id'],'form':t.get('form'),'sense':t.get('intended_sense')})
  for t in r.get('review_lexical_targets',[]):
   if isinstance(t,dict) and t.get('id') in usage:usage[t['id']]['review'].append({'level':level,'passage_id':r['id'],'form':t.get('form'),'stage':t.get('review_stage')})
  for q in r.get('questions',[]):
   if isinstance(q,dict):
    for tid in q.get('target_ids',[]) if isinstance(q.get('target_ids'),list) else []:
     if tid in usage:usage[tid]['questions'].append({'level':level,'passage_id':r['id'],'question_id':q.get('id')})
OUT.write_text(json.dumps({'usage':usage},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(usage,ensure_ascii=False))

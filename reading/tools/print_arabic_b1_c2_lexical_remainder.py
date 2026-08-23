#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
D=json.loads((ROOT/'reading/audit/arabic_b1_c2_lexical_diagnostic_adjudication_2026-08-23.json').read_text(encoding='utf-8'))
LEVELS=('b1','b2','c1','c2')
IDX={}
for l in LEVELS:
 rows=[json.loads(x) for x in (ROOT/f'reading/arabic/{l}/passages.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
 IDX[l]={r['id']:r for r in rows}
print('=== NEW TARGET REMAINDER ===')
for x in D.get('unresolved',[]):
 if x.get('decision')=='UNRESOLVED_FALSE_RUNNING_TEXT_REVIEW':continue
 dg=x['diagnostic'];pid=dg['passage_id'];l=pid.split('-')[1];r=IDX[l][pid]
 print(json.dumps({'decision':x.get('decision'),'passage_id':pid,'target_id':dg.get('target_id'),'form':dg.get('form'),'declared':dg.get('declared'),'target_metadata':x.get('target_metadata'),'supported_hits':x.get('supported_hits'),'text':r.get('text')},ensure_ascii=False))
print('=== QUESTION-LINKED FALSE RUNNING TEXT ===')
for x in D.get('unresolved',[]):
 if x.get('decision')!='UNRESOLVED_FALSE_RUNNING_TEXT_REVIEW':continue
 dg=x['diagnostic'];pid=dg['passage_id'];l=pid.split('-')[1];r=IDX[l][pid];tid=dg.get('target_id');refs=[q.get('id') for q in r.get('questions',[]) if tid in (q.get('target_ids') or [])]
 if refs:print(json.dumps({'passage_id':pid,'target_id':tid,'form':dg.get('form'),'review_stage':dg.get('review_stage'),'question_ids':refs},ensure_ascii=False))

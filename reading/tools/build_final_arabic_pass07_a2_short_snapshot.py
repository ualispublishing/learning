#!/usr/bin/env python3
"""Build a compact snapshot of any currently below-band A2 passages."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'reading/arabic/a2/passages.jsonl'
OUT=ROOT/'reading/audit/final_arabic_pass07_a2_short_snapshot.jsonl'
TOKEN=re.compile(r'\S+')
rows=[json.loads(x) for x in SRC.read_text(encoding='utf-8').splitlines() if x.strip()]
if len(rows)!=60 or len({r['id'] for r in rows})!=60:
    raise SystemExit('A2 canonical corpus must contain 60 unique passages')
short=[]
for r in rows:
    actual=len(TOKEN.findall(str(r.get('text',''))))
    if actual!=int(r.get('word_count',0) or 0):
        raise SystemExit(f"{r['id']}: stored/actual word count mismatch")
    if actual<140:
        short.append({
            'id':r['id'],'unit':r['unit'],'sequence':r['sequence'],'word_count':actual,
            'title':r.get('title',''),'text':r.get('text',''),
            'new_target_forms':[t.get('form','') for t in r.get('new_lexical_targets',[])],
            'new_target_ids':[t.get('id','') for t in r.get('new_lexical_targets',[])],
            'p06_zero_new_word': bool(str(r['id']).endswith('-p06') and r.get('new_lexical_targets')==[] and r.get('speed_training',{}).get('new_word_policy')=='none'),
        })
OUT.write_text(('\n'.join(json.dumps(r,ensure_ascii=False) for r in short)+'\n') if short else '',encoding='utf-8')
print(json.dumps({'short_passages':len(short),'by_unit':{str(u):sum(1 for r in short if r['unit']==u) for u in sorted({r['unit'] for r in short})}},ensure_ascii=False))

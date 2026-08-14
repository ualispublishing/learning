#!/usr/bin/env python3
"""Remove three stale ar-r2063 review entries left after فعالية=event was remapped.

B1 U02 P05 uses فعالية in the ordinary event/activity sense, which is not rank
2063. B1 U02 P06 and C2 U06 P05 do not contain the surface at all. No reader
text is changed.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
TARGET='ar-r2063'
EXPECTED={
 'ar-b1-u02-p05':('b1','فعالية','event_surface'),
 'ar-b1-u02-p06':('b1','فعالية','absent_surface'),
 'ar-c2-u06-p05':('c2','فعالية','absent_surface'),
}
loaded={}
for level in ('b1','c2'):
 p=ROOT/f'reading/arabic/{level}/passages.jsonl'
 loaded[level]=[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
by={r['id']:(level,r) for level,rows in loaded.items() for r in rows}
hits=[]
for level,rows in loaded.items():
 for r in rows:
  for t in r.get('review_lexical_targets',[]):
   if isinstance(t,dict) and t.get('id')==TARGET:hits.append((r['id'],level,t.get('form')))
assert set(hits)=={(pid,level,form) for pid,(level,form,_) in EXPECTED.items()},hits
for pid,(level,form,state) in EXPECTED.items():
 r=by[pid][1]
 if state=='event_surface':
  assert 'فعالية' in r.get('text',''),(pid,r.get('text'))
  # Event-planning context, not effectiveness/efficiency.
  assert any(x in r.get('text','') for x in ('فعالية خارجية','وقت الفعالية','تصميم الفعالية')),(pid,r.get('text'))
 else:
  assert 'فعالية' not in r.get('text',''),(pid,r.get('text'))
 r['review_lexical_targets']=[t for t in r.get('review_lexical_targets',[]) if not (isinstance(t,dict) and t.get('id')==TARGET)]
 r['revision']=int(r.get('revision',1))+1
 notes=r.setdefault('quality',{}).setdefault('notes',[])
 note='Final adversarial review repair: removed stale ar-r2063 review metadata after فعالية=event was remapped to source-backed مناسبة; reader text unchanged.'
 if note not in notes:notes.append(note)
for level,rows in loaded.items():
 p=ROOT/f'reading/arabic/{level}/passages.jsonl'
 p.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
remaining=[(r['id'],t) for rows in loaded.values() for r in rows for t in r.get('review_lexical_targets',[]) if isinstance(t,dict) and t.get('id')==TARGET]
assert not remaining,remaining
print(json.dumps({'removed':sorted(EXPECTED),'target_id':TARGET},ensure_ascii=False))

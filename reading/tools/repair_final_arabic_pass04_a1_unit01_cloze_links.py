#!/usr/bin/env python3
"""Add the four missing target_ids confirmed by final Pass 04 in A1 Unit 01."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'
EXPECTED={
 ('ar-a1-u01-p02','q5','فقط','ar-r54'),
 ('ar-a1-u01-p03','q5','هناك','ar-r40'),
 ('ar-a1-u01-p04','q5','يمكن','ar-r36'),
 ('ar-a1-u01-p05','q5','حتى','ar-r56'),
}
rows=[json.loads(line) for line in PATH.read_text(encoding='utf-8').splitlines() if line.strip()]
by={r['id']:r for r in rows}
repairs=[]
for pid,qid,answer,tid in EXPECTED:
    r=by[pid];qs={q['id']:q for q in r['questions']};ans={a['question_id']:a for a in r['answer_key']};q=qs[qid]
    assert q['type']=='cloze_transfer',(pid,q)
    assert ans[qid]['answer'].strip(' .،؛')==answer,(pid,ans[qid])
    # The target must already be a declared new/review lexical item in this passage.
    target_ids={t.get('id') for t in [*r.get('new_lexical_targets',[]),*r.get('review_lexical_targets',[])] if isinstance(t,dict)}
    assert tid in target_ids,(pid,tid,target_ids)
    assert not q.get('target_ids'),(pid,qid,q.get('target_ids'))
    q['target_ids']=[tid]
    repairs.append({'passage_id':pid,'question_id':qid,'answer':answer,'target_id':tid})
for pid in sorted({x[0] for x in EXPECTED}):
    r=by[pid];r['revision']=int(r.get('revision',1))+1
    notes=r.setdefault('quality',{}).setdefault('notes',[])
    note='Final audit Pass 04 repair: added the missing lexical target_id to a verified Unit-01 cloze transfer item; prompt and answer unchanged.'
    if note not in notes:notes.append(note)
PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
print(json.dumps({'repair_count':len(repairs),'repairs':repairs},ensure_ascii=False))

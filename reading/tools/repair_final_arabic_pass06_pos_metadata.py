#!/usr/bin/env python3
"""Correct nine source-backed POS metadata errors found by strengthened Pass 06.

This does not adjudicate intended-sense semantics. In particular فعالية/ar-r2063
remains queued for the separate lexical-sense pass because the source sense is
'effectiveness; efficiency' while the reader context uses 'event/activity'.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a2/passages.jsonl'
EXPECTED={
 ('ar-a2-u05-p05','ar-r1190','خبرة'):'noun',
 ('ar-a2-u07-p01','ar-r2063','فعالية'):'noun',
 ('ar-a2-u07-p02','ar-r510','بيان'):'noun',
 ('ar-a2-u07-p03','ar-r702','تأثير'):'noun',
 ('ar-a2-u07-p04','ar-r337','أعلن'):'verb',
 ('ar-a2-u08-p01','ar-r144','منطقة'):'noun',
 ('ar-a2-u08-p05','ar-r445','مجتمع'):'noun',
 ('ar-a2-u09-p01','ar-r638','قصة'):'noun',
 ('ar-a2-u09-p03','ar-r1267','مطعم'):'noun',
}
rows=[json.loads(x) for x in PATH.read_text(encoding='utf-8').splitlines() if x.strip()]
by={r['id']:r for r in rows};repairs=[];touched=set()
for (pid,tid,form),new_pos in EXPECTED.items():
 r=by[pid];hits=[t for t in r.get('new_lexical_targets',[]) if isinstance(t,dict) and t.get('id')==tid]
 assert len(hits)==1,(pid,tid,hits);t=hits[0];assert t.get('form')==form,(pid,tid,t)
 old=t.get('part_of_speech');assert old!=new_pos,(pid,tid,old)
 t['part_of_speech']=new_pos;touched.add(pid);repairs.append({'passage_id':pid,'target_id':tid,'form':form,'old_pos':old,'new_pos':new_pos})
for pid in touched:
 r=by[pid];r['revision']=int(r.get('revision',1))+1
 notes=r.setdefault('quality',{}).setdefault('notes',[]);note='Final audit Pass 06 repair: corrected lexical target part-of-speech metadata to match the canonical source row; lexical-sense review remains independent.'
 if note not in notes:notes.append(note)
PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
print(json.dumps({'repair_count':len(repairs),'repairs':repairs,'semantic_followup_required':['ar-r2063/فعالية']},ensure_ascii=False))

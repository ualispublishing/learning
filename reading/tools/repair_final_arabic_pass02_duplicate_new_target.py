#!/usr/bin/env python3
"""Guarded repair for Pass-02 duplicate new target ar-r487 in ar-b1-u02-p01."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/b1/passages.jsonl'
TARGET_ID='ar-r487'
FIRST_PID='ar-b1-u01-p04'
REPAIR_PID='ar-b1-u02-p01'

rows=[json.loads(line) for line in PATH.read_text(encoding='utf-8').splitlines() if line.strip()]
by_id={r['id']:r for r in rows}
assert FIRST_PID in by_id and REPAIR_PID in by_id
first=by_id[FIRST_PID]
row=by_id[REPAIR_PID]
first_hits=[t for t in first.get('new_lexical_targets',[]) if t.get('id')==TARGET_ID]
second_hits=[t for t in row.get('new_lexical_targets',[]) if t.get('id')==TARGET_ID]
assert len(first_hits)==1, first_hits
assert len(second_hits)==1, second_hits
assert first_hits[0].get('intended_sense')=='result; outcome'
assert second_hits[0].get('intended_sense')=='result; outcome'
assert second_hits[0].get('form')=='نتيجة'

row['new_lexical_targets']=[t for t in row.get('new_lexical_targets',[]) if t.get('id')!=TARGET_ID]
reviews=row.setdefault('review_lexical_targets',[])
if not any(t.get('id')==TARGET_ID for t in reviews):
    reviews.append({'form':'نتيجة','id':TARGET_ID,'representation':'running_text','review_stage':'R1'})
row['revision']=int(row.get('revision',1))+1
quality=row.setdefault('quality',{})
notes=quality.setdefault('notes',[])
msg='Final audit Pass 02 repair: ar-r487/نتيجة was already introduced at ar-b1-u01-p04; this occurrence is review, not a second new introduction.'
if msg not in notes:
    notes.append(msg)

assert not any(t.get('id')==TARGET_ID for t in row.get('new_lexical_targets',[]))
assert sum(1 for t in row.get('review_lexical_targets',[]) if t.get('id')==TARGET_ID)==1
PATH.write_text('\n'.join(json.dumps(r,ensure_ascii=False,sort_keys=True) for r in rows)+'\n',encoding='utf-8')
print('repaired',REPAIR_PID,TARGET_ID,'new->review')

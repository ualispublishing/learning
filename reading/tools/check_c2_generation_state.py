#!/usr/bin/env python3
"""Write structural C2 generation state only; performs no passage-quality audit."""
from __future__ import annotations
import json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'reading/arabic/c2/passages.jsonl'
OUT=ROOT/'reading/planning/C2_GENERATION_STATE.json'
ID_RE=re.compile(r'^ar-c2-u(\d{2})-p(\d{2})$')
rows=[]
if SRC.exists():
    rows=[json.loads(line) for line in SRC.read_text(encoding='utf-8').splitlines() if line.strip()]
units=Counter(int(r.get('unit',0) or 0) for r in rows)
q=sum(len(r.get('questions',[])) for r in rows)
a=sum(len(r.get('answer_key',[])) for r in rows)
unit_details={str(i):{'passages':units.get(i,0),'complete_six':units.get(i,0)==6} for i in range(1,11)}
ids=[r.get('id') for r in rows]
duplicate_ids=sorted([k for k,v in Counter(ids).items() if k and v>1])
sequences=[r.get('sequence') for r in rows]
sequence_ints=sorted(x for x in sequences if isinstance(x,int))
sequence_exact_1_60=(len(rows)==60 and sequence_ints==list(range(1,61)))
question_count_errors=[{'id':r.get('id'),'questions':len(r.get('questions',[]))} for r in rows if len(r.get('questions',[]))!=10]
answer_count_errors=[{'id':r.get('id'),'answers':len(r.get('answer_key',[]))} for r in rows if len(r.get('answer_key',[]))!=10]
id_shape_errors=[]
unit_passage_pairs=[]
for r in rows:
    m=ID_RE.match(str(r.get('id','')))
    if not m:
        id_shape_errors.append(r.get('id'))
        continue
    unit=int(m.group(1)); passage=int(m.group(2))
    unit_passage_pairs.append((unit,passage))
    if unit!=int(r.get('unit',0) or 0) or not 1<=passage<=6:
        id_shape_errors.append(r.get('id'))
expected_pairs={(u,p) for u in range(1,11) for p in range(1,7)}
actual_pairs=set(unit_passage_pairs)
full_unit_passage_grid=(actual_pairs==expected_pairs and len(unit_passage_pairs)==60)
structural_complete=(
    len(rows)==60 and q==600 and a==600 and not duplicate_ids and
    all(units.get(i,0)==6 for i in range(1,11)) and sequence_exact_1_60 and
    not question_count_errors and not answer_count_errors and not id_shape_errors and
    full_unit_passage_grid
)
payload={
    'purpose':'structural generation continuity only; not a linguistic, pedagogical, lexical, factual, schema, or answer-quality audit',
    'cefr':'C2','passages':len(rows),'questions':q,'answers':a,
    'units':unit_details,
    'complete_units':[i for i in range(1,11) if units.get(i,0)==6],
    'missing_or_incomplete_units':[i for i in range(1,11) if units.get(i,0)!=6],
    'duplicate_ids':duplicate_ids,
    'sequence_exact_1_60':sequence_exact_1_60,
    'sequence_values':sequence_ints,
    'question_count_errors':question_count_errors,
    'answer_count_errors':answer_count_errors,
    'id_shape_errors':id_shape_errors,
    'full_unit_passage_grid':full_unit_passage_grid,
    'structural_continuity':structural_complete,
    'generation_complete':structural_complete,
    'formal_quality_audits_deferred':True
}
OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(payload,ensure_ascii=False))
if not structural_complete:
    raise SystemExit('C2 structural generation gate failed')

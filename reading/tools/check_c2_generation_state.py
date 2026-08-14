#!/usr/bin/env python3
"""Write structural C2 generation state only; performs no quality audit."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'reading/arabic/c2/passages.jsonl'
OUT=ROOT/'reading/planning/C2_GENERATION_STATE.json'
rows=[]
if SRC.exists():
    rows=[json.loads(line) for line in SRC.read_text(encoding='utf-8').splitlines() if line.strip()]
units=Counter(int(r.get('unit',0) or 0) for r in rows)
q=sum(len(r.get('questions',[])) for r in rows)
a=sum(len(r.get('answer_key',[])) for r in rows)
unit_details={str(i):{'passages':units.get(i,0),'complete_six':units.get(i,0)==6} for i in range(1,11)}
payload={
    'purpose':'structural generation continuity only; not a linguistic, pedagogical, lexical, factual, schema, or answer-quality audit',
    'cefr':'C2','passages':len(rows),'questions':q,'answers':a,
    'units':unit_details,
    'complete_units':[i for i in range(1,11) if units.get(i,0)==6],
    'missing_or_incomplete_units':[i for i in range(1,11) if units.get(i,0)!=6],
    'duplicate_ids':sorted([k for k,v in Counter(r.get('id') for r in rows).items() if k and v>1]),
    'structural_continuity': all(units.get(i,0)==6 for i in range(1,max([0,*units.keys()])+1)) if units else True,
    'formal_quality_audits_deferred':True
}
OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(payload,ensure_ascii=False))

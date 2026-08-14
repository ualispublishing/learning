#!/usr/bin/env python3
"""Inventory enum-like values used by the Arabic corpus for schema-contract review."""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
OUT=ROOT/'reading/audit/final_arabic_schema_contract_value_inventory.json'
fields={
    'domains':Counter(),
    'passage_types':Counter(),
    'context_strategies':Counter(),
    'review_stages':Counter(),
}
by_level={level:{k:Counter() for k in fields} for level in LEVELS}
for level in LEVELS:
    p=ROOT/f'reading/arabic/{level}/passages.jsonl'
    for line in p.read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        r=json.loads(line)
        for v in r.get('domains',[]):
            fields['domains'][v]+=1; by_level[level]['domains'][v]+=1
        pt=r.get('passage_type')
        fields['passage_types'][pt]+=1; by_level[level]['passage_types'][pt]+=1
        for t in r.get('new_lexical_targets',[]):
            for v in t.get('context_strategy',[]):
                fields['context_strategies'][v]+=1; by_level[level]['context_strategies'][v]+=1
        for t in r.get('review_lexical_targets',[]):
            v=t.get('review_stage')
            fields['review_stages'][v]+=1; by_level[level]['review_stages'][v]+=1
payload={
    'scope':'Arabic A1-C2 canonical reading corpus',
    'totals':{k:dict(sorted(v.items(),key=lambda x:(-x[1],str(x[0])))) for k,v in fields.items()},
    'by_level':{level:{k:dict(sorted(v.items(),key=lambda x:(-x[1],str(x[0])))) for k,v in groups.items()} for level,groups in by_level.items()},
}
OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(payload['totals'],ensure_ascii=False))

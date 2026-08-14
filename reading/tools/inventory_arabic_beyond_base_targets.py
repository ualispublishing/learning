#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
OUT=ROOT/'reading/audit/final_arabic_beyond_base_target_inventory.json'
items=[]
for level in LEVELS:
    p=ROOT/f'reading/arabic/{level}/passages.jsonl'
    for line in p.read_text(encoding='utf-8').splitlines():
        if not line.strip():continue
        r=json.loads(line)
        for t in r.get('new_lexical_targets',[]):
            if isinstance(t,dict) and t.get('beyond_base') is True:
                items.append({'level':level,'passage_id':r['id'],'target':t})
payload={'count':len(items),'items':items,'id_prefixes':sorted({str(x['target'].get('id','')).split('-')[0] for x in items})}
OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'count':len(items),'ids':[x['target'].get('id') for x in items[:30]]},ensure_ascii=False))

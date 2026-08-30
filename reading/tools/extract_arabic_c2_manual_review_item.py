#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
src=READING/'audit'/'arabic_b1_c2_metalinguistic_manual_queue_2026-08-30.json'
out=READING/'audit'/'arabic_c2_metalinguistic_manual_item_2026-08-30.json'
d=json.loads(src.read_text(encoding='utf-8'))
items=[x for x in d['items'] if x['level']=='C2']
if len(items)!=1: raise SystemExit(f'expected one C2 item, found {len(items)}')
r={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'C2','date':'2026-08-30','canonical_binding':d['canonical_bindings']['c2'],'count':1,'item':items[0],'release_claim':False}
out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(r,ensure_ascii=False,indent=2))

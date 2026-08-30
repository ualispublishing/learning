#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
src=READING/'audit'/'arabic_b1_c2_metalinguistic_cefr_triage_2026-08-30.json'
out=READING/'audit'/'arabic_b1_c2_metalinguistic_manual_queue_2026-08-30.json'
d=json.loads(src.read_text(encoding='utf-8'))
items=[x for x in d['results'] if x['decision']=='MANUAL_REVIEW']
if len(items)!=d['manual_review_count'] or len(items)!=11: raise SystemExit(f'queue mismatch: {len(items)}')
report={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','levels':['B1','B2','C1','C2'],'date':'2026-08-30','source_artifact':str(src.relative_to(ROOT)),'canonical_bindings':d['canonical_bindings'],'count':len(items),'items':items,'release_claim':False}
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))

#!/usr/bin/env python3
"""Record fresh Arabic Gate B A1 Unit 9 decisions from the rebuilt Gate B inventory."""
from __future__ import annotations
import hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; CANONICAL=READING/'arabic/a1/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'; DECISION_PATH=DECISION_DIR/'a1_u09.json'; EXPECTED_IDS=[f'ar-a1-u09-p{i:02d}' for i in range(1,7)]; EXPECTED_FINDINGS=15
def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def load_meta():
 source=Path(__file__).with_name('apply_arabic_gate_b_a1_unit09.py'); spec=importlib.util.spec_from_file_location('arabic_gate_b_a1_u09_meta',source)
 if spec is None or spec.loader is None: raise SystemExit('cannot load Unit 9 repair metadata')
 mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod.FINDING_META
def main():
 raw=CANONICAL.read_bytes(); canonical_sha=sha(raw); rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(48,54)]!=EXPECTED_IDS: raise SystemExit('A1 Unit 9 layout/id drift')
 for r in rows[48:54]:
  q=r.get('quality',{})
  for field in ('linguistic_review','pedagogical_review','answer_key_check','schema_check'):
   if q.get(field)!='pass': raise SystemExit(f"{r.get('id')}: {field} is not pass")
  if q.get('status')!='draft' or q.get('coverage_check')!='pending': raise SystemExit(f"{r.get('id')}: unexpected release/coverage state")
 inv=json.loads(INVENTORY.read_text(encoding='utf-8')); a1=inv.get('levels',{}).get('a1',{})
 if inv.get('project_id')!='LANG-A1C2' or inv.get('language')!='arabic' or (inv.get('records'),inv.get('questions'),inv.get('answers'))!=(360,3600,3600) or a1.get('canonical_sha256')!=canonical_sha: raise SystemExit('Gate B inventory identity/scope/hash drift')
 hashes=a1.get('record_learner_facing_sha256',{}); meta=load_meta()
 if set(meta)!=set(EXPECTED_IDS) or sum(len(meta[p]) for p in EXPECTED_IDS)!=EXPECTED_FINDINGS: raise SystemExit('Unit 9 finding metadata drift')
 decisions=[]
 for pid in EXPECTED_IDS:
  h=hashes.get(pid)
  if not isinstance(h,str) or len(h)!=64: raise SystemExit(f'missing authoritative learner hash for {pid}')
  findings=[{'finding_id':f'{pid}-gB-{idx:02d}','field':field,'dimension':dimension,'severity':severity,'status':'REPAIRED','rationale':rationale} for idx,(field,dimension,severity,rationale) in enumerate(meta[pid],1)]
  decisions.append({'passage_id':pid,'learner_facing_sha256':h,'decision':'PASS_AFTER_REPAIR','finding_count':len(findings),'findings':findings})
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'A1','unit':9,'date':'2026-09-01','gate':'Gate B — passage-by-passage linguistic/naturalness audit','canonical_path':'reading/arabic/a1/passages.jsonl','canonical_sha256':canonical_sha,'records_reviewed':6,'records_with_findings':6,'fresh_findings':EXPECTED_FINDINGS,'decisions':decisions,'quality_promotion':False,'release_claim':False,'guard':'Learner-facing hashes come only from the freshly rebuilt authoritative Gate B inventory and are independently revalidated by the progress synchronizer.'}
 DECISION_DIR.mkdir(parents=True,exist_ok=True); DECISION_PATH.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps({'level':'A1','unit':9,'records_reviewed':6,'fresh_findings':EXPECTED_FINDINGS,'canonical_sha256':canonical_sha},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

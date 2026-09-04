#!/usr/bin/env python3
"""Record fresh Arabic Gate B B2 Unit 10 decisions."""
from __future__ import annotations
import hashlib, importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'
CANONICAL=READING/'arabic/b2/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'
DECISION=READING/'audit/arabic_gate_b_decisions_2026-08-30/b2_u10.json'
IDS=[f'ar-b2-u10-p{i:02d}' for i in range(1,7)]; FINDINGS=12; WITH=5
def sha(b): return hashlib.sha256(b).hexdigest()
def meta():
 p=Path(__file__).with_name('apply_arabic_gate_b_b2_unit10.py'); s=importlib.util.spec_from_file_location('u10',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m.FINDING_META
def main():
 raw=CANONICAL.read_bytes(); rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]; csha=sha(raw)
 if len(rows)!=60 or [rows[i].get('id') for i in range(54,60)]!=IDS: raise SystemExit('B2 Unit 10 layout/id drift')
 for r in rows[54:60]:
  q=r.get('quality',{})
  if any(q.get(f)!='pass' for f in ('linguistic_review','pedagogical_review','answer_key_check','schema_check')) or q.get('status')!='draft' or q.get('coverage_check')!='pending': raise SystemExit(f"{r.get('id')}: quality-state drift")
 inv=json.loads(INVENTORY.read_text()); b2=inv.get('levels',{}).get('b2',{})
 if (inv.get('project_id'),inv.get('language'),inv.get('records'),inv.get('questions'),inv.get('answers'),b2.get('canonical_sha256'))!=('LANG-A1C2','arabic',360,3600,3600,csha): raise SystemExit('Gate B inventory drift')
 mm=meta()
 if set(mm)!=set(IDS) or sum(map(len,mm.values()))!=FINDINGS or sum(bool(v) for v in mm.values())!=WITH: raise SystemExit('finding metadata drift')
 hashes=b2.get('record_learner_facing_sha256',{}); decisions=[]
 for pid in IDS:
  h=hashes.get(pid)
  if not isinstance(h,str) or len(h)!=64: raise SystemExit(f'missing learner hash {pid}')
  fs=[{'finding_id':f'{pid}-gB-{i:02d}','field':f,'dimension':d,'severity':s,'status':'REPAIRED','rationale':r} for i,(f,d,s,r) in enumerate(mm[pid],1)]
  decisions.append({'passage_id':pid,'learner_facing_sha256':h,'decision':'PASS_AFTER_REPAIR' if fs else 'PASS','finding_count':len(fs),'findings':fs})
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'B2','unit':10,'date':'2026-09-04','gate':'Gate B — passage-by-passage linguistic/naturalness audit','canonical_path':'reading/arabic/b2/passages.jsonl','canonical_sha256':csha,'records_reviewed':6,'records_with_findings':WITH,'fresh_findings':FINDINGS,'decisions':decisions,'quality_promotion':False,'release_claim':False,'guard':'Learner-facing hashes come only from the freshly rebuilt authoritative Gate B inventory and are independently revalidated by the progress synchronizer. Legitimate B2 grammar-in-context/discourse analysis is retained; this internal Gate B pass does not constitute educator/publication release approval.'}
 DECISION.parent.mkdir(parents=True,exist_ok=True); DECISION.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__': main()

#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; R=ROOT/'reading'; CAN=R/'arabic/c2/passages.jsonl'; INV=R/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; DEC=R/'audit/arabic_gate_b_decisions_2026-08-30/c2_u09.json'; IDS=[f'ar-c2-u09-p{i:02d}' for i in range(1,7)]
def sha(b): return hashlib.sha256(b).hexdigest()
def meta():
 p=Path(__file__).with_name('apply_arabic_gate_b_c2_unit09.py'); s=importlib.util.spec_from_file_location('c2u09',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m.META
def main():
 raw=CAN.read_bytes(); rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]; csha=sha(raw)
 if len(rows)!=60 or [rows[i].get('id') for i in range(48,54)]!=IDS: raise SystemExit('layout drift')
 for r in rows[48:54]:
  q=r.get('quality',{})
  if any(q.get(f)!='pass' for f in ('linguistic_review','pedagogical_review','answer_key_check','schema_check')) or q.get('status')!='draft' or q.get('coverage_check')!='pending': raise SystemExit('quality drift')
 inv=json.loads(INV.read_text()); c2=inv['levels']['c2']
 if (inv.get('project_id'),inv.get('language'),inv.get('records'),inv.get('questions'),inv.get('answers'),c2.get('canonical_sha256'))!=('LANG-A1C2','arabic',360,3600,3600,csha): raise SystemExit('inventory drift')
 mm=meta()
 if sum(map(len,mm.values()))!=12 or sum(bool(v) for v in mm.values())!=6: raise SystemExit('finding drift')
 hashes=c2['record_learner_facing_sha256']; ds=[]
 for pid in IDS:
  fs=[{'finding_id':f'{pid}-gB-{i:02d}','field':f,'dimension':d,'severity':s,'status':'REPAIRED','rationale':r} for i,(f,d,s,r) in enumerate(mm[pid],1)]
  ds.append({'passage_id':pid,'learner_facing_sha256':hashes[pid],'decision':'PASS_AFTER_REPAIR' if fs else 'PASS','finding_count':len(fs),'findings':fs})
 doc={'schema_version':1,'project_id':'LANG-A1C2','language':'arabic','level':'C2','unit':9,'date':'2026-09-05','gate':'Gate B — passage-by-passage linguistic/naturalness audit','canonical_path':'reading/arabic/c2/passages.jsonl','canonical_sha256':csha,'records_reviewed':6,'records_with_findings':6,'fresh_findings':12,'decisions':ds,'quality_promotion':False,'release_claim':False,'guard':'Learner-facing hashes come only from the freshly rebuilt authoritative Gate B inventory and are independently revalidated by the progress synchronizer. C2 internal Gate B evidence does not constitute educator/publication release approval.'}
 DEC.parent.mkdir(parents=True,exist_ok=True); DEC.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__': main()

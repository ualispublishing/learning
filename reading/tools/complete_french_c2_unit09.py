#!/usr/bin/env python3
"""Serialize French C2 Unit09 generation/seal and prepare Unit10."""
from __future__ import annotations
import json,os,runpy,subprocess,sys,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[2]; T=R/'reading/tools'; A=R/'reading/audit'; C1=R/'reading/french/c1/passages.jsonl'; C2=R/'reading/french/c2/passages.jsonl'; OUT=A/'french_c2_unit09_pipeline.json'; sys.path.insert(0,str(T))
def run(n): print('=== RUN',n,'==='); runpy.run_path(str(T/n),run_name='__main__')
def env(n,u):
 old=os.environ.get('C2_UNIT'); os.environ['C2_UNIT']=str(u)
 try: run(n)
 finally:
  if old is None: os.environ.pop('C2_UNIT',None)
  else: os.environ['C2_UNIT']=old
def rows(): return [json.loads(x) for x in C2.read_text(encoding='utf-8').splitlines() if x.strip()]
def h(p): return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def verify():
 a=json.loads((A/'french_c2_unit09_generation_review.json').read_text(encoding='utf-8')); l=json.loads((A/'french_c2_unit09_frontier_lock.json').read_text(encoding='utf-8')); b=h(C2); c1=h(C1)
 if a.get('status')!='PASS' or a.get('c2_canonical_blob')!=b or l.get('status')!='PASS' or l.get('c2_canonical_blob')!=b or l.get('c1_canonical_blob')!=c1 or l.get('last_sequence')!=54: raise AssertionError('C2 Unit09 seal mismatch')
def prep10(st): env('resolve_french_c2_unit_plan.py',10); st.append('resolve_c2_unit10_plan'); env('probe_french_c2_unit_targets.py',10); st.append('probe_c2_unit10_targets'); env('sync_french_c2_unit_frontier.py',9); st.append('sync_c2_unit09_to_unit10')
def main():
 A.mkdir(exist_ok=True); before=C2.read_bytes(); start=len(rows()); gen=seal=front=False; err=None; st=[]
 try:
  if start>54: raise AssertionError(f'Unit09 transaction cannot operate above 54 rows: {start}')
  if start==54: verify(); seal=True; st.append('verify_existing_c2_unit09'); prep10(st); front=True
  else:
   if start!=48: raise AssertionError(f'C2 Unit09 requires 48-row Unit08 prefix, got {start}')
   prev=json.loads((A/'french_c2_unit08_frontier_lock.json').read_text(encoding='utf-8'))
   if prev.get('status')!='PASS' or prev.get('c2_canonical_blob')!=h(C2): raise AssertionError('C2 Unit08 dependency not sealed')
   env('resolve_french_c2_unit_plan.py',9); st.append('resolve_c2_unit09_plan'); env('probe_french_c2_unit_targets.py',9); st.append('probe_c2_unit09_targets'); run('select_french_c2_unit09_targets.py'); st.append('select_c2_unit09_targets'); run('generate_french_c2_unit09.py'); gen=True; st.append('generate_c2_unit09'); env('audit_french_c2_unit_generation.py',9); st.append('audit_c2_unit09'); env('lock_french_c2_unit_frontier.py',9); st.append('lock_c2_unit09'); verify(); seal=True; prep10(st); front=True
 except Exception:
  err=traceback.format_exc(); print(err)
  if gen and not seal: C2.write_bytes(before); st.append('restore_prec2unit09_after_strict_failure')
  elif seal: st.append('preserve_sealed_c2_unit09_despite_unit10_prep_failure')
  (A/'french_c2_unit09_pipeline_failure.txt').write_text(err,encoding='utf-8')
 if front:
  for p in A.glob('french_c2_unit09_*failure.txt'): p.unlink(missing_ok=True)
 out={'status':'PASS_TO_C2_UNIT10' if front else ('C2_UNIT09_PASS_UNIT10_PREP_PENDING' if seal else 'C2_UNIT09_PENDING'),'date':'2026-08-18','starting_c2_passages':start,'ending_c2_passages':len(rows()),'c1_blob':h(C1),'c2_blob':h(C2),'c2_unit09_pass':seal,'c2_unit10_frontier_prepared':front,'completed_stages':st,'error':err}
 if front:
  p=json.loads((A/'french_c2_unit10_plan.json').read_text(encoding='utf-8')); q=json.loads((A/'french_c2_unit10_target_probe.json').read_text(encoding='utf-8')); out.update({'unit10_theme':p['theme'],'unit10_genres':p['genres'],'remaining_fresh_source_terms':q['fresh_count']})
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(out,ensure_ascii=False,indent=2))
 if not front: raise SystemExit(1)
if __name__=='__main__': main()

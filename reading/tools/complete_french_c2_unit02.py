#!/usr/bin/env python3
"""Serialize C2 Unit02 generation/seal and prepare Unit03."""
from __future__ import annotations
import json,os,runpy,subprocess,sys,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[2];T=R/'reading/tools';A=R/'reading/audit';C1=R/'reading/french/c1/passages.jsonl';C2=R/'reading/french/c2/passages.jsonl';OUT=A/'french_c2_unit02_pipeline.json';sys.path.insert(0,str(T))
def run(n):print('=== RUN',n,'===');runpy.run_path(str(T/n),run_name='__main__')
def env(n,u):
 old=os.environ.get('C2_UNIT');os.environ['C2_UNIT']=str(u)
 try:run(n)
 finally:
  if old is None:os.environ.pop('C2_UNIT',None)
  else:os.environ['C2_UNIT']=old
def rows():return [json.loads(x) for x in C2.read_text().splitlines() if x.strip()] if C2.exists() else []
def h(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def verify():
 r=json.loads((A/'french_c2_unit02_generation_review.json').read_text());l=json.loads((A/'french_c2_unit02_frontier_lock.json').read_text());blob=h(C2);c1=h(C1)
 if r.get('status')!='PASS' or r.get('c2_canonical_blob')!=blob or l.get('status')!='PASS' or l.get('c2_canonical_blob')!=blob or l.get('c1_canonical_blob')!=c1 or l.get('last_sequence')!=12:raise AssertionError('C2 Unit02 seal mismatch')
 return l
def prep3(st):env('resolve_french_c2_unit_plan.py',3);st.append('resolve_c2_unit03_plan');env('probe_french_c2_unit_targets.py',3);st.append('probe_c2_unit03_targets');env('sync_french_c2_unit_frontier.py',2);st.append('sync_c2_unit02_to_unit03')
def main():
 A.mkdir(exist_ok=True);before=C2.read_bytes() if C2.exists() else None;n=len(rows());gen=False;seal=False;front=False;err=None;st=[]
 try:
  if n>12:raise AssertionError(f'Unit02 transaction cannot operate above 12 rows: {n}')
  if n==12:verify();seal=True;st.append('verify_existing_c2_unit02');prep3(st);front=True
  else:
   if n!=6:raise AssertionError(f'C2 Unit02 requires 6-row Unit01 prefix, got {n}')
   l1=json.loads((A/'french_c2_unit01_frontier_lock.json').read_text());
   if l1.get('status')!='PASS' or l1.get('c2_canonical_blob')!=h(C2):raise AssertionError('C2 Unit01 dependency not sealed')
   env('resolve_french_c2_unit_plan.py',2);st.append('resolve_c2_unit02_plan');env('probe_french_c2_unit_targets.py',2);st.append('probe_c2_unit02_targets');run('select_french_c2_unit02_targets.py');st.append('select_c2_unit02_targets');run('generate_french_c2_unit02.py');gen=True;st.append('generate_c2_unit02');env('audit_french_c2_unit_generation.py',2);st.append('audit_c2_unit02');env('lock_french_c2_unit_frontier.py',2);st.append('lock_c2_unit02');verify();seal=True;prep3(st);front=True
 except Exception:
  err=traceback.format_exc();print(err)
  if gen and not seal:C2.write_bytes(before);st.append('restore_prec2unit02_after_strict_failure')
  elif seal:st.append('preserve_sealed_c2_unit02_despite_unit03_prep_failure')
  (A/'french_c2_unit02_pipeline_failure.txt').write_text(err)
 if front:
  for p in A.glob('french_c2_unit02_*failure.txt'):p.unlink(missing_ok=True)
 result={'status':'PASS_TO_C2_UNIT03' if front else ('C2_UNIT02_PASS_UNIT03_PREP_PENDING' if seal else 'C2_UNIT02_PENDING'),'date':'2026-08-17','starting_c2_passages':n,'ending_c2_passages':len(rows()),'c1_blob':h(C1),'c2_blob':h(C2),'c2_unit02_pass':seal,'c2_unit03_frontier_prepared':front,'completed_stages':st,'error':err}
 if front:
  p=json.loads((A/'french_c2_unit03_plan.json').read_text());q=json.loads((A/'french_c2_unit03_target_probe.json').read_text());result.update({'unit03_theme':p['theme'],'unit03_genres':p['genres'],'remaining_fresh_source_terms':q['fresh_count']})
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
 if not front:raise SystemExit(1)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Serialize C1 Unit07 generation/seal and prepare Unit08."""
from __future__ import annotations
import json,os,runpy,subprocess,sys,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[2];T=R/'reading/tools';A=R/'reading/audit';C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';OUT=A/'french_c1_unit07_pipeline.json';sys.path.insert(0,str(T))
def run(n):print('=== RUN',n,'===');runpy.run_path(str(T/n),run_name='__main__')
def env(n,u):
 old=os.environ.get('C1_UNIT');os.environ['C1_UNIT']=str(u)
 try:run(n)
 finally:
  if old is None:os.environ.pop('C1_UNIT',None)
  else:os.environ['C1_UNIT']=old
def rows():return [json.loads(x) for x in C1.read_text().splitlines() if x.strip()] if C1.exists() else []
def h(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def pblob(n):return subprocess.check_output(['git','hash-object','--stdin'],input='\n'.join([x for x in C1.read_text().splitlines() if x.strip()][:n])+'\n',text=True).strip()
def verify(blob):
 l=json.loads((A/'french_c1_unit07_frontier_lock.json').read_text());r=json.loads((A/'french_c1_unit07_generation_review.json').read_text())
 if l.get('status')!='PASS' or l.get('last_sequence')!=42 or l.get('c1_canonical_blob')!=blob or l.get('b2_canonical_blob')!=h(B2) or r.get('status')!='PASS' or r.get('c1_canonical_blob')!=blob:raise AssertionError('Unit07 seal mismatch')
 return l
def prep(st):env('resolve_french_c1_unit_plan.py',8);st.append('resolve_c1_unit08_plan');env('probe_french_c1_unit_targets.py',8);st.append('probe_c1_unit08_targets');env('sync_french_c1_unit_frontier.py',7);st.append('sync_c1_unit07_to_unit08')
def main():
 A.mkdir(exist_ok=True);before=C1.read_bytes() if C1.exists() else None;n=len(rows());gen=False;seal=False;front=False;err=None;st=[]
 try:
  if n>42:
   b=pblob(42);l=verify(b);OUT.write_text(json.dumps({'status':'DEPENDENCY_PASS','starting_c1_passages':n,'ending_c1_passages':n,'c1_blob':h(C1),'unit07_prefix_blob':b,'c1_unit07_pass':True,'accepted_c1_default':l['accepted_c1_default_new_targets_per_standard_passage'],'default_is_hard_quota':False,'completed_stages':['verify_existing_sealed_c1_unit07_prefix'],'error':None},ensure_ascii=False,indent=2)+'\n');return
  if n==42:verify(h(C1));seal=True;st.append('verify_existing_sealed_c1_unit07');prep(st);front=True
  else:
   if n!=36:raise AssertionError(f'Unit07 requires 36 rows, got {n}')
   l6=json.loads((A/'french_c1_unit06_frontier_lock.json').read_text());
   if l6.get('status')!='PASS' or l6.get('c1_canonical_blob')!=h(C1):raise AssertionError('Unit06 dependency not sealed')
   env('resolve_french_c1_unit_plan.py',7);st.append('resolve_c1_unit07_plan');env('probe_french_c1_unit_targets.py',7);st.append('probe_c1_unit07_targets');run('select_french_c1_unit07_targets.py');st.append('select_c1_unit07_targets');run('generate_french_c1_unit07.py');gen=True;st.append('generate_c1_unit07');env('audit_french_c1_unit_generation.py',7);st.append('audit_c1_unit07_generation');env('lock_french_c1_unit_frontier.py',7);st.append('lock_c1_unit07');verify(h(C1));seal=True;prep(st);front=True
 except Exception:
  err=traceback.format_exc();print(err)
  if gen and not seal:C1.write_bytes(before);st.append('restore_preunit07_after_strict_failure')
  elif seal:st.append('preserve_sealed_unit07_despite_unit08_prep_failure')
  (A/'french_c1_unit07_pipeline_failure.txt').write_text(err)
 if front:
  for p in A.glob('french_c1_unit07_*failure.txt'):p.unlink(missing_ok=True)
 result={'status':'PASS_TO_C1_UNIT08' if front else ('C1_UNIT07_PASS_UNIT08_PREP_PENDING' if seal else 'C1_UNIT07_PENDING'),'date':'2026-08-17','starting_c1_passages':n,'ending_c1_passages':len(rows()),'b2_blob':h(B2),'c1_blob':h(C1),'c1_unit07_pass':seal,'c1_unit08_frontier_prepared':front,'completed_stages':st,'error':err}
 if seal:result.update({'accepted_c1_default':json.loads((A/'french_c1_unit07_frontier_lock.json').read_text())['accepted_c1_default_new_targets_per_standard_passage'],'default_is_hard_quota':False})
 if front:
  p=json.loads((A/'french_c1_unit08_plan.json').read_text());q=json.loads((A/'french_c1_unit08_target_probe.json').read_text());result.update({'unit08_theme':p.get('theme'),'unit08_genres':p.get('genres'),'remaining_fresh_source_terms':q.get('fresh_count')})
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
 if not front:raise SystemExit(1)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Serialize C1 Unit10, full C1 integrity seal, durable completion, and C2 readiness."""
from __future__ import annotations
import json,os,runpy,subprocess,sys,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[2];T=R/'reading/tools';A=R/'reading/audit';C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';OUT=A/'french_c1_unit10_pipeline.json';sys.path.insert(0,str(T))
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
def verify10(blob):
 l=json.loads((A/'french_c1_unit10_frontier_lock.json').read_text());r=json.loads((A/'french_c1_unit10_generation_review.json').read_text())
 if l.get('status')!='PASS' or l.get('last_sequence')!=60 or l.get('c1_canonical_blob')!=blob or l.get('b2_canonical_blob')!=h(B2):raise AssertionError('Unit10 lock mismatch')
 if r.get('status')!='PASS' or r.get('c1_canonical_blob')!=blob:raise AssertionError('Unit10 review mismatch')
 return l
def finish(st):
 run('audit_french_c1_generation_integrity.py');st.append('audit_full_c1_generation_integrity');integ=json.loads((A/'french_c1_generation_integrity.json').read_text())
 if integ.get('status')!='PASS' or integ.get('canonical_blob')!=h(C1):raise AssertionError('full C1 integrity/live mismatch')
 run('sync_french_c1_completion.py');st.append('sync_c1_completion');run('prepare_french_c2_readiness.py');st.append('prepare_c2_readiness')
def main():
 A.mkdir(exist_ok=True);before=C1.read_bytes() if C1.exists() else None;n=len(rows());gen=False;seal=False;integrity=False;ready=False;err=None;st=[]
 try:
  if n>60:raise AssertionError(f'C1 canonical exceeds 60 rows: {n}')
  if n==60:
   verify10(h(C1));seal=True;st.append('verify_existing_sealed_c1_unit10');finish(st);integrity=True;ready=True
  else:
   if n!=54:raise AssertionError(f'Unit10 requires 54 rows, got {n}')
   l9=json.loads((A/'french_c1_unit09_frontier_lock.json').read_text())
   if l9.get('status')!='PASS' or l9.get('c1_canonical_blob')!=h(C1):raise AssertionError('Unit09 dependency not sealed')
   env('resolve_french_c1_unit_plan.py',10);st.append('resolve_c1_unit10_plan');env('probe_french_c1_unit_targets.py',10);st.append('probe_c1_unit10_targets');run('select_french_c1_unit10_targets.py');st.append('select_c1_unit10_targets');run('generate_french_c1_unit10.py');gen=True;st.append('generate_c1_unit10');env('audit_french_c1_unit_generation.py',10);st.append('audit_c1_unit10_generation');env('lock_french_c1_unit_frontier.py',10);st.append('lock_c1_unit10');verify10(h(C1));seal=True;finish(st);integrity=True;ready=True
 except Exception:
  err=traceback.format_exc();print(err)
  if gen and not seal:C1.write_bytes(before);st.append('restore_preunit10_after_strict_failure')
  elif seal:st.append('preserve_sealed_unit10_despite_completion_or_c2_prep_failure')
  (A/'french_c1_unit10_pipeline_failure.txt').write_text(err)
 if ready:
  for p in A.glob('french_c1_unit10_*failure.txt'):p.unlink(missing_ok=True)
 status='PASS_TO_C2_UNIT01_CALIBRATION' if ready else ('C1_INTEGRITY_PASS_C2_PREP_PENDING' if integrity else ('C1_UNIT10_PASS_COMPLETION_PENDING' if seal else 'C1_UNIT10_PENDING'))
 result={'status':status,'date':'2026-08-17','starting_c1_passages':n,'ending_c1_passages':len(rows()),'b2_blob':h(B2),'c1_blob':h(C1),'c1_unit10_pass':seal,'c1_generation_integrity_pass':integrity,'c2_readiness_pass':ready,'completed_stages':st,'error':err}
 if ready:
  r=json.loads((A/'french_c2_readiness.json').read_text());result.update({'c2_word_band':[r['c2_word_min'],r['c2_word_max']],'c2_lexical_planning_band':r['c2_lexical_planning_band'],'unit01_theme':r['unit01_theme'],'unit01_genres':r['unit01_genres'],'fresh_top3000_continuation':r['fresh_top3000_continuation']})
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
 if not ready:raise SystemExit(1)
if __name__=='__main__':main()

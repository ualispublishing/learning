#!/usr/bin/env python3
"""Serialize strict C2 Unit01 calibration and prepare exact Unit02 frontier."""
from __future__ import annotations
import json,os,runpy,subprocess,sys,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[2];T=R/'reading/tools';A=R/'reading/audit';C1=R/'reading/french/c1/passages.jsonl';C2=R/'reading/french/c2/passages.jsonl';OUT=A/'french_c2_unit01_pipeline.json';sys.path.insert(0,str(T))
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
 review=json.loads((A/'french_c2_unit01_calibration_review.json').read_text());lock=json.loads((A/'french_c2_unit01_frontier_lock.json').read_text());blob=h(C2);c1=h(C1)
 if review.get('status')!='PASS' or review.get('c2_canonical_blob')!=blob or review.get('c1_canonical_blob')!=c1:raise AssertionError('C2 Unit01 review/live mismatch')
 if lock.get('status')!='PASS' or lock.get('c2_canonical_blob')!=blob or lock.get('c1_canonical_blob')!=c1 or lock.get('last_sequence')!=6:raise AssertionError('C2 Unit01 lock/live mismatch')
 return lock
def prep2(st):
 env('resolve_french_c2_unit_plan.py',2);st.append('resolve_c2_unit02_plan');env('probe_french_c2_unit_targets.py',2);st.append('probe_c2_unit02_targets');env('sync_french_c2_unit_frontier.py',1);st.append('sync_c2_unit01_to_unit02')
def main():
 A.mkdir(exist_ok=True);before=C2.read_bytes() if C2.exists() else None;before_exists=C2.exists();n=len(rows());generated=False;sealed=False;front=False;err=None;st=[]
 try:
  ready=json.loads((A/'french_c2_readiness.json').read_text());c1=h(C1)
  if ready.get('status')!='PASS' or ready.get('c1_canonical_blob')!=c1:raise AssertionError('C2 readiness not sealed to live C1')
  if n>6:raise AssertionError(f'C2 Unit01 calibration cannot run with {n} rows')
  if n==6:
   verify();sealed=True;st.append('verify_existing_c2_unit01_calibration');prep2(st);front=True
  else:
   run('select_french_c2_unit01_targets.py');st.append('select_c2_unit01_targets');run('generate_french_c2_unit01_retry.py');generated=True;st.append('generate_c2_unit01_quality_preflight');run('audit_french_c2_unit01_calibration.py');st.append('audit_c2_unit01_calibration');run('lock_french_c2_unit01_frontier.py');st.append('lock_c2_unit01');verify();sealed=True;prep2(st);front=True
 except Exception:
  err=traceback.format_exc();print(err)
  if generated and not sealed:
   if before_exists:C2.write_bytes(before)
   elif C2.exists():C2.unlink()
   st.append('restore_precalibration_c2_after_strict_failure')
  elif sealed:st.append('preserve_sealed_c2_unit01_despite_unit02_prep_failure')
  (A/'french_c2_unit01_pipeline_failure.txt').write_text(err)
 if front:
  for p in A.glob('french_c2_unit01_*failure.txt'):p.unlink(missing_ok=True)
 result={'status':'PASS_TO_C2_UNIT02' if front else ('C2_UNIT01_PASS_UNIT02_PREP_PENDING' if sealed else 'C2_UNIT01_CALIBRATION_PENDING'),'date':'2026-08-17','starting_c2_passages':n,'ending_c2_passages':len(rows()),'c1_blob':h(C1),'c2_blob':h(C2) if C2.exists() else None,'c2_unit01_pass':sealed,'c2_unit02_frontier_prepared':front,'completed_stages':st,'error':err}
 if sealed:
  l=json.loads((A/'french_c2_unit01_frontier_lock.json').read_text());result.update({'accepted_c2_default':l['accepted_c2_default_new_targets_per_standard_passage'],'default_is_hard_quota':False,'word_band':l['unit01_word_band']})
 if front:
  p=json.loads((A/'french_c2_unit02_plan.json').read_text());q=json.loads((A/'french_c2_unit02_target_probe.json').read_text());result.update({'unit02_theme':p['theme'],'unit02_genres':p['genres'],'remaining_fresh_source_terms':q['fresh_count']})
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
 if not front:raise SystemExit(1)
if __name__=='__main__':main()

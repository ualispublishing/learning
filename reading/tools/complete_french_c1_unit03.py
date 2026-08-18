#!/usr/bin/env python3
"""Serialize C1 through Unit03 and prepare exact Unit04 frontier.

At exactly 18 canonical C1 passages, verify the existing Unit03 lock/review and
prepare Unit04 directly. With later units present, verify the sealed first-18
prefix and exit read-only. A newly generated Unit03 is restored only if its own
strict review/frontier lock fails.
"""
from __future__ import annotations
import json,os,runpy,subprocess,sys,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[2];TOOLS=R/'reading/tools';AUD=R/'reading/audit';C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';OUT=AUD/'french_c1_unit03_pipeline.json';sys.path.insert(0,str(TOOLS))
def run(name):print(f'=== RUN {name} ===');runpy.run_path(str(TOOLS/name),run_name='__main__')
def run_env(name,unit):
 old=os.environ.get('C1_UNIT');os.environ['C1_UNIT']=str(unit)
 try:run(name)
 finally:
  if old is None:os.environ.pop('C1_UNIT',None)
  else:os.environ['C1_UNIT']=old
def rows():
 if not C1.exists():return []
 return [json.loads(x) for x in C1.read_text(encoding='utf-8').splitlines() if x.strip()]
def h(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip() if p.exists() else None
def prefix_blob(n):
 lines=[x for x in C1.read_text(encoding='utf-8').splitlines() if x.strip()];text='\n'.join(lines[:n])+'\n';return subprocess.check_output(['git','hash-object','--stdin'],input=text,text=True).strip()
def verify_unit03(blob):
 lock=json.loads((AUD/'french_c1_unit03_frontier_lock.json').read_text(encoding='utf-8'));review=json.loads((AUD/'french_c1_unit03_generation_review.json').read_text(encoding='utf-8'));b2blob=h(B2)
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=18 or lock.get('c1_canonical_blob')!=blob or lock.get('b2_canonical_blob')!=b2blob:raise AssertionError('sealed C1 Unit03 lock mismatch')
 if review.get('status')!='PASS' or review.get('c1_canonical_blob')!=blob:raise AssertionError('C1 Unit03 review/blob mismatch')
 return lock,b2blob
def main():
 AUD.mkdir(parents=True,exist_ok=True);before=C1.read_bytes() if C1.exists() else None;before_exists=C1.exists();before_n=len(rows());generated=False;sealed=False;frontier=False;error=None;stages=[]
 if before_n>18:
  pblob=prefix_blob(18);lock,b2blob=verify_unit03(pblob)
  result={'status':'DEPENDENCY_PASS','date':'2026-08-17','starting_c1_passages':before_n,'ending_c1_passages':before_n,'b2_blob':b2blob,'c1_blob':h(C1),'c1_unit03_prefix_blob':pblob,'c1_unit03_pass':True,'completed_stages':['verify_existing_sealed_c1_unit03_prefix'],'accepted_c1_default':lock['accepted_c1_default_new_targets_per_standard_passage'],'default_is_hard_quota':False,'error':None};OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False));return
 if before_n==18:
  try:
   live=h(C1);lock,_=verify_unit03(live);sealed=True;stages.append('verify_existing_sealed_c1_unit03')
   run_env('resolve_french_c1_unit_plan.py',4);stages.append('resolve_c1_unit04_plan');run_env('probe_french_c1_unit_targets.py',4);stages.append('probe_c1_unit04_targets');run_env('sync_french_c1_unit_frontier.py',3);stages.append('sync_c1_unit03_to_unit04');frontier=True
  except Exception:error=traceback.format_exc();print(error);(AUD/'french_c1_unit03_pipeline_failure.txt').write_text(error)
  if frontier:
   for p in AUD.glob('french_c1_unit03_*failure.txt'):p.unlink(missing_ok=True)
  status='PASS_TO_C1_UNIT04' if frontier else 'C1_UNIT03_PASS_UNIT04_PREP_PENDING';result={'status':status,'date':'2026-08-17','starting_c1_passages':18,'ending_c1_passages':18,'b2_blob':h(B2),'c1_blob':h(C1),'c1_unit03_pass':True,'c1_unit04_frontier_prepared':frontier,'completed_stages':stages,'error':error,'accepted_c1_default':lock['accepted_c1_default_new_targets_per_standard_passage'],'default_is_hard_quota':False}
  if frontier:
   plan=json.loads((AUD/'french_c1_unit04_plan.json').read_text(encoding='utf-8'));probe=json.loads((AUD/'french_c1_unit04_target_probe.json').read_text(encoding='utf-8'));result.update({'unit04_theme':plan.get('theme'),'unit04_genres':plan.get('genres'),'remaining_fresh_source_terms':probe.get('fresh_count')})
  OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
  if not frontier:raise SystemExit(1)
  return
 try:
  run('complete_french_c1_unit02.py');stages.append('complete_or_verify_c1_unit02')
  lock2=json.loads((AUD/'french_c1_unit02_frontier_lock.json').read_text(encoding='utf-8'))
  if lock2.get('status')!='PASS' or lock2.get('last_sequence')!=12:raise AssertionError('C1 Unit02 not locked')
  for name in ('resolve_french_c1_unit03_plan.py','probe_french_c1_unit03_targets.py','select_french_c1_unit03_targets.py'):
   run(name);stages.append(name.removesuffix('.py'))
  if len(rows())!=12:raise AssertionError(f'unsupported C1 frontier for Unit03 generation: {len(rows())} rows')
  run('generate_french_c1_unit03_retry.py');generated=True;stages.append('generate_c1_unit03_quality_preflight')
  run_env('audit_french_c1_unit_generation.py',3);stages.append('audit_c1_unit03_generation');review=json.loads((AUD/'french_c1_unit03_generation_review.json').read_text(encoding='utf-8'))
  if review.get('status')!='PASS' or review.get('c1_canonical_blob')!=h(C1):raise AssertionError('Unit03 review/live mismatch')
  run_env('lock_french_c1_unit_frontier.py',3);stages.append('lock_c1_unit03');lock3=json.loads((AUD/'french_c1_unit03_frontier_lock.json').read_text(encoding='utf-8'))
  if lock3.get('status')!='PASS' or lock3.get('c1_canonical_blob')!=h(C1):raise AssertionError('Unit03 lock/live mismatch')
  sealed=True;run_env('resolve_french_c1_unit_plan.py',4);stages.append('resolve_c1_unit04_plan');run_env('probe_french_c1_unit_targets.py',4);stages.append('probe_c1_unit04_targets');run_env('sync_french_c1_unit_frontier.py',3);stages.append('sync_c1_unit03_to_unit04');frontier=True
 except Exception:
  error=traceback.format_exc();print(error)
  if generated and not sealed:
   if before_exists:C1.write_bytes(before)
   elif C1.exists():C1.unlink()
   stages.append('restore_preunit03_c1_after_strict_failure')
  elif sealed:stages.append('preserve_sealed_c1_unit03_despite_unit04_prep_failure')
  (AUD/'french_c1_unit03_pipeline_failure.txt').write_text(error)
 if frontier:
  for p in AUD.glob('french_c1_unit03_*failure.txt'):p.unlink(missing_ok=True)
 status='PASS_TO_C1_UNIT04' if frontier else ('C1_UNIT03_PASS_UNIT04_PREP_PENDING' if sealed else 'C1_UNIT03_PENDING');result={'status':status,'date':'2026-08-17','starting_c1_passages':before_n,'ending_c1_passages':len(rows()),'b2_blob':h(B2),'c1_blob':h(C1),'c1_unit03_pass':sealed,'c1_unit04_frontier_prepared':frontier,'completed_stages':stages,'error':error}
 if sealed:
  lock=json.loads((AUD/'french_c1_unit03_frontier_lock.json').read_text(encoding='utf-8'));result.update({'accepted_c1_default':lock['accepted_c1_default_new_targets_per_standard_passage'],'default_is_hard_quota':False})
 if frontier:
  plan=json.loads((AUD/'french_c1_unit04_plan.json').read_text(encoding='utf-8'));probe=json.loads((AUD/'french_c1_unit04_target_probe.json').read_text(encoding='utf-8'));result.update({'unit04_theme':plan.get('theme'),'unit04_genres':plan.get('genres'),'remaining_fresh_source_terms':probe.get('fresh_count')})
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
 if not frontier:raise SystemExit(1)
if __name__=='__main__':main()

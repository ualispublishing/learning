#!/usr/bin/env python3
"""Serialize C1 Unit05 generation and prepare exact Unit06 frontier."""
from __future__ import annotations
import json,os,runpy,subprocess,sys,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[2];TOOLS=R/'reading/tools';AUD=R/'reading/audit';C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';OUT=AUD/'french_c1_unit05_pipeline.json';sys.path.insert(0,str(TOOLS))
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
def verify_unit(blob):
 lock=json.loads((AUD/'french_c1_unit05_frontier_lock.json').read_text(encoding='utf-8'));review=json.loads((AUD/'french_c1_unit05_generation_review.json').read_text(encoding='utf-8'))
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=30 or lock.get('c1_canonical_blob')!=blob or lock.get('b2_canonical_blob')!=h(B2):raise AssertionError('sealed Unit05 lock mismatch')
 if review.get('status')!='PASS' or review.get('c1_canonical_blob')!=blob:raise AssertionError('Unit05 review/blob mismatch')
 return lock
def main():
 AUD.mkdir(parents=True,exist_ok=True);before=C1.read_bytes() if C1.exists() else None;before_exists=C1.exists();before_n=len(rows());generated=False;sealed=False;frontier=False;error=None;stages=[]
 if before_n>30:
  pblob=prefix_blob(30);lock=verify_unit(pblob);result={'status':'DEPENDENCY_PASS','starting_c1_passages':before_n,'ending_c1_passages':before_n,'c1_blob':h(C1),'unit05_prefix_blob':pblob,'c1_unit05_pass':True,'accepted_c1_default':lock['accepted_c1_default_new_targets_per_standard_passage'],'default_is_hard_quota':False,'completed_stages':['verify_existing_sealed_c1_unit05_prefix'],'error':None};OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False));return
 if before_n==30:
  try:
   live=h(C1);lock=verify_unit(live);sealed=True;stages.append('verify_existing_sealed_c1_unit05');run_env('resolve_french_c1_unit_plan.py',6);stages.append('resolve_c1_unit06_plan');run_env('probe_french_c1_unit_targets.py',6);stages.append('probe_c1_unit06_targets');run_env('sync_french_c1_unit_frontier.py',5);stages.append('sync_c1_unit05_to_unit06');frontier=True
  except Exception:error=traceback.format_exc();print(error);(AUD/'french_c1_unit05_pipeline_failure.txt').write_text(error)
 else:
  try:
   run('complete_french_c1_unit04.py');stages.append('complete_or_verify_c1_unit04');lock4=json.loads((AUD/'french_c1_unit04_frontier_lock.json').read_text(encoding='utf-8'))
   if lock4.get('status')!='PASS' or lock4.get('last_sequence')!=24 or lock4.get('c1_canonical_blob')!=h(C1):raise AssertionError('Unit04 dependency not sealed')
   run_env('resolve_french_c1_unit_plan.py',5);stages.append('resolve_c1_unit05_plan');run_env('probe_french_c1_unit_targets.py',5);stages.append('probe_c1_unit05_targets');run('select_french_c1_unit05_targets.py');stages.append('select_c1_unit05_targets')
   if len(rows())!=24:raise AssertionError('Unit05 generation requires 24-row frontier')
   run('generate_french_c1_unit05.py');generated=True;stages.append('generate_c1_unit05')
   run_env('audit_french_c1_unit_generation.py',5);stages.append('audit_c1_unit05_generation');review=json.loads((AUD/'french_c1_unit05_generation_review.json').read_text(encoding='utf-8'))
   if review.get('status')!='PASS' or review.get('c1_canonical_blob')!=h(C1):raise AssertionError('Unit05 audit/live mismatch')
   run_env('lock_french_c1_unit_frontier.py',5);stages.append('lock_c1_unit05');lock5=json.loads((AUD/'french_c1_unit05_frontier_lock.json').read_text(encoding='utf-8'))
   if lock5.get('status')!='PASS' or lock5.get('c1_canonical_blob')!=h(C1):raise AssertionError('Unit05 lock/live mismatch')
   sealed=True;run_env('resolve_french_c1_unit_plan.py',6);stages.append('resolve_c1_unit06_plan');run_env('probe_french_c1_unit_targets.py',6);stages.append('probe_c1_unit06_targets');run_env('sync_french_c1_unit_frontier.py',5);stages.append('sync_c1_unit05_to_unit06');frontier=True
  except Exception:
   error=traceback.format_exc();print(error)
   if generated and not sealed:
    if before_exists:C1.write_bytes(before)
    elif C1.exists():C1.unlink()
    stages.append('restore_preunit05_after_strict_failure')
   elif sealed:stages.append('preserve_sealed_unit05_despite_unit06_prep_failure')
   (AUD/'french_c1_unit05_pipeline_failure.txt').write_text(error)
 if frontier:
  for p in AUD.glob('french_c1_unit05_*failure.txt'):p.unlink(missing_ok=True)
 status='PASS_TO_C1_UNIT06' if frontier else ('C1_UNIT05_PASS_UNIT06_PREP_PENDING' if sealed else 'C1_UNIT05_PENDING');result={'status':status,'date':'2026-08-17','starting_c1_passages':before_n,'ending_c1_passages':len(rows()),'b2_blob':h(B2),'c1_blob':h(C1),'c1_unit05_pass':sealed,'c1_unit06_frontier_prepared':frontier,'completed_stages':stages,'error':error}
 if sealed:
  lock=json.loads((AUD/'french_c1_unit05_frontier_lock.json').read_text(encoding='utf-8'));result.update({'accepted_c1_default':lock['accepted_c1_default_new_targets_per_standard_passage'],'default_is_hard_quota':False})
 if frontier:
  plan=json.loads((AUD/'french_c1_unit06_plan.json').read_text(encoding='utf-8'));probe=json.loads((AUD/'french_c1_unit06_target_probe.json').read_text(encoding='utf-8'));result.update({'unit06_theme':plan.get('theme'),'unit06_genres':plan.get('genres'),'remaining_fresh_source_terms':probe.get('fresh_count')})
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
 if not frontier:raise SystemExit(1)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Serialize C1 Unit06 generation, strict seal, and prepare exact Unit07 frontier."""
from __future__ import annotations
import json,os,runpy,subprocess,sys,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[2];TOOLS=R/'reading/tools';AUD=R/'reading/audit';C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';OUT=AUD/'french_c1_unit06_pipeline.json';sys.path.insert(0,str(TOOLS))
def run(name):print(f'=== RUN {name} ===');runpy.run_path(str(TOOLS/name),run_name='__main__')
def run_env(name,unit):
 old=os.environ.get('C1_UNIT');os.environ['C1_UNIT']=str(unit)
 try:run(name)
 finally:
  if old is None:os.environ.pop('C1_UNIT',None)
  else:os.environ['C1_UNIT']=old
def rows():return [json.loads(x) for x in C1.read_text(encoding='utf-8').splitlines() if x.strip()] if C1.exists() else []
def h(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip() if p.exists() else None
def prefix_blob(n):
 lines=[x for x in C1.read_text(encoding='utf-8').splitlines() if x.strip()];return subprocess.check_output(['git','hash-object','--stdin'],input='\n'.join(lines[:n])+'\n',text=True).strip()
def verify(blob):
 lock=json.loads((AUD/'french_c1_unit06_frontier_lock.json').read_text());review=json.loads((AUD/'french_c1_unit06_generation_review.json').read_text())
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=36 or lock.get('c1_canonical_blob')!=blob or lock.get('b2_canonical_blob')!=h(B2):raise AssertionError('Unit06 lock mismatch')
 if review.get('status')!='PASS' or review.get('c1_canonical_blob')!=blob:raise AssertionError('Unit06 review mismatch')
 return lock
def prep7(stages):
 run_env('resolve_french_c1_unit_plan.py',7);stages.append('resolve_c1_unit07_plan');run_env('probe_french_c1_unit_targets.py',7);stages.append('probe_c1_unit07_targets');run_env('sync_french_c1_unit_frontier.py',6);stages.append('sync_c1_unit06_to_unit07')
def main():
 AUD.mkdir(parents=True,exist_ok=True);before=C1.read_bytes() if C1.exists() else None;before_exists=C1.exists();n=len(rows());generated=False;sealed=False;frontier=False;error=None;stages=[]
 try:
  if n>36:
   blob=prefix_blob(36);lock=verify(blob);result={'status':'DEPENDENCY_PASS','starting_c1_passages':n,'ending_c1_passages':n,'c1_blob':h(C1),'unit06_prefix_blob':blob,'c1_unit06_pass':True,'accepted_c1_default':lock['accepted_c1_default_new_targets_per_standard_passage'],'default_is_hard_quota':False,'completed_stages':['verify_existing_sealed_c1_unit06_prefix'],'error':None};OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False));return
  if n==36:
   lock=verify(h(C1));sealed=True;stages.append('verify_existing_sealed_c1_unit06');prep7(stages);frontier=True
  else:
   if n!=30:raise AssertionError(f'Unit06 requires 30-row sealed source, got {n}')
   lock5=json.loads((AUD/'french_c1_unit05_frontier_lock.json').read_text())
   if lock5.get('status')!='PASS' or lock5.get('c1_canonical_blob')!=h(C1):raise AssertionError('Unit05 dependency not sealed')
   run_env('resolve_french_c1_unit_plan.py',6);stages.append('resolve_c1_unit06_plan');run_env('probe_french_c1_unit_targets.py',6);stages.append('probe_c1_unit06_targets');run('select_french_c1_unit06_targets.py');stages.append('select_c1_unit06_targets');run('generate_french_c1_unit06.py');generated=True;stages.append('generate_c1_unit06')
   run_env('audit_french_c1_unit_generation.py',6);stages.append('audit_c1_unit06_generation');review=json.loads((AUD/'french_c1_unit06_generation_review.json').read_text())
   if review.get('status')!='PASS' or review.get('c1_canonical_blob')!=h(C1):raise AssertionError('Unit06 audit/live mismatch')
   run_env('lock_french_c1_unit_frontier.py',6);stages.append('lock_c1_unit06');lock6=json.loads((AUD/'french_c1_unit06_frontier_lock.json').read_text())
   if lock6.get('status')!='PASS' or lock6.get('c1_canonical_blob')!=h(C1):raise AssertionError('Unit06 lock/live mismatch')
   sealed=True;prep7(stages);frontier=True
 except Exception:
  error=traceback.format_exc();print(error)
  if generated and not sealed:
   if before_exists:C1.write_bytes(before)
   elif C1.exists():C1.unlink()
   stages.append('restore_preunit06_after_strict_failure')
  elif sealed:stages.append('preserve_sealed_unit06_despite_unit07_prep_failure')
  (AUD/'french_c1_unit06_pipeline_failure.txt').write_text(error,encoding='utf-8')
 if frontier:
  for p in AUD.glob('french_c1_unit06_*failure.txt'):p.unlink(missing_ok=True)
 result={'status':'PASS_TO_C1_UNIT07' if frontier else ('C1_UNIT06_PASS_UNIT07_PREP_PENDING' if sealed else 'C1_UNIT06_PENDING'),'date':'2026-08-17','starting_c1_passages':n,'ending_c1_passages':len(rows()),'b2_blob':h(B2),'c1_blob':h(C1),'c1_unit06_pass':sealed,'c1_unit07_frontier_prepared':frontier,'completed_stages':stages,'error':error}
 if sealed:
  lock=json.loads((AUD/'french_c1_unit06_frontier_lock.json').read_text());result.update({'accepted_c1_default':lock['accepted_c1_default_new_targets_per_standard_passage'],'default_is_hard_quota':False})
 if frontier:
  plan=json.loads((AUD/'french_c1_unit07_plan.json').read_text());probe=json.loads((AUD/'french_c1_unit07_target_probe.json').read_text());result.update({'unit07_theme':plan.get('theme'),'unit07_genres':plan.get('genres'),'remaining_fresh_source_terms':probe.get('fresh_count')})
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
 if not frontier:raise SystemExit(1)
if __name__=='__main__':main()

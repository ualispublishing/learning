#!/usr/bin/env python3
"""Serialize C1 through Unit03 and prepare exact Unit04 frontier.

A freshly generated Unit03 is restored only if its own strict review/frontier lock
fails. Once Unit03 is locked it remains canonical even if Unit04 preparation
later fails.
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
def main():
 AUD.mkdir(parents=True,exist_ok=True);before=C1.read_bytes() if C1.exists() else None;before_exists=C1.exists();before_n=len(rows());generated=False;unit03_sealed=False;frontier_pass=False;error=None;stages=[]
 try:
  run('complete_french_c1_unit02.py');stages.append('complete_or_verify_c1_unit02')
  lock2=json.loads((AUD/'french_c1_unit02_frontier_lock.json').read_text(encoding='utf-8'))
  if lock2.get('status')!='PASS' or lock2.get('last_sequence')!=12:raise AssertionError('C1 Unit02 not locked')
  for name in ('resolve_french_c1_unit03_plan.py','probe_french_c1_unit03_targets.py','select_french_c1_unit03_targets.py'):
   run(name);stages.append(name.removesuffix('.py'))
  rs=rows()
  if len(rs)==12:
   run('generate_french_c1_unit03_retry.py');generated=True;stages.append('generate_c1_unit03_quality_preflight')
  elif len(rs)==18 and rs[-1].get('id')=='fr-c1-u03-p06':stages.append('reuse_existing_c1_unit03_for_review')
  else:raise AssertionError(f'unsupported C1 frontier for Unit03: {len(rs)} rows')
  run_env('audit_french_c1_unit_generation.py',3);stages.append('audit_c1_unit03_generation')
  review=json.loads((AUD/'french_c1_unit03_generation_review.json').read_text(encoding='utf-8'))
  if review.get('status')!='PASS' or review.get('c1_canonical_blob')!=h(C1):raise AssertionError('Unit03 review/live mismatch')
  run_env('lock_french_c1_unit_frontier.py',3);stages.append('lock_c1_unit03')
  lock3=json.loads((AUD/'french_c1_unit03_frontier_lock.json').read_text(encoding='utf-8'))
  if lock3.get('status')!='PASS' or lock3.get('c1_canonical_blob')!=h(C1):raise AssertionError('Unit03 lock/live mismatch')
  unit03_sealed=True
  run_env('resolve_french_c1_unit_plan.py',4);stages.append('resolve_c1_unit04_plan')
  run_env('probe_french_c1_unit_targets.py',4);stages.append('probe_c1_unit04_targets')
  run_env('sync_french_c1_unit_frontier.py',3);stages.append('sync_c1_unit03_to_unit04');frontier_pass=True
 except Exception:
  error=traceback.format_exc();print(error)
  if generated and not unit03_sealed:
   if before_exists:C1.write_bytes(before)
   elif C1.exists():C1.unlink()
   stages.append('restore_preunit03_c1_after_strict_failure')
  elif unit03_sealed:stages.append('preserve_sealed_c1_unit03_despite_unit04_prep_failure')
  (AUD/'french_c1_unit03_pipeline_failure.txt').write_text(error,encoding='utf-8')
 if frontier_pass:
  for p in AUD.glob('french_c1_unit03_*failure.txt'):p.unlink(missing_ok=True)
 status='PASS_TO_C1_UNIT04' if frontier_pass else ('C1_UNIT03_PASS_UNIT04_PREP_PENDING' if unit03_sealed else 'C1_UNIT03_PENDING')
 result={'status':status,'date':'2026-08-17','starting_c1_passages':before_n,'ending_c1_passages':len(rows()),'b2_blob':h(B2),'c1_blob':h(C1),'c1_unit03_pass':unit03_sealed,'c1_unit04_frontier_prepared':frontier_pass,'completed_stages':stages,'error':error}
 if unit03_sealed:
  lock=json.loads((AUD/'french_c1_unit03_frontier_lock.json').read_text(encoding='utf-8'));result.update({'accepted_c1_default':lock['accepted_c1_default_new_targets_per_standard_passage'],'default_is_hard_quota':False})
 if frontier_pass:
  plan=json.loads((AUD/'french_c1_unit04_plan.json').read_text(encoding='utf-8'));probe=json.loads((AUD/'french_c1_unit04_target_probe.json').read_text(encoding='utf-8'));result.update({'unit04_theme':plan.get('theme'),'unit04_genres':plan.get('genres'),'remaining_fresh_source_terms':probe.get('fresh_count')})
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
 if not frontier_pass:raise SystemExit(1)
if __name__=='__main__':main()

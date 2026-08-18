#!/usr/bin/env python3
"""Serialize B2 seal -> C1 Unit01 calibration -> calibrated Unit02 frontier.

A newly generated C1 Unit01 is restored to its pre-run state if the strict
post-calibration audit fails. Independently valid B2 progress is preserved.
"""
from __future__ import annotations
import json,runpy,subprocess,sys,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[2];TOOLS=R/'reading/tools';AUD=R/'reading/audit';B2=R/'reading/french/b2/passages.jsonl';C1=R/'reading/french/c1/passages.jsonl';OUT=AUD/'french_c1_unit01_pipeline.json'
sys.path.insert(0,str(TOOLS))
def run(name):print(f'=== RUN {name} ===');runpy.run_path(str(TOOLS/name),run_name='__main__')
def load_rows(path):
 if not path.exists():return []
 return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
def hash_file(path):return subprocess.check_output(['git','hash-object',str(path)],text=True).strip() if path.exists() else None
def main():
 AUD.mkdir(parents=True,exist_ok=True);before_exists=C1.exists();before_bytes=C1.read_bytes() if before_exists else None;before_rows=len(load_rows(C1));stages=[];generated_here=False;b2_pass=False;c1_pass=False;error=None
 try:
  run('complete_french_b2_to_c1_frontier.py');stages.append('complete_or_verify_b2_to_c1_prep')
  b2audit=json.loads((AUD/'french_b2_generation_integrity.json').read_text(encoding='utf-8'));b2blob=hash_file(B2)
  if b2audit.get('status')!='PASS' or b2audit.get('canonical_blob')!=b2blob or b2audit.get('passages')!=60:raise AssertionError('B2 not sealed after completion orchestrator')
  b2_pass=True
  for name in ('prepare_french_c1_readiness.py','resolve_french_c1_unit01_plan.py','probe_french_c1_unit01_targets.py','select_french_c1_unit01_calibration_targets.py'):
   run(name);stages.append(name.removesuffix('.py'))
  current=load_rows(C1)
  if not current:
   run('generate_french_c1_unit01_calibration_retry.py');generated_here=True;stages.append('generate_c1_unit01_calibration_preflight')
  elif len(current)==6 and [r.get('id') for r in current]==[f'fr-c1-u01-p{i:02d}' for i in range(1,7)]:
   stages.append('reuse_existing_c1_unit01_for_strict_review')
  else:raise AssertionError(f'C1 canonical frontier unsupported for Unit01 calibration: {len(current)} rows')
  run('audit_french_c1_unit01_calibration.py');stages.append('audit_c1_unit01_calibration')
  review=json.loads((AUD/'french_c1_unit01_calibration_review.json').read_text(encoding='utf-8'));c1blob=hash_file(C1)
  if review.get('status')!='PASS' or review.get('c1_canonical_blob')!=c1blob:raise AssertionError('C1 Unit01 strict audit/live blob mismatch')
  run('lock_french_c1_unit01_frontier.py');stages.append('lock_c1_unit01')
  lock=json.loads((AUD/'french_c1_unit01_frontier_lock.json').read_text(encoding='utf-8'))
  if lock.get('status')!='PASS' or lock.get('c1_canonical_blob')!=c1blob:raise AssertionError('C1 Unit01 lock/live mismatch')
  run('resolve_french_c1_unit02_plan.py');stages.append('resolve_c1_unit02_plan')
  run('probe_french_c1_unit02_targets.py');stages.append('probe_c1_unit02_targets')
  run('sync_french_c1_unit01_frontier.py');stages.append('sync_c1_unit01_to_unit02')
  c1_pass=True
 except Exception:
  error=traceback.format_exc();print(error)
  if generated_here and not c1_pass:
   if before_exists:C1.write_bytes(before_bytes)
   elif C1.exists():C1.unlink()
   stages.append('restore_precalibration_c1_after_strict_failure')
  fail=AUD/'french_c1_unit01_pipeline_failure.txt';fail.write_text(error,encoding='utf-8')
 if c1_pass:
  for pat in ('french_c1_*failure.txt','french_c1_unit01_pipeline_failure.txt'):
   for p in AUD.glob(pat):p.unlink(missing_ok=True)
 result={'status':'PASS_TO_C1_UNIT02' if c1_pass else ('B2_PASS_C1_UNIT01_PENDING' if b2_pass else 'PARTIAL'),'date':'2026-08-17','starting_c1_passages':before_rows,'ending_c1_passages':len(load_rows(C1)),'b2_blob':hash_file(B2),'c1_blob':hash_file(C1),'b2_generation_integrity_pass':b2_pass,'c1_unit01_calibration_pass':c1_pass,'completed_stages':stages,'error':error}
 if c1_pass:
  review=json.loads((AUD/'french_c1_unit01_calibration_review.json').read_text(encoding='utf-8'));plan2=json.loads((AUD/'french_c1_unit02_plan.json').read_text(encoding='utf-8'));probe2=json.loads((AUD/'french_c1_unit02_target_probe.json').read_text(encoding='utf-8'));result.update({'c1_word_band':review['word_band'],'accepted_c1_default':review['accepted_c1_default_new_targets_per_standard_passage'],'accepted_default_is_hard_quota':review['accepted_default_is_hard_quota'],'unit02_theme':plan2.get('theme'),'unit02_genres':plan2.get('genres'),'remaining_fresh_source_terms':probe2.get('fresh_count')})
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
 if not c1_pass:raise SystemExit(1)
if __name__=='__main__':main()

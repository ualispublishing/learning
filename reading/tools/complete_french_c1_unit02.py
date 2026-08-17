#!/usr/bin/env python3
"""Serialize calibrated Unit01 -> guarded C1 Unit02 -> Unit03 frontier."""
from __future__ import annotations
import json,runpy,subprocess,sys,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[2];TOOLS=R/'reading/tools';AUD=R/'reading/audit';C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';OUT=AUD/'french_c1_unit02_pipeline.json';sys.path.insert(0,str(TOOLS))
def run(name):print(f'=== RUN {name} ===');runpy.run_path(str(TOOLS/name),run_name='__main__')
def rows():
 if not C1.exists():return []
 return [json.loads(x) for x in C1.read_text(encoding='utf-8').splitlines() if x.strip()]
def h(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip() if p.exists() else None
def main():
 AUD.mkdir(parents=True,exist_ok=True);before=C1.read_bytes() if C1.exists() else None;before_exists=C1.exists();before_n=len(rows());generated=False;pass2=False;error=None;stages=[]
 try:
  run('complete_french_c1_unit01_calibration.py');stages.append('complete_or_verify_c1_unit01')
  lock1=json.loads((AUD/'french_c1_unit01_frontier_lock.json').read_text(encoding='utf-8'))
  if lock1.get('status')!='PASS' or lock1.get('last_sequence')!=6:raise AssertionError('C1 Unit01 not locked after calibration orchestrator')
  for name in ('resolve_french_c1_unit02_plan.py','probe_french_c1_unit02_targets.py','select_french_c1_unit02_targets.py'):
   run(name);stages.append(name.removesuffix('.py'))
  rs=rows()
  if len(rs)==6:
   run('generate_french_c1_unit02.py');generated=True;stages.append('generate_c1_unit02')
  elif len(rs)==12 and rs[-1].get('id')=='fr-c1-u02-p06':stages.append('reuse_existing_c1_unit02_for_review')
  else:raise AssertionError(f'unsupported C1 frontier for Unit02: {len(rs)} rows')
  run('audit_french_c1_unit02_generation.py');stages.append('audit_c1_unit02_generation')
  review=json.loads((AUD/'french_c1_unit02_generation_review.json').read_text(encoding='utf-8'))
  if review.get('status')!='PASS' or review.get('c1_canonical_blob')!=h(C1):raise AssertionError('Unit02 review/live blob mismatch')
  run('lock_french_c1_unit02_frontier.py');stages.append('lock_c1_unit02')
  lock2=json.loads((AUD/'french_c1_unit02_frontier_lock.json').read_text(encoding='utf-8'))
  if lock2.get('status')!='PASS' or lock2.get('c1_canonical_blob')!=h(C1):raise AssertionError('Unit02 lock/live mismatch')
  run('resolve_french_c1_unit03_plan.py');stages.append('resolve_c1_unit03_plan')
  run('probe_french_c1_unit03_targets.py');stages.append('probe_c1_unit03_targets')
  run('sync_french_c1_unit02_frontier.py');stages.append('sync_c1_unit02_to_unit03');pass2=True
 except Exception:
  error=traceback.format_exc();print(error)
  if generated and not pass2:
   if before_exists:C1.write_bytes(before)
   elif C1.exists():C1.unlink()
   stages.append('restore_preunit02_c1_after_strict_failure')
  (AUD/'french_c1_unit02_pipeline_failure.txt').write_text(error,encoding='utf-8')
 if pass2:
  for p in AUD.glob('french_c1_unit02_*failure.txt'):p.unlink(missing_ok=True)
 result={'status':'PASS_TO_C1_UNIT03' if pass2 else 'C1_UNIT02_PENDING','date':'2026-08-17','starting_c1_passages':before_n,'ending_c1_passages':len(rows()),'b2_blob':h(B2),'c1_blob':h(C1),'c1_unit02_pass':pass2,'completed_stages':stages,'error':error}
 if pass2:
  lock=json.loads((AUD/'french_c1_unit02_frontier_lock.json').read_text(encoding='utf-8'));plan=json.loads((AUD/'french_c1_unit03_plan.json').read_text(encoding='utf-8'));probe=json.loads((AUD/'french_c1_unit03_target_probe.json').read_text(encoding='utf-8'));result.update({'accepted_c1_default':lock['accepted_c1_default_new_targets_per_standard_passage'],'default_is_hard_quota':False,'unit03_theme':plan.get('theme'),'unit03_genres':plan.get('genres'),'remaining_fresh_source_terms':probe.get('fresh_count')})
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
 if not pass2:raise SystemExit(1)
if __name__=='__main__':main()

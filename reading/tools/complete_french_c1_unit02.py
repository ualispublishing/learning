#!/usr/bin/env python3
"""Serialize calibrated Unit01 -> guarded C1 Unit02 -> Unit03 frontier.

When later C1 units already exist, verify the sealed first-twelve-passage prefix
and exit without replaying earlier units or rewinding durable state. A freshly
generated Unit02 is restored only if its own strict review/frontier lock fails.
"""
from __future__ import annotations
import json,runpy,subprocess,sys,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[2];TOOLS=R/'reading/tools';AUD=R/'reading/audit';C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';OUT=AUD/'french_c1_unit02_pipeline.json';sys.path.insert(0,str(TOOLS))
def run(name):print(f'=== RUN {name} ===');runpy.run_path(str(TOOLS/name),run_name='__main__')
def rows():
 if not C1.exists():return []
 return [json.loads(x) for x in C1.read_text(encoding='utf-8').splitlines() if x.strip()]
def h(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip() if p.exists() else None
def prefix_blob(n):
 lines=[x for x in C1.read_text(encoding='utf-8').splitlines() if x.strip()];text='\n'.join(lines[:n])+'\n'
 return subprocess.check_output(['git','hash-object','--stdin'],input=text,text=True).strip()
def main():
 AUD.mkdir(parents=True,exist_ok=True);before=C1.read_bytes() if C1.exists() else None;before_exists=C1.exists();before_n=len(rows());generated=False;unit02_sealed=False;frontier_pass=False;error=None;stages=[]
 if before_n>12:
  lock=json.loads((AUD/'french_c1_unit02_frontier_lock.json').read_text(encoding='utf-8'));review=json.loads((AUD/'french_c1_unit02_generation_review.json').read_text(encoding='utf-8'));pblob=prefix_blob(12);b2blob=h(B2)
  if lock.get('status')!='PASS' or lock.get('last_sequence')!=12 or lock.get('c1_canonical_blob')!=pblob or lock.get('b2_canonical_blob')!=b2blob:raise AssertionError('sealed C1 Unit02 prefix/lock mismatch in dependency mode')
  if review.get('status')!='PASS' or review.get('c1_canonical_blob')!=pblob:raise AssertionError('C1 Unit02 review/prefix mismatch in dependency mode')
  result={'status':'DEPENDENCY_PASS','date':'2026-08-17','starting_c1_passages':before_n,'ending_c1_passages':before_n,'b2_blob':b2blob,'c1_blob':h(C1),'c1_unit02_prefix_blob':pblob,'c1_unit02_pass':True,'completed_stages':['verify_existing_sealed_c1_unit02_prefix'],'accepted_c1_default':lock['accepted_c1_default_new_targets_per_standard_passage'],'default_is_hard_quota':False,'error':None};OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2));return
 try:
  run('complete_french_c1_unit01_calibration.py');stages.append('complete_or_verify_c1_unit01')
  lock1=json.loads((AUD/'french_c1_unit01_frontier_lock.json').read_text(encoding='utf-8'))
  if lock1.get('status')!='PASS' or lock1.get('last_sequence')!=6:raise AssertionError('C1 Unit01 not locked after calibration orchestrator')
  for name in ('resolve_french_c1_unit02_plan.py','probe_french_c1_unit02_targets.py','select_french_c1_unit02_targets.py'):
   run(name);stages.append(name.removesuffix('.py'))
  rs=rows()
  if len(rs)==6:
   run('generate_french_c1_unit02_retry.py');generated=True;stages.append('generate_c1_unit02_quality_preflight')
  elif len(rs)==12 and rs[-1].get('id')=='fr-c1-u02-p06':stages.append('reuse_existing_c1_unit02_for_review')
  else:raise AssertionError(f'unsupported C1 frontier for Unit02: {len(rs)} rows')
  run('audit_french_c1_unit02_generation.py');stages.append('audit_c1_unit02_generation')
  review=json.loads((AUD/'french_c1_unit02_generation_review.json').read_text(encoding='utf-8'))
  if review.get('status')!='PASS' or review.get('c1_canonical_blob')!=h(C1):raise AssertionError('Unit02 review/live blob mismatch')
  run('lock_french_c1_unit02_frontier.py');stages.append('lock_c1_unit02')
  lock2=json.loads((AUD/'french_c1_unit02_frontier_lock.json').read_text(encoding='utf-8'))
  if lock2.get('status')!='PASS' or lock2.get('c1_canonical_blob')!=h(C1):raise AssertionError('Unit02 lock/live mismatch')
  unit02_sealed=True
  run('resolve_french_c1_unit03_plan.py');stages.append('resolve_c1_unit03_plan');run('probe_french_c1_unit03_targets.py');stages.append('probe_c1_unit03_targets');run('sync_french_c1_unit02_frontier.py');stages.append('sync_c1_unit02_to_unit03');frontier_pass=True
 except Exception:
  error=traceback.format_exc();print(error)
  if generated and not unit02_sealed:
   if before_exists:C1.write_bytes(before)
   elif C1.exists():C1.unlink()
   stages.append('restore_preunit02_c1_after_strict_failure')
  elif unit02_sealed:stages.append('preserve_sealed_c1_unit02_despite_unit03_prep_failure')
  (AUD/'french_c1_unit02_pipeline_failure.txt').write_text(error,encoding='utf-8')
 if frontier_pass:
  for p in AUD.glob('french_c1_unit02_*failure.txt'):p.unlink(missing_ok=True)
 status='PASS_TO_C1_UNIT03' if frontier_pass else ('C1_UNIT02_PASS_UNIT03_PREP_PENDING' if unit02_sealed else 'C1_UNIT02_PENDING')
 result={'status':status,'date':'2026-08-17','starting_c1_passages':before_n,'ending_c1_passages':len(rows()),'b2_blob':h(B2),'c1_blob':h(C1),'c1_unit02_pass':unit02_sealed,'c1_unit03_frontier_prepared':frontier_pass,'completed_stages':stages,'error':error}
 if unit02_sealed:
  lock=json.loads((AUD/'french_c1_unit02_frontier_lock.json').read_text(encoding='utf-8'));result.update({'accepted_c1_default':lock['accepted_c1_default_new_targets_per_standard_passage'],'default_is_hard_quota':False})
 if frontier_pass:
  plan=json.loads((AUD/'french_c1_unit03_plan.json').read_text(encoding='utf-8'));probe=json.loads((AUD/'french_c1_unit03_target_probe.json').read_text(encoding='utf-8'));result.update({'unit03_theme':plan.get('theme'),'unit03_genres':plan.get('genres'),'remaining_fresh_source_terms':probe.get('fresh_count')})
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
 if not frontier_pass:raise SystemExit(1)
if __name__=='__main__':main()

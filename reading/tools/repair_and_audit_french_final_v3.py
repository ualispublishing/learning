#!/usr/bin/env python3
"""French final repair transaction v3: minimal confirmed repairs + audit v3."""
from __future__ import annotations
import json,runpy,traceback
from pathlib import Path

HERE=Path(__file__).resolve().parent
base_path=HERE/'repair_and_audit_french_final.py'
ns=runpy.run_path(str(base_path),run_name='french_final_repair_base')
C2=ns['C2'];A=ns['A'];OUT=A/'french_final_repair_transaction.json';AUDIT=A/'french_final_whole_audit.json';REJECTED=A/'french_final_whole_audit_rejected_candidate.json'

def repair_unit01_calibration(rows):
 by={r['id']:r for r in rows};r=by['fr-c2-u01-p06'];q=next(x for x in r['questions'] if x.get('id')=='q5')
 old='Quelle posture finale caractérise la calibration C2 ?'
 new='Quelle posture finale caractérise ce checkpoint conceptuel ?'
 if q.get('prompt')==old:q['prompt']=new
 elif 'calibration' in ns['norm'](q.get('prompt','')) if 'norm' in ns else ('calibration' in q.get('prompt','').casefold()):
  raise AssertionError('Unit01 q5 calibration wording changed; review before rewriting')
 r['revision']=int(r.get('revision',1))+1
 note='Final French review: removed learner-facing internal calibration wording from checkpoint question q5.'
 notes=r.setdefault('quality',{}).setdefault('notes',[])
 if note not in notes:notes.append(note)
 return rows

def main():
 original=C2.read_bytes();before=ns['h'](C2);stages=[];error=None;candidate_blob=None;audit_status=None
 try:
  current=ns['rows']()
  candidate=ns['regenerate_unit10_from_sealed_prefix'](current);stages.append('regenerate_unit10_shared_case_preflight')
  candidate=ns['apply_confirmed_repairs'](candidate);stages.append('apply_confirmed_unit04_unit05_unit06_repairs')
  candidate=repair_unit01_calibration(candidate);stages.append('remove_unit01_calibration_learner_leak')
  ns['write_rows'](candidate);candidate_blob=ns['h'](C2)
  runpy.run_path(str(HERE/'audit_french_final_whole_v3.py'),run_name='__main__')
  audit=json.loads(AUDIT.read_text(encoding='utf-8'));audit_status=audit.get('status')
  if audit_status!='PASS' or not audit.get('approval_ready') or audit.get('audit_pass_count',0)<10:raise AssertionError('French final audit v3 not approval-ready')
  if audit.get('level_blobs',{}).get('c2')!=candidate_blob:raise AssertionError('French final audit v3 not bound to candidate C2 blob')
  stages.append('pass_15_lens_whole_french_audit_v3')
  for p in [REJECTED,A/'french_final_workflow_failure.txt']:
   p.unlink(missing_ok=True)
 except Exception:
  error=traceback.format_exc();print(error)
  if AUDIT.exists():
   try:
    rejected=json.loads(AUDIT.read_text(encoding='utf-8'));rejected['candidate_rejected_and_canonical_restored']=True;rejected['restored_c2_blob']=before;REJECTED.write_text(json.dumps(rejected,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');AUDIT.unlink()
   except Exception:pass
  C2.write_bytes(original);stages.append('restore_original_c2_after_v3_failure')
 result={'status':'PASS_READY_FOR_FRENCH_APPROVAL' if error is None else 'FAIL_RESTORED','date':'2026-08-18','repair_version':3,'before_c2_blob':before,'candidate_repaired_c2_blob':candidate_blob,'final_c2_blob':ns['h'](C2),'audit_status':audit_status,'completed_stages':stages,'confirmed_repairs':['Unit01 P06 calibration learner-language leak','Unit04 P03/P04 role order','Unit05 P01 honest analytical genre reclassification','Unit05 P03/P04 role order','Unit06 reçu noun-sense alignment','Unit10 P03/P04 genuine shared-case pair'],'historical_frontier_locks_preserved':True,'error':error}
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
 if error is not None:raise SystemExit(1)
if __name__=='__main__':main()

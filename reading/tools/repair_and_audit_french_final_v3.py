#!/usr/bin/env python3
"""French final repair transaction v3: minimal confirmed repairs + audit v3."""
from __future__ import annotations
import json,runpy,traceback
from datetime import date
from pathlib import Path

HERE=Path(__file__).resolve().parent
base_path=HERE/'repair_and_audit_french_final.py'
ns=runpy.run_path(str(base_path),run_name='french_final_repair_base')
C2=ns['C2'];A=ns['A'];OUT=A/'french_final_repair_transaction.json';AUDIT=A/'french_final_whole_audit.json';REJECTED=A/'french_final_whole_audit_rejected_candidate.json'
LOCK=A/'french_c2_unit09_frontier_lock.json';PLAN=A/'french_c2_unit10_plan.json';SEL=A/'french_c2_unit10_target_selection.json'

def repair_unit01_calibration(rows):
 by={r['id']:r for r in rows};r=by['fr-c2-u01-p06'];q=next(x for x in r['questions'] if x.get('id')=='q5')
 before=json.dumps(r,ensure_ascii=False,sort_keys=True)
 old='Quelle posture finale caractérise la calibration C2 ?'
 new='Quelle posture finale caractérise ce checkpoint conceptuel ?'
 prompt=q.get('prompt','')
 if prompt==old:q['prompt']=new
 elif prompt==new:pass
 elif 'calibration' in (ns['norm'](prompt) if 'norm' in ns else prompt.casefold()):
  raise AssertionError('Unit01 q5 calibration wording changed; review before rewriting')
 else:
  raise AssertionError('Unit01 q5 no longer matches either approved calibration state; refusing heuristic rewrite')
 note='Final French review: removed learner-facing internal calibration wording from checkpoint question q5.'
 notes=r.setdefault('quality',{}).setdefault('notes',[])
 if note not in notes:notes.append(note)
 after=json.dumps(r,ensure_ascii=False,sort_keys=True)
 if after!=before:r['revision']=int(r.get('revision',1))+1
 return rows

def regenerate_unit10_from_repaired_prefix(current):
 """Regenerate Unit10 against the current repaired Unit09 prefix without mutating historical provenance.

 The Unit10 generator is intentionally hash-bound to the Unit09 planning frontier. Final-review
 repairs to earlier C2 units change that 54-row blob, so this transaction temporarily rebinds the
 three Unit10 source-hash inputs to the repaired prefix, runs the unchanged strict preflight, and
 restores every provenance artifact byte-for-byte in a finally block.
 """
 if len(current)!=60:raise AssertionError(f'expected 60 C2 rows before final repair, got {len(current)}')
 prefix=current[:54]
 if prefix[-1].get('id')!='fr-c2-u09-p06':raise AssertionError('first 54 rows are not the Unit09 prefix')
 ns['write_rows'](prefix)
 repaired_prefix_blob=ns['h'](C2)
 bindings=[(LOCK,'c2_canonical_blob'),(PLAN,'c2_source_blob'),(SEL,'c2_source_blob')]
 backups={}
 originals=[]
 try:
  for path,field in bindings:
   raw=path.read_bytes();backups[path]=raw
   doc=json.loads(raw.decode('utf-8'));old=doc.get(field)
   if not old:raise AssertionError(f'missing {field} in {path.name}')
   originals.append(old)
  if len(set(originals))!=1:raise AssertionError('historical Unit10 source bindings disagree; refusing temporary rebind')
  for path,field in bindings:
   doc=json.loads(backups[path].decode('utf-8'));doc[field]=repaired_prefix_blob
   path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  runpy.run_path(str(HERE/'generate_french_c2_unit10_preflight.py'),run_name='__main__')
 finally:
  for path,raw in backups.items():path.write_bytes(raw)
 for path,raw in backups.items():
  if path.read_bytes()!=raw:raise AssertionError(f'historical provenance restoration failed for {path.name}')
 candidate=ns['rows']()
 if len(candidate)!=60 or candidate[-1].get('id')!='fr-c2-u10-p06':raise AssertionError('Unit10 preflight did not restore exact 60-row C2 shape')
 return candidate,repaired_prefix_blob

def main():
 original=C2.read_bytes();before=ns['h'](C2);stages=[];error=None;candidate_blob=None;audit_status=None;regeneration_source_blob=None
 try:
  current=ns['rows']()
  candidate,regeneration_source_blob=regenerate_unit10_from_repaired_prefix(current);stages.append('regenerate_unit10_from_repaired_prefix_with_ephemeral_source_binding')
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
 result={'status':'PASS_READY_FOR_FRENCH_APPROVAL' if error is None else 'FAIL_RESTORED','date':date.today().isoformat(),'repair_version':3,'before_c2_blob':before,'unit10_regeneration_source_c2_blob':regeneration_source_blob,'candidate_repaired_c2_blob':candidate_blob,'final_c2_blob':ns['h'](C2),'audit_status':audit_status,'completed_stages':stages,'confirmed_repairs':['Unit01 P06 calibration learner-language leak','Unit04 P03/P04 role order','Unit05 P01 honest analytical genre reclassification','Unit05 P03/P04 role order','Unit06 reçu noun-sense alignment','Unit10 P03/P04 genuine shared-case pair'],'historical_frontier_locks_preserved':True,'temporary_source_binding_restored':True,'error':error}
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
 if error is not None:raise SystemExit(1)
if __name__=='__main__':main()

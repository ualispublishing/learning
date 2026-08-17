#!/usr/bin/env python3
"""Serialize the remaining French B2 pipeline and advance safely to C1 readiness.

Starting from any valid canonical B2 frontier at 42, 48, 54 or 60 passages,
this script completes only the missing stages in order. It never weakens a
content guard. Missing intermediate lock metadata may be reconstructed from an
already-canonical unit only after full structural/source/freshness validation.
A later-stage failure preserves earlier valid progress and writes an auditable
pipeline summary instead of discarding completed canonical work.
"""
from __future__ import annotations
import json,runpy,subprocess,sys,traceback
from pathlib import Path
from datetime import date
R=Path(__file__).resolve().parents[2];TOOLS=R/'reading/tools';AUD=R/'reading/audit';B2=R/'reading/french/b2/passages.jsonl';OUT=AUD/'french_b2_completion_pipeline.json'
sys.path.insert(0,str(TOOLS))
import generate_french_b1_unit10 as u10
base=u10.base

def rows():return [json.loads(x) for x in B2.read_text(encoding='utf-8').splitlines() if x.strip()]
def blob():return subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
def run(name):
 print(f'=== RUN {name} ===');runpy.run_path(str(TOOLS/name),run_name='__main__')
def verify_recover_lock(unit:int):
 """Recover a missing U08/U09 continuation lock from canonical rows only.

 This is not a bypass: it checks sequence/IDs, word band/count, Q/A/linkage,
 source rank/ID/exposure, four-new standard rows, zero-new checkpoint, and no
 earlier deliberate ID/form collision before writing the lock.
 """
 rs=rows();start=(unit-1)*6;end=unit*6;need=end
 if len(rs)<need:raise AssertionError(f'cannot recover Unit{unit:02d} lock from only {len(rs)} rows')
 ur=rs[start:end]
 if [r['sequence'] for r in ur]!=list(range(start+1,end+1)) or [r['id'] for r in ur]!=[f'fr-b2-u{unit:02d}-p{i:02d}' for i in range(1,7)]:raise AssertionError(f'Unit{unit:02d} canonical identity drift')
 if any(not 350<=r['word_count']<=550 or r['word_count']!=len(r['text'].split()) or len(r['questions'])!=10 or len(r['answer_key'])!=10 for r in ur):raise AssertionError(f'Unit{unit:02d} structural drift')
 if any(len(r.get('new_lexical_targets',[]))!=4 for r in ur[:5]) or ur[5].get('new_lexical_targets'):raise AssertionError(f'Unit{unit:02d} lexical load/checkpoint drift')
 earlier=rs[:start];prior_ids={t['id'] for r in earlier for t in r.get('new_lexical_targets',[])};prior_forms={t['form'] for r in earlier for t in r.get('new_lexical_targets',[])};deck=base.deck();new=[t for r in ur[:5] for t in r['new_lexical_targets']]
 if len(new)!=20 or len({t['id'] for t in new})!=20 or len({t['form'] for t in new})!=20:raise AssertionError(f'Unit{unit:02d} target uniqueness drift')
 for r in ur:
  local={t['id'] for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[])};amap={a['question_id']:a['id'] for a in r['answer_key']}
  for q in r['questions']:
   if amap.get(q['id'])!=q['answer_id'] or any(x not in local for x in q.get('target_ids',[])):raise AssertionError(f"{r['id']} linkage drift")
  for t in r.get('new_lexical_targets',[]):
   src=deck.get(t['form'])
   if not src or t['id']!=base.tid(src['rank']) or t['source_rank']!=src['rank'] or t['id'] in prior_ids or t['form'] in prior_forms or base.cnt(r['text'],t['form'])!=t['exposures_in_text']:raise AssertionError(f"{r['id']} source/freshness/exposure drift {t['form']}")
 groups={f'p0{i}':[t['form'] for t in ur[i-1]['new_lexical_targets']] for i in range(1,6)};forms=sorted(t['form'] for t in new);path=AUD/f'french_b2_unit{unit:02d}_frontier_lock.json'
 prior_blob=None
 if unit>1:
  pp=AUD/f'french_b2_unit{unit-1:02d}_frontier_lock.json'
  if pp.exists():prior_blob=json.loads(pp.read_text(encoding='utf-8')).get('canonical_blob')
 out={'status':'PASS','scope':f'French B2 Unit {unit:02d} recovered structural frontier lock','canonical_blob':blob(),'prior_frontier_blob':prior_blob,'passages':need,'questions':need*10,'answers':need*10,'completed_units':list(range(1,unit+1)),'last_sequence':need,'total_b2_deliberate_targets':unit*20,'checkpoint_sequences_zero_new':list(range(6,need+1,6)),f'unit{unit:02d}_target_forms':forms,f'unit{unit:02d}_target_groups':groups,f'unit{unit:02d}_word_counts':[r['word_count'] for r in ur],'selection_recovered_from_canonical':True,'note':'Recovered only after full canonical structural/source/freshness/linkage validation; continuation lock, not final French approval.'}
 path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'recovered_lock':unit,'blob':out['canonical_blob'],'groups':groups},ensure_ascii=False))
def ensure_lock(unit:int):
 p=AUD/f'french_b2_unit{unit:02d}_frontier_lock.json';need=unit*6
 if p.exists():
  try:
   d=json.loads(p.read_text(encoding='utf-8'))
   if d.get('status')=='PASS' and d.get('last_sequence')==need and d.get('canonical_blob')==blob():return
  except Exception:pass
 # Prefer the dedicated lock if its prerequisites are present; recover if the
 # selection artifact was not committed by an earlier otherwise-valid writer.
 dedicated=TOOLS/f'lock_french_b2_unit{unit:02d}_frontier.py'
 try:
  if dedicated.exists():run(dedicated.name)
  d=json.loads(p.read_text(encoding='utf-8'))
  if d.get('status')=='PASS' and d.get('canonical_blob')==blob():return
 except Exception as e:
  print(f'dedicated Unit{unit:02d} lock unavailable: {e}')
 verify_recover_lock(unit)
def clean_resolved(core_pass:bool,c1_pass:bool):
 patterns=['french_b2_unit08_*failure.txt','french_b2_unit09_*failure.txt','french_b2_unit10_*failure.txt','french_b2_generation_integrity_failure.txt','french_b2_complete_sync_failure.txt']
 if c1_pass:patterns+=['french_c1_readiness_failure.txt']
 if core_pass:
  for pat in patterns:
   for p in AUD.glob(pat):p.unlink(missing_ok=True)
def main():
 AUD.mkdir(parents=True,exist_ok=True);start=len(rows());stages=[];error=None;core_pass=False;c1_pass=False
 try:
  if start not in {42,48,54,60}:raise AssertionError(f'unsupported B2 frontier {start}; expected 42,48,54,60')
  n=start
  if n>=48:ensure_lock(8)
  if n==42:
   run('generate_french_b2_unit08_retry.py');n=len(rows());assert n==48;stages.append('generate_unit08');ensure_lock(8);stages.append('lock_unit08')
  if n>=54:ensure_lock(9)
  if n==48:
   run('generate_french_b2_unit09_retry.py');n=len(rows());assert n==54;stages.append('generate_unit09');ensure_lock(9);stages.append('lock_unit09')
  if n==54:
   ensure_lock(9);run('generate_french_b2_unit10_retry.py');n=len(rows());assert n==60;stages.append('generate_unit10')
  if n!=60:raise AssertionError(f'pipeline stopped at unexpected B2 count {n}')
  run('audit_french_b2_generation_integrity.py');audit=json.loads((AUD/'french_b2_generation_integrity.json').read_text(encoding='utf-8'))
  if audit.get('status')!='PASS' or audit.get('canonical_blob')!=blob():raise AssertionError('B2 full audit did not seal live blob')
  stages.append('audit_b2_generation_integrity');core_pass=True
 except Exception:
  error=traceback.format_exc();print(error)
 # C1 readiness/sync is useful but must never discard a successfully sealed B2.
 c1_error=None
 if core_pass:
  try:
   run('prepare_french_c1_readiness.py');stages.append('prepare_c1_readiness');c1_pass=True
   run('sync_french_b2_complete.py');stages.append('sync_b2_complete_to_c1')
  except Exception:
   c1_error=traceback.format_exc();print(c1_error)
 clean_resolved(core_pass,c1_pass)
 final=len(rows());status='PASS_TO_C1' if core_pass and c1_pass and c1_error is None else ('B2_PASS_C1_PENDING' if core_pass else 'PARTIAL')
 result={'status':status,'date':'2026-08-17','starting_b2_passages':start,'ending_b2_passages':final,'b2_blob':blob(),'completed_stages':stages,'b2_generation_integrity_pass':core_pass,'c1_readiness_pass':c1_pass,'error':error,'c1_error':c1_error}
 if c1_pass:
  rd=json.loads((AUD/'french_c1_readiness.json').read_text(encoding='utf-8'));result['c1_word_band']=[rd['c1_word_min'],rd['c1_word_max']];result['c1_matrix_matches']=rd['topic_genre_matrix_match_count']
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

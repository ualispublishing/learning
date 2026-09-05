#!/usr/bin/env python3
"""Apply fresh Arabic Gate C A1 Unit 3 comprehension/grounding repair."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/a1/passages.jsonl'
DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/a1_u03.json'
EXPECTED_GIT_BLOB='0d3c1620f720ba096c665e1ab9154f97772a0a0e'
EXPECTED_MANIFEST='e80ad4592de2638164b4341ea1e9fb6a0d4ecc2e5594b8bfd281af39466894c4'
OLD='أكمل: هذه تفاحة صغيرة؛ أريد تفاحة _____. '
# canonical has no trailing space; keep a separate exact value below
OLD_PROMPT='أكمل: هذه تفاحة صغيرة؛ أريد تفاحة _____. '
NEW_PROMPT='أكمل بما يعني واحدة إضافية: هذه تفاحة صغيرة؛ أريد تفاحة _____. '
NOTE='2026-09-05 fresh Gate C comprehension/answer-grounding review (A1 Unit 3): 60 question-answer pairs reviewed; one ambiguous transfer prompt repaired; no educator/publication release claim.'
def blob(data:bytes)->str: return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def main():
 if DECISION.exists(): raise SystemExit('duplicate Gate C A1 Unit 3 frontier')
 m=json.loads((READING/'STATE_MANIFEST.json').read_text());
 if m.get('aggregate_sha256')!=EXPECTED_MANIFEST: raise SystemExit('state manifest drift')
 r=json.loads((READING/'RELEASE_STATUS.json').read_text())['languages']['arabic']; c=r.get('comprehension_review_progress',{})
 if r.get('release_state')!='REOPEN_REQUIRED' or r.get('educator_release_ready') is not False: raise SystemExit('release boundary drift')
 if (c.get('fresh_records_reviewed'),c.get('fresh_qa_pairs_reviewed'),c.get('fresh_records_with_findings'),c.get('fresh_findings'))!=(12,120,2,2): raise SystemExit('Gate C frontier drift')
 if r['latest_deterministic_gate']['open_findings']!=1080: raise SystemExit('deterministic frontier drift')
 raw=PATH.read_bytes()
 if blob(raw)!=EXPECTED_GIT_BLOB: raise SystemExit('A1 canonical blob drift')
 rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]
 ids=[f'ar-a1-u03-p{i:02d}' for i in range(1,7)]
 if [rows[i].get('id') for i in range(12,18)]!=ids: raise SystemExit('Unit 3 id/order drift')
 before={x['id']:json.loads(json.dumps(x,ensure_ascii=False)) for x in rows[12:18]}
 t=rows[16]; qs={q['id']:q for q in t['questions']}; ans={a['question_id']:a for a in t['answer_key']}
 # tolerate no trailing space only; reject any semantic drift
 current=qs['q10']['prompt']
 expected='أكمل: هذه تفاحة صغيرة؛ أريد تفاحة _____. '
 if current.endswith(' '): exact_old=expected
 else: exact_old=expected.rstrip()
 if current!=exact_old or qs['q10'].get('target_ids')!=['ar-r97'] or ans['q10'].get('answer')!='أخرى': raise SystemExit('p05/q10 frontier drift')
 qs['q10']['prompt']=NEW_PROMPT.rstrip()
 t['revision']=int(t.get('revision',0))+1; notes=t['quality'].setdefault('notes',[])
 if NOTE not in notes: notes.append(NOTE)
 for i,pid in enumerate(ids,start=12):
  old=before[pid]; new=rows[i]
  if len(new['questions'])!=10 or len(new['answer_key'])!=10: raise SystemExit(f'{pid}: 10Q/10A drift')
  if {q['answer_id'] for q in new['questions']}!={a['id'] for a in new['answer_key']}: raise SystemExit(f'{pid}: linkage drift')
  if new['text']!=old['text'] or new['answer_key']!=old['answer_key']: raise SystemExit(f'{pid}: text/answer changed')
  if new.get('new_lexical_targets')!=old.get('new_lexical_targets') or new.get('review_lexical_targets')!=old.get('review_lexical_targets'): raise SystemExit(f'{pid}: lexical drift')
  for k in ('status','coverage_check','linguistic_review','pedagogical_review','answer_key_check','schema_check'):
   if new['quality'].get(k)!=old['quality'].get(k): raise SystemExit(f'{pid}: quality {k} changed')
  if pid!='ar-a1-u03-p05' and new!=old: raise SystemExit(f'{pid}: clean PASS record changed')
 PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in rows)+'\n')
 print(json.dumps({'gate':'C','level':'A1','unit':3,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':1,'fresh_findings':1,'repaired':'ar-a1-u03-p05/question q10','quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))
if __name__=='__main__': main()

#!/usr/bin/env python3
"""Validate canonical French B2 Unit06 and record its exact frontier blob."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];B2=R/'reading/french/b2/passages.jsonl';OUT=R/'reading/audit/french_b2_unit06_frontier_lock.json'
EXPECTED_B2='939ec4d433c8b5a8893093eca6f8e8a90ff2c1d4'
U6={'téléphone','compte','message','adresse','photo','nom','visage','voix','contrôler','suivre','connaître','cacher','client','bureau','demander','répondre','vendre','chercher','trouver','monde'}
def main():
 blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if blob!=EXPECTED_B2:raise AssertionError(f'B2 Unit06 blob drift: {blob} != {EXPECTED_B2}')
 rows=[json.loads(x) for x in B2.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=36 or [r['sequence'] for r in rows]!=list(range(1,37)) or rows[-1]['id']!='fr-b2-u06-p06':raise AssertionError('B2 Unit06 frontier not canonical')
 if any(not 350<=r['word_count']<=550 or r['word_count']!=len(r['text'].split()) or len(r['questions'])!=10 or len(r['answer_key'])!=10 for r in rows):raise AssertionError('B2 structural/count failure')
 all_ids=set();all_forms=set()
 for unit in range(6):
  start=unit*6;new=[t for r in rows[start:start+5] for t in r['new_lexical_targets']];ids={t['id'] for t in new};forms={t['form'] for t in new}
  if len(new)!=20 or len(ids)!=20 or len(forms)!=20:raise AssertionError(f'Unit{unit+1:02d} target count/uniqueness drift')
  if all_ids&ids or all_forms&forms:raise AssertionError('cross-unit B2 target collision')
  all_ids|=ids;all_forms|=forms
 if {t['form'] for r in rows[30:35] for t in r['new_lexical_targets']}!=U6:raise AssertionError('Unit06 target-set drift')
 if any(rows[i]['new_lexical_targets'] for i in (5,11,17,23,29,35)):raise AssertionError('checkpoint new-target failure')
 pair='fr-b2-u06-data-control-opinions'
 if rows[32]['paired_text_group']!=pair or rows[33]['paired_text_group']!=pair:raise AssertionError('Unit06 paired-opinion link failure')
 for r in rows:
  local={t['id'] for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[])};amap={a['question_id']:a['id'] for a in r['answer_key']}
  for q in r['questions']:
   if amap.get(q['id'])!=q['answer_id'] or any(x not in local for x in q.get('target_ids',[])):raise AssertionError(f"{r['id']} linkage failure")
 out={'status':'PASS','scope':'French B2 Unit 06 frontier lock','canonical_blob':blob,'passages':36,'questions':360,'answers':360,'completed_units':[1,2,3,4,5,6],'last_sequence':36,'total_b2_deliberate_targets':120,'checkpoint_sequences_zero_new':[6,12,18,24,30,36],'unit06_target_forms':sorted(U6),'unit06_word_counts':[r['word_count'] for r in rows[30:36]],'paired_text_group':pair,'note':'Lightweight frontier lock for safe B2 Unit07 continuation; not final French approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()

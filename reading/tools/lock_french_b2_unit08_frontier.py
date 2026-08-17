#!/usr/bin/env python3
"""Validate canonical French B2 Unit08 and record the exact continuation blob.

Unlike the generator, this lock does not assume the post-Unit08 blob in advance.
It requires the sealed Unit07 prefix state plus exactly six valid Unit08 rows and
the audited target selection, then records the resulting live blob for Unit09.
"""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2]
B2=R/'reading/french/b2/passages.jsonl';U7=R/'reading/audit/french_b2_unit07_frontier_lock.json';SEL=R/'reading/audit/french_b2_unit08_target_selection.json';OUT=R/'reading/audit/french_b2_unit08_frontier_lock.json'
def main():
 u7=json.loads(U7.read_text(encoding='utf-8'));sel=json.loads(SEL.read_text(encoding='utf-8'))
 if u7.get('status')!='PASS' or u7.get('last_sequence')!=42:raise AssertionError('Unit07 lock missing/stale')
 if sel.get('status')!='PASS' or sel.get('b2_source_blob')!=u7.get('canonical_blob') or sel.get('selected_count')!=20:raise AssertionError('Unit08 target selection missing/stale')
 rows=[json.loads(x) for x in B2.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=48 or [r['sequence'] for r in rows]!=list(range(1,49)) or rows[-1]['id']!='fr-b2-u08-p06':raise AssertionError('B2 Unit08 frontier not canonical')
 if [r['id'] for r in rows[42:]]!=[f'fr-b2-u08-p{i:02d}' for i in range(1,7)]:raise AssertionError('Unit08 IDs drift')
 if any(not 350<=r['word_count']<=550 or r['word_count']!=len(r['text'].split()) or len(r['questions'])!=10 or len(r['answer_key'])!=10 for r in rows):raise AssertionError('B2 structural/count failure')
 all_ids=set();all_forms=set()
 for unit in range(8):
  new=[t for r in rows[unit*6:unit*6+5] for t in r.get('new_lexical_targets',[])];ids={t['id'] for t in new};forms={t['form'] for t in new}
  if len(new)!=20 or len(ids)!=20 or len(forms)!=20:raise AssertionError(f'Unit{unit+1:02d} target count/uniqueness drift')
  if all_ids&ids or all_forms&forms:raise AssertionError('cross-unit B2 target collision')
  all_ids|=ids;all_forms|=forms
 expected={x['form'] for x in sel['selected']};actual={t['form'] for r in rows[42:47] for t in r['new_lexical_targets']}
 if actual!=expected:raise AssertionError(f'Unit08 target selection drift: actual={sorted(actual)} expected={sorted(expected)}')
 if any(rows[i]['new_lexical_targets'] for i in (5,11,17,23,29,35,41,47)):raise AssertionError('checkpoint new-target failure')
 for r in rows:
  local={t['id'] for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[])};amap={a['question_id']:a['id'] for a in r['answer_key']}
  for q in r['questions']:
   if amap.get(q['id'])!=q['answer_id'] or any(x not in local for x in q.get('target_ids',[])):raise AssertionError(f"{r['id']} linkage failure")
 blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 groups=sel['passage_groups']
 out={'status':'PASS','scope':'French B2 Unit 08 frontier lock','canonical_blob':blob,'prior_unit07_blob':u7['canonical_blob'],'passages':48,'questions':480,'answers':480,'completed_units':[1,2,3,4,5,6,7,8],'last_sequence':48,'total_b2_deliberate_targets':160,'checkpoint_sequences_zero_new':[6,12,18,24,30,36,42,48],'unit08_target_forms':sorted(expected),'unit08_target_groups':groups,'unit08_semantic_fallback_count':sel.get('semantic_fallback_count',0),'unit08_word_counts':[r['word_count'] for r in rows[42:48]],'note':'Lightweight structural frontier lock for safe B2 Unit09 continuation; not final French approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()

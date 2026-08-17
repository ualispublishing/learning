#!/usr/bin/env python3
"""Validate canonical French B2 Unit07 and record its exact continuation lock."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];B2=R/'reading/french/b2/passages.jsonl';OUT=R/'reading/audit/french_b2_unit07_frontier_lock.json'
EXPECTED='5ff899452326f679b7c16b0ff33d8f38fa99719a'
U7={'film','musique','chanson','jouer','histoire','lire','écrire','mot','ton','sens','sujet','imaginer','avis','aimer','beau','drôle','vie','présent','société','politique'}
def main():
 blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if blob!=EXPECTED:raise AssertionError(f'B2 Unit07 blob drift: {blob} != {EXPECTED}')
 rows=[json.loads(x) for x in B2.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=42 or [r['sequence'] for r in rows]!=list(range(1,43)) or rows[-1]['id']!='fr-b2-u07-p06':raise AssertionError('B2 Unit07 frontier not canonical')
 if any(not 350<=r['word_count']<=550 or r['word_count']!=len(r['text'].split()) or len(r['questions'])!=10 or len(r['answer_key'])!=10 for r in rows):raise AssertionError('B2 structural/count failure')
 ids=set();forms=set()
 for unit in range(7):
  new=[t for r in rows[unit*6:unit*6+5] for t in r['new_lexical_targets']];ui={t['id'] for t in new};uf={t['form'] for t in new}
  if len(new)!=20 or len(ui)!=20 or len(uf)!=20:raise AssertionError(f'Unit{unit+1:02d} target drift')
  if ids&ui or forms&uf:raise AssertionError('cross-unit target collision')
  ids|=ui;forms|=uf
 if {t['form'] for r in rows[36:41] for t in r['new_lexical_targets']}!=U7:raise AssertionError('Unit07 target-set drift')
 if any(rows[i]['new_lexical_targets'] for i in (5,11,17,23,29,35,41)):raise AssertionError('checkpoint new-target failure')
 for r in rows:
  local={t['id'] for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[])};amap={a['question_id']:a['id'] for a in r['answer_key']}
  for q in r['questions']:
   if amap.get(q['id'])!=q['answer_id'] or any(x not in local for x in q.get('target_ids',[])):raise AssertionError(f"{r['id']} linkage failure")
 out={'status':'PASS','scope':'French B2 Unit 07 frontier lock','canonical_blob':blob,'passages':42,'questions':420,'answers':420,'completed_units':[1,2,3,4,5,6,7],'last_sequence':42,'total_b2_deliberate_targets':140,'checkpoint_sequences_zero_new':[6,12,18,24,30,36,42],'unit07_target_forms':sorted(U7),'unit07_word_counts':[r['word_count'] for r in rows[36:42]],'note':'Lightweight frontier lock for safe B2 Unit08 continuation; not final French approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()

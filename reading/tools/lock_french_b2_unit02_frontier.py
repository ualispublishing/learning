#!/usr/bin/env python3
"""Validate the canonical B2 Unit 02 frontier and record its exact blob lock.

This is a lightweight generation frontier lock, not a final audit.
"""
from __future__ import annotations
import json,subprocess
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
B2=REPO/'reading/french/b2/passages.jsonl'; OUT=REPO/'reading/audit/french_b2_unit02_frontier_lock.json'
EXPECTED_U1={'supposer','cause','effet','preuve','sécurité','protéger','suffire','moyen','public','apporter','libre','accepter','tromper','certain','général','ressembler','apprécier','ainsi','valoir','intéresser'}
EXPECTED_U2={'promettre','avenir','attendre','confiance','grave','calmer','solution','responsabilité','partager','opinion','secret','surtout','ordre','lieu','coût','préférer','ramener','pareil','lumière','pousser'}

def main():
 rows=[json.loads(x) for x in B2.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=12 or [r['sequence'] for r in rows]!=list(range(1,13)) or rows[-1]['id']!='fr-b2-u02-p06': raise AssertionError('B2 Unit02 frontier not canonical')
 if any(not 350<=r['word_count']<=550 or r['word_count']!=len(r['text'].split()) for r in rows): raise AssertionError('B2 word-band/count failure')
 if any(len(r['questions'])!=10 or len(r['answer_key'])!=10 for r in rows): raise AssertionError('assessment count failure')
 u1=[t for r in rows[:5] for t in r['new_lexical_targets']]; u2=[t for r in rows[6:11] for t in r['new_lexical_targets']]
 if {t['form'] for t in u1}!=EXPECTED_U1 or len({t['id'] for t in u1})!=20: raise AssertionError('Unit01 target drift')
 if {t['form'] for t in u2}!=EXPECTED_U2 or len({t['id'] for t in u2})!=20: raise AssertionError('Unit02 target drift')
 if {t['id'] for t in u1}&{t['id'] for t in u2} or {t['form'] for t in u1}&{t['form'] for t in u2}: raise AssertionError('B2 U1/U2 target collision')
 if rows[5]['new_lexical_targets'] or rows[11]['new_lexical_targets']: raise AssertionError('checkpoint new-target failure')
 for r in rows:
  local={t['id'] for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[])}
  amap={a['question_id']:a['id'] for a in r['answer_key']}
  for q in r['questions']:
   if amap.get(q['id'])!=q['answer_id'] or any(x not in local for x in q.get('target_ids',[])): raise AssertionError(f"{r['id']} linkage failure")
 blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 out={'status':'PASS','scope':'French B2 Unit 02 frontier lock','canonical_blob':blob,'passages':12,'questions':120,'answers':120,'completed_units':[1,2],'last_sequence':12,'unit01_targets':20,'unit02_targets':20,'unit02_checkpoint_zero_new':True,'note':'Lightweight source frontier lock for the next guarded B2 unit; not final French approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()

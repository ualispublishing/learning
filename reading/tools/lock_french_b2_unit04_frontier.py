#!/usr/bin/env python3
"""Validate canonical French B2 Unit04 and record its exact frontier blob."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
REPO=Path(__file__).resolve().parents[2];B2=REPO/'reading/french/b2/passages.jsonl';OUT=REPO/'reading/audit/french_b2_unit04_frontier_lock.json'
EXPECTED_B2='125d8c87641ee5a0fbd958a415ede82f95c40eff'
SETS=[
{'supposer','cause','effet','preuve','sécurité','protéger','suffire','moyen','public','apporter','libre','accepter','tromper','certain','général','ressembler','apprécier','ainsi','valoir','intéresser'},
{'promettre','décider','attendre','confiance','grave','calmer','choisir','problème','maintenir','simplement','secret','surtout','ordre','lieu','doute','préférer','ramener','pareil','lumière','pousser'},
{'juste','chance','groupe','réussir','permettre','refuser','accord','obliger','vérité','vrai','faux','mentir','victime','dommage','aider','difficile','garder','donner','loi','guerre'},
{'coin','côté','arbre','air','voiture','proche','besoin','simple','construire','ouvrir','fermer','utiliser','haut','bas','monter','descendre','entrer','sortir','servir','nouveau'}]
def main():
 blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if blob!=EXPECTED_B2:raise AssertionError(f'B2 Unit04 blob drift: {blob}')
 rows=[json.loads(x) for x in B2.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=24 or [r['sequence'] for r in rows]!=list(range(1,25)) or rows[-1]['id']!='fr-b2-u04-p06':raise AssertionError('B2 Unit04 frontier not canonical')
 if any(not 350<=r['word_count']<=550 or r['word_count']!=len(r['text'].split()) or len(r['questions'])!=10 or len(r['answer_key'])!=10 for r in rows):raise AssertionError('B2 structural/count failure')
 all_ids=set();all_forms=set()
 for unit,expected in enumerate(SETS):
  start=unit*6;new=[t for r in rows[start:start+5] for t in r['new_lexical_targets']]
  ids={t['id'] for t in new};forms={t['form'] for t in new}
  if len(new)!=20 or forms!=expected or len(ids)!=20:raise AssertionError(f'Unit{unit+1:02d} target drift')
  if all_ids&ids or all_forms&forms:raise AssertionError('cross-unit target collision')
  all_ids|=ids;all_forms|=forms
 if any(rows[i]['new_lexical_targets'] for i in (5,11,17,23)):raise AssertionError('checkpoint new-target failure')
 for r in rows:
  local={t['id'] for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[])};amap={a['question_id']:a['id'] for a in r['answer_key']}
  for q in r['questions']:
   if amap.get(q['id'])!=q['answer_id'] or any(x not in local for x in q.get('target_ids',[])):raise AssertionError(f"{r['id']} linkage failure")
 out={'status':'PASS','scope':'French B2 Unit 04 frontier lock','canonical_blob':blob,'passages':24,'questions':240,'answers':240,'completed_units':[1,2,3,4],'last_sequence':24,'total_b2_deliberate_targets':80,'checkpoint_sequences_zero_new':[6,12,18,24],'unit04_target_forms':sorted(SETS[3]),'unit04_word_counts':[r['word_count'] for r in rows[18:24]],'note':'Lightweight frontier lock for safe B2 Unit05 continuation; not final French approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Validate canonical French B2 Unit05 and record its exact frontier blob.

This script is intentionally inert until invoked after Unit05 canonicalization.
It is a lightweight continuation lock, not final French approval.
"""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];B2=R/'reading/french/b2/passages.jsonl';OUT=R/'reading/audit/french_b2_unit05_frontier_lock.json'
SETS=[
{'supposer','cause','effet','preuve','sécurité','protéger','suffire','moyen','public','apporter','libre','accepter','tromper','certain','général','ressembler','apprécier','ainsi','valoir','intéresser'},
{'promettre','décider','attendre','confiance','grave','calmer','choisir','problème','maintenir','simplement','secret','surtout','ordre','lieu','doute','préférer','ramener','pareil','lumière','pousser'},
{'juste','chance','groupe','réussir','permettre','refuser','accord','obliger','vérité','vrai','faux','mentir','victime','dommage','aider','difficile','garder','donner','loi','guerre'},
{'coin','côté','arbre','air','voiture','proche','besoin','simple','construire','ouvrir','fermer','utiliser','haut','bas','monter','descendre','entrer','sortir','servir','nouveau'},
{'été','année','mois','nuit','passé','long','changer','continuer','rester','devenir','compter','montrer','croire','penser','sembler','comprendre','préparer','action','mer','terre'}]

def main():
 rows=[json.loads(x) for x in B2.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=30 or [r['sequence'] for r in rows]!=list(range(1,31)) or rows[-1]['id']!='fr-b2-u05-p06':raise AssertionError('B2 Unit05 frontier not canonical')
 if any(not 350<=r['word_count']<=550 or r['word_count']!=len(r['text'].split()) or len(r['questions'])!=10 or len(r['answer_key'])!=10 for r in rows):raise AssertionError('B2 structural/count failure')
 all_ids=set();all_forms=set()
 for unit,expected in enumerate(SETS):
  start=unit*6;new=[t for r in rows[start:start+5] for t in r['new_lexical_targets']];ids={t['id'] for t in new};forms={t['form'] for t in new}
  if len(new)!=20 or forms!=expected or len(ids)!=20:raise AssertionError(f'Unit{unit+1:02d} target drift')
  if all_ids&ids or all_forms&forms:raise AssertionError('cross-unit target collision')
  all_ids|=ids;all_forms|=forms
 if any(rows[i]['new_lexical_targets'] for i in (5,11,17,23,29)):raise AssertionError('checkpoint new-target failure')
 for r in rows:
  local={t['id'] for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[])};amap={a['question_id']:a['id'] for a in r['answer_key']}
  for q in r['questions']:
   if amap.get(q['id'])!=q['answer_id'] or any(x not in local for x in q.get('target_ids',[])):raise AssertionError(f"{r['id']} linkage failure")
 blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 out={'status':'PASS','scope':'French B2 Unit 05 frontier lock','canonical_blob':blob,'passages':30,'questions':300,'answers':300,'completed_units':[1,2,3,4,5],'last_sequence':30,'total_b2_deliberate_targets':100,'checkpoint_sequences_zero_new':[6,12,18,24,30],'unit05_target_forms':sorted(SETS[4]),'unit05_word_counts':[r['word_count'] for r in rows[24:30]],'note':'Lightweight frontier lock for safe B2 Unit06 continuation; not final French approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Validate canonical French B2 Unit03 and record its exact frontier blob.

This is a lightweight generation lock for safe continuation, not final French
approval.
"""
from __future__ import annotations
import json,subprocess
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
B2=REPO/'reading/french/b2/passages.jsonl'; OUT=REPO/'reading/audit/french_b2_unit03_frontier_lock.json'
U1={'supposer','cause','effet','preuve','sécurité','protéger','suffire','moyen','public','apporter','libre','accepter','tromper','certain','général','ressembler','apprécier','ainsi','valoir','intéresser'}
U2={'promettre','décider','attendre','confiance','grave','calmer','choisir','problème','maintenir','simplement','secret','surtout','ordre','lieu','doute','préférer','ramener','pareil','lumière','pousser'}
U3={'juste','chance','groupe','réussir','permettre','refuser','accord','obliger','vérité','vrai','faux','mentir','victime','dommage','aider','difficile','garder','donner','loi','guerre'}

def main():
 rows=[json.loads(x) for x in B2.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=18 or [r['sequence'] for r in rows]!=list(range(1,19)) or rows[-1]['id']!='fr-b2-u03-p06': raise AssertionError('B2 Unit03 frontier not canonical')
 if any(not 350<=r['word_count']<=550 or r['word_count']!=len(r['text'].split()) for r in rows): raise AssertionError('B2 word-band/count failure')
 if any(len(r['questions'])!=10 or len(r['answer_key'])!=10 for r in rows): raise AssertionError('assessment count failure')
 sets=[]
 for start,expected in ((0,U1),(6,U2),(12,U3)):
  new=[t for r in rows[start:start+5] for t in r['new_lexical_targets']]
  if len(new)!=20 or {t['form'] for t in new}!=expected or len({t['id'] for t in new})!=20: raise AssertionError(f'Unit target drift at rows {start+1}-{start+5}')
  sets.append(({t['id'] for t in new},{t['form'] for t in new}))
 if any(rows[i]['new_lexical_targets'] for i in (5,11,17)): raise AssertionError('checkpoint new-target failure')
 all_ids=set();all_forms=set()
 for ids,forms in sets:
  if all_ids&ids or all_forms&forms: raise AssertionError('cross-unit B2 target collision')
  all_ids|=ids;all_forms|=forms
 for r in rows:
  local={t['id'] for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[])}
  amap={a['question_id']:a['id'] for a in r['answer_key']}
  for q in r['questions']:
   if amap.get(q['id'])!=q['answer_id'] or any(x not in local for x in q.get('target_ids',[])): raise AssertionError(f"{r['id']} linkage failure")
 blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 out={'status':'PASS','scope':'French B2 Unit 03 frontier lock','canonical_blob':blob,'passages':18,'questions':180,'answers':180,'completed_units':[1,2,3],'last_sequence':18,'targets_per_completed_unit':20,'total_b2_deliberate_targets':60,'checkpoint_sequences_zero_new':[6,12,18],'unit03_target_forms':sorted(U3),'unit03_word_counts':[r['word_count'] for r in rows[12:18]],'note':'Lightweight source frontier lock for safe B2 Unit04 continuation; not final French approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()

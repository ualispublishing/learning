#!/usr/bin/env python3
"""Narrow post-calibration language repair for French B2 Unit 01.

Repairs learner-facing phrasing only.  The six-passage structure, 20-target pool,
word band, paired viewpoints, questions/answers, and all curriculum guards remain.
"""
from __future__ import annotations
import json,subprocess
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_b1_unit10 as u10
base=u10.base
REPO=Path(__file__).resolve().parents[2]
CANON=REPO/'reading/french/b2/passages.jsonl'
SCHEMA=REPO/'reading/schema/passage.schema.json'
EXPECTED_B2_BLOB='c770284cfd08cb500503af474890ff21fe90d19c'

def main():
    got=subprocess.check_output(['git','hash-object',str(CANON)],text=True).strip()
    if got!=EXPECTED_B2_BLOB: raise AssertionError(f'B2 blob drift: {got} != {EXPECTED_B2_BLOB}')
    rows=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
    if len(rows)!=6 or rows[-1]['id']!='fr-b2-u01-p06': raise AssertionError('unexpected B2 calibration frontier')
    byid={r['id']:r for r in rows}

    p3=byid['fr-b2-u01-p03']
    old="le public peut avoir l’impression que les choix méthodologiques ont été faits hors de sa portée."
    new="le public peut avoir l’impression que les choix méthodologiques ont été faits sans qu’il puisse en suivre le raisonnement."
    if p3['text'].count(old)!=1: raise AssertionError('P03 phrasing anchor missing')
    p3['text']=p3['text'].replace(old,new)

    p4=byid['fr-b2-u01-p04']
    old="mais à montrer ce à quoi chaque donnée peut ou ne peut pas ressembler."
    new="mais à montrer à quoi chaque donnée peut ressembler sans forcément représenter l’ensemble de la population."
    if p4['text'].count(old)!=1: raise AssertionError('P04 phrasing anchor missing')
    p4['text']=p4['text'].replace(old,new)

    p6=byid['fr-b2-u01-p06']
    old="à identifier la stance d’un auteur lorsqu’il limite ou renforce une affirmation."
    new="à identifier la position d’un auteur lorsqu’il limite ou renforce une affirmation."
    if p6['text'].count(old)!=1: raise AssertionError('P06 stance anchor missing')
    p6['text']=p6['text'].replace(old,new)
    q7=next(q for q in p6['questions'] if q['id']=='q7')
    if q7['prompt']!="Quelle stance finale le checkpoint adopte-t-il face à l’incertitude ?": raise AssertionError('P06 q7 prompt anchor missing')
    q7['prompt']="Quelle position finale le checkpoint adopte-t-il face à l’incertitude ?"

    V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')))
    for r in rows:
        r['word_count']=len(r['text'].split())
        errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
        if errs: raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:6]]}")
        if not 350<=r['word_count']<=550: raise AssertionError(f"{r['id']}: B2 word band {r['word_count']}")
        if len(r['questions'])!=10 or len(r['answer_key'])!=10: raise AssertionError(f"{r['id']}: assessment count")
        local={t['id'] for fld in ('new_lexical_targets','review_lexical_targets') for t in r.get(fld,[]) if isinstance(t,dict)}
        amap={a['question_id']:a['id'] for a in r['answer_key']}
        for q in r['questions']:
            if amap.get(q['id'])!=q['answer_id'] or any(tid not in local for tid in q.get('target_ids',[])): raise AssertionError(f"{r['id']} {q['id']}: linkage")
        for t in r.get('new_lexical_targets',[]):
            actual=base.cnt(r['text'],t['form'])
            if actual!=t['exposures_in_text']: raise AssertionError(f"{r['id']}: exposure drift {t['form']} {actual} != {t['exposures_in_text']}")
        for t in r.get('review_lexical_targets',[]):
            if t['representation'] in {'running_text','summary'} and base.cnt(r['text'],t['form'])<1: raise AssertionError(f"{r['id']}: invisible review {t['form']}")
    if 'stance' in '\n'.join(r['text'] for r in rows) or any('stance' in q['prompt'] for r in rows for q in r['questions']): raise AssertionError('learner-facing stance Anglicism remains')
    CANON.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
    print(json.dumps({'status':'PASS','repair':'B2 Unit01 calibration language','word_counts':{r['id']:r['word_count'] for r in rows}},ensure_ascii=False))
if __name__=='__main__': main()

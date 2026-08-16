#!/usr/bin/env python3
"""Post-calibration semantic/linguistic precision repair for French B1 Unit 01.

The initial guarded unit is mechanically valid. This targeted pass tightens the
teaching sense of `impliquer` to the validated root gloss (entail/imply) rather
than relying on the broader participation use, and smooths two minor phrases.
"""
from __future__ import annotations
import json,re,subprocess
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_a2_unit03 as base

REPO=Path(__file__).resolve().parents[2]
CANON=REPO/'reading'/'french'/'b1'/'passages.jsonl'
SCHEMA=REPO/'reading'/'schema'/'passage.schema.json'
OUT=REPO/'reading'/'audit'/'french_b1_unit01_calibration_review.json'
EXPECTED_BLOB='43352e6babf1851bc05bbecbc2346cfc3117e76b'
FORMS=('poursuivre','époque','trace','convaincre','position','impliquer','machine','code','recommencer','étranger','peuple','futur','regretter','profiter','ennui')

def qmap(r): return {q['id']:q for q in r['questions']}
def amap(r): return {a['question_id']:a for a in r['answer_key']}
def recalc(r):
    r['word_count']=len(r['text'].split())
    r['sentence_count']=max(1,len(re.findall(r'[.!?](?:[»”"])?',r['text'])))
    for t in r.get('new_lexical_targets',[]):
        t['exposures_in_text']=base.cnt(r['text'],t['form'])

def main():
    blob=subprocess.check_output(['git','hash-object',str(CANON)],text=True).strip()
    if blob!=EXPECTED_BLOB: raise AssertionError(f'B1 calibration blob drift: {blob} != {EXPECTED_BLOB}')
    rows=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
    if len(rows)!=6 or rows[-1]['id']!='fr-b1-u01-p06': raise AssertionError('unexpected B1 Unit01 frontier')
    byid={r['id']:r for r in rows}

    p2=byid['fr-b1-u01-p02']
    p2['text']="""Quelques jours plus tard, Camille assiste à une réunion sur la rénovation d’une petite salle communautaire. Le projet semble simple : déplacer la cuisine, agrandir l’espace principal et remplacer une fenêtre ancienne. Pourtant, les habitants n’ont pas tous la même position. Certains veulent commencer les travaux rapidement, tandis que d’autres craignent que le coût augmente et demandent davantage d’informations.

Sami prépare une courte présentation pour convaincre le groupe de conserver une partie du budget pour l’accessibilité. Il comprend vite que convaincre ne consiste pas seulement à parler plus fort. Il doit présenter des raisons qui répondent à la position des personnes hésitantes. Une résidente explique par exemple que déplacer la cuisine pourrait impliquer des travaux supplémentaires et réduire l’espace disponible. Sami modifie alors son schéma et montre une option qui garde la cuisine au même endroit tout en améliorant l’entrée.

La responsable souhaite aussi entendre les personnes qui utilisent rarement la salle, car les travaux auront des conséquences pour elles. Elle distribue donc un questionnaire et propose une seconde rencontre. Camille remarque que cette méthode n’oblige personne à changer immédiatement de position. Elle élargit plutôt les informations disponibles avant la décision. À la fin, Sami n’a pas convaincu tout le monde, mais la discussion est devenue plus précise : les désaccords portent maintenant sur des choix concrets plutôt que sur des impressions générales. Avant de partir, les participants inscrivent les points encore discutés sur un tableau commun. Cette liste permettra de comparer les nouvelles réponses sans faire comme si le désaccord avait déjà disparu."""
    qs=qmap(p2); ans=amap(p2)
    qs['q1']['target_ids']=['fr-rank-0889']; ans['q1']['answer']='Les participants précisent leurs positions, répondent à des objections concrètes et recueillent davantage d’informations.'
    qs['q5']['prompt']='Dans « déplacer la cuisine pourrait impliquer des travaux supplémentaires », que signifie « impliquer » ?'; qs['q5']['target_ids']=['fr-rank-0899']; ans['q5']['answer']='Avoir ces travaux comme conséquence du choix envisagé.'
    qs['q6']['target_ids']=['fr-rank-0889']; ans['q6']['answer']='Parce qu’elles peuvent être affectées par les travaux et apporter une position ou une information absente de la réunion.'
    qs['q7']['target_ids']=[]
    recalc(p2)
    impl=next(t for t in p2['new_lexical_targets'] if t['form']=='impliquer')
    if 'imply' not in impl.get('intended_sense',''): raise AssertionError('validated impliquer root sense unexpectedly changed')

    p4=byid['fr-b1-u01-p04']
    p4['text']=p4['text'].replace('Le panneau explique qu’un peuple ne se résume pas à une seule histoire.', 'Le panneau explique que l’histoire d’un peuple ne se résume pas à un seul récit.')
    p4['text']=p4['text'].replace('L’image d’une époque peut donc changer quand de nouveaux témoignages apparaissent.', 'L’image proposée d’une époque peut donc changer quand de nouveaux témoignages apparaissent.')
    recalc(p4)

    p5=byid['fr-b1-u01-p05']
    p5['text']=p5['text'].replace('Certaines tâches répétitives, comme classer des fichiers, lui ont donné de l’ennui sur le moment,', 'Certaines tâches répétitives, comme classer des fichiers, lui ont causé de l’ennui sur le moment,')
    recalc(p5)

    p6=byid['fr-b1-u01-p06']
    p6['text']=p6['text'].replace('pour convaincre, il faut comprendre les raisons de l’autre personne et impliquer celles qui seront touchées par la décision.', 'pour convaincre, il faut comprendre les raisons de l’autre personne et vérifier ce que le choix peut impliquer pour celles qui seront touchées par la décision.')
    p6['text']=p6['text'].replace('qu’un peuple contient plusieurs histoires', 'que l’histoire d’un peuple rassemble plusieurs récits')
    qs=qmap(p6); ans=amap(p6)
    qs['q1']['prompt']='Quelle compétence générale Camille développe-t-elle pendant le projet ?'; qs['q1']['target_ids']=['fr-rank-0899']; ans['q1']['answer']='Elle apprend à vérifier, comparer, discuter des positions et anticiper ce qu’une décision peut impliquer.'
    recalc(p6)

    V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')))
    failures=[]; new=[]
    for r in rows:
        errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
        if errs: failures.append(f"{r['id']}: schema {errs[0].message}")
        if not 220<=r['word_count']<=350: failures.append(f"{r['id']}: word band {r['word_count']}")
        if len(r['questions'])!=10 or len(r['answer_key'])!=10: failures.append(f"{r['id']}: q/a count")
        local={t['id'] for fld in ('new_lexical_targets','review_lexical_targets') for t in r.get(fld,[]) if isinstance(t,dict)}
        aa={a['question_id']:a['id'] for a in r['answer_key']}
        for q in r['questions']:
            if aa.get(q['id'])!=q['answer_id']: failures.append(f"{r['id']}/{q['id']}: answer linkage")
            if any(t not in local for t in q.get('target_ids',[])): failures.append(f"{r['id']}/{q['id']}: undeclared target")
        for t in r.get('new_lexical_targets',[]):
            if base.cnt(r['text'],t['form'])!=t['exposures_in_text']: failures.append(f"{r['id']}/{t['form']}: exposure mismatch")
            new.append(t)
        for t in r.get('review_lexical_targets',[]):
            if t.get('representation') in {'running_text','summary'} and base.cnt(r['text'],t['form'])<1: failures.append(f"{r['id']}: invisible review {t['form']}")
    if len(new)!=15 or len({t['id'] for t in new})!=15 or rows[-1]['new_lexical_targets']!=[]: failures.append('lexical-cycle invariant')
    if failures: raise AssertionError('; '.join(failures[:12]))

    CANON.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
    post_blob=subprocess.check_output(['git','hash-object',str(CANON)],text=True).strip()
    audit={
      'status':'PASS','scope':'French B1 Unit 01 post-calibration review','pre_repair_blob':blob,'post_repair_blob':post_blob,
      'passages':6,'questions':60,'answers':60,'new_targets':15,'checkpoint_zero_new':True,
      'word_counts':{r['id']:r['word_count'] for r in rows},
      'calibration_findings':[
        {'type':'workflow_path','resolution':'corrected repository-relative B1 paths before any canonical write'},
        {'type':'word_band','passage_id':'fr-b1-u01-p01','resolution':'expanded naturally from 215 words to within the 220-350 B1 band; threshold unchanged'},
        {'type':'review_visibility','passage_id':'fr-b1-u01-p05','form':'proposer','resolution':'added a natural exact infinitive occurrence; exact-form guard unchanged'},
        {'type':'lexical_sense_precision','passage_id':'fr-b1-u01-p02','form':'impliquer','root_gloss':'imply','resolution':'reframed the deliberate teaching use to the consequence/entail sense supported directly by the validated root gloss; no root CSV mutation or sense override used'},
        {'type':'linguistic_polish','passage_ids':['fr-b1-u01-p04','fr-b1-u01-p05','fr-b1-u01-p06'],'resolution':'smoothed peuple/ennui phrasing while preserving target visibility and assessment linkage'}
      ],
      'mechanical_validation':'PASS','final_language_wide_audit_deferred':True,
      'notes':['This calibration review is intentionally stricter than the generation workflow before scaling B1.', 'The validated root lexical CSV remains unchanged.']
    }
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','post_blob':post_blob,'word_counts':audit['word_counts'],'new_targets':15},ensure_ascii=False))

if __name__=='__main__': main()

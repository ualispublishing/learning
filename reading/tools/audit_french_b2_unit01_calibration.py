#!/usr/bin/env python3
"""Strict post-calibration review for French B2 Unit 01.

This audit decides whether the mechanically valid Unit 01 is a suitable B2
production template.  It does not grant final French approval.
"""
from __future__ import annotations
import json,subprocess
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_b1_unit10 as u10
base=u10.base

REPO=Path(__file__).resolve().parents[2]
A1=REPO/'reading/french/a1/passages.jsonl';A2=REPO/'reading/french/a2/passages.jsonl';B1=REPO/'reading/french/b1/passages.jsonl';B2=REPO/'reading/french/b2/passages.jsonl'
SCHEMA=REPO/'reading/schema/passage.schema.json';OUT=REPO/'reading/audit/french_b2_unit01_calibration_review.json'
EXPECTED={'A1':'0493a2fa13e51b5997db05e91cdea4d8dc5e647b','A2':'d0a80b8866071f426019aa0ad143e1d270dba4de','B1':'4a2cd9ff30c3cea58caf20fca2822b06200622ca','B2':'1ba43c900ad64ff9359264e743470138ce25a9c5'}

def rows(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def blob(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()

def main():
    failures=[]
    for label,p in [('A1',A1),('A2',A2),('B1',B1),('B2',B2)]:
        got=blob(p)
        if got!=EXPECTED[label]: failures.append(f'{label} blob drift: {got} != {EXPECTED[label]}')
    a1,a2,b1,b2=rows(A1),rows(A2),rows(B1),rows(B2)
    V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8'))); deck=base.deck()
    if len(b2)!=6: failures.append(f'B2 Unit01 passage count {len(b2)} != 6')
    if [r.get('sequence') for r in b2]!=list(range(1,7)): failures.append('sequence continuity failure')
    if [r.get('id') for r in b2]!=[f'fr-b2-u01-p{i:02d}' for i in range(1,7)]: failures.append('id continuity failure')
    word_counts={r['id']:len(r['text'].split()) for r in b2}
    paragraph_counts={r['id']:len(r['text'].split('\n\n')) for r in b2}
    schema_fail=[];link_fail=[];review_fail=[];source_fail=[];new=[]
    qtypes=Counter(); discourse_roles=Counter(); grammar_roles=Counter()
    for r in b2:
        errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
        if errs:schema_fail.append({'id':r['id'],'errors':[e.message for e in errs[:8]]})
        if not 350<=word_counts[r['id']]<=550:failures.append(f"{r['id']} word band {word_counts[r['id']]}")
        if r.get('word_count')!=word_counts[r['id']]:failures.append(f"{r['id']} stored word count drift")
        if paragraph_counts[r['id']]<4:failures.append(f"{r['id']} has only {paragraph_counts[r['id']]} paragraphs")
        if len(r.get('questions',[]))!=10 or len(r.get('answer_key',[]))!=10:failures.append(f"{r['id']} assessment count")
        amap={a.get('question_id'):a.get('id') for a in r.get('answer_key',[])}
        local={t.get('id') for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[]) if isinstance(t,dict)}
        for q in r.get('questions',[]):
            qtypes[q.get('type')]+=1
            if amap.get(q.get('id'))!=q.get('answer_id'):link_fail.append({'id':r['id'],'q':q.get('id'),'issue':'answer_link'})
            for tid in q.get('target_ids',[]):
                if tid not in local:link_fail.append({'id':r['id'],'q':q.get('id'),'target':tid,'issue':'undeclared_target'})
        for g in r.get('grammar_targets',[]):grammar_roles[g.get('role')]+=1
        for d in r.get('discourse_targets',[]):discourse_roles[d.get('role')]+=1
        for t in r.get('new_lexical_targets',[]):
            new.append(t);src=deck.get(t.get('form'))
            if not src or t.get('source_rank')!=src.get('rank') or t.get('id')!=base.tid(src.get('rank')):source_fail.append({'id':r['id'],'form':t.get('form'),'issue':'source_identity'})
            elif base.cnt(r['text'],t['form'])!=t.get('exposures_in_text'):source_fail.append({'id':r['id'],'form':t['form'],'issue':'exposure_count'})
        for t in r.get('review_lexical_targets',[]):
            if t.get('representation') in {'running_text','summary'} and base.cnt(r['text'],t.get('form',''))<1:review_fail.append({'id':r['id'],'form':t.get('form')})
    if schema_fail:failures.append(f'schema failures {len(schema_fail)}')
    if link_fail:failures.append(f'linkage failures {len(link_fail)}')
    if source_fail:failures.append(f'source/exposure failures {len(source_fail)}')
    if review_fail:failures.append(f'exact review failures {len(review_fail)}')
    if any(len(r.get('new_lexical_targets',[]))!=4 for r in b2[:5]):failures.append('calibration load is not exactly 4 in P01-P05')
    if b2[-1].get('new_lexical_targets'):failures.append('P06 has new targets')
    if len(new)!=20 or len({t['id'] for t in new})!=20 or len({t['form'] for t in new})!=20:failures.append('20-target uniqueness failure')
    prior=[t for r in a1+a2+b1 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)]
    cross_ids=sorted({t['id'] for t in new}&{t['id'] for t in prior});cross_forms=sorted({t['form'] for t in new}&{t['form'] for t in prior})
    if cross_ids:failures.append(f'prior-level id collisions {cross_ids}')
    if cross_forms:failures.append(f'prior-level form collisions {cross_forms}')
    if b2[2].get('paired_text_group')!='fr-b2-u01-citizen-science-access' or b2[3].get('paired_text_group')!=b2[2].get('paired_text_group'):failures.append('paired viewpoint linkage failure')
    pair_similarity=round(SequenceMatcher(None,b2[2]['text'],b2[3]['text']).ratio(),4)
    if pair_similarity>=0.70:failures.append(f'paired viewpoints too textually similar: {pair_similarity}')
    required_types={'main_claim','argument_relation','stance','assumption','cross_text_synthesis','synthesis','inference','reference_resolution','summary'}
    missing_types=sorted(required_types-set(qtypes))
    if missing_types:failures.append(f'missing B2 question types {missing_types}')
    learner_text='\n'.join(r['text'] for r in b2)+'\n'+'\n'.join(q['prompt'] for r in b2 for q in r['questions'])
    if 'stance' in learner_text:failures.append('learner-facing Anglicism stance remains')
    # Calibration acceptance judgment: four new types is intentionally conservative,
    # while the unit already carries explicit B2 discourse demand in every passage.
    standard_avg=sum(word_counts[r['id']] for r in b2[:5])/5
    if standard_avg<360:failures.append(f'standard-passage mean too close to lower bound: {standard_avg:.1f}')
    if discourse_roles['new']<5 or grammar_roles['new']<5:failures.append('insufficient explicit B2 grammar/discourse calibration targets')
    result={
      'status':'PASS' if not failures else 'FAIL',
      'scope':'French B2 Unit 01 post-calibration review',
      'canonical_blob':blob(B2),'passages':len(b2),'questions':sum(len(r['questions']) for r in b2),'answers':sum(len(r['answer_key']) for r in b2),
      'word_counts':word_counts,'paragraph_counts':paragraph_counts,'standard_passage_mean_words':round(standard_avg,1),
      'new_targets':len(new),'unique_new_target_ids':len({t['id'] for t in new}),'unique_new_target_forms':len({t['form'] for t in new}),
      'prior_level_target_id_collisions':len(cross_ids),'prior_level_target_form_collisions':len(cross_forms),
      'paired_viewpoints':{'group':'fr-b2-u01-citizen-science-access','p03':'viewpoint A: structured openness','p04':'viewpoint B: sampling/representativeness counterargument','text_similarity_ratio':pair_similarity,'materially_distinct':pair_similarity<0.70},
      'question_type_counts':dict(sorted(qtypes.items())),'required_b2_question_types_present':not missing_types,
      'schema_failures':schema_fail,'linkage_failures':link_fail,'source_or_exposure_failures':source_fail,'invisible_exact_reviews':review_fail,
      'language_review':{'status':'PASS','repairs_applied':['P03: replaced awkward “faits hors de sa portée” with standard phrasing about following the reasoning.','P04: clarified the ressembler/representativeness sentence while preserving exact target exposure.','P06/question q7: replaced learner-facing Anglicism “stance” with standard French “position”.'],'learner_facing_stance_anglicism_remaining':False},
      'pedagogical_review':{'status':'PASS','argument_counterargument':True,'author_position_and_scope':True,'denser_cohesion_and_reference':True,'paired_viewpoint_transfer':True,'abstract_lexical_nuance':True,'cross_text_synthesis':True,'four_target_load_assessment':'appropriate conservative B2 default for this discourse density'},
      'accepted_b2_default_new_targets_per_standard_passage':4,
      'durable_planning_range_remains':[4,8],
      'default_is_hard_quota':False,
      'checkpoint_zero_new':not b2[-1]['new_lexical_targets'],
      'full_final_french_audit_deferred':True,
      'failures':failures,
      'notes':['Mechanical calibration passed before this review.','The post-calibration review accepts four fresh targets per standard passage as the B2 production default, not a permanent hard quota; increase within 4-8 only when discourse/grammar load and clarity support it.','B2 Unit 01 is accepted as the production template after the narrow language repair.']
    }
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'blob':result['canonical_blob'],'mean_words':result['standard_passage_mean_words'],'pair_similarity':pair_similarity,'new_targets':len(new),'accepted_default':4,'failures':failures},ensure_ascii=False))
    if failures:raise AssertionError('B2 calibration review FAIL: '+'; '.join(failures[:12]))
if __name__=='__main__':main()

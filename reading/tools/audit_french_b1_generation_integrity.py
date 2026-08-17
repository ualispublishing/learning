#!/usr/bin/env python3
"""Fail-closed generation-integrity audit for the completed French B1 corpus.

This is a generation milestone audit, not the deferred final French approval audit.
It does not mutate canonical passages or the validated lexical source.
"""
from __future__ import annotations
import json,re,subprocess
from collections import Counter,defaultdict
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_b1_unit10 as u10

base=u10.base
REPO=Path(__file__).resolve().parents[2]
A1=REPO/'reading/french/a1/passages.jsonl'
A2=REPO/'reading/french/a2/passages.jsonl'
B1=REPO/'reading/french/b1/passages.jsonl'
SCHEMA=REPO/'reading/schema/passage.schema.json'
OUT=REPO/'reading/audit/french_b1_generation_integrity.json'
EXPECTED={'A1':'0493a2fa13e51b5997db05e91cdea4d8dc5e647b','A2':'d0a80b8866071f426019aa0ad143e1d270dba4de','B1':'4a2cd9ff30c3cea58caf20fca2822b06200622ca'}

def rows(path): return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
def blob(path): return subprocess.check_output(['git','hash-object',str(path)],text=True).strip()

def main():
    failures=[]
    for label,path in [('A1',A1),('A2',A2),('B1',B1)]:
        got=blob(path)
        if got!=EXPECTED[label]: failures.append(f'{label} blob drift: {got} != {EXPECTED[label]}')
    a1,a2,b1=rows(A1),rows(A2),rows(B1)
    schema=json.loads(SCHEMA.read_text(encoding='utf-8')); validator=Draft202012Validator(schema); deck=base.deck()
    if len(b1)!=60: failures.append(f'B1 passage count {len(b1)} != 60')
    if [r.get('sequence') for r in b1]!=list(range(1,61)): failures.append('B1 sequence continuity failure')
    ids=[r.get('id') for r in b1]
    expected_ids=[f'fr-b1-u{u:02d}-p{p:02d}' for u in range(1,11) for p in range(1,7)]
    if ids!=expected_ids: failures.append('B1 id/unit ordering failure')
    if len(set(ids))!=len(ids): failures.append('duplicate B1 passage ids')

    qn=an=0; new=[]; invisible=[]; source_fail=[]; linkage=[]; schema_fail=[]; word_fail=[]; stored_word_fail=[]
    units=defaultdict(lambda:{'passages':0,'new_targets':0,'checkpoint_zero_new':False})
    for r in b1:
        errs=sorted(validator.iter_errors(r),key=lambda e:list(e.path))
        if errs: schema_fail.append({'id':r.get('id'),'errors':[e.message for e in errs[:10]]})
        wc=len(r.get('text','').split())
        if not 220<=wc<=350: word_fail.append({'id':r.get('id'),'word_count':wc})
        if r.get('word_count')!=wc: stored_word_fail.append({'id':r.get('id'),'stored':r.get('word_count'),'actual':wc})
        qs=r.get('questions',[]); ans=r.get('answer_key',[]); qn+=len(qs); an+=len(ans)
        if len(qs)!=10 or len(ans)!=10: linkage.append({'id':r.get('id'),'issue':'assessment_count'})
        amap={a.get('question_id'):a.get('id') for a in ans}; local={str(t.get('id')) for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[]) if isinstance(t,dict) and t.get('id')}
        for q in qs:
            if amap.get(q.get('id'))!=q.get('answer_id'): linkage.append({'id':r.get('id'),'question':q.get('id'),'issue':'answer_link'})
            for tid in q.get('target_ids',[]):
                if tid not in local: linkage.append({'id':r.get('id'),'question':q.get('id'),'target':tid,'issue':'undeclared_target'})
        for t in r.get('new_lexical_targets',[]):
            new.append(t); form=t.get('form'); src=deck.get(form)
            if not src or t.get('source_rank')!=src.get('rank') or t.get('id')!=base.tid(src.get('rank')):
                source_fail.append({'id':r.get('id'),'target':t,'issue':'source_identity'})
            elif base.cnt(r.get('text',''),form)!=t.get('exposures_in_text'):
                source_fail.append({'id':r.get('id'),'form':form,'issue':'stored_exposure_count','stored':t.get('exposures_in_text'),'actual':base.cnt(r.get('text',''),form)})
        for t in r.get('review_lexical_targets',[]):
            if t.get('representation') in {'running_text','summary'} and base.cnt(r.get('text',''),t.get('form',''))<1:
                invisible.append({'id':r.get('id'),'form':t.get('form')})
        u=str(r.get('unit')); units[u]['passages']+=1; units[u]['new_targets']+=len(r.get('new_lexical_targets',[]))
        if r.get('id','').endswith('-p06'): units[u]['checkpoint_zero_new']=not r.get('new_lexical_targets')

    new_ids=[t.get('id') for t in new]; new_forms=[t.get('form') for t in new]
    prior=[t for r in a1+a2 for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)]
    prior_ids={t.get('id') for t in prior}; prior_forms={t.get('form') for t in prior}
    cross_ids=sorted(set(new_ids)&prior_ids); cross_forms=sorted(set(new_forms)&prior_forms)
    dup_ids=[k for k,v in Counter(new_ids).items() if v>1]; dup_forms=[k for k,v in Counter(new_forms).items() if v>1]
    if qn!=600: failures.append(f'question count {qn} != 600')
    if an!=600: failures.append(f'answer count {an} != 600')
    if len(new)!=150: failures.append(f'new target count {len(new)} != 150')
    if dup_ids: failures.append(f'duplicate B1 target ids: {dup_ids}')
    if dup_forms: failures.append(f'duplicate B1 target forms: {dup_forms}')
    if cross_ids: failures.append(f'A1/A2↔B1 target id collisions: {cross_ids}')
    if cross_forms: failures.append(f'A1/A2↔B1 target form collisions: {cross_forms}')
    for u in map(str,range(1,11)):
        if units[u]['passages']!=6 or units[u]['new_targets']!=15 or not units[u]['checkpoint_zero_new']:
            failures.append(f'Unit {u} invariant failure: {units[u]}')
    if schema_fail: failures.append(f'schema failures: {len(schema_fail)}')
    if word_fail: failures.append(f'word-band failures: {len(word_fail)}')
    if stored_word_fail: failures.append(f'stored word-count failures: {len(stored_word_fail)}')
    if linkage: failures.append(f'question/answer/target linkage failures: {len(linkage)}')
    if source_fail: failures.append(f'source/exposure failures: {len(source_fail)}')
    if invisible: failures.append(f'invisible exact reviews: {len(invisible)}')

    result={
      'status':'PASS' if not failures else 'FAIL',
      'scope':'French B1 generation milestone',
      'canonical_blob':blob(B1),'passages':len(b1),'questions':qn,'answers':an,
      'new_targets':len(new),'unique_new_target_ids':len(set(new_ids)),'unique_new_target_forms':len(set(new_forms)),
      'a1_a2_cross_level_target_id_collisions':len(cross_ids),'a1_a2_cross_level_target_form_collisions':len(cross_forms),
      'units':dict(units),'schema_failures':schema_fail,'word_band_failures':word_fail,'stored_word_count_failures':stored_word_fail,
      'linkage_failures':linkage,'source_or_exposure_failures':source_fail,'invisible_exact_reviews':invisible,'failures':failures,
      'coverage_note':'estimated_known_token_coverage remains unmeasured placeholder data; no percentage is inferred',
      'full_final_audit_deferred':True,
      'method_notes':[
        'Validated all 60 canonical B1 records against the passage schema and 220-350 word planning band.',
        'Rechecked 600 question/answer links, local question-target declarations, source rank/id identity and exact stored exposure counts.',
        'Rechecked exact visibility of all deliberate running-text/summary reviews and all 10 zero-new P06 checkpoints.',
        'Rechecked 150 B1 new targets for within-B1 uniqueness and collisions against all deliberate French A1+A2 new targets by source id and visible form.',
        'This is a generation-integrity closeout, not the deferred language-wide French final multi-pass approval audit.'
      ]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'passages':len(b1),'questions':qn,'answers':an,'new_targets':len(new),'cross_id_collisions':len(cross_ids),'cross_form_collisions':len(cross_forms),'failures':failures},ensure_ascii=False))
    if failures: raise AssertionError('B1 integrity FAIL: '+'; '.join(failures[:12]))

if __name__=='__main__': main()

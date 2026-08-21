import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'reading/urdu/a1/passages.jsonl'
STAGE=ROOT/'reading/urdu/a1/staging/unit08'
AUDIT=ROOT/'reading/audit/urdu_a1_unit08_promotion_2026-08-21.json'
EXPECTED='b4fcf0bbc07d62cd3e743b8d0a6d49df2d6b0df3d03aa892384d0501a7ef1d4a'
FILES=[f'ur-a1-u08-p0{i}.json' for i in range(1,7)]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def fail(msg): raise SystemExit(msg)
def learner_surfaces(p):
    yield p.get('text','')
    for q in p.get('questions',[]): yield q.get('prompt','')
    for a in p.get('answer_key',[]): yield a.get('answer','')
def main():
    before=sha(CANON)
    if before!=EXPECTED: fail(f'canonical hash drift: {before}')
    canon=[json.loads(x) for x in CANON.read_text(encoding='utf-8').splitlines() if x.strip()]
    if len(canon)!=42 or [p.get('sequence') for p in canon]!=list(range(1,43)): fail('canonical frontier mismatch')
    staged=[]; staged_blobs={}
    for fn in FILES:
        path=STAGE/fn
        if not path.exists(): fail(f'missing staging file {fn}')
        staged_blobs[fn]=hashlib.sha1((f'blob {len(path.read_bytes())}\0'.encode()+path.read_bytes())).hexdigest()
        staged.append(json.loads(path.read_text(encoding='utf-8')))
    if [p.get('sequence') for p in staged]!=list(range(43,49)): fail('staged sequence mismatch')
    if [p.get('id') for p in staged]!=[f'ur-a1-u08-p0{i}' for i in range(1,7)]: fail('staged id mismatch')
    existing_ids={t.get('id') for p in canon for t in p.get('new_lexical_targets',[]) if t.get('id')}
    new_ids=[]; problems=[]
    for idx,p in enumerate(staged,1):
        qs=p.get('questions',[]); ans=p.get('answer_key',[])
        if len(qs)!=10 or len(ans)!=10: problems.append([p['id'],'cardinality'])
        qids={q.get('id') for q in qs}; aids={a.get('question_id') for a in ans}
        if qids!=aids: problems.append([p['id'],'answer_linkage'])
        local={t.get('id') for t in p.get('new_lexical_targets',[])}|{t.get('id') for t in p.get('review_lexical_targets',[])}
        for q in qs:
            for tid in q.get('target_ids',[]):
                if tid not in local: problems.append([p['id'],q.get('id'),'target_not_locally_declared',tid])
        for t in p.get('new_lexical_targets',[]):
            tid=t.get('id'); form=t.get('form','')
            if tid in existing_ids: problems.append([p['id'],'new_target_collision',tid])
            if tid: new_ids.append(tid)
            if form and form not in p.get('text',''): problems.append([p['id'],'new_target_not_visible',form])
        for t in p.get('review_lexical_targets',[]):
            if t.get('representation')=='running_text' and t.get('form') and t['form'] not in p.get('text',''):
                problems.append([p['id'],'running_text_review_not_visible',t['form']])
        if idx==6 and p.get('new_lexical_targets'): problems.append([p['id'],'checkpoint_has_new_targets'])
        for s in learner_surfaces(p):
            if re.search(r'[A-Za-z]',s or ''): problems.append([p['id'],'roman_script_learner_surface',s])
        wc=len((p.get('text') or '').split())
        if wc!=p.get('word_count') or not 90<=wc<=140: problems.append([p['id'],'word_count',wc,p.get('word_count')])
    if len(new_ids)!=10 or len(set(new_ids))!=10: problems.append(['unit08','new_target_id_count',len(new_ids),len(set(new_ids))])
    if problems: fail('promotion validation failed: '+json.dumps(problems,ensure_ascii=False))
    merged=canon+staged
    CANON.write_text('\n'.join(json.dumps(p,ensure_ascii=False,sort_keys=True) for p in merged)+'\n',encoding='utf-8')
    after=sha(CANON)
    audit={
      'schema_version':1,'date':'2026-08-21','language':'ur','level':'A1','unit':8,
      'status':'GUARDED_PROMOTION_APPLIED_NEEDS_REVIEW','before_sha256':before,'after_sha256':after,
      'staged_git_blobs':staged_blobs,'canonical_passages_after':48,'canonical_questions_after':480,'canonical_answers_after':480,
      'promoted_sequences':list(range(43,49)),'new_target_ids_added':new_ids,'source_lexicon_mutated':False,
      'checks':{'frontier_sha256_exact':True,'staging_files_present':True,'sequences_contiguous':True,'a1_word_band_90_140':True,'ten_questions_and_answers':True,'answer_linkage':True,'question_targets_locally_declared':True,'new_targets_visible':True,'running_text_reviews_visible':True,'new_target_id_collisions':0,'p06_zero_new_targets':True,'learner_facing_roman_script_zero':True},
      'formal_final_audit':'deferred under generation-first policy','next_generation_frontier':'Urdu A1 Unit 09 sequences 49-54; staged already on the dependent Unit 09 branch.','release_effect':'Generation progress only; Urdu remains non-release-ready.'}
    AUDIT.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS_GUARDED_PROMOTION_UNIT08','before':before,'after':after,'records':48,'new_targets':len(new_ids)},ensure_ascii=False))
if __name__=='__main__': main()

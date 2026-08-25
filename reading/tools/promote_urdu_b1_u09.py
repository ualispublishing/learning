#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; STAGE=ROOT/'reading/audit/urdu_b1_u09_generation_candidate'; TARGET=ROOT/'reading/urdu/b1/passages.jsonl'; SCHEMA=ROOT/'reading/schema/passage.schema.json'; DATE='2026-08-24'
IDS=[f'ur-b1-u09-p{i:02d}' for i in range(1,7)]; SEQS=list(range(49,55)); TARGETS=['ur-rank-1980','ur-rank-1678','ur-rank-1714','ur-rank-1706','ur-rank-1735','ur-rank-1782','ur-rank-1728','ur-rank-1662','ur-rank-1985','ur-rank-1988','ur-rank-1679','ur-rank-1669','ur-rank-1712','ur-rank-1729','ur-rank-1791']; ROLES=['instructional','reinforcement','interleaved','transfer','integration','checkpoint']; GENRES={'local report','proposal','viewpoint'}
def jl(p): return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def fail(x): raise SystemExit('Fail closed: '+x)
def rep(s,a,b,label):
    if s.count(a)!=1: fail(f'{label}: expected phrase once: {a!r}')
    return s.replace(a,b,1)
def main():
    sch=json.loads(SCHEMA.read_text(encoding='utf-8')); req=set(sch['required']); ptypes=set(sch['properties']['passage_type']['enum']); domains=set(sch['properties']['domains']['items']['enum']); qtypes=set(sch['$defs']['question']['properties']['type']['enum']); strategies=set(sch['$defs']['newLexicalTarget']['properties']['context_strategy']['items']['enum'])
    a1=jl(ROOT/'reading/urdu/a1/passages.jsonl'); a2=jl(ROOT/'reading/urdu/a2/passages.jsonl'); b1=jl(TARGET)
    if len(a1)!=60 or len(a2)!=60 or len(b1)!=48 or [r['sequence'] for r in b1]!=list(range(1,49)): fail('canonical Urdu pre-state is not A1=60 A2=60 B1=1-48')
    sp=ROOT/'reading/STATUS.json'; cp=ROOT/'reading/CONTINUATION.json'; pp=ROOT/'reading/planning/ACTIVE_GENERATION_PLAN.json'; s=json.loads(sp.read_text()); c=json.loads(cp.read_text()); p=json.loads(pp.read_text())
    if s['current']['canonical_passages']!=888 or s['languages']['urdu']['canonical_passages']!=168: fail('STATUS counts drifted')
    if p.get('active_unit')!=9 or p.get('start_sequence')!=49 or p.get('existing_active_level_passages')!=48: fail('active plan drifted from Unit 9')
    if 'Urdu B1 Unit 9 / sequence 49' not in c.get('active_frontier',{}).get('production',{}).get('action',''): fail('CONTINUATION drifted from Unit 9')
    before=TARGET.read_bytes(); before_sha=hashlib.sha256(before).hexdigest(); taught={t['id'] for r in a1+a2+b1 for t in r.get('new_lexical_targets',[])}; col=sorted(taught.intersection(TARGETS))
    if col: fail(f'target freshness collision: {col}')
    rows=[]; learner=[]
    for i in range(1,7):
        f=STAGE/f'ur-b1-u09-p{i:02d}.json';
        if not f.exists(): fail(f'missing {f.relative_to(ROOT)}')
        r=json.loads(f.read_text(encoding='utf-8')); r['word_count']=len(r['text'].split()); r['sentence_count']=r['text'].count('۔')
        for t in r.get('new_lexical_targets',[]): t['exposures_in_text']=r['text'].count(t['form'])
        f.write_text(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8'); rows.append(r); learner += [r['title'],r['text']]+[q['prompt'] for q in r['questions']]+[a['answer'] for a in r['answer_key']]
    if [r['id'] for r in rows]!=IDS or [r['sequence'] for r in rows]!=SEQS or [r['passage_type'] for r in rows]!=ROLES: fail('identity/sequence/role contract failed')
    if [len(r['new_lexical_targets']) for r in rows]!=[3,3,3,3,3,0] or [t['id'] for r in rows[:5] for t in r['new_lexical_targets']]!=TARGETS: fail('target contract failed')
    if any(t['exposures_in_text']<1 for r in rows for t in r['new_lexical_targets']): fail('target absent from text')
    if not GENRES.issubset({r['genre'] for r in rows}): fail('required genres missing')
    prior=''
    for r in rows[:5]:
        for t in r['new_lexical_targets']:
            if t['form'] in prior: fail(f'premature exact-form exposure: {t["form"]}/{t["id"]}')
        prior+='\n'+'\n'.join([r['title'],r['text']]+[q['prompt'] for q in r['questions']]+[a['answer'] for a in r['answer_key']])
    p6=rows[-1]; forms={t['form'] for r in rows[:5] for t in r['new_lexical_targets']}; reviews={t['form'] for t in p6['review_lexical_targets'] if t['representation']=='running_text'}
    if p6['new_lexical_targets'] or not p6['speed_training']['timed'] or p6['speed_training']['new_word_policy']!='none' or reviews!=forms or any(x not in p6['text'] for x in forms): fail('checkpoint contract failed')
    for r in rows:
        if req-set(r): fail(f'{r["id"]} missing required fields')
        if r['passage_type'] not in ptypes or any(d not in domains for d in r['domains']): fail(f'enum failure {r["id"]}')
        if len(r['questions'])!=10 or len(r['answer_key'])!=10 or not 220<=r['word_count']<=320: fail(f'QA/word-band failure {r["id"]}')
        amap={a['id']:a for a in r['answer_key']}
        if set(amap)!={f'a{i}' for i in range(1,11)} or {q['id'] for q in r['questions']}!={f'q{i}' for i in range(1,11)}: fail(f'QA IDs drifted {r["id"]}')
        for t in r.get('new_lexical_targets',[]):
            if any(x not in strategies for x in t['context_strategy']): fail(f'context strategy failed {r["id"]}/{t["id"]}')
        for q in r['questions']:
            if q['type'] not in qtypes or q['answer_id'] not in amap or amap[q['answer_id']]['question_id']!=q['id']: fail(f'QA link/type failed {r["id"]}/{q["id"]}')
    if re.search(r'[A-Za-z\u0900-\u097F]','\n'.join(learner)): fail('learner-facing script leakage')
    payload=''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows).encode(); TARGET.write_bytes(before+payload); after=TARGET.read_bytes(); final=jl(TARGET)
    if after[:len(before)]!=before or len(final)!=54 or [r['sequence'] for r in final]!=list(range(1,55)) or [r['id'] for r in final[-6:]]!=IDS: fail('post-append canonical check failed')
    (STAGE/'manifest.json').write_text(json.dumps({'schema_version':1,'project_id':'LANG-A1C2','language':'ur','cefr':'B1','unit':9,'date':DATE,'status':'CANONICALIZED','canonical_target':'reading/urdu/b1/passages.jsonl','sequence_range':[49,54],'record_count':6,'release_promotion':False},ensure_ascii=False,indent=2)+'\n')
    checks={k:'PASS' for k in ['canonical_prestate','freshness','record_count','sequence_49_through_54','role_cycle','question_answer_10x10','bidirectional_links','target_distribution','target_text_exposure','first_introduction_order','required_genres','checkpoint_policy','checkpoint_recycling','learner_script_scan','schema_enums_context_strategies','b1_word_band','preexisting_bytes_preserved']}
    (ROOT/'reading/audit/urdu_b1_u09_generation_validation_2026-08-24.json').write_text(json.dumps({'schema_version':1,'project_id':'LANG-A1C2','language':'ur','cefr':'B1','unit':9,'date':DATE,'canonicalized':True,'release_promotion':False,'word_counts':[r['word_count'] for r in rows],'checks':checks},ensure_ascii=False,indent=2)+'\n')
    (ROOT/'reading/audit/urdu_b1_u09_promotion_2026-08-24.json').write_text(json.dumps({'schema_version':1,'project_id':'LANG-A1C2','language':'ur','cefr':'B1','unit':9,'date':DATE,'status':'CANONICAL_PROMOTION_PASS','release_promotion':False,'before_record_count':48,'after_record_count':54,'appended_sequences':SEQS,'appended_ids':IDS,'preexisting_bytes_preserved_exactly':True,'canonical_sha256_before':before_sha,'canonical_sha256_after':hashlib.sha256(after).hexdigest()},ensure_ascii=False,indent=2)+'\n')
    lp=ROOT/'reading/audit/urdu_b1_u09_lexical_sense_check_2026-08-24.json'; lex=json.loads(lp.read_text()); lex['status']='CANONICAL_FRESHNESS_PASS_EXTERNAL_LEXICAL_REVIEW_DEFERRED'; lex['freshness_result']='PASS'; lex['freshness_scope']='Exact target IDs checked against all canonical Urdu A1, A2, and B1 sequences 1-48 immediately before Unit 9 append.'; lp.write_text(json.dumps(lex,ensure_ascii=False,indent=2)+'\n')
    s['current']['canonical_passages']=894; s['current']['remaining_generation_passages']=186; u=s['languages']['urdu']; u['canonical_passages']=174; u['remaining_generation_passages']=186; sp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
    c['production']['canonical_passages']=894; c['production']['urdu']['canonical_passages']=174; c['active_frontier']['production']={'language':'urdu','level':'B1','action':'Continue generation-first production from Urdu B1 Unit 10 / sequence 55 using the canonical roadmap and ten-question contract.'}; c['exact_next_actions']=['Validate the routed state bundle and live canonical counts.','Use reading/planning/ACTIVE_GENERATION_PLAN.json to start guarded Urdu B1 Unit 10 generation at sequence 55.','Keep release/educator verification separate from generation progress.']; cp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
    p.update({'active_unit':10,'start_sequence':55,'existing_active_level_passages':54,'active_unit_roadmap':{'unit':10,'theme':'B1 synthesis','genres':['longer integrated article','paired short texts','checkpoint']}}); pp.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
    tp=ROOT/'reading/TASKS.md'; t=tp.read_text(); t=rep(t,'Canonical production frontier: **Urdu B1, Unit 9, sequence 49**.','Canonical production frontier: **Urdu B1, Unit 10, sequence 55**.','TASKS frontier'); t=rep(t,'- Urdu: 168/360 generated; A1-A2 complete, B1 in progress.','- Urdu: 174/360 generated; A1-A2 complete, B1 in progress.','TASKS Urdu'); t=rep(t,'- Project: 888/1080 generated.','- Project: 894/1080 generated.','TASKS project'); tp.write_text(t)
    hp=ROOT/'reading/AGENT_HANDOFF_V2.md'; h=hp.read_text(); h=rep(h,'- Canonical generated total: **888**.','- Canonical generated total: **894**.','handoff total'); h=rep(h,'- Urdu: **168/360**; A1-A2 generation complete and B1 generation in progress.','- Urdu: **174/360**; A1-A2 generation complete and B1 generation in progress.','handoff Urdu'); h=rep(h,'Continue **Urdu B1**, starting from Unit 9 / sequence 49, under:','Continue **Urdu B1**, starting from Unit 10 / sequence 55, under:','handoff frontier'); h=rep(h,'B1 Unit 9 uses the roadmap theme **public life and community choices** with `local report`, `proposal`, and `viewpoint` genres.','B1 Unit 10 uses the roadmap theme **B1 synthesis** with `longer integrated article`, `paired short texts`, and `checkpoint` genres.','handoff roadmap'); h=rep(h,'resume guarded generation at **Urdu B1 Unit 9 / sequence 49** using the B1 Unit 9 roadmap theme `public life and community choices`.','resume guarded generation at **Urdu B1 Unit 10 / sequence 55** using the B1 Unit 10 roadmap theme `B1 synthesis`.','handoff next'); hp.write_text(h)
    print('Unit 9 canonical promotion prepared: B1 48 -> 54; project 888 -> 894; Urdu 168 -> 174; next Unit 10 / 55')
    return 0
if __name__=='__main__': raise SystemExit(main())

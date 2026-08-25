#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
STAGE=ROOT/'reading/audit/urdu_b1_u10_generation_candidate'
TARGET=ROOT/'reading/urdu/b1/passages.jsonl'
SCHEMA=ROOT/'reading/schema/passage.schema.json'
DATE='2026-08-24'
IDS=[f'ur-b1-u10-p{i:02d}' for i in range(1,7)]
SEQS=list(range(55,61))
TARGETS=['ur-rank-1650','ur-rank-1671','ur-rank-1675','ur-rank-1661','ur-rank-1688','ur-rank-1660','ur-rank-1702','ur-rank-1676','ur-rank-1750','ur-rank-1670','ur-rank-1682','ur-rank-1665','ur-rank-1690','ur-rank-1759','ur-rank-1758']
ROLES=['instructional','reinforcement','interleaved','transfer','integration','checkpoint']
GENRES={'longer integrated article','paired short texts','checkpoint'}

def jl(p:Path): return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def fail(x): raise SystemExit('Fail closed: '+x)
def rep(s,a,b,label):
    if s.count(a)!=1: fail(f'{label}: expected phrase once: {a!r}')
    return s.replace(a,b,1)
def urdu_tokens(text:str): return re.findall(r'[\u0600-\u06FF]+', text)

def main():
    sch=json.loads(SCHEMA.read_text(encoding='utf-8')); req=set(sch['required'])
    ptypes=set(sch['properties']['passage_type']['enum']); domains=set(sch['properties']['domains']['items']['enum'])
    qtypes=set(sch['$defs']['question']['properties']['type']['enum']); strategies=set(sch['$defs']['newLexicalTarget']['properties']['context_strategy']['items']['enum'])
    a1=jl(ROOT/'reading/urdu/a1/passages.jsonl'); a2=jl(ROOT/'reading/urdu/a2/passages.jsonl'); b1=jl(TARGET)
    if len(a1)!=60 or len(a2)!=60 or len(b1)!=54 or [r['sequence'] for r in b1]!=list(range(1,55)):
        fail('canonical Urdu pre-state is not A1=60 A2=60 B1=1-54')
    sp=ROOT/'reading/STATUS.json'; cp=ROOT/'reading/CONTINUATION.json'; pp=ROOT/'reading/planning/ACTIVE_GENERATION_PLAN.json'
    s=json.loads(sp.read_text(encoding='utf-8')); c=json.loads(cp.read_text(encoding='utf-8')); p=json.loads(pp.read_text(encoding='utf-8'))
    if s['current']['canonical_passages']!=894 or s['languages']['urdu']['canonical_passages']!=174: fail('STATUS counts drifted from B1 Unit 10 pre-state')
    if s['current']['active_language']!='urdu' or s['current']['active_level']!='B1': fail('STATUS frontier is not Urdu B1')
    if p.get('active_unit')!=10 or p.get('start_sequence')!=55 or p.get('existing_active_level_passages')!=54: fail('active plan drifted from B1 Unit 10 / 55')
    if 'Urdu B1 Unit 10 / sequence 55' not in c.get('active_frontier',{}).get('production',{}).get('action',''): fail('CONTINUATION drifted from B1 Unit 10 / 55')
    before=TARGET.read_bytes(); before_sha=hashlib.sha256(before).hexdigest()
    taught={t['id'] for r in a1+a2+b1 for t in r.get('new_lexical_targets',[])}; col=sorted(taught.intersection(TARGETS))
    if col: fail(f'target freshness collision: {col}')
    rows=[]; learner=[]
    for i in range(1,7):
        f=STAGE/f'ur-b1-u10-p{i:02d}.json'
        if not f.exists(): fail(f'missing {f.relative_to(ROOT)}')
        r=json.loads(f.read_text(encoding='utf-8')); r['word_count']=len(r['text'].split()); r['sentence_count']=r['text'].count('۔')
        for t in r.get('new_lexical_targets',[]): t['exposures_in_text']=sum(1 for tok in urdu_tokens(r['text']) if tok==t['form'])
        f.write_text(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8'); rows.append(r)
        learner += [r['title'],r['text']]+[q['prompt'] for q in r['questions']]+[a['answer'] for a in r['answer_key']]
    if [r['id'] for r in rows]!=IDS or [r['sequence'] for r in rows]!=SEQS or [r['passage_type'] for r in rows]!=ROLES: fail('identity/sequence/role contract failed')
    if [len(r['new_lexical_targets']) for r in rows]!=[3,3,3,3,3,0] or [t['id'] for r in rows[:5] for t in r['new_lexical_targets']]!=TARGETS: fail('target contract failed')
    if any(t['exposures_in_text']<1 for r in rows for t in r['new_lexical_targets']): fail('new target absent as exact token from passage text')
    if not GENRES.issubset({r['genre'] for r in rows}): fail('required synthesis genres missing')
    prior_tokens=set()
    for r in rows[:5]:
        for t in r['new_lexical_targets']:
            if t['form'] in prior_tokens: fail(f'premature exact-token exposure: {t["form"]}/{t["id"]}')
        current='\n'.join([r['title'],r['text']]+[q['prompt'] for q in r['questions']]+[a['answer'] for a in r['answer_key']])
        prior_tokens.update(urdu_tokens(current))
    p6=rows[-1]; forms={t['form'] for r in rows[:5] for t in r['new_lexical_targets']}; reviews={t['form'] for t in p6['review_lexical_targets'] if t['representation']=='running_text'}; p6_tokens=set(urdu_tokens(p6['text']))
    if p6['new_lexical_targets'] or not p6['speed_training']['timed'] or p6['speed_training']['new_word_policy']!='none': fail('P6 checkpoint policy failed')
    if reviews!=forms or not forms.issubset(p6_tokens): fail('P6 does not visibly recycle all 15 targets as exact tokens')
    for r in rows:
        missing=req-set(r)
        if missing: fail(f'{r["id"]} missing fields {sorted(missing)}')
        if r['passage_type'] not in ptypes or any(d not in domains for d in r['domains']): fail(f'enum failure {r["id"]}')
        if len(r['questions'])!=10 or len(r['answer_key'])!=10 or not 220<=r['word_count']<=320: fail(f'QA/word-band failure {r["id"]}: {r["word_count"]}')
        amap={a['id']:a for a in r['answer_key']}
        if set(amap)!={f'a{i}' for i in range(1,11)} or {q['id'] for q in r['questions']}!={f'q{i}' for i in range(1,11)}: fail(f'QA IDs drifted {r["id"]}')
        for t in r.get('new_lexical_targets',[]):
            if any(x not in strategies for x in t['context_strategy']): fail(f'context strategy failed {r["id"]}/{t["id"]}')
        for q in r['questions']:
            if q['type'] not in qtypes or q['answer_id'] not in amap or amap[q['answer_id']]['question_id']!=q['id']: fail(f'QA link/type failed {r["id"]}/{q["id"]}')
    if re.search(r'[A-Za-z\u0900-\u097F]','\n'.join(learner)): fail('learner-facing Latin/Devanagari leakage')
    payload=''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows).encode('utf-8'); TARGET.write_bytes(before+payload); after=TARGET.read_bytes(); final=jl(TARGET)
    if after[:len(before)]!=before or len(final)!=60 or [r['sequence'] for r in final]!=list(range(1,61)) or [r['id'] for r in final[-6:]]!=IDS: fail('B1 completion append check failed')
    (STAGE/'manifest.json').write_text(json.dumps({'schema_version':1,'project_id':'LANG-A1C2','language':'ur','cefr':'B1','unit':10,'date':DATE,'status':'CANONICALIZED_B1_COMPLETE','canonical_target':'reading/urdu/b1/passages.jsonl','sequence_range':[55,60],'record_count':6,'level_record_count':60,'release_promotion':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    checks={k:'PASS' for k in ['canonical_prestate','freshness','record_count','sequence_55_through_60','b1_exactly_60','role_cycle','question_answer_10x10','bidirectional_links','target_distribution','exact_token_target_exposure','exact_token_first_introduction_order','required_genres','checkpoint_policy','checkpoint_recycling','learner_script_scan','schema_enums_context_strategies','b1_word_band','preexisting_bytes_preserved']}
    (ROOT/'reading/audit/urdu_b1_u10_generation_validation_2026-08-24.json').write_text(json.dumps({'schema_version':1,'project_id':'LANG-A1C2','language':'ur','cefr':'B1','unit':10,'date':DATE,'canonicalized':True,'b1_generation_complete':True,'release_promotion':False,'word_counts':[r['word_count'] for r in rows],'checks':checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'reading/audit/urdu_b1_u10_promotion_2026-08-24.json').write_text(json.dumps({'schema_version':1,'project_id':'LANG-A1C2','language':'ur','cefr':'B1','unit':10,'date':DATE,'status':'CANONICAL_PROMOTION_PASS_B1_COMPLETE','release_promotion':False,'before_record_count':54,'after_record_count':60,'appended_sequences':SEQS,'appended_ids':IDS,'preexisting_bytes_preserved_exactly':True,'canonical_sha256_before':before_sha,'canonical_sha256_after':hashlib.sha256(after).hexdigest(),'next_generation_frontier':'Urdu B2 Unit 1 / sequence 1'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lp=ROOT/'reading/audit/urdu_b1_u10_lexical_sense_check_2026-08-24.json'; lex=json.loads(lp.read_text(encoding='utf-8')); lex['status']='CANONICAL_FRESHNESS_PASS_EXTERNAL_LEXICAL_REVIEW_DEFERRED'; lex['freshness_result']='PASS'; lex['freshness_scope']='Exact target IDs checked against all canonical Urdu A1, A2, and B1 sequences 1-54 immediately before Unit 10 append.'; lp.write_text(json.dumps(lex,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    s['current']['canonical_passages']=900; s['current']['remaining_generation_passages']=180; s['current']['active_level']='B2'; u=s['languages']['urdu']; u['generation_state']='B2_IN_PROGRESS'; u['canonical_passages']=180; u['remaining_generation_passages']=180; u['complete_levels']=['A1','A2','B1']; u['next_generation_level']='B2'; sp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    c['production']['canonical_passages']=900; cu=c['production']['urdu']; cu['state']='B2_GENERATION_IN_PROGRESS'; cu['canonical_passages']=180; cu['complete_levels']=['A1','A2','B1']; cu['next_generation_level']='B2'; c['active_frontier']['production']={'language':'urdu','level':'B2','action':'Continue generation-first production from Urdu B2 Unit 1 / sequence 1 using the canonical roadmap and ten-question contract.'}; c['exact_next_actions']=['Validate the routed state bundle and live canonical counts.','Use reading/planning/ACTIVE_GENERATION_PLAN.json to start guarded Urdu B2 Unit 1 generation at sequence 1.','Keep release/educator verification separate from generation progress.']; cp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    p['active_language']='urdu'; p['active_level']='B2'; p['active_unit']=1; p['start_sequence']=1; p['canonical_active_path']='reading/urdu/b2/passages.jsonl'; p['existing_active_level_passages']=0; p['roadmap_lookup']='$.levels.B2'; p['active_unit_roadmap']={'unit':1,'theme':'science and society','genres':['popular science','analysis','paired viewpoints']}; pp.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tp=ROOT/'reading/TASKS.md'; t=tp.read_text(encoding='utf-8'); t=rep(t,'## P1 — active production: Urdu B1','## P1 — active production: Urdu B2','TASKS heading'); t=rep(t,'Canonical production frontier: **Urdu B1, Unit 10, sequence 55**.','Canonical production frontier: **Urdu B2, Unit 1, sequence 1**.','TASKS frontier'); t=rep(t,'Read `reading/planning/ACTIVE_GENERATION_PLAN.json` and the exact B1 entry in `reading/planning/topic_genre_matrix.json`.','Read `reading/planning/ACTIVE_GENERATION_PLAN.json` and the exact B2 entry in `reading/planning/topic_genre_matrix.json`.','TASKS roadmap'); t=rep(t,'Generate Urdu B1 in guarded unit or large bounded batches under the generation-first policy.','Generate Urdu B2 in guarded unit or large bounded batches under the generation-first policy.','TASKS generation'); t=rep(t,'- Urdu: 174/360 generated; A1-A2 complete, B1 in progress.','- Urdu: 180/360 generated; A1-B1 complete, B2 in progress.','TASKS Urdu'); t=rep(t,'- Project: 894/1080 generated.','- Project: 900/1080 generated.','TASKS project'); tp.write_text(t,encoding='utf-8')
    hp=ROOT/'reading/AGENT_HANDOFF_V2.md'; h=hp.read_text(encoding='utf-8'); h=rep(h,'- Canonical generated total: **894**.','- Canonical generated total: **900**.','handoff total'); h=rep(h,'- Urdu: **174/360**; A1-A2 generation complete and B1 generation in progress.','- Urdu: **180/360**; A1-B1 generation complete and B2 generation in progress.','handoff Urdu'); h=rep(h,'Continue **Urdu B1**, starting from Unit 10 / sequence 55, under:','Continue **Urdu B2**, starting from Unit 1 / sequence 1, under:','handoff frontier'); h=rep(h,'B1 Unit 10 uses the roadmap theme **B1 synthesis** with `longer integrated article`, `paired short texts`, and `checkpoint` genres.','B2 Unit 1 uses the roadmap theme **science and society** with `popular science`, `analysis`, and `paired viewpoints` genres.','handoff roadmap'); h=rep(h,'resume guarded generation at **Urdu B1 Unit 10 / sequence 55** using the B1 Unit 10 roadmap theme `B1 synthesis`.','resume guarded generation at **Urdu B2 Unit 1 / sequence 1** using the B2 Unit 1 roadmap theme `science and society`.','handoff next'); hp.write_text(h,encoding='utf-8')
    print('Urdu B1 complete: 60/60 canonical passages'); print('Production totals: project 900/1080; Urdu 180/360'); print('Next frontier: Urdu B2 Unit 1 / sequence 1')
    return 0
if __name__=='__main__': raise SystemExit(main())

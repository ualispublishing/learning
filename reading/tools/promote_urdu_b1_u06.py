#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
STAGE=ROOT/'reading/audit/urdu_b1_u06_generation_candidate'
TARGET=ROOT/'reading/urdu/b1/passages.jsonl'
SCHEMA=ROOT/'reading/schema/passage.schema.json'
DATE='2026-08-24'
IDS=[f'ur-b1-u06-p{i:02d}' for i in range(1,7)]
SEQS=list(range(31,37))
TARGETS=['ur-rank-1816','ur-rank-1856','ur-rank-1811','ur-rank-1823','ur-rank-1843','ur-rank-1833','ur-rank-1813','ur-rank-1854','ur-rank-1846','ur-rank-1870','ur-rank-1828','ur-rank-1800','ur-rank-1849','ur-rank-1848','ur-rank-1835']
ROLES=['instructional','reinforcement','interleaved','transfer','integration','checkpoint']
GENRES={'narrative','cultural explanation','reflection'}

def jl(p): return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def fail(x): raise SystemExit('Fail closed: '+x)
def rep(s,a,b,label):
    if s.count(a)!=1: fail(f'{label}: expected live-state phrase once: {a!r}')
    return s.replace(a,b,1)

def main():
    sch=json.loads(SCHEMA.read_text(encoding='utf-8')); req=set(sch['required'])
    ptypes=set(sch['properties']['passage_type']['enum']); domains=set(sch['properties']['domains']['items']['enum'])
    qtypes=set(sch['$defs']['question']['properties']['type']['enum']); strategies=set(sch['$defs']['newLexicalTarget']['properties']['context_strategy']['items']['enum'])
    a1=jl(ROOT/'reading/urdu/a1/passages.jsonl'); a2=jl(ROOT/'reading/urdu/a2/passages.jsonl'); b1=jl(TARGET)
    if len(a1)!=60 or len(a2)!=60: fail('Urdu A1/A2 must each contain 60 passages')
    if len(b1)!=30 or [r['sequence'] for r in b1]!=list(range(1,31)): fail('Urdu B1 must be exactly sequences 1-30 before Unit 6')
    sp=ROOT/'reading/STATUS.json'; cp=ROOT/'reading/CONTINUATION.json'; pp=ROOT/'reading/planning/ACTIVE_GENERATION_PLAN.json'
    s=json.loads(sp.read_text(encoding='utf-8')); c=json.loads(cp.read_text(encoding='utf-8')); p=json.loads(pp.read_text(encoding='utf-8'))
    if s['current']['canonical_passages']!=870 or s['languages']['urdu']['canonical_passages']!=150: fail('STATUS counts drifted from Unit 6 pre-state')
    if s['current']['active_language']!='urdu' or s['current']['active_level']!='B1': fail('active STATUS frontier is not Urdu B1')
    if p.get('active_unit')!=6 or p.get('start_sequence')!=31 or p.get('existing_active_level_passages')!=30: fail('active plan is not Unit 6 / sequence 31')
    if 'Urdu B1 Unit 6 / sequence 31' not in c.get('active_frontier',{}).get('production',{}).get('action',''): fail('CONTINUATION is not Unit 6 / sequence 31')
    before=TARGET.read_bytes(); before_sha=hashlib.sha256(before).hexdigest()
    taught={t['id'] for r in a1+a2+b1 for t in r.get('new_lexical_targets',[])}
    col=sorted(taught.intersection(TARGETS))
    if col: fail(f'target freshness collision: {col}')
    rows=[]; learner=[]
    for i in range(1,7):
        f=STAGE/f'ur-b1-u06-p{i:02d}.json'
        if not f.exists(): fail(f'missing {f.relative_to(ROOT)}')
        r=json.loads(f.read_text(encoding='utf-8')); r['word_count']=len(r['text'].split()); r['sentence_count']=r['text'].count('۔')
        for t in r.get('new_lexical_targets',[]): t['exposures_in_text']=r['text'].count(t['form'])
        f.write_text(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8'); rows.append(r)
        learner += [r['title'],r['text']] + [q['prompt'] for q in r['questions']] + [a['answer'] for a in r['answer_key']]
    if [r['id'] for r in rows]!=IDS or [r['sequence'] for r in rows]!=SEQS: fail('ID/sequence contract failed')
    if [r['passage_type'] for r in rows]!=ROLES: fail('role cycle failed')
    if [len(r['new_lexical_targets']) for r in rows]!=[3,3,3,3,3,0]: fail('target distribution failed')
    if [t['id'] for r in rows[:5] for t in r['new_lexical_targets']]!=TARGETS: fail('target order/identity failed')
    if any(t['exposures_in_text']<1 for r in rows for t in r['new_lexical_targets']): fail('new target absent from text')
    if not GENRES.issubset({r['genre'] for r in rows}): fail('required genres missing')
    prior=''
    for r in rows[:5]:
        for t in r['new_lexical_targets']:
            if t['form'] in prior: fail(f'premature exact-form exposure: {t["form"]}/{t["id"]}')
        prior += '\n'+'\n'.join([r['title'],r['text']]+[q['prompt'] for q in r['questions']]+[a['answer'] for a in r['answer_key']])
    p6=rows[-1]; forms={t['form'] for r in rows[:5] for t in r['new_lexical_targets']}; reviews={t['form'] for t in p6['review_lexical_targets'] if t['representation']=='running_text'}
    if p6['new_lexical_targets'] or not p6['speed_training']['timed'] or p6['speed_training']['new_word_policy']!='none': fail('P6 checkpoint policy failed')
    if reviews!=forms or any(x not in p6['text'] for x in forms): fail('P6 does not visibly recycle all 15 targets')
    for r in rows:
        miss=req-set(r)
        if miss: fail(f'{r["id"]} missing fields {sorted(miss)}')
        if r['passage_type'] not in ptypes or any(d not in domains for d in r['domains']): fail(f'enum failure {r["id"]}')
        if len(r['questions'])!=10 or len(r['answer_key'])!=10: fail(f'10x10 failed {r["id"]}')
        if not 220<=r['word_count']<=320: fail(f'B1 word band failed {r["id"]}: {r["word_count"]}')
        amap={a['id']:a for a in r['answer_key']}
        if set(amap)!={f'a{i}' for i in range(1,11)} or {q['id'] for q in r['questions']}!={f'q{i}' for i in range(1,11)}: fail(f'QA IDs drifted {r["id"]}')
        for t in r.get('new_lexical_targets',[]):
            if any(x not in strategies for x in t['context_strategy']): fail(f'context strategy failed {r["id"]}/{t["id"]}')
        for q in r['questions']:
            if q['type'] not in qtypes or q['answer_id'] not in amap or amap[q['answer_id']]['question_id']!=q['id']: fail(f'QA link/type failed {r["id"]}/{q["id"]}')
    if re.search(r'[A-Za-z\u0900-\u097F]','\n'.join(learner)): fail('learner-facing Latin/Devanagari leakage')
    payload=''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows).encode()
    TARGET.write_bytes(before+payload); after=TARGET.read_bytes()
    if after[:len(before)]!=before: fail('pre-existing canonical bytes changed')
    final=jl(TARGET)
    if len(final)!=36 or [r['sequence'] for r in final]!=list(range(1,37)) or [r['id'] for r in final[-6:]]!=IDS: fail('post-append canonical check failed')
    (STAGE/'manifest.json').write_text(json.dumps({'schema_version':1,'project_id':'LANG-A1C2','language':'ur','cefr':'B1','unit':6,'date':DATE,'status':'CANONICALIZED','canonical_target':'reading/urdu/b1/passages.jsonl','sequence_range':[31,36],'record_count':6,'release_promotion':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    checks={k:'PASS' for k in ['prior_a1_a2_60_each','prior_b1_sequences_1_through_30_exact','freshness_across_all_prior_urdu_target_ids','record_count','sequence_31_through_36','role_cycle','question_answer_10x10','bidirectional_links','new_target_distribution_3_3_3_3_3_0','new_target_text_exposure','first_introduction_order','required_genres','p6_checkpoint_policy','p6_all_target_recycling','learner_script_scan','schema_required_fields_enums_and_context_strategies','b1_word_band','preexisting_canonical_bytes_preserved']}
    (ROOT/'reading/audit/urdu_b1_u06_generation_validation_2026-08-24.json').write_text(json.dumps({'schema_version':1,'project_id':'LANG-A1C2','language':'ur','cefr':'B1','unit':6,'date':DATE,'canonicalized':True,'release_promotion':False,'word_counts':[r['word_count'] for r in rows],'checks':checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'reading/audit/urdu_b1_u06_promotion_2026-08-24.json').write_text(json.dumps({'schema_version':1,'project_id':'LANG-A1C2','language':'ur','cefr':'B1','unit':6,'date':DATE,'status':'CANONICAL_PROMOTION_PASS','release_promotion':False,'before_record_count':30,'after_record_count':36,'appended_sequences':SEQS,'appended_ids':IDS,'preexisting_bytes_preserved_exactly':True,'canonical_sha256_before':before_sha,'canonical_sha256_after':hashlib.sha256(after).hexdigest()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lp=ROOT/'reading/audit/urdu_b1_u06_lexical_sense_check_2026-08-24.json'; lex=json.loads(lp.read_text(encoding='utf-8')); lex['status']='PASS_FOR_GENERATION_TARGET_SENSES_AND_CANONICAL_FRESHNESS'; lex['freshness_result']='PASS'; lex['freshness_scope']='Exact target IDs checked against all canonical Urdu A1, A2, and B1 sequences 1-30 immediately before Unit 6 append.'; lp.write_text(json.dumps(lex,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    s['current']['canonical_passages']=876; s['current']['remaining_generation_passages']=204; u=s['languages']['urdu']; u['canonical_passages']=156; u['remaining_generation_passages']=204; u['generation_state']='B1_IN_PROGRESS'; u['next_generation_level']='B1'; sp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    c['production']['canonical_passages']=876; cu=c['production']['urdu']; cu['canonical_passages']=156; cu['state']='B1_GENERATION_IN_PROGRESS'; cu['next_generation_level']='B1'; c['active_frontier']['production']={'language':'urdu','level':'B1','action':'Continue generation-first production from Urdu B1 Unit 7 / sequence 37 using the canonical roadmap and ten-question contract.'}; c['exact_next_actions']=['Validate the routed state bundle and live canonical counts.','Use reading/planning/ACTIVE_GENERATION_PLAN.json to start guarded Urdu B1 Unit 7 generation at sequence 37.','Keep release/educator verification separate from generation progress.']; cp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    p['active_language']='urdu'; p['active_level']='B1'; p['active_unit']=7; p['start_sequence']=37; p['canonical_active_path']='reading/urdu/b1/passages.jsonl'; p['existing_active_level_passages']=36; p['roadmap_lookup']='$.levels.B1'; p['active_unit_roadmap']={'unit':7,'theme':'relationships and communication','genres':['narrative','advice column','reflection']}; pp.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tp=ROOT/'reading/TASKS.md'; t=tp.read_text(encoding='utf-8'); t=rep(t,'Canonical production frontier: **Urdu B1, Unit 6, sequence 31**.','Canonical production frontier: **Urdu B1, Unit 7, sequence 37**.','TASKS frontier'); t=rep(t,'- Urdu: 150/360 generated; A1-A2 complete, B1 in progress.','- Urdu: 156/360 generated; A1-A2 complete, B1 in progress.','TASKS Urdu'); t=rep(t,'- Project: 870/1080 generated.','- Project: 876/1080 generated.','TASKS project'); tp.write_text(t,encoding='utf-8')
    hp=ROOT/'reading/AGENT_HANDOFF_V2.md'; h=hp.read_text(encoding='utf-8'); h=rep(h,'- Canonical generated total: **870**.','- Canonical generated total: **876**.','handoff total'); h=rep(h,'- Urdu: **150/360**; A1-A2 generation complete and B1 generation in progress.','- Urdu: **156/360**; A1-A2 generation complete and B1 generation in progress.','handoff Urdu'); h=rep(h,'Continue **Urdu B1**, starting from Unit 6 / sequence 31, under:','Continue **Urdu B1**, starting from Unit 7 / sequence 37, under:','handoff frontier'); h=rep(h,'B1 Unit 6 uses the roadmap theme **travel, culture, and misunderstanding** with `narrative`, `cultural explanation`, and `reflection` genres.','B1 Unit 7 uses the roadmap theme **relationships and communication** with `narrative`, `advice column`, and `reflection` genres.','handoff roadmap'); h=rep(h,'resume guarded generation at **Urdu B1 Unit 6 / sequence 31** using the B1 Unit 6 roadmap theme `travel, culture, and misunderstanding`.','resume guarded generation at **Urdu B1 Unit 7 / sequence 37** using the B1 Unit 7 roadmap theme `relationships and communication`.','handoff next'); hp.write_text(h,encoding='utf-8')
    print('Unit 6 canonical promotion prepared: 30 -> 36 B1 records'); print('Production totals: 870 -> 876; Urdu 150 -> 156'); print('Next: Urdu B1 Unit 7 / sequence 37')
    return 0
if __name__=='__main__': raise SystemExit(main())

#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, subprocess

ROOT=Path('.')
A2=ROOT/'reading/urdu/a2/passages.jsonl'
A1=ROOT/'reading/urdu/a1/passages.jsonl'
STATUS=ROOT/'reading/STATUS.json'
CONT=ROOT/'reading/CONTINUATION.json'
TASKS=ROOT/'reading/TASKS.md'
HANDOFF=ROOT/'reading/AGENT_HANDOFF_V2.md'
LEX=ROOT/'reading/audit/urdu_a2_u05_lexical_sense_check_2026-08-24.json'
QUAL=ROOT/'reading/audit/urdu_a2_u05_quality_pass_2026-08-24.json'

SOURCE_BLOB='f010af2c7418a233aa9dfc47905c7a8c63696605'
PACKET_SHA='4cc7a4b3eb3893ba3b4d758a2e78312daafa03d861b654a573eed36b37272dd8'
PACKET_BYTES=51132
PARTS=[
('reading/staging/u05_exact_p01.tmp','d2d9e19066a77a0975ad60bc57a465499f3e204a'),
('reading/staging/u05_exact_p02.tmp','16424a7d60761b4d735f35ef7b354b3241c48845'),
('reading/staging/u05_exact_p03.tmp','97a32c4e6c3a55e36f356901d840e2865b6e19ba'),
('reading/staging/u05_exact_p04.tmp','ac1cc8999ee2c2f4d2b99d3a79d9ce497834f9a7'),
('reading/staging/u05_exact_p05.tmp','35e2c6c172591a4a4aeb44d2443257c682f0a5c6'),
('reading/staging/u05_exact_p06.tmp','7005d1f1b825c3bcc42289db968d5f65106902bc'),
]
TARGETS={
'ur-a2-u05-p01':['ur-rank-0833','ur-rank-0807'],
'ur-a2-u05-p02':['ur-rank-0809','ur-rank-0813'],
'ur-a2-u05-p03':['ur-rank-0774','ur-rank-0695'],
'ur-a2-u05-p04':['ur-rank-0944','ur-rank-0961'],
'ur-a2-u05-p05':[],
'ur-a2-u05-p06':[],
}
WCS=[213,211,208,214,210,211]
ROLES=['instructional','reinforcement','interleaved','transfer','integration','fluency']
GENRES={'profile','how-to','short article'}
EXTERNAL_EVIDENCE={
'ur-rank-0833':('Rekhta Dictionary','https://www.rekhta.org/urdudictionary?keyword=%D8%B4%D9%88%D9%82'),
'ur-rank-0807':('Wiktionary (Urdu entry; cites Urdu Lughat/Rekhta/Platts)','https://en.wiktionary.org/wiki/%D8%B5%D9%84%D8%A7%D8%AD%DB%8C%D8%AA'),
'ur-rank-0809':('Rekhta Dictionary','https://www.rekhta.org/urdudictionary?keyword=%D8%A7%D8%B3%D8%AA%D8%A7%D8%AF'),
'ur-rank-0813':('Cambridge English–Urdu Dictionary','https://dictionary.cambridge.org/dictionary/english-urdu/regular'),
'ur-rank-0774':('Cambridge English–Urdu Dictionary','https://dictionary.cambridge.org/dictionary/english-urdu/preparation'),
'ur-rank-0695':('Rekhta Dictionary','https://www.rekhta.org/urdudictionary?keyword=maqsad'),
'ur-rank-0944':('Rekhta Dictionary','https://www.rekhta.org/urdudictionary?keyword=%D9%85%D8%B7%D8%A7%D9%84%D8%B9%DB%81'),
'ur-rank-0961':('Rekhta Dictionary','https://www.rekhta.org/urdudictionary?keyword=%D8%BA%D9%88%D8%B1'),
}

def git_blob(b): return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def sha256(b): return hashlib.sha256(b).hexdigest()
def rows(b): return [json.loads(x) for x in b.splitlines()]
def fail(s): raise SystemExit(s)

src=A2.read_bytes()
if git_blob(src)!=SOURCE_BLOB: fail(f'A2 source blob drift: {git_blob(src)}')
old=rows(src)
if len(old)!=24 or [x['sequence'] for x in old]!=list(range(1,25)): fail('A2 source sequence/count drift')

st=json.loads(STATUS.read_text(encoding='utf-8'))
co=json.loads(CONT.read_text(encoding='utf-8'))
if st['current']['canonical_passages']!=804 or st['languages']['urdu']['canonical_passages']!=84: fail('STATUS frontier drift')
if co['production']['canonical_passages']!=804 or co['production']['urdu']['canonical_passages']!=84: fail('CONTINUATION count drift')
if 'Unit 5 / sequence 25' not in co['active_frontier']['production']['action']: fail('CONTINUATION frontier drift')

parts=[]
for path,expected in PARTS:
    b=(ROOT/path).read_bytes()
    if git_blob(b)!=expected: fail(f'staged byte drift: {path}')
    parts.append(b)
packet=b'\n'.join(parts)+b'\n'
if len(packet)!=PACKET_BYTES or sha256(packet)!=PACKET_SHA: fail('reviewed Unit 5 packet hash/size drift')
recs=rows(packet)
if len(recs)!=6: fail('Unit 5 packet count')

introduced=set()
for p in [A1,A2]:
    for r in rows(p.read_bytes()):
        introduced |= {t['id'] for t in r.get('new_lexical_targets',[])}

questions=answers=0
exposures={}
for i,r in enumerate(recs):
    rid=f'ur-a2-u05-p{i+1:02d}'
    if (r.get('id'),r.get('sequence'),r.get('unit'),r.get('language'),r.get('cefr'))!=(rid,25+i,5,'ur','A2'): fail(f'{rid}: identity')
    if r.get('passage_type')!=ROLES[i] or r.get('genre') not in GENRES: fail(f'{rid}: roadmap')
    wc=len(r['text'].split())
    if wc!=r.get('word_count') or wc!=WCS[i] or not 140<=wc<=220: fail(f'{rid}: word count')
    qs,ans=r['questions'],r['answer_key']
    if len(qs)!=10 or len(ans)!=10: fail(f'{rid}: q/a count')
    questions+=10; answers+=10
    for n,(q,a) in enumerate(zip(qs,ans),1):
        if q.get('id')!=f'q{n}' or q.get('answer_id')!=f'a{n}' or a.get('id')!=f'a{n}' or a.get('question_id')!=f'q{n}' or not a.get('answer','').strip(): fail(f'{rid}: q/a link')
    nts=r.get('new_lexical_targets',[])
    ids=[t['id'] for t in nts]
    if ids!=TARGETS[rid]: fail(f'{rid}: target set')
    exposures[rid]={}
    for t in nts:
        if t['id'] in introduced: fail(f'{rid}: target not fresh: {t["id"]}')
        c=r['text'].count(t['form'])
        if c!=t['exposures_in_text'] or c<2: fail(f'{rid}: target exposure')
        if not any(t['id'] in q.get('target_ids',[]) for q in qs): fail(f'{rid}: target unassessed')
        exposures[rid][t['id']]=c
if sum(len(v) for v in TARGETS.values())!=8: fail('target total')
if recs[4]['new_lexical_targets'] or recs[5]['new_lexical_targets']: fail('P5/P6 new-target policy')
if recs[5]['speed_training'].get('new_word_policy')!='none' or not recs[5]['speed_training'].get('timed'): fail('P6 fluency policy')

result=src+packet
if len(rows(result))!=30: fail('result A2 count')
A2.write_bytes(result)
result_blob=git_blob(result)

target_rows=[]
for r in recs[:4]:
    for t in r['new_lexical_targets']:
        source,url=EXTERNAL_EVIDENCE[t['id']]
        target_rows.append({'id':t['id'],'form':t['form'],'source_rank':t['source_rank'],'accepted_sense':t['intended_sense'],'external_evidence_source':source,'url':url})
LEX.write_text(json.dumps({
'schema_version':1,'project_id':'LANG-A1C2','language':'ur','cefr':'A2','unit':5,'date':'2026-08-24',
'status':'PASS_FOR_GENERATION_TARGET_SENSES',
'scope':'Deliberate learner-facing senses only. This does not validate whole-passage linguistic/pedagogical quality or educator/publication release readiness.',
'source_lexicon':'reading/lexicons/urdu.jsonl',
'canonical_freshness_method':'All eight candidate IDs were searched against the complete live canonical Urdu A1 and Urdu A2 new_lexical_targets and were absent before Unit 5.',
'targets':target_rows,
'generation_policy':{'P1_P4_new_targets_per_passage':2,'P5_new_targets':0,'P6_new_targets':0,'P6_new_word_policy':'none'},
'quality_promotion':False
},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

QUAL.write_text(json.dumps({
'schema_version':1,'project_id':'LANG-A1C2','language':'ur','cefr':'A2','unit':5,'date':'2026-08-24',
'status':'PASS_AFTER_PRECANONICAL_READER_PASS',
'scope':'Bounded generation-stage reader-first pass for Unit 5 only: naturalness, target-sense clarity, answer grounding/linkage, operational A2 grammar, word-band checks, roadmap role/genre checks, and fluency new-word policy. Formal corpus-wide linguistic, pedagogical, CEFR/coverage, independent/native, and educator-release gates remain pending.',
'source_canonical_git_blob':SOURCE_BLOB,'source_a2_passages':24,'packet_sha256':PACKET_SHA,
'result_canonical_git_blob':result_blob,'result_a2_passages':30,'project_passages_after':810,'urdu_passages_after':90,
'unit_sequences':list(range(25,31)),'passages':6,'questions':questions,'answers':answers,
'word_counts':{r['id']:r['word_count'] for r in recs},'new_target_ids_by_passage':TARGETS,'new_target_exposures':exposures,
'lexical_sense_evidence':'reading/audit/urdu_a2_u05_lexical_sense_check_2026-08-24.json',
'reader_first_note':'Reader-first pass corrected the guitar passage to say that the learner records her practice rather than her voice; final packet is hash-locked above.',
'checks':{'source_blob_guard':True,'packet_hash_guard':True,'six_component_blob_guards':True,'fresh_target_ids_against_live_urdu_a1_a2':True,'six_passage_role_order':True,'roadmap_genres_only':True,'word_band_140_220':True,'exactly_10_questions_and_10_answers_each':True,'bidirectional_q_a_links':True,'each_new_target_assessed':True,'target_exposure_metadata_recounted':True,'p5_has_no_new_deliberate_targets':True,'p6_has_no_new_deliberate_targets':True,'p6_new_word_policy_none':True,'post_write_project_and_urdu_counts':True},
'quality_promotion':False,'educator_release_ready':False
},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

st['current']['canonical_passages']=810; st['current']['remaining_generation_passages']=270
st['languages']['urdu']['canonical_passages']=90; st['languages']['urdu']['remaining_generation_passages']=270
STATUS.write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

co['production']['canonical_passages']=810; co['production']['urdu']['canonical_passages']=90
co['active_frontier']['production']['action']='Continue generation-first production from Urdu A2 Unit 6 / sequence 31 using the canonical roadmap and ten-question contract. Do not reopen Urdu A1 generation unless fresh evidence identifies a concrete defect.'
oldnext='Use reading/planning/ACTIVE_GENERATION_PLAN.json to start the next guarded Urdu A2 Unit 5 batch at sequence 25.'
newnext='Use reading/planning/ACTIVE_GENERATION_PLAN.json to start the next guarded Urdu A2 Unit 6 batch at sequence 31.'
if oldnext not in co['exact_next_actions']: fail('CONTINUATION exact-next-action drift')
co['exact_next_actions']=[newnext if x==oldnext else x for x in co['exact_next_actions']]
CONT.write_text(json.dumps(co,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def rep(path,old,new):
    s=path.read_text(encoding='utf-8')
    if old not in s: fail(f'{path}: missing expected live text: {old}')
    path.write_text(s.replace(old,new),encoding='utf-8')
rep(TASKS,'Canonical production frontier: **Urdu A2, Unit 5, sequence 25**.','Canonical production frontier: **Urdu A2, Unit 6, sequence 31**.')
rep(TASKS,'- Urdu: 84/360 generated; A1 complete, A2 in progress.','- Urdu: 90/360 generated; A1 complete, A2 in progress.')
rep(TASKS,'- Project: 804/1080 generated.','- Project: 810/1080 generated.')
rep(HANDOFF,'- Canonical generated total: **804**.','- Canonical generated total: **810**.')
rep(HANDOFF,'- Urdu: **84/360**; A1 generation complete and A2 generation in progress.','- Urdu: **90/360**; A1 generation complete and A2 generation in progress.')
rep(HANDOFF,'- Urdu A2 canonical path: `reading/urdu/a2/passages.jsonl`; Units 1-4 currently contain sequences 1-24.','- Urdu A2 canonical path: `reading/urdu/a2/passages.jsonl`; Units 1-5 currently contain sequences 1-30.')
rep(HANDOFF,'Continue **Urdu A2**, starting from Unit 5 / sequence 25, under:','Continue **Urdu A2**, starting from Unit 6 / sequence 31, under:')
rep(HANDOFF,'Unit 5 uses the roadmap theme **hobbies and learning skills** with `profile`, `how-to`, and `short article` genres.','Unit 6 uses the roadmap theme **transport and travel** with `travel story`, `information page`, and `message` genres.')
rep(HANDOFF,'Run `python reading/tools/validate_continuation_state.py`; if it passes, resume guarded generation at **Urdu A2 Unit 5 / sequence 25** using the Unit 5 roadmap theme `hobbies and learning skills`.','Run `python reading/tools/validate_continuation_state.py`; if it passes, resume guarded generation at **Urdu A2 Unit 6 / sequence 31** using the Unit 6 roadmap theme `transport and travel`.')

subprocess.run(['python','reading/tools/extract_active_generation_plan.py'],check=True)
subprocess.run(['python','reading/tools/refresh_state_manifest.py'],check=True)
subprocess.run(['python','reading/tools/validate_continuation_state.py'],check=True)
print(json.dumps({'status':'PASS','source_blob':SOURCE_BLOB,'packet_sha256':PACKET_SHA,'result_blob':result_blob,'project_after':810,'urdu_after':90,'next_unit':6,'next_sequence':31}))

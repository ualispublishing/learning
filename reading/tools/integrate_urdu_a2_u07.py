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
PLAN=ROOT/'reading/planning/ACTIVE_GENERATION_PLAN.json'
LEX=ROOT/'reading/audit/urdu_a2_u07_lexical_sense_check_2026-08-24.json'
QUAL=ROOT/'reading/audit/urdu_a2_u07_quality_pass_2026-08-24.json'

SOURCE_BLOB='0d686ecf3ab8f89cd494a437adcebbf0270f62a1'
PACKET_SHA='f3cdb83aac3a1df30ba4ea5c3883b1b0883350967b22ae00d6248dd3c515722c'
PACKET_BYTES=51529
PARTS=[
('reading/staging/u07_exact_p01.tmp','6e96845dc021832ab0e7427d43971770ece85a79'),
('reading/staging/u07_exact_p02.tmp','b3d0da535ad12b839ede516dd53057324c9a5a2e'),
('reading/staging/u07_exact_p03.tmp','b5cb60dabb4e41993a57c961ec1a793f3c8710b9'),
('reading/staging/u07_exact_p04.tmp','f61caf7a95ce7d058237d7dc13d3b11c8a9bbab9'),
('reading/staging/u07_exact_p05.tmp','2aee366e5803a9a98343fb9ffbb9b1b2e647995c'),
('reading/staging/u07_exact_p06.tmp','4216560fbb29eaa1c4e1af60b071a37da8dcaaad'),
]
TARGETS={
'ur-a2-u07-p01':['ur-rank-0530','ur-rank-0541'],
'ur-a2-u07-p02':['ur-rank-0586','ur-rank-0618'],
'ur-a2-u07-p03':['ur-rank-0622','ur-rank-0646'],
'ur-a2-u07-p04':['ur-rank-0648','ur-rank-0649'],
'ur-a2-u07-p05':[],
'ur-a2-u07-p06':[],
}
WCS=[198,193,194,211,220,201]
ROLES=['instructional','reinforcement','interleaved','transfer','integration','fluency']
GENRES={'brief news report','announcement','reaction'}
EXTERNAL_EVIDENCE={
'ur-rank-0530':('Rekhta Dictionary','https://www.rekhtadictionary.com/meaning-of-tanziim?lang=ur'),
'ur-rank-0541':('Rekhta Dictionary','https://www.rekhta.org/urdudictionary?keyword=%D9%88%D8%A7%D9%82%D8%B9%D8%A7%D8%AA'),
'ur-rank-0586':('Rekhta Dictionary','https://www.rekhta.org/urdudictionary?keyword=news'),
'ur-rank-0618':('Rekhta Dictionary','https://www.rekhta.org/urdudictionary?keyword=%D8%B9%D9%88%D8%A7%D9%85'),
'ur-rank-0622':('Rekhta Dictionary','https://www.rekhtadictionary.com/meaning-of-natiija?lang=ur'),
'ur-rank-0646':('Rekhta Dictionary','https://www.rekhtadictionary.com/meaning-of-sargarm?lang=ur'),
'ur-rank-0648':('Rekhta Dictionary','https://www.rekhtadictionary.com/meaning-of-shahrii?lang=ur'),
'ur-rank-0649':('Rekhta Dictionary','https://www.rekhtadictionary.com/meaning-of-intizaamiya?lang=ur'),
}


def git_blob(b): return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def sha256(b): return hashlib.sha256(b).hexdigest()
def rows(b): return [json.loads(x) for x in b.splitlines()]
def fail(s): raise SystemExit(s)

src=A2.read_bytes()
if git_blob(src)!=SOURCE_BLOB: fail(f'A2 source blob drift: {git_blob(src)}')
old=rows(src)
if len(old)!=36 or [x['sequence'] for x in old]!=list(range(1,37)): fail('A2 source sequence/count drift')

st=json.loads(STATUS.read_text(encoding='utf-8'))
co=json.loads(CONT.read_text(encoding='utf-8'))
if st['current']['canonical_passages']!=816 or st['languages']['urdu']['canonical_passages']!=96: fail('STATUS frontier drift')
if co['production']['canonical_passages']!=816 or co['production']['urdu']['canonical_passages']!=96: fail('CONTINUATION count drift')
if 'Unit 7 / sequence 37' not in co['active_frontier']['production']['action']: fail('CONTINUATION frontier drift')

parts=[]
for path,expected in PARTS:
    b=(ROOT/path).read_bytes()
    if git_blob(b)!=expected: fail(f'staged byte drift: {path}')
    parts.append(b)
packet=b'\n'.join(parts)+b'\n'
if len(packet)!=PACKET_BYTES or sha256(packet)!=PACKET_SHA: fail('reviewed Unit 7 packet hash/size drift')
recs=rows(packet)
if len(recs)!=6: fail('Unit 7 packet count')

# Exact-ID freshness is intentionally checked across BOTH live Urdu levels.
# This protects against reused/colliding lexicon IDs even when the attached form differs.
introduced=set()
introduced_forms={}
for p in [A1,A2]:
    for r in rows(p.read_bytes()):
        for t in r.get('new_lexical_targets',[]):
            introduced.add(t['id'])
            introduced_forms.setdefault(t['id'],set()).add(t.get('form'))

# Known lexicon/canonical collision found during Unit 7 planning. It is excluded from TARGETS.
unsafe_id='ur-rank-0636'
if unsafe_id not in introduced: fail('expected canonical collision evidence for ur-rank-0636 is missing; re-audit freshness assumptions')

questions=answers=0
exposures={}
for i,r in enumerate(recs):
    rid=f'ur-a2-u07-p{i+1:02d}'
    if (r.get('id'),r.get('sequence'),r.get('unit'),r.get('language'),r.get('cefr'))!=(rid,37+i,7,'ur','A2'): fail(f'{rid}: identity')
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
        if t['id'] in introduced: fail(f'{rid}: target ID not fresh: {t["id"]}; canonical forms={sorted(x for x in introduced_forms.get(t["id"],set()) if x)}')
        c=r['text'].count(t['form'])
        if c!=t['exposures_in_text'] or c<2: fail(f'{rid}: target exposure')
        if not any(t['id'] in q.get('target_ids',[]) for q in qs): fail(f'{rid}: target unassessed')
        exposures[rid][t['id']]=c
if sum(len(v) for v in TARGETS.values())!=8: fail('target total')
if recs[4]['new_lexical_targets'] or recs[5]['new_lexical_targets']: fail('P5/P6 new-target policy')
if recs[5]['speed_training'].get('new_word_policy')!='none' or not recs[5]['speed_training'].get('timed'): fail('P6 fluency policy')

result=src+packet
if len(rows(result))!=42: fail('result A2 count')
A2.write_bytes(result)
result_blob=git_blob(result)

target_rows=[]
for r in recs[:4]:
    for t in r['new_lexical_targets']:
        source,url=EXTERNAL_EVIDENCE[t['id']]
        target_rows.append({'id':t['id'],'form':t['form'],'source_rank':t['source_rank'],'accepted_sense':t['intended_sense'],'external_evidence_source':source,'url':url})
LEX.write_text(json.dumps({
'schema_version':1,'project_id':'LANG-A1C2','language':'ur','cefr':'A2','unit':7,'date':'2026-08-24',
'status':'PASS_FOR_GENERATION_TARGET_SENSES',
'scope':'Deliberate learner-facing senses only. This does not validate whole-passage linguistic/pedagogical quality or educator/publication release readiness.',
'source_lexicon':'reading/lexicons/urdu.jsonl',
'canonical_freshness_method':'All eight final target IDs were searched against the complete live canonical Urdu A1 and pre-append Urdu A2 new_lexical_targets and were absent before Unit 7. Freshness is enforced by ID, not merely by form.',
'collision_note':{'excluded_id':'ur-rank-0636','reason':'Current project lexicon maps this ID to مشترکہ, while canonical Urdu A1 already uses the same ID for دسمبر. The ID was excluded from Unit 7 rather than treated as fresh.'},
'targets':target_rows,
'generation_policy':{'P1_P4_new_targets_per_passage':2,'P5_new_targets':0,'P6_new_targets':0,'P6_new_word_policy':'none'},
'quality_promotion':False
},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

QUAL.write_text(json.dumps({
'schema_version':1,'project_id':'LANG-A1C2','language':'ur','cefr':'A2','unit':7,'date':'2026-08-24',
'status':'PASS_AFTER_PRECANONICAL_READER_PASS',
'scope':'Bounded generation-stage reader-first pass for Unit 7 only: naturalness, target-sense clarity, answer grounding/linkage, operational A2 grammar, word-band checks, roadmap role/genre checks, fictional/local-news framing, and fluency new-word policy. Formal corpus-wide linguistic, pedagogical, CEFR/coverage, independent/native, and educator-release gates remain pending.',
'source_canonical_git_blob':SOURCE_BLOB,'source_a2_passages':36,'packet_sha256':PACKET_SHA,
'result_canonical_git_blob':result_blob,'result_a2_passages':42,'project_passages_after':822,'urdu_passages_after':102,
'unit_sequences':list(range(37,43)),'passages':6,'questions':questions,'answers':answers,
'word_counts':{r['id']:r['word_count'] for r in recs},'new_target_ids_by_passage':TARGETS,'new_target_exposures':exposures,
'lexical_sense_evidence':'reading/audit/urdu_a2_u07_lexical_sense_check_2026-08-24.json',
'reader_first_note':'Reader-first pass normalized پودے لگانے in the garden announcement and smoothed the description of the new park seating before the final packet hash was frozen.',
'checks':{'source_blob_guard':True,'packet_hash_guard':True,'six_component_blob_guards':True,'fresh_target_ids_against_live_urdu_a1_a2':True,'known_unsafe_id_collision_excluded':True,'six_passage_role_order':True,'roadmap_genres_only':True,'word_band_140_220':True,'exactly_10_questions_and_10_answers_each':True,'bidirectional_q_a_links':True,'each_new_target_assessed':True,'target_exposure_metadata_recounted':True,'constructed_local_scenarios_not_real_world_claims':True,'p5_has_no_new_deliberate_targets':True,'p6_has_no_new_deliberate_targets':True,'p6_new_word_policy_none':True,'post_write_project_and_urdu_counts':True},
'quality_promotion':False,'educator_release_ready':False
},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

st['current']['canonical_passages']=822; st['current']['remaining_generation_passages']=258
st['languages']['urdu']['canonical_passages']=102; st['languages']['urdu']['remaining_generation_passages']=258
STATUS.write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

co['production']['canonical_passages']=822; co['production']['urdu']['canonical_passages']=102
co['active_frontier']['production']['action']='Continue generation-first production from Urdu A2 Unit 8 / sequence 43 using the canonical roadmap and ten-question contract. Do not reopen Urdu A1 generation unless fresh evidence identifies a concrete defect.'
oldnext='Use reading/planning/ACTIVE_GENERATION_PLAN.json to start the next guarded Urdu A2 Unit 7 batch at sequence 37.'
newnext='Use reading/planning/ACTIVE_GENERATION_PLAN.json to start the next guarded Urdu A2 Unit 8 batch at sequence 43.'
if oldnext not in co['exact_next_actions']: fail('CONTINUATION exact-next-action drift')
co['exact_next_actions']=[newnext if x==oldnext else x for x in co['exact_next_actions']]
CONT.write_text(json.dumps(co,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def rep(path,old,new):
    s=path.read_text(encoding='utf-8')
    if old not in s: fail(f'{path}: missing expected live text: {old}')
    path.write_text(s.replace(old,new),encoding='utf-8')
rep(TASKS,'Canonical production frontier: **Urdu A2, Unit 7, sequence 37**.','Canonical production frontier: **Urdu A2, Unit 8, sequence 43**.')
rep(TASKS,'- Urdu: 96/360 generated; A1 complete, A2 in progress.','- Urdu: 102/360 generated; A1 complete, A2 in progress.')
rep(TASKS,'- Project: 816/1080 generated.','- Project: 822/1080 generated.')
rep(HANDOFF,'- Canonical generated total: **816**.','- Canonical generated total: **822**.')
rep(HANDOFF,'- Urdu: **96/360**; A1 generation complete and A2 generation in progress.','- Urdu: **102/360**; A1 generation complete and A2 generation in progress.')
rep(HANDOFF,'- Urdu A2 canonical path: `reading/urdu/a2/passages.jsonl`; Units 1-6 currently contain sequences 1-36.','- Urdu A2 canonical path: `reading/urdu/a2/passages.jsonl`; Units 1-7 currently contain sequences 1-42.')
rep(HANDOFF,'Continue **Urdu A2**, starting from Unit 7 / sequence 37, under:','Continue **Urdu A2**, starting from Unit 8 / sequence 43, under:')

# Derive next roadmap from the canonical matrix after the frontier changes; do not guess it.
subprocess.run(['python','reading/tools/extract_active_generation_plan.py'],check=True)
plan=json.loads(PLAN.read_text(encoding='utf-8'))
if plan.get('active_unit')!=8 or plan.get('start_sequence')!=43: fail('derived Unit 8 plan drift')
road=plan['active_unit_roadmap']
theme=road['theme']; genres=road['genres']
old_line='Unit 7 uses the roadmap theme **community events and simple news** with `brief news report`, `announcement`, and `reaction` genres.'
new_line=f"Unit 8 uses the roadmap theme **{theme}** with " + ', '.join(f'`{g}`' for g in genres[:-1]) + (f', and `{genres[-1]}` genres.' if len(genres)>1 else f'`{genres[0]}` genre.')
rep(HANDOFF,old_line,new_line)
rep(HANDOFF,'Run `python reading/tools/validate_continuation_state.py`; if it passes, resume guarded generation at **Urdu A2 Unit 7 / sequence 37** using the Unit 7 roadmap theme `community events and simple news`.','Run `python reading/tools/validate_continuation_state.py`; if it passes, resume guarded generation at **Urdu A2 Unit 8 / sequence 43** using the Unit 8 roadmap theme `'+theme+'`.')

subprocess.run(['python','reading/tools/refresh_state_manifest.py'],check=True)
subprocess.run(['python','reading/tools/validate_continuation_state.py'],check=True)
print(json.dumps({'status':'PASS','source_blob':SOURCE_BLOB,'packet_sha256':PACKET_SHA,'result_blob':result_blob,'project_after':822,'urdu_after':102,'next_unit':8,'next_sequence':43,'next_theme':theme,'next_genres':genres},ensure_ascii=False))

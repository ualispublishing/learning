#!/usr/bin/env python3
import json,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).parent
QB=ROOT/'question-bank'
errors=[]
def check(cond,msg):
    if not cond: errors.append(msg)

def parse_meta():
    raw=(ROOT/'data-meta.js').read_text(encoding='utf-8').strip();marker=';window.CISSP_CHUNKS=[];'
    assert raw.startswith('window.CISSP_META=') and marker in raw
    return json.loads(raw[len('window.CISSP_META='):raw.index(marker)])

def parse_chunk(name):
    raw=(ROOT/name).read_text(encoding='utf-8').strip();pre='window.CISSP_CHUNKS.push(';suf=');'
    assert raw.startswith(pre) and raw.endswith(suf),f'{name} wrapper invalid'
    return json.loads(raw[len(pre):-len(suf)])

def load_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]

meta=parse_meta();chunks=[parse_chunk(f'data-d{i}.js') for i in range(1,9)]+[parse_chunk('data-ai.js'),parse_chunk('data-precision.js')]
objectives=sum((c['objectives'] for c in chunks),[]);high=sum((c['high'] for c in chunks),[]);base_questions=sum((c['questions'] for c in chunks),[])
release_manifest=json.loads((QB/'RELEASED_BATCHES.json').read_text(encoding='utf-8'));released=[]
for b in release_manifest.get('released_batches',[]):
    batch=[]
    for rel in b.get('files',[]):batch+=load_jsonl(ROOT/rel)
    released+=batch
    dist=Counter(x.get('difficulty_tier') for x in batch)
    check(len(batch)==b.get('records'),f"{b.get('batch_id')} record count drift")
    check(sum(x.get('format')=='mcq' for x in batch)==b.get('standard_mcq'),f"{b.get('batch_id')} MCQ count drift")
    check(sum(x.get('format')=='bellringer' for x in batch)==b.get('bellringers'),f"{b.get('batch_id')} Bellringer count drift")
    check({k:dist.get(k,0) for k in ('F','E','S','B')}==b.get('difficulty'),f"{b.get('batch_id')} difficulty drift")
released_mcq=[x for x in released if x.get('format')=='mcq'];bellringers=[x for x in released if x.get('format')=='bellringer'];all_questions=base_questions+released_mcq
cover_raw=(ROOT/'coverage-detail.js').read_text(encoding='utf-8').strip();marker=';\nwindow.CISSP_AI_COVERAGE='
assert cover_raw.startswith('window.CISSP_COVERAGE=') and marker in cover_raw and cover_raw.endswith(';')
coverage=json.loads(cover_raw[len('window.CISSP_COVERAGE='):cover_raw.index(marker)]);ai=json.loads(cover_raw[cover_raw.index(marker)+len(marker):-1])
release=json.loads((ROOT/'RELEASE_STATUS.json').read_text(encoding='utf-8'));semantic=json.loads((ROOT/'SEMANTIC_ITEM_AUDIT.json').read_text(encoding='utf-8'))
expected_counts={1:12,2:6,3:10,4:3,5:6,6:5,7:15,8:5};expected_weights={1:16,2:10,3:13,4:13,5:13,6:12,7:13,8:10}
check(len(meta['domains'])==8,'Expected 8 domains');check(sum(d['weight'] for d in meta['domains'])==100,'Weights !=100');check({d['num']:d['weight'] for d in meta['domains']}==expected_weights,'Official weights drift')
for d,n in expected_counts.items():check(sum(o['domain_num']==d for o in objectives)==n,f'D{d} objective count wrong')
ids=[o['id'] for o in objectives];check(len(ids)==62 and len(ids)==len(set(ids)),'Objective IDs incomplete/duplicate')
for d,n in expected_counts.items():check(all(f'{d}.{i}' in ids for i in range(1,n+1)),f'D{d} missing objective ID')
check(set(coverage)==set(ids),'Subtopic coverage keys must exactly match objectives');check(all(isinstance(v,list) and v and all(isinstance(x,str) and x.strip() for x in v) for v in coverage.values()),'Invalid subtopic coverage')
check(set(ai)==set(str(i) for i in range(1,9)),'AI coverage must include all domains');check(all(isinstance(v,list) and v for v in ai.values()),'Empty AI coverage domain')
for o in objectives:
    check(bool(o.get('direct','').strip()) and bool(o.get('trap','').strip()),f"Objective {o['id']} missing content");check(all(s in meta['sources'] for s in o.get('source_ids',[])),f"Objective {o['id']} source invalid")
for h in high:
    check(h['objective'] in ids,f"Card {h['id']} objective invalid");check(bool(h.get('front','').strip()) and bool(h.get('direct','').strip()) and bool(h.get('trap','').strip()),f"Card {h['id']} missing content");check(all(s in meta['sources'] for s in h.get('source_ids',[])),f"Card {h['id']} source invalid")
for q in base_questions:
    check(q['objective'] in ids,f"Base question {q['id']} objective invalid");check(len(q['options'])==4 and isinstance(q['answer'],int) and 0<=q['answer']<4,f"Base question {q['id']} answer/options invalid");check(bool(q.get('stem','').strip()) and bool(q.get('explanation','').strip()),f"Base question {q['id']} content missing")
for q in released:
    check(all(o in ids for o in q.get('objectives',[])),f"Released record {q.get('id')} objective invalid");check(all(s in meta['sources'] for s in q.get('source_ids',[])),f"Released record {q.get('id')} source invalid");check(str(q.get('review_status','')).startswith('SEMANTIC_REVIEWED_'),f"Released record {q.get('id')} not semantically reviewed");orig=q.get('originality',{});check(orig.get('origin')=='original-from-public-scope' and orig.get('no_external_question_seed') is True,f"Released record {q.get('id')} originality provenance invalid")
    if q.get('format')=='mcq':check(len(q.get('options',[]))==4 and isinstance(q.get('answer'),int) and 0<=q['answer']<4 and len(q.get('distractor_rationales',[]))==4,f"Released MCQ {q.get('id')} invalid")
    elif q.get('format')=='bellringer':check(q.get('difficulty_tier')=='B' and 4<=len(q.get('prompts',[]))<=8 and bool(q.get('rubric')),f"Bellringer {q.get('id')} invalid")
    else:check(False,f"Released record {q.get('id')} format invalid")
check(len({h['id'] for h in high})==len(high),'Duplicate high-card ID');check(len({q['id'] for q in all_questions})==len(all_questions),'Duplicate standard-question ID');check(len({q['id'] for q in released})==len(released),'Duplicate released-batch ID')
computed_cards=62+len(high);subtopics=sum(len(v) for v in coverage.values());ai_areas=sum(len(v) for v in ai.values());sources=len(meta['sources'])
check(computed_cards==140,'Runtime cards !=140');check(len(base_questions)==56,'Base question baseline !=56');check(len(all_questions)==79,'Released standard MCQs !=79');check(len(bellringers)==1,'Released Bellringers !=1');check(len(all_questions)+len(bellringers)==80,'Question-bank records !=80');check(sources==20,'Source count !=20');check(subtopics==344,'Subtopic count !=344');check(ai_areas==33,'AI area count !=33')
for d in range(1,9):
    check(sum((q.get('domain_num') if 'domain_num' in q else q.get('domain_primary'))==d for q in all_questions)>=9,f'D{d} standard-question coverage too low');check(sum(h['domain_num']==d and h['id'].startswith('PX-') for h in high)==4,f'D{d} precision cards !=4');check(sum(h['domain_num']==d and h['id'].startswith('AI-') for h in high)==1,f'D{d} AI cards !=1')
cal_raw=(ROOT/'data-question-calibration.js').read_text(encoding='utf-8');check(all(f'"Q-{i:03d}"' in cal_raw for i in range(1,57)),'Base difficulty calibration incomplete')
check(meta['meta'].get('version')=='1.3.0','Metadata version drift');check(meta['meta'].get('audited_on')=='2026-08-24','Metadata audit date drift');check(meta['meta'].get('objective_count')==62 and meta['meta'].get('subtopic_checks')==subtopics and meta['meta'].get('ai_coverage_areas')==ai_areas and meta['meta'].get('card_count')==computed_cards,'Metadata knowledge counts drift');check(meta['meta'].get('question_count')==79 and meta['meta'].get('bellringer_count')==1 and meta['meta'].get('question_bank_records')==80 and meta['meta'].get('semantic_items_reviewed')==220,'Metadata bank counts drift');check(meta['meta'].get('source_count')==sources and meta['meta'].get('domain_weight_total')==100,'Metadata source/weight drift')
rs=release.get('scope',{});check(release.get('project_id')=='CISSP-ATLAS' and release.get('release')=='1.3.0' and release.get('status')=='READY_FOR_STUDY','Release identity/version/state drift');check(rs.get('domains')==8 and rs.get('numbered_objectives')==62 and rs.get('subtopic_checks')==subtopics and rs.get('ai_coverage_areas')==ai_areas and rs.get('layered_cards')==computed_cards and rs.get('standard_scenario_questions')==79 and rs.get('bellringers')==1 and rs.get('question_bank_records')==80 and rs.get('semantic_items_reviewed')==220 and rs.get('sources')==sources and rs.get('official_weight_total_percent')==100,'Release scope drift')
expected_semantic={*(f"OBJ-{o['id']}" for o in objectives),*(h['id'] for h in high),*(q['id'] for q in base_questions),*(q['id'] for q in released)};sem_items=semantic.get('items',{});allowed={'VERIFIED','VERIFIED_AFTER_CORRECTION','VERIFIED_WITH_SOURCE_SCOPE_NOTE'}
check(semantic.get('release')=='1.3.0' and semantic.get('audit_date')=='2026-08-24','Semantic release/date drift');check(set(sem_items)==expected_semantic,f'Semantic coverage mismatch expected {len(expected_semantic)} got {len(sem_items)}');check(len(expected_semantic)==220,'Semantic item count !=220');check(all(v.get('status') in allowed for v in sem_items.values()),'Semantic audit contains unreviewed status');ss=semantic.get('scope',{});check(ss.get('objective_cards')==62 and ss.get('high_yield_cards')==38 and ss.get('ai_cards')==8 and ss.get('precision_cards')==32 and ss.get('standard_questions')==79 and ss.get('bellringers')==1 and ss.get('total_items')==220,'Semantic scope drift');summary=semantic.get('summary',{});check(summary.get('answer_key_reversals')==0 and summary.get('material_factual_errors_remaining')==0,'Semantic summary reports unresolved error')
html=(ROOT/'index.html').read_text(encoding='utf-8');required=['data-meta.js']+[f'data-d{i}.js' for i in range(1,9)]+['data-ai.js','data-precision.js','coverage-detail.js','data-question-calibration.js','bootstrap.js','styles.css','mobile-fix.css','enhancements.css','id="today"','id="learn"','id="practice"','id="blueprint"','id="progress"','id="sources"','id="quizDifficulty"','id="startBellringer"','<option>79</option>','RELEASE v1.3']
check(all(x in html for x in required),'HTML shell/assets/v1.3 controls incomplete');check('Weighted mixed domains' not in html,'Misleading weighted-mix wording present');bootstrap=(ROOT/'bootstrap.js').read_text(encoding='utf-8');app=(ROOT/'app.js').read_text(encoding='utf-8');enh=(ROOT/'enhancements.js').read_text(encoding='utf-8');check('RELEASED_BATCHES.json' in bootstrap and 'CISSP_BELLRINGERS' in bootstrap and "import('./app.js')" in bootstrap,'Bootstrap release loading incomplete');check('CISSP_CHUNKS.flatMap' in app and 'D.cards=' in app,'App runtime assembly missing');check('startCalibratedQuiz' in enh and 'startBellringer' in enh and 'data-conf' in enh and 'distractor_rationales' in enh and 'addSubtopicSearch' in enh,'Enhanced practice workflow incomplete');check((QB/'quality_gate.py').exists() and (QB/'QUESTION_BANK_EXPANSION_PLAN.md').exists(),'Question-bank quality system incomplete')
if errors:
    print('FAIL');[print('-',e) for e in errors];sys.exit(1)
print('PASS')
print(f"release=1.3.0 status=READY_FOR_STUDY domains=8 objectives=62 subtopic_checks={subtopics} ai_areas={ai_areas} cards={computed_cards} standard_questions={len(all_questions)} bellringers={len(bellringers)} bank_records={len(all_questions)+len(bellringers)} sources={sources} semantic_items={len(sem_items)} weights=100%")

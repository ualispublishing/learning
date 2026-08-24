#!/usr/bin/env python3
import json,sys
from pathlib import Path
ROOT=Path(__file__).parent
meta_raw=(ROOT/'data-meta.js').read_text(encoding='utf-8').strip()
assert meta_raw.startswith('window.CISSP_META=') and ';window.CISSP_CHUNKS=[];' in meta_raw
meta=json.loads(meta_raw[len('window.CISSP_META='):meta_raw.index(';window.CISSP_CHUNKS=[];')])
chunks=[]
for name in [*(f'data-d{i}.js' for i in range(1,9)),'data-ai.js','data-precision.js']:
    raw=(ROOT/name).read_text(encoding='utf-8').strip(); pre='window.CISSP_CHUNKS.push('; suf=');'
    assert raw.startswith(pre) and raw.endswith(suf), f'{name} wrapper invalid'; chunks.append(json.loads(raw[len(pre):-len(suf)]))
data={**meta,'objectives':sum((c['objectives'] for c in chunks),[]),'high':sum((c['high'] for c in chunks),[]),'questions':sum((c['questions'] for c in chunks),[])}
cover_raw=(ROOT/'coverage-detail.js').read_text(encoding='utf-8').strip(); marker=';\nwindow.CISSP_AI_COVERAGE='
assert cover_raw.startswith('window.CISSP_COVERAGE=') and marker in cover_raw and cover_raw.endswith(';'), 'coverage-detail.js wrapper invalid'
coverage=json.loads(cover_raw[len('window.CISSP_COVERAGE='):cover_raw.index(marker)])
ai=json.loads(cover_raw[cover_raw.index(marker)+len(marker):-1])
release=json.loads((ROOT/'RELEASE_STATUS.json').read_text(encoding='utf-8'))
errors=[]
def check(cond,msg):
    if not cond: errors.append(msg)
expected_counts={1:12,2:6,3:10,4:3,5:6,6:5,7:15,8:5}; expected_weights={1:16,2:10,3:13,4:13,5:13,6:12,7:13,8:10}
check(len(data['domains'])==8,'Expected 8 domains')
check(sum(d['weight'] for d in data['domains'])==100,'Weights != 100')
check({d['num']:d['weight'] for d in data['domains']}==expected_weights,'Weights differ from current official outline')
for d,n in expected_counts.items(): check(sum(o['domain_num']==d for o in data['objectives'])==n,f'D{d} objective count wrong')
ids=[o['id'] for o in data['objectives']]
check(len(ids)==62 and len(ids)==len(set(ids)),'Objective IDs incomplete/duplicate')
for d,n in expected_counts.items(): check(all(f'{d}.{i}' in ids for i in range(1,n+1)),f'D{d} missing ID')
check(set(coverage)==set(ids),'Subtopic coverage keys do not exactly match 62 objectives')
check(all(isinstance(v,list) and v and all(isinstance(x,str) and x.strip() for x in v) for v in coverage.values()),'Subtopic coverage contains empty/invalid entries')
check(set(ai)==set(str(i) for i in range(1,9)),'AI coverage must include all eight domains')
check(all(isinstance(v,list) and v for v in ai.values()),'AI coverage contains empty domain entries')
for o in data['objectives']:
    check(bool(o.get('direct','').strip()) and bool(o.get('trap','').strip()),f"Objective {o['id']} missing content")
    check(all(s in data['sources'] for s in o.get('source_ids',[])),f"Objective {o['id']} source invalid")
for h in data['high']:
    check(h['objective'] in ids,f"High card {h['id']} objective invalid")
    check(bool(h.get('front','').strip()) and bool(h.get('direct','').strip()) and bool(h.get('trap','').strip()),f"High card {h['id']} missing content")
    check(all(s in data['sources'] for s in h['source_ids']),f"High card {h['id']} source invalid")
for q in data['questions']:
    check(q['objective'] in ids,f"Question {q['id']} objective invalid")
    check(len(q['options'])==4 and isinstance(q['answer'],int) and 0<=q['answer']<4,f"Question {q['id']} answer/options invalid")
    check(bool(q.get('stem','').strip()) and bool(q.get('explanation','').strip()),f"Question {q['id']} content missing")
check(len({h['id'] for h in data['high']})==len(data['high']),'Duplicate high card ID')
check(len({q['id'] for q in data['questions']})==len(data['questions']),'Duplicate question ID')
computed_cards=62+len(data['high']); subtopics=sum(len(v) for v in coverage.values()); ai_areas=sum(len(v) for v in ai.values()); sources=len(data['sources'])
check(computed_cards==140,'Runtime cards != 140')
check(len(data['questions'])==56,'Runtime questions != 56')
check(sources==20,'Source count != 20')
check(subtopics==344,'Subtopic check count != 344')
check(ai_areas==33,'AI coverage area count != 33')
for d in range(1,9):
    check(sum(q['domain_num']==d for q in data['questions'])==7,f'D{d} scenario count != 7')
    check(sum(h['domain_num']==d and h['id'].startswith('PX-') for h in data['high'])==4,f'D{d} precision-card count != 4')
    check(sum(h['domain_num']==d and h['id'].startswith('AI-') for h in data['high'])==1,f'D{d} AI-card count != 1')
check(meta['meta'].get('version')=='1.2.0','Metadata version drift')
check(meta['meta'].get('objective_count')==len(ids),'Metadata objective count drift')
check(meta['meta'].get('subtopic_checks')==subtopics,'Metadata subtopic count drift')
check(meta['meta'].get('ai_coverage_areas')==ai_areas,'Metadata AI coverage count drift')
check(meta['meta'].get('card_count')==computed_cards,'Metadata card count drift')
check(meta['meta'].get('question_count')==len(data['questions']),'Metadata question count drift')
check(meta['meta'].get('source_count')==sources,'Metadata source count drift')
check(meta['meta'].get('domain_weight_total')==sum(d['weight'] for d in data['domains']),'Metadata weight total drift')
rs=release.get('scope',{})
check(release.get('project_id')=='CISSP-ATLAS' and release.get('release')=='1.2.0' and release.get('status')=='READY_FOR_STUDY','Release status identity/version/state drift')
check(rs.get('domains')==8 and rs.get('numbered_objectives')==62 and rs.get('subtopic_checks')==subtopics and rs.get('ai_coverage_areas')==ai_areas and rs.get('layered_cards')==computed_cards and rs.get('original_scenario_questions')==len(data['questions']) and rs.get('sources')==sources and rs.get('official_weight_total_percent')==100,'Release scope drift')
check((ROOT/'TOMORROW_START.md').exists() and 'Run the 16-question diagnostic once' in (ROOT/'TOMORROW_START.md').read_text(encoding='utf-8'),'Tomorrow-start guide missing or incomplete')
html=(ROOT/'index.html').read_text(encoding='utf-8')
required=['data-meta.js']+[f'data-d{i}.js' for i in range(1,9)]+['data-ai.js','data-precision.js','coverage-detail.js','app.js','enhancements.js','styles.css','mobile-fix.css','enhancements.css','id="today"','id="learn"','id="practice"','id="blueprint"','id="progress"','id="sources"','<option>56</option>','Mixed domains','RELEASE v1.2']
check(all(x in html for x in required),'HTML shell/assets/release labels incomplete')
check('Weighted mixed domains' not in html,'Practice label falsely claims weighted sampling')
app=(ROOT/'app.js').read_text(encoding='utf-8'); enh=(ROOT/'enhancements.js').read_text(encoding='utf-8')
check('CISSP_CHUNKS.flatMap' in app and 'D.cards=' in app and 'layersFor' in app,'Runtime assembly missing')
check('diagnosticSet' in enh and 'decorateBlueprint' in enh and 'cissp_atlas_diagnostic_v1' in enh and 'addSubtopicSearch' in enh,'Enhancement workflow incomplete')
if errors:
    print('FAIL'); [print('-',e) for e in errors]; sys.exit(1)
print('PASS')
print(f"release=1.2.0 status=READY_FOR_STUDY domains=8 objectives={len(ids)} subtopic_checks={subtopics} ai_areas={ai_areas} cards={computed_cards} questions={len(data['questions'])} sources={sources} weights=100%")

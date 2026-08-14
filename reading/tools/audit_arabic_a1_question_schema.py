#!/usr/bin/env python3
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'reading/arabic/a1/passages.jsonl'
SCHEMA=ROOT/'reading/schema/passage.schema.json'
OUT=ROOT/'reading/audit/arabic_a1_question_schema.json'

rows=[json.loads(x) for x in SRC.read_text(encoding='utf-8').splitlines() if x.strip()]
schema=json.loads(SCHEMA.read_text(encoding='utf-8'))
Draft202012Validator.check_schema(schema)
validator=Draft202012Validator(schema)

all_target_ids=set()
for r in rows:
    all_target_ids.update(x['id'] for x in r.get('new_lexical_targets',[]))
    all_target_ids.update(x['id'] for x in r.get('review_lexical_targets',[]))


def schema_problem(error):
    path='.'.join(str(x) for x in error.absolute_path) or '<record>'
    return f'json_schema:{path}:{error.message}'


results=[]; problems=[]
for r in rows:
    pid=r.get('id','<missing-id>'); qs=r.get('questions',[]); ans=r.get('answer_key',[])
    local=[]

    schema_errors=sorted(validator.iter_errors(r),key=lambda e:(list(e.absolute_path),e.message))
    local.extend(schema_problem(e) for e in schema_errors)

    qids=[q.get('id') for q in qs]; aids=[a.get('id') for a in ans]
    if len(qs)!=10: local.append(f'question_count={len(qs)}')
    if len(ans)!=10: local.append(f'answer_count={len(ans)}')
    if len(set(qids))!=len(qids): local.append('duplicate_question_ids')
    if len(set(aids))!=len(aids): local.append('duplicate_answer_ids')
    if set(qids)!={f'q{i}' for i in range(1,11)}: local.append('question_id_set_not_q1_q10')
    if set(aids)!={f'a{i}' for i in range(1,11)}: local.append('answer_id_set_not_a1_a10')
    amap={a.get('id'):a for a in ans}
    for i,q in enumerate(qs,1):
        expected=f'a{i}'
        if q.get('answer_id')!=expected: local.append(f'{q.get("id")}:answer_id_not_{expected}')
        a=amap.get(expected)
        if not a or a.get('question_id')!=q.get('id'): local.append(f'{q.get("id")}:broken_reverse_answer_link')
        if not str(q.get('prompt','')).strip(): local.append(f'{q.get("id")}:empty_prompt')
        if a and not str(a.get('answer','')).strip(): local.append(f'{q.get("id")}:empty_answer')
        for tid in q.get('target_ids',[]):
            if tid not in all_target_ids: local.append(f'{q.get("id")}:unknown_target_id:{tid}')
        if q.get('options'):
            answer=str(a.get('answer','')).rstrip('.').strip() if a else ''
            opts={str(x).rstrip('.').strip() for x in q['options']}
            if answer not in opts: local.append(f'{q.get("id")}:answer_not_in_options')
    if r.get('sequence')==6 and r.get('new_lexical_targets'): local.append('p6_has_new_lexical_targets')
    if local: problems.extend(f'{pid}:{x}' for x in local)
    results.append({
        'id':pid,
        'questions':len(qs),
        'answers':len(ans),
        'json_schema_errors':len(schema_errors),
        'gate':'PASS' if not local else 'FAIL',
        'problems':local,
    })

summary={
    'passage_count':len(rows),
    'expected_passages':6,
    'expected_questions_per_passage':10,
    'expected_total_questions':60,
    'actual_total_questions':sum(len(r.get('questions',[])) for r in rows),
    'actual_total_answers':sum(len(r.get('answer_key',[])) for r in rows),
    'canonical_schema':'reading/schema/passage.schema.json',
    'json_schema_valid_passages':sum(x['json_schema_errors']==0 for x in results),
    'passages_passing':sum(x['gate']=='PASS' for x in results),
    'problems':problems,
    'gate':'PASS' if len(rows)==6 and not problems else 'FAIL',
    'passages':results,
}
OUT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
if summary['gate']!='PASS': raise SystemExit('Arabic A1 question/schema audit failed')

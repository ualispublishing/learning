#!/usr/bin/env python3
"""Apply fresh Arabic Gate C A1 Unit 4 comprehension/grounding repairs."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
PATH=READING/'arabic/a1/passages.jsonl'
DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/a1_u04.json'
EXPECTED_GIT_BLOB='fd436f46d67d36c3104fd0786da23e564e9ee51c'
EXPECTED_MANIFEST='b60f347bdc773321f9496647275c8d8127371d612735377f317cb83039edef5e'
P01_OLD='أكمل: هذا والدي؛ هو _____ي.'
P01_NEW='اختر من «أب» و«ابن»: هذا والدي؛ هو _____ي.'
P05_OLD='أكمل: يقف الطالب _____ المعلم.'
P05_NEW='إذا كان المعلم خلف الطالب، أكمل: يقف الطالب _____ المعلم.'
NOTE='2026-09-05 fresh Gate C comprehension/answer-grounding review (A1 Unit 4): 60 question-answer pairs reviewed; two ambiguous transfer prompts repaired; no educator/publication release claim.'

def blob(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def main():
    if DECISION.exists():
        raise SystemExit('duplicate Gate C A1 Unit 4 frontier')
    m=json.loads((READING/'STATE_MANIFEST.json').read_text(encoding='utf-8'))
    if m.get('aggregate_sha256')!=EXPECTED_MANIFEST:
        raise SystemExit('state manifest drift')
    r=json.loads((READING/'RELEASE_STATUS.json').read_text(encoding='utf-8'))['languages']['arabic']
    c=r.get('comprehension_review_progress',{})
    if r.get('release_state')!='REOPEN_REQUIRED' or r.get('educator_release_ready') is not False:
        raise SystemExit('release boundary drift')
    if (c.get('fresh_records_reviewed'),c.get('fresh_qa_pairs_reviewed'),c.get('fresh_records_with_findings'),c.get('fresh_findings'))!=(18,180,3,3):
        raise SystemExit('Gate C frontier drift')
    if r['latest_deterministic_gate']['open_findings']!=1080:
        raise SystemExit('deterministic frontier drift')
    raw=PATH.read_bytes()
    if blob(raw)!=EXPECTED_GIT_BLOB:
        raise SystemExit('A1 canonical blob drift')
    rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
    ids=[f'ar-a1-u04-p{i:02d}' for i in range(1,7)]
    if [rows[i].get('id') for i in range(18,24)]!=ids:
        raise SystemExit('Unit 4 id/order drift')
    before={x['id']:json.loads(json.dumps(x,ensure_ascii=False)) for x in rows[18:24]}

    p01=rows[18]; q01={q['id']:q for q in p01['questions']}; a01={a['question_id']:a for a in p01['answer_key']}
    if q01['q10'].get('prompt')!=P01_OLD or q01['q10'].get('target_ids')!=['ar-r122'] or a01['q10'].get('answer')!='أب':
        raise SystemExit('p01/q10 frontier drift')
    q01['q10']['prompt']=P01_NEW
    p01['revision']=int(p01.get('revision',0))+1
    n=p01['quality'].setdefault('notes',[])
    if NOTE not in n: n.append(NOTE)

    p05=rows[22]; q05={q['id']:q for q in p05['questions']}; a05={a['question_id']:a for a in p05['answer_key']}
    if q05['q9'].get('prompt')!=P05_OLD or q05['q9'].get('target_ids')!=['ar-r131'] or a05['q9'].get('answer')!='أمام':
        raise SystemExit('p05/q9 frontier drift')
    q05['q9']['prompt']=P05_NEW
    p05['revision']=int(p05.get('revision',0))+1
    n=p05['quality'].setdefault('notes',[])
    if NOTE not in n: n.append(NOTE)

    repaired={'ar-a1-u04-p01','ar-a1-u04-p05'}
    for i,pid in enumerate(ids,start=18):
        old=before[pid]; new=rows[i]
        if len(new['questions'])!=10 or len(new['answer_key'])!=10:
            raise SystemExit(f'{pid}: 10Q/10A drift')
        if {q['answer_id'] for q in new['questions']}!={a['id'] for a in new['answer_key']}:
            raise SystemExit(f'{pid}: linkage drift')
        if new['text']!=old['text'] or new['answer_key']!=old['answer_key']:
            raise SystemExit(f'{pid}: text/answer changed')
        if new.get('new_lexical_targets')!=old.get('new_lexical_targets') or new.get('review_lexical_targets')!=old.get('review_lexical_targets'):
            raise SystemExit(f'{pid}: lexical drift')
        for k in ('status','coverage_check','linguistic_review','pedagogical_review','answer_key_check','schema_check'):
            if new['quality'].get(k)!=old['quality'].get(k):
                raise SystemExit(f'{pid}: quality {k} changed')
        if pid not in repaired and new!=old:
            raise SystemExit(f'{pid}: clean PASS record changed')
    PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in rows)+'\n',encoding='utf-8')
    print(json.dumps({'gate':'C','level':'A1','unit':4,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':2,'fresh_findings':2,'repairs':['ar-a1-u04-p01/question q10','ar-a1-u04-p05/question q9'],'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()

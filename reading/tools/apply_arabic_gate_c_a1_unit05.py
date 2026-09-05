#!/usr/bin/env python3
"""Apply fresh Arabic Gate C A1 Unit 5 comprehension/grounding repairs."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
PATH=READING/'arabic/a1/passages.jsonl'
DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/a1_u05.json'
EXPECTED_GIT_BLOB='82e5ee9e56b6c57c6150667d79035c2bb3464c2b'
EXPECTED_MANIFEST='b53a41acc586c2f11ee12d645b38d18e063551e763c7465070a1adf4c978280a'
NOTE='2026-09-05 fresh Gate C comprehension/answer-grounding review (A1 Unit 5): 60 question-answer pairs reviewed; ten underconstrained transfer prompts repaired across five records; no educator/publication release claim.'
REPAIRS={
 ('ar-a1-u05-p01','q9'):('أكمل: _____ الدرس في الثامنة.','اختر من «بدأ» و«يبدأ» ثم أكمل عن أمس: _____ الدرس في الثامنة.',['ar-r177'],'بدأ'),
 ('ar-a1-u05-p01','q10'):('أكمل: المعلم _____ إلى الصف الآن.','اختر من «يأتي» و«يعود»: المعلم في غرفة المعلمين، ثم _____ إلى الصف للمرة الأولى هذا الصباح.',['ar-r181'],'يأتي'),
 ('ar-a1-u05-p02','q9'):('أكمل: _____ كتاب على الطاولة.','أكمل بالفعل الذي يعني وجود شيء في المكان: _____ كتاب على الطاولة.',['ar-r184'],'يوجد'),
 ('ar-a1-u05-p02','q10'):('أكمل: _____ المدرسة يتحدث مع المعلمين.','أكمل بكلمة الشخص المسؤول عن المدرسة: _____ المدرسة يتحدث مع المعلمين.',['ar-r169'],'مدير'),
 ('ar-a1-u05-p03','q9'):('أكمل: دوري أن أكتب، و_____ أخي أن يقرأ.','اختر من «دور» و«داخل»: دوري أن أكتب، و_____ أخي أن يقرأ.',['ar-r176'],'دور'),
 ('ar-a1-u05-p03','q10'):('أكمل: الطلاب _____ الصف الآن.','اختر من «داخل» و«خارج»: الطلاب _____ الصف الآن، وليسوا في الساحة.',['ar-r188'],'داخل'),
 ('ar-a1-u05-p04','q9'):('أكمل: الطالب _____ عن كتابه أمام الصف.','أكمل بالفعل الذي يعني أنه يتكلم: الطالب _____ عن كتابه أمام الصف.',['ar-r196'],'يتحدث'),
 ('ar-a1-u05-p04','q10'):('أكمل: أبي _____ في مكتب قريب.','أكمل بالفعل الذي يعني أنه يقوم بعمله هناك: أبي _____ في مكتب قريب.',['ar-r128'],'يعمل'),
 ('ar-a1-u05-p05','q9'):('أكمل: في الشهر _____ سأزور صديقي.','اختر من «المقبل» و«الماضي»: في الشهر _____ سأزور صديقي.',['ar-r197'],'المقبل'),
 ('ar-a1-u05-p05','q10'):('أكمل: بعد المدرسة _____ الطالب إلى المنزل.','اختر من «يأتي» و«يعود»: بعد المدرسة _____ الطالب إلى منزله من جديد.',['ar-r201'],'يعود'),
}

def blob(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def main():
    if DECISION.exists(): raise SystemExit('duplicate Gate C A1 Unit 5 frontier')
    m=json.loads((READING/'STATE_MANIFEST.json').read_text(encoding='utf-8'))
    if m.get('aggregate_sha256')!=EXPECTED_MANIFEST: raise SystemExit('state manifest drift')
    r=json.loads((READING/'RELEASE_STATUS.json').read_text(encoding='utf-8'))['languages']['arabic']
    c=r.get('comprehension_review_progress',{})
    if r.get('release_state')!='REOPEN_REQUIRED' or r.get('educator_release_ready') is not False: raise SystemExit('release boundary drift')
    if (c.get('fresh_records_reviewed'),c.get('fresh_qa_pairs_reviewed'),c.get('fresh_records_with_findings'),c.get('fresh_findings'))!=(24,240,5,5): raise SystemExit('Gate C frontier drift')
    if r['latest_deterministic_gate']['open_findings']!=1080: raise SystemExit('deterministic frontier drift')
    raw=PATH.read_bytes()
    if blob(raw)!=EXPECTED_GIT_BLOB: raise SystemExit('A1 canonical blob drift')
    rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
    ids=[f'ar-a1-u05-p{i:02d}' for i in range(1,7)]
    if [rows[i].get('id') for i in range(24,30)]!=ids: raise SystemExit('Unit 5 id/order drift')
    before={x['id']:json.loads(json.dumps(x,ensure_ascii=False)) for x in rows[24:30]}
    by={r['id']:r for r in rows[24:30]}
    for (pid,qid),(old,new,target,answer) in REPAIRS.items():
        rec=by[pid]; qs={q['id']:q for q in rec['questions']}; ans={a['question_id']:a for a in rec['answer_key']}
        if qs[qid].get('prompt')!=old or qs[qid].get('target_ids')!=target or ans[qid].get('answer')!=answer:
            raise SystemExit(f'{pid}/{qid} frontier drift')
        qs[qid]['prompt']=new
    repaired={pid for pid,_ in REPAIRS}
    for pid in repaired:
        rec=by[pid]; rec['revision']=int(rec.get('revision',0))+1; notes=rec['quality'].setdefault('notes',[])
        if NOTE not in notes: notes.append(NOTE)
    for i,pid in enumerate(ids,start=24):
        old=before[pid]; new=rows[i]
        if len(new['questions'])!=10 or len(new['answer_key'])!=10: raise SystemExit(f'{pid}: 10Q/10A drift')
        if {q['answer_id'] for q in new['questions']}!={a['id'] for a in new['answer_key']}: raise SystemExit(f'{pid}: linkage drift')
        if new['text']!=old['text'] or new['answer_key']!=old['answer_key']: raise SystemExit(f'{pid}: text/answer changed')
        if new.get('new_lexical_targets')!=old.get('new_lexical_targets') or new.get('review_lexical_targets')!=old.get('review_lexical_targets'): raise SystemExit(f'{pid}: lexical drift')
        for k in ('status','coverage_check','linguistic_review','pedagogical_review','answer_key_check','schema_check'):
            if new['quality'].get(k)!=old['quality'].get(k): raise SystemExit(f'{pid}: quality {k} changed')
        if pid not in repaired and new!=old: raise SystemExit(f'{pid}: clean PASS record changed')
    PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in rows)+'\n',encoding='utf-8')
    print(json.dumps({'gate':'C','level':'A1','unit':5,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':5,'fresh_findings':10,'repair_fields':[f'{p}/{q}' for p,q in REPAIRS],'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()

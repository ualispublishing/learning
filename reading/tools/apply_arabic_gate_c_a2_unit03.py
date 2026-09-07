#!/usr/bin/env python3
"""Apply fresh Arabic Gate C A2 Unit 3 comprehension/grounding repairs."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
PATH=READING/'arabic/a2/passages.jsonl'
DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u03.json'
EXPECTED_GIT_BLOB='1a282c06b2aa7aac54b39418aa6946489d3a0307'
EXPECTED_MANIFEST='e7ac517cde7b069b8e7eafb8744c39a57daea0c0295e34db7e63d329242fdc0d'
NOTE='2026-09-06 fresh Gate C comprehension/answer-grounding review (A2 Unit 3): 60 question-answer pairs reviewed; ten underconstrained transfer prompts repaired across five records; no educator/publication release claim.'
REPAIRS={
 ('ar-a2-u03-p01','q9'):('أكمل: زرت هذا المكان _____، أي قبل أيام قليلة.','اختر من «مؤخرًا» و«مجددًا»: زرت هذا المكان _____، أي قبل أيام قليلة.',['ar-r865'],'مؤخرًا'),
 ('ar-a2-u03-p01','q10'):('أكمل: لم أفهم الجملة، فقرأتها _____.','اختر من «مجددا» و«مؤخرا»: لم أفهم الجملة، فقرأتها _____.',['ar-r868'],'مجددا'),
 ('ar-a2-u03-p02','q9'):('أكمل: استمعت إلى _____ للمحاضرة بعد العودة إلى البيت.','اختر من «تسجيل» و«نظرة»: استمعت إلى _____ للمحاضرة بعد العودة إلى البيت.',['ar-r872'],'تسجيل'),
 ('ar-a2-u03-p02','q10'):('أكمل: ألقيت _____ على الخريطة قبل الخروج.','اختر من «نظرة» و«تسجيل»: ألقيت _____ على الخريطة قبل الخروج.',['ar-r867'],'نظرة'),
 ('ar-a2-u03-p03','q9'):('أكمل: حضرنا _____ تخرج أخي العام الماضي.','اختر من «حفل» و«زمن»: حضرنا _____ تخرج أخي العام الماضي.',['ar-r761'],'حفل'),
 ('ar-a2-u03-p03','q10'):('أكمل: تغير الحي كثيرًا مع مرور _____.','اختر من «الزمن» و«الحفل»: تغير الحي كثيرًا مع مرور _____.',['ar-r765'],'الزمن'),
 ('ar-a2-u03-p04','q9'):('أكمل: حضر _____ الطلاب إلى النشاط، لكن بعضهم غاب.','اختر من «معظم» و«جميع»: حضر _____ الطلاب إلى النشاط، لكن بعضهم غاب.',['ar-r723'],'معظم'),
 ('ar-a2-u03-p04','q10'):('أكمل: _____ أن المتجر مفتوح، لكنه كان مغلقًا.','اختر من «ظننت» و«علمت»: _____ أن المتجر مفتوح، لكنه كان مغلقًا.',['ar-r885'],'ظننت'),
 ('ar-a2-u03-p05','q9'):('أكمل: تركت الرحلة _____ جميلًا في ذاكرتي.','اختر من «أثرًا» و«فوزًا»: تركت الرحلة _____ جميلًا في ذاكرتي.',['ar-r899'],'أثرًا'),
 ('ar-a2-u03-p05','q10'):('أكمل: _____ فريقنا في المباراة الأخيرة.','اختر من «فاز» و«خسر»: _____ فريقنا في المباراة الأخيرة.',['ar-r897'],'فاز'),
}

def blob(data:bytes)->str:return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def main():
    if DECISION.exists(): raise SystemExit('duplicate Gate C A2 Unit 3 frontier')
    m=json.loads((READING/'STATE_MANIFEST.json').read_text(encoding='utf-8'))
    if m.get('aggregate_sha256')!=EXPECTED_MANIFEST: raise SystemExit('state manifest drift')
    r=json.loads((READING/'RELEASE_STATUS.json').read_text(encoding='utf-8'))['languages']['arabic']; c=r.get('comprehension_review_progress',{})
    if r.get('release_state')!='REOPEN_REQUIRED' or r.get('educator_release_ready') is not False: raise SystemExit('release boundary drift')
    if (c.get('fresh_records_reviewed'),c.get('fresh_qa_pairs_reviewed'),c.get('fresh_records_with_findings'),c.get('fresh_findings'))!=(72,720,45,83): raise SystemExit('Gate C frontier drift')
    if c.get('levels_completed')!=['A1']: raise SystemExit('Gate C completed-level frontier drift')
    if r['latest_deterministic_gate']['open_findings']!=1080: raise SystemExit('deterministic frontier drift')
    raw=PATH.read_bytes()
    if blob(raw)!=EXPECTED_GIT_BLOB: raise SystemExit('A2 canonical blob drift')
    rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]; ids=[f'ar-a2-u03-p{i:02d}' for i in range(1,7)]
    if [rows[i].get('id') for i in range(12,18)]!=ids: raise SystemExit('A2 Unit 3 id/order drift')
    before={x['id']:json.loads(json.dumps(x,ensure_ascii=False)) for x in rows[12:18]}; by={r['id']:r for r in rows[12:18]}
    for (pid,qid),(old,new,target,answer) in REPAIRS.items():
        rec=by[pid]; qs={q['id']:q for q in rec['questions']}; ans={a['question_id']:a for a in rec['answer_key']}
        if qs[qid].get('prompt')!=old or qs[qid].get('target_ids')!=target or ans[qid].get('answer')!=answer: raise SystemExit(f'{pid}/{qid} frontier drift')
        qs[qid]['prompt']=new
    repaired={pid for pid,_ in REPAIRS}
    for pid in repaired:
        rec=by[pid]; rec['revision']=int(rec.get('revision',0))+1; notes=rec['quality'].setdefault('notes',[])
        if NOTE not in notes: notes.append(NOTE)
    for i,pid in enumerate(ids,start=12):
        old=before[pid]; new=rows[i]
        if len(new['questions'])!=10 or len(new['answer_key'])!=10: raise SystemExit(f'{pid}: 10Q/10A drift')
        if {q['answer_id'] for q in new['questions']}!={a['id'] for a in new['answer_key']}: raise SystemExit(f'{pid}: linkage drift')
        if new['text']!=old['text'] or new['answer_key']!=old['answer_key']: raise SystemExit(f'{pid}: text/answer changed')
        if new.get('new_lexical_targets')!=old.get('new_lexical_targets') or new.get('review_lexical_targets')!=old.get('review_lexical_targets'): raise SystemExit(f'{pid}: lexical drift')
        for k in ('status','coverage_check','linguistic_review','pedagogical_review','answer_key_check','schema_check'):
            if new['quality'].get(k)!=old['quality'].get(k): raise SystemExit(f'{pid}: quality {k} changed')
        if pid not in repaired and new!=old: raise SystemExit(f'{pid}: clean PASS record changed')
    PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in rows)+'\n',encoding='utf-8')
    print(json.dumps({'gate':'C','level':'A2','unit':3,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':5,'fresh_findings':10,'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()

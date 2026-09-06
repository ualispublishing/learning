#!/usr/bin/env python3
"""Apply fresh Arabic Gate C A1 Unit 10 comprehension/grounding repairs."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
PATH=READING/'arabic/a1/passages.jsonl'
DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/a1_u10.json'
EXPECTED_GIT_BLOB='4dadc2e910b21ed324943d4e79ffe1506bffe990'
EXPECTED_MANIFEST='6d6c4fb486520cc9aa244a1b5e43c30c88be341aca7178bc8bae53bf16110dd1'
NOTE='2026-09-05 fresh Gate C comprehension/answer-grounding review (A1 Unit 10): 60 question-answer pairs reviewed; ten underconstrained transfer prompts repaired across five records; no educator/publication release claim.'
REPAIRS={
 ('ar-a1-u10-p01','q9'):('أكمل: أنا _____ أضع كتابي في الحقيبة قبل المدرسة.','اختر من «دائمًا» و«أحيانًا»: أنا _____ أضع كتابي في الحقيبة قبل المدرسة.',['ar-r235'],'دائمًا'),
 ('ar-a1-u10-p01','q10'):('أكمل: بقي _____ من الماء في الكأس.','اختر من «قليل» و«كثير»: بقي _____ من الماء في الكأس.',['ar-r266'],'قليل'),
 ('ar-a1-u10-p02','q9'):('أكمل: هذه _____ سهلة لحفظ الكلمات.','اختر من «طريقة» و«نهاية»: هذه _____ سهلة لحفظ الكلمات.',['ar-r237'],'طريقة'),
 ('ar-a1-u10-p02','q10'):('أكمل: اليوم أخذت طريقًا _____ إلى المدرسة.','اختر من «مختلفًا» و«قليلًا»: اليوم أخذت طريقًا _____ إلى المدرسة.',['ar-r249'],'مختلفًا'),
 ('ar-a1-u10-p03','q9'):('أكمل: تعمل _____ من الطلاب على المشروع.','اختر من «مجموعة» و«نهاية»: تعمل _____ من الطلاب على المشروع.',['ar-r246'],'مجموعة'),
 ('ar-a1-u10-p03','q10'):('أكمل: في _____ الدرس نراجع الكلمات.','اختر من «نهاية» و«مجموعة»: في _____ الدرس نراجع الكلمات.',['ar-r245'],'نهاية'),
 ('ar-a1-u10-p04','q9'):('أكمل: انتظر _____ واحدة.','إذا كان المقصود وقتًا قصيرًا جدًا، اختر من «لحظة» و«صورة»: انتظر _____ واحدة.',['ar-r461'],'لحظة'),
 ('ar-a1-u10-p04','q10'):('أكمل: التقطنا _____ أمام المدرسة.','اختر من «صورة» و«صفحة»: التقطنا _____ أمام المدرسة.',['ar-r357'],'صورة'),
 ('ar-a1-u10-p05','q9'):('أكمل: اقرأ _____ الأولى من الكتاب.','اختر من «الصفحة» و«النادي»: اقرأ _____ الأولى من الكتاب.',['ar-r262'],'الصفحة'),
 ('ar-a1-u10-p05','q10'):('أكمل: عندي _____ عن النص.','إذا كنت أريد جوابًا، اختر من «سؤال» و«نهاية»: عندي _____ عن النص.',['ar-r499'],'سؤال'),
}

def blob(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def main():
    if DECISION.exists(): raise SystemExit('duplicate Gate C A1 Unit 10 frontier')
    m=json.loads((READING/'STATE_MANIFEST.json').read_text(encoding='utf-8'))
    if m.get('aggregate_sha256')!=EXPECTED_MANIFEST: raise SystemExit('state manifest drift')
    r=json.loads((READING/'RELEASE_STATUS.json').read_text(encoding='utf-8'))['languages']['arabic']; c=r.get('comprehension_review_progress',{})
    if r.get('release_state')!='REOPEN_REQUIRED' or r.get('educator_release_ready') is not False: raise SystemExit('release boundary drift')
    if (c.get('fresh_records_reviewed'),c.get('fresh_qa_pairs_reviewed'),c.get('fresh_records_with_findings'),c.get('fresh_findings'))!=(54,540,30,53): raise SystemExit('Gate C frontier drift')
    if c.get('levels_completed')!=[]: raise SystemExit('unexpected pre-A1-completion state')
    if r['latest_deterministic_gate']['open_findings']!=1080: raise SystemExit('deterministic frontier drift')
    raw=PATH.read_bytes()
    if blob(raw)!=EXPECTED_GIT_BLOB: raise SystemExit('A1 canonical blob drift')
    rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]; ids=[f'ar-a1-u10-p{i:02d}' for i in range(1,7)]
    if [rows[i].get('id') for i in range(54,60)]!=ids: raise SystemExit('Unit 10 id/order drift')
    before={x['id']:json.loads(json.dumps(x,ensure_ascii=False)) for x in rows[54:60]}; by={r['id']:r for r in rows[54:60]}
    for (pid,qid),(old,new,target,answer) in REPAIRS.items():
        rec=by[pid]; qs={q['id']:q for q in rec['questions']}; ans={a['question_id']:a for a in rec['answer_key']}
        if qs[qid].get('prompt')!=old or qs[qid].get('target_ids')!=target or ans[qid].get('answer')!=answer: raise SystemExit(f'{pid}/{qid} frontier drift')
        qs[qid]['prompt']=new
    repaired={pid for pid,_ in REPAIRS}
    for pid in repaired:
        rec=by[pid]; rec['revision']=int(rec.get('revision',0))+1; notes=rec['quality'].setdefault('notes',[])
        if NOTE not in notes: notes.append(NOTE)
    for i,pid in enumerate(ids,start=54):
        old=before[pid]; new=rows[i]
        if len(new['questions'])!=10 or len(new['answer_key'])!=10: raise SystemExit(f'{pid}: 10Q/10A drift')
        if {q['answer_id'] for q in new['questions']}!={a['id'] for a in new['answer_key']}: raise SystemExit(f'{pid}: linkage drift')
        if new['text']!=old['text'] or new['answer_key']!=old['answer_key']: raise SystemExit(f'{pid}: text/answer changed')
        if new.get('new_lexical_targets')!=old.get('new_lexical_targets') or new.get('review_lexical_targets')!=old.get('review_lexical_targets'): raise SystemExit(f'{pid}: lexical drift')
        for k in ('status','coverage_check','linguistic_review','pedagogical_review','answer_key_check','schema_check'):
            if new['quality'].get(k)!=old['quality'].get(k): raise SystemExit(f'{pid}: quality {k} changed')
        if pid not in repaired and new!=old: raise SystemExit(f'{pid}: clean PASS record changed')
    PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in rows)+'\n',encoding='utf-8')
    print(json.dumps({'gate':'C','level':'A1','unit':10,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':5,'fresh_findings':10,'repair_fields':[f'{p}/{q}' for p,q in REPAIRS],'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()

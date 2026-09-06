#!/usr/bin/env python3
"""Apply fresh Arabic Gate C A2 Unit 2 comprehension/grounding repairs."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
PATH=READING/'arabic/a2/passages.jsonl'
DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u02.json'
EXPECTED_GIT_BLOB='5c1c815934d86fcce1fbc9b76728549bba61be0c'
EXPECTED_MANIFEST='40d1f1524516481b1364b99489fe7afe633ea364f33b97eb6e126eb928b36e21'
NOTE='2026-09-06 fresh Gate C comprehension/answer-grounding review (A2 Unit 2): 60 question-answer pairs reviewed; ten underconstrained transfer prompts repaired across five records; no educator/publication release claim.'
REPAIRS={
 ('ar-a2-u02-p01','q9'):('أكمل: عندي _____ مع طبيب الأسنان في العاشرة.','اختر من «موعد» و«رد»: عندي _____ مع طبيب الأسنان في العاشرة.',['ar-r691'],'موعد'),
 ('ar-a2-u02-p01','q10'):('أكمل: أرسلت رسالة إلى صديقي وانتظرت _____.','اختر من «رده» و«موعده»: أرسلت رسالة إلى صديقي وانتظرت _____.',['ar-r663'],'رده'),
 ('ar-a2-u02-p02','q9'):('أكمل: لست _____ من رقم القاعة؛ سأتحقق منه.','اختر من «متأكدًا» و«بعيدًا»: لست _____ من رقم القاعة؛ سأتحقق منه.',['ar-r648'],'متأكدًا'),
 ('ar-a2-u02-p02','q10'):('أكمل: انتهى هذا الدرس، والدرس _____ يبدأ بعد عشر دقائق.','اختر من «التالي» و«السابق»: انتهى هذا الدرس، والدرس _____ يبدأ بعد عشر دقائق.',['ar-r623'],'التالي'),
 ('ar-a2-u02-p03','q9'):('أكمل: عندما تغير الموعد _____ بصديقي لأخبره.','اختر من «اتصلت» و«انتظرت»: عندما تغير الموعد _____ بصديقي لأخبره.',['ar-r674'],'اتصلت'),
 ('ar-a2-u02-p03','q10'):('أكمل: لا أستطيع الآن؛ سأتحدث معك في وقت _____.','اختر من «لاحق» و«سابق»: لا أستطيع الآن؛ سأتحدث معك في وقت _____.',['ar-r673'],'لاحق'),
 ('ar-a2-u02-p04','q9'):('أكمل: عندي أكثر من _____ للوصول إلى الجامعة.','اختر من «اختيار» و«موعد»: عندي أكثر من _____ للوصول إلى الجامعة.',['ar-r682'],'اختيار'),
 ('ar-a2-u02-p04','q10'):('أكمل: عنواني _____ مختلف عن عنواني القديم.','اختر من «الحالي» و«التالي»: عنواني _____ مختلف عن عنواني القديم.',['ar-r621'],'الحالي'),
 ('ar-a2-u02-p05','q9'):('أكمل: سجلت في _____ قصيرة لتعلم التصوير.','اختر من «دورة» و«زيارة»: سجلت في _____ قصيرة لتعلم التصوير.',['ar-r661'],'دورة'),
 ('ar-a2-u02-p05','q10'):('أكمل: يحتاج السفر إلى _____ جيد للوقت والحجوزات.','اختر من «تنظيم» و«سعر»: يحتاج السفر إلى _____ جيد للوقت والحجوزات.',['ar-r659'],'تنظيم'),
}

def blob(data:bytes)->str:return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def main():
    if DECISION.exists(): raise SystemExit('duplicate Gate C A2 Unit 2 frontier')
    m=json.loads((READING/'STATE_MANIFEST.json').read_text(encoding='utf-8'))
    if m.get('aggregate_sha256')!=EXPECTED_MANIFEST: raise SystemExit('state manifest drift')
    r=json.loads((READING/'RELEASE_STATUS.json').read_text(encoding='utf-8'))['languages']['arabic']; c=r.get('comprehension_review_progress',{})
    if r.get('release_state')!='REOPEN_REQUIRED' or r.get('educator_release_ready') is not False: raise SystemExit('release boundary drift')
    if (c.get('fresh_records_reviewed'),c.get('fresh_qa_pairs_reviewed'),c.get('fresh_records_with_findings'),c.get('fresh_findings'))!=(66,660,40,73): raise SystemExit('Gate C frontier drift')
    if c.get('levels_completed')!=['A1']: raise SystemExit('Gate C completed-level frontier drift')
    if r['latest_deterministic_gate']['open_findings']!=1080: raise SystemExit('deterministic frontier drift')
    raw=PATH.read_bytes()
    if blob(raw)!=EXPECTED_GIT_BLOB: raise SystemExit('A2 canonical blob drift')
    rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]; ids=[f'ar-a2-u02-p{i:02d}' for i in range(1,7)]
    if [rows[i].get('id') for i in range(6,12)]!=ids: raise SystemExit('A2 Unit 2 id/order drift')
    before={x['id']:json.loads(json.dumps(x,ensure_ascii=False)) for x in rows[6:12]}; by={r['id']:r for r in rows[6:12]}
    for (pid,qid),(old,new,target,answer) in REPAIRS.items():
        rec=by[pid]; qs={q['id']:q for q in rec['questions']}; ans={a['question_id']:a for a in rec['answer_key']}
        if qs[qid].get('prompt')!=old or qs[qid].get('target_ids')!=target or ans[qid].get('answer')!=answer: raise SystemExit(f'{pid}/{qid} frontier drift')
        qs[qid]['prompt']=new
    repaired={pid for pid,_ in REPAIRS}
    for pid in repaired:
        rec=by[pid]; rec['revision']=int(rec.get('revision',0))+1; notes=rec['quality'].setdefault('notes',[])
        if NOTE not in notes: notes.append(NOTE)
    for i,pid in enumerate(ids,start=6):
        old=before[pid]; new=rows[i]
        if len(new['questions'])!=10 or len(new['answer_key'])!=10: raise SystemExit(f'{pid}: 10Q/10A drift')
        if {q['answer_id'] for q in new['questions']}!={a['id'] for a in new['answer_key']}: raise SystemExit(f'{pid}: linkage drift')
        if new['text']!=old['text'] or new['answer_key']!=old['answer_key']: raise SystemExit(f'{pid}: text/answer changed')
        if new.get('new_lexical_targets')!=old.get('new_lexical_targets') or new.get('review_lexical_targets')!=old.get('review_lexical_targets'): raise SystemExit(f'{pid}: lexical drift')
        for k in ('status','coverage_check','linguistic_review','pedagogical_review','answer_key_check','schema_check'):
            if new['quality'].get(k)!=old['quality'].get(k): raise SystemExit(f'{pid}: quality {k} changed')
        if pid not in repaired and new!=old: raise SystemExit(f'{pid}: clean PASS record changed')
    PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in rows)+'\n',encoding='utf-8')
    print(json.dumps({'gate':'C','level':'A2','unit':2,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':5,'fresh_findings':10,'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Apply fresh Arabic Gate C A1 Unit 8 comprehension/grounding repairs."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
PATH=READING/'arabic/a1/passages.jsonl'
DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/a1_u08.json'
EXPECTED_GIT_BLOB='19d0a3f8f235486d396494f0085baf2e561d7d6a'
EXPECTED_MANIFEST='1ff53a65decd2256c7b3411f60796cfdae2e321728bb04becc42aa7449aa1a95'
NOTE='2026-09-05 fresh Gate C comprehension/answer-grounding review (A1 Unit 8): 60 question-answer pairs reviewed; ten underconstrained transfer prompts repaired across five records; no educator/publication release claim.'
REPAIRS={
 ('ar-a1-u08-p01','q9'):('أكمل: سامر _____ بالتعب بعد يوم طويل.','اختر من «يشعر» و«يصل»: سامر _____ بالتعب بعد يوم طويل.',['ar-r216'],'يشعر'),
 ('ar-a1-u08-p01','q10'):('أكمل: لا أجد كتابي؛ عندي _____.','اختر من «مشكلة» و«مساعدة»: لا أجد كتابي؛ عندي _____.',['ar-r211'],'مشكلة'),
 ('ar-a1-u08-p02','q9'):('أكمل: عندي _____ إلى ماء.','اختر من «حاجة» و«مساعدة»: عندي _____ إلى ماء.',['ar-r349'],'حاجة'),
 ('ar-a1-u08-p02','q10'):('أكمل: طلبت _____ من صديقتي.','اختر من «مساعدة» و«حاجة»: طلبت _____ من صديقتي.',['ar-r258'],'مساعدة'),
 ('ar-a1-u08-p03','q9'):('أكمل: أمسك القلم ب_____.','اختر من «يدي» و«رأسي»: أمسك القلم ب_____.',['ar-r397'],'يدي'),
 ('ar-a1-u08-p03','q10'):('أكمل: أضع القبعة على _____.','اختر من «رأسي» و«يدي»: أضع القبعة على _____.',['ar-r319'],'رأسي'),
 ('ar-a1-u08-p04','q9'):('أكمل: أشعر بنبض _____ بعد الجري.','اختر من «قلبي» و«يدي»: أشعر بنبض _____ بعد الجري.',['ar-r446'],'قلبي'),
 ('ar-a1-u08-p04','q10'):('أكمل: سقط الكتاب لكنه بقي _____.','اختر من «سالمًا» و«متعبًا»: سقط الكتاب لكنه بقي _____.',['ar-r479'],'سالمًا'),
 ('ar-a1-u08-p05','q9'):('أكمل: _____ أن أقرأ الصفحة وحدي.','اختر من «سأحاول» و«سأرفض»: _____ أن أقرأ الصفحة وحدي.',['ar-r465'],'سأحاول'),
 ('ar-a1-u08-p05','q10'):('أكمل: بعد النوم عندي _____ أكثر.','اختر من «قوة» و«مشكلة»: بعد النوم عندي _____ أكثر.',['ar-r327'],'قوة'),
}

def blob(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def main():
    if DECISION.exists(): raise SystemExit('duplicate Gate C A1 Unit 8 frontier')
    m=json.loads((READING/'STATE_MANIFEST.json').read_text(encoding='utf-8'))
    if m.get('aggregate_sha256')!=EXPECTED_MANIFEST: raise SystemExit('state manifest drift')
    r=json.loads((READING/'RELEASE_STATUS.json').read_text(encoding='utf-8'))['languages']['arabic']; c=r.get('comprehension_review_progress',{})
    if r.get('release_state')!='REOPEN_REQUIRED' or r.get('educator_release_ready') is not False: raise SystemExit('release boundary drift')
    if (c.get('fresh_records_reviewed'),c.get('fresh_qa_pairs_reviewed'),c.get('fresh_records_with_findings'),c.get('fresh_findings'))!=(42,420,20,33): raise SystemExit('Gate C frontier drift')
    if r['latest_deterministic_gate']['open_findings']!=1080: raise SystemExit('deterministic frontier drift')
    raw=PATH.read_bytes()
    if blob(raw)!=EXPECTED_GIT_BLOB: raise SystemExit('A1 canonical blob drift')
    rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]; ids=[f'ar-a1-u08-p{i:02d}' for i in range(1,7)]
    if [rows[i].get('id') for i in range(42,48)]!=ids: raise SystemExit('Unit 8 id/order drift')
    before={x['id']:json.loads(json.dumps(x,ensure_ascii=False)) for x in rows[42:48]}; by={r['id']:r for r in rows[42:48]}
    for (pid,qid),(old,new,target,answer) in REPAIRS.items():
        rec=by[pid]; qs={q['id']:q for q in rec['questions']}; ans={a['question_id']:a for a in rec['answer_key']}
        if qs[qid].get('prompt')!=old or qs[qid].get('target_ids')!=target or ans[qid].get('answer')!=answer: raise SystemExit(f'{pid}/{qid} frontier drift')
        qs[qid]['prompt']=new
    repaired={pid for pid,_ in REPAIRS}
    for pid in repaired:
        rec=by[pid]; rec['revision']=int(rec.get('revision',0))+1; notes=rec['quality'].setdefault('notes',[])
        if NOTE not in notes: notes.append(NOTE)
    for i,pid in enumerate(ids,start=42):
        old=before[pid]; new=rows[i]
        if len(new['questions'])!=10 or len(new['answer_key'])!=10: raise SystemExit(f'{pid}: 10Q/10A drift')
        if {q['answer_id'] for q in new['questions']}!={a['id'] for a in new['answer_key']}: raise SystemExit(f'{pid}: linkage drift')
        if new['text']!=old['text'] or new['answer_key']!=old['answer_key']: raise SystemExit(f'{pid}: text/answer changed')
        if new.get('new_lexical_targets')!=old.get('new_lexical_targets') or new.get('review_lexical_targets')!=old.get('review_lexical_targets'): raise SystemExit(f'{pid}: lexical drift')
        for k in ('status','coverage_check','linguistic_review','pedagogical_review','answer_key_check','schema_check'):
            if new['quality'].get(k)!=old['quality'].get(k): raise SystemExit(f'{pid}: quality {k} changed')
        if pid not in repaired and new!=old: raise SystemExit(f'{pid}: clean PASS record changed')
    PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in rows)+'\n',encoding='utf-8')
    print(json.dumps({'gate':'C','level':'A1','unit':8,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':5,'fresh_findings':10,'repair_fields':[f'{p}/{q}' for p,q in REPAIRS],'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Apply fresh Arabic Gate C A1 Unit 9 comprehension/grounding repairs."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
PATH=READING/'arabic/a1/passages.jsonl'
DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/a1_u09.json'
EXPECTED_GIT_BLOB='72dd2670304312268fb1c8e3d80b8b08004faef5'
EXPECTED_MANIFEST='f5ec5d17c61a464dbef0e94af72ae99056a6ea99efcc8c04ca3d029f9d73ff5f'
NOTE='2026-09-05 fresh Gate C comprehension/answer-grounding review (A1 Unit 9): 60 question-answer pairs reviewed; ten underconstrained transfer prompts repaired across five records; no educator/publication release claim.'
REPAIRS={
 ('ar-a1-u09-p01','q9'):('أكمل: رميت _____ إلى صديقي.','اختر من «الكرة» و«اللاعب»: رميت _____ إلى صديقي.',['ar-r200'],'الكرة'),
 ('ar-a1-u09-p01','q10'):('أكمل: سامر _____ في الفريق.','اختر من «لاعب» و«كرة»: سامر _____ في الفريق.',['ar-r296'],'لاعب'),
 ('ar-a1-u09-p02','q9'):('أكمل: شاهدنا _____ كرة في المساء.','اختر من «مباراة» و«نادي»: شاهدنا _____ كرة في المساء.',['ar-r180'],'مباراة'),
 ('ar-a1-u09-p02','q10'):('أكمل: أذهب إلى _____ القراءة يوم الخميس.','اختر من «نادي» و«مباراة»: أذهب إلى _____ القراءة يوم الخميس.',['ar-r174'],'نادي'),
 ('ar-a1-u09-p03','q9'):('أكمل: ألعب مع _____ بعد المدرسة.','اختر من «أصدقائي» و«المباراة»: ألعب مع _____ بعد المدرسة.',['ar-r480'],'أصدقائي'),
 ('ar-a1-u09-p03','q10'):('أكمل: أنا _____ لأن صديقي جاء.','اختر من «سعيد» و«بعيد»: أنا _____ لأن صديقي جاء.',['ar-r205'],'سعيد'),
 ('ar-a1-u09-p04','q9'):('أكمل: عندي _____ لزيارة المكتبة اليوم.','اختر من «فرصة» و«مشاركة»: عندي _____ لزيارة المكتبة اليوم.',['ar-r340'],'فرصة'),
 ('ar-a1-u09-p04','q10'):('أكمل: أحب _____ في أنشطة الصف.','اختر من «المشاركة» و«الفرصة»: أحب _____ في أنشطة الصف.',['ar-r304'],'المشاركة'),
 ('ar-a1-u09-p05','q9'):('أكمل: سجل الفريق _____ في الشوط الأول.','اختر من «هدفًا» و«فوزًا»: سجل الفريق _____ في الشوط الأول.',['ar-r242'],'هدفًا'),
 ('ar-a1-u09-p05','q10'):('أكمل: انتهت المباراة ب_____ فريقنا.','اختر من «فوز» و«فرصة»: انتهت المباراة ب_____ فريقنا.',['ar-r290'],'فوز'),
}

def blob(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def main():
    if DECISION.exists(): raise SystemExit('duplicate Gate C A1 Unit 9 frontier')
    m=json.loads((READING/'STATE_MANIFEST.json').read_text(encoding='utf-8'))
    if m.get('aggregate_sha256')!=EXPECTED_MANIFEST: raise SystemExit('state manifest drift')
    r=json.loads((READING/'RELEASE_STATUS.json').read_text(encoding='utf-8'))['languages']['arabic']; c=r.get('comprehension_review_progress',{})
    if r.get('release_state')!='REOPEN_REQUIRED' or r.get('educator_release_ready') is not False: raise SystemExit('release boundary drift')
    if (c.get('fresh_records_reviewed'),c.get('fresh_qa_pairs_reviewed'),c.get('fresh_records_with_findings'),c.get('fresh_findings'))!=(48,480,25,43): raise SystemExit('Gate C frontier drift')
    if r['latest_deterministic_gate']['open_findings']!=1080: raise SystemExit('deterministic frontier drift')
    raw=PATH.read_bytes()
    if blob(raw)!=EXPECTED_GIT_BLOB: raise SystemExit('A1 canonical blob drift')
    rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]; ids=[f'ar-a1-u09-p{i:02d}' for i in range(1,7)]
    if [rows[i].get('id') for i in range(48,54)]!=ids: raise SystemExit('Unit 9 id/order drift')
    before={x['id']:json.loads(json.dumps(x,ensure_ascii=False)) for x in rows[48:54]}; by={r['id']:r for r in rows[48:54]}
    for (pid,qid),(old,new,target,answer) in REPAIRS.items():
        rec=by[pid]; qs={q['id']:q for q in rec['questions']}; ans={a['question_id']:a for a in rec['answer_key']}
        if qs[qid].get('prompt')!=old or qs[qid].get('target_ids')!=target or ans[qid].get('answer')!=answer: raise SystemExit(f'{pid}/{qid} frontier drift')
        qs[qid]['prompt']=new
    repaired={pid for pid,_ in REPAIRS}
    for pid in repaired:
        rec=by[pid]; rec['revision']=int(rec.get('revision',0))+1; notes=rec['quality'].setdefault('notes',[])
        if NOTE not in notes: notes.append(NOTE)
    for i,pid in enumerate(ids,start=48):
        old=before[pid]; new=rows[i]
        if len(new['questions'])!=10 or len(new['answer_key'])!=10: raise SystemExit(f'{pid}: 10Q/10A drift')
        if {q['answer_id'] for q in new['questions']}!={a['id'] for a in new['answer_key']}: raise SystemExit(f'{pid}: linkage drift')
        if new['text']!=old['text'] or new['answer_key']!=old['answer_key']: raise SystemExit(f'{pid}: text/answer changed')
        if new.get('new_lexical_targets')!=old.get('new_lexical_targets') or new.get('review_lexical_targets')!=old.get('review_lexical_targets'): raise SystemExit(f'{pid}: lexical drift')
        for k in ('status','coverage_check','linguistic_review','pedagogical_review','answer_key_check','schema_check'):
            if new['quality'].get(k)!=old['quality'].get(k): raise SystemExit(f'{pid}: quality {k} changed')
        if pid not in repaired and new!=old: raise SystemExit(f'{pid}: clean PASS record changed')
    PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in rows)+'\n',encoding='utf-8')
    print(json.dumps({'gate':'C','level':'A1','unit':9,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':5,'fresh_findings':10,'repair_fields':[f'{p}/{q}' for p,q in REPAIRS],'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()

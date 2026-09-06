#!/usr/bin/env python3
"""Apply fresh Arabic Gate C A2 Unit 1 comprehension/grounding repairs."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
PATH=READING/'arabic/a2/passages.jsonl'
DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u01.json'
EXPECTED_GIT_BLOB='be23a9ec562738ea30948aa15e23c670d9b396bb'
EXPECTED_MANIFEST='6f30f6850eb1f0959ab7e118733bafb7337fd63e00f546fa973cf312ecc16884'
NOTE='2026-09-06 fresh Gate C comprehension/answer-grounding review (A2 Unit 1): 60 question-answer pairs reviewed; ten underconstrained transfer prompts repaired across five records; no educator/publication release claim.'
REPAIRS={
 ('ar-a2-u01-p01','q9'):('أكمل: يوجد البنك في _____ الرئيسي قرب السوق.','اختر من «الشارع» و«الخدمة»: يوجد البنك في _____ الرئيسي قرب السوق.',['ar-r564'],'الشارع'),
 ('ar-a2-u01-p01','q10'):('أكمل: يقدم هذا المكتب _____ للسكان كل صباح.','اختر من «خدمة» و«شارع»: يقدم هذا المكتب _____ للسكان كل صباح.',['ar-r583'],'خدمة'),
 ('ar-a2-u01-p02','q9'):('أكمل: اتصلت بالمكتب عبر _____ لمعرفة الموعد.','اختر من «الهاتف» و«البنك»: اتصلت بالمكتب عبر _____ لمعرفة الموعد.',['ar-r576'],'الهاتف'),
 ('ar-a2-u01-p02','q10'):('أكمل: ذهبت إلى _____ لأقوم بمعاملة مالية.','اختر من «البنك» و«الهاتف»: ذهبت إلى _____ لأقوم بمعاملة مالية.',['ar-r581'],'البنك'),
 ('ar-a2-u01-p03','q9'):('أكمل: وضع المركز _____ عن تغيير وقت العمل.','اختر من «إعلانًا» و«رسالة»: وضع المركز _____ عن تغيير وقت العمل.',['ar-r563'],'إعلانًا'),
 ('ar-a2-u01-p03','q10'):('أكمل: أرسلت إلى صديقتي _____ فيها الموعد الجديد.','اختر من «رسالة» و«إعلانًا»: أرسلت إلى صديقتي _____ فيها الموعد الجديد.',['ar-r544'],'رسالة'),
 ('ar-a2-u01-p04','q9'):('أكمل: كانت هذه أول _____ لي للمركز الجديد.','اختر من «زيارة» و«قسم»: كانت هذه أول _____ لي للمركز الجديد.',['ar-r590'],'زيارة'),
 ('ar-a2-u01-p04','q10'):('أكمل: اسأل في _____ الاستقبال عن الموعد.','اختر من «قسم» و«زيارة»: اسأل في _____ الاستقبال عن الموعد.',['ar-r594'],'قسم'),
 ('ar-a2-u01-p05','q9'):('أكمل: قرأت _____ الطعام قبل أن أطلب.','اختر من «قائمة» و«سعر»: قرأت _____ الطعام قبل أن أطلب.',['ar-r595'],'قائمة'),
 ('ar-a2-u01-p05','q10'):('أكمل: سألت عن _____ الكتاب قبل شرائه.','اختر من «سعر» و«قائمة»: سألت عن _____ الكتاب قبل شرائه.',['ar-r613'],'سعر'),
}

def blob(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def main():
    if DECISION.exists(): raise SystemExit('duplicate Gate C A2 Unit 1 frontier')
    m=json.loads((READING/'STATE_MANIFEST.json').read_text(encoding='utf-8'))
    if m.get('aggregate_sha256')!=EXPECTED_MANIFEST: raise SystemExit('state manifest drift')
    r=json.loads((READING/'RELEASE_STATUS.json').read_text(encoding='utf-8'))['languages']['arabic']; c=r.get('comprehension_review_progress',{})
    if r.get('release_state')!='REOPEN_REQUIRED' or r.get('educator_release_ready') is not False: raise SystemExit('release boundary drift')
    if (c.get('fresh_records_reviewed'),c.get('fresh_qa_pairs_reviewed'),c.get('fresh_records_with_findings'),c.get('fresh_findings'))!=(60,600,35,63): raise SystemExit('Gate C frontier drift')
    if c.get('levels_completed')!=['A1']: raise SystemExit('Gate C completed-level frontier drift')
    if r['latest_deterministic_gate']['open_findings']!=1080: raise SystemExit('deterministic frontier drift')
    raw=PATH.read_bytes()
    if blob(raw)!=EXPECTED_GIT_BLOB: raise SystemExit('A2 canonical blob drift')
    rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]; ids=[f'ar-a2-u01-p{i:02d}' for i in range(1,7)]
    if [rows[i].get('id') for i in range(0,6)]!=ids: raise SystemExit('A2 Unit 1 id/order drift')
    before={x['id']:json.loads(json.dumps(x,ensure_ascii=False)) for x in rows[0:6]}; by={r['id']:r for r in rows[0:6]}
    for (pid,qid),(old,new,target,answer) in REPAIRS.items():
        rec=by[pid]; qs={q['id']:q for q in rec['questions']}; ans={a['question_id']:a for a in rec['answer_key']}
        if qs[qid].get('prompt')!=old or qs[qid].get('target_ids')!=target or ans[qid].get('answer')!=answer: raise SystemExit(f'{pid}/{qid} frontier drift')
        qs[qid]['prompt']=new
    repaired={pid for pid,_ in REPAIRS}
    for pid in repaired:
        rec=by[pid]; rec['revision']=int(rec.get('revision',0))+1; notes=rec['quality'].setdefault('notes',[])
        if NOTE not in notes: notes.append(NOTE)
    for i,pid in enumerate(ids,start=0):
        old=before[pid]; new=rows[i]
        if len(new['questions'])!=10 or len(new['answer_key'])!=10: raise SystemExit(f'{pid}: 10Q/10A drift')
        if {q['answer_id'] for q in new['questions']}!={a['id'] for a in new['answer_key']}: raise SystemExit(f'{pid}: linkage drift')
        if new['text']!=old['text'] or new['answer_key']!=old['answer_key']: raise SystemExit(f'{pid}: text/answer changed')
        if new.get('new_lexical_targets')!=old.get('new_lexical_targets') or new.get('review_lexical_targets')!=old.get('review_lexical_targets'): raise SystemExit(f'{pid}: lexical drift')
        for k in ('status','coverage_check','linguistic_review','pedagogical_review','answer_key_check','schema_check'):
            if new['quality'].get(k)!=old['quality'].get(k): raise SystemExit(f'{pid}: quality {k} changed')
        if pid not in repaired and new!=old: raise SystemExit(f'{pid}: clean PASS record changed')
    PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in rows)+'\n',encoding='utf-8')
    print(json.dumps({'gate':'C','level':'A2','unit':1,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':5,'fresh_findings':10,'repair_fields':[f'{p}/{q}' for p,q in REPAIRS],'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()

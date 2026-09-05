#!/usr/bin/env python3
"""Apply fresh Arabic Gate C A1 Unit 6 comprehension/grounding repairs."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
PATH=READING/'arabic/a1/passages.jsonl'
DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/a1_u06.json'
EXPECTED_GIT_BLOB='588929e2f1c79f73500d025a3d663fd598240e9d'
EXPECTED_MANIFEST='afc5214176c40956a5450500a6a716c4328a90f851195784f41938a2671eeb6c'
NOTE='2026-09-05 fresh Gate C comprehension/answer-grounding review (A1 Unit 6): 60 question-answer pairs reviewed; nine underconstrained transfer prompts repaired across five records; no educator/publication release claim.'
REPAIRS={
 ('ar-a1-u06-p01','q9'):('أكمل: هذا _____ قصير إلى السوق.','اختر من «طريق» و«موقع»: هذا _____ قصير إلى السوق.',['ar-r135'],'طريق'),
 ('ar-a1-u06-p01','q10'):('أكمل: مشيت _____ الباب.','اختر من «نحو» و«تحت»: مشيت _____ الباب.',['ar-r267'],'نحو'),
 ('ar-a1-u06-p02','q9'):('أكمل: أبي يقود _____ إلى العمل.','اختر من «السيارة» و«الطريق»: أبي يقود _____ إلى العمل.',['ar-r170'],'السيارة'),
 ('ar-a1-u06-p02','q10'):('أكمل: القطار _____ إلى المحطة في الثامنة.','اختر من «يصل» و«يبدأ»: القطار _____ إلى المحطة في الثامنة.',['ar-r317'],'يصل'),
 ('ar-a1-u06-p03','q9'):('أكمل: الحقيبة _____ الكرسي.','إذا كانت الحقيبة أسفل الكرسي، أكمل: الحقيبة _____ الكرسي.',['ar-r264'],'تحت'),
 ('ar-a1-u06-p04','q9'):('أكمل الأمر: _____ إلى الصف الآن.','إذا كنت تطلب من سامر التوجه إلى الصف، أكمل الأمر: _____ إلى الصف الآن.',['ar-r361'],'اذهب'),
 ('ar-a1-u06-p04','q10'):('أكمل: سامر _____ الحافلة عند الباب.','أكمل بالفعل الذي يعني أنه يبقى عند الباب حتى تأتي الحافلة: سامر _____ الحافلة عند الباب.',['ar-r447'],'ينتظر'),
 ('ar-a1-u06-p05','q9'):('أكمل: ما _____ المدرسة على هذه الخريطة؟','اختر من «موقع» و«وسط»: ما _____ المدرسة على هذه الخريطة؟',['ar-r488'],'موقع'),
 ('ar-a1-u06-p05','q10'):('أكمل: الشجرة في _____ الحديقة.','إذا كانت الشجرة في المنتصف، أكمل: الشجرة في _____ الحديقة.',['ar-r491'],'وسط'),
}

def blob(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def main():
    if DECISION.exists(): raise SystemExit('duplicate Gate C A1 Unit 6 frontier')
    m=json.loads((READING/'STATE_MANIFEST.json').read_text(encoding='utf-8'))
    if m.get('aggregate_sha256')!=EXPECTED_MANIFEST: raise SystemExit('state manifest drift')
    r=json.loads((READING/'RELEASE_STATUS.json').read_text(encoding='utf-8'))['languages']['arabic']
    c=r.get('comprehension_review_progress',{})
    if r.get('release_state')!='REOPEN_REQUIRED' or r.get('educator_release_ready') is not False: raise SystemExit('release boundary drift')
    if (c.get('fresh_records_reviewed'),c.get('fresh_qa_pairs_reviewed'),c.get('fresh_records_with_findings'),c.get('fresh_findings'))!=(30,300,10,15): raise SystemExit('Gate C frontier drift')
    if r['latest_deterministic_gate']['open_findings']!=1080: raise SystemExit('deterministic frontier drift')
    raw=PATH.read_bytes()
    if blob(raw)!=EXPECTED_GIT_BLOB: raise SystemExit('A1 canonical blob drift')
    rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
    ids=[f'ar-a1-u06-p{i:02d}' for i in range(1,7)]
    if [rows[i].get('id') for i in range(30,36)]!=ids: raise SystemExit('Unit 6 id/order drift')
    before={x['id']:json.loads(json.dumps(x,ensure_ascii=False)) for x in rows[30:36]}
    by={r['id']:r for r in rows[30:36]}
    for (pid,qid),(old,new,target,answer) in REPAIRS.items():
        rec=by[pid]; qs={q['id']:q for q in rec['questions']}; ans={a['question_id']:a for a in rec['answer_key']}
        if qs[qid].get('prompt')!=old or qs[qid].get('target_ids')!=target or ans[qid].get('answer')!=answer:
            raise SystemExit(f'{pid}/{qid} frontier drift')
        qs[qid]['prompt']=new
    repaired={pid for pid,_ in REPAIRS}
    for pid in repaired:
        rec=by[pid]; rec['revision']=int(rec.get('revision',0))+1; notes=rec['quality'].setdefault('notes',[])
        if NOTE not in notes: notes.append(NOTE)
    for i,pid in enumerate(ids,start=30):
        old=before[pid]; new=rows[i]
        if len(new['questions'])!=10 or len(new['answer_key'])!=10: raise SystemExit(f'{pid}: 10Q/10A drift')
        if {q['answer_id'] for q in new['questions']}!={a['id'] for a in new['answer_key']}: raise SystemExit(f'{pid}: linkage drift')
        if new['text']!=old['text'] or new['answer_key']!=old['answer_key']: raise SystemExit(f'{pid}: text/answer changed')
        if new.get('new_lexical_targets')!=old.get('new_lexical_targets') or new.get('review_lexical_targets')!=old.get('review_lexical_targets'): raise SystemExit(f'{pid}: lexical drift')
        for k in ('status','coverage_check','linguistic_review','pedagogical_review','answer_key_check','schema_check'):
            if new['quality'].get(k)!=old['quality'].get(k): raise SystemExit(f'{pid}: quality {k} changed')
        if pid not in repaired and new!=old: raise SystemExit(f'{pid}: clean PASS record changed')
    PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in rows)+'\n',encoding='utf-8')
    print(json.dumps({'gate':'C','level':'A1','unit':6,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':5,'fresh_findings':9,'repair_fields':[f'{p}/{q}' for p,q in REPAIRS],'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()

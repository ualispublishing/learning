#!/usr/bin/env python3
"""Apply fresh Arabic Gate C A1 Unit 7 comprehension/grounding repairs."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
READING=ROOT/'reading'
PATH=READING/'arabic/a1/passages.jsonl'
DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/a1_u07.json'
EXPECTED_GIT_BLOB='1bc62ea4dd65be2953d2b57fb1d84f7eef64eaf6'
EXPECTED_MANIFEST='da372789c875d7028c369474ed9482ebac9b071e5eaf28941faca3e2506d42c1'
NOTE='2026-09-05 fresh Gate C comprehension/answer-grounding review (A1 Unit 7): 60 question-answer pairs reviewed; nine underconstrained transfer prompts repaired across five records; no educator/publication release claim.'
REPAIRS={
 ('ar-a1-u07-p01','q9'):('أكمل: في _____ غيوم كثيرة اليوم.','اختر من «السماء» و«الموسم»: في _____ غيوم كثيرة اليوم.',['ar-r489'],'السماء'),
 ('ar-a1-u07-p01','q10'):('أكمل: الشتاء _____ بارد في بلاد كثيرة.','اختر من «موسم» و«صباح»: الشتاء _____ بارد في بلاد كثيرة.',['ar-r451'],'موسم'),
 ('ar-a1-u07-p02','q9'):('أكمل: الحرارة اليوم عشرون _____.','اختر من «درجة» و«موسم»: الحرارة اليوم عشرون _____.',['ar-r496'],'درجة'),
 ('ar-a1-u07-p02','q10'):('أكمل: من الغيوم _____ أن المطر قريب.','اختر من «يبدو» و«يجب»: من الغيوم _____ أن المطر قريب.',['ar-r111'],'يبدو'),
 ('ar-a1-u07-p03','q9'):('أكمل: في الأسبوع _____ عندنا نشاط جديد.','اختر من «القادم» و«الماضي»: في الأسبوع _____ عندنا نشاط جديد.',['ar-r363'],'القادم'),
 ('ar-a1-u07-p03','q10'):('أكمل: _____ أزور صديقي مساءً إذا انتهيت مبكرًا.','اختر من «ربما» و«يجب»: _____ أزور صديقي مساءً إذا انتهيت مبكرًا.',['ar-r105'],'ربما'),
 ('ar-a1-u07-p04','q10'):('أكمل: بقيت هناك ثلاثة _____.','إذا كانت المدة من الاثنين إلى الأربعاء، أكمل: بقيت هناك ثلاثة _____.',['ar-r232'],'أيام'),
 ('ar-a1-u07-p05','q9'):('أكمل: بقيت في المكتبة _____ واحدة.','إذا بقيت ستين دقيقة، أكمل: بقيت في المكتبة _____ واحدة.',['ar-r225'],'ساعة'),
 ('ar-a1-u07-p05','q10'):('أكمل: في هذا _____ عندنا خمسة أيام مدرسة.','اختر من «الأسبوع» و«الساعة»: في هذا _____ عندنا خمسة أيام مدرسة.',['ar-r252'],'الأسبوع'),
}

def blob(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def main():
    if DECISION.exists(): raise SystemExit('duplicate Gate C A1 Unit 7 frontier')
    m=json.loads((READING/'STATE_MANIFEST.json').read_text(encoding='utf-8'))
    if m.get('aggregate_sha256')!=EXPECTED_MANIFEST: raise SystemExit('state manifest drift')
    r=json.loads((READING/'RELEASE_STATUS.json').read_text(encoding='utf-8'))['languages']['arabic']
    c=r.get('comprehension_review_progress',{})
    if r.get('release_state')!='REOPEN_REQUIRED' or r.get('educator_release_ready') is not False: raise SystemExit('release boundary drift')
    if (c.get('fresh_records_reviewed'),c.get('fresh_qa_pairs_reviewed'),c.get('fresh_records_with_findings'),c.get('fresh_findings'))!=(36,360,15,24): raise SystemExit('Gate C frontier drift')
    if r['latest_deterministic_gate']['open_findings']!=1080: raise SystemExit('deterministic frontier drift')
    raw=PATH.read_bytes()
    if blob(raw)!=EXPECTED_GIT_BLOB: raise SystemExit('A1 canonical blob drift')
    rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
    ids=[f'ar-a1-u07-p{i:02d}' for i in range(1,7)]
    if [rows[i].get('id') for i in range(36,42)]!=ids: raise SystemExit('Unit 7 id/order drift')
    before={x['id']:json.loads(json.dumps(x,ensure_ascii=False)) for x in rows[36:42]}
    by={r['id']:r for r in rows[36:42]}
    for (pid,qid),(old,new,target,answer) in REPAIRS.items():
        rec=by[pid]; qs={q['id']:q for q in rec['questions']}; ans={a['question_id']:a for a in rec['answer_key']}
        if qs[qid].get('prompt')!=old or qs[qid].get('target_ids')!=target or ans[qid].get('answer')!=answer:
            raise SystemExit(f'{pid}/{qid} frontier drift')
        qs[qid]['prompt']=new
    repaired={pid for pid,_ in REPAIRS}
    for pid in repaired:
        rec=by[pid]; rec['revision']=int(rec.get('revision',0))+1; notes=rec['quality'].setdefault('notes',[])
        if NOTE not in notes: notes.append(NOTE)
    for i,pid in enumerate(ids,start=36):
        old=before[pid]; new=rows[i]
        if len(new['questions'])!=10 or len(new['answer_key'])!=10: raise SystemExit(f'{pid}: 10Q/10A drift')
        if {q['answer_id'] for q in new['questions']}!={a['id'] for a in new['answer_key']}: raise SystemExit(f'{pid}: linkage drift')
        if new['text']!=old['text'] or new['answer_key']!=old['answer_key']: raise SystemExit(f'{pid}: text/answer changed')
        if new.get('new_lexical_targets')!=old.get('new_lexical_targets') or new.get('review_lexical_targets')!=old.get('review_lexical_targets'): raise SystemExit(f'{pid}: lexical drift')
        for k in ('status','coverage_check','linguistic_review','pedagogical_review','answer_key_check','schema_check'):
            if new['quality'].get(k)!=old['quality'].get(k): raise SystemExit(f'{pid}: quality {k} changed')
        if pid not in repaired and new!=old: raise SystemExit(f'{pid}: clean PASS record changed')
    PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in rows)+'\n',encoding='utf-8')
    print(json.dumps({'gate':'C','level':'A1','unit':7,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':5,'fresh_findings':9,'repair_fields':[f'{p}/{q}' for p,q in REPAIRS],'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()

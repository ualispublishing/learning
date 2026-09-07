#!/usr/bin/env python3
"""Apply fresh Arabic Gate C A2 Unit 5 comprehension/grounding repairs."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'
PATH=READING/'arabic/a2/passages.jsonl'; DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u05.json'
EXPECTED_GIT_BLOB='a1b60ab98efe3a83a0b2e837644385c50851ca62'; EXPECTED_MANIFEST='ff534e0cce821524df6ec660894a5b88b433813449227f74f40e43648c5f0d85'
NOTE='2026-09-06 fresh Gate C comprehension/answer-grounding review (A2 Unit 5): 60 question-answer pairs reviewed; ten underconstrained transfer prompts repaired across five records; no educator/publication release claim.'
REPAIRS={
 ('ar-a2-u05-p01','q9'):('أكمل: أحب _____ الأماكن القديمة في المدينة.','اختر من «تصوير» و«مسابقة»: أحب _____ الأماكن القديمة في المدينة.',['ar-r912'],'تصوير'),
 ('ar-a2-u05-p01','q10'):('أكمل: شاركت المدرسة في _____ للقراءة.','اختر من «مسابقة» و«تصوير»: شاركت المدرسة في _____ للقراءة.',['ar-r908'],'مسابقة'),
 ('ar-a2-u05-p02','q9'):('أكمل: يحتاج هذا القرار إلى _____ قبل أن أختار.','اختر من «تفكير» و«تصوير»: يحتاج هذا القرار إلى _____ قبل أن أختار.',['ar-r948'],'تفكير'),
 ('ar-a2-u05-p02','q10'):('أكمل: بعد الموعد نحتاج إلى _____ النتيجة الأسبوع القادم.','اختر من «متابعة» و«مسابقة»: بعد الموعد نحتاج إلى _____ النتيجة الأسبوع القادم.',['ar-r957'],'متابعة'),
 ('ar-a2-u05-p03','q9'):('أكمل: أول _____ في الخطة هي اختيار الموضوع.','اختر من «خطوة» و«مشاريع»: أول _____ في الخطة هي اختيار الموضوع.',['ar-r934'],'خطوة'),
 ('ar-a2-u05-p03','q10'):('أكمل: يعمل الطلاب على _____ علمية صغيرة.','اختر من «مشاريع» و«مشروع»: يعمل الطلاب على عدة _____ علمية صغيرة.',['ar-r935'],'مشاريع'),
 ('ar-a2-u05-p04','q9'):('أكمل: المشي بعد العشاء أصبح _____ يومية عندي.','اختر من «عادة» و«مسابقة»: المشي بعد العشاء أصبح _____ يومية عندي.',['ar-r977'],'عادة'),
 ('ar-a2-u05-p04','q10'):('أكمل: بدأ الطفل _____ إلى زملائه الجدد.','اختر من «يتعرف» و«ينسى»: بدأ الطفل _____ إلى زملائه الجدد.',['ar-r926'],'يتعرف'),
 ('ar-a2-u05-p05','q9'):('أكمل: يحتاج العزف الجيد إلى _____ منتظم.','اختر من «تدريب» و«مسابقة»: يحتاج العزف الجيد إلى _____ منتظم.',['ar-r806'],'تدريب'),
 ('ar-a2-u05-p05','q10'):('أكمل: لديه _____ طويلة في العمل مع الأطفال.','اختر من «خبرة» و«خطوة»: لديه _____ طويلة في العمل مع الأطفال.',['ar-r1190'],'خبرة'),
}
def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def main():
 if DECISION.exists(): raise SystemExit('duplicate Gate C A2 Unit 5 frontier')
 m=json.loads((READING/'STATE_MANIFEST.json').read_text());
 if m.get('aggregate_sha256')!=EXPECTED_MANIFEST: raise SystemExit('state manifest drift')
 r=json.loads((READING/'RELEASE_STATUS.json').read_text())['languages']['arabic']; c=r.get('comprehension_review_progress',{})
 if r.get('release_state')!='REOPEN_REQUIRED' or r.get('educator_release_ready') is not False: raise SystemExit('release boundary drift')
 if (c.get('fresh_records_reviewed'),c.get('fresh_qa_pairs_reviewed'),c.get('fresh_records_with_findings'),c.get('fresh_findings'))!=(84,840,55,103): raise SystemExit('Gate C frontier drift')
 if c.get('levels_completed')!=['A1'] or r['latest_deterministic_gate']['open_findings']!=1080: raise SystemExit('review/release frontier drift')
 raw=PATH.read_bytes();
 if blob(raw)!=EXPECTED_GIT_BLOB: raise SystemExit('A2 canonical blob drift')
 rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]; ids=[f'ar-a2-u05-p{i:02d}' for i in range(1,7)]
 if [rows[i].get('id') for i in range(24,30)]!=ids: raise SystemExit('A2 Unit 5 id/order drift')
 before={x['id']:json.loads(json.dumps(x,ensure_ascii=False)) for x in rows[24:30]}; by={r['id']:r for r in rows[24:30]}
 for (pid,qid),(old,new,target,answer) in REPAIRS.items():
  rec=by[pid]; qs={q['id']:q for q in rec['questions']}; ans={a['question_id']:a for a in rec['answer_key']}
  if qs[qid].get('prompt')!=old or qs[qid].get('target_ids')!=target or ans[qid].get('answer')!=answer: raise SystemExit(f'{pid}/{qid} frontier drift')
  qs[qid]['prompt']=new
 repaired={p for p,_ in REPAIRS}
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
 PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in rows)+'\n')
 print(json.dumps({'gate':'C','level':'A2','unit':5,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':5,'fresh_findings':10,'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))
if __name__=='__main__': main()

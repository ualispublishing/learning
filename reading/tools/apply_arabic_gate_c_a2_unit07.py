#!/usr/bin/env python3
"""Apply fresh Arabic Gate C A2 Unit 7 comprehension/grounding repairs."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/a2/passages.jsonl'; DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u07.json'
EXPECTED_GIT_BLOB='92fd8341936e13cb4a7f7ce942921c9632ee2451'; EXPECTED_MANIFEST='b41675dbbb68a6f893d01df1b09f8a25e82df43901cb2aabec17f54d7ccf9d71'
NOTE='2026-09-07 fresh Gate C comprehension/answer-grounding review (A2 Unit 7): 60 question-answer pairs reviewed; ten underconstrained news/community transfer prompts repaired across five records; no educator/publication release claim.'
REPAIRS={
('ar-a2-u07-p01','q9'):('أكمل: نظم المركز _____ ثقافية يوم الجمعة.','اختر من «مناسبة» و«جمهور»: نظم المركز _____ ثقافية يوم الجمعة.',['ar-r593'],'مناسبة'),
('ar-a2-u07-p01','q10'):('أكمل: صفق _____ بعد انتهاء العرض.','اختر من «الجمهور» و«المناسبة»: صفق _____ بعد انتهاء العرض.',['ar-r975'],'الجمهور'),
('ar-a2-u07-p02','q9'):('أكمل: نشرت _____ المحلية خبر افتتاح المركز.','اختر من «الصحافة» و«البيان»: نشرت _____ المحلية خبر افتتاح المركز.',['ar-r1285'],'الصحافة'),
('ar-a2-u07-p02','q10'):('أكمل: أصدرت المدرسة _____ عن وقت الإغلاق.','اختر من «بيانًا» و«صحافة»: أصدرت المدرسة _____ عن وقت الإغلاق.',['ar-r510'],'بيانًا'),
('ar-a2-u07-p03','q9'):('أكمل: أجرى الفريق _____ لمعرفة سبب المشكلة.','اختر من «تحقيقًا» و«تأثيرًا»: أجرى الفريق _____ لمعرفة سبب المشكلة.',['ar-r218'],'تحقيقًا'),
('ar-a2-u07-p03','q10'):('أكمل: للطقس _____ على خطة الرحلة.','اختر من «تأثير» و«تحقيق»: للطقس _____ على خطة الرحلة.',['ar-r702'],'تأثير'),
('ar-a2-u07-p04','q9'):('أكمل: _____ النادي موعد الفعالية الجديدة.','اختر من «أعلن» و«أظهرت»: _____ النادي موعد الفعالية الجديدة.',['ar-r337'],'أعلن'),
('ar-a2-u07-p04','q10'):('أكمل: _____ الدراسة أن معظم المشاركين فضلوا الوقت المسائي.','اختر من «أظهرت» و«أعلن»: _____ الدراسة أن معظم المشاركين فضلوا الوقت المسائي.',['ar-r1128'],'أظهرت'),
('ar-a2-u07-p05','q9'):('أكمل: كتبت ثلاث أفكار _____ في الملخص.','اختر من «رئيسية» و«ثانوية»: كتبت ثلاث أفكار _____ في الملخص.',['ar-r905'],'رئيسية'),
('ar-a2-u07-p05','q10'):('أكمل: _____ المنظمون حضور عدد كبير إذا كان الطقس مناسبًا.','اختر من «يتوقع» و«يؤكد»: _____ المنظمون، على سبيل التقدير لا التأكيد، حضور عدد كبير إذا كان الطقس مناسبًا.',['ar-r1349'],'يتوقع')}
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def main():
 if DECISION.exists():raise SystemExit('duplicate Gate C A2 Unit 7 frontier')
 m=json.loads((READING/'STATE_MANIFEST.json').read_text())
 if m.get('aggregate_sha256')!=EXPECTED_MANIFEST:raise SystemExit('state manifest drift')
 r=json.loads((READING/'RELEASE_STATUS.json').read_text())['languages']['arabic'];c=r['comprehension_review_progress']
 if r['release_state']!='REOPEN_REQUIRED' or r['educator_release_ready'] is not False:raise SystemExit('release boundary drift')
 if (c['fresh_records_reviewed'],c['fresh_qa_pairs_reviewed'],c['fresh_records_with_findings'],c['fresh_findings'])!=(96,960,65,123) or c['levels_completed']!=['A1']:raise SystemExit('Gate C frontier drift')
 if r['latest_deterministic_gate']['open_findings']!=1080:raise SystemExit('deterministic frontier drift')
 raw=PATH.read_bytes()
 if blob(raw)!=EXPECTED_GIT_BLOB:raise SystemExit('A2 canonical blob drift')
 rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()];ids=[f'ar-a2-u07-p{i:02d}' for i in range(1,7)]
 if [rows[i].get('id') for i in range(36,42)]!=ids:raise SystemExit('A2 Unit 7 id/order drift')
 before={x['id']:json.loads(json.dumps(x,ensure_ascii=False)) for x in rows[36:42]};by={r['id']:r for r in rows[36:42]}
 for (pid,qid),(old,new,target,answer) in REPAIRS.items():
  qs={q['id']:q for q in by[pid]['questions']};ans={a['question_id']:a for a in by[pid]['answer_key']}
  if qs[qid].get('prompt')!=old or qs[qid].get('target_ids')!=target or ans[qid].get('answer')!=answer:raise SystemExit(f'{pid}/{qid} frontier drift')
  qs[qid]['prompt']=new
 repaired={p for p,_ in REPAIRS}
 for p in repaired:
  by[p]['revision']=int(by[p].get('revision',0))+1;notes=by[p]['quality'].setdefault('notes',[])
  if NOTE not in notes:notes.append(NOTE)
 for i,p in enumerate(ids,start=36):
  o,n=before[p],rows[i]
  if len(n['questions'])!=10 or len(n['answer_key'])!=10:raise SystemExit(f'{p}: 10Q/10A drift')
  if {q['answer_id'] for q in n['questions']}!={a['id'] for a in n['answer_key']}:raise SystemExit(f'{p}: linkage drift')
  if n['text']!=o['text'] or n['answer_key']!=o['answer_key'] or n.get('new_lexical_targets')!=o.get('new_lexical_targets') or n.get('review_lexical_targets')!=o.get('review_lexical_targets'):raise SystemExit(f'{p}: protected content drift')
  for k in ('status','coverage_check','linguistic_review','pedagogical_review','answer_key_check','schema_check'):
   if n['quality'].get(k)!=o['quality'].get(k):raise SystemExit(f'{p}: quality {k} changed')
  if p not in repaired and n!=o:raise SystemExit(f'{p}: clean PASS record changed')
 PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in rows)+'\n')
 print(json.dumps({'gate':'C','level':'A2','unit':7,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':5,'fresh_findings':10,'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

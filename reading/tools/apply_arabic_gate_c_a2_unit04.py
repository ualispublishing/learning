#!/usr/bin/env python3
"""Apply fresh Arabic Gate C A2 Unit 4 comprehension/grounding repairs."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'
PATH=READING/'arabic/a2/passages.jsonl'; DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u04.json'
EXPECTED_GIT_BLOB='8004f7361c4b8d382fcd0be888ec8eac3367c6be'; EXPECTED_MANIFEST='ff34fa934bcf95f46d667087efb3ff6c082da17a34d030af12068422d939f055'
NOTE='2026-09-06 fresh Gate C comprehension/answer-grounding review (A2 Unit 4): 60 question-answer pairs reviewed; ten transfer-prompt defects repaired across five records, including one malformed cloze stem and one unnatural target context; no educator/publication release claim.'
REPAIRS={
 ('ar-a2-u04-p01','q9'):('أكمل: أريد قميصًا من _____ أكبر.','اختر من «حجم» و«قطع»: أريد صندوقًا ذا _____ أكبر.',['ar-r763'],'حجم'),
 ('ar-a2-u04-p01','q10'):('أكمل: في العلبة عشر _____ من البسكويت.','اختر من «قطع» و«حجم»: في العلبة عشر _____ من البسكويت.',['ar-r725'],'قطع'),
 ('ar-a2-u04-p02','q9'):('أكمل: سألت عن _____ الهاتف قبل شرائه.','اختر من «ثمن» و«صفقة»: سألت عن _____ الهاتف قبل شرائه.',['ar-r939'],'ثمن'),
 ('ar-a2-u04-p02','q10'):('أكمل: اشتريت الكتابين بسعر منخفض؛ كانت _____ جيدة.','اختر من «صفقة» و«ثمن»: اشتريت الكتابين بسعر منخفض؛ كانت _____ جيدة.',['ar-r941'],'صفقة'),
 ('ar-a2-u04-p03','q9'):('أكمل: هذا الكتاب مفيد جدًا وي_____ ثمنه.','اختر من «يستحق» و«يستخدم»: هذا الكتاب مفيد جدًا و_____ ثمنه.',['ar-r920'],'يستحق'),
 ('ar-a2-u04-p03','q10'):('أكمل: حملت _____ جديدًا لتنظيم وقتي.','اختر من «تطبيقًا» و«اشتراكًا»: حملت _____ جديدًا لتنظيم وقتي.',['ar-r919'],'تطبيقًا'),
 ('ar-a2-u04-p04','q9'):('أكمل: هذا الطعام ما زال _____ للأكل.','اختر من «صالحًا» و«فاسدًا»: هذا الطعام ما زال _____ للأكل.',['ar-r716'],'صالحًا'),
 ('ar-a2-u04-p04','q10'):('أكمل: أخذت كتابًا إلكترونيًا _____ النسخة الورقية.','اختر من «بدل» و«مع»: أخذت كتابًا إلكترونيًا _____ النسخة الورقية.',['ar-r719'],'بدل'),
 ('ar-a2-u04-p05','q9'):('أكمل: يحتاج الهاتف إلى _____ قبل أن أستخدمه مرة أخرى.','اختر من «إصلاح» و«صفقة»: يحتاج الهاتف إلى _____ قبل أن أستخدمه مرة أخرى.',['ar-r963'],'إصلاح'),
 ('ar-a2-u04-p05','q10'):('أكمل: بعد المشكلة أصبح الوضع _____ من قبل.','اختر من «أسوأ» و«أفضل»: بعد المشكلة ازداد سوءًا؛ أصبح الوضع _____ من قبل.',['ar-r972'],'أسوأ'),
}
def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def main():
 if DECISION.exists(): raise SystemExit('duplicate Gate C A2 Unit 4 frontier')
 m=json.loads((READING/'STATE_MANIFEST.json').read_text());
 if m.get('aggregate_sha256')!=EXPECTED_MANIFEST: raise SystemExit('state manifest drift')
 r=json.loads((READING/'RELEASE_STATUS.json').read_text())['languages']['arabic']; c=r.get('comprehension_review_progress',{})
 if r.get('release_state')!='REOPEN_REQUIRED' or r.get('educator_release_ready') is not False: raise SystemExit('release boundary drift')
 if (c.get('fresh_records_reviewed'),c.get('fresh_qa_pairs_reviewed'),c.get('fresh_records_with_findings'),c.get('fresh_findings'))!=(78,780,50,93): raise SystemExit('Gate C frontier drift')
 if c.get('levels_completed')!=['A1'] or r['latest_deterministic_gate']['open_findings']!=1080: raise SystemExit('review/release frontier drift')
 raw=PATH.read_bytes();
 if blob(raw)!=EXPECTED_GIT_BLOB: raise SystemExit('A2 canonical blob drift')
 rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]; ids=[f'ar-a2-u04-p{i:02d}' for i in range(1,7)]
 if [rows[i].get('id') for i in range(18,24)]!=ids: raise SystemExit('A2 Unit 4 id/order drift')
 before={x['id']:json.loads(json.dumps(x,ensure_ascii=False)) for x in rows[18:24]}; by={r['id']:r for r in rows[18:24]}
 for (pid,qid),(old,new,target,answer) in REPAIRS.items():
  rec=by[pid]; qs={q['id']:q for q in rec['questions']}; ans={a['question_id']:a for a in rec['answer_key']}
  if qs[qid].get('prompt')!=old or qs[qid].get('target_ids')!=target or ans[qid].get('answer')!=answer: raise SystemExit(f'{pid}/{qid} frontier drift')
  qs[qid]['prompt']=new
 repaired={p for p,_ in REPAIRS}
 for pid in repaired:
  rec=by[pid]; rec['revision']=int(rec.get('revision',0))+1; notes=rec['quality'].setdefault('notes',[])
  if NOTE not in notes: notes.append(NOTE)
 for i,pid in enumerate(ids,start=18):
  old=before[pid]; new=rows[i]
  if len(new['questions'])!=10 or len(new['answer_key'])!=10: raise SystemExit(f'{pid}: 10Q/10A drift')
  if {q['answer_id'] for q in new['questions']}!={a['id'] for a in new['answer_key']}: raise SystemExit(f'{pid}: linkage drift')
  if new['text']!=old['text'] or new['answer_key']!=old['answer_key']: raise SystemExit(f'{pid}: text/answer changed')
  if new.get('new_lexical_targets')!=old.get('new_lexical_targets') or new.get('review_lexical_targets')!=old.get('review_lexical_targets'): raise SystemExit(f'{pid}: lexical drift')
  for k in ('status','coverage_check','linguistic_review','pedagogical_review','answer_key_check','schema_check'):
   if new['quality'].get(k)!=old['quality'].get(k): raise SystemExit(f'{pid}: quality {k} changed')
  if pid not in repaired and new!=old: raise SystemExit(f'{pid}: clean PASS record changed')
 PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in rows)+'\n')
 print(json.dumps({'gate':'C','level':'A2','unit':4,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':5,'fresh_findings':10,'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))
if __name__=='__main__': main()

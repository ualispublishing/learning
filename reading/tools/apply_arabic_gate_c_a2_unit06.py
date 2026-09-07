#!/usr/bin/env python3
"""Apply fresh Arabic Gate C A2 Unit 6 comprehension/grounding repairs."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/a2/passages.jsonl'; DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u06.json'
EXPECTED_GIT_BLOB='213cecdb625c23cc7c47b3bddef9e10fa7ef68ae'; EXPECTED_MANIFEST='6df583461dd3b7a26de67ebed3894d05591f40fd48cde526a25b68c55067629e'
NOTE='2026-09-06 fresh Gate C comprehension/answer-grounding review (A2 Unit 6): 60 question-answer pairs reviewed; ten underconstrained travel transfer prompts repaired across five records; no educator/publication release claim.'
REPAIRS={
('ar-a2-u06-p01','q9'):('أكمل: سافرنا إلى المدينة بال_____.','اختر من «طائرة» و«قطار»: سافرنا جوًا إلى المدينة بال_____.',['ar-r720'],'طائرة'),
('ar-a2-u06-p01','q10'):('أكمل: وصلنا إلى _____ قبل الرحلة بساعتين.','اختر من «المطار» و«القرية»: وصلنا إلى _____ لإنهاء إجراءات الرحلة قبل الإقلاع بساعتين.',['ar-r1005'],'المطار'),
('ar-a2-u06-p02','q9'):('أكمل: أخذنا _____ من المحطة إلى المدينة التالية.','اختر من «قطارًا» و«طائرة»: أخذنا _____ يسير على السكة من المحطة إلى المدينة التالية.',['ar-r1597'],'قطارًا'),
('ar-a2-u06-p02','q10'):('أكمل: استمر _____ عشر دقائق قبل فتح الباب.','اختر من «الانتظار» و«الوصول»: استمر _____ عشر دقائق قبل فتح الباب.',['ar-r741'],'الانتظار'),
('ar-a2-u06-p03','q9'):('أكمل: القطار والحافلة من وسائل _____ داخل المدينة.','اختر من «النقل» و«الانتظار»: القطار والحافلة من وسائل _____ داخل المدينة.',['ar-r316'],'النقل'),
('ar-a2-u06-p03','q10'):('أكمل: توجد _____ نقل مختلفة داخل المدينة.','اختر من «وسائل» و«قرى»: توجد _____ نقل مختلفة داخل المدينة.',['ar-r855'],'وسائل'),
('ar-a2-u06-p04','q9'):('أكمل: القطار _____ في هذه المحطة خمس دقائق.','اختر من «يتوقف» و«يطير»: القطار _____ في هذه المحطة خمس دقائق.',['ar-r849'],'يتوقف'),
('ar-a2-u06-p04','q10'):('أكمل: هذا الوقت _____ للاجتماع عندي.','اختر من «مناسب» و«أسوأ»: هذا الوقت _____ للاجتماع عندي.',['ar-r836'],'مناسب'),
('ar-a2-u06-p05','q9'):('أكمل: زاروا _____ صغيرة بين الجبال.','اختر من «قرية» و«بحر»: زاروا _____ صغيرة بين الجبال.',['ar-r837'],'قرية'),
('ar-a2-u06-p05','q10'):('أكمل: مشينا على الشاطئ قرب _____.','اختر من «البحر» و«القرية»: أبحرت السفينة في _____.',['ar-r835'],'البحر')}
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def main():
 if DECISION.exists():raise SystemExit('duplicate Gate C A2 Unit 6 frontier')
 m=json.loads((READING/'STATE_MANIFEST.json').read_text());
 if m.get('aggregate_sha256')!=EXPECTED_MANIFEST:raise SystemExit('state manifest drift')
 r=json.loads((READING/'RELEASE_STATUS.json').read_text())['languages']['arabic'];c=r['comprehension_review_progress']
 if r['release_state']!='REOPEN_REQUIRED' or r['educator_release_ready'] is not False:raise SystemExit('release boundary drift')
 if (c['fresh_records_reviewed'],c['fresh_qa_pairs_reviewed'],c['fresh_records_with_findings'],c['fresh_findings'])!=(90,900,60,113) or c['levels_completed']!=['A1']:raise SystemExit('Gate C frontier drift')
 if r['latest_deterministic_gate']['open_findings']!=1080:raise SystemExit('deterministic frontier drift')
 raw=PATH.read_bytes();
 if blob(raw)!=EXPECTED_GIT_BLOB:raise SystemExit('A2 canonical blob drift')
 rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()];ids=[f'ar-a2-u06-p{i:02d}' for i in range(1,7)]
 if [rows[i].get('id') for i in range(30,36)]!=ids:raise SystemExit('A2 Unit 6 id/order drift')
 before={x['id']:json.loads(json.dumps(x,ensure_ascii=False)) for x in rows[30:36]};by={r['id']:r for r in rows[30:36]}
 for (pid,qid),(old,new,target,answer) in REPAIRS.items():
  qs={q['id']:q for q in by[pid]['questions']};ans={a['question_id']:a for a in by[pid]['answer_key']}
  if qs[qid].get('prompt')!=old or qs[qid].get('target_ids')!=target or ans[qid].get('answer')!=answer:raise SystemExit(f'{pid}/{qid} frontier drift')
  qs[qid]['prompt']=new
 repaired={p for p,_ in REPAIRS}
 for p in repaired:
  by[p]['revision']=int(by[p].get('revision',0))+1;notes=by[p]['quality'].setdefault('notes',[])
  if NOTE not in notes:notes.append(NOTE)
 for i,p in enumerate(ids,start=30):
  o,n=before[p],rows[i]
  if len(n['questions'])!=10 or len(n['answer_key'])!=10:raise SystemExit(f'{p}: 10Q/10A drift')
  if {q['answer_id'] for q in n['questions']}!={a['id'] for a in n['answer_key']}:raise SystemExit(f'{p}: linkage drift')
  if n['text']!=o['text'] or n['answer_key']!=o['answer_key'] or n.get('new_lexical_targets')!=o.get('new_lexical_targets') or n.get('review_lexical_targets')!=o.get('review_lexical_targets'):raise SystemExit(f'{p}: protected content drift')
  for k in ('status','coverage_check','linguistic_review','pedagogical_review','answer_key_check','schema_check'):
   if n['quality'].get(k)!=o['quality'].get(k):raise SystemExit(f'{p}: quality {k} changed')
  if p not in repaired and n!=o:raise SystemExit(f'{p}: clean PASS record changed')
 PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in rows)+'\n')
 print(json.dumps({'gate':'C','level':'A2','unit':6,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':5,'fresh_findings':10,'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

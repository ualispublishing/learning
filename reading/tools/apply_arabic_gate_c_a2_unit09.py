#!/usr/bin/env python3
"""Apply fresh Arabic Gate C A2 Unit 9 comprehension/grounding repairs."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/a2/passages.jsonl'; DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u09.json'
EXPECTED_GIT_BLOB='16ddb6ac525610c7e230419ab1328738b46e634d'; EXPECTED_MANIFEST='f114bb20956dc69a8e960fc1c018db510184c5c395b0e989914cbd837408834d'
NOTE='2026-09-07 fresh Gate C comprehension/answer-grounding review (A2 Unit 9): 60 question-answer pairs reviewed; three underconstrained culture/story transfer prompts repaired across three records; no educator/publication release claim.'
REPAIRS={
('ar-a2-u09-p01','q9'):('أكمل: حكت الجدة _____ عن طفولتها.','اختر من «قصة» و«نسخة»: حكت الجدة _____ عن طفولتها.',['ar-r638'],'قصة'),
('ar-a2-u09-p02','q9'):('أكمل: عندي _____ إلكترونية من الكتاب.','اختر من «نسخة» و«قصة»: عندي _____ إلكترونية من الكتاب.',['ar-r1149'],'نسخة'),
('ar-a2-u09-p03','q9'):('أكمل: حجزنا طاولة في _____ قريب.','اختر من «مطعم» و«مطار»: حجزنا طاولة للعشاء في _____ قريب.',['ar-r1267'],'مطعم')}
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def main():
 if DECISION.exists():raise SystemExit('duplicate Gate C A2 Unit 9 frontier')
 m=json.loads((READING/'STATE_MANIFEST.json').read_text())
 if m.get('aggregate_sha256')!=EXPECTED_MANIFEST:raise SystemExit('state manifest drift')
 r=json.loads((READING/'RELEASE_STATUS.json').read_text())['languages']['arabic'];c=r['comprehension_review_progress']
 if r['release_state']!='REOPEN_REQUIRED' or r['educator_release_ready'] is not False:raise SystemExit('release boundary drift')
 if (c['fresh_records_reviewed'],c['fresh_qa_pairs_reviewed'],c['fresh_records_with_findings'],c['fresh_findings'])!=(108,1080,74,139) or c['levels_completed']!=['A1']:raise SystemExit('Gate C frontier drift')
 if r['latest_deterministic_gate']['open_findings']!=1080:raise SystemExit('deterministic frontier drift')
 raw=PATH.read_bytes()
 if blob(raw)!=EXPECTED_GIT_BLOB:raise SystemExit('A2 canonical blob drift')
 rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()];ids=[f'ar-a2-u09-p{i:02d}' for i in range(1,7)]
 if [rows[i].get('id') for i in range(48,54)]!=ids:raise SystemExit('A2 Unit 9 id/order drift')
 before={x['id']:json.loads(json.dumps(x,ensure_ascii=False)) for x in rows[48:54]};by={r['id']:r for r in rows[48:54]}
 for (pid,qid),(old,new,target,answer) in REPAIRS.items():
  qs={q['id']:q for q in by[pid]['questions']};ans={a['question_id']:a for a in by[pid]['answer_key']}
  if qs[qid].get('prompt')!=old or qs[qid].get('target_ids')!=target or ans[qid].get('answer')!=answer:raise SystemExit(f'{pid}/{qid} frontier drift')
  qs[qid]['prompt']=new
 repaired={p for p,_ in REPAIRS}
 for p in repaired:
  by[p]['revision']=int(by[p].get('revision',0))+1;notes=by[p]['quality'].setdefault('notes',[])
  if NOTE not in notes:notes.append(NOTE)
 for i,p in enumerate(ids,start=48):
  o,n=before[p],rows[i]
  if len(n['questions'])!=10 or len(n['answer_key'])!=10:raise SystemExit(f'{p}: 10Q/10A drift')
  if {q['answer_id'] for q in n['questions']}!={a['id'] for a in n['answer_key']}:raise SystemExit(f'{p}: linkage drift')
  if n['text']!=o['text'] or n['answer_key']!=o['answer_key'] or n.get('new_lexical_targets')!=o.get('new_lexical_targets') or n.get('review_lexical_targets')!=o.get('review_lexical_targets'):raise SystemExit(f'{p}: protected content drift')
  for k in ('status','coverage_check','linguistic_review','pedagogical_review','answer_key_check','schema_check'):
   if n['quality'].get(k)!=o['quality'].get(k):raise SystemExit(f'{p}: quality {k} changed')
  if p not in repaired and n!=o:raise SystemExit(f'{p}: clean PASS record changed')
 PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in rows)+'\n')
 print(json.dumps({'gate':'C','level':'A2','unit':9,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':3,'fresh_findings':3,'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

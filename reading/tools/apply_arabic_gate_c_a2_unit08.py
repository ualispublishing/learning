#!/usr/bin/env python3
"""Apply fresh Arabic Gate C A2 Unit 8 comprehension/grounding repairs."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/a2/passages.jsonl'; DECISION=READING/'audit/arabic_gate_c_decisions_2026-09-05/a2_u08.json'
EXPECTED_GIT_BLOB='57a033ef76d073078d4bd3103987f7bfacc03e07'; EXPECTED_MANIFEST='0d09c5ee4b74d992b589e453b907339530c94ed1fd4ab37a655d2695feab02b3'
NOTE='2026-09-07 fresh Gate C comprehension/answer-grounding review (A2 Unit 8): 60 question-answer pairs reviewed; six underconstrained environmental transfer prompts repaired across four records; no educator/publication release claim.'
REPAIRS={
('ar-a2-u08-p01','q9'):('أكمل: هذه _____ هادئة من الحديقة.','اختر من «منطقة» و«مواد»: هذه _____ هادئة من الحديقة.',['ar-r144'],'منطقة'),
('ar-a2-u08-p01','q10'):('أكمل: صنع الطلاب النموذج من _____ بسيطة معاد استخدامها.','اختر من «مواد» و«منطقة»: صنع الطلاب النموذج من _____ بسيطة معاد استخدامها.',['ar-r843'],'مواد'),
('ar-a2-u08-p02','q9'):('أكمل: نحاول تقليل _____ الورق عندما لا نحتاج إليه.','اختر من «استخدام» و«طاقة»: نحاول تقليل _____ الورق عندما لا نحتاج إليه.',['ar-r545'],'استخدام'),
('ar-a2-u08-p02','q10'):('أكمل: تحتاج الأجهزة الكهربائية إلى _____.','اختر من «طاقة» و«استخدام»: تحتاج الأجهزة الكهربائية إلى _____.',['ar-r524'],'طاقة'),
('ar-a2-u08-p03','q9'):('أكمل: يحتاج _____ النبات إلى ماء وضوء مناسبين.','اختر من «نمو» و«منطقة»: يحتاج _____ النبات إلى ماء وضوء مناسبين.',['ar-r818'],'نمو'),
('ar-a2-u08-p05','q9'):('أكمل: شارك أفراد _____ في اقتراح حلول للحي.','اختر من «المجتمع» و«الطاقة»: شارك أفراد _____ في اقتراح حلول للحي.',['ar-r445'],'المجتمع')}
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def main():
 if DECISION.exists():raise SystemExit('duplicate Gate C A2 Unit 8 frontier')
 m=json.loads((READING/'STATE_MANIFEST.json').read_text())
 if m.get('aggregate_sha256')!=EXPECTED_MANIFEST:raise SystemExit('state manifest drift')
 r=json.loads((READING/'RELEASE_STATUS.json').read_text())['languages']['arabic'];c=r['comprehension_review_progress']
 if r['release_state']!='REOPEN_REQUIRED' or r['educator_release_ready'] is not False:raise SystemExit('release boundary drift')
 if (c['fresh_records_reviewed'],c['fresh_qa_pairs_reviewed'],c['fresh_records_with_findings'],c['fresh_findings'])!=(102,1020,70,133) or c['levels_completed']!=['A1']:raise SystemExit('Gate C frontier drift')
 if r['latest_deterministic_gate']['open_findings']!=1080:raise SystemExit('deterministic frontier drift')
 raw=PATH.read_bytes()
 if blob(raw)!=EXPECTED_GIT_BLOB:raise SystemExit('A2 canonical blob drift')
 rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()];ids=[f'ar-a2-u08-p{i:02d}' for i in range(1,7)]
 if [rows[i].get('id') for i in range(42,48)]!=ids:raise SystemExit('A2 Unit 8 id/order drift')
 before={x['id']:json.loads(json.dumps(x,ensure_ascii=False)) for x in rows[42:48]};by={r['id']:r for r in rows[42:48]}
 for (pid,qid),(old,new,target,answer) in REPAIRS.items():
  qs={q['id']:q for q in by[pid]['questions']};ans={a['question_id']:a for a in by[pid]['answer_key']}
  if qs[qid].get('prompt')!=old or qs[qid].get('target_ids')!=target or ans[qid].get('answer')!=answer:raise SystemExit(f'{pid}/{qid} frontier drift')
  qs[qid]['prompt']=new
 repaired={p for p,_ in REPAIRS}
 for p in repaired:
  by[p]['revision']=int(by[p].get('revision',0))+1;notes=by[p]['quality'].setdefault('notes',[])
  if NOTE not in notes:notes.append(NOTE)
 for i,p in enumerate(ids,start=42):
  o,n=before[p],rows[i]
  if len(n['questions'])!=10 or len(n['answer_key'])!=10:raise SystemExit(f'{p}: 10Q/10A drift')
  if {q['answer_id'] for q in n['questions']}!={a['id'] for a in n['answer_key']}:raise SystemExit(f'{p}: linkage drift')
  if n['text']!=o['text'] or n['answer_key']!=o['answer_key'] or n.get('new_lexical_targets')!=o.get('new_lexical_targets') or n.get('review_lexical_targets')!=o.get('review_lexical_targets'):raise SystemExit(f'{p}: protected content drift')
  for k in ('status','coverage_check','linguistic_review','pedagogical_review','answer_key_check','schema_check'):
   if n['quality'].get(k)!=o['quality'].get(k):raise SystemExit(f'{p}: quality {k} changed')
  if p not in repaired and n!=o:raise SystemExit(f'{p}: clean PASS record changed')
 PATH.write_text('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in rows)+'\n')
 print(json.dumps({'gate':'C','level':'A2','unit':8,'records_reviewed':6,'qa_pairs_reviewed':60,'records_repaired':4,'fresh_findings':6,'quality_promotion':False,'release_claim':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Apply fresh Arabic Gate B C1 Unit 5 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; R=ROOT/'reading'
PATH=R/'arabic/c1/passages.jsonl'; RELEASE=R/'RELEASE_STATUS.json'; INVENTORY=R/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; DD=R/'audit/arabic_gate_b_decisions_2026-08-30'
IDS=[f'ar-c1-u05-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-04 fresh Gate B naturalness review (C1 Unit 5): learner-facing prose/Q/A reviewed passage by passage; only high-confidence MSA grammar, idiom, reference, semantic, and assessment-wording repairs applied; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-c1-u05-p02':[(
  'قد يكون الأثر صغيرًا لكنه ثابت بما يكفي ليهم على مدى طويل، وقد يكون كبيرًا في رقم واحد لكنه غير مستقر.',
  'قد يكون الأثر صغيرًا لكنه ثابت بما يكفي ليكون مهمًا على مدى طويل، وقد يكون كبيرًا في رقم واحد لكنه غير مستقر.'
 )],
 'ar-c1-u05-p06':[(
  'وقد يكون تدفق البيانات غزيرًا لكنه يفقد الحالات التي تصمت فيها الأجهزة عند أسوأ الأعطال.',
  'وقد يكون تدفق البيانات غزيرًا لكن قد تغيب عنه الحالات التي تصمت فيها الأجهزة عند أسوأ الأعطال.'
 )],
}
QA_REPAIRS={
 'ar-c1-u05-p02':{'answers':{'q2':('الأول الأسابيع منفردة، والثاني المسار عبر الزمن مع التباين.','الأول يعرض الأسابيع منفردة، والثاني يعرض المسار عبر الزمن مع التباين.')}},
 'ar-c1-u05-p05':{'answers':{'q10':('ظهور شيء أو أصبح واضحًا بعد أن لم يكن بارزًا.','ظهور شيء أو اتضاحه بعد أن لم يكن بارزًا.')}},
 'ar-c1-u05-p06':{'answers':{'q10':('تقابل قرار التصرف تحت المخاطر بحكم معرفي مستقل وتمنع رفع الثقة لغويًا لمجرد أن القرار عاجل.','تفصل بين قرار التصرف تحت المخاطر والحكم المعرفي المستقل، وتمنع رفع الثقة لغويًا لمجرد أن القرار عاجل.')}},
}
FINDING_META={
 'ar-c1-u05-p01':[],
 'ar-c1-u05-p02':[("text","grammar_wording","moderate","بما يكفي ليهم is malformed/ambiguous without the intended predicative construction; state explicitly that the small stable effect can be important over a long period."),("answer q2","grammar_wording","moderate","الأول الأسابيع منفردة lacks a verb and does not form a complete answer to what the two graphs show; restore parallel verbal clauses.")],
 'ar-c1-u05-p03':[],
 'ar-c1-u05-p04':[],
 'ar-c1-u05-p05':[("answer q10","grammar_wording","moderate","ظهور شيء أو أصبح واضحًا coordinates a noun phrase with a finite verb; use the parallel verbal noun اتضاحه.")],
 'ar-c1-u05-p06':[("text","semantic_precision","moderate","تدفق البيانات ... يفقد الحالات assigns omission directly to the flow in an awkward way; state that relevant cases may be absent from the abundant stream while preserving the lexical targets."),("answer q10","naturalness_idiomaticity","moderate","تقابل قرار ... بحكم is awkward for the discourse function of لكن; the passage separates action thresholds from epistemic confidence rather than pairing one decision with another.")],
}
def sha(b): return hashlib.sha256(b).hexdigest()
def wc(t): return len(TOKEN.findall(t))
def targets(r):
 forms=[]
 for field in ('new_lexical_targets','review_lexical_targets'):
  for x in r.get(field,[]):
   f=x.get('form')
   if isinstance(f,str) and f and f not in forms: forms.append(f)
 text=r.get('text',''); return {f:text.count(f) for f in forms}
def main():
 raw=PATH.read_bytes(); pre=sha(raw); rel=json.loads(RELEASE.read_text()); ar=rel['languages']['arabic']; p=ar['naturalness_review_progress']
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False: raise SystemExit('Arabic release gate drift')
 if p.get('fresh_records_reviewed')!=264 or p.get('levels_completed')!=['A1','A2','B1','B2']: raise SystemExit('C1 Unit 5 progress frontier drift')
 if not (DD/'c1_u04.json').exists() or (DD/'c1_u05.json').exists(): raise SystemExit('C1 Unit 5 decision frontier drift')
 inv=json.loads(INVENTORY.read_text()); c1=inv.get('levels',{}).get('c1',{})
 if c1.get('canonical_sha256')!=pre or c1.get('fresh_review_status')!='IN_PROGRESS': raise SystemExit('C1 inventory/hash frontier drift')
 rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(24,30)]!=IDS: raise SystemExit('C1 Unit 5 layout/id drift')
 by={r['id']:r for r in rows}; before={pid:targets(by[pid]) for pid in IDS}
 for pid in IDS:
  r=by[pid]; q=r.get('quality',{})
  if q.get('status')!='draft' or q.get('coverage_check')!='pending' or any(q.get(f)!='pending' for f in ('linguistic_review','pedagogical_review','answer_key_check','schema_check')): raise SystemExit(f'{pid}: quality frontier drift')
  for old,new in TEXT_REPAIRS.get(pid,[]):
   if r.get('text','').count(old)!=1: raise SystemExit(f'{pid}: text source drift: {old!r}')
   r['text']=r['text'].replace(old,new,1)
  ans={a['question_id']:a for a in r.get('answer_key',[])}
  for qid,(old,new) in QA_REPAIRS.get(pid,{}).get('answers',{}).items():
   if qid not in ans or ans[qid].get('answer')!=old: raise SystemExit(f'{pid}/{qid}: answer drift')
   ans[qid]['answer']=new
  r['word_count']=wc(r['text'])
  if not 500<=r['word_count']<=800: raise SystemExit(f"{pid}: word count {r['word_count']} outside C1 band")
  if targets(r)!=before[pid]: raise SystemExit(f'{pid}: lexical target occurrence drift')
  if len(r.get('questions',[]))!=10 or len(r.get('answer_key',[]))!=10: raise SystemExit(f'{pid}: 10Q/10A invariant failed')
  aid={a['id']:a for a in r['answer_key']}
  for question in r['questions']:
   a=question.get('answer_id')
   if a not in aid or aid[a].get('question_id')!=question.get('id'): raise SystemExit(f"{pid}: answer linkage drift at {question.get('id')}")
  r['revision']=int(r.get('revision',0) or 0)+1; q=r.setdefault('quality',{})
  for f in ('linguistic_review','pedagogical_review','answer_key_check','schema_check'): q[f]='pass'
  if NOTE not in q.setdefault('notes',[]): q['notes'].append(NOTE)
 total=sum(len(FINDING_META[x]) for x in IDS); withf=sum(bool(FINDING_META[x]) for x in IDS)
 if (total,withf)!=(5,3): raise SystemExit(f'finding metadata drift: {total}/{withf}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows))
 print(json.dumps({'level':'C1','unit':5,'records_reviewed':6,'records_with_findings':withf,'fresh_findings':total,'pre_repair_canonical_sha256':pre,'post_repair_canonical_sha256':sha(PATH.read_bytes())},ensure_ascii=False,indent=2))
if __name__=='__main__': main()

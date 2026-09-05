#!/usr/bin/env python3
"""Apply fresh Arabic Gate B C1 Unit 10 assessment/naturalness repairs."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; R=ROOT/'reading'; PATH=R/'arabic/c1/passages.jsonl'; RELEASE=R/'RELEASE_STATUS.json'; INV=R/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; DD=R/'audit/arabic_gate_b_decisions_2026-08-30'
IDS=[f'ar-c1-u10-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-04 fresh Gate B naturalness review (C1 Unit 10): learner-facing prose/Q/A reviewed passage by passage; only high-confidence MSA naturalness, semantic, reference, and assessment-wording repairs applied; no educator/publication release claim.'
REPAIRS={
'ar-c1-u10-p01':[('answer q1','فصل ما تثبته الدراسة عن ما يضيفه الحكم المهني والأهداف المؤسسية.','القضية هي ضرورة الفصل بين ما تثبته الدراسة وما يضيفه الحكم المهني والأهداف المؤسسية عند الانتقال من الدليل إلى التوصية.','assessment_wording')],
'ar-c1-u10-p02':[('answer q1','لأن الموظفين تعلموا تجنب الكلمات المقاسة لا حل مشكلة الفهم.','القضية هي أن قياس وضوح التواصل بعدد الكلمات الرسمية قد يدفع الموظفين إلى تحسين المؤشر بدل تحسين الفهم، لذلك يجب ربط القياس بقدرة المستخدم الفعلية على تنفيذ المطلوب.','assessment_wording')],
'ar-c1-u10-p03':[('answer q2','تفتيش الأجهزة التي تظهر فيها الإشارة مع مراجعة قريبة.','تفتيش الأجهزة التي تظهر فيها الإشارة، مع تحديد مهلة قصيرة للمراجعة.','naturalness')],
'ar-c1-u10-p04':[('answer q1','أن نتيجة حالة واحدة تعيد تفسير قرار كان محفوفًا ببدائل ومخاطر لم تكن معلومة مسبقًا.','القضية هي أن نجاح حالة واحدة بعد وقوعها قد يجعل قرارًا سابقًا يبدو حتميًا أو أفضل مما كان تحت البدائل والمخاطر التي كانت معلومة وقت الاختيار.','assessment_wording')],
'ar-c1-u10-p05':[('answer q1','اختيار عناصر محدودة وجعلها تمثل تاريخ المؤسسة أو أداءها كله.','القضية هي أن المؤسسة قد تعيد بناء تاريخها أو أداءها من عناصر محدودة فتجعل جزءًا ممثلًا للكل، لذلك يجب إظهار تغير الأهداف والمقاييس وما تُرك خارج الإطار.','assessment_wording')],
'ar-c1-u10-p06':[('answer q1','رسم خريطة الحجة وفصل مستوياتها قبل إصدار حكم قابل للمراجعة.','القضية هي أن القارئ المتقدم يرسم خريطة متعددة المستويات للحجة، ويفصل الدليل والتفسير والقيم والسلطة والسرد، ثم يصدر حكمًا قابلًا للمراجعة والتحديث.','assessment_wording')],
}
META={}
for pid,reps in REPAIRS.items():
 items=[]
 for field,_old,_new,dimension in reps:
  if dimension=='assessment_wording':
   rationale='The current q1 prompt requires a one-sentence summary, but this keyed response remains a noun/causal/subordinate fragment from the earlier task shape; replace it with a complete standalone summary while preserving the passage interpretation.'
  else:
   rationale='The phrase «مراجعة قريبة» is an awkward and temporally imprecise rendering of the passage’s explicit short review window; state the short review deadline directly.'
  items.append((field,dimension,'moderate',rationale))
 META[pid]=items
def sha(b): return hashlib.sha256(b).hexdigest()
def wc(t): return len(TOKEN.findall(t))
def targets(r):
 fs=[]
 for k in ('new_lexical_targets','review_lexical_targets'):
  for x in r.get(k,[]):
   f=x.get('form')
   if isinstance(f,str) and f and f not in fs: fs.append(f)
 t=r.get('text',''); return {f:t.count(f) for f in fs}
def main():
 raw=PATH.read_bytes(); pre=sha(raw); rel=json.loads(RELEASE.read_text()); ar=rel['languages']['arabic']; p=ar['naturalness_review_progress']; d=ar['latest_deterministic_gate']
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False: raise SystemExit('release gate drift')
 if (p.get('fresh_records_reviewed'),p.get('fresh_records_with_findings'),p.get('fresh_findings'),d.get('open_findings'))!=(294,247,476,1344) or p.get('levels_completed')!=['A1','A2','B1','B2']: raise SystemExit('C1 Unit 10 frontier drift')
 if not (DD/'c1_u09.json').exists() or (DD/'c1_u10.json').exists(): raise SystemExit('decision frontier drift')
 inv=json.loads(INV.read_text()); c1=inv.get('levels',{}).get('c1',{})
 if c1.get('canonical_sha256')!=pre or c1.get('fresh_review_status')!='IN_PROGRESS': raise SystemExit('inventory/hash frontier drift')
 rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]
 if len(rows)!=60 or [rows[i].get('id') for i in range(54,60)]!=IDS: raise SystemExit('C1 Unit 10 layout drift')
 by={r['id']:r for r in rows}; before={pid:targets(by[pid]) for pid in IDS}
 for pid in IDS:
  r=by[pid]; q=r.get('quality',{})
  if q.get('status')!='draft' or q.get('coverage_check')!='pending' or any(q.get(f)!='pending' for f in ('linguistic_review','pedagogical_review','answer_key_check','schema_check')): raise SystemExit(f'{pid}: quality frontier drift')
  qs={x['id']:x for x in r.get('questions',[])}; ans={a['question_id']:a for a in r.get('answer_key',[])}
  if qs.get('q1',{}).get('type')!='summary' or qs.get('q1',{}).get('prompt')!='لخّص في جملة واحدة القضية المركزية التي يعالجها النص.': raise SystemExit(f'{pid}: q1 summary prompt drift')
  for field,old,new,_dim in REPAIRS[pid]:
   qid=field.split()[-1]
   if ans.get(qid,{}).get('answer')!=old: raise SystemExit(f'{pid}/{qid}: answer drift')
   ans[qid]['answer']=new
  r['word_count']=wc(r['text'])
  if not 500<=r['word_count']<=800: raise SystemExit(f'{pid}: word band drift')
  if targets(r)!=before[pid]: raise SystemExit(f'{pid}: lexical target drift')
  if len(r.get('questions',[]))!=10 or len(r.get('answer_key',[]))!=10: raise SystemExit(f'{pid}: 10Q/10A invariant failed')
  aid={a['id']:a for a in r['answer_key']}
  for qq in r['questions']:
   a=qq.get('answer_id')
   if a not in aid or aid[a].get('question_id')!=qq.get('id'): raise SystemExit(f'{pid}: answer linkage drift')
  r['revision']=int(r.get('revision',0) or 0)+1; q=r.setdefault('quality',{})
  for f in ('linguistic_review','pedagogical_review','answer_key_check','schema_check'): q[f]='pass'
  if NOTE not in q.setdefault('notes',[]): q['notes'].append(NOTE)
 if (sum(len(META[x]) for x in IDS),sum(bool(META[x]) for x in IDS))!=(6,6): raise SystemExit('finding metadata drift')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows))
 print(json.dumps({'level':'C1','unit':10,'records_reviewed':6,'records_with_findings':6,'fresh_findings':6,'pre_repair_canonical_sha256':pre,'post_repair_canonical_sha256':sha(PATH.read_bytes())},ensure_ascii=False,indent=2))
if __name__=='__main__': main()

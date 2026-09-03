#!/usr/bin/env python3
"""Apply fresh Arabic Gate B B1 Unit 9 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/b1/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; RELEASE=READING/'RELEASE_STATUS.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'
EXPECTED_IDS=[f'ar-b1-u09-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-03 fresh Gate B naturalness review (B1 Unit 9): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied where needed; legitimate B1 grammar-in-context analysis retained; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-b1-u09-p02':[
  ('هل لدى الجهة معلومات كافية لتعرف المهمة؟ ومتى يصبح إصلاحها ضمن واجبها التشغيلي بعد التسجيل؟','هل لدى الجهة معلومات كافية لتعرف المهمة؟ ومتى يصبح تنفيذ الإصلاح ضمن واجبها التشغيلي بعد التسجيل؟'),
 ],
}
QA_REPAIRS={
 'ar-b1-u09-p03':{'answers':{
  'q1':('لأن أعداد المتقدمين والبدائل تختلف، فينتج عن المساواة العددية فرص وحاجات مختلفة.','لأن أعداد المتقدمين والحاجة إلى البدائل تختلف، فيجعل التوزيع العددي المتساوي فرص الحصول على مقعد مختلفة.'),
  'q4':('يجعل معدل فرصة المقعد مختلفًا رغم تساوي عدد المقاعد بين الأحياء.','يجعل فرصة الحصول على مقعد مختلفة رغم تساوي عدد المقاعد بين الأحياء.'),
  'q10':('نسبة أو قيمة تلخص مقدارًا بالنسبة إلى عدد أو فترة.','نسبة تعبّر عن مقدار شيء مقارنة بعدد كلي أو خلال فترة محددة.'),
 }},
 'ar-b1-u09-p04':{'questions':{
  'q3':('لماذا لا يكون انخفاض سرعة الموقع هو الحل المطلوب؟','لماذا لا تكون زيادة سرعة الموقع هي الحل المطلوب؟'),
 }},
}
FINDING_META={
 'ar-b1-u09-p01':[],
 'ar-b1-u09-p02':[
  ('text','reference_clarity','moderate','Make the institutional duty refer explicitly to carrying out the repair rather than ambiguously to repairing the task itself.'),
 ],
 'ar-b1-u09-p03':[
  ('answer q1','semantic_precision','moderate','Equal numerical allocation changes the opportunity to obtain a seat; it does not itself create different underlying needs.'),
  ('answer q4','answer_wording','minor','Use the direct expression فرصة الحصول على مقعد rather than the awkward معدل فرصة المقعد.'),
  ('answer q10','semantic_precision','minor','Define معدل as a ratio or measure relative to a total or time period rather than the vague مقدار بالنسبة إلى عدد أو فترة.'),
 ],
 'ar-b1-u09-p04':[
  ('question q3','assessment_clarity','moderate','The intended contrast is that increasing site speed would not solve the comprehension problem; asking why decreasing speed is not the solution makes the item trivial and reverses the design.'),
 ],
 'ar-b1-u09-p05':[],
 'ar-b1-u09-p06':[],
}
def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def wc(text:str)->int:return len(TOKEN.findall(text))
def target_counts(r):
 text=str(r.get('text','')).casefold(); out={}
 for t in r.get('new_lexical_targets',[]):
  form=str(t.get('form','')).strip()
  if not form: raise SystemExit(f"{r['id']}: blank target")
  out[str(t.get('id',form))]=text.count(form.casefold())
 return out
def replace_once(text,old,new,label):
 c=text.count(old)
 if c!=1: raise SystemExit(f'{label}: expected literal once, found {c}: {old}')
 return text.replace(old,new,1)
def main():
 raw=PATH.read_bytes(); actual=sha(raw)
 inv=json.loads(INVENTORY.read_text(encoding='utf-8')); b1=inv.get('levels',{}).get('b1',{}); bound=b1.get('canonical_sha256')
 if not isinstance(bound,str) or len(bound)!=64 or actual!=bound: raise SystemExit(f'B1 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 9 review')
 rel=json.loads(RELEASE.read_text(encoding='utf-8')); ar=rel.get('languages',{}).get('arabic',{}); prog=ar.get('naturalness_review_progress',{})
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False or prog.get('fresh_records_reviewed')!=168 or prog.get('levels_completed')!=['A1','A2']: raise SystemExit('Arabic Gate B frontier drift: expected 168 reviewed with A1/A2 complete and B1 Unit 9 next')
 if not (DECISION_DIR/'b1_u08.json').exists() or (DECISION_DIR/'b1_u09.json').exists(): raise SystemExit('B1 decision frontier drift: Unit 8 must exist and Unit 9 must not')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(48,54)]!=EXPECTED_IDS: raise SystemExit('B1 Unit 9 layout/id drift')
 by={r['id']:r for r in rows}; before={pid:target_counts(by[pid]) for pid in EXPECTED_IDS}
 for pid in EXPECTED_IDS:
  r=by[pid]; text=r['text']
  for old,new in TEXT_REPAIRS.get(pid,[]): text=replace_once(text,old,new,f'{pid} text')
  r['text']=text; qs={q['id']:q for q in r.get('questions',[])}; aa={a['question_id']:a for a in r.get('answer_key',[])}; edits=QA_REPAIRS.get(pid,{})
  for qid,(old,new) in edits.get('questions',{}).items():
   if qs[qid].get('prompt')!=old: raise SystemExit(f'{pid}/{qid}: question drift: {qs[qid].get("prompt")!r}')
   qs[qid]['prompt']=new
  for qid,(old,new) in edits.get('answers',{}).items():
   if aa[qid].get('answer')!=old: raise SystemExit(f'{pid}/{qid}: answer drift: {aa[qid].get("answer")!r}')
   aa[qid]['answer']=new
  r['word_count']=wc(r['text'])
  if not 220<=r['word_count']<=350: raise SystemExit(f"{pid}: word count {r['word_count']} outside B1 band")
  if target_counts(r)!=before[pid]: raise SystemExit(f'{pid}: lexical target occurrence drift')
  if len(r.get('questions',[]))!=10 or len(r.get('answer_key',[]))!=10: raise SystemExit(f'{pid}: 10Q/10A invariant failed')
  ans_by_id={a['id']:a for a in r['answer_key']}
  for q in r['questions']:
   a=ans_by_id.get(q.get('answer_id'))
   if not a or a.get('question_id')!=q.get('id'): raise SystemExit(f"{pid}/{q.get('id')}: answer linkage drift")
  r['revision']=int(r.get('revision',0) or 0)+1; quality=r.setdefault('quality',{})
  if quality.get('status')!='draft' or quality.get('coverage_check')!='pending': raise SystemExit(f'{pid}: unexpected release/coverage state')
  for field in ('linguistic_review','pedagogical_review','answer_key_check','schema_check'): quality[field]='pass'
  if NOTE not in quality.setdefault('notes',[]): quality['notes'].append(NOTE)
 total=sum(len(FINDING_META[p]) for p in EXPECTED_IDS)
 if total!=5 or sum(bool(FINDING_META[p]) for p in EXPECTED_IDS)!=3: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'B1','unit':9,'records_reviewed':6,'records_with_findings':3,'fresh_findings':total,'pre_repair_canonical_sha256':actual,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

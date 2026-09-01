#!/usr/bin/env python3
"""Apply fresh Arabic Gate B A2 Unit 8 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/a2/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; RELEASE=READING/'RELEASE_STATUS.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'
EXPECTED_IDS=[f'ar-a2-u08-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-01 fresh Gate B naturalness review (A2 Unit 8): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-a2-u08-p01':[
  ('أثناء العمل لاحظوا أن معظم النفايات كانت قريبة من مكان لا توجد فيه سلة واضحة.', 'أثناء العمل لاحظوا أن معظم النفايات كانت قريبة من مكان لا توجد فيه سلة نفايات قريبة.'),
  ('وافق المشرف وقال إن النشاط البيئي الجيد لا يكتفي بإزالة ما نراه؛ يحاول أيضًا فهم لماذا ظهر في هذا المكان.', 'وافق المشرف وقال إن النشاط البيئي الجيد لا يكتفي بإزالة ما نراه؛ بل يحاول أيضًا فهم سبب ظهور المشكلة في هذا المكان.'),
 ],
 'ar-a2-u08-p04':[
  ('بعد ليلة كثيرة الرياح ذهبت نور مع أسرتها إلى شاطئ قريب من البحر.', 'بعد ليلة شديدة الرياح ذهبت نور مع أسرتها إلى شاطئ قريب من البحر.'),
 ],
}
QA_REPAIRS={
 'ar-a2-u08-p01':{'answers':{
  'q4':('الأنواع التي صُنعت منها الأشياء مثل الورق والبلاستيك والمعدن.','المواد التي تتكوّن منها الأشياء، مثل الورق والبلاستيك والمعدن.'),
 }},
 'ar-a2-u08-p02':{'answers':{
  'q3':('الطريقة والقدر الذي تُستهلك به الكهرباء في الإضاءة والأجهزة وغيرها.','مقدار الكهرباء المستعملة وكيفية استعمالها في الإضاءة والأجهزة وغيرها.'),
  'q4':('القدرة التي تشغل الإضاءة والتدفئة والأجهزة الكهربائية.','ما تحتاج إليه الإضاءة والتدفئة والأجهزة الكهربائية لكي تعمل.'),
 }},
 'ar-a2-u08-p05':{
  'questions':{'q7':('إلى ماذا تشير «معلوماتها» في الجملة الأخيرة تقريبًا؟','إلى ماذا تشير «معلوماتها» في قول المدير «أن تبقى معلوماتها صحيحة ومفيدة»؟')},
  'answers':{
   'q1':('إنشاء خريطة بيئية عملية يستفيد منها سكان المجتمع في حياتهم اليومية.','إنشاء خريطة بيئية عملية يستفيد منها سكان المنطقة في حياتهم اليومية.'),
   'q3':('مجموعة السكان والأشخاص الذين يعيشون ويستخدمون الخدمات في المنطقة.','الأشخاص الذين يعيشون في المنطقة ويستخدمون خدماتها.'),
  },
 },
 'ar-a2-u08-p06':{'answers':{
  'q2':('تمييز الاستخدام الضروري من الاستخدام الذي يعمل بلا فائدة.','تمييز الاستخدام الضروري من الاستخدام غير الضروري.'),
 }},
}
FINDING_META={
 'ar-a2-u08-p01':[
  ('text','naturalness_idiomaticity','minor','Replace the vague سلة واضحة with the intended concrete object سلة نفايات.'),
  ('text','reference_clarity','minor','Replace the vague لماذا ظهر with an explicit reference to the environmental problem appearing in that location.'),
  ('answer q4','semantic_precision','minor','Define materials as what objects are made from, rather than as the types from which the objects were made.'),
 ],
 'ar-a2-u08-p02':[
  ('answer q3','grammar_wording','moderate','Replace the mismatched الطريقة والقدر الذي...به with a grammatically direct A2 definition of electricity use.'),
  ('answer q4','semantic_precision','minor','Define energy through what lighting, heating, and electrical devices need to operate rather than as an abstract القدرة.'),
 ],
 'ar-a2-u08-p03':[],
 'ar-a2-u08-p04':[
  ('text','naturalness_idiomaticity','minor','Replace ليلة كثيرة الرياح with the idiomatic ليلة شديدة الرياح.'),
 ],
 'ar-a2-u08-p05':[
  ('answer q1','answer_wording','minor','Avoid the redundant سكان المجتمع and identify the intended local users as سكان المنطقة.'),
  ('answer q3','answer_wording','minor','Remove the redundant مجموعة السكان والأشخاص and define المجتمع directly through people living in and using the area.'),
  ('question q7','assessment_clarity','moderate','Replace the vague الجملة الأخيرة تقريبًا locator with the exact quoted phrase containing معلوماتها.'),
 ],
 'ar-a2-u08-p06':[
  ('answer q2','naturalness_idiomaticity','moderate','An استخدام does not itself يعمل; contrast necessary with unnecessary use directly.'),
 ],
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
 inv=json.loads(INVENTORY.read_text(encoding='utf-8')); a2=inv.get('levels',{}).get('a2',{}); bound=a2.get('canonical_sha256')
 if not isinstance(bound,str) or len(bound)!=64 or actual!=bound: raise SystemExit(f'A2 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 8 review')
 rel=json.loads(RELEASE.read_text(encoding='utf-8')); ar=rel.get('languages',{}).get('arabic',{}); prog=ar.get('naturalness_review_progress',{})
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False or prog.get('fresh_records_reviewed')!=102 or prog.get('levels_completed')!=['A1']: raise SystemExit('Arabic Gate B frontier drift: expected 102 reviewed with A1 complete and A2 Unit 8 next')
 if not (DECISION_DIR/'a2_u07.json').exists() or (DECISION_DIR/'a2_u08.json').exists(): raise SystemExit('A2 decision frontier drift: Unit 7 must exist and Unit 8 must not')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(42,48)]!=EXPECTED_IDS: raise SystemExit('A2 Unit 8 layout/id drift')
 by={r['id']:r for r in rows}; before={pid:target_counts(by[pid]) for pid in EXPECTED_IDS}
 for pid in EXPECTED_IDS:
  r=by[pid]; text=r['text']
  for old,new in TEXT_REPAIRS.get(pid,[]): text=replace_once(text,old,new,f'{pid} text')
  r['text']=text; qs={q['id']:q for q in r.get('questions',[])}; aa={a['question_id']:a for a in r.get('answer_key',[])}; edits=QA_REPAIRS.get(pid,{})
  for qid,(old,new) in edits.get('questions',{}).items():
   if qs[qid].get('prompt')!=old: raise SystemExit(f'{pid}/{qid}: question drift')
   qs[qid]['prompt']=new
  for qid,(old,new) in edits.get('answers',{}).items():
   if aa[qid].get('answer')!=old: raise SystemExit(f'{pid}/{qid}: answer drift')
   aa[qid]['answer']=new
  r['word_count']=wc(r['text'])
  if not 140<=r['word_count']<=220: raise SystemExit(f"{pid}: word count {r['word_count']} outside A2 band")
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
 if total!=10: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'A2','unit':8,'records_reviewed':6,'records_with_findings':5,'fresh_findings':total,'pre_repair_canonical_sha256':actual,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Apply fresh Arabic Gate B B1 Unit 2 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/b1/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; RELEASE=READING/'RELEASE_STATUS.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'
EXPECTED_IDS=[f'ar-b1-u02-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-01 fresh Gate B naturalness review (B1 Unit 2): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied where needed; legitimate B1 grammar-in-context analysis retained; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-b1-u02-p01':[
  ('الفرق بين الشخص الذي يظهر عنده الخطأ والسبب الذي جعل الخطأ ممكنًا أصلًا.', 'الفرق بين الشخص الذي يبدو أن الخطأ مرتبط به والسبب الذي جعل الخطأ ممكنًا أصلًا.'),
 ],
 'ar-b1-u02-p04':[
  ('قررت أن تكتب في ذهنها احتمالين على الأقل عندما لا تعرف سبب قرار ما:', 'قررت أن تضع في ذهنها احتمالين على الأقل عندما لا تعرف سبب قرار ما:'),
 ],
 'ar-b1-u02-p05':[
  ('كان التغيير الحقيقي في تصميم النشاط، لا في عنوانه فقط.', 'كان التغيير الحقيقي في تصميم النشاط، لا في مكانه فقط.'),
 ],
}
QA_REPAIRS={
 'ar-b1-u02-p01':{
  'questions':{'q2':('متى كان سامر قد كتب الجزء؟','منذ متى كان الجزء مكتوبًا؟')},
 },
 'ar-b1-u02-p02':{
  'questions':{
   'q8':('ما وظيفة «إذا» في فكرة أن جمع المعلومات يسمح باختيار تعديل أدق؟','ما وظيفة «إذا» في قول النص إن كلمة «حل» قد تكون مضللة «إذا فهمناها كشيء ينهي المشكلة فورًا»؟'),
   'q10':('لماذا لا يشترط النص اختفاء كل الزحمة لاعتبار التعديل أفضل؟','لماذا لا يشترط النص اختفاء الازدحام تمامًا لاعتبار التعديل أفضل؟'),
  },
  'answers':{'q8':('تربط تحقق شرط، وهو جمع معلومات كافية، بالقدرة على اتخاذ تعديل أدق.','تربط «إذا» الحكم بأن كلمة «حل» قد تكون مضللة بشرط فهمها كشيء ينهي المشكلة فورًا.')},
 },
 'ar-b1-u02-p03':{
  'questions':{'q7':('ما وظيفة «لكن» في قول النص إن العبارتين صحيحتان لغويًا لكن مرجعهما مختلف؟','ما وظيفة «لكن» في قول نور: «الكلمتان واضحتان، لكن المرجع ليس واضحًا»؟')},
  'answers':{'q7':('توضح تعارضًا بين صحة الصياغة اللغوية وعدم كفاية المرجع المشترك لفهمها.','تستدرك على وضوح الكلمتين لتبين أن وضوح الألفاظ لا يكفي إذا كان المرجع نفسه غامضًا.')},
 },
 'ar-b1-u02-p04':{
  'questions':{'q8':('ما وظيفة «لو» في الفكرة التي تتخيل اعتراض مريم قبل أن تسأل عن السبب؟','ما وظيفة «بل» في قول النص: «بل أن تعرف أولًا ما الذي تعترض عليه»؟')},
  'answers':{'q8':('تبني حالة افتراضية مخالفة لما حدث لتوضيح نتيجة ممكنة لو تصرفت مريم مبكرًا.','تصحح الفكرة السابقة: المقصود ليس تجاهل الشعور أو ترك الاعتراض، بل معرفة سبب الاعتراض أولًا.')},
 },
 'ar-b1-u02-p05':{
  'questions':{
   'q6':('ما الفرق بين تغيير العنوان وتغيير التصميم؟','ما الفرق بين تغيير المكان وتغيير التصميم؟'),
   'q7':('ما وظيفة «بدل» في انتقال النص من النقل المباشر إلى إعادة تصميم البرنامج؟','ما وظيفة «بدل» في عبارة «استخدام لوحة واحدة بدل لوحتين»؟'),
  },
  'answers':{'q7':('تقدم خيارًا بديلًا يحل محل الخطة التي لا تناسب المكان الجديد.','تدل على الاستبدال: اختارت كل مجموعة لوحة واحدة مكان لوحتين لتقليل المساحة المطلوبة.')},
 },
}
FINDING_META={
 'ar-b1-u02-p01':[
  ('text','naturalness_idiomaticity','moderate','Replace the awkward الشخص الذي يظهر عنده الخطأ with a natural formulation that says the error appears associated with the person.'),
  ('question q2','assessment_grounding','minor','Ask directly since when the part had been written so the wording aligns with the passage and the answer منذ عصر السبت.'),
 ],
 'ar-b1-u02-p02':[
  ('question/answer q8','assessment_grounding','moderate','The original q8 analyzed an implicit conditional about information gathering that is not stated with إذا. Rebind it to the passage’s exact إذا clause about understanding حل as something that ends a problem immediately.'),
  ('question q10','register','minor','Replace colloquial الزحمة with standard MSA الازدحام in the learner-facing question.'),
 ],
 'ar-b1-u02-p03':[
  ('question/answer q7','assessment_grounding','moderate','The original q7 paraphrased a contrast not quoted in the passage. Rebind لكن to Noor’s exact sentence الكلمتان واضحتان، لكن المرجع ليس واضحًا.'),
 ],
 'ar-b1-u02-p04':[
  ('text','naturalness_idiomaticity','minor','Replace تكتب في ذهنها with the idiomatic تضع في ذهنها for keeping alternative explanations in mind.'),
  ('question/answer q8','assessment_grounding','moderate','The original q8 analyzed لو although لو does not occur in the passage. Rebind the grammar-in-context task to the exact corrective بل construction.'),
 ],
 'ar-b1-u02-p05':[
  ('text/question q6','semantic_alignment','moderate','The intended contrast is changing the event’s place versus redesigning it, not changing its title/address. Repair عنوانه/العنوان to مكانه/المكان.'),
  ('question/answer q7','assessment_grounding','minor','Ground بدل in the exact phrase استخدام لوحة واحدة بدل لوحتين and explain its substitution function.'),
 ],
 'ar-b1-u02-p06':[],
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
 if not isinstance(bound,str) or len(bound)!=64 or actual!=bound: raise SystemExit(f'B1 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 2 review')
 rel=json.loads(RELEASE.read_text(encoding='utf-8')); ar=rel.get('languages',{}).get('arabic',{}); prog=ar.get('naturalness_review_progress',{})
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False or prog.get('fresh_records_reviewed')!=126 or prog.get('levels_completed')!=['A1','A2']: raise SystemExit('Arabic Gate B frontier drift: expected 126 reviewed with A1/A2 complete and B1 Unit 2 next')
 if not (DECISION_DIR/'b1_u01.json').exists() or (DECISION_DIR/'b1_u02.json').exists(): raise SystemExit('Gate B decision frontier drift: B1 Unit 1 must exist and B1 Unit 2 must not')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(6,12)]!=EXPECTED_IDS: raise SystemExit('B1 Unit 2 layout/id drift')
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
  if not 240<=r['word_count']<=340: raise SystemExit(f"{pid}: word count {r['word_count']} outside guarded B1 Unit 2 band")
  if target_counts(r)!=before[pid]: raise SystemExit(f'{pid}: new lexical target occurrence drift')
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
 if total!=9: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'B1','unit':2,'records_reviewed':6,'records_with_findings':5,'fresh_findings':total,'pre_repair_canonical_sha256':actual,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

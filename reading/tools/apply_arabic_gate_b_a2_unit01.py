#!/usr/bin/env python3
"""Apply fresh Arabic Gate B A2 Unit 1 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/a2/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; RELEASE=READING/'RELEASE_STATUS.json'
EXPECTED_IDS=[f'ar-a2-u01-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-01 fresh Gate B naturalness review (A2 Unit 1): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-a2-u01-p01':[
  ('عندما أعرف الشارع والخدمة التي يقدمها كل مكان، يصبح الحي الجديد أقل غربة.', 'عندما أعرف الشارع وأعرف الخدمة التي يقدمها كل مكان، يصبح الحي الجديد أقل غربة.'),
 ],
 'ar-a2-u01-p02':[
  ('اتصل بالهاتف، فسمع رسالة مسجلة', 'استخدم الهاتف للاتصال، فسمع رسالة مسجلة'),
 ],
 'ar-a2-u01-p04':[
  ('أنهت المعاملة وقدمت لهما الورقة المطلوبة.', 'أنهت الموظفة المعاملة وقدمت لهما الورقة المطلوبة.'),
 ],
}
QA_REPAIRS={
 'ar-a2-u01-p01':{'answers':{
  'q4':('مساعدة أو عمل يقدمه المركز للناس لتلبية حاجة عملية.','عمل أو مساعدة يقدمها مكان أو مؤسسة للناس.'),
 }},
 'ar-a2-u01-p03':{'answers':{
  'q3':('نص عام موضوع في المدخل لإبلاغ السكان بمعلومة مهمة.','نص معلّق عند المدخل لإبلاغ السكان بمعلومة مهمة.'),
  'q4':('معلومة مكتوبة ترسلها نور مباشرة إلى الجارة.','كلام مكتوب ترسله نور مباشرة إلى الجارة.'),
 }},
 'ar-a2-u01-p04':{'answers':{
  'q3':('الذهاب إلى المركز لغرض محدد ثم المغادرة بعد إنجازه.','الذهاب إلى المركز للقيام بأمر ثم العودة.'),
  'q8':('لأن المؤسسة فيها أقسام متعددة وقد يضيع الوقت إذا تحرك الشخص من دون ترتيب.','لأن المؤسسة فيها أقسام متعددة وقد يضيع الوقت إذا انتقل الشخص بينها من دون ترتيب.'),
 }},
 'ar-a2-u01-p05':{'answers':{
  'q3':('مجموعة منظمة من المنتجات والأسعار المعروضة للزبائن.','قائمة بأسماء المنتجات وأسعارها.'),
  'q5':('لأنها قديمة وقد تجعل الزبائن يحتارون بسبب اختلاف السعر.','لأنها غير محدّثة وقد تجعل الزبائن يحتارون بسبب اختلاف السعر.'),
 }},
 'ar-a2-u01-p06':{'answers':{
  'q5':('أصبحت تعرف طرقه وخدماته وكيف تحصل على المعلومات وتستخدم المؤسسات المحلية بفعالية.','أصبحت تعرف طرقه وخدماته وكيف تحصل على المعلومات وكيف تستخدم المؤسسات المحلية.'),
 }},
}
FINDING_META={
 'ar-a2-u01-p01':[
  ('text','naturalness_idiomaticity','minor','Avoid coordinating الشارع directly with the relative-clause service phrase; repeat أعرف for a natural parallel structure.'),
  ('answer q4','answer_wording','minor','Replace the abstract تلبية حاجة عملية service gloss with direct A2 learner-facing wording.'),
 ],
 'ar-a2-u01-p02':[
  ('text','naturalness_idiomaticity','moderate','Replace اتصل بالهاتف, which sounds like calling the phone itself, with استخدم الهاتف للاتصال.'),
 ],
 'ar-a2-u01-p03':[
  ('answer q3','naturalness_idiomaticity','minor','Use نص معلّق rather than the literal-sounding نص موضوع for a posted announcement.'),
  ('answer q4','semantic_precision','minor','Define رسالة قصيرة as written words sent directly, rather than as the information itself.'),
 ],
 'ar-a2-u01-p04':[
  ('text','reference_clarity','moderate','Name الموظفة explicitly as the subject who completes the transaction and gives the paper.'),
  ('answer q3','answer_wording','minor','Simplify the context definition of زيارة and avoid an unnecessarily narrow formal formulation.'),
  ('answer q8','naturalness_idiomaticity','minor','Use انتقل بين الأقسام rather than تحرك الشخص for navigating departments.'),
 ],
 'ar-a2-u01-p05':[
  ('answer q3','answer_wording','minor','Define قائمة الأسعار concretely as product names and their prices.'),
  ('answer q5','semantic_precision','minor','Describe the list as غير محدّثة rather than قديمة, which is the actual problem in context.'),
 ],
 'ar-a2-u01-p06':[
  ('answer q5','answer_wording','minor','Replace the abstract بفعالية summary with a direct statement that she knows how to use local institutions.'),
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
 if not isinstance(bound,str) or len(bound)!=64 or actual!=bound: raise SystemExit(f'A2 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 1 review')
 rel=json.loads(RELEASE.read_text(encoding='utf-8')); ar=rel.get('languages',{}).get('arabic',{}); prog=ar.get('naturalness_review_progress',{})
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False or prog.get('fresh_records_reviewed')!=60 or prog.get('levels_completed')!=['A1']: raise SystemExit('Arabic Gate B frontier drift: expected A1 complete and A2 Unit 1 next')
 if (READING/'audit/arabic_gate_b_decisions_2026-08-30/a2_u01.json').exists(): raise SystemExit('A2 Unit 1 decision artifact already exists; refusing duplicate review')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(0,6)]!=EXPECTED_IDS: raise SystemExit('A2 Unit 1 layout/id drift')
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
 if total!=11: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'A2','unit':1,'records_reviewed':6,'records_with_findings':6,'fresh_findings':total,'pre_repair_canonical_sha256':actual,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

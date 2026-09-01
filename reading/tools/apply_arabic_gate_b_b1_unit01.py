#!/usr/bin/env python3
"""Apply fresh Arabic Gate B B1 Unit 1 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/b1/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; RELEASE=READING/'RELEASE_STATUS.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'
EXPECTED_IDS=[f'ar-b1-u01-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-01 fresh Gate B naturalness review (B1 Unit 1): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied where needed; legitimate B1 grammar-in-context analysis retained; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-b1-u01-p02':[
  ('اقترحت أن يأخذوا جزء سامر نهائيًا ويكملوا المشروع بأنفسهم.', 'اقترحت أن يتولوا جزء سامر من العمل نهائيًا ويكملوا المشروع بأنفسهم.'),
 ],
 'ar-b1-u01-p06':[
  ('بعد ذلك تُقارن النتائج المحتملة والأولويات، ويُتخذ خيار يمكن مراجعته إذا ظهرت خبرة جديدة.', 'بعد ذلك تُقارن النتائج المحتملة والأولويات، ويُتخذ خيار يمكن مراجعته إذا اكتسب الشخص خبرة جديدة.'),
 ],
}
QA_REPAIRS={
 'ar-b1-u01-p01':{
  'questions':{'q7':('ما دلالة «حتى إن» في «حتى إن كانت الإجابة لا الآن»؟','ما دلالة «مع ذلك» في «أحيانًا يكون الشيء جيدًا، ومع ذلك لا يكون الخيار المناسب في الوقت الحالي»؟')},
  'answers':{'q7':('تفيد أن وضوح القرار يظل مهمًا حتى في الحالة التي تكون فيها النتيجة عدم التسجيل الآن.','تفيد أن كون الشيء جيدًا لا يمنع أن يكون غير مناسب في الوقت الحالي؛ فهي تقدم نتيجة تخالف التوقع الأول.')},
 },
 'ar-b1-u01-p03':{
  'questions':{'q7':('ما وظيفة «حتى» في «لا تحتاج دائمًا إلى كتابة أمثلة طويلة حتى تكون واضحة»؟','ما وظيفة «حتى» في «المهارة لا تحتاج دائمًا إلى وظيفة رسمية حتى تظهر»؟')},
  'answers':{'q7':('تربط طول الأمثلة بالغاية المطلوبة، وهي الوضوح، ثم ينفي النص أن الطول شرط دائم لتحقيقها.','تربط «حتى» هنا الوسيلة بالغاية: الوظيفة الرسمية ليست شرطًا لازمًا لكي تظهر المهارة.')},
 },
 'ar-b1-u01-p05':{'answers':{
  'q5':('بديل متاح يمكن اختياره بعد مقارنة فوائده وكلفه.','بديل متاح يمكن اختياره بعد مقارنة فوائده وتكاليفه.'),
 }},
 'ar-b1-u01-p06':{
  'questions':{
   'q5':('ماذا تعني «خبرة» في عبارة «إذا ظهرت خبرة جديدة»؟','ماذا تعني «خبرة» في عبارة «إذا اكتسب الشخص خبرة جديدة»؟'),
   'q9':('ما وظيفة «إذا» في فكرة مراجعة القرار «إذا ظهرت خبرة جديدة»؟','ما وظيفة «إذا» في فكرة مراجعة القرار «إذا اكتسب الشخص خبرة جديدة»؟'),
  },
  'answers':{
   'q5':('معلومة أو تجربة جديدة تكشف أثر القرار وتسمح بإعادة تقييمه.','تجربة أو معرفة جديدة يكتسبها الشخص وقد تساعده على إعادة تقييم القرار.'),
   'q9':('تجعل ظهور معلومات أو تجربة جديدة شرطًا لإعادة النظر في القرار.','تجعل اكتساب خبرة جديدة شرطًا محتملًا لإعادة النظر في القرار.'),
  },
 },
}
FINDING_META={
 'ar-b1-u01-p01':[
  ('question/answer q7','assessment_grounding','moderate','The original q7 quoted حتى إن كانت الإجابة لا الآن, a phrase that does not occur in the passage. Rebind the grammar-in-context item to the actual concessive phrase مع ذلك.'),
 ],
 'ar-b1-u01-p02':[
  ('text','naturalness_idiomaticity','minor','Replace يأخذوا جزء سامر with the idiomatic task-allocation wording يتولوا جزء سامر من العمل.'),
 ],
 'ar-b1-u01-p03':[
  ('question/answer q7','assessment_grounding','moderate','The original q7 quoted a sentence about writing long examples that is absent from the passage. Rebind حتى to the actual sentence about a skill appearing without a formal job.'),
 ],
 'ar-b1-u01-p04':[],
 'ar-b1-u01-p05':[
  ('answer q5','answer_wording','minor','Use the unambiguous تكاليفه rather than the undiacritized كلفه in the learner-facing definition of خيار.'),
 ],
 'ar-b1-u01-p06':[
  ('text','naturalness_idiomaticity','moderate','Replace the non-idiomatic إذا ظهرت خبرة جديدة with إذا اكتسب الشخص خبرة جديدة.'),
  ('question/answer q5,q9','assessment_alignment','minor','Align both assessment items and answers with the repaired phrase while preserving the intended vocabulary and conditional-in-context tasks.'),
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
 inv=json.loads(INVENTORY.read_text(encoding='utf-8')); b1=inv.get('levels',{}).get('b1',{}); bound=b1.get('canonical_sha256')
 if not isinstance(bound,str) or len(bound)!=64 or actual!=bound: raise SystemExit(f'B1 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 1 review')
 rel=json.loads(RELEASE.read_text(encoding='utf-8')); ar=rel.get('languages',{}).get('arabic',{}); prog=ar.get('naturalness_review_progress',{})
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False or prog.get('fresh_records_reviewed')!=120 or prog.get('levels_completed')!=['A1','A2']: raise SystemExit('Arabic Gate B frontier drift: expected 120 reviewed with A1/A2 complete and B1 Unit 1 next')
 if not (DECISION_DIR/'a2_u10.json').exists() or (DECISION_DIR/'b1_u01.json').exists(): raise SystemExit('Gate B decision frontier drift: A2 Unit 10 must exist and B1 Unit 1 must not')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(0,6)]!=EXPECTED_IDS: raise SystemExit('B1 Unit 1 layout/id drift')
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
  if not 240<=r['word_count']<=340: raise SystemExit(f"{pid}: word count {r['word_count']} outside guarded B1 Unit 1 band")
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
 if total!=6: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'B1','unit':1,'records_reviewed':6,'records_with_findings':5,'fresh_findings':total,'pre_repair_canonical_sha256':actual,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

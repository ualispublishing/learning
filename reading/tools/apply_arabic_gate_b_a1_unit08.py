#!/usr/bin/env python3
"""Apply fresh Arabic Gate B A1 Unit 8 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PATH=ROOT/'reading/arabic/a1/passages.jsonl'
EXPECTED_SHA256='811ec6d2ea83ecff7013caf03527bdb403a782bc7926ebe572e035f44ff75e80'
EXPECTED_IDS=[f'ar-a1-u08-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-08-31 fresh Gate B naturalness review (A1 Unit 8): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-a1-u08-p02':[('في اليوم التالي تشعر ليلى أفضل وتذهب إلى المدرسة.','في اليوم التالي تشعر ليلى بأنها أفضل وتذهب إلى المدرسة.')],
 'ar-a1-u08-p04':[('تسأل ليلى: هل كل شيء سالم؟ تقول الممرضة: هذا نشاط تعليمي بسيط، وأنت الآن مرتاحة.','تسأل ليلى: هل جسمي سالم بعد هذا النشاط؟ تقول الممرضة: نعم، أنت بخير الآن، وهذا نشاط تعليمي بسيط.')],
 'ar-a1-u08-p05':[('بهذه الطريقة لا أحول الراحة أو النشاط إلى مشكلة.','بهذه الطريقة أعود إلى النشاط بهدوء ولا أتعب نفسي.')],
 'ar-a1-u08-p06':[('وإذا كانت عندها حاجة إلى شيء تطلبه، وإذا كان العمل صعبًا تطلب مساعدة.','وإذا كانت في حاجة إلى شيء تطلبه، وإذا كان العمل صعبًا تطلب مساعدة.')],
}
QA_REPAIRS={
 'ar-a1-u08-p01':{'answers':{
  'q4':('حالة أو أمر غير جيد يحتاج إلى الانتباه.','شيء غير جيد يحتاج إلى الانتباه.'),
  'q7':('أمر صعب أو غير جيد يحتاج إلى حل أو انتباه.','شيء صعب يحتاج إلى حل أو انتباه.'),
 }},
 'ar-a1-u08-p02':{'answers':{
  'q4':('عمل يخفف المهمة عن شخص أو يعينه عليها.','أن يساعد شخصٌ شخصًا آخر في عمل.'),
  'q7':('عون يقدمه شخص لآخر.','أن يساعد شخصٌ شخصًا آخر.'),
 }},
 'ar-a1-u08-p03':{'answers':{
  'q4':('جزء الجسم الذي توجد فيه العينان والوجه.','الجزء الأعلى من الجسم، وفيه الوجه والعينان.'),
 }},
 'ar-a1-u08-p04':{'answers':{
  'q4':('غير متضرر أو بخير.','أن جسمها بخير ولم يصبه ضرر.'),
  'q7':('بخير أو غير مصاب بضرر.','بخير ولم يصبه ضرر.'),
 }},
 'ar-a1-u08-p05':{'answers':{
  'q3':('أقوم بمحاولة لفعل الشيء دون ضمان النتيجة.','أبدأ فعل شيء وأرى هل أستطيع.'),
 }},
}
FINDING_META={
 'ar-a1-u08-p01':[
  ('answer q4','answer_wording','minor','Simplify the contextual meaning of مشكلة for an A1 learner.'),
  ('answer q7','answer_wording','minor','Replace the abstract standalone definition of مشكلة with direct everyday wording.'),
 ],
 'ar-a1-u08-p02':[
  ('text','grammar_syntax','moderate','Repair تشعر ليلى أفضل to the grammatical تشعر ليلى بأنها أفضل.'),
  ('answer q4','answer_wording','minor','Explain مساعدة through a concrete person-helping-person action rather than abstract task language.'),
  ('answer q7','answer_wording','minor','Replace the formal عون يقدمه definition with direct A1 wording.'),
 ],
 'ar-a1-u08-p03':[
  ('answer q4','semantic_precision','minor','Describe the head as the upper body part with the face and eyes rather than saying the eyes and face are located inside it.'),
 ],
 'ar-a1-u08-p04':[
  ('text','naturalness_idiomaticity','moderate','Replace the vague هل كل شيء سالم with a body-specific question and a direct response.'),
  ('answer q4','semantic_precision','minor','Ground سالم in the body context rather than an unspecified object state.'),
  ('answer q7','answer_wording','minor','Simplify the standalone meaning of سالم while preserving the unharmed sense.'),
 ],
 'ar-a1-u08-p05':[
  ('text','naturalness_idiomaticity','minor','Replace the awkward claim about turning rest or activity into a problem with a natural gradual-return statement.'),
  ('answer q3','answer_wording','minor','Replace the abstract دون ضمان النتيجة definition of أحاول with direct A1 action wording.'),
 ],
 'ar-a1-u08-p06':[
  ('text','naturalness_idiomaticity','minor','Use the idiomatic في حاجة إلى construction in the cumulative passage.'),
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
 if actual!=EXPECTED_SHA256: raise SystemExit(f'A1 canonical drift: expected {EXPECTED_SHA256}, got {actual}; rebind Unit 8 review')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(42,48)]!=EXPECTED_IDS: raise SystemExit('A1 Unit 8 layout/id drift')
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
  if not 90<=r['word_count']<=140: raise SystemExit(f"{pid}: word count {r['word_count']} outside A1 band")
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
 if total!=12: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'A1','unit':8,'records_reviewed':6,'records_with_findings':6,'fresh_findings':total,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Apply fresh Arabic Gate B A1 Unit 10 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PATH=ROOT/'reading/arabic/a1/passages.jsonl'
EXPECTED_SHA256='ce323f03fa375291484645859848c00a85b6d83d8bf17ac7f498adf62300d1d3'
EXPECTED_IDS=[f'ar-a1-u10-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-01 fresh Gate B naturalness review (A1 Unit 10): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-a1-u10-p03':[
  ('عند نهاية الحديث يقول المعلم:', 'في نهاية الحديث يقول المعلم:'),
  ('نهاية اليوم يمكن أن تكون وقتًا صغيرًا لفهم ما حدث منذ الصباح.', 'نهاية اليوم يمكن أن تكون وقتًا قصيرًا لفهم ما حدث منذ الصباح.'),
 ],
 'ar-a1-u10-p04':[
  ('كنا جميعًا نضحك قبل أن نأخذ الصورة.', 'كنا جميعًا نضحك قبل أن نلتقط الصورة.'),
 ],
}
QA_REPAIRS={
 'ar-a1-u10-p01':{'answers':{
  'q3':('أن هذا هو ما تفعله عادة في كل مرة تقريبًا.','أنها تفعل هذا في كل مرة.'),
 }},
 'ar-a1-u10-p02':{'answers':{
  'q7':('غير مماثل أو غير نفسه.','ليس مثل شيء آخر.'),
 }},
 'ar-a1-u10-p03':{'answers':{
  'q7':('الجزء الأخير أو الوقت الذي ينتهي عنده الشيء.','الجزء الأخير من الشيء.'),
 }},
 'ar-a1-u10-p04':{'answers':{
  'q4':('تمثيل مرئي لشخص أو مكان أو لحظة.','شيء نراه لوجه أو مكان أو حدث، مثل صورة في الهاتف.'),
  'q7':('رسم أو لقطة مرئية لشيء أو شخص.','شيء نراه لشخص أو مكان، مثل صورة في الهاتف.'),
 }},
 'ar-a1-u10-p05':{'answers':{
  'q3':('ورقة أو جانب من أوراق الكتاب يحمل نصًا.','جزء من الكتاب نقرأ فيه الكلمات أو نرى فيه الصور.'),
 }},
 'ar-a1-u10-p06':{
  'questions':{
   'q10':('أيهما جزء من كتاب: «صفحة» أم «صورة» بالضرورة؟','أيهما جزء من الكتاب نفسه: «صفحة» أم «صورة»؟'),
  },
  'answers':{
   'q1':('ليلى تستطيع الآن قراءة موضوعات يومية كثيرة وفهمها على مستوى المستوى المبتدئ الأول.','ليلى تستطيع الآن قراءة موضوعات يومية كثيرة وفهمها في المستوى المبتدئ الأول.'),
   'q10':('صفحة هي جزء بنيوي من الكتاب؛ وقد توجد صورة داخلها.','الصفحة جزء من الكتاب، أما الصورة فقد توجد في الصفحة.'),
  },
 },
}
FINDING_META={
 'ar-a1-u10-p01':[
  ('answer q3','semantic_precision','minor','Define دائمًا as every time rather than weakening it to almost every time.'),
 ],
 'ar-a1-u10-p02':[
  ('answer q7','answer_wording','minor','Replace the awkward غير نفسه definition of مختلف with a direct A1 comparison meaning.'),
 ],
 'ar-a1-u10-p03':[
  ('text','naturalness_idiomaticity','minor','Use في نهاية الحديث rather than the less natural عند نهاية الحديث.'),
  ('text','naturalness_idiomaticity','minor','Replace وقتًا صغيرًا with the idiomatic وقتًا قصيرًا for a short period of time.'),
  ('answer q7','answer_wording','minor','Simplify the definition of نهاية to a direct A1 meaning.'),
 ],
 'ar-a1-u10-p04':[
  ('text','naturalness_idiomaticity','minor','Use نلتقط الصورة for taking a photograph rather than the literal نأخذ الصورة.'),
  ('answer q4','answer_wording','minor','Replace the abstract تمثيل مرئي definition of صورة with concrete A1 wording.'),
  ('answer q7','answer_wording','minor','Replace لقطة مرئية terminology with a concrete learner-facing definition of صورة.'),
 ],
 'ar-a1-u10-p05':[
  ('answer q3','semantic_precision','minor','Define صفحة as a part of a book rather than ambiguously as a sheet or side of a sheet.'),
 ],
 'ar-a1-u10-p06':[
  ('answer q1','grammar_wording','moderate','Remove the duplicated على مستوى المستوى phrase in the A1 cumulative gist answer.'),
  ('question q10','assessment_clarity','minor','Remove the awkward بالضرورة construction and ask the page-versus-image contrast directly.'),
  ('answer q10','answer_wording','minor','Replace the technical جزء بنيوي wording with a direct A1 explanation of a page.'),
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
 if actual!=EXPECTED_SHA256: raise SystemExit(f'A1 canonical drift: expected {EXPECTED_SHA256}, got {actual}; rebind Unit 10 review')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(54,60)]!=EXPECTED_IDS: raise SystemExit('A1 Unit 10 layout/id drift')
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
 print(json.dumps({'level':'A1','unit':10,'records_reviewed':6,'records_with_findings':6,'fresh_findings':total,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

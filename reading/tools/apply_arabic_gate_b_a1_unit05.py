#!/usr/bin/env python3
"""Apply fresh Arabic Gate B A1 Unit 5 naturalness/Q&A repairs."""
from __future__ import annotations

import hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'
EXPECTED_SHA256='6fc4f6a502fd0c89a91d50102c6144cc1e40a6b7b3cde2c1d12fd45136dbf281'
EXPECTED_IDS=[f'ar-a1-u05-p{i:02d}' for i in range(1,7)]
TOKEN=re.compile(r'\S+')
NOTE='2026-08-31 fresh Gate B naturalness review (A1 Unit 5): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied; no educator/publication release claim.'

TEXT_REPAIRS={
 'ar-a1-u05-p01':[
  ('تقول مريم: أحب أن يأتي المعلم في الوقت، لأن الدرس يبدأ بشكل منظم.','تقول مريم: أحب أن يأتي المعلم في الوقت، لأن الدرس يبدأ بطريقة منظمة.'),
 ],
 'ar-a1-u05-p03':[
  ('في حصة صغيرة يقسم المعلم الطلاب إلى مجموعات.','في حصة قصيرة يقسم المعلم الطلاب إلى مجموعات.'),
 ],
 'ar-a1-u05-p04':[
  ('يعمل النادي في غرفة صغيرة داخل المدرسة مرتين في الأسبوع.','يجتمع النادي في غرفة صغيرة داخل المدرسة مرتين في الأسبوع، ويعمل الطلاب هناك على أنشطة القراءة.'),
 ],
 'ar-a1-u05-p06':[
  ('في نهاية اليوم تعود ليلى إلى المنزل وهي تعرف ماذا بدأت، وماذا أنجزت، ومتى ستعود إلى المدرسة.','في نهاية اليوم تعود ليلى إلى المنزل وهي تعرف كيف بدأ يومها، وماذا أنجزت، ومتى ستعود إلى المدرسة.'),
 ],
}

QA_REPAIRS={
 'ar-a1-u05-p01':{'answers':{
  'q8':('يأتي يدل على المجيء أو الوصول، أما يعود فيدل على الرجوع.','يأتي يعني المجيء إلى المكان، ويعود يعني الرجوع إليه.'),
 }},
 'ar-a1-u05-p02':{'answers':{
  'q4':('أن الباب حاضر أو موجود في المكان.','أن هناك بابًا في المكان.'),
  'q7':('يكون حاضرًا أو موجودًا.','أن هناك شيئًا في المكان.'),
 }},
 'ar-a1-u05-p03':{'answers':{
  'q7':('في باطن المكان أو في جهته الداخلية.','في الجهة الداخلية من المكان.'),
 }},
 'ar-a1-u05-p04':{
  'questions':{
   'q2':('كم مرة يعمل النادي في الأسبوع؟','كم مرة يجتمع النادي في الأسبوع؟'),
  },
 },
 'ar-a1-u05-p05':{'answers':{
  'q6':('الأسبوع المقبل.','الأسبوع المقبل.'),
  'q7':('يرجع إلى المكان أو الحالة السابقة.','يرجع إلى مكان كان فيه من قبل.'),
 },'explanations':{
  'q6':('في هذا التعبير تأتي «المقبل» بعد «الأسبوع» وتوافقه في التعريف.','نقول «الأسبوع المقبل» عن الأسبوع الذي يأتي بعد هذا الأسبوع.'),
 }},
 'ar-a1-u05-p06':{
  'questions':{
   'q4':('إلى ماذا تشير «داخل الصفوف»؟','ماذا تعني «داخل» في «داخل الصفوف»؟'),
  },
  'answers':{
   'q4':('إلى المكان الموجود في الجهة الداخلية من الصفوف.','في الصفوف، لا خارجها.'),
   'q6':('يكون حاضرًا أو موجودًا.','أن هناك شيئًا في المكان.'),
  },
 },
}

FINDING_META={
 'ar-a1-u05-p01':[
  ('text','naturalness_idiomaticity','minor','Replace يبدأ بشكل منظم with the more natural بطريقة منظمة.'),
  ('answer q8','answer_wording','minor','Simplify the يأتي/يعود contrast for an A1 learner.'),
 ],
 'ar-a1-u05-p02':[
  ('answer q4','semantic_precision','moderate','Avoid describing an inanimate door as حاضر; express existence directly.'),
  ('answer q7','answer_wording','minor','Define يوجد through a concrete there-is meaning rather than حاضر/موجود wording.'),
 ],
 'ar-a1-u05-p03':[
  ('text','naturalness_idiomaticity','minor','Use حصة قصيرة for a short lesson rather than حصة صغيرة.'),
  ('answer q7','answer_wording','minor','Replace the formal باطن المكان definition with direct A1 wording.'),
 ],
 'ar-a1-u05-p04':[
  ('text','naturalness_idiomaticity','moderate','Use يجتمع for the club meeting while retaining the target يعمل in a natural student-activity clause.'),
  ('question q2','question_wording','minor','Ask how often the club meets rather than how often the club itself works.'),
 ],
 'ar-a1-u05-p05':[
  ('explanation q6','answer_wording','minor','Replace a formal agreement/definiteness explanation with a direct meaning-based explanation of الأسبوع المقبل.'),
  ('answer q7','answer_wording','minor','Define يعود with a concrete place-return meaning suitable for A1.'),
 ],
 'ar-a1-u05-p06':[
  ('text','naturalness_idiomaticity','minor','Replace ماذا بدأت with the natural phrase كيف بدأ يومها.'),
  ('question/answer q4','semantic_precision','moderate','Test the meaning of داخل directly instead of asking what the phrase داخل الصفوف refers to.'),
  ('answer q6','answer_wording','minor','Use the same concrete A1 existence meaning for يوجد in the cumulative passage.'),
 ],
}

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def wc(text:str)->int:return len(TOKEN.findall(text))
def target_counts(r:dict)->dict:
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
 if actual!=EXPECTED_SHA256: raise SystemExit(f'A1 canonical drift: expected {EXPECTED_SHA256}, got {actual}; rebind Unit 5 review')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)): raise SystemExit('A1 layout drift')
 if [rows[i].get('id') for i in range(24,30)]!=EXPECTED_IDS: raise SystemExit('A1 Unit 5 id/layout drift')
 by={r['id']:r for r in rows}; before={pid:target_counts(by[pid]) for pid in EXPECTED_IDS}
 for pid in EXPECTED_IDS:
  r=by[pid]; text=r['text']
  for old,new in TEXT_REPAIRS.get(pid,[]): text=replace_once(text,old,new,f'{pid} text')
  r['text']=text
  qs={q['id']:q for q in r.get('questions',[])}; aa={a['question_id']:a for a in r.get('answer_key',[])}
  edits=QA_REPAIRS.get(pid,{})
  for qid,(old,new) in edits.get('questions',{}).items():
   if qs[qid].get('prompt')!=old: raise SystemExit(f'{pid}/{qid}: question drift')
   qs[qid]['prompt']=new
  for qid,(old,new) in edits.get('answers',{}).items():
   if aa[qid].get('answer')!=old: raise SystemExit(f'{pid}/{qid}: answer drift')
   aa[qid]['answer']=new
  for qid,(old,new) in edits.get('explanations',{}).items():
   if aa[qid].get('explanation','')!=old: raise SystemExit(f'{pid}/{qid}: explanation drift')
   aa[qid]['explanation']=new
  r['word_count']=wc(r['text'])
  if not 90<=r['word_count']<=140: raise SystemExit(f"{pid}: word count {r['word_count']} outside A1 band")
  if target_counts(r)!=before[pid]: raise SystemExit(f'{pid}: lexical target occurrence drift')
  if len(r.get('questions',[]))!=10 or len(r.get('answer_key',[]))!=10: raise SystemExit(f'{pid}: 10Q/10A invariant failed')
  ans_by_id={a['id']:a for a in r['answer_key']}
  for q in r['questions']:
   a=ans_by_id.get(q.get('answer_id'))
   if not a or a.get('question_id')!=q.get('id'): raise SystemExit(f"{pid}/{q.get('id')}: answer linkage drift")
  r['revision']=int(r.get('revision',0) or 0)+1
  quality=r.setdefault('quality',{})
  if quality.get('status')!='draft' or quality.get('coverage_check')!='pending': raise SystemExit(f'{pid}: unexpected release/coverage state')
  for field in ('linguistic_review','pedagogical_review','answer_key_check','schema_check'): quality[field]='pass'
  notes=quality.setdefault('notes',[])
  if NOTE not in notes: notes.append(NOTE)
 total=sum(len(FINDING_META[p]) for p in EXPECTED_IDS)
 if total!=13: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'A1','unit':5,'records_reviewed':6,'records_with_findings':6,'fresh_findings':total,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__': main()

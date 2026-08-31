#!/usr/bin/env python3
"""Apply fresh Arabic Gate B A1 Unit 4 naturalness/Q&A repairs."""
from __future__ import annotations

import hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'
EXPECTED_SHA256='767ad84ec37e5cb074af91a3802e4b2a467f2c9d06f5a91d3fcf43a8b4ad3a35'
EXPECTED_IDS=[f'ar-a1-u04-p{i:02d}' for i in range(1,7)]
TOKEN=re.compile(r'\S+')
NOTE='2026-08-31 fresh Gate B naturalness review (A1 Unit 4): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied; no educator/publication release claim.'

TEXT_REPAIRS={
 'ar-a1-u04-p01':[
  ('تقول ليلى: في مرة أخرى سأريك صورة أكبر، لأن عندنا ناسًا كثيرين في العائلة.','تقول ليلى: في المرة القادمة سأريك صورة أكبر، لأن في عائلتنا أفرادًا كثيرين.'),
  ('وتذكر أنها قريبة لهم.','وتقول إنها من أقاربهم.'),
 ],
 'ar-a1-u04-p02':[
  ('تقول ليلى: هذه نور، وهي شخص جديد في صفنا.','تقول ليلى: هذه نور، وهي شخص جديد بيننا في الصف.'),
 ],
 'ar-a1-u04-p03':[
  ('في الداخل تجلس ابنة أمينة مع كتاب.','في الداخل تجلس ابنة أمينة وهي تقرأ كتابًا.'),
 ],
 'ar-a1-u04-p05':[
  ('تقول ليلى: نعم، كل شخص هنا قريب لنا.','تقول ليلى: نعم، كل شخص هنا من أقاربنا.'),
 ],
 'ar-a1-u04-p06':[
  ('في البيت تعرف أباها وأمها وأخاها، وتعرف أن سامر ابن أخيها.','في البيت تعيش مع أبيها وأمها وأخيها، وتعرف أن سامر ابن أخيها.'),
  ('وتسمع ما يقول الناس في الحديث.','وتستمع إلى ما يقوله الناس في الحديث.'),
 ],
}

QA_REPAIRS={
 'ar-a1-u04-p01':{'answers':{
  'q4':('ولد ذكر مرتبط بأبيه أو أمه؛ هنا هو ولد أخي ليلى.','ولد؛ وهنا هو ولد أخي ليلى.'),
  'q7':('الولد الذكر لشخص ما.','ولد لشخص ما.'),
 }},
 'ar-a1-u04-p02':{'answers':{
  'q3':('الكلمة التي يُعرَف بها الشخص.','ما نسمّي به الشخص.'),
 }},
 'ar-a1-u04-p03':{'answers':{
  'q4':('يتكلم بكلمات أو يخبر الآخرين بشيء.','يتكلم ويخبر الآخرين بشيء.'),
 }},
 'ar-a1-u04-p04':{
  'questions':{
   'q9':('أكمل: سأ_____ صديقي بموعد الدرس.','أكمل: أنا _____ صديقي بموعد الدرس.'),
  },
  'answers':{
   'q3':('أن أم ليلى أعطتها معلومة أو قالت لها خبرًا.','أن أم ليلى أعطتها معلومة أو أخبرتها بشيء.'),
   'q7':('أشخاص؛ مجموعة من البشر.','مجموعة من الأشخاص.'),
  },
 },
 'ar-a1-u04-p05':{'answers':{
  'q4':('في الجهة التي تقع في مقدمة البيت.','في المكان خارج البيت من الجهة الأمامية.'),
  'q7':('في الجهة المقابلة للمقدمة أو قدام الشيء.','في الجهة الأمامية من الشيء، لا خلفه.'),
 }},
}

FINDING_META={
 'ar-a1-u04-p01':[
  ('text','naturalness_idiomaticity','moderate','Replace في مرة أخرى and the unidiomatic عندنا ناسًا construction with natural contemporary MSA.'),
  ('text','naturalness_idiomaticity','minor','Replace قريبة لهم with the idiomatic kinship expression من أقاربهم.'),
  ('answer q4','answer_wording','minor','Remove an over-formal and awkward definition of ابن while preserving the passage relation.'),
  ('answer q7','answer_wording','minor','Simplify the standalone definition of ابن for an A1 learner.'),
 ],
 'ar-a1-u04-p02':[
  ('text','naturalness_idiomaticity','minor','Make the new-person description natural without removing the target شخص.'),
  ('answer q3','answer_wording','minor','Replace an abstract passive definition of اسم with direct A1 wording.'),
 ],
 'ar-a1-u04-p03':[
  ('text','naturalness_idiomaticity','minor','Replace تجلس ... مع كتاب with a natural reading action.'),
  ('answer q4','answer_wording','minor','Simplify the explanation of يقول and remove awkward wording.'),
 ],
 'ar-a1-u04-p04':[
  ('question q9','question_wording','moderate','Repair a cloze whose prefix plus keyed answer would incorrectly produce سأأخبر.'),
  ('answer q3','answer_wording','minor','Replace قالت لها خبرًا with a natural explanation of أخبرتني.'),
  ('answer q7','answer_wording','minor','Use a direct A1 definition of ناس instead of a semicolon-heavy abstract gloss.'),
 ],
 'ar-a1-u04-p05':[
  ('text','naturalness_idiomaticity','minor','Replace قريب لنا with the idiomatic kinship expression من أقاربنا.'),
  ('answer q4','semantic_precision','moderate','Define أمام البيت as a front-side location rather than a vague direction.'),
  ('answer q7','semantic_precision','major','Correct an answer that wrongly described أمام as opposite to the front.'),
 ],
 'ar-a1-u04-p06':[
  ('text','naturalness_idiomaticity','minor','Use تعيش مع for immediate family rather than the unnatural تعرف أباها listing.'),
  ('text','naturalness_idiomaticity','minor','Replace تسمع ما يقول الناس في الحديث with idiomatic listening wording.'),
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
 if actual!=EXPECTED_SHA256: raise SystemExit(f'A1 canonical drift: expected {EXPECTED_SHA256}, got {actual}; rebind Unit 4 review')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)): raise SystemExit('A1 layout drift')
 if [rows[i].get('id') for i in range(18,24)]!=EXPECTED_IDS: raise SystemExit('A1 Unit 4 id/layout drift')
 by={r['id']:r for r in rows}; before={pid:target_counts(by[pid]) for pid in EXPECTED_IDS}
 for pid in EXPECTED_IDS:
  r=by[pid]; text=r['text']
  for old,new in TEXT_REPAIRS.get(pid,[]): text=replace_once(text,old,new,f'{pid} text')
  r['text']=text
  qs={q['id']:q for q in r.get('questions',[])}; aa={a['question_id']:a for a in r.get('answer_key',[])}
  for qid,(old,new) in QA_REPAIRS.get(pid,{}).get('questions',{}).items():
   if qs[qid].get('prompt')!=old: raise SystemExit(f'{pid}/{qid}: question drift')
   qs[qid]['prompt']=new
  for qid,(old,new) in QA_REPAIRS.get(pid,{}).get('answers',{}).items():
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
  r['revision']=int(r.get('revision',0) or 0)+1
  quality=r.setdefault('quality',{})
  if quality.get('status')!='draft' or quality.get('coverage_check')!='pending': raise SystemExit(f'{pid}: unexpected release/coverage state')
  for field in ('linguistic_review','pedagogical_review','answer_key_check','schema_check'): quality[field]='pass'
  notes=quality.setdefault('notes',[])
  if NOTE not in notes: notes.append(NOTE)
 total=sum(len(FINDING_META[p]) for p in EXPECTED_IDS)
 if total!=16: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'A1','unit':4,'records_reviewed':6,'records_with_findings':6,'fresh_findings':total,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__': main()

#!/usr/bin/env python3
"""Apply fresh Arabic Gate B A1 Unit 3 naturalness/Q&A repairs."""
from __future__ import annotations

import hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'
EXPECTED_SHA256='56afae7c5cff90c15f81427fe5ea5bb0a69baf016525318932e11d4708fbf824'
EXPECTED_IDS=[f'ar-a1-u03-p{i:02d}' for i in range(1,7)]
TOKEN=re.compile(r'\S+')
NOTE='2026-08-31 fresh Gate B naturalness review (A1 Unit 3): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied; no educator/publication release claim.'

TEXT_REPAIRS={
 'ar-a1-u03-p02':[
  ('في النهاية يكون عدد الأشياء في الحقيبة قليلًا، وكل شيء فيها له مكان في عشاء اليوم.','في النهاية يكون عدد الأشياء في الحقيبة قليلًا، وكلها أشياء ضرورية لعشاء اليوم.')
 ],
 'ar-a1-u03-p03':[
  ('تقول الأم: وأنا أعرف عند من نسأل إذا لم نجد شيئًا.','تقول الأم: وأنا أعرف أننا نسأل عند صندوق الخدمة إذا لم نجد شيئًا.')
 ],
 'ar-a1-u03-p04':[
  ('بعد الطعام تتأكد ليلى أن طلبها صار صحيحًا قبل أن تغادر مع أمها.','بعد الطعام تتأكد ليلى أن الماء والخبز هما ما طلبته قبل أن تغادر مع أمها.')
 ],
 'ar-a1-u03-p05':[
  ('تقول ليلى: عندنا طماطم كثيرة، هل نحتاج إلى سلطة أخرى؟','تقول ليلى: عندنا سلطة على الطاولة، هل نحتاج إلى سلطة أخرى؟')
 ],
 'ar-a1-u03-p06':[
  ('وإذا سألها العامل لماذا اختارت الماء أو الطعام تذكر السبب.','وإذا سألها العامل لماذا اختارت الماء تذكر السبب.')
 ],
}

QA_REPAIRS={
 'ar-a1-u03-p01':{'answers':{
  'q3':('أن ليلى تستمتع به وتفضله كطعام.','أن ليلى تحب أكله.'),
  'q7':('أحسن أو أنسب في نظر المتكلم.','أحسن أو أنسب للمتكلم.'),
 }},
 'ar-a1-u03-p04':{'answers':{
  'q7':('عن الامتنان أو الأدب عند تلقي شيء أو عرض.','لشكر شخص عندما يساعدنا أو يعطينا شيئًا.'),
 }},
 'ar-a1-u03-p05':{'answers':{
  'q7':('واحدة إضافية أو مختلفة، مع اسم مؤنث.','واحدة إضافية أو مختلفة.'),
 }},
}

FINDING_META={
 'ar-a1-u03-p01':[
  ('answer q3','answer_wording','minor','Replace an abstract preference explanation with direct A1 wording.'),
  ('answer q7','answer_wording','minor','Simplify the definition of أفضل while preserving its contextual meaning.'),
 ],
 'ar-a1-u03-p02':[
  ('text','naturalness_idiomaticity','minor','Replace translation-like له مكان في عشاء اليوم with a natural relation to the meal.'),
 ],
 'ar-a1-u03-p03':[
  ('text','naturalness_idiomaticity','moderate','Replace unidiomatic عند من نسأل with a valid location use of عند at the service desk.'),
 ],
 'ar-a1-u03-p04':[
  ('text','semantic_precision','minor','State concretely that the received food and drink match what was ordered.'),
  ('answer q7','answer_wording','minor','Explain شكرًا through a concrete A1 social use rather than abstract terminology.'),
 ],
 'ar-a1-u03-p05':[
  ('text','pragmatic_plausibility','moderate','Establish an existing salad before asking whether another salad is needed.'),
  ('answer q7','answer_wording','minor','Remove an unnecessary grammatical-label clause from the A1 meaning answer.'),
 ],
 'ar-a1-u03-p06':[
  ('text','semantic_precision','minor','Keep the recap faithful to the cafe event: the worker asks about the water choice, not food generally.'),
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
 if actual!=EXPECTED_SHA256: raise SystemExit(f'A1 canonical drift: expected {EXPECTED_SHA256}, got {actual}; rebind Unit 3 review')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)): raise SystemExit('A1 layout drift')
 if [rows[i].get('id') for i in range(12,18)]!=EXPECTED_IDS: raise SystemExit('A1 Unit 3 id/layout drift')
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
 if total!=9: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'A1','unit':3,'records_reviewed':6,'records_with_findings':6,'fresh_findings':total,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__': main()

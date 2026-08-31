#!/usr/bin/env python3
"""Apply fresh Arabic Gate B A1 Unit 6 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/arabic/a1/passages.jsonl'
EXPECTED_SHA256='1abc3122f5ed396b4e54b78ce5f2493d4212c30a33f57f5e43b1ec52b4af0e26'
EXPECTED_IDS=[f'ar-a1-u06-p{i:02d}' for i in range(1,7)]
TOKEN=re.compile(r'\S+')
NOTE='2026-08-31 fresh Gate B naturalness review (A1 Unit 6): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-a1-u06-p01': [('ثم امشي في الطريق الكبير نحو الحديقة.','ثم امشي في الطريق الرئيسي نحو الحديقة.')],
 'ar-a1-u06-p03': [('تقول مريم: لا نصعد إلى الجسر؛ الممر الذي نريده تحت الجسر.','تقول مريم: لا نمر فوق الجسر؛ الممر الذي نريده تحت الجسر.')],
 'ar-a1-u06-p06': [('بهذه الكلمات تعرف ليلى كيف تبدأ الطريق، وكيف تستمر فيه، وكيف تعرف أنها وصلت.','بهذه الكلمات تعرف ليلى كيف تبدأ السير، وكيف تستمر في الطريق، وكيف تعرف أنها وصلت.')],
}
QA_REPAIRS={
 'ar-a1-u06-p02': {'answers':{
  'q3':('المركبة التي يركبانها إلى المركز.','مركبة تسير على الطريق وتنقلهما إلى المركز.'),
  'q4':('متى نبلغ المكان المقصود.','متى نصل إلى المكان الذي نريد الذهاب إليه.'),
  'q7':('يبلغ المكان المقصود.','يأتي إلى المكان في نهاية الطريق.'),
 }},
 'ar-a1-u06-p03': {'answers':{
  'q4':('أن المكان يحتاج إلى مسافة أكبر للوصول إليه.','أنه غير قريب ويحتاج الوصول إليه إلى وقت أكثر.'),
  'q7':('غير قريب؛ تفصله مسافة كبيرة نسبيًا.','ليس قريبًا؛ يحتاج الوصول إليه إلى وقت أكثر.'),
 }},
 'ar-a1-u06-p04': {'answers':{
  'q3':('انتقلي أو سيري إلى المكان المطلوب.','سيري إلى المكان المطلوب.'),
 }},
 'ar-a1-u06-p05': {'answers':{
  'q4':('الجزء المركزي بين الجوانب.','منتصف الشيء.'),
 }},
 'ar-a1-u06-p06': {'answers':{
  'q6':('باتجاه.','في اتجاه.'),
 }},
}
FINDING_META={
 'ar-a1-u06-p01': [('text','naturalness_idiomaticity','minor','Use الطريق الرئيسي for a main road rather than the literal-sounding الطريق الكبير.')],
 'ar-a1-u06-p02': [
  ('answer q3','answer_wording','minor','Explain سيارة concretely rather than as the formal المركبة التي يركبانها.'),
  ('answer q4','semantic_precision','minor','Make the meaning of نصل a complete, direct learner-facing statement.'),
  ('answer q7','answer_wording','minor','Replace يبلغ المكان المقصود with simpler A1 arrival wording.'),
 ],
 'ar-a1-u06-p03': [
  ('text','naturalness_idiomaticity','moderate','Replace لا نصعد إلى الجسر with the natural route contrast لا نمر فوق الجسر.'),
  ('answer q4','answer_wording','minor','Explain بعيد through direct distance/time language rather than an abstract larger-distance formulation.'),
  ('answer q7','answer_wording','minor','Remove the formal تفصله مسافة كبيرة نسبيًا definition in favor of A1 wording.'),
 ],
 'ar-a1-u06-p04': [('answer q3','answer_wording','minor','Remove the formal انتقلي synonym from the A1 gloss of اذهبي.')],
 'ar-a1-u06-p05': [('answer q4','answer_wording','minor','Replace الجزء المركزي بين الجوانب with the direct A1 meaning منتصف الشيء.')],
 'ar-a1-u06-p06': [
  ('text','naturalness_idiomaticity','minor','Replace تبدأ الطريق with the natural تبدأ السير while preserving the route sequence.'),
  ('answer q6','answer_wording','minor','Use the complete phrase في اتجاه for the meaning of نحو.'),
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
 if actual!=EXPECTED_SHA256: raise SystemExit(f'A1 canonical drift: expected {EXPECTED_SHA256}, got {actual}; rebind Unit 6 review')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)): raise SystemExit('A1 layout drift')
 if [rows[i].get('id') for i in range(30,36)]!=EXPECTED_IDS: raise SystemExit('A1 Unit 6 id/layout drift')
 by={r['id']:r for r in rows}; before={pid:target_counts(by[pid]) for pid in EXPECTED_IDS}
 for pid in EXPECTED_IDS:
  r=by[pid]; text=r['text']
  for old,new in TEXT_REPAIRS.get(pid,[]): text=replace_once(text,old,new,f'{pid} text')
  r['text']=text; qs={q['id']:q for q in r.get('questions',[])}; aa={a['question_id']:a for a in r.get('answer_key',[])}
  edits=QA_REPAIRS.get(pid,{})
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
  r['revision']=int(r.get('revision',0) or 0)+1
  quality=r.setdefault('quality',{})
  if quality.get('status')!='draft' or quality.get('coverage_check')!='pending': raise SystemExit(f'{pid}: unexpected release/coverage state')
  for field in ('linguistic_review','pedagogical_review','answer_key_check','schema_check'): quality[field]='pass'
  notes=quality.setdefault('notes',[])
  if NOTE not in notes: notes.append(NOTE)
 total=sum(len(FINDING_META[p]) for p in EXPECTED_IDS)
 if total!=11: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'A1','unit':6,'records_reviewed':6,'records_with_findings':6,'fresh_findings':total,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__': main()

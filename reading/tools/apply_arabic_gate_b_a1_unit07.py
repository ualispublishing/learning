#!/usr/bin/env python3
"""Apply fresh Arabic Gate B A1 Unit 7 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PATH=ROOT/'reading/arabic/a1/passages.jsonl'
EXPECTED_SHA256='34a80a4536e11fc9c0f53ac1ca0421cb2658673855422cea3ec2873cdb0186a4'
EXPECTED_IDS=[f'ar-a1-u07-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-08-31 fresh Gate B naturalness review (A1 Unit 7): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-a1-u07-p01':[('تقول: الآن أفهم لماذا نختار الملابس حسب السماء والموسم، لا حسب اليوم فقط.','تقول: الآن أفهم لماذا نختار الملابس حسب حالة السماء والموسم، لا حسب اليوم فقط.')],
 'ar-a1-u07-p05':[('بجانب كل يوم تكتب ساعة الخروج المقترحة.','بجانب كل يوم تكتب الساعة التي تريد أن تخرج فيها.')],
 'ar-a1-u07-p06':[('بهذه الطريقة لا تتحكم حالة الجو في كل خططها، لكنها تساعدها على اختيار الملابس والوقت المناسبين.','بهذه الطريقة لا تغيّر ليلى كل خططها بسبب الجو، بل تستخدم معلوماته لاختيار الملابس والوقت المناسبين.')],
}
QA_REPAIRS={
 'ar-a1-u07-p01':{'answers':{'q3':('الجزء الذي تنظر إليه ليلى فوقها لترى الغيوم والجو.','ما نراه فوقنا وفيه الشمس والغيوم.')}},
 'ar-a1-u07-p02':{'answers':{
  'q4':('أن الجو يظهر أو يُشعر ليلى بأنه أبرد.','أن ليلى تشعر أن الجو أبرد مما توقعت.'),
  'q7':('يظهر أو يعطي انطباعًا معينًا.','نظن أن شيئًا على حال معينة من غير تأكد.'),
 }},
 'ar-a1-u07-p03':{'answers':{'q7':('قد يحدث؛ على سبيل الاحتمال.','قد يحدث، لكنه غير مؤكد.')},'explanations':{'q6':('«قادم» يوافق «الأسبوع» هنا في التذكير.','نقول «الأسبوع القادم» عن الأسبوع الذي سيأتي بعد هذا الأسبوع.')}},
 'ar-a1-u07-p04':{'answers':{'q7':('جمع يوم.','عدة أيام.')}},
 'ar-a1-u07-p05':{'answers':{'q4':('مجموعة الأيام السبعة التي تنظم فيها ليلى خطتها.','سبعة أيام متتالية.')}},
}
FINDING_META={
 'ar-a1-u07-p01':[
  ('text','naturalness_idiomaticity','minor','Use حسب حالة السماء rather than the compressed حسب السماء for a weather-based clothing choice.'),
  ('answer q3','answer_wording','minor','Replace the cumbersome definition of السماء with a concrete A1 description.'),
 ],
 'ar-a1-u07-p02':[
  ('answer q4','semantic_precision','minor','Explain يبدو الجو أبرد through Leila’s perception rather than awkward يظهر أو يُشعر wording.'),
  ('answer q7','answer_wording','minor','Give يبدو a direct uncertainty-based A1 meaning instead of abstract impression language.'),
 ],
 'ar-a1-u07-p03':[
  ('explanation q6','answer_wording','minor','Replace grammatical-gender jargon with a direct meaning-based explanation of الأسبوع القادم.'),
  ('answer q7','answer_wording','minor','Replace على سبيل الاحتمال with the direct meaning may happen but is not certain.'),
 ],
 'ar-a1-u07-p04':[('answer q7','semantic_precision','minor','Answer the meaning of أيام directly instead of giving the grammatical label جمع يوم.')],
 'ar-a1-u07-p05':[
  ('text','naturalness_idiomaticity','minor','Replace stiff ساعة الخروج المقترحة with a natural statement of the time she wants to leave.'),
  ('answer q4','answer_wording','minor','Define أسبوع directly as seven consecutive days rather than tying the definition to Leila’s plan.'),
 ],
 'ar-a1-u07-p06':[('text','naturalness_idiomaticity','minor','Replace the awkward weather-controls-plans phrasing with a natural statement that Leila does not change every plan because of weather.')],
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
 if actual!=EXPECTED_SHA256: raise SystemExit(f'A1 canonical drift: expected {EXPECTED_SHA256}, got {actual}; rebind Unit 7 review')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(36,42)]!=EXPECTED_IDS: raise SystemExit('A1 Unit 7 layout/id drift')
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
  r['revision']=int(r.get('revision',0) or 0)+1; quality=r.setdefault('quality',{})
  if quality.get('status')!='draft' or quality.get('coverage_check')!='pending': raise SystemExit(f'{pid}: unexpected release/coverage state')
  for field in ('linguistic_review','pedagogical_review','answer_key_check','schema_check'): quality[field]='pass'
  if NOTE not in quality.setdefault('notes',[]): quality['notes'].append(NOTE)
 total=sum(len(FINDING_META[p]) for p in EXPECTED_IDS)
 if total!=10: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'A1','unit':7,'records_reviewed':6,'records_with_findings':6,'fresh_findings':total,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

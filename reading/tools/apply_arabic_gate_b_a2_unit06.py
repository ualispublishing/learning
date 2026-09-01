#!/usr/bin/env python3
"""Apply fresh Arabic Gate B A2 Unit 6 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/a2/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; RELEASE=READING/'RELEASE_STATUS.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'
EXPECTED_IDS=[f'ar-a2-u06-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-01 fresh Gate B naturalness review (A2 Unit 6): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-a2-u06-p01':[
  ('وفي رحلة العودة كانت نور تعرف الترتيب، فانتقلت بين الشاشات والبوابة بهدوء أكبر وساعدت أخاها الصغير في قراءة الرقم.', 'وفي رحلة العودة كانت نور تعرف الترتيب، فراجعت الشاشات ثم توجهت إلى البوابة بهدوء أكبر وساعدت أخاها الصغير في قراءة الرقم.'),
 ],
 'ar-a2-u06-p02':[
  ('المشكلة كانت أنني لم أكن أعرف هل سيتغير الوقت أكثر.', 'المشكلة كانت أنني لم أكن أعرف هل سيزداد التأخير.'),
 ],
 'ar-a2-u06-p03':[
  ('في يوم السفر تم الانتقال بسهولة، واشترت تذكرة الحافلة بعد خروجها من المحطة.', 'في يوم السفر انتقلت نور بسهولة، واشترت تذكرة الحافلة بعد خروجها من المحطة.'),
  ('لا يكفي أن أعرف وقت كل جزء منفصلًا؛ يجب أن أفكر أيضًا في المسافة والوقت بينهما.', 'لا يكفي أن أعرف وقت كل جزء على حدة؛ يجب أن أفكر أيضًا في المسافة والوقت بينهما.'),
 ],
 'ar-a2-u06-p05':[
  ('والناس يعرف بعضهم بعضًا أكثر،', 'والناس يعرفون بعضهم بعضًا أكثر،'),
 ],
 'ar-a2-u06-p06':[
  ('حتى عندما لا يسير كل جزء تمامًا كما كان مكتوبًا.', 'حتى عندما لا يسير كل جزء تمامًا كما كان مخططًا له.'),
 ],
}
QA_REPAIRS={
 'ar-a2-u06-p01':{
  'questions':{'q9':('أكمل: سافرنا إلى المدينة بالط_____.','أكمل: سافرنا إلى المدينة بال_____.')},
 },
 'ar-a2-u06-p02':{'answers':{
  'q1':('تراجعان معلومات الرحلة والطريق وتنتقلان إلى الرصيف الجديد عندما يتغير.','تراجعان معلومات الرحلة والطريق وتنتقلان إلى الرصيف الجديد عندما يتغير رصيف القطار.'),
 }},
 'ar-a2-u06-p03':{'answers':{
  'q3':('وسائل تُستخدم للانتقال من مكان إلى آخر.','الانتقال من مكان إلى آخر باستخدام وسيلة مثل القطار أو الحافلة.'),
 }},
 'ar-a2-u06-p04':{'answers':{
  'q3':('تتوقف عن الحركة في محطة حتى ينزل أو يركب الناس.','تقف الحافلة في محطة حتى ينزل الناس أو يركبوا.'),
  'q4':('ملائمة وسهلة لاستخدام نور للوصول إلى المكتبة.','ملائمة لنور ويسهل منها الوصول إلى المكتبة.'),
  'q5':('لأن سهولة المشي ووجود ممر آمن أثرا في الطريق الحقيقي.','لأن سهولة المشي ووجود ممر آمن أثرا في اختيار الطريق.'),
 }},
 'ar-a2-u06-p05':{'answers':{
  'q3':('مكان سكني صغير أقل حجمًا وحركة من المدينة.','مكان صغير يسكن فيه الناس، وهو أصغر من المدينة عادةً.'),
 }},
 'ar-a2-u06-p06':{'answers':{
  'q1':('السفر يصبح أسهل عندما تخطط نور للاتصالات والانتظار والبدائل بين أجزاء الرحلة.','السفر يصبح أسهل عندما تخطط نور لأوقات الانتقال والانتظار والبدائل بين أجزاء الرحلة.'),
 }},
}
FINDING_META={
 'ar-a2-u06-p01':[
  ('text','naturalness_idiomaticity','minor','Replace the awkward movement between screens and the gate with reviewing the screens and then going to the gate.'),
  ('question q9','assessment_clarity','moderate','Remove the partial-word airplane cloze and ask for the complete lexical target after the preposition/article frame.'),
 ],
 'ar-a2-u06-p02':[
  ('text','naturalness_idiomaticity','minor','Replace هل سيتغير الوقت أكثر with the direct travel-delay wording هل سيزداد التأخير.'),
  ('answer q1','reference_clarity','minor','Make explicit that the platform changes, rather than leaving عندما يتغير without a clear subject.'),
 ],
 'ar-a2-u06-p03':[
  ('text','naturalness_idiomaticity','minor','Replace bureaucratic تم الانتقال with the direct active narrative انتقلت نور.'),
  ('text','naturalness_idiomaticity','minor','Replace وقت كل جزء منفصلًا with the idiomatic وقت كل جزء على حدة.'),
  ('answer q3','semantic_precision','moderate','The original answer defines وسائل نقل rather than the target نقل; define transport as movement using a vehicle or mode.'),
 ],
 'ar-a2-u06-p04':[
  ('answer q3','answer_wording','minor','Define a bus stopping at a stop directly rather than as an abstract cessation of movement.'),
  ('answer q4','naturalness_idiomaticity','minor','Replace ملائمة وسهلة لاستخدام نور with direct suitability/access wording.'),
  ('answer q5','naturalness_idiomaticity','minor','Replace الطريق الحقيقي with the actual decision being explained: choosing the route.'),
 ],
 'ar-a2-u06-p05':[
  ('text','grammar_wording','moderate','Repair subject-verb agreement: الناس يعرفون بعضهم بعضًا.'),
  ('answer q3','answer_wording','minor','Define قرية with direct A2 wording instead of أقل حجمًا وحركة.'),
 ],
 'ar-a2-u06-p06':[
  ('text','naturalness_idiomaticity','minor','A travel plan is planned rather than written; use كما كان مخططًا له.'),
  ('answer q1','semantic_precision','minor','Replace ambiguous الاتصالات, which suggests communications, with أوقات الانتقال for travel connections/transfers.'),
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
 if not isinstance(bound,str) or len(bound)!=64 or actual!=bound: raise SystemExit(f'A2 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 6 review')
 rel=json.loads(RELEASE.read_text(encoding='utf-8')); ar=rel.get('languages',{}).get('arabic',{}); prog=ar.get('naturalness_review_progress',{})
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False or prog.get('fresh_records_reviewed')!=90 or prog.get('levels_completed')!=['A1']: raise SystemExit('Arabic Gate B frontier drift: expected 90 reviewed with A1 complete and A2 Unit 6 next')
 if not (DECISION_DIR/'a2_u05.json').exists() or (DECISION_DIR/'a2_u06.json').exists(): raise SystemExit('A2 decision frontier drift: Unit 5 must exist and Unit 6 must not')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(30,36)]!=EXPECTED_IDS: raise SystemExit('A2 Unit 6 layout/id drift')
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
 if total!=14: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'A2','unit':6,'records_reviewed':6,'records_with_findings':6,'fresh_findings':total,'pre_repair_canonical_sha256':actual,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

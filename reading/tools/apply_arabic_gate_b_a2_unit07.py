#!/usr/bin/env python3
"""Apply fresh Arabic Gate B A2 Unit 7 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/a2/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; RELEASE=READING/'RELEASE_STATUS.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'
EXPECTED_IDS=[f'ar-a2-u07-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-01 fresh Gate B naturalness review (A2 Unit 7): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-a2-u07-p01':[
  ('لكنني فهمت أن الفعالية يمكن أن تجمع أنشطة وجمهورًا مختلفين في المكان نفسه.', 'لكنني فهمت أن الفعالية يمكن أن تجمع أنشطة مختلفة وجمهورًا متنوعًا في المكان نفسه.'),
 ],
 'ar-a2-u07-p03':[
  ('ثم كتبوا تقريرًا قصيرًا يقترح مكان انتظار مختلفًا على بعد مسافة قليلة.', 'ثم كتبوا تقريرًا قصيرًا يقترح مكان انتظار مختلفًا على مسافة قصيرة.'),
 ],
}
QA_REPAIRS={
 'ar-a2-u07-p01':{'answers':{
  'q4':('الناس الذين حضروا الفعالية لمشاهدتها أو المشاركة فيها كزوار.','الناس الذين يحضرون الفعالية لمشاهدتها أو المشاركة فيها.'),
  'q5':('لأنها ترى أن الحدث يحتوي على أنشطة وجماهير فرعية متعددة لا نشاطًا واحدًا.','لأنها ترى أن الفعالية تضم أنشطة مختلفة ويأتيها زوار لأغراض مختلفة، لا نشاطًا واحدًا فقط.'),
 }},
 'ar-a2-u07-p02':{'answers':{
  'q3':('جهة أو عمل ينشر أخبارًا وتقارير عن المنطقة.','وسائل الإعلام المحلية التي تنشر أخبار المنطقة وتقاريرها.'),
 }},
 'ar-a2-u07-p03':{'answers':{
  'q4':('النتيجة أو الأثر الذي تسببه السيارات في سهولة حركة المشاة وسلامتها.','الأثر الذي تسببه السيارات في حركة المشاة وسلامتهم.'),
 }},
 'ar-a2-u07-p04':{'answers':{
  'q3':('نشر أو أخبر الجمهور رسميًا بخطة أو قرار.','أخبر الجمهور رسميًا بخطة أو قرار.'),
 }},
 'ar-a2-u07-p05':{'answers':{
  'q4':('يعتقدون أن هذا العدد قد يحضر مستقبلًا، من دون تأكيد.','يعتقدون أن نحو هذا العدد من الأشخاص قد يحضر مستقبلًا، من دون تأكيد.'),
  'q5':('لأن الرقم توقع يعتمد أيضًا على شرط الطقس ولم يحدث الحدث بعد.','لأن الرقم مجرد توقع يعتمد أيضًا على حالة الطقس، والفعالية لم تحدث بعد.'),
 }},
 'ar-a2-u07-p06':{'answers':{
  'q4':('تحدد المصدر، تميز البيان من الوصف الصحفي، تنظر إلى الدليل والتأثير، تستخرج الأفكار الرئيسية، وتفصل الحقيقة عن التوقع.','تحدد المصدر، وتميز البيان عن الوصف الصحفي، وتنظر إلى الدليل والتأثير، وتستخرج الأفكار الرئيسية، وتفصل الحقيقة عن التوقع.'),
 }},
}
FINDING_META={
 'ar-a2-u07-p01':[
  ('text','grammar_wording','moderate','Repair the mixed agreement in أنشطة وجمهورًا مختلفين by giving each coordinated element a natural modifier.'),
  ('answer q4','answer_wording','minor','Define الجمهور directly without the redundant phrasing المشاركة فيها كزوار.'),
  ('answer q5','semantic_precision','minor','Explain the shift in Noor’s understanding through varied activities and visitor purposes rather than the abstract جماهير فرعية formulation.'),
 ],
 'ar-a2-u07-p02':[
  ('answer q3','semantic_precision','minor','Define الصحافة المحلية as local media that publish area news and reports rather than as an ambiguous جهة أو عمل.'),
 ],
 'ar-a2-u07-p03':[
  ('text','naturalness_idiomaticity','minor','Replace the redundant على بعد مسافة قليلة with the idiomatic على مسافة قصيرة.'),
  ('answer q4','semantic_precision','minor','Explain the cars’ impact directly on pedestrian movement and safety rather than on the ease of movement and its safety.'),
 ],
 'ar-a2-u07-p04':[
  ('answer q3','answer_wording','minor','Define أعلن with the direct communicative meaning أخبر الجمهور رسميًا and remove the incomplete نشر alternative.'),
 ],
 'ar-a2-u07-p05':[
  ('answer q4','semantic_precision','moderate','A number itself cannot attend; make the predicted attendees explicit.'),
  ('answer q5','answer_wording','minor','Clarify that the number is only a weather-dependent forecast and the event has not yet occurred.'),
 ],
 'ar-a2-u07-p06':[
  ('answer q4','grammar_wording','minor','Use the idiomatic contrast preposition تميز ... عن rather than تميز ... من.'),
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
 if not isinstance(bound,str) or len(bound)!=64 or actual!=bound: raise SystemExit(f'A2 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 7 review')
 rel=json.loads(RELEASE.read_text(encoding='utf-8')); ar=rel.get('languages',{}).get('arabic',{}); prog=ar.get('naturalness_review_progress',{})
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False or prog.get('fresh_records_reviewed')!=96 or prog.get('levels_completed')!=['A1']: raise SystemExit('Arabic Gate B frontier drift: expected 96 reviewed with A1 complete and A2 Unit 7 next')
 if not (DECISION_DIR/'a2_u06.json').exists() or (DECISION_DIR/'a2_u07.json').exists(): raise SystemExit('A2 decision frontier drift: Unit 6 must exist and Unit 7 must not')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(36,42)]!=EXPECTED_IDS: raise SystemExit('A2 Unit 7 layout/id drift')
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
 if total!=10: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'A2','unit':7,'records_reviewed':6,'records_with_findings':6,'fresh_findings':total,'pre_repair_canonical_sha256':actual,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

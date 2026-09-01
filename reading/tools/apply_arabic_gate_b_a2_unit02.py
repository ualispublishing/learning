#!/usr/bin/env python3
"""Apply fresh Arabic Gate B A2 Unit 2 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/a2/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; RELEASE=READING/'RELEASE_STATUS.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'
EXPECTED_IDS=[f'ar-a2-u02-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-01 fresh Gate B naturalness review (A2 Unit 2): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-a2-u02-p01':[
  ('قالت نور: الدعوة سهلة، لكن الرد الجيد يحتاج أحيانًا إلى أن أنظر إلى خطتي قبل أن أقول نعم أو لا.', 'قالت نور: قبول الدعوة قد يكون سهلًا، لكن الرد الجيد يحتاج أحيانًا إلى أن أنظر إلى خطتي قبل أن أقول نعم أو لا.'),
 ],
 'ar-a2-u02-p02':[
  ('فوجدتا ورقة كتب عليها الوقت نفسه.', 'فوجدتا ورقة مكتوبًا عليها الوقت نفسه.'),
 ],
 'ar-a2-u02-p03':[
  ('لا أريد أن أصلك متأخرة من غير أن أخبرك.', 'لا أريد أن أصل إليك متأخرة من غير أن أخبرك.'),
 ],
 'ar-a2-u02-p04':[
  ('لم تعد الخطة الحالية هي الحديقة، بل أصبح اللقاء في بيت مريم في الوقت نفسه.', 'لم تعد الخطة الحالية هي الذهاب إلى الحديقة، بل أصبح اللقاء في بيت مريم في الوقت نفسه.'),
 ],
 'ar-a2-u02-p05':[
  ('فتحتا تقويميهما وحددتا الأيام التي تحتاج إلى تغيير.', 'فتحتا تقويميهما وحددتا المواعيد التي تحتاجان إلى تعديلها.'),
 ],
}
QA_REPAIRS={
 'ar-a2-u02-p02':{'answers':{
  'q8':('لأنه أعطى مريم دليلًا مستقلًا وأزال الشك.','لأنه أكد الموعد من مصدر آخر وأزال الشك.'),
 }},
 'ar-a2-u02-p03':{'answers':{
  'q3':('تواصلت معها هاتفيًا لتخبرها بتغيير الخطة.','اتصلت بها لتخبرها بتغيير الخطة.'),
 }},
 'ar-a2-u02-p04':{'answers':{
  'q3':('بديل مختلف يمكن أن يحل محل الخطة الأصلية.','خيار آخر يمكن أن يحل محل الخطة الأصلية.'),
  'q4':('الخطة الموجودة والمعتمدة في الوقت الراهن.','الخطة التي يتبعنها الآن.'),
 }},
 'ar-a2-u02-p05':{'answers':{
  'q4':('ترتيب المواعيد والواجبات بحيث لا تتعارض بلا خطة.','ترتيب المواعيد والواجبات حتى لا تتعارض.'),
 }},
 'ar-a2-u02-p06':{
  'questions':{
   'q3':('ماذا تفعل إذا لن تصل في الوقت المتفق عليه؟','ماذا تفعل نور إذا عرفت أنها لن تصل في الوقت المتفق عليه؟'),
   'q8':('إلى ماذا تشير «البديل» في الجملة الأخيرة؟','إلى ماذا تشير كلمة «البديل» في عبارة «يتفقوا معًا على البديل»؟'),
  },
 },
}
FINDING_META={
 'ar-a2-u02-p01':[
  ('text','naturalness_idiomaticity','minor','Replace the unnatural statement الدعوة سهلة with a clear statement about accepting an invitation.'),
 ],
 'ar-a2-u02-p02':[
  ('text','grammar_wording','moderate','Replace ورقة كتب عليها with the correctly formed passive description ورقة مكتوبًا عليها.'),
  ('answer q8','answer_wording','minor','Replace the abstract دليلًا مستقلًا explanation with a direct statement that another source confirmed the time.'),
 ],
 'ar-a2-u02-p03':[
  ('text','grammar_wording','moderate','Repair لا أريد أن أصلك متأخرة to the idiomatic motion construction لا أريد أن أصل إليك متأخرة.'),
  ('answer q3','answer_wording','minor','Explain اتصلت بسلمى directly as calling her rather than the formal تواصلت معها هاتفيًا.'),
 ],
 'ar-a2-u02-p04':[
  ('text','semantic_precision','moderate','Do not equate the current plan itself with الحديقة; state that the plan had been to go to the park.'),
  ('answer q3','answer_wording','minor','Replace the redundant بديل مختلف definition of اختيار آخر with direct choice wording.'),
  ('answer q4','answer_wording','minor','Replace the formal الموجودة والمعتمدة في الوقت الراهن definition with a direct explanation of the plan being followed now.'),
 ],
 'ar-a2-u02-p05':[
  ('text','reference_clarity','moderate','The days themselves do not need changing; identify the appointments/times that the students need to adjust.'),
  ('answer q4','semantic_precision','minor','Remove the contradictory بلا خطة phrase from the definition of organizing time.'),
 ],
 'ar-a2-u02-p06':[
  ('question q3','grammar_wording','moderate','Repair the ungrammatical إذا لن تصل construction and anchor the question clearly to Noor.'),
  ('question q8','assessment_clarity','moderate','The word البديل is not in the final sentence; point to the actual phrase in which it appears.'),
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
 if not isinstance(bound,str) or len(bound)!=64 or actual!=bound: raise SystemExit(f'A2 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 2 review')
 rel=json.loads(RELEASE.read_text(encoding='utf-8')); ar=rel.get('languages',{}).get('arabic',{}); prog=ar.get('naturalness_review_progress',{})
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False or prog.get('fresh_records_reviewed')!=66 or prog.get('levels_completed')!=['A1']: raise SystemExit('Arabic Gate B frontier drift: expected 66 reviewed with A1 complete and A2 Unit 2 next')
 if not (DECISION_DIR/'a2_u01.json').exists() or (DECISION_DIR/'a2_u02.json').exists(): raise SystemExit('A2 decision frontier drift: Unit 1 must exist and Unit 2 must not')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(6,12)]!=EXPECTED_IDS: raise SystemExit('A2 Unit 2 layout/id drift')
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
 if total!=12: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'A2','unit':2,'records_reviewed':6,'records_with_findings':6,'fresh_findings':total,'pre_repair_canonical_sha256':actual,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Apply fresh Arabic Gate B A2 Unit 9 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/a2/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; RELEASE=READING/'RELEASE_STATUS.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'
EXPECTED_IDS=[f'ar-a2-u09-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-01 fresh Gate B naturalness review (A2 Unit 9): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied where needed; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-a2-u09-p03':[
  ('بينما يطلب كل شخص مشروبه بصورة منفصلة.', 'بينما يطلب كل شخص مشروبه على حدة.'),
 ],
 'ar-a2-u09-p04':[
  ('لكن هذه العادة يمكن أن تتغير من مناسبة إلى أخرى.', 'لكن هذه الطقوس يمكن أن تتغير من مناسبة إلى أخرى.'),
 ],
}
QA_REPAIRS={
 'ar-a2-u09-p01':{
  'questions':{'q8':('إلى ماذا تشير «التي وراءها»؟','إلى ماذا يعود الضمير «ها» في «القصة التي وراءها»؟')},
  'answers':{'q8':('إلى القصة أو المعنى الموجود خلف العادة.','إلى العادة التي تتحدث عنها الجدة.')},
 },
 'ar-a2-u09-p03':{'answers':{
  'q7':('عندما يفهمون أن بإمكانهم السؤال وأنهم ليسوا أمام اختبار للعادات.','عندما يفهمون أن بإمكانهم السؤال وأن العشاء ليس اختبارًا لمعرفة العادات.'),
 }},
 'ar-a2-u09-p04':{
  'questions':{'q7':('إلى ماذا تشير «هذه العادة»؟','إلى ماذا تشير «هذه الطقوس»؟')},
  'answers':{'q7':('إلى الطقس أو الفعل المتكرر في احتفالات العائلة، مثل الصورة أو الطبق.','إلى الطقوس المتكررة في احتفالات العائلة، مثل الصورة الجماعية أو الطبق المعين.')},
 },
 'ar-a2-u09-p05':{'answers':{
  'q7':('مجموعة الناس والأسر الذين يعيشون ضمن المكان ويتفاعلون فيه.','الأشخاص والأسر الذين يعيشون في المكان ويتفاعلون فيه.'),
 }},
 'ar-a2-u09-p06':{
  'questions':{'q2':('ماذا تعلمت من مقارنة نسختين من حكاية؟','ماذا تعلمت نور من مقارنة نسختين من حكاية؟')},
  'answers':{'q7':('لا، تشابه الهدف واختلف الشكل والتنظيم.','لا، كان الهدف متشابهًا لكن الشكل والتنظيم كانا مختلفين.')},
 },
}
FINDING_META={
 'ar-a2-u09-p01':[
  ('question/answer q8','assessment_clarity','moderate','The phrase التي وراءها is not itself a referent; ask directly what the pronoun ها refers to and answer العادة.'),
 ],
 'ar-a2-u09-p02':[],
 'ar-a2-u09-p03':[
  ('text','naturalness_idiomaticity','minor','Replace بصورة منفصلة with the more natural على حدة for ordering each drink separately.'),
  ('answer q7','answer_wording','minor','Replace the awkward ليسوا أمام اختبار للعادات with a direct statement that dinner is not a test of custom knowledge.'),
 ],
 'ar-a2-u09-p04':[
  ('text','reference_clarity','moderate','The singular هذه العادة follows plural طقوسًا متكررة; retain the plural reference as هذه الطقوس.'),
  ('question/answer q7','assessment_clarity','moderate','Align the reference-resolution item with the repaired plural phrase and remove the erroneous الطقس answer wording.'),
 ],
 'ar-a2-u09-p05':[
  ('answer q7','grammar_wording','minor','Remove the redundant مجموعة الناس والأسر and use a direct plural definition of community.'),
 ],
 'ar-a2-u09-p06':[
  ('question q2','assessment_clarity','minor','Name Noor explicitly so the subject of تعلمت is not implicit in an isolated assessment item.'),
  ('answer q7','grammar_wording','minor','Repair the compressed coordination تشابه الهدف واختلف الشكل والتنظيم into a complete contrast sentence.'),
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
 if not isinstance(bound,str) or len(bound)!=64 or actual!=bound: raise SystemExit(f'A2 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 9 review')
 rel=json.loads(RELEASE.read_text(encoding='utf-8')); ar=rel.get('languages',{}).get('arabic',{}); prog=ar.get('naturalness_review_progress',{})
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False or prog.get('fresh_records_reviewed')!=108 or prog.get('levels_completed')!=['A1']: raise SystemExit('Arabic Gate B frontier drift: expected 108 reviewed with A1 complete and A2 Unit 9 next')
 if not (DECISION_DIR/'a2_u08.json').exists() or (DECISION_DIR/'a2_u09.json').exists(): raise SystemExit('A2 decision frontier drift: Unit 8 must exist and Unit 9 must not')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(48,54)]!=EXPECTED_IDS: raise SystemExit('A2 Unit 9 layout/id drift')
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
 if total!=8: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'A2','unit':9,'records_reviewed':6,'records_with_findings':5,'fresh_findings':total,'pre_repair_canonical_sha256':actual,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

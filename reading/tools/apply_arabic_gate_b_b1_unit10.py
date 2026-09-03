#!/usr/bin/env python3
"""Apply fresh Arabic Gate B B1 Unit 10 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/b1/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; RELEASE=READING/'RELEASE_STATUS.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'
EXPECTED_IDS=[f'ar-b1-u10-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-03 fresh Gate B naturalness review (B1 Unit 10): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied where needed; legitimate B1 grammar-in-context analysis retained; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-b1-u10-p05':[
  ('وجد أن الحاجة إلى الانتظار تتركز في ساعتين مرتين في الأسبوع.','وجد أن الحاجة إلى الانتظار تتركز في فترة مدتها ساعتان، مرتين في الأسبوع.'),
  ('بعد التجربة قال الطرفان إن الحل ليس مثاليًا لكنه أفضل من الخيارين الأولين.','بعد التجربة قال الطرفان إن الحل ليس مثاليًا، لكنه أفضل من تحويل المساحة كلها إلى منطقة جلوس ثابتة أو إبقائها كما كانت.'),
 ],
}
QA_REPAIRS={
 'ar-b1-u10-p01':{'answers':{
  'q9':('استخدام الملخص كبداية، الرجوع إلى النص للادعاءات المهمة، ومراجعة الاقتباسات من شخص آخر.','استخدام الملخص كبداية، والرجوع إلى النص للادعاءات المهمة، وأن يراجع شخص آخر كل اقتباس مهم.'),
 }},
 'ar-b1-u10-p03':{'answers':{
  'q2':('حجز وسيلة النقل على موعد الثامنة.','حجز وسيلة النقل للانطلاق في الثامنة.'),
  'q7':('الأولى قابلة للمراجعة، والثانية تسمح للآخر بالتصرف والتكلف اعتمادًا عليها.','الأولى قابلة للتغيير، والثانية تسمح للآخرين بالتصرف وتحمل تكلفة اعتمادًا عليها.'),
 }},
 'ar-b1-u10-p04':{
  'answers':{
   'q1':('لأن سجلها يظهر ارتباطًا ولا يعزل المشي عن عوامل أخرى تكفي لإثبات السبب.','لأن سجلها يظهر ارتباطًا ولا يعزل أثر المشي عن عوامل أخرى، فلا يكفي لإثبات السبب.'),
  },
  'questions':{
   'q8':('إلى ماذا تشير «النمط»؟','إلى ماذا يشير «النمط»؟'),
  },
 },
 'ar-b1-u10-p05':{
  'answers':{
   'q2':('في ساعتين مرتين في الأسبوع.','في فترة مدتها ساعتان، مرتين في الأسبوع.'),
   'q4':('تغيير محدد في الخطة لتحسينها استجابة إلى دليل أو مشكلة من غير إلغاء المشروع كله.','تغيير محدد في الخطة لتحسينها استجابةً لدليل أو مشكلة من غير إلغاء المشروع كله.'),
   'q8':('إلى تحويل المكان للجلوس من دون مرونة أو رفض التغيير للحفاظ على الاستخدام القديم.','تحويل المساحة كلها إلى منطقة جلوس ثابتة، أو إبقاؤها كما كانت.'),
  },
  'questions':{
   'q8':('إلى ماذا تشير «الخيارين الأولين»؟','ما الخياران اللذان قارن بهما الطرفان الحل الجديد؟'),
  },
 },
 'ar-b1-u10-p06':{'questions':{
  'q2':('ما سؤالان تسألهما نور قبل قول «النص يعني»؟','ما السؤالان اللذان تسألهما نور قبل أن تقول «النص يعني»؟'),
  'q8':('إلى ماذا تشير «الطريق إليها»؟','إلى ماذا يشير التعبير «الطريق إليها»؟'),
 }},
}
FINDING_META={
 'ar-b1-u10-p01':[
  ('answer q9','answer_wording','minor','Clarify that a different person reviews each important quotation; the prior wording could mean reviewing quotations produced by another person.'),
 ],
 'ar-b1-u10-p02':[],
 'ar-b1-u10-p03':[
  ('answer q2','naturalness_idiomaticity','minor','Replace حجز ... على موعد with the idiomatic statement that the transport was booked for departure at eight.'),
  ('answer q7','semantic_precision','moderate','A final approval enables others to act and incur cost; التكلف is not the intended meaning here.'),
 ],
 'ar-b1-u10-p04':[
  ('answer q1','semantic_precision','major','The old answer says other factors are sufficient to prove causation, the opposite of the passage; state that failure to isolate them prevents a causal proof.'),
  ('question q8','grammar_wording','moderate','The referent النمط is masculine, so the reference-resolution question must use يشير, not تشير.'),
 ],
 'ar-b1-u10-p05':[
  ('text + answer q2','reference_clarity','moderate','Clarify that the waiting need occurs during a two-hour period twice each week rather than using the ambiguous في ساعتين مرتين في الأسبوع.'),
  ('answer q4','naturalness_idiomaticity','minor','Use the idiomatic collocation استجابةً لدليل أو مشكلة rather than استجابة إلى.'),
  ('text + question/answer q8','assessment_clarity','moderate','The text referred to two earlier options without stating them explicitly; name the fixed-seating and no-change alternatives and ask about those grounded options directly.'),
 ],
 'ar-b1-u10-p06':[
  ('question q2','grammar_wording','moderate','Repair the malformed ما سؤالان construction to the definite dual question ما السؤالان اللذان....'),
  ('question q8','grammar_wording','moderate','The head noun التعبير/الطريق is masculine, so the reference-resolution question must use يشير.'),
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
 inv=json.loads(INVENTORY.read_text(encoding='utf-8')); b1=inv.get('levels',{}).get('b1',{}); bound=b1.get('canonical_sha256')
 if not isinstance(bound,str) or len(bound)!=64 or actual!=bound: raise SystemExit(f'B1 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 10 review')
 rel=json.loads(RELEASE.read_text(encoding='utf-8')); ar=rel.get('languages',{}).get('arabic',{}); prog=ar.get('naturalness_review_progress',{})
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False or prog.get('fresh_records_reviewed')!=174 or prog.get('levels_completed')!=['A1','A2']: raise SystemExit('Arabic Gate B frontier drift: expected 174 reviewed with A1/A2 complete and B1 Unit 10 next')
 if not (DECISION_DIR/'b1_u09.json').exists() or (DECISION_DIR/'b1_u10.json').exists(): raise SystemExit('B1 decision frontier drift: Unit 9 must exist and Unit 10 must not')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(54,60)]!=EXPECTED_IDS: raise SystemExit('B1 Unit 10 layout/id drift')
 by={r['id']:r for r in rows}; before={pid:target_counts(by[pid]) for pid in EXPECTED_IDS}
 for pid in EXPECTED_IDS:
  r=by[pid]; text=r['text']
  for old,new in TEXT_REPAIRS.get(pid,[]): text=replace_once(text,old,new,f'{pid} text')
  r['text']=text; qs={q['id']:q for q in r.get('questions',[])}; aa={a['question_id']:a for a in r.get('answer_key',[])}; edits=QA_REPAIRS.get(pid,{})
  for qid,(old,new) in edits.get('questions',{}).items():
   if qs[qid].get('prompt')!=old: raise SystemExit(f'{pid}/{qid}: question drift: {qs[qid].get("prompt")!r}')
   qs[qid]['prompt']=new
  for qid,(old,new) in edits.get('answers',{}).items():
   if aa[qid].get('answer')!=old: raise SystemExit(f'{pid}/{qid}: answer drift: {aa[qid].get("answer")!r}')
   aa[qid]['answer']=new
  r['word_count']=wc(r['text'])
  if not 220<=r['word_count']<=350: raise SystemExit(f"{pid}: word count {r['word_count']} outside B1 band")
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
 if total!=10 or sum(bool(FINDING_META[p]) for p in EXPECTED_IDS)!=5: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'B1','unit':10,'records_reviewed':6,'records_with_findings':5,'fresh_findings':total,'pre_repair_canonical_sha256':actual,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

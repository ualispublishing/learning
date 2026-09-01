#!/usr/bin/env python3
"""Apply fresh Arabic Gate B B1 Unit 3 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/b1/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; RELEASE=READING/'RELEASE_STATUS.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'
EXPECTED_IDS=[f'ar-b1-u03-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-01 fresh Gate B naturalness review (B1 Unit 3): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied where needed; legitimate B1 grammar-in-context analysis retained; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-b1-u03-p02':[
  ('وإذا نجح المثال وحده، يبحث عن حالة مختلفة ليرى هل فهم القاعدة أم حفظ الحركة فقط.', 'وإذا نجح في المثال وحده، يبحث عن حالة مختلفة ليرى هل فهم القاعدة أم حفظ الحركة فقط.'),
 ],
 'ar-b1-u03-p05':[
  ('كانت تضع فقرتها في الموقع، وبعد ثوان تظهر اقتراحات تصحيح تحت الكلمات والجمل.', 'كانت تضع فقرتها في الموقع، وبعد ثوان تظهر اقتراحات للتصحيح تحت الكلمات والجمل.'),
 ],
 'ar-b1-u03-p06':[
  ('كان هدفها أن يصبح استخدامها أكثر قصدًا: أداة مناسبة، في وقت مناسب، مع سؤال واضح عن الفائدة والحدود.', 'كان هدفها أن يصبح استخدامها أكثر وعيًا: أداة مناسبة، في وقت مناسب، مع سؤال واضح عن الفائدة والحدود.'),
 ],
}
QA_REPAIRS={
 'ar-b1-u03-p02':{
  'questions':{
   'q1':('لماذا لا يكفي الفيديو الأول سامرًا؟','لماذا لا يكون الفيديو الأول كافيًا لسامر؟'),
   'q8':('ما وظيفة «إذا» في طريقة سامر لاختبار مثال جديد؟','ما وظيفة «إذا» في «وإذا نجح في المثال وحده، يبحث عن حالة مختلفة»؟'),
  },
  'answers':{
   'q8':('تقدم حالة اختبار محتملة وتربطها بالخطوة التالية التي يستخدمها للتحقق من الفهم.','تجعل نجاح سامر في مثال واحد شرطًا للبحث عن حالة مختلفة حتى يختبر هل فهم القاعدة أم حفظ الخطوات فقط.'),
  },
 },
 'ar-b1-u03-p04':{
  'questions':{'q5':('كيف تجمع قاعدة تسمية الملفات بين الحماية وإمكانية الوصول؟','كيف يجمع النظام الجديد بين الحماية وإمكانية الوصول؟')},
 },
 'ar-b1-u03-p05':{
  'questions':{'q6':('ما وظيفة «عندما» في وصف ما تفعله مريم حين يقدم النظام تصحيحًا يغيّر المعنى؟','ما وظيفة «عندما» في «عندما قدمت تصحيحًا يغيّر المعنى، لم تكتف برفضه»؟')},
 },
 'ar-b1-u03-p06':{
  'questions':{'q5':('ما المقصود بالاستخدام «الأكثر قصدًا» في النهاية؟','ما المقصود بالاستخدام «الأكثر وعيًا» في النهاية؟')},
 },
}
FINDING_META={
 'ar-b1-u03-p01':[],
 'ar-b1-u03-p02':[
  ('question q1','naturalness_idiomaticity','minor','Replace the awkward لماذا لا يكفي الفيديو الأول سامرًا؟ with the natural MSA wording لماذا لا يكون الفيديو الأول كافيًا لسامر؟'),
  ('text/question/answer q8','naturalness_and_assessment_alignment','moderate','Repair the malformed وإذا نجح المثال وحده to وإذا نجح في المثال وحده and bind the conditional question directly to that exact sentence.'),
 ],
 'ar-b1-u03-p03':[],
 'ar-b1-u03-p04':[
  ('question q5','assessment_alignment','moderate','The original question attributes both protection and access to the file-naming rule alone, while the answer describes the broader backup/shared-folder system. Ask about the system as a whole.'),
 ],
 'ar-b1-u03-p05':[
  ('text','naturalness_idiomaticity','minor','Replace the awkward nominal sequence اقتراحات تصحيح with the idiomatic اقتراحات للتصحيح.'),
  ('question q6','assessment_grounding','minor','Ground the عندما grammar item in the exact passage sentence rather than an indirect paraphrase using حين.'),
 ],
 'ar-b1-u03-p06':[
  ('text/question q5','naturalness_idiomaticity','moderate','Replace the calqued أكثر قصدًا with the natural learner-facing أكثر وعيًا and align the comprehension question to the repaired phrase.'),
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
 if not isinstance(bound,str) or len(bound)!=64 or actual!=bound: raise SystemExit(f'B1 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 3 review')
 rel=json.loads(RELEASE.read_text(encoding='utf-8')); ar=rel.get('languages',{}).get('arabic',{}); prog=ar.get('naturalness_review_progress',{})
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False or prog.get('fresh_records_reviewed')!=132 or prog.get('levels_completed')!=['A1','A2']: raise SystemExit('Arabic Gate B frontier drift: expected 132 reviewed with A1/A2 complete and B1 Unit 3 next')
 if not (DECISION_DIR/'b1_u02.json').exists() or (DECISION_DIR/'b1_u03.json').exists(): raise SystemExit('Gate B decision frontier drift: B1 Unit 2 must exist and B1 Unit 3 must not')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(12,18)]!=EXPECTED_IDS: raise SystemExit('B1 Unit 3 layout/id drift')
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
  if not 235<=r['word_count']<=340: raise SystemExit(f"{pid}: word count {r['word_count']} outside guarded B1 Unit 3 band")
  if target_counts(r)!=before[pid]: raise SystemExit(f'{pid}: new lexical target occurrence drift')
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
 if total!=6: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'B1','unit':3,'records_reviewed':6,'records_with_findings':4,'fresh_findings':total,'pre_repair_canonical_sha256':actual,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

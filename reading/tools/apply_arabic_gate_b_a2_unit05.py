#!/usr/bin/env python3
"""Apply fresh Arabic Gate B A2 Unit 5 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/a2/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; RELEASE=READING/'RELEASE_STATUS.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'
EXPECTED_IDS=[f'ar-a2-u05-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-01 fresh Gate B naturalness review (A2 Unit 5): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-a2-u05-p03':[
  ('في البداية بدت الفكرة كبيرة، لأنها احتاجت إلى زيارة الأماكن والتصوير والكتابة واختيار الصور.', 'في البداية بدا المشروع كبيرًا، لأنه احتاج إلى زيارة الأماكن والتصوير والكتابة واختيار الصور.'),
 ],
 'ar-a2-u05-p06':[
  ('وما المشروع الصغير الذي يمكن أن يجبرني على استخدام ما تعلمته؟', 'وما المشروع الصغير الذي يمكن أن يدفعني إلى استخدام ما تعلمته؟'),
 ],
}
QA_REPAIRS={
 'ar-a2-u05-p01':{'answers':{
  'q3':('التقاط الصور وتعلم كيفية تكوينها بصورة أفضل.','التقاط الصور وتعلم كيف تجعل الصورة أفضل.'),
  'q4':('نشاط يتنافس فيه المشاركون للحصول على نتيجة أو جائزة أفضل.','نشاط يتنافس فيه المشاركون للفوز أو للحصول على جائزة.'),
 }},
 'ar-a2-u05-p02':{'answers':{
  'q1':('تكتب ملاحظات عن محاولاتها وتقارنها في المتابعة مع المدرب.','تكتب ملاحظات عن محاولاتها ثم تراجعها مع المدرب في اللقاءات التالية.'),
  'q3':('تحليل ما نجح وما يحتاج إلى تغيير بدل الاختيار السريع فقط.','التفكير فيما نجح وما يحتاج إلى تغيير بدل الاختيار بسرعة.'),
  'q4':('الرجوع إلى المحاولات السابقة ومراقبة ما تغير مع الاستمرار.','الرجوع إلى المحاولات السابقة لمعرفة ما تغير مع الوقت.'),
 }},
 'ar-a2-u05-p04':{
  'questions':{'q10':('أكمل: بدأ الطفل ي_____ إلى زملائه الجدد.','أكمل: بدأ الطفل _____ إلى زملائه الجدد.')},
  'answers':{'q5':('لأن هدى لم تعد تشترط إنهاء كمية كبيرة في جلسة واحدة.','لأن هدى لم تعد تشعر أن عليها إنهاء كمية كبيرة في جلسة واحدة.')},
 },
 'ar-a2-u05-p05':{'answers':{
  'q4':('معرفة ومهارة تتكون من التجربة والفهم عبر الوقت.','معرفة ومهارة يكتسبهما الشخص من التجربة والفهم مع الوقت.'),
 }},
 'ar-a2-u05-p06':{
  'questions':{'q7':('أيهما أوسع زمنًا ومعرفة: محاولة تدريب واحدة أم خبرة؟','أيهما يدل على تعلم يتراكم مع الوقت: محاولة تدريب واحدة أم خبرة؟')},
  'answers':{
   'q1':('تحسين الهواية يحتاج إلى تدريب مقصود وتأمل ومتابعة وخطوات وعادات صغيرة.','تحسين مهارة في هواية يحتاج إلى تدريب مقصود وتفكير ومتابعة وخطوات وعادات صغيرة.'),
   'q10':('لأنها انتقلت من الحكم العام على نفسها إلى إدارة عملية التعلم نفسها.','لأنها صارت تسأل عن المهارة والخطوة والنتيجة التالية بدل أن تسأل فقط هل هي جيدة أم لا.'),
  },
 },
}
FINDING_META={
 'ar-a2-u05-p01':[
  ('answer q3','answer_wording','minor','Replace the abstract تكوينها phrasing with a direct A2 explanation of photography as taking and improving pictures.'),
  ('answer q4','semantic_precision','minor','Define a contest directly in terms of competing to win or receive a prize rather than an unclear أفضل نتيجة.'),
 ],
 'ar-a2-u05-p02':[
  ('answer q1','naturalness_idiomaticity','minor','Replace تقارنها في المتابعة with direct wording about reviewing attempts with the trainer in later meetings.'),
  ('answer q3','answer_wording','minor','Simplify the explanation of تفكير to considering what worked and what should change.'),
  ('answer q4','answer_wording','minor','Define متابعة as returning to earlier attempts to see what changes over time.'),
 ],
 'ar-a2-u05-p03':[
  ('text','reference_clarity','minor','Refer to the project itself as large rather than the vague idea, and align the following pronoun.'),
 ],
 'ar-a2-u05-p04':[
  ('answer q5','naturalness_idiomaticity','minor','Replace the formal تشترط إنهاء كمية كبيرة with a direct statement about not feeling she must finish a large amount at once.'),
  ('question q10','assessment_clarity','moderate','Remove the partial-word cloze ي_____ and ask for the complete target form يتعرف.'),
 ],
 'ar-a2-u05-p05':[
  ('answer q4','grammar_wording','moderate','Repair the singular agreement in معرفة ومهارة تتكون and state naturally how experience is acquired over time.'),
 ],
 'ar-a2-u05-p06':[
  ('text','naturalness_idiomaticity','minor','Replace the overly forceful يجبرني with يدفعني in the reflective project question.'),
  ('answer q1','semantic_precision','minor','A hobby itself is not what improves; describe improving a skill within a hobby.'),
  ('question q7','assessment_clarity','moderate','Replace the unnatural أوسع زمنًا ومعرفة comparison with a direct contrast about learning accumulated over time.'),
  ('answer q10','answer_wording','minor','Replace the abstract إدارة عملية التعلم نفسها with direct A2 wording about asking more specific learning questions.'),
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
 if not isinstance(bound,str) or len(bound)!=64 or actual!=bound: raise SystemExit(f'A2 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 5 review')
 rel=json.loads(RELEASE.read_text(encoding='utf-8')); ar=rel.get('languages',{}).get('arabic',{}); prog=ar.get('naturalness_review_progress',{})
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False or prog.get('fresh_records_reviewed')!=84 or prog.get('levels_completed')!=['A1']: raise SystemExit('Arabic Gate B frontier drift: expected 84 reviewed with A1 complete and A2 Unit 5 next')
 if not (DECISION_DIR/'a2_u04.json').exists() or (DECISION_DIR/'a2_u05.json').exists(): raise SystemExit('A2 decision frontier drift: Unit 4 must exist and Unit 5 must not')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(24,30)]!=EXPECTED_IDS: raise SystemExit('A2 Unit 5 layout/id drift')
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
 if total!=13: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'A2','unit':5,'records_reviewed':6,'records_with_findings':6,'fresh_findings':total,'pre_repair_canonical_sha256':actual,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

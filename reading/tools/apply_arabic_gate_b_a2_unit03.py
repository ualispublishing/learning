#!/usr/bin/env python3
"""Apply fresh Arabic Gate B A2 Unit 3 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/a2/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; RELEASE=READING/'RELEASE_STATUS.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'
EXPECTED_IDS=[f'ar-a2-u03-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-01 fresh Gate B naturalness review (A2 Unit 3): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-a2-u03-p01':[
  ('منحتها الصورة نظرة على فترة لا تحتفظ عنها بذكريات كثيرة.', 'أعطتها الصورة لمحة عن فترة لا تحتفظ عنها بذكريات كثيرة.'),
  ('بعد أن عادت إلى بيتها فتحت الصورة مجددًا على هاتفها، لأنها كانت قد التقطت لها نسخة.', 'بعد أن عادت إلى بيتها فتحت الصورة مجددًا على هاتفها، لأنها كانت قد حفظت نسخة منها هناك.'),
 ],
 'ar-a2-u03-p02':[
  ('في النهاية حفظت نسخة من التسجيل في هاتفها، ليس لأنه حدث مهم جدًا، بل لأنه جعل مساءً عاديًا من الماضي يبدو قريبًا مرة أخرى.', 'في النهاية حفظت نسخة من التسجيل في هاتفها، ليس لأن المناسبة كانت مهمة جدًا، بل لأنه جعل مساءً عاديًا من الماضي يبدو قريبًا مرة أخرى.'),
 ],
 'ar-a2-u03-p04':[
  ('لكن تفاصيل أخرى ظهرت عند طلاب قليلين فقط.', 'لكن تفاصيل أخرى ظهرت لدى عدد قليل من الطلاب فقط.'),
 ],
 'ar-a2-u03-p05':[
  ('أجاب الأب: بعض الأحداث تترك أثرًا واضحًا، لكن تفاصيل الأثر قد تختفي ثم تعود عندما نرى شيئًا مرتبطًا بها.', 'أجاب الأب: بعض الأحداث تترك أثرًا واضحًا، لكن هذا الأثر قد يبقى حتى عندما تختفي بعض تفاصيل الحدث، ثم تعود تلك التفاصيل عندما نرى شيئًا مرتبطًا به.'),
 ],
 'ar-a2-u03-p06':[
  ('اكتشفت أن صورة واحدة قد تجعلها تنظر إلى يوم قديم مجددًا، وأن تسجيلًا صوتيًا يعيد أصواتًا لا تستطيع الصورة حفظها.', 'اكتشفت أن صورة واحدة قد تجعلها تنظر إلى يوم قديم مجددًا، وأن تسجيلًا صوتيًا يعيد إليها أصواتًا لا تستطيع الصورة حفظها.'),
 ],
}
QA_REPAIRS={
 'ar-a2-u03-p01':{'answers':{
  'q3':('في وقت قريب من الحاضر.','منذ وقت قريب.'),
  'q4':('لتراها مرة أخرى وتلاحظ تفاصيل جديدة.','لتنظر إليها مرة أخرى وتلاحظ تفاصيل جديدة.'),
 }},
 'ar-a2-u03-p02':{'answers':{
  'q3':('ملف محفوظ يحتوي على أصوات حدث سابق.','ملف صوتي محفوظ من حدث سابق.'),
  'q4':('إلقاء نظر على الصور لفحصها بسرعة أو بعناية.','أن تنظر إلى الصور لفحصها.'),
 }},
 'ar-a2-u03-p03':{'answers':{
  'q4':('فترة من الوقت في الماضي.','وقت مضى.'),
 }},
 'ar-a2-u03-p04':{'answers':{
  'q4':('كان لدى نور اعتقاد في الماضي ثم تغير بعد التجربة.','كانت تعتقد شيئًا في الماضي ثم تغير رأيها بعد التجربة.'),
 }},
 'ar-a2-u03-p05':{'answers':{
  'q3':('علامة أو تأثيرًا يبقى من الحدث بعد انتهائه.','علامة أو تأثير يبقى بعد انتهاء الحدث.'),
 }},
 'ar-a2-u03-p06':{
  'questions':{
   'q8':('إلى ماذا تشير «كل مصدر» في الجملة الأخيرة؟','ما المصادر التي يقصدها النص بعبارة «كل مصدر» في الجملة الأخيرة؟'),
   'q10':('لماذا لا يحتاج مصدر واحد إلى حمل القصة كاملة؟','لماذا لا يكفي مصدر واحد وحده لإعادة بناء القصة كاملة؟'),
  },
 },
}
FINDING_META={
 'ar-a2-u03-p01':[
  ('text','naturalness_idiomaticity','minor','Replace the literal-sounding منحتها الصورة نظرة with the idiomatic أعطتها الصورة لمحة.'),
  ('text','naturalness_idiomaticity','minor','Replace the awkward التقطت لها نسخة description with a direct statement that a copy of the photo was saved on the phone.'),
  ('answer q3','semantic_precision','minor','Define مؤخرًا directly as something that happened a short time ago rather than vaguely near the present.'),
  ('answer q4','answer_wording','minor','Use تنظر إليها rather than تراها to match the repeated act of looking at the photo.'),
 ],
 'ar-a2-u03-p02':[
  ('text','reference_clarity','moderate','The antecedent of حدث incorrectly treats the recording itself as the event; refer to the occasion instead.'),
  ('answer q3','answer_wording','minor','Simplify the definition of تسجيل صوتي to a saved audio file from an earlier event.'),
  ('answer q4','answer_wording','minor','Define نظرة with direct learner-facing wording instead of the abstract speed-or-care formulation.'),
 ],
 'ar-a2-u03-p03':[
  ('answer q4','answer_wording','minor','Replace the redundant فترة من الوقت في الماضي definition of زمن مضى with direct A2 wording.'),
 ],
 'ar-a2-u03-p04':[
  ('text','naturalness_idiomaticity','minor','Use لدى عدد قليل من الطلاب rather than عند طلاب قليلين for details recalled by only a few students.'),
  ('answer q4','answer_wording','minor','Explain كنت أظن directly as a past belief that later changed, rather than describing an abstract اعتقاد.'),
 ],
 'ar-a2-u03-p05':[
  ('text','semantic_precision','moderate','Clarify that the أثر can remain while event details fade, while preserving the required أثر target exposure count.'),
  ('answer q3','grammar_wording','moderate','Repair the case mismatch in علامة أو تأثيرًا and give a grammatically parallel definition of أثر.'),
 ],
 'ar-a2-u03-p06':[
  ('text','naturalness_idiomaticity','minor','Add the object pronoun in يعيد إليها أصواتًا so the recording naturally brings sounds back to Noor.'),
  ('question q8','assessment_clarity','moderate','كل مصدر is not a referring pronoun; ask explicitly which sources the phrase denotes.'),
  ('question q10','naturalness_idiomaticity','minor','Replace حمل القصة كاملة with the natural question of whether one source is sufficient to reconstruct the whole story.'),
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
 if not isinstance(bound,str) or len(bound)!=64 or actual!=bound: raise SystemExit(f'A2 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 3 review')
 rel=json.loads(RELEASE.read_text(encoding='utf-8')); ar=rel.get('languages',{}).get('arabic',{}); prog=ar.get('naturalness_review_progress',{})
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False or prog.get('fresh_records_reviewed')!=72 or prog.get('levels_completed')!=['A1']: raise SystemExit('Arabic Gate B frontier drift: expected 72 reviewed with A1 complete and A2 Unit 3 next')
 if not (DECISION_DIR/'a2_u02.json').exists() or (DECISION_DIR/'a2_u03.json').exists(): raise SystemExit('A2 decision frontier drift: Unit 2 must exist and Unit 3 must not')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(12,18)]!=EXPECTED_IDS: raise SystemExit('A2 Unit 3 layout/id drift')
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
 if total!=15: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'A2','unit':3,'records_reviewed':6,'records_with_findings':6,'fresh_findings':total,'pre_repair_canonical_sha256':actual,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

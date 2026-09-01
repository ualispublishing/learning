#!/usr/bin/env python3
"""Apply fresh Arabic Gate B A1 Unit 9 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PATH=ROOT/'reading/arabic/a1/passages.jsonl'
EXPECTED_SHA256='236115dfb8ad693895f8e8703b5572d390ca328ba56a40b2ff3d5efa30fc38dd'
EXPECTED_IDS=[f'ar-a1-u09-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-01 fresh Gate B naturalness review (A1 Unit 9): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-a1-u09-p05':[('في نهاية الوقت يسجل فريق ليلى هدفًا آخر ويحقق فوزًا صغيرًا.','في نهاية الوقت يسجل فريق ليلى هدفًا آخر ويحقق الفوز.')],
 'ar-a1-u09-p06':[('أحيانًا يحملون كرة إلى الحديقة ويصبح كل شخص لاعبًا في لعبة قصيرة.','أحيانًا يحملون كرة إلى الحديقة ويكون كل شخص لاعبًا في لعبة قصيرة.')],
}
QA_REPAIRS={
 'ar-a1-u09-p01':{'answers':{
  'q3':('الشيء المستدير الذي يلعب به الأطفال.','شيء مستدير نلعب به.'),
 }},
 'ar-a1-u09-p02':{'answers':{
  'q7':('مكان أو جماعة لأنشطة مشتركة.','مكان يجتمع فيه الناس لأنشطة مشتركة.'),
 }},
 'ar-a1-u09-p03':{'answers':{
  'q7':('فرح أو مسرور.','مسرور.'),
 }},
 'ar-a1-u09-p04':{'answers':{
  'q3':('إمكان مناسب لفعل شيء أو تجربته.','وقت مناسب يمكنك فيه أن تفعل شيئًا.'),
  'q5':('لا، هي اختيار وفرصة.','لا، يمكن للطالب أن يشارك إذا أراد.'),
  'q6':('وقت أو إمكان مناسب لفعل شيء.','وقت مناسب يمكنك فيه أن تفعل شيئًا.'),
  'q7':('القيام بنشاط مع الآخرين أو أخذ جزء فيه.','أن تفعل نشاطًا مع الآخرين.'),
 }},
 'ar-a1-u09-p05':{'answers':{
  'q3':('إدخال الكرة بطريقة تزيد نتيجة الفريق.','نقطة يسجلها الفريق في المباراة.'),
  'q4':('أن ينتهي اللعب بنتيجة أفضل لفريق ليلى.','أن ينتهي اللعب وفريق ليلى هو الفائز.'),
  'q7':('النجاح على الطرف الآخر في مباراة أو منافسة.','أن تنتهي المباراة وفريقك هو الفائز.'),
 }},
 'ar-a1-u09-p06':{'answers':{
  'q1':('ليلى تستمتع بوقت الفراغ من خلال أنشطة وأصدقاء مختلفة، لا من خلال الفوز فقط.','ليلى تستمتع بوقت الفراغ من خلال أنشطة مختلفة ومع أصدقائها، لا من خلال الفوز فقط.'),
  'q4':('لأنها تستمتع بالأصدقاء والتجربة والوقت نفسه.','لأنها تستمتع بوقتها مع أصدقائها وبالتجربة نفسها.'),
  'q6':('إمكان مناسب لفعل شيء.','وقت مناسب يمكنك فيه أن تفعل شيئًا.'),
 }},
}
FINDING_META={
 'ar-a1-u09-p01':[
  ('answer q3','answer_wording','minor','Define كرة concretely for an A1 learner rather than with the broad الشيء المستدير wording.'),
 ],
 'ar-a1-u09-p02':[
  ('answer q7','semantic_precision','minor','Keep نادي in the place sense taught by this passage rather than broadening the definition to a place or group.'),
 ],
 'ar-a1-u09-p03':[
  ('answer q7','answer_wording','minor','Replace the mismatched noun/adjective gloss فرح أو مسرور with a direct adjective meaning for سعيد.'),
 ],
 'ar-a1-u09-p04':[
  ('answer q3','answer_wording','minor','Replace the abstract إمكان مناسب wording with a direct A1 explanation of فرصة.'),
  ('answer q5','answer_wording','minor','Answer the voluntary-participation question directly instead of saying participation is an اختيار وفرصة.'),
  ('answer q6','answer_wording','minor','Simplify the standalone definition of فرصة to direct learner-facing wording.'),
  ('answer q7','naturalness_idiomaticity','minor','Replace the literal أخذ جزء فيه wording with a natural explanation of مشاركة.'),
 ],
 'ar-a1-u09-p05':[
  ('text','naturalness_idiomaticity','minor','Replace the awkward فوزًا صغيرًا collocation with the natural يحقق الفوز.'),
  ('answer q3','semantic_precision','minor','Explain a match هدف as a scored point rather than the vague إدخال الكرة بطريقة تزيد نتيجة الفريق.'),
  ('answer q4','answer_wording','minor','Explain فوز through the team ending as the winner rather than an abstract better-result formulation.'),
  ('answer q7','naturalness_idiomaticity','minor','Replace النجاح على الطرف الآخر with a natural A1 definition of winning a match.'),
 ],
 'ar-a1-u09-p06':[
  ('text','naturalness_idiomaticity','minor','Replace يصبح كل شخص لاعبًا with the natural stable-role wording يكون كل شخص لاعبًا.'),
  ('answer q1','grammar_agreement','moderate','Repair the mixed-coordination agreement defect in أنشطة وأصدقاء مختلفة by separating the activity and friend phrases.'),
  ('answer q4','naturalness_idiomaticity','minor','Replace تستمتع بالأصدقاء with the natural تستمتع بوقتها مع أصدقائها wording.'),
  ('answer q6','answer_wording','minor','Simplify the cumulative definition of فرصة for A1 learners.'),
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
 if actual!=EXPECTED_SHA256: raise SystemExit(f'A1 canonical drift: expected {EXPECTED_SHA256}, got {actual}; rebind Unit 9 review')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(48,54)]!=EXPECTED_IDS: raise SystemExit('A1 Unit 9 layout/id drift')
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
 if total!=15: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'A1','unit':9,'records_reviewed':6,'records_with_findings':6,'fresh_findings':total,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Apply fresh Arabic Gate B B1 Unit 7 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/b1/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; RELEASE=READING/'RELEASE_STATUS.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'
EXPECTED_IDS=[f'ar-b1-u07-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-02 fresh Gate B naturalness review (B1 Unit 7): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied where needed; legitimate B1 grammar-in-context analysis retained; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-b1-u07-p04':[
  ('اتفقتا على إعلان تاريخ النشاط والعناصر المؤكدة، ووضع عبارة واضحة بأنهم سيحدّثون بقية التفاصيل لاحقًا.', 'اتفقتا على إعلان تاريخ النشاط والعناصر المؤكدة، مع عبارة واضحة تفيد بأن بقية التفاصيل ستُحدَّث لاحقًا.'),
  ('أي قاعة تحقق أكبر قدر من الوصول من غير أن تفسد الأجزاء التي تحتاج إلى هدوء؟', 'أي قاعة تتيح وصولًا أسهل من غير أن تفسد الأجزاء التي تحتاج إلى هدوء؟'),
 ],
 'ar-b1-u07-p05':[
  ('استغرقت الاجتماعات طويلًا، وشعر بعضهم أن لا أحد يستطيع إنجاز مهمة مستقلة من غير انتظار المجموعة.', 'استغرقت الاجتماعات وقتًا طويلًا، وشعر بعضهم أن لا أحد يستطيع إنجاز مهمة مستقلة من غير انتظار المجموعة.'),
 ],
}
QA_REPAIRS={
 'ar-b1-u07-p01':{
  'questions':{
   'q4':('كيف يصلحان سوء الفهم؟','كيف تصلحان سوء الفهم؟'),
  },
 },
 'ar-b1-u07-p03':{
  'answers':{
   'q9':('استلم أو وصل إليه شيء مثل رسالة أو تعليق أو خبر.','استلم شيئًا أو وصله شيء مثل رسالة أو تعليق أو خبر.'),
  },
 },
 'ar-b1-u07-p04':{
  'answers':{
   'q8':('تضع قيدًا على تحقيق فائدة الوصول: ينبغي ألا يؤدي ذلك إلى إفساد الفقرات التي تحتاج إلى هدوء.','تضع قيدًا على تفضيل سهولة الوصول: ينبغي ألا يؤدي ذلك إلى إفساد الفقرات التي تحتاج إلى هدوء.'),
  },
 },
}
FINDING_META={
 'ar-b1-u07-p01':[
  ('question q4','grammar_gender_agreement','minor','The question refers to the two female participants نور وهدى but uses masculine dual يصلحان; restore feminine dual تصلحان.'),
 ],
 'ar-b1-u07-p02':[],
 'ar-b1-u07-p03':[
  ('answer q9','definition_grammar_and_naturalness','minor','Complete the first branch of the definition of تلقى by supplying its object and use the idiomatic وصله شيء in the second branch.'),
 ],
 'ar-b1-u07-p04':[
  ('text','reference_clarity_and_naturalness','minor','Replace the ambiguous بأنهم سيحدّثون after the dual-feminine subject with an impersonal passive formulation that preserves the intended plan.'),
  ('text/answer q8','lexical_naturalness','minor','Replace the calqued أكبر قدر من الوصول / فائدة الوصول phrasing with natural wording around ease of access while preserving the tradeoff with quiet.'),
 ],
 'ar-b1-u07-p05':[
  ('text','naturalness_duration_construction','minor','Replace the unidiomatic استغرقت الاجتماعات طويلًا with the standard duration construction استغرقت الاجتماعات وقتًا طويلًا.'),
 ],
 'ar-b1-u07-p06':[],
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
 if not isinstance(bound,str) or len(bound)!=64 or actual!=bound: raise SystemExit(f'B1 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 7 review')
 rel=json.loads(RELEASE.read_text(encoding='utf-8')); ar=rel.get('languages',{}).get('arabic',{}); prog=ar.get('naturalness_review_progress',{})
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False or prog.get('fresh_records_reviewed')!=156 or prog.get('levels_completed')!=['A1','A2']: raise SystemExit('Arabic Gate B frontier drift: expected 156 reviewed with A1/A2 complete and B1 Unit 7 next')
 if not (DECISION_DIR/'b1_u06.json').exists() or (DECISION_DIR/'b1_u07.json').exists(): raise SystemExit('Gate B decision frontier drift: B1 Unit 6 must exist and B1 Unit 7 must not')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(36,42)]!=EXPECTED_IDS: raise SystemExit('B1 Unit 7 layout/id drift')
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
  if not 220<=r['word_count']<=340: raise SystemExit(f"{pid}: word count {r['word_count']} outside guarded B1 Unit 7 band")
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
 if total!=5: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'B1','unit':7,'records_reviewed':6,'records_with_findings':4,'fresh_findings':total,'pre_repair_canonical_sha256':actual,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

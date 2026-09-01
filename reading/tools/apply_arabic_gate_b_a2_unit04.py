#!/usr/bin/env python3
"""Apply fresh Arabic Gate B A2 Unit 4 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/a2/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; RELEASE=READING/'RELEASE_STATUS.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'
EXPECTED_IDS=[f'ar-a2-u04-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-01 fresh Gate B naturalness review (A2 Unit 4): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-a2-u04-p01':[
  ('قالت الأم: المقارنة ليست بين السعر فقط؛ علينا أن نقارن الحجم والكمية وما نحتاج إليه فعلًا.', 'قالت الأم: لا ينبغي أن تعتمد المقارنة على السعر فقط؛ علينا أن نقارن الحجم والكمية وما نحتاج إليه فعلًا.'),
 ],
 'ar-a2-u04-p02':[
  ('قال أبوها: الصفقة الحقيقية تعتمد على ما تحتاجين إليه، لا على كلمة «خصم» وحدها.', 'قال أبوها: الصفقة الجيدة تعتمد على ما تحتاجين إليه، لا على كلمة «خصم» وحدها.'),
 ],
 'ar-a2-u04-p03':[
  ('قالت: التطبيق مفيد، لكن الشيء المفيد لا يستحق الشراء تلقائيًا؛ القيمة تعتمد على مقدار استخدامي له.', 'قالت: التطبيق مفيد، لكن ليس كل شيء مفيد يستحق الشراء تلقائيًا؛ القيمة تعتمد على مقدار استخدامي له.'),
 ],
 'ar-a2-u04-p04':[
  ('عمل هذه المرة بصورة طبيعية.', 'عمل هذه المرة كما ينبغي.'),
 ],
 'ar-a2-u04-p05':[
  ('توقف كرسي مكتب نور عن الثبات لأن إحدى قطعه ارتخت.', 'لم يعد كرسي مكتب نور ثابتًا لأن إحدى قطعه ارتخت.'),
  ('قال العامل إن الإصلاح بسيط ولا يحتاج إلى قطعة غالية، وإن الكرسي بعد الإصلاح قد يستمر سنوات أخرى.', 'قال العامل إن الإصلاح بسيط ولا يحتاج إلى قطعة غيار غالية، وإن الكرسي بعد الإصلاح قد يستمر سنوات أخرى.'),
  ('لكن في هذه الحالة كان الإصلاح أقل ثمنًا ولم يجعل الشيء أسوأ، لذلك كان القرار أسهل.', 'لكن في هذه الحالة كان الإصلاح أقل ثمنًا ولم يجعل الكرسي أسوأ، لذلك كان القرار أسهل.'),
 ],
 'ar-a2-u04-p06':[
  ('وفي الأشياء الرقمية، مثل اشتراك في تطبيق، تفكر هل الاستخدام المتوقع يستحق المبلغ.', 'وفي الأشياء الرقمية، مثل اشتراك في تطبيق، تفكر هل ستستخدم التطبيق بما يكفي ليستحق المبلغ.'),
  ('وأحيانًا يكون الإصلاح أغلى أو يجعل النتيجة أسوأ على المدى القريب.', 'وأحيانًا يكون الإصلاح أغلى أو تكون النتيجة بعده أسوأ.'),
 ],
}
QA_REPAIRS={
 'ar-a2-u04-p01':{'answers':{
  'q3':('مقدار كبر أو صغر العبوة أو الشيء.','مقدار كبر الشيء أو صغره.'),
 }},
 'ar-a2-u04-p02':{'answers':{
  'q4':('شراء يعطي قيمة مناسبة أو فائدة جيدة مقارنة بما يدفعه الشخص ويحتاج إليه.','شراء مفيد بسعر مناسب لما يحتاج إليه الشخص.'),
  'q7':('اتفاق أو عملية شراء، وقد توصف بالجيدة إذا كانت قيمتها مناسبة.','عملية شراء أو اتفاق، وهنا تعني عملية شراء.'),
 }},
 'ar-a2-u04-p03':{'answers':{
  'q3':('أن فائدته وقيمته تبرران المبلغ المدفوع.','أن فائدته مناسبة للمبلغ الذي ندفعه.'),
  'q8':('حتى تعتمد على استعمالها الحقيقي في قرار الاشتراك.','حتى تعرف هل تستخدمها بما يكفي قبل أن تشترك.'),
 }},
 'ar-a2-u04-p05':{'answers':{
  'q3':('إعادة الشيء المعطل أو المتضرر إلى حالة تعمل جيدًا.','إعادة الشيء المعطل أو المتضرر إلى حالة جيدة ليعمل كما ينبغي.'),
 }},
 'ar-a2-u04-p06':{
  'questions':{
   'q4':('لماذا لا تعني الصفقة دائمًا شراءً جيدًا؟','لماذا لا يعني العرض أو الخصم دائمًا صفقة جيدة؟'),
  },
  'answers':{
   'q6':('تكون قيمته كافية لما يُدفع مقابله.','تكون فائدته مناسبة للثمن المدفوع.'),
  },
 },
}
FINDING_META={
 'ar-a2-u04-p01':[
  ('text','naturalness_idiomaticity','moderate','Replace المقارنة ليست بين السعر فقط with a natural statement that comparison should not depend on price alone.'),
  ('answer q3','answer_wording','minor','Define حجم with the direct phrase مقدار كبر الشيء أو صغره.'),
 ],
 'ar-a2-u04-p02':[
  ('text','naturalness_idiomaticity','minor','Use الصفقة الجيدة rather than the unnatural evaluative phrase الصفقة الحقيقية.'),
  ('answer q4','answer_wording','minor','Replace the abstract value formulation with a direct A2 explanation of a good deal.'),
  ('answer q7','semantic_precision','minor','Define صفقة as a purchase or agreement without implying that the word itself means a good-value purchase.'),
 ],
 'ar-a2-u04-p03':[
  ('text','naturalness_idiomaticity','minor','Repair الشيء المفيد لا يستحق الشراء تلقائيًا to the natural ليس كل شيء مفيد construction.'),
  ('answer q3','answer_wording','minor','Explain يستحق الثمن directly as benefit being appropriate for the amount paid.'),
  ('answer q8','answer_wording','minor','State the practical reason for tracking use: to know whether the new exercises are used enough before subscribing.'),
 ],
 'ar-a2-u04-p04':[
  ('text','naturalness_idiomaticity','minor','Replace عمل بصورة طبيعية with the idiomatic عمل كما ينبغي for a functioning lamp.'),
 ],
 'ar-a2-u04-p05':[
  ('text','naturalness_idiomaticity','moderate','Replace توقف الكرسي عن الثبات with the direct لم يعد الكرسي ثابتًا.'),
  ('text','semantic_precision','minor','Specify قطعة غيار when describing a replacement part needed for a repair.'),
  ('text','reference_clarity','minor','Refer to the chair directly rather than the vague الشيء in the repair conclusion.'),
  ('answer q3','answer_wording','minor','Define إصلاح with a direct statement about returning a damaged object to good working condition.'),
 ],
 'ar-a2-u04-p06':[
  ('text','semantic_precision','moderate','Usage itself does not deserve a price; state whether Noor will use the app enough for it to be worth the amount.'),
  ('text','naturalness_idiomaticity','minor','Replace يجعل النتيجة أسوأ على المدى القريب with a direct comparison of the post-repair result.'),
  ('question q4','assessment_clarity','moderate','A صفقة is not inherently a good purchase; ask why an offer or discount does not always amount to a good deal.'),
  ('answer q6','answer_wording','minor','Define يستحق with direct benefit-versus-price wording.'),
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
 if not isinstance(bound,str) or len(bound)!=64 or actual!=bound: raise SystemExit(f'A2 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 4 review')
 rel=json.loads(RELEASE.read_text(encoding='utf-8')); ar=rel.get('languages',{}).get('arabic',{}); prog=ar.get('naturalness_review_progress',{})
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False or prog.get('fresh_records_reviewed')!=78 or prog.get('levels_completed')!=['A1']: raise SystemExit('Arabic Gate B frontier drift: expected 78 reviewed with A1 complete and A2 Unit 4 next')
 if not (DECISION_DIR/'a2_u03.json').exists() or (DECISION_DIR/'a2_u04.json').exists(): raise SystemExit('A2 decision frontier drift: Unit 3 must exist and Unit 4 must not')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(18,24)]!=EXPECTED_IDS: raise SystemExit('A2 Unit 4 layout/id drift')
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
 if total!=17: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'A2','unit':4,'records_reviewed':6,'records_with_findings':6,'fresh_findings':total,'pre_repair_canonical_sha256':actual,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

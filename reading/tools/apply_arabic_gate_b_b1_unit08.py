#!/usr/bin/env python3
"""Apply fresh Arabic Gate B B1 Unit 8 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/b1/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; RELEASE=READING/'RELEASE_STATUS.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'
EXPECTED_IDS=[f'ar-b1-u08-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-02 fresh Gate B naturalness review (B1 Unit 8): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied where needed; legitimate B1 grammar-in-context analysis retained; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-b1-u08-p05':[
  ('ولكي تختبر الفرق، اختار الطلاب مؤشرًا ثانيًا: عدد الزيارات إلى المكتبة، لا عدد الاستعارات فقط.','ولاختبار الفرق، اختار الطلاب مؤشرًا ثانيًا: عدد الزيارات إلى المكتبة، لا عدد الاستعارات فقط.'),
 ],
}
QA_REPAIRS={
 'ar-b1-u08-p02':{'questions':{'q6':('ما وظيفة «حتى» في «حتى الوصول إلى مصدر أصلي لا يكفي إذا كان القارئ يعتمد نسخة قديمة»؟','ما وظيفة «حتى» في «حتى الوصول إلى مصدر أصلي لا يكفي إذا كان القارئ يعتمد على نسخة قديمة منه»؟')}},
 'ar-b1-u08-p04':{'answers':{'q7':('عدد الأماكن التي عرضت الكلام مقابل عدد المصادر المستقلة التي أنتجته أو تحققته.','عدد الأماكن التي عرضت الكلام مقابل عدد المصادر المستقلة التي أنتجته أو تحققت منه.')}},
 'ar-b1-u08-p06':{
  'questions':{'q6':('ما وظيفة «لكن» في قول النص إن نور لم تستنتج أن البرنامج لم يفد ولم تقبل السبب بوصفه مؤكدًا؟','ما وظيفة تكرار «لم» في «لم تستنتج أن البرنامج لم يفد، ولم تقبل السبب المقترح بوصفه مؤكدًا»؟')},
  'answers':{'q6':('تجنب نتيجتين متطرفتين وتبقي التفسير مفتوحًا أمام أكثر من احتمال تدعمه الأدلة بدرجات مختلفة.','يستبعد احتمالين متطرفين: أن البرنامج لم يفد أصلًا، وأن السبب المقترح مؤكد، فيبقي التفسير مفتوحًا أمام أكثر من احتمال تدعمه الأدلة بدرجات مختلفة.')},
 },
}
FINDING_META={
 'ar-b1-u08-p01':[],
 'ar-b1-u08-p02':[('question q6','quoted_grammar_grounding','minor','Restore the omitted preposition على and pronoun منه so the quoted clause exactly matches the grammatical wording in the passage.')],
 'ar-b1-u08-p03':[],
 'ar-b1-u08-p04':[('answer q7','verb_complement_grammar','minor','Replace the invalid transitive تحققته construction with the standard تحققت منه complement.')],
 'ar-b1-u08-p05':[('text','purpose_clause_subject_alignment','minor','Replace the dangling feminine-singular purpose clause ولكي تختبر الفرق before the plural subject الطلاب with the neutral purpose phrase ولاختبار الفرق.')],
 'ar-b1-u08-p06':[('question/answer q6','grammar_grounding_and_answer_alignment','minor','The question attributes لكن to a sentence that contains no لكن; bind the task to the repeated لم construction actually present and align the answer with the two negated extremes.')],
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
 if not isinstance(bound,str) or len(bound)!=64 or actual!=bound: raise SystemExit(f'B1 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 8 review')
 rel=json.loads(RELEASE.read_text(encoding='utf-8')); ar=rel.get('languages',{}).get('arabic',{}); prog=ar.get('naturalness_review_progress',{}); det=ar.get('latest_deterministic_gate',{})
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False or prog.get('fresh_records_reviewed')!=162 or prog.get('fresh_records_with_findings')!=142 or prog.get('fresh_findings')!=278 or prog.get('levels_completed')!=['A1','A2'] or det.get('open_findings')!=1872: raise SystemExit('Arabic Gate B frontier drift: expected 162 reviewed / 142 records with findings / 278 findings / 1872 blockers with A1/A2 complete and B1 Unit 8 next')
 if not (DECISION_DIR/'b1_u07.json').exists() or (DECISION_DIR/'b1_u08.json').exists(): raise SystemExit('Gate B decision frontier drift: B1 Unit 7 must exist and B1 Unit 8 must not')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(42,48)]!=EXPECTED_IDS: raise SystemExit('B1 Unit 8 layout/id drift')
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
  if not 220<=r['word_count']<=340: raise SystemExit(f"{pid}: word count {r['word_count']} outside guarded B1 Unit 8 band")
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
 if total!=4: raise SystemExit(f'finding metadata drift: {total}')
 PATH.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 print(json.dumps({'level':'B1','unit':8,'records_reviewed':6,'records_with_findings':4,'fresh_findings':total,'pre_repair_canonical_sha256':actual,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

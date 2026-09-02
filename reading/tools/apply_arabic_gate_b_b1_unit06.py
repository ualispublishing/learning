#!/usr/bin/env python3
"""Apply fresh Arabic Gate B B1 Unit 6 naturalness/Q&A repairs."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; READING=ROOT/'reading'; PATH=READING/'arabic/b1/passages.jsonl'; INVENTORY=READING/'audit/arabic_gate_b_naturalness_inventory_2026-08-30.json'; RELEASE=READING/'RELEASE_STATUS.json'; DECISION_DIR=READING/'audit/arabic_gate_b_decisions_2026-08-30'
EXPECTED_IDS=[f'ar-b1-u06-p{i:02d}' for i in range(1,7)]; TOKEN=re.compile(r'\S+')
NOTE='2026-09-02 fresh Gate B naturalness review (B1 Unit 6): learner-facing prose/Q/A reviewed passage by passage; bounded repairs applied where needed; legitimate B1 grammar-in-context analysis retained; no educator/publication release claim.'
TEXT_REPAIRS={
 'ar-b1-u06-p01':[
  ('لم تستبدل نور منظورًا بمنظور واحد جديد؛ صارت تجمع أوصافًا لها أغراض مختلفة، وتسأل في كل مرة ما الذي يظهره المصدر وما الذي يتركه خارج الصورة.', 'لم تستبدل نور منظورًا بآخر جديد؛ صارت تجمع أوصافًا لها أغراض مختلفة، وتسأل في كل مرة ما الذي يظهره المصدر وما الذي يتركه خارج الصورة.'),
 ],
 'ar-b1-u06-p03':[
  ('كانت الترجمة مفهومة نحويًا، لكنها بدت شديدة ومباشرة أكثر مما أرادت.', 'كانت الترجمة مفهومة نحويًا، لكنها بدت أشد لهجة وأكثر مباشرة مما أرادت.'),
 ],
 'ar-b1-u06-p04':[
  ('في مطار خلال رحلة خيالية سمع سامر وهدى إعلانًا جويًا يقول إن مجموعة من المسافرين مطلوب منها التوجه إلى مكتب قرب البوابة.', 'في مطار خلال رحلة خيالية سمع سامر وهدى إعلانًا في صالة السفر الجوي يقول إن مجموعة من المسافرين مطلوب منها التوجه إلى مكتب قرب البوابة.'),
 ],
}
FIELD_REPAIRS={
 'ar-b1-u06-p04':{
  'title':('إعلان جوي فهمه شخصان بطريقتين','إعلان في المطار فهمه شخصان بطريقتين'),
 },
}
QA_REPAIRS={
 'ar-b1-u06-p02':{
  'questions':{
   'q2':('ماذا تقدم الأسرة له عند وصوله؟','ماذا تقدم له الأسرة، وماذا تطلب منه عند وصوله؟'),
  },
 },
 'ar-b1-u06-p04':{
  'questions':{
   'q9':('ما معنى «جوي» في «إعلان جوي»؟','ما معنى «جوي» في «السفر الجوي»؟'),
  },
 },
 'ar-b1-u06-p06':{
  'answers':{
   'q5':('سوء الفهم يُصلح أفضل عندما نميز بين التجربة المحددة والحكم الواسع ونبحث عن السياق الناقص.','يُعالَج سوء الفهم على نحو أفضل عندما نميز بين التجربة المحددة والحكم الواسع ونبحث عن السياق الناقص.'),
  },
 },
}
FINDING_META={
 'ar-b1-u06-p01':[
  ('text','naturalness_idiomaticity','minor','Replace the awkward لم تستبدل نور منظورًا بمنظور واحد جديد with the idiomatic contrast لم تستبدل نور منظورًا بآخر جديد.'),
 ],
 'ar-b1-u06-p02':[
  ('question q2','assessment_alignment','minor','The prompt asks only what the family offers, while the keyed answer also includes what it asks Samer to do. Expand the prompt so both keyed details are explicitly requested.'),
 ],
 'ar-b1-u06-p03':[
  ('text','naturalness_comparative','minor','Replace the malformed comparative بدت شديدة ومباشرة أكثر مما أرادت with the natural MSA بدت أشد لهجة وأكثر مباشرة مما أرادت.'),
 ],
 'ar-b1-u06-p04':[
  ('text/title/question q9','lexical_naturalness_and_grounding','moderate','Avoid the forced collocation إعلان جوي. Ground جوي naturally in السفر الجوي, retitle the passage as an airport announcement, and align q9 to the exact natural phrase.'),
 ],
 'ar-b1-u06-p05':[],
 'ar-b1-u06-p06':[
  ('answer q5','naturalness_grammar','minor','Replace the unidiomatic سوء الفهم يُصلح أفضل with the standard passive construction يُعالَج سوء الفهم على نحو أفضل.'),
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
 if not isinstance(bound,str) or len(bound)!=64 or actual!=bound: raise SystemExit(f'B1 canonical/inventory drift: canonical={actual}, inventory={bound}; rebind Unit 6 review')
 rel=json.loads(RELEASE.read_text(encoding='utf-8')); ar=rel.get('languages',{}).get('arabic',{}); prog=ar.get('naturalness_review_progress',{})
 if ar.get('release_state')!='REOPEN_REQUIRED' or ar.get('educator_release_ready') is not False or prog.get('fresh_records_reviewed')!=150 or prog.get('levels_completed')!=['A1','A2']: raise SystemExit('Arabic Gate B frontier drift: expected 150 reviewed with A1/A2 complete and B1 Unit 6 next')
 if not (DECISION_DIR/'b1_u05.json').exists() or (DECISION_DIR/'b1_u06.json').exists(): raise SystemExit('Gate B decision frontier drift: B1 Unit 5 must exist and B1 Unit 6 must not')
 rows=[json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)) or [rows[i].get('id') for i in range(30,36)]!=EXPECTED_IDS: raise SystemExit('B1 Unit 6 layout/id drift')
 by={r['id']:r for r in rows}; before={pid:target_counts(by[pid]) for pid in EXPECTED_IDS}
 for pid in EXPECTED_IDS:
  r=by[pid]; text=r['text']
  for old,new in TEXT_REPAIRS.get(pid,[]): text=replace_once(text,old,new,f'{pid} text')
  r['text']=text
  for field,(old,new) in FIELD_REPAIRS.get(pid,{}).items():
   if r.get(field)!=old: raise SystemExit(f'{pid}/{field}: field drift')
   r[field]=new
  qs={q['id']:q for q in r.get('questions',[])}; aa={a['question_id']:a for a in r.get('answer_key',[])}; edits=QA_REPAIRS.get(pid,{})
  for qid,(old,new) in edits.get('questions',{}).items():
   if qs[qid].get('prompt')!=old: raise SystemExit(f'{pid}/{qid}: question drift')
   qs[qid]['prompt']=new
  for qid,(old,new) in edits.get('answers',{}).items():
   if aa[qid].get('answer')!=old: raise SystemExit(f'{pid}/{qid}: answer drift')
   aa[qid]['answer']=new
  r['word_count']=wc(r['text'])
  if not 220<=r['word_count']<=340: raise SystemExit(f"{pid}: word count {r['word_count']} outside guarded B1 Unit 6 band")
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
 print(json.dumps({'level':'B1','unit':6,'records_reviewed':6,'records_with_findings':5,'fresh_findings':total,'pre_repair_canonical_sha256':actual,'post_repair_canonical_sha256':sha(PATH.read_bytes()),'word_counts':{p:by[p]['word_count'] for p in EXPECTED_IDS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Strict post-generation audit for French C2 Unit01 calibration."""
from __future__ import annotations
import csv,json,re,subprocess
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_b1_unit10 as u10
base=u10.base
R=Path(__file__).resolve().parents[2];A1=R/'reading/french/a1/passages.jsonl';A2=R/'reading/french/a2/passages.jsonl';B1=R/'reading/french/b1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';C1=R/'reading/french/c1/passages.jsonl';C2=R/'reading/french/c2/passages.jsonl';SCHEMA=R/'reading/schema/passage.schema.json';C1IN=R/'reading/audit/french_c1_generation_integrity.json';READY=R/'reading/audit/french_c2_readiness.json';SEL=R/'reading/audit/french_c2_unit01_target_selection.json';LEX3=R/'french_top3000.csv';OUT=R/'reading/audit/french_c2_unit01_calibration_review.json'
def h(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def load(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def deck3():
 out={}
 with LEX3.open(encoding='utf-8',newline='') as f:
  for row in csv.DictReader(f):
   form=(row.get('Front') or '').strip();b=row.get('Back') or '';mr=re.search(r'Rank:\s*(\d+)',b)
   if form and mr:out[form]=int(mr.group(1))
 return out
def main():
 integ=json.loads(C1IN.read_text());ready=json.loads(READY.read_text());sel=json.loads(SEL.read_text());c1=h(C1);rows=load(C2);blob=h(C2);prior=load(A1)+load(A2)+load(B1)+load(B2)+load(C1)
 if integ.get('status')!='PASS' or integ.get('canonical_blob')!=c1 or ready.get('status')!='PASS' or ready.get('c1_canonical_blob')!=c1:raise AssertionError('C2 calibration requires sealed C1/readiness')
 if sel.get('status')!='PASS' or sel.get('c1_source_blob')!=c1 or sel.get('calibration_new_targets_per_standard_passage')!=5:raise AssertionError('C2 selection/readiness mismatch')
 if len(rows)!=6 or [r['id'] for r in rows]!=[f'fr-c2-u01-p{i:02d}' for i in range(1,7)] or [r['sequence'] for r in rows]!=list(range(1,7)):raise AssertionError('C2 Unit01 exact six-row frontier required')
 V=Draft202012Validator(json.loads(SCHEMA.read_text()));D=deck3();pid={t['id'] for r in prior for t in r.get('new_lexical_targets',[])};pf={t['form'] for r in prior for t in r.get('new_lexical_targets',[])};new=[];qtypes=Counter();wcs=[];language_repairs=[]
 banned_fragments=['Le lecteur C2','À C2,','audit de','calibration C2','pipeline','frontier lock']
 for i,r in enumerate(rows,1):
  errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
  if errs:raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:10]]}")
  wc=len(r['text'].split());wcs.append(wc)
  if r['word_count']!=wc or not 700<=wc<=1200:raise AssertionError(f"{r['id']}: word band/count {r['word_count']} actual={wc}")
  if len(r['questions'])!=10 or len(r['answer_key'])!=10:raise AssertionError(f"{r['id']}: expected 10 Q/A")
  qtypes.update(q['type'] for q in r['questions']);local={t['id'] for fld in ('new_lexical_targets','review_lexical_targets') for t in r.get(fld,[])};amap={a['question_id']:a['id'] for a in r['answer_key']}
  for q in r['questions']:
   if amap.get(q['id'])!=q['answer_id'] or any(x not in local for x in q.get('target_ids',[])):raise AssertionError(f"{r['id']} {q['id']}: linkage failure")
  count=len(r.get('new_lexical_targets',[]))
  if i<=5 and count!=5:raise AssertionError(f"{r['id']}: calibration standard passage expected 5 new targets, got {count}")
  if i==6 and count!=0:raise AssertionError('C2 Unit01 checkpoint must be zero-new')
  for frag in banned_fragments:
   if frag.lower() in r['text'].lower():language_repairs.append({'passage':r['id'],'fragment':frag})
  for t in r.get('new_lexical_targets',[]):
   rank=D.get(t['form']);exact=base.cnt(r['text'],t['form'])
   if not rank or rank<=1000 or t.get('source_lexicon')!='french_top3000.csv' or t.get('source_rank')!=rank or t['id']!=base.tid(rank):raise AssertionError(f"{r['id']}: invalid C2 advanced source identity {t}")
   if t['id'] in pid or t['form'] in pf:raise AssertionError(f"{r['id']}: prior-level collision {t['form']}")
   if exact<1 or exact!=t['exposures_in_text']:raise AssertionError(f"{r['id']}: exact exposure drift {t['form']}")
   new.append(t)
  for t in r.get('review_lexical_targets',[]):
   if t.get('representation') in {'running_text','summary'} and base.cnt(r['text'],t['form'])<1:raise AssertionError(f"{r['id']}: invisible review {t['form']}")
 if language_repairs:raise AssertionError(f'learner-facing internal/curriculum language requires repair: {language_repairs}')
 if len(new)!=25 or len({t['id'] for t in new})!=25 or len({t['form'] for t in new})!=25:raise AssertionError('C2 Unit01 must have 25 unique new targets')
 if {t['form'] for t in new}!={x['form'] for x in sel['selected']}:raise AssertionError('C2 selection/canonical target mismatch')
 p3,p4=rows[2],rows[3]
 if not p3.get('paired_text_group') or p3.get('paired_text_group')!=p4.get('paired_text_group'):raise AssertionError('C2 P03/P04 paired group missing')
 ratio=SequenceMatcher(None,p3['text'],p4['text']).ratio()
 if ratio>=0.50:raise AssertionError(f'C2 paired texts insufficiently distinct: {ratio:.3f}')
 required={'main_claim','ambiguity_resolution','assumption','rhetorical_function','stance','vocabulary_in_context','cross_text_synthesis','register_style','inference','summary','synthesis'}
 if not required.issubset(qtypes):raise AssertionError(f'C2 question coverage missing {sorted(required-set(qtypes))}')
 markers=('contre-exemple','contreargument','contre-argument','rivale','rival','révision','portée','ambigu')
 density={r['id']:sum(m in r['text'].lower() for m in markers) for r in rows[:5]}
 if any(v<2 for v in density.values()):raise AssertionError(f'C2 conceptual reasoning density too low {density}')
 out={'status':'PASS','scope':'French C2 Unit01 strict calibration review','c1_canonical_blob':c1,'c2_canonical_blob':blob,'theme':ready['unit01_theme'],'genres':ready['unit01_genres'],'passages':6,'questions':60,'answers':60,'word_counts':wcs,'word_band':[700,1200],'unique_new_target_ids':25,'unique_new_target_forms':25,'source_policy':'french_top3000.csv rank > 1000','prior_level_collisions':0,'checkpoint_zero_new':True,'paired_text_group':p3['paired_text_group'],'paired_text_similarity_ratio':round(ratio,4),'question_type_counts':dict(sorted(qtypes.items())),'reasoning_density':density,'schema':'PASS','linkage':'PASS','source_identity':'PASS','exact_exposure':'PASS','exact_review_visibility':'PASS','learner_facing_language':'PASS','pedagogical_review':'PASS','accepted_c2_default_new_targets_per_standard_passage':5,'accepted_default_is_hard_quota':False,'durable_lexical_planning_band':ready['c2_lexical_planning_band'],'note':'Five new targets is accepted as conservative C2 production default after calibration, below the maximum planning band; increase only when discourse load permits.'}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

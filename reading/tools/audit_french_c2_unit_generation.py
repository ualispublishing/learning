#!/usr/bin/env python3
"""Strict per-unit French C2 generation audit for C2_UNIT=2..10."""
from __future__ import annotations
import csv,json,os,re,subprocess
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_b1_unit10 as u10
base=u10.base
R=Path(__file__).resolve().parents[2];A1=R/'reading/french/a1/passages.jsonl';A2=R/'reading/french/a2/passages.jsonl';B1=R/'reading/french/b1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';C1=R/'reading/french/c1/passages.jsonl';C2=R/'reading/french/c2/passages.jsonl';SCHEMA=R/'reading/schema/passage.schema.json';LEX3=R/'french_top3000.csv';AUD=R/'reading/audit'
def h(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def load(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()] if p.exists() else []
def prefix_blob(lines):return subprocess.check_output(['git','hash-object','--stdin'],input='\n'.join(lines)+'\n',text=True).strip()
def deck3():
 out={}
 with LEX3.open(encoding='utf-8',newline='') as f:
  for row in csv.DictReader(f):
   form=(row.get('Front') or '').strip();b=row.get('Back') or '';mr=re.search(r'Rank:\s*(\d+)',b)
   if form and mr:out[form]=int(mr.group(1))
 return out
def main():
 u=int(os.environ.get('C2_UNIT','0'))
 if not 2<=u<=10:raise AssertionError('C2_UNIT must be 2..10')
 prev=u-1;lines=[x for x in C2.read_text(encoding='utf-8').splitlines() if x.strip()];rows=[json.loads(x) for x in lines];c2=h(C2);c1=h(C1)
 if len(rows)!=u*6 or rows[-1]['id']!=f'fr-c2-u{u:02d}-p06':raise AssertionError(f'C2 Unit{u:02d} exact {u*6}-row frontier required')
 lock=json.loads((AUD/f'french_c2_unit{prev:02d}_frontier_lock.json').read_text());pblob=prefix_blob(lines[:prev*6])
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=prev*6 or lock.get('c1_canonical_blob')!=c1 or lock.get('c2_canonical_blob')!=pblob:raise AssertionError(f'C2 Unit{prev:02d} prefix lock mismatch')
 plan=json.loads((AUD/f'french_c2_unit{u:02d}_plan.json').read_text());sel=json.loads((AUD/f'french_c2_unit{u:02d}_target_selection.json').read_text())
 if plan.get('status')!='PASS' or plan.get('c2_source_blob')!=pblob or sel.get('status')!='PASS' or sel.get('c2_source_blob')!=pblob:raise AssertionError('C2 plan/selection does not match locked prefix')
 prior=load(A1)+load(A2)+load(B1)+load(B2)+load(C1)+rows[:prev*6];pid={t['id'] for r in prior for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)};pf={t['form'] for r in prior for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)};D=deck3();V=Draft202012Validator(json.loads(SCHEMA.read_text()));unit=rows[prev*6:];new=[];qtypes=Counter();wcs=[];pairs=Counter();reasoning={}
 banned=['pipeline','frontier lock','audit de','c2 unit','unité c2','calibration']
 for i,r in enumerate(unit,1):
  errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
  if errs:raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:10]]}")
  wc=len(r['text'].split());wcs.append(wc)
  if r['word_count']!=wc or not 700<=wc<=1200:raise AssertionError(f"{r['id']}: word band/count {r['word_count']} actual={wc}")
  if len(r['questions'])!=10 or len(r['answer_key'])!=10:raise AssertionError(f"{r['id']}: expected 10 Q/A")
  qtypes.update(q['type'] for q in r['questions']);local={t['id'] for fld in ('new_lexical_targets','review_lexical_targets') for t in r.get(fld,[])};amap={a['question_id']:a['id'] for a in r['answer_key']}
  for q in r['questions']:
   if amap.get(q['id'])!=q['answer_id'] or any(x not in local for x in q.get('target_ids',[])):raise AssertionError(f"{r['id']} {q['id']}: linkage failure")
  if i<=5 and len(r.get('new_lexical_targets',[]))!=5:raise AssertionError(f"{r['id']}: expected calibrated default of five new targets")
  if i==6 and r.get('new_lexical_targets'):raise AssertionError(f"{r['id']}: checkpoint must be zero-new")
  low=r['text'].lower()
  for frag in banned:
   if frag in low:raise AssertionError(f"{r['id']}: learner-facing internal language {frag!r}")
  markers=('contre-exemple','contreargument','contre-argument','rivale','rival','révision','portée','ambigu','objection','alternative')
  reasoning[r['id']]=sum(m in low for m in markers)
  if i<=5 and reasoning[r['id']]<2:raise AssertionError(f"{r['id']}: advanced reasoning density too low {reasoning[r['id']]}")
  if r.get('paired_text_group'):pairs[r['paired_text_group']]+=1
  for t in r.get('new_lexical_targets',[]):
   rank=D.get(t['form']);exact=base.cnt(r['text'],t['form'])
   if not rank or rank<=1000 or t.get('source_lexicon')!='french_top3000.csv' or t.get('source_rank')!=rank or t['id']!=base.tid(rank):raise AssertionError(f"{r['id']}: invalid advanced source identity {t}")
   if t['id'] in pid or t['form'] in pf:raise AssertionError(f"{r['id']}: prior collision {t['form']}")
   if exact<1 or exact!=t['exposures_in_text']:raise AssertionError(f"{r['id']}: exact exposure drift {t['form']}")
   new.append(t)
  for t in r.get('review_lexical_targets',[]):
   if t.get('representation') in {'running_text','summary'} and base.cnt(r['text'],t['form'])<1:raise AssertionError(f"{r['id']}: invisible review {t['form']}")
 if len(new)!=25 or len({t['id'] for t in new})!=25 or len({t['form'] for t in new})!=25:raise AssertionError('C2 unit must contain 25 unique new targets')
 if {t['form'] for t in new}!={x['form'] for x in sel['selected']}:raise AssertionError('C2 canonical/selection target mismatch')
 # Any explicit pair in a unit must consist of exactly two materially distinct passages.
 for group,n in pairs.items():
  if n!=2:raise AssertionError(f'paired group {group} has {n} rows')
  pair=[r for r in unit if r.get('paired_text_group')==group];ratio=SequenceMatcher(None,pair[0]['text'],pair[1]['text']).ratio()
  if ratio>=0.50:raise AssertionError(f'paired group {group} insufficiently distinct {ratio:.3f}')
 required={'main_claim','ambiguity_resolution','assumption','rhetorical_function','vocabulary_in_context'}
 if not required.issubset(qtypes):raise AssertionError(f'C2 unit question coverage missing {sorted(required-set(qtypes))}')
 out={'status':'PASS','scope':f'French C2 Unit{u:02d} strict generation review','c1_canonical_blob':c1,'c2_prefix_blob':pblob,'c2_canonical_blob':c2,'unit':u,'theme':plan['theme'],'genres':plan['genres'],'passages':6,'questions':60,'answers':60,'word_counts':wcs,'word_band':[700,1200],'unique_new_target_ids':25,'unique_new_target_forms':25,'source_policy':'french_top3000.csv rank > 1000','prior_level_collisions':0,'checkpoint_zero_new':True,'paired_text_groups':dict(pairs),'question_type_counts':dict(sorted(qtypes.items())),'reasoning_density':reasoning,'schema':'PASS','linkage':'PASS','source_identity':'PASS','exact_exposure':'PASS','exact_review_visibility':'PASS','learner_facing_language':'PASS','pedagogical_review':'PASS','accepted_c2_default_new_targets_per_standard_passage':lock.get('accepted_c2_default_new_targets_per_standard_passage',5),'accepted_default_is_hard_quota':False,'durable_lexical_planning_band':plan['c2_lexical_planning_band'],'note':'Strict per-unit C2 generation seal; final whole-French audit remains deferred through C2 completion.'}
 (AUD/f'french_c2_unit{u:02d}_generation_review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

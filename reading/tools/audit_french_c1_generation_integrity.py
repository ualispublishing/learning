#!/usr/bin/env python3
"""Full French C1 generation-integrity seal; final whole-French audit remains deferred through C2."""
from __future__ import annotations
import json,subprocess
from collections import Counter
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_b1_unit10 as u10
base=u10.base
R=Path(__file__).resolve().parents[2];A1=R/'reading/french/a1/passages.jsonl';A2=R/'reading/french/a2/passages.jsonl';B1=R/'reading/french/b1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';C1=R/'reading/french/c1/passages.jsonl';SCHEMA=R/'reading/schema/passage.schema.json';OUT=R/'reading/audit/french_c1_generation_integrity.json'
EXPECTED={'A1':'0493a2fa13e51b5997db05e91cdea4d8dc5e647b','A2':'d0a80b8866071f426019aa0ad143e1d270dba4de','B1':'4a2cd9ff30c3cea58caf20fca2822b06200622ca','B2':'38976211f13329ba3e2b0b9dbd6868699023d05d'}
def load(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
 prior=[]
 for lab,p in [('A1',A1),('A2',A2),('B1',B1),('B2',B2)]:
  got=subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
  if got!=EXPECTED[lab]:raise AssertionError(f'{lab} source blob drift {got} != {EXPECTED[lab]}')
  prior+=load(p)
 rows=load(C1);blob=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip()
 if len(rows)!=60 or [r['sequence'] for r in rows]!=list(range(1,61)):raise AssertionError('C1 must contain exact sequences 1-60')
 if [r['id'] for r in rows]!=[f'fr-c1-u{u:02d}-p{p:02d}' for u in range(1,11) for p in range(1,7)]:raise AssertionError('C1 ID ordering failure')
 V=Draft202012Validator(json.loads(SCHEMA.read_text()));deck=base.deck();pid={t['id'] for r in prior for t in r.get('new_lexical_targets',[])};pf={t['form'] for r in prior for t in r.get('new_lexical_targets',[])};ids=[];forms=[];questions=answers=0;checkpoints=[];units={};qtypes=Counter();pairs=Counter();wcs={}
 for r in rows:
  errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
  if errs:raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:8]]}")
  wc=len(r['text'].split());wcs[r['id']]=wc
  if r['word_count']!=wc or not 500<=wc<=800:raise AssertionError(f"{r['id']}: C1 word band/count {r['word_count']} actual={wc}")
  if len(r['questions'])!=10 or len(r['answer_key'])!=10:raise AssertionError(f"{r['id']}: expected 10 Q/A")
  questions+=10;answers+=10;qtypes.update(q['type'] for q in r['questions'])
  if r.get('paired_text_group'):pairs[r['paired_text_group']]+=1
  local={t['id'] for fld in ('new_lexical_targets','review_lexical_targets') for t in r.get(fld,[])};amap={a['question_id']:a['id'] for a in r['answer_key']}
  for q in r['questions']:
   if amap.get(q['id'])!=q['answer_id'] or any(x not in local for x in q.get('target_ids',[])):raise AssertionError(f"{r['id']} {q['id']}: linkage failure")
  u=r['unit'];units.setdefault(u,{'passages':0,'new_targets':0,'checkpoint_zero_new':None});units[u]['passages']+=1
  if r['sequence']%6==0:
   checkpoints.append(r['sequence']);units[u]['checkpoint_zero_new']=(not r.get('new_lexical_targets'))
   if r.get('new_lexical_targets'):raise AssertionError(f"{r['id']}: checkpoint introduced new targets")
  elif len(r.get('new_lexical_targets',[]))!=4:raise AssertionError(f"{r['id']}: standard C1 passage must have four new targets")
  units[u]['new_targets']+=len(r.get('new_lexical_targets',[]))
  for t in r.get('new_lexical_targets',[]):
   src=deck.get(t['form']);exact=base.cnt(r['text'],t['form'])
   if not src or t['source_rank']!=src['rank'] or t['id']!=base.tid(src['rank']):raise AssertionError(f"{r['id']}: source identity {t}")
   if t['id'] in pid or t['form'] in pf:raise AssertionError(f"{r['id']}: prior-level collision {t['form']}")
   if exact<1 or exact!=t['exposures_in_text']:raise AssertionError(f"{r['id']}: exposure drift {t['form']}")
   ids.append(t['id']);forms.append(t['form'])
  for t in r.get('review_lexical_targets',[]):
   if t.get('representation') in {'running_text','summary'} and base.cnt(r['text'],t['form'])<1:raise AssertionError(f"{r['id']}: invisible exact review {t['form']}")
 if questions!=600 or answers!=600:raise AssertionError('C1 Q/A totals must be 600/600')
 if len(ids)!=200 or len(set(ids))!=200 or len(set(forms))!=200:raise AssertionError('C1 must contain 200 unique deliberate targets')
 if set(ids)&pid or set(forms)&pf:raise AssertionError('C1 prior-level collision')
 if checkpoints!=[6,12,18,24,30,36,42,48,54,60]:raise AssertionError(f'C1 checkpoint drift {checkpoints}')
 if set(units)!=set(range(1,11)) or any(v['passages']!=6 or v['new_targets']!=20 or v['checkpoint_zero_new'] is not True for v in units.values()):raise AssertionError(f'C1 unit structure drift {units}')
 if any(v!=2 for v in pairs.values()):raise AssertionError(f'C1 paired group size drift {dict(pairs)}')
 required={'main_claim','argument_relation','assumption','inference','stance','summary','vocabulary_in_context','cross_text_synthesis','synthesis'}
 if not required.issubset(qtypes):raise AssertionError(f'C1 question coverage missing {sorted(required-set(qtypes))}')
 out={'status':'PASS','scope':'French C1 generation integrity','canonical_blob':blob,'passages':60,'questions':600,'answers':600,'units':10,'unique_new_target_ids':200,'unique_new_target_forms':200,'prior_level_collisions':0,'checkpoint_sequences_zero_new':checkpoints,'unit_structure':units,'word_count_min':min(wcs.values()),'word_count_max':max(wcs.values()),'question_type_counts':dict(sorted(qtypes.items())),'paired_text_groups':dict(sorted(pairs.items())),'source_identity':'PASS','exposure_counts':'PASS','exact_reviews':'PASS','schema':'PASS','linkage':'PASS','word_band':'PASS','accepted_c1_default_new_targets_per_standard_passage':4,'accepted_default_is_hard_quota':False,'note':'Generation-integrity seal only. Full final French multi-pass audit remains deferred until C2 is complete.'}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

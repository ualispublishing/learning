#!/usr/bin/env python3
"""Full French B2 generation-integrity audit.

This is a generation seal, not the deferred final whole-French language-wide
multi-pass audit. It validates the complete 60-passage B2 canonical layer and
all vocabulary/source/linkage invariants needed before C1 generation begins.
"""
from __future__ import annotations
import json,re,subprocess
from collections import Counter
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_b1_unit10 as u10
base=u10.base
R=Path(__file__).resolve().parents[2]
A1=R/'reading/french/a1/passages.jsonl';A2=R/'reading/french/a2/passages.jsonl';B1=R/'reading/french/b1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';SCHEMA=R/'reading/schema/passage.schema.json';OUT=R/'reading/audit/french_b2_generation_integrity.json'
EXPECTED_PRIOR={'A1':'0493a2fa13e51b5997db05e91cdea4d8dc5e647b','A2':'d0a80b8866071f426019aa0ad143e1d270dba4de','B1':'4a2cd9ff30c3cea58caf20fca2822b06200622ca'}
def load(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
 for lab,p in [('A1',A1),('A2',A2),('B1',B1)]:
  got=subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
  if got!=EXPECTED_PRIOR[lab]:raise AssertionError(f'{lab} source blob drift: {got} != {EXPECTED_PRIOR[lab]}')
 prior_rows=load(A1)+load(A2)+load(B1);rows=load(B2);blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if len(rows)!=60 or [r.get('sequence') for r in rows]!=list(range(1,61)):raise AssertionError('B2 must contain exact sequences 1-60')
 if [r.get('id') for r in rows]!=[f'fr-b2-u{u:02d}-p{p:02d}' for u in range(1,11) for p in range(1,7)]:raise AssertionError('B2 id/unit ordering failure')
 V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')));deck=base.deck();prior_ids={t.get('id') for r in prior_rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)};prior_forms={t.get('form') for r in prior_rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)}
 new_ids=[];new_forms=[];questions=answers=0;checkpoint_sequences=[];unit_counts={};word_counts={};qtypes=Counter();paired=Counter()
 for r in rows:
  errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
  if errs:raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:8]]}")
  if not 350<=r['word_count']<=550 or r['word_count']!=len(r['text'].split()):raise AssertionError(f"{r['id']}: word band/count {r['word_count']} vs {len(r['text'].split())}")
  if len(r['questions'])!=10 or len(r['answer_key'])!=10:raise AssertionError(f"{r['id']}: expected 10 Q/A")
  questions+=len(r['questions']);answers+=len(r['answer_key']);word_counts[r['id']]=r['word_count'];qtypes.update(q.get('type') for q in r['questions'])
  if r.get('paired_text_group'):paired[r['paired_text_group']]+=1
  local={t['id'] for fld in ('new_lexical_targets','review_lexical_targets') for t in r.get(fld,[])};amap={a['question_id']:a['id'] for a in r['answer_key']}
  for q in r['questions']:
   if amap.get(q['id'])!=q['answer_id']:raise AssertionError(f"{r['id']} {q['id']}: answer linkage failure")
   bad=[x for x in q.get('target_ids',[]) if x not in local]
   if bad:raise AssertionError(f"{r['id']} {q['id']}: non-local targets {bad}")
  u=r['unit'];unit_counts.setdefault(u,{'passages':0,'new_targets':0,'checkpoint_zero_new':None});unit_counts[u]['passages']+=1
  if r['sequence']%6==0:
   checkpoint_sequences.append(r['sequence']);unit_counts[u]['checkpoint_zero_new']=(len(r.get('new_lexical_targets',[]))==0)
   if r.get('new_lexical_targets'):raise AssertionError(f"{r['id']}: checkpoint introduced new targets")
  else:
   if len(r.get('new_lexical_targets',[]))!=4:raise AssertionError(f"{r['id']}: standard passage must have four new targets")
  unit_counts[u]['new_targets']+=len(r.get('new_lexical_targets',[]))
  for t in r.get('new_lexical_targets',[]):
   src=deck.get(t.get('form'))
   if not src:raise AssertionError(f"{r['id']}: missing source term {t.get('form')}")
   if t['source_rank']!=src['rank'] or t['id']!=base.tid(src['rank']):raise AssertionError(f"{r['id']}: source identity drift {t}")
   if t['id'] in prior_ids or t['form'] in prior_forms:raise AssertionError(f"{r['id']}: prior-level collision {t['form']}")
   exact=base.cnt(r['text'],t['form'])
   if exact!=t['exposures_in_text'] or exact<1:raise AssertionError(f"{r['id']}: exposure drift {t['form']} stored={t['exposures_in_text']} actual={exact}")
   new_ids.append(t['id']);new_forms.append(t['form'])
  for t in r.get('review_lexical_targets',[]):
   if t.get('representation') in {'running_text','summary'} and base.cnt(r['text'],t['form'])<1:raise AssertionError(f"{r['id']}: invisible exact review {t['form']}")
 if questions!=600 or answers!=600:raise AssertionError(f'B2 Q/A totals {questions}/{answers}, expected 600/600')
 if len(new_ids)!=200 or len(set(new_ids))!=200 or len(set(new_forms))!=200:raise AssertionError('B2 must contain 200 unique deliberate new targets')
 if set(new_ids)&prior_ids or set(new_forms)&prior_forms:raise AssertionError('B2 target collision with A1-A2-B1')
 if checkpoint_sequences!=[6,12,18,24,30,36,42,48,54,60]:raise AssertionError(f'checkpoint sequence drift {checkpoint_sequences}')
 if set(unit_counts)!=set(range(1,11)) or any(v['passages']!=6 or v['new_targets']!=20 or v['checkpoint_zero_new'] is not True for v in unit_counts.values()):raise AssertionError(f'unit structure drift {unit_counts}')
 # Paired groups must be actual pairs, never singleton/overloaded groups.
 if any(n!=2 for n in paired.values()):raise AssertionError(f'paired text group size drift {dict(paired)}')
 out={'status':'PASS','scope':'French B2 generation integrity','canonical_blob':blob,'passages':60,'questions':600,'answers':600,'units':10,'unique_new_target_ids':200,'unique_new_target_forms':200,'prior_level_collisions':0,'checkpoint_sequences_zero_new':checkpoint_sequences,'unit_structure':unit_counts,'word_count_min':min(word_counts.values()),'word_count_max':max(word_counts.values()),'question_type_counts':dict(sorted(qtypes.items())),'paired_text_groups':dict(sorted(paired.items())),'source_identity':'PASS','exposure_counts':'PASS','exact_reviews':'PASS','schema':'PASS','linkage':'PASS','word_band':'PASS','note':'Generation-integrity seal only. Full final French language-wide multi-pass audit remains deferred until C1-C2 generation is complete.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

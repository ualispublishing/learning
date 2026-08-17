#!/usr/bin/env python3
"""Strict post-calibration audit for French C1 Unit01.

This audit decides whether the conservative four-new-target calibration load is
acceptable as the C1 production default. It does not grant final French approval.
The default remains a production default rather than a hard quota.
"""
from __future__ import annotations
import json,re,subprocess
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_b1_unit10 as u10
base=u10.base
R=Path(__file__).resolve().parents[2]
A1=R/'reading/french/a1/passages.jsonl';A2=R/'reading/french/a2/passages.jsonl';B1=R/'reading/french/b1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';C1=R/'reading/french/c1/passages.jsonl';SCHEMA=R/'reading/schema/passage.schema.json'
B2AUD=R/'reading/audit/french_b2_generation_integrity.json';READY=R/'reading/audit/french_c1_readiness.json';PLAN=R/'reading/audit/french_c1_unit01_plan.json';PROBE=R/'reading/audit/french_c1_unit01_target_probe.json';SEL=R/'reading/audit/french_c1_unit01_target_selection.json';OUT=R/'reading/audit/french_c1_unit01_calibration_review.json'
EXPECTED_PRIOR={'A1':'0493a2fa13e51b5997db05e91cdea4d8dc5e647b','A2':'d0a80b8866071f426019aa0ad143e1d270dba4de','B1':'4a2cd9ff30c3cea58caf20fca2822b06200622ca'}
BANNED_TEXT=[r'(?i)source[- ]?backed',r'(?i)\btarget(?:s)?\b',r'(?i)\bcalibration\b',r'(?i)semantic fallback',r'(?i)audited? fallback',r'(?i)curriculum metadata']
REQUIRED_TYPES={'main_claim','argument_relation','assumption','inference','stance','summary','vocabulary_in_context'}

def load(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def paragraphs(text):return [x.strip() for x in text.split('\n\n') if x.strip()]
def norm(s):return re.sub(r'\s+',' ',s.lower()).strip()
def main():
 for lab,p in [('A1',A1),('A2',A2),('B1',B1)]:
  got=subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
  if got!=EXPECTED_PRIOR[lab]:raise AssertionError(f'{lab} blob drift: {got} != {EXPECTED_PRIOR[lab]}')
 b2aud=json.loads(B2AUD.read_text(encoding='utf-8'));ready=json.loads(READY.read_text(encoding='utf-8'));plan=json.loads(PLAN.read_text(encoding='utf-8'));probe=json.loads(PROBE.read_text(encoding='utf-8'));sel=json.loads(SEL.read_text(encoding='utf-8'))
 b2blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if b2aud.get('status')!='PASS' or b2aud.get('canonical_blob')!=b2blob or b2aud.get('passages')!=60:raise AssertionError('B2 generation seal/live blob mismatch')
 for name,obj in [('readiness',ready),('plan',plan),('probe',probe),('selection',sel)]:
  if obj.get('status')!='PASS' or obj.get('b2_canonical_blob')!=b2blob:raise AssertionError(f'C1 {name} artifact missing/stale')
 lo,hi=int(ready['c1_word_min']),int(ready['c1_word_max'])
 if (lo,hi)!=(int(plan['c1_word_min']),int(plan['c1_word_max'])) or (lo,hi)!=(int(probe['c1_word_min']),int(probe['c1_word_max'])):raise AssertionError('C1 word-band artifact disagreement')
 hints=sel.get('explicit_lexical_load_hints',[])
 if any(int(x[0])>4 for x in hints):raise AssertionError(f'canonical C1 standard requires higher lexical minimum than calibration load: {hints}')
 rows=load(C1)
 if len(rows)!=6 or [r['sequence'] for r in rows]!=list(range(1,7)) or [r['id'] for r in rows]!=[f'fr-c1-u01-p{i:02d}' for i in range(1,7)]:raise AssertionError('C1 Unit01 canonical identity/order failure')
 V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')));prior=load(A1)+load(A2)+load(B1)+load(B2);prior_ids={t['id'] for r in prior for t in r.get('new_lexical_targets',[])};prior_forms={t['form'] for r in prior for t in r.get('new_lexical_targets',[])};deck=base.deck();selected={x['form'] for x in sel['selected']}
 qtypes=Counter();new=[];word_counts=[];paragraph_counts=[];language_flags=[];pedagogy={}
 for r in rows:
  errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
  if errs:raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:8]]}")
  wc=len(r['text'].split());word_counts.append(wc);paragraph_counts.append(len(paragraphs(r['text'])))
  if r['word_count']!=wc or not lo<=wc<=hi:raise AssertionError(f"{r['id']}: C1 word band/count failure {r['word_count']} / {wc}, band {lo}-{hi}")
  if len(paragraphs(r['text']))<4:raise AssertionError(f"{r['id']}: expected at least four paragraphs")
  if len(r['questions'])!=10 or len(r['answer_key'])!=10:raise AssertionError(f"{r['id']}: expected 10 Q/A")
  if r['sequence']<=5 and len(r['new_lexical_targets'])!=4:raise AssertionError(f"{r['id']}: expected four calibration new targets")
  if r['sequence']==6 and r['new_lexical_targets']:raise AssertionError('C1 checkpoint must be zero-new')
  local={t['id'] for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[])};amap={a['question_id']:a['id'] for a in r['answer_key']}
  for q in r['questions']:
   qtypes[q['type']]+=1
   if amap.get(q['id'])!=q['answer_id'] or any(x not in local for x in q.get('target_ids',[])):raise AssertionError(f"{r['id']} {q['id']}: local linkage failure")
  for t in r.get('new_lexical_targets',[]):
   src=deck.get(t['form'])
   if not src or t['id'] in prior_ids or t['form'] in prior_forms or t['source_rank']!=src['rank'] or t['id']!=base.tid(src['rank']):raise AssertionError(f"{r['id']}: source/freshness failure {t}")
   exact=base.cnt(r['text'],t['form'])
   if exact<1 or exact!=t['exposures_in_text']:raise AssertionError(f"{r['id']}: exposure failure {t['form']} stored={t['exposures_in_text']} actual={exact}")
   new.append(t)
  for t in r.get('review_lexical_targets',[]):
   if t.get('representation') in {'running_text','summary'} and base.cnt(r['text'],t['form'])<1:raise AssertionError(f"{r['id']}: invisible exact review {t['form']}")
  for pat in BANNED_TEXT:
   if re.search(pat,r['text']):language_flags.append({'id':r['id'],'pattern':pat})
  # C1-specific pedagogy: each standard passage must explicitly contain at least
  # three of these reasoning functions; Unit01 as a whole must cover them all.
  textn=norm(r['text'])
  checks={
   'scope':any(x in textn for x in ['portée','condition','limite','validité','généralisation']),
   'counterargument':any(x in textn for x in ['objection','contreargument','position concurrente','argument opposé','désaccord']),
   'uncertainty_or_revision':any(x in textn for x in ['incertitude','révision','réviser','modifier','changer la conclusion','provisoire']),
   'source_method':any(x in textn for x in ['source','méthode','donnée','preuve','témoignage','archive','statistique']),
   'normative_bridge':any(x in textn for x in ['valeur','critère','normatif','acceptable','équité','risque','recommandation','décision'])
  }
  pedagogy[r['id']]=checks
  if r['sequence']<=5 and sum(checks.values())<3:raise AssertionError(f"{r['id']}: insufficient C1 reasoning-function density {checks}")
 if language_flags:raise AssertionError(f'learner-facing internal/audit wording detected: {language_flags}')
 if len(new)!=20 or len({t['id'] for t in new})!=20 or len({t['form'] for t in new})!=20 or {t['form'] for t in new}!=selected:raise AssertionError('C1 calibration target set/uniqueness failure')
 if set(t['id'] for t in new)&prior_ids or set(t['form'] for t in new)&prior_forms:raise AssertionError('C1 target collision with A1-B2')
 if not REQUIRED_TYPES.issubset(set(qtypes)):raise AssertionError(f'C1 question-type coverage missing {sorted(REQUIRED_TYPES-set(qtypes))}')
 # C1 calibration should include at least one cross-text task because P02/P03 are paired.
 if qtypes.get('cross_text_synthesis',0)<1:raise AssertionError('C1 calibration lacks cross-text synthesis assessment')
 pair='fr-c1-u01-action-under-uncertainty-viewpoints'
 if rows[1].get('paired_text_group')!=pair or rows[2].get('paired_text_group')!=pair or any(rows[i].get('paired_text_group') is not None for i in (0,3,4,5)):raise AssertionError('C1 paired-text structure failure')
 similarity=SequenceMatcher(None,norm(rows[1]['text']),norm(rows[2]['text'])).ratio()
 if similarity>=0.45:raise AssertionError(f'C1 paired viewpoints insufficiently distinct: similarity={similarity:.4f}')
 whole={k:any(v[k] for v in pedagogy.values()) for k in next(iter(pedagogy.values()))}
 if not all(whole.values()):raise AssertionError(f'C1 calibration missing reasoning dimension across unit: {whole}')
 c1blob=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip()
 out={'status':'PASS','scope':'French C1 Unit 01 calibration review','b2_canonical_blob':b2blob,'c1_canonical_blob':c1blob,'theme':plan.get('theme'),'genres':plan.get('genres'),'word_band':[lo,hi],'word_counts':word_counts,'paragraph_counts':paragraph_counts,'passages':6,'questions':60,'answers':60,'unique_new_target_ids':20,'unique_new_target_forms':20,'prior_level_collisions':0,'checkpoint_zero_new':True,'question_type_counts':dict(sorted(qtypes.items())),'paired_group':pair,'paired_similarity_ratio':round(similarity,4),'language_review':'PASS','pedagogical_review':'PASS','source_identity':'PASS','exposure_counts':'PASS','exact_reviews':'PASS','schema':'PASS','linkage':'PASS','accepted_c1_default_new_targets_per_standard_passage':4,'accepted_default_is_hard_quota':False,'planning_note':'Four new targets per standard passage is accepted as a conservative C1 production default after calibration, not a hard quota. Increase only when canonical policy and discourse load support it; never drop below an explicit standard minimum.','final_french_audit':'DEFERRED_UNTIL_C2_COMPLETE'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

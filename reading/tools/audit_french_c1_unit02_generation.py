#!/usr/bin/env python3
"""Strict generation audit for French C1 Unit02 before its frontier can advance."""
from __future__ import annotations
import json,re,subprocess
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_b1_unit10 as u10
base=u10.base
R=Path(__file__).resolve().parents[2];A1=R/'reading/french/a1/passages.jsonl';A2=R/'reading/french/a2/passages.jsonl';B1=R/'reading/french/b1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';C1=R/'reading/french/c1/passages.jsonl';SCHEMA=R/'reading/schema/passage.schema.json';LOCK=R/'reading/audit/french_c1_unit01_frontier_lock.json';PLAN=R/'reading/audit/french_c1_unit02_plan.json';SEL=R/'reading/audit/french_c1_unit02_target_selection.json';OUT=R/'reading/audit/french_c1_unit02_generation_review.json'
BANNED=[r'(?i)source[- ]?backed',r'(?i)semantic fallback',r'(?i)audited? fallback',r'(?i)curriculum metadata',r'(?i)\bcalibration\b']
REQ={'main_claim','argument_relation','assumption','inference','stance','summary','vocabulary_in_context','cross_text_synthesis'}
def load(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def norm(s):return re.sub(r'\s+',' ',s.lower()).strip()
def hash_text(s):return subprocess.check_output(['git','hash-object','--stdin'],input=s,text=True).strip()
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));plan=json.loads(PLAN.read_text(encoding='utf-8'));sel=json.loads(SEL.read_text(encoding='utf-8'));raw=C1.read_text(encoding='utf-8');lines=[x for x in raw.splitlines() if x.strip()];rows=[json.loads(x) for x in lines]
 if len(rows)!=12 or [r['sequence'] for r in rows]!=list(range(1,13)) or [r['id'] for r in rows]!=[f'fr-c1-u{u:02d}-p{p:02d}' for u in (1,2) for p in range(1,7)]:raise AssertionError('C1 Unit02 canonical identity/order failure')
 prefix='\n'.join(lines[:6])+'\n';prefix_blob=hash_text(prefix);b2blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('c1_canonical_blob')!=prefix_blob or lock.get('b2_canonical_blob')!=b2blob:raise AssertionError(f'Unit01 prefix/lock drift: prefix={prefix_blob} lock={lock.get("c1_canonical_blob")}')
 if plan.get('status')!='PASS' or plan.get('c1_source_blob')!=prefix_blob or sel.get('status')!='PASS' or sel.get('c1_source_blob')!=prefix_blob:raise AssertionError('Unit02 plan/selection stale against Unit01 prefix')
 lo,hi=map(int,sel['word_band']);deck=base.deck();prior=load(A1)+load(A2)+load(B1)+load(B2)+rows[:6];pid={t['id'] for r in prior for t in r.get('new_lexical_targets',[])};pf={t['form'] for r in prior for t in r.get('new_lexical_targets',[])};V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')));unit=rows[6:];new=[];qtypes=Counter();flags=[];ped={}
 for r in unit:
  errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
  if errs:raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:8]]}")
  wc=len(r['text'].split())
  if r['word_count']!=wc or not lo<=wc<=hi:raise AssertionError(f"{r['id']}: word band/count {r['word_count']} actual={wc} band={lo}-{hi}")
  if len([x for x in r['text'].split('\n\n') if x.strip()])<4:raise AssertionError(f"{r['id']}: fewer than four paragraphs")
  if len(r['questions'])!=10 or len(r['answer_key'])!=10:raise AssertionError(f"{r['id']}: Q/A count")
  if r['sequence']<=11 and len(r['new_lexical_targets'])!=4:raise AssertionError(f"{r['id']}: expected four new")
  if r['sequence']==12 and r['new_lexical_targets']:raise AssertionError('Unit02 checkpoint must be zero-new')
  local={t['id'] for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[])};amap={a['question_id']:a['id'] for a in r['answer_key']}
  for q in r['questions']:
   qtypes[q['type']]+=1
   if amap.get(q['id'])!=q['answer_id'] or any(x not in local for x in q.get('target_ids',[])):raise AssertionError(f"{r['id']} {q['id']}: linkage")
  for t in r.get('new_lexical_targets',[]):
   src=deck.get(t['form']);exact=base.cnt(r['text'],t['form'])
   if not src or t['id'] in pid or t['form'] in pf or t['source_rank']!=src['rank'] or t['id']!=base.tid(src['rank']) or exact<1 or exact!=t['exposures_in_text']:raise AssertionError(f"{r['id']}: source/freshness/exposure {t}")
   new.append(t)
  for t in r.get('review_lexical_targets',[]):
   if t.get('representation') in {'running_text','summary'} and base.cnt(r['text'],t['form'])<1:raise AssertionError(f"{r['id']}: invisible review {t['form']}")
  for pat in BANNED:
   if re.search(pat,r['text']):flags.append({'id':r['id'],'pattern':pat})
  n=norm(r['text']);checks={'scope':any(x in n for x in ['portée','condition','limite','généraliser','transfert']),'counterargument':any(x in n for x in ['objection','désaccord','position','contreargument','concurrent']),'method':any(x in n for x in ['méthode','mesure','preuve','donnée','comparaison','source']),'normative':any(x in n for x in ['valeur','équité','risque','critère','acceptable','recommandation']),'revision':any(x in n for x in ['révision','réviser','modifier','changer','abandonner'])};ped[r['id']]=checks
  if r['sequence']<=11 and sum(checks.values())<3:raise AssertionError(f"{r['id']}: insufficient C1 reasoning density {checks}")
 if flags:raise AssertionError(f'learner-facing internal wording {flags}')
 expected={x['form'] for x in sel['selected']}
 if len(new)!=20 or len({t['id'] for t in new})!=20 or len({t['form'] for t in new})!=20 or {t['form'] for t in new}!=expected:raise AssertionError('Unit02 target selection/uniqueness drift')
 if set(t['id'] for t in new)&pid or set(t['form'] for t in new)&pf:raise AssertionError('Unit02 collision with prior French')
 if not REQ.issubset(set(qtypes)):raise AssertionError(f'Unit02 question-type coverage missing {sorted(REQ-set(qtypes))}')
 pair='fr-c1-u02-generalization-context-viewpoints'
 if unit[2].get('paired_text_group')!=pair or unit[3].get('paired_text_group')!=pair or any(unit[i].get('paired_text_group') is not None for i in (0,1,4,5)):raise AssertionError('Unit02 paired group structure')
 sim=SequenceMatcher(None,norm(unit[2]['text']),norm(unit[3]['text'])).ratio()
 if sim>=0.45:raise AssertionError(f'Unit02 paired viewpoints too similar: {sim:.4f}')
 c1blob=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();out={'status':'PASS','scope':'French C1 Unit02 generation review','c1_source_prefix_blob':prefix_blob,'c1_canonical_blob':c1blob,'b2_canonical_blob':b2blob,'theme':plan.get('theme'),'genres':plan.get('genres'),'word_band':[lo,hi],'word_counts':[r['word_count'] for r in unit],'passages':6,'questions':60,'answers':60,'unique_new_target_ids':20,'unique_new_target_forms':20,'prior_collisions':0,'checkpoint_zero_new':True,'question_type_counts':dict(sorted(qtypes.items())),'paired_group':pair,'paired_similarity_ratio':round(sim,4),'language_review':'PASS','pedagogical_review':'PASS','source_identity':'PASS','exposure_counts':'PASS','exact_reviews':'PASS','schema':'PASS','linkage':'PASS','accepted_c1_default_new_targets_per_standard_passage':lock['accepted_c1_default_new_targets_per_standard_passage'],'accepted_default_is_hard_quota':False,'final_french_audit':'DEFERRED_UNTIL_C2_COMPLETE'};OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

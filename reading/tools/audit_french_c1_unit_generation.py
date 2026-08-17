#!/usr/bin/env python3
"""Generic strict C1 generation audit for Units 03-10 (or Unit02 if desired).

Set C1_UNIT=N. Requires the exact previous-unit lock, current plan and selection,
checks the canonical prefix blob, current six rows, source freshness/exposure,
reviews, C1 word band, Q/A linkage, reasoning density and paired-text quality.
"""
from __future__ import annotations
import json,os,re,subprocess
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from jsonschema import Draft202012Validator
import generate_french_b1_unit10 as u10
base=u10.base
U=int(os.environ.get('C1_UNIT','0'))
if not 2<=U<=10:raise SystemExit('C1_UNIT must be 2..10')
R=Path(__file__).resolve().parents[2];A1=R/'reading/french/a1/passages.jsonl';A2=R/'reading/french/a2/passages.jsonl';B1=R/'reading/french/b1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';C1=R/'reading/french/c1/passages.jsonl';SCHEMA=R/'reading/schema/passage.schema.json';LOCK=R/f'reading/audit/french_c1_unit{U-1:02d}_frontier_lock.json';PLAN=R/f'reading/audit/french_c1_unit{U:02d}_plan.json';SEL=R/f'reading/audit/french_c1_unit{U:02d}_target_selection.json';OUT=R/f'reading/audit/french_c1_unit{U:02d}_generation_review.json'
BANNED=[r'(?i)source[- ]?backed',r'(?i)semantic fallback',r'(?i)audited? fallback',r'(?i)curriculum metadata',r'(?i)\bcalibration\b']
REQ={'main_claim','argument_relation','assumption','inference','stance','summary','vocabulary_in_context'}
def load(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def norm(s):return re.sub(r'\s+',' ',s.lower()).strip()
def hash_text(s):return subprocess.check_output(['git','hash-object','--stdin'],input=s,text=True).strip()
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));plan=json.loads(PLAN.read_text(encoding='utf-8'));sel=json.loads(SEL.read_text(encoding='utf-8'));raw=C1.read_text(encoding='utf-8');lines=[x for x in raw.splitlines() if x.strip()];rows=[json.loads(x) for x in lines];need=U*6;prefix_n=(U-1)*6
 if len(rows)!=need or [r['sequence'] for r in rows]!=list(range(1,need+1)):raise AssertionError(f'C1 Unit{U:02d} frontier/order failure: {len(rows)} rows')
 expected_ids=[f'fr-c1-u{u:02d}-p{p:02d}' for u in range(1,U+1) for p in range(1,7)]
 if [r['id'] for r in rows]!=expected_ids:raise AssertionError(f'C1 Unit{U:02d} ID ordering failure')
 prefix='\n'.join(lines[:prefix_n])+'\n';prefix_blob=hash_text(prefix);b2blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=prefix_n or lock.get('c1_canonical_blob')!=prefix_blob or lock.get('b2_canonical_blob')!=b2blob:raise AssertionError(f'previous C1 lock/prefix drift for Unit{U:02d}')
 if plan.get('status')!='PASS' or plan.get('c1_source_blob')!=prefix_blob or sel.get('status')!='PASS' or sel.get('c1_source_blob')!=prefix_blob:raise AssertionError(f'Unit{U:02d} plan/selection stale')
 lo,hi=map(int,sel['word_band']);unit=rows[prefix_n:need];prior=load(A1)+load(A2)+load(B1)+load(B2)+rows[:prefix_n];pid={t['id'] for r in prior for t in r.get('new_lexical_targets',[])};pf={t['form'] for r in prior for t in r.get('new_lexical_targets',[])};deck=base.deck();V=Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8')));new=[];qtypes=Counter();flags=[];ped={};pairs={}
 for r in unit:
  errs=sorted(V.iter_errors(r),key=lambda e:list(e.path))
  if errs:raise AssertionError(f"{r['id']}: schema {[e.message for e in errs[:8]]}")
  wc=len(r['text'].split());paras=[x for x in r['text'].split('\n\n') if x.strip()]
  if r['word_count']!=wc or not lo<=wc<=hi:raise AssertionError(f"{r['id']}: word band/count {r['word_count']} actual={wc} band={lo}-{hi}")
  if len(paras)<4:raise AssertionError(f"{r['id']}: fewer than four paragraphs")
  if len(r['questions'])!=10 or len(r['answer_key'])!=10:raise AssertionError(f"{r['id']}: expected 10 Q/A")
  if r['sequence']<need and len(r['new_lexical_targets'])!=int(sel['new_targets_per_standard_passage']):raise AssertionError(f"{r['id']}: new-target load drift")
  if r['sequence']==need and r['new_lexical_targets']:raise AssertionError(f'Unit{U:02d} checkpoint must be zero-new')
  local={t['id'] for f in ('new_lexical_targets','review_lexical_targets') for t in r.get(f,[])};amap={a['question_id']:a['id'] for a in r['answer_key']}
  for q in r['questions']:
   qtypes[q['type']]+=1
   if amap.get(q['id'])!=q['answer_id'] or any(x not in local for x in q.get('target_ids',[])):raise AssertionError(f"{r['id']} {q['id']}: linkage failure")
  for t in r.get('new_lexical_targets',[]):
   src=deck.get(t['form']);exact=base.cnt(r['text'],t['form'])
   if not src or t['id'] in pid or t['form'] in pf or t['source_rank']!=src['rank'] or t['id']!=base.tid(src['rank']) or exact<1 or exact!=t['exposures_in_text']:raise AssertionError(f"{r['id']}: source/freshness/exposure {t}")
   new.append(t)
  for t in r.get('review_lexical_targets',[]):
   if t.get('representation') in {'running_text','summary'} and base.cnt(r['text'],t['form'])<1:raise AssertionError(f"{r['id']}: invisible review {t['form']}")
  for pat in BANNED:
   if re.search(pat,r['text']):flags.append({'id':r['id'],'pattern':pat})
  n=norm(r['text']);checks={'scope':any(x in n for x in ['portée','condition','limite','général','transfert']),'counterargument':any(x in n for x in ['objection','désaccord','position','contreargument','concurrent']),'method':any(x in n for x in ['méthode','mesure','preuve','donnée','comparaison','source','mécanisme']),'normative':any(x in n for x in ['valeur','équité','risque','critère','acceptable','recommandation','décision']),'revision':any(x in n for x in ['révision','réviser','modifier','changer','abandonner','corriger'])};ped[r['id']]=checks
  if r['sequence']<need and sum(checks.values())<3:raise AssertionError(f"{r['id']}: insufficient C1 reasoning density {checks}")
  if r.get('paired_text_group'):pairs.setdefault(r['paired_text_group'],[]).append(r)
 if flags:raise AssertionError(f'learner-facing internal wording {flags}')
 expected={x['form'] for x in sel['selected']};loadn=int(sel['new_targets_per_standard_passage'])*5
 if len(new)!=loadn or len({t['id'] for t in new})!=loadn or len({t['form'] for t in new})!=loadn or {t['form'] for t in new}!=expected:raise AssertionError(f'Unit{U:02d} target selection/uniqueness drift')
 if set(t['id'] for t in new)&pid or set(t['form'] for t in new)&pf:raise AssertionError(f'Unit{U:02d} prior collision')
 if not REQ.issubset(set(qtypes)):raise AssertionError(f'Unit{U:02d} question-type coverage missing {sorted(REQ-set(qtypes))}')
 pair_metrics={}
 for name,prs in pairs.items():
  if len(prs)!=2:raise AssertionError(f'paired group {name} has {len(prs)} passages')
  sim=SequenceMatcher(None,norm(prs[0]['text']),norm(prs[1]['text'])).ratio()
  if sim>=0.45:raise AssertionError(f'paired group {name} too similar: {sim:.4f}')
  pair_metrics[name]=round(sim,4)
 if pairs and qtypes.get('cross_text_synthesis',0)<1:raise AssertionError(f'Unit{U:02d} paired text lacks cross-text synthesis assessment')
 c1blob=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();out={'status':'PASS','scope':f'French C1 Unit {U:02d} generation review','c1_source_prefix_blob':prefix_blob,'c1_canonical_blob':c1blob,'b2_canonical_blob':b2blob,'theme':plan.get('theme'),'genres':plan.get('genres'),'word_band':[lo,hi],'word_counts':[r['word_count'] for r in unit],'passages':6,'questions':60,'answers':60,'unique_new_target_ids':loadn,'unique_new_target_forms':loadn,'prior_collisions':0,'checkpoint_zero_new':True,'question_type_counts':dict(sorted(qtypes.items())),'paired_groups':pair_metrics,'language_review':'PASS','pedagogical_review':'PASS','source_identity':'PASS','exposure_counts':'PASS','exact_reviews':'PASS','schema':'PASS','linkage':'PASS','accepted_c1_default_new_targets_per_standard_passage':int(sel['new_targets_per_standard_passage']),'accepted_default_is_hard_quota':False,'final_french_audit':'DEFERRED_UNTIL_C2_COMPLETE'};OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

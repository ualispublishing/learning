#!/usr/bin/env python3
"""Select 20 fresh content targets for French C1 Unit02.

Requires the calibrated Unit01 lock, canonical Unit02 plan and exhaustive Unit02
freshness probe. Four targets/P01-P05 remains the calibrated default, never a
hard quota. Selection deliberately excludes function words and uses forms that
support professional judgment: certainty, necessity, evidence intake, affected
people, stopping rules, implementation and consequence severity.
"""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_c1_unit01_frontier_lock.json';PLAN=R/'reading/audit/french_c1_unit02_plan.json';PROBE=R/'reading/audit/french_c1_unit02_target_probe.json';OUT=R/'reading/audit/french_c1_unit02_target_selection.json'
SELECTION=[
 ('p01_frame','sûr'),('p01_claim','falloir'),('p01_scope','vraiment'),('p01_qualify','seul'),
 ('p02_method','regarder'),('p02_evidence','entendre'),('p02_compare','parler'),('p02_uncertainty','passer'),
 ('p03_view','homme'),('p03_concede','femme'),('p03_cause','gens'),('p03_transfer','peut-être'),
 ('p04_actor','arriver'),('p04_value','partir'),('p04_tradeoff','laisser'),('p04_constraint','arrêter'),
 ('p05_synthesis','petit'),('p05_judgment','grand'),('p05_revision','mourir'),('p05_condition','appeler')]
BANNED={'être','avoir','de','je','pas','le','que','vous','tu','et','il','un','en','ça','on','une','elle','me','du','te','se','toi','lui','votre','cette','son','par','ou','des','sa','ses','leur','mes','tes','cet','dont','ni','aucun','aucune','la'}
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));plan=json.loads(PLAN.read_text(encoding='utf-8'));probe=json.loads(PROBE.read_text(encoding='utf-8'));c1blob=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();b2blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=6 or lock.get('c1_canonical_blob')!=c1blob or lock.get('b2_canonical_blob')!=b2blob:raise AssertionError('C1 Unit01 lock/live mismatch')
 if plan.get('status')!='PASS' or plan.get('c1_source_blob')!=c1blob or probe.get('status')!='PASS' or probe.get('c1_source_blob')!=c1blob:raise AssertionError('C1 Unit02 plan/probe missing or stale')
 default=int(lock['accepted_c1_default_new_targets_per_standard_passage'])
 if default!=4 or lock.get('accepted_default_is_hard_quota') is not False:raise AssertionError(f'unexpected calibrated C1 default metadata: {default}')
 fresh={x['form']:x for x in probe.get('fresh',[])};selected=[];used=set()
 for slot,form in SELECTION:
  if form not in fresh:raise AssertionError(f'C1 Unit02 curated target is not fresh/source-backed: {form}')
  if form in used or form in BANNED:raise AssertionError(f'C1 Unit02 invalid curated target: {form}')
  used.add(form);item=dict(fresh[form]);item['slot']=slot;item['semantic_fallback']=False;item['pedagogical_content_word']=True;selected.append(item)
 groups={k:[x['form'] for x in selected if x['slot'].startswith(k+'_')] for k in ['p01','p02','p03','p04','p05']}
 if len(selected)!=20 or len(used)!=20 or any(len(v)!=4 for v in groups.values()):raise AssertionError('C1 Unit02 selection structure failure')
 out={'status':'PASS','scope':'French C1 Unit02 pedagogical target selection','b2_canonical_blob':b2blob,'c1_source_blob':c1blob,'c1_unit01_lock':'reading/audit/french_c1_unit01_frontier_lock.json','c1_plan_artifact':'reading/audit/french_c1_unit02_plan.json','theme':plan.get('theme'),'genres':plan.get('genres'),'word_band':[plan['c1_word_min'],plan['c1_word_max']],'new_targets_per_standard_passage':default,'default_is_hard_quota':False,'selected_count':20,'selected':selected,'passage_groups':groups,'semantic_fallback_count':0,'pedagogical_filter':'curated fresh content words tied to professional-judgment reasoning; no function-word fallback','note':'Four is the calibrated C1 default, not a hard quota.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','selected_count':20,'groups':groups},ensure_ascii=False))
if __name__=='__main__':main()

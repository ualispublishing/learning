#!/usr/bin/env python3
"""Curated fresh target selection for C1 Unit06: law, rights, and interpretation."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_c1_unit05_frontier_lock.json';PLAN=R/'reading/audit/french_c1_unit06_plan.json';PROBE=R/'reading/audit/french_c1_unit06_target_probe.json';OUT=R/'reading/audit/french_c1_unit06_target_selection.json'
SELECTION=[
 ('p01_actor','agent'),('p01_submit','présenter'),('p01_fault','faute'),('p01_omit','ignorer'),
 ('p02_offense','crime'),('p02_homicide','meurtre'),('p02_liability','coupable'),('p02_oath','jurer'),
 ('p03_detention','prison'),('p03_sentence','peine'),('p03_release','libérer'),('p03_theft','vol'),
 ('p04_seize','enlever'),('p04_force','frapper'),('p04_enforcement_register','flic'),('p04_capture','attraper'),
 ('p05_consider','tenir'),('p05_lift','lever'),('p05_deliver','remettre'),('p05_exception','hors')]
BANNED={'être','avoir','de','je','pas','le','que','vous','tu','et','il','un','en','ça','on','une','elle','me','du','te','se','toi','lui','votre','cette','son','par','ou','des','sa','ses','leur','mes','tes','cet','dont','ni','aucun','aucune','la'}
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));plan=json.loads(PLAN.read_text(encoding='utf-8'));probe=json.loads(PROBE.read_text(encoding='utf-8'));c1blob=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();b2blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=30 or lock.get('c1_canonical_blob')!=c1blob or lock.get('b2_canonical_blob')!=b2blob:raise AssertionError('C1 Unit05 lock/live mismatch')
 if plan.get('status')!='PASS' or plan.get('c1_source_blob')!=c1blob or probe.get('status')!='PASS' or probe.get('c1_source_blob')!=c1blob:raise AssertionError('Unit06 plan/probe stale')
 fresh={x['form']:x for x in probe.get('fresh',[])};used=set();selected=[]
 for slot,form in SELECTION:
  if form not in fresh:raise AssertionError(f'C1 Unit06 curated target is not fresh/source-backed: {form}')
  if form in used or form in BANNED:raise AssertionError(f'C1 Unit06 invalid target: {form}')
  used.add(form);item=dict(fresh[form]);item.update({'slot':slot,'semantic_fallback':False,'pedagogical_content_word':True});selected.append(item)
 groups={k:[x['form'] for x in selected if x['slot'].startswith(k+'_')] for k in ['p01','p02','p03','p04','p05']}
 if len(selected)!=20 or any(len(v)!=4 for v in groups.values()):raise AssertionError('Unit06 target structure failure')
 out={'status':'PASS','scope':'French C1 Unit06 pedagogical target selection','b2_canonical_blob':b2blob,'c1_source_blob':c1blob,'theme':plan.get('theme'),'genres':plan.get('genres'),'word_band':[plan['c1_word_min'],plan['c1_word_max']],'new_targets_per_standard_passage':4,'default_is_hard_quota':False,'selected_count':20,'selected':selected,'passage_groups':groups,'semantic_fallback_count':0,'pedagogical_filter':'fresh content words mapped to legal actors, offenses, detention/remedy, coercive enforcement and interpretive procedure','note':'Four is calibrated C1 default, not quota. Colloquial flic is taught explicitly as a register contrast, not as neutral legal terminology.'}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','groups':groups},ensure_ascii=False))
if __name__=='__main__':main()

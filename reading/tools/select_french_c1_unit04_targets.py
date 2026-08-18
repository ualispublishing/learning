#!/usr/bin/env python3
"""Curated fresh target selection for C1 Unit04: language, identity, society."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_c1_unit03_frontier_lock.json';PLAN=R/'reading/audit/french_c1_unit04_plan.json';PROBE=R/'reading/audit/french_c1_unit04_target_probe.json';OUT=R/'reading/audit/french_c1_unit04_target_selection.json'
SELECTION=[
 ('p01_formal','monsieur'),('p01_formal2','madame'),('p01_informal','gars'),('p01_informal2','mec'),
 ('p02_gender1','fille'),('p02_gender2','garçon'),('p02_family1','fils'),('p02_family2','frère'),
 ('p03_relation1','copain'),('p03_relation2','copine'),('p03_relation3','mari'),('p03_group','bande'),
 ('p04_listen','écouter'),('p04_language','anglais'),('p04_politeness','pardon'),('p04_category','genre'),
 ('p05_address1','maman'),('p05_address2','papa'),('p05_school','lycée'),('p05_socialization','grandir')]
BANNED={'être','avoir','de','je','pas','le','que','vous','tu','et','il','un','en','ça','on','une','elle','me','du','te','se','toi','lui','votre','cette','son','par','ou','des','sa','ses','leur','mes','tes','cet','dont','ni','aucun','aucune','la'}
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));plan=json.loads(PLAN.read_text(encoding='utf-8'));probe=json.loads(PROBE.read_text(encoding='utf-8'));c1blob=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();b2blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=18 or lock.get('c1_canonical_blob')!=c1blob or lock.get('b2_canonical_blob')!=b2blob:raise AssertionError('C1 Unit03 lock/live mismatch')
 if plan.get('status')!='PASS' or plan.get('c1_source_blob')!=c1blob or probe.get('status')!='PASS' or probe.get('c1_source_blob')!=c1blob:raise AssertionError('Unit04 plan/probe stale')
 if int(lock['accepted_c1_default_new_targets_per_standard_passage'])!=4 or lock.get('accepted_default_is_hard_quota') is not False:raise AssertionError('unexpected C1 default metadata')
 fresh={x['form']:x for x in probe.get('fresh',[])};used=set();selected=[]
 for slot,form in SELECTION:
  if form not in fresh:raise AssertionError(f'C1 Unit04 curated target is not fresh/source-backed: {form}')
  if form in used or form in BANNED:raise AssertionError(f'C1 Unit04 invalid curated target: {form}')
  used.add(form);item=dict(fresh[form]);item['slot']=slot;item['semantic_fallback']=False;item['pedagogical_content_word']=True;selected.append(item)
 groups={k:[x['form'] for x in selected if x['slot'].startswith(k+'_')] for k in ['p01','p02','p03','p04','p05']}
 if len(selected)!=20 or any(len(v)!=4 for v in groups.values()):raise AssertionError('Unit04 target structure failure')
 out={'status':'PASS','scope':'French C1 Unit04 pedagogical target selection','b2_canonical_blob':b2blob,'c1_source_blob':c1blob,'theme':plan.get('theme'),'genres':plan.get('genres'),'word_band':[plan['c1_word_min'],plan['c1_word_max']],'new_targets_per_standard_passage':4,'default_is_hard_quota':False,'selected_count':20,'selected':selected,'passage_groups':groups,'semantic_fallback_count':0,'pedagogical_filter':'fresh social/register/family/group/language/socialization content words; analyzed as contextual labels, not stereotypes','note':'Four is calibrated C1 default, not quota.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','groups':groups},ensure_ascii=False))
if __name__=='__main__':main()

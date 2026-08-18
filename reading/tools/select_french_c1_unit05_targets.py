#!/usr/bin/env python3
"""Curated fresh target selection for C1 Unit05: scientific uncertainty and communication."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_c1_unit04_frontier_lock.json';PLAN=R/'reading/audit/french_c1_unit05_plan.json';PROBE=R/'reading/audit/french_c1_unit05_target_probe.json';OUT=R/'reading/audit/french_c1_unit05_target_selection.json'
SELECTION=[
 ('p01_confidence','sûrement'),('p01_absolute','absolument'),('p01_appearance','paraître'),('p01_sufficiency','assez'),
 ('p02_exception','sauf'),('p02_order','premier'),('p02_end','finir'),('p02_magnitude','moins'),
 ('p03_category1','blanc'),('p03_category2','rouge'),('p03_taxonomy','espèce'),('p03_publication','papier'),
 ('p04_report','ressentir'),('p04_risk','craindre'),('p04_outcome','mort'),('p04_harm','blesser'),
 ('p05_population','américain'),('p05_generalize','partout'),('p05_time','cours'),('p05_background','fond')]
BANNED={'être','avoir','de','je','pas','le','que','vous','tu','et','il','un','en','ça','on','une','elle','me','du','te','se','toi','lui','votre','cette','son','par','ou','des','sa','ses','leur','mes','tes','cet','dont','ni','aucun','aucune','la'}
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));plan=json.loads(PLAN.read_text(encoding='utf-8'));probe=json.loads(PROBE.read_text(encoding='utf-8'));c1blob=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();b2blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=24 or lock.get('c1_canonical_blob')!=c1blob or lock.get('b2_canonical_blob')!=b2blob:raise AssertionError('C1 Unit04 lock/live mismatch')
 if plan.get('status')!='PASS' or plan.get('c1_source_blob')!=c1blob or probe.get('status')!='PASS' or probe.get('c1_source_blob')!=c1blob:raise AssertionError('Unit05 plan/probe stale')
 if int(lock['accepted_c1_default_new_targets_per_standard_passage'])!=4 or lock.get('accepted_default_is_hard_quota') is not False:raise AssertionError('unexpected C1 default metadata')
 fresh={x['form']:x for x in probe.get('fresh',[])};used=set();selected=[]
 for slot,form in SELECTION:
  if form not in fresh:raise AssertionError(f'C1 Unit05 curated target is not fresh/source-backed: {form}')
  if form in used or form in BANNED:raise AssertionError(f'C1 Unit05 invalid curated target: {form}')
  used.add(form);item=dict(fresh[form]);item['slot']=slot;item['semantic_fallback']=False;item['pedagogical_content_word']=True;selected.append(item)
 groups={k:[x['form'] for x in selected if x['slot'].startswith(k+'_')] for k in ['p01','p02','p03','p04','p05']}
 if len(selected)!=20 or any(len(v)!=4 for v in groups.values()):raise AssertionError('Unit05 target structure failure')
 out={'status':'PASS','scope':'French C1 Unit05 pedagogical target selection','b2_canonical_blob':b2blob,'c1_source_blob':c1blob,'theme':plan.get('theme'),'genres':plan.get('genres'),'word_band':[plan['c1_word_min'],plan['c1_word_max']],'new_targets_per_standard_passage':4,'default_is_hard_quota':False,'selected_count':20,'selected':selected,'passage_groups':groups,'semantic_fallback_count':0,'pedagogical_filter':'fresh content words mapped to confidence, study boundaries, observable categories, harm/risk and transfer/generalization','note':'Four is calibrated C1 default, not quota.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASS','groups':groups},ensure_ascii=False))
if __name__=='__main__':main()

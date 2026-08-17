#!/usr/bin/env python3
"""Generic exhaustive freshness probe for target C1 Units 02-10.

Set C1_UNIT=N. Requires target plan and exact previous-unit frontier lock.
"""
from __future__ import annotations
import json,os,subprocess,sys
from pathlib import Path
U=int(os.environ.get('C1_UNIT','0'))
if not 2<=U<=10:raise SystemExit('C1_UNIT must be target unit 2..10')
R=Path(__file__).resolve().parents[2];TOOLS=R/'reading/tools';sys.path.insert(0,str(TOOLS))
import generate_french_b1_unit10 as u10
base=u10.base
A1=R/'reading/french/a1/passages.jsonl';A2=R/'reading/french/a2/passages.jsonl';B1=R/'reading/french/b1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';C1=R/'reading/french/c1/passages.jsonl';LOCK=R/f'reading/audit/french_c1_unit{U-1:02d}_frontier_lock.json';PLAN=R/f'reading/audit/french_c1_unit{U:02d}_plan.json';OUT=R/f'reading/audit/french_c1_unit{U:02d}_target_probe.json'
def load(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
 lock=json.loads(LOCK.read_text(encoding='utf-8'));plan=json.loads(PLAN.read_text(encoding='utf-8'));c1blob=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();b2blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip();prev=(U-1)*6
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=prev or lock.get('c1_canonical_blob')!=c1blob or lock.get('b2_canonical_blob')!=b2blob:raise AssertionError(f'C1 Unit{U-1:02d} lock/live mismatch')
 if plan.get('status')!='PASS' or plan.get('c1_source_blob')!=c1blob or plan.get('b2_canonical_blob')!=b2blob:raise AssertionError(f'C1 Unit{U:02d} plan missing/stale')
 rows=load(A1)+load(A2)+load(B1)+load(B2)+load(C1);prior=[t for r in rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)];ids={t.get('id') for t in prior};forms={t.get('form') for t in prior};deck=base.deck();items=[]
 for form,data in sorted(deck.items(),key=lambda kv:kv[1]['rank']):
  rank=data['rank'];tid=base.tid(rank);status='fresh' if form not in forms and tid not in ids else 'already_deliberate';items.append({'form':form,'status':status,'rank':rank,'id':tid,'meaning':data.get('meaning')})
 fresh=[x for x in items if x['status']=='fresh'];needed=int(plan['accepted_c1_default_new_targets_per_standard_passage'])*5
 if len(fresh)<needed:raise AssertionError(f'Only {len(fresh)} fresh source terms remain; need at least {needed} for Unit{U:02d}')
 out={'status':'PASS','scope':f'French C1 Unit{U:02d} exhaustive target probe','b2_canonical_blob':b2blob,'c1_source_blob':c1blob,'previous_frontier_lock':f'reading/audit/french_c1_unit{U-1:02d}_frontier_lock.json','c1_plan_artifact':f'reading/audit/french_c1_unit{U:02d}_plan.json','c1_theme':plan.get('theme'),'c1_genres':plan.get('genres'),'c1_word_min':plan['c1_word_min'],'c1_word_max':plan['c1_word_max'],'accepted_c1_default_new_targets_per_standard_passage':plan['accepted_c1_default_new_targets_per_standard_passage'],'accepted_default_is_hard_quota':False,'prior_deliberate_targets':len(prior),'deck_entries':len(items),'fresh_count':len(fresh),'fresh':fresh,'already_deliberate_count':len(items)-len(fresh),'note':f'Exhaustive source probe for C1 Unit{U:02d}; no canonical write.'};OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','unit':U,'fresh_count':len(fresh),'theme':plan.get('theme')},ensure_ascii=False))
if __name__=='__main__':main()

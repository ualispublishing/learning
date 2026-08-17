#!/usr/bin/env python3
"""Exhaustive source/freshness probe for French C1 Unit01 calibration.

Requires the sealed B2 generation-integrity artifact and resolved canonical C1
Unit01 plan. Scans the full read-only French source deck against all deliberate
A1-B2 targets. No C1 canonical content is written.
"""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];TOOLS=R/'reading/tools';sys.path.insert(0,str(TOOLS))
import generate_french_b1_unit10 as u10
base=u10.base
A1=R/'reading/french/a1/passages.jsonl';A2=R/'reading/french/a2/passages.jsonl';B1=R/'reading/french/b1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';AUD=R/'reading/audit/french_b2_generation_integrity.json';PLAN=R/'reading/audit/french_c1_unit01_plan.json';OUT=R/'reading/audit/french_c1_unit01_target_probe.json'
def load(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
 audit=json.loads(AUD.read_text(encoding='utf-8'));plan=json.loads(PLAN.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if audit.get('status')!='PASS' or audit.get('canonical_blob')!=blob or audit.get('passages')!=60:raise AssertionError('C1 probe requires matching sealed B2')
 if plan.get('status')!='PASS' or plan.get('b2_canonical_blob')!=blob:raise AssertionError('C1 Unit01 plan missing/stale')
 rows=load(A1)+load(A2)+load(B1)+load(B2);prior=[t for r in rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)];ids={t.get('id') for t in prior};forms={t.get('form') for t in prior};deck=base.deck();items=[]
 for form,data in sorted(deck.items(),key=lambda kv:kv[1]['rank']):
  rank=data['rank'];tid=base.tid(rank);status='fresh' if form not in forms and tid not in ids else 'already_deliberate';items.append({'form':form,'status':status,'rank':rank,'id':tid,'meaning':data.get('meaning')})
 fresh=[x for x in items if x['status']=='fresh']
 if len(fresh)<25:raise AssertionError(f'Only {len(fresh)} fresh source terms remain; insufficient for safe C1 calibration exploration')
 out={'status':'PASS','scope':'French C1 Unit01 exhaustive target probe','b2_canonical_blob':blob,'c1_plan_artifact':'reading/audit/french_c1_unit01_plan.json','c1_theme':plan.get('theme'),'c1_genres':plan.get('genres'),'c1_word_min':plan['c1_word_min'],'c1_word_max':plan['c1_word_max'],'prior_deliberate_targets':len(prior),'deck_entries':len(items),'fresh_count':len(fresh),'fresh':fresh,'already_deliberate_count':len(items)-len(fresh),'note':'Exhaustive source probe only. C1 calibration target load is intentionally not fixed here.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','fresh_count':len(fresh),'prior_deliberate_targets':len(prior),'theme':plan.get('theme'),'word_band':[plan['c1_word_min'],plan['c1_word_max']]},ensure_ascii=False))
if __name__=='__main__':main()

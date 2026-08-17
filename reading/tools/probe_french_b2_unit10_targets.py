#!/usr/bin/env python3
"""Exhaustive dependency-locked freshness probe for final B2 Unit10.

Scans the full read-only French top-1000 deck, sorted by source rank, against all
prior deliberate French targets. This avoids narrowing the final synthesis unit
to a hand-picked candidate subset while preserving source identity and freshness.
"""
from __future__ import annotations
import json,subprocess
from pathlib import Path
import generate_french_b1_unit10 as u10
base=u10.base
R=Path(__file__).resolve().parents[2];B2=R/'reading/french/b2/passages.jsonl';LOCK=R/'reading/audit/french_b2_unit09_frontier_lock.json';OUT=R/'reading/audit/french_b2_unit10_target_probe.json'
PATHS=[R/'reading/french/a1/passages.jsonl',R/'reading/french/a2/passages.jsonl',R/'reading/french/b1/passages.jsonl',B2]
def main():
 if not LOCK.exists():raise AssertionError('Unit09 frontier lock missing; Unit10 probe must not run early')
 lock=json.loads(LOCK.read_text(encoding='utf-8'));blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=54 or blob!=lock.get('canonical_blob'):raise AssertionError('Unit09 lock/live B2 mismatch')
 rows=[]
 for p in PATHS:rows += [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len([r for r in rows if r.get('cefr')=='B2'])!=54:raise AssertionError('expected 54 B2 passages before Unit10 probe')
 prior=[t for r in rows for t in r.get('new_lexical_targets',[]) if isinstance(t,dict)];ids={t.get('id') for t in prior};forms={t.get('form') for t in prior};deck=base.deck();items=[]
 for form,data in sorted(deck.items(),key=lambda kv:kv[1]['rank']):
  rank=data['rank'];tid=base.tid(rank);status='fresh' if form not in forms and tid not in ids else 'already_deliberate'
  items.append({'form':form,'status':status,'rank':rank,'id':tid,'meaning':data.get('meaning')})
 fresh=[x for x in items if x['status']=='fresh']
 result={'status':'PASS','scope':'French B2 Unit 10 exhaustive target probe','theme':'B2 synthesis','genres':['paired long texts','integrated analysis','checkpoint'],'b2_source_blob':blob,'prior_deliberate_targets':len(prior),'deck_entries':len(items),'fresh_count':len(fresh),'fresh':fresh,'already_deliberate_count':len(items)-len(fresh),'note':'Exhaustive rank-ordered scan of the full read-only French source deck; not generation approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','b2_source_blob':blob,'prior_deliberate_targets':len(prior),'deck_entries':len(items),'fresh_count':len(fresh)},ensure_ascii=False))
if __name__=='__main__':main()

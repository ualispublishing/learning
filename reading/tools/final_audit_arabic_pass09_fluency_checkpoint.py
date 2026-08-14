#!/usr/bin/env python3
"""Final Arabic review pass 09: Unit-P6 fluency/checkpoint suitability.

Checks the documented generation architecture mechanically. Coverage/mastery
claims remain deferred until actual lexical coverage is measured. An empty
explicit lexical-review list is acceptable only for a final cross-domain
capstone that is explicitly zero-new and depends on the preceding C2 units.
"""
from __future__ import annotations
import json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEVELS=('a1','a2','b1','b2','c1','c2')
OUT=ROOT/'reading/audit/final_arabic_pass09_fluency_checkpoint.json'
P_RE=re.compile(r'-p(\d{2})$')

def final_capstone_exception(level,r,new,reviews,st,tags):
 return (
  level=='c2' and r.get('unit')==10 and r.get('id')=='ar-c2-u10-p06'
  and not new and not reviews and st.get('new_word_policy')=='none' and st.get('timed') is True
  and 'zero_new_targets' in tags
  and any('C2 Units 01-09' in str(x) for x in r.get('prerequisites',[]))
 )

def main():
 hard=[];flags=[];summary={};accepted=[]
 for level in LEVELS:
  rows=[json.loads(x) for x in (ROOT/f'reading/arabic/{level}/passages.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
  p6=[r for r in rows if P_RE.search(r['id']) and int(P_RE.search(r['id']).group(1))==6]
  c=Counter()
  if len(p6)!=10:hard.append({'code':'p6_count','level':level,'expected':10,'actual':len(p6)})
  for r in p6:
   pid=r['id'];new=r.get('new_lexical_targets',[]) if isinstance(r.get('new_lexical_targets'),list) else []
   if new:
    hard.append({'code':'p6_has_new_lexical_targets','level':level,'passage_id':pid,'target_ids':[t.get('id') for t in new if isinstance(t,dict)]});c['p6_has_new_lexical_targets']+=1
   st=r.get('speed_training',{}) if isinstance(r.get('speed_training'),dict) else {}
   if st.get('new_word_policy') not in {'none','controlled'}:
    flags.append({'code':'p6_unexpected_new_word_policy','level':level,'passage_id':pid,'value':st.get('new_word_policy')});c['p6_unexpected_new_word_policy']+=1
   if st.get('comprehension_gate') not in {0.8,0.85,0.9}:
    flags.append({'code':'p6_unexpected_comprehension_gate','level':level,'passage_id':pid,'value':st.get('comprehension_gate')});c['p6_unexpected_comprehension_gate']+=1
   if st.get('benchmark_eligible') is True:
    flags.append({'code':'p6_benchmark_enabled_before_final_coverage_calibration','level':level,'passage_id':pid});c['p6_benchmark_enabled_before_final_coverage_calibration']+=1
   tags=r.get('reader_tags',[]) if isinstance(r.get('reader_tags'),list) else []
   if not any(str(tag).startswith('unit_role:') and any(k in str(tag) for k in ('fluency','checkpoint','integration')) for tag in tags):
    flags.append({'code':'p6_missing_fluency_checkpoint_role_tag','level':level,'passage_id':pid,'reader_tags':tags});c['p6_missing_fluency_checkpoint_role_tag']+=1
   if st.get('timed') is not True:
    flags.append({'code':'p6_not_currently_timed','level':level,'passage_id':pid});c['p6_not_currently_timed']+=1
   reviews=r.get('review_lexical_targets',[]) if isinstance(r.get('review_lexical_targets'),list) else []
   if not reviews:
    if final_capstone_exception(level,r,new,reviews,st,tags):
     accepted.append({'passage_id':pid,'reason':'final cross-domain C2 capstone is explicitly zero-new, timed, and depends on Units 01-09; exact prior-target surface/lemma inspector found no honest lexical review item to add'})
     c['accepted_empty_review_final_capstone']+=1
    else:
     flags.append({'code':'p6_has_no_explicit_review_targets','level':level,'passage_id':pid});c['p6_has_no_explicit_review_targets']+=1
  summary[level]={'p6_passages':len(p6),'flags_by_code':dict(c),'all_p6_zero_new_targets':all(not r.get('new_lexical_targets') for r in p6)}
 payload={'pass':9,'name':'fluency_checkpoint_suitability','scope':'Arabic A1-C2 P6 passages','method':'unit-role, zero-new-target, timing, comprehension-gate, benchmark-conservatism, explicit-review diagnostics, and one source-evidenced final-capstone exception','supporting_evidence':['reading/audit/final_arabic_c2_capstone_prior_target_matches.json'],'not_claimed':['actual learner fluency','known-token coverage','benchmark readiness before calibration'],'levels':summary,'accepted_exceptions':accepted,'totals':{'p6_passages':sum(x['p6_passages'] for x in summary.values()),'hard_issues':len(hard),'review_flags':len(flags),'accepted_exceptions':len(accepted)},'hard_issues':hard,'flags':flags,'status':'FAIL' if hard else ('REVIEW_REQUIRED' if flags else 'PASS')}
 OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(payload['totals'],ensure_ascii=False));print('status='+payload['status'])
 if hard:raise SystemExit(1)
if __name__=='__main__':main()

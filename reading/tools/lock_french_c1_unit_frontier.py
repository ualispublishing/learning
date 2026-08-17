#!/usr/bin/env python3
"""Generic C1 frontier lock for Units 03-10. Set C1_UNIT=N."""
from __future__ import annotations
import json,os,subprocess
from pathlib import Path
U=int(os.environ.get('C1_UNIT','0'))
if not 2<=U<=10:raise SystemExit('C1_UNIT must be 2..10')
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';AUD=R/f'reading/audit/french_c1_unit{U:02d}_generation_review.json';SEL=R/f'reading/audit/french_c1_unit{U:02d}_target_selection.json';PLAN=R/f'reading/audit/french_c1_unit{U:02d}_plan.json';OUT=R/f'reading/audit/french_c1_unit{U:02d}_frontier_lock.json'
def main():
 audit=json.loads(AUD.read_text(encoding='utf-8'));sel=json.loads(SEL.read_text(encoding='utf-8'));plan=json.loads(PLAN.read_text(encoding='utf-8'));c1blob=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();b2blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip();need=U*6
 if audit.get('status')!='PASS' or audit.get('c1_canonical_blob')!=c1blob or audit.get('b2_canonical_blob')!=b2blob:raise AssertionError(f'Unit{U:02d} audit/live mismatch')
 if sel.get('status')!='PASS' or plan.get('status')!='PASS' or audit.get('accepted_default_is_hard_quota') is not False:raise AssertionError(f'Unit{U:02d} metadata drift')
 rows=[json.loads(x) for x in C1.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=need or rows[-1]['id']!=f'fr-c1-u{U:02d}-p06' or [r['sequence'] for r in rows]!=list(range(1,need+1)):raise AssertionError(f'Unit{U:02d} frontier drift')
 start=(U-1)*6;expected={x['form'] for x in sel['selected']};actual={t['form'] for r in rows[start:start+5] for t in r['new_lexical_targets']}
 load=int(sel['new_targets_per_standard_passage'])
 if actual!=expected or len(actual)!=load*5 or rows[need-1]['new_lexical_targets']:raise AssertionError(f'Unit{U:02d} targets/checkpoint drift')
 out={'status':'PASS','scope':f'French C1 Unit {U:02d} frontier lock','b2_canonical_blob':b2blob,'c1_canonical_blob':c1blob,'passages':need,'questions':need*10,'answers':need*10,'completed_units':list(range(1,U+1)),'last_sequence':need,f'unit{U:02d}_theme':plan.get('theme'),f'unit{U:02d}_genres':plan.get('genres'),f'unit{U:02d}_word_band':audit.get('word_band'),f'unit{U:02d}_word_counts':audit.get('word_counts'),f'unit{U:02d}_target_forms':sorted(actual),f'unit{U:02d}_target_groups':sel.get('passage_groups'),f'unit{U:02d}_checkpoint_zero_new':True,'accepted_c1_default_new_targets_per_standard_passage':load,'accepted_default_is_hard_quota':False,f'unit{U:02d}_review_artifact':f'reading/audit/french_c1_unit{U:02d}_generation_review.json','note':f'Safe continuation lock after C1 Unit{U:02d}; not final French approval.'};OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

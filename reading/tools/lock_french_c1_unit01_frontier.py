#!/usr/bin/env python3
"""Lock French C1 Unit01 only after the strict calibration review passes."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';AUD=R/'reading/audit/french_c1_unit01_calibration_review.json';SEL=R/'reading/audit/french_c1_unit01_target_selection.json';PLAN=R/'reading/audit/french_c1_unit01_plan.json';OUT=R/'reading/audit/french_c1_unit01_frontier_lock.json'
def main():
 audit=json.loads(AUD.read_text(encoding='utf-8'));sel=json.loads(SEL.read_text(encoding='utf-8'));plan=json.loads(PLAN.read_text(encoding='utf-8'));c1blob=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();b2blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if audit.get('status')!='PASS' or audit.get('c1_canonical_blob')!=c1blob or audit.get('b2_canonical_blob')!=b2blob:raise AssertionError('C1 calibration audit/live blob mismatch')
 if audit.get('accepted_c1_default_new_targets_per_standard_passage')!=4 or audit.get('accepted_default_is_hard_quota') is not False:raise AssertionError('C1 calibration default not accepted as expected')
 if sel.get('status')!='PASS' or sel.get('b2_canonical_blob')!=b2blob or plan.get('status')!='PASS' or plan.get('b2_canonical_blob')!=b2blob:raise AssertionError('C1 selection/plan stale')
 rows=[json.loads(x) for x in C1.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=6 or [r['sequence'] for r in rows]!=list(range(1,7)) or rows[-1]['id']!='fr-c1-u01-p06':raise AssertionError('C1 Unit01 frontier not canonical')
 if any(len(r['questions'])!=10 or len(r['answer_key'])!=10 for r in rows):raise AssertionError('C1 Unit01 Q/A count drift')
 if any(len(r['new_lexical_targets'])!=4 for r in rows[:5]) or rows[5]['new_lexical_targets']:raise AssertionError('C1 Unit01 lexical load/checkpoint drift')
 expected={x['form'] for x in sel['selected']};actual={t['form'] for r in rows[:5] for t in r['new_lexical_targets']}
 if actual!=expected or len(actual)!=20:raise AssertionError('C1 Unit01 target-selection drift')
 out={'status':'PASS','scope':'French C1 Unit 01 calibrated frontier lock','b2_canonical_blob':b2blob,'c1_canonical_blob':c1blob,'passages':6,'questions':60,'answers':60,'completed_units':[1],'last_sequence':6,'unit01_theme':plan.get('theme'),'unit01_genres':plan.get('genres'),'unit01_word_band':audit.get('word_band'),'unit01_word_counts':audit.get('word_counts'),'unit01_target_forms':sorted(actual),'unit01_target_groups':sel.get('passage_groups'),'unit01_new_targets_per_standard_passage':4,'unit01_checkpoint_zero_new':True,'accepted_c1_default_new_targets_per_standard_passage':4,'accepted_default_is_hard_quota':False,'calibration_review_artifact':'reading/audit/french_c1_unit01_calibration_review.json','note':'Safe continuation lock for C1 Unit02. This is not final French approval.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

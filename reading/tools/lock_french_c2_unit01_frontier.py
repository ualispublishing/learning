#!/usr/bin/env python3
"""Lock exact C2 Unit01 calibrated frontier after strict review PASS."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';C2=R/'reading/french/c2/passages.jsonl';REVIEW=R/'reading/audit/french_c2_unit01_calibration_review.json';SEL=R/'reading/audit/french_c2_unit01_target_selection.json';OUT=R/'reading/audit/french_c2_unit01_frontier_lock.json'
def h(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def main():
 review=json.loads(REVIEW.read_text());sel=json.loads(SEL.read_text());rows=[json.loads(x) for x in C2.read_text().splitlines() if x.strip()];c1=h(C1);c2=h(C2)
 if review.get('status')!='PASS' or review.get('c1_canonical_blob')!=c1 or review.get('c2_canonical_blob')!=c2:raise AssertionError('C2 Unit01 review/live mismatch')
 if len(rows)!=6 or rows[-1]['id']!='fr-c2-u01-p06':raise AssertionError('C2 Unit01 exact frontier required')
 groups={k:[t['form'] for r in rows[:5] if r['id'].endswith(k) for t in r['new_lexical_targets']] for k in ['p01','p02','p03','p04','p05']}
 # Above comprehension by suffix yields one matching row per group.
 if any(len(v)!=5 for v in groups.values()):raise AssertionError(f'C2 target groups invalid {groups}')
 out={'status':'PASS','scope':'French C2 Unit01 calibrated frontier lock','c1_canonical_blob':c1,'c2_canonical_blob':c2,'passages':6,'questions':60,'answers':60,'completed_units':[1],'last_sequence':6,'unit01_theme':review['theme'],'unit01_genres':review['genres'],'unit01_word_band':review['word_band'],'unit01_word_counts':review['word_counts'],'unit01_target_forms':[t['form'] for r in rows[:5] for t in r['new_lexical_targets']],'unit01_target_groups':groups,'unit01_checkpoint_zero_new':True,'accepted_c2_default_new_targets_per_standard_passage':review['accepted_c2_default_new_targets_per_standard_passage'],'accepted_default_is_hard_quota':False,'durable_lexical_planning_band':review['durable_lexical_planning_band'],'source_policy':'validated french_top3000.csv continuation rank > 1000','unit01_review_artifact':'reading/audit/french_c2_unit01_calibration_review.json','note':'Safe calibrated continuation lock after C2 Unit01; not final French approval.'}
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASS','c2_blob':c2,'groups':groups},ensure_ascii=False))
if __name__=='__main__':main()

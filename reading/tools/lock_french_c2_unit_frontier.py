#!/usr/bin/env python3
"""Lock exact French C2 Unit N frontier after strict unit review PASS (C2_UNIT=2..10)."""
from __future__ import annotations
import json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';C2=R/'reading/french/c2/passages.jsonl';AUD=R/'reading/audit'
def h(p):return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def main():
 u=int(os.environ.get('C2_UNIT','0'))
 if not 2<=u<=10:raise AssertionError('C2_UNIT must be 2..10')
 review=json.loads((AUD/f'french_c2_unit{u:02d}_generation_review.json').read_text());sel=json.loads((AUD/f'french_c2_unit{u:02d}_target_selection.json').read_text());rows=[json.loads(x) for x in C2.read_text().splitlines() if x.strip()];c1=h(C1);c2=h(C2)
 if review.get('status')!='PASS' or review.get('unit')!=u or review.get('c1_canonical_blob')!=c1 or review.get('c2_canonical_blob')!=c2:raise AssertionError('C2 review/live mismatch')
 if len(rows)!=u*6 or rows[-1]['id']!=f'fr-c2-u{u:02d}-p06':raise AssertionError('C2 exact frontier mismatch')
 unit=rows[(u-1)*6:u*6];groups={f'p{i:02d}':[t['form'] for t in unit[i-1]['new_lexical_targets']] for i in range(1,6)}
 if any(len(v)!=5 for v in groups.values()) or unit[-1]['new_lexical_targets']:raise AssertionError(f'C2 unit target/checkpoint structure failure {groups}')
 out={'status':'PASS','scope':f'French C2 Unit{u:02d} frontier lock','c1_canonical_blob':c1,'c2_canonical_blob':c2,'passages':u*6,'questions':u*60,'answers':u*60,'completed_units':list(range(1,u+1)),'last_sequence':u*6,f'unit{u:02d}_theme':review['theme'],f'unit{u:02d}_genres':review['genres'],f'unit{u:02d}_word_band':review['word_band'],f'unit{u:02d}_word_counts':review['word_counts'],f'unit{u:02d}_target_forms':[t['form'] for r in unit[:5] for t in r['new_lexical_targets']],f'unit{u:02d}_target_groups':groups,f'unit{u:02d}_checkpoint_zero_new':True,'accepted_c2_default_new_targets_per_standard_passage':review['accepted_c2_default_new_targets_per_standard_passage'],'accepted_default_is_hard_quota':False,'durable_lexical_planning_band':review['durable_lexical_planning_band'],'source_policy':'validated french_top3000.csv continuation rank > 1000',f'unit{u:02d}_review_artifact':f'reading/audit/french_c2_unit{u:02d}_generation_review.json','note':f'Safe C2 Unit{u:02d} continuation lock; not final French approval.'}
 (AUD/f'french_c2_unit{u:02d}_frontier_lock.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASS','unit':u,'c2_blob':c2,'groups':groups},ensure_ascii=False))
if __name__=='__main__':main()

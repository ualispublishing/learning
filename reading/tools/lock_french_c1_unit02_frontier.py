#!/usr/bin/env python3
"""Lock French C1 Unit02 only after its strict generation review passes."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];C1=R/'reading/french/c1/passages.jsonl';B2=R/'reading/french/b2/passages.jsonl';AUD=R/'reading/audit/french_c1_unit02_generation_review.json';SEL=R/'reading/audit/french_c1_unit02_target_selection.json';PLAN=R/'reading/audit/french_c1_unit02_plan.json';OUT=R/'reading/audit/french_c1_unit02_frontier_lock.json'
def main():
 audit=json.loads(AUD.read_text(encoding='utf-8'));sel=json.loads(SEL.read_text(encoding='utf-8'));plan=json.loads(PLAN.read_text(encoding='utf-8'));c1blob=subprocess.check_output(['git','hash-object',str(C1)],text=True).strip();b2blob=subprocess.check_output(['git','hash-object',str(B2)],text=True).strip()
 if audit.get('status')!='PASS' or audit.get('c1_canonical_blob')!=c1blob or audit.get('b2_canonical_blob')!=b2blob:raise AssertionError('Unit02 audit/live blob mismatch')
 if sel.get('status')!='PASS' or plan.get('status')!='PASS' or audit.get('accepted_c1_default_new_targets_per_standard_passage')!=4 or audit.get('accepted_default_is_hard_quota') is not False:raise AssertionError('Unit02 plan/selection/default metadata drift')
 rows=[json.loads(x) for x in C1.read_text(encoding='utf-8').splitlines() if x.strip()]
 if len(rows)!=12 or rows[-1]['id']!='fr-c1-u02-p06' or [r['sequence'] for r in rows]!=list(range(1,13)):raise AssertionError('Unit02 canonical frontier drift')
 expected={x['form'] for x in sel['selected']};actual={t['form'] for r in rows[6:11] for t in r['new_lexical_targets']}
 if actual!=expected or len(actual)!=20 or rows[11]['new_lexical_targets']:raise AssertionError('Unit02 target/checkpoint drift')
 out={'status':'PASS','scope':'French C1 Unit 02 frontier lock','b2_canonical_blob':b2blob,'c1_canonical_blob':c1blob,'passages':12,'questions':120,'answers':120,'completed_units':[1,2],'last_sequence':12,'unit02_theme':plan.get('theme'),'unit02_genres':plan.get('genres'),'unit02_word_band':audit.get('word_band'),'unit02_word_counts':audit.get('word_counts'),'unit02_target_forms':sorted(actual),'unit02_target_groups':sel.get('passage_groups'),'unit02_checkpoint_zero_new':True,'accepted_c1_default_new_targets_per_standard_passage':4,'accepted_default_is_hard_quota':False,'unit02_review_artifact':'reading/audit/french_c1_unit02_generation_review.json','note':'Safe continuation lock for C1 Unit03; not final French approval.'};OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

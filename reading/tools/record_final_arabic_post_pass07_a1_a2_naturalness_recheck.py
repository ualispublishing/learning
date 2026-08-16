#!/usr/bin/env python3
"""Record current-text A1/A2 Pass11 revalidation after Pass07 expansions."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/audit/final_arabic_pass11_naturalness_review.json'
SNAP='reading/audit/final_arabic_post_pass07_a1_a2_naturalness_snapshot.jsonl'
REPAIR='reading/tools/repair_final_arabic_post_pass07_a1_naturalness.py'
data=json.loads(PATH.read_text(encoding='utf-8'))
if data.get('pass')!=11: raise SystemExit('unexpected Pass11 ledger')
a1=data['levels']['a1']; a2=data['levels']['a2']
# Fail closed if another chat has already advanced these fields.
if a1.get('high_confidence_repairs_applied')!=28 or a1.get('passages_touched')!=26:
    raise SystemExit('A1 ledger source state changed; inspect before recording recheck')
if a2.get('high_confidence_repairs_applied')!=7 or a2.get('passages_touched')!=7:
    raise SystemExit('A2 ledger source state changed; inspect before recording recheck')
for level in ('a1','a2'):
    if not data['levels'][level].get('review_complete'):
        raise SystemExit(f'{level}: original Pass11 must already be complete')
# Nine current-text A1 repairs; four overlap previously repaired passages and five are newly touched.
a1['high_confidence_repairs_applied']=37
a1['passages_touched']=31
for src in (SNAP,REPAIR):
    if src not in a1['repair_sources']: a1['repair_sources'].append(src)
a1['post_pass07_recheck']={
    'passages_rechecked':28,
    'high_confidence_repairs_applied':9,
    'passages_touched':9,
    'status':'PASS_AFTER_REPAIR',
    'snapshot':SNAP,
    'repair_source':REPAIR,
    'note':'All 28 A1 passages expanded after the original Pass11 read were re-read in current ending context. Nine high-confidence tense, event-order, logic, or MSA-idiom defects introduced by the Pass07 append-only expansions were repaired with literal-source, metadata, lexical-occurrence, and band guards; Pass07 remained at zero review flags after repair.'
}
a1['note']='Original full A1 Pass11 review plus targeted post-Pass07 current-text recheck are complete; current canonical A1 prose is covered by naturalness review evidence.'
if SNAP not in a2['repair_sources']: a2['repair_sources'].append(SNAP)
a2['post_pass07_recheck']={
    'passages_rechecked':38,
    'high_confidence_repairs_applied':0,
    'passages_touched':0,
    'status':'PASS_NO_ADDITIONAL_REPAIR',
    'snapshot':SNAP,
    'note':'All 38 A2 passages expanded after the original Pass11 read were re-read in current ending context. No additional high-confidence grammar, idiom, tense-continuity, event-order, or naturalness defect was found; stylistic-only alternatives were left unchanged.'
}
a2['note']='Original full A2 Pass11 review plus targeted post-Pass07 current-text recheck are complete; current canonical A2 prose is covered by naturalness review evidence.'
data['post_pass07_revalidation']={
    'levels':['A1','A2'],
    'passages_rechecked':66,
    'a1_passages':28,
    'a2_passages':38,
    'repairs_applied':9,
    'status':'COMPLETE',
    'snapshot':SNAP,
    'pass07_review_flags_after_repair':0,
    'coverage_metric_note':'Pass07 lexical coverage remains UNMEASURED, reported separately from actionable review flags.'
}
data['totals']['passages_fully_reviewed_in_completed_levels']=360
data['totals']['levels_complete']=6
data['totals']['levels_pending']=0
data['status']='COMPLETE'
data['final_approval_claim']=False
PATH.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'a1_total_repairs':37,'a1_unique_touched':31,'a1_rechecked':28,'a2_rechecked':38,'post_pass07_repairs':9,'levels_complete':6},ensure_ascii=False))

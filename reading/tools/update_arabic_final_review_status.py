#!/usr/bin/env python3
"""Synchronize Arabic final-review pass status into reading/STATUS.json.

This consumes persisted audit artifacts and never upgrades final approval while
the adversarial pass reports blockers.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
STATUS=ROOT/'reading/STATUS.json'
AUD=ROOT/'reading/audit'
FILES={
 'pass01':AUD/'final_arabic_pass01_data_integrity.json',
 'pass02':AUD/'final_arabic_pass02_lexical_exposure_integrity.json',
 'pass03':AUD/'final_arabic_pass03_question_composition.json',
 'pass04':AUD/'final_arabic_pass04_answer_evidence_alignment.json',
 'pass05':AUD/'final_arabic_pass05_script_orthography_hygiene.json',
 'pass06':AUD/'final_arabic_pass06_lexical_source_identity.json',
 'pass07':AUD/'final_arabic_pass07_cefr_difficulty_calibration.json',
 'pass08':AUD/'final_arabic_pass08_continuity_duplicate_balance.json',
 'pass09':AUD/'final_arabic_pass09_fluency_checkpoint.json',
 'pass10':AUD/'final_arabic_pass10_adjudication.json',
 'pass11':AUD/'final_arabic_pass11_naturalness_review.json',
 'pass12':AUD/'final_arabic_pass12_adversarial_gate_falsification.json',
}
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
 s=load(STATUS);a={k:load(v) for k,v in FILES.items()}
 adv=a['pass12'];assert adv.get('final_approval') is False
 pass_status={k:v.get('status','RECORDED') for k,v in a.items()}
 s['arabic_final_review']={
  'phase':'IN_PROGRESS',
  'minimum_distinct_passes_required':10,
  'distinct_passes_recorded':12,
  'pass_status':pass_status,
  'hard_regressions':adv.get('hard_regressions',[]),
  'approval_blockers':adv.get('final_approval_blockers',[]),
  'manual_naturalness_progress':a['pass11'].get('levels',{}),
  'final_approval':False,
  'adversarial_gate':'BLOCKED_WITHOUT_HARD_REGRESSION' if not adv.get('hard_regressions') else 'FAIL_REGRESSION',
  'key_clean_gates':['pass01','pass02','pass05','pass06','pass08','pass09'],
  'source_adjudicated_gate':'pass10',
 }
 s['phase']='Arabic A1-C2 generation is complete. Final multi-pass Arabic review is in progress; final approval remains blocked by question-composition, CEFR/length-and-coverage calibration, and unfinished A2-C2 manual naturalness review.'
 s['approved_passages']=0
 s['next_actions']=[
  'continue Pass 11 manual Arabic naturalness review from A2 through C2, recording and repairing only high-confidence defects',
  'resolve Pass 07 by recalibrating passage lengths to the documented CEFR production bands and measuring known-token coverage after text stabilization',
  'resolve Pass 03 with passage-specific question-set revisions where documented grammar/style or synthesis coverage is pedagogically weak; do not mass-template questions merely to satisfy quotas',
  'rerun dependent mechanical, lexical, evidence, and adversarial gates after substantive text/question revisions; do not grant final approval until Pass 12 has no blockers',
 ]
 files=s.setdefault('important_files',[])
 for p in [
  'reading/audit/final_arabic_pass12_adversarial_gate_falsification.json',
  'reading/audit/final_arabic_pass11_naturalness_review.json',
  'reading/audit/final_arabic_pass07_cefr_difficulty_calibration.json',
  'reading/audit/final_arabic_pass03_question_composition.json',
  'reading/audit/final_arabic_pass10_adjudication.json',
  'reading/tools/update_arabic_final_review_status.py',
 ]:
  if p not in files:files.append(p)
 STATUS.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'distinct_passes':12,'blockers':len(adv.get('final_approval_blockers',[])),'final_approval':False,'pass11_complete_levels':sum(1 for x in a['pass11'].get('levels',{}).values() if x.get('review_complete'))},ensure_ascii=False))
if __name__=='__main__':main()

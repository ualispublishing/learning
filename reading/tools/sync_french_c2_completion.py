#!/usr/bin/env python3
"""Transition French from sealed C2 generation to whole-corpus final audit."""
from __future__ import annotations
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2]
C1=R/'reading/french/c1/passages.jsonl'; C2=R/'reading/french/c2/passages.jsonl'; AUD=R/'reading/audit'
STATUS=R/'reading/STATUS.json'; TASKS=R/'reading/TASKS.md'; HANDOFF=R/'reading/AGENT_HANDOFF.md'; STATE=R/'reading/planning/C2_GENERATION_STATE.json'
def h(p): return subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
def main():
 rows=[json.loads(x) for x in C2.read_text(encoding='utf-8').splitlines() if x.strip()]; blob=h(C2); c1=h(C1)
 lock=json.loads((AUD/'french_c2_unit10_frontier_lock.json').read_text(encoding='utf-8')); review=json.loads((AUD/'french_c2_unit10_generation_review.json').read_text(encoding='utf-8'))
 if len(rows)!=60 or rows[-1]['id']!='fr-c2-u10-p06': raise AssertionError('French C2 exact 60-row completion required')
 if lock.get('status')!='PASS' or lock.get('last_sequence')!=60 or lock.get('c2_canonical_blob')!=blob or lock.get('c1_canonical_blob')!=c1: raise AssertionError('Unit10 lock/live mismatch')
 if review.get('status')!='PASS' or review.get('c2_canonical_blob')!=blob: raise AssertionError('Unit10 review/live mismatch')
 s=json.loads(STATUS.read_text(encoding='utf-8')); fr=s['french']; fr['state']='FINAL_AUDIT_ACTIVE'; fr['canonical_passages']=360; fr['questions']=3600; fr['answers']=3600; fr.setdefault('levels',{})['c2']=60
 c=fr.setdefault('c2_generation',{}); c.update({'status':'GENERATION_COMPLETE_PENDING_FINAL_AUDIT','passages':60,'questions':600,'answers':600,'completed_units':list(range(1,11)),'last_sequence':60,'canonical_blob':blob,'accepted_default_new_targets_per_standard_passage':lock.get('accepted_c2_default_new_targets_per_standard_passage',5),'accepted_default_is_hard_quota':False,'source_policy':'validated french_top3000.csv continuation rank > 1000','last_frontier_lock':'reading/audit/french_c2_unit10_frontier_lock.json','next_unit':None,'next_theme':None,'next_genres':[],'next_target_probe':None,'next_fresh_source_terms':None})
 fr['next_target']='Run the whole-French final review using at least 10 distinct audit lenses; repair defects, rerun integrity checks, and only then mark French finally approved.'
 s['updated']='2026-08-18'; s['phase']='Arabic sealed. French A1-C2 generation complete at 360 canonical passages; whole-French multi-pass final audit is now active. Urdu remains paused.'
 STATUS.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 # Replace the stale planning claim with the real, sealed completion state.
 st={'status':'GENERATION_COMPLETE_PENDING_FINAL_AUDIT','language':'fr','cefr':'C2','canonical_blob':blob,'passages':60,'units':10,'last_sequence':60,'completed_units':list(range(1,11)),'source_of_truth':'reading/french/c2/passages.jsonl + reading/audit/french_c2_unit10_frontier_lock.json','next_phase':'whole-French final audit (>=10 distinct passes)','note':'Generation completion is not final French approval.'}
 STATE.write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 t=TASKS.read_text(encoding='utf-8'); key='#### French whole-corpus final audit — IMMEDIATE NEXT'
 if key not in t:
  t+='\n\n'+key+'\n- [x] French C2 Unit 10 sealed; French generation is complete at 360 passages / 3,600 linked Q/A.\n- [ ] Run at least 10 distinct final-review passes from `reading/planning/GENERATION_FIRST_FINAL_AUDIT_POLICY.md`.\n- [ ] Consume `reading/audit/french_c2_deferred_quality_notes.json` and repair all confirmed defects.\n- [ ] Re-run schema/ID/link/count/exposure/spacing/duplicate/topic-balance checks after repairs.\n- [ ] Do not mark French finally approved until the adversarial final pass also succeeds.\n'
 TASKS.write_text(t,encoding='utf-8')
 hh=HANDOFF.read_text(encoding='utf-8'); key2='### French generation complete — final audit frontier'
 if key2 not in hh:
  hh+='\n\n'+key2+f'\n- French C2 Unit 10 sealed; canonical C2 blob `{blob}`.\n- French now has 360 canonical passages and 3,600 linked questions/answers across A1-C2.\n- Generation is complete, but French is **not finally approved**.\n- Next work is the policy-required >=10-pass whole-French final audit, beginning with known deferred qualitative notes and independent structural/linguistic/adversarial passes.\n'
 HANDOFF.write_text(hh,encoding='utf-8')
 print(json.dumps({'status':'PASS','c2_blob':blob,'french_passages':360,'french_qa':3600,'next_phase':'FINAL_AUDIT_ACTIVE'},ensure_ascii=False))
if __name__=='__main__': main()

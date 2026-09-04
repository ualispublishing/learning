#!/usr/bin/env python3
"""Synchronize VERIFICATION_TASKS.md after Arabic Gate B B2 Unit 8."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; R=ROOT/'reading'; P=R/'VERIFICATION_TASKS.md'
REL=R/'RELEASE_STATUS.json'; DEC=R/'audit/arabic_gate_b_decisions_2026-08-30/b2_u08.json'
REVIEWED=228; WITH=190; FINDINGS=387; BLOCKERS=1608
def rep(t,o,n):
 c=t.count(o)
 if c!=1: raise SystemExit(f'expected one anchor, got {c}: {o[:80]}')
 return t.replace(o,n,1)
def main():
 rel=json.loads(REL.read_text()); ar=rel['languages']['arabic']; g=ar['naturalness_review_progress']; d=ar['latest_deterministic_gate']
 if (g['fresh_records_reviewed'],g['fresh_records_with_findings'],g['fresh_findings'],d['open_findings'])!=(REVIEWED,WITH,FINDINGS,BLOCKERS): raise SystemExit('Unit 8 regenerated counters differ from expected frontier')
 dec=json.loads(DEC.read_text())
 if (dec['records_reviewed'],dec['records_with_findings'],dec['fresh_findings'])!=(6,3,3) or dec.get('quality_promotion') is not False or dec.get('release_claim') is not False: raise SystemExit('Unit 8 decision artifact drift')
 t=P.read_text(); marker='reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u08.json'
 if marker in t:
  if t.count(marker)!=1 or t.count('228/360')!=1 or f'**{BLOCKERS}**' not in t: raise SystemExit('partial Unit 8 sync')
  return
 t=rep(t,'Current release position: fresh deterministic revalidation is **FAIL** with **1632** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.','Current release position: fresh deterministic revalidation is **FAIL** with **1608** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.')
 t=rep(t,'Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1632**. This is a release-evidence gate, not semantic approval.','Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1608**. This is a release-evidence gate, not semantic approval.')
 u7='B2 Unit 7 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u07.json` — 6 current-corpus records reviewed, 3 repaired and 3 clean PASS records, with 5 fresh high-confidence grammar/naturalness/reference/assessment findings closed. Fresh Gate B progress is now 222/360 records; B2 remains in progress and this is not an educator/publication release claim.'
 u8=u7+'\n\nB2 Unit 8 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u08.json` — 6 current-corpus records reviewed, 3 repaired and 3 clean PASS records, with 3 fresh high-confidence naturalness/grammar findings closed. Fresh Gate B progress is now 228/360 records; B2 remains in progress and this is not an educator/publication release claim.'
 t=rep(t,u7,u8)
 c7='- [x] Arabic B2 Unit 7 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 5 fresh learner-facing findings across 3 records and recorded 3 clean PASS records with hash-bound decision evidence;'
 c8=c7+'\n- [x] Arabic B2 Unit 8 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 3 fresh learner-facing findings across 3 records and recorded 3 clean PASS records with hash-bound decision evidence;'
 t=rep(t,c7,c8)
 if t.count(marker)!=1 or t.count('228/360')!=1: raise SystemExit('Unit 8 summary bind failed')
 P.write_text(t)
if __name__=='__main__': main()

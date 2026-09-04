#!/usr/bin/env python3
"""Synchronize VERIFICATION_TASKS.md after Arabic Gate B B2 Unit 10."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; R=ROOT/'reading'; P=R/'VERIFICATION_TASKS.md'
REL=R/'RELEASE_STATUS.json'; DEC=R/'audit/arabic_gate_b_decisions_2026-08-30/b2_u10.json'
REVIEWED=240; WITH=200; FINDINGS=413; BLOCKERS=1560
def rep(t,o,n):
 c=t.count(o)
 if c!=1: raise SystemExit(f'expected one anchor, got {c}: {o[:80]}')
 return t.replace(o,n,1)
def main():
 rel=json.loads(REL.read_text()); ar=rel['languages']['arabic']; g=ar['naturalness_review_progress']; d=ar['latest_deterministic_gate']
 if (g['fresh_records_reviewed'],g['fresh_records_with_findings'],g['fresh_findings'],d['open_findings'])!=(REVIEWED,WITH,FINDINGS,BLOCKERS): raise SystemExit('Unit 10 regenerated counters differ from expected frontier')
 if 'B2' not in g.get('levels_completed',[]): raise SystemExit('B2 not marked complete after Unit 10')
 dec=json.loads(DEC.read_text())
 if (dec['records_reviewed'],dec['records_with_findings'],dec['fresh_findings'])!=(6,5,12) or dec.get('quality_promotion') is not False or dec.get('release_claim') is not False: raise SystemExit('Unit 10 decision artifact drift')
 t=P.read_text(); marker='reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u10.json'
 if marker in t:
  if t.count(marker)!=1 or t.count('240/360')!=1 or f'**{BLOCKERS}**' not in t: raise SystemExit('partial Unit 10 sync')
  return
 t=rep(t,'Current release position: fresh deterministic revalidation is **FAIL** with **1584** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.','Current release position: fresh deterministic revalidation is **FAIL** with **1560** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.')
 t=rep(t,'Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1584**. This is a release-evidence gate, not semantic approval.','Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1560**. This is a release-evidence gate, not semantic approval.')
 u9='B2 Unit 9 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u09.json` — 6 current-corpus records reviewed, 5 repaired and 1 clean PASS record, with 14 fresh high-confidence grammar/naturalness/semantic/assessment findings closed. Fresh Gate B progress is now 234/360 records; B2 remains in progress and this is not an educator/publication release claim.'
 u10=u9+'\n\nB2 Unit 10 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u10.json` — 6 current-corpus records reviewed, 5 repaired and 1 clean PASS record, with 12 fresh high-confidence grammar/naturalness/semantic/reference findings closed. Fresh Gate B progress is now 240/360 records; B2 Gate B is complete, the next ordered frontier is C1 Unit 1, and this is not an educator/publication release claim.'
 t=rep(t,u9,u10)
 c9='- [x] Arabic B2 Unit 9 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 14 fresh learner-facing findings across 5 records and recorded 1 clean PASS with hash-bound decision evidence;'
 c10=c9+'\n- [x] Arabic B2 Unit 10 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 12 fresh learner-facing findings across 5 records and recorded 1 clean PASS with hash-bound decision evidence; B2 Gate B is complete and C1 Unit 1 is next;'
 t=rep(t,c9,c10)
 if t.count(marker)!=1 or t.count('240/360')!=1: raise SystemExit('Unit 10 summary bind failed')
 P.write_text(t)
if __name__=='__main__': main()

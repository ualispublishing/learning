#!/usr/bin/env python3
"""Synchronize VERIFICATION_TASKS.md after Arabic Gate B B2 Unit 7."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; R=ROOT/'reading'; P=R/'VERIFICATION_TASKS.md'
REL=R/'RELEASE_STATUS.json'; DEC=R/'audit/arabic_gate_b_decisions_2026-08-30/b2_u07.json'
REVIEWED=222; WITH=187; FINDINGS=384; BLOCKERS=1632
def rep(t,o,n):
 c=t.count(o)
 if c!=1: raise SystemExit(f'expected one anchor, got {c}: {o[:80]}')
 return t.replace(o,n,1)
def main():
 rel=json.loads(REL.read_text()); ar=rel['languages']['arabic']; g=ar['naturalness_review_progress']; d=ar['latest_deterministic_gate']
 if (g['fresh_records_reviewed'],g['fresh_records_with_findings'],g['fresh_findings'],d['open_findings'])!=(REVIEWED,WITH,FINDINGS,BLOCKERS): raise SystemExit('Unit 7 regenerated counters differ from expected frontier')
 dec=json.loads(DEC.read_text())
 if (dec['records_reviewed'],dec['records_with_findings'],dec['fresh_findings'])!=(6,3,5) or dec.get('quality_promotion') is not False or dec.get('release_claim') is not False: raise SystemExit('Unit 7 decision artifact drift')
 t=P.read_text(); marker='reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u07.json'
 if marker in t:
  if t.count(marker)!=1 or t.count('222/360')!=1 or f'**{BLOCKERS}**' not in t: raise SystemExit('partial Unit 7 sync')
  return
 t=rep(t,'Current release position: fresh deterministic revalidation is **FAIL** with **1656** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.','Current release position: fresh deterministic revalidation is **FAIL** with **1632** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.')
 t=rep(t,'Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1656**. This is a release-evidence gate, not semantic approval.','Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1632**. This is a release-evidence gate, not semantic approval.')
 u6='B2 Unit 6 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u06.json` — 6 current-corpus records reviewed, 5 repaired and 1 clean PASS record, with 16 fresh high-confidence grammar/naturalness/reference/semantic/assessment findings closed. Fresh Gate B progress is now 216/360 records; B2 remains in progress and this is not an educator/publication release claim.'
 u7=u6+'\n\nB2 Unit 7 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u07.json` — 6 current-corpus records reviewed, 3 repaired and 3 clean PASS records, with 5 fresh high-confidence grammar/naturalness/reference/assessment findings closed. Fresh Gate B progress is now 222/360 records; B2 remains in progress and this is not an educator/publication release claim.'
 t=rep(t,u6,u7)
 c6='- [x] Arabic B2 Unit 6 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 16 fresh learner-facing findings across 5 records and recorded 1 clean PASS with hash-bound decision evidence;'
 c7=c6+'\n- [x] Arabic B2 Unit 7 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 5 fresh learner-facing findings across 3 records and recorded 3 clean PASS records with hash-bound decision evidence;'
 t=rep(t,c6,c7)
 if t.count(marker)!=1 or t.count('222/360')!=1: raise SystemExit('Unit 7 summary bind failed')
 P.write_text(t)
if __name__=='__main__': main()

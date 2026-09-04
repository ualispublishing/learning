#!/usr/bin/env python3
"""Synchronize VERIFICATION_TASKS.md after Arabic Gate B C1 Unit 2."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; R=ROOT/'reading'; P=R/'VERIFICATION_TASKS.md'
REL=R/'RELEASE_STATUS.json'; DEC=R/'audit/arabic_gate_b_decisions_2026-08-30/c1_u02.json'
REVIEWED=252; WITH=211; FINDINGS=431; BLOCKERS=1512
def rep(t,o,n):
 c=t.count(o)
 if c!=1: raise SystemExit(f'expected one anchor, got {c}: {o[:80]}')
 return t.replace(o,n,1)
def main():
 rel=json.loads(REL.read_text()); ar=rel['languages']['arabic']; g=ar['naturalness_review_progress']; d=ar['latest_deterministic_gate']
 if (g['fresh_records_reviewed'],g['fresh_records_with_findings'],g['fresh_findings'],d['open_findings'])!=(REVIEWED,WITH,FINDINGS,BLOCKERS): raise SystemExit('C1 Unit 2 regenerated counters differ from expected frontier')
 if g.get('levels_completed') != ['A1','A2','B1','B2']: raise SystemExit('unexpected completed levels after C1 Unit 2')
 dec=json.loads(DEC.read_text())
 if (dec['records_reviewed'],dec['records_with_findings'],dec['fresh_findings'])!=(6,6,8) or dec.get('quality_promotion') is not False or dec.get('release_claim') is not False: raise SystemExit('C1 Unit 2 decision artifact drift')
 t=P.read_text(); marker='reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u02.json'
 if marker in t:
  if t.count(marker)!=1 or t.count('252/360')!=1 or f'**{BLOCKERS}**' not in t: raise SystemExit('partial C1 Unit 2 sync')
  return
 t=rep(t,'Current release position: fresh deterministic revalidation is **FAIL** with **1536** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.','Current release position: fresh deterministic revalidation is **FAIL** with **1512** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.')
 t=rep(t,'Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1536**. This is a release-evidence gate, not semantic approval.','Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1512**. This is a release-evidence gate, not semantic approval.')
 u1='C1 Unit 1 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u01.json` — 6 current-corpus records reviewed, 5 repaired and 1 clean PASS record, with 10 fresh high-confidence grammar/naturalness/reference/semantic/assessment findings closed. Fresh Gate B progress is now 246/360 records; C1 is in progress and this is not an educator/publication release claim.'
 u2=u1+'\n\nC1 Unit 2 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u02.json` — 6 current-corpus records reviewed and repaired, with 8 fresh high-confidence grammar/naturalness/semantic findings closed. Fresh Gate B progress is now 252/360 records; C1 remains in progress and this is not an educator/publication release claim.'
 t=rep(t,u1,u2)
 c1='- [x] Arabic C1 Unit 1 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 10 fresh learner-facing findings across 5 records and recorded 1 clean PASS with hash-bound decision evidence;'
 c2=c1+'\n- [x] Arabic C1 Unit 2 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 8 fresh learner-facing findings across all 6 records with hash-bound decision evidence;'
 t=rep(t,c1,c2)
 if t.count(marker)!=1 or t.count('252/360')!=1: raise SystemExit('C1 Unit 2 summary bind failed')
 P.write_text(t)
if __name__=='__main__': main()

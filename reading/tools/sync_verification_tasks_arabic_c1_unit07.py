#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; R=ROOT/'reading'; P=R/'VERIFICATION_TASKS.md'; REL=R/'RELEASE_STATUS.json'; DEC=R/'audit/arabic_gate_b_decisions_2026-08-30/c1_u07.json'
REVIEWED=282; WITH=235; FINDINGS=463; BLOCKERS=1392
def rep(t,o,n):
 if t.count(o)!=1: raise SystemExit('anchor drift: '+o[:80])
 return t.replace(o,n,1)
def main():
 ar=json.loads(REL.read_text())['languages']['arabic']; g=ar['naturalness_review_progress']; d=ar['latest_deterministic_gate']; dec=json.loads(DEC.read_text())
 if (g['fresh_records_reviewed'],g['fresh_records_with_findings'],g['fresh_findings'],d['open_findings'])!=(REVIEWED,WITH,FINDINGS,BLOCKERS): raise SystemExit('counter drift')
 if g.get('levels_completed')!=['A1','A2','B1','B2']: raise SystemExit('level frontier drift')
 if (dec['records_reviewed'],dec['records_with_findings'],dec['fresh_findings'])!=(6,6,6) or dec.get('quality_promotion') is not False or dec.get('release_claim') is not False: raise SystemExit('decision drift')
 t=P.read_text(); marker='reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u07.json'
 if marker in t: return
 t=rep(t,'Current release position: fresh deterministic revalidation is **FAIL** with **1416** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.','Current release position: fresh deterministic revalidation is **FAIL** with **1392** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.')
 t=rep(t,'Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1416**. This is a release-evidence gate, not semantic approval.','Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1392**. This is a release-evidence gate, not semantic approval.')
 u6='C1 Unit 6 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u06.json` — 6 current-corpus records reviewed, 5 repaired and 1 clean PASS record, with 5 fresh high-confidence grammar/assessment findings closed. Fresh Gate B progress is now 276/360 records; C1 remains in progress and this is not an educator/publication release claim.'
 t=rep(t,u6,u6+'\n\nC1 Unit 7 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u07.json` — 6 current-corpus records reviewed and repaired, with 6 fresh high-confidence assessment-alignment findings closed. Fresh Gate B progress is now 282/360 records; C1 remains in progress and this is not an educator/publication release claim.')
 c6='- [x] Arabic C1 Unit 6 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 5 fresh learner-facing findings across 5 records and recorded 1 clean PASS with hash-bound decision evidence;'
 t=rep(t,c6,c6+'\n- [x] Arabic C1 Unit 7 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 6 fresh summary-answer alignment findings across all 6 records with hash-bound decision evidence;')
 P.write_text(t)
if __name__=='__main__': main()

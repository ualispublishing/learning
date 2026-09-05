#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; R=ROOT/'reading'; P=R/'VERIFICATION_TASKS.md'; REL=R/'RELEASE_STATUS.json'; DEC=R/'audit/arabic_gate_b_decisions_2026-08-30/c2_u04.json'
REVIEWED=324; WITH=275; FINDINGS=506; BLOCKERS=1224
def rep(t,o,n):
 if t.count(o)!=1: raise SystemExit('anchor drift: '+o[:80])
 return t.replace(o,n,1)
def main():
 ar=json.loads(REL.read_text())['languages']['arabic']; g=ar['naturalness_review_progress']; d=ar['latest_deterministic_gate']; dec=json.loads(DEC.read_text())
 if (g['fresh_records_reviewed'],g['fresh_records_with_findings'],g['fresh_findings'],d['open_findings'])!=(REVIEWED,WITH,FINDINGS,BLOCKERS): raise SystemExit('counter drift')
 if g.get('levels_completed')!=['A1','A2','B1','B2','C1']: raise SystemExit('C2 frontier drift')
 if (dec['records_reviewed'],dec['records_with_findings'],dec['fresh_findings'])!=(6,6,8) or dec.get('quality_promotion') is not False or dec.get('release_claim') is not False: raise SystemExit('decision drift')
 t=P.read_text(); marker='reading/audit/arabic_gate_b_decisions_2026-08-30/c2_u04.json'
 if marker in t: return
 t=rep(t,'Current release position: fresh deterministic revalidation is **FAIL** with **1248** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.','Current release position: fresh deterministic revalidation is **FAIL** with **1224** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.')
 t=rep(t,'Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1248**. This is a release-evidence gate, not semantic approval.','Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1224**. This is a release-evidence gate, not semantic approval.')
 u3='C2 Unit 3 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c2_u03.json` — 6 current-corpus records reviewed, 4 repaired and 2 clean PASS records, with 4 fresh high-confidence summary-answer assessment/reference findings closed. Fresh Gate B progress is now 318/360 records; C2 remains in progress and this is not an educator/publication release claim.'
 t=rep(t,u3,u3+'\n\nC2 Unit 4 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c2_u04.json` — 6 current-corpus records reviewed and repaired, with 8 fresh high-confidence summary-answer assessment/naturalness/semantic findings closed. Fresh Gate B progress is now 324/360 records; C2 remains in progress and this is not an educator/publication release claim.')
 c3='- [x] Arabic C2 Unit 3 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 4 fresh summary-answer assessment/reference findings across 4 records and recorded 2 clean PASS records with hash-bound decision evidence;'
 t=rep(t,c3,c3+'\n- [x] Arabic C2 Unit 4 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 8 fresh summary-answer assessment/naturalness/semantic findings across all 6 records with hash-bound decision evidence;')
 P.write_text(t)
if __name__=='__main__': main()

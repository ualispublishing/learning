#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; R=ROOT/'reading'; P=R/'VERIFICATION_TASKS.md'; REL=R/'RELEASE_STATUS.json'; DEC=R/'audit/arabic_gate_b_decisions_2026-08-30/c1_u09.json'
REVIEWED=294; WITH=247; FINDINGS=476; BLOCKERS=1344
def rep(t,o,n):
 if t.count(o)!=1: raise SystemExit('anchor drift: '+o[:80])
 return t.replace(o,n,1)
def main():
 ar=json.loads(REL.read_text())['languages']['arabic']; g=ar['naturalness_review_progress']; d=ar['latest_deterministic_gate']; dec=json.loads(DEC.read_text())
 if (g['fresh_records_reviewed'],g['fresh_records_with_findings'],g['fresh_findings'],d['open_findings'])!=(REVIEWED,WITH,FINDINGS,BLOCKERS): raise SystemExit('counter drift')
 if g.get('levels_completed')!=['A1','A2','B1','B2']: raise SystemExit('level frontier drift')
 if (dec['records_reviewed'],dec['records_with_findings'],dec['fresh_findings'])!=(6,6,7) or dec.get('quality_promotion') is not False or dec.get('release_claim') is not False: raise SystemExit('decision drift')
 t=P.read_text(); marker='reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u09.json'
 if marker in t: return
 t=rep(t,'Current release position: fresh deterministic revalidation is **FAIL** with **1368** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.','Current release position: fresh deterministic revalidation is **FAIL** with **1344** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.')
 t=rep(t,'Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1368**. This is a release-evidence gate, not semantic approval.','Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1344**. This is a release-evidence gate, not semantic approval.')
 u8='C1 Unit 8 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u08.json` — 6 current-corpus records reviewed and repaired, with 6 fresh high-confidence summary-answer assessment-alignment findings closed. Fresh Gate B progress is now 288/360 records; C1 remains in progress and this is not an educator/publication release claim.'
 t=rep(t,u8,u8+'\n\nC1 Unit 9 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c1_u09.json` — 6 current-corpus records reviewed and repaired, with 7 fresh high-confidence assessment-alignment and semantic findings closed. Fresh Gate B progress is now 294/360 records; C1 remains in progress and this is not an educator/publication release claim.')
 c8='- [x] Arabic C1 Unit 8 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 6 fresh summary-answer alignment findings across all 6 records with hash-bound decision evidence;'
 t=rep(t,c8,c8+'\n- [x] Arabic C1 Unit 9 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 7 fresh findings across all 6 records with hash-bound decision evidence;')
 P.write_text(t)
if __name__=='__main__': main()

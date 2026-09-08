#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'reading/VERIFICATION_TASKS.md'
E0="B1 Unit 9 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/b1_u09.json` — 6 exact-current records / 60 question-answer pairs reviewed as clean PASSes with no fresh Gate C findings and no learner-facing mutation. Fresh Gate C progress is 174/360 records and 1,740/3,600 Q/A pairs; A1 and A2 remain the completed Gate C levels, B1 remains in progress, and this is not an educator/publication release claim."
E1="B1 Unit 10 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/b1_u10.json` — 6 exact-current records / 60 question-answer pairs reviewed as clean PASSes with no fresh Gate C findings and no learner-facing mutation. Fresh Gate C progress is 180/360 records and 1,800/3,600 Q/A pairs; A1, A2, and B1 are now the completed Gate C levels, overall Gate C remains in progress, and this is not an educator/publication release claim."
C0="- [x] Arabic B1 Unit 9 Gate C batch: reviewed 6 passages / 60 question-answer pairs as six clean PASSes with no fresh findings or learner-facing mutation; Gate C is 174/360 records overall, A1/A2 remain complete, and B1 remains in progress; review remains internal-only;"
C1="- [x] Arabic B1 Unit 10 Gate C batch: reviewed 6 passages / 60 question-answer pairs as six clean PASSes with no fresh findings or learner-facing mutation; Gate C is 180/360 records overall, A1/A2/B1 are complete, and overall Gate C remains in progress; review remains internal-only;"
def main():
 t=P.read_text()
 if 'Current release position: fresh deterministic revalidation is **FAIL** with **1080** open evidence findings' not in t:raise SystemExit('blocker frontier drift')
 if (E1 in t)!=(C1 in t):raise SystemExit('partial B1 Unit 10 queue state')
 if E1 in t:return
 if E0 not in t or C0 not in t:raise SystemExit('B1 Unit 9 anchors missing')
 P.write_text(t.replace(E0,E0+'\n\n'+E1,1).replace(C0,C0+'\n'+C1,1))
 print('B1 Unit 10 clean Gate C completion evidence synchronized')
if __name__=='__main__':main()

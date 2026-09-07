#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PATH=ROOT/'reading/VERIFICATION_TASKS.md'
E0="A2 Unit 10 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u10.json` — 6 exact-current records / 60 question-answer pairs reviewed as clean PASSes with no fresh Gate C findings and no learner-facing mutation. Fresh Gate C progress is 120/360 records and 1,200/3,600 Q/A pairs; A1 and A2 are now completed Gate C levels, while the review remains internal-only and this is not an educator/publication release claim."
E1="B1 Unit 1 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/b1_u01.json` — 6 exact-current records / 60 question-answer pairs reviewed as clean PASSes with no fresh Gate C findings and no learner-facing mutation. Fresh Gate C progress is 126/360 records and 1,260/3,600 Q/A pairs; A1 and A2 remain the completed Gate C levels, B1 is now in progress, and this is not an educator/publication release claim."
C0="- [x] Arabic A2 Unit 10 Gate C batch: reviewed 6 passages / 60 question-answer pairs as six clean PASSes with no fresh findings or learner-facing mutation; A2 Gate C is complete, Gate C is 120/360 records overall, and A1/A2 are the completed levels; review remains internal-only;"
C1="- [x] Arabic B1 Unit 1 Gate C batch: reviewed 6 passages / 60 question-answer pairs as six clean PASSes with no fresh findings or learner-facing mutation; Gate C is 126/360 records overall, A1/A2 remain complete, and B1 is in progress; review remains internal-only;"
def main():
 text=PATH.read_text(encoding='utf-8')
 if 'Current release position: fresh deterministic revalidation is **FAIL** with **1080** open evidence findings' not in text: raise SystemExit('blocker frontier drift')
 if (E1 in text)!=(C1 in text): raise SystemExit('partial B1 Unit 1 queue state')
 if E1 in text: print('B1 Unit 1 evidence already synchronized'); return
 if E0 not in text or C0 not in text: raise SystemExit('A2 Unit 10 anchors missing')
 PATH.write_text(text.replace(E0,E0+'\n\n'+E1,1).replace(C0,C0+'\n'+C1,1),encoding='utf-8')
 print('B1 Unit 1 clean Gate C verification evidence synchronized; release claim unchanged')
if __name__=='__main__':main()

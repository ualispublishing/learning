#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PATH=ROOT/'reading/VERIFICATION_TASKS.md'
E9="A2 Unit 9 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u09.json` — 6 exact-current records / 60 question-answer pairs reviewed; 3 competing-answer ambiguities across story, version/copy, and restaurant transfer items were repaired in `ar-a2-u09-p01` through `p03`; `p04` through `p06` are clean PASSes. Fresh Gate C progress is 114/360 records and 1,140/3,600 Q/A pairs; A1 remains the only completed Gate C level and this is not an educator/publication release claim."
E10="A2 Unit 10 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u10.json` — 6 exact-current records / 60 question-answer pairs reviewed as clean PASSes with no fresh Gate C findings and no learner-facing mutation. Fresh Gate C progress is 120/360 records and 1,200/3,600 Q/A pairs; A1 and A2 are now completed Gate C levels, while the review remains internal-only and this is not an educator/publication release claim."
C9="- [x] Arabic A2 Unit 9 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 3 competing-answer ambiguities across `ar-a2-u09-p01` through `p03`, recorded `p04` through `p06` as clean PASSes, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 114/360 records and remains internal-only;"
C10="- [x] Arabic A2 Unit 10 Gate C batch: reviewed 6 passages / 60 question-answer pairs as six clean PASSes with no fresh findings or learner-facing mutation; A2 Gate C is complete, Gate C is 120/360 records overall, and A1/A2 are the completed levels; review remains internal-only;"
def main():
 text=PATH.read_text(encoding='utf-8')
 if 'Current release position: fresh deterministic revalidation is **FAIL** with **1080** open evidence findings' not in text:raise SystemExit('blocker frontier drift')
 if (E10 in text)!=(C10 in text):raise SystemExit('partial A2 Unit 10 queue state')
 if E10 in text:print('A2 Unit 10 evidence already synchronized');return
 if E9 not in text or C9 not in text:raise SystemExit('A2 Unit 9 anchors missing')
 PATH.write_text(text.replace(E9,E9+'\n\n'+E10,1).replace(C9,C9+'\n'+C10,1),encoding='utf-8');print('A2 Unit 10 clean verification evidence synchronized; A2 Gate C complete; release claim unchanged')
if __name__=='__main__':main()

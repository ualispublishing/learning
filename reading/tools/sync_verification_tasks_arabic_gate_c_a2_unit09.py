#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PATH=ROOT/'reading/VERIFICATION_TASKS.md'
E8="A2 Unit 8 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u08.json` — 6 exact-current records / 60 question-answer pairs reviewed; 6 competing-answer ambiguities across area, materials, usage, energy, growth, and community transfer items were repaired across `ar-a2-u08-p01`, `p02`, `p03`, and `p05`; `p04` and `p06` are clean PASSes. Fresh Gate C progress is 108/360 records and 1,080/3,600 Q/A pairs; A1 remains the only completed Gate C level and this is not an educator/publication release claim."
E9="A2 Unit 9 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u09.json` — 6 exact-current records / 60 question-answer pairs reviewed; 3 competing-answer ambiguities across story, version/copy, and restaurant transfer items were repaired in `ar-a2-u09-p01` through `p03`; `p04` through `p06` are clean PASSes. Fresh Gate C progress is 114/360 records and 1,140/3,600 Q/A pairs; A1 remains the only completed Gate C level and this is not an educator/publication release claim."
C8="- [x] Arabic A2 Unit 8 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 6 competing-answer ambiguities across `ar-a2-u08-p01`, `p02`, `p03`, and `p05`, recorded `p04` and `p06` as clean PASSes, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 108/360 records and remains internal-only;"
C9="- [x] Arabic A2 Unit 9 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 3 competing-answer ambiguities across `ar-a2-u09-p01` through `p03`, recorded `p04` through `p06` as clean PASSes, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 114/360 records and remains internal-only;"
def main():
 text=PATH.read_text(encoding='utf-8')
 if 'Current release position: fresh deterministic revalidation is **FAIL** with **1080** open evidence findings' not in text:raise SystemExit('blocker frontier drift')
 if (E9 in text)!=(C9 in text):raise SystemExit('partial A2 Unit 9 queue state')
 if E9 in text:print('A2 Unit 9 evidence already synchronized');return
 if E8 not in text or C8 not in text:raise SystemExit('A2 Unit 8 anchors missing')
 PATH.write_text(text.replace(E8,E8+'\n\n'+E9,1).replace(C8,C8+'\n'+C9,1),encoding='utf-8');print('A2 Unit 9 verification evidence synchronized; release claim unchanged')
if __name__=='__main__':main()

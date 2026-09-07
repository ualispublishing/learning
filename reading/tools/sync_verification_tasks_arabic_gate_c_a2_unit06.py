#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PATH=ROOT/'reading/VERIFICATION_TASKS.md'
E5="A2 Unit 5 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u05.json` — 6 exact-current records / 60 question-answer pairs reviewed; 10 competing-answer ambiguities across photography, contest, thinking, follow-up, step, projects, habit, getting acquainted, training, and experience transfer items were repaired across `ar-a2-u05-p01` through `p05`; `p06` is a clean PASS. Fresh Gate C progress is 90/360 records and 900/3,600 Q/A pairs; A1 remains the only completed Gate C level and this is not an educator/publication release claim."
E6="A2 Unit 6 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u06.json` — 6 exact-current records / 60 question-answer pairs reviewed; 10 competing-answer ambiguities across airplane, airport, train, waiting, transport, means, stopping, suitability, village, and sea transfer items were repaired across `ar-a2-u06-p01` through `p05`; `p06` is a clean PASS. Fresh Gate C progress is 96/360 records and 960/3,600 Q/A pairs; A1 remains the only completed Gate C level and this is not an educator/publication release claim."
C5="- [x] Arabic A2 Unit 5 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 10 competing-answer ambiguities across `ar-a2-u05-p01` through `p05`, recorded `p06` as a clean PASS, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 90/360 records and remains internal-only;"
C6="- [x] Arabic A2 Unit 6 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 10 competing-answer ambiguities across `ar-a2-u06-p01` through `p05`, recorded `p06` as a clean PASS, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 96/360 records and remains internal-only;"
def main():
 text=PATH.read_text(encoding='utf-8')
 if 'Current release position: fresh deterministic revalidation is **FAIL** with **1080** open evidence findings' not in text:raise SystemExit('blocker frontier drift')
 if (E6 in text)!=(C6 in text):raise SystemExit('partial A2 Unit 6 queue state')
 if E6 in text:print('A2 Unit 6 evidence already synchronized');return
 if E5 not in text or C5 not in text:raise SystemExit('A2 Unit 5 anchors missing')
 PATH.write_text(text.replace(E5,E5+'\n\n'+E6,1).replace(C5,C5+'\n'+C6,1),encoding='utf-8');print('A2 Unit 6 verification evidence synchronized; release claim unchanged')
if __name__=='__main__':main()

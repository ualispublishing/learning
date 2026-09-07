#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PATH=ROOT/'reading/VERIFICATION_TASKS.md'
E6="A2 Unit 6 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u06.json` — 6 exact-current records / 60 question-answer pairs reviewed; 10 competing-answer ambiguities across airplane, airport, train, waiting, transport, means, stopping, suitability, village, and sea transfer items were repaired across `ar-a2-u06-p01` through `p05`; `p06` is a clean PASS. Fresh Gate C progress is 96/360 records and 960/3,600 Q/A pairs; A1 remains the only completed Gate C level and this is not an educator/publication release claim."
E7="A2 Unit 7 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u07.json` — 6 exact-current records / 60 question-answer pairs reviewed; 10 competing-answer ambiguities across occasion, audience, press, statement, inquiry, effect, announcement, observed result, main idea, and forecast transfer items were repaired across `ar-a2-u07-p01` through `p05`; `p06` is a clean PASS. Fresh Gate C progress is 102/360 records and 1,020/3,600 Q/A pairs; A1 remains the only completed Gate C level and this is not an educator/publication release claim."
C6="- [x] Arabic A2 Unit 6 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 10 competing-answer ambiguities across `ar-a2-u06-p01` through `p05`, recorded `p06` as a clean PASS, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 96/360 records and remains internal-only;"
C7="- [x] Arabic A2 Unit 7 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 10 competing-answer ambiguities across `ar-a2-u07-p01` through `p05`, recorded `p06` as a clean PASS, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 102/360 records and remains internal-only;"
def main():
 text=PATH.read_text(encoding='utf-8')
 if 'Current release position: fresh deterministic revalidation is **FAIL** with **1080** open evidence findings' not in text:raise SystemExit('blocker frontier drift')
 if (E7 in text)!=(C7 in text):raise SystemExit('partial A2 Unit 7 queue state')
 if E7 in text:print('A2 Unit 7 evidence already synchronized');return
 if E6 not in text or C6 not in text:raise SystemExit('A2 Unit 6 anchors missing')
 PATH.write_text(text.replace(E6,E6+'\n\n'+E7,1).replace(C6,C6+'\n'+C7,1),encoding='utf-8');print('A2 Unit 7 verification evidence synchronized; release claim unchanged')
if __name__=='__main__':main()

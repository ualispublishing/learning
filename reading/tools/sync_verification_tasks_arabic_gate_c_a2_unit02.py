#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PATH=ROOT/'reading/VERIFICATION_TASKS.md'
E1="A2 Unit 1 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u01.json` — 6 exact-current records / 60 question-answer pairs reviewed; 10 competing-answer ambiguities across street, service, phone, bank, announcement, message, visit, department, list, and price transfer items were repaired across `ar-a2-u01-p01` through `p05`; `p06` is a clean PASS. Fresh Gate C progress is 66/360 records and 660/3,600 Q/A pairs; A1 remains the only completed Gate C level and this is not an educator/publication release claim."
E2="A2 Unit 2 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u02.json` — 6 exact-current records / 60 question-answer pairs reviewed; 10 competing-answer ambiguities across appointment, reply, certainty, next, calling, later time, choice, current plan, course, and organization transfer items were repaired across `ar-a2-u02-p01` through `p05`; `p06` is a clean PASS. Fresh Gate C progress is 72/360 records and 720/3,600 Q/A pairs; A1 remains the only completed Gate C level and this is not an educator/publication release claim."
C1="- [x] Arabic A2 Unit 1 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 10 competing-answer ambiguities across `ar-a2-u01-p01` through `p05`, recorded `p06` as a clean PASS, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 66/360 records and remains internal-only;"
C2="- [x] Arabic A2 Unit 2 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 10 competing-answer ambiguities across `ar-a2-u02-p01` through `p05`, recorded `p06` as a clean PASS, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 72/360 records and remains internal-only;"
def main():
 text=PATH.read_text(encoding='utf-8')
 if 'Current release position: fresh deterministic revalidation is **FAIL** with **1080** open evidence findings' not in text: raise SystemExit('blocker frontier drift')
 if (E2 in text)!=(C2 in text): raise SystemExit('partial A2 Unit 2 queue state')
 if E2 in text: print('A2 Unit 2 evidence already synchronized'); return
 if E1 not in text or C1 not in text: raise SystemExit('A2 Unit 1 anchors missing')
 PATH.write_text(text.replace(E1,E1+'\n\n'+E2,1).replace(C1,C1+'\n'+C2,1),encoding='utf-8'); print('A2 Unit 2 verification evidence synchronized; release claim unchanged')
if __name__=='__main__':main()

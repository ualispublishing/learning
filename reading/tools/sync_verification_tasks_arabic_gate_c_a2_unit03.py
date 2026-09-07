#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PATH=ROOT/'reading/VERIFICATION_TASKS.md'
E2="A2 Unit 2 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u02.json` — 6 exact-current records / 60 question-answer pairs reviewed; 10 competing-answer ambiguities across appointment, reply, certainty, next, calling, later time, choice, current plan, course, and organization transfer items were repaired across `ar-a2-u02-p01` through `p05`; `p06` is a clean PASS. Fresh Gate C progress is 72/360 records and 720/3,600 Q/A pairs; A1 remains the only completed Gate C level and this is not an educator/publication release claim."
E3="A2 Unit 3 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u03.json` — 6 exact-current records / 60 question-answer pairs reviewed; 10 competing-answer ambiguities across recently, again, recording, look, ceremony, time, most, thought, effect, and won transfer items were repaired across `ar-a2-u03-p01` through `p05`; `p06` is a clean PASS. Fresh Gate C progress is 78/360 records and 780/3,600 Q/A pairs; A1 remains the only completed Gate C level and this is not an educator/publication release claim."
C2="- [x] Arabic A2 Unit 2 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 10 competing-answer ambiguities across `ar-a2-u02-p01` through `p05`, recorded `p06` as a clean PASS, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 72/360 records and remains internal-only;"
C3="- [x] Arabic A2 Unit 3 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 10 competing-answer ambiguities across `ar-a2-u03-p01` through `p05`, recorded `p06` as a clean PASS, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 78/360 records and remains internal-only;"
def main():
 text=PATH.read_text(encoding='utf-8')
 if 'Current release position: fresh deterministic revalidation is **FAIL** with **1080** open evidence findings' not in text: raise SystemExit('blocker frontier drift')
 if (E3 in text)!=(C3 in text): raise SystemExit('partial A2 Unit 3 queue state')
 if E3 in text: print('A2 Unit 3 evidence already synchronized'); return
 if E2 not in text or C2 not in text: raise SystemExit('A2 Unit 2 anchors missing')
 PATH.write_text(text.replace(E2,E2+'\n\n'+E3,1).replace(C2,C2+'\n'+C3,1),encoding='utf-8'); print('A2 Unit 3 verification evidence synchronized; release claim unchanged')
if __name__=='__main__':main()

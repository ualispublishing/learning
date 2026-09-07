#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PATH=ROOT/'reading/VERIFICATION_TASKS.md'
E3="A2 Unit 3 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u03.json` — 6 exact-current records / 60 question-answer pairs reviewed; 10 competing-answer ambiguities across recently, again, recording, look, ceremony, time, most, thought, effect, and won transfer items were repaired across `ar-a2-u03-p01` through `p05`; `p06` is a clean PASS. Fresh Gate C progress is 78/360 records and 780/3,600 Q/A pairs; A1 remains the only completed Gate C level and this is not an educator/publication release claim."
E4="A2 Unit 4 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u04.json` — 6 exact-current records / 60 question-answer pairs reviewed; 10 transfer-prompt defects were repaired across `ar-a2-u04-p01` through `p05`, including an unnatural size-target context and a malformed worth-it cloze stem; `p06` is a clean PASS. Fresh Gate C progress is 84/360 records and 840/3,600 Q/A pairs; A1 remains the only completed Gate C level and this is not an educator/publication release claim."
C3="- [x] Arabic A2 Unit 3 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 10 competing-answer ambiguities across `ar-a2-u03-p01` through `p05`, recorded `p06` as a clean PASS, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 78/360 records and remains internal-only;"
C4="- [x] Arabic A2 Unit 4 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 10 transfer-prompt defects across `ar-a2-u04-p01` through `p05` (including the size-context and malformed worth-it stems), recorded `p06` as a clean PASS, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 84/360 records and remains internal-only;"
def main():
 text=PATH.read_text(encoding='utf-8')
 if 'Current release position: fresh deterministic revalidation is **FAIL** with **1080** open evidence findings' not in text: raise SystemExit('blocker frontier drift')
 if (E4 in text)!=(C4 in text): raise SystemExit('partial A2 Unit 4 queue state')
 if E4 in text: print('A2 Unit 4 evidence already synchronized'); return
 if E3 not in text or C3 not in text: raise SystemExit('A2 Unit 3 anchors missing')
 PATH.write_text(text.replace(E3,E3+'\n\n'+E4,1).replace(C3,C3+'\n'+C4,1),encoding='utf-8'); print('A2 Unit 4 verification evidence synchronized; release claim unchanged')
if __name__=='__main__':main()

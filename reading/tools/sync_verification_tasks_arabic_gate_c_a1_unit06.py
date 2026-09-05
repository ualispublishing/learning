#!/usr/bin/env python3
"""Add exact Arabic Gate C A1 Unit 6 evidence to the live verification queue."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/VERIFICATION_TASKS.md'
E5="A1 Unit 5 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u05.json` — 6 exact-current records / 60 question-answer pairs reviewed; 10 competing-answer ambiguities across the transfer clozes of `ar-a1-u05-p01` through `p05` were repaired by constraining the intended tense, motion, existence, role, location, speech, work, and future/return meanings; `p06` is a clean PASS. Fresh Gate C progress is 30/360 records and 300/3,600 Q/A pairs; this is an internal comprehension/answer-grounding audit, not an educator/publication release claim."
E6="A1 Unit 6 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u06.json` — 6 exact-current records / 60 question-answer pairs reviewed; 9 competing-answer ambiguities across route, direction, transport, arrival, spatial, imperative, waiting, map-location, and center transfer items were repaired across `ar-a1-u06-p01` through `p05`; `p06` is a clean PASS. Fresh Gate C progress is 36/360 records and 360/3,600 Q/A pairs; this is an internal comprehension/answer-grounding audit, not an educator/publication release claim."
C5="- [x] Arabic A1 Unit 5 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 10 competing-answer ambiguities across the transfer clozes of `ar-a1-u05-p01` through `p05`, recorded `p06` as a clean PASS, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 30/360 records and remains internal-only;"
C6="- [x] Arabic A1 Unit 6 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 9 competing-answer ambiguities across `ar-a1-u06-p01` through `p05`, recorded `p06` as a clean PASS, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 36/360 records and remains internal-only;"

def main():
    text=PATH.read_text(encoding='utf-8')
    if 'Current release position: fresh deterministic revalidation is **FAIL** with **1080** open evidence findings' not in text:
        raise SystemExit('verification queue blocker frontier drift')
    he,hc=E6 in text,C6 in text
    if he!=hc: raise SystemExit('partial Gate C Unit 6 queue state')
    if he:
        print('Arabic Gate C A1 Unit 6 verification evidence already synchronized')
        return
    if E5 not in text or C5 not in text: raise SystemExit('Gate C Unit 5 insertion anchors missing')
    text=text.replace(E5,E5+'\n\n'+E6,1)
    text=text.replace(C5,C5+'\n'+C6,1)
    PATH.write_text(text,encoding='utf-8')
    print('Arabic Gate C A1 Unit 6 verification evidence synchronized; release claim unchanged')

if __name__=='__main__':main()

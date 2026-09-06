#!/usr/bin/env python3
"""Add exact Arabic Gate C A1 Unit 10 evidence to the live verification queue."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/VERIFICATION_TASKS.md'
E9="A1 Unit 9 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u09.json` — 6 exact-current records / 60 question-answer pairs reviewed; 10 competing-answer ambiguities across ball, player, match, club, friends, happy, opportunity, participation, goal, and win transfer items were repaired across `ar-a1-u09-p01` through `p05`; `p06` is a clean PASS. Fresh Gate C progress is 54/360 records and 540/3,600 Q/A pairs; this is an internal comprehension/answer-grounding audit, not an educator/publication release claim."
E10="A1 Unit 10 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u10.json` — 6 exact-current records / 60 question-answer pairs reviewed; 10 competing-answer ambiguities across always, little, way, different, group, end, moment, picture, page, and question transfer items were repaired across `ar-a1-u10-p01` through `p05`; `p06` is a clean PASS. Fresh Gate C progress is 60/360 records and 600/3,600 Q/A pairs; A1 is now internally complete for Gate C, but this is not an educator/publication release claim."
C9="- [x] Arabic A1 Unit 9 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 10 competing-answer ambiguities across `ar-a1-u09-p01` through `p05`, recorded `p06` as a clean PASS, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 54/360 records and remains internal-only;"
C10="- [x] Arabic A1 Unit 10 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 10 competing-answer ambiguities across `ar-a1-u10-p01` through `p05`, recorded `p06` as a clean PASS, rebound affected Gate B evidence to exact-current learner-facing hashes, and completed the A1 Gate C level; Gate C is 60/360 records and remains internal-only;"

def main():
    text=PATH.read_text(encoding='utf-8')
    if 'Current release position: fresh deterministic revalidation is **FAIL** with **1080** open evidence findings' not in text:
        raise SystemExit('verification queue blocker frontier drift')
    he,hc=E10 in text,C10 in text
    if he!=hc: raise SystemExit('partial Gate C Unit 10 queue state')
    if he:
        print('Arabic Gate C A1 Unit 10 verification evidence already synchronized')
        return
    if E9 not in text or C9 not in text: raise SystemExit('Gate C Unit 9 insertion anchors missing')
    text=text.replace(E9,E9+'\n\n'+E10,1)
    text=text.replace(C9,C9+'\n'+C10,1)
    PATH.write_text(text,encoding='utf-8')
    print('Arabic Gate C A1 Unit 10 verification evidence synchronized; A1 internally complete; release claim unchanged')

if __name__=='__main__':main()

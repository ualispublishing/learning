#!/usr/bin/env python3
"""Add exact Arabic Gate C A1 Unit 9 evidence to the live verification queue."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/VERIFICATION_TASKS.md'
E8="A1 Unit 8 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u08.json` — 6 exact-current records / 60 question-answer pairs reviewed; 10 competing-answer ambiguities across feeling, problem, need, help, hand, head, heart, safe, try, and strength transfer items were repaired across `ar-a1-u08-p01` through `p05`; `p06` is a clean PASS. Fresh Gate C progress is 48/360 records and 480/3,600 Q/A pairs; this is an internal comprehension/answer-grounding audit, not an educator/publication release claim."
E9="A1 Unit 9 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u09.json` — 6 exact-current records / 60 question-answer pairs reviewed; 10 competing-answer ambiguities across ball, player, match, club, friends, happy, opportunity, participation, goal, and win transfer items were repaired across `ar-a1-u09-p01` through `p05`; `p06` is a clean PASS. Fresh Gate C progress is 54/360 records and 540/3,600 Q/A pairs; this is an internal comprehension/answer-grounding audit, not an educator/publication release claim."
C8="- [x] Arabic A1 Unit 8 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 10 competing-answer ambiguities across `ar-a1-u08-p01` through `p05`, recorded `p06` as a clean PASS, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 48/360 records and remains internal-only;"
C9="- [x] Arabic A1 Unit 9 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 10 competing-answer ambiguities across `ar-a1-u09-p01` through `p05`, recorded `p06` as a clean PASS, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 54/360 records and remains internal-only;"

def main():
    text=PATH.read_text(encoding='utf-8')
    if 'Current release position: fresh deterministic revalidation is **FAIL** with **1080** open evidence findings' not in text:
        raise SystemExit('verification queue blocker frontier drift')
    he,hc=E9 in text,C9 in text
    if he!=hc: raise SystemExit('partial Gate C Unit 9 queue state')
    if he:
        print('Arabic Gate C A1 Unit 9 verification evidence already synchronized')
        return
    if E8 not in text or C8 not in text: raise SystemExit('Gate C Unit 8 insertion anchors missing')
    text=text.replace(E8,E8+'\n\n'+E9,1)
    text=text.replace(C8,C8+'\n'+C9,1)
    PATH.write_text(text,encoding='utf-8')
    print('Arabic Gate C A1 Unit 9 verification evidence synchronized; release claim unchanged')

if __name__=='__main__':main()

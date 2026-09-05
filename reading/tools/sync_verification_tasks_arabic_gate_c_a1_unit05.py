#!/usr/bin/env python3
"""Add exact Arabic Gate C A1 Unit 5 evidence to the live verification queue."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/VERIFICATION_TASKS.md'
E4="A1 Unit 4 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u04.json` — 6 exact-current records / 60 question-answer pairs reviewed; 2 competing-answer ambiguities in `ar-a1-u04-p01/q10` and `ar-a1-u04-p05/q9` repaired by constraining the kinship and spatial prompts, with 4 records recorded as clean PASS. Fresh Gate C progress is 24/360 records and 240/3,600 Q/A pairs; this is an internal comprehension/answer-grounding audit, not an educator/publication release claim."
E5="A1 Unit 5 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u05.json` — 6 exact-current records / 60 question-answer pairs reviewed; 10 competing-answer ambiguities across the transfer clozes of `ar-a1-u05-p01` through `p05` were repaired by constraining the intended tense, motion, existence, role, location, speech, work, and future/return meanings; `p06` is a clean PASS. Fresh Gate C progress is 30/360 records and 300/3,600 Q/A pairs; this is an internal comprehension/answer-grounding audit, not an educator/publication release claim."
C4="- [x] Arabic A1 Unit 4 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 2 competing-answer ambiguities in `ar-a1-u04-p01/q10` and `ar-a1-u04-p05/q9`, recorded 4 clean PASS records, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 24/360 records and remains internal-only;"
C5="- [x] Arabic A1 Unit 5 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 10 competing-answer ambiguities across the transfer clozes of `ar-a1-u05-p01` through `p05`, recorded `p06` as a clean PASS, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 30/360 records and remains internal-only;"

def main():
    text=PATH.read_text(encoding='utf-8')
    if 'Current release position: fresh deterministic revalidation is **FAIL** with **1080** open evidence findings' not in text:
        raise SystemExit('verification queue blocker frontier drift')
    he,hc=E5 in text,C5 in text
    if he!=hc: raise SystemExit('partial Gate C Unit 5 queue state')
    if he:
        print('Arabic Gate C A1 Unit 5 verification evidence already synchronized')
        return
    if E4 not in text or C4 not in text: raise SystemExit('Gate C Unit 4 insertion anchors missing')
    text=text.replace(E4,E4+'\n\n'+E5,1)
    text=text.replace(C4,C4+'\n'+C5,1)
    PATH.write_text(text,encoding='utf-8')
    print('Arabic Gate C A1 Unit 5 verification evidence synchronized; release claim unchanged')

if __name__=='__main__':main()

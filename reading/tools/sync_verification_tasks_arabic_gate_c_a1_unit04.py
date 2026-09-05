#!/usr/bin/env python3
"""Add exact Arabic Gate C A1 Unit 4 evidence to the live verification queue."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/VERIFICATION_TASKS.md'
E3="A1 Unit 3 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u03.json` — 6 exact-current records / 60 question-answer pairs reviewed; 1 competing-answer ambiguity in `ar-a1-u03-p05/q10` repaired by constraining the prompt to the additional-item sense, with 5 records recorded as clean PASS. Fresh Gate C progress is 18/360 records and 180/3,600 Q/A pairs; this is an internal comprehension/answer-grounding audit, not an educator/publication release claim."
E4="A1 Unit 4 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u04.json` — 6 exact-current records / 60 question-answer pairs reviewed; 2 competing-answer ambiguities in `ar-a1-u04-p01/q10` and `ar-a1-u04-p05/q9` repaired by constraining the kinship and spatial prompts, with 4 records recorded as clean PASS. Fresh Gate C progress is 24/360 records and 240/3,600 Q/A pairs; this is an internal comprehension/answer-grounding audit, not an educator/publication release claim."
C3="- [x] Arabic A1 Unit 3 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 1 competing-answer ambiguity in `ar-a1-u03-p05/q10`, recorded 5 clean PASS records, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 18/360 records and remains internal-only;"
C4="- [x] Arabic A1 Unit 4 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 2 competing-answer ambiguities in `ar-a1-u04-p01/q10` and `ar-a1-u04-p05/q9`, recorded 4 clean PASS records, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 24/360 records and remains internal-only;"

def main():
    text=PATH.read_text(encoding='utf-8')
    if 'Current release position: fresh deterministic revalidation is **FAIL** with **1080** open evidence findings' not in text:
        raise SystemExit('verification queue blocker frontier drift')
    he,hc=E4 in text,C4 in text
    if he!=hc: raise SystemExit('partial Gate C Unit 4 queue state')
    if he:
        print('Arabic Gate C A1 Unit 4 verification evidence already synchronized')
        return
    if E3 not in text or C3 not in text:
        raise SystemExit('Gate C Unit 3 insertion anchors missing')
    text=text.replace(E3,E3+'\n\n'+E4,1)
    text=text.replace(C3,C3+'\n'+C4,1)
    PATH.write_text(text,encoding='utf-8')
    print('Arabic Gate C A1 Unit 4 verification evidence synchronized; release claim unchanged')

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Add exact Arabic Gate C A2 Unit 1 evidence to the live verification queue."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'reading/VERIFICATION_TASKS.md'
E10="A1 Unit 10 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u10.json` — 6 exact-current records / 60 question-answer pairs reviewed; 10 competing-answer ambiguities across always, little, way, different, group, end, moment, picture, page, and question transfer items were repaired across `ar-a1-u10-p01` through `p05`; `p06` is a clean PASS. Fresh Gate C progress is 60/360 records and 600/3,600 Q/A pairs; A1 is now internally complete for Gate C, but this is not an educator/publication release claim."
EA2="A2 Unit 1 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a2_u01.json` — 6 exact-current records / 60 question-answer pairs reviewed; 10 competing-answer ambiguities across street, service, phone, bank, announcement, message, visit, department, list, and price transfer items were repaired across `ar-a2-u01-p01` through `p05`; `p06` is a clean PASS. Fresh Gate C progress is 66/360 records and 660/3,600 Q/A pairs; A1 remains the only completed Gate C level and this is not an educator/publication release claim."
C10="- [x] Arabic A1 Unit 10 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 10 competing-answer ambiguities across `ar-a1-u10-p01` through `p05`, recorded `p06` as a clean PASS, rebound affected Gate B evidence to exact-current learner-facing hashes, and completed the A1 Gate C level; Gate C is 60/360 records and remains internal-only;"
CA2="- [x] Arabic A2 Unit 1 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 10 competing-answer ambiguities across `ar-a2-u01-p01` through `p05`, recorded `p06` as a clean PASS, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 66/360 records and remains internal-only;"

def main():
    text=PATH.read_text(encoding='utf-8')
    if 'Current release position: fresh deterministic revalidation is **FAIL** with **1080** open evidence findings' not in text:
        raise SystemExit('verification queue blocker frontier drift')
    he,hc=EA2 in text,CA2 in text
    if he!=hc: raise SystemExit('partial Gate C A2 Unit 1 queue state')
    if he:
        print('Arabic Gate C A2 Unit 1 verification evidence already synchronized')
        return
    if E10 not in text or C10 not in text: raise SystemExit('Gate C A1 Unit 10 insertion anchors missing')
    text=text.replace(E10,E10+'\n\n'+EA2,1)
    text=text.replace(C10,C10+'\n'+CA2,1)
    PATH.write_text(text,encoding='utf-8')
    print('Arabic Gate C A2 Unit 1 verification evidence synchronized; release claim unchanged')

if __name__=='__main__':main()

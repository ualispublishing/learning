#!/usr/bin/env python3
"""Add exact Arabic Gate C A1 Unit 2 evidence to the live verification queue."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading/VERIFICATION_TASKS.md"
E1 = "A1 Unit 1 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u01.json` — 6 exact-current records / 60 question-answer pairs reviewed; 1 contextual-sense answer-key defect in `ar-a1-u01-p04/q3` repaired and 5 records recorded as clean PASS. Fresh Gate C progress is 6/360 records and 60/3,600 Q/A pairs; this is an internal comprehension/answer-grounding audit, not an educator/publication release claim."
E2 = "A1 Unit 2 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u02.json` — 6 exact-current records / 60 question-answer pairs reviewed; 1 competing-answer ambiguity in `ar-a1-u02-p01/q9` repaired by constraining the prompt, with 5 records recorded as clean PASS. Fresh Gate C progress is 12/360 records and 120/3,600 Q/A pairs; this is an internal comprehension/answer-grounding audit, not an educator/publication release claim."
C1 = "- [x] Arabic A1 Unit 1 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 1 contextual-sense answer-key defect in `ar-a1-u01-p04/q3`, recorded 5 clean PASS records, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 6/360 records and remains internal-only;"
C2 = "- [x] Arabic A1 Unit 2 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 1 competing-answer ambiguity in `ar-a1-u02-p01/q9`, recorded 5 clean PASS records, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 12/360 records and remains internal-only;"


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    if "Current release position: fresh deterministic revalidation is **FAIL** with **1080** open evidence findings" not in text:
        raise SystemExit("verification queue blocker frontier drift")
    he, hc = E2 in text, C2 in text
    if he != hc:
        raise SystemExit("partial Gate C Unit 2 queue state")
    if he:
        print("Arabic Gate C A1 Unit 2 verification evidence already synchronized")
        return
    if E1 not in text or C1 not in text:
        raise SystemExit("Gate C Unit 1 insertion anchors missing")
    text = text.replace(E1, E1 + "\n\n" + E2, 1)
    text = text.replace(C1, C1 + "\n" + C2, 1)
    PATH.write_text(text, encoding="utf-8")
    print("Arabic Gate C A1 Unit 2 verification evidence synchronized; release claim unchanged")


if __name__ == "__main__":
    main()

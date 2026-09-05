#!/usr/bin/env python3
"""Add exact Arabic Gate C A1 Unit 1 evidence to the live verification queue."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading/VERIFICATION_TASKS.md"

EVIDENCE_MARKER = "C2 Unit 10 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/c2_u10.json` — 6 current-corpus records reviewed and repaired, with 19 fresh high-confidence summary/detail assessment-alignment/naturalness/grammar findings closed. Fresh Gate B progress is now 360/360 records; C2 Gate B and the corpus-wide fresh Gate B internal review are complete; this is not an educator/publication release claim."
EVIDENCE = "A1 Unit 1 Gate C evidence: `reading/audit/arabic_gate_c_decisions_2026-09-05/a1_u01.json` — 6 exact-current records / 60 question-answer pairs reviewed; 1 contextual-sense answer-key defect in `ar-a1-u01-p04/q3` repaired and 5 records recorded as clean PASS. Fresh Gate C progress is 6/360 records and 60/3,600 Q/A pairs; this is an internal comprehension/answer-grounding audit, not an educator/publication release claim."
CHECK_MARKER = "- [x] Arabic C2 Unit 10 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; closed 19 fresh summary/detail assessment-alignment/naturalness/grammar findings across all 6 records with hash-bound decision evidence; C2 and corpus-wide fresh Gate B internal review are complete;"
CHECK = "- [x] Arabic A1 Unit 1 Gate C batch: reviewed 6 passages / 60 question-answer pairs; repaired 1 contextual-sense answer-key defect in `ar-a1-u01-p04/q3`, recorded 5 clean PASS records, and rebound affected Gate B evidence to exact-current learner-facing hashes; Gate C is 6/360 records and remains internal-only;"


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    if "Current release position: fresh deterministic revalidation is **FAIL** with **1080** open evidence findings" not in text:
        raise SystemExit("verification queue blocker frontier drift")
    if EVIDENCE in text or CHECK in text:
        raise SystemExit("Gate C A1 Unit 1 verification evidence already present")
    if EVIDENCE_MARKER not in text or CHECK_MARKER not in text:
        raise SystemExit("verification queue insertion anchors missing")
    text = text.replace(EVIDENCE_MARKER, EVIDENCE_MARKER + "\n\n" + EVIDENCE, 1)
    text = text.replace(CHECK_MARKER, CHECK_MARKER + "\n" + CHECK, 1)
    if "Updated: 2026-09-04" in text:
        text = text.replace("Updated: 2026-09-04", "Updated: 2026-09-05", 1)
    PATH.write_text(text, encoding="utf-8")
    print("Arabic Gate C A1 Unit 1 verification evidence synchronized; release claim unchanged")


if __name__ == "__main__":
    main()

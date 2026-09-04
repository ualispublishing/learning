#!/usr/bin/env python3
"""Synchronize VERIFICATION_TASKS.md after Arabic Gate B B2 Unit 4."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading/VERIFICATION_TASKS.md"


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one match, found {count}: {old[:100]!r}")
    return text.replace(old, new, 1)


def main() -> int:
    text = PATH.read_text(encoding="utf-8")

    text = replace_once(
        text,
        "Current release position: fresh deterministic revalidation is **FAIL** with **1728** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.",
        "Current release position: fresh deterministic revalidation is **FAIL** with **1704** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.",
    )
    text = replace_once(
        text,
        "Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1728**. This is a release-evidence gate, not semantic approval.",
        "Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1704**. This is a release-evidence gate, not semantic approval.",
    )

    unit3 = (
        "B2 Unit 3 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u03.json` — "
        "6 current-corpus records reviewed, 5 repaired and 1 clean PASS, with 15 fresh high-confidence "
        "grammar/naturalness/semantic findings closed. Fresh Gate B progress is now 198/360 records; "
        "B2 remains in progress and this is not an educator/publication release claim."
    )
    unit4 = (
        unit3
        + "\n\nB2 Unit 4 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u04.json` — "
        "6 current-corpus records reviewed, 4 repaired and 2 clean PASS records, with 6 fresh high-confidence "
        "naturalness/assessment/reference/semantic findings closed. Fresh Gate B progress is now 204/360 records; "
        "B2 remains in progress and this is not an educator/publication release claim."
    )
    text = replace_once(text, unit3, unit4)

    unit3_check = (
        "- [x] Arabic B2 Unit 3 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; "
        "closed 15 fresh learner-facing findings across 5 records and recorded 1 clean PASS with hash-bound decision evidence;"
    )
    unit4_check = (
        unit3_check
        + "\n- [x] Arabic B2 Unit 4 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; "
        "closed 6 fresh learner-facing findings across 4 records and recorded 2 clean PASS records with hash-bound decision evidence;"
    )
    text = replace_once(text, unit3_check, unit4_check)

    if "**1728**" in text or "open findings **1728**" in text:
        raise SystemExit("stale Unit 3 deterministic blocker remains")
    if text.count("b2_u04.json") != 1 or text.count("204/360") != 1:
        raise SystemExit("Unit 4 verification summary did not bind exactly once")

    PATH.write_text(text, encoding="utf-8")
    print("synchronized reading/VERIFICATION_TASKS.md to Arabic B2 Unit 4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

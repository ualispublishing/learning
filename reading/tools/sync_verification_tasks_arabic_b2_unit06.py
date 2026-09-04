#!/usr/bin/env python3
"""Synchronize VERIFICATION_TASKS.md after Arabic Gate B B2 Unit 6."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
PATH = READING / "VERIFICATION_TASKS.md"
RELEASE = READING / "RELEASE_STATUS.json"
DECISION = READING / "audit/arabic_gate_b_decisions_2026-08-30/b2_u06.json"

EXPECTED_REVIEWED = 216
EXPECTED_WITH_FINDINGS = 184
EXPECTED_FINDINGS = 379
EXPECTED_BLOCKERS = 1656


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one verification anchor, found {count}: {old[:100]!r}")
    return text.replace(old, new, 1)


def main() -> int:
    release = json.loads(RELEASE.read_text(encoding="utf-8"))
    arabic = release["languages"]["arabic"]
    gate = arabic["naturalness_review_progress"]
    det = arabic["latest_deterministic_gate"]
    if (gate["fresh_records_reviewed"], gate["fresh_records_with_findings"], gate["fresh_findings"]) != (
        EXPECTED_REVIEWED, EXPECTED_WITH_FINDINGS, EXPECTED_FINDINGS
    ):
        raise SystemExit("Unit 6 Gate B progress counters do not match expected exact frontier")
    if det["open_findings"] != EXPECTED_BLOCKERS:
        raise SystemExit(f"unexpected deterministic blocker count: {det['open_findings']}")

    doc = json.loads(DECISION.read_text(encoding="utf-8"))
    if (doc["records_reviewed"], doc["records_with_findings"], doc["fresh_findings"]) != (6, 5, 16):
        raise SystemExit("Unit 6 decision artifact summary drift")
    if doc.get("quality_promotion") is not False or doc.get("release_claim") is not False:
        raise SystemExit("Unit 6 decision artifact must not claim release")

    text = PATH.read_text(encoding="utf-8")
    marker = "reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u06.json"
    if marker in text:
        if text.count(marker) != 1 or text.count("216/360") != 1:
            raise SystemExit("Unit 6 verification queue appears partially or multiply synchronized")
        if f"**{EXPECTED_BLOCKERS}**" not in text or f"open findings **{EXPECTED_BLOCKERS}**" not in text:
            raise SystemExit("Unit 6 queue marker exists but deterministic blocker summary is stale")
        print("reading/VERIFICATION_TASKS.md already synchronized to Arabic B2 Unit 6")
        return 0

    text = replace_once(
        text,
        "Current release position: fresh deterministic revalidation is **FAIL** with **1680** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.",
        "Current release position: fresh deterministic revalidation is **FAIL** with **1656** open evidence findings; educator/publication release remains **not ready** under the current assurance profile.",
    )
    text = replace_once(
        text,
        "Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1680**. This is a release-evidence gate, not semantic approval.",
        "Fresh deterministic evidence: `reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json` — 360 records, 3,600 questions, 3,600 answers; status **FAIL**; open findings **1656**. This is a release-evidence gate, not semantic approval.",
    )
    unit5 = (
        "B2 Unit 5 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u05.json` — "
        "6 current-corpus records reviewed, 4 repaired and 2 clean PASS records, with 12 fresh high-confidence "
        "grammar/naturalness/reference/semantic/assessment findings closed. Fresh Gate B progress is now 210/360 records; "
        "B2 remains in progress and this is not an educator/publication release claim."
    )
    unit6 = (
        unit5
        + "\n\nB2 Unit 6 Gate B evidence: `reading/audit/arabic_gate_b_decisions_2026-08-30/b2_u06.json` — "
        "6 current-corpus records reviewed, 5 repaired and 1 clean PASS record, with 16 fresh high-confidence "
        "grammar/naturalness/reference/semantic/assessment findings closed. Fresh Gate B progress is now 216/360 records; "
        "B2 remains in progress and this is not an educator/publication release claim."
    )
    text = replace_once(text, unit5, unit6)
    unit5_check = (
        "- [x] Arabic B2 Unit 5 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; "
        "closed 12 fresh learner-facing findings across 4 records and recorded 2 clean PASS records with hash-bound decision evidence;"
    )
    unit6_check = (
        unit5_check
        + "\n- [x] Arabic B2 Unit 6 Gate B batch: reviewed 6 passages / 60 questions / 60 answers; "
        "closed 16 fresh learner-facing findings across 5 records and recorded 1 clean PASS with hash-bound decision evidence;"
    )
    text = replace_once(text, unit5_check, unit6_check)
    if text.count(marker) != 1 or text.count("216/360") != 1:
        raise SystemExit("Unit 6 verification summary did not bind exactly once")
    PATH.write_text(text, encoding="utf-8")
    print("synchronized reading/VERIFICATION_TASKS.md to Arabic B2 Unit 6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

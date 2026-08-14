#!/usr/bin/env python3
"""Persist the already-audited Arabic A1 Unit 01 approval state.

This script is deliberately narrow: it does not edit passage prose, targets,
questions, answers, or review scheduling. It only synchronizes the supported-
coverage result and final quality state after the independent Unit-01 gates
have passed.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASSAGES = ROOT / "reading" / "arabic" / "a1" / "passages.jsonl"
SUPPORTED = ROOT / "reading" / "audit" / "arabic_a1_supported_coverage.json"
EXPECTED_IDS = [f"ar-a1-u01-p{i:02d}" for i in range(1, 7)]
FINAL_NOTE = (
    "Supported-control coverage PASS: 1.0 under the documented curriculum-control "
    "classification; this is a planning/control result, not a learner-mastery claim."
)


def main() -> None:
    audit = json.loads(SUPPORTED.read_text(encoding="utf-8"))
    if audit.get("status") != "PASS":
        raise SystemExit("supported-control audit is not PASS")

    records = [
        json.loads(line)
        for line in PASSAGES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    ids = [record.get("id") for record in records]
    if ids != EXPECTED_IDS:
        raise SystemExit(f"unexpected Arabic Unit-01 passage IDs/order: {ids!r}")

    for record in records:
        quality = record.get("quality") or {}
        required_passes = {
            "linguistic_review": "pass",
            "pedagogical_review": "pass",
            "answer_key_check": "pass",
            "schema_check": "pass",
        }
        for field, expected in required_passes.items():
            if quality.get(field) != expected:
                raise SystemExit(f"{record['id']}: {field} must be {expected!r}")

        record["estimated_known_token_coverage"] = 1.0
        quality["coverage_check"] = "pass"
        quality["status"] = "approved"

        notes = [
            note
            for note in quality.get("notes", [])
            if "measured coverage pending" not in note.lower()
            and "supported lexical-control measurement pending" not in note.lower()
        ]
        if FINAL_NOTE not in notes:
            notes.append(FINAL_NOTE)
        quality["notes"] = notes
        record["quality"] = quality

        speed = record.get("speed_training") or {}
        speed["benchmark_eligible"] = record["id"] == "ar-a1-u01-p06"
        record["speed_training"] = speed

    PASSAGES.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )
    print("finalized Arabic A1 Unit 01: 6 approved passages; P6 benchmark eligible")


if __name__ == "__main__":
    main()

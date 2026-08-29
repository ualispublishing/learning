#!/usr/bin/env python3
"""Validate one submitted LANG-WB native-review sign-off record.

This validates the record itself against the current production candidate. It
does not decide whether all three languages are ready for final promotion; that
is the job of workbook_final_human_promotion_gate.py.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import workbook_final_human_promotion_gate as gate

ALLOWED_OUTCOMES = {"PASS", "FAIL", "HOLD"}


def problem_list(record: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    lang = record.get("language")
    if lang not in gate.LANGUAGES:
        return ["language"]

    manifest = gate.load_json(gate.MANIFEST_PATH)
    manifest_langs = manifest.get("sentence_curation", {}).get("languages", {})
    expected_decision = (manifest_langs.get(lang) or {}).get("decision_sha256")
    if not expected_decision:
        return ["missing_manifest_decision_sha256"]

    master_rel = f"completed/languages/workbooks/v1.0/{lang}/{gate.MASTER_NAMES[lang]}"
    master_path = gate.ROOT / master_rel
    if not master_path.exists():
        return [f"missing_master:{master_rel}"]

    manifest_blob = gate.git_blob_sha(gate.MANIFEST_PATH)
    master_blob = gate.git_blob_sha(master_path)
    problems.extend(
        gate.binding_problems(
            record,
            lang=lang,
            expected_master_path=master_rel,
            expected_master_blob=master_blob,
            expected_decision_sha=expected_decision,
            expected_manifest_blob=manifest_blob,
        )
    )

    try:
        reviewed_at = gate.parse_review_time(record.get("review_completed_utc"))
        candidate_generated = gate.parse_review_time(manifest.get("generated_utc"))
        now_utc = datetime.now(timezone.utc)
        if reviewed_at < candidate_generated:
            problems.append("review_before_candidate_generated")
        if reviewed_at > now_utc + gate.MAX_FUTURE_CLOCK_SKEW:
            problems.append("review_timestamp_in_future")
    except ValueError as exc:
        problems.append(f"review_completed_utc:{exc}")

    if not gate.reviewer_complete(record):
        problems.append("reviewer_qualification")

    outcome = record.get("review_outcome")
    if outcome not in ALLOWED_OUTCOMES:
        problems.append("review_outcome")

    scope = record.get("scope_attestation")
    if not isinstance(scope, dict):
        problems.append("scope_attestation")
    else:
        for field in gate.REQUIRED_SCOPE_FIELDS:
            if field not in scope or not isinstance(scope.get(field), bool):
                problems.append(f"scope:{field}:missing_or_not_boolean")

    if not str(record.get("attestation", "")).strip():
        problems.append("attestation")

    defects = record.get("defects")
    holds = record.get("holds")
    if not isinstance(defects, list):
        problems.append("defects_not_list")
        defects = []
    if not isinstance(holds, list):
        problems.append("holds_not_list")
        holds = []

    if outcome == "PASS":
        for field in gate.REQUIRED_SCOPE_FIELDS:
            if not isinstance(scope, dict) or scope.get(field) is not True:
                problems.append(f"scope:{field}:PASS_requires_true")
        if defects:
            problems.append("PASS_defects_not_empty")
        if holds:
            problems.append("PASS_holds_not_empty")
        if not str(record.get("pass_condition_acknowledged", "")).strip():
            problems.append("pass_condition_acknowledged")
    elif outcome == "FAIL":
        if not defects:
            problems.append("FAIL_requires_defects")
    elif outcome == "HOLD":
        if not holds:
            problems.append("HOLD_requires_holds")

    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("signoff", help="Path to one native-signoff JSON record")
    args = parser.parse_args()
    path = Path(args.signoff).resolve()

    report: dict[str, Any] = {
        "schema": "lang-wb-native-signoff-validation-v1",
        "path": str(path),
        "gate": "FAIL",
        "language": None,
        "review_outcome": None,
        "problems": [],
        "note": "PASS here validates this submitted record only; final release still requires the separate three-language promotion gate.",
    }
    try:
        record = gate.load_json(path)
        report["language"] = record.get("language")
        report["review_outcome"] = record.get("review_outcome")
        report["problems"] = problem_list(record)
    except Exception as exc:
        report["problems"] = [f"parse_error:{type(exc).__name__}:{exc}"]

    if not report["problems"]:
        report["gate"] = "PASS"
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

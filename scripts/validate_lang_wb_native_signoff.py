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


def problem_list(record: dict[str, Any]) -> list[str]:
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

    try:
        candidate_generated = gate.parse_review_time(manifest.get("generated_utc"))
    except ValueError as exc:
        return [f"manifest_generated_utc:{exc}"]

    return gate.validate_signoff_record(
        record,
        lang=lang,
        expected_master_path=master_rel,
        expected_master_blob=gate.git_blob_sha(master_path),
        expected_decision_sha=expected_decision,
        expected_manifest_blob=gate.git_blob_sha(gate.MANIFEST_PATH),
        candidate_generated_at=candidate_generated,
        now_utc=datetime.now(timezone.utc),
    )


def filename_problems(path: Path, language: Any) -> list[str]:
    """Ensure promotion discovery will see this record under its declared language."""
    if language not in gate.LANGUAGES:
        return []
    problems: list[str] = []
    if path.suffix.lower() != ".json":
        problems.append("filename_extension")
    if not path.name.startswith(f"{language}_"):
        problems.append("filename_language_prefix")
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
        report["problems"].extend(filename_problems(path, record.get("language")))
    except Exception as exc:
        report["problems"] = [f"parse_error:{type(exc).__name__}:{exc}"]

    if not report["problems"]:
        report["gate"] = "PASS"
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

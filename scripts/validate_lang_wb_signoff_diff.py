#!/usr/bin/env python3
"""Validate LANG-WB native-signoff changes between two Git refs.

Only newly added sign-off JSON records are permitted. Existing sign-off records
are immutable: modification, rename, or deletion fails closed. Every added JSON
must also pass the current-candidate single-record validator.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any

import validate_lang_wb_native_signoff as signoff

ROOT = Path(__file__).resolve().parents[1]
SIGNOFF_GLOB = "audit/language-workbooks/v1.0/native-signoffs/*.json"


def git_diff_name_status(base: str, head: str) -> list[list[str]]:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "diff",
            "--name-status",
            "--find-renames",
            base,
            head,
            "--",
            SIGNOFF_GLOB,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    rows: list[list[str]] = []
    for raw in result.stdout.splitlines():
        if not raw.strip():
            continue
        rows.append(raw.split("\t"))
    return rows


def validate_added(path_text: str) -> dict[str, Any]:
    path = (ROOT / path_text).resolve()
    record = signoff.gate.load_json(path)
    problems = signoff.problem_list(record)
    problems.extend(signoff.filename_problems(path, record.get("language")))
    return {
        "path": path_text,
        "language": record.get("language"),
        "review_outcome": record.get("review_outcome"),
        "problems": problems,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_ref")
    parser.add_argument("head_ref")
    args = parser.parse_args()

    report: dict[str, Any] = {
        "schema": "lang-wb-native-signoff-diff-validation-v1",
        "base_ref": args.base_ref,
        "head_ref": args.head_ref,
        "gate": "FAIL",
        "added_records": [],
        "immutable_change_violations": [],
        "problems": [],
        "note": "Only newly added immutable native-signoff JSON records are permitted; each addition must pass the single-record current-candidate validator.",
    }

    try:
        changes = git_diff_name_status(args.base_ref, args.head_ref)
        for parts in changes:
            status = parts[0]
            status_code = status[:1]
            paths = parts[1:]

            if status_code != "A" or len(paths) != 1:
                violation = {"status": status, "paths": paths}
                report["immutable_change_violations"].append(violation)
                report["problems"].append(
                    f"immutable_signoff_change:{status}:{'->'.join(paths)}"
                )
                continue

            path_text = paths[0]
            try:
                item = validate_added(path_text)
            except Exception as exc:
                item = {
                    "path": path_text,
                    "language": None,
                    "review_outcome": None,
                    "problems": [f"parse_or_validation_error:{type(exc).__name__}:{exc}"],
                }
            report["added_records"].append(item)
            for problem in item["problems"]:
                report["problems"].append(f"{path_text}:{problem}")
    except Exception as exc:
        report["problems"].append(f"diff_error:{type(exc).__name__}:{exc}")

    if not report["problems"]:
        report["gate"] = "PASS"

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

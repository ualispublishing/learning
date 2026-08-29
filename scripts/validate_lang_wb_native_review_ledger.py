#!/usr/bin/env python3
"""Validate a completed LANG-WB native-review worksheet against current sources.

Exit codes:
- 0: all 2,000 structured rows are explicitly PASS and source-bound.
- 2: worksheet is source-valid but incomplete or contains FAIL/HOLD outcomes.
- 1: malformed worksheet, source drift, or other validation error.

A zero exit code is only a structured-row preflight. It is not final linguistic
certification; the full rendered master workbook must still be reviewed and a
separate immutable native-signoff record must pass the final promotion gate.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import build_lang_wb_native_review_ledgers as ledgers

ALLOWED_OUTCOMES = {"PASS", "FAIL", "HOLD"}
IMMUTABLE_FIELDS = (
    "item_type",
    "rank",
    "level",
    "target",
    "english",
    "part_of_speech",
    "attribution",
)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def fail(message: str) -> None:
    raise ValueError(message)


def validate_source_binding(lang: str, rows: list[dict[str, str]]) -> dict[str, Any]:
    names = ledgers.LANGUAGES[lang]
    base = ledgers.RELEASE / lang
    vocabulary_path = base / names["vocabulary"]
    sentence_path = base / names["sentences"]
    master_path = base / names["master"]

    vocabulary = ledgers.read_rows(vocabulary_path)
    sentences = ledgers.read_rows(sentence_path)
    ledgers.validate_source_rows(lang, vocabulary, sentences)
    expected = ledgers.ledger_rows(vocabulary, sentences)

    if len(rows) != len(expected):
        fail(f"row_count={len(rows)}, expected={len(expected)}")

    for index, (actual, source) in enumerate(zip(rows, expected), start=1):
        for field in IMMUTABLE_FIELDS:
            if actual.get(field, "") != source.get(field, ""):
                fail(f"source_drift row={index} field={field!r}")

    manifest = json.loads(ledgers.MANIFEST.read_text(encoding="utf-8"))
    decision_sha = (
        manifest.get("sentence_curation", {})
        .get("languages", {})
        .get(lang, {})
        .get("decision_sha256")
    )
    if not decision_sha:
        fail("release manifest missing sentence decision SHA-256")

    return {
        "master_workbook_path": str(master_path.relative_to(ledgers.ROOT)),
        "master_workbook_git_blob_sha": ledgers.git_blob_sha(master_path),
        "vocabulary_csv_path": str(vocabulary_path.relative_to(ledgers.ROOT)),
        "vocabulary_csv_git_blob_sha": ledgers.git_blob_sha(vocabulary_path),
        "sentence_csv_path": str(sentence_path.relative_to(ledgers.ROOT)),
        "sentence_csv_git_blob_sha": ledgers.git_blob_sha(sentence_path),
        "sentence_decision_sha256": decision_sha,
        "release_manifest_path": str(ledgers.MANIFEST.relative_to(ledgers.ROOT)),
        "release_manifest_git_blob_sha": ledgers.git_blob_sha(ledgers.MANIFEST),
    }


def validate_reviews(rows: list[dict[str, str]]) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    problems: list[str] = []

    for index, row in enumerate(rows, start=1):
        outcome = row.get("review_outcome", "").strip().upper()
        if not outcome:
            counts["UNREVIEWED"] += 1
            continue
        if outcome not in ALLOWED_OUTCOMES:
            counts["INVALID"] += 1
            problems.append(f"row {index}: invalid review_outcome={outcome!r}")
            continue

        counts[outcome] += 1
        defect_type = row.get("defect_type", "").strip()
        notes = row.get("reviewer_notes", "").strip()
        correction = row.get("proposed_correction", "").strip()

        if outcome == "PASS":
            if defect_type:
                problems.append(f"row {index}: PASS must not carry defect_type")
            if correction:
                problems.append(f"row {index}: PASS must not carry proposed_correction")
        elif outcome == "FAIL":
            if not defect_type:
                problems.append(f"row {index}: FAIL requires defect_type")
            if not notes:
                problems.append(f"row {index}: FAIL requires reviewer_notes")
        elif outcome == "HOLD":
            if not notes:
                problems.append(f"row {index}: HOLD requires reviewer_notes")

    if problems:
        fail("; ".join(problems[:25]))

    incomplete = counts["UNREVIEWED"] > 0
    failed = counts["FAIL"] > 0
    held = counts["HOLD"] > 0
    if incomplete:
        gate = "INCOMPLETE"
    elif failed:
        gate = "FAIL"
    elif held:
        gate = "HOLD"
    else:
        gate = "PASS"

    return {
        "gate": gate,
        "counts": {
            "PASS": counts["PASS"],
            "FAIL": counts["FAIL"],
            "HOLD": counts["HOLD"],
            "UNREVIEWED": counts["UNREVIEWED"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("language", choices=tuple(ledgers.LANGUAGES))
    parser.add_argument(
        "ledger",
        nargs="?",
        help="Path to completed ledger; defaults to audit/.../native-review-ledgers/<language>_native_review_ledger.csv",
    )
    args = parser.parse_args()

    lang = args.language
    ledger_path = (
        Path(args.ledger).resolve()
        if args.ledger
        else ledgers.OUT / f"{lang}_native_review_ledger.csv"
    )
    report_path = ledger_path.with_name(ledger_path.stem + "_validation.json")

    report: dict[str, Any] = {
        "schema": "lang-wb-native-review-ledger-validation-v1",
        "release": "v1.0",
        "language": lang,
        "ledger_path": str(ledger_path),
        "structural_gate": "FAIL",
        "review_gate": "UNKNOWN",
        "source_binding": None,
        "review_counts": None,
        "error": None,
        "note": "Structured-row PASS is not final certification; complete rendered-master review and final immutable sign-off remain mandatory.",
    }

    try:
        fieldnames, rows = read_csv(ledger_path)
        if fieldnames != ledgers.LEDGER_FIELDS:
            fail(f"unexpected ledger columns: {fieldnames!r}")
        if any(set(row) != set(ledgers.LEDGER_FIELDS) for row in rows):
            fail("ledger row schema drift")

        binding = validate_source_binding(lang, rows)
        review = validate_reviews(rows)
        report["structural_gate"] = "PASS"
        report["review_gate"] = review["gate"]
        report["source_binding"] = binding
        report["review_counts"] = review["counts"]
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["review_gate"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

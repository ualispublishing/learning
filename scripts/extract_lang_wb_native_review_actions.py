#!/usr/bin/env python3
"""Extract reviewer-recorded FAIL/HOLD items from a LANG-WB native-review ledger.

This tool never adjudicates language and never edits a reviewer decision. It
validates the ledger against the current production candidate, then projects
only explicit FAIL/HOLD rows into a compact remediation JSON file.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import build_lang_wb_native_review_ledgers as ledgers
import validate_lang_wb_native_review_ledger as validator


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("language", choices=tuple(ledgers.LANGUAGES))
    parser.add_argument(
        "ledger",
        nargs="?",
        help="Path to reviewed ledger; defaults to audit/.../native-review-ledgers/<language>_native_review_ledger.csv",
    )
    parser.add_argument(
        "--out",
        help="Optional output JSON path. Defaults beside the ledger as *_actions.json.",
    )
    args = parser.parse_args()

    lang = args.language
    ledger_path = (
        Path(args.ledger).resolve()
        if args.ledger
        else ledgers.OUT / f"{lang}_native_review_ledger.csv"
    )
    out_path = (
        Path(args.out).resolve()
        if args.out
        else ledger_path.with_name(ledger_path.stem + "_actions.json")
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    report: dict[str, Any] = {
        "schema": "lang-wb-native-review-actions-v1",
        "release": "v1.0",
        "language": lang,
        "ledger_path": str(ledger_path),
        "source_binding": None,
        "counts": None,
        "actions": [],
        "error": None,
        "note": "Projection of explicit human reviewer decisions only; no linguistic inference or status mutation is performed.",
    }

    try:
        fieldnames, rows = validator.read_csv(ledger_path)
        if fieldnames != ledgers.LEDGER_FIELDS:
            validator.fail(f"unexpected ledger columns: {fieldnames!r}")
        if any(set(row) != set(ledgers.LEDGER_FIELDS) for row in rows):
            validator.fail("ledger row schema drift")

        binding = validator.validate_source_binding(lang, rows)
        review = validator.validate_reviews(rows)
        counts: Counter[str] = Counter()
        actions: list[dict[str, Any]] = []

        for ordinal, row in enumerate(rows, start=1):
            outcome = row.get("review_outcome", "").strip().upper()
            counts[outcome or "UNREVIEWED"] += 1
            if outcome not in {"FAIL", "HOLD"}:
                continue
            actions.append(
                {
                    "ledger_row": ordinal,
                    "item_type": row["item_type"],
                    "rank": int(row["rank"]),
                    "level": row["level"],
                    "target": row["target"],
                    "english": row["english"],
                    "part_of_speech": row["part_of_speech"],
                    "attribution": row["attribution"],
                    "review_outcome": outcome,
                    "defect_type": row["defect_type"],
                    "reviewer_notes": row["reviewer_notes"],
                    "proposed_correction": row["proposed_correction"],
                }
            )

        report["source_binding"] = binding
        report["counts"] = {
            "PASS": counts["PASS"],
            "FAIL": counts["FAIL"],
            "HOLD": counts["HOLD"],
            "UNREVIEWED": counts["UNREVIEWED"],
            "action_items": len(actions),
            "review_gate": review["gate"],
        }
        report["actions"] = actions
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
        out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build a CEFR-neutral Arabic multiword-expression exposure ledger.

The canonical phrase bank remains the source of truth. This builder assigns stable
IDs by canonical CSV row order and deliberately does *not* infer CEFR level from
that order. Level eligibility is a separate reviewed concern.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "arabic_phrase_bank.csv"
OUTPUT = ROOT / "reading" / "ledgers" / "arabic_phrase_exposure.jsonl"
SUMMARY = ROOT / "reading" / "ledgers" / "arabic_phrase_exposure_summary.json"


def build() -> tuple[int, int]:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()

    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["Front", "Back"]:
            raise ValueError(f"Unexpected phrase-bank schema: {reader.fieldnames!r}")

        for source_row, row in enumerate(reader, start=1):
            front = (row.get("Front") or "").strip()
            if not front:
                raise ValueError(f"Empty Front at canonical phrase-bank row {source_row}")
            if front in seen:
                raise ValueError(f"Duplicate phrase front at row {source_row}: {front}")
            seen.add(front)

            rows.append(
                {
                    "id": f"ar-p{source_row:03d}",
                    "language": "ar",
                    "kind": "multiword_expression",
                    "source": "arabic_phrase_bank.csv",
                    "source_row": source_row,
                    "front": front,
                    "cefr_eligibility": "unreviewed",
                    "introduced_in": None,
                    "meaningful_contacts": 0,
                    "learner_successes": 0,
                    "learner_failures": 0,
                    "last_contact_passage": None,
                    "next_reinforcement_stage": "R0",
                }
            )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )

    summary = {
        "status": "PASS",
        "language": "ar",
        "source": "arabic_phrase_bank.csv",
        "source_rows": len(rows),
        "ledger_rows": len(rows),
        "unique_fronts": len(seen),
        "id_namespace": "ar-pNNN",
        "cefr_policy": "neutral; source order does not imply learner level",
        "learner_success_assumed": False,
        "notes": [
            "The canonical phrase bank is not modified by this build.",
            "All phrase CEFR eligibility begins unreviewed and must be assigned by an explicit pedagogical review layer.",
            "Phrase exposure is kept separate from the ranked ar-rNN single-word ledger.",
        ],
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(rows), len(seen)


if __name__ == "__main__":
    count, unique = build()
    print(f"built {count} Arabic phrase-ledger rows ({unique} unique fronts)")

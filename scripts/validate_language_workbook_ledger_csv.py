#!/usr/bin/env python3
"""Fail closed when a LANG-WB adjudication CSV row changes column shape.

This protects the repair pipeline from malformed quoting around comma-containing
proposals. A row that parses to more or fewer columns than its header must never
reach the linguistic repair applicator.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit" / "language-workbooks" / "v1.0"
LEDGER_DIRS = (AUDIT / "row_by_row", AUDIT / "row_by_row_vocab")


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle, strict=True)
            try:
                header = next(reader)
            except StopIteration:
                return [f"{path}: empty CSV"]
            if not header or len(set(header)) != len(header):
                errors.append(f"{path}: invalid or duplicate header fields: {header!r}")
            if header[:3] != ["rank", "status", "note"]:
                errors.append(f"{path}: unexpected leading header fields: {header!r}")
            expected = len(header)
            for row in reader:
                if not row or all(not cell.strip() for cell in row):
                    continue
                if len(row) != expected:
                    rank = row[0] if row else "?"
                    errors.append(
                        f"{path}:{reader.line_num}: rank {rank}: parsed {len(row)} columns; "
                        f"expected {expected}. Check CSV quoting around commas."
                    )
    except csv.Error as exc:
        errors.append(f"{path}: CSV parse error: {exc}")
    return errors


def main() -> None:
    files = sorted(path for directory in LEDGER_DIRS for path in directory.glob("*.csv"))
    if not files:
        raise SystemExit("No LANG-WB ledger CSV files found")
    errors: list[str] = []
    for path in files:
        errors.extend(validate_file(path))
    if errors:
        print("LANG-WB ledger CSV shape gate: FAIL")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(f"LANG-WB ledger CSV shape gate: PASS ({len(files)} files)")


if __name__ == "__main__":
    main()

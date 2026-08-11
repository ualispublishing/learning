#!/usr/bin/env python3
"""Promote a validated Arabic precision candidate to arabic_top1000.csv."""
from __future__ import annotations

import csv
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "audit" / "arabic_top1000_precision_candidate.csv"
TARGET = ROOT / "arabic_top1000.csv"
ARABIC_ONLY = re.compile(r"^[\u0621-\u064a]+$")


def main() -> None:
    with CANDIDATE.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1000:
        raise SystemExit(f"Refusing promotion: expected 1000 rows, got {len(rows)}")
    if not rows or list(rows[0].keys()) != ["Front", "Back"]:
        raise SystemExit("Refusing promotion: schema must be Front,Back")

    fronts = [r["Front"].strip() for r in rows]
    if len(set(fronts)) != 1000:
        raise SystemExit("Refusing promotion: exact fronts are not unique")
    bad_fronts = [x for x in fronts if not ARABIC_ONLY.fullmatch(x)]
    if bad_fronts:
        raise SystemExit(f"Refusing promotion: non-Arabic-only fronts: {bad_fronts[:20]!r}")

    for i, r in enumerate(rows, start=1):
        b = r["Back"]
        required = [
            f"Rank: {i}",
            "Meaning / grammatical senses:",
            "Published POS:",
            "Sources:",
            "Al-Said (2023), Table 4",
            "CALIMA-MSA r13",
        ]
        missing = [x for x in required if x not in b]
        if missing:
            raise SystemExit(f"Refusing promotion at rank {i}: missing {missing!r}")
        forbidden = ["Root Word:", "Synonyms:", "Example:", "AR: (self)"]
        found = [x for x in forbidden if x in b]
        if found:
            raise SystemExit(f"Refusing promotion at rank {i}: forbidden legacy fields {found!r}")
        if "function word" in b and "Root: —" not in b:
            raise SystemExit(f"Refusing promotion at rank {i}: function-word root policy missing")

    shutil.copyfile(CANDIDATE, TARGET)
    print("Promoted validated Al-Said/CALIMA 1000-row Arabic precision deck.")


if __name__ == "__main__":
    main()

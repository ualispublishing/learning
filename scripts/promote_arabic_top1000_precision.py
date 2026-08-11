#!/usr/bin/env python3
"""Promote a fully validated Arabic precision candidate to arabic_top1000.csv."""
from __future__ import annotations

import csv
import re
import shutil
from collections import defaultdict
from pathlib import Path

from finalize_arabic_top1000_precision import ALLOWED_DUPLICATES

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
    groups: dict[str, list[int]] = defaultdict(list)
    for rank, front in enumerate(fronts, 1):
        groups[front].append(rank)
    bad_dupes = {
        front: ranks for front, ranks in groups.items()
        if len(ranks) > 1 and ALLOWED_DUPLICATES.get(front) != set(ranks)
    }
    if bad_dupes:
        raise SystemExit(f"Refusing promotion: unexpected duplicate fronts: {bad_dupes!r}")

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
            "Existing Top-1000 inventory",
            "CALIMA-MSA r13",
        ]
        missing = [x for x in required if x not in b]
        if missing:
            raise SystemExit(f"Refusing promotion at rank {i}: missing {missing!r}")
        forbidden = ["Root Word:", "Synonyms:", "Example:", "AR: (self)"]
        found = [x for x in forbidden if x in b]
        if found:
            raise SystemExit(f"Refusing promotion at rank {i}: forbidden legacy fields {found!r}")
        if not b.strip():
            raise SystemExit(f"Refusing promotion at rank {i}: empty back")

    shutil.copyfile(CANDIDATE, TARGET)
    print("Promoted validated 1,000-row Arabic precision deck; rank/order preserved.")


if __name__ == "__main__":
    main()

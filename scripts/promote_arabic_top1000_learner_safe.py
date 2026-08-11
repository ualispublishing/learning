#!/usr/bin/env python3
"""Promote only a learner-safe Arabic Top-1000 candidate."""
from __future__ import annotations

import csv
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "audit" / "arabic_top1000_precision_candidate.csv"
TARGET = ROOT / "arabic_top1000.csv"
ARABIC_ONLY = re.compile(r"^[\u0621-\u064a]+$")
RANK_RE = re.compile(r"(?m)^Rank:\s*(\d+)\s*$")
MEANING_RE = re.compile(r"(?m)^Meaning:\s*(.+?)\s*$")

FORBIDDEN = [
    "+he;it", "+it;him", "+me", "+you", "it;they;she+", "he;it+", "you_[",
    "[def.", "[indef.", "<verb>", "the+", "and+", "for +", "Meaning / grammatical senses:",
]


def main() -> None:
    with CANDIDATE.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1000 or (rows and list(rows[0]) != ["Front", "Back"]):
        raise SystemExit("Refusing promotion: candidate must contain exactly 1000 Front,Back rows")

    seen: dict[str, list[int]] = {}
    for i, row in enumerate(rows, 1):
        front = row["Front"].strip()
        back = row["Back"] or ""
        if not ARABIC_ONLY.fullmatch(front):
            raise SystemExit(f"Refusing promotion rank {i}: invalid front {front!r}")
        seen.setdefault(front, []).append(i)
        m = RANK_RE.search(back)
        if not m or int(m.group(1)) != i:
            raise SystemExit(f"Refusing promotion rank {i}: bad rank metadata")
        meaning = MEANING_RE.search(back)
        if not meaning or not meaning.group(1).strip():
            raise SystemExit(f"Refusing promotion rank {i}: missing learner meaning")
        required = ["Published POS:", "Sources:", "Al-Said (2023), Table 4", "CALIMA-MSA r13"]
        if any(x not in back for x in required):
            raise SystemExit(f"Refusing promotion rank {i}: missing provenance/grammar metadata")
        for frag in FORBIDDEN:
            if frag in back:
                raise SystemExit(f"Refusing promotion rank {i}: raw morphology artifact {frag!r}")
        if any(ch in meaning.group(1) for ch in "[]<>") or "+" in meaning.group(1):
            raise SystemExit(f"Refusing promotion rank {i}: markup in learner meaning")

    dupes = {w: ranks for w, ranks in seen.items() if len(ranks) > 1}
    if dupes != {"ما": [10, 347]}:
        raise SystemExit(f"Refusing promotion: unexpected duplicate fronts {dupes!r}")

    shutil.copyfile(CANDIDATE, TARGET)
    print("Promoted learner-safe 1000-row Arabic deck.")


if __name__ == "__main__":
    main()

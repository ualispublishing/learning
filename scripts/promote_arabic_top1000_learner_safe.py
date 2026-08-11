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

RAW_ARTIFACTS = [
    "+he;it", "+it;him", "+me", "+you", "it;they;she+", "he;it+", "you_[",
    "[def.", "[indef.", "<verb>", "the+", "and+", "for +", "Meaning / grammatical senses:",
    "be valiant",
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
        learner_meaning = meaning.group(1).strip()
        required = ["Part of speech:", "Sources:", "Al-Said (2023), Table 4", "CALIMA-MSA r13", "Learner-safety review"]
        if any(x not in back for x in required):
            raise SystemExit(f"Refusing promotion rank {i}: missing learner/provenance metadata")
        for frag in RAW_ARTIFACTS:
            if frag in back:
                raise SystemExit(f"Refusing promotion rank {i}: raw morphology/bad-gloss artifact {frag!r}")
        if any(ch in learner_meaning for ch in "[]<>_") or "+" in learner_meaning:
            raise SystemExit(f"Refusing promotion rank {i}: machine markup in learner meaning {learner_meaning!r}")
        if len(learner_meaning) > 320:
            raise SystemExit(f"Refusing promotion rank {i}: learner meaning is excessively long")

    dupes = {w: ranks for w, ranks in seen.items() if len(ranks) > 1}
    if dupes != {"ما": [10, 347]}:
        raise SystemExit(f"Refusing promotion: unexpected duplicate fronts {dupes!r}")

    shutil.copyfile(CANDIDATE, TARGET)
    print("Promoted learner-safe 1000-row Arabic deck.")


if __name__ == "__main__":
    main()

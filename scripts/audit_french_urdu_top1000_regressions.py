#!/usr/bin/env python3
"""Hard regression tripwires for promoted French/Urdu Top-1000 decks."""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEANING_RE = re.compile(r"(?m)^Meaning:\s*(.+?)\s*$")
RANK_RE = re.compile(r"(?m)^Rank:\s*(\d+)\s*$")

EXPECTED = {
    "french": {
        "debout": ("standing",),
        "service": ("service",),
        "abandonner": ("abandon",),
        "relation": ("relationship",),
        "profiter": ("benefit",),
        "lycée": ("high school",),
        "falloir": ("necessary", "must"),
        "chez": ("home", "place"),
        "dont": ("whose",),
        "reprendre": ("resume",),
        "nul": ("none", "worthless"),
        "chose": ("thing",),
    },
    "urdu": {
        "کام": ("work",),
        "ساتھ": ("with",),
        "پہلے": ("before",),
        "دوسرے": ("second", "other"),
        "سامنے": ("front",),
        "درمیان": ("between",),
        "یہی": ("this",),
        "اندر": ("inside",),
        "نیچے": ("below",),
        "سی": ("like",),
        "آ": ("come",),
        "آئی": ("came",),
    },
}


def audit(language: str) -> None:
    path = ROOT / f"{language}_top1000.csv"
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1000:
        raise SystemExit(f"{path.name}: expected 1000 rows, got {len(rows)}")
    fronts = [(r.get("Front") or "").strip() for r in rows]
    if len(set(fronts)) != 1000:
        raise SystemExit(f"{path.name}: expected 1000 distinct fronts")
    by_front = {front: row for front, row in zip(fronts, rows)}
    problems = []
    for i, row in enumerate(rows, 1):
        back = row.get("Back") or ""
        rm = RANK_RE.search(back)
        if not rm or int(rm.group(1)) != i:
            problems.append(f"rank metadata mismatch at row {i} {fronts[i-1]!r}")
        if not MEANING_RE.search(back):
            problems.append(f"missing learner meaning at row {i} {fronts[i-1]!r}")
    for front, alternatives in EXPECTED[language].items():
        row = by_front.get(front)
        if not row:
            problems.append(f"missing critical front {front!r}")
            continue
        m = MEANING_RE.search(row.get("Back") or "")
        meaning = m.group(1).casefold() if m else ""
        if not any(x.casefold() in meaning for x in alternatives):
            problems.append(f"critical meaning mismatch {front!r}: {meaning!r}")
    if problems:
        raise SystemExit("\n".join(problems))
    print(f"{language}: 1000 rows, unique fronts, rank metadata, meanings, and {len(EXPECTED[language])} critical tripwires PASS")


def main():
    audit("french")
    audit("urdu")


if __name__ == "__main__":
    main()

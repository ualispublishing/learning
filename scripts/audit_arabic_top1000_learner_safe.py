#!/usr/bin/env python3
"""Independent learner-safety audit for arabic_top1000.csv."""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from finalize_arabic_top1000_precision import FINAL_REPAIRS
from rebuild_arabic_top1000_learner_safe import CRITICAL

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "arabic_top1000.csv"
SOURCE = ROOT / "audit" / "al_said_2023_msa1000.csv"
SUMMARY = ROOT / "audit" / "arabic_top1000_learner_safety_summary.json"
DETAIL = ROOT / "audit" / "arabic_top1000_learner_safety_audit.csv"
DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
ARABIC_ONLY = re.compile(r"^[\u0621-\u064a]+$")
RANK_RE = re.compile(r"(?m)^Rank:\s*(\d+)\s*$")
MEANING_RE = re.compile(r"(?m)^Meaning:\s*(.+?)\s*$")

RAW_ARTIFACTS = [
    "+he;it", "+it;him", "+me", "+you", "it;they;she+", "he;it+", "you_[",
    "[def.", "[indef.", "<verb>", "the+", "and+", "for +", "Meaning / grammatical senses:",
    "be valiant", "to;for + you", "in+me", "above+me", "towards+me",
]

# Direct tripwires for errors that previously passed morphology-only validation.
EXACT_EXPECTATIONS = {
    1: "in", 4: "on", 6: "to", 22: "not", 23: "but", 32: "well",
    45: "yes", 83: "very", 89: "also", 112: "thank", 127: "hello",
    133: "around", 148: "sorry", 194: "therefore", 269: "must",
    281: "because", 326: "thus", 347: "exclamative", 353: "these",
    460: "as if", 500: "speech", 503: "throughout", 550: "results",
    626: "together", 634: "except", 700: "still", 710: "when",
    785: "oil", 798: "sleep", 852: "treatment", 927: "according to",
}


def undiac(text: str) -> str:
    return DIAC.sub("", unicodedata.normalize("NFC", text or "").replace("ـ", "")).strip()


def expected_fronts() -> list[str]:
    with SOURCE.open(encoding="utf-8", newline="") as f:
        src = list(csv.DictReader(f))
    return [FINAL_REPAIRS.get(int(r["rank"]), undiac(r["front"])) for r in src]


def main() -> None:
    from camel_tools.morphology.analyzer import Analyzer
    from camel_tools.morphology.database import MorphologyDB

    with TARGET.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    expected = expected_fronts()
    analyzer = Analyzer(MorphologyDB.builtin_db("calima-msa-r13", flags="a"), backoff="NONE", cache_size=10000)

    flags = Counter()
    details = []
    fronts = []
    camel_ok = 0

    for i, row in enumerate(rows, 1):
        front = undiac(row.get("Front", ""))
        back = row.get("Back", "") or ""
        fronts.append(front)
        row_flags = []

        if not ARABIC_ONLY.fullmatch(front):
            row_flags.append("invalid_front")
        if i > len(expected) or front != expected[i-1]:
            row_flags.append("rank_inventory_mismatch")
        m = RANK_RE.search(back)
        if not m or int(m.group(1)) != i:
            row_flags.append("rank_metadata_mismatch")
        mm = MEANING_RE.search(back)
        meaning = mm.group(1).strip() if mm else ""
        if not meaning:
            row_flags.append("missing_meaning")
        if any(frag in back for frag in RAW_ARTIFACTS):
            row_flags.append("raw_morphology_or_known_bad_gloss")
        if any(ch in meaning for ch in "[]<>_") or "+" in meaning:
            row_flags.append("machine_markup_in_meaning")
        if len(meaning) > 320:
            row_flags.append("meaning_too_long_for_learner")
        required_meaning = EXACT_EXPECTATIONS.get(i)
        if required_meaning and required_meaning.casefold() not in meaning.casefold():
            row_flags.append("critical_meaning_mismatch")
        if "Part of speech:" not in back or "Sources:" not in back or "Learner-safety review" not in back:
            row_flags.append("missing_metadata")

        analyses = analyzer.analyze(front) if ARABIC_ONLY.fullmatch(front) else []
        if analyses:
            camel_ok += 1

        for fl in row_flags:
            flags[fl] += 1
        details.append({
            "rank": i,
            "front": front,
            "meaning": meaning,
            "camel_analysis_count": len(analyses),
            "flags": "|".join(row_flags),
        })

    counts = Counter(fronts)
    dupes = {w: [i for i, f in enumerate(fronts, 1) if f == w] for w, n in counts.items() if n > 1}
    if dupes != {"ما": [10, 347]}:
        flags["unexpected_duplicates"] += 1
    if len(rows) != 1000:
        flags["bad_row_count"] += 1

    with DETAIL.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["rank", "front", "meaning", "camel_analysis_count", "flags"])
        w.writeheader(); w.writerows(details)

    summary = {
        "source": "arabic_top1000.csv",
        "row_count": len(rows),
        "rank_inventory_matches": sum(1 for i, f in enumerate(fronts) if i < len(expected) and f == expected[i]),
        "distinct_front_spellings": len(set(fronts)),
        "intentional_duplicate_fronts": {"ما": [10, 347]},
        "camel_rows_with_analysis": camel_ok,
        "learner_meaning_rows": sum(1 for d in details if d["meaning"]),
        "flag_counts": dict(sorted(flags.items())),
        "blocking_problem_count": sum(flags.values()),
        "learner_safety_policy": [
            "No raw CALIMA gloss or morphology markup is learner-facing.",
            "Every row has a concise English learner meaning.",
            "High-risk function words and homographs have explicit rank-specific meanings.",
            "Known prior semantic failures have dedicated tripwire tests.",
            "Existing 1,000 rank/order is preserved exactly.",
        ],
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if flags:
        raise SystemExit("Learner-safety audit found blocking problems")


if __name__ == "__main__":
    main()

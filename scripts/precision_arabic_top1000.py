#!/usr/bin/env python3
"""Independent audit for the finalized Arabic Top-1000 deck.

Checks all 1,000 learner-facing rows while preserving the existing rank/order exactly.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from finalize_arabic_top1000_precision import FINAL_REPAIRS, ALLOWED_DUPLICATES

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "arabic_top1000.csv"
RANK_SOURCE = ROOT / "audit" / "al_said_2023_msa1000.csv"
AUDIT_DIR = ROOT / "audit"
AUDIT_CSV = AUDIT_DIR / "arabic_top1000_morphology_audit.csv"
AUDIT_JSON = AUDIT_DIR / "arabic_top1000_audit_summary.json"
DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
ARABIC_ONLY = re.compile(r"^[\u0621-\u064a]+$")
RANK_RE = re.compile(r"(?m)^Rank:\s*(\d+)\s*$")


def undiac(text: str) -> str:
    return DIAC.sub("", unicodedata.normalize("NFC", text or "").replace("ـ", "")).strip()


def expected_inventory() -> list[str]:
    with RANK_SOURCE.open(encoding="utf-8", newline="") as f:
        src = list(csv.DictReader(f))
    return [FINAL_REPAIRS.get(int(r["rank"]), undiac(r["front"])) for r in src]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()

    from camel_tools.morphology.analyzer import Analyzer
    from camel_tools.morphology.database import MorphologyDB

    with SOURCE.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        schema = reader.fieldnames
        rows = list(reader)

    expected = expected_inventory()
    db = MorphologyDB.builtin_db("calima-msa-r13", flags="a")
    analyzer = Analyzer(db, backoff="NONE", cache_size=10000)

    flags = Counter()
    audit_rows = []
    fronts = [undiac(r.get("Front", "")) for r in rows]

    if schema != ["Front", "Back"]:
        flags["bad_schema"] += 1
    if len(rows) != 1000:
        flags["bad_row_count"] += 1

    groups: dict[str, list[int]] = defaultdict(list)
    for rank, front in enumerate(fronts, 1):
        groups[front].append(rank)
    for front, ranks in groups.items():
        if len(ranks) > 1 and ALLOWED_DUPLICATES.get(front) != set(ranks):
            flags["unexpected_duplicate_front"] += 1

    for i, row in enumerate(rows, 1):
        front = undiac(row.get("Front", ""))
        back = row.get("Back", "") or ""
        row_flags = []

        if not ARABIC_ONLY.fullmatch(front):
            row_flags.append("non_arabic_or_multiword_front")
        if i <= len(expected) and front != expected[i - 1]:
            row_flags.append("rank_inventory_mismatch")

        m = RANK_RE.search(back)
        if not m or int(m.group(1)) != i:
            row_flags.append("back_rank_mismatch")

        required = [
            "Meaning / grammatical senses:",
            "Published POS:",
            "Sources:",
            "Existing Top-1000 inventory",
            "CALIMA-MSA r13",
        ]
        if any(x not in back for x in required):
            row_flags.append("missing_precision_metadata")
        if not back.strip():
            row_flags.append("empty_back")
        if any(x in back for x in ["Root Word:", "Synonyms:", "Example:", "AR: (self)"]):
            row_flags.append("legacy_generated_field_present")
        if "Orthographic variants encountered" in back:
            row_flags.append("orthographic_lexemes_merged")

        analyses = analyzer.analyze(front) if ARABIC_ONLY.fullmatch(front) else []
        # Human-resolved items may legitimately be absent/misclassified in CALIMA; the
        # finalizer records that human resolution. Non-manual rows must analyze.
        human_resolved = "Human precision review" in back
        if not analyses and not human_resolved:
            row_flags.append("camel_no_analysis_without_human_resolution")

        for fl in row_flags:
            flags[fl] += 1
        audit_rows.append({
            "rank": i,
            "front": front,
            "expected_front": expected[i - 1] if i <= len(expected) else "",
            "camel_analysis_count": len(analyses),
            "human_resolved": str(human_resolved).lower(),
            "flags": "|".join(row_flags),
        })

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    with AUDIT_CSV.open("w", encoding="utf-8", newline="") as f:
        fields = ["rank", "front", "expected_front", "camel_analysis_count", "human_resolved", "flags"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(audit_rows)

    summary = {
        "source": "arabic_top1000.csv",
        "row_count": len(rows),
        "schema": schema,
        "distinct_front_spellings": len(set(fronts)),
        "intentional_duplicate_fronts": {k: sorted(v) for k, v in ALLOWED_DUPLICATES.items()},
        "rank_inventory_matches": sum(1 for i, x in enumerate(fronts) if i < len(expected) and x == expected[i]),
        "camel_rows_analyzed": sum(1 for r in audit_rows if int(r["camel_analysis_count"]) > 0),
        "human_resolved_rows": sum(1 for r in audit_rows if r["human_resolved"] == "true"),
        "flag_counts": dict(sorted(flags.items())),
        "blocking_problem_count": sum(flags.values()),
        "principles": {
            "ranking": "Existing 1,000-item rank/order is preserved exactly.",
            "orthography": "Clear source extraction defects are repaired without moving ranks.",
            "morphology": "CALIMA-MSA r13 validates ordinary rows; explicit human review resolves analyzer/source exceptions.",
            "roots": "No invented root for closed-class/function words or uncertain cases.",
        },
    }
    AUDIT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if flags:
        raise SystemExit("Arabic precision audit found blocking problems")
    if not args.audit_only:
        raise SystemExit("Use --audit-only; mutation is handled by the finalizer/promotion gate")


if __name__ == "__main__":
    main()

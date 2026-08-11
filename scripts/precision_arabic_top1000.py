#!/usr/bin/env python3
"""Independent audit for the precision Arabic Top-1000 deck.

The audit checks the final learner-facing CSV against the repaired Al-Said rank inventory
and CALIMA-MSA coverage. It deliberately preserves Arabic orthographic distinctions:
أ / إ / آ / ا and ى / ي are not duplicate-normalized into one word.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from build_arabic_top1000_precision import SOURCE_REPAIRS

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "arabic_top1000.csv"
RANK_SOURCE = ROOT / "audit" / "al_said_2023_msa1000.csv"
AUDIT_DIR = ROOT / "audit"
AUDIT_CSV = AUDIT_DIR / "arabic_top1000_morphology_audit.csv"
AUDIT_JSON = AUDIT_DIR / "arabic_top1000_audit_summary.json"
DIAC = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
ARABIC_ONLY = re.compile(r"^[\u0621-\u064a]+$")
RANK_RE = re.compile(r"(?m)^Rank:\s*(\d+)\s*$")
ROOT_RE = re.compile(r"(?m)^\s*Root:\s*(.*)$")


def undiac(text: str) -> str:
    return DIAC.sub("", unicodedata.normalize("NFC", text or "").replace("ـ", "")).strip()


def expected_inventory() -> list[str]:
    with RANK_SOURCE.open(encoding="utf-8", newline="") as f:
        src = list(csv.DictReader(f))
    out = []
    for row in src:
        rank = int(row["rank"])
        out.append(SOURCE_REPAIRS.get(rank, undiac(row["front"])))
    return out


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
    if len(set(fronts)) != len(fronts):
        flags["duplicate_exact_front"] += len(fronts) - len(set(fronts))

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

        required = ["Meaning / grammatical senses:", "Published POS:", "Sources:",
                    "Al-Said (2023), Table 4", "CALIMA-MSA r13"]
        if any(x not in back for x in required):
            row_flags.append("missing_precision_metadata")
        if any(x in back for x in ["Root Word:", "Synonyms:", "Example:", "AR: (self)"]):
            row_flags.append("legacy_generated_field_present")
        if "Orthographic variants encountered" in back:
            row_flags.append("orthographic_lexemes_merged")

        analyses = analyzer.analyze(front) if ARABIC_ONLY.fullmatch(front) else []
        if not analyses:
            row_flags.append("camel_no_analysis")

        root_lines = ROOT_RE.findall(back)
        if "closed-class/function word" in back:
            if any(value.strip() != "— (closed-class/function word; no productive lexical root asserted)"
                   for value in root_lines if "closed-class/function word" in back and value.strip().startswith("—") is False):
                row_flags.append("function_word_root_policy_violation")

        for fl in row_flags:
            flags[fl] += 1
        audit_rows.append({
            "rank": i,
            "front": front,
            "expected_front": expected[i - 1] if i <= len(expected) else "",
            "camel_analysis_count": len(analyses),
            "flags": "|".join(row_flags),
        })

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    with AUDIT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["rank", "front", "expected_front", "camel_analysis_count", "flags"])
        w.writeheader(); w.writerows(audit_rows)

    blocking = {
        k: v for k, v in flags.items()
        if k not in {""}
    }
    summary = {
        "source": "arabic_top1000.csv",
        "row_count": len(rows),
        "schema": schema,
        "unique_exact_fronts": len(set(fronts)),
        "rank_inventory_matches": sum(1 for i, x in enumerate(fronts) if i < len(expected) and x == expected[i]),
        "camel_rows_analyzed": sum(1 for r in audit_rows if int(r["camel_analysis_count"]) > 0),
        "flag_counts": dict(sorted(flags.items())),
        "blocking_problem_count": sum(blocking.values()),
        "principles": {
            "ranking": "Al-Said 2023 Table 4 controls the 1,000-item order.",
            "orthography": "Distinct Arabic spellings are preserved; hamza/alif variants are not collapsed.",
            "morphology": "CALIMA-MSA r13 validates morphology; it does not replace the ranked inventory.",
            "roots": "No invented root for closed-class/function words.",
        },
    }
    AUDIT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if blocking:
        raise SystemExit("Arabic precision audit found blocking problems")
    if not args.audit_only:
        raise SystemExit("Use --audit-only; mutation is handled by the builder/promotion gate")


if __name__ == "__main__":
    main()

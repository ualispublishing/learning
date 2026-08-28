#!/usr/bin/env python3
"""Audit final v1.0 language-workbook decisions for cross-rank corruption.

This is a production-integrity audit, not a linguistic auto-fixer. It detects
patterns that should never pass unnoticed after row-level approvals, including:
- duplicate final target strings,
- duplicate final bilingual pairs,
- approved text copied exactly from another rank's audited source pair,
- approved target copied from another rank while English remains the current
  rank's source English (a strong stale-evidence signature), and
- CORRECT_APPROVED rows where both sides were replaced wholesale.

The report is intentionally conservative: findings are review candidates, not
permission to change learner text automatically.
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURATION = ROOT / "curation" / "language-workbooks" / "v1.0"
AUDIT = ROOT / "audit" / "language-workbooks" / "v1.0"
LANGUAGES = ("arabic", "french", "urdu")
RESOLVED = {"KEEP", "CORRECT_APPROVED", "REPLACE_APPROVED"}
DIAC_AR = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").replace("ـ", "")
    value = DIAC_AR.sub("", value)
    return re.sub(r"\s+", " ", value).strip().casefold()


def final_pair(row: dict) -> tuple[str, str]:
    status = row.get("status")
    if status == "KEEP":
        return row["source_target"].strip(), row["source_english"].strip()
    if status in {"CORRECT_APPROVED", "REPLACE_APPROVED"}:
        return row["approved_target"].strip(), row["approved_english"].strip()
    raise SystemExit(f"rank {row.get('rank')}: unresolved/unsupported status {status!r}")


def ref(row: dict) -> dict:
    target, english = final_pair(row)
    return {
        "rank": row["rank"],
        "status": row["status"],
        "source_target": row["source_target"],
        "source_english": row["source_english"],
        "final_target": target,
        "final_english": english,
        "approval_source": row.get("approval_source"),
        "approval_note": row.get("approval_note"),
    }


def duplicates(rows: list[dict], key_fn) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        groups[key_fn(row)].append(row)
    result = []
    for key, members in groups.items():
        if len(members) > 1:
            result.append({"normalized_key": key, "rows": [ref(r) for r in members]})
    result.sort(key=lambda g: [x["rank"] for x in g["rows"]])
    return result


def audit_language(language: str) -> dict:
    path = CURATION / f"{language}_sentence_row_decisions.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("rows")
    if not isinstance(rows, list) or len(rows) != 1000:
        raise SystemExit(f"{language}: expected exactly 1000 decision rows")
    if any(r.get("status") not in RESOLVED for r in rows):
        raise SystemExit(f"{language}: unresolved status remains")

    source_pair_index = defaultdict(list)
    source_target_index = defaultdict(list)
    source_english_index = defaultdict(list)
    for row in rows:
        source_pair_index[(norm(row["source_target"]), norm(row["source_english"]))].append(row["rank"])
        source_target_index[norm(row["source_target"])].append(row["rank"])
        source_english_index[norm(row["source_english"])].append(row["rank"])

    target_dupes = duplicates(rows, lambda r: norm(final_pair(r)[0]))
    pair_dupes = duplicates(rows, lambda r: (norm(final_pair(r)[0]), norm(final_pair(r)[1])))
    english_dupes = duplicates(rows, lambda r: norm(final_pair(r)[1]))

    high = []
    medium = []
    changed_both = []
    changed_target_only = []
    changed_english_only = []

    for row in rows:
        status = row["status"]
        if status == "KEEP":
            continue
        target, english = final_pair(row)
        source_t = row["source_target"].strip()
        source_e = row["source_english"].strip()
        changed_t = norm(target) != norm(source_t)
        changed_e = norm(english) != norm(source_e)
        if changed_t and changed_e:
            changed_both.append(row["rank"])
        elif changed_t:
            changed_target_only.append(row["rank"])
        elif changed_e:
            changed_english_only.append(row["rank"])

        other_pair_ranks = [
            rank for rank in source_pair_index[(norm(target), norm(english))]
            if rank != row["rank"]
        ]
        other_target_ranks = [
            rank for rank in source_target_index[norm(target)]
            if rank != row["rank"]
        ]
        other_english_ranks = [
            rank for rank in source_english_index[norm(english)]
            if rank != row["rank"]
        ]

        reasons = []
        if other_pair_ranks:
            reasons.append(f"final pair equals audited source pair of rank(s) {other_pair_ranks}")
        if changed_t and not changed_e and other_target_ranks:
            reasons.append(
                "target changed to another rank's audited source while English remained this rank's source"
            )
        if changed_e and not changed_t and other_english_ranks:
            reasons.append(
                "English changed to another rank's audited source while target remained this rank's source"
            )
        if status == "CORRECT_APPROVED" and changed_t and changed_e and other_pair_ranks:
            reasons.append("CORRECT_APPROVED wholesale replacement duplicates another source row")

        if reasons:
            high.append({
                **ref(row),
                "reasons": reasons,
                "other_source_pair_ranks": other_pair_ranks,
                "other_source_target_ranks": other_target_ranks,
                "other_source_english_ranks": other_english_ranks,
            })
        elif status == "CORRECT_APPROVED" and changed_t and changed_e:
            medium.append({
                **ref(row),
                "reasons": ["CORRECT_APPROVED changed both target and English; requires semantic re-verification"],
                "other_source_target_ranks": other_target_ranks,
                "other_source_english_ranks": other_english_ranks,
            })

    target_duplicate_ranks = sorted({r["rank"] for g in target_dupes for r in g["rows"]})
    pair_duplicate_ranks = sorted({r["rank"] for g in pair_dupes for r in g["rows"]})
    high_ranks = sorted({r["rank"] for r in high})
    medium_ranks = sorted({r["rank"] for r in medium})

    return {
        "language": language,
        "source_zip_sha256": data.get("source_zip_sha256"),
        "status_counts": dict(sorted(Counter(r["status"] for r in rows).items())),
        "changed_both_count": len(changed_both),
        "changed_target_only_count": len(changed_target_only),
        "changed_english_only_count": len(changed_english_only),
        "target_duplicate_group_count": len(target_dupes),
        "target_duplicate_ranks": target_duplicate_ranks,
        "pair_duplicate_group_count": len(pair_dupes),
        "pair_duplicate_ranks": pair_duplicate_ranks,
        "english_duplicate_group_count": len(english_dupes),
        "high_confidence_cross_rank_findings_count": len(high),
        "high_confidence_cross_rank_ranks": high_ranks,
        "medium_wholesale_correction_findings_count": len(medium),
        "medium_wholesale_correction_ranks": medium_ranks,
        "target_duplicate_groups": target_dupes,
        "pair_duplicate_groups": pair_dupes,
        "high_confidence_cross_rank_findings": high,
        "medium_wholesale_correction_findings": medium,
        "english_duplicate_groups": english_dupes,
    }


def main() -> None:
    languages = {language: audit_language(language) for language in LANGUAGES}
    result = {
        "release": "v1.0",
        "gate": "FAIL" if any(
            x["target_duplicate_group_count"]
            or x["pair_duplicate_group_count"]
            or x["high_confidence_cross_rank_findings_count"]
            or x["medium_wholesale_correction_findings_count"]
            for x in languages.values()
        ) else "PASS",
        "languages": languages,
        "policy": (
            "Target/pair collisions and cross-rank copied corrections block production. "
            "English duplicates alone are reported for review because intentional gender/register/lexical variants may share English."
        ),
    }
    out = AUDIT / "final_decision_integrity_audit.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    compact = {
        "gate": result["gate"],
        "languages": {
            language: {
                key: value
                for key, value in audit.items()
                if key in {
                    "status_counts",
                    "changed_both_count",
                    "changed_target_only_count",
                    "changed_english_only_count",
                    "target_duplicate_group_count",
                    "target_duplicate_ranks",
                    "pair_duplicate_group_count",
                    "pair_duplicate_ranks",
                    "english_duplicate_group_count",
                    "high_confidence_cross_rank_findings_count",
                    "high_confidence_cross_rank_ranks",
                    "medium_wholesale_correction_findings_count",
                    "medium_wholesale_correction_ranks",
                }
            }
            for language, audit in languages.items()
        },
    }
    print(json.dumps(compact, ensure_ascii=False, indent=2))
    if result["gate"] != "PASS":
        raise SystemExit("final decision integrity audit found production-blocking cross-rank/collision findings")


if __name__ == "__main__":
    main()

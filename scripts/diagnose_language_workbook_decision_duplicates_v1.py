#!/usr/bin/env python3
"""Temporary diagnostic for normalized collisions in final workbook decisions."""
from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURATION = ROOT / "curation" / "language-workbooks" / "v1.0"
DIAC_AR = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").replace("ـ", "")
    value = DIAC_AR.sub("", value)
    return re.sub(r"\s+", " ", value).strip().casefold()


def final_pair(row: dict) -> tuple[str, str]:
    if row["status"] == "KEEP":
        return row["source_target"], row["source_english"]
    return row["approved_target"], row["approved_english"]


def groups(rows: list[dict], side: int) -> list[list[dict]]:
    by = defaultdict(list)
    for row in rows:
        pair = final_pair(row)
        by[norm(pair[side])].append({
            "rank": row["rank"],
            "status": row["status"],
            "target": pair[0],
            "english": pair[1],
            "source_target": row["source_target"],
            "source_english": row["source_english"],
            "approval_note": row.get("approval_note"),
            "approval_source": row.get("approval_source"),
        })
    return [g for g in by.values() if len(g) > 1]


def main() -> None:
    result = {}
    for language in ("arabic", "french", "urdu"):
        data = json.loads((CURATION / f"{language}_sentence_row_decisions.json").read_text(encoding="utf-8"))
        rows = data["rows"]
        target = groups(rows, 0)
        english = groups(rows, 1)
        result[language] = {
            "target_duplicate_groups": target,
            "english_duplicate_groups": english,
            "target_group_count": len(target),
            "english_group_count": len(english),
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

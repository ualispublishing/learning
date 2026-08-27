#!/usr/bin/env python3
"""Build a compact, source-locked queue of unresolved sentence rows.

This report does not alter any row decision. It mirrors the live compiled decision
files so reviewers can inspect unresolved bilingual pairs and their exact audit
evidence without scanning three 1000-row ledgers.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURATION = ROOT / "curation" / "language-workbooks" / "v1.0"
OUT = CURATION / "sentence_native_review_queue.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    report: dict = {
        "artifact": "sentence native-review queue",
        "release": "v1.0",
        "policy": "Read-only projection of live NATIVE_REVIEW rows; no inference or status changes are performed.",
        "languages": {},
        "total_unresolved": 0,
    }

    for language in ("arabic", "french", "urdu"):
        doc = load(CURATION / f"{language}_sentence_row_decisions.json")
        rows = []
        for row in doc.get("rows", []):
            if row.get("status") != "NATIVE_REVIEW":
                continue
            rows.append(
                {
                    "rank": row["rank"],
                    "audit_fingerprint": row.get("audit_fingerprint"),
                    "source_target": row.get("source_target"),
                    "source_english": row.get("source_english"),
                    "confirmed_findings": row.get("confirmed_findings", []),
                    "editorial_flags": row.get("editorial_flags", []),
                }
            )
        report["languages"][language] = {
            "source_zip_sha256": doc.get("source_zip_sha256"),
            "count": len(rows),
            "rows": rows,
        }
        report["total_unresolved"] += len(rows)

    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "total_unresolved": report["total_unresolved"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

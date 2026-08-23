#!/usr/bin/env python3
"""Compile one authoritative curation decision for every workbook sentence row.

The completed row-by-row editorial audit is the source of truth. This script does
not re-audit or invent new corrections. It only converts the audit ledgers into
explicit per-rank states that downstream correction/regeneration must obey.

Initial states:
- KEEP: the row was explicitly inside a completed audit range and no issue was logged.
- CORRECT_PENDING_SECOND_PASS: a confirmed/high-confidence finding contains an
  audited recommendation that can be verified and promoted.
- REPLACE_PENDING_SECOND_PASS: the audit explicitly calls for replacement or
  retranslation rather than a deterministic edit.
- NATIVE_REVIEW: the audit flagged register/naturalness/ambiguity or supplied no
  deterministic correction.

Only a later second-pass verification may promote pending states to
CORRECT_APPROVED / REPLACE_APPROVED. Regeneration must fail while any pending or
native-review state remains.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "audit" / "language-workbooks" / "v1.0"
OUT = ROOT / "curation" / "language-workbooks" / "v1.0"

CONFIG = {
    "arabic": {
        "source": ROOT / "completed/languages/workbooks/v1.0/arabic/arabic_sentence_bank_1000.csv",
        "ledgers": [
            "arabic_sentence_editorial_audit_001_250.json",
            "arabic_sentence_editorial_audit_251_500.json",
            "arabic_sentence_editorial_audit_501_750.json",
            "arabic_sentence_editorial_audit_751_1000.json",
        ],
        "source_zip_sha256": "b72f70d3b724c3060da55f74ea1753da249d8eb38a6dbdea3dcc28798d077914",
    },
    "french": {
        "source": ROOT / "completed/languages/workbooks/v1.0/french/french_sentence_bank_1000.csv",
        "ledgers": [
            "french_sentence_editorial_audit_001_250.json",
            "french_sentence_editorial_audit_251_500.json",
            "french_sentence_editorial_audit_501_750.json",
            "french_sentence_editorial_audit_751_1000.json",
        ],
        "source_zip_sha256": "9e35994767f7307dc1fa9d5efcc36681f3756a1bdaaa02c1381b3eb11461261e",
    },
    "urdu": {
        "source": ROOT / "completed/languages/workbooks/v1.0/urdu/urdu_sentence_bank_1000.csv",
        "ledgers": [
            "urdu_sentence_editorial_audit.json",
            "urdu_sentence_editorial_audit_251_500.json",
            "urdu_sentence_editorial_audit_501_750.json",
            "urdu_sentence_editorial_audit_751_1000.json",
        ],
        "source_zip_sha256": "d55d3b4f95a6957093d7b46ddb244fd3a6530367dfc9fefd9baced598c9234a5",
    },
}


def load_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1000:
        raise SystemExit(f"Expected 1000 rows in {path}, found {len(rows)}")
    for expected, row in enumerate(rows, start=1):
        if int(row["rank"]) != expected:
            raise SystemExit(f"Rank drift in {path}: expected {expected}, found {row['rank']}")
    return rows


def is_replace_action(value: object) -> bool:
    if not isinstance(value, str):
        return False
    value = value.lower()
    return "replace" in value or "retranslate" in value


def compile_language(language: str, cfg: dict) -> dict:
    rows = load_rows(cfg["source"])
    audited_ranks: set[int] = set()
    confirmed: dict[int, list[dict]] = {}
    flags: dict[int, list[dict]] = {}

    for filename in cfg["ledgers"]:
        path = AUDIT / filename
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("source_zip_sha256") not in (None, cfg["source_zip_sha256"]):
            raise SystemExit(f"Source hash mismatch in {path}")

        span = data.get("range")
        if span:
            start, end = int(span["start"]), int(span["end"])
        else:
            # The original Urdu 1-250 ledger predates the explicit range object.
            start, end = 1, 250
        for rank in range(start, end + 1):
            if rank in audited_ranks:
                raise SystemExit(f"Overlapping audit coverage for {language} rank {rank}")
            audited_ranks.add(rank)

        for item in data.get("confirmed_or_high_confidence_findings", []):
            rank = int(item["rank"])
            confirmed.setdefault(rank, []).append({"ledger": filename, **item})

        for item in data.get("normalization_or_editorial_flags", []):
            for rank in item.get("ranks", []):
                rank = int(rank)
                flags.setdefault(rank, []).append({"ledger": filename, **item})

    expected = set(range(1, 1001))
    if audited_ranks != expected:
        missing = sorted(expected - audited_ranks)
        extra = sorted(audited_ranks - expected)
        raise SystemExit(f"Incomplete audit coverage for {language}; missing={missing[:20]} extra={extra[:20]}")

    decisions = []
    for row in rows:
        rank = int(row["rank"])
        c = confirmed.get(rank, [])
        f = flags.get(rank, [])

        if c:
            if any(is_replace_action(item.get("recommended_action")) for item in c):
                status = "REPLACE_PENDING_SECOND_PASS"
            elif all(item.get("recommended") for item in c):
                status = "CORRECT_PENDING_SECOND_PASS"
            else:
                status = "NATIVE_REVIEW"
        elif f:
            status = "NATIVE_REVIEW"
        else:
            status = "KEEP"

        decisions.append(
            {
                "rank": rank,
                "status": status,
                "source_target": row["target"],
                "source_english": row["english"],
                "source_attribution": row["attribution"],
                "confirmed_findings": c,
                "editorial_flags": f,
                "approved_target": None,
                "approved_english": None,
                "approval_note": None,
            }
        )

    counts: dict[str, int] = {}
    for item in decisions:
        counts[item["status"]] = counts.get(item["status"], 0) + 1

    return {
        "artifact": f"{language} sentence row decisions",
        "release": "v1.0",
        "language": language,
        "source_path": str(cfg["source"].relative_to(ROOT)),
        "source_zip_sha256": cfg["source_zip_sha256"],
        "decision_source": "completed row-by-row editorial audit",
        "policy": {
            "row_count": 1000,
            "every_rank_has_exactly_one_status": True,
            "corrections_must_come_from_audited_row": True,
            "independent_rederivation_during_build_forbidden": True,
            "pending_or_native_review_blocks_regeneration": True,
            "second_pass_required_before_correction_or_replacement_approval": True,
        },
        "status_counts": counts,
        "rows": decisions,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {"release": "v1.0", "languages": {}, "total_rows": 0, "unresolved_rows": 0}
    for language, cfg in CONFIG.items():
        compiled = compile_language(language, cfg)
        path = OUT / f"{language}_sentence_row_decisions.json"
        path.write_text(json.dumps(compiled, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        counts = compiled["status_counts"]
        unresolved = sum(v for k, v in counts.items() if k != "KEEP")
        summary["languages"][language] = {"status_counts": counts, "unresolved_rows": unresolved}
        summary["total_rows"] += 1000
        summary["unresolved_rows"] += unresolved

    (OUT / "sentence_row_decision_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

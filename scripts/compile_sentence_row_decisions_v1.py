#!/usr/bin/env python3
"""Compile one authoritative curation decision for every workbook sentence row.

The completed row-by-row editorial audit is the source of truth. This script does
not invent build-time corrections. It converts the audit ledgers into an explicit
state for every rank and preserves an existing approval only when the source row
and its exact audit evidence are unchanged.

Second-pass review may discover that a first-pass recommendation itself was
incomplete or overconfident. Such changes must be recorded in a language-specific
`*_sentence_second_pass_amendments.json` audit file. An amendment replaces the
audit evidence for only the named rank; it never edits the source row directly.

Initial states:
- KEEP
- CORRECT_PENDING_SECOND_PASS
- REPLACE_PENDING_SECOND_PASS
- NATIVE_REVIEW

Approved states preserved only under an unchanged audit fingerprint:
- CORRECT_APPROVED
- REPLACE_APPROVED
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "audit" / "language-workbooks" / "v1.0"
OUT = ROOT / "curation" / "language-workbooks" / "v1.0"
RESOLVED = {"KEEP", "CORRECT_APPROVED", "REPLACE_APPROVED"}
APPROVED = {"CORRECT_APPROVED", "REPLACE_APPROVED"}

CONFIG = {
    "arabic": {
        "source": ROOT / "completed/languages/workbooks/v1.0/arabic/arabic_sentence_bank_1000.csv",
        "ledgers": [
            "arabic_sentence_editorial_audit_001_250.json",
            "arabic_sentence_editorial_audit_251_500.json",
            "arabic_sentence_editorial_audit_501_750.json",
            "arabic_sentence_editorial_audit_751_1000.json",
        ],
        "amendments": "arabic_sentence_second_pass_amendments.json",
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
        "amendments": "french_sentence_second_pass_amendments.json",
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
        "amendments": "urdu_sentence_second_pass_amendments.json",
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


def fingerprint(row: dict, confirmed: list[dict], flags: list[dict]) -> str:
    payload = {
        "source_target": row["target"],
        "source_english": row["english"],
        "source_attribution": row["attribution"],
        "confirmed_findings": confirmed,
        "editorial_flags": flags,
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_previous(path: Path) -> dict[int, dict]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("rows", [])
    return {int(row["rank"]): row for row in rows if isinstance(row, dict) and "rank" in row}


def apply_second_pass_amendments(language: str, cfg: dict, confirmed: dict[int, list[dict]], flags: dict[int, list[dict]]) -> None:
    filename = cfg.get("amendments")
    if not filename:
        return
    path = AUDIT / filename
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("language") != language or data.get("release") != "v1.0":
        raise SystemExit(f"Second-pass amendment identity/version mismatch: {path}")
    if data.get("source_zip_sha256") != cfg["source_zip_sha256"]:
        raise SystemExit(f"Second-pass amendment source hash mismatch: {path}")

    seen: set[int] = set()
    for amendment in data.get("amendments", []):
        rank = int(amendment["rank"])
        if rank in seen or not 1 <= rank <= 1000:
            raise SystemExit(f"Invalid/duplicate amendment rank {language}:{rank}")
        seen.add(rank)
        if not amendment.get("reason"):
            raise SystemExit(f"Missing amendment reason {language}:{rank}")

        new_confirmed = amendment.get("confirmed_findings", [])
        new_flags = amendment.get("editorial_flags", [])
        confirmed[rank] = [
            {"ledger": filename, "second_pass_amendment": True, **item}
            for item in new_confirmed
        ]
        flags[rank] = [
            {"ledger": filename, "second_pass_amendment": True, "ranks": [rank], **item}
            for item in new_flags
        ]


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

    # Explicit second-pass audit corrections supersede first-pass evidence only
    # for their named ranks. This is the only supported way to change an audit
    # recommendation after first-pass completion.
    apply_second_pass_amendments(language, cfg, confirmed, flags)

    output_path = OUT / f"{language}_sentence_row_decisions.json"
    previous = load_previous(output_path)
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

        audit_fingerprint = fingerprint(row, c, f)
        prior = previous.get(rank)
        approved_target = None
        approved_english = None
        approval_note = None
        approval_source = None

        if (
            prior
            and prior.get("audit_fingerprint") == audit_fingerprint
            and prior.get("status") in APPROVED
        ):
            status = prior["status"]
            approved_target = prior.get("approved_target")
            approved_english = prior.get("approved_english")
            approval_note = prior.get("approval_note")
            approval_source = prior.get("approval_source")

        decisions.append(
            {
                "rank": rank,
                "status": status,
                "audit_fingerprint": audit_fingerprint,
                "source_target": row["target"],
                "source_english": row["english"],
                "source_attribution": row["attribution"],
                "confirmed_findings": c,
                "editorial_flags": f,
                "approved_target": approved_target,
                "approved_english": approved_english,
                "approval_note": approval_note,
                "approval_source": approval_source,
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
        "decision_source": "completed row-by-row editorial audit plus explicit second-pass amendments",
        "policy": {
            "row_count": 1000,
            "every_rank_has_exactly_one_status": True,
            "corrections_must_come_from_audited_row": True,
            "independent_rederivation_during_build_forbidden": True,
            "pending_or_native_review_blocks_regeneration": True,
            "second_pass_required_before_correction_or_replacement_approval": True,
            "second_pass_audit_changes_require_explicit_amendment_file": True,
            "approval_survives_recompile_only_when_audit_fingerprint_matches": True,
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
        unresolved = sum(v for k, v in counts.items() if k not in RESOLVED)
        summary["languages"][language] = {"status_counts": counts, "unresolved_rows": unresolved}
        summary["total_rows"] += 1000
        summary["unresolved_rows"] += unresolved

    (OUT / "sentence_row_decision_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

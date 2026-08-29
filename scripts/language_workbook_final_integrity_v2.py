#!/usr/bin/env python3
"""Final-integrity v2 for language workbook v1.0.

This preserves the v1 source-lock model and adds two narrowly scoped exceptions for
historical KEEP rows:
- SOURCE_PAIR_REPAIR: repairs a provably corrupted bilingual source pair using explicit
  external evidence.
- DISPLAY_NORMALIZATION: permits punctuation/whitespace-only target cleanup while
  requiring the non-punctuation target content and English translation to remain exact.

Ordinary KEEP rows remain immutable.
"""
from __future__ import annotations

import argparse
import json
import unicodedata
from collections import Counter

import language_workbook_final_integrity_v1 as legacy

ROOT = legacy.ROOT
CURATION = legacy.CURATION
OVERRIDES = legacy.OVERRIDES
AUDIT = legacy.AUDIT
LANGUAGES = legacy.LANGUAGES
HISTORICAL_RESOLVED = legacy.HISTORICAL_RESOLVED
FINAL_RESOLVED = legacy.FINAL_RESOLVED
REVIEW_REQUIRED = legacy.REVIEW_REQUIRED
SOURCE_PAIR_REPAIR = "SOURCE_PAIR_REPAIR"
DISPLAY_NORMALIZATION = "DISPLAY_NORMALIZATION"

# Re-export helpers used by the guarded renderer.
load_json = legacy.load_json
historical_final = legacy.historical_final
load_overrides = legacy.load_overrides


def apply_source_pair_repair(language: str, row: dict, override: dict) -> dict:
    rank = int(row["rank"])
    if row.get("status") != "KEEP":
        raise SystemExit(f"{language} rank {rank}: SOURCE_PAIR_REPAIR is only valid for historical KEEP rows")
    if override.get("override_kind") != SOURCE_PAIR_REPAIR:
        raise SystemExit(
            f"{language} rank {rank}: historical KEEP override requires an explicit supported override_kind"
        )

    expected_attr = (row.get("source_attribution") or "").strip()
    if not expected_attr or override.get("source_attribution") != expected_attr:
        raise SystemExit(
            f"{language} rank {rank}: SOURCE_PAIR_REPAIR source_attribution mismatch; refusing stale repair"
        )

    evidence = override.get("external_evidence")
    if not isinstance(evidence, list) or len(evidence) < 2:
        raise SystemExit(f"{language} rank {rank}: SOURCE_PAIR_REPAIR requires at least two evidence entries")
    for i, item in enumerate(evidence, start=1):
        if isinstance(item, str):
            if not item.strip():
                raise SystemExit(f"{language} rank {rank}: external_evidence item {i} is blank")
        elif isinstance(item, dict):
            if not item or not all(isinstance(k, str) and k for k in item):
                raise SystemExit(f"{language} rank {rank}: malformed external_evidence item {i}")
        else:
            raise SystemExit(f"{language} rank {rank}: external_evidence item {i} must be string or object")

    final_status = override.get("final_status")
    if final_status not in {"CORRECT_APPROVED", "REPLACE_APPROVED"}:
        raise SystemExit(
            f"{language} rank {rank}: SOURCE_PAIR_REPAIR must resolve to CORRECT_APPROVED or REPLACE_APPROVED"
        )

    # v1 still performs the exact source_target/source_english/historical identity checks,
    # requires a review note, requires final target/English, and forbids a no-op correction.
    effective = legacy.apply_override(language, row, override)
    effective["source_pair_repair"] = True
    effective["source_pair_repair_evidence"] = evidence
    return effective


def display_skeleton(value: str) -> str:
    """Return exact semantic characters after dropping only Unicode punctuation/separators."""
    value = unicodedata.normalize("NFKC", value or "")
    return "".join(
        ch for ch in value
        if not ch.isspace()
        and not unicodedata.category(ch).startswith("P")
        and not unicodedata.category(ch).startswith("Z")
    )


def apply_display_normalization(language: str, row: dict, override: dict) -> dict:
    rank = int(row["rank"])
    if row.get("status") != "KEEP":
        raise SystemExit(f"{language} rank {rank}: DISPLAY_NORMALIZATION is only valid for historical KEEP rows")
    if override.get("override_kind") != DISPLAY_NORMALIZATION:
        raise SystemExit(f"{language} rank {rank}: invalid DISPLAY_NORMALIZATION override_kind")

    expected_attr = (row.get("source_attribution") or "").strip()
    if not expected_attr or override.get("source_attribution") != expected_attr:
        raise SystemExit(
            f"{language} rank {rank}: DISPLAY_NORMALIZATION source_attribution mismatch; refusing stale normalization"
        )

    if override.get("normalization_scope") != "punctuation_whitespace_only":
        raise SystemExit(
            f"{language} rank {rank}: DISPLAY_NORMALIZATION requires normalization_scope='punctuation_whitespace_only'"
        )
    if override.get("final_status") != "CORRECT_APPROVED":
        raise SystemExit(f"{language} rank {rank}: DISPLAY_NORMALIZATION must resolve to CORRECT_APPROVED")

    source_target = row["source_target"].strip()
    source_english = row["source_english"].strip()
    final_target = override.get("final_target")
    final_english = override.get("final_english")
    if not isinstance(final_target, str) or not final_target.strip():
        raise SystemExit(f"{language} rank {rank}: DISPLAY_NORMALIZATION final_target missing")
    if final_english != source_english:
        raise SystemExit(
            f"{language} rank {rank}: DISPLAY_NORMALIZATION may not change the English translation"
        )
    if display_skeleton(final_target) != display_skeleton(source_target):
        raise SystemExit(
            f"{language} rank {rank}: DISPLAY_NORMALIZATION changed non-punctuation target content"
        )
    if final_target.strip() == source_target:
        raise SystemExit(f"{language} rank {rank}: DISPLAY_NORMALIZATION is a no-op")

    # v1 verifies exact historical target/English/source identity and requires the review note.
    effective = legacy.apply_override(language, row, override)
    effective["display_normalization"] = True
    effective["display_normalization_scope"] = "punctuation_whitespace_only"
    return effective


def effective_language(language: str) -> dict:
    path = CURATION / f"{language}_sentence_row_decisions.json"
    data = load_json(path)
    if data.get("release") != "v1.0" or data.get("language") != language:
        raise SystemExit(f"{language}: decision identity/release mismatch")
    rows = data.get("rows")
    if not isinstance(rows, list) or len(rows) != 1000:
        raise SystemExit(f"{language}: expected 1000 historical decisions")
    source_hash = data.get("source_zip_sha256")
    if not isinstance(source_hash, str) or not source_hash:
        raise SystemExit(f"{language}: source hash missing")
    overrides = load_overrides(language, source_hash)

    effective_rows = []
    source_pair_repairs = 0
    display_normalizations = 0
    for expected_rank, row in enumerate(rows, start=1):
        if int(row.get("rank", -1)) != expected_rank:
            raise SystemExit(f"{language}: rank drift at {expected_rank}")
        status = row.get("status")
        if status not in HISTORICAL_RESOLVED:
            raise SystemExit(f"{language} rank {expected_rank}: historical unresolved status {status!r}")

        override = overrides.get(expected_rank)
        if status == "KEEP":
            if override is None:
                effective = dict(row)
                effective["historical_status"] = status
                effective["historical_target"] = row["source_target"]
                effective["historical_english"] = row["source_english"]
                effective["final_integrity_reviewed"] = True
            elif override.get("override_kind") == SOURCE_PAIR_REPAIR:
                effective = apply_source_pair_repair(language, row, override)
                source_pair_repairs += 1
            elif override.get("override_kind") == DISPLAY_NORMALIZATION:
                effective = apply_display_normalization(language, row, override)
                display_normalizations += 1
            else:
                raise SystemExit(
                    f"{language} rank {expected_rank}: historical KEEP override has unsupported override_kind"
                )
        elif override is not None:
            if override.get("override_kind") in {SOURCE_PAIR_REPAIR, DISPLAY_NORMALIZATION}:
                raise SystemExit(
                    f"{language} rank {expected_rank}: {override.get('override_kind')} cannot be used for historical {status}"
                )
            effective = legacy.apply_override(language, row, override)
        else:
            hist_target, hist_english = historical_final(row)
            effective = dict(row)
            effective["historical_status"] = status
            effective["historical_target"] = hist_target
            effective["historical_english"] = hist_english
            effective["status"] = REVIEW_REQUIRED
            effective["approved_target"] = None
            effective["approved_english"] = None
            effective["approval_note"] = None
            effective["approval_source"] = None
            effective["final_integrity_reviewed"] = False
        effective_rows.append(effective)

    out = dict(data)
    out["rows"] = effective_rows
    out["final_integrity_override_count"] = len(overrides)
    out["source_pair_repair_count"] = source_pair_repairs
    out["display_normalization_count"] = display_normalizations
    out["status_counts"] = dict(sorted(Counter(r["status"] for r in effective_rows).items()))
    return out


def final_pair(row: dict) -> tuple[str, str] | None:
    status = row.get("status")
    if status == REVIEW_REQUIRED:
        return None
    if status == "KEEP":
        return row["source_target"].strip(), row["source_english"].strip()
    return row["approved_target"].strip(), row["approved_english"].strip()


def compile_review() -> dict:
    languages = {}
    unresolved_total = 0
    final_rows_total = 0
    repair_total = 0
    normalization_total = 0
    for language in LANGUAGES:
        data = effective_language(language)
        queue = []
        for row in data["rows"]:
            pair = final_pair(row)
            if pair is None:
                queue.append({
                    "rank": row["rank"],
                    "source_target": row["source_target"],
                    "source_english": row["source_english"],
                    "historical_status": row["historical_status"],
                    "historical_target": row["historical_target"],
                    "historical_english": row["historical_english"],
                    "historical_approval_note": row.get("historical_approval_note", row.get("approval_note")),
                    "historical_approval_source": row.get("historical_approval_source", row.get("approval_source")),
                })

        unresolved = len(queue)
        unresolved_total += unresolved
        final_rows_total += len(data["rows"])
        repair_total += data["source_pair_repair_count"]
        normalization_total += data["display_normalization_count"]
        languages[language] = {
            "source_zip_sha256": data["source_zip_sha256"],
            "status_counts": data["status_counts"],
            "final_integrity_override_count": data["final_integrity_override_count"],
            "source_pair_repair_count": data["source_pair_repair_count"],
            "display_normalization_count": data["display_normalization_count"],
            "unresolved_rows": unresolved,
            "review_queue": queue,
        }

    return {
        "release": "v1.0",
        "integrity_layer": "v2",
        "gate": "PASS" if unresolved_total == 0 else "BLOCKED",
        "total_rows": final_rows_total,
        "unresolved_rows": unresolved_total,
        "source_pair_repair_count": repair_total,
        "display_normalization_count": normalization_total,
        "languages": languages,
        "policy": (
            "Historical non-KEEP approvals require exact source-locked final-integrity overrides. "
            "Historical KEEP rows remain immutable except explicit SOURCE_PAIR_REPAIR overrides with external evidence, "
            "or DISPLAY_NORMALIZATION overrides that can change punctuation/whitespace only while preserving target content and exact English."
        ),
    }


def write_review_outputs() -> dict:
    result = compile_review()
    AUDIT.mkdir(parents=True, exist_ok=True)
    (AUDIT / "final_integrity_review_queue.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "release": result["release"],
        "integrity_layer": result["integrity_layer"],
        "gate": result["gate"],
        "total_rows": result["total_rows"],
        "unresolved_rows": result["unresolved_rows"],
        "source_pair_repair_count": result["source_pair_repair_count"],
        "display_normalization_count": result["display_normalization_count"],
        "languages": {
            language: {
                "status_counts": info["status_counts"],
                "final_integrity_override_count": info["final_integrity_override_count"],
                "source_pair_repair_count": info["source_pair_repair_count"],
                "display_normalization_count": info["display_normalization_count"],
                "unresolved_rows": info["unresolved_rows"],
            }
            for language, info in result["languages"].items()
        },
        "policy": result["policy"],
    }
    (AUDIT / "final_integrity_review_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-resolved", action="store_true")
    args = parser.parse_args()
    result = write_review_outputs()
    if args.require_resolved and result["unresolved_rows"]:
        raise SystemExit(
            f"final integrity review incomplete: {result['unresolved_rows']} source-locked rows remain"
        )


if __name__ == "__main__":
    main()

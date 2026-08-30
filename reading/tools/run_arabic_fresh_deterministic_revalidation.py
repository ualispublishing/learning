#!/usr/bin/env python3
"""Fresh deterministic release revalidation for the complete Arabic A1-C2 corpus.

This is a 100%-record deterministic/evidence-state gate. It does not substitute for
semantic, native-professional, educator, independent-model, or blind human review.
It never edits canonical content or bulk-promotes review metadata.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
AUDIT = READING / "audit" / "arabic_fresh_deterministic_revalidation_2026-08-30.json"
LEVELS = ("a1", "a2", "b1", "b2", "c1", "c2")
EXPECTED_RECORDS_PER_LEVEL = 60
EXPECTED_RECORDS = 360
EXPECTED_QA = 3600


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def read_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            if not raw.strip():
                continue
            try:
                rows.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                raise AssertionError(f"{path.relative_to(ROOT)}:{lineno}: invalid JSON: {exc}") from exc
    return rows


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from strings(k)
            yield from strings(v)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def main() -> int:
    preflight = subprocess.run(
        [sys.executable, "reading/tools/validate_continuation_state.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if preflight.returncode != 0:
        print(preflight.stdout)
        raise SystemExit("State preflight failed; refusing Arabic release revalidation")

    gate0 = json.loads((READING / "audit" / "post_generation_gate0_2026-08-30.json").read_text(encoding="utf-8"))
    if gate0.get("status") != "PASS" or gate0.get("canonical_totals", {}).get("project") != 1080:
        raise SystemExit("Fresh post-generation Gate 0 PASS for 1080/1080 is required")

    category_counts = Counter()
    quality_status_counts = Counter()
    coverage_check_counts = Counter()
    linguistic_review_counts = Counter()
    pedagogical_review_counts = Counter()
    answer_key_check_counts = Counter()
    schema_check_counts = Counter()
    level_summary = {}
    canonical_hashes = {}
    total_records = 0
    total_questions = 0
    total_answers = 0
    all_ids = []
    structural_errors = []

    for level in LEVELS:
        path = READING / "arabic" / level / "passages.jsonl"
        data = path.read_bytes()
        rows = read_jsonl(path)
        if len(rows) != EXPECTED_RECORDS_PER_LEVEL:
            structural_errors.append(f"{level.upper()}: {len(rows)} records != 60")
        sequences = [r.get("sequence") for r in rows]
        if sequences != list(range(1, 61)):
            structural_errors.append(f"{level.upper()}: sequences are not exactly 1..60")

        level_counts = Counter()
        level_q = 0
        level_a = 0
        for record in rows:
            rid = record.get("id")
            all_ids.append(rid)
            quality = record.get("quality") if isinstance(record.get("quality"), dict) else {}
            status = quality.get("status", "missing")
            coverage = quality.get("coverage_check", "missing")
            linguistic = quality.get("linguistic_review", "missing")
            pedagogical = quality.get("pedagogical_review", "missing")
            answer_check = quality.get("answer_key_check", "missing")
            schema_check = quality.get("schema_check", "missing")

            quality_status_counts[status] += 1
            coverage_check_counts[coverage] += 1
            linguistic_review_counts[linguistic] += 1
            pedagogical_review_counts[pedagogical] += 1
            answer_key_check_counts[answer_check] += 1
            schema_check_counts[schema_check] += 1

            checks = {
                "not_approved": status != "approved",
                "coverage_not_pass": coverage != "pass",
                "coverage_missing_or_zero": not isinstance(record.get("estimated_known_token_coverage"), (int, float)) or record.get("estimated_known_token_coverage", 0) <= 0,
                "linguistic_not_pass": linguistic != "pass",
                "pedagogical_not_pass": pedagogical != "pass",
                "answer_key_not_pass": answer_check != "pass",
                "schema_check_not_pass": schema_check != "pass",
            }
            for category, failed in checks.items():
                if failed:
                    category_counts[category] += 1
                    level_counts[category] += 1

            qs = record.get("questions") if isinstance(record.get("questions"), list) else []
            ans = record.get("answer_key") if isinstance(record.get("answer_key"), list) else []
            level_q += len(qs)
            level_a += len(ans)
            if len(qs) != 10:
                category_counts["question_count_not_10"] += 1
                level_counts["question_count_not_10"] += 1
            if len(ans) != 10:
                category_counts["answer_count_not_10"] += 1
                level_counts["answer_count_not_10"] += 1

            qids = [q.get("id") for q in qs]
            aids = [a.get("id") for a in ans]
            if len(qids) != len(set(qids)) or len(aids) != len(set(aids)):
                category_counts["qa_duplicate_ids"] += 1
                level_counts["qa_duplicate_ids"] += 1
            answer_by_id = {a.get("id"): a for a in ans}
            linkage_bad = False
            for q in qs:
                aid = q.get("answer_id")
                a = answer_by_id.get(aid)
                if not a or a.get("question_id") != q.get("id"):
                    linkage_bad = True
                    break
            if linkage_bad:
                category_counts["answer_linkage_error"] += 1
                level_counts["answer_linkage_error"] += 1

            if any(unicodedata.normalize("NFC", s) != s for s in strings(record)):
                category_counts["unicode_not_nfc"] += 1
                level_counts["unicode_not_nfc"] += 1

        total_records += len(rows)
        total_questions += level_q
        total_answers += level_a
        canonical_hashes[level] = {
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "git_blob": git_blob_sha(data),
        }
        gate0_entry = gate0["canonical_files"].get(path.relative_to(ROOT).as_posix())
        if not gate0_entry or gate0_entry.get("sha256") != canonical_hashes[level]["sha256"]:
            structural_errors.append(f"{level.upper()}: canonical hash differs from fresh Gate 0 baseline")
        level_summary[level] = {
            "records": len(rows),
            "questions": level_q,
            "answers": level_a,
            "finding_classes": dict(sorted(level_counts.items())),
        }

    if total_records != EXPECTED_RECORDS:
        structural_errors.append(f"Arabic total records {total_records} != 360")
    if total_questions != EXPECTED_QA:
        structural_errors.append(f"Arabic total questions {total_questions} != 3600")
    if total_answers != EXPECTED_QA:
        structural_errors.append(f"Arabic total answers {total_answers} != 3600")
    if len(all_ids) != len(set(all_ids)):
        structural_errors.append("Duplicate Arabic passage IDs across levels")

    open_findings = sum(category_counts.values())
    status = "FAIL" if structural_errors or open_findings else "PASS"
    audit = {
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "language": "arabic",
        "gate": "fresh deterministic educator-release revalidation",
        "date": str(date(2026, 8, 30)),
        "status": status,
        "scope": "100% of Arabic A1-C2 canonical records; deterministic structure, Q/A linkage, Unicode normalization, and recorded release-evidence metadata only.",
        "preflight": {
            "continuation_validator": "PASS",
            "gate0_artifact": "reading/audit/post_generation_gate0_2026-08-30.json",
            "gate0_status": gate0.get("status"),
        },
        "records": total_records,
        "questions": total_questions,
        "answers": total_answers,
        "open_findings": open_findings,
        "finding_classes": dict(sorted(category_counts.items())),
        "quality_status_counts": dict(sorted(quality_status_counts.items())),
        "coverage_check_counts": dict(sorted(coverage_check_counts.items())),
        "linguistic_review_counts": dict(sorted(linguistic_review_counts.items())),
        "pedagogical_review_counts": dict(sorted(pedagogical_review_counts.items())),
        "answer_key_check_counts": dict(sorted(answer_key_check_counts.items())),
        "schema_check_counts": dict(sorted(schema_check_counts.items())),
        "levels": level_summary,
        "canonical_hashes": canonical_hashes,
        "structural_errors": structural_errors,
        "release_claim": False,
        "interpretation": (
            "A PASS here would establish only the deterministic/evidence-state prerequisite. "
            "A FAIL identifies unresolved release-evidence or structural blockers. Neither result substitutes for semantic/native/educator/blind review."
        ),
        "guard": "Do not bulk-promote draft/pending metadata to clear this gate; each quality field requires substantive supporting review evidence.",
    }
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2))

    # A deterministic release gate may legitimately report FAIL while the audit execution itself succeeds.
    # Exit nonzero only for structural/preflight failures that make the evidence invalid.
    return 1 if structural_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

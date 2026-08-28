#!/usr/bin/env python3
"""Source-locked final integrity layer for language workbook v1.0 decisions.

Historical approval files and compiled row decisions are retained as provenance,
but production does not trust a historical non-KEEP decision automatically.
Every historical CORRECT_APPROVED/REPLACE_APPROVED row is reopened as
FINAL_REVIEW_REQUIRED until an explicit final-integrity override re-verifies that
exact live source row and historical result.

Override files live in:
  curation/language-workbooks/v1.0/final_integrity_overrides/<language>_*.json

This makes the integrity repair additive and reproducible rather than rewriting
or deleting the earlier audit trail that exposed the rank-drift problem.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURATION = ROOT / "curation" / "language-workbooks" / "v1.0"
OVERRIDES = CURATION / "final_integrity_overrides"
AUDIT = ROOT / "audit" / "language-workbooks" / "v1.0"
LANGUAGES = ("arabic", "french", "urdu")
HISTORICAL_RESOLVED = {"KEEP", "CORRECT_APPROVED", "REPLACE_APPROVED"}
FINAL_RESOLVED = {"KEEP", "CORRECT_APPROVED", "REPLACE_APPROVED"}
REVIEW_REQUIRED = "FINAL_REVIEW_REQUIRED"
DIAC_AR = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").replace("ـ", "")
    value = DIAC_AR.sub("", value)
    return re.sub(r"\s+", " ", value).strip().casefold()


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def historical_final(row: dict) -> tuple[str, str]:
    status = row.get("status")
    if status == "KEEP":
        return row["source_target"].strip(), row["source_english"].strip()
    if status in {"CORRECT_APPROVED", "REPLACE_APPROVED"}:
        target = row.get("approved_target")
        english = row.get("approved_english")
        if not isinstance(target, str) or not target.strip():
            raise SystemExit(f"rank {row.get('rank')}: historical approved_target missing")
        if not isinstance(english, str) or not english.strip():
            raise SystemExit(f"rank {row.get('rank')}: historical approved_english missing")
        return target.strip(), english.strip()
    raise SystemExit(f"rank {row.get('rank')}: historical status is unresolved: {status!r}")


def load_overrides(language: str, source_hash: str) -> dict[int, dict]:
    OVERRIDES.mkdir(parents=True, exist_ok=True)
    result: dict[int, dict] = {}
    for path in sorted(OVERRIDES.glob(f"{language}_*.json")):
        doc = load_json(path)
        if doc.get("release") != "v1.0" or doc.get("language") != language:
            raise SystemExit(f"final override identity/release mismatch: {path}")
        if doc.get("source_zip_sha256") != source_hash:
            raise SystemExit(f"final override source hash mismatch: {path}")
        overrides = doc.get("overrides")
        if not isinstance(overrides, list):
            raise SystemExit(f"final override file lacks overrides list: {path}")
        for item in overrides:
            rank = int(item.get("rank", -1))
            if not 1 <= rank <= 1000:
                raise SystemExit(f"invalid final override rank {rank}: {path}")
            if rank in result:
                raise SystemExit(f"duplicate final override for {language} rank {rank}")
            copied = dict(item)
            copied["_override_source"] = str(path.relative_to(ROOT))
            result[rank] = copied
    return result


def apply_override(language: str, row: dict, override: dict) -> dict:
    rank = int(row["rank"])
    hist_status = row.get("status")
    hist_target, hist_english = historical_final(row)

    exact_checks = {
        "source_target": row.get("source_target"),
        "source_english": row.get("source_english"),
        "historical_status": hist_status,
        "historical_target": hist_target,
        "historical_english": hist_english,
    }
    for key, expected in exact_checks.items():
        if override.get(key) != expected:
            raise SystemExit(
                f"{language} rank {rank}: final override {key} mismatch; "
                "refusing stale/cross-rank override"
            )

    final_status = override.get("final_status")
    if final_status not in FINAL_RESOLVED:
        raise SystemExit(f"{language} rank {rank}: invalid final_status {final_status!r}")
    note = override.get("review_note")
    if not isinstance(note, str) or not note.strip():
        raise SystemExit(f"{language} rank {rank}: final override requires review_note")

    source_target = row["source_target"].strip()
    source_english = row["source_english"].strip()
    if final_status == "KEEP":
        target, english = source_target, source_english
    else:
        target = override.get("final_target")
        english = override.get("final_english")
        if not isinstance(target, str) or not target.strip():
            raise SystemExit(f"{language} rank {rank}: final_target missing")
        if not isinstance(english, str) or not english.strip():
            raise SystemExit(f"{language} rank {rank}: final_english missing")
        target, english = target.strip(), english.strip()
        if final_status == "CORRECT_APPROVED" and target == source_target and english == source_english:
            raise SystemExit(f"{language} rank {rank}: no-op final correction; use KEEP")

    effective = dict(row)
    effective["historical_status"] = hist_status
    effective["historical_target"] = hist_target
    effective["historical_english"] = hist_english
    effective["historical_approval_note"] = row.get("approval_note")
    effective["historical_approval_source"] = row.get("approval_source")
    effective["status"] = final_status
    effective["approved_target"] = target
    effective["approved_english"] = english
    effective["approval_note"] = note.strip()
    effective["approval_source"] = override["_override_source"]
    effective["final_integrity_reviewed"] = True
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
    for expected_rank, row in enumerate(rows, start=1):
        if int(row.get("rank", -1)) != expected_rank:
            raise SystemExit(f"{language}: rank drift at {expected_rank}")
        status = row.get("status")
        if status not in HISTORICAL_RESOLVED:
            raise SystemExit(f"{language} rank {expected_rank}: historical unresolved status {status!r}")

        if status == "KEEP":
            if expected_rank in overrides:
                raise SystemExit(
                    f"{language} rank {expected_rank}: override supplied for historical KEEP row; "
                    "KEEP rows are already source-locked and must not be silently changed"
                )
            effective = dict(row)
            effective["historical_status"] = status
            effective["historical_target"] = row["source_target"]
            effective["historical_english"] = row["source_english"]
            effective["final_integrity_reviewed"] = True
        elif expected_rank in overrides:
            effective = apply_override(language, row, overrides[expected_rank])
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
    for language in LANGUAGES:
        data = effective_language(language)
        queue = []
        resolved_pairs = []
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
            else:
                resolved_pairs.append((int(row["rank"]), pair[0], pair[1]))

        unresolved = len(queue)
        unresolved_total += unresolved
        final_rows_total += len(data["rows"])
        languages[language] = {
            "source_zip_sha256": data["source_zip_sha256"],
            "status_counts": data["status_counts"],
            "final_integrity_override_count": data["final_integrity_override_count"],
            "unresolved_rows": unresolved,
            "review_queue": queue,
        }

    return {
        "release": "v1.0",
        "gate": "PASS" if unresolved_total == 0 else "BLOCKED",
        "total_rows": final_rows_total,
        "unresolved_rows": unresolved_total,
        "languages": languages,
        "policy": (
            "Historical non-KEEP approvals are untrusted after production integrity exposed cross-rank application. "
            "Each must receive an exact source-locked final-integrity override before production."
        ),
    }


def write_review_outputs() -> dict:
    result = compile_review()
    AUDIT.mkdir(parents=True, exist_ok=True)
    full_path = AUDIT / "final_integrity_review_queue.json"
    full_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "release": result["release"],
        "gate": result["gate"],
        "total_rows": result["total_rows"],
        "unresolved_rows": result["unresolved_rows"],
        "languages": {
            language: {
                "status_counts": info["status_counts"],
                "final_integrity_override_count": info["final_integrity_override_count"],
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

#!/usr/bin/env python3
"""Normalize only the currently identified non-NFC Arabic canonical JSONL records.

The repair is byte-bounded: it NFC-normalizes raw JSONL lines without reserializing
JSON, asserts the exact expected affected-record distribution, and verifies that each
changed parsed record equals the recursively NFC-normalized pre-change record.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READING = ROOT / "reading"
SOURCE_AUDIT = READING / "audit" / "arabic_fresh_deterministic_revalidation_2026-08-30.json"
OUTPUT_AUDIT = READING / "audit" / "arabic_nfc_repair_2026-08-30.json"
LEVELS = ("a1", "a2", "b1", "b2", "c1", "c2")
EXPECTED_AFFECTED = {"a1": 0, "a2": 1, "b1": 3, "b2": 2, "c1": 0, "c2": 4}
EXPECTED_TOTAL = 10


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def norm_obj(value):
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [norm_obj(x) for x in value]
    if isinstance(value, dict):
        return {norm_obj(k): norm_obj(v) for k, v in value.items()}
    return value


def main() -> int:
    source = json.loads(SOURCE_AUDIT.read_text(encoding="utf-8"))
    if source.get("status") != "FAIL" or source.get("finding_classes", {}).get("unicode_not_nfc") != EXPECTED_TOTAL:
        raise SystemExit("Source Arabic audit no longer has the expected 10 non-NFC records; refusing repair")
    if source.get("structural_errors"):
        raise SystemExit("Source Arabic audit has structural errors; refusing normalization repair")

    changed_records = []
    file_results = {}
    total_changed = 0

    for level in LEVELS:
        path = READING / "arabic" / level / "passages.jsonl"
        before_bytes = path.read_bytes()
        expected_hash = source["canonical_hashes"][level]["sha256"]
        if sha256(before_bytes) != expected_hash:
            raise SystemExit(f"{level.upper()}: source hash drifted; refusing repair")

        raw_lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        out_lines = []
        level_changed = 0
        for lineno, raw in enumerate(raw_lines, 1):
            newline = "\n" if raw.endswith("\n") else ""
            body = raw[:-1] if newline else raw
            normalized = unicodedata.normalize("NFC", body)
            if normalized != body:
                before_obj = json.loads(body)
                after_obj = json.loads(normalized)
                if after_obj != norm_obj(before_obj):
                    raise SystemExit(f"{level.upper()} line {lineno}: change exceeds recursive NFC normalization")
                rid = before_obj.get("id")
                changed_records.append({"level": level.upper(), "line": lineno, "id": rid})
                level_changed += 1
            out_lines.append(normalized + newline)

        if level_changed != EXPECTED_AFFECTED[level]:
            raise SystemExit(f"{level.upper()}: affected lines {level_changed} != expected {EXPECTED_AFFECTED[level]}")
        total_changed += level_changed
        after_text = "".join(out_lines)
        after_bytes = after_text.encode("utf-8")
        if unicodedata.normalize("NFC", after_text) != after_text:
            raise SystemExit(f"{level.upper()}: file still contains non-NFC text after repair")
        if level_changed:
            path.write_bytes(after_bytes)
        file_results[level] = {
            "path": path.relative_to(ROOT).as_posix(),
            "affected_records": level_changed,
            "before_sha256": sha256(before_bytes),
            "before_git_blob": git_blob(before_bytes),
            "after_sha256": sha256(after_bytes),
            "after_git_blob": git_blob(after_bytes),
            "bytes_before": len(before_bytes),
            "bytes_after": len(after_bytes),
        }

    if total_changed != EXPECTED_TOTAL:
        raise SystemExit(f"Total affected records {total_changed} != expected {EXPECTED_TOTAL}")

    result = {
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "language": "arabic",
        "repair": "NFC normalization of deterministic non-NFC findings",
        "date": "2026-08-30",
        "status": "APPLIED",
        "source_audit": "reading/audit/arabic_fresh_deterministic_revalidation_2026-08-30.json",
        "source_open_findings": source["open_findings"],
        "affected_records": total_changed,
        "expected_distribution": {k.upper(): v for k, v in EXPECTED_AFFECTED.items()},
        "changed_records": changed_records,
        "files": file_results,
        "semantic_change": false,
        "repair_scope": "Unicode NFC composition only; JSON serialization/order/content otherwise preserved.",
        "required_reruns": [
            "post-generation Gate 0 hashes/state integrity",
            "fresh Arabic deterministic release revalidation",
        ],
        "release_claim": false,
    }
    OUTPUT_AUDIT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

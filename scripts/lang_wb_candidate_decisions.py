#!/usr/bin/env python3
"""Build and validate candidate-specific LANG-WB sentence decision snapshots.

Historical curation ledgers remain immutable provenance. Current human review binds
instead to deterministic snapshots built from the exact row-by-row adjudication
ledgers, the exact post-adjudication staging rows, and the exact rendered companion
sentence CSVs.
"""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import apply_language_workbook_linguistic_repairs as repairs

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit" / "language-workbooks" / "v1.0"
RELEASE = ROOT / "completed" / "languages" / "workbooks" / "v1.0"
OUT = AUDIT / "native-review-ledgers"
LANGUAGES = ("arabic", "french", "urdu")
SCHEMA = "lang-wb-resolved-sentence-decisions-v1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def sentence_csv_path(lang: str) -> Path:
    return RELEASE / lang / f"{lang}_sentence_bank_1000.csv"


def stage_csv_path(lang: str) -> Path:
    return repairs.STAGE / f"{lang}_sentences.csv"


def snapshot_path(lang: str) -> Path:
    return OUT / f"{lang}_resolved_sentence_decisions.json"


def historical_curation_path(lang: str) -> Path:
    return ROOT / "curation" / "language-workbooks" / "v1.0" / f"{lang}_sentence_row_decisions.json"


def read_sentence_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise RuntimeError(f"missing sentence companion CSV: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = reader.fieldnames or []
    expected = ["rank", "level", "target", "english", "attribution"]
    if fields != expected:
        raise RuntimeError(f"{path}: unexpected sentence CSV headers {fields!r}")
    if len(rows) != 1000 or [int(r["rank"]) for r in rows] != list(range(1, 1001)):
        raise RuntimeError(f"{path}: sentence ranks must be exactly 1..1000")
    return rows


def read_stage_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise RuntimeError(f"missing post-adjudication staging CSV: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = reader.fieldnames or []
    if fields != repairs.SENT_FIELDS:
        raise RuntimeError(f"{path}: unexpected staging sentence headers {fields!r}")
    if len(rows) != 1000 or [int(r["rank"]) for r in rows] != list(range(1, 1001)):
        raise RuntimeError(f"{path}: staging sentence ranks must be exactly 1..1000")
    return rows


def ledger_files(lang: str) -> list[Path]:
    pattern = repairs.ledger_pattern(lang)
    found: list[tuple[int, int, Path]] = []
    for path in repairs.SENT_LEDGER_DIR.glob("*.csv"):
        match = pattern.match(path.name)
        if match:
            found.append((int(match.group(1)), int(match.group(2)), path))
    found.sort()
    return [path for _, _, path in found]


def verify_decision_against_stage(item: dict[str, str], stage: dict[str, str]) -> None:
    """Ensure the post-adjudication staging row actually reflects its decision."""
    rank = int(item["rank"])
    status = item["status"]
    proposed_target = (item.get("proposed_target") or "").strip()
    proposed_english = (item.get("proposed_english") or "").strip()

    if status == "PASS":
        # repairs.load_ledgers already rejects proposals on PASS rows. The stage
        # itself is the source-locked accepted text after the repair pass.
        return
    if status != "REPAIR":
        raise RuntimeError(f"rank {rank}: unsupported sentence status {status!r}")
    if proposed_target and stage["target"] != proposed_target:
        raise RuntimeError(
            f"rank {rank}: post-adjudication staging target does not match proposed_target: "
            f"{stage['target']!r} != {proposed_target!r}"
        )
    if proposed_english and stage["english"] != proposed_english:
        raise RuntimeError(
            f"rank {rank}: post-adjudication staging English does not match proposed_english: "
            f"{stage['english']!r} != {proposed_english!r}"
        )


def provenance_profile(rows: list[dict[str, str]], lang: str) -> dict[str, Any]:
    attrs = [(row.get("attribution") or "").strip() for row in rows]
    if any(not value for value in attrs):
        raise RuntimeError(f"{lang}: every final sentence row must retain nonblank provenance")
    external = sum("CC-BY 2.0" in value and "tatoeba.org" in value for value in attrs)
    controlled = sum(value.startswith("Original controlled learner sentence — UALIS Publishing v1.0.") for value in attrs)
    if lang in {"arabic", "french"}:
        if external != 1000:
            raise RuntimeError(f"{lang}: expected 1000 Tatoeba/CC-BY provenance rows, found {external}")
        mode = "external_tatoeba_cc_by_2_0_france"
    else:
        if controlled != 1000:
            raise RuntimeError(f"{lang}: expected 1000 UALIS controlled-original provenance rows, found {controlled}")
        mode = "ualis_controlled_original"
    return {
        "mode": mode,
        "provenance_rows": len(attrs),
        "licensed_external_attribution_rows": external,
        "ualis_controlled_original_rows": controlled,
    }


def build_language_snapshot(lang: str, *, write: bool = True) -> dict[str, Any]:
    if lang not in LANGUAGES:
        raise RuntimeError(f"unsupported language: {lang}")
    final_path = sentence_csv_path(lang)
    stage_path = stage_csv_path(lang)
    final_rows = read_sentence_rows(final_path)
    stage_rows = read_stage_rows(stage_path)
    adjudications = repairs.load_ledgers(repairs.SENT_LEDGER_DIR, lang, "sentence")
    if len(adjudications) != 1000:
        raise RuntimeError(f"{lang}: expected 1000 sentence adjudications, found {len(adjudications)}")

    status_counts = Counter()
    snapshot_rows: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    for item, stage, final in zip(adjudications, stage_rows, final_rows):
        rank = int(item["rank"])
        if int(stage["rank"]) != rank or int(final["rank"]) != rank:
            raise RuntimeError(f"{lang}: rank alignment drift at {rank}")
        verify_decision_against_stage(item, stage)
        status_counts[item["status"]] += 1

        fields = ("level", "target", "english", "attribution")
        drift = {field: {"stage": stage[field], "final": final[field]} for field in fields if stage[field] != final[field]}
        if drift:
            mismatches.append({"rank": rank, "status": item["status"], "drift": drift})
            continue

        snapshot_rows.append({
            "rank": rank,
            "status": item["status"],
            "proposed_target": (item.get("proposed_target") or "").strip() or None,
            "proposed_english": (item.get("proposed_english") or "").strip() or None,
            "adjudication_note": (item.get("note") or "").strip() or None,
            "post_adjudication_stage_level": stage["level"],
            "post_adjudication_stage_target": stage["target"],
            "post_adjudication_stage_english": stage["english"],
            "post_adjudication_stage_attribution": stage["attribution"],
            "final_level": final["level"],
            "final_target": final["target"],
            "final_english": final["english"],
            "final_attribution": final["attribution"],
        })

    if mismatches:
        preview = json.dumps(mismatches[:20], ensure_ascii=False)
        raise RuntimeError(
            f"{lang}: rendered companion sentence bank does not exactly match post-adjudication staging "
            f"at {len(mismatches)} rank(s): {preview}"
        )

    source_files = ledger_files(lang)
    if not source_files:
        raise RuntimeError(f"{lang}: no sentence adjudication files found")
    profile = provenance_profile(final_rows, lang)
    historical = historical_curation_path(lang)
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "release": "v1.0",
        "language": lang,
        "binding_role": "current_candidate_sentence_decision_authority",
        "decision_basis": (
            "row-by-row sentence adjudications matched to the exact post-adjudication staging rows, "
            "which in turn match the exact rendered companion sentence CSV"
        ),
        "row_count": len(snapshot_rows),
        "unresolved_holds": 0,
        "status_counts": dict(sorted(status_counts.items())),
        "post_adjudication_stage_path": str(stage_path.relative_to(ROOT)),
        "post_adjudication_stage_sha256": sha256_path(stage_path),
        "post_adjudication_stage_git_blob_sha": git_blob_sha(stage_path),
        "sentence_csv_path": str(final_path.relative_to(ROOT)),
        "sentence_csv_sha256": sha256_path(final_path),
        "sentence_csv_git_blob_sha": git_blob_sha(final_path),
        "adjudication_sources": [
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256_path(path),
                "git_blob_sha": git_blob_sha(path),
            }
            for path in source_files
        ],
        "historical_curation": {
            "path": str(historical.relative_to(ROOT)),
            "sha256": sha256_path(historical) if historical.exists() else None,
            "binding_role": "historical_provenance_only_not_current_candidate_authority",
        },
        "provenance": profile,
        "rows": snapshot_rows,
    }
    raw = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path = snapshot_path(lang)
    if write:
        OUT.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return {
        "path": str(path.relative_to(ROOT)),
        "schema": SCHEMA,
        "sha256": sha256_bytes(raw),
        "rows": len(snapshot_rows),
        "unresolved_holds": 0,
        "status_counts": dict(sorted(status_counts.items())),
        "post_adjudication_stage_path": payload["post_adjudication_stage_path"],
        "post_adjudication_stage_sha256": payload["post_adjudication_stage_sha256"],
        "post_adjudication_stage_git_blob_sha": payload["post_adjudication_stage_git_blob_sha"],
        "sentence_csv_sha256": payload["sentence_csv_sha256"],
        "sentence_csv_git_blob_sha": payload["sentence_csv_git_blob_sha"],
        "adjudication_sources": payload["adjudication_sources"],
        "historical_curation": payload["historical_curation"],
        **profile,
    }


def build_all(*, write: bool = True) -> dict[str, dict[str, Any]]:
    return {lang: build_language_snapshot(lang, write=write) for lang in LANGUAGES}


def validate_snapshot(lang: str, manifest_entry: dict[str, Any] | None = None) -> dict[str, Any]:
    path = snapshot_path(lang)
    if not path.exists():
        raise RuntimeError(f"{lang}: missing candidate sentence decision snapshot: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != SCHEMA or payload.get("release") != "v1.0" or payload.get("language") != lang:
        raise RuntimeError(f"{lang}: candidate decision snapshot identity/schema mismatch")
    if payload.get("row_count") != 1000 or payload.get("unresolved_holds") != 0:
        raise RuntimeError(f"{lang}: candidate decision snapshot row/hold invariant failed")
    current = build_language_snapshot(lang, write=False)
    actual_sha = sha256_path(path)
    if actual_sha != current["sha256"]:
        raise RuntimeError(f"{lang}: candidate decision snapshot is stale relative to current adjudications/staging/output")
    if manifest_entry is not None:
        if manifest_entry.get("decision_path") != current["path"]:
            raise RuntimeError(f"{lang}: manifest decision_path mismatch")
        if manifest_entry.get("decision_schema") != SCHEMA:
            raise RuntimeError(f"{lang}: manifest decision_schema mismatch")
        if manifest_entry.get("decision_sha256") != actual_sha:
            raise RuntimeError(f"{lang}: manifest decision_sha256 mismatch")
        if manifest_entry.get("rows") != 1000 or manifest_entry.get("unresolved_rows") != 0:
            raise RuntimeError(f"{lang}: manifest decision row/hold invariant failed")
        if manifest_entry.get("status_counts") != current["status_counts"]:
            raise RuntimeError(f"{lang}: manifest decision status_counts mismatch")
        if manifest_entry.get("post_adjudication_stage_sha256") != current["post_adjudication_stage_sha256"]:
            raise RuntimeError(f"{lang}: manifest post_adjudication_stage_sha256 mismatch")
        if manifest_entry.get("sentence_csv_sha256") != current["sentence_csv_sha256"]:
            raise RuntimeError(f"{lang}: manifest sentence_csv_sha256 mismatch")
    return current


if __name__ == "__main__":
    print(json.dumps(build_all(write=True), ensure_ascii=False, indent=2))

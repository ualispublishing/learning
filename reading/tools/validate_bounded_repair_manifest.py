from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_relative_path(value: str, *, prefix: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise SystemExit(f"Unsafe repository path: {value}")
    normalized = path.as_posix()
    if not normalized.startswith(prefix):
        raise SystemExit(f"Path must start with {prefix!r}: {value}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail-closed preflight for bounded repair manifests.")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    manifest = load(args.manifest)
    if manifest.get("schema_version") != 1:
        raise SystemExit(f"Unsupported schema_version: {manifest.get('schema_version')}")

    required = {
        "date",
        "language",
        "level",
        "unit",
        "input_file",
        "expected_before_sha256",
        "expected_scope",
        "repair_evidence_file",
        "post_evidence_file",
        "repairs",
        "false_positives",
    }
    missing = sorted(required - set(manifest))
    if missing:
        raise SystemExit(f"Missing required manifest fields: {missing}")

    input_path = safe_relative_path(manifest["input_file"], prefix="reading/")
    repair_path = safe_relative_path(manifest["repair_evidence_file"], prefix="reading/audit/")
    post_path = safe_relative_path(manifest["post_evidence_file"], prefix="reading/audit/")
    if len({input_path, repair_path, post_path}) != 3:
        raise SystemExit("Input and evidence paths must be distinct")
    if not input_path.exists():
        raise SystemExit(f"Input corpus does not exist: {input_path}")

    raw = input_path.read_bytes()
    actual_sha = hashlib.sha256(raw).hexdigest()
    if actual_sha != manifest["expected_before_sha256"]:
        raise SystemExit(
            f"FAIL CLOSED: manifest before SHA-256 {manifest['expected_before_sha256']} != corpus {actual_sha}"
        )

    records = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    level_field = manifest.get("level_field", "cefr")
    unit_field = manifest.get("unit_field", "unit")
    scoped = [
        r
        for r in records
        if r.get(level_field) == manifest["level"] and r.get(unit_field) == manifest["unit"]
    ]
    scoped_ids = {r["id"] for r in scoped}
    questions = [q for r in scoped for q in r.get("questions", [])]
    answers = [a for r in scoped for a in r.get("answer_key", [])]
    actual_scope = {"records": len(scoped), "questions": len(questions), "answers": len(answers)}
    if actual_scope != manifest["expected_scope"]:
        raise SystemExit(f"Scope mismatch: expected={manifest['expected_scope']}, actual={actual_scope}")

    question_ids_by_passage = {r["id"]: {q["id"] for q in r.get("questions", [])} for r in scoped}
    answer_ids_by_passage = {r["id"]: {a["question_id"] for a in r.get("answer_key", [])} for r in scoped}
    declared_target_ids_by_passage = {
        r["id"]: {
            item["id"]
            for field in ("new_lexical_targets", "review_lexical_targets", "grammar_targets", "discourse_targets")
            for item in r.get(field, [])
            if isinstance(item, dict) and isinstance(item.get("id"), str) and item.get("id")
        }
        for r in scoped
    }
    for rid in scoped_ids:
        if question_ids_by_passage[rid] != answer_ids_by_passage[rid]:
            raise SystemExit(f"Question/answer linkage mismatch in {rid}")

    repair_keys = []
    for repair in manifest["repairs"]:
        key = (repair["passage_id"], repair["question_id"])
        repair_keys.append(key)
        if repair["passage_id"] not in scoped_ids:
            raise SystemExit(f"Repair is outside declared unit scope: {key}")
        if repair["question_id"] not in question_ids_by_passage[repair["passage_id"]]:
            raise SystemExit(f"Unknown repair question: {key}")
        for side in ("before", "after"):
            missing_side = sorted({"prompt", "type", "answer"} - set(repair.get(side, {})))
            if missing_side:
                raise SystemExit(f"Repair {key} missing {side} fields: {missing_side}")
        before_has_targets = "target_ids" in repair.get("before", {})
        after_has_targets = "target_ids" in repair.get("after", {})
        if before_has_targets != after_has_targets:
            raise SystemExit(f"Repair {key} must specify target_ids on both before and after, or neither")
        if before_has_targets:
            for side in ("before", "after"):
                value = repair[side]["target_ids"]
                if value is not None:
                    if not isinstance(value, list) or any(not isinstance(x, str) or not x for x in value):
                        raise SystemExit(f"Repair {key} has invalid {side}.target_ids: {value!r}")
                    if len(value) != len(set(value)):
                        raise SystemExit(f"Repair {key} has duplicate {side}.target_ids: {value!r}")
            unknown = sorted(set(repair["after"]["target_ids"] or []) - declared_target_ids_by_passage[repair["passage_id"]])
            if unknown:
                raise SystemExit(f"Repair {key} links undeclared target IDs: {unknown}")

    fp_keys = []
    for fp in manifest["false_positives"]:
        key = (fp["passage_id"], fp["question_id"])
        fp_keys.append(key)
        if fp["passage_id"] not in scoped_ids:
            raise SystemExit(f"False positive is outside declared unit scope: {key}")
        if fp["question_id"] not in question_ids_by_passage[fp["passage_id"]]:
            raise SystemExit(f"Unknown false-positive question: {key}")
        missing_fp = sorted({"prompt", "type", "answer", "reason"} - set(fp))
        if missing_fp:
            raise SystemExit(f"False positive {key} missing fields: {missing_fp}")

    if len(set(repair_keys)) != len(repair_keys):
        raise SystemExit("Duplicate repair keys in manifest")
    if len(set(fp_keys)) != len(fp_keys):
        raise SystemExit("Duplicate false-positive keys in manifest")
    overlap = sorted(set(repair_keys) & set(fp_keys))
    if overlap:
        raise SystemExit(f"Repair/false-positive keys overlap: {overlap}")

    print(
        json.dumps(
            {
                "status": "PASS_MANIFEST_PREFLIGHT",
                "manifest": str(args.manifest),
                "scope": actual_scope,
                "repairs": len(repair_keys),
                "false_positives": len(fp_keys),
                "input_sha256": actual_sha,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import apply_bounded_assessment_repairs as engine


def validate_output_by_passage(records: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    scoped, questions, answers = engine.validate_scope(records, manifest)
    by_record = {r["id"]: r for r in scoped}

    repair_keys = set()
    for repair in manifest.get("repairs", []):
        key = (repair["passage_id"], repair["question_id"])
        if key in repair_keys:
            raise SystemExit(f"Duplicate repair key in manifest: {key}")
        repair_keys.add(key)
        record = by_record.get(repair["passage_id"])
        if record is None:
            raise SystemExit(f"Missing repair passage in output: {repair['passage_id']}")
        qs, ans = engine.qa_maps(record)
        q = qs.get(repair["question_id"])
        a = ans.get(repair["question_id"])
        if q is None or a is None:
            raise SystemExit(f"Missing repair question/answer in output: {key}")
        expected_after = repair["after"]
        actual_after = engine.exact_triplet(q, a)
        wanted_after = (
            expected_after["prompt"],
            expected_after["type"],
            expected_after["answer"],
        )
        if actual_after != wanted_after:
            raise SystemExit(f"Output drift at {key}: expected={wanted_after!r}, actual={actual_after!r}")
        if "explanation" in expected_after and a.get("explanation") != expected_after["explanation"]:
            raise SystemExit(f"Explanation drift at {key}")

    fp_specs: dict[tuple[str, str], dict[str, Any]] = {}
    for fp in manifest.get("false_positives", []):
        key = (fp["passage_id"], fp["question_id"])
        if key in fp_specs:
            raise SystemExit(f"Duplicate false-positive key in manifest: {key}")
        fp_specs[key] = fp
        record = by_record.get(fp["passage_id"])
        if record is None:
            raise SystemExit(f"Missing false-positive passage: {fp['passage_id']}")
        qs, ans = engine.qa_maps(record)
        q = qs.get(fp["question_id"])
        a = ans.get(fp["question_id"])
        if q is None or a is None:
            raise SystemExit(f"Missing false-positive question/answer: {key}")
        actual = engine.exact_triplet(q, a)
        expected = (fp["prompt"], fp["type"], fp["answer"])
        if actual != expected:
            raise SystemExit(f"False-positive drift at {key}: expected={expected!r}, actual={actual!r}")

    formal_types = set(manifest.get("formal_types", engine.DEFAULT_FORMAL_TYPES))
    formal_markers = tuple(manifest.get("formal_prompt_markers", engine.DEFAULT_FORMAL_PROMPT_MARKERS))
    allowed_false_positives: list[dict[str, Any]] = []
    unexpected_findings: list[dict[str, Any]] = []
    fp_seen = set()

    for record in scoped:
        answers_by_qid = {a["question_id"]: a for a in record.get("answer_key", [])}
        for q in record.get("questions", []):
            prompt = q.get("prompt", "")
            is_formal = q.get("type") in formal_types or any(marker in prompt for marker in formal_markers)
            if not is_formal:
                continue
            key = (record["id"], q["id"])
            finding = {
                "passage_id": record["id"],
                "question_id": q["id"],
                "type": q.get("type"),
                "prompt": prompt,
            }
            if key in fp_specs:
                finding["answer"] = answers_by_qid[q["id"]].get("answer")
                finding["reason"] = fp_specs[key]["reason"]
                allowed_false_positives.append(finding)
                fp_seen.add(key)
            else:
                unexpected_findings.append(finding)

    if fp_seen != set(fp_specs):
        raise SystemExit(f"False-positive scan mismatch: expected={sorted(fp_specs)}, seen={sorted(fp_seen)}")
    if unexpected_findings:
        raise SystemExit(f"Unexpected residual metalinguistic findings: {unexpected_findings}")

    duplicate_prompts: list[dict[str, Any]] = []
    for record in scoped:
        prompt_counts = Counter(q.get("prompt", "") for q in record.get("questions", []))
        for prompt, count in sorted(prompt_counts.items()):
            if prompt and count > 1:
                duplicate_prompts.append({
                    "passage_id": record["id"],
                    "prompt": prompt,
                    "count": count,
                })
    if duplicate_prompts:
        raise SystemExit(f"Duplicate prompts within passage: {duplicate_prompts}")

    return {
        "scope": {"records": len(scoped), "questions": len(questions), "answers": len(answers)},
        "allowed_false_positives": allowed_false_positives,
        "unexpected_findings": unexpected_findings,
        "duplicate_prompts": duplicate_prompts,
        "question_type_counts": dict(sorted(Counter(q.get("type") for q in questions).items())),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply/verify fail-closed bounded repairs with duplicate-prompt checks scoped per passage."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    manifest = engine.read_json(args.manifest)
    if manifest.get("schema_version") != 1:
        raise SystemExit(f"Unsupported manifest schema_version: {manifest.get('schema_version')}")

    engine.validate_output = validate_output_by_passage
    if args.verify:
        engine.verify_manifest(args.manifest, manifest)
    else:
        engine.apply_manifest(args.manifest, manifest)


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_FORMAL_TYPES = {
    "grammar_category",
    "grammar_function",
    "grammar_identification",
    "person_form",
}
DEFAULT_FORMAL_PROMPT_MARKERS = (
    "التصنيف النحوي",
    "ما الوظيفة النحوية",
    "ما وظيفة «",
    "ماذا تصف «",
    "ماذا تعبر «",
    "ماذا تفعل «",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_jsonl(path: Path) -> tuple[bytes, list[str], list[dict[str, Any]], dict[str, int]]:
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    lines = text.splitlines()
    records: list[dict[str, Any]] = []
    by_id: dict[str, int] = {}
    for idx, line in enumerate(lines):
        if not line.strip():
            continue
        record = json.loads(line)
        rid = record["id"]
        if rid in by_id:
            raise SystemExit(f"Duplicate record id: {rid}")
        by_id[rid] = idx
        records.append(record)
    return raw, lines, records, by_id


def unit_records(records: list[dict[str, Any]], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    level_field = manifest.get("level_field", "cefr")
    unit_field = manifest.get("unit_field", "unit")
    return [
        r
        for r in records
        if r.get(level_field) == manifest["level"] and r.get(unit_field) == manifest["unit"]
    ]


def qa_maps(record: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    questions = {q["id"]: q for q in record.get("questions", [])}
    answers = {a["question_id"]: a for a in record.get("answer_key", [])}
    return questions, answers


def exact_triplet(q: dict[str, Any], a: dict[str, Any]) -> tuple[Any, Any, Any]:
    return q.get("prompt"), q.get("type"), a.get("answer")


def validate_scope(records: list[dict[str, Any]], manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    scoped = unit_records(records, manifest)
    questions = [q for r in scoped for q in r.get("questions", [])]
    answers = [a for r in scoped for a in r.get("answer_key", [])]
    expected = manifest["expected_scope"]
    actual = {"records": len(scoped), "questions": len(questions), "answers": len(answers)}
    if actual != expected:
        raise SystemExit(f"Scope mismatch: expected={expected}, actual={actual}")
    for r in scoped:
        q_ids = {q["id"] for q in r.get("questions", [])}
        a_ids = {a["question_id"] for a in r.get("answer_key", [])}
        if q_ids != a_ids:
            raise SystemExit(f"Question/answer linkage mismatch in {r['id']}")
    return scoped, questions, answers


def validate_output(records: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    scoped, questions, answers = validate_scope(records, manifest)
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
        qs, ans = qa_maps(record)
        q = qs.get(repair["question_id"])
        a = ans.get(repair["question_id"])
        if q is None or a is None:
            raise SystemExit(f"Missing repair question/answer in output: {key}")
        expected_after = repair["after"]
        actual_after = exact_triplet(q, a)
        wanted_after = (
            expected_after["prompt"],
            expected_after["type"],
            expected_after["answer"],
        )
        if actual_after != wanted_after:
            raise SystemExit(f"Output drift at {key}: expected={wanted_after!r}, actual={actual_after!r}")
        if "explanation" in expected_after and a.get("explanation") != expected_after["explanation"]:
            raise SystemExit(f"Explanation drift at {key}")
        if "target_ids" in expected_after and q.get("target_ids") != expected_after["target_ids"]:
            raise SystemExit(f"Target linkage drift at {key}: expected={expected_after["target_ids"]!r}, actual={q.get("target_ids")!r}")

    fp_specs: dict[tuple[str, str], dict[str, Any]] = {}
    for fp in manifest.get("false_positives", []):
        key = (fp["passage_id"], fp["question_id"])
        if key in fp_specs:
            raise SystemExit(f"Duplicate false-positive key in manifest: {key}")
        fp_specs[key] = fp
        record = by_record.get(fp["passage_id"])
        if record is None:
            raise SystemExit(f"Missing false-positive passage: {fp['passage_id']}")
        qs, ans = qa_maps(record)
        q = qs.get(fp["question_id"])
        a = ans.get(fp["question_id"])
        if q is None or a is None:
            raise SystemExit(f"Missing false-positive question/answer: {key}")
        actual = exact_triplet(q, a)
        expected = (fp["prompt"], fp["type"], fp["answer"])
        if actual != expected:
            raise SystemExit(f"False-positive drift at {key}: expected={expected!r}, actual={actual!r}")

    formal_types = set(manifest.get("formal_types", DEFAULT_FORMAL_TYPES))
    formal_markers = tuple(manifest.get("formal_prompt_markers", DEFAULT_FORMAL_PROMPT_MARKERS))
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

    prompt_counts = Counter(q.get("prompt", "") for q in questions)
    duplicate_prompts = sorted(p for p, count in prompt_counts.items() if p and count > 1)
    if duplicate_prompts:
        raise SystemExit(f"Duplicate prompts in bounded unit: {duplicate_prompts}")

    return {
        "scope": {"records": len(scoped), "questions": len(questions), "answers": len(answers)},
        "allowed_false_positives": allowed_false_positives,
        "unexpected_findings": unexpected_findings,
        "duplicate_prompts": duplicate_prompts,
        "question_type_counts": dict(sorted(Counter(q.get("type") for q in questions).items())),
    }


def apply_manifest(manifest_path: Path, manifest: dict[str, Any]) -> None:
    input_path = Path(manifest["input_file"])
    repair_evidence_path = Path(manifest["repair_evidence_file"])
    post_evidence_path = Path(manifest["post_evidence_file"])

    raw, lines, records, line_index_by_id = load_jsonl(input_path)
    before_sha = sha256_bytes(raw)
    expected_before = manifest["expected_before_sha256"]
    if before_sha != expected_before:
        raise SystemExit(f"FAIL CLOSED: expected input SHA-256 {expected_before}, got {before_sha}")

    validate_scope(records, manifest)
    by_record = {r["id"]: r for r in records}
    passage_text_before = {r["id"]: r.get("text") for r in records}
    applied: list[dict[str, Any]] = []
    touched_ids = set()
    seen_keys = set()

    for repair in manifest.get("repairs", []):
        key = (repair["passage_id"], repair["question_id"])
        if key in seen_keys:
            raise SystemExit(f"Duplicate repair key: {key}")
        seen_keys.add(key)
        record = by_record.get(repair["passage_id"])
        if record is None:
            raise SystemExit(f"Missing repair passage: {repair['passage_id']}")
        questions, answers = qa_maps(record)
        q = questions.get(repair["question_id"])
        a = answers.get(repair["question_id"])
        if q is None or a is None:
            raise SystemExit(f"Missing repair question/answer: {key}")

        expected_before_triplet = (
            repair["before"]["prompt"],
            repair["before"]["type"],
            repair["before"]["answer"],
        )
        actual_before_triplet = exact_triplet(q, a)
        if actual_before_triplet != expected_before_triplet:
            raise SystemExit(
                f"Source drift at {key}: expected={expected_before_triplet!r}, actual={actual_before_triplet!r}"
            )

        if "target_ids" in repair["before"] and q.get("target_ids") != repair["before"]["target_ids"]:
            raise SystemExit(f"Target-linkage source drift at {key}: expected={repair["before"]["target_ids"]!r}, actual={q.get("target_ids")!r}")
        target_ids_before = copy.deepcopy(q.get("target_ids"))
        before_snapshot = {
            "prompt": q.get("prompt"),
            "type": q.get("type"),
            "answer": a.get("answer"),
            "target_ids": target_ids_before,
        }
        after = repair["after"]
        q["prompt"] = after["prompt"]
        q["type"] = after["type"]
        a["answer"] = after["answer"]
        if "explanation" in after:
            a["explanation"] = after["explanation"]
        if "target_ids" in after:
            wanted_target_ids = copy.deepcopy(after["target_ids"])
            if wanted_target_ids is None:
                q.pop("target_ids", None)
            else:
                q["target_ids"] = wanted_target_ids
        elif q.get("target_ids") != target_ids_before:
            raise SystemExit(f"Target linkage changed unexpectedly at {key}")
        touched_ids.add(record["id"])
        applied.append(
            {
                "passage_id": key[0],
                "question_id": key[1],
                "before": before_snapshot,
                "after": {
                    "prompt": q.get("prompt"),
                    "type": q.get("type"),
                    "answer": a.get("answer"),
                    "explanation": a.get("explanation"),
                    "target_ids": copy.deepcopy(q.get("target_ids")),
                },
            }
        )

    if seen_keys != {
        (r["passage_id"], r["question_id"]) for r in manifest.get("repairs", [])
    }:
        raise SystemExit("Repair inventory mismatch")

    for rid, original_text in passage_text_before.items():
        if by_record[rid].get("text") != original_text:
            raise SystemExit(f"Passage prose changed unexpectedly: {rid}")

    for rid in touched_ids:
        line_idx = line_index_by_id[rid]
        lines[line_idx] = json.dumps(by_record[rid], ensure_ascii=False, sort_keys=True)

    serialized = "\n".join(lines) + ("\n" if raw.endswith(b"\n") else "")
    input_path.write_text(serialized, encoding="utf-8")
    after_sha = sha256_bytes(input_path.read_bytes())

    _, _, output_records, _ = load_jsonl(input_path)
    validation = validate_output(output_records, manifest)

    false_positives = validation["allowed_false_positives"]
    target_linkage_changed_count = sum(
        1 for item in applied if item["before"].get("target_ids") != item["after"].get("target_ids")
    )
    repair_evidence = {
        "schema_version": 1,
        "date": manifest["date"],
        "language": manifest["language"],
        "level": manifest["level"],
        "unit": manifest["unit"],
        "manifest": str(manifest_path),
        "status": "BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW",
        "before_sha256": before_sha,
        "after_sha256": after_sha,
        "inventory_candidates": len(applied) + len(false_positives),
        "confirmed_repairs": len(applied),
        "adjudicated_false_positive_count": len(false_positives),
        "adjudicated_false_positives": false_positives,
        "passage_text_changed": False,
        "target_linkage_changed_count": target_linkage_changed_count,
        "notable_sense_corrections": manifest.get("notable_sense_corrections", []),
        "repairs": applied,
        "release_effect": manifest.get(
            "release_effect",
            f"{manifest['language']} remains review-blocked; independent semantic/native/educator review required.",
        ),
    }
    post_evidence = {
        "schema_version": 1,
        "date": manifest["date"],
        "language": manifest["language"],
        "level": manifest["level"],
        "unit": manifest["unit"],
        "manifest": str(manifest_path),
        "bound_sha256": after_sha,
        "scope": validation["scope"],
        "inventory_candidates": len(applied) + len(false_positives),
        "confirmed_repairs": len(applied),
        "adjudicated_false_positive_count": len(false_positives),
        "allowed_false_positives": false_positives,
        "unexpected_formal_metalinguistic_finding_count": len(validation["unexpected_findings"]),
        "unexpected_findings": validation["unexpected_findings"],
        "exact_duplicate_prompt_count": len(validation["duplicate_prompts"]),
        "duplicate_prompts": validation["duplicate_prompts"],
        "passage_text_changed": False,
        "target_linkage_changed_count": target_linkage_changed_count,
        "question_type_counts": validation["question_type_counts"],
        "status": manifest.get("pass_status", "PASS_DETERMINISTIC_BOUNDED_REPAIR"),
        "limitations": "Deterministic/self-review only; independent native/educator review remains required.",
        "release_effect": repair_evidence["release_effect"],
    }
    write_json(repair_evidence_path, repair_evidence)
    write_json(post_evidence_path, post_evidence)
    print(
        json.dumps(
            {
                "status": post_evidence["status"],
                "manifest": str(manifest_path),
                "before_sha256": before_sha,
                "after_sha256": after_sha,
                "repairs": len(applied),
                "false_positives": len(false_positives),
                **validation["scope"],
            },
            ensure_ascii=False,
        )
    )


def verify_manifest(manifest_path: Path, manifest: dict[str, Any]) -> None:
    input_path = Path(manifest["input_file"])
    post_evidence_path = Path(manifest["post_evidence_file"])
    if not post_evidence_path.exists():
        raise SystemExit(f"Missing postrepair evidence: {post_evidence_path}")
    post = read_json(post_evidence_path)
    raw, _, records, _ = load_jsonl(input_path)
    current_sha = sha256_bytes(raw)
    if current_sha != post.get("bound_sha256"):
        raise SystemExit(
            f"Output SHA mismatch: evidence={post.get('bound_sha256')}, current={current_sha}"
        )
    validation = validate_output(records, manifest)
    expected_candidates = len(manifest.get("repairs", [])) + len(manifest.get("false_positives", []))
    expected_target_linkage_changes = sum(
        1
        for repair in manifest.get("repairs", [])
        if ("target_ids" in repair.get("before", {}) or "target_ids" in repair.get("after", {}))
        and repair.get("before", {}).get("target_ids") != repair.get("after", {}).get("target_ids")
    )
    checks = {
        "scope": validation["scope"],
        "inventory_candidates": expected_candidates,
        "confirmed_repairs": len(manifest.get("repairs", [])),
        "adjudicated_false_positive_count": len(manifest.get("false_positives", [])),
        "unexpected_formal_metalinguistic_finding_count": 0,
        "exact_duplicate_prompt_count": 0,
        "target_linkage_changed_count": expected_target_linkage_changes,
    }
    for key, expected in checks.items():
        if post.get(key) != expected:
            raise SystemExit(f"Postrepair evidence mismatch for {key}: expected={expected!r}, got={post.get(key)!r}")
    print(json.dumps({"status": "PASS_VERIFY", "manifest": str(manifest_path), "bound_sha256": current_sha}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply or verify exact, fail-closed bounded assessment repairs.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    manifest = read_json(args.manifest)
    if manifest.get("schema_version") != 1:
        raise SystemExit(f"Unsupported manifest schema_version: {manifest.get('schema_version')}")
    if args.verify:
        verify_manifest(args.manifest, manifest)
    else:
        apply_manifest(args.manifest, manifest)


if __name__ == "__main__":
    main()

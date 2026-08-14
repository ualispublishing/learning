#!/usr/bin/env python3
"""Final Arabic review pass 01: schema, identifiers, linkage, and data integrity.

This is intentionally a structural/mechanical audit only. It does not make
linguistic, pedagogical, lexical-sense, factual, or CEFR-quality claims.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
LEVELS = ("a1", "a2", "b1", "b2", "c1", "c2")
SCHEMA_PATH = ROOT / "reading/schema/passage.schema.json"
OUT = ROOT / "reading/audit/final_arabic_pass01_data_integrity.json"
ID_RE = re.compile(r"^ar-(a1|a2|b1|b2|c1|c2)-u(\d{2})-p(\d{2})$")


def issue(bucket: list[dict], code: str, **details) -> None:
    bucket.append({"code": code, **details})


def load_level(level: str, issues: list[dict]) -> list[dict]:
    path = ROOT / f"reading/arabic/{level}/passages.jsonl"
    rows: list[dict] = []
    if not path.exists():
        issue(issues, "missing_level_file", level=level, path=str(path.relative_to(ROOT)))
        return rows
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except Exception as exc:
            issue(issues, "invalid_json", level=level, line=lineno, error=str(exc))
            continue
        row["__audit_line__"] = lineno
        rows.append(row)
    return rows


def main() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    hard_issues: list[dict] = []
    warnings: list[dict] = []
    level_summaries: dict[str, dict] = {}
    all_ids: list[str] = []

    for level in LEVELS:
        rows = load_level(level, hard_issues)
        passage_ids = [str(r.get("id", "")) for r in rows]
        all_ids.extend(passage_ids)
        unit_counter = Counter(r.get("unit") for r in rows)
        seq_counter = Counter(r.get("sequence") for r in rows)

        if len(rows) != 60:
            issue(hard_issues, "level_passage_count", level=level, expected=60, actual=len(rows))
        expected_units = {i: 6 for i in range(1, 11)}
        actual_units = {i: unit_counter.get(i, 0) for i in range(1, 11)}
        if actual_units != expected_units:
            issue(hard_issues, "unit_grid", level=level, expected=expected_units, actual=actual_units)
        expected_sequences = set(range(1, 61))
        actual_sequences = {x for x in seq_counter if isinstance(x, int)}
        if actual_sequences != expected_sequences or any(seq_counter[x] != 1 for x in actual_sequences):
            issue(
                hard_issues,
                "sequence_grid",
                level=level,
                missing=sorted(expected_sequences - actual_sequences),
                extra=sorted(actual_sequences - expected_sequences),
                duplicates=sorted([x for x, n in seq_counter.items() if isinstance(x, int) and n > 1]),
            )

        id_counter = Counter(passage_ids)
        duplicates = sorted([pid for pid, n in id_counter.items() if pid and n > 1])
        if duplicates:
            issue(hard_issues, "duplicate_passage_ids_within_level", level=level, ids=duplicates)

        schema_error_count = 0
        q_count_errors = 0
        a_count_errors = 0
        linkage_errors = 0
        target_reference_warnings = 0

        for row in rows:
            lineno = row.pop("__audit_line__", None)
            pid = str(row.get("id", ""))
            unit = row.get("unit")

            match = ID_RE.match(pid)
            if not match:
                issue(hard_issues, "passage_id_shape", level=level, passage_id=pid, line=lineno)
            else:
                id_level, unit_text, passage_text = match.groups()
                expected_prefix_level = level
                if id_level != expected_prefix_level:
                    issue(hard_issues, "passage_id_level_mismatch", level=level, passage_id=pid, line=lineno)
                if isinstance(unit, int) and int(unit_text) != unit:
                    issue(hard_issues, "passage_id_unit_mismatch", level=level, passage_id=pid, unit=unit, line=lineno)
                pnum = int(passage_text)
                if pnum not in range(1, 7):
                    issue(hard_issues, "passage_id_pnum_out_of_range", level=level, passage_id=pid, pnum=pnum, line=lineno)

            errors = sorted(validator.iter_errors(row), key=lambda e: list(e.absolute_path))
            for err in errors:
                schema_error_count += 1
                issue(
                    hard_issues,
                    "json_schema",
                    level=level,
                    passage_id=pid,
                    line=lineno,
                    path="/".join(str(x) for x in err.absolute_path),
                    message=err.message,
                )

            questions = row.get("questions", []) if isinstance(row.get("questions"), list) else []
            answers = row.get("answer_key", []) if isinstance(row.get("answer_key"), list) else []
            if len(questions) != 10:
                q_count_errors += 1
                issue(hard_issues, "question_count", level=level, passage_id=pid, expected=10, actual=len(questions))
            if len(answers) != 10:
                a_count_errors += 1
                issue(hard_issues, "answer_count", level=level, passage_id=pid, expected=10, actual=len(answers))

            qids = [q.get("id") for q in questions if isinstance(q, dict)]
            aids = [a.get("id") for a in answers if isinstance(a, dict)]
            q_answer_ids = [q.get("answer_id") for q in questions if isinstance(q, dict)]
            a_question_ids = [a.get("question_id") for a in answers if isinstance(a, dict)]

            expected_qids = [f"q{i}" for i in range(1, 11)]
            expected_aids = [f"a{i}" for i in range(1, 11)]
            if qids != expected_qids:
                linkage_errors += 1
                issue(hard_issues, "question_id_order", level=level, passage_id=pid, expected=expected_qids, actual=qids)
            if aids != expected_aids:
                linkage_errors += 1
                issue(hard_issues, "answer_id_order", level=level, passage_id=pid, expected=expected_aids, actual=aids)
            if q_answer_ids != expected_aids:
                linkage_errors += 1
                issue(hard_issues, "question_answer_id_linkage", level=level, passage_id=pid, expected=expected_aids, actual=q_answer_ids)
            if a_question_ids != expected_qids:
                linkage_errors += 1
                issue(hard_issues, "answer_question_id_linkage", level=level, passage_id=pid, expected=expected_qids, actual=a_question_ids)

            lexical_ids = {
                t.get("id")
                for field in ("new_lexical_targets", "review_lexical_targets")
                for t in (row.get(field, []) if isinstance(row.get(field), list) else [])
                if isinstance(t, dict) and t.get("id")
            }
            for q in questions:
                if not isinstance(q, dict):
                    continue
                for tid in q.get("target_ids", []) if isinstance(q.get("target_ids"), list) else []:
                    if tid not in lexical_ids:
                        target_reference_warnings += 1
                        issue(
                            warnings,
                            "question_target_not_in_passage_lexical_targets",
                            level=level,
                            passage_id=pid,
                            question_id=q.get("id"),
                            target_id=tid,
                        )

        level_summaries[level] = {
            "passages": len(rows),
            "questions": sum(len(r.get("questions", [])) for r in rows if isinstance(r.get("questions"), list)),
            "answers": sum(len(r.get("answer_key", [])) for r in rows if isinstance(r.get("answer_key"), list)),
            "units": actual_units,
            "schema_errors": schema_error_count,
            "question_count_errors": q_count_errors,
            "answer_count_errors": a_count_errors,
            "linkage_errors": linkage_errors,
            "target_reference_warnings": target_reference_warnings,
        }

    cross_level_duplicates = sorted([pid for pid, n in Counter(all_ids).items() if pid and n > 1])
    if cross_level_duplicates:
        issue(hard_issues, "duplicate_passage_ids_across_corpus", ids=cross_level_duplicates)

    payload = {
        "pass": 1,
        "name": "data_integrity_schema_linkage",
        "scope": "Arabic A1-C2 canonical reading corpus",
        "method": "canonical JSON Schema validation plus independent count/ID/sequence/question-answer linkage checks",
        "not_claimed": ["linguistic quality", "pedagogical quality", "lexical-sense correctness", "fact correctness", "CEFR calibration"],
        "levels": level_summaries,
        "totals": {
            "passages": sum(x["passages"] for x in level_summaries.values()),
            "questions": sum(x["questions"] for x in level_summaries.values()),
            "answers": sum(x["answers"] for x in level_summaries.values()),
            "hard_issues": len(hard_issues),
            "warnings": len(warnings),
        },
        "hard_issues": hard_issues,
        "warnings": warnings,
        "status": "PASS" if not hard_issues else "FAIL",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["totals"], ensure_ascii=False))
    print("status=" + payload["status"])
    if hard_issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

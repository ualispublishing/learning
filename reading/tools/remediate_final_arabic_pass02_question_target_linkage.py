#!/usr/bin/env python3
"""Repair seven final Arabic question-target linkage defects.

Four A1 checkpoint/transfer questions legitimately test previously introduced
lexical items but omitted those items from the passage-local review schedule.
Three B1 Unit 02 questions point at unrelated lexical IDs and are corrected to
the locally declared target IDs matching the prompt words.

Allowed mutations only:
- append four A1 review_lexical_targets entries;
- replace target_ids on three exact B1 questions.
Everything else is fail-closed and immutable.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

A1_REVIEW_ADDITIONS = {
    "ar-a1-u01-p06": {
        "id": "ar-r56", "form": "حتى", "review_stage": "R1", "representation": "other",
        "expected_sequence": 6,
    },
    "ar-a1-u04-p05": {
        "id": "ar-r53", "form": "بعض", "review_stage": "R4", "representation": "contrast",
        "expected_sequence": 23,
    },
    "ar-a1-u05-p05": {
        "id": "ar-r181", "form": "يأتي", "review_stage": "R2", "representation": "contrast",
        "expected_sequence": 29,
    },
    "ar-a1-u06-p05": {
        "id": "ar-r391", "form": "بعيد", "review_stage": "R1", "representation": "contrast",
        "expected_sequence": 35,
    },
}

B1_TARGET_FIXES = {
    ("ar-b1-u02-p01", "q5"): {
        "prompt": "ماذا يعني «سبب» عندما يسأل الفريق لماذا ظهرت المشكلة؟",
        "old": ["ar-r292"],
        "new": ["ar-r113"],
        "form": "سبب",
    },
    ("ar-b1-u02-p01", "q6"): {
        "prompt": "ماذا تعني «نسخة» في سياق ملفات التقرير؟",
        "old": ["ar-r2626"],
        "new": ["ar-r1149"],
        "form": "نسخة",
    },
    ("ar-b1-u02-p02", "q5"): {
        "prompt": "ماذا يعني «حل» في هذا النص؟",
        "old": ["ar-r867"],
        "new": ["ar-r412"],
        "form": "حل",
    },
}


def read_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_rows(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def declared_ids(row: dict) -> set[str]:
    result = set()
    for field in ("new_lexical_targets", "review_lexical_targets"):
        for item in row.get(field, []):
            if isinstance(item, dict) and item.get("id"):
                result.add(str(item["id"]))
    return result


def question_map(row: dict) -> dict[str, dict]:
    return {str(q.get("id")): q for q in row.get("questions", []) if isinstance(q, dict)}


def projection(row: dict, *, remove_review: bool = False, changed_qids: set[str] | None = None) -> dict:
    x = copy.deepcopy(row)
    if remove_review:
        x.pop("review_lexical_targets", None)
    if changed_qids:
        for q in x.get("questions", []):
            if str(q.get("id")) in changed_qids:
                q.pop("target_ids", None)
    return x


def find_prior_intro(rows: list[dict], pid: str, target_id: str, form: str) -> dict:
    current = next((row for row in rows if str(row.get("id")) == pid), None)
    if current is None:
        raise AssertionError(f"missing current passage {pid}")
    seq = int(current.get("sequence"))
    matches = []
    for row in rows:
        if int(row.get("sequence", 10**9)) >= seq:
            continue
        for item in row.get("new_lexical_targets", []):
            if isinstance(item, dict) and str(item.get("id")) == target_id:
                matches.append((row, item))
    if len(matches) != 1:
        raise AssertionError(f"{pid}: expected exactly one prior introduction for {target_id}, got {len(matches)}")
    row, item = matches[0]
    if str(item.get("form")) != form:
        raise AssertionError(f"{pid}: prior intro form drift for {target_id}: {item.get('form')!r} != {form!r}")
    return {"passage_id": row.get("id"), "sequence": row.get("sequence"), "form": item.get("form")}


def main() -> None:
    a1_path = ROOT / "reading/arabic/a1/passages.jsonl"
    b1_path = ROOT / "reading/arabic/b1/passages.jsonl"
    a1 = read_rows(a1_path)
    b1 = read_rows(b1_path)
    if len(a1) != 60 or len(b1) != 60:
        raise AssertionError(f"expected 60 A1 and 60 B1 passages, got A1={len(a1)} B1={len(b1)}")

    a1_before = copy.deepcopy(a1)
    b1_before = copy.deepcopy(b1)
    a1_by_id = {str(r.get("id")): r for r in a1}
    b1_by_id = {str(r.get("id")): r for r in b1}

    prior_evidence = {}
    for pid, spec in A1_REVIEW_ADDITIONS.items():
        row = a1_by_id.get(pid)
        if row is None:
            raise AssertionError(f"missing {pid}")
        if int(row.get("sequence")) != spec["expected_sequence"]:
            raise AssertionError(f"{pid}: sequence drift {row.get('sequence')} != {spec['expected_sequence']}")
        current_reviews = row.get("review_lexical_targets", [])
        if not isinstance(current_reviews, list):
            raise AssertionError(f"{pid}: review_lexical_targets is not a list")
        if any(isinstance(x, dict) and str(x.get("id")) == spec["id"] for x in current_reviews):
            raise AssertionError(f"{pid}: {spec['id']} is already declared as a review target")
        q_hits = [
            q for q in row.get("questions", [])
            if isinstance(q, dict) and spec["id"] in [str(x) for x in (q.get("target_ids", []) if isinstance(q.get("target_ids"), list) else [])]
        ]
        if not q_hits:
            raise AssertionError(f"{pid}: no question currently references {spec['id']}")
        prior_evidence[pid] = find_prior_intro(a1, pid, spec["id"], spec["form"])
        current_reviews.append({
            "form": spec["form"],
            "id": spec["id"],
            "representation": spec["representation"],
            "review_stage": spec["review_stage"],
        })

    changed_b1: dict[str, set[str]] = {}
    for (pid, qid), spec in B1_TARGET_FIXES.items():
        row = b1_by_id.get(pid)
        if row is None:
            raise AssertionError(f"missing {pid}")
        q = question_map(row).get(qid)
        if q is None:
            raise AssertionError(f"{pid}: missing {qid}")
        if q.get("prompt") != spec["prompt"]:
            raise AssertionError(f"{pid} {qid}: prompt drift: {q.get('prompt')!r}")
        current = [str(x) for x in (q.get("target_ids", []) if isinstance(q.get("target_ids"), list) else [])]
        if current != spec["old"]:
            raise AssertionError(f"{pid} {qid}: target-id drift {current} != {spec['old']}")
        local_declared = declared_ids(row)
        if spec["new"][0] not in local_declared:
            raise AssertionError(f"{pid} {qid}: corrected target {spec['new'][0]} is not locally declared")
        local_items = [
            item for field in ("new_lexical_targets", "review_lexical_targets")
            for item in row.get(field, [])
            if isinstance(item, dict) and str(item.get("id")) == spec["new"][0]
        ]
        if len(local_items) != 1 or str(local_items[0].get("form")) != spec["form"]:
            raise AssertionError(f"{pid} {qid}: corrected target/form declaration mismatch: {local_items}")
        q["target_ids"] = list(spec["new"])
        changed_b1.setdefault(pid, set()).add(qid)

    a1_before_by_id = {str(r.get("id")): r for r in a1_before}
    for pid, new in a1_by_id.items():
        old = a1_before_by_id[pid]
        if pid in A1_REVIEW_ADDITIONS:
            if projection(old, remove_review=True) != projection(new, remove_review=True):
                raise AssertionError(f"{pid}: mutation outside review_lexical_targets")
            if len(new.get("review_lexical_targets", [])) != len(old.get("review_lexical_targets", [])) + 1:
                raise AssertionError(f"{pid}: expected exactly one review-target append")
        elif old != new:
            raise AssertionError(f"{pid}: unselected A1 record changed")

    b1_before_by_id = {str(r.get("id")): r for r in b1_before}
    for pid, new in b1_by_id.items():
        old = b1_before_by_id[pid]
        if pid in changed_b1:
            if projection(old, changed_qids=changed_b1[pid]) != projection(new, changed_qids=changed_b1[pid]):
                raise AssertionError(f"{pid}: mutation outside selected question target_ids")
        elif old != new:
            raise AssertionError(f"{pid}: unselected B1 record changed")

    write_rows(a1_path, a1)
    write_rows(b1_path, b1)
    print(json.dumps({
        "a1_review_declarations_added": len(A1_REVIEW_ADDITIONS),
        "b1_question_target_ids_corrected": len(B1_TARGET_FIXES),
        "prior_introduction_evidence": prior_evidence,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

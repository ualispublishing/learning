#!/usr/bin/env python3
"""Final Arabic review pass 02: lexical target/exposure integrity.

Checks bookkeeping and chronology of deliberate *new* lexical targets. Review
items that were not previously introduced inside the reader are diagnostics,
not failures, because they may be prerequisite/core vocabulary learned outside
the reader. This pass does not judge sense, register, or CEFR placement.
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEVELS = ("a1", "a2", "b1", "b2", "c1", "c2")
OUT = ROOT / "reading/audit/final_arabic_pass02_lexical_exposure_integrity.json"
DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
NONWORD = re.compile(r"[^\u0621-\u064A\u0660-\u0669A-Za-z0-9]+")


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").replace("ـ", "")
    value = DIACRITICS.sub("", value)
    value = value.replace("ٱ", "ا")
    value = NONWORD.sub(" ", value)
    return " ".join(value.split())


def occurrences(text: str, form: str) -> int:
    t = f" {norm(text)} "
    f = norm(form)
    if not f:
        return 0
    return t.count(f" {f} ")


def load_rows() -> list[tuple[int, int, dict]]:
    rows: list[tuple[int, int, dict]] = []
    for li, level in enumerate(LEVELS):
        path = ROOT / f"reading/arabic/{level}/passages.jsonl"
        for raw in path.read_text(encoding="utf-8").splitlines():
            if raw.strip():
                row = json.loads(raw)
                rows.append((li, int(row.get("sequence", 0) or 0), row))
    rows.sort(key=lambda x: (x[0], x[1], x[2].get("id", "")))
    return rows


def add(bucket: list[dict], code: str, **data) -> None:
    bucket.append({"code": code, **data})


def main() -> None:
    rows = load_rows()
    hard: list[dict] = []
    warnings: list[dict] = []
    introduced_at: dict[str, str] = {}
    introduced_forms: defaultdict[str, list[dict]] = defaultdict(list)
    level_summary = {
        level: {
            "new_targets": 0,
            "review_targets": 0,
            "p6_new_targets": 0,
            "zero_exact_exposure_warnings": 0,
            "review_targets_without_prior_reader_introduction": 0,
        }
        for level in LEVELS
    }

    for li, seq, row in rows:
        level = str(row.get("cefr", "")).lower()
        pid = row.get("id")
        pnum_match = re.search(r"-p(\d{2})$", str(pid))
        pnum = int(pnum_match.group(1)) if pnum_match else None
        text = row.get("text", "")
        new_targets = row.get("new_lexical_targets", []) if isinstance(row.get("new_lexical_targets"), list) else []
        review_targets = row.get("review_lexical_targets", []) if isinstance(row.get("review_lexical_targets"), list) else []
        level_summary.setdefault(level, {
            "new_targets": 0,
            "review_targets": 0,
            "p6_new_targets": 0,
            "zero_exact_exposure_warnings": 0,
            "review_targets_without_prior_reader_introduction": 0,
        })
        level_summary[level]["new_targets"] += len(new_targets)
        level_summary[level]["review_targets"] += len(review_targets)
        if pnum == 6:
            level_summary[level]["p6_new_targets"] += len(new_targets)
            if new_targets:
                add(warnings, "checkpoint_has_new_targets", passage_id=pid, target_ids=[t.get("id") for t in new_targets if isinstance(t, dict)])

        local_ids: set[str] = set()
        for target in new_targets:
            if not isinstance(target, dict):
                add(hard, "new_target_not_object", passage_id=pid, value=repr(target))
                continue
            tid = target.get("id")
            form = target.get("form") or target.get("lemma") or ""
            if not tid:
                add(hard, "new_target_missing_id", passage_id=pid, form=form)
                continue
            if tid in local_ids:
                add(hard, "duplicate_new_target_id_within_passage", passage_id=pid, target_id=tid)
            local_ids.add(tid)
            if tid in introduced_at:
                add(hard, "target_reintroduced_as_new", passage_id=pid, target_id=tid, first_passage=introduced_at[tid])
            else:
                introduced_at[tid] = pid
            nf = norm(str(form))
            if nf:
                introduced_forms[nf].append({"target_id": tid, "passage_id": pid, "level": level, "form": form})
            exact = occurrences(text, str(form))
            declared = target.get("exposures_in_text")
            if exact == 0:
                level_summary[level]["zero_exact_exposure_warnings"] += 1
                add(warnings, "new_target_form_not_exactly_found_in_text", passage_id=pid, target_id=tid, form=form, declared_exposures=declared)
            elif isinstance(declared, int) and declared != exact:
                add(warnings, "declared_exposure_count_differs_from_exact_surface_count", passage_id=pid, target_id=tid, form=form, declared=declared, exact_surface_count=exact)

        for target in review_targets:
            if not isinstance(target, dict):
                add(hard, "review_target_not_object", passage_id=pid, value=repr(target))
                continue
            tid = target.get("id")
            if not tid:
                add(hard, "review_target_missing_id", passage_id=pid, form=target.get("form"))
                continue
            if tid not in introduced_at:
                level_summary[level]["review_targets_without_prior_reader_introduction"] += 1
                add(
                    warnings,
                    "review_target_without_prior_reader_introduction",
                    passage_id=pid,
                    target_id=tid,
                    form=target.get("form"),
                    interpretation="may be legitimate prerequisite/core vocabulary; verify against curriculum/ledger rather than treating as an automatic defect",
                )

        passage_target_ids = {
            t.get("id")
            for t in [*new_targets, *review_targets]
            if isinstance(t, dict) and t.get("id")
        }
        for q in row.get("questions", []) if isinstance(row.get("questions"), list) else []:
            if not isinstance(q, dict):
                continue
            tids = q.get("target_ids", []) if isinstance(q.get("target_ids"), list) else []
            for tid in tids:
                if tid not in passage_target_ids:
                    add(warnings, "question_target_not_declared_in_passage_targets", passage_id=pid, question_id=q.get("id"), target_id=tid)

    repeated_forms = {form: entries for form, entries in introduced_forms.items() if len(entries) > 1}
    for form, entries in sorted(repeated_forms.items()):
        add(
            warnings,
            "normalized_surface_introduced_under_multiple_target_ids",
            normalized_form=form,
            introductions=entries,
            interpretation="may be legitimate homography/POS/sense distinction; send to lexical-sense pass",
        )

    payload = {
        "pass": 2,
        "name": "lexical_target_exposure_integrity",
        "scope": "Arabic A1-C2 canonical reading corpus",
        "method": "new-target ID chronology, exact-surface exposure diagnostics, checkpoint diagnostics, question target linkage, and prerequisite/core review diagnostics",
        "not_claimed": [
            "lexical sense correctness",
            "register correctness",
            "CEFR placement",
            "morphological equivalence when exact surface differs",
            "whether a review target was learned outside the reader",
            "learner mastery",
        ],
        "levels": level_summary,
        "totals": {
            "passages": len(rows),
            "unique_introduced_target_ids": len(introduced_at),
            "hard_issues": len(hard),
            "warnings": len(warnings),
            "normalized_surfaces_with_multiple_target_ids": len(repeated_forms),
        },
        "hard_issues": hard,
        "warnings": warnings,
        "status": "PASS" if not hard else "FAIL",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["totals"], ensure_ascii=False))
    print("status=" + payload["status"])
    if hard:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

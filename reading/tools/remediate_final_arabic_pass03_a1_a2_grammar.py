#!/usr/bin/env python3
"""Guarded remediation of genuine A1/A2 Pass 03 grammar/form deficits.

For each currently grammar-light A1/A2 passage, repurpose exactly one redundant
single-word-definition item as a genuine grammatical-category question. The
lexical target must still be assessed by another lexical item in the same set,
and its stored POS metadata must support an unambiguous Arabic answer.

Passage prose, lexical scheduling metadata, question IDs, target IDs and all
unselected questions are preserved. Fail closed on any unexpected schema or
pedagogical drift.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEVELS = ("a1", "a2")
LEXICAL_TYPES = {"vocabulary_in_context", "single_word_definition", "cloze_transfer", "register_style"}
GRAMMAR_TYPES = {"grammar_in_context", "grammar_category", "grammar_choice", "grammar_identification", "grammar_function", "person_form", "contrast", "register_style"}
MIN_GRAMMAR = 2
MIN_LEXICAL = 2


def lexical_role(q: dict) -> bool:
    t = str(q.get("type", ""))
    if t in LEXICAL_TYPES:
        return True
    tids = q.get("target_ids", []) if isinstance(q.get("target_ids"), list) else []
    return t == "contrast" and any(str(tid).startswith("ar-r") for tid in tids)


def pos_answer(raw: object) -> str | None:
    """Map only high-confidence POS metadata to an Arabic category answer."""
    if not isinstance(raw, str) or not raw.strip():
        return None
    p = raw.strip().lower()
    # Reject explicitly mixed alternatives; another candidate may be available.
    if " / " in p or " or " in p:
        return None
    if "elative" in p or "comparative-superlative" in p:
        return "اسم تفضيل"
    if "interrogative" in p:
        return "أداة استفهام"
    if "relative pronoun" in p:
        return "اسم موصول"
    if "demonstrative" in p:
        return "اسم إشارة"
    if "preposition" in p:
        return "حرف جر"
    if "conjunction" in p or "coordinator" in p:
        return "حرف عطف"
    if "pronoun" in p:
        return "ضمير"
    if "place adverb" in p:
        return "ظرف مكان"
    if "time adverb" in p or "temporal adverb" in p:
        return "ظرف زمان"
    if "adverb" in p:
        return "ظرف"
    if "imperfect" in p or "present verb" in p:
        return "فعل مضارع"
    if "perfect verb" in p or "past verb" in p:
        return "فعل ماضٍ"
    if "imperative" in p:
        return "فعل أمر"
    if "verb" in p:
        return "فعل"
    if "adjective" in p:
        return "صفة"
    if "numeral" in p or p == "number":
        return "عدد"
    if "particle" in p:
        return "أداة"
    if p == "noun" or p.startswith("noun ("):
        return "اسم"
    return None


def read_rows(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def write_rows(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), encoding="utf-8")


def answer_entry(row: dict, qid: str) -> dict:
    hits = [a for a in row.get("answer_key", []) if isinstance(a, dict) and a.get("question_id") == qid]
    if len(hits) != 1:
        raise AssertionError(f"{row.get('id')}: expected one answer entry for {qid}, got {len(hits)}")
    return hits[0]


def immutable_projection(row: dict, changed_qid: str) -> dict:
    """Projection that removes only fields this remediation may change."""
    x = copy.deepcopy(row)
    for q in x.get("questions", []):
        if q.get("id") == changed_qid:
            q.pop("type", None)
            q.pop("prompt", None)
    for a in x.get("answer_key", []):
        if a.get("question_id") == changed_qid:
            a.pop("answer", None)
    quality = x.get("quality")
    if isinstance(quality, dict):
        quality.pop("notes", None)
    return x


def main() -> None:
    changed_total = 0
    by_level = {}
    for level in LEVELS:
        path = ROOT / f"reading/arabic/{level}/passages.jsonl"
        rows = read_rows(path)
        if len(rows) != 60:
            raise AssertionError(f"{level}: expected 60 passages, got {len(rows)}")
        before = copy.deepcopy(rows)
        changed_ids: dict[str, str] = {}

        for row in rows:
            qs = row.get("questions", [])
            if len(qs) != 10 or len(row.get("answer_key", [])) != 10:
                raise AssertionError(f"{row.get('id')}: expected 10 questions and 10 answers")
            grammar_before = sum(str(q.get("type", "")) in GRAMMAR_TYPES for q in qs)
            if grammar_before >= MIN_GRAMMAR:
                continue
            if grammar_before != 1:
                raise AssertionError(f"{row.get('id')}: unexpected grammar count {grammar_before}")
            lexical_before = sum(lexical_role(q) for q in qs)
            if lexical_before < 3:
                raise AssertionError(f"{row.get('id')}: only {lexical_before} lexical-role items; cannot safely repurpose one")

            meta = {}
            for item in row.get("new_lexical_targets", []) + row.get("review_lexical_targets", []):
                if isinstance(item, dict) and item.get("id"):
                    meta[str(item["id"])] = item

            candidates = []
            for q in qs:
                if q.get("type") != "single_word_definition":
                    continue
                tids = q.get("target_ids", []) if isinstance(q.get("target_ids"), list) else []
                if len(tids) != 1:
                    continue
                tid = str(tids[0])
                other_lexical = [other for other in qs if other.get("id") != q.get("id") and lexical_role(other) and tid in [str(x) for x in (other.get("target_ids", []) if isinstance(other.get("target_ids"), list) else [])]]
                if not other_lexical:
                    continue
                item = meta.get(tid, {})
                answer = pos_answer(item.get("part_of_speech"))
                form = item.get("form") or item.get("lemma")
                if answer and isinstance(form, str) and form.strip():
                    candidates.append((q, tid, form.strip(), answer))

            if not candidates:
                all_defs = [(q.get("id"), q.get("target_ids")) for q in qs if q.get("type") == "single_word_definition"]
                raise AssertionError(f"{row.get('id')}: no unambiguous redundant definition candidate; definitions={all_defs}")

            q, tid, form, category_answer = candidates[0]
            qid = str(q.get("id"))
            old_answer = copy.deepcopy(answer_entry(row, qid))
            q["type"] = "grammar_category"
            q["prompt"] = f"ما التصنيف النحوي لكلمة «{form}» في هذا الاستعمال؟"
            ans = answer_entry(row, qid)
            ans["answer"] = category_answer
            # Preserve linkage and all other answer metadata.
            if {k: v for k, v in ans.items() if k != "answer"} != {k: v for k, v in old_answer.items() if k != "answer"}:
                raise AssertionError(f"{row.get('id')} {qid}: answer metadata drift")

            grammar_after = sum(str(x.get("type", "")) in GRAMMAR_TYPES for x in qs)
            lexical_after = sum(lexical_role(x) for x in qs)
            if grammar_after < MIN_GRAMMAR or lexical_after < MIN_LEXICAL:
                raise AssertionError(f"{row.get('id')}: postcondition roles grammar={grammar_after}, lexical={lexical_after}")

            note = f"Final Pass 03 remediation: {qid} repurposed from redundant lexical definition to grammatical-category retrieval for {tid}; another lexical item still tests the target."
            notes = row.setdefault("quality", {}).setdefault("notes", [])
            if note not in notes:
                notes.append(note)
            changed_ids[str(row.get("id"))] = qid
            changed_total += 1

        # Guard every changed and unchanged row against unintended mutation.
        for old, new in zip(before, rows):
            pid = str(old.get("id"))
            if old.get("id") != new.get("id"):
                raise AssertionError("row identity/order drift")
            if pid in changed_ids:
                qid = changed_ids[pid]
                if immutable_projection(old, qid) != immutable_projection(new, qid):
                    raise AssertionError(f"{pid}: mutation outside approved question/answer fields")
                if old.get("text") != new.get("text"):
                    raise AssertionError(f"{pid}: passage prose changed")
                if old.get("new_lexical_targets") != new.get("new_lexical_targets") or old.get("review_lexical_targets") != new.get("review_lexical_targets"):
                    raise AssertionError(f"{pid}: lexical schedule changed")
            elif old != new:
                raise AssertionError(f"{pid}: unselected passage changed")

        write_rows(path, rows)
        by_level[level] = len(changed_ids)

    if by_level != {"a1": 39, "a2": 42} or changed_total != 81:
        raise AssertionError(f"expected A1=39, A2=42, total=81; got {by_level}, total={changed_total}")
    print(json.dumps({"changed": changed_total, "by_level": by_level}, ensure_ascii=False))


if __name__ == "__main__":
    main()

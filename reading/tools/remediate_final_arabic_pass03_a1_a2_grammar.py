#!/usr/bin/env python3
"""Guarded remediation of genuine A1/A2 Pass 03 grammar/form deficits.

For each currently grammar-light A1/A2 passage, repurpose the minimum number of
redundant single-word-definition items needed to reach two genuine grammar/form
questions. Every converted lexical target must remain assessed by another
unconverted lexical item in the same set, and its POS metadata must support an
unambiguous Arabic category answer.

Passage prose, lexical scheduling metadata, question IDs, target IDs and all
unselected questions are preserved. Fail closed on any unexpected schema or
pedagogical drift.
"""
from __future__ import annotations

import copy
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEVELS = ("a1", "a2")
LEXICAL_TYPES = {"vocabulary_in_context", "single_word_definition", "cloze_transfer", "register_style"}
GRAMMAR_TYPES = {"grammar_in_context", "grammar_category", "grammar_choice", "grammar_identification", "grammar_function", "person_form", "contrast", "register_style"}
MIN_GRAMMAR = 2
MIN_LEXICAL = 2

# Explicit contextual adjudications for lexicon entries whose global POS field
# allows more than one use but whose role in this exact canonical passage is
# unambiguous. Never generalize these answers to the same lemma elsewhere.
USAGE_POS_OVERRIDES = {
    ("ar-a2-u05-p04", "q6"): "اسم",  # عادة in «عادة أصغر» / «العادة الجيدة»
}


def lexical_role(q: dict) -> bool:
    t = str(q.get("type", ""))
    if t in LEXICAL_TYPES:
        return True
    tids = q.get("target_ids", []) if isinstance(q.get("target_ids"), list) else []
    return t == "contrast" and any(str(tid).startswith("ar-r") for tid in tids)


def q_target_ids(q: dict) -> list[str]:
    raw = q.get("target_ids", [])
    return [str(x) for x in raw] if isinstance(raw, list) else []


def pos_answer(raw: object) -> str | None:
    """Map only high-confidence POS metadata to an Arabic category answer."""
    if not isinstance(raw, str) or not raw.strip():
        return None
    p = raw.strip().lower()

    if "elative" in p or "comparative-superlative" in p:
        return "اسم تفضيل"
    if "imperfect" in p or "present verb" in p:
        return "فعل مضارع"
    if "perfect verb" in p or "past verb" in p:
        return "فعل ماضٍ"

    if " / " in p or " or " in p:
        return None
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


def immutable_projection(row: dict, changed_qids: set[str]) -> dict:
    """Projection that removes only fields this remediation may change."""
    x = copy.deepcopy(row)
    for q in x.get("questions", []):
        if str(q.get("id")) in changed_qids:
            q.pop("type", None)
            q.pop("prompt", None)
    for a in x.get("answer_key", []):
        if str(a.get("question_id")) in changed_qids:
            a.pop("answer", None)
    quality = x.get("quality")
    if isinstance(quality, dict):
        quality.pop("notes", None)
    return x


def candidate_inventory(pid: str, qs: list[dict], meta: dict[str, dict]) -> list[dict]:
    candidates: list[dict] = []
    for q in qs:
        if q.get("type") != "single_word_definition":
            continue
        qid = str(q.get("id"))
        tids = q_target_ids(q)
        if len(tids) != 1:
            continue
        tid = tids[0]
        item = meta.get(tid, {})
        answer = USAGE_POS_OVERRIDES.get((pid, qid)) or pos_answer(item.get("part_of_speech"))
        form = item.get("form") or item.get("lemma")
        if not answer or not isinstance(form, str) or not form.strip():
            continue
        support_ids = [
            str(other.get("id"))
            for other in qs
            if other.get("id") != q.get("id") and lexical_role(other) and tid in q_target_ids(other)
        ]
        if support_ids:
            candidates.append({
                "q": q,
                "qid": qid,
                "tid": tid,
                "form": form.strip(),
                "answer": answer,
                "support_ids": support_ids,
                "part_of_speech": item.get("part_of_speech"),
                "contextual_override": (pid, qid) in USAGE_POS_OVERRIDES,
            })
    return candidates


def choose_candidates(qs: list[dict], candidates: list[dict], needed: int) -> list[dict] | None:
    """Choose a conversion set whose lexical supports remain after conversion."""
    lexical_before = sum(lexical_role(q) for q in qs)
    for combo in itertools.combinations(candidates, needed):
        selected_ids = {c["qid"] for c in combo}
        if lexical_before - needed < MIN_LEXICAL:
            continue
        if any(not any(sid not in selected_ids for sid in c["support_ids"]) for c in combo):
            continue
        return list(combo)
    return None


def main() -> None:
    changed_passages = 0
    changed_questions = 0
    by_level: dict[str, dict[str, int]] = {}

    for level in LEVELS:
        path = ROOT / f"reading/arabic/{level}/passages.jsonl"
        rows = read_rows(path)
        if len(rows) != 60:
            raise AssertionError(f"{level}: expected 60 passages, got {len(rows)}")
        before = copy.deepcopy(rows)
        changed_ids: dict[str, set[str]] = {}
        level_passages = 0
        level_questions = 0

        for row in rows:
            pid = str(row.get("id"))
            qs = row.get("questions", [])
            if len(qs) != 10 or len(row.get("answer_key", [])) != 10:
                raise AssertionError(f"{pid}: expected 10 questions and 10 answers")

            grammar_before = sum(str(q.get("type", "")) in GRAMMAR_TYPES for q in qs)
            if grammar_before >= MIN_GRAMMAR:
                continue
            if grammar_before < 0 or grammar_before > 1:
                raise AssertionError(f"{pid}: unexpected grammar count {grammar_before}")
            needed = MIN_GRAMMAR - grammar_before
            lexical_before = sum(lexical_role(q) for q in qs)
            if lexical_before - needed < MIN_LEXICAL:
                raise AssertionError(
                    f"{pid}: grammar={grammar_before}, lexical={lexical_before}, "
                    f"need {needed} conversions but would fall below lexical minimum {MIN_LEXICAL}"
                )

            meta: dict[str, dict] = {}
            for item in row.get("new_lexical_targets", []) + row.get("review_lexical_targets", []):
                if isinstance(item, dict) and item.get("id"):
                    meta[str(item["id"])] = item

            candidates = candidate_inventory(pid, qs, meta)
            selected = choose_candidates(qs, candidates, needed)
            if selected is None:
                definitions = []
                for q in qs:
                    if q.get("type") != "single_word_definition":
                        continue
                    qid = str(q.get("id"))
                    tids = q_target_ids(q)
                    item = meta.get(tids[0], {}) if len(tids) == 1 else {}
                    definitions.append({
                        "question_id": qid,
                        "target_ids": tids,
                        "part_of_speech": item.get("part_of_speech"),
                        "mapped_answer": USAGE_POS_OVERRIDES.get((pid, qid)) or pos_answer(item.get("part_of_speech")),
                        "support_ids": [
                            str(other.get("id")) for other in qs
                            if other.get("id") != q.get("id") and lexical_role(other)
                            and len(tids) == 1 and tids[0] in q_target_ids(other)
                        ],
                    })
                raise AssertionError(
                    f"{pid}: cannot safely choose {needed} grammar conversions; "
                    f"grammar={grammar_before}, lexical={lexical_before}, definitions={definitions}"
                )

            selected_ids = {c["qid"] for c in selected}
            for c in selected:
                q = c["q"]
                qid = c["qid"]
                old_answer = copy.deepcopy(answer_entry(row, qid))
                q["type"] = "grammar_category"
                q["prompt"] = f"ما التصنيف النحوي لكلمة «{c['form']}» في هذا الاستعمال؟"
                ans = answer_entry(row, qid)
                ans["answer"] = c["answer"]
                if {k: v for k, v in ans.items() if k != "answer"} != {k: v for k, v in old_answer.items() if k != "answer"}:
                    raise AssertionError(f"{pid} {qid}: answer metadata drift")

                note = (
                    f"Final Pass 03 remediation: {qid} repurposed from redundant lexical definition "
                    f"to grammatical-category retrieval for {c['tid']}; another lexical item still tests the target."
                )
                if c["contextual_override"]:
                    note += " POS answer adjudicated from this passage's explicit syntactic use."
                notes = row.setdefault("quality", {}).setdefault("notes", [])
                if note not in notes:
                    notes.append(note)

            grammar_after = sum(str(q.get("type", "")) in GRAMMAR_TYPES for q in qs)
            lexical_after = sum(lexical_role(q) for q in qs)
            if grammar_after < MIN_GRAMMAR or lexical_after < MIN_LEXICAL:
                raise AssertionError(f"{pid}: postcondition roles grammar={grammar_after}, lexical={lexical_after}")
            for c in selected:
                if not any(
                    str(other.get("id")) not in selected_ids
                    and lexical_role(other)
                    and c["tid"] in q_target_ids(other)
                    for other in qs
                ):
                    raise AssertionError(f"{pid} {c['qid']}: converted target lost independent lexical assessment")

            changed_ids[pid] = selected_ids
            changed_passages += 1
            changed_questions += len(selected)
            level_passages += 1
            level_questions += len(selected)

        for old, new in zip(before, rows):
            pid = str(old.get("id"))
            if old.get("id") != new.get("id"):
                raise AssertionError("row identity/order drift")
            if pid in changed_ids:
                qids = changed_ids[pid]
                if immutable_projection(old, qids) != immutable_projection(new, qids):
                    raise AssertionError(f"{pid}: mutation outside approved question/answer fields")
                if old.get("text") != new.get("text"):
                    raise AssertionError(f"{pid}: passage prose changed")
                if old.get("new_lexical_targets") != new.get("new_lexical_targets") or old.get("review_lexical_targets") != new.get("review_lexical_targets"):
                    raise AssertionError(f"{pid}: lexical schedule changed")
            elif old != new:
                raise AssertionError(f"{pid}: unselected passage changed")

        write_rows(path, rows)
        by_level[level] = {"passages": level_passages, "questions": level_questions}

    expected_passages = {"a1": 39, "a2": 42}
    actual_passages = {level: stats["passages"] for level, stats in by_level.items()}
    if actual_passages != expected_passages or changed_passages != 81:
        raise AssertionError(
            f"expected grammar-deficit passages A1=39/A2=42/total=81; "
            f"got {by_level}, total_passages={changed_passages}"
        )
    if changed_questions < changed_passages:
        raise AssertionError("question-change count cannot be smaller than changed passage count")

    print(json.dumps({
        "changed_passages": changed_passages,
        "changed_questions": changed_questions,
        "by_level": by_level,
        "contextual_pos_overrides": len(USAGE_POS_OVERRIDES),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

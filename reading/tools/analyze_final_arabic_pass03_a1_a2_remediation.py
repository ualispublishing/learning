#!/usr/bin/env python3
"""Build a compact, fail-closed remediation map for remaining A1/A2 Pass 03 debt.

This tool does not change canonical passages. It identifies whether a grammar-
light passage contains a redundant lexical-definition question that can safely
be repurposed as a form/category task while the same target remains tested by a
separate lexical item. It also inventories zero/new-target context for passages
with lexical shortfalls so those are handled explicitly rather than by relabeling.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reading/audit/final_arabic_pass03_a1_a2_remediation_map.json"
LEVELS = ("a1", "a2")

COMPREHENSION = {"gist", "literal_detail", "sequence", "cause_effect", "reference_resolution", "main_claim"}
INFERENCE = {"inference", "motive", "stance", "assumption", "ambiguity_resolution", "argument_relation"}
LEXICAL = {"vocabulary_in_context", "single_word_definition", "cloze_transfer", "register_style"}
GRAMMAR_STYLE = {"grammar_in_context", "grammar_category", "grammar_choice", "grammar_identification", "grammar_function", "person_form", "contrast", "register_style"}
DISCOURSE = {"main_claim", "argument_relation", "stance", "tone", "rhetorical_function", "assumption", "ambiguity_resolution", "reference_resolution", "register_style", "grammar_function", "contrast"}
SYNTHESIS = {"paraphrase", "summary", "synthesis", "cross_text_synthesis"}
PASSAGE_CENTERED = COMPREHENSION | INFERENCE | DISCOURSE | SYNTHESIS | {"vocabulary_in_context"}
MINIMA = {
    "a1": {"passage_centered": 3, "lexical": 2, "grammar_style": 2},
    "a2": {"passage_centered": 4, "lexical": 2, "grammar_style": 2},
}


def counts(types: list[str]) -> dict[str, int]:
    return {
        "passage_centered": sum(t in PASSAGE_CENTERED for t in types),
        "lexical": sum(t in LEXICAL for t in types),
        "grammar_style": sum(t in GRAMMAR_STYLE for t in types),
    }


def main() -> None:
    result = {"scope": "remaining A1/A2 Pass 03 remediation planning", "levels": {}, "totals": {}}
    totals = Counter()
    for level in LEVELS:
        path = ROOT / f"reading/arabic/{level}/passages.jsonl"
        rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        if len(rows) != 60:
            raise AssertionError(f"{level}: expected 60 passages, got {len(rows)}")
        flagged = []
        for row in rows:
            qs = row.get("questions", [])
            if len(qs) != 10 or len(row.get("answer_key", [])) != 10:
                raise AssertionError(f"{row.get('id')}: expected 10 questions/answers")
            types = [str(q.get("type", "")) for q in qs]
            c = counts(types)
            deficits = {k: {"minimum": v, "actual": c[k]} for k, v in MINIMA[level].items() if c[k] < v}
            if not deficits:
                continue

            target_meta = {}
            for item in row.get("new_lexical_targets", []) + row.get("review_lexical_targets", []):
                if isinstance(item, dict) and item.get("id"):
                    target_meta[item["id"]] = item

            lexical_occurrences = defaultdict(list)
            for q in qs:
                if q.get("type") in LEXICAL:
                    for tid in q.get("target_ids", []) if isinstance(q.get("target_ids"), list) else []:
                        lexical_occurrences[tid].append(q.get("id"))

            grammar_candidates = []
            if "grammar_style" in deficits:
                for q in qs:
                    if q.get("type") != "single_word_definition":
                        continue
                    tids = q.get("target_ids", []) if isinstance(q.get("target_ids"), list) else []
                    if len(tids) != 1:
                        continue
                    tid = tids[0]
                    other_lexical = [qid for qid in lexical_occurrences.get(tid, []) if qid != q.get("id")]
                    if not other_lexical:
                        continue
                    meta = target_meta.get(tid, {})
                    grammar_candidates.append({
                        "question_id": q.get("id"),
                        "target_id": tid,
                        "form": meta.get("form") or meta.get("lemma"),
                        "part_of_speech": meta.get("part_of_speech"),
                        "other_lexical_question_ids": other_lexical,
                        "old_prompt": q.get("prompt"),
                    })

            lexical_context = None
            if "lexical" in deficits:
                lexical_context = {
                    "passage_type": row.get("passage_type"),
                    "new_word_policy": row.get("speed_training", {}).get("new_word_policy") if isinstance(row.get("speed_training"), dict) else None,
                    "new_targets": [{"id": x.get("id"), "form": x.get("form"), "part_of_speech": x.get("part_of_speech")} for x in row.get("new_lexical_targets", []) if isinstance(x, dict)],
                    "review_targets": [{"id": x.get("id"), "form": x.get("form"), "review_stage": x.get("review_stage")} for x in row.get("review_lexical_targets", []) if isinstance(x, dict)],
                    "questions": [{"id": q.get("id"), "type": q.get("type"), "target_ids": q.get("target_ids", []), "prompt": q.get("prompt")} for q in qs],
                }

            flagged.append({
                "id": row.get("id"),
                "unit": row.get("unit"),
                "sequence": row.get("sequence"),
                "deficits": deficits,
                "question_types": types,
                "grammar_candidates": grammar_candidates,
                "lexical_context": lexical_context,
            })
            totals["flagged_passages"] += 1
            for d in deficits:
                totals[d + "_deficits"] += 1
            if "grammar_style" in deficits:
                if grammar_candidates:
                    totals["grammar_deficits_with_safe_definition_candidate"] += 1
                else:
                    totals["grammar_deficits_without_candidate"] += 1

        result["levels"][level] = {
            "flagged_passages": len(flagged),
            "items": flagged,
        }
    result["totals"] = dict(totals)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["totals"], ensure_ascii=False))


if __name__ == "__main__":
    main()

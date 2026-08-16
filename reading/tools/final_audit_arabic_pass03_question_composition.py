#!/usr/bin/env python3
"""Final Arabic review pass 03: pedagogical question-composition diagnostic.

Compares question-role mixes with the documented Ten-Question Standard. The
standard describes default distributions, so deviations are REVIEW flags rather
than automatic failures. A single well-designed question may legitimately serve
more than one pedagogical role (for example, a connective-function question is
both grammar/style and discourse analysis). This pass does not judge individual
answer correctness; that is handled separately by Pass 04.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEVELS = ("a1", "a2", "b1", "b2", "c1", "c2")
OUT = ROOT / "reading/audit/final_arabic_pass03_question_composition.json"

COMPREHENSION = {"gist", "literal_detail", "sequence", "cause_effect", "reference_resolution", "main_claim"}
INFERENCE = {"inference", "motive", "stance", "assumption", "ambiguity_resolution", "argument_relation"}
LEXICAL = {"vocabulary_in_context", "single_word_definition", "cloze_transfer", "register_style"}
GRAMMAR_STYLE = {"grammar_in_context", "grammar_category", "grammar_choice", "grammar_identification", "grammar_function", "person_form", "contrast", "register_style"}
# Multi-role classification is intentional. Questions about the function of a
# connective or an explicit contrast can test grammar/form while also testing
# cohesion, discourse relation, or rhetorical organization. Excluding those
# labels from discourse produced false deficits in otherwise valid B2-C2 sets.
DISCOURSE = {
    "main_claim", "argument_relation", "stance", "tone", "rhetorical_function",
    "assumption", "ambiguity_resolution", "reference_resolution", "register_style",
    "grammar_function", "contrast",
}
SYNTHESIS = {"paraphrase", "summary", "synthesis", "cross_text_synthesis"}
# vocabulary_in_context is passage-linked by schema/standard definition and is
# therefore passage-centred as well as lexical. Generic single-word definition
# and transfer cloze items remain outside this set.
PASSAGE_CENTERED = COMPREHENSION | INFERENCE | DISCOURSE | SYNTHESIS | {"vocabulary_in_context"}

# Broad minima derived from the documented default distributions. They are
# intentionally not exact quotas: Pass 03 flags pedagogically material gaps
# without rejecting legitimate alternate mixes.
MINIMA = {
    "a1": {"passage_centered": 3, "lexical": 2, "grammar_style": 2},
    "a2": {"passage_centered": 4, "lexical": 2, "grammar_style": 2},
    "b1": {"comprehension_inference": 4, "lexical": 2, "grammar_style": 2, "synthesis": 1},
    "b2": {"comprehension_inference": 2, "lexical": 2, "grammar_style": 2, "discourse": 2, "synthesis": 1},
    "c1": {"inference": 2, "lexical": 2, "grammar_style": 2, "discourse": 2, "synthesis": 2},
    "c2": {"inference": 2, "lexical": 2, "grammar_style": 2, "discourse": 2, "synthesis": 2},
}


def counts(types: list[str]) -> dict[str, int]:
    s = set(types)
    return {
        "passage_centered": sum(t in PASSAGE_CENTERED for t in types),
        "comprehension": sum(t in COMPREHENSION for t in types),
        "inference": sum(t in INFERENCE for t in types),
        "comprehension_inference": sum(t in (COMPREHENSION | INFERENCE) for t in types),
        "lexical": sum(t in LEXICAL for t in types),
        "grammar_style": sum(t in GRAMMAR_STYLE for t in types),
        "discourse": sum(t in DISCOURSE for t in types),
        "synthesis": sum(t in SYNTHESIS for t in types),
        "distinct_types": len(s),
    }


def main() -> None:
    flags: list[dict] = []
    level_summaries: dict[str, dict] = {}
    total_passages = 0

    for level in LEVELS:
        path = ROOT / f"reading/arabic/{level}/passages.jsonl"
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        total_passages += len(rows)
        type_counter = Counter()
        flagged_passages = 0
        deficiency_counter = Counter()
        low_diversity = 0
        lexical_quiz_heavy = 0

        for row in rows:
            qs = row.get("questions", [])
            types = [str(q.get("type", "")) for q in qs if isinstance(q, dict)]
            type_counter.update(types)
            c = counts(types)
            deficits = {
                category: {"minimum": minimum, "actual": c.get(category, 0)}
                for category, minimum in MINIMA[level].items()
                if c.get(category, 0) < minimum
            }
            if deficits:
                flagged_passages += 1
                deficiency_counter.update(deficits.keys())
                flags.append({
                    "code": "default_distribution_deficit",
                    "level": level,
                    "passage_id": row.get("id"),
                    "question_types": types,
                    "category_counts": c,
                    "deficits": deficits,
                })
            if c["distinct_types"] < 5:
                low_diversity += 1
                flags.append({
                    "code": "low_question_type_diversity",
                    "level": level,
                    "passage_id": row.get("id"),
                    "distinct_types": c["distinct_types"],
                    "question_types": types,
                })
            definition_count = sum(t == "single_word_definition" for t in types)
            if level in {"b2", "c1", "c2"} and definition_count > 2:
                lexical_quiz_heavy += 1
                flags.append({
                    "code": "advanced_passage_definition_heavy",
                    "level": level,
                    "passage_id": row.get("id"),
                    "single_word_definition_questions": definition_count,
                })

        level_summaries[level] = {
            "passages": len(rows),
            "flagged_for_default_distribution": flagged_passages,
            "low_type_diversity": low_diversity,
            "advanced_definition_heavy": lexical_quiz_heavy,
            "deficiency_categories": dict(deficiency_counter),
            "question_type_totals": dict(sorted(type_counter.items())),
        }

    payload = {
        "pass": 3,
        "name": "question_composition_against_ten_question_standard",
        "scope": "Arabic A1-C2 canonical reading corpus",
        "reference": "reading/planning/TEN_QUESTION_STANDARD.md",
        "interpretation": "diagnostic only: documented distributions are defaults; overlapping pedagogical roles are counted where the question type genuinely encodes both roles",
        "classification_notes": {
            "vocabulary_in_context": "counts as lexical and passage-centred",
            "grammar_function": "counts as grammar/style and discourse because it tests connective/structural function",
            "contrast": "counts as grammar/style and discourse because it tests an explicit contrast relation",
        },
        "levels": level_summaries,
        "totals": {"passages": total_passages, "review_flags": len(flags)},
        "flags": flags,
        "status": "PASS" if not flags else "REVIEW_REQUIRED",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["totals"], ensure_ascii=False))
    print("status=" + payload["status"])


if __name__ == "__main__":
    main()

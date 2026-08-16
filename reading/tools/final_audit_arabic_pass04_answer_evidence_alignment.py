#!/usr/bin/env python3
"""Final Arabic review pass 04: answer/evidence alignment diagnostics.

This pass is deliberately two-stage:
1. conservative heuristics identify review candidates;
2. classifier-safe benign cases are retained as non-blocking diagnostics while
   unresolved semantic/evidence candidates remain blocking.

A surface mismatch is never, by itself, a claim that an answer is wrong.
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEVELS = ("a1", "a2", "b1", "b2", "c1", "c2")
OUT = ROOT / "reading/audit/final_arabic_pass04_answer_evidence_alignment.json"
DIAC = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
ARWORD = re.compile(r"[\u0621-\u064A]+")
QUOTED = re.compile(r"«([^»]+)»")
STOP = {
    "في", "من", "إلى", "على", "عن", "مع", "أن", "إن", "ما", "ماذا", "لماذا",
    "كيف", "متى", "أين", "هو", "هي", "هم", "هن", "هذا", "هذه", "ذلك", "تلك",
    "التي", "الذي", "ثم", "أو", "و", "ف", "ب", "ل", "ك", "كان", "كانت", "يكون",
    "تكون", "قد", "لا", "لم", "لن", "كل", "بعد", "قبل",
}
DIRECT = {"literal_detail", "sequence", "reference_resolution", "cause_effect"}
LONG = {"gist", "summary", "synthesis", "cross_text_synthesis", "main_claim", "inference", "motive", "stance", "assumption", "argument_relation"}
GRAMMAR_CATEGORY_TYPES = {"grammar_category", "grammar_identification", "grammar_choice", "person_form"}
CONTRAST_EXPLANATION_MARKERS = {
    "الأول", "الأولى", "الثاني", "الثانية", "أما", "بينما", "لكن", "مقابل",
    "تعني", "يعني", "تصف", "يصف", "التعليق", "الإلغاء", "وصفي", "سببي",
}


def norm(s: object) -> str:
    s = unicodedata.normalize("NFKC", str(s or "")).replace("ـ", "").replace("ٱ", "ا")
    return DIAC.sub("", s)


def toks(s: object) -> list[str]:
    return [x for x in ARWORD.findall(norm(s)) if x not in STOP and len(x) > 1]


def add(items: list[dict], code: str, **kw: object) -> None:
    items.append({"code": code, **kw})


def contrast_is_explanatory(answer: str, quoted_options: list[str]) -> bool:
    na = norm(answer).strip(" .،؛:؟!")
    # Literal reuse is obviously aligned.
    if any(norm(option) in na for option in quoted_options):
        return True
    words = set(ARWORD.findall(na))
    # A sufficiently substantive answer with explicit contrast/explanation
    # structure is not suspicious merely because it paraphrases the options.
    return len(toks(answer)) >= 3 and bool(words & CONTRAST_EXPLANATION_MARKERS or na.startswith("لا"))


def main() -> None:
    unresolved: list[dict] = []
    benign: list[dict] = []
    level_summary: dict[str, dict] = {}
    total_q = 0

    for level in LEVELS:
        path = ROOT / f"reading/arabic/{level}/passages.jsonl"
        rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        counts = Counter()
        benign_counts = Counter()
        passages_flagged: set[str] = set()

        for row in rows:
            pid = str(row["id"])
            passage_text = str(row.get("text", ""))
            text_tokens = set(toks(passage_text))
            qs = row.get("questions", [])
            answers = {
                a.get("question_id"): a
                for a in row.get("answer_key", [])
                if isinstance(a, dict)
            }
            seen_prompts: set[str] = set()

            for q in qs:
                total_q += 1
                qid = str(q.get("id"))
                typ = str(q.get("type", ""))
                prompt = str(q.get("prompt", ""))
                a = answers.get(qid, {})
                answer = str(a.get("answer", ""))
                np = " ".join(norm(prompt).split())

                if np in seen_prompts:
                    add(unresolved, "duplicate_prompt_within_passage", level=level, passage_id=pid, question_id=qid, prompt=prompt)
                    counts["duplicate_prompt_within_passage"] += 1
                    passages_flagged.add(pid)
                seen_prompts.add(np)

                if not answer.strip():
                    add(unresolved, "empty_answer", level=level, passage_id=pid, question_id=qid)
                    counts["empty_answer"] += 1
                    passages_flagged.add(pid)
                    continue

                if " ".join(norm(answer).split()) == np:
                    add(unresolved, "answer_equals_prompt", level=level, passage_id=pid, question_id=qid)
                    counts["answer_equals_prompt"] += 1
                    passages_flagged.add(pid)

                at = toks(answer)
                if typ in DIRECT and at and text_tokens and not (set(at) & text_tokens):
                    add(
                        unresolved,
                        "direct_answer_zero_content_overlap_with_passage",
                        level=level,
                        passage_id=pid,
                        question_id=qid,
                        type=typ,
                        prompt=prompt,
                        answer=answer,
                        passage_text=passage_text,
                    )
                    counts["direct_answer_zero_content_overlap_with_passage"] += 1
                    passages_flagged.add(pid)

                if typ in LONG and len(at) < 2:
                    add(
                        unresolved,
                        "high_level_answer_extremely_short",
                        level=level,
                        passage_id=pid,
                        question_id=qid,
                        type=typ,
                        prompt=prompt,
                        answer=answer,
                        content_tokens=at,
                    )
                    counts["high_level_answer_extremely_short"] += 1
                    passages_flagged.add(pid)

                if typ == "contrast":
                    opts = QUOTED.findall(prompt)
                    if len(opts) >= 2 and not contrast_is_explanatory(answer, opts):
                        add(
                            unresolved,
                            "contrast_answer_not_semantically_structured_for_quoted_options",
                            level=level,
                            passage_id=pid,
                            question_id=qid,
                            prompt=prompt,
                            answer=answer,
                            quoted_options=opts,
                        )
                        counts["contrast_answer_not_semantically_structured_for_quoted_options"] += 1
                        passages_flagged.add(pid)
                    elif len(opts) >= 2 and not any(norm(o) in norm(answer) for o in opts):
                        add(
                            benign,
                            "contrast_surface_mismatch_but_explanatory",
                            level=level,
                            passage_id=pid,
                            question_id=qid,
                            prompt=prompt,
                            answer=answer,
                            quoted_options=opts,
                        )
                        benign_counts["contrast_surface_mismatch_but_explanatory"] += 1

                if typ == "cloze_transfer":
                    tids = q.get("target_ids", []) if isinstance(q.get("target_ids"), list) else []
                    if not tids:
                        add(unresolved, "cloze_without_target_id", level=level, passage_id=pid, question_id=qid, prompt=prompt, answer=answer)
                        counts["cloze_without_target_id"] += 1
                        passages_flagged.add(pid)

            # Duplicate answers are only suspicious when the same answer is used
            # across question roles where semantic duplication could indicate a
            # repeated/weak item. Repeated grammatical-category labels (e.g.
            # two independently correct answers of "اسم") are expected.
            answer_groups: dict[str, list[dict]] = defaultdict(list)
            q_by_id = {str(q.get("id")): q for q in qs if isinstance(q, dict)}
            for a in row.get("answer_key", []):
                if not isinstance(a, dict):
                    continue
                key = " ".join(norm(a.get("answer", "")).split())
                if key:
                    qid = str(a.get("question_id"))
                    q = q_by_id.get(qid, {})
                    answer_groups[key].append({
                        "question_id": qid,
                        "type": q.get("type"),
                        "prompt": q.get("prompt"),
                    })
            for answer_text, members in answer_groups.items():
                if len(members) < 2:
                    continue
                types = {str(m.get("type")) for m in members}
                if types and types <= GRAMMAR_CATEGORY_TYPES:
                    add(
                        benign,
                        "duplicate_grammar_category_answer_expected",
                        level=level,
                        passage_id=pid,
                        answer=answer_text,
                        questions=members,
                    )
                    benign_counts["duplicate_grammar_category_answer_expected"] += 1
                else:
                    add(
                        unresolved,
                        "duplicate_answer_text_within_passage",
                        level=level,
                        passage_id=pid,
                        answer=answer_text,
                        questions=members,
                        passage_text=passage_text,
                    )
                    counts["duplicate_answer_text_within_passage"] += 1
                    passages_flagged.add(pid)

        level_summary[level] = {
            "passages": len(rows),
            "flagged_passages": len(passages_flagged),
            "unresolved_by_code": dict(counts),
            "nonblocking_benign_by_code": dict(benign_counts),
        }

    payload = {
        "pass": 4,
        "name": "answer_evidence_alignment_diagnostics",
        "scope": "Arabic A1-C2 canonical reading corpus",
        "method": "conservative candidate detection with nonblocking classifier-safe benign classes; unresolved surface candidates retain passage context for explicit semantic adjudication",
        "not_claimed": [
            "semantic incorrectness from zero lexical overlap",
            "morphological equivalence from raw token overlap",
            "full answer-key correctness without adjudication",
        ],
        "levels": level_summary,
        "totals": {
            "questions": total_q,
            "unresolved_review_flags": len(unresolved),
            "nonblocking_benign_diagnostics": len(benign),
            "raw_diagnostics": len(unresolved) + len(benign),
            # compatibility for status tooling
            "review_flags": len(unresolved),
        },
        "flags": unresolved,
        "nonblocking_benign_diagnostics": benign,
        "status": "PASS" if not unresolved else "REVIEW_REQUIRED",
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["totals"], ensure_ascii=False))
    print("status=" + payload["status"])


if __name__ == "__main__":
    main()

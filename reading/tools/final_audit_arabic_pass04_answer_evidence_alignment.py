#!/usr/bin/env python3
"""Final Arabic review pass 04: answer/evidence alignment diagnostics.

Two-stage/fail-closed model:
1. conservative heuristics generate candidates;
2. classifier-safe benign cases and explicit reviewed adjudications are retained
   as non-blocking evidence, while unresolved candidates remain blocking.

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
ADJ = ROOT / "reading/audit/final_arabic_pass04_adjudications.json"
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
CONTRAST_EXPLANATION_MARKERS = {
    "الأول", "الأولى", "الثاني", "الثانية", "أما", "بينما", "لكن", "مقابل",
    "تعني", "يعني", "تصف", "يصف", "التعليق", "الإلغاء", "وصفي", "سببي",
}
PUNCT = " .،؛:؟!"


def norm(s: object) -> str:
    s = unicodedata.normalize("NFKC", str(s or "")).replace("ـ", "").replace("ٱ", "ا")
    return DIAC.sub("", s)


def toks(s: object) -> list[str]:
    return [x for x in ARWORD.findall(norm(s)) if x not in STOP and len(x) > 1]


def add(items: list[dict], code: str, **kw: object) -> None:
    items.append({"code": code, **kw})


def candidate_key(item: dict) -> str:
    return "|".join([
        str(item.get("code", "")),
        str(item.get("level", "")),
        str(item.get("passage_id", "")),
        str(item.get("question_id", "")),
    ])


def contrast_is_explanatory(answer: str, quoted_options: list[str]) -> bool:
    na = norm(answer).strip(PUNCT)
    if any(norm(option).strip(PUNCT) in na for option in quoted_options):
        return True
    words = set(ARWORD.findall(na))
    return len(toks(answer)) >= 3 and bool(words & CONTRAST_EXPLANATION_MARKERS or na.startswith("لا"))


def main() -> None:
    raw_unresolved: list[dict] = []
    benign: list[dict] = []
    total_q = 0
    passage_counts: dict[str, int] = {}

    for level in LEVELS:
        path = ROOT / f"reading/arabic/{level}/passages.jsonl"
        rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        passage_counts[level] = len(rows)

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
                    add(raw_unresolved, "duplicate_prompt_within_passage", level=level, passage_id=pid, question_id=qid, prompt=prompt)
                seen_prompts.add(np)

                if not answer.strip():
                    add(raw_unresolved, "empty_answer", level=level, passage_id=pid, question_id=qid)
                    continue

                if " ".join(norm(answer).split()) == np:
                    add(raw_unresolved, "answer_equals_prompt", level=level, passage_id=pid, question_id=qid)

                at = toks(answer)
                if typ in DIRECT and at and text_tokens and not (set(at) & text_tokens):
                    add(
                        raw_unresolved,
                        "direct_answer_zero_content_overlap_with_passage",
                        level=level,
                        passage_id=pid,
                        question_id=qid,
                        type=typ,
                        prompt=prompt,
                        answer=answer,
                        passage_text=passage_text,
                    )

                if typ in LONG and len(at) < 2:
                    add(
                        raw_unresolved,
                        "high_level_answer_extremely_short",
                        level=level,
                        passage_id=pid,
                        question_id=qid,
                        type=typ,
                        prompt=prompt,
                        answer=answer,
                        content_tokens=at,
                    )

                if typ == "contrast":
                    opts = QUOTED.findall(prompt)
                    if len(opts) >= 2 and not contrast_is_explanatory(answer, opts):
                        add(
                            raw_unresolved,
                            "contrast_answer_not_semantically_structured_for_quoted_options",
                            level=level,
                            passage_id=pid,
                            question_id=qid,
                            prompt=prompt,
                            answer=answer,
                            quoted_options=opts,
                        )
                    elif len(opts) >= 2 and not any(norm(o).strip(PUNCT) in norm(answer).strip(PUNCT) for o in opts):
                        add(
                            benign,
                            "contrast_surface_mismatch_but_explanatory",
                            level=level,
                            passage_id=pid,
                            question_id=qid,
                            prompt=prompt,
                            answer=answer,
                            quoted_options=opts,
                            resolution="AUTO_BENIGN_EXPLANATORY_CONTRAST",
                        )

                if typ == "cloze_transfer":
                    tids = q.get("target_ids", []) if isinstance(q.get("target_ids"), list) else []
                    if not tids:
                        add(raw_unresolved, "cloze_without_target_id", level=level, passage_id=pid, question_id=qid, prompt=prompt, answer=answer)

            # Duplicate answer text alone is nonblocking. Duplicate prompts are
            # independently detected above and remain blocking.
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
                add(
                    benign,
                    "duplicate_answer_text_nonblocking",
                    level=level,
                    passage_id=pid,
                    answer=answer_text,
                    questions=members,
                    resolution="AUTO_BENIGN_DUPLICATE_ANSWER_ONLY",
                )

    adj_payload = json.loads(ADJ.read_text(encoding="utf-8")) if ADJ.exists() else {"adjudications": {}}
    adjudications = adj_payload.get("adjudications", {})
    if not isinstance(adjudications, dict):
        raise AssertionError("Pass 04 adjudications must be an object keyed by candidate id")

    unresolved: list[dict] = []
    matched_adjudications: set[str] = set()
    for item in raw_unresolved:
        key = candidate_key(item)
        decision = adjudications.get(key)
        if isinstance(decision, dict) and decision.get("resolution") == "PASS_SUPPORTED":
            matched_adjudications.add(key)
            benign.append({
                **item,
                "code": "manually_adjudicated_surface_candidate",
                "original_code": item.get("code"),
                "candidate_key": key,
                "resolution": "MANUAL_PASS_SUPPORTED",
                "adjudication_reason": decision.get("reason", ""),
            })
        else:
            unresolved.append(item)

    stale_adjudications = sorted(set(adjudications) - matched_adjudications)

    level_summary: dict[str, dict] = {}
    for level in LEVELS:
        u = [x for x in unresolved if x.get("level") == level]
        b = [x for x in benign if x.get("level") == level]
        level_summary[level] = {
            "passages": passage_counts[level],
            "flagged_passages": len({str(x.get("passage_id")) for x in u}),
            "unresolved_by_code": dict(Counter(str(x.get("code")) for x in u)),
            "nonblocking_benign_by_code": dict(Counter(str(x.get("code")) for x in b)),
        }

    payload = {
        "pass": 4,
        "name": "answer_evidence_alignment_diagnostics",
        "scope": "Arabic A1-C2 canonical reading corpus",
        "method": "conservative candidate detection plus explicit manual adjudication; classifier-safe benign diagnostics remain visible and only unresolved semantic/evidence candidates block",
        "not_claimed": [
            "semantic incorrectness from zero lexical overlap",
            "morphological equivalence from raw token overlap",
            "full answer-key correctness without adjudication",
        ],
        "adjudication_source": "reading/audit/final_arabic_pass04_adjudications.json",
        "levels": level_summary,
        "totals": {
            "questions": total_q,
            "raw_blocking_candidates_before_adjudication": len(raw_unresolved),
            "manual_adjudications_applied": len(matched_adjudications),
            "stale_adjudications": len(stale_adjudications),
            "unresolved_review_flags": len(unresolved),
            "nonblocking_benign_diagnostics": len(benign),
            "raw_diagnostics": len(raw_unresolved) + len([x for x in benign if x.get("resolution", "").startswith("AUTO_")]),
            "review_flags": len(unresolved),
        },
        "flags": unresolved,
        "nonblocking_benign_diagnostics": benign,
        "stale_adjudication_keys": stale_adjudications,
        "status": "PASS" if not unresolved else "REVIEW_REQUIRED",
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["totals"], ensure_ascii=False))
    print("status=" + payload["status"])


if __name__ == "__main__":
    main()

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

INPUT = Path("reading/arabic/a2/passages.jsonl")
REPAIR_EVIDENCE = Path("reading/audit/arabic_a2_u09_metalinguistic_repair_2026-08-22.json")
POST_EVIDENCE = Path("reading/audit/arabic_a2_u09_metalinguistic_postrepair_2026-08-22.json")
EXPECTED_BEFORE_SHA256 = "f27ad06c372d316ca70346e19a10a72645577897de8db676e317d869d8945e1c"
UNIT = 9

REPAIRS = {
    ("ar-a2-u09-p01", "q6"): {
        "before_prompt": "ما التصنيف النحوي لكلمة «قصة» في هذا الاستعمال؟",
        "before_type": "grammar_category",
        "before_answer": "اسم",
        "prompt": "إذا وصفت الحكاية التي روتها الجدة، أي عبارة أنسب: «قصة عائلية» أم «قصة عائلي»؟",
        "type": "grammar_choice",
        "answer": "قصة عائلية.",
        "explanation": "التعبير الطبيعي هو «قصة عائلية» عند وصف حكاية مرتبطة بالعائلة.",
    },
    ("ar-a2-u09-p02", "q6"): {
        "before_prompt": "ما التصنيف النحوي لكلمة «نسخة» في هذا الاستعمال؟",
        "before_type": "grammar_category",
        "before_answer": "فعل ماضٍ",
        "prompt": "إذا قارنت نور رواية الجد برواية الخالة، أي تعبير أنسب: «نسخة الجد من القصة» أم «نسخة الجد القصة»؟",
        "type": "grammar_choice",
        "answer": "نسخة الجد من القصة.",
        "explanation": "«نسخة» هنا اسم بمعنى رواية أو صيغة من القصة، ويأتي طبيعيًا مع «من»؛ وليست فعلًا ماضيًا في هذا السياق.",
    },
    ("ar-a2-u09-p03", "q6"): {
        "before_prompt": "ما التصنيف النحوي لكلمة «مطعم» في هذا الاستعمال؟",
        "before_type": "grammar_category",
        "before_answer": "اسم",
        "prompt": "للتحدث عن مكان العشاء، أي جملة أنسب: «ذهبنا إلى مطعم قريب» أم «ذهبنا مطعم قريب»؟",
        "type": "grammar_choice",
        "answer": "ذهبنا إلى مطعم قريب.",
        "explanation": "التعبير الطبيعي هو «ذهبنا إلى مطعم قريب» عند ذكر الوجهة.",
    },
}

FALSE_POSITIVES = {
    ("ar-a2-u09-p06", "q10"): {
        "prompt": "لماذا يستخدم النص أسئلة «من؟ متى؟ لماذا؟» في النهاية؟",
        "type": "grammar_function",
        "answer": "لتقديم طريقة عملية لفحص العادة وسياقها قبل التعميم.",
        "reason": "Discourse-comprehension question asks why the passage ends with a practical question set for examining a custom and its context; it does not require a grammatical label or form identification.",
    }
}

FORMAL_TYPES = {"grammar_category", "grammar_function", "grammar_identification", "person_form"}
FORMAL_PROMPT_MARKERS = ("التصنيف النحوي", "ما الوظيفة النحوية", "ما وظيفة «", "ماذا تصف «", "ماذا تعبر «", "ماذا تفعل «")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    raw = INPUT.read_bytes()
    before_sha = digest(raw)
    if before_sha != EXPECTED_BEFORE_SHA256:
        raise SystemExit(f"FAIL CLOSED: expected {EXPECTED_BEFORE_SHA256}, got {before_sha}")

    records = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    before_text = {r["id"]: r.get("text") for r in records}
    applied, found = [], set()

    for r in records:
        if r.get("cefr") != "A2" or r.get("unit") != UNIT:
            continue
        qs = {q["id"]: q for q in r.get("questions", [])}
        ans = {a["question_id"]: a for a in r.get("answer_key", [])}
        for key, spec in REPAIRS.items():
            pid, qid = key
            if pid != r.get("id"):
                continue
            q, a = qs.get(qid), ans.get(qid)
            if q is None or a is None:
                raise SystemExit(f"Missing {pid}/{qid}")
            actual = (q.get("prompt"), q.get("type"), a.get("answer"))
            expected = (spec["before_prompt"], spec["before_type"], spec["before_answer"])
            if actual != expected:
                raise SystemExit(f"Source drift at {pid}/{qid}: {actual!r}")
            before = {"prompt": q["prompt"], "type": q["type"], "answer": a["answer"]}
            q["prompt"], q["type"] = spec["prompt"], spec["type"]
            a["answer"], a["explanation"] = spec["answer"], spec["explanation"]
            applied.append({
                "passage_id": pid,
                "question_id": qid,
                "before": before,
                "after": {"prompt": q["prompt"], "type": q["type"], "answer": a["answer"], "explanation": a["explanation"]},
            })
            found.add(key)

    if found != set(REPAIRS):
        raise SystemExit(f"Repair inventory mismatch: missing={sorted(set(REPAIRS) - found)}")
    if any(r.get("text") != before_text[r["id"]] for r in records):
        raise SystemExit("Passage prose changed unexpectedly")

    unit_records = [r for r in records if r.get("cefr") == "A2" and r.get("unit") == UNIT]
    if len(unit_records) != 6:
        raise SystemExit(f"Expected 6 Unit {UNIT:02d} records, found {len(unit_records)}")
    questions = [q for r in unit_records for q in r.get("questions", [])]
    answers = [a for r in unit_records for a in r.get("answer_key", [])]
    if (len(questions), len(answers)) != (60, 60):
        raise SystemExit(f"Expected 60Q/60A, found {len(questions)}Q/{len(answers)}A")
    for r in unit_records:
        if {q["id"] for q in r["questions"]} != {a["question_id"] for a in r["answer_key"]}:
            raise SystemExit(f"Question/answer linkage mismatch in {r['id']}")

    allowed_false_positives = []
    unexpected_findings = []
    fp_seen = set()
    for r in unit_records:
        answers_by_qid = {a["question_id"]: a for a in r.get("answer_key", [])}
        for q in r.get("questions", []):
            key = (r["id"], q["id"])
            prompt = q.get("prompt", "")
            is_formal = q.get("type") in FORMAL_TYPES or any(m in prompt for m in FORMAL_PROMPT_MARKERS)
            if not is_formal:
                continue
            finding = {"passage_id": r["id"], "question_id": q["id"], "type": q.get("type"), "prompt": prompt}
            if key in FALSE_POSITIVES:
                spec = FALSE_POSITIVES[key]
                a = answers_by_qid[q["id"]]
                if (prompt, q.get("type"), a.get("answer")) != (spec["prompt"], spec["type"], spec["answer"]):
                    raise SystemExit(f"False-positive source drift at {key}")
                finding["answer"] = a.get("answer")
                finding["reason"] = spec["reason"]
                allowed_false_positives.append(finding)
                fp_seen.add(key)
            else:
                unexpected_findings.append(finding)

    if fp_seen != set(FALSE_POSITIVES):
        raise SystemExit(f"False-positive inventory mismatch: missing={sorted(set(FALSE_POSITIVES)-fp_seen)}")
    if unexpected_findings:
        raise SystemExit(f"Residual unexpected metalinguistic findings: {unexpected_findings}")

    prompt_counts = Counter(q.get("prompt", "") for q in questions)
    duplicate_prompts = sorted(p for p, n in prompt_counts.items() if p and n > 1)
    if duplicate_prompts:
        raise SystemExit(f"Duplicate Unit {UNIT:02d} prompts: {duplicate_prompts}")

    serialized = "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in records) + "\n"
    INPUT.write_text(serialized, encoding="utf-8")
    after_sha = digest(INPUT.read_bytes())

    repair_evidence = {
        "schema_version": 1,
        "date": "2026-08-22",
        "language": "ar",
        "level": "A2",
        "unit": UNIT,
        "status": "BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW",
        "before_sha256": before_sha,
        "after_sha256": after_sha,
        "inventory_candidates": len(REPAIRS) + len(FALSE_POSITIVES),
        "confirmed_repairs": len(applied),
        "adjudicated_false_positive_count": len(allowed_false_positives),
        "adjudicated_false_positives": allowed_false_positives,
        "passage_text_changed": False,
        "notable_sense_corrections": ["نسخة: live context is the noun 'version/copy', not a past-tense verb."],
        "repairs": applied,
        "release_effect": "Arabic remains educator-blocked; independent semantic/native/educator review required.",
    }
    post_evidence = {
        "schema_version": 1,
        "date": "2026-08-22",
        "language": "ar",
        "level": "A2",
        "unit": UNIT,
        "bound_sha256": after_sha,
        "scope": {"records": len(unit_records), "questions": len(questions), "answers": len(answers)},
        "inventory_candidates": len(REPAIRS) + len(FALSE_POSITIVES),
        "confirmed_repairs": len(applied),
        "adjudicated_false_positive_count": len(allowed_false_positives),
        "allowed_false_positives": allowed_false_positives,
        "unexpected_formal_metalinguistic_finding_count": len(unexpected_findings),
        "unexpected_findings": unexpected_findings,
        "exact_duplicate_prompt_count": len(duplicate_prompts),
        "duplicate_prompts": duplicate_prompts,
        "passage_text_changed": False,
        "question_type_counts": dict(sorted(Counter(q.get("type") for q in questions).items())),
        "status": "PASS_DETERMINISTIC_A2_UNIT09",
        "limitations": "Deterministic/self-review only; independent native/educator review remains required.",
        "release_effect": "Arabic remains educator-blocked.",
    }
    REPAIR_EVIDENCE.write_text(json.dumps(repair_evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    POST_EVIDENCE.write_text(json.dumps(post_evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": post_evidence["status"], "before_sha256": before_sha, "after_sha256": after_sha,
        "candidates": len(REPAIRS)+len(FALSE_POSITIVES), "repairs": len(applied),
        "false_positives": len(allowed_false_positives), "records": len(unit_records),
        "questions": len(questions), "answers": len(answers),
    }, ensure_ascii=False))

if __name__ == "__main__":
    main()

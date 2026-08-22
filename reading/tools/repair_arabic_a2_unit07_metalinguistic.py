from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

INPUT = Path("reading/arabic/a2/passages.jsonl")
REPAIR_EVIDENCE = Path("reading/audit/arabic_a2_u07_metalinguistic_repair_2026-08-21.json")
POST_EVIDENCE = Path("reading/audit/arabic_a2_u07_metalinguistic_postrepair_2026-08-21.json")
EXPECTED_BEFORE_SHA256 = "f27ad06c372d316ca70346e19a10a72645577897de8db676e317d869d8945e1c"

REPAIRS = {
    ("ar-a2-u07-p01", "q6"): {
        "before_prompt": "ما التصنيف النحوي لكلمة «مناسبة» في هذا الاستعمال؟",
        "before_type": "grammar_category",
        "before_answer": "اسم",
        "prompt": "إذا كنت تصف حدثًا ثقافيًا في الساحة، أي عبارة أنسب: «مناسبة ثقافية» أم «جمهور ثقافي»؟",
        "type": "grammar_choice",
        "answer": "مناسبة ثقافية.",
        "explanation": "«مناسبة» تناسب الحديث عن الحدث نفسه، أما «جمهور» فيشير إلى الحاضرين أو المتابعين.",
    },
    ("ar-a2-u07-p02", "q7"): {
        "before_prompt": "ما التصنيف النحوي لكلمة «بيان» في هذا الاستعمال؟",
        "before_type": "grammar_category",
        "before_answer": "اسم",
        "prompt": "إذا أصدرت الإدارة نصًا رسميًا عن موعد الإغلاق، أي عبارة أنسب: «بيان من الإدارة» أم «صحافة من الإدارة»؟",
        "type": "grammar_choice",
        "answer": "بيان من الإدارة.",
        "explanation": "«بيان» هو النص الرسمي الصادر عن الجهة نفسها، بينما «الصحافة» تنشر الأخبار والتقارير.",
    },
    ("ar-a2-u07-p03", "q6"): {
        "before_prompt": "ما التصنيف النحوي لكلمة «تحقيق» في هذا الاستعمال؟",
        "before_type": "grammar_category",
        "before_answer": "اسم",
        "prompt": "إذا جمع الطلاب معلومات ليفهموا المشكلة، أي عبارة أنسب: «أجروا تحقيقًا بسيطًا» أم «صنعوا تحقيقًا بسيطًا»؟",
        "type": "grammar_choice",
        "answer": "أجروا تحقيقًا بسيطًا.",
        "explanation": "التعبير الطبيعي هو «أجرى تحقيقًا» عند القيام ببحث أو تقصٍّ منظم.",
    },
    ("ar-a2-u07-p03", "q7"): {
        "before_prompt": "ما التصنيف النحوي لكلمة «تأثير» في هذا الاستعمال؟",
        "before_type": "grammar_category",
        "before_answer": "اسم",
        "prompt": "إذا تحدثت عن نتيجة الازدحام على المشاة، أي عبارة أنسب: «تأثير الازدحام على المشاة» أم «تأثير الازدحام بالمشاة»؟",
        "type": "grammar_choice",
        "answer": "تأثير الازدحام على المشاة.",
        "explanation": "يأتي «تأثير» في هذا المعنى عادة مع «على» لبيان من يقع عليه الأثر.",
    },
    ("ar-a2-u07-p04", "q6"): {
        "before_prompt": "ما التصنيف النحوي لكلمة «أعلن» في هذا الاستعمال؟",
        "before_type": "grammar_category",
        "before_answer": "فعل",
        "prompt": "لنقل قرار المركز، أي جملة أنسب: «أعلن المركز أنه سيضيف ساعتين» أم «أعلن المركز من ساعتين»؟",
        "type": "grammar_choice",
        "answer": "أعلن المركز أنه سيضيف ساعتين.",
        "explanation": "يأتي «أعلن» هنا مع جملة تبين ما أعلنه المركز.",
    },
    ("ar-a2-u07-p05", "q6"): {
        "before_prompt": "ما التصنيف النحوي لكلمة «رئيسية» في هذا الاستعمال؟",
        "before_type": "grammar_category",
        "before_answer": "صفة",
        "prompt": "لوصف ثلاث أفكار مهمة في الملخص، أي عبارة أنسب: «ثلاث أفكار رئيسية» أم «ثلاث أفكار رئيسي»؟",
        "type": "grammar_choice",
        "answer": "ثلاث أفكار رئيسية.",
        "explanation": "«رئيسية» توافق «أفكار» في هذا التركيب الطبيعي.",
    },
    ("ar-a2-u07-p06", "q9"): {
        "before_prompt": "ماذا تصف «رئيسية»؟",
        "before_type": "grammar_function",
        "before_answer": "المعلومات الأساسية الأكثر أهمية في الخبر أو الملخص.",
        "prompt": "في ملخص قصير جدًا، أيهما تختار أولًا: المعلومات الرئيسية أم التفاصيل الثانوية؟",
        "type": "contrast",
        "answer": "المعلومات الرئيسية.",
        "explanation": "الملخص القصير يقدّم المعلومات الأساسية أولًا ويترك كثيرًا من التفاصيل الثانوية.",
    },
}

FORMAL_TYPES = {"grammar_category", "grammar_function", "grammar_identification", "person_form"}
FORMAL_PROMPT_MARKERS = ("التصنيف النحوي", "ما الوظيفة النحوية", "ما وظيفة «", "ماذا تصف «")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    raw = INPUT.read_bytes()
    before_sha256 = sha256_bytes(raw)
    if before_sha256 != EXPECTED_BEFORE_SHA256:
        raise SystemExit(
            f"FAIL CLOSED: expected Arabic A2 SHA-256 {EXPECTED_BEFORE_SHA256}, got {before_sha256}"
        )

    original_lines = raw.decode("utf-8").splitlines()
    records = [json.loads(line) for line in original_lines if line.strip()]
    before_text = {r["id"]: r.get("text") for r in records}

    applied = []
    found_keys = set()

    for record in records:
        if record.get("cefr") != "A2" or record.get("unit") != 7:
            continue
        questions = {q["id"]: q for q in record.get("questions", [])}
        answers_by_qid = {a["question_id"]: a for a in record.get("answer_key", [])}
        for (passage_id, question_id), spec in REPAIRS.items():
            if passage_id != record.get("id"):
                continue
            q = questions.get(question_id)
            a = answers_by_qid.get(question_id)
            if q is None or a is None:
                raise SystemExit(f"Missing {passage_id}/{question_id}")
            if q.get("prompt") != spec["before_prompt"]:
                raise SystemExit(f"Prompt drift at {passage_id}/{question_id}: {q.get('prompt')!r}")
            if q.get("type") != spec["before_type"]:
                raise SystemExit(f"Type drift at {passage_id}/{question_id}: {q.get('type')!r}")
            if a.get("answer") != spec["before_answer"]:
                raise SystemExit(f"Answer drift at {passage_id}/{question_id}: {a.get('answer')!r}")

            before = {
                "prompt": q["prompt"],
                "type": q["type"],
                "answer": a["answer"],
            }
            q["prompt"] = spec["prompt"]
            q["type"] = spec["type"]
            a["answer"] = spec["answer"]
            a["explanation"] = spec["explanation"]
            after = {
                "prompt": q["prompt"],
                "type": q["type"],
                "answer": a["answer"],
                "explanation": a["explanation"],
            }
            found_keys.add((passage_id, question_id))
            applied.append(
                {
                    "passage_id": passage_id,
                    "question_id": question_id,
                    "before": before,
                    "after": after,
                }
            )

    if found_keys != set(REPAIRS):
        missing = sorted(set(REPAIRS) - found_keys)
        extra = sorted(found_keys - set(REPAIRS))
        raise SystemExit(f"Repair inventory mismatch; missing={missing}, extra={extra}")

    for record in records:
        if record.get("text") != before_text[record["id"]]:
            raise SystemExit(f"Passage prose changed unexpectedly: {record['id']}")

    serialized = "\n".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True) for record in records
    ) + "\n"
    INPUT.write_text(serialized, encoding="utf-8")
    after_sha256 = sha256_bytes(INPUT.read_bytes())

    unit_records = [r for r in records if r.get("cefr") == "A2" and r.get("unit") == 7]
    if len(unit_records) != 6:
        raise SystemExit(f"Expected 6 Unit 07 records, found {len(unit_records)}")

    questions = [q for r in unit_records for q in r.get("questions", [])]
    answers = [a for r in unit_records for a in r.get("answer_key", [])]
    if len(questions) != 60 or len(answers) != 60:
        raise SystemExit(f"Expected 60Q/60A, found {len(questions)}Q/{len(answers)}A")

    for record in unit_records:
        q_ids = {q["id"] for q in record.get("questions", [])}
        a_q_ids = {a["question_id"] for a in record.get("answer_key", [])}
        if q_ids != a_q_ids:
            raise SystemExit(f"Question/answer linkage mismatch in {record['id']}")

    formal_findings = []
    for record in unit_records:
        for q in record.get("questions", []):
            prompt = q.get("prompt", "")
            if q.get("type") in FORMAL_TYPES or any(marker in prompt for marker in FORMAL_PROMPT_MARKERS):
                formal_findings.append(
                    {
                        "passage_id": record["id"],
                        "question_id": q["id"],
                        "type": q.get("type"),
                        "prompt": prompt,
                    }
                )

    prompt_counts = Counter(q.get("prompt", "") for q in questions)
    duplicate_prompts = sorted(p for p, count in prompt_counts.items() if p and count > 1)
    if formal_findings:
        raise SystemExit(f"Residual Unit07 metalinguistic findings: {formal_findings}")
    if duplicate_prompts:
        raise SystemExit(f"Duplicate Unit07 prompts: {duplicate_prompts}")

    repair_evidence = {
        "schema_version": 1,
        "date": "2026-08-21",
        "language": "ar",
        "level": "A2",
        "unit": 7,
        "status": "BOUNDED_REPAIR_APPLIED_NEEDS_INDEPENDENT_REVIEW",
        "before_sha256": before_sha256,
        "after_sha256": after_sha256,
        "inventory_candidates": len(REPAIRS),
        "confirmed_repairs": len(applied),
        "passage_text_changed": False,
        "notable_sense_corrections": [],
        "repairs": applied,
        "release_effect": "Arabic remains educator-blocked; independent semantic/native/educator review required.",
    }

    post_evidence = {
        "schema_version": 1,
        "date": "2026-08-21",
        "language": "ar",
        "level": "A2",
        "unit": 7,
        "bound_sha256": after_sha256,
        "scope": {"records": len(unit_records), "questions": len(questions), "answers": len(answers)},
        "inventory_candidates": len(REPAIRS),
        "confirmed_repairs": len(applied),
        "passage_text_changed": False,
        "formal_metalinguistic_finding_count": len(formal_findings),
        "findings": formal_findings,
        "exact_duplicate_prompt_count": len(duplicate_prompts),
        "duplicate_prompts": duplicate_prompts,
        "question_type_counts": dict(sorted(Counter(q.get("type") for q in questions).items())),
        "status": "PASS_DETERMINISTIC_A2_UNIT07",
        "limitations": "Deterministic/self-review only; independent native/educator review remains required.",
        "release_effect": "Arabic remains educator-blocked.",
    }

    REPAIR_EVIDENCE.write_text(
        json.dumps(repair_evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    POST_EVIDENCE.write_text(
        json.dumps(post_evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "status": post_evidence["status"],
                "before_sha256": before_sha256,
                "after_sha256": after_sha256,
                "repairs": len(applied),
                "records": len(unit_records),
                "questions": len(questions),
                "answers": len(answers),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

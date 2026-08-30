#!/usr/bin/env python3
"""Repair Arabic A1 Unit 1 low-level metalinguistic questions.

This is a deliberately bounded Q/A-only repair. It rewrites exactly nine questions
that test formal grammatical labels into A1-appropriate use/comprehension tasks.
Passage prose, lexical targets, IDs, ordering, and all other questions remain intact.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading" / "arabic" / "a1" / "passages.jsonl"
AUDIT = ROOT / "reading" / "audit" / "arabic_a1_u01_metalinguistic_repair_2026-08-30.json"
EXPECTED_SHA256 = "d6142ee56ec830c4a41cb7244fe99c65824cebbe59ff2e9b8f44d4640c9e228b"
FORMAL_TYPES = {"grammar_category", "grammar_function", "grammar_identification", "person_form"}

REPAIRS = {
    ("ar-a1-u01-p01", "q6"): {
        "old_type": "grammar_category",
        "old_prompt": "ما التصنيف النحوي الأدق لـ«هنا» في الاستعمال المكاني؟",
        "new_question": {
            "answer_id": "a6", "id": "q6",
            "prompt": "إذا كانت ليلى في الغرفة والكتاب بجانبها، فأيهما أنسب: «الكتاب هنا» أم «الكتاب هناك»؟",
            "target_ids": ["ar-r34"], "type": "contrast"
        },
        "new_answer": "الكتاب هنا.",
        "new_explanation": "«هنا» تدل في هذا السياق على المكان القريب من المتكلم."
    },
    ("ar-a1-u01-p02", "q7"): {
        "old_type": "grammar_category",
        "old_prompt": "ما وظيفة «بعد» في «بعد قليل»؟",
        "new_question": {
            "answer_id": "a7", "id": "q7",
            "prompt": "إذا قالت الأم «بعد قليل نذهب إلى المدرسة»، فهل الذهاب الآن أم لاحقًا؟",
            "target_ids": ["ar-r37"], "type": "sequence"
        },
        "new_answer": "لاحقًا، بعد قليل.",
        "new_explanation": "«بعد قليل» تضع الذهاب في وقت يأتي بعد لحظة الكلام."
    },
    ("ar-a1-u01-p02", "q9"): {
        "old_type": "grammar_identification",
        "old_prompt": "ما الكلمة التي تنفي الفعل في «لم تأخذ كل الكتب»؟",
        "new_question": {
            "answer_id": "a9", "id": "q9",
            "prompt": "اختر الجملة الصحيحة لنفي أخذ الكتب في الماضي: «لم تأخذ كل الكتب» أم «لا أخذت كل الكتب»؟",
            "type": "grammar_choice"
        },
        "new_answer": "لم تأخذ كل الكتب.",
        "new_explanation": "هذه هي الصيغة الصحيحة لنفي الفعل الماضي المقصود في هذا السياق."
    },
    ("ar-a1-u01-p03", "q6"): {
        "old_type": "grammar_category",
        "old_prompt": "ما التصنيف النحوي الأدق لـ«هناك» في الاستعمال المكاني؟",
        "new_question": {
            "answer_id": "a6", "id": "q6",
            "prompt": "في «أريد أن أذهب إلى هناك مرة أخرى»، إلى أي مكان تشير «هناك»؟",
            "target_ids": ["ar-r40"], "type": "reference_resolution"
        },
        "new_answer": "إلى الحديقة.",
        "new_explanation": "الحديقة هي المكان المذكور الذي تريد ليلى الذهاب إليه مرة أخرى."
    },
    ("ar-a1-u01-p03", "q10"): {
        "old_type": "person_form",
        "old_prompt": "في «أريد»، من صاحب الفعل؟",
        "new_question": {
            "answer_id": "a10", "id": "q10",
            "prompt": "إذا قالت ليلى «أريد أن أعود الآن»، فمن الذي يريد العودة؟",
            "type": "reference_resolution"
        },
        "new_answer": "ليلى.",
        "new_explanation": "ليلى هي المتكلمة في الجملة، لذلك هي التي تريد العودة."
    },
    ("ar-a1-u01-p05", "q7"): {
        "old_type": "grammar_function",
        "old_prompt": "ماذا تدل «حتى» في «حتى المساء»؟",
        "new_question": {
            "answer_id": "a7", "id": "q7",
            "prompt": "إذا بقيت ليلى في المكتبة حتى المساء، متى انتهى بقاؤها هناك؟",
            "target_ids": ["ar-r56"], "type": "sequence"
        },
        "new_answer": "عند المساء، عندما جاء المساء.",
        "new_explanation": "«حتى المساء» تحدد المساء بوصفه نهاية مدة البقاء."
    },
    ("ar-a1-u01-p05", "q9"): {
        "old_type": "grammar_identification",
        "old_prompt": "ما صيغة العدد في كلمة «كتابين»؟",
        "new_question": {
            "answer_id": "a9", "id": "q9",
            "prompt": "اختر الصيغة الصحيحة: «أخذت ليلى كتابين» أم «أخذت ليلى كتابان»؟",
            "type": "grammar_choice"
        },
        "new_answer": "أخذت ليلى كتابين.",
        "new_explanation": "هذه هي الصيغة الصحيحة في الجملة كما استعملها النص."
    },
    ("ar-a1-u01-p06", "q8"): {
        "old_type": "grammar_function",
        "old_prompt": "في «حتى المساء»، ماذا تحدد «حتى»؟",
        "new_question": {
            "answer_id": "a8", "id": "q8",
            "prompt": "إذا قرأت ليلى حتى المساء، متى تنتهي القراءة؟",
            "target_ids": ["ar-r56"], "type": "sequence"
        },
        "new_answer": "عند المساء.",
        "new_explanation": "المساء هو نهاية المدة في عبارة «حتى المساء»."
    },
    ("ar-a1-u01-p06", "q10"): {
        "old_type": "grammar_function",
        "old_prompt": "ما وظيفة «أو» في «كتابًا واحدًا أو اثنين»؟",
        "new_question": {
            "answer_id": "a10", "id": "q10",
            "prompt": "أي عبارة تدل على خيارين: «كتابًا واحدًا أو اثنين» أم «كتابًا واحدًا واثنين معًا»؟",
            "type": "contrast"
        },
        "new_answer": "كتابًا واحدًا أو اثنين.",
        "new_explanation": "«أو» تعرض هنا بديلين ممكنين، لا جمع البديلين معًا."
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    before = PATH.read_bytes()
    if sha256(before) != EXPECTED_SHA256:
        raise SystemExit("Arabic A1 canonical hash drifted; refusing Unit 1 repair")

    lines = PATH.read_text(encoding="utf-8").splitlines()
    if len(lines) != 60:
        raise SystemExit(f"Expected 60 A1 records, found {len(lines)}")
    records = [json.loads(line) for line in lines]
    if [r.get("sequence") for r in records] != list(range(1, 61)):
        raise SystemExit("Arabic A1 sequence drift")

    changed = []
    for record in records[:6]:
        rid = record["id"]
        if record.get("unit") != 1:
            raise SystemExit(f"{rid}: first six records are no longer Unit 1")
        q_by_id = {q["id"]: q for q in record["questions"]}
        a_by_qid = {a["question_id"]: a for a in record["answer_key"]}
        for qid in [qid for (pid, qid) in REPAIRS if pid == rid]:
            spec = REPAIRS[(rid, qid)]
            q = q_by_id[qid]
            a = a_by_qid[qid]
            if q.get("type") != spec["old_type"] or q.get("prompt") != spec["old_prompt"]:
                raise SystemExit(f"{rid}/{qid}: source question drifted; refusing repair")
            record["questions"][record["questions"].index(q)] = spec["new_question"]
            a["answer"] = spec["new_answer"]
            a["explanation"] = spec["new_explanation"]
            changed.append({
                "passage_id": rid,
                "question_id": qid,
                "old_type": spec["old_type"],
                "new_type": spec["new_question"]["type"],
                "new_prompt": spec["new_question"]["prompt"],
                "new_answer": spec["new_answer"],
            })

        note = "2026-08-30 A1 Unit 1 metalinguistic remediation: formal-label items rewritten as reading/use tasks; all 10 question-answer links re-reviewed."
        if note not in record["quality"].setdefault("notes", []):
            record["quality"]["notes"].append(note)
        record["revision"] = int(record.get("revision", 0)) + 1

    if len(changed) != 9:
        raise SystemExit(f"Expected exactly 9 repaired questions, changed {len(changed)}")

    # Post-repair Unit 1 invariants.
    for record in records[:6]:
        if len(record["questions"]) != 10 or len(record["answer_key"]) != 10:
            raise SystemExit(f"{record['id']}: question/answer count drift")
        qids = {q["id"] for q in record["questions"]}
        if qids != {f"q{i}" for i in range(1, 11)}:
            raise SystemExit(f"{record['id']}: question IDs drift")
        for ans in record["answer_key"]:
            if ans["question_id"] not in qids:
                raise SystemExit(f"{record['id']}: answer linkage drift")
        formal = [(q["id"], q["type"]) for q in record["questions"] if q.get("type") in FORMAL_TYPES]
        if formal:
            raise SystemExit(f"{record['id']}: formal metalinguistic types remain: {formal}")

    after_text = "\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in records) + "\n"
    PATH.write_text(after_text, encoding="utf-8")
    after = PATH.read_bytes()

    audit = {
        "schema_version": 1,
        "project_id": "LANG-A1C2",
        "language": "arabic",
        "level": "A1",
        "unit": 1,
        "date": "2026-08-30",
        "status": "APPLIED_AND_REVIEWED_INTERNAL",
        "scope": "Question/answer-only remediation of nine low-level formal-label items across Arabic A1 Unit 1; passage prose and lexical inventory unchanged.",
        "source_sha256": EXPECTED_SHA256,
        "result_sha256": sha256(after),
        "passages_reviewed": 6,
        "questions_reviewed": 60,
        "answers_reviewed": 60,
        "questions_repaired": 9,
        "repairs": changed,
        "post_repair_formal_question_types_in_unit": 0,
        "quality_interpretation": "Internal substantive Q/A remediation only. It does not substitute for required independent native, educator, model-family, or blind post-repair review.",
        "release_claim": False,
    }
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

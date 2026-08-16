#!/usr/bin/env python3
"""Resolve the final eight A2 Pass 03 lexical-composition deficits.

Only already-scheduled review vocabulary is used. Passage prose, lexical
schedules, grammar/discourse targets, question/answer IDs, and all unselected
questions remain unchanged. The script fails closed on source drift.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "reading/arabic/a2/passages.jsonl"

# passage_id -> question_id -> replacement fields.
# expected_* fields are source-state guards and are removed before mutation.
CHANGES = {
    "ar-a2-u08-p04": {
        "q5": {
            "expected_type": "summary",
            "expected_prompt": "لخص ما تلاحظه الأسرة بعد العاصفة.",
            "type": "vocabulary_in_context",
            "prompt": "ماذا يعني «أثره» في «قد يظهر أثره في مكان آخر»؟",
            "target_ids": ["ar-r899"],
            "answer": "النتيجة أو التأثير الذي يظهر في مكان آخر.",
        }
    },
    "ar-a2-u09-p04": {
        "q10": {
            "expected_type": "summary",
            "expected_prompt": "لخص ما تعلمته نور عن الاحتفالات.",
            "type": "vocabulary_in_context",
            "prompt": "ما معنى «الجمهور» في وصف الحفل؟",
            "target_ids": ["ar-r975"],
            "answer": "الأشخاص الذين حضروا الحفل وشاهدوا البرنامج.",
        }
    },
    "ar-a2-u10-p01": {
        "q3": {
            "expected_type": "literal_detail",
            "expected_prompt": "أين تقابل نور هدى في النهاية؟",
            "type": "vocabulary_in_context",
            "prompt": "ماذا تعني عبارة «في موعدها» في وصف وصول نور؟",
            "target_ids": ["ar-r691"],
            "answer": "في الوقت المحدد للقاء.",
        },
        "q6": {
            "expected_type": "summary",
            "expected_prompt": "لخص الحلول الثلاثة التي تستخدمها نور.",
            "type": "vocabulary_in_context",
            "prompt": "ما معنى «إعلان» عند باب المكتبة في هذا السياق؟",
            "target_ids": ["ar-r563"],
            "answer": "إشعار مكتوب يقدم معلومة للزوار.",
        },
    },
    "ar-a2-u10-p02": {
        "q5": {
            "expected_type": "summary",
            "expected_prompt": "لخص مصادر المعلومات في مشروع نور.",
            "type": "vocabulary_in_context",
            "prompt": "ماذا تعني «نسخة رقمية» من الصورة القديمة؟",
            "target_ids": ["ar-r1149"],
            "answer": "صورة محفوظة بصيغة رقمية يمكن استخدامها ومقارنتها بالصورة الحديثة.",
        }
    },
    "ar-a2-u10-p03": {
        "q3": {
            "expected_type": "literal_detail",
            "expected_prompt": "ما المشكلة في الشاحن الأول؟",
            "type": "vocabulary_in_context",
            "prompt": "ماذا يعني أن الشاحن «غير مناسب» لجهاز هدى؟",
            "target_ids": ["ar-r836"],
            "answer": "أنه لا يلائم جهازها أو حاجتها رغم أنه يعمل.",
        },
        "q6": {
            "expected_type": "contrast",
            "expected_prompt": "ما الفرق بين «صالح» و«مناسب» في حالة الشاحن؟",
            "type": "contrast",
            "prompt": "ما الفرق بين «صالح» و«مناسب» في حالة الشاحن؟",
            "target_ids": ["ar-r716", "ar-r836"],
            "answer": "صالح يعني أنه يعمل، ومناسب يعني أنه يلائم جهاز هدى وحاجتها.",
        },
    },
    "ar-a2-u10-p04": {
        "q5": {
            "expected_type": "summary",
            "expected_prompt": "لخص تطور المعلومات من الخبر الأول إلى الثاني.",
            "type": "vocabulary_in_context",
            "prompt": "ماذا يعني «أظهرت البيانات» في الخبر الثاني؟",
            "target_ids": ["ar-r1128"],
            "answer": "بيّنت البيانات وكشفت ما حدث في الاستخدام بعد التجربة.",
        }
    },
    "ar-a2-u10-p05": {
        "q5": {
            "expected_type": "summary",
            "expected_prompt": "لخص ما تغير وما بقي في الاجتماع.",
            "type": "vocabulary_in_context",
            "prompt": "ما معنى «نسخة» عندما يروي الأطفال القصة؟",
            "target_ids": ["ar-r1149"],
            "answer": "رواية أو صيغة من القصة كما يتذكرها كل طفل.",
        }
    },
    "ar-a2-u10-p06": {
        "q10": {
            "expected_type": "synthesis",
            "expected_prompt": "كيف يجمع النص بين مجالات مختلفة في مهارة واحدة؟",
            "type": "vocabulary_in_context",
            "prompt": "ما معنى «التدريب» في سياق التعلم؟",
            "target_ids": ["ar-r806"],
            "answer": "ممارسة متكررة تساعد على تطوير مهارة.",
        }
    },
}


def read_rows() -> list[dict]:
    return [json.loads(x) for x in PATH.read_text(encoding="utf-8").splitlines() if x.strip()]


def write_rows(rows: list[dict]) -> None:
    PATH.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), encoding="utf-8")


def qmap(row: dict) -> dict[str, dict]:
    return {str(q.get("id")): q for q in row.get("questions", []) if isinstance(q, dict)}


def amap(row: dict) -> dict[str, dict]:
    return {str(a.get("question_id")): a for a in row.get("answer_key", []) if isinstance(a, dict)}


def immutable_projection(row: dict, changed_qids: set[str]) -> dict:
    x = copy.deepcopy(row)
    for q in x.get("questions", []):
        if str(q.get("id")) in changed_qids:
            for key in ("type", "prompt", "target_ids"):
                q.pop(key, None)
    for a in x.get("answer_key", []):
        if str(a.get("question_id")) in changed_qids:
            a.pop("answer", None)
    quality = x.get("quality")
    if isinstance(quality, dict):
        quality.pop("notes", None)
    return x


def main() -> None:
    rows = read_rows()
    if len(rows) != 60:
        raise AssertionError(f"expected 60 A2 passages, got {len(rows)}")
    by_id = {str(r.get("id")): r for r in rows}
    if not set(CHANGES) <= set(by_id):
        raise AssertionError(f"missing target passages: {sorted(set(CHANGES) - set(by_id))}")

    before = copy.deepcopy(rows)
    changed_questions = 0

    for pid, qchanges in CHANGES.items():
        row = by_id[pid]
        if len(row.get("questions", [])) != 10 or len(row.get("answer_key", [])) != 10:
            raise AssertionError(f"{pid}: expected 10 questions and 10 answers")
        review_ids = {
            str(t.get("id"))
            for t in row.get("review_lexical_targets", [])
            if isinstance(t, dict) and t.get("id")
        }
        qs = qmap(row)
        ans = amap(row)
        for qid, spec in qchanges.items():
            q = qs.get(qid)
            a = ans.get(qid)
            if q is None or a is None:
                raise AssertionError(f"{pid}: missing {qid} question/answer linkage")
            if q.get("type") != spec["expected_type"] or q.get("prompt") != spec["expected_prompt"]:
                raise AssertionError(
                    f"{pid} {qid}: source drift; got type={q.get('type')!r} prompt={q.get('prompt')!r}"
                )
            tids = [str(x) for x in spec["target_ids"]]
            if not set(tids) <= review_ids:
                raise AssertionError(f"{pid} {qid}: replacement targets are not scheduled review items: {tids}")
            q["type"] = spec["type"]
            q["prompt"] = spec["prompt"]
            q["target_ids"] = tids
            a["answer"] = spec["answer"]
            changed_questions += 1

        note = (
            "Final Pass 03 A2 lexical remediation: repurposed only existing assessment slots to test "
            "already scheduled review vocabulary; passage prose and lexical schedule unchanged."
        )
        notes = row.setdefault("quality", {}).setdefault("notes", [])
        if note not in notes:
            notes.append(note)

    # Strong mutation boundary: only approved question fields, linked answer text,
    # and one quality note may differ in the eight selected records.
    before_by_id = {str(r.get("id")): r for r in before}
    after_by_id = {str(r.get("id")): r for r in rows}
    for pid, old in before_by_id.items():
        new = after_by_id[pid]
        if pid not in CHANGES:
            if old != new:
                raise AssertionError(f"{pid}: unselected passage changed")
            continue
        qids = set(CHANGES[pid])
        if immutable_projection(old, qids) != immutable_projection(new, qids):
            raise AssertionError(f"{pid}: mutation outside approved question/answer fields")
        for field in (
            "text", "title", "word_count", "sentence_count", "new_lexical_targets",
            "review_lexical_targets", "grammar_targets", "discourse_targets", "speed_training"
        ):
            if old.get(field) != new.get(field):
                raise AssertionError(f"{pid}: forbidden drift in {field}")

    if changed_questions != 10:
        raise AssertionError(f"expected 10 question-slot changes across 8 passages, got {changed_questions}")

    write_rows(rows)
    print(json.dumps({"passages": len(CHANGES), "question_slots_changed": changed_questions}, ensure_ascii=False))


if __name__ == "__main__":
    main()
